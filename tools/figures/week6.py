"""Week 6 figures: data structures (list, tuple, dict), f-strings and text
files. Every value comes from the code of the page."""
import io

from matplotlib.font_manager import FontProperties
from matplotlib.textpath import text_to_path

from cfsfig import (AX0, AX0_FILL, AX1, AX1_FILL, BAD, CELL, GREY, MONO,
                    MUTED, RES, RES_FILL, SANS, SEL, SEL_FILL, TEXT, arrow,
                    cells, chip, new_fig, pill, rbox, save, text)


def fig_for(xlim, ylim, width=None):
    """new_fig with the height that keeps one data unit square.

    The default width keeps the scale of the other week 4-6 figures."""
    width = width or min(6.4, 0.47 * (xlim[1] - xlim[0]))
    height = width * (ylim[1] - ylim[0]) / (xlim[1] - xlim[0])
    return new_fig(width, height, xlim, ylim)


def pt_to_data(ax, pt):
    """A length in points, in data units (x direction)."""
    ax.apply_aspect()
    px = ax.transData.transform((1, 0))[0] - ax.transData.transform((0, 0))[0]
    return pt / 72 * ax.figure.dpi / px


def char_w(ax, fs):
    """The advance of one monospace character at size fs, in data units.

    JetBrains Mono advances 0.6 em; the SVG places glyphs by this unhinted
    advance (Agg's hinted extents at the screen dpi are a few % shorter)."""
    return pt_to_data(ax, 0.6 * fs)


def code(ax, x, y, parts, fs=10.5):
    """One line of code from (text, colour) parts, left-aligned at x.

    Returns the (x0, x1) span of every part."""
    cw = char_w(ax, fs)
    spans = []
    for s, col in parts:
        ax.text(x, y, s, fontsize=fs, family=MONO, color=col or TEXT,
                ha='left', va='center', zorder=5)
        spans.append((x, x + len(s) * cw))
        x += len(s) * cw
    return spans


def line(ax, x, y, parts, fs=10, ha='left'):
    """One line of mixed text: parts are (text, colour, mono) pieces."""
    widths = []
    for s, col, mono in parts:
        prop = FontProperties(family=MONO if mono else SANS, size=fs)
        adv = text_to_path.get_text_width_height_descent(s, prop, False)[0]
        widths.append(pt_to_data(ax, adv))
    x0 = {'left': x, 'center': x - sum(widths) / 2,
          'right': x - sum(widths)}[ha]
    for (s, col, mono), wd in zip(parts, widths):
        ax.text(x0, y, s, fontsize=fs, color=col or TEXT, ha='left',
                va='center', family=MONO if mono else SANS, zorder=5)
        x0 += wd


def name_box(ax, x, y, name, w, h=0.6):
    """A variable name in a rounded box centred at height y, left edge x."""
    rbox(ax, x, y - h / 2, w, h, AX0_FILL, r=0.12)
    text(ax, x + w / 2, y, name, AX0, mono=True, fs=10.5)


def nl_pill(ax, x, y, fs=9):
    """The newline character, shown as a small amber capsule."""
    pill(ax, x, y, '\\n', AX1, AX1_FILL, mono=True, fs=fs, ha='left')


# ---------------------------------------------------------------- 12.0
def step(T1, T2, k, dt):              # 12.1: two bodies exchange heat
    flow = k * (T1 - T2) * dt
    return T1 - flow, T2 + flow


def fig_12_0_structures():
    """list, tuple and dict: how each one looks, how to get a value, and
    whether it can change."""
    temps = [80.0, 50.0, 35.0]          # 13.1: the temperatures file
    r = step(100.0, 20.0, 0.25, 1)      # 12.1
    rooms = {"lab": 20.0, "fridge": 4.0}   # 12.2
    w, h = 1.3, 0.62
    xd, xr = 2.9, 7.5                   # the drawing, the two notes
    fig, ax = fig_for((-0.3, 12.5), (-5.85, 0.2))
    rows = [('list  [ ]', 'temps', -0.45, 'temps[0]', temps[0], True),
            ('tuple  ( )', 'r', -2.05, 'r[0]', r[0], False),
            ('dict  { }', 'rooms', -3.65, 'rooms["lab"]', rooms["lab"],
             True)]
    for head, name, top, expr, val, can in rows:
        pill(ax, 0, top - h / 2, head, SEL, SEL_FILL, mono=True, fs=10,
             ha='left')
        text(ax, 0.05, top - h - 0.25, name, MUTED, mono=True, fs=9.5,
             ha='left')
        line(ax, xr, top - 0.15, [(expr, TEXT, True),
                                  ('  gives  ', MUTED, False),
                                  (f'{val:.1f}', RES, True)], fs=10)
        text(ax, xr, top - 0.65, 'can change' if can else 'cannot change',
             RES if can else BAD, fs=9.5, ha='left')
    for (_, _, top, *_), vals in zip(rows[:2], [temps, r]):
        for j in range(len(vals)):
            text(ax, xd + j * w + w / 2, top + 0.2, str(j), MUTED, fs=8)
        cells(ax, xd, top, [[f'{v:.1f}' for v in vals]], w=w, h=h, fs=10)
    top = rows[2][2]
    for i, (k, v) in enumerate(rooms.items()):
        y = top - i * (h + 0.1)
        rbox(ax, xd, y - h + 0.035, 1.95, h - 0.07, AX0_FILL, r=0.1)
        text(ax, xd + 0.975, y - h / 2, f'"{k}"', AX0, mono=True, fs=10)
        arrow(ax, (xd + 2.0, y - h / 2), (xd + 2.45, y - h / 2), AX0,
              lw=1.2, ms=8)
        cells(ax, xd + 2.5, y, [[f'{v:.1f}']], w=w, h=h, fs=10)
    text(ax, 0, -5.5, 'a list and a tuple: by index;  a dict: by key',
         GREY, fs=10, ha='left')
    return save(fig, 'w6_12_0_structures')


# ---------------------------------------------------------------- 12.1
def fig_12_1_return_tuple():
    """step returns one tuple; keep it whole, or unpack it into two names."""
    T1_0, T2_0, k, dt = 100.0, 20.0, 0.25, 1
    flow = k * (T1_0 - T2_0) * dt
    r = step(T1_0, T2_0, k, dt)
    T1, T2 = step(T1_0, T2_0, k, dt)
    assert r == (T1, T2)
    w, h = 1.3, 0.65
    fig, ax = fig_for((-0.3, 11.2), (-7.0, 1.05))
    chip(ax, -0.2, 0.7, 'return T1 - flow, T2 + flow', fs=10)
    line(ax, 7.0, 0.7, [('flow', MUTED, True), (' is ', MUTED, False),
                        (f'{flow:.1f}', MUTED, True)], fs=9.5)
    # keep the tuple in one name
    chip(ax, -0.2, -0.55, 'r = step(100.0, 20.0, 0.25, 1)', fs=10)
    name_box(ax, 0, -1.85, 'r', 1.2)
    arrow(ax, (1.28, -1.85), (3.48, -1.85), AX0)
    text(ax, 3.5, -1.85 + h / 2 + 0.22, 'tuple', MUTED, fs=8.5, ha='left')
    cells(ax, 3.5, -1.85 + h / 2, [[f'{v:.1f}' for v in r]], w=w, h=h,
          fs=10.5)
    for j in range(2):
        text(ax, 3.5 + j * w + w / 2, -1.85 - h / 2 - 0.25, f'r[{j}]', AX0,
             mono=True, fs=9.5)
    # unpack it into two names
    top = -3.35
    chip(ax, -0.2, top, 'T1, T2 = step(100.0, 20.0, 0.25, 1)', fs=10)
    x0 = 3.5
    text(ax, x0, top - 0.75, 'tuple', MUTED, fs=8.5, ha='left')
    cells(ax, x0, top - 0.9, [[f'{v:.1f}' for v in r]], w=w, h=h, fs=10.5)
    for j, name in enumerate(['T1', 'T2']):
        xc = x0 + j * w + w / 2
        bx = xc - 0.6 + (j - 0.5) * 1.6
        arrow(ax, (xc, top - 0.95 - h), (bx + 0.6, top - 2.38), AX0, lw=1.4)
        name_box(ax, bx, top - 2.7, name, 1.2)
    line(ax, 0, top - 3.45, [('one name for each element:  ', MUTED, False),
                             ('T1', MUTED, True), (' is ', MUTED, False),
                             (f'{T1:.1f}', MUTED, True),
                             (',  ', MUTED, False), ('T2', MUTED, True),
                             (' is ', MUTED, False),
                             (f'{T2:.1f}', MUTED, True)], fs=9.5)
    return save(fig, 'w6_12_1_return_tuple')


# ---------------------------------------------------------------- 12.2
def fig_12_2_keys_values():
    """studs: every key leads to one value; studs["Moshe"] looks it up."""
    studs = {"Avi": 90, "Moshe": 80, "Adam": 70}
    look = "Moshe"
    fig, ax = fig_for((-0.3, 11.4), (-3.95, 1.05))
    chip(ax, -0.2, 0.7, 'studs={"Avi": 90, "Moshe": 80, "Adam": 70}', fs=10)
    text(ax, 1.1, -0.15, 'keys', MUTED, fs=9.5)
    text(ax, 4.55, -0.15, 'values', MUTED, fs=9.5)
    for i, (k, v) in enumerate(studs.items()):
        y = -0.85 - i * 0.9
        hit = k == look
        rbox(ax, 0, y - 0.3, 2.2, 0.6, AX0_FILL, ec=SEL if hit else None,
             lw=2.0 if hit else 0, r=0.12)
        text(ax, 1.1, y, f'"{k}"', AX0, mono=True, fs=10.5)
        arrow(ax, (2.3, y), (3.9, y), AX0)
        cells(ax, 4.0, y + 0.3, [[str(v)]], w=1.1, h=0.6,
              edges=[[SEL if hit else None]])
    y = -0.85 - list(studs).index(look) * 0.9
    line(ax, 5.9, y, [(f'studs["{look}"]', SEL, True),
                      ('  gives  ', MUTED, False),
                      (str(studs[look]), RES, True)], fs=10)
    text(ax, 0, -3.6, 'a key leads to its value; a value does not lead back',
         GREY, fs=10, ha='left')
    return save(fig, 'w6_12_2_keys_values')


def fig_12_2_char_count():
    """get_char_count('jerry'), one character at a time."""
    text_ = 'jerry'
    char_count, steps = {}, []         # the page's solution, step by step
    for char in text_:
        new = char not in char_count
        if new:
            char_count[char] = 1
        else:
            char_count[char] += 1
        steps.append((char, dict(char_count), new))
    w, h, pw = 1.0, 0.6, 1.8
    xd = 2.0
    fig, ax = fig_for((-0.3, 12.4), (-5.55, 1.1))
    chip(ax, -0.2, 0.75, "get_char_count('jerry')", fs=10)
    text(ax, w / 2, -0.05, 'char', AX1, mono=True, fs=9.5)
    line(ax, xd, -0.05, [('char_count', MUTED, True),
                         (' after this character', MUTED, False)], fs=9.5)
    for r, (char, state, new) in enumerate(steps):
        y = -0.4 - r * 0.85
        cells(ax, 0, y, [[repr(char)]], w=w, h=h, fills=[[AX1_FILL]],
              fs=10.5)
        arrow(ax, (w + 0.1, y - h / 2), (xd - 0.15, y - h / 2), GREY,
              lw=1.2, ms=9)
        keys = list(state)
        fills = [(RES_FILL if new else SEL_FILL) if k == char else None
                 for k in keys]
        edges = [(RES if new else SEL) if k == char else None for k in keys]
        cells(ax, xd, y, [[f"'{k}': {state[k]}" for k in keys]], w=pw, h=h,
              fills=[fills], edges=[edges], fs=9.5)
        note = 'new key: 1' if new else '+1'
        text(ax, xd + 4 * pw + 0.25, y - h / 2, note, RES if new else SEL,
             fs=9.5, ha='left')
    line(ax, 0, -5.15, [('returns  ', MUTED, False),
                        (str(char_count), RES, True)], fs=10)
    return save(fig, 'w6_12_2_char_count')


# ---------------------------------------------------------------- 13.0
def fig_13_0_fstring():
    """f"... {name} ... {pi:.2f}": each field is replaced by its value."""
    name = 'Avi'
    pi = 3.14159265359
    out = f"My name is {name} and I like {pi:.2f}"
    fs = 10.5
    fig, ax = fig_for((-0.3, 10.4), (-2.35, 2.5))
    rbox(ax, -0.15, -0.33, 9.85, 0.66, CELL, r=0.12, z=1)
    sp = code(ax, 0, 0, [('f"My name is ', TEXT), ('{', AX0), ('name', AX0),
                         ('}', AX0), (' and I like ', TEXT), ('{', AX0),
                         ('pi', AX0), (':', SEL), ('.2', SEL), ('f', SEL),
                         ('}', AX0), ('"', TEXT)], fs=fs)
    # the parts of {pi:.2f}: leader lines up, labels to the left
    rows = [(6, 0.75, [('pi', AX0, True), (' is ', MUTED, False),
                       ('3.14159265359', AX0, True)]),
            (7, 1.25, [('a colon: the format comes after it', SEL,
                        False)]),
            (8, 1.75, [('.2', SEL, True), (': 2 digits after the point',
                                           SEL, False)]),
            (9, 2.25, [('f', SEL, True), (': fixed-point notation', SEL,
                                          False)])]
    xl = sp[6][0] - 0.35
    for k, y, parts in rows:
        xm = (sp[k][0] + sp[k][1]) / 2
        col = AX0 if k == 6 else SEL
        ax.plot([xm, xm, xl + 0.15], [0.28, y, y], color=col, lw=1.1,
                zorder=4, solid_capstyle='round')
        line(ax, xl, y, parts, fs=9.5, ha='right')
    # the string that comes out
    cw = char_w(ax, fs)
    yo = -1.55
    xo = 2 * cw                         # under the text, after f"
    rbox(ax, xo - 0.12, yo - 0.33, len(out) * cw + 0.24, 0.66, RES_FILL,
         r=0.12, z=1)
    code(ax, xo, yo, [(out, TEXT)], fs=fs)
    i_name = out.index(name)
    i_pi = out.index(f'{pi:.2f}')
    for (a, b), (i, n) in [((sp[1][0], sp[3][1]), (i_name, len(name))),
                           ((sp[5][0], sp[10][1]), (i_pi, 4))]:
        arrow(ax, ((a + b) / 2, -0.36), (xo + (i + n / 2) * cw, yo + 0.36),
              RES, lw=1.4)
    text(ax, xo + len(out) * cw + 0.3, yo, 'a str', RES, fs=9.5, ha='left')
    return save(fig, 'w6_13_0_fstring')


# ---------------------------------------------------------------- 13.1
def fig_13_1_lines():
    """An editor shows lines; the file has \\n at the end of each one."""
    content = ('This is line one\nThis is line two\nThis is line three\n'
               'This is line four\n')       # the page's sequence of characters
    lines = content.split('\n')[:-1]
    fs = 10.5
    fig, ax = fig_for((-0.3, 8.6), (-4.35, 1.05))
    pill(ax, 0, 0.7, 'test.txt', TEXT, CELL, mono=True, fs=10, ha='left')
    rbox(ax, -0.1, -2.95, 7.0, 3.3, CELL, r=0.15, z=1)
    cw = char_w(ax, fs)
    for i, s in enumerate(lines):
        y = -0.2 - i * 0.75
        text(ax, 0.25, y, str(i + 1), MUTED, fs=9, mono=True)
        code(ax, 0.7, y, [(s, TEXT)], fs=fs)
        nl_pill(ax, 0.7 + len(s) * cw + 0.35, y)
    line(ax, 0, -3.5, [('for every ', MUTED, False), ('\\n', AX1, True),
                       (' in the file, the editor starts a new line', MUTED,
                        False)], fs=10)
    line(ax, 0, -4.0, [('it does not show the ', MUTED, False),
                       ('\\n', AX1, True), (' itself', MUTED, False)],
         fs=10)
    return save(fig, 'w6_13_1_lines')


def fig_13_1_to_numbers():
    """From a file of temperatures to numbers: readlines, strip, float."""
    temps = [80.0, 50.0, 35.0]         # the page's file: one per line
    f = io.StringIO()
    for T in temps:
        f.write(f"{T:.1f}\n")
    content = f.getvalue()
    lines = io.StringIO(content).readlines()
    stripped = [s.strip() for s in lines]
    numbers = [float(s) for s in stripped]
    assert numbers == temps
    n, w, h, fs = len(lines), 2.3, 0.62, 10
    x0 = 0.0
    fig, ax = fig_for((-2.9, 12.0), (-6.25, 1.1))
    cw = char_w(ax, fs)
    # the file: one sequence of characters
    text(ax, -0.25, 0.4, 'the file', MUTED, fs=9.5, ha='right')
    parts, seg = [], []
    for s in stripped:
        seg.append(len(''.join(p for p, _ in parts)))
        parts += [(s, TEXT), ('\\n', AX1)]
    seq_w = sum(len(p) for p, _ in parts) * cw
    xs = x0 + (n * w - seq_w) / 2
    rbox(ax, xs - 0.15, 0.08, seq_w + 0.3, 0.64, CELL, r=0.12, z=1)
    code(ax, xs, 0.4, parts, fs=fs)
    rows = [('f.readlines()', [repr(s) for s in lines], None,
             'a list of str'),
            ('.strip()', [repr(s) for s in stripped], None,
             'str, no newline'),
            ('float(...)', [f'{v:.1f}' for v in numbers], RES_FILL,
             'float: numbers')]
    prev = [(xs + (seg[j] + 2) * cw, 0.05) for j in range(n)]
    for r, (method, vals, fill, kind) in enumerate(rows):
        top = -1.2 - r * 1.95
        for j in range(n):
            xc = x0 + j * w + w / 2
            arrow(ax, prev[j], (xc, top + 0.05), GREY, lw=1.2, ms=9)
        chip(ax, n * w + 0.3, top + 0.5, method, fs=9.5)
        cells(ax, x0, top, [vals], w=w, h=h, fs=fs,
              fills=[[fill] * n] if fill else None)
        if kind == 'str, no newline':
            line(ax, -0.25, top - h / 2, [('str, no ', MUTED, False),
                                          ('\\n', AX1, True)], fs=9.5,
                 ha='right')
        else:
            text(ax, -0.25, top - h / 2, kind, RES if fill else MUTED,
                 fs=9.5, ha='right')
        prev = [(x0 + j * w + w / 2, top - h - 0.05) for j in range(n)]
    return save(fig, 'w6_13_1_to_numbers')


FIGURES = [fig_12_0_structures, fig_12_1_return_tuple, fig_12_2_keys_values,
           fig_12_2_char_count, fig_13_0_fstring, fig_13_1_lines,
           fig_13_1_to_numbers]
