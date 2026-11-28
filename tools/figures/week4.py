"""Week 4 figures: loops (for, range, while, break / continue, nested loops,
list comprehensions). Every value comes from the code of the page."""
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch
from matplotlib.textpath import text_to_path
from matplotlib.transforms import Affine2D

from cfsfig import (AX0, AX0_FILL, AX1, AX1_FILL, BAD, BAD_FILL, CELL,
                    FADED, GREY, GREY_FILL, MONO, MUTED, RES, RES_FILL, SANS,
                    SEL, SEL_FILL, TEXT, arrow, cells, chip, new_fig, pill,
                    rbox, save, text)


def fig_for(xlim, ylim, width=6.4):
    """new_fig with the height that keeps one data unit square."""
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

    Returns the (x0, x1) span of every part, for brackets and labels."""
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


def under(ax, x0, x1, y, color, label=None, fs=9):
    """A thin bracket under a span of code, with a label below it."""
    ax.plot([x0, x0, x1, x1], [y + 0.08, y, y, y + 0.08], color=color,
            lw=1.3, zorder=4, solid_capstyle='round')
    if label:
        text(ax, (x0 + x1) / 2, y - 0.25, label, color, fs=fs)


def cell_texts(ax, x0, y0, values, colors, w=1.0, h=0.7, fs=11, mono=True):
    """Text over cells drawn empty: a colour per cell (one row)."""
    for j, (v, c) in enumerate(zip(values, colors)):
        text(ax, x0 + j * w + w / 2, y0 - h / 2, v, c, fs=fs, mono=mono)


# ---------------------------------------------------------------- 6.0
def fig_6_0_loop_trace():
    """count_spaces("a b c"): char takes one character per round."""
    s = "a b c"
    rounds, cnt = [], 0                 # the page's solution, round by round
    for char in s:
        if char == " ":
            cnt = cnt + 1
        rounds.append((char, cnt))
    assert cnt == 2                     # the check on the page: 2
    n, w, h = len(rounds), 1.25, 0.7
    xb, xr = 0.0, 1.85                  # "before" column, first round
    xa = xr + n * w + 0.6               # "after" column
    fig, ax = fig_for((-2.3, xa + w + 0.9), (-3.55, 1.75))
    chip(ax, -2.2, 1.35, 'count_spaces("a b c")', fs=10.5)
    sp = code(ax, 3.3, 1.35, [('for char in s:', MUTED)], fs=9.5)
    text(ax, sp[0][1] + 0.3, 1.35, 'one character per round', MUTED,
         fs=9.5, ha='left')
    # headers
    text(ax, -0.15, 0.4, 'round', MUTED, fs=9.5, ha='right')
    text(ax, xb + w / 2, 0.4, 'before', MUTED, fs=9.5)
    text(ax, xa + w / 2, 0.4, 'after', MUTED, fs=9.5)
    for k in range(n):
        text(ax, xr + k * w + w / 2, 0.4, str(k + 1), AX1, fs=10)
    # char: one cell per round
    text(ax, -0.15, -h / 2, 'char', AX1, ha='right', mono=True)
    cells(ax, xr, 0, [[repr(c) for c, _ in rounds]], w=w, h=h,
          fills=[[AX1_FILL] * n])
    # cnt: before the loop, after every round, after the loop
    y1 = -1.65
    text(ax, -0.15, y1 - h / 2, 'cnt', ha='right', mono=True)
    cells(ax, xb, y1, [['0']], w=w, h=h)
    grew = [rounds[k][1] > (rounds[k - 1][1] if k else 0) for k in range(n)]
    cells(ax, xr, y1, [[str(v) for _, v in rounds]], w=w, h=h,
          fills=[[RES_FILL if g else None for g in grew]])
    cells(ax, xa, y1, [[str(cnt)]], w=w, h=h, fills=[[RES_FILL]],
          edges=[[RES]])
    for k in range(n):
        x = xr + k * w + w / 2
        arrow(ax, (x, -h - 0.05), (x, y1 + 0.05), RES if grew[k] else GREY,
              lw=1.4)
        if grew[k]:
            text(ax, x + 0.3, (y1 - h) / 2 + 0.05, '+1', RES, fs=10,
                 ha='left')
    text(ax, xb + w / 2, y1 - h - 0.35, 'cnt = 0', MUTED, fs=9.5, mono=True)
    text(ax, xa + w / 2, y1 - h - 0.35, 'return cnt', MUTED, fs=9.5,
         mono=True)
    line(ax, xr + n * w / 2, y1 - h - 0.85,
         [('cnt', GREY, True), (' grows by 1 in the rounds where ', GREY,
                                False),
          ('char', GREY, True), (' is a space', GREY, False)], ha='center')
    return save(fig, 'w4_6_0_loop_trace')


# ---------------------------------------------------------------- 6.1
def fig_6_1_range():
    """range(10) and range(3, 10, 2) on the integers: start in, stop out."""
    first = list(range(10))             # the page: print(list(range(10)))
    second = list(range(3, 10, 2))      # the page: print(list(range(3,10, 2)))
    ints = list(range(11))
    w, h = 0.82, 0.62
    fig, ax = fig_for((-0.2, len(ints) * w + 0.2), (-5.0, 0.75), width=6.2)

    def strip(top, picked, label, desc, stop, start=None, step=None):
        yl = top + (1.05 if step else 0.38)
        pill(ax, 0.05, yl, label, SEL, SEL_FILL, mono=True, ha='left',
             fs=10)
        text(ax, 3.55, yl, desc, MUTED, ha='left', fs=9.5)
        fills = [[SEL_FILL if v in picked else GREY_FILL for v in ints]]
        edges = [[BAD if v == stop else None for v in ints]]
        cells(ax, 0, top, [[''] * len(ints)], fills=fills, edges=edges, w=w,
              h=h)
        cell_texts(ax, 0, top, [str(v) for v in ints],
                   [TEXT if v in picked else FADED for v in ints], w=w, h=h,
                   fs=10)
        text(ax, stop * w + w / 2, top - h - 0.22, 'stop', BAD, fs=9.5)
        if start is not None:
            text(ax, start * w + w / 2, top - h - 0.22, 'start', SEL,
                 fs=9.5)
        if step:
            for a, b in zip(picked[:-1], picked[1:]):
                arrow(ax, (a * w + w / 2 + 0.05, top + 0.06),
                      (b * w + w / 2 - 0.05, top + 0.06), SEL, lw=1.2,
                      rad=-0.45, ms=9)
                text(ax, (a + b) / 2 * w + w / 2, top + 0.52, f'+{step}',
                     SEL, fs=9)

    strip(-0.25, first, 'range(10)', 'from 0, step 1 (the defaults)', 10,
          start=0)
    strip(-2.95, second, 'range(3, 10, 2)', 'from 3, step 2', 10, start=3,
          step=2)
    line(ax, 0, -4.65, [('range(start, stop, step)', GREY, True),
                        (': start included, stop not included', GREY,
                         False)])
    return save(fig, 'w4_6_1_range')


def fig_6_1_differences():
    """4 measurements give 3 differences: i runs over range(len(T2) - 1)."""
    T2 = [20.0, 40.0, 50.0, 55.0]       # temperature of the cold body
    rises = []
    for i in range(len(T2) - 1):
        rises.append(T2[i + 1] - T2[i])
    n, w, h = len(T2), 1.3, 0.7
    fig, ax = fig_for((-2.3, 8.6), (-4.75, 1.05))
    text(ax, -0.15, 0.4, 'index', GREY, ha='right', fs=9.5)
    for j in range(n):
        text(ax, j * w + w / 2, 0.4, str(j), GREY, fs=9.5)
    text(ax, -0.15, -h / 2, 'T2', ha='right', mono=True)
    cells(ax, 0, 0, [[f'{v:.1f}' for v in T2]], w=w, h=h,
          fills=[[AX1_FILL] * n])
    text(ax, n * w + 0.3, -h / 2, f'{n} measurements', AX1, ha='left',
         fs=10)
    # one bracket between every two neighbours, its difference below
    y_br, top = -1.15, -1.9
    for i in range(n - 1):
        a, b = i * w + w / 2 + 0.07, (i + 1) * w + w / 2 - 0.07
        ax.plot([a, a, b, b], [-h - 0.05, y_br, y_br, -h - 0.05], color=RES,
                lw=1.4, zorder=1)
        arrow(ax, ((a + b) / 2, y_br), ((a + b) / 2, top + 0.02), RES,
              lw=1.4)
        text(ax, (a + b) / 2 + 0.12, (y_br + top) / 2, f'i={i}', AX1, fs=9,
             ha='left')
    text(ax, w / 2 - 0.15, top - h / 2, 'rises', RES, ha='right', mono=True)
    cells(ax, w / 2, top, [[f'{v:.1f}' for v in rises]], w=w, h=h,
          fills=[[RES_FILL] * (n - 1)])
    text(ax, n * w + 0.3, top - h / 2, f'{n - 1} differences', RES,
         ha='left', fs=10)
    text(ax, -0.15, (y_br + top) / 2, 'T2[i + 1] - T2[i]', RES,
         ha='right', mono=True, fs=9.5)
    chip(ax, -2.2, -3.4, 'for i in range(len(T2) - 1):', fs=10)
    text(ax, 3.85, -3.4, 'range(3): i = 0, 1, 2', MUTED, ha='left', fs=10,
         mono=True)
    text(ax, 3.1, -4.3, 'n measurements give n - 1 differences', GREY,
         fs=10)
    return save(fig, 'w4_6_1_differences')


# ---------------------------------------------------------------- 7.0
def diamond(ax, cx, cy, hw, hh, fc, r=0.18):
    """A diamond with rounded corners, centred at (cx, cy)."""
    side = 1.0
    p = FancyBboxPatch((-side / 2, -side / 2), side, side,
                       boxstyle=f'round,pad=0,rounding_size={r}', fc=fc,
                       ec='none', zorder=2)
    s = 2 ** 0.5
    p.set_transform(Affine2D().rotate_deg(45).scale(hw * s, hh * s)
                    .translate(cx, cy) + ax.transData)
    ax.add_patch(p)


def path_arrow(ax, pts, color, lw=1.6):
    """A polyline through pts with a filled head on the last segment."""
    xs, ys = zip(*pts[:-1])
    ax.plot(xs, ys, color=color, lw=lw, zorder=3, solid_capstyle='round',
            solid_joinstyle='round')
    arrow(ax, pts[-2], pts[-1], color, lw=lw)


def fig_7_0_while_flow():
    """The flow of a while loop, and the parts of the page's first example."""
    fig, ax = fig_for((-0.1, 11.7), (-4.35, 1.95))
    cx = 2.7
    text(ax, cx, 1.65, 'while condition:', TEXT, mono=True, fs=10.5)
    arrow(ax, (cx, 1.35), (cx, 0.8), TEXT)
    diamond(ax, cx, 0.1, 1.55, 0.68, AX1_FILL)
    text(ax, cx, 0.1, 'condition', AX1, weight='bold')
    # True: the statements, then back to the check
    arrow(ax, (cx, -0.6), (cx, -1.35), SEL)
    text(ax, cx + 0.15, -0.95, 'True', SEL, ha='left', fs=10)
    rbox(ax, cx - 1.5, -2.25, 3.0, 0.85, SEL_FILL, r=0.12)
    text(ax, cx, -1.825, 'statements', TEXT)
    path_arrow(ax, [(cx + 1.5, -1.825), (cx + 2.25, -1.825),
                    (cx + 2.25, 0.1), (cx + 1.58, 0.1)], SEL)
    text(ax, cx + 2.4, -0.85, 'check\nagain', SEL, ha='left', fs=9.5)
    # False: leave the loop
    path_arrow(ax, [(cx - 1.58, 0.1), (cx - 2.3, 0.1), (cx - 2.3, -3.5),
                    (cx - 1.75, -3.5)], GREY)
    text(ax, cx - 1.95, 0.4, 'False', GREY, fs=10)
    rbox(ax, cx - 1.7, -3.92, 3.4, 0.85, GREY_FILL, r=0.12)
    text(ax, cx, -3.495, 'rest of the code', GREY)

    # the page's first example, with the same colours
    x0, fs = 7.3, 10.5
    cw = char_w(ax, fs)
    text(ax, x0, 1.65, 'the example below', MUTED, ha='left', fs=9.5)
    lines = [[('n = 0', TEXT)],
             [('while ', TEXT), ('n < 10', AX1), (':', TEXT)],
             [('    print(n)', TEXT)],
             [('    n = n + 1', TEXT)],
             [('print("goodbye")', GREY)]]
    ys = [0.85, 0.1, -0.65, -1.25, -2.15]
    for y, parts in zip(ys, lines):
        code(ax, x0, y, parts, fs=fs)
    rbox(ax, x0 + 6 * cw - 0.08, ys[1] - 0.3, 6 * cw + 0.16, 0.6, AX1_FILL,
         r=0.1, z=1)
    rbox(ax, x0 + 4 * cw - 0.12, ys[3] - 0.32, 9 * cw + 0.24,
         ys[2] - ys[3] + 0.64, SEL_FILL, r=0.1, z=1)
    rbox(ax, x0 - 0.12, ys[4] - 0.3, 16 * cw + 0.24, 0.6, GREY_FILL, r=0.1,
         z=1)
    text(ax, x0, -3.2, 'the condition is checked', GREY, fs=10, ha='left')
    text(ax, x0, -3.65, 'before every round;', GREY, fs=10, ha='left')
    text(ax, x0, -4.1, 'the first False ends the loop', GREY, fs=10,
         ha='left')
    return save(fig, 'w4_7_0_while_flow')


# ---------------------------------------------------------------- 8.0
def fig_8_0_for_vs_while():
    """The same n rounds: range(n) holds the start, the stop and the step."""
    fig, ax = fig_for((-0.3, 13.1), (-4.6, 1.2))
    fs = 10.5
    text(ax, 0, 0.85, 'for', weight='bold', ha='left')
    rbox(ax, -0.15, -1.25, 5.6, 1.75, CELL, r=0.15, z=1)
    sp = code(ax, 0.1, 0.1, [('for i in ', TEXT), ('range(n)', SEL),
                             (':', TEXT)], fs=fs)
    code(ax, 0.1, -0.6, [('    do_something', TEXT)], fs=fs)
    x0, x1 = sp[1]
    rbox(ax, x0 - 0.06, -0.2, x1 - x0 + 0.12, 0.6, SEL_FILL, r=0.1, z=1.5)
    line(ax, 2.65, -1.7, [('range(n)', SEL, True),
                          (' holds all three:', SEL, False)], fs=9.5,
         ha='center')
    text(ax, 2.65, -2.1, 'start 0, stop n, step 1', SEL, fs=9.5)

    xw = 6.6
    text(ax, xw, 0.85, 'while', weight='bold', ha='left')
    rbox(ax, xw - 0.15, -2.5, 6.6, 3.0, CELL, r=0.15, z=1)
    ys = [0.1, -0.55, -1.2, -1.85]
    code(ax, xw + 0.1, ys[0], [('i=0', AX0)], fs=fs)
    code(ax, xw + 0.1, ys[1], [('while ', TEXT), ('i<n', AX1), (':', TEXT)],
         fs=fs)
    code(ax, xw + 0.1, ys[2], [('    do_something', TEXT)], fs=fs)
    code(ax, xw + 0.1, ys[3], [('    ', TEXT), ('i = i+1', RES)], fs=fs)
    xp = xw + 4.0
    pill(ax, xp, ys[0], 'start', AX0, AX0_FILL, fs=9, ha='left')
    pill(ax, xp, ys[1], 'stop check', AX1, AX1_FILL, fs=9, ha='left')
    pill(ax, xp, ys[3], 'step', RES, RES_FILL, fs=9, ha='left')
    text(ax, xw + 3.1, -2.95, 'forget the step: an infinite loop', BAD,
         fs=9.5)

    # both: the same values of i
    vals = ['0', '1', '2', '...', 'n-1']
    w = 1.05
    xs = 6.4 - 2.5 * w
    text(ax, xs - 0.15, -3.85, 'i', ha='right', mono=True)
    cells(ax, xs, -3.5, [vals], w=w, h=0.7, fs=10,
          fills=[[AX1_FILL, AX1_FILL, AX1_FILL, None, AX1_FILL]])
    text(ax, xs + 5 * w + 0.25, -3.85, 'n rounds in both loops', AX1,
         ha='left', fs=10)
    return save(fig, 'w4_8_0_for_vs_while')


# ---------------------------------------------------------------- 8.1
def fig_8_1_break_continue():
    """The page's list with break and with continue: which rounds run."""
    lst = [4, 2, -6, 3, -9]

    def run(keyword):                   # the page's two loops, recorded
        states = []
        for elem in lst:
            if elem < 0:
                states.append('jump')
                if keyword == 'break':
                    break
                continue
            states.append('full')
        return states + ['never'] * (len(lst) - len(states))

    w, h = 1.25, 0.7
    n = len(lst)
    fig, ax = fig_for((-2.6, 10.4), (-5.1, 1.05))
    chip(ax, -2.5, 0.65, 'lst = [4, 2, -6, 3,-9]', fs=10.5)
    rows = [('break', run('break'), BAD, BAD_FILL, -0.3),
            ('continue', run('continue'), AX1, AX1_FILL, -2.15)]
    for word, states, col, fill, top in rows:
        pill(ax, -0.25, top - h / 2, word, col, fill, mono=True, ha='right',
             fs=10)
        fills = [[{'full': RES_FILL, 'jump': fill, 'never': GREY_FILL}[s]
                  for s in states]]
        edges = [[col if s == 'jump' else None for s in states]]
        cells(ax, 0, top, [[''] * n], fills=fills, edges=edges, w=w, h=h)
        cell_texts(ax, 0, top, [str(v) for v in lst],
                   [FADED if s == 'never' else TEXT for s in states], w=w,
                   h=h)
        text(ax, n * w + 0.35, top - h / 2, 'done', TEXT, mono=True,
             ha='left')
        if word == 'break':
            j = states.index('jump')
            arrow(ax, ((j + 0.5) * w, top + 0.02), (n * w + 0.3, top - 0.2),
                  BAD, lw=1.5, rad=-0.3)
            text(ax, (j + 0.5) * w, top - h - 0.3,
                 'leaves the loop: 3 and -9 are never checked', BAD, fs=9.5,
                 ha='left')
        else:
            for j, s in enumerate(states):
                if s == 'jump' and j + 1 < n:
                    arrow(ax, ((j + 0.62) * w, top + 0.02),
                          ((j + 1.4) * w, top + 0.02), AX1, lw=1.3,
                          rad=-0.6, ms=9)
            text(ax, 0, top - h - 0.3,
                 'skips the rest of the round, and goes on to the next one',
                 AX1, fs=9.5, ha='left')
    # legend
    y = -4.2
    for x, fill, label in [(0.0, RES_FILL, 'the whole round ran'),
                           (4.6, GREY_FILL, 'never reached')]:
        rbox(ax, x, y - 0.22, 0.44, 0.44, fill, r=0.08)
        text(ax, x + 0.6, y, label, MUTED, ha='left', fs=9.5)
    line(ax, 0, -4.8, [('a negative number first prints ', GREY, False),
                       ('"First negative number is"', GREY, True)], fs=9.5)
    return save(fig, 'w4_8_1_break_continue')


# ---------------------------------------------------------------- 8.2
def fig_8_2_pairs_grid():
    """all_pairs(3): the inner loop runs fully for every value of i."""
    n = 3
    order = []                          # the page's loops, in print order
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            order.append((i, j))
    w, h = 2.25, 0.9
    fig, ax = fig_for((-3.2, 11.05), (-4.1, 1.75))
    chip(ax, -3.1, 1.4, 'all_pairs(3)', fs=10.5)
    vals = [[f'({i}, {j})' for j in range(1, n + 1)] for i in range(1, n + 1)]
    cells(ax, 0, 0, [[''] * n for _ in range(n)], w=w, h=h)
    for k, (i, j) in enumerate(order):
        x, y = (j - 1) * w, -(i - 1) * h - h / 2
        text(ax, x + 0.3, y, str(k + 1), MUTED, fs=9)
        text(ax, x + w / 2 + 0.2, y, vals[i - 1][j - 1], mono=True, fs=10.5)
    for i in range(1, n + 1):
        text(ax, -0.15, -(i - 1) * h - h / 2, f'i = {i}', AX0, ha='right',
             mono=True, fs=10)
    for j in range(1, n + 1):
        text(ax, (j - 1) * w + w / 2, 0.3, f'j = {j}', AX1, mono=True, fs=10)
    # the axes: outer loop down, inner loop across
    arrow(ax, (-1.75, 0), (-1.75, -n * h), AX0, lw=2)
    pill(ax, -2.25, -n * h / 2, 'outer loop', AX0, AX0_FILL, rotation=90,
         fs=9.5)
    arrow(ax, (0, 0.75), (n * w, 0.75), AX1, lw=2)
    pill(ax, n * w / 2, 1.12, 'inner loop', AX1, AX1_FILL, fs=9.5)
    # from the end of a row to the start of the next one
    for i in range(n - 1):
        arrow(ax, (n * w + 0.12, -i * h - h / 2),
              (n * w + 0.12, -(i + 1) * h - h / 2), AX0, lw=1.4, rad=-0.6,
              ms=9)
    line(ax, n * w + 0.55, -h, [('next ', AX0, False), ('i', AX0, True),
                                (':', AX0, False)], fs=9.5)
    line(ax, n * w + 0.55, -h - 0.4, [('j', AX0, True),
                                      (' starts again', AX0, False)],
         fs=9.5)
    text(ax, n * w + 0.55, -h - 0.8, 'from 1', AX0, ha='left', fs=9.5)
    line(ax, n * w / 2, -n * h - 0.45,
         [(f'{len(order)} lines: for every ', GREY, False), ('i', GREY, True),
          (', ', GREY, False), ('j', GREY, True),
          (' runs over 1, 2, 3', GREY, False)], ha='center')
    text(ax, n * w / 2, -n * h - 0.95, 'small numbers: the order of the lines',
         MUTED, fs=9.5)
    return save(fig, 'w4_8_2_pairs_grid')


# ---------------------------------------------------------------- 8.3
def fig_8_3_comprehension():
    """The loop and the comprehension, part by part, in the same colours."""
    lst_included = [2, 5, 11, 12]
    result = [i**2 for i in range(1, 11) if i in lst_included]
    fs = 10.5
    fig, ax = fig_for((-0.3, 13.6), (-5.55, 1.3))
    text(ax, 0, 1.0, 'lst_included=[2,5,11,12]', MUTED, mono=True, fs=10,
         ha='left')
    text(ax, 0, 0.45, 'loop', weight='bold', ha='left')
    rbox(ax, -0.15, -2.35, 7.6, 2.5, CELL, r=0.15, z=1)
    ys = [-0.2, -0.8, -1.4, -2.0]
    code(ax, 0.1, ys[0], [('lst=[]', AX0)], fs=fs)
    code(ax, 0.1, ys[1], [('for i in range(1,11)', AX1), (':', TEXT)], fs=fs)
    code(ax, 0.1, ys[2], [('    ', TEXT), ('if i in lst_included', SEL),
                          (':', TEXT)], fs=fs)
    code(ax, 0.1, ys[3], [('        lst.append(', TEXT), ('i**2', RES),
                          (')', TEXT)], fs=fs)
    xp = 8.0
    for y, label, col, fill in [(ys[0], 'a new list', AX0, AX0_FILL),
                                (ys[1], 'the loop', AX1, AX1_FILL),
                                (ys[2], 'the filter', SEL, SEL_FILL),
                                (ys[3], 'the value to add', RES, RES_FILL)]:
        pill(ax, xp, y, label, col, fill, fs=9, ha='left')

    text(ax, 0, -3.05, 'list comprehension: the value comes first',
         weight='bold', ha='left')
    rbox(ax, -0.15, -4.25, 13.6, 0.85, CELL, r=0.15, z=1)
    y = -3.83
    sp = code(ax, 0.1, y, [('[', AX0), ('i**2', RES), (' ', TEXT),
                           ('for i in range(1,11)', AX1), (' ', TEXT),
                           ('if i in lst_included', SEL), (']', AX0)], fs=fs)
    yb = y - 0.55
    for k, col in [(1, RES), (3, AX1), (5, SEL)]:
        under(ax, sp[k][0], sp[k][1], yb, col)
    text(ax, 0.1, -5.35, 'result:', MUTED, ha='left', fs=10)
    cells(ax, 1.5, -5.0, [[str(v) for v in result]], w=1.0, h=0.65,
          fills=[[RES_FILL] * len(result)], fs=10.5)
    line(ax, 1.5 + len(result) + 0.3, -5.33,
         [('of 1..10, only 2 and 5 are in ', MUTED, False),
          ('lst_included', MUTED, True)], fs=9.5)
    return save(fig, 'w4_8_3_comprehension')


FIGURES = [fig_6_0_loop_trace, fig_6_1_range, fig_6_1_differences,
           fig_7_0_while_flow, fig_8_0_for_vs_while, fig_8_1_break_continue,
           fig_8_2_pairs_grid, fig_8_3_comprehension]
