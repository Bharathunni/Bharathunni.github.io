"""End-to-end test on synthetic files in all three formats, with a fake exchange (no network)."""
import io
import os
import tempfile
import zipfile
from datetime import date, timedelta

os.environ["MASCAN_HOME"] = tempfile.mkdtemp(prefix="mascan_test_")

import polars as pl  # noqa: E402
import pytest  # noqa: E402

from mascan import build, config, download, manifest, qa  # noqa: E402
from mascan.parse import ParseError, parse  # noqa: E402

UDIFF_HDR = ("TradDt,BizDt,Sgmt,Src,FinInstrmTp,FinInstrmId,ISIN,TckrSymb,SctySrs,XpryDt,FininstrmActlXpryDt,"
             "StrkPric,OptnTp,FinInstrmNm,OpnPric,HghPric,LwPric,ClsPric,LastPric,PrvsClsgPric,UndrlygPric,"
             "SttlmPric,OpnIntrst,ChngInOpnIntrst,TtlTradgVol,TtlTrfVal,TtlNbOfTxsExctd,SsnId,NewBrdLotQty,Rmks")


def zipped(name, text):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(name, text)
    return buf.getvalue()


def udiff(d, src, n=30):
    lines = [UDIFF_HDR]
    for i in range(n):
        lines.append(f"{d},{d},CM,{src},STK,{500000 + i},INE{i:03d}A01011,SYM{i},{'EQ' if src == 'NSE' else 'A'},,,,,"
                     f"NAME {i},100.0,110.5,95.0,{100 + i * 0.25},105,101.0,,105,,,{1000 + i},1050000.50,321,F1,1,")
    return "\n".join(lines) + "\n"


def nse_legacy(d, n=30, isin=True):
    hdr = "SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,TOTTRDQTY,TOTTRDVAL,TIMESTAMP,TOTALTRADES" + (",ISIN," if isin else ",")
    ts = d.strftime("%d-%b-%Y").upper()
    rows = [f"SYM{i},EQ,100,110,95,{100 + i * 0.25},105,101,{1000 + i},1050000.5,{ts},321" + (f",INE{i:03d}A01011," if isin else ",")
            for i in range(n)]
    return "\n".join([hdr] + rows) + "\n"


def bse_legacy(d, n=30):
    hdr = "SC_CODE,SC_NAME,SC_GROUP,SC_TYPE,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,NO_TRADES,NO_OF_SHRS,NET_TURNOV,TDCLOINDI,ISIN_CODE,TRADING_DATE"
    rows = [f"{500000 + i},NAME {i}    ,A ,Q,100.00,110.00,95.00,{100 + i * 0.25},105.00,101.00,321,{1000 + i},1050000.00,,INE{i:03d}A01011,{d:%d-%b-%y}"
            for i in range(n)]
    return "\n".join([hdr] + rows) + "\n"


class Resp:
    def __init__(self, code, content=b""):
        self.status_code, self.content = code, content


class FakeExchange:
    """Serves files for weekdays only; HTML page for one 'blocked' day; 404 otherwise."""
    def __init__(self, exch):
        self.exch = exch
        self.calls = 0

    def get(self, url, timeout=None):
        self.calls += 1
        name = url.rsplit("/", 1)[1]
        for d in (date(2024, 6, 3) + timedelta(days=k) for k in range(60)):
            if d.weekday() >= 5:
                continue
            for fmt, u, fname in config.candidates(self.exch, d):
                if fname != name or u != url:
                    continue
                if self.exch == "nse":
                    if fmt == "udiff" and d >= date(2024, 7, 8) and "nsearchives" in u:
                        return Resp(200, zipped(name[:-4], udiff(d.isoformat(), "NSE")))
                    if fmt == "nse_legacy" and d < date(2024, 7, 8) and "nsearchives" in u:
                        return Resp(200, zipped(name[:-4], nse_legacy(d)))
                else:
                    if fmt == "udiff" and d >= date(2024, 7, 8):
                        return Resp(200, udiff(d.isoformat(), "BSE").encode())
                    if fmt == "bse_legacy" and d < date(2024, 7, 8) and "ISINCODE" in name:
                        return Resp(200, zipped(name.replace(".zip", ".CSV"), bse_legacy(d)))
        return Resp(404, b"<html>Not found</html>")


@pytest.fixture(scope="module", autouse=True)
def fast():
    config.REQUEST_GAP_SECONDS = 0
    download.random.random = lambda: 0
    download.time.sleep = lambda s: None


def test_parsers_agree_across_formats():
    d = date(2024, 7, 5)
    a = parse(zipped("x.csv", nse_legacy(d)), "nse", d)
    b = parse(zipped("x.csv", udiff(d.isoformat(), "NSE")), "nse", d)
    c = parse(zipped("x.CSV", bse_legacy(d)), "bse", d)
    e = parse(udiff(d.isoformat(), "BSE").encode(), "bse", d)
    for df in (a, b, c, e):
        assert df.height == 30 and df["date"].unique().to_list() == [d]
        assert df["isin"].null_count() == 0 and df["close"].min() == 100.0 and df["close"].max() == 107.25
    assert a["code"][0] == "SYM0" and c["code"][0] == "500000" and e["code"][0] == "500000"
    assert c["name"][0] == "NAME 0" and c["series"][0] == "A"          # whitespace stripped
    assert a["volume"][0] == 1000 and c["turnover"][0] == 1050000.0


def test_old_file_without_isin_parses():
    d = date(2008, 1, 2)
    df = parse(zipped("x.csv", nse_legacy(d, isin=False)), "nse", d)
    assert df.height == 30 and df["isin"].null_count() == 30


def test_wrong_date_inside_file_is_rejected():
    with pytest.raises(ParseError):
        parse(zipped("x.csv", nse_legacy(date(2024, 7, 4))), "nse", date(2024, 7, 5))


def test_html_is_not_mistaken_for_data():
    assert download.classify(b"<!DOCTYPE html><html>Access Denied</html>") == "html"
    assert download.classify(b"<!doctype html><html><head><base href=\"/\"></head><body><app-root></app-root>") == "notfound"
    assert download.classify(b"PK\x03\x04rest") == "zip"
    assert download.classify(UDIFF_HDR.encode() + b"\n") == "csv"
    with pytest.raises(ParseError):
        parse(b"a,b,c\n1,2,3\n", "nse", date(2024, 7, 5))


def test_end_to_end_and_idempotent():
    start, end = date(2024, 6, 24), date(2024, 7, 19)   # spans the format switch
    fakes = {}

    def factory(exch):
        fakes[exch] = FakeExchange(exch)
        return fakes[exch]

    s1 = download.run(["nse", "bse"], start, end, session_factory=factory)
    assert s1["nse"]["ok"] == 20 and s1["bse"]["ok"] == 20            # 4 weeks of weekdays
    assert s1["nse"]["missing"] == 6 and s1["nse"]["blocked"] == 0   # weekends

    s2 = download.run(["nse", "bse"], start, end, session_factory=factory)
    assert s2["nse"]["ok"] == 0 and s2["nse"]["skipped"] == 26 and fakes["nse"].calls == 0

    r = build.run()
    assert r["files_parsed"] == 40 and not r["failed"]
    assert build.run()["files_parsed"] == 0                           # nothing new -> nothing rebuilt

    df = build.load().collect()
    assert df.height == 40 * 30
    assert set(df["fmt"].unique()) == {"udiff", "nse_legacy", "bse_legacy"}
    assert df.filter(pl.col("exch") == "nse")["date"].n_unique() == 20

    q = qa.run()
    assert q["hard"] == 0, q["issues"]


def test_qa_catches_truncated_day_and_missing_exchange():
    d = date(2024, 7, 22)
    rel = f"nse/2024/BhavCopy_NSE_CM_0_0_0_{d:%Y%m%d}_F_0000.csv.zip"
    (config.RAW / rel).write_bytes(zipped("x.csv", udiff(d.isoformat(), "NSE", n=5)))   # truncated file
    with manifest.connect() as con:
        manifest.upsert(con, exch="nse", d=d.isoformat(), status="ok", fmt="udiff", path=rel, bytes=1,
                        sha256="x", http=200, note=None, fetched_at="t")
    build.run()
    q = qa.run()
    checks = {(i["check"], i["exch"]) for i in q["issues"]}
    assert ("low_row_count", "nse") in checks and ("missing_vs_other_exchange", "bse") in checks
    assert q["hard"] >= 1


def test_bse_soft_404_is_missing_not_blocked():
    class Shell:
        def get(self, url, timeout=None):
            return Resp(200, b"<!doctype html><html><head><title>BSE</title></head><body><app-root></app-root></body></html>")

    row = download.fetch_day(Shell(), "bse", date(2026, 11, 10))
    assert row["status"] == "missing"


def test_blocked_run_aborts_instead_of_recording_holidays():
    class Blocked:
        def get(self, url, timeout=None):
            return Resp(403, b"<html>Access Denied</html>")

    s = download.run(["nse"], date(2023, 1, 2), date(2023, 3, 1), session_factory=lambda e: Blocked())
    assert s["nse"]["blocked"] == config.MAX_CONSECUTIVE_BLOCKS and "aborted_at" in s["nse"]
    with manifest.connect() as con:
        assert con.execute("SELECT COUNT(*) FROM files WHERE d LIKE '2023%' AND status='missing'").fetchone()[0] == 0
