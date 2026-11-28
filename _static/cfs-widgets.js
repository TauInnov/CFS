/* cfs-widgets.js: interactive widgets for the CFS course site.
 *
 * A widget on a page is a raw-HTML block in a markdown cell (no blank lines
 * inside it, so MyST passes it through as one block):
 *
 *   <div class="cfs-widget" data-widget="slice1d" dir="ltr" data-cfs='{...}'>
 *   <p dir="rtl"><strong>Title.</strong> Hebrew text for Colab / no JavaScript.</p>
 *   </div>
 *
 * When the page loads, every .cfs-widget[data-widget] is replaced by the
 * widget of that name, built from the JSON in data-cfs. The values in the
 * JSON come from the page's own code (computed in Python when the cell was
 * written); the functions in part 1 follow Python / NumPy exactly.
 *
 * Add a widget type:
 *   CFSWidgets.register('name', function (root, data, api) { ... });
 *   api.frame(root, data)            -> body element under the title and hint
 *   api.stepper(root, data, render)  -> Back / Next / Reset / dots around
 *                                       render(stage, step, index, previous)
 *   api.h, api.rich, api.core         DOM helpers and the Python semantics
 *
 * No external libraries; the site works offline. Colours and layout are in
 * cfs-widgets.css (light and dark palettes of tools/figures/cfsfig.py).
 */
(function (global) {
  'use strict';

  /* ------------------------------------------------------------------ */
  /* 1. Python and NumPy semantics (pure functions; tested under Node)   */
  /* ------------------------------------------------------------------ */

  function pyError(type, message) {
    var e = new Error(message);
    e.pyType = type;            // 'ValueError', 'IndexError', ... or 'hint'
    return e;
  }

  /* list(range(*slice(start, stop, step).indices(n))), as CPython does it */
  function sliceIndices(n, start, stop, step) {
    if (step === null || step === undefined) { step = 1; }
    if (step === 0) { throw pyError('ValueError', 'slice step cannot be zero'); }
    var neg = step < 0;
    var lower = neg ? -1 : 0;
    var upper = neg ? n - 1 : n;
    function adjust(v, dflt) {
      if (v === null || v === undefined) { return dflt; }
      if (v < 0) {
        v += n;
        if (v < lower) { v = lower; }
      } else if (v > upper) {
        v = upper;
      }
      return v;
    }
    var s = adjust(start, neg ? upper : lower);
    var e = adjust(stop, neg ? lower : upper);
    var out = [];
    var i;
    if (neg) {
      for (i = s; i > e; i += step) { out.push(i); }
    } else {
      for (i = s; i < e; i += step) { out.push(i); }
    }
    return out;
  }

  var INT_RE = /^[+-]?(0|[1-9][0-9]*)$/;
  var FLOAT_RE = /^[+-]?([0-9]+\.[0-9]*|\.[0-9]+|[0-9]+(\.[0-9]*)?e[+-]?[0-9]+)$/i;

  /* One number typed by a student: an int, or the real Python error. */
  function parseNumber(text, inSlice) {
    var p = String(text).replace(/\s+/g, '');
    if (inSlice && (p === '' || p === 'None')) { return null; }
    if (inSlice && p === 'True') { return 1; }
    if (inSlice && p === 'False') { return 0; }
    if (INT_RE.test(p)) { return parseInt(p, 10); }
    if (FLOAT_RE.test(p)) {
      if (inSlice) {
        throw pyError('TypeError', 'slice indices must be integers or None ' +
                      'or have an __index__ method');
      }
      throw pyError('IndexError', 'only integers, slices (`:`), ellipsis ' +
                    '(`...`), numpy.newaxis (`None`) and integer or boolean ' +
                    'arrays are valid indices');
    }
    throw pyError('hint', 'כתבו מספר שלם, למשל `2` או `-3`.');
  }

  /* "2:8:2" -> slice, "-1" -> int, "" -> null (an axis left out) */
  function parseIndex(text) {
    var s = String(text).replace(/\s+/g, '');
    if (s === '') { return null; }
    var parts = s.split(':');
    if (parts.length > 3) { throw pyError('SyntaxError', 'invalid syntax'); }
    if (parts.length === 1) {
      return { kind: 'int', value: parseNumber(parts[0], false) };
    }
    var v = parts.map(function (p) { return parseNumber(p, true); });
    return { kind: 'slice', start: v[0], stop: v[1],
             step: parts.length === 3 ? v[2] : null };
  }

  function sliceText(sl) {
    function part(v) { return v === null || v === undefined ? '' : String(v); }
    var t = part(sl.start) + ':' + part(sl.stop);
    if (sl.step !== null && sl.step !== undefined) { t += ':' + sl.step; }
    return t;
  }

  function indexText(ix) {
    if (ix === null) { return ':'; }
    return ix.kind === 'int' ? String(ix.value) : sliceText(ix);
  }

  /* The positions one index selects on an axis of size n. */
  function indexAxis(ix, n, axis) {
    if (ix === null) { ix = { kind: 'slice', start: null, stop: null, step: null }; }
    if (ix.kind === 'int') {
      var v = ix.value;
      if (v < -n || v >= n) {
        throw pyError('IndexError', 'index ' + v + ' is out of bounds for axis ' +
                      axis + ' with size ' + n);
      }
      return { indices: [v < 0 ? v + n : v], keep: false };
    }
    return { indices: sliceIndices(n, ix.start, ix.stop, ix.step), keep: true };
  }

  function sumOf(a) {
    var s = 0;
    for (var i = 0; i < a.length; i++) { s += a[i]; }
    return s;
  }

  var OPS = {
    sum: sumOf,
    mean: function (a) { return sumOf(a) / a.length; },
    max: function (a) { return Math.max.apply(null, a); },
    min: function (a) { return Math.min.apply(null, a); },
    std: function (a) {     // ddof=0, as NumPy's default
      var m = sumOf(a) / a.length;
      return Math.sqrt(sumOf(a.map(function (x) { return (x - m) * (x - m); })) /
                       a.length);
    }
  };

  /* M.op(axis=axis) for a 2-D list of rows; axis 0, 1 or null (no axis). */
  function reduce(M, op, axis) {
    var f = OPS[op];
    var R = M.length;
    var C = M[0].length;
    var i, j, col;
    if (axis === 0) {
      var out0 = [];
      for (j = 0; j < C; j++) {
        col = [];
        for (i = 0; i < R; i++) { col.push(M[i][j]); }
        out0.push(f(col));
      }
      return { shape: [C], values: out0 };
    }
    if (axis === 1) {
      return { shape: [R], values: M.map(function (row) { return f(row); }) };
    }
    var all = [];
    M.forEach(function (row) { all = all.concat(row); });
    return { shape: [], values: [f(all)] };
  }

  function pyShape(shape) {        // (5, 60)  (60,)  ()
    return '(' + shape.join(', ') + (shape.length === 1 ? ',' : '') + ')';
  }

  function npShape(shape) {        // NumPy's error text: (5,60)  (60,)
    return '(' + shape.join(',') + (shape.length === 1 ? ',' : '') + ')';
  }

  /* NumPy's broadcasting rule for two shapes, compared from the right. */
  function broadcast(a, b) {
    var n = Math.max(a.length, b.length);
    var pairs = [];
    var ok = true;
    for (var k = 1; k <= n; k++) {
      var ia = a.length - k;
      var ib = b.length - k;
      var x = ia >= 0 ? a[ia] : 1;
      var y = ib >= 0 ? b[ib] : 1;
      var good = x === y || x === 1 || y === 1;
      if (!good) { ok = false; }
      pairs.unshift({ a: x, b: y, padA: ia < 0, padB: ib < 0, ok: good,
                      out: good ? (x === 1 ? y : x) : null });
    }
    var res = { ok: ok, pairs: pairs };
    if (ok) {
      res.shape = pairs.map(function (p) { return p.out; });
    } else {
      res.error = 'operands could not be broadcast together with shapes ' +
                  npShape(a) + ' ' + npShape(b) + ' ';
      for (var m = pairs.length - 1; m >= 0; m--) {
        if (!pairs[m].ok) { res.failed = m; break; }
      }
    }
    return res;
  }

  function fmt(x, d) {
    var s = Number(x).toFixed(d);
    if (Number(s) === 0) { s = s.replace('-', ''); }
    return s;
  }

  /* len(range(start, stop, step)), as Python computes it. */
  function rangeLen(start, stop, step) {
    if (step === 0) { throw pyError('ValueError', 'range() arg 3 must not be zero'); }
    var n = step > 0 ? Math.ceil((stop - start) / step) : Math.ceil((start - stop) / -step);
    return Math.max(0, n);
  }

  /* list(range(start, stop, step)); for long ranges only the first `cap`
     values and the last one are listed (values[k] = start + k * step). */
  function rangeValues(start, stop, step, cap) {
    var n = rangeLen(start, stop, step);
    var out = [];
    var k;
    if (cap === undefined || n <= cap) {
      for (k = 0; k < n; k++) { out.push(start + k * step); }
      return { len: n, values: out, cut: false };
    }
    for (k = 0; k < cap - 1; k++) { out.push(start + k * step); }
    return { len: n, values: out, last: start + (n - 1) * step, cut: true };
  }

  /* One argument of range() typed by a student: an int, null (left empty),
     or the real Python error. */
  function parseRangeArg(text) {
    var p = String(text).replace(/\s+/g, '');
    if (p === '') { return null; }
    if (INT_RE.test(p)) { return parseInt(p, 10); }
    if (p === 'True') { return 1; }
    if (p === 'False') { return 0; }
    if (FLOAT_RE.test(p)) {
      throw pyError('TypeError', "'float' object cannot be interpreted as an integer");
    }
    if (p === 'None') {
      throw pyError('TypeError', "'NoneType' object cannot be interpreted as an integer");
    }
    throw pyError('hint', 'כתבו מספר שלם, למשל `2` או `-3`.');
  }

  /* The call written in three boxes (start, stop, step), as Python reads it:
     range(stop), range(start, stop) or range(start, stop, step). */
  function rangeCall(startText, stopText, stepText) {
    var a = parseRangeArg(startText);
    var b = parseRangeArg(stopText);
    var c = parseRangeArg(stepText);
    if (b === null) {
      if (a === null && c === null) {
        throw pyError('TypeError', 'range expected at least 1 argument, got 0');
      }
      throw pyError('hint', 'כתבו ערך ל-`stop`.');
    }
    var text = a === null && c === null ? 'range(' + b + ')' :
               c === null ? 'range(' + a + ', ' + b + ')' :
               'range(' + (a === null ? 0 : a) + ', ' + b + ', ' + c + ')';
    var start = a === null ? 0 : a;
    var step = c === null ? 1 : c;
    rangeLen(start, b, step);          // raises for step 0
    return { text: text, start: start, stop: b, step: step };
  }

  var core = {
    pyError: pyError, sliceIndices: sliceIndices, parseNumber: parseNumber,
    parseIndex: parseIndex, sliceText: sliceText, indexText: indexText,
    indexAxis: indexAxis, reduce: reduce, pyShape: pyShape, npShape: npShape,
    broadcast: broadcast, fmt: fmt, rangeLen: rangeLen, rangeValues: rangeValues,
    parseRangeArg: parseRangeArg, rangeCall: rangeCall
  };

  if (typeof module === 'object' && module.exports) { module.exports = core; }
  if (typeof document === 'undefined') { return; }

  /* ------------------------------------------------------------------ */
  /* 2. DOM helpers                                                      */
  /* ------------------------------------------------------------------ */

  function append(el, c) {
    if (c === null || c === undefined || c === false) { return; }
    if (Array.isArray(c)) { c.forEach(function (x) { append(el, x); }); return; }
    el.appendChild(typeof c === 'object' ? c : document.createTextNode(String(c)));
  }

  function h(tag, attrs) {
    var el = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v === null || v === undefined || v === false) { return; }
        if (k === 'class') { el.className = v; }
        else if (k === 'text') { el.textContent = v; }
        else if (k.slice(0, 2) === 'on') { el.addEventListener(k.slice(2), v); }
        else { el.setAttribute(k, v === true ? '' : v); }
      });
    }
    for (var i = 2; i < arguments.length; i++) { append(el, arguments[i]); }
    return el;
  }

  var SVGNS = 'http://www.w3.org/2000/svg';
  function s(tag, attrs, text) {
    var el = document.createElementNS(SVGNS, tag);
    Object.keys(attrs || {}).forEach(function (k) { el.setAttribute(k, attrs[k]); });
    if (text !== undefined) { el.textContent = text; }
    return el;
  }

  /* Hebrew text with `code` spans: each span is an LTR island. */
  function rich(text) {
    return String(text).split('`').map(function (part, i) {
      if (i % 2 === 0) { return part; }
      return h('code', { class: 'cw-ic', dir: 'ltr' }, part);
    });
  }

  function button(label, onclick, attrs) {
    var a = { type: 'button', class: 'cw-btn', onclick: onclick };
    Object.keys(attrs || {}).forEach(function (k) { a[k] = attrs[k]; });
    return h('button', a, label);
  }

  function codeButton(label, onclick) {
    return button(label, onclick, { class: 'cw-btn cw-btn-code', dir: 'ltr' });
  }

  /* A group of toggle buttons; exactly one is pressed. */
  function toggleGroup(items, label, onpick) {
    var btns = [];
    var group = h('div', { class: 'cw-toggle', role: 'group', 'aria-label': label });
    items.forEach(function (it) {
      var b = button(it.label, function () { pick(it.value); onpick(it.value); },
                     { class: 'cw-btn' + (it.code ? ' cw-btn-code' : ''),
                       dir: it.code ? 'ltr' : 'rtl', 'aria-pressed': 'false' });
      b._value = it.value;
      btns.push(b);
      group.appendChild(b);
    });
    function pick(v) {
      btns.forEach(function (b) { b.setAttribute('aria-pressed', String(b._value === v)); });
    }
    group.pick = pick;
    return group;
  }

  function errorBox(e) {
    if (e.pyType === 'hint') {
      return h('div', { class: 'cw-error', dir: 'rtl' }, rich(e.message));
    }
    return h('div', { class: 'cw-error' },
             h('code', { dir: 'ltr' }, (e.pyType || 'Error') + ': ' + e.message));
  }

  function cell(text, cls) {
    return h('span', { class: 'cw-cell' + (cls ? ' ' + cls : '') }, text);
  }

  function clear(el) {
    while (el.firstChild) { el.removeChild(el.firstChild); }
  }

  /* A strip of n cells that wraps into even rows (16 -> 8 + 8, not 14 + 2):
     the fewest rows that fit, with the cells spread evenly over them. */
  function balance(strip, n, unitPx) {
    function layout() {
      var w = strip.clientWidth;
      if (!w) { return; }
      var fit = Math.max(1, Math.floor((w + 4) / (unitPx + 4)));
      var per = Math.ceil(n / Math.ceil(n / fit));
      strip.style.gridTemplateColumns = 'repeat(' + per + ', minmax(0, ' +
                                        Math.round(unitPx * 1.35) + 'px))';
    }
    strip.classList.add('cw-balanced');
    layout();
    if (typeof ResizeObserver !== 'undefined') {
      new ResizeObserver(layout).observe(strip);
    } else {
      global.addEventListener('resize', layout);
    }
  }

  /* Title and short instruction (Hebrew, RTL) above the widget's body. */
  function frame(root, data, hint) {
    clear(root);
    root.classList.add('cw-ready');
    root.setAttribute('dir', 'ltr');
    var head = h('div', { class: 'cw-head', dir: 'rtl' },
      h('div', { class: 'cw-title', role: 'heading', 'aria-level': '4' },
        rich(data.title || '')),
      (data.hint || hint) ? h('div', { class: 'cw-hint' }, rich(data.hint || hint)) : null);
    var body = h('div', { class: 'cw-body' });
    root.appendChild(head);
    root.appendChild(body);
    return body;
  }

  /* A labelled text input: the label sits under the box (start, stop...). */
  function labelledInput(label, value, oninput, width) {
    var inp = h('input', { class: 'cw-in', type: 'text', value: value,
                           autocomplete: 'off', autocapitalize: 'off',
                           spellcheck: 'false', size: String(width || 4),
                           oninput: oninput });
    return { input: inp,
             el: h('label', { class: 'cw-lab' }, inp, h('span', { class: 'cw-lab-text' }, label)) };
  }

  /* ------------------------------------------------------------------ */
  /* 3. The stepper: steps, highlighted code lines, Back / Next / Reset  */
  /* ------------------------------------------------------------------ */
  /* data.code: optional full listing (each step lights data.steps[i].lines)
   * data.steps[i].code: optional commands of that step only
   * data.steps[i].caption: Hebrew, with `code`
   * render(stage, step, i, previous): draws the state of step i            */
  function stepper(root, data, render) {
    return stepperIn(frame(root, data, data.hint ||
                           'לחצו על "הבא" כדי להתקדם צעד אחד, ועל "הקודם" כדי לחזור.'),
                     data, render);
  }

  /* A widget made of a few short examples: a toggle picks the example, and
     each example (data.scenarios[k]: label, code, steps) is its own stepper.
     makeRender(scenario) returns a fresh render function for it. */
  function scenarioStepper(root, data, makeRender) {
    var body = frame(root, data, data.hint);
    var holder = h('div', { class: 'cw-scenario' });
    var group = toggleGroup(data.scenarios.map(function (sc, k) {
      return { label: sc.label, value: k };
    }), 'דוגמאות', function (k) { show(k); });
    body.appendChild(group);
    body.appendChild(holder);
    function show(k) {
      clear(holder);
      group.pick(k);
      stepperIn(holder, data.scenarios[k], makeRender(data.scenarios[k]));
    }
    show(0);
  }

  /* The stepper inside a given element. */
  function stepperIn(parent, data, render) {
    var body = h('div', { class: 'cw-stepper' });
    parent.appendChild(body);
    var steps = data.steps;
    var cur = -1;
    var listing = null;
    var lineEls = [];
    if (data.code) {
      listing = h('pre', { class: 'cw-listing', dir: 'ltr' });
      data.code.forEach(function (line) {
        var el = h('span', { class: 'cw-line' + (/^\s*#/.test(line) ? ' cw-comment' : '') },
                   line === '' ? ' ' : line);
        lineEls.push(el);
        listing.appendChild(el);
      });
      body.appendChild(listing);
    }
    var cmds = data.code ? null : h('pre', { class: 'cw-listing', dir: 'ltr' });
    if (cmds) { body.appendChild(cmds); }
    var caption = h('div', { class: 'cw-caption', dir: 'rtl', 'aria-live': 'polite' });
    var stage = h('div', { class: 'cw-stage' });
    body.appendChild(caption);
    body.appendChild(stage);

    var back = button('הקודם', function () { go(cur - 1); }, { dir: 'rtl' });
    var next = button('הבא', function () { go(cur + 1); },
                      { dir: 'rtl', class: 'cw-btn cw-btn-main' });
    var reset = button('התחלה מחדש', function () { go(0); }, { dir: 'rtl' });
    var dots = h('div', { class: 'cw-dots', role: 'group', 'aria-label': 'צעדים' });
    var dotEls = steps.map(function (st, i) {
      var d = h('button', { type: 'button', class: 'cw-dot',
                            'aria-label': 'צעד ' + (i + 1) + ' מתוך ' + steps.length,
                            onclick: function () { go(i); } });
      dots.appendChild(d);
      return d;
    });
    var counter = h('span', { class: 'cw-counter', dir: 'ltr' });
    body.appendChild(h('div', { class: 'cw-controls' },
      reset, h('div', { class: 'cw-dotwrap' }, dots, counter), back, next));

    body.addEventListener('keydown', function (ev) {
      if (ev.target && /^(INPUT|SELECT|TEXTAREA)$/.test(ev.target.tagName)) { return; }
      if (ev.key === 'ArrowRight') { go(cur + 1); ev.preventDefault(); }
      if (ev.key === 'ArrowLeft') { go(cur - 1); ev.preventDefault(); }
    });

    function go(i) {
      if (i < 0 || i >= steps.length || i === cur) { return; }
      var prev = cur;
      cur = i;
      var st = steps[i];
      lineEls.forEach(function (el, k) {
        el.classList.toggle('cw-on', (st.lines || []).indexOf(k) >= 0);
      });
      if (cmds) {   // "# ..." a comment; "|..." printed output, "!..." an error
        clear(cmds);
        (st.code || []).forEach(function (line) {
          var c0 = line.charAt(0);
          var out = c0 === '|' || c0 === '!';
          cmds.appendChild(h('span', { class: 'cw-line' +
                                       (out ? ' cw-output' + (c0 === '!' ? ' cw-bad-text' : '') : ' cw-on') +
                                       (/^\s*#/.test(line) ? ' cw-comment' : '') },
                             out ? line.slice(1) : line));
        });
      }
      clear(caption);
      append(caption, rich(st.caption || ''));
      render(stage, st, i, prev);
      back.disabled = i === 0;
      next.disabled = i === steps.length - 1;
      dotEls.forEach(function (d, k) {
        d.classList.toggle('cw-done', k <= i);
        if (k === i) { d.setAttribute('aria-current', 'step'); }
        else { d.removeAttribute('aria-current'); }
      });
      counter.textContent = (i + 1) + ' / ' + steps.length;
    }
    go(data.start || 0);
    return { go: go };
  }

  /* ------------------------------------------------------------------ */
  /* 4. Registry and mounting                                            */
  /* ------------------------------------------------------------------ */

  var registry = {};
  function register(name, fn) { registry[name] = fn; }

  var api = { core: core, h: h, s: s, rich: rich, frame: frame, stepper: stepper,
              button: button, cell: cell, errorBox: errorBox, clear: clear };

  function mount(el) {
    if (el.classList.contains('cw-ready')) { return; }
    var fn = registry[el.getAttribute('data-widget')];
    if (!fn) { return; }
    var data;
    try {
      data = JSON.parse(el.getAttribute('data-cfs') || '{}');
    } catch (e) {
      if (global.console) { global.console.error('cfs-widgets: bad data-cfs', e); }
      return;       // the Hebrew fallback text stays on the page
    }
    try {
      fn(el, data, api);
    } catch (e2) {
      if (global.console) { global.console.error('cfs-widgets:', e2); }
    }
  }

  function mountAll() {
    var els = document.querySelectorAll('.cfs-widget[data-widget]');
    for (var i = 0; i < els.length; i++) { mount(els[i]); }
  }

  /* ------------------------------------------------------------------ */
  /* 5. The widgets                                                      */
  /* ------------------------------------------------------------------ */

  /* 7.4 -- one-dimensional slicing: y[start:stop:step] */
  register('slice1d', function (root, d) {
    var body = frame(root, d);
    var n = d.values.length;
    var dec = d.decimals === undefined ? 1 : d.decimals;
    var init = (d.init || '2:8:2').split(':');
    var fields = ['start', 'stop', 'step'].map(function (lbl, k) {
      return labelledInput(lbl, init[k] || '', update, 4);
    });
    body.appendChild(h('div', { class: 'cw-expr', dir: 'ltr' },
      h('span', { class: 'cw-code' }, d.name + '['), fields[0].el,
      h('span', { class: 'cw-code' }, ':'), fields[1].el,
      h('span', { class: 'cw-code' }, ':'), fields[2].el,
      h('span', { class: 'cw-code' }, ']')));
    if (d.presets) {
      body.appendChild(h('div', { class: 'cw-chips', role: 'group', 'aria-label': 'דוגמאות' },
        d.presets.map(function (p) {
          return codeButton(d.name + '[' + p + ']', function () {
            var parts = p.split(':');
            fields.forEach(function (f, k) { f.input.value = parts[k] || ''; });
            update();
          });
        })));
    }
    var cells = [];
    var strip = h('div', { class: 'cw-strip' });
    d.values.forEach(function (v, i) {
      var c = cell(fmt(v, dec));
      cells.push(c);
      strip.appendChild(h('div', { class: 'cw-unit' },
        h('span', { class: 'cw-idx' }, String(i)), c,
        h('span', { class: 'cw-nidx' }, String(i - n))));
    });
    body.appendChild(strip);
    balance(strip, n, 42);
    body.appendChild(h('div', { class: 'cw-legend' },
      h('span', { class: 'cw-key-idx' }, 'above: index'), '   ',
      h('span', { class: 'cw-key-nidx' }, 'below: index from the end')));
    var out = h('div', { class: 'cw-out', 'aria-live': 'polite' });
    body.appendChild(out);

    function update() {
      clear(out);
      var parts;
      var idx;
      try {
        parts = fields.map(function (f) { return parseNumber(f.input.value, true); });
        idx = sliceIndices(n, parts[0], parts[1], parts[2]);
      } catch (e) {
        cells.forEach(function (c) { c.classList.remove('cw-sel'); });
        out.appendChild(errorBox(e));
        return;
      }
      var chosen = {};
      idx.forEach(function (i) { chosen[i] = true; });
      cells.forEach(function (c, i) { c.classList.toggle('cw-sel', !!chosen[i]); });
      var expr = d.name + '[' + sliceText({ start: parts[0], stop: parts[1], step: parts[2] }) + ']';
      out.appendChild(h('div', { class: 'cw-line-out' },
        h('code', { class: 'cw-chip' }, expr),
        h('span', { class: 'cw-muted cw-mono' },
          idx.length ? '  indices ' + idx.join(', ') : '  no index')));
      if (idx.length) {
        out.appendChild(h('div', { class: 'cw-strip cw-result' },
          idx.map(function (i) { return cell(fmt(d.values[i], dec), 'cw-res'); })));
      }
      out.appendChild(h('div', { class: 'cw-muted cw-mono' },
        idx.length ? 'len ' + idx.length + ', shape ' + pyShape([idx.length])
                   : 'an empty array, shape (0,)'));
    }
    update();
  });

  /* 7.8 -- a boolean mask with a threshold: mask = y > h */
  register('mask', function (root, d) {
    var body = frame(root, d);
    var dec = d.decimals === undefined ? 2 : d.decimals;
    var op = d.ops[0];
    var hv = d.h.value;
    var ops = toggleGroup(d.ops.map(function (o) { return { label: o, value: o, code: true }; }),
                          'השוואה', function (v) { op = v; update(); });
    var hText = h('span', { class: 'cw-code' });
    var range = h('input', { type: 'range', class: 'cw-range', min: d.h.min, max: d.h.max,
                             step: d.h.step, value: hv, 'aria-label': 'h',
                             oninput: function () { hv = Number(range.value); update(); } });
    body.appendChild(h('div', { class: 'cw-expr cw-wrap', dir: 'ltr' },
      h('span', { class: 'cw-code' }, 'mask = ' + d.name), ops,
      h('label', { class: 'cw-slider' }, hText, range)));
    var code = h('div', { class: 'cw-line-out' });
    body.appendChild(code);
    var units = [];
    var strip = h('div', { class: 'cw-strip' });
    d.values.forEach(function (v, i) {
      var c = cell(fmt(v, dec));
      var m = h('span', { class: 'cw-flag' });
      units.push({ c: c, m: m });
      strip.appendChild(h('div', { class: 'cw-unit' },
        h('span', { class: 'cw-idx cw-idx-small' }, String(i)), c, m));
    });
    body.appendChild(strip);
    balance(strip, d.values.length, 46);
    var out = h('div', { class: 'cw-out', 'aria-live': 'polite' });
    body.appendChild(out);

    function update() {
      hText.textContent = 'h = ' + hv;
      clear(code);
      code.appendChild(h('code', { class: 'cw-chip' }, 'mask = ' + d.name + ' ' + op + ' ' + hv));
      var kept = [];
      d.values.forEach(function (v, i) {
        var t = op === '>' ? v > hv : op === '>=' ? v >= hv : op === '<' ? v < hv : v <= hv;
        units[i].c.classList.toggle('cw-sel', t);
        units[i].m.textContent = t ? 'True' : 'False';
        units[i].m.classList.toggle('cw-true', t);
        if (t) { kept.push(v); }
      });
      clear(out);
      out.appendChild(h('div', { class: 'cw-facts cw-mono' },
        h('span', {}, 'mask.sum() → ', h('b', {}, String(kept.length))),
        h('span', {}, 'np.any(mask) → ', h('b', {}, kept.length > 0 ? 'True' : 'False')),
        h('span', {}, 'np.all(mask) → ',
          h('b', {}, kept.length === d.values.length ? 'True' : 'False'))));
      out.appendChild(h('div', { class: 'cw-muted cw-mono' },
        d.name + '[mask]: ' + kept.length + ' values, shape ' + pyShape([kept.length])));
      if (kept.length) {
        out.appendChild(h('div', { class: 'cw-strip cw-result cw-compact' },
          kept.map(function (v) { return cell(fmt(v, dec), 'cw-res'); })));
      }
    }
    ops.pick(op);
    update();
  });

  /* Shorten a long list of positions: first 6, ..., last (as the figures do). */
  function shortList(list) {
    if (list.length <= 8) { return list.slice(); }
    return list.slice(0, 6).concat(['…', list[list.length - 1]]);
  }

  /* 9.2 -- slicing a 2-D array by axes: Y[row, col] */
  register('slice2d', function (root, d) {
    var body = frame(root, d);
    var R = d.shape[0];
    var C = d.shape[1];
    var dec = d.decimals === undefined ? 1 : d.decimals;
    var shown = d.cols;                 // the columns drawn, e.g. 0..5 and 59
    var init = d.init || ['1', ''];
    var fr = labelledInput('axis 0', init[0], update, 4);
    var fc = labelledInput('axis 1', init[1], update, 4);
    body.appendChild(h('div', { class: 'cw-expr', dir: 'ltr' },
      h('span', { class: 'cw-code' }, d.name + '['), fr.el,
      h('span', { class: 'cw-code' }, ','), fc.el,
      h('span', { class: 'cw-code' }, ']')));
    if (d.presets) {
      body.appendChild(h('div', { class: 'cw-chips', role: 'group', 'aria-label': 'דוגמאות' },
        d.presets.map(function (p) {
          var label = d.name + '[' + p[0] + (p[1] ? ', ' + p[1] : '') + ']';
          return codeButton(label, function () {
            fr.input.value = p[0];
            fc.input.value = p[1];
            update();
          });
        })));
    }
    /* the grid: header row of column indices, one row per run */
    var gridCols = [];
    shown.forEach(function (j, k) {
      if (k > 0 && j !== shown[k - 1] + 1) { gridCols.push({ gap: [shown[k - 1] + 1, j - 1] }); }
      gridCols.push({ j: j });
    });
    var grid = h('div', { class: 'cw-grid' });
    grid.style.gridTemplateColumns = 'auto repeat(' + gridCols.length + ', auto)';
    grid.appendChild(h('span', { class: 'cw-axis-note cw-ax0-text' }, 'axis 0 ↓'));
    gridCols.forEach(function (gc) {
      grid.appendChild(h('span', { class: 'cw-head-cell cw-ax1-text' },
                         gc.gap ? '…' : String(gc.j)));
    });
    var cellsAt = [];
    for (var i = 0; i < R; i++) {
      grid.appendChild(h('span', { class: 'cw-row-label cw-ax0-text' }, String(i)));
      var row = [];
      gridCols.forEach(function (gc) {
        var c = cell(gc.gap ? '…' : fmt(d.values[i][gc.j], dec), gc.gap ? 'cw-gapcell' : '');
        row.push({ c: c, gc: gc });
        grid.appendChild(c);
      });
      cellsAt.push(row);
    }
    body.appendChild(h('div', { class: 'cw-scroll' },
      h('div', { class: 'cw-axis-top cw-ax1-text' }, 'axis 1: ' + (d.colLabel || 'time') + ' →'),
      grid));
    var out = h('div', { class: 'cw-out', 'aria-live': 'polite' });
    body.appendChild(out);

    function describe(sel, n, word, plural, at) {
      if (!sel.keep) { return at + sel.indices[0]; }
      if (sel.indices.length === n && sel.indices.every(function (v, k) { return v === k; })) {
        return 'every ' + word;
      }
      if (!sel.indices.length) { return 'no ' + plural; }
      return plural + ' ' + shortList(sel.indices).join(', ');
    }

    function update() {
      clear(out);
      var rIx;
      var cIx;
      var rs;
      var cs;
      try {
        rIx = parseIndex(fr.input.value);
        cIx = parseIndex(fc.input.value);
        if (rIx === null) { throw pyError('hint', 'כתבו אינדקס או פריסה בציר 0, למשל `1` או `:`.'); }
        rs = indexAxis(rIx, R, 0);
        cs = indexAxis(cIx, C, 1);
      } catch (e) {
        cellsAt.forEach(function (row) { row.forEach(function (x) { x.c.classList.remove('cw-sel'); }); });
        out.appendChild(errorBox(e));
        return;
      }
      var colSet = {};
      cs.indices.forEach(function (j) { colSet[j] = true; });
      var rowSet = {};
      rs.indices.forEach(function (i) { rowSet[i] = true; });
      cellsAt.forEach(function (row, i) {
        row.forEach(function (x) {
          var on = false;
          if (rowSet[i]) {
            if (x.gc.gap) {
              for (var j = x.gc.gap[0]; j <= x.gc.gap[1]; j++) { if (colSet[j]) { on = true; break; } }
            } else {
              on = !!colSet[x.gc.j];
            }
          }
          x.c.classList.toggle('cw-sel', on);
        });
      });
      var shape = [];
      if (rs.keep) { shape.push(rs.indices.length); }
      if (cs.keep) { shape.push(cs.indices.length); }
      var expr = d.name + '[' + indexText(rIx) + ', ' + indexText(cIx) + ']';
      var line = h('div', { class: 'cw-line-out' }, h('code', { class: 'cw-chip' }, expr));
      if (cIx === null || (cIx.kind === 'slice' && cIx.start === null &&
                           cIx.stop === null && cIx.step === null)) {
        line.appendChild(h('span', { class: 'cw-muted cw-mono' },
                           '  same as ' + d.name + '[' + indexText(rIx) + ']'));
      }
      out.appendChild(line);
      var desc = describe(rs, R, d.rowLabel || 'run', (d.rowLabel || 'run') + 's', (d.rowLabel || 'run') + ' ') +
                 ', ' + describe(cs, C, d.colLabel || 'time', (d.colLabel || 'time') + 's', 'at ' + (d.colLabel || 'time') + ' ');
      var empty = shape.indexOf(0) >= 0;
      if (shape.length === 0) {
        out.appendChild(h('div', { class: 'cw-strip cw-result' },
          cell(fmt(d.values[rs.indices[0]][cs.indices[0]], dec), 'cw-res')));
        out.appendChild(h('div', { class: 'cw-res-text cw-mono' }, 'one number: ' + desc));
        return;
      }
      if (!empty && shape.length === 1) {       // a 1-D result prints as a row
        var list = rs.keep ? rs.indices.map(function (ri) { return [ri, cs.indices[0]]; })
                           : cs.indices.map(function (cj) { return [rs.indices[0], cj]; });
        out.appendChild(h('div', { class: 'cw-strip cw-result' },
          shortList(list).map(function (rc) {
            return cell(rc === '…' ? '…' : fmt(d.values[rc[0]][rc[1]], dec), 'cw-res');
          })));
      } else if (!empty) {
        var colsShown = shortList(cs.indices);
        var res = h('div', { class: 'cw-grid cw-result-grid' });
        res.style.gridTemplateColumns = 'repeat(' + colsShown.length + ', auto)';
        rs.indices.forEach(function (ri) {
          colsShown.forEach(function (cj) {
            res.appendChild(cell(cj === '…' ? '…' : fmt(d.values[ri][cj], dec), 'cw-res'));
          });
        });
        out.appendChild(h('div', { class: 'cw-scroll' }, res));
      }
      out.appendChild(h('div', { class: 'cw-res-text cw-mono' },
        'shape ' + pyShape(shape) + ': ' + desc));
    }
    update();
  });

  /* 9.6 -- reductions along an axis: Ys.mean(axis=0) */
  register('axis', function (root, d) {
    var body = frame(root, d);
    var dec = d.decimals === undefined ? 1 : d.decimals;
    var R = d.values.length;
    var C = d.values[0].length;
    var op = (d.init && d.init.op) || d.ops[0];
    var axis = d.init && d.init.axis !== undefined ? d.init.axis : 0;
    var opG = toggleGroup(d.ops.map(function (o) { return { label: o, value: o, code: true }; }),
                          'פעולה', function (v) { op = v; update(); });
    var axG = toggleGroup([{ label: 'axis=0', value: 0, code: true },
                           { label: 'axis=1', value: 1, code: true },
                           { label: 'no axis', value: null, code: true }],
                          'ציר', function (v) { axis = v; update(); });
    body.appendChild(h('div', { class: 'cw-expr cw-wrap', dir: 'ltr' }, opG, axG));
    if (d.def) { body.appendChild(h('div', { class: 'cw-muted cw-mono cw-def' }, d.def)); }
    var code = h('div', { class: 'cw-line-out' });
    body.appendChild(code);
    var grid = h('div', { class: 'cw-grid cw-axis-grid' });
    grid.style.gridTemplateColumns = 'auto repeat(' + C + ', auto) auto';
    grid.appendChild(h('span', {}));
    d.colLabels.forEach(function (l) { grid.appendChild(h('span', { class: 'cw-head-cell cw-ax1-text' }, l)); });
    var colRes = h('span', { class: 'cw-head-cell cw-res-text' });
    grid.appendChild(colRes);
    var cells = [];
    var rowOut = [];
    d.values.forEach(function (row, i) {
      grid.appendChild(h('span', { class: 'cw-row-label cw-ax0-text' }, d.rowLabels[i]));
      cells.push(row.map(function (v) { var c = cell(fmt(v, dec)); grid.appendChild(c); return c; }));
      var o = cell('', 'cw-res cw-slot');
      rowOut.push(o);
      grid.appendChild(o);
    });
    /* arrows and the result row under the grid (axis=0) */
    grid.appendChild(h('span', {}));
    var arrows = [];
    for (var j = 0; j < C; j++) {
      var a = h('span', { class: 'cw-arrow cw-ax0-text', 'aria-hidden': 'true' }, '↓');
      arrows.push(a);
      grid.appendChild(a);
    }
    grid.appendChild(h('span', {}));
    var rowLabelOut = h('span', { class: 'cw-row-label cw-res-text' });
    grid.appendChild(rowLabelOut);
    var colOut = [];
    for (j = 0; j < C; j++) {
      var o2 = cell('', 'cw-res cw-slot');
      colOut.push(o2);
      grid.appendChild(o2);
    }
    var corner = cell('', 'cw-res cw-slot');      // no axis: everything in one cell
    grid.appendChild(corner);
    body.appendChild(h('div', { class: 'cw-scroll' },
      h('div', { class: 'cw-axis-top cw-ax1-text' }, 'axis 1: time →'), grid));
    var note = h('div', { class: 'cw-res-text cw-mono', 'aria-live': 'polite' });
    body.appendChild(note);

    function update() {
      var r = reduce(d.values, op, axis);
      clear(code);
      var expr = d.name + '.' + op + '(' + (axis === null ? '' : 'axis=' + axis) + ')';
      code.appendChild(h('code', { class: 'cw-chip' }, expr));
      code.appendChild(h('span', { class: 'cw-muted cw-mono' },
        '  shape ' + pyShape([R, C]) + ' → ' + pyShape(r.shape)));
      arrows.forEach(function (a) { a.classList.toggle('cw-on', axis === 0); });
      cells.forEach(function (row) {
        row.forEach(function (c) {
          c.classList.toggle('cw-ax0-fill', axis === 0);
          c.classList.toggle('cw-ax1-fill', axis === 1);
          c.classList.toggle('cw-all-fill', axis === null);
        });
      });
      rowOut.forEach(function (o, i) {
        o.textContent = axis === 1 ? fmt(r.values[i], dec) : '';
        o.classList.toggle('cw-on', axis === 1);
      });
      colOut.forEach(function (o, k) {
        o.textContent = axis === 0 ? fmt(r.values[k], dec) : '';
        o.classList.toggle('cw-on', axis === 0);
      });
      rowLabelOut.textContent = axis === 0 ? op : '';
      corner.textContent = axis === null ? fmt(r.values[0], dec) : '';
      corner.classList.toggle('cw-on', axis === null);
      colRes.textContent = axis === 1 ? op : axis === null ? op + '()' : '';
      var what = { mean: 'mean', std: 'standard deviation', max: 'maximum', sum: 'sum' }[op] || op;
      note.textContent = axis === 0 ? 'axis 0 (run) disappears: one ' + what + ' per time' :
                         axis === 1 ? 'axis 1 (time) disappears: one ' + what + ' per run' :
                         'no axis: one number from all ' + (R * C) + ' values';
    }
    opG.pick(op);
    axG.pick(axis);
    update();
  });

  /* 9.5 -- broadcasting two shapes, or NumPy's error */
  register('broadcast', function (root, d) {
    var body = frame(root, d);
    var pick = 0;
    var chips = h('div', { class: 'cw-chips', role: 'group', 'aria-label': 'זוגות' });
    var chipEls = d.pairs.map(function (p, k) {
      var b = codeButton(p.expr, function () { pick = k; update(); });
      b.setAttribute('aria-pressed', 'false');
      chips.appendChild(b);
      return b;
    });
    body.appendChild(chips);
    var out = h('div', { class: 'cw-out', 'aria-live': 'polite' });
    body.appendChild(out);

    /* columns drawn for an axis of size c: all up to 5, else 4 and "..." */
    function drawnCols(c) { return c <= 5 ? { n: c, more: false } : { n: 4, more: true }; }

    /* An operand drawn at the result's shape (or its own, when target is
       null). A 1-D operand is a row. Cells repeated along an axis of size 1
       are dashed; values[i][j] holds the operand's own drawn cells. */
    function block(opnd, target, cls) {
      var sh = opnd.shape.length === 1 ? [1, opnd.shape[0]] : opnd.shape;
      var tr = target ? target[0] : sh[0];
      var dc = drawnCols(target ? target[1] : sh[1]);
      var g = h('div', { class: 'cw-grid cw-bgrid' });
      g.style.gridTemplateColumns = 'repeat(' + (dc.n + (dc.more ? 1 : 0)) + ', auto)';
      for (var i = 0; i < tr; i++) {
        var realRow = sh[0] !== 1 || i === 0;
        for (var j = 0; j < dc.n + (dc.more ? 1 : 0); j++) {
          var txt;
          var real;
          if (j === dc.n) {                       // the "..." column
            txt = '…';
            real = realRow && sh[1] !== 1;
          } else {
            txt = opnd.values[sh[0] === 1 ? 0 : i][sh[1] === 1 ? 0 : j];
            real = realRow && (sh[1] !== 1 || j === 0);
          }
          g.appendChild(cell(txt, cls + (real ? '' : ' cw-stretched')));
        }
      }
      return g;
    }

    function update() {
      chipEls.forEach(function (b, k) { b.setAttribute('aria-pressed', String(k === pick)); });
      clear(out);
      var p = d.pairs[pick];
      var A = d.operands[p.a];
      var B = d.operands[p.b];
      var res = broadcast(A.shape, B.shape);
      /* the rule, from the right: a table of sizes */
      var n = res.pairs.length;
      var t = h('div', { class: 'cw-rule' });
      t.style.gridTemplateColumns = 'auto auto repeat(' + n + ', 3.2em)';
      function rowOf(label, shape, key, padKey, cls) {
        t.appendChild(h('span', { class: 'cw-rule-name ' + cls }, label));
        t.appendChild(h('span', { class: 'cw-rule-shape cw-muted' }, pyShape(shape)));
        res.pairs.forEach(function (pr, k) {
          var bad = !pr.ok;
          t.appendChild(h('span', { class: 'cw-rule-size' + (pr[padKey] ? ' cw-padded' : '') +
                                    (bad ? ' cw-bad-text' : '') },
                          pr[padKey] ? '(1)' : String(pr[key])));
        });
      }
      rowOf(p.a, A.shape, 'a', 'padA', 'cw-ax0-text');
      rowOf(p.b, B.shape, 'b', 'padB', 'cw-ax1-text');
      t.appendChild(h('span', {}));
      t.appendChild(h('span', {}));
      res.pairs.forEach(function (pr) {
        t.appendChild(h('span', { class: 'cw-rule-size ' + (pr.ok ? 'cw-res-text' : 'cw-bad-text') },
                        pr.ok ? '✓' : '✗'));
      });
      if (res.ok) {
        t.appendChild(h('span', { class: 'cw-rule-name cw-res-text' }, 'result'));
        t.appendChild(h('span', { class: 'cw-rule-shape cw-res-text' }, pyShape(res.shape)));
        res.shape.forEach(function (v) { t.appendChild(h('span', { class: 'cw-rule-size cw-res-text' }, String(v))); });
      }
      out.appendChild(h('div', { class: 'cw-line-out' }, h('code', { class: 'cw-chip' }, p.expr)));
      out.appendChild(h('div', { class: 'cw-scroll' }, h('div', { class: 'cw-muted cw-small', dir: 'ltr' },
        'compared from the right; a missing axis counts as (1)'), t));
      if (!res.ok) {
        var bad = res.pairs[res.failed];
        out.appendChild(errorBox(pyError('ValueError', res.error)));
        out.appendChild(h('div', { class: 'cw-note', dir: 'rtl' },
          rich('מימין לשמאל: `' + bad.a + '` מול `' + bad.b + '`. הגדלים שונים, ואף אחד מהם אינו 1.')));
        out.appendChild(h('div', { class: 'cw-blocks' },
          h('div', { class: 'cw-block' }, h('div', { class: 'cw-block-title cw-ax0-text' }, p.a + '  ' + pyShape(A.shape)), block(A, null, 'cw-a')),
          h('div', { class: 'cw-block' }, h('div', { class: 'cw-block-title cw-ax1-text' }, p.b + '  ' + pyShape(B.shape)), block(B, null, 'cw-b'))));
        return;
      }
      var target = res.shape.length === 1 ? [1, res.shape[0]] : res.shape;
      function path(shape) {
        var steps = [pyShape(shape)];
        if (shape.length < res.shape.length) {
          var padded = [];
          for (var k = 0; k < res.shape.length - shape.length; k++) { padded.push(1); }
          steps.push(pyShape(padded.concat(shape)));
        }
        if (pyShape(res.shape) !== steps[steps.length - 1]) { steps.push(pyShape(res.shape)); }
        return steps.join(' → ');
      }
      var resGrid = h('div', { class: 'cw-grid cw-bgrid' });
      var rdc = drawnCols(target[1]);
      resGrid.style.gridTemplateColumns = 'repeat(' + (rdc.n + (rdc.more ? 1 : 0)) +
                                          ', auto)';
      p.result.forEach(function (row) { row.forEach(function (v) { resGrid.appendChild(cell(v, 'cw-res')); }); });
      out.appendChild(h('div', { class: 'cw-blocks' },
        h('div', { class: 'cw-block' }, h('div', { class: 'cw-block-title cw-ax0-text' }, p.a),
          block(A, target, 'cw-a'), h('div', { class: 'cw-muted cw-small' }, path(A.shape))),
        h('div', { class: 'cw-block' }, h('div', { class: 'cw-block-title cw-ax1-text' }, p.b),
          block(B, target, 'cw-b'), h('div', { class: 'cw-muted cw-small' }, path(B.shape))),
        h('div', { class: 'cw-block' }, h('div', { class: 'cw-block-title cw-res-text' }, 'result'),
          resGrid, h('div', { class: 'cw-res-text cw-small' }, 'shape ' + pyShape(res.shape)))));
      out.appendChild(h('div', { class: 'cw-muted cw-small', dir: 'ltr' },
        'dashed cells: values repeated along an axis of size 1'));
    }
    update();
  });

  /* 10.3 -- the update loop fills one column per round */
  register('loopgrid', function (root, d) {
    var sel = d.selectRow === undefined ? 1 : d.selectRow;
    var grid = null;
    var cellsAt = [];
    var heads = [];
    var rowBtns = [];
    var formula = h('pre', { class: 'cw-formula', dir: 'ltr', 'aria-live': 'polite' });
    var current = null;

    function build(stage) {
      grid = h('div', { class: 'cw-grid cw-loop-grid' });
      grid.style.gridTemplateColumns = 'auto repeat(' + d.colLabels.length + ', auto)';
      grid.appendChild(h('span', { class: 'cw-axis-note cw-ax0-text' }, d.rowAxis || 'axis 0'));
      d.colLabels.forEach(function (l) {
        var hc = h('span', { class: 'cw-head-cell cw-ax1-text' }, l);
        heads.push(hc);
        grid.appendChild(hc);
      });
      d.rowLabels.forEach(function (l, i) {
        var b = h('button', { type: 'button', class: 'cw-row-btn cw-ax0-text', 'aria-pressed': String(i === sel),
                              onclick: function () { sel = i; refreshRows(); showFormula(); } }, l);
        rowBtns.push(b);
        grid.appendChild(b);
        cellsAt.push(d.colLabels.map(function (lab) {
          var c = cell('', lab === '…' ? 'cw-gapcell' : '');
          grid.appendChild(c);
          return c;
        }));
      });
      stage.appendChild(h('div', { class: 'cw-scroll' },
        h('div', { class: 'cw-axis-top cw-ax1-text' }, d.colAxis || 'axis 1 →'), grid));
      stage.appendChild(h('div', { class: 'cw-muted cw-small', dir: 'rtl' },
        rich(d.rowHint || 'לחצו על שורה כדי לראות את החישוב שלה.')));
      stage.appendChild(formula);
    }
    function refreshRows() {
      rowBtns.forEach(function (b, i) { b.setAttribute('aria-pressed', String(i === sel)); });
    }
    function showFormula() {
      clear(formula);
      if (!current) { return; }
      var lines = current.formulas ? current.formulas[sel] : current.formula;
      append(formula, (lines || []).join('\n'));
    }
    stepper(root, d, function (stage, st) {
      if (!grid) { build(stage); }
      current = st;
      d.values.forEach(function (row, i) {
        row.forEach(function (v, j) {
          var filled = j < st.filled || (st.alsoFilled || []).indexOf(j) >= 0;
          var c = cellsAt[i][j];
          c.textContent = filled ? v : d.empty[j];
          c.classList.toggle('cw-faded', !filled);
          c.classList.toggle('cw-res', st.hl === j);
          c.classList.toggle('cw-src', st.src === j);
        });
      });
      heads.forEach(function (hc, j) { hc.classList.toggle('cw-res-text', st.hl === j); });
      showFormula();
    });
  });

  /* 13.4 -- commits, branches and HEAD, drawn as in the figure */
  register('gitgraph', function (root, d) {
    var W = d.width || 420;
    var H = d.height || 150;
    var fileBox = null;
    var svg = null;
    var prevNodes = {};
    function colour(c) { return 'var(--cw-' + c + ')'; }
    stepper(root, d, function (stage, st) {
      if (!svg) {
        svg = s('svg', { viewBox: '0 0 ' + W + ' ' + H, class: 'cw-svg', role: 'img' });
        stage.appendChild(svg);
        fileBox = h('div', { class: 'cw-file' });
        stage.appendChild(fileBox);
      }
      while (svg.firstChild) { svg.removeChild(svg.firstChild); }
      svg.setAttribute('aria-label', st.alt || '');
      var nodes = {};
      d.nodes.forEach(function (nd) { nodes[nd.id] = nd; });
      (st.refs || []).forEach(function (rf) {     // connectors go under the circles
        if (!rf.link) { return; }
        var nd = nodes[rf.node];
        svg.appendChild(s('line', { x1: nd.x, y1: nd.y, x2: nd.x + (rf.dx === undefined ? 16 : rf.dx),
                                    y2: nd.y + (rf.dy || 0), stroke: colour(rf.color || 'ax0'),
                                    'stroke-width': 1.5 }));
      });
      (st.edges || []).forEach(function (e) {
        var a = nodes[e[0]];
        var b = nodes[e[1]];
        svg.appendChild(s('line', { x1: a.x, y1: a.y, x2: b.x, y2: b.y, class: 'cw-edge' +
                                    (prevNodes[e[1]] ? '' : ' cw-new') }));
      });
      var now = {};
      (st.nodes || []).forEach(function (sn) {
        var nd = nodes[sn.id];
        var c = sn.color || nd.color;
        now[sn.id] = true;
        var g = s('g', { class: prevNodes[sn.id] ? '' : 'cw-new' });
        g.appendChild(s('circle', { cx: nd.x, cy: nd.y, r: 11, fill: colour(c + '-fill'),
                                    stroke: colour(c), 'stroke-width': 2.5 }));
        var lab = sn.label || nd.label;
        if (lab) {
          var below = nd.labelBelow;
          g.appendChild(s('text', { x: nd.x, y: below ? nd.y + 30 : nd.y - 19, 'text-anchor': 'middle',
                                    fill: colour(sn.labelColor || c) }, lab));
        }
        svg.appendChild(g);
      });
      (st.refs || []).forEach(function (rf) {
        var nd = nodes[rf.node];
        var x = nd.x + (rf.dx === undefined ? 16 : rf.dx);
        var y = nd.y + (rf.dy || 0);
        var c = rf.color || 'ax0';
        var g = s('g', { class: 'cw-ref' });
        var rect = s('rect', { x: x, y: y - 10, rx: 4, height: 20, width: 10,
                               fill: colour(rf.fill || 'page'), stroke: colour(c), 'stroke-width': 1.5 });
        var txt = s('text', { x: x + 6, y: y + 4, fill: colour(c) }, rf.text);
        g.appendChild(rect);
        g.appendChild(txt);
        svg.appendChild(g);
        var w = 0;
        try { w = txt.getBBox().width; } catch (e) { w = 0; }
        rect.setAttribute('width', (w > 0 ? w : rf.text.length * 7.3) + 12);
      });
      prevNodes = now;
      clear(fileBox);
      if (st.file) {
        fileBox.appendChild(h('div', { class: 'cw-file-name cw-mono' }, st.fileName || d.fileName || ''));
        var pre = h('pre', { class: 'cw-file-text', dir: 'ltr' });
        st.file.forEach(function (line) {
          var cls = /^(<<<<<<<|=======|>>>>>>>)/.test(line) ? 'cw-bad-text' : '';
          if (line.charAt(0) === '+') { cls = 'cw-res-text'; line = line.slice(1); }
          pre.appendChild(h('span', { class: 'cw-line ' + cls }, line));
        });
        fileBox.appendChild(pre);
      }
    });
  });

  /* ------------------------------------------------------------------ */

  /* ---------------------------- weeks 4-6 ---------------------------- */

  var markerCount = 0;
  /* An arrowhead marker inside this svg; returns its url(#id). */
  function arrowMarker(svg, cls) {
    var id = 'cw-arrow-' + (++markerCount);
    var defs = svg.querySelector('defs') || svg.appendChild(s('defs', {}));
    var m = s('marker', { id: id, viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7,
                          markerHeight: 7, orient: 'auto-start-reverse' });
    m.appendChild(s('path', { d: 'M0,0 L10,5 L0,10 z', class: cls }));
    defs.appendChild(m);
    return 'url(#' + id + ')';
  }

  /* range values on a number line: chosen numbers violet, stop hollow red */
  function numberLine(box, call, r) {
    var lo = Math.min(call.start, call.stop);
    var hi = Math.max(call.start, call.stop);
    if (hi - lo > 30 || r.cut) {
      box.appendChild(h('div', { class: 'cw-muted cw-small', dir: 'rtl' },
                        rich('ציר המספרים מוצג לטווחים של עד 30 מספרים.')));
      return;
    }
    var W = 340;
    var y = 46;
    var sp = hi > lo ? Math.min(40, 296 / (hi - lo)) : 0;
    var x0 = (W - sp * (hi - lo)) / 2;
    function X(v) { return x0 + (v - lo) * sp; }
    var svg = s('svg', { viewBox: '0 0 ' + W + ' 104', class: 'cw-svg cw-numsvg', role: 'img',
                         'aria-label': 'list(' + call.text + ') on the number line' });
    var mk = arrowMarker(svg, 'cw-mark-sel');
    svg.appendChild(s('line', { x1: X(lo) - 14, y1: y, x2: X(hi) + 14, y2: y, class: 'cw-axisline' }));
    var chosen = {};
    r.values.forEach(function (v) { chosen[v] = true; });
    var every = sp >= 15 ? 1 : sp >= 9 ? 2 : 5;
    for (var v = lo; v <= hi; v++) {
      svg.appendChild(s('line', { x1: X(v), y1: y - 4, x2: X(v), y2: y + 4, class: 'cw-tick' }));
      var show = (v - lo) % every === 0 || v === call.start || v === call.stop ||
                 (chosen[v] && sp >= 12);
      if (show) {
        svg.appendChild(s('text', { x: X(v), y: y + 22, 'text-anchor': 'middle',
                                    class: chosen[v] ? 'cw-t-sel' : 'cw-t-muted' }, String(v)));
      }
    }
    if (r.values.length >= 2 && r.values.length <= 16) {      // one arc per step
      for (var k = 0; k + 1 < r.values.length; k++) {
        var x1 = X(r.values[k]);
        var x2 = X(r.values[k + 1]);
        var top = y - 10 - Math.min(24, Math.abs(x2 - x1) * 0.45 + 4);
        svg.appendChild(s('path', { d: 'M' + x1 + ',' + (y - 9) + ' Q' + ((x1 + x2) / 2) + ',' + top +
                                       ' ' + x2 + ',' + (y - 9), class: 'cw-arc', 'marker-end': mk }));
      }
    }
    svg.appendChild(s('circle', { cx: X(call.stop), cy: y, r: 6, class: 'cw-stopdot' }));
    r.values.forEach(function (val) {
      svg.appendChild(s('circle', { cx: X(val), cy: y, r: 6, class: 'cw-ondot' }));
    });
    if (call.start === call.stop) {
      svg.appendChild(s('text', { x: X(call.start), y: y + 42, 'text-anchor': 'middle',
                                  class: 'cw-t-bad' }, 'start = stop'));
    } else {
      svg.appendChild(s('text', { x: X(call.start), y: y + 42, 'text-anchor': 'middle',
                                  class: 'cw-t-muted' }, 'start'));
      svg.appendChild(s('text', { x: X(call.stop), y: y + 42, 'text-anchor': 'middle',
                                  class: 'cw-t-bad' }, 'stop'));
    }
    box.appendChild(svg);
  }

  /* 6.1 -- range(start, stop, step) on a number line */
  register('range1d', function (root, d) {
    var body = frame(root, d);
    var init = d.init || ['3', '10', '2'];
    var fields = ['start', 'stop', 'step'].map(function (lbl, k) {
      return labelledInput(lbl, init[k] || '', update, 4);
    });
    body.appendChild(h('div', { class: 'cw-expr', dir: 'ltr' },
      h('span', { class: 'cw-code' }, 'range('), fields[0].el,
      h('span', { class: 'cw-code' }, ','), fields[1].el,
      h('span', { class: 'cw-code' }, ','), fields[2].el,
      h('span', { class: 'cw-code' }, ')')));
    if (d.presets) {
      body.appendChild(h('div', { class: 'cw-chips', role: 'group', 'aria-label': 'דוגמאות' },
        d.presets.map(function (p) {
          return codeButton(rangeCall(p[0], p[1], p[2]).text, function () {
            fields.forEach(function (f, k) { f.input.value = p[k]; });
            update();
          });
        })));
    }
    var line = h('div', { class: 'cw-numline' });
    var out = h('div', { class: 'cw-out', 'aria-live': 'polite' });
    body.appendChild(line);
    body.appendChild(out);

    function update() {
      clear(line);
      clear(out);
      var call;
      var r;
      try {
        call = rangeCall(fields[0].input.value, fields[1].input.value, fields[2].input.value);
        r = rangeValues(call.start, call.stop, call.step, 40);
      } catch (e) {
        out.appendChild(errorBox(e));
        return;
      }
      numberLine(line, call, r);
      out.appendChild(h('div', { class: 'cw-line-out' },
                        h('code', { class: 'cw-chip' }, 'list(' + call.text + ')')));
      if (r.len) {
        var shown = r.cut ? r.values.slice(0, 6).concat(['…', r.last]) : r.values;
        out.appendChild(h('div', { class: 'cw-strip cw-result' }, shown.map(function (v) {
          return cell(String(v), v === '…' ? 'cw-gapcell' : 'cw-res');
        })));
        out.appendChild(h('div', { class: 'cw-muted cw-mono' },
                          'len(' + call.text + ') → ' + r.len));
      } else {
        out.appendChild(h('div', { class: 'cw-note', dir: 'rtl' },
                          rich('טווח ריק: לולאת `for` עליו לא תרוץ אף פעם.')));
      }
    }
    update();
  });

  /* 6.0, 8.2, 12.2 -- a loop step by step: the sequence it walks over (with a
     pointer) or the grid of pairs it visits, the variables, the condition, a
     dict, the printed output. Each part is drawn only if the data has it. */
  function buildLoop(stage, d) {
    var p = {};
    if (d.seq) {
      var g = h('div', { class: 'cw-grid cw-seq' });
      g.style.gridTemplateColumns = 'auto repeat(' + d.seq.items.length + ', auto)';
      g.appendChild(h('span', {}));
      d.seq.items.forEach(function (it, k) {
        g.appendChild(h('span', { class: 'cw-head-cell cw-ax1-text' }, String(k)));
      });
      g.appendChild(h('span', { class: 'cw-row-label' }, d.seq.name));
      p.items = d.seq.items.map(function (it) {
        var c = cell(it, 'cw-big');
        g.appendChild(c);
        return c;
      });
      g.appendChild(h('span', {}));
      p.ptr = d.seq.items.map(function () {
        var c = h('span', { class: 'cw-ptr' });
        g.appendChild(c);
        return c;
      });
      if (d.seq.trace) {
        g.appendChild(h('span', { class: 'cw-row-label cw-res-text' }, d.seq.trace));
        p.trace = d.seq.items.map(function () {
          var c = cell('', 'cw-res cw-slot');
          g.appendChild(c);
          return c;
        });
      }
      stage.appendChild(h('div', { class: 'cw-scroll' }, g));
      if (d.seq.traceNote) {
        stage.appendChild(h('div', { class: 'cw-muted cw-small', dir: 'ltr' }, d.seq.traceNote));
      }
    }
    if (d.grid) {
      var gr = h('div', { class: 'cw-grid cw-pairs' });
      gr.style.gridTemplateColumns = 'auto repeat(' + d.grid.cols.length + ', auto)';
      gr.appendChild(h('span', {}));
      d.grid.cols.forEach(function (c) {
        gr.appendChild(h('span', { class: 'cw-head-cell cw-ax1-text' }, d.grid.colName + ' = ' + c));
      });
      p.pairs = d.grid.rows.map(function (r) {
        gr.appendChild(h('span', { class: 'cw-row-label cw-ax0-text' }, d.grid.rowName + ' = ' + r));
        return d.grid.cols.map(function (c) {
          var el = h('span', { class: 'cw-cell cw-pair' },
                     h('span', {}, '(' + r + ', ' + c + ')'), h('span', { class: 'cw-order' }));
          gr.appendChild(el);
          return el;
        });
      });
      stage.appendChild(h('div', { class: 'cw-scroll' }, gr));
    }
    p.state = h('div', { class: 'cw-state' });
    stage.appendChild(p.state);
    if (d.output) {
      p.out = h('pre', { class: 'cw-listing cw-printed', dir: 'ltr', 'aria-live': 'polite' });
      stage.appendChild(h('div', { class: 'cw-muted cw-small', dir: 'ltr' }, d.output));
      stage.appendChild(p.out);
    }
    return p;
  }

  function drawLoop(p, d, st) {
    if (p.items) {
      p.items.forEach(function (c, k) {
        c.classList.toggle('cw-sel', st.ptr === k);
        c.classList.toggle('cw-faded', st.end ? true : (st.ptr !== null && st.ptr !== undefined && k < st.ptr));
      });
      p.ptr.forEach(function (c, k) { c.textContent = st.ptr === k ? '↑ ' + d.seq.var : ''; });
    }
    if (p.trace) {
      p.trace.forEach(function (c, k) {
        var v = st.trace ? st.trace[k] : null;
        c.textContent = v === null || v === undefined ? '' : v;
        c.classList.toggle('cw-on', v !== null && v !== undefined);
        c.classList.toggle('cw-hot', st.traceNew === k);
      });
    }
    if (p.pairs) {
      var order = {};
      (st.visited || []).forEach(function (rc, k) { order[rc[0] + ',' + rc[1]] = k + 1; });
      p.pairs.forEach(function (row, r) {
        row.forEach(function (el, c) {
          var o = order[r + ',' + c];
          el.classList.toggle('cw-visited', !!o);
          el.classList.toggle('cw-sel', !!st.cell && st.cell[0] === r && st.cell[1] === c);
          el.lastChild.textContent = o ? String(o) : '';
        });
      });
    }
    clear(p.state);
    if (st.vars && st.vars.length) {
      p.state.appendChild(h('div', { class: 'cw-vars' }, st.vars.map(function (v) {
        return h('div', { class: 'cw-var' + (v[2] ? ' cw-changed' : '') },
                 h('span', { class: 'cw-var-name' }, v[0]), h('span', { class: 'cw-var-val' }, v[1]));
      })));
    }
    if (st.cond) {
      p.state.appendChild(h('div', { class: 'cw-cond', dir: 'ltr' },
        h('code', {}, st.cond[0]), h('span', { class: 'cw-muted' }, ' → '),
        h('code', {}, st.cond[1]), h('span', { class: 'cw-muted' }, ' → '),
        h('b', { class: st.cond[2] ? 'cw-true' : 'cw-false' }, st.cond[2] ? 'True' : 'False')));
    }
    if (st.dict) {
      var box = h('div', { class: 'cw-dict', dir: 'ltr' },
                  h('div', { class: 'cw-var-name' }, st.dict.name));
      if (!st.dict.rows.length) {
        box.appendChild(h('div', { class: 'cw-dict-empty' }, '{}'));
      } else {
        var t = h('div', { class: 'cw-grid cw-dict-grid' });
        t.style.gridTemplateColumns = 'auto auto';
        t.appendChild(h('span', { class: 'cw-head-cell cw-muted' }, 'key'));
        t.appendChild(h('span', { class: 'cw-head-cell cw-muted' }, 'value'));
        st.dict.rows.forEach(function (kv) {
          var hot = kv[0] === st.dict.changed;
          t.appendChild(cell(kv[0], hot && st.dict.isNew ? 'cw-res cw-new' : ''));
          t.appendChild(cell(kv[1], hot ? 'cw-res cw-new' : ''));
        });
        box.appendChild(t);
      }
      p.state.appendChild(box);
    }
    if (p.out) {
      clear(p.out);
      (st.output || []).forEach(function (line, k, all) {
        p.out.appendChild(h('span', { class: 'cw-line' + (st.outNew && k === all.length - 1 ? ' cw-on' : '') }, line));
      });
      if (!(st.output || []).length) { p.out.appendChild(h('span', { class: 'cw-line cw-comment' }, ' ')); }
    }
  }

  register('loopstate', function (root, d) {
    var parts = null;
    stepper(root, d, function (stage, st) {
      if (!parts) { parts = buildLoop(stage, d); }
      drawLoop(parts, d, st);
    });
  });

  /* 10.0, 10.1 -- names (inside frames) and arrows to the objects they name.
     A fixed layout per example, so nothing jumps between steps. */
  var MEM = { nameX: 14, nameW: 88, objX: 172, cellW: 27, W: 344 };

  function memLayout(sc) {
    var frames = [];
    var fIndex = {};
    var objs = [];
    var oIndex = {};
    sc.steps.forEach(function (st) {
      st.frames.forEach(function (f) {
        var key = f.title || '';
        if (!(key in fIndex)) { fIndex[key] = frames.length; frames.push({ title: f.title, names: [] }); }
        var fr = frames[fIndex[key]];
        f.vars.forEach(function (v) { if (fr.names.indexOf(v[0]) < 0) { fr.names.push(v[0]); } });
      });
      Object.keys(st.objects).forEach(function (k) {
        var o = st.objects[k];
        if (!(k in oIndex)) { oIndex[k] = objs.length; objs.push({ key: k, kind: o.kind, maxLen: 1 }); }
        (o.items || []).forEach(function (it) {   // wide enough for the longest item ever shown
          objs[oIndex[k]].maxLen = Math.max(objs[oIndex[k]].maxLen, String(it).length);
        });
      });
    });
    var y = 26;
    var fpos = {};
    frames.forEach(function (fr) {
      var top = y;
      var head = fr.title ? 20 : 0;
      var rows = {};
      fr.names.forEach(function (nm, k) { rows[nm] = top + head + 17 + 32 * k; });
      var hgt = head + 32 * fr.names.length + 6;
      fpos[fr.title || ''] = { top: top, h: hgt, rows: rows };
      y = top + hgt + 14;
    });
    var yo = 26;
    var opos = {};
    objs.forEach(function (o) {
      opos[o.key] = { top: yo, kind: o.kind, cw: Math.max(MEM.cellW, Math.round(o.maxLen * 7.6 + 11)) };
      yo += o.kind === 'list' ? 50 : 38;
    });
    return { frames: frames, fpos: fpos, opos: opos, H: Math.max(y, yo) + 4,
             titled: frames.some(function (f) { return !!f.title; }) };
  }

  function objCentre(lay, key) {
    var o = lay.opos[key];
    return o.kind === 'list' ? o.top + 29 : o.top + 17;
  }

  function drawMemory(svg, lay, st) {
    while (svg.firstChild) { svg.removeChild(svg.firstChild); }
    var mk = arrowMarker(svg, 'cw-mark-text');
    var mkMoved = arrowMarker(svg, 'cw-mark-sel');
    svg.appendChild(s('text', { x: MEM.nameX - 6, y: 14, class: 'cw-t-muted cw-t-small' },
                      lay.titled ? 'frames' : 'names'));
    svg.appendChild(s('text', { x: MEM.objX, y: 14, class: 'cw-t-muted cw-t-small' }, 'objects'));
    var fresh = st.fresh || [];
    var moved = st.moved || [];
    /* objects first, so arrows end on top of them */
    Object.keys(st.objects).forEach(function (key) {
      var o = st.objects[key];
      var pos = lay.opos[key];
      var g = s('g', { class: fresh.indexOf(key) >= 0 ? 'cw-new' : '' });
      if (o.kind === 'list') {
        o.items.forEach(function (it, j) {
          var cw = pos.cw;
          var x = MEM.objX + cw * j;
          var hot = st.changed && st.changed[0] === key && st.changed[1] === j;
          g.appendChild(s('text', { x: x + (cw - 2) / 2, y: pos.top + 11, 'text-anchor': 'middle',
                                    class: 'cw-t-muted cw-t-small' }, String(j)));
          g.appendChild(s('rect', { x: x, y: pos.top + 15, width: cw - 2, height: 28, rx: 5,
                                    class: 'cw-objcell' + (hot ? ' cw-objcell-hot' : '') +
                                           (fresh.indexOf(key) >= 0 ? ' cw-objcell-new' : '') }));
          g.appendChild(s('text', { x: x + (cw - 2) / 2, y: pos.top + 33, 'text-anchor': 'middle',
                                    class: 'cw-t-obj' }, it));
        });
        if (!o.items.length) {
          g.appendChild(s('rect', { x: MEM.objX, y: pos.top + 15, width: 30, height: 28, rx: 5, class: 'cw-objcell' }));
        }
      } else {
        var w = Math.max(34, String(o.value).length * 8 + 16);
        g.appendChild(s('rect', { x: MEM.objX, y: pos.top + 3, width: w, height: 28, rx: 6,
                                  class: 'cw-objcell' + (fresh.indexOf(key) >= 0 ? ' cw-objcell-new' : '') }));
        g.appendChild(s('text', { x: MEM.objX + w / 2, y: pos.top + 21, 'text-anchor': 'middle',
                                  class: 'cw-t-obj' }, String(o.value)));
      }
      svg.appendChild(g);
    });
    st.frames.forEach(function (f) {
      var fp = lay.fpos[f.title || ''];
      var isFn = !!f.title && f.title !== 'global';
      var g = s('g', { class: (st.newFrame && st.newFrame === f.title) ? 'cw-new' : '' });
      if (f.title) {
        g.appendChild(s('rect', { x: 6, y: fp.top, width: MEM.nameX + MEM.nameW, height: fp.h, rx: 8,
                                  class: 'cw-frame' + (isFn ? ' cw-frame-fn' : '') }));
        g.appendChild(s('text', { x: 14, y: fp.top + 14, class: isFn ? 'cw-t-ax1 cw-t-small' : 'cw-t-muted cw-t-small' },
                        f.title));
      }
      f.vars.forEach(function (v) {
        var yc = fp.rows[v[0]];
        var isMoved = moved.indexOf(v[0]) >= 0 && (!st.movedFrame || st.movedFrame === (f.title || ''));
        var x1 = MEM.nameX + MEM.nameW - 6;
        var x2 = MEM.objX - 3;
        var y2 = objCentre(lay, v[1]);
        g.appendChild(s('path', { d: 'M' + x1 + ',' + yc + ' C' + (x1 + 34) + ',' + yc + ' ' + (x2 - 34) + ',' + y2 +
                                     ' ' + x2 + ',' + y2,
                                  class: 'cw-ref-arrow' + (isMoved ? ' cw-ref-moved' : ''),
                                  'marker-end': isMoved ? mkMoved : mk }));
        g.appendChild(s('rect', { x: MEM.nameX, y: yc - 12, width: MEM.nameW - 6, height: 24, rx: 5,
                                  class: 'cw-namebox' + (isMoved ? ' cw-namebox-moved' : '') }));
        g.appendChild(s('text', { x: MEM.nameX + 7, y: yc + 4, class: 'cw-t-name' }, v[0]));
      });
      svg.appendChild(g);
    });
    svg.setAttribute('aria-label', st.alt || '');
  }

  register('memory', function (root, d) {
    scenarioStepper(root, d, function (sc) {
      var lay = memLayout(sc);
      var svg = null;
      var out = null;
      return function (stage, st) {
        if (!svg) {
          svg = s('svg', { viewBox: '0 0 ' + MEM.W + ' ' + lay.H, class: 'cw-svg cw-memsvg', role: 'img' });
          stage.appendChild(svg);
          if (sc.output) {
            stage.appendChild(h('div', { class: 'cw-muted cw-small', dir: 'ltr' }, sc.output));
            out = h('pre', { class: 'cw-listing cw-printed', dir: 'ltr', 'aria-live': 'polite' });
            stage.appendChild(out);
          }
        }
        drawMemory(svg, lay, st);
        if (out) {
          clear(out);
          (st.output || []).forEach(function (line, k, all) {
            out.appendChild(h('span', { class: 'cw-line' + (st.outNew && k >= all.length - st.outNew ? ' cw-on' : '') }, line));
          });
          if (!(st.output || []).length) { out.appendChild(h('span', { class: 'cw-line' }, ' ')); }
        }
      };
    });
  });

  global.CFSWidgets = { register: register, mount: mount, mountAll: mountAll,
                        api: api, core: core };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountAll);
  } else {
    mountAll();
  }
})(typeof window !== 'undefined' ? window : this);
