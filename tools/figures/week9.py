"""Week 9 figures: multi-dimensional arrays (the throw array Y, 5 runs x 60 times)."""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import ConnectionPatch, Rectangle

from cfsfig import (AX0, AX0_FILL, AX1, AX1_FILL, BAD, BAD_FILL, EDGE, GREY,
                    GREY_FILL, MONO, RES, RES_FILL, SEL, SEL_FILL, TEXT,
                    arrow, cells, new_fig, save, text)

# the data of the week 9 pages
g, theta = 9.8, np.radians(45)
v0_runs = np.array([18.0, 19.5, 20.0, 20.5, 22.0])
t = np.linspace(0, 2 * 20.0 * np.sin(theta) / g, 60)
Y = v0_runs[:, None] * np.sin(theta) * t - 0.5 * g * t**2
SHOWN = 6                                   # time columns drawn, then "..."


def y_cells():
    return [[f'{Y[i, j]:.1f}' for j in range(SHOWN)] + ['...']
            for i in range(5)]


def y_labels(ax, x0, y0, h=0.7):
    """Run labels on the left, time labels on top, and the two axis arrows."""
    for i in range(5):
        text(ax, x0 - 0.15, y0 - i * h - h / 2, f'run {i}', AX0, ha='right')
    for j in range(SHOWN):
        text(ax, x0 + j + 0.5, y0 + 0.25, f't[{j}]', AX1, fs=10)
    text(ax, x0 + SHOWN + 0.5, y0 + 0.25, 't[59]', AX1, fs=10)
    arrow(ax, (x0 - 1.75, y0), (x0 - 1.75, y0 - 5 * h), AX0, lw=2)
    text(ax, x0 - 2.0, y0 - 2.5 * h, 'axis 0: run', AX0, rotation=90,
         ha='right')
    arrow(ax, (x0, y0 + 0.75), (x0 + SHOWN + 1, y0 + 0.75), AX1, lw=2)
    text(ax, x0 + (SHOWN + 1) / 2, y0 + 1.05, 'axis 1: time', AX1)


def fig_9_6_mean_axis0():
    fig, ax = new_fig(6.4, 4.3, (-3.0, 7.4), (-5.6, 1.9))
    y_labels(ax, 0, 0)
    cells(ax, 0, 0, y_cells())
    for j in range(SHOWN):
        arrow(ax, (j + 0.5, -3.65), (j + 0.5, -4.4), AX0)
    cells(ax, 0, -4.45, [[f'{Y[:, j].mean():.1f}' for j in range(SHOWN)]
                         + ['...']], fills=[[RES_FILL] * (SHOWN + 1)])
    text(ax, -0.15, -4.8, 'mean', RES, ha='right')
    text(ax, 3.5, -5.45, 'Y.mean(axis=0): shape (5, 60) -> (60,)', RES,
         mono=True)
    return save(fig, '9_6_mean_axis0')


def fig_9_6_max_axis1():
    fig, ax = new_fig(6.4, 3.6, (-3.0, 9.4), (-4.4, 1.9))
    y_labels(ax, 0, 0)
    cells(ax, 0, 0, y_cells())
    for i in range(5):
        arrow(ax, (SHOWN + 1.05, -i * 0.7 - 0.35), (SHOWN + 1.8, -i * 0.7 - 0.35),
              AX1)
    cells(ax, SHOWN + 1.85, 0, [[f'{m:.1f}'] for m in Y.max(axis=1)],
          fills=[[RES_FILL]] * 5, w=1.1)
    text(ax, SHOWN + 2.4, 0.25, 'max', RES, fs=10)
    text(ax, 3.5, -4.05, 'Y.max(axis=1): shape (5, 60) -> (5,)', RES,
         mono=True)
    return save(fig, '9_6_max_axis1')


# ===================================================================
# helpers for the figures of 9.1-9.5 and 9.7
# ===================================================================
X = v0_runs[:, None] * np.cos(theta) * t     # 9.1, 9.2: the x coordinate
AX2 = '#37474f'          # axis 2 (coordinate): a dark slate, apart from 0/1
FADED = '#a0a0a0'        # values of the cells that are not selected
IPU = 0.44               # inches per cell unit, as in the 9.6 figures
H = 0.7                  # cell height


def f1(v):
    return f'{v:.1f}'


def canvas(xlim, ylim, ipu=IPU, below=0.0, right=0.0):
    """A figure whose cell axes (1 cell = 1 unit) fill the top left.

    `below` / `right` inches stay free under / beside it for a plot.
    """
    gw = (xlim[1] - xlim[0]) * ipu
    gh = (ylim[1] - ylim[0]) * ipu
    fig = plt.figure(figsize=(gw + right, gh + below))
    ax = fig.add_axes([0, below / (gh + below), gw / (gw + right),
                       gh / (gh + below)])
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig, ax


def inch_axes(fig, left, bottom, width, height):
    """A normal plot axes placed in inches from the figure's bottom left."""
    fw, fh = fig.get_size_inches()
    ax = fig.add_axes([left / fw, bottom / fh, width / fw, height / fh])
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    ax.tick_params(labelsize=10)
    return ax


def grid(ax, x0, y0, values, fills=None, edges=None, colors=None, dashed=None,
         w=1.0, h=H, fs=11, z=2):
    """Like cfsfig.cells, with text colours, dashed cells and a z level.

    A value None leaves the place empty; a dashed cell has a dashed edge in
    its edge colour. Highlighted (edged) cells are drawn above their
    neighbours, so their whole border shows.
    """
    def pick(table, i, j):
        return table[i][j] if table is not None else None

    for i, row in enumerate(values):
        for j, v in enumerate(row):
            if v is None:
                continue
            ec, dash = pick(edges, i, j), pick(dashed, i, j)
            ax.add_patch(Rectangle(
                (x0 + j * w, y0 - (i + 1) * h), w, h,
                fc=pick(fills, i, j) or 'white', ec=ec or EDGE,
                lw=1.4 if dash else (2.0 if ec else 0.9),
                ls=(0, (3, 2)) if dash else '-',
                zorder=z + (0.2 if ec else 0)))
            ax.text(x0 + j * w + w / 2, y0 - i * h - h / 2, v, ha='center',
                    va='center', fontsize=fs, family=MONO,
                    color=pick(colors, i, j) or TEXT, zorder=z + 0.5)


def table(n, m, value):
    """An n x m list of lists holding one value."""
    return [[value] * m for _ in range(n)]


def axis_labels(ax, x0, y0, rows, cols, w=1.0, h=H, c0=AX0, c1=AX1,
                ax0='axis 0: run', ax1='axis 1: time', gap=1.75):
    """Row labels and axis-0 arrow on the left, column labels and axis-1
    arrow on top (as y_labels, for any labels and colours)."""
    for i, r in enumerate(rows):
        text(ax, x0 - 0.15, y0 - i * h - h / 2, r, c0, ha='right')
    for j, c in enumerate(cols):
        text(ax, x0 + j * w + w / 2, y0 + 0.25, c, c1, fs=10)
    n, m = len(rows), len(cols)
    if ax0:
        arrow(ax, (x0 - gap, y0), (x0 - gap, y0 - n * h), c0, lw=2)
        text(ax, x0 - gap - 0.25, y0 - n * h / 2, ax0, c0, rotation=90,
             ha='right')
    if ax1:
        arrow(ax, (x0, y0 + 0.75), (x0 + m * w, y0 + 0.75), c1, lw=2)
        text(ax, x0 + m * w / 2, y0 + 1.05, ax1, c1)


def mono_parts(ax, x, y, parts, fs=11, ha='center'):
    """One monospace line written in pieces of different colours."""
    fig = ax.figure
    unit_in = fig.get_size_inches()[0] * ax.get_position().width / \
        (ax.get_xlim()[1] - ax.get_xlim()[0])
    cw = 0.602 * fs / 72 / unit_in               # DejaVu Sans Mono advance
    n = sum(len(s) for s, _ in parts)
    x = x - n * cw / 2 if ha == 'center' else x
    for s, c in parts:
        ax.text(x, y, s, color=c, fontsize=fs, family=MONO, ha='left',
                va='center', zorder=5)
        x += len(s) * cw


def bracket(ax, x, y_top, y_bot, color, lw=1.6):
    """A square bracket on the right of rows y_top..y_bot."""
    ax.plot([x, x + 0.15, x + 0.15, x], [y_top, y_top, y_bot, y_bot],
            color=color, lw=lw, zorder=4, solid_capstyle='butt')


def layers(ax, x0, y0, front, back, dx, dy, front_fill=None,
           front_color=None, front_edge=None, w=1.0, h=H, fs=11):
    """Two layers of a 3-D array: back (index 1) behind front (index 0)."""
    n, m = len(back), len(back[0])
    grid(ax, x0 + dx, y0 + dy, back, fills=table(n, m, GREY_FILL),
         colors=table(n, m, GREY), w=w, h=h, fs=fs, z=2)
    grid(ax, x0, y0, front, fills=front_fill, colors=front_color,
         edges=front_edge, w=w, h=h, fs=fs, z=3)


# ---------------------------------------------------------------- 9.1
def fig_9_1_runs_grid():
    """Y as a grid (a row per run, with its v0) and the same row as a curve."""
    sel = 2                                   # Y[2], the third run
    xlim, ylim = (-4.2, 8.0), (-4.3, 1.4)
    fig, ax = canvas(xlim, ylim, below=2.3)
    fills = [[SEL_FILL if i == sel else None] * (SHOWN + 1) for i in range(5)]
    edges = [[SEL if i == sel else None] * (SHOWN + 1) for i in range(5)]
    grid(ax, 0, 0, y_cells(), fills=fills, edges=edges)
    grid(ax, -1.55, 0, [[f1(v)] for v in v0_runs], w=1.2,
         fills=table(5, 1, AX0_FILL),
         edges=[[SEL] if i == sel else [None] for i in range(5)])
    text(ax, -0.95, 0.25, 'v0_runs', AX0, fs=10, mono=True)
    axis_labels(ax, -1.55, 0, [f'run {i}' for i in range(5)], [], gap=1.9,
                ax1=None)
    axis_labels(ax, 0, 0, [], [f't[{j}]' for j in range(SHOWN)] + ['t[59]'],
                ax0=None)
    text(ax, 7.15, -sel * H - H / 2, 'Y[2]', SEL, mono=True, ha='left',
         weight='bold')
    mono_parts(ax, 3.5, -3.95, [('Y.shape = (', TEXT), ('5', AX0),
                                (', ', TEXT), ('60', AX1), (')', TEXT)])

    # the same rows as curves: y against t
    ipu = IPU
    left = (-1.55 - xlim[0]) * ipu
    p = inch_axes(fig, left, 0.45, (xlim[1] - 0.3 - xlim[0]) * ipu - left,
                  1.7)
    for i in range(5):
        if i != sel:
            p.plot(t, Y[i], color=FADED, lw=1.2)
    p.plot(t, Y[sel], color=SEL, lw=2.6)
    p.set_xlim(0, t[-1] * 1.02)
    p.set_ylim(0, Y.max() * 1.12)
    p.set_xlabel('t (s)', color=AX1, fontsize=11)
    p.set_ylabel('y (m)', fontsize=11)
    k = 44                                    # where the arrow meets the curve
    fig.add_artist(ConnectionPatch(
        xyA=(7.5, -sel * H - H / 2 - 0.25), coordsA=ax.transData,
        xyB=(t[k], Y[sel, k]), coordsB=p.transData, arrowstyle='->',
        mutation_scale=14, color=SEL, lw=1.6, zorder=6,
        connectionstyle='arc3,rad=-0.25'))
    text(p, 0.06, 13.1, 'one row of Y = one curve', SEL, fs=10, ha='left')
    return save(fig, '9_1_runs_grid')


def fig_9_1_xy_layers():
    """XY (5, 60, 2): two layers, x in front and y behind; axis 2 is depth."""
    dx, dy = 0.9, 0.7
    front = [[f1(X[i, j]) for j in range(SHOWN)] + ['...'] for i in range(5)]
    fig, ax = canvas((-3.0, 11.5), (-5.4, 1.05), ipu=0.43)
    layers(ax, 0, 0, front, y_cells(), dx, dy)
    axis_labels(ax, 0, 0, [f'run {i}' for i in range(5)], [], ax1=None)
    # time labels under the front layer (the back layer hides the top)
    for j in range(SHOWN):
        text(ax, j + 0.5, -3.75, f't[{j}]', AX1, fs=10)
    text(ax, SHOWN + 0.5, -3.75, 't[59]', AX1, fs=10)
    arrow(ax, (0, -4.2), (SHOWN + 1, -4.2), AX1, lw=2)
    text(ax, (SHOWN + 1) / 2, -4.55, 'axis 1: time', AX1)
    # axis 2: from the front layer to the back one
    s = (SHOWN + 1.3, -3.7)
    e = (s[0] + 1.6 * dx, s[1] + 1.6 * dy)
    arrow(ax, s, e, AX2, lw=2)
    text(ax, s[0] + 0.25, s[1] - 0.2, '0: x', AX2, ha='left')
    text(ax, e[0] + 0.15, e[1] - 0.05, '1: y', AX2, ha='left')
    text(ax, e[0] - 0.3, e[1] + 0.55, 'axis 2: coordinate', AX2, ha='left')
    mono_parts(ax, 3.5, -5.1, [('XY.shape = (', TEXT), ('5', AX0),
                               (', ', TEXT), ('60', AX1), (', ', TEXT),
                               ('2', AX2), (')', TEXT)])
    return save(fig, '9_1_xy_layers')


# ---------------------------------------------------------------- 9.2
def slice_panel(ax, x0, y0, title, pick, shape, meaning, xy=False):
    """A small Y (or XY) grid with index labels; the picked cells purple."""
    n, m = 5, SHOWN + 1
    fills = [[SEL_FILL if pick(i, j) else None for j in range(m)]
             for i in range(n)]
    edges = [[SEL if pick(i, j) else None for j in range(m)]
             for i in range(n)]
    colors = [[TEXT if pick(i, j) else FADED for j in range(m)]
              for i in range(n)]
    for i in range(n):
        text(ax, x0 - 0.2, y0 - i * H - H / 2, str(i), AX0, ha='right',
             fs=10)
    arrow(ax, (x0 - 0.75, y0), (x0 - 0.75, y0 - n * H), AX0, lw=1.6, ms=11)
    if xy:
        dx, dy = 0.9, 0.7
        front = [[f1(X[i, j]) for j in range(SHOWN)] + ['...']
                 for i in range(n)]
        layers(ax, x0, y0, front, y_cells(), dx, dy, front_fill=fills,
               front_color=colors, front_edge=edges, fs=10)
        sx, sy = x0 + m + 0.2, y0 - n * H - 0.15
        arrow(ax, (sx, sy), (sx + dx, sy + dy), AX2, lw=1.6, ms=11)
        text(ax, sx + 0.05, sy - 0.3, '0', AX2, fs=10)
        text(ax, sx + dx + 0.2, sy + dy + 0.05, '1', AX2, fs=10)
        top = y0 + dy
    else:
        grid(ax, x0, y0, y_cells(), fills=fills, edges=edges, colors=colors,
             fs=10)
        for j in range(SHOWN):
            text(ax, x0 + j + 0.5, y0 + 0.25, str(j), AX1, fs=10)
        text(ax, x0 + SHOWN + 0.5, y0 + 0.25, '59', AX1, fs=10)
        arrow(ax, (x0, y0 + 0.62), (x0 + m, y0 + 0.62), AX1, lw=1.6, ms=11)
        top = y0 + 0.62
    text(ax, x0 - 0.9, top + 0.5, title, SEL, ha='left', mono=True, fs=12,
         weight='bold')
    text(ax, x0 + m / 2, y0 - n * H - 0.4, shape, RES, mono=True, fs=10)
    text(ax, x0 + m / 2, y0 - n * H - 0.9, meaning, GREY, fs=10)


def fig_9_2_slicing():
    """Y[1], Y[:, 2], Y[1, 2] and XY[:, :, 0], each with its shape."""
    fig, ax = canvas((-1.2, 17.75), (-11.2, 1.75), ipu=0.33)
    xr = 9.2                                  # left edge of the right column
    slice_panel(ax, 0, 0, 'Y[1]', lambda i, j: i == 1,
                'shape (60,)', 'run 1, every time')
    slice_panel(ax, xr, 0, 'Y[:, 2]', lambda i, j: j == 2,
                'shape (5,)', 'every run, at time 2')
    slice_panel(ax, 0, -6.4, 'Y[1, 2]', lambda i, j: (i, j) == (1, 2),
                f'one number: {Y[1, 2]:.1f}', 'run 1, at time 2')
    slice_panel(ax, xr, -6.4, 'XY[:, :, 0]', lambda i, j: True,
                'shape (5, 60)', 'x of every run, at every time', xy=True)
    return save(fig, '9_2_slicing')


def fig_9_2_row_vs_column():
    """The bug: Y[0] is a row (60,), Y[:, 0] is a column (5,)."""
    fig, ax = canvas((-1.2, 17.2), (-4.85, 1.75), ipu=0.33)
    slice_panel(ax, 0, 0, 'Y[0]', lambda i, j: i == 0,
                'shape (60,)', 'the whole trajectory of run 0')
    slice_panel(ax, 9.2, 0, 'Y[:, 0]', lambda i, j: j == 0,
                'shape (5,)', 'the start height of every run')
    return save(fig, '9_2_row_vs_column')


# ---------------------------------------------------------------- 9.3
def fig_9_3_transpose():
    """Y.T swaps the axes: Y[2, 10] becomes Y_time_major[10, 2]."""
    js = [0, 1, None, 10, None]               # None: a "..." column / row
    names = ['t[0]', 't[1]', '', 't[10]', 't[59]']
    w = 1.2

    def val(i, j):
        return '...' if j is None else f1(Y[i, j])

    left = [[val(i, j) for j in js] for i in range(5)]
    right = [[val(i, j) for i in range(5)] for j in js]
    pl = [[SEL_FILL if (i, k) == (2, 3) else None for k in range(5)]
          for i in range(5)]
    el = [[SEL if (i, k) == (2, 3) else None for k in range(5)]
          for i in range(5)]
    pr = [list(r) for r in zip(*pl)]
    er = [list(r) for r in zip(*el)]
    r0, wr = 9.6, 1.32
    fig, ax = canvas((-2.65, 16.35), (-4.85, 2.15), ipu=0.33)
    grid(ax, 0, 0, left, fills=pl, edges=el, w=w)
    axis_labels(ax, 0, 0, [f'run {i}' for i in range(5)], names, w=w)
    grid(ax, r0, 0, right, fills=pr, edges=er, w=wr)
    axis_labels(ax, r0, 0, names, [f'run {i}' for i in range(5)], w=wr,
                c0=AX1, c1=AX0, ax0='axis 0: time', ax1='axis 1: run')
    text(ax, 2.5 * w, 1.75, 'Y  (5, 60)', mono=True, fs=10)
    text(ax, r0 + 2.5 * wr, 1.75, 'Y_time_major = Y.T  (60, 5)', mono=True,
         fs=10)
    v = f'{Y[2, 10]:.1f}'
    text(ax, 2.5 * w, -3.95, f'Y[2, 10] = {v}', SEL, mono=True, fs=10)
    text(ax, r0 + 2.5 * wr, -3.95, f'Y_time_major[10, 2] = {v}', SEL,
         mono=True, fs=10)
    arrow(ax, (2.5 * w + 1.9, -4.15), (r0 + 2.5 * wr - 3.6, -4.15), SEL,
          rad=0.3)
    return save(fig, '9_3_transpose')


def fig_9_3_reshape_bug():
    """reshape reads row by row: wrong[0] is run 0 at five times, not t[0]."""
    nt = 10                                    # time columns drawn
    wrong = Y.reshape(60, 5)
    right = Y.T
    fig, ax = canvas((-2.75, 11.6), (-8.95, 1.4))
    vals = [[f1(Y[i, j]) for j in range(nt)] + ['...'] for i in range(5)]
    fills = table(5, nt + 1, None)
    edges = table(5, nt + 1, None)
    for j in range(10):
        fills[0][j] = BAD_FILL if j < 5 else None
        edges[0][j] = BAD
    grid(ax, 0, 0, vals, fills=fills, edges=edges)
    axis_labels(ax, 0, 0, [f'run {i}' for i in range(5)],
                [f't[{j}]' for j in range(nt)] + ['t[59]'])
    text(ax, 5.5, -3.95, 'reshape reads Y row by row: all of run 0, then '
         'run 1, ...', GREY, fs=10)

    def small(x0, y0, rows, rlabels, rcolor, fill, edge, title, tcolor,
              note, clabels=None):
        vals = [[f1(v) for v in r] for r in rows] + [['...'] * 5]
        f = [[fill] * 5, [None] * 5, [None] * 5]
        e = [[edge] * 5, [edge if edge == BAD else None] * 5, [None] * 5]
        grid(ax, x0, y0, vals, fills=f, edges=e)
        for i, r in enumerate(rlabels):
            text(ax, x0 - 0.15, y0 - i * H - H / 2, r, rcolor, ha='right',
                 fs=10)
        for j, c in enumerate(clabels or []):
            text(ax, x0 + j + 0.5, y0 + 0.25, c, AX0, fs=10)
        text(ax, x0 + 2.5, y0 + (0.75 if clabels else 0.35), title, tcolor,
             mono=True, fs=10)
        text(ax, x0 + 2.5, y0 - 3 * H - 0.35, note, tcolor, fs=10)

    small(-0.4, -5.2, wrong[:2], ['0', '1', ''], GREY, BAD_FILL, BAD,
          'wrong = Y.reshape(n_t, n_runs)', BAD, 'row 0: run 0, t[0] to t[4]')
    small(6.3, -5.2, right[:2], ['t[0]', 't[1]', ''], AX1, RES_FILL, RES,
          'right = Y.T', RES, 'row 0: t[0] of runs 0 to 4',
          clabels=[f'run {i}' for i in range(5)])
    text(ax, 4.45, -8.55, 'np.all(wrong == right)  ->  False', BAD,
         mono=True)
    return save(fig, '9_3_reshape_bug')


# ---------------------------------------------------------------- 9.4
def height(v0, times):
    """The page's height(): the height (m) of one run at the given times."""
    return v0 * np.sin(theta) * times - 0.5 * g * times**2


v0_new = 21.0
y_new = height(v0_new, t)


def fig_9_4_add_run():
    """(5, 60) and (1, 60) stacked along axis 0 give (6, 60)."""
    gap = 0.25
    fig, ax = canvas((-3.0, 10.7), (-5.8, 1.4))
    grid(ax, 0, 0, y_cells())
    ny = -5 * H - gap                         # top of the new row
    grid(ax, 0, ny, [[f1(v) for v in y_new[:SHOWN]] + ['...']],
         fills=table(1, SHOWN + 1, SEL_FILL),
         edges=table(1, SHOWN + 1, SEL))
    axis_labels(ax, 0, 0, [f'run {i}' for i in range(5)],
                [f't[{j}]' for j in range(SHOWN)] + ['t[59]'], ax0=None)
    text(ax, -0.15, ny - H / 2, 'run 5', SEL, ha='right')
    arrow(ax, (-1.75, 0), (-1.75, ny - H), AX0, lw=2)
    text(ax, -2.0, (ny - H) / 2, 'axis 0: run', AX0, rotation=90, ha='right')
    # the result: a green frame around all six rows
    ax.add_patch(Rectangle((-0.1, ny - H - 0.1), SHOWN + 1.2, -ny + H + 0.2,
                           fc='none', ec=RES, lw=2.2, zorder=4))
    bracket(ax, SHOWN + 1.3, -0.05, -5 * H + 0.05, TEXT)
    text(ax, SHOWN + 1.65, -1.55, 'Y', mono=True, ha='left', fs=10)
    text(ax, SHOWN + 1.65, -1.95, '(5, 60)', mono=True, ha='left', fs=10)
    bracket(ax, SHOWN + 1.3, ny - 0.05, ny - H + 0.05, SEL)
    text(ax, SHOWN + 1.65, ny - 0.15, 'y_new[None, :]', SEL, mono=True,
         ha='left', fs=10)
    text(ax, SHOWN + 1.65, ny - 0.55, '(1, 60)', SEL, mono=True, ha='left',
         fs=10)
    text(ax, 3.5, -5.0, 'Y_extended = np.concatenate([Y, y_new[None, :]])',
         RES, mono=True, fs=10)
    text(ax, 3.5, -5.5, 'Y_extended.shape: (6, 60)', RES, mono=True, fs=10)
    return save(fig, '9_4_add_run')


def fig_9_4_missing_axis():
    """The bug: y_new (60,) has one axis, Y (5, 60) has two."""
    fig, ax = canvas((-3.0, 10.2), (-6.65, 1.4))
    y_labels(ax, 0, 0)
    grid(ax, 0, 0, y_cells())
    text(ax, SHOWN + 1.3, -1.4, 'index 0: Y', mono=True, ha='left', fs=10)
    text(ax, SHOWN + 1.3, -1.85, '2 dimension(s)', ha='left', fs=10)
    sy = -4.9                                  # top of the y_new strip
    grid(ax, 0, sy, [[f1(v) for v in y_new[:SHOWN]] + ['...']],
         fills=table(1, SHOWN + 1, SEL_FILL))
    text(ax, -0.15, sy - H / 2, 'y_new', SEL, mono=True, ha='right')
    arrow(ax, (0, sy - H - 0.3), (SHOWN + 1, sy - H - 0.3), AX1, lw=2)
    text(ax, (SHOWN + 1) / 2, sy - H - 0.65, 'axis 0: time (its only axis)',
         AX1)
    text(ax, SHOWN + 1.3, sy - 0.2, 'index 1: y_new', SEL, mono=True,
         ha='left', fs=10)
    text(ax, SHOWN + 1.3, sy - 0.65, '1 dimension(s)', SEL, ha='left', fs=10)
    # the strip cannot go under Y: there is no run axis to put it on
    xa = 3.5
    arrow(ax, (xa, sy + 0.1), (xa, -5 * H - 0.12), BAD, lw=1.8)
    c, r = (xa, (sy - 5 * H) / 2), 0.22
    ax.plot([c[0] - r, c[0] + r], [c[1] - r, c[1] + r], color=BAD, lw=2.4,
            zorder=6)
    ax.plot([c[0] - r, c[0] + r], [c[1] + r, c[1] - r], color=BAD, lw=2.4,
            zorder=6)
    text(ax, xa + 0.45, c[1] + 0.22, 'np.concatenate([Y, y_new])', BAD,
         mono=True, ha='left', fs=10)
    text(ax, xa + 0.45, c[1] - 0.22, '-> ValueError', BAD, mono=True,
         ha='left', fs=10)
    return save(fig, '9_4_missing_axis')


# ---------------------------------------------------------------- 9.5
def fig_9_5_broadcast():
    """v0_runs[:, None] (5, 1) and t (60,) are stretched to (5, 60)."""
    w, nc = 1.15, 4                            # cell width, columns drawn
    m = nc + 1
    r0 = 7.7
    fig, ax = canvas((-1.65, 13.95), (-9.55, 1.45), ipu=0.4)
    # v0_runs[:, None]: one column, copied along axis 1
    vv = [[f1(v)] * nc + ['...'] for v in v0_runs]
    grid(ax, 0, 0, vv, w=w,
         fills=[[AX0_FILL] + [None] * nc] * 5,
         dashed=[[None] + [True] * nc] * 5,
         edges=[[None] + [AX0] * nc] * 5,
         colors=[[TEXT] + [AX0] * nc] * 5)
    text(ax, nc * w / 2, 0.4, 'v0_runs[:, None]', AX0, mono=True)
    arrow(ax, (-0.35, 0), (-0.35, -5 * H), AX0, lw=2)
    text(ax, -0.6, -2.5 * H, 'axis 0: run', AX0, rotation=90, ha='right')
    text(ax, m * w / 2, -3.95, '(5, 1) -> (5, 60)', AX0, mono=True, fs=10)
    # t: one row, copied along axis 0
    tv = [[f'{t[j]:.2f}' for j in range(nc)] + ['...']] * 5
    grid(ax, r0, 0, tv, w=w,
         fills=[[AX1_FILL] * nc + [None]] + [[None] * m] * 4,
         dashed=[[None] * m] + [[True] * m] * 4,
         edges=[[None] * m] + [[AX1] * m] * 4,
         colors=[[TEXT] * m] + [[AX1] * m] * 4)
    text(ax, r0 - 0.15, -H / 2, 't', AX1, mono=True, ha='right')
    arrow(ax, (r0, 0.75), (r0 + m * w, 0.75), AX1, lw=2)
    text(ax, r0 + m * w / 2, 1.05, 'axis 1: time', AX1)
    text(ax, r0 + m * w / 2, -3.95, '(60,) -> (1, 60) -> (5, 60)', AX1,
         mono=True, fs=10)
    # the result
    x0 = (r0 + m * w) / 2 - m * w / 2
    top = -5.25
    arrow(ax, (m * w / 2 + 0.3, -4.3), (x0 + 1.2, top - 0.1), RES)
    arrow(ax, (r0 + m * w / 2 - 0.3, -4.3), (x0 + m * w - 1.2, top - 0.1),
          RES)
    yv = [[f1(Y[i, j]) for j in range(nc)] + ['...'] for i in range(5)]
    grid(ax, x0, top, yv, w=w, fills=table(5, m, RES_FILL))
    text(ax, x0 - 0.15, top - 2.5 * H, 'Y', RES, mono=True, ha='right')
    text(ax, x0 + m * w + 0.2, top - 2.5 * H, 'shape (5, 60)', RES,
         mono=True, ha='left', fs=10)
    text(ax, (r0 + m * w) / 2, top - 5 * H - 0.45,
         'Y = v0_runs[:, None] * np.sin(theta) * t - 0.5 * g * t**2', RES,
         mono=True, fs=10)
    return save(fig, '9_5_broadcast')


def fig_9_5_shape_mismatch():
    """The bug: (5,) against (60,), two lengths with nothing to pair."""
    w = 1.15
    fig, ax = canvas((-3.1, 8.75), (-5.0, 0.35))
    grid(ax, 0, 0, [[f1(v) for v in v0_runs]], w=w,
         fills=[[AX0_FILL] * 5])
    grid(ax, 0, -1.5, [[f'{t[j]:.2f}' for j in range(SHOWN)] + ['...']],
         w=w, fills=[[AX1_FILL] * SHOWN + [None]])
    text(ax, -0.15, -H / 2, 'v0_runs  (5,)', AX0, mono=True, ha='right')
    text(ax, -0.15, -1.5 - H / 2, 't  (60,)', AX1, mono=True, ha='right')
    for j in range(5):
        x = j * w + w / 2
        ax.plot([x, x], [-H - 0.05, -1.45], color=GREY, lw=1.2,
                ls=(0, (2, 2)), zorder=1)
    x1, x2, yb = 5 * w + 0.05, 7 * w - 0.05, -1.5 - H - 0.1
    ax.plot([x1, x1, x2, x2], [yb, yb - 0.15, yb - 0.15, yb], color=BAD,
            lw=1.6, zorder=4)
    text(ax, (x1 + x2) / 2, yb - 0.45, 't[5] to t[59]: no partner', BAD,
         fs=10)
    text(ax, 2.8, -3.2, '5 against 60: not equal, and neither is 1', BAD)
    text(ax, 2.8, -3.9, 'ValueError: operands could not be broadcast',
         BAD, mono=True, fs=10)
    text(ax, 2.8, -4.4, 'together with shapes (5,) (60,)', BAD, mono=True,
         fs=10)
    return save(fig, '9_5_shape_mismatch')


# ---------------------------------------------------------------- 9.7
angles_deg = np.array([15.0, 30.0, 45.0, 60.0, 75.0])
R = np.array([[19.4, 21.0, 20.2, 19.8],
              [34.1, 35.6, 34.9, 35.0],
              [39.0, 39.0, 39.0, 43.0],
              [35.8, 34.2, 35.5, 34.9],
              [20.5, 19.6, 20.1, 20.6]])


IPU7 = 0.385


def fig_9_7_errorbar():
    """R (angle, repetition): mean and sem along axis 1, then the plot."""
    N = R.shape[1]
    means = R.mean(axis=1)
    sem = R.std(axis=1, ddof=1) / np.sqrt(N)
    sel = 2                                    # the 45 degree row
    w = 1.1
    xlim, ylim = (-2.75, 7.75), (-4.35, 1.45)
    fig, ax = canvas(xlim, ylim, ipu=IPU7, right=2.25)
    ed = [[SEL if i == sel else None] * N for i in range(5)]
    grid(ax, 0, 0, [[f1(v) for v in r] for r in R], w=w, edges=ed)
    axis_labels(ax, 0, 0, [f'{a:.0f} deg' for a in angles_deg],
                [f'rep {k}' for k in range(N)], w=w, gap=1.95,
                ax0='axis 0: angle', ax1='axis 1: repetition')
    for i in range(5):
        y = -i * H - H / 2
        arrow(ax, (N * w + 0.05, y), (N * w + 0.65, y), AX1, ms=11)
    xm = N * w + 0.7
    res = [[f1(m), f'{s:.2f}'] for m, s in zip(means, sem)]
    grid(ax, xm, 0, res, w=w, fills=table(5, 2, RES_FILL),
         edges=[[SEL, SEL] if i == sel else [None, None] for i in range(5)])
    text(ax, xm + w / 2, 0.25, 'means', RES, mono=True, fs=10)
    text(ax, xm + 1.5 * w, 0.25, 'sem', RES, mono=True, fs=10)
    text(ax, 2.5, -3.95, 'R.mean(axis=1): shape (5, 4) -> (5,)', RES,
         mono=True, fs=10)

    # the errorbar plot of the page, small
    gw = (xlim[1] - xlim[0]) * IPU7
    gh = (ylim[1] - ylim[0]) * IPU7
    p = inch_axes(fig, gw + 0.55, 0.5, 1.6, gh - 0.85)
    a = np.linspace(0, 90, 200)
    p.plot(a, 20.0**2 * np.sin(np.radians(2 * a)) / g, color=FADED, lw=1.2)
    for i in range(5):
        c = SEL if i == sel else RES
        p.errorbar(angles_deg[i], means[i], yerr=sem[i], fmt='o', ms=4.5,
                   color=c, capsize=3, lw=1.4)
    p.set_xlim(0, 90)
    p.set_ylim(0, 48)
    p.set_xticks([0, 45, 90])
    p.set_yticks([0, 20, 40])
    p.set_xlabel('Launch angle (degrees)', fontsize=10)
    text(p, 0, 53, 'Range R (m)', fs=10)
    text(p, 49, 44.5, f'{means[sel]:.1f} ± {sem[sel]:.2f}', SEL, fs=10,
         ha='left')
    fig.add_artist(ConnectionPatch(
        xyA=(xm + 2 * w + 0.1, -sel * H - H / 2), coordsA=ax.transData,
        xyB=(43, means[sel]), coordsB=p.transData, arrowstyle='->',
        mutation_scale=14, color=SEL, lw=1.6, zorder=6,
        connectionstyle='arc3,rad=-0.2'))
    return save(fig, '9_7_errorbar')


FIGURES = [fig_9_6_mean_axis0, fig_9_6_max_axis1,
           fig_9_1_runs_grid, fig_9_1_xy_layers,
           fig_9_2_slicing, fig_9_2_row_vs_column,
           fig_9_3_transpose, fig_9_3_reshape_bug,
           fig_9_4_add_run, fig_9_4_missing_axis,
           fig_9_5_broadcast, fig_9_5_shape_mismatch,
           fig_9_7_errorbar]
