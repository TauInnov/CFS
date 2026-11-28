"""Week 9 figures: multi-dimensional arrays (the throw array Y, 5 runs x 60 times)."""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import ConnectionPatch

from cfsfig import (AX0, AX0_FILL, AX1, AX1_FILL, AX2, AX2_FILL, BAD,
                    BAD_FILL, CELL, EDGE, FADED, GREY, GREY_FILL, MONO,
                    MUTED, PAGE, RES, RES_FILL, SEL, SEL_FILL, TEXT, arrow,
                    chip, new_fig, pill, rbox, save, text)

# the data of the week 9 pages
g, theta = 9.8, np.radians(45)
v0_runs = np.array([18.0, 19.5, 20.0, 20.5, 22.0])
t = np.linspace(0, 2 * 20.0 * np.sin(theta) / g, 60)
Y = v0_runs[:, None] * np.sin(theta) * t - 0.5 * g * t**2
SHOWN = 6                                   # time columns drawn, then "..."
X = v0_runs[:, None] * np.cos(theta) * t     # 9.1, 9.2: the x coordinate
IPU = 0.44               # inches per cell unit, as in the 9.6 figures
H = 0.7                  # cell height


def f1(v):
    return f'{v:.1f}'


def y_cells():
    return [[f'{Y[i, j]:.1f}' for j in range(SHOWN)] + ['...']
            for i in range(5)]


# ===================================================================
# drawing helpers (on top of cfsfig)
# ===================================================================
def grid(ax, x0, y0, values, fills=None, edges=None, colors=None, dashed=None,
         w=1.0, h=H, fs=11, z=2, gap=0.07):
    """Rounded cells like cfsfig.cells, with text colours, dashed cells and
    a z level.

    (x0, y0) is the top-left corner; values, fills, edges, colors, dashed
    are lists of rows. A value None leaves the place empty; an edge colour
    draws a 2 pt outline (a highlight); a dashed cell is an outline only, a
    copy that broadcasting makes, in its edge colour.
    """
    def pick(table, i, j):
        return table[i][j] if table is not None else None

    r = min(0.12, 0.18 * min(w, h))
    for i, row in enumerate(values):
        for j, v in enumerate(row):
            if v is None:
                continue
            ec, dash = pick(edges, i, j), pick(dashed, i, j)
            fc = 'none' if dash else (pick(fills, i, j) or CELL)
            rbox(ax, x0 + j * w + gap / 2, y0 - (i + 1) * h + gap / 2,
                 w - gap, h - gap, fc, ec=ec,
                 lw=1.3 if dash else (2.0 if ec else 0.0), r=r,
                 z=z + (0.2 if ec else 0), ls=(0, (3, 2)) if dash else '-')
            ax.text(x0 + j * w + w / 2, y0 - i * h - h / 2, v, ha='center',
                    va='center', fontsize=fs, family=MONO,
                    color=pick(colors, i, j) or TEXT, zorder=z + 0.5)


def ring(ax, x0, y0, i0, j0, i1, j1, color, w=1.0, h=H, gap=0.07, lw=2.0,
         z=4.5):
    """One rounded outline around the cells i0..i1, j0..j1 of a grid whose
    top-left corner is (x0, y0): a selection drawn as one group."""
    rbox(ax, x0 + j0 * w + gap / 2, y0 - (i1 + 1) * h + gap / 2,
         (j1 - j0 + 1) * w - gap, (i1 - i0 + 1) * h - gap, 'none', ec=color,
         lw=lw, r=min(0.12, 0.18 * min(w, h)), z=z)


def table(n, m, value):
    """An n x m list of lists holding one value."""
    return [[value] * m for _ in range(n)]


def axis_labels(ax, x0, y0, rows, cols, w=1.0, h=H, c0=AX0, f0=AX0_FILL,
                c1=AX1, f1=AX1_FILL, ax0='axis 0: run', ax1='axis 1: time',
                gap=1.75, lift=0.0):
    """Row labels and the axis-0 arrow on the left, column labels and the
    axis-1 arrow on top (raised by `lift`); the axis names in pills."""
    for i, r in enumerate(rows):
        text(ax, x0 - 0.15, y0 - i * h - h / 2, r, c0, ha='right')
    for j, c in enumerate(cols):
        text(ax, x0 + j * w + w / 2, y0 + 0.25 + lift, c, c1, fs=10)
    n, m = len(rows), len(cols)
    if ax0:
        arrow(ax, (x0 - gap, y0), (x0 - gap, y0 - n * h), c0, lw=2)
        pill(ax, x0 - gap - 0.45, y0 - n * h / 2, ax0, c0, f0, rotation=90)
    if ax1:
        arrow(ax, (x0, y0 + 0.75 + lift), (x0 + m * w, y0 + 0.75 + lift),
              c1, lw=2)
        pill(ax, x0 + m * w / 2, y0 + 1.17 + lift, ax1, c1, f1)


def y_labels(ax, x0, y0):
    """Run labels on the left, time labels on top, and the two axis arrows."""
    axis_labels(ax, x0, y0, [f'run {i}' for i in range(5)],
                [f't[{j}]' for j in range(SHOWN)] + ['t[59]'])


PAD = {'chip': 0.42, 'pill': 0.32}           # the bbox pads of chip / pill


def inline(ax, x, y, parts, ha='center', fs=10, gap=0.1):
    """Chips, pills and text side by side on one line, measured.

    parts: ('chip', code), ('pill', s, fg, bg), ('mono', s, color) or
    ('text', s, color); x is the left end, the centre or the right end of
    the line (ha); gap is the space between two parts, in inches.
    """
    fig = ax.figure
    ax.apply_aspect()
    ren = fig.canvas.get_renderer()
    p0 = ax.transData.transform((0, 0))[0]
    upx = 1 / (ax.transData.transform((1, 0))[0] - p0)     # units per pixel
    made = []
    for kind, s, *c in parts:
        if kind == 'chip':
            chip(ax, 0, y, s, fs=fs)
        elif kind == 'pill':
            pill(ax, 0, y, s, c[0], c[1], fs=fs, mono=True, ha='left')
        else:
            text(ax, 0, y, s, c[0], fs=fs, ha='left', mono=kind == 'mono')
        t_ = ax.texts[-1]
        pad = PAD.get(kind, 0) * fs * fig.dpi / 72 * upx
        made.append((t_, pad, t_.get_window_extent(ren).width * upx))
    sp = gap * fig.dpi * upx
    total = sum(wd + 2 * p for _, p, wd in made) + sp * (len(made) - 1)
    left = {'left': x, 'center': x - total / 2, 'right': x - total}[ha]
    for t_, p, wd in made:
        t_.set_x(left + p)
        left += wd + 2 * p + sp


def mono_parts(ax, x, y, parts, fs=11, ha='center'):
    """One monospace line written in pieces of different colours."""
    fig = ax.figure
    unit_in = fig.get_size_inches()[0] * ax.get_position().width / \
        (ax.get_xlim()[1] - ax.get_xlim()[0])
    cw = 0.6 * fs / 72 / unit_in                 # JetBrains Mono advance
    n = sum(len(s) for s, _ in parts)
    x = x - n * cw / 2 if ha == 'center' else x
    for s, c in parts:
        ax.text(x, y, s, color=c, fontsize=fs, family=MONO, ha='left',
                va='center', zorder=5)
        x += len(s) * cw


def bracket(ax, x, y_top, y_bot, color, lw=1.6):
    """A square bracket on the right of rows y_top..y_bot."""
    ax.plot([x, x + 0.15, x + 0.15, x], [y_top, y_top, y_bot, y_bot],
            color=color, lw=lw, zorder=4, solid_capstyle='round',
            solid_joinstyle='round')


def sheet(ax, x0, y0, n, m, w, h, z):
    """The card under one layer of a 3-D array; it hides what is behind."""
    p = 0.1
    rbox(ax, x0 - p, y0 - n * h - p, m * w + 2 * p, n * h + 2 * p, PAGE,
         ec=EDGE, lw=1.0, r=0.16, z=z)


def layers(ax, x0, y0, front, back, dx, dy, front_fill=None,
           front_color=None, w=1.0, h=H, fs=11):
    """Two layers of a 3-D array: back (index 1) behind front (index 0)."""
    n, m = len(back), len(back[0])
    sheet(ax, x0 + dx, y0 + dy, n, m, w, h, z=1.8)
    grid(ax, x0 + dx, y0 + dy, back, fills=table(n, m, GREY_FILL),
         colors=table(n, m, GREY), w=w, h=h, fs=fs, z=2)
    sheet(ax, x0, y0, n, m, w, h, z=2.8)
    grid(ax, x0, y0, front, fills=front_fill, colors=front_color, w=w, h=h,
         fs=fs, z=3)


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
    """A plot axes placed in inches from the figure's bottom left; its
    colours come from cfsfig's rcParams."""
    fw, fh = fig.get_size_inches()
    ax = fig.add_axes([left / fw, bottom / fh, width / fw, height / fh])
    ax.tick_params(labelsize=10)
    return ax


def link(fig, xy_a, ax_a, xy_b, ax_b, color, rad):
    """A curved arrow with a filled head from one axes to another."""
    fig.add_artist(ConnectionPatch(
        xyA=xy_a, coordsA=ax_a.transData, xyB=xy_b, coordsB=ax_b.transData,
        arrowstyle='-|>', mutation_scale=12, color=color, lw=1.6, zorder=6,
        capstyle='round', joinstyle='round',
        connectionstyle=f'arc3,rad={rad}'))


# ---------------------------------------------------------------- 9.6
def fig_9_6_mean_axis0():
    fig, ax = new_fig(6.4, 4.4, (-3.0, 7.4), (-6.0, 1.9))
    y_labels(ax, 0, 0)
    grid(ax, 0, 0, y_cells())
    for j in range(SHOWN):
        arrow(ax, (j + 0.5, -3.65), (j + 0.5, -4.4), AX0)
    grid(ax, 0, -4.45, [[f'{Y[:, j].mean():.1f}' for j in range(SHOWN)]
                        + ['...']], fills=[[RES_FILL] * (SHOWN + 1)])
    text(ax, -0.15, -4.8, 'mean', RES, ha='right')
    inline(ax, 3.5, -5.68, [('chip', 'Y.mean(axis=0)'),
                            ('pill', 'shape (5, 60) -> (60,)', RES,
                             RES_FILL)])
    return save(fig, '9_6_mean_axis0')


def fig_9_6_max_axis1():
    fig, ax = new_fig(6.4, 3.7, (-3.0, 9.4), (-4.7, 1.9))
    y_labels(ax, 0, 0)
    grid(ax, 0, 0, y_cells())
    for i in range(5):
        arrow(ax, (SHOWN + 1.05, -i * 0.7 - 0.35),
              (SHOWN + 1.8, -i * 0.7 - 0.35), AX1)
    grid(ax, SHOWN + 1.85, 0, [[f'{m:.1f}'] for m in Y.max(axis=1)],
         fills=[[RES_FILL]] * 5, w=1.3)
    text(ax, SHOWN + 2.5, 0.25, 'max', RES, fs=10)
    inline(ax, 3.5, -4.28, [('chip', 'Y.max(axis=1)'),
                            ('pill', 'shape (5, 60) -> (5,)', RES,
                             RES_FILL)])
    return save(fig, '9_6_max_axis1')


# ---------------------------------------------------------------- 9.1
def fig_9_1_runs_grid():
    """Y as a grid (a row per run, with its v0) and the same row as a curve."""
    sel = 2                                   # Y[2], the third run
    xlim, ylim = (-4.2, 8.0), (-4.3, 1.5)
    fig, ax = canvas(xlim, ylim, below=2.3)
    fills = [[SEL_FILL if i == sel else None] * (SHOWN + 1) for i in range(5)]
    grid(ax, 0, 0, y_cells(), fills=fills)
    ring(ax, 0, 0, sel, 0, sel, SHOWN, SEL)
    grid(ax, -1.55, 0, [[f1(v)] for v in v0_runs], w=1.2,
         fills=table(5, 1, AX0_FILL))
    ring(ax, -1.55, 0, sel, 0, sel, 0, SEL, w=1.2)
    text(ax, -0.95, 0.25, 'v0_runs', AX0, fs=10, mono=True)
    axis_labels(ax, -1.55, 0, [f'run {i}' for i in range(5)], [], gap=1.9,
                ax1=None)
    axis_labels(ax, 0, 0, [], [f't[{j}]' for j in range(SHOWN)] + ['t[59]'],
                ax0=None)
    pill(ax, 7.3, -sel * H - H / 2, 'Y[2]', SEL, SEL_FILL, fs=11,
         mono=True, ha='left')
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
    p.plot(t, Y[sel], color=SEL, lw=2.6, solid_capstyle='round')
    p.set_xlim(0, t[-1] * 1.02)
    p.set_ylim(0, Y.max() * 1.12)
    p.set_xlabel('t (s)', color=AX1, fontsize=11)
    p.set_ylabel('y (m)', fontsize=11)
    k = 44                                    # where the arrow meets the curve
    link(fig, (7.65, -sel * H - H / 2 - 0.32), ax, (t[k], Y[sel, k]), p, SEL,
         -0.25)
    text(p, 0.06, 13.1, 'one row of Y = one curve', SEL, fs=10, ha='left')
    return save(fig, '9_1_runs_grid')


def fig_9_1_xy_layers():
    """XY (5, 60, 2): two layers, x in front and y behind; axis 2 is depth."""
    dx, dy = 0.9, 0.7
    front = [[f1(X[i, j]) for j in range(SHOWN)] + ['...'] for i in range(5)]
    fig, ax = canvas((-3.0, 11.5), (-5.65, 1.05), ipu=0.43)
    layers(ax, 0, 0, front, y_cells(), dx, dy)
    axis_labels(ax, 0, 0, [f'run {i}' for i in range(5)], [], ax1=None)
    # time labels under the front layer (the back layer hides the top)
    for j in range(SHOWN):
        text(ax, j + 0.5, -3.87, f't[{j}]', AX1, fs=10)
    text(ax, SHOWN + 0.5, -3.87, 't[59]', AX1, fs=10)
    arrow(ax, (0, -4.25), (SHOWN + 1, -4.25), AX1, lw=2)
    pill(ax, (SHOWN + 1) / 2, -4.67, 'axis 1: time', AX1, AX1_FILL)
    # axis 2: from the front layer to the back one
    s = (SHOWN + 1.3, -3.7)
    e = (s[0] + 1.6 * dx, s[1] + 1.6 * dy)
    arrow(ax, s, e, AX2, lw=2)
    text(ax, s[0] + 0.25, s[1] - 0.2, '0: x', AX2, ha='left')
    text(ax, e[0] + 0.15, e[1] - 0.05, '1: y', AX2, ha='left')
    pill(ax, e[0] - 0.2, e[1] + 0.6, 'axis 2: coordinate', AX2, AX2_FILL,
         ha='left')
    mono_parts(ax, 3.5, -5.4, [('XY.shape = (', TEXT), ('5', AX0),
                               (', ', TEXT), ('60', AX1), (', ', TEXT),
                               ('2', AX2), (')', TEXT)])
    return save(fig, '9_1_xy_layers')


# ---------------------------------------------------------------- 9.2
def slice_panel(ax, x0, y0, title, pick, shape, meaning, xy=False):
    """A small Y (or XY) grid with index labels; the picked cells violet."""
    n, m = 5, SHOWN + 1
    fills = [[SEL_FILL if pick(i, j) else None for j in range(m)]
             for i in range(n)]
    colors = [[TEXT if pick(i, j) else FADED for j in range(m)]
              for i in range(n)]
    rows = [i for i in range(n) if any(pick(i, j) for j in range(m))]
    cols = [j for j in range(m) if any(pick(i, j) for i in range(n))]
    sel = (rows[0], cols[0], rows[-1], cols[-1])   # a block of cells
    for i in range(n):
        text(ax, x0 - 0.2, y0 - i * H - H / 2, str(i), AX0, ha='right',
             fs=10)
    arrow(ax, (x0 - 0.75, y0), (x0 - 0.75, y0 - n * H), AX0, lw=1.6, ms=11)
    if xy:
        dx, dy = 0.9, 0.7
        front = [[f1(X[i, j]) for j in range(SHOWN)] + ['...']
                 for i in range(n)]
        layers(ax, x0, y0, front, y_cells(), dx, dy, front_fill=fills,
               front_color=colors, fs=10)
        sx, sy = x0 + m + 0.25, y0 - n * H - 0.15
        arrow(ax, (sx, sy), (sx + dx, sy + dy), AX2, lw=1.6, ms=11)
        text(ax, sx + 0.05, sy - 0.3, '0', AX2, fs=10)
        text(ax, sx + dx + 0.2, sy + dy + 0.05, '1', AX2, fs=10)
        top = y0 + dy + 0.1
    else:
        grid(ax, x0, y0, y_cells(), fills=fills, colors=colors, fs=10)
        for j in range(SHOWN):
            text(ax, x0 + j + 0.5, y0 + 0.25, str(j), AX1, fs=10)
        text(ax, x0 + SHOWN + 0.5, y0 + 0.25, '59', AX1, fs=10)
        arrow(ax, (x0, y0 + 0.62), (x0 + m, y0 + 0.62), AX1, lw=1.6, ms=11)
        top = y0 + 0.62
    ring(ax, x0, y0, *sel, SEL)
    pill(ax, x0 - 0.75, top + 0.6, title, SEL, SEL_FILL, fs=11, mono=True,
         ha='left')
    pill(ax, x0 + m / 2, y0 - n * H - 0.5, shape, RES, RES_FILL, mono=True)
    text(ax, x0 + m / 2, y0 - n * H - 1.12, meaning, MUTED, fs=10)


def fig_9_2_slicing():
    """Y[1], Y[:, 2], Y[1, 2] and XY[:, :, 0], each with its shape."""
    fig, ax = canvas((-1.2, 17.75), (-11.55, 1.9), ipu=0.33)
    xr, yr = 9.2, -6.75                       # the right column, second row
    slice_panel(ax, 0, 0, 'Y[1]', lambda i, j: i == 1,
                'shape (60,)', 'run 1, every time')
    slice_panel(ax, xr, 0, 'Y[:, 2]', lambda i, j: j == 2,
                'shape (5,)', 'every run, at time 2')
    slice_panel(ax, 0, yr, 'Y[1, 2]', lambda i, j: (i, j) == (1, 2),
                f'one number: {Y[1, 2]:.1f}', 'run 1, at time 2')
    slice_panel(ax, xr, yr, 'XY[:, :, 0]', lambda i, j: True,
                'shape (5, 60)', 'x of every run, at every time', xy=True)
    return save(fig, '9_2_slicing')


def fig_9_2_row_vs_column():
    """The bug: Y[0] is a row (60,), Y[:, 0] is a column (5,)."""
    fig, ax = canvas((-1.2, 17.2), (-4.9, 1.9), ipu=0.33)
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
    pr = [list(r) for r in zip(*pl)]
    r0, wr = 9.6, 1.32
    fig, ax = canvas((-2.65, 16.35), (-4.85, 2.6), ipu=0.33)
    grid(ax, 0, 0, left, fills=pl, w=w)
    ring(ax, 0, 0, 2, 3, 2, 3, SEL, w=w)
    axis_labels(ax, 0, 0, [f'run {i}' for i in range(5)], names, w=w)
    grid(ax, r0, 0, right, fills=pr, w=wr)
    ring(ax, r0, 0, 3, 2, 3, 2, SEL, w=wr)
    axis_labels(ax, r0, 0, names, [f'run {i}' for i in range(5)], w=wr,
                c0=AX1, f0=AX1_FILL, c1=AX0, f1=AX0_FILL,
                ax0='axis 0: time', ax1='axis 1: run')
    inline(ax, 2.5 * w, 2.1, [('chip', 'Y'),
                              ('pill', '(5, 60)', TEXT, GREY_FILL)])
    inline(ax, r0 + 2.5 * wr, 2.1, [('chip', 'Y_time_major = Y.T'),
                                    ('pill', '(60, 5)', TEXT, GREY_FILL)])
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
    fig, ax = canvas((-2.75, 11.6), (-9.25, 1.55))
    vals = [[f1(Y[i, j]) for j in range(nt)] + ['...'] for i in range(5)]
    fills = table(5, nt + 1, None)
    for j in range(5):
        fills[0][j] = BAD_FILL
    grid(ax, 0, 0, vals, fills=fills)
    ring(ax, 0, 0, 0, 0, 0, 4, BAD)            # becomes wrong[0]
    ring(ax, 0, 0, 0, 5, 0, 9, BAD)            # becomes wrong[1]
    axis_labels(ax, 0, 0, [f'run {i}' for i in range(5)],
                [f't[{j}]' for j in range(nt)] + ['t[59]'])
    text(ax, 5.5, -3.95, 'reshape reads Y row by row: all of run 0, then '
         'run 1, ...', MUTED, fs=10)
    y0 = -5.55                                 # top of the two small grids

    def small(x0, rows, rlabels, rcolor, fill, edge, code, tcolor, note,
              clabels=None):
        vals = [[f1(v) for v in r] for r in rows] + [['...'] * 5]
        f = [[fill] * 5, [None] * 5, [None] * 5]
        grid(ax, x0, y0, vals, fills=f)
        for i in range(2 if edge == BAD else 1):
            ring(ax, x0, y0, i, 0, i, 4, edge)
        for i, r in enumerate(rlabels):
            text(ax, x0 - 0.15, y0 - i * H - H / 2, r, rcolor, ha='right',
                 fs=10)
        for j, c in enumerate(clabels or []):
            text(ax, x0 + j + 0.5, y0 + 0.25, c, AX0, fs=10)
        chip(ax, x0 + 2.5, y0 + 0.88, code, fs=10, ha='center')
        text(ax, x0 + 2.5, y0 - 3 * H - 0.38, note, tcolor, fs=10)

    small(-0.4, wrong[:2], ['0', '1', ''], GREY, BAD_FILL, BAD,
          'wrong = Y.reshape(n_t, n_runs)', BAD, 'row 0: run 0, t[0] to t[4]')
    small(6.3, right[:2], ['t[0]', 't[1]', ''], AX1, RES_FILL, RES,
          'right = Y.T', RES, 'row 0: t[0] of runs 0 to 4',
          clabels=[f'run {i}' for i in range(5)])
    text(ax, 4.45, -8.9, 'np.all(wrong == right)  ->  False', BAD,
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
    fig, ax = canvas((-3.0, 10.7), (-6.35, 1.65))
    grid(ax, 0, 0, y_cells())
    ny = -5 * H - gap                         # top of the new row
    grid(ax, 0, ny, [[f1(v) for v in y_new[:SHOWN]] + ['...']],
         fills=table(1, SHOWN + 1, SEL_FILL))
    ring(ax, 0, ny, 0, 0, 0, SHOWN, SEL)
    axis_labels(ax, 0, 0, [f'run {i}' for i in range(5)],
                [f't[{j}]' for j in range(SHOWN)] + ['t[59]'], ax0=None,
                lift=0.1)
    text(ax, -0.15, ny - H / 2, 'run 5', SEL, ha='right')
    arrow(ax, (-1.75, 0), (-1.75, ny - H), AX0, lw=2)
    pill(ax, -2.2, (ny - H) / 2, 'axis 0: run', AX0, AX0_FILL, rotation=90)
    # the result: a green frame around all six rows
    rbox(ax, -0.08, ny - H - 0.08, SHOWN + 1.16, -ny + H + 0.16, 'none',
         ec=RES, lw=2.2, r=0.2, z=4)
    bracket(ax, SHOWN + 1.3, -0.05, -5 * H + 0.05, TEXT)
    text(ax, SHOWN + 1.65, -1.45, 'Y', mono=True, ha='left', fs=10)
    pill(ax, SHOWN + 1.75, -2.0, '(5, 60)', TEXT, GREY_FILL, mono=True,
         ha='left')
    bracket(ax, SHOWN + 1.3, ny - 0.05, ny - H + 0.05, SEL)
    text(ax, SHOWN + 1.65, ny - 0.12, 'y_new[None, :]', SEL, mono=True,
         ha='left', fs=10)
    pill(ax, SHOWN + 1.75, ny - 0.68, '(1, 60)', SEL, SEL_FILL, mono=True,
         ha='left')
    chip(ax, 3.5, -5.22,
         'Y_extended = np.concatenate([Y, y_new[None, :]])', fs=10,
         ha='center')
    pill(ax, 3.5, -5.95, 'Y_extended.shape: (6, 60)', RES, RES_FILL,
         mono=True)
    return save(fig, '9_4_add_run')


def fig_9_4_missing_axis():
    """The bug: y_new (60,) has one axis, Y (5, 60) has two."""
    fig, ax = canvas((-3.0, 10.2), (-6.8, 1.9))
    y_labels(ax, 0, 0)
    grid(ax, 0, 0, y_cells())
    text(ax, SHOWN + 1.3, -1.4, 'index 0: Y', mono=True, ha='left', fs=10)
    text(ax, SHOWN + 1.3, -1.85, '2 dimension(s)', ha='left', fs=10)
    sy = -4.9                                  # top of the y_new strip
    grid(ax, 0, sy, [[f1(v) for v in y_new[:SHOWN]] + ['...']],
         fills=table(1, SHOWN + 1, SEL_FILL))
    text(ax, -0.15, sy - H / 2, 'y_new', SEL, mono=True, ha='right')
    arrow(ax, (0, sy - H - 0.3), (SHOWN + 1, sy - H - 0.3), AX1, lw=2)
    pill(ax, (SHOWN + 1) / 2, sy - H - 0.72, 'axis 0: time (its only axis)',
         AX1, AX1_FILL)
    text(ax, SHOWN + 1.3, sy - 0.2, 'index 1: y_new', SEL, mono=True,
         ha='left', fs=10)
    text(ax, SHOWN + 1.3, sy - 0.65, '1 dimension(s)', SEL, ha='left', fs=10)
    # the strip cannot go under Y: there is no run axis to put it on
    xa = 3.5
    arrow(ax, (xa, sy + 0.1), (xa, -5 * H - 0.12), BAD, lw=1.8)
    c, r = (xa, (sy - 5 * H) / 2), 0.22
    for d in (1, -1):
        ax.plot([c[0] - r, c[0] + r], [c[1] - d * r, c[1] + d * r],
                color=BAD, lw=2.4, zorder=6, solid_capstyle='round')
    text(ax, xa + 0.45, c[1] + 0.22, 'np.concatenate([Y, y_new])', BAD,
         mono=True, ha='left', fs=10)
    text(ax, xa + 0.45, c[1] - 0.22, '-> ValueError', BAD, mono=True,
         ha='left', fs=10)
    return save(fig, '9_4_missing_axis')


# ---------------------------------------------------------------- 9.5
def fig_9_5_broadcast():
    """v0_runs[:, None] (5, 1) and t (60,) are stretched to (5, 60)."""
    w, nc = 1.25, 4                            # cell width, columns drawn
    m = nc + 1
    r0 = 8.0
    fig, ax = canvas((-1.3, 14.35), (-9.7, 1.55), ipu=0.4)
    # v0_runs[:, None]: one column, copied along axis 1
    vv = [[f1(v)] * nc + ['...'] for v in v0_runs]
    grid(ax, 0, 0, vv, w=w, fs=10,
         fills=[[AX0_FILL] + [None] * nc] * 5,
         dashed=[[None] + [True] * nc] * 5,
         edges=[[None] + [AX0] * nc] * 5,
         colors=[[TEXT] + [AX0] * nc] * 5)
    text(ax, nc * w / 2, 0.4, 'v0_runs[:, None]', AX0, mono=True)
    arrow(ax, (-0.35, 0), (-0.35, -5 * H), AX0, lw=2)
    pill(ax, -0.8, -2.5 * H, 'axis 0: run', AX0, AX0_FILL, rotation=90)
    pill(ax, m * w / 2, -3.98, '(5, 1) -> (5, 60)', AX0, AX0_FILL, mono=True)
    # t: one row, copied along axis 0
    tv = [[f'{t[j]:.2f}' for j in range(nc)] + ['...']] * 5
    grid(ax, r0, 0, tv, w=w, fs=10,
         fills=[[AX1_FILL] * nc + [None]] + [[None] * m] * 4,
         dashed=[[None] * m] + [[True] * m] * 4,
         edges=[[None] * m] + [[AX1] * m] * 4,
         colors=[[TEXT] * m] + [[AX1] * m] * 4)
    text(ax, r0 - 0.15, -H / 2, 't', AX1, mono=True, ha='right')
    arrow(ax, (r0, 0.75), (r0 + m * w, 0.75), AX1, lw=2)
    pill(ax, r0 + m * w / 2, 1.17, 'axis 1: time', AX1, AX1_FILL)
    pill(ax, r0 + m * w / 2, -3.98, '(60,) -> (1, 60) -> (5, 60)', AX1,
         AX1_FILL, mono=True)
    # the result
    x0 = (r0 + m * w) / 2 - m * w / 2
    top = -5.3
    arrow(ax, (m * w / 2 + 0.3, -4.45), (x0 + 1.2, top - 0.1), RES)
    arrow(ax, (r0 + m * w / 2 - 0.3, -4.45), (x0 + m * w - 1.2, top - 0.1),
          RES)
    yv = [[f1(Y[i, j]) for j in range(nc)] + ['...'] for i in range(5)]
    grid(ax, x0, top, yv, w=w, fills=table(5, m, RES_FILL), fs=10)
    text(ax, x0 - 0.15, top - 2.5 * H, 'Y', RES, mono=True, ha='right')
    pill(ax, x0 + m * w + 0.3, top - 2.5 * H, 'shape (5, 60)', RES,
         RES_FILL, mono=True, ha='left')
    chip(ax, (r0 + m * w) / 2, top - 5 * H - 0.55,
         'Y = v0_runs[:, None] * np.sin(theta) * t - 0.5 * g * t**2',
         fs=10, ha='center')
    return save(fig, '9_5_broadcast')


def fig_9_5_shape_mismatch():
    """The bug: (5,) against (60,), two lengths with nothing to pair."""
    w = 1.15
    fig, ax = canvas((-3.1, 8.75), (-5.0, 0.35))
    grid(ax, 0, 0, [[f1(v) for v in v0_runs]], w=w,
         fills=[[AX0_FILL] * 5])
    grid(ax, 0, -1.5, [[f'{t[j]:.2f}' for j in range(SHOWN)] + ['...']],
         w=w, fills=[[AX1_FILL] * SHOWN + [None]])
    inline(ax, -0.15, -H / 2, [('mono', 'v0_runs', AX0),
                               ('pill', '(5,)', AX0, AX0_FILL)], ha='right',
           fs=11, gap=0.06)
    inline(ax, -0.15, -1.5 - H / 2, [('mono', 't', AX1),
                                     ('pill', '(60,)', AX1, AX1_FILL)],
           ha='right', fs=11, gap=0.06)
    for j in range(5):
        x = j * w + w / 2
        ax.plot([x, x], [-H - 0.05, -1.45], color=GREY, lw=1.2,
                ls=(0, (2, 2)), zorder=1)
    x1, x2, yb = 5 * w + 0.05, 7 * w - 0.05, -1.5 - H - 0.1
    ax.plot([x1, x1, x2, x2], [yb, yb - 0.15, yb - 0.15, yb], color=BAD,
            lw=1.6, zorder=4, solid_joinstyle='round',
            solid_capstyle='round')
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
    w = 1.2
    xlim, ylim = (-2.75, 8.05), (-4.5, 1.55)
    fig, ax = canvas(xlim, ylim, ipu=IPU7, right=2.1)
    grid(ax, 0, 0, [[f1(v) for v in r] for r in R], w=w, fs=10)
    ring(ax, 0, 0, sel, 0, sel, N - 1, SEL, w=w)
    axis_labels(ax, 0, 0, [f'{a:.0f} deg' for a in angles_deg],
                [f'rep {k}' for k in range(N)], w=w, gap=1.95,
                ax0='axis 0: angle', ax1='axis 1: repetition')
    for i in range(5):
        y = -i * H - H / 2
        arrow(ax, (N * w + 0.05, y), (N * w + 0.65, y), AX1, ms=11)
    xm = N * w + 0.7
    res = [[f1(m), f'{s:.2f}'] for m, s in zip(means, sem)]
    grid(ax, xm, 0, res, w=w, fills=table(5, 2, RES_FILL), fs=10)
    ring(ax, xm, 0, sel, 0, sel, 1, SEL, w=w)
    text(ax, xm + w / 2, 0.25, 'means', RES, mono=True, fs=10)
    text(ax, xm + 1.5 * w, 0.25, 'sem', RES, mono=True, fs=10)
    inline(ax, 2.5, -4.08, [('chip', 'R.mean(axis=1)'),
                            ('pill', 'shape (5, 4) -> (5,)', RES,
                             RES_FILL)])

    # the errorbar plot of the page, small
    gw = (xlim[1] - xlim[0]) * IPU7
    gh = (ylim[1] - ylim[0]) * IPU7
    p = inch_axes(fig, gw + 0.55, 0.6, 1.45, gh - 1.0)
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
    link(fig, (xm + 2 * w + 0.1, -sel * H - H / 2), ax, (43, means[sel]), p,
         SEL, -0.2)
    return save(fig, '9_7_errorbar')


FIGURES = [fig_9_6_mean_axis0, fig_9_6_max_axis1,
           fig_9_1_runs_grid, fig_9_1_xy_layers,
           fig_9_2_slicing, fig_9_2_row_vs_column,
           fig_9_3_transpose, fig_9_3_reshape_bug,
           fig_9_4_add_run, fig_9_4_missing_axis,
           fig_9_5_broadcast, fig_9_5_shape_mismatch,
           fig_9_7_errorbar]
