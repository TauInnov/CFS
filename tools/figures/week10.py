"""Week 10 figures: time series (diff and intervals, cumsum and trapezoid,
the update loop)."""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Rectangle

from cfsfig import (AX0, AX1, AX1_FILL, BAD, BAD_FILL, EDGE, GREY,
                    GREY_FILL, MONO, RES, RES_FILL, TEXT, arrow, new_fig,
                    save, text)


def num(v, nd=3):
    """A value as the page prints it: 15.0, 0.25, 14.902, -0.098."""
    return str(round(float(v), nd))


def grid(ax, x0, y0, values, fills=None, colors=None, edges=None, w=1.25,
         h=0.6, fs=10):
    """Cells like cfsfig.cells, with a text colour per cell.

    (x0, y0) is the top-left corner; values, fills, colors, edges are lists
    of rows (None = white fill, dark text, grey edge).
    """
    for i, row in enumerate(values):
        for j, s in enumerate(row):
            fc = fills[i][j] if fills and fills[i][j] else 'white'
            tc = colors[i][j] if colors and colors[i][j] else TEXT
            ec = edges[i][j] if edges and edges[i][j] else EDGE
            elw = 1.8 if edges and edges[i][j] else 0.9
            ax.add_patch(Rectangle((x0 + j * w, y0 - (i + 1) * h), w, h,
                                   fc=fc, ec=ec, lw=elw, zorder=2))
            ax.text(x0 + j * w + w / 2, y0 - i * h - h / 2, s, ha='center',
                    va='center', fontsize=fs, color=tc, family=MONO,
                    zorder=3)


# ---------------------------------------------------------------- 10.1
def fig_10_1_diff_intervals():
    """n points on the time axis give n - 1 intervals; diff sits in each."""
    t = np.array([0.0, 0.5, 1.0, 1.5])      # time (s)
    x = np.array([0.0, 0.25, 1.0, 2.25])    # position (m)
    v = np.diff(x) / np.diff(t)
    t_mid = (t[:-1] + t[1:]) / 2
    n = len(t)

    w, h = 1.3, 0.7
    fig, ax = new_fig(6.4, 3.9, (-2.6, 7.9), (-5.2, 1.1))
    text(ax, -0.15, -h / 2, 't', AX1, ha='right', mono=True)
    grid(ax, 0, 0, [[num(a) for a in t]], fills=[[AX1_FILL] * n], w=w, h=h,
         fs=11)
    text(ax, -0.15, -0.85 - h / 2, 'x', TEXT, ha='right', mono=True)
    grid(ax, 0, -0.85, [[num(a) for a in x]], w=w, h=h, fs=11)
    arrow(ax, (0, 0.45), (n * w, 0.45), AX1, lw=2)
    text(ax, n * w / 2, 0.8, 'time', AX1)
    text(ax, n * w + 0.3, -0.85, f'{n} points', TEXT, ha='left')

    # one interval between every two neighbours, its value at the middle
    y_cells, y_br = -0.85 - h, -1.95
    for j in range(n - 1):
        a, b = j * w + w / 2 + 0.07, (j + 1) * w + w / 2 - 0.07
        ax.plot([a, a, b, b], [y_cells - 0.05, y_br, y_br, y_cells - 0.05],
                color=AX1, lw=1.4, zorder=1)
        arrow(ax, ((a + b) / 2, y_br), ((a + b) / 2, -2.33), AX1, lw=1.4,
              ms=11)
    rows = [('np.diff(x)', [num(a) for a in np.diff(x)], RES_FILL),
            ('v', [num(a) for a in v], RES_FILL),
            ('t_mid', [num(a) for a in t_mid], AX1_FILL)]
    top = -2.35
    for i, (name, vals, fill) in enumerate(rows):
        y0 = top - i * (h + 0.12)
        text(ax, w / 2 - 0.15, y0 - h / 2, name,
             AX1 if fill == AX1_FILL else RES, ha='right', mono=True)
        grid(ax, w / 2, y0, [vals], fills=[[fill] * (n - 1)], w=w, h=h,
             fs=11)
    text(ax, n * w + 0.3, top - 0.45, f'{n - 1} intervals', RES, ha='left')
    text(ax, n * w / 2, top - 3 * (h + 0.12) - 0.25,
         'np.diff(x): shape (4,) -> (3,)', RES, mono=True)
    return save(fig, '10_1_diff_intervals')


# ---------------------------------------------------------------- 10.2
def fig_10_2_cumsum_steps():
    """np.cumsum(d): every element is the sum of the steps up to it."""
    x = np.array([0.5, 0.75, 1.5, 2.75])    # position (m)
    d = np.diff(x)                          # three differences
    c = np.cumsum(d)
    n = len(d)

    w, h, s = 1.5, 0.6, 1.6                 # cell width, height, m -> units
    gap = 0.3                               # between two columns
    fig, ax = new_fig(5.0, 4.9, (-2.9, 4.7), (-1.75, 3.75))
    for j in range(n):
        x0 = j * w + gap / 2
        for k in range(j + 1):
            y0 = c[k] * s - d[k] * s
            new = k == j
            ax.add_patch(Rectangle((x0, y0), w - gap, d[k] * s,
                                   fc=AX1_FILL if new else GREY_FILL,
                                   ec=AX1 if new else EDGE,
                                   lw=1.8 if new else 0.9, zorder=2))
            ax.text(x0 + (w - gap) / 2, y0 + d[k] * s / 2, num(d[k]),
                    ha='center', va='center', fontsize=10, family=MONO,
                    color=TEXT if new else GREY, zorder=3)
        ax.add_patch(Rectangle((x0, 0), w - gap, c[j] * s, fill=False,
                               ec=RES, lw=1.6, zorder=4))
        if j > 0:                           # the total so far, kept
            ax.plot([x0 - gap, x0], [c[j - 1] * s] * 2, color=GREY,
                    lw=1, ls='--', zorder=1)
    ax.plot([-0.1, n * w + 0.1], [0, 0], color=EDGE, lw=1.2)
    text(ax, -0.15, -0.15 - h / 2, 'd', AX1, ha='right', mono=True)
    grid(ax, 0, -0.15, [[num(a) for a in d]], fills=[[AX1_FILL] * n], w=w,
         h=h, fs=11)
    text(ax, -0.15, -0.9 - h / 2, 'np.cumsum(d)', RES, ha='right',
         mono=True)
    grid(ax, 0, -0.9, [[num(a) for a in c]], fills=[[RES_FILL] * n], w=w,
         h=h, fs=11)
    return save(fig, '10_2_cumsum_steps')


def impulse_data():
    """t_hit and F of the page's hidden cell (the force sensor)."""
    rng = np.random.default_rng(2)
    t_hit = np.round(np.arange(41) * 0.005, 3)
    F = np.where((t_hit > 0.05) & (t_hit < 0.15),
                 0.7 * np.pi / 0.2 * np.sin(np.pi * (t_hit - 0.05) / 0.1),
                 0.0)
    F = np.round(F + rng.normal(0, 0.03, t_hit.shape), 2)
    return t_hit, F


def fig_10_2_trapezoid():
    """Four force readings: three trapezoids, against four slices."""
    t_hit, F = impulse_data()
    i0, m = 11, 4                           # readings 11..14: 55 to 70 ms
    tt = t_hit[i0:i0 + m] * 1000            # ms, as in the page's plot
    FF = F[i0:i0 + m]
    F_mid = (FF[:-1] + FF[1:]) / 2
    dt = (t_hit[1] - t_hit[0]) * 1000

    fig, (top, bot) = plt.subplots(2, 1, figsize=(6.4, 5.0), sharex=True,
                                   gridspec_kw={'hspace': 0.42})
    for a in (top, bot):
        a.plot(tt, FF, 'o', color=TEXT, ms=6, zorder=5)
        for x_, f_ in zip(tt, FF):
            a.text(x_ - 0.5, f_ + 0.15, num(f_, 2), ha='right', va='bottom',
                   fontsize=10, family=MONO, color=TEXT, zorder=6)
        a.axvline(tt[-1], color=GREY, lw=1, ls=':', zorder=1)
        a.set_ylim(0, 8.4)
        a.set_ylabel('F (N)', fontsize=10)
        a.tick_params(labelsize=9)
        for side in ('right', 'top'):
            a.spines[side].set_visible(False)

    for j in range(m - 1):
        top.add_patch(Polygon([(tt[j], 0), (tt[j], FF[j]),
                               (tt[j + 1], FF[j + 1]), (tt[j + 1], 0)],
                              closed=True, fc=RES_FILL, ec=RES, lw=1.4,
                              zorder=2))
        top.plot([tt[j], tt[j + 1]], [F_mid[j]] * 2, color=RES, lw=1.2,
                 ls='--', zorder=3)
    top.text(tt[0] + dt / 2, F_mid[0] - 0.35, 'F_mid', ha='center',
             va='top', fontsize=10, family=MONO, color=RES, zorder=4)
    top.set_title(f'{m} readings bound {m - 1} intervals: '
                  'one trapezoid each', loc='left', fontsize=10, color=RES)

    for j in range(m):
        last = j == m - 1
        bot.add_patch(Rectangle((tt[j], 0), dt, FF[j],
                                fc=BAD_FILL if last else GREY_FILL,
                                ec=BAD if last else EDGE, lw=1.4, zorder=2))
    bot.text(tt[-1] + dt / 2, FF[-1] / 2, 'past the\nlast reading',
             ha='center', va='center', fontsize=9, color=BAD, zorder=4)
    bot.set_title(f'every reading times dt: {m} slices, '
                  'one step too many', loc='left', fontsize=10, color=BAD)
    bot.set_xlim(tt[0] - 4, tt[-1] + dt + 2)
    bot.set_xticks(np.append(tt, tt[-1] + dt))
    bot.set_xlabel('t (ms)', fontsize=10)
    return save(fig, '10_2_trapezoid_slices')


# ---------------------------------------------------------------- 10.3
def drag_runs():
    """v of the page's loop for three values of k (shape (3, 401))."""
    g, v0, dt = 9.8, 15.0, 0.01
    k = np.array([0.0, 0.5, 1.0])      # drag constants (1/s)
    n_steps = 401                      # 4 s
    v = np.zeros((3, n_steps))         # (k value, step)
    y = np.zeros((3, n_steps))
    v[:, 0] = v0
    for n in range(n_steps - 1):
        v[:, n + 1] = v[:, n] - (g + k * v[:, n]) * dt
        y[:, n + 1] = y[:, n] + v[:, n] * dt
    return k, v


def fig_10_3_k_step_grid():
    """The (k, step) array fills one column per round of the loop."""
    k, v = drag_runs()
    cols = 4                           # steps drawn, then "..."
    w, h = 1.3, 0.55
    fig, ax = new_fig(5.6, 6.0, (-3.3, 6.6), (-9.55, 0.95))
    text(ax, -3.2, 0.75, 'for n in range(n_steps - 1):', TEXT, fs=10,
         ha='left', mono=True)
    text(ax, -3.2, 0.3, '    v[:, n + 1] = v[:, n] - (g + k * v[:, n]) * dt',
         TEXT, fs=10, ha='left', mono=True)

    heads = ['before the loop:', 'n = 0', 'n = 1']
    for p, head in enumerate(heads):
        y_top = -1.85 - p * 2.95       # top of the grid of this panel
        y_head = y_top + (1.35 if p == 0 else 0.75)
        text(ax, -3.2, y_head, head, TEXT, fs=10, ha='left', weight='bold')
        if p == 0:
            text(ax, -0.3, y_head, 'v[:, 0] = v0', TEXT, fs=10, ha='left',
                 mono=True)
        vals, fills, colors = [], [], []
        for i in range(3):
            row, frow, crow = [], [], []
            for c in range(cols):
                if c <= p:
                    row.append(num(v[i, c]))
                    frow.append(RES_FILL if (c == p and p > 0) else None)
                    crow.append(None)
                else:
                    row.append('0.0')
                    frow.append(GREY_FILL)
                    crow.append(GREY)
            vals.append(row + ['...'])
            fills.append(frow + [GREY_FILL])
            colors.append(crow + [GREY])
        grid(ax, 0, y_top, vals, fills=fills, colors=colors, w=w, h=h)
        for i in range(3):
            text(ax, -0.15, y_top - i * h - h / 2, f'k = {k[i]}', AX0,
                 fs=10, ha='right')
        for c in range(cols):
            text(ax, c * w + w / 2, y_top + 0.22, str(c), AX1, fs=10)
        if p > 0:                      # column p - 1 gives column p
            arrow(ax, ((p - 1) * w + w / 2 + 0.1, y_top + 0.45),
                  (p * w + w / 2 - 0.1, y_top + 0.45), RES, lw=1.6, ms=12,
                  rad=-0.5)
    y0 = -1.85
    arrow(ax, (-2.35, y0), (-2.35, y0 - 3 * h), AX0, lw=2)
    text(ax, -2.6, y0 - 1.5 * h, 'axis 0: k', AX0, fs=10, rotation=90,
         ha='right')
    arrow(ax, (0, y0 + 0.55), ((cols + 1) * w, y0 + 0.55), AX1, lw=2)
    text(ax, (cols + 1) * w / 2, y0 + 0.85, 'axis 1: step n', AX1, fs=10)
    return save(fig, '10_3_k_step_grid')


def fig_10_3_dependency_chain():
    """The loop waits for every new value; the one-line version does not."""
    g, v0, dt = 9.8, 15.0, 0.01
    n_steps = int(2 * v0 / g / dt) + 1
    v_sim = np.zeros(n_steps)
    v_sim[0] = v0
    for n in range(n_steps - 1):
        v_sim[n + 1] = v_sim[n] - g * dt
    v_wrong = np.zeros(len(v_sim))
    v_wrong[0] = v0
    before = v_wrong.copy()
    v_wrong[1:] = v_wrong[:-1] - g * dt    # a wrong attempt to vectorize
    shown = 5
    w, h = 1.3, 0.6

    fig, ax = new_fig(6.2, 3.8, (-2.6, 8.0), (-5.75, 0.75))
    text(ax, -2.5, 0.45, 'the loop: every value from the one just computed',
         TEXT, fs=10, ha='left', weight='bold')
    y1 = -0.75
    text(ax, -0.15, y1 - h / 2, 'v_sim', TEXT, fs=10, ha='right', mono=True)
    grid(ax, 0, y1, [[num(a) for a in v_sim[:shown]] + ['...']],
         fills=[[None] + [RES_FILL] * (shown - 1) + [None]], w=w, h=h)
    for j in range(shown - 1):
        arrow(ax, (j * w + w / 2 + 0.1, y1 + 0.05),
              ((j + 1) * w + w / 2 - 0.1, y1 + 0.05), RES, lw=1.4, ms=11,
              rad=-0.6)

    text(ax, -2.5, -2.05, 'v_wrong[1:] = v_wrong[:-1] - g * dt', TEXT,
         fs=10, ha='left', mono=True)
    y2, y3 = -2.6, -4.55
    text(ax, -0.15, y2 - h / 2, 'before', GREY, fs=10, ha='right')
    zeros = [GREY_FILL if a == 0 else None for a in before[:shown]]
    grid(ax, 0, y2, [[num(a) for a in before[:shown]] + ['...']],
         fills=[zeros + [None]],
         colors=[[GREY if a == 0 else None for a in before[:shown]] + [None]],
         w=w, h=h)
    text(ax, -0.15, y3 - h / 2, 'after', TEXT, fs=10, ha='right')
    right = np.isclose(v_wrong[:shown], v_sim[:shown])
    grid(ax, 0, y3, [[num(a) for a in v_wrong[:shown]] + ['...']],
         fills=[[None] + [RES_FILL if r else BAD_FILL for r in right[1:]]
                + [None]], w=w, h=h)
    for j in range(shown - 1):
        good = right[j + 1]
        arrow(ax, (j * w + w / 2, y2 - h - 0.05),
              ((j + 1) * w + w / 2 - 0.15, y3 + 0.05),
              RES if good else BAD, lw=1.4, ms=11)
    text(ax, shown * w / 2 + 0.6, y3 - h - 0.45,
         'all at once, from the old zeros', BAD, fs=10)
    return save(fig, '10_3_dependency_chain')


FIGURES = [fig_10_1_diff_intervals, fig_10_2_cumsum_steps, fig_10_2_trapezoid,
           fig_10_3_k_step_grid, fig_10_3_dependency_chain]
