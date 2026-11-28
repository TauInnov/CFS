"""Week 5 figures: names and objects in memory, memory in functions,
default values and functions as parameters. Every value comes from the
code of the page."""
import inspect

from matplotlib.font_manager import FontProperties
from matplotlib.textpath import text_to_path

from cfsfig import (AX0, AX0_FILL, CELL, FADED, GREY, MONO, MUTED, RES,
                    RES_FILL, SANS, SEL, SEL_FILL, TEXT, arrow, cells, chip,
                    new_fig, pill, rbox, save, text)


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


def name_box(ax, x, y, name, w, h=0.6, color=None, fill=None):
    """A variable name: a rounded box centred at height y, left edge x.
    Returns the middle of its right edge (where its arrow starts)."""
    rbox(ax, x, y - h / 2, w, h, fill or AX0_FILL, r=0.12)
    text(ax, x + w / 2, y, name, color or AX0, mono=True, fs=10.5)
    return (x + w, y)


def list_obj(ax, x, y, values, fills=None, edges=None, w=0.75, h=0.6,
             label='list', fs=10.5, index=True):
    """An object: cells centred at height y (a list: with indices above).
    Returns the middle of its left edge (where arrows end)."""
    cells(ax, x, y + h / 2, [values], w=w, h=h, fs=fs,
          fills=[fills] if fills else None, edges=[edges] if edges else None)
    if index:
        for j in range(len(values)):
            text(ax, x + j * w + w / 2, y + h / 2 + 0.2, str(j), MUTED, fs=8)
    if label:
        text(ax, x, y + h / 2 + (0.55 if index else 0.25), label, MUTED,
             fs=8.5, ha='left', va='center')
    return (x - 0.02, y)


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


def frame(ax, x, y, w, h, title):
    """A frame (the names of one scope): a soft panel with its title."""
    rbox(ax, x, y - h, w, h, CELL, r=0.15, z=1)
    text(ax, x + 0.2, y - 0.3, title, MUTED, fs=9.5, ha='left')


# ---------------------------------------------------------------- 10.0
def fig_10_0_names():
    """a=3, b=a: two names, one object; b=a copies the arrow."""
    a = 3
    b = a
    assert b is a                       # one object, two names
    fig, ax = fig_for((-0.3, 8.1), (-3.6, 1.05))
    chip(ax, -0.2, 0.7, 'a=3', fs=10.5)
    chip(ax, 1.3, 0.7, 'b=a', fs=10.5)
    text(ax, 0, -0.2, 'names', MUTED, fs=9.5, ha='left')
    text(ax, 5.4, -0.2, 'objects', MUTED, fs=9.5, ha='left')
    pa = name_box(ax, 0, -0.95, 'a', 1.4)
    pb = name_box(ax, 0, -2.05, 'b', 1.4)
    p3 = list_obj(ax, 5.4, -1.5, [str(a)], w=0.9, label='int', index=False)
    for p, rad in [(pa, -0.12), (pb, 0.12)]:
        arrow(ax, (p[0] + 0.08, p[1]), p3, AX0, rad=rad)
    line(ax, 3.9, -3.15, [('b=a', GREY, True),
                          (' copies the arrow, not the object', GREY, False)],
         ha='center')
    return save(fig, 'w5_10_0_names')


def fig_10_0_rebind():
    """orig_list = [6,7,8,9] moves one arrow; copy_list keeps the old list."""
    orig_list = [1, 2, 3]
    copy_list = orig_list
    same_before = copy_list is orig_list
    old = orig_list
    orig_list = [6, 7, 8, 9]
    assert same_before and copy_list is old and orig_list is not old
    nw = 2.6
    fig, ax = fig_for((-0.3, 10.5), (-7.4, 1.05))

    # after the first two lines
    text(ax, 0, 0.7, 'after line 2', weight='bold', ha='left')
    chip(ax, 2.9, 0.7, 'copy_list = orig_list', fs=10)
    p1 = name_box(ax, 0, -0.75, 'orig_list', nw)
    p2 = name_box(ax, 0, -1.85, 'copy_list', nw)
    pl = list_obj(ax, 6.0, -1.3, [str(v) for v in old])
    arrow(ax, (p1[0] + 0.08, p1[1]), pl, AX0, rad=-0.12)
    arrow(ax, (p2[0] + 0.08, p2[1]), pl, AX0, rad=0.12)
    text(ax, 6.0, -2.3, 'one list, two names', MUTED, fs=9.5, ha='left')

    # after the third line
    top = -3.4
    text(ax, 0, top, 'after line 3', weight='bold', ha='left')
    chip(ax, 2.9, top, 'orig_list = [6,7,8,9]', fs=10)
    q1 = name_box(ax, 0, top - 1.55, 'orig_list', nw)
    q2 = name_box(ax, 0, top - 2.85, 'copy_list', nw)
    pn = list_obj(ax, 6.0, top - 1.45, [str(v) for v in orig_list],
                  fills=[RES_FILL] * len(orig_list), label='a new list')
    po = list_obj(ax, 6.0, top - 3.1, [str(v) for v in copy_list])
    arrow(ax, (q1[0] + 0.08, q1[1]), pn, RES, rad=-0.05)
    arrow(ax, (q2[0] + 0.08, q2[1]), po, AX0, rad=0.05)
    arrow(ax, (q1[0] + 0.08, q1[1] - 0.12), (po[0], po[1] + 0.12), GREY,
          ls='--', lw=1.2, rad=0.1)
    line(ax, 0, top - 3.75, [('dashed: the old arrow of ', GREY, False),
                             ('orig_list', GREY, True)], fs=9.5)
    return save(fig, 'w5_10_0_rebind')


def fig_10_0_edit_copy():
    """Editing a shared list shows in both names; .copy() makes a new list."""
    orig_list = [1, 2, 3]               # cell: copy_list = orig_list
    copy_list = orig_list
    orig_list[0] = 1000
    shared = list(copy_list)
    orig2 = [1, 2, 3]                   # cell: real_copy = orig_list.copy()
    real_copy = orig2.copy()
    orig2[0] = 1000
    assert shared == orig_list == orig2 and real_copy == [1, 2, 3]
    nw, w = 2.6, 1.2
    sel = [SEL_FILL, None, None]
    edg = [SEL, None, None]
    fig, ax = fig_for((-0.3, 12.0), (-8.1, 1.1))

    text(ax, 0, 0.75, 'Two names, one list', weight='bold', ha='left')
    chip(ax, 4.9, 0.75, 'copy_list = orig_list', fs=10)
    chip(ax, 4.9, 0.05, 'orig_list[0] = 1000', fs=10)
    p1 = name_box(ax, 0, -1.4, 'orig_list', nw)
    p2 = name_box(ax, 0, -2.5, 'copy_list', nw)
    pl = list_obj(ax, 6.0, -1.95, [str(v) for v in shared], fills=sel,
                  edges=edg, w=w)
    arrow(ax, (p1[0] + 0.08, p1[1]), pl, AX0, rad=-0.12)
    arrow(ax, (p2[0] + 0.08, p2[1]), pl, AX0, rad=0.12)
    text(ax, 6.0, -2.75, 'both names see 1000', SEL, fs=9.5, ha='left')

    top = -4.0
    text(ax, 0, top, 'A copy: two lists', weight='bold', ha='left')
    chip(ax, 4.9, top, 'real_copy = orig_list.copy()', fs=10)
    chip(ax, 4.9, top - 0.7, 'orig_list[0] = 1000', fs=10)
    q1 = name_box(ax, 0, top - 2.15, 'orig_list', nw)
    q2 = name_box(ax, 0, top - 3.45, 'real_copy', nw)
    pa = list_obj(ax, 6.0, top - 2.15, [str(v) for v in orig2], fills=sel,
                  edges=edg, w=w)
    pb = list_obj(ax, 6.0, top - 3.45, [str(v) for v in real_copy],
                  fills=[RES_FILL] * 3, w=w, label=None, index=False)
    arrow(ax, (q1[0] + 0.08, q1[1]), pa, AX0)
    arrow(ax, (q2[0] + 0.08, q2[1]), pb, RES)
    line(ax, 9.8, top - 3.45, [('.copy()', RES, True),
                               (': a new list', RES, False)], fs=9.5)
    return save(fig, 'w5_10_0_edit_copy')


# ---------------------------------------------------------------- 10.1
def call_frames(ax, names, title):
    """The two frames of a call: the global names and the function's names.
    Returns where the arrows of the global and the local name start."""
    frame(ax, 0, -0.05, 3.6, 1.45, 'global')
    frame(ax, 0, -2.2, 3.6, 1.45, '')
    text(ax, 0.2, -2.5, title, MUTED, fs=9.5, ha='left', mono=True)
    g = name_box(ax, 1.0, -0.95, names[0], 2.2)
    loc = name_box(ax, 1.0, -3.1, names[1], 2.2)
    return (g[0] + 0.08, g[1]), (loc[0] + 0.08, loc[1])


def fig_10_1_number_arg():
    """add1(n): the local n gets a new object; the global n keeps 6."""
    def add1(n):
        n = n + 1
        return n
    n = 6
    out = add1(n)
    assert out == 7 and n == 6
    fig, ax = fig_for((-0.3, 12.0), (-5.35, 1.05))
    chip(ax, -0.2, 0.7, 'n = 6', fs=10)
    chip(ax, 1.55, 0.7, 'add1(n)', fs=10)
    g, loc = call_frames(ax, ('n', 'n'), 'add1(n)')
    six = list_obj(ax, 6.6, -0.95, [str(n)], label='int', index=False)
    seven = list_obj(ax, 6.6, -3.1, [str(out)], fills=[SEL_FILL],
                     edges=[SEL], label='int', index=False)
    arrow(ax, g, six, AX0)
    arrow(ax, loc, six, GREY, ls='--', lw=1.2, rad=0.12)
    arrow(ax, loc, seven, SEL)
    line(ax, 4.0, -3.4, [('n = n + 1', SEL, True)], fs=9.5)
    line(ax, 7.6, -0.8, [('the global ', MUTED, False), ('n', MUTED, True),
                         (',', MUTED, False)], fs=9.5)
    line(ax, 7.6, -1.2, [('and the local ', GREY, False),
                         ('n', GREY, True), (' at the call', GREY, False)],
         fs=9.5)
    line(ax, 7.6, -2.95, [('the local ', SEL, False), ('n', SEL, True),
                          (' after', SEL, False)], fs=9.5)
    line(ax, 7.6, -3.35, [('n = n + 1', SEL, True), (': a new int', SEL,
                                                     False)], fs=9.5)
    line(ax, 0, -4.4, [('add1(n)', MUTED, True), (' returns 7; the global ',
                                                  MUTED, False),
                       ('n', MUTED, True), (' still points to 6:', MUTED,
                                            False)], fs=9.5)
    line(ax, 0, -4.9, [('print(n)', MUTED, True), (' gives 6', MUTED, False)],
         fs=9.5)
    return save(fig, 'w5_10_1_number_arg')


def fig_10_1_list_arg():
    """func(a): x and a are two names of one list; append changes it."""
    def func(x):
        x.append(9)
    a = [4, 5, 6, 7, 8]
    before = len(a)
    func(a)
    assert a == [4, 5, 6, 7, 8, 9]
    k, w = len(a), 0.75
    fills = [None] * before + [SEL_FILL] * (k - before)
    edges = [None] * before + [SEL] * (k - before)
    fig, ax = fig_for((-0.3, 12.0), (-5.35, 1.05))
    chip(ax, -0.2, 0.7, 'a=[4,5,6,7,8]', fs=10)
    chip(ax, 3.25, 0.7, 'func(a)', fs=10)
    g, loc = call_frames(ax, ('a', 'x'), 'func(a)')
    lst = list_obj(ax, 6.2, -2.0, [str(v) for v in a], fills=fills,
                   edges=edges, w=w)
    arrow(ax, g, lst, AX0, rad=-0.12)
    arrow(ax, loc, lst, AX0, rad=0.12)
    line(ax, 6.2 + (k - 0.5) * w, -2.7, [('x.append(9)', SEL, True)],
         fs=9.5, ha='center')
    line(ax, 0, -4.4, [('x', MUTED, True), (' and ', MUTED, False),
                       ('a', MUTED, True),
                       (' are two names of the same list;', MUTED, False)],
         fs=9.5)
    line(ax, 0, -4.9, [('after the call, ', MUTED, False),
                       ('print(a)', MUTED, True), (' gives ', MUTED, False),
                       (str(a), MUTED, True)], fs=9.5)
    return save(fig, 'w5_10_1_list_arg')


# ---------------------------------------------------------------- 11.0
def fig_11_0_defaults():
    """Each parameter gets a value: from the call (by place or by name), or
    its default value."""
    def f1(x, y=1):
        return x + y

    def f2(x=1, y=2, z=3):
        return x + y + z

    calls = [('f1(1, 2)', f1, (1, 2), {}), ('f1(3)', f1, (3,), {}),
             ('f2(y=5)', f2, (), {'y': 5})]
    fig, ax = fig_for((-0.3, 11.6), (-5.1, 1.05))
    text(ax, 0, 0.7, 'def f1(x, y=1):', MUTED, mono=True, fs=10, ha='left')
    text(ax, 5.2, 0.7, 'def f2(x=1, y=2, z=3):', MUTED, mono=True, fs=10,
         ha='left')
    w, h, xs = 1.1, 0.65, 3.6
    for r, (label, f, args, kwargs) in enumerate(calls):
        y = -0.7 - r * 1.45
        chip(ax, 0, y, label, fs=10.5)
        bound = inspect.signature(f).bind(*args, **kwargs)
        given = dict(bound.arguments)
        bound.apply_defaults()
        for j, (p, v) in enumerate(bound.arguments.items()):
            x = xs + j * (w + 0.25)
            text(ax, x + w / 2, y + h / 2 + 0.22, p, MUTED, mono=True, fs=9.5)
            if p in given:
                rbox(ax, x, y - h / 2, w, h, AX0_FILL, r=0.12)
                text(ax, x + w / 2, y, str(v), AX0, mono=True, fs=10.5)
                if p in kwargs:
                    text(ax, x + w / 2, y - h / 2 - 0.22, 'by name', AX0,
                         fs=8.5)
            else:
                rbox(ax, x, y - h / 2, w, h, CELL, ec=FADED, lw=1.1, r=0.12,
                     ls='--')
                text(ax, x + w / 2, y, str(v), GREY, mono=True, fs=10.5)
        xr = xs + 3 * (w + 0.25) + 0.4
        arrow(ax, (xr, y), (xr + 0.7, y), RES, lw=1.4)
        text(ax, xr + 0.9, y, f'returns {f(*args, **kwargs)}', RES, fs=10,
             ha='left')
    y = -4.75
    rbox(ax, 0, y - 0.2, 0.42, 0.42, AX0_FILL, r=0.08)
    text(ax, 0.6, y, 'from the call', MUTED, fs=9.5, ha='left')
    rbox(ax, 3.4, y - 0.2, 0.42, 0.42, CELL, ec=FADED, lw=1.1, r=0.08,
         ls='--')
    text(ax, 4.0, y, 'the default value', MUTED, fs=9.5, ha='left')
    return save(fig, 'w5_11_0_defaults')


def fig_11_0_function_param():
    """pairs_op calls op on every pair of neighbours; op is a parameter."""
    def add(x, y):
        return x + y

    def multiply(x, y):
        return x * y

    def pairs_op(lst, op):
        results = []
        for i in range(len(lst) - 1):
            results.append(op(lst[i], lst[i + 1]))
        return results

    nums = [1, 2, 3, 4]
    rows = [('add', pairs_op(nums, add)),
            ('multiply', pairs_op(nums, multiply))]
    n, w, h = len(nums), 1.2, 0.65
    fig, ax = fig_for((-2.6, 11.6), (-5.55, 1.0))
    text(ax, -0.15, 0.35, 'index', MUTED, ha='right', fs=9)
    for j in range(n):
        text(ax, j * w + w / 2, 0.35, str(j), MUTED, fs=9)
    text(ax, -0.15, -h / 2, 'nums', ha='right', mono=True)
    cells(ax, 0, 0, [[str(v) for v in nums]], w=w, h=h)
    y_br, y_op = -1.05, -2.0
    for i in range(n - 1):
        a, b = i * w + w / 2 + 0.07, (i + 1) * w + w / 2 - 0.07
        ax.plot([a, a, b, b], [-h - 0.05, y_br, y_br, -h - 0.05], color=SEL,
                lw=1.4, zorder=1)
        arrow(ax, ((a + b) / 2, y_br), ((a + b) / 2, y_op + 0.26), SEL,
              lw=1.3)
    pill(ax, n * w / 2, y_op, 'op(lst[i], lst[i+1])', SEL, SEL_FILL,
         mono=True, fs=9.5)
    line(ax, n * w + 0.2, y_op, [('one call of ', SEL, False),
                                 ('op', SEL, True),
                                 (' for every pair', SEL, False)], fs=9.5)
    for r, (name, res) in enumerate(rows):
        top = -2.75 - r * 1.05
        cells(ax, w / 2, top, [[str(v) for v in res]], w=w, h=h,
              fills=[[RES_FILL] * len(res)])
        text(ax, w / 2 - 0.15, top - h / 2, f'op = {name}', RES, ha='right',
             mono=True, fs=10)
        text(ax, n * w + 0.2, top - h / 2, f'pairs_op(nums, {name})',
             MUTED, mono=True, fs=9.5, ha='left')
    line(ax, n * w / 2 + 1.6, -5.1,
         [('the same loop; only the function passed as ', GREY, False),
          ('op', GREY, True), (' changes', GREY, False)], ha='center')
    return save(fig, 'w5_11_0_function_param')


FIGURES = [fig_10_0_names, fig_10_0_rebind, fig_10_0_edit_copy,
           fig_10_1_number_arg, fig_10_1_list_arg, fig_11_0_defaults,
           fig_11_0_function_param]
