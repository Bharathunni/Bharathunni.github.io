/* Bharath R Unni: site script. No dependencies.
   1. Theme toggle (light / dark), with a circular reveal where supported.
   2. Command menu (Ctrl/Cmd K, or "/").
   3. Home page: rotating taglines, live IST clock, copy email, cover magnet and audit stamps.
   4. Articles: wide tables scroll on phones, KaTeX equations, reading progress.
   5. Back-to-top button and soft reveal on scroll. */
(function () {
  var doc = document.documentElement;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var SITE = window.SITE || {};

  function store(key, value) { try { localStorage.setItem(key, value); } catch (e) {} }

  /* ---------- Toast ---------- */
  var toastEl = document.querySelector('[data-toast]');
  var toastTimer;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add('is-visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('is-visible'); }, 1800);
  }

  function copyEmail() {
    if (!SITE.email) return;
    var done = function () { toast('Email copied: ' + SITE.email); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(SITE.email).then(done, function () { window.location.href = 'mailto:' + SITE.email; });
    } else {
      window.location.href = 'mailto:' + SITE.email;
    }
  }

  /* ---------- 1. Theme ---------- */
  function setTheme(next, origin) {
    var apply = function () { doc.setAttribute('data-theme', next); store('theme', next); };
    if (!document.startViewTransition || reduceMotion) { apply(); return; }
    var x = origin ? origin.x : window.innerWidth / 2;
    var y = origin ? origin.y : 0;
    var r = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y));
    doc.classList.add('theme-vt');
    var vt = document.startViewTransition(apply);
    vt.ready.then(function () {
      doc.animate(
        { clipPath: ['circle(0px at ' + x + 'px ' + y + 'px)', 'circle(' + r + 'px at ' + x + 'px ' + y + 'px)'] },
        { duration: 520, easing: 'cubic-bezier(0.22, 0.7, 0.18, 1)', pseudoElement: '::view-transition-new(root)' }
      );
    }).catch(function () {});
    vt.finished.finally(function () { doc.classList.remove('theme-vt'); });
  }
  function toggleTheme(origin) { setTheme(doc.getAttribute('data-theme') === 'dark' ? 'light' : 'dark', origin); }

  document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var r = btn.getBoundingClientRect();
      toggleTheme({ x: r.left + r.width / 2, y: r.top + r.height / 2 });
    });
  });

  /* ---------- 2. Command menu ---------- */
  var cmdk = document.querySelector('[data-cmdk]');
  var cmdkData = [];
  try { cmdkData = JSON.parse(document.getElementById('cmdk-data').textContent); } catch (e) {}
  var iconTpl = document.getElementById('cmdk-icons');
  var isMac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
  if (isMac) document.querySelectorAll('[data-mod]').forEach(function (el) { el.textContent = '⌘'; });

  if (cmdk) {
    var input = cmdk.querySelector('[data-cmdk-input]');
    var list = cmdk.querySelector('[data-cmdk-list]');
    var results = [], active = 0, lastFocus = null;

    var iconFor = function (name) {
      var holder = iconTpl && iconTpl.content.querySelector('[data-icon="' + name + '"]');
      return holder ? holder.innerHTML : '';
    };
    var norm = function (s) { return (s || '').toLowerCase(); };
    var score = function (item, q) {
      if (!q) return 1;
      var t = norm(item.title), h = norm(item.hint) + ' ' + norm(item.group);
      if (t.indexOf(q) === 0) return 4;
      if (t.indexOf(q) > -1) return 3;
      var words = q.split(/\s+/).filter(Boolean);
      if (words.every(function (w) { return t.indexOf(w) > -1 || h.indexOf(w) > -1; })) return 2;
      return 0;
    };

    var render = function () {
      var q = norm(input.value.trim());
      results = cmdkData
        .map(function (item, i) { return { item: item, s: score(item, q), i: i }; })
        .filter(function (r) { return r.s > 0; })
        .sort(function (a, b) { return q ? (b.s - a.s) || (a.i - b.i) : a.i - b.i; })
        .map(function (r) { return r.item; });
      if (q) {
        // Keep groups together in their original order after scoring.
        var order = [];
        results.forEach(function (r) { if (order.indexOf(r.group) < 0) order.push(r.group); });
        results.sort(function (a, b) { return order.indexOf(a.group) - order.indexOf(b.group); });
      }
      active = 0;
      list.innerHTML = '';
      if (!results.length) {
        list.innerHTML = '<li class="cmdk__empty">Nothing found. Try another word.</li>';
        return;
      }
      var group = null;
      results.forEach(function (item, i) {
        if (item.group !== group) {
          group = item.group;
          var g = document.createElement('li');
          g.className = 'cmdk__group';
          g.setAttribute('role', 'presentation');
          g.textContent = group;
          list.appendChild(g);
        }
        var li = document.createElement('li');
        li.className = 'cmdk__item';
        li.id = 'cmdk-opt-' + i;
        li.setAttribute('role', 'option');
        li.innerHTML = iconFor(item.icon) + '<span class="cmdk__title"></span>' + (item.hint ? '<span class="cmdk__hint"></span>' : '');
        li.querySelector('.cmdk__title').textContent = item.title;
        if (item.hint) li.querySelector('.cmdk__hint').textContent = item.hint;
        li.addEventListener('mousemove', function () { if (active !== i) { active = i; highlight(false); } });
        li.addEventListener('click', function () { run(item); });
        list.appendChild(li);
      });
      highlight(true);
    };

    var highlight = function (scroll) {
      list.querySelectorAll('.cmdk__item').forEach(function (el, i) {
        var on = i === active;
        el.setAttribute('aria-selected', on ? 'true' : 'false');
        if (on) {
          input.setAttribute('aria-activedescendant', el.id);
          if (scroll) el.scrollIntoView({ block: 'nearest' });
        }
      });
    };

    var run = function (item) {
      close();
      if (item.action === 'theme') { toggleTheme(); return; }
      if (item.action === 'copy-email') { copyEmail(); return; }
      if (item.url) {
        if (item.external) window.open(item.url, '_blank', 'noopener');
        else window.location.href = item.url;
      }
    };

    var open = function () {
      if (!cmdk.hidden) return;
      lastFocus = document.activeElement;
      cmdk.hidden = false;
      cmdk.classList.remove('is-closing');
      doc.style.overflow = 'hidden';
      input.value = '';
      render();
      setTimeout(function () { input.focus(); }, 10);
    };
    var close = function () {
      if (cmdk.hidden || cmdk.classList.contains('is-closing')) return;
      cmdk.classList.add('is-closing');
      doc.style.overflow = '';
      setTimeout(function () {
        cmdk.hidden = true;
        cmdk.classList.remove('is-closing');
        if (lastFocus && lastFocus.focus) lastFocus.focus();
      }, reduceMotion ? 0 : 150);
    };

    input.addEventListener('input', render);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); if (results.length) { active = (active + 1) % results.length; highlight(true); } }
      else if (e.key === 'ArrowUp') { e.preventDefault(); if (results.length) { active = (active - 1 + results.length) % results.length; highlight(true); } }
      else if (e.key === 'Enter') { e.preventDefault(); if (results[active]) run(results[active]); }
    });
    cmdk.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.preventDefault(); close(); }
      if (e.key === 'Tab') { e.preventDefault(); input.focus(); }
    });
    cmdk.querySelectorAll('[data-cmdk-close]').forEach(function (el) { el.addEventListener('click', close); });
    document.querySelectorAll('[data-cmdk-open]').forEach(function (el) { el.addEventListener('click', open); });

    document.addEventListener('keydown', function (e) {
      var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName) || e.target.isContentEditable;
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); cmdk.hidden ? open() : close(); return; }
      if (typing || e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.key === '/') { e.preventDefault(); open(); }
      else if (e.key.toLowerCase() === 'd' && cmdk.hidden) { toggleTheme(); }
    });
  }

  /* ---------- 3. Home page ---------- */

  // Rotating taglines
  document.querySelectorAll('[data-flip]').forEach(function (el) {
    var items;
    try { items = JSON.parse(el.getAttribute('data-items')); } catch (e) { return; }
    if (!items || items.length < 2 || reduceMotion) return;
    var i = 0, timer = null;
    var span = el.querySelector('.flip__text');
    var step = function () {
      span.classList.remove('is-in');
      span.classList.add('is-out');
      setTimeout(function () {
        i = (i + 1) % items.length;
        span.textContent = items[i];
        span.classList.remove('is-out');
        void span.offsetWidth;
        span.classList.add('is-in');
      }, 330);
    };
    var start = function () { if (!timer) timer = setInterval(step, 3200); };
    var stop = function () { clearInterval(timer); timer = null; };
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) { en[0].isIntersecting && !document.hidden ? start() : stop(); }).observe(el);
    } else { start(); }
    document.addEventListener('visibilitychange', function () { document.hidden ? stop() : start(); });
  });

  // Live clock in IST, with the difference from the visitor's own time
  var clock = document.querySelector('[data-clock]');
  if (clock) {
    var tz = SITE.timezone || 'Asia/Kolkata';
    var diffEl = document.querySelector('[data-clock-diff]');
    var fmt;
    try { fmt = new Intl.DateTimeFormat('en-GB', { timeZone: tz, hour: '2-digit', minute: '2-digit', hour12: false }); } catch (e) {}
    var offsetMins = function (date, zone) {
      var p = new Intl.DateTimeFormat('en-US', { timeZone: zone, hourCycle: 'h23', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric' }).formatToParts(date);
      var get = function (t) { return +p.filter(function (x) { return x.type === t; })[0].value; };
      return (Date.UTC(get('year'), get('month') - 1, get('day'), get('hour'), get('minute')) - Math.floor(date.getTime() / 60000) * 60000) / 60000;
    };
    var tick = function () {
      var now = new Date();
      if (fmt) clock.textContent = fmt.format(now);
      clock.setAttribute('datetime', now.toISOString());
      if (diffEl) {
        try {
          var diff = offsetMins(now, tz) + now.getTimezoneOffset();
          if (Math.abs(diff) < 1) { diffEl.textContent = ' · same time as you'; }
          else {
            var h = Math.floor(Math.abs(diff) / 60), m = Math.abs(diff) % 60;
            diffEl.textContent = ' · ' + h + 'h' + (m ? ' ' + m + 'm' : '') + (diff > 0 ? ' ahead' : ' behind');
          }
        } catch (e) { diffEl.textContent = ''; }
      }
    };
    tick();
    setInterval(tick, 15000);
  }

  // Copy email
  document.querySelectorAll('[data-copy-email]').forEach(function (btn) {
    btn.addEventListener('click', copyEmail);
  });

  // Cover: the monogram leans toward the cursor; a click stamps the page
  var cover = document.querySelector('[data-cover]');
  if (cover) {
    var magnet = cover.querySelector('[data-magnet]');
    var stamps = cover.querySelector('[data-stamps]');
    var words = ['Vouched ✓', 'Tallied', 'True & Fair', 'Verified', 'Dr = Cr', 'Reconciled'];
    var w = 0, raf = null;
    cover.addEventListener('pointermove', function (e) {
      if (e.pointerType !== 'mouse') return;
      var r = cover.getBoundingClientRect();
      var x = e.clientX - r.left, y = e.clientY - r.top;
      cover.style.setProperty('--mx', x + 'px');
      cover.style.setProperty('--my', y + 'px');
      if (reduceMotion || !magnet) return;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(function () {
        var dx = (x - r.width / 2) / 6, dy = (y - r.height / 2) / 6;
        magnet.style.transform = 'translate(' + dx + 'px,' + dy + 'px)';
      });
    });
    cover.addEventListener('pointerleave', function () { if (magnet) magnet.style.transform = ''; });
    cover.addEventListener('click', function (e) {
      if (!stamps) return;
      var r = cover.getBoundingClientRect();
      var s = document.createElement('span');
      s.className = 'stamp';
      s.textContent = words[w++ % words.length];
      s.style.left = (e.clientX - r.left) + 'px';
      s.style.top = (e.clientY - r.top) + 'px';
      s.style.setProperty('--r', (Math.random() * 18 - 13).toFixed(1) + 'deg');
      stamps.appendChild(s);
      setTimeout(function () { s.remove(); }, 2700);
      if (navigator.vibrate) { try { navigator.vibrate(8); } catch (err) {} }
    });
  }

  /* ---------- 4. Articles ---------- */
  var prose = document.querySelector('[data-prose]');

  if (prose) {
    // Wrap tables so they scroll horizontally instead of squashing.
    prose.querySelectorAll('table').forEach(function (table) {
      var box = document.createElement('div');
      box.className = 'table-scroll';
      table.parentNode.insertBefore(box, table);
      box.appendChild(table);
      var hint = document.createElement('p');
      hint.className = 'scroll-hint';
      hint.setAttribute('aria-hidden', 'true');
      hint.textContent = 'Swipe table →';
      box.parentNode.insertBefore(hint, box.nextSibling);
    });
    var markScrollable = function () {
      prose.querySelectorAll('.table-scroll').forEach(function (box) {
        box.classList.toggle('is-scrollable', box.scrollWidth > box.clientWidth + 1);
      });
    };
    markScrollable();
    window.addEventListener('resize', markScrollable);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(markScrollable);

    // Equations: kramdown outputs \( ... \) and \[ ... \]; render them with KaTeX.
    if (/\\\(|\\\[/.test(prose.textContent)) {
      var base = 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/';
      var css = document.createElement('link');
      css.rel = 'stylesheet';
      css.href = base + 'katex.min.css';
      document.head.appendChild(css);
      var load = function (src, done) {
        var s = document.createElement('script');
        s.src = src; s.onload = done; document.head.appendChild(s);
      };
      load(base + 'katex.min.js', function () {
        load(base + 'contrib/auto-render.min.js', function () {
          window.renderMathInElement(prose, {
            delimiters: [
              { left: '\\[', right: '\\]', display: true },
              { left: '\\(', right: '\\)', display: false }
            ],
            throwOnError: false
          });
          markScrollable();
        });
      });
    }

    prose.querySelectorAll(':scope > h2, :scope > .example, :scope > .table-scroll, :scope > blockquote, :scope > p > img')
      .forEach(function (el) { (el.tagName === 'IMG' ? el.parentNode : el).classList.add('reveal'); });

    // Reading progress
    var progress = document.querySelector('[data-progress]');
    if (progress) {
      var update = function () {
        var r = prose.getBoundingClientRect();
        var total = r.height - window.innerHeight * 0.6;
        var pct = total > 0 ? Math.min(100, Math.max(0, Math.round((-r.top + window.innerHeight * 0.2) / total * 100))) : 100;
        progress.textContent = pct;
      };
      update();
      window.addEventListener('scroll', update, { passive: true });
    }
  }

  /* ---------- 5. Back to top, reveal ---------- */
  var toTop = document.querySelector('[data-to-top]');
  if (toTop) {
    var onScroll = function () { toTop.classList.toggle('is-visible', window.scrollY > 640); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    toTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' }); });
  }

  var items = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) {
    items.forEach(function (el) { el.classList.add('is-in'); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    var batch = 0;
    entries.forEach(function (entry) {
      // Also reveal anything already scrolled past, so a fast scroll never leaves gaps.
      if (entry.isIntersecting || entry.boundingClientRect.top < 0) {
        entry.target.style.transitionDelay = Math.min(batch++, 5) * 70 + 'ms';
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -6% 0px', threshold: 0.05 });
  items.forEach(function (el) { io.observe(el); });
})();
