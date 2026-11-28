"""Week 8 figures: Matplotlib (the parts of a figure, the subplot grid,
a histogram)."""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

from cfsfig import (AX0, AX0_FILL, AX1, AX1_FILL, CELL, GREY, GREY_FILL, MONO,
                    MUTED, PAGE, RES, RES_FILL, SEL, SEL_FILL, TEXT, arrow,
                    chip, new_fig, pill, rbox, save, text)


def rrect(ax, x, y, w, h, fc, ec=None, lw=0.0, r_in=0.04, z=2, ls='-'):
    """A rounded box in axes whose x and y units differ: the corners stay
    round (radius r_in inches). Set the axis limits first."""
    p0 = ax.transData.transform((0, 0))
    px = ax.transData.transform((1, 1)) - p0         # pixels per unit
    dpi = ax.figure.dpi
    ux, uy = dpi / px[0], dpi / px[1]                # units per inch
    r = min(r_in * ux, w / 2, h / 2 * ux / uy)
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f'round,pad=0,rounding_size={r}',
                                mutation_aspect=uy / ux, fc=fc,
                                ec=ec if ec else 'none', lw=lw, ls=ls,
                                zorder=z))


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


# ---------------------------------------------------------------- 8.1
def fig_8_1_anatomy():
    """The throw of page 8.1, every part named by the call that sets it."""
    # the page's example (8.1); the legend label is the one 8.4 uses
    g, v0 = 9.8, 20.0
    theta = np.radians(45)
    t_flight = 2 * v0 * np.sin(theta) / g
    t = np.linspace(0, t_flight, 100)
    y = v0 * np.sin(theta) * t - 0.5 * g * t**2

    fig = plt.figure(figsize=(6.3, 4.4))
    ax = fig.add_axes([0.31, 0.2, 0.38, 0.58])
    ax.plot(t, y, color=AX0, lw=2, solid_capstyle='round',
            label=r"$\theta=45^\circ$")
    ax.set_title(r"Throw height versus time ($\theta=45^\circ$)", fontsize=10)
    ax.set_xlabel("t (s)", fontsize=10)
    ax.set_ylabel("y (m)", fontsize=10)
    ax.tick_params(labelsize=10)
    ax.legend(fontsize=10, loc='lower center')

    # under the plot: a rounded card that shows the area of the axes
    under = fig.add_axes([0, 0, 1, 1], zorder=-1)
    under.set_xlim(0, 1)
    under.set_ylim(0, 1)
    under.axis('off')
    over = fig.add_axes([0, 0, 1, 1], zorder=10)
    over.set_xlim(0, 1)
    over.set_ylim(0, 1)
    over.axis('off')

    fig.canvas.draw()
    inv = fig.transFigure.inverted()

    def box(artist):
        """Corners (x0, y0, x1, y1) of an artist, in figure fractions."""
        (x0, y0), (x1, y1) = inv.transform(artist.get_window_extent())
        return x0, y0, x1, y1

    x0, y0, x1, y1 = box(ax.patch)
    px, py = 0.012, 0.016                   # the card's margin
    rrect(under, x0 - px, y0 - py, x1 - x0 + 2 * px, y1 - y0 + 2 * py, CELL,
          r_in=0.1)
    # the figure: the whole canvas
    rrect(over, 0.005, 0.005, 0.99, 0.99, 'none', ec=GREY, lw=1.4, ls='--',
          r_in=0.14)

    def callout(xy_text, xy_to, part, call):
        tx, ty = xy_text
        text(over, tx, ty + 0.045, part, MUTED, fs=10, ha='left')
        pill(over, tx + 0.006, ty, call, SEL, SEL_FILL, fs=10, mono=True,
             ha='left')
        arrow(over, (tx + 0.012, ty - 0.035), xy_to, SEL, lw=1.2, ms=10)

    pill(over, 0.025, 0.95, 'fig', SEL, SEL_FILL, fs=11, mono=True,
         ha='left')
    text(over, 0.085, 0.95, 'the whole figure', MUTED, fs=10, ha='left')

    x0, y0, x1, y1 = box(ax.title)
    callout((0.73, 0.9), (x1 + 0.005, (y0 + y1) / 2), 'title',
            'ax.set_title(...)')
    x0, y0, x1, y1 = box(ax.yaxis.label)
    callout((0.02, 0.665), (x0 - 0.005, (y0 + y1) / 2), 'y label',
            'ax.set_ylabel(...)')
    x0, y0, x1, y1 = box(ax.xaxis.label)
    callout((0.73, 0.07), (x1 + 0.01, (y0 + y1) / 2), 'x label',
            'ax.set_xlabel(...)')
    tick = [lb for lb in ax.get_xticklabels() if lb.get_text()][1]
    x0, y0, x1, y1 = box(tick)
    callout((0.02, 0.07), ((x0 + x1) / 2, y0 - 0.005), 'ticks',
            'ax.set_xticks([...])')
    x0, y0, x1, y1 = box(ax.get_legend())
    callout((0.73, 0.33), (x1 + 0.005, (y0 + y1) / 2), 'legend',
            'ax.legend()')
    j = 72                                  # a point on the falling curve
    px, py = inv.transform(ax.transData.transform((t[j], y[j])))
    callout((0.73, 0.6), (px + 0.01, py + 0.005), 'curve', 'ax.plot(t, y)')
    x0, y0, x1, y1 = box(ax.patch)
    pill(over, 0.025, 0.84, 'ax', SEL, SEL_FILL, fs=11, mono=True,
         ha='left')
    text(over, 0.072, 0.84, 'one axes, where we draw', MUTED, fs=10,
         ha='left')
    arrow(over, (0.06, 0.81), (x0 + 0.02, y1 - 0.04), SEL, lw=1.2, ms=10)
    return save(fig, '8_1_figure_axes')


# ---------------------------------------------------------------- 8.6
def panel(ax, x, y, w, h, label, fs=11):
    """One subplot drawn as an empty axes card with its index inside."""
    rbox(ax, x, y, w, h, CELL, r=0.16)
    text(ax, x + w / 2, y + h / 2, label, TEXT, fs=fs, mono=True)


def fig_8_6_axs_grid():
    """plt.subplots(1, 3) gives axs[i]; plt.subplots(2, 2), axs[row, col]."""
    fig, ax = new_fig(6.4, 5.4, (-2.4, 7.6), (-7.85, 0.6))
    w, h, gap = 2.0, 1.15, 0.35

    # (1, 3): a one-dimensional axs, as in the page's first example
    chip(ax, -2.25, 0.15, 'fig, axs = plt.subplots(1, 3, figsize=(12, 4))',
         fs=10)
    for i in range(3):
        panel(ax, i * (w + gap), -1.75, w, h, f'axs[{i}]')
    inline(ax, 3 * w + 2 * gap, -2.2,
           [('text', 'one-dimensional,', MUTED),
            ('pill', 'shape (3,)', TEXT, GREY_FILL)], ha='right')

    # (2, 2): a two-dimensional axs, axs[row, col]
    top = -2.9
    chip(ax, -2.25, top, 'fig, axs = plt.subplots(2, 2)', fs=10)
    x_left, w2, h2 = 1.1, 2.4, 1.15
    y_row0 = top - 1.6 - h2                  # bottom of row 0
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
    pill(ax, -0.62, (y_row0 + h2 + y_bottom) / 2, 'axis 0: row', AX0,
         AX0_FILL, rotation=90)
    x_right = x_left + 2 * w2 + gap
    arrow(ax, (x_left, y_row0 + h2 + 0.58), (x_right, y_row0 + h2 + 0.58),
          AX1, lw=2)
    pill(ax, (x_left + x_right) / 2, y_row0 + h2 + 0.95, 'axis 1: col', AX1,
         AX1_FILL)
    inline(ax, x_right, y_bottom - 0.45,
           [('text', 'two-dimensional,', MUTED),
            ('pill', 'shape (2, 2)', TEXT, GREY_FILL)], ha='right')
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
    bot.set_xlim(edges[0] - 0.06, edges[-1] + 0.06)

    # the readings as points, repeated values stacked
    seen = {}
    for r, b in zip(readings, which):
        key = round(r, 1)
        seen[key] = seen.get(key, 0) + 1
        top.plot(r, seen[key], 'o', ms=7, color=AX1, mew=0, zorder=3)
    top.set_ylim(0.2, max(seen.values()) + 1.4)
    top.set_yticks([])
    top.spines['left'].set_visible(False)
    top.set_title('readings: 30 values', loc='left', color=AX1, fontsize=10)
    e = edges[4]                                      # 20.1, an edge itself
    top.annotate('on an edge: counted\nin the bin to its right',
                 xy=(e + 0.01, 4.0), xytext=(e + 0.27, 4.35), fontsize=10,
                 color=MUTED, va='center', zorder=4,
                 bbox={'fc': PAGE, 'ec': 'none', 'pad': 1},
                 arrowprops={'arrowstyle': '-|>', 'color': GREY, 'lw': 1,
                             'mutation_scale': 10, 'shrinkA': 2,
                             'shrinkB': 2})

    # the counts become the bar heights; one block per reading
    width = edges[1] - edges[0]
    bot.set_ylim(0, counts.max() + 1.6)
    bx, kx, ky = 0.004, 0.017, 0.13         # insets: bar, block (x and y)
    for b in range(n_bins):
        for k in range(counts[b]):
            rrect(bot, edges[b] + kx, k + ky, width - 2 * kx, 1 - 2 * ky,
                  RES_FILL, r_in=0.03)
        # the bar: from below 0, so the axis clips its lower corners
        rrect(bot, edges[b] + bx, -0.5, width - 2 * bx, counts[b] + 0.5,
              'none', ec=RES, lw=1.4, r_in=0.06, z=3)
        bot.text(edges[b] + width / 2, counts[b] + 0.25, str(counts[b]),
                 ha='center', va='bottom', color=RES, fontsize=11,
                 family=MONO, weight='bold')
    bot.set_ylabel('Number of readings', fontsize=10)
    bot.set_xlabel('Thermometer reading (°C)', fontsize=10)
    bot.set_xticks(edges)
    bot.set_xticklabels([f'{x:g}' for x in edges], fontsize=10)
    bot.tick_params(axis='y', labelsize=10)
    bot.set_title('bins=8: 8 equal bins, from the smallest reading to the '
                  'largest', loc='left', color=MUTED, fontsize=10)

    for a in (top, bot):
        for x in edges:
            a.axvline(x, color=GREY, lw=0.9, ls=(0, (3, 3)), zorder=1)
    return save(fig, '8_8_histogram_bins')


FIGURES = [fig_8_1_anatomy, fig_8_6_axs_grid, fig_8_8_hist_bins]
