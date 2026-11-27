"""Week 8 figures: Matplotlib (the parts of a figure, the subplot grid,
a histogram)."""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from cfsfig import (AX0, AX1, EDGE, GREY, MONO, RES, RES_FILL, SEL, TEXT,
                    arrow, new_fig, save, text)


# ---------------------------------------------------------------- 8.1
def fig_8_1_anatomy():
    """The throw of page 8.1, every part named by the call that sets it."""
    # the page's example (8.1); the legend label is the one 8.4 uses
    g, v0 = 9.8, 20.0
    theta = np.radians(45)
    t_flight = 2 * v0 * np.sin(theta) / g
    t = np.linspace(0, t_flight, 100)
    y = v0 * np.sin(theta) * t - 0.5 * g * t**2

    fig = plt.figure(figsize=(6.4, 4.4))
    ax = fig.add_axes([0.31, 0.2, 0.38, 0.58])
    ax.plot(t, y, label=r"$\theta=45^\circ$")
    ax.set_title(r"Throw height versus time ($\theta=45^\circ$)", fontsize=10)
    ax.set_xlabel("t (s)", fontsize=10)
    ax.set_ylabel("y (m)", fontsize=10)
    ax.tick_params(labelsize=9)
    ax.legend(fontsize=9, loc='lower center')
    ax.set_facecolor('#eef3fa')

    over = fig.add_axes([0, 0, 1, 1], zorder=10)
    over.set_xlim(0, 1)
    over.set_ylim(0, 1)
    over.axis('off')
    over.patch.set_alpha(0)

    fig.canvas.draw()
    inv = fig.transFigure.inverted()

    def box(artist):
        """Corners (x0, y0, x1, y1) of an artist, in figure fractions."""
        (x0, y0), (x1, y1) = inv.transform(artist.get_window_extent())
        return x0, y0, x1, y1

    # the figure: the whole canvas
    over.add_patch(Rectangle((0.005, 0.005), 0.99, 0.99, fill=False,
                             ec=GREY, lw=1.4, ls='--'))

    def callout(xy_text, xy_to, part, call, ha='left'):
        tx, ty = xy_text
        text(over, tx, ty + 0.035, part, GREY, fs=10, ha=ha)
        text(over, tx, ty, call, SEL, fs=10, ha=ha, mono=True)
        start = (tx + (0.005 if ha == 'left' else -0.005), ty - 0.03)
        arrow(over, start, xy_to, SEL, lw=1.2, ms=10)

    text(over, 0.02, 0.955, 'fig', SEL, fs=11, ha='left', mono=True,
         weight='bold')
    text(over, 0.08, 0.955, 'the whole figure', GREY, fs=10, ha='left')

    x0, y0, x1, y1 = box(ax.title)
    callout((0.74, 0.9), (x1 + 0.005, (y0 + y1) / 2), 'title',
            'ax.set_title(...)')
    x0, y0, x1, y1 = box(ax.yaxis.label)
    callout((0.02, 0.55), (x0 - 0.005, (y0 + y1) / 2), 'y label',
            'ax.set_ylabel(...)')
    x0, y0, x1, y1 = box(ax.xaxis.label)
    callout((0.74, 0.07), (x1 + 0.01, (y0 + y1) / 2), 'x label',
            'ax.set_xlabel(...)')
    tick = [lb for lb in ax.get_xticklabels() if lb.get_text()][1]
    x0, y0, x1, y1 = box(tick)
    callout((0.02, 0.07), ((x0 + x1) / 2, y0 - 0.005), 'ticks',
            'ax.set_xticks([...])')
    x0, y0, x1, y1 = box(ax.get_legend())
    callout((0.74, 0.33), (x1 + 0.005, (y0 + y1) / 2), 'legend',
            'ax.legend()')
    j = 72                                  # a point on the falling curve
    px, py = inv.transform(ax.transData.transform((t[j], y[j])))
    callout((0.74, 0.6), (px + 0.01, py + 0.005), 'curve', 'ax.plot(t, y)')
    x0, y0, x1, y1 = box(ax.patch)
    text(over, 0.02, 0.84, 'ax', SEL, fs=11, ha='left', mono=True,
         weight='bold')
    text(over, 0.07, 0.84, 'one axes, where we draw', GREY, fs=10,
         ha='left')
    arrow(over, (0.06, 0.815), (x0 + 0.02, y1 - 0.04), SEL, lw=1.2, ms=10)
    return save(fig, '8_1_figure_axes')


# ---------------------------------------------------------------- 8.6
def panel(ax, x, y, w, h, label, fs=11):
    """One subplot drawn as an empty axes frame with its index inside."""
    ax.add_patch(Rectangle((x, y), w, h, fc='#f7f9fc', ec=EDGE, lw=1.1,
                           zorder=2))
    text(ax, x + w / 2, y + h / 2, label, TEXT, fs=fs, mono=True)


def fig_8_6_axs_grid():
    """plt.subplots(1, 3) gives axs[i]; plt.subplots(2, 2), axs[row, col]."""
    fig, ax = new_fig(6.4, 5.0, (-2.4, 7.6), (-7.2, 0.6))
    w, h, gap = 2.0, 1.15, 0.35

    # (1, 3): a one-dimensional axs, as in the page's first example
    text(ax, -2.3, 0.15, 'fig, axs = plt.subplots(1, 3, figsize=(12, 4))',
         TEXT, fs=10, ha='left', mono=True)
    for i in range(3):
        panel(ax, i * (w + gap), -1.75, w, h, f'axs[{i}]')
    text(ax, 3 * w + 2 * gap, -2.15, 'one-dimensional, shape (3,)', GREY,
         fs=10, ha='right')

    # (2, 2): a two-dimensional axs, axs[row, col]
    top = -2.85
    text(ax, -2.3, top, 'fig, axs = plt.subplots(2, 2)', TEXT, fs=10,
         ha='left', mono=True)
    x_left, w2, h2 = 1.1, 2.4, 1.15
    y_row0 = top - 1.35 - h2                 # bottom of row 0
    for r in range(2):
        for c in range(2):
            panel(ax, x_left + c * (w2 + gap), y_row0 - r * (h2 + gap), w2,
                  h2, f'axs[{r}, {c}]')
        text(ax, x_left - 0.15, y_row0 - r * (h2 + gap) + h2 / 2,
             f'row {r}', AX0, ha='right')
    for c in range(2):
        text(ax, x_left + c * (w2 + gap) + w2 / 2, y_row0 + h2 + 0.22,
             f'col {c}', AX1)
    y_bottom = y_row0 - (h2 + gap)
    arrow(ax, (-0.2, y_row0 + h2), (-0.2, y_bottom), AX0, lw=2)
    text(ax, -0.45, (y_row0 + h2 + y_bottom) / 2, 'axis 0: row', AX0,
         rotation=90, ha='right')
    x_right = x_left + 2 * w2 + gap
    arrow(ax, (x_left, y_row0 + h2 + 0.6), (x_right, y_row0 + h2 + 0.6),
          AX1, lw=2)
    text(ax, (x_left + x_right) / 2, y_row0 + h2 + 0.88, 'axis 1: col', AX1)
    text(ax, x_right, y_bottom - 0.4, 'two-dimensional, shape (2, 2)', GREY,
         fs=10, ha='right')
    return save(fig, '8_6_subplots_grid')


# ---------------------------------------------------------------- 8.8
def fig_8_8_hist_bins():
    """The 30 thermometer readings of 8.8: points, bin edges, bar heights."""
    readings = np.array([
        19.6, 20.3, 20.1, 19.8, 20.5, 20.0, 19.9, 20.2, 20.7, 19.5,
        20.1, 20.4, 19.7, 20.0, 20.3, 19.9, 20.6, 20.2, 19.8, 20.1,
        19.4, 20.0, 20.2, 20.8, 19.9, 20.3, 20.1, 19.7, 20.0, 20.4])
    counts, edges = np.histogram(readings, bins=8)    # what ax.hist counts
    n_bins = len(counts)
    which = np.clip(np.searchsorted(edges, readings, side='right') - 1,
                    0, n_bins - 1)                  # the bin of each reading
    assert (np.bincount(which, minlength=n_bins) == counts).all()

    fig, (top, bot) = plt.subplots(
        2, 1, figsize=(6.4, 4.6), sharex=True,
        gridspec_kw={'height_ratios': [1, 1.6], 'hspace': 0.22})

    # the readings as points, repeated values stacked
    seen = {}
    for r, b in zip(readings, which):
        key = round(r, 1)
        seen[key] = seen.get(key, 0) + 1
        top.plot(r, seen[key], 'o', ms=7, color=AX1, mec='white', mew=0.6,
                 zorder=3)
    top.set_ylim(0.2, max(seen.values()) + 1.4)
    top.set_yticks([])
    for side in ('left', 'right', 'top'):
        top.spines[side].set_visible(False)
    top.set_title('readings: 30 values', loc='left', color=AX1, fontsize=10)
    e = edges[4]                                      # 20.1, an edge itself
    top.annotate('on an edge: counted\nin the bin to its right',
                 xy=(e + 0.01, 4.0), xytext=(e + 0.27, 4.35), fontsize=9,
                 color=GREY, va='center', zorder=4,
                 bbox={'fc': 'white', 'ec': 'none', 'pad': 1},
                 arrowprops={'arrowstyle': '->', 'color': GREY, 'lw': 1})

    # the counts become the bar heights; one block per reading
    width = edges[1] - edges[0]
    for b in range(n_bins):
        for k in range(counts[b]):
            bot.add_patch(Rectangle((edges[b], k), width, 1, fc=RES_FILL,
                                    ec='white', lw=1.2, zorder=2))
        bot.add_patch(Rectangle((edges[b], 0), width, counts[b], fill=False,
                                ec=RES, lw=1.4, zorder=3))
        bot.text(edges[b] + width / 2, counts[b] + 0.25, str(counts[b]),
                 ha='center', va='bottom', color=RES, fontsize=11,
                 family=MONO, weight='bold')
    bot.set_ylim(0, counts.max() + 1.6)
    bot.set_ylabel('Number of readings', fontsize=10)
    bot.set_xlabel('Thermometer reading (°C)', fontsize=10)
    for side in ('right', 'top'):
        bot.spines[side].set_visible(False)
    bot.set_xticks(edges)
    bot.set_xticklabels([f'{x:g}' for x in edges], fontsize=9)
    bot.tick_params(axis='y', labelsize=9)
    bot.set_title('bins=8: 8 equal bins, from the smallest reading to the '
                  'largest', loc='left', color=GREY, fontsize=10)

    for a in (top, bot):
        for x in edges:
            a.axvline(x, color=GREY, lw=0.9, ls='--', zorder=1)
    bot.set_xlim(edges[0] - 0.06, edges[-1] + 0.06)
    return save(fig, '8_8_histogram_bins')


FIGURES = [fig_8_1_anatomy, fig_8_6_axs_grid, fig_8_8_hist_bins]
