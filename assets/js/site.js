/* Bharathunni: small site script.
   1. Makes wide tables scroll sideways on phones.
   2. Loads the equation renderer (KaTeX) only on pages that contain equations.
   3. Gentle fade-in as sections scroll into view. */
(function () {
  var prose = document.querySelector('.prose');

  // 1. Wrap tables so they scroll horizontally instead of squashing.
  if (prose) {
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
  }

  // 2. Equations: kramdown outputs \( ... \) and \[ ... \]; render them with KaTeX.
  if (prose && /\\\(|\\\[/.test(prose.textContent)) {
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
      });
    });
  }

  // 3. Reveal on scroll.
  if (prose) {
    prose.querySelectorAll(':scope > h2, :scope > .example, :scope > .table-scroll, :scope > blockquote')
      .forEach(function (el) { el.classList.add('reveal'); });
  }
  var items = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) {
    items.forEach(function (el) { el.classList.add('is-in'); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
  items.forEach(function (el, i) {
    el.style.transitionDelay = Math.min(i, 4) * 60 + 'ms';
    io.observe(el);
  });
})();
