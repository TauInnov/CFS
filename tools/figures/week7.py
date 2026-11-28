"""Week 7 figures: one-dimensional arrays (NumPy basics)."""
import numpy as np
from matplotlib.patches import Rectangle

from cfsfig import (AX0, AX0_FILL, AX1, AX1_FILL, BAD, BAD_FILL, GREY,
                    GREY_FILL, MUTED, RES, RES_FILL, SEL, SEL_FILL, TEXT,
                    arrow, cells, chip, new_fig, pill, save, text)

g = 9.8


def fig_for(xlim, ylim, width=6.4):
    """new_fig with the height that keeps one data unit square."""
    height = width * (ylim[1] - ylim[0]) / (xlim[1] - xlim[0])
    return new_fig(width, height, xlim, ylim)


def f1(v):
    return f'{v:.1f}'


def bracket(ax, x0, x1, y, color, label=None, below=True, fs=10):
    """A square bracket under (or over) the cells x0..x1, with a label."""
    d = -0.15 if below else 0.15
    ax.plot([x0 + 0.05, x0 + 0.05, x1 - 0.05, x1 - 0.05],
            [y, y + d, y + d, y], color=color, lw=1.6, zorder=4)
    if label:
        text(ax, (x0 + x1) / 2, y + 2.4 * d, label, color, fs=fs,
             va='top' if below else 'bottom', mono=True)


# ---------------------------------------------------------------- 7.1
def fig_7_1_loop_vs_array():
    """A loop computes one element per round; an array expression all at once."""
    y0, v0 = 0.0, 15.0
    t_list = [0.0, 0.333, 0.667, 1.0, 1.333, 1.667, 2.0, 2.333, 2.667, 3.0]
    y = [y0 + v0 * t - 0.5 * g * t**2 for t in t_list]
    n = 5                                    # cells drawn, then "..."
    tv = [str(t) for t in t_list[:n]] + ['...']
    yv = [f'{v:.2f}' for v in y[:n]] + ['...']
    w = 1.25
    fig, ax = fig_for((-2.6, 7.9), (-8.35, 0.9))

    # loop: one arrow per round, numbered
    text(ax, -2.5, 0.55, 'Loop: one element per round', ha='left',
         weight='bold')
    cells(ax, 0, 0, [tv], w=w)
    text(ax, -0.15, -0.35, 't_list', ha='right', mono=True)
    cells(ax, 0, -1.9, [yv], w=w)
    text(ax, -0.15, -2.25, 'y_loop', ha='right', mono=True)
    for j in range(n):
        x = j * w + w / 2
        arrow(ax, (x, -0.75), (x, -1.85), AX1)
        text(ax, x + 0.28, -1.3, str(j + 1), AX1, fs=9)
    text(ax, 3.7, -3.05, 'for t in t_list:  y_loop.append(...)', GREY,
         fs=10, mono=True)

    # array: one expression, every element at once
    text(ax, -2.5, -3.85, 'Array: one expression, every element at once',
         ha='left', weight='bold')
    cells(ax, 0, -4.4, [tv], w=w, fills=[[AX1_FILL] * n + [None]])
    text(ax, -0.15, -4.75, 't_arr', ha='right', mono=True)
    cells(ax, 0, -6.3, [yv], w=w, fills=[[RES_FILL] * n + [None]])
    text(ax, -0.15, -6.65, 'y_arr', ha='right', mono=True)
    for j in range(n):
        x = j * w + w / 2
        arrow(ax, (x, -5.15), (x, -6.25), RES)
    chip(ax, 3.7, -7.45, 'y_arr = y0 + v0 * t_arr - 0.5 * g * t_arr**2',
         fs=10, ha='center')
    text(ax, 3.7, -8.05, 'the same numbers, without a loop', GREY, fs=10)
    return save(fig, '7_1_loop_vs_array')


# ---------------------------------------------------------------- 7.3
def fig_7_3_shape():
    """y of shape (3, 30): rows are launch angles, columns are times."""
    v0 = 15.0
    angles_deg = np.array([30, 45, 60])
    t = np.linspace(0, 3, 30)
    theta = np.radians(angles_deg)[:, None]
    y = v0 * np.sin(theta) * t - 0.5 * g * t**2
    shown = 6
    vals = [[f1(y[i, j]) for j in range(shown)] + ['...'] for i in range(3)]
    fig, ax = fig_for((-3.4, 8.9), (-4.2, 1.7))
    cells(ax, 0, 0, vals)
    for i, a in enumerate(angles_deg):
        text(ax, -0.15, -i * 0.7 - 0.35, f'{a} deg', AX0, ha='right')
    for j in range(shown):
        text(ax, j + 0.5, 0.25, f't[{j}]', AX1, fs=10)
    text(ax, shown + 0.5, 0.25, 't[29]', AX1, fs=10)
    # the two axes
    arrow(ax, (-2.0, 0), (-2.0, -2.1), AX0, lw=2)
    pill(ax, -2.45, -1.05, '3 angles', AX0, AX0_FILL, rotation=90)
    arrow(ax, (0, 0.75), (shown + 1, 0.75), AX1, lw=2)
    pill(ax, (shown + 1) / 2, 1.15, '30 times', AX1, AX1_FILL)
    # the properties
    x = 7.4
    text(ax, x, -0.2, 'y.shape = (3, 30)', mono=True, ha='left')
    text(ax, x, -0.85, 'y.ndim  = 2', mono=True, ha='left')
    text(ax, x, -1.5, 'y.size  = 90', mono=True, ha='left')
    text(ax, x, -2.15, 'y.dtype = float64', mono=True, ha='left')
    text(ax, 3.5, -2.9, 'one row = one trajectory (one angle)', GREY,
         fs=10)
    text(ax, 3.5, -3.5, '3 x 30 = 90 elements', GREY, fs=10)
    return save(fig, '7_3_shape')


def fig_7_3_int_dtype():
    """Assigning 0.75 into an int array keeps only 0."""
    fig, ax = fig_for((-2.0, 8.9), (-3.6, 1.0), width=5.6)
    chip(ax, -1.9, 0.62, 't_bug = np.array([0, 1, 2, 3])', fs=10)
    text(ax, 5.3, 0.62, 'dtype: int64', MUTED, ha='left', mono=True, fs=10)
    cells(ax, 0, 0, [['0', '1', '2', '3']])
    text(ax, -0.15, -0.35, 't_bug', ha='right', mono=True)
    text(ax, 0.5, -1.25, 't_bug[0] = 0.75', BAD, mono=True, ha='left')
    arrow(ax, (0.5, -1.45), (0.5, -1.85), BAD)
    cells(ax, 0, -1.9, [['0', '1', '2', '3']],
          fills=[[BAD_FILL, None, None, None]],
          edges=[[BAD, None, None, None]])
    text(ax, -0.15, -2.25, 't_bug', ha='right', mono=True)
    text(ax, 4.3, -2.25, '0.75 is cut to 0, with no warning', BAD,
         ha='left', fs=10)
    text(ax, 0.5, -3.1, 'an int array keeps only whole numbers', GREY,
         ha='left', fs=10)
    return save(fig, '7_3_int_dtype')


# ---------------------------------------------------------------- 7.4
def fig_7_4_index_ruler():
    """Positive and negative indices of y, and three slices."""
    v0 = 15.0
    t = np.linspace(0, 3, 16)
    y = v0 * t - 0.5 * g * t**2
    n, w = len(y), 0.95
    vals = [f1(v) for v in y]
    fig, ax = fig_for((-0.2, n * w + 0.2), (-7.25, 1.25), width=7.4)
    # the array with its two index rows
    text(ax, 0, 1.05, 'y  (16 elements)', ha='left', mono=True)
    text(ax, n * w, 1.05, 'above: index    below: index from the end',
         GREY, fs=9, ha='right')
    for j in range(n):
        text(ax, j * w + w / 2, 0.35, str(j), AX1, fs=9)
        text(ax, j * w + w / 2, -1.05, str(j - n), GREY, fs=8.5)
    cells(ax, 0, 0, [vals], w=w, fs=8.5)

    def strip(top, picked, label):
        code, desc = label.split('   ', 1)
        fills = [[SEL_FILL if j in picked else GREY_FILL for j in range(n)]]
        shown = [[vals[j] if j in picked else '' for j in range(n)]]
        pill(ax, 0.05, top + 0.36, code.strip(), SEL, SEL_FILL, mono=True,
             ha='left', fs=10)
        text(ax, 1.75, top + 0.36, desc.strip(), MUTED, ha='left', fs=10)
        cells(ax, 0, top, shown, fills=fills, w=w, fs=8.5)

    strip(-2.1, set(range(8)), 'y[:8]    indices 0..7 (8 is not included)')
    strip(-3.65, set(range(0, n, 3)), 'y[::3]   every third, from index 0')
    strip(-5.2, set(range(n - 3, n)), 'y[-3:]   the last three')
    text(ax, 0, -6.8, 'slice [start:stop:step]: start included, '
         'stop not included', GREY, ha='left', fs=10)
    return save(fig, '7_4_index_ruler')


# ---------------------------------------------------------------- 7.5
def fig_7_5_view_copy():
    """A slice is a view of the same cells; .copy() makes new cells."""
    raw = [20.0, 18.8, -999.0, -999.0, -999.0, 5.2, 0.1]
    new = [17.6, 12.4, 8.9]
    after = raw[:2] + new + raw[5:]
    w = 1.4
    sel = [[None, None, SEL_FILL, SEL_FILL, SEL_FILL, None, None]]
    edg = [[None, None, SEL, SEL, SEL, None, None]]
    fig, ax = fig_for((-3.0, 10.1), (-10.3, 0.9), width=7.0)

    # view
    text(ax, -2.9, 0.6, 'View', ha='left', weight='bold')
    chip(ax, -1.65, 0.6, 'middle = raw_log[2:5]', fs=10.5)
    cells(ax, 0, 0, [[f1(v) for v in raw]], w=w, edges=edg, fs=10)
    text(ax, -0.15, -0.35, 'raw_log', ha='right', mono=True)
    bracket(ax, 2 * w, 5 * w, -0.8, SEL, 'middle: the same 3 cells')
    text(ax, 4.9, -1.85, 'middle[:] = [17.6, 12.4, 8.9]', SEL, mono=True)
    arrow(ax, (4.9, -2.1), (4.9, -2.6), SEL)
    cells(ax, 0, -2.65, [[f1(v) for v in after]], w=w, fills=sel, edges=edg,
          fs=10)
    text(ax, -0.15, -3.0, 'raw_log', ha='right', mono=True)
    text(ax, 4.9, -3.75, 'raw_log changed too', SEL, fs=10)

    # copy
    text(ax, -2.9, -4.75, 'Copy', ha='left', weight='bold')
    chip(ax, -1.65, -4.75, 'cleaned = raw_log2[2:5].copy()', fs=10.5)
    cells(ax, 0, -5.35, [[f1(v) for v in raw]], w=w, fs=10)
    text(ax, -0.15, -5.7, 'raw_log2', ha='right', mono=True)
    arrow(ax, (4.2, -6.1), (4.2, -7.2), RES)
    text(ax, 4.35, -6.65, '.copy(): new cells', RES, fs=10, ha='left')
    cells(ax, 2 * w, -7.25, [[f1(v) for v in new]], w=w, fs=10,
          fills=[[RES_FILL] * 3])
    text(ax, 2 * w - 0.15, -7.6, 'cleaned', ha='right', mono=True)
    text(ax, 4.9, -8.55, 'after  cleaned[:] = [17.6, 12.4, 8.9]:', GREY,
         fs=10)
    text(ax, 4.9, -9.15, 'raw_log2 is unchanged', GREY, fs=10)
    text(ax, 4.9, -9.75, '(still -999.0 in cells 2..4)', GREY, fs=10)
    return save(fig, '7_5_view_copy')


# ---------------------------------------------------------------- 7.7
def fig_7_7_scalar_array():
    """vy = v0 * np.sin(theta) - g * t: a scalar minus an array."""
    v0 = 20.0
    theta = np.radians(45)
    t = np.linspace(0, 3, 30)
    gt = g * t
    vy = v0 * np.sin(theta) - g * t
    n, w = 5, 1.25
    sc = f'{v0 * np.sin(theta):.2f}'
    fig, ax = fig_for((-4.3, 8.9), (-4.2, 1.0), width=7.0)
    chip(ax, -4.2, 0.7, 'vy = v0 * np.sin(theta) - g * t', fs=10.5)
    # the scalar: one real cell, then dashed copies for every element
    cells(ax, 0, 0, [[sc]], w=w, fills=[[AX0_FILL]])
    for j in range(1, n):
        ax.add_patch(Rectangle((j * w + 0.06, -0.64), w - 0.12, 0.58,
                               fill=False, ec=AX0, ls='--', lw=1.1,
                               zorder=3))
        text(ax, j * w + w / 2, -0.35, sc, AX0, mono=True)
    text(ax, (n + 0.5) * w, -0.35, '...', AX0, mono=True)
    text(ax, -0.15, -0.35, 'v0 * np.sin(theta)', AX0, ha='right',
         mono=True, fs=10)
    text(ax, (n + 1) * w + 0.2, -0.2, 'one number,', AX0, ha='left',
         fs=9.5)
    text(ax, (n + 1) * w + 0.2, -0.6, 'used for every t', AX0, ha='left',
         fs=9.5)
    # minus the array g * t
    cells(ax, 0, -0.9, [[f'{v:.2f}' for v in gt[:n]] + ['...']], w=w,
          fills=[[AX1_FILL] * n + [None]])
    text(ax, -0.15, -1.25, '-   g * t', AX1, ha='right', mono=True)
    text(ax, (n + 1) * w + 0.2, -1.25, '30 values', AX1, ha='left',
         fs=9.5)
    ax.plot([0, (n + 1) * w], [-1.82, -1.82], color=TEXT, lw=1.4)
    # equals vy, element by element
    cells(ax, 0, -2.0, [[f'{v:.2f}' for v in vy[:n]] + ['...']], w=w,
          fills=[[RES_FILL] * n + [None]])
    text(ax, -0.15, -2.35, 'vy', RES, ha='right', mono=True)
    text(ax, (n + 1) * w + 0.2, -2.35, '30 values', RES, ha='left',
         fs=9.5)
    text(ax, 3.7, -3.4, 'each column: the same scalar, minus one element',
         GREY, fs=10)
    return save(fig, '7_7_scalar_array')


# ---------------------------------------------------------------- 7.8
def fig_7_8_mask():
    """The mask y >= 0 near the landing, the kept values, and the landing index."""
    v0 = 15.0
    t = np.linspace(0, 4, 40)
    y = v0 * t - 0.5 * g * t**2
    above = y >= 0
    land = int(np.where(y < 0)[0][0])
    js = list(range(land - 3, land + 3))      # a window around the landing
    w = 1.3
    k = len(js)
    fig, ax = fig_for((-4.4, (k + 2) * w + 0.3), (-7.2, 1.05), width=7.0)
    text(ax, -0.15, 0.35, 'index', GREY, ha='right', fs=9.5)
    text(ax, 0.5 * w, 0.35, '...', GREY, fs=9.5)
    for m, j in enumerate(js):
        text(ax, (m + 1) * w + w / 2, 0.35, str(j), GREY, fs=9.5)
    text(ax, (k + 1) * w + w / 2, 0.35, '...', GREY, fs=9.5)
    row = lambda vals: [['...'] + vals + ['...']]   # noqa: E731
    cells(ax, 0, 0, row([f'{t[j]:.2f}' for j in js]), w=w, fs=10)
    text(ax, -0.15, -0.35, 't', ha='right', mono=True)
    cells(ax, 0, -0.9, row([f'{y[j]:.2f}' for j in js]), w=w, fs=10)
    text(ax, -0.15, -1.25, 'y', ha='right', mono=True)
    mask_fill = [None] + [SEL_FILL if above[j] else GREY_FILL for j in js] \
        + [None]
    cells(ax, 0, -2.1, row([str(bool(above[j])) for j in js]), w=w, fs=9,
          fills=[mask_fill])
    text(ax, -0.15, -2.45, 'above_ground = y >= 0', ha='right', mono=True,
         fs=10)
    # y[above_ground]: only the True cells are kept
    kept = [j for j in js if above[j]]
    for m, j in enumerate(js):
        if above[j]:
            x = (m + 1) * w + w / 2
            arrow(ax, (x, -2.85), (x, -3.5), SEL)
    cells(ax, 0, -3.55, [['...'] + [f'{y[j]:.2f}' for j in kept]], w=w,
          fs=10, fills=[[RES_FILL] * (len(kept) + 1)])
    text(ax, -0.15, -3.9, 'y[above_ground]', ha='right', mono=True,
         color=RES, fs=10)
    text(ax, (len(kept) + 1) * w + 0.2, -3.9,
         f'{above.sum()} of {len(y)} values kept', RES, fs=10,
         ha='left')
    # the landing index: the first True of y < 0
    m_land = js.index(land) + 1
    x_land = m_land * w + w / 2
    arrow(ax, (x_land, -5.0), (x_land, -2.85), BAD, lw=1.8)
    text(ax, x_land, -5.35, f'np.where(y < 0)[0][0] = {land}', BAD,
         mono=True, fs=10)
    text(ax, x_land, -5.95, f'landing_idx: t = {t[land]:.2f} s', BAD,
         fs=10)
    text(ax, 3.6, -6.75, f'y has {len(y)} values; shown: indices '
         f'{js[0]}..{js[-1]}', GREY, fs=9.5)
    return save(fig, '7_8_mask')


# ---------------------------------------------------------------- 7.10
def fig_7_10_inside_out():
    """The range formula built from the inside out, one code line per step."""
    steps = [
        (r'$\theta$ in radians', 'theta = np.radians(theta_deg)'),
        (r'$2\theta$', 'two_theta = 2 * theta'),
        (r'$\sin(2\theta)$', 'sin_two_theta = np.sin(two_theta)'),
        (r'$v_0^2 \sin(2\theta)$', 'numerator = v0**2 * sin_two_theta'),
        (r'$R = \dfrac{v_0^2 \sin(2\theta)}{g}$', 'R = numerator / g'),
    ]
    fig, ax = fig_for((-0.2, 13.4), (-7.4, 0.8), width=7.4)
    text(ax, 1.9, 0.45, 'formula, inside out', AX0, weight='bold')
    text(ax, 8.9, 0.45, 'one line of code per step', RES, weight='bold')
    fills = [AX0_FILL, AX0_FILL, AX0_FILL, AX0_FILL, RES_FILL]
    for k, (math, code) in enumerate(steps):
        top = -k * 1.45
        hgt = 1.15 if k == len(steps) - 1 else 0.85
        cells(ax, 0, top, [['']], w=3.8, h=hgt, fills=[[fills[k]]])
        ax.text(1.9, top - hgt / 2, math, ha='center', va='center',
                fontsize=12, color=TEXT, zorder=5)
        cells(ax, 4.6, top, [['']], w=8.6, h=hgt, fills=[[fills[k]]])
        text(ax, 4.8, top - hgt / 2, code, mono=True, ha='left', fs=10)
        arrow(ax, (3.85, top - hgt / 2), (4.55, top - hgt / 2), GREY)
        if k < len(steps) - 1:
            arrow(ax, (1.9, top - hgt - 0.02), (1.9, top - 1.43), AX0)
    return save(fig, '7_10_inside_out')


FIGURES = [fig_7_1_loop_vs_array, fig_7_3_shape, fig_7_3_int_dtype,
           fig_7_4_index_ruler, fig_7_5_view_copy, fig_7_7_scalar_array,
           fig_7_8_mask, fig_7_10_inside_out]
