# bharathunni.github.io

My personal site: analytical finance frameworks, published as long-form pieces.

Live at **https://bharathunni.github.io**

Everything below can be done on github.com in a web browser. You don't need to install anything.

---

## 1. Turn the site on (one time only)

1. On github.com, open this repository and go to **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to *Deploy from a branch*.
3. Set **Branch** to `main` and the folder to `/ (root)`. Click **Save**.
4. Wait about two minutes, then visit https://bharathunni.github.io.

From then on, every change saved to the `main` branch goes live automatically within one or two minutes.

---

## 2. Change your name, positioning line or contact details

Open **`_config.yml`**, click the pencil icon (Edit), and change the text inside the quotes:

| Setting | What it controls |
|---|---|
| `name` | Your name, at the top of the home page and in the header |
| `credential` | The small line above your name ("Chartered Accountant") |
| `positioning` | The one-line statement under your name. **Replace the placeholder.** |
| `email`, `linkedin` | Footer contact links. Set one to `""` to hide it. |
| `description` | The text Google and LinkedIn show when someone shares your link |

Click **Commit changes**. The change is live in a minute or two.

---

## 3. Add a new framework article

1. Open the **`templates`** folder, then **`new-framework.md`**. Click the copy icon to copy its contents.
2. Go back to the main page of the repository and open the **`_frameworks`** folder.
3. Click **Add file → Create new file**.
4. Name the file with its number and a short title, using lowercase and hyphens, for example
   `02-fp-and-a-operating-model.md`.
   The file name becomes the web address: `bharathunni.github.io/frameworks/02-fp-and-a-operating-model/`.
5. Paste the template, then edit the four lines at the top, between the `---` lines:
   - `number:` the next number in sequence (2, 3, 4 ...). This controls the order on the home page; the highest number appears first.
   - `title:` the article title, inside quotes.
   - `summary:` one or two sentences, inside quotes. These appear under the title and on the home page.
   - `date:` in the format `2026-11-01`.
6. Replace the body text below the second `---` with your article.
7. Click **Commit changes**.

The article appears on the home page automatically. Reading time is calculated for you.

To **edit** an article, open its file in `_frameworks`, click the pencil icon, change it, and commit.
To **remove** one, open the file, click the `...` menu, and choose **Delete file**.

The first article (`01-working-capital-cycle.md`) is placeholder content. Replace its text with your real framework, or delete it once you've published your own.

---

## 4. Formatting cheat sheet

Articles are written in **Markdown**, a plain-text format where a few symbols control the layout.

### Headings and text

```
## Section heading          (numbered 01, 02, 03 ... automatically)
### Sub-heading
#### Small amber label

**bold text**
*italic text*
[link text](https://example.com)

- bullet point
- another bullet

1. numbered point
2. another numbered point
```

Leave a blank line between paragraphs.

### Tables

```
| Item        | FY25 ($'000) | FY26 ($'000) |
|:------------|-------------:|-------------:|
| Revenue     |       10,000 |       12,000 |
| Costs       |      (7,000) |      (8,100) |
| Profit      |        3,000 |        3,900 |
{: .has-total}
```

- The second line sets the alignment: `:---` aligns left (for labels) and `---:` aligns right (**use this for every number column** so the figures line up).
- `{: .has-total}` on the line straight after the table styles the last row as a total, with a rule above and a double rule below. Leave it out if the table has no total.
- The columns don't need to line up neatly in the file. It just makes the table easier to read while you edit.
- On phones, wide tables scroll sideways and show a "Swipe table" hint automatically.

### Equations

Put an equation between double dollar signs, on its own lines with a blank line above and below, to show it centred:

```
$$
\text{CCC} = \text{DIO} + \text{DSO} - \text{DPO}
$$
```

Inside a sentence, use the same double dollar signs inline: `a margin of $$\tfrac{3{,}900}{12{,}000} = 32.5\%$$`.

Useful pieces:

| You type | You get |
|---|---|
| `\frac{a}{b}` | a fraction |
| `\text{Revenue}` | normal upright words inside an equation |
| `\times` | × |
| `\Delta` | Δ |
| `\sum_{t=1}^{n}` | Σ with limits |
| `x^2`, `CF_t` | superscript, subscript |
| `\%` | % (a plain % would break the equation) |
| `12{,}000` | a comma inside a number |

For a long equation that's too wide for a phone, split it across lines. Copy the `\begin{aligned}` pattern from the first article.

A single `$` for currency (like $6.5m) is safe and won't be treated as an equation.

### Worked example box

```
<div class="example" markdown="1">

#### Worked example

Your step-by-step numbers. Tables and equations work in here too.

</div>
```

Keep the blank lines exactly as shown.

### Pull quote and footnotes

```
> A key takeaway, shown in large text with an amber bar.

A sentence that needs a source.[^1]

[^1]: The note text. All notes are collected at the end of the article.
```

---

## 5. If something looks wrong

- **The change hasn't appeared yet:** wait two minutes, then hard-refresh the page (Ctrl+Shift+R on Windows, Cmd+Shift+R on Mac).
- **The site stopped updating:** open the **Actions** tab in the repository. A red ✗ next to your latest change means the build failed, and clicking it shows the error. The usual cause is a missing `---` line or a missing quote mark in the four lines at the top of an article.
- **An equation shows raw code:** check that it starts and ends with `$$`, and that any `%` is written as `\%`.

---

## 6. Using your own domain later (optional)

If you buy a domain such as `bharathunni.com`:

1. In **Settings → Pages → Custom domain**, enter the domain and save.
2. At your domain registrar, add the DNS records GitHub shows on that page. GitHub's guide is linked from there.
3. In `_config.yml`, change `url:` to your new address.

---

## What's in this repository

| Path | What it is | Edit it? |
|---|---|---|
| `_config.yml` | Your name, positioning line, contact details | Yes |
| `_frameworks/` | One file per article | Yes |
| `templates/new-framework.md` | Blank starting point for a new article | Copy it, don't edit it |
| `index.html` | Home page layout | Rarely |
| `_layouts/` | Page layouts shared by every page | Rarely |
| `assets/css/site.css` | Colours, fonts, spacing (colours are at the top) | Rarely |
| `assets/js/site.js` | Table scrolling, equation display, fade-ins | No |

**Design reference.** Fonts: Source Serif 4 (body text), IBM Plex Sans (headings), IBM Plex Mono (labels and figures). Colours: background `#0F0F0D`, panels `#171714`, rules `#2A2925`, text `#E8E3D6`, muted text `#9A958A`, amber accent `#D9A441`.
