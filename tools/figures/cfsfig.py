"""Shared drawing style for the course's explanatory figures (weeks 4-13).

One visual language for every week:
- an array is drawn as rounded cells holding the real values of the
  page's example;
- axis 0 (run, angle, k) is vertical, in blue; axis 1 (time, repetition)
  is horizontal, in amber; when an axis changes role (a transpose), the
  colour follows the meaning;
- the result of an operation is green, a selection violet, an error red,
  "not selected" / False a neutral grey;
- every text in a figure is English (Inter for text, JetBrains Mono NL for
  code and values, the cut without ligatures; both fonts are in tools/figures/fonts, SIL OFL).

Every figure is drawn twice: once for the light page and once for the
dark page. The theme comes from the environment variable CFS_THEME
("light" or "dark"); make_figures.py runs each week module once per theme.
The colour names below (AX0, RES_FILL, TEXT, ...) hold the values of the
current theme, so a module that imports them draws the right colours.

Files: course/figures/<name>.svg (light) and <name>-dark.svg (dark),
with a transparent background and text as paths. A page shows both with
two {image} directives, classes only-light and only-dark.
"""
import os
import pathlib

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt                      # noqa: E402
from matplotlib import font_manager                  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parents[1] / 'course' / 'figures'
THEME = os.environ.get('CFS_THEME', 'light')
assert THEME in ('light', 'dark'), THEME

for _f in sorted((HERE / 'fonts').glob('*.ttf')):
    font_manager.fontManager.addfont(str(_f))
SANS = 'Inter'
MONO = 'JetBrains Mono NL'      # the NL cut: no ligatures (>= stays >=)

_PALETTE = {
    'light': dict(
        AX0='#2563eb', AX0_FILL='#dbeafe', AX0_FILL2='#bfdbfe',
        AX1='#d97706', AX1_FILL='#fef3c7',
        AX2='#475569', AX2_FILL='#e2e8f0',
        RES='#059669', RES_FILL='#d1fae5',
        SEL='#7c3aed', SEL_FILL='#ede9fe',
        BAD='#dc2626', BAD_FILL='#fee2e2',
        GREY='#64748b', GREY_FILL='#f1f5f9',
        CELL='#f1f5f9', EDGE='#cbd5e1', TEXT='#1e293b', MUTED='#64748b',
        FADED='#94a3b8', CHIP='#0f172a', CHIP_TEXT='#f8fafc',
        PAGE='#ffffff'),
    'dark': dict(
        AX0='#60a5fa', AX0_FILL='#1e3a5f', AX0_FILL2='#27507f',
        AX1='#fbbf24', AX1_FILL='#4a3712',
        AX2='#94a3b8', AX2_FILL='#334155',
        RES='#34d399', RES_FILL='#0f3d30',
        SEL='#a78bfa', SEL_FILL='#352a5c',
        BAD='#f87171', BAD_FILL='#4c1d1d',
        GREY='#94a3b8', GREY_FILL='#1f2733',
        CELL='#1f2733', EDGE='#334155', TEXT='#e2e8f0', MUTED='#94a3b8',
        FADED='#5b6b80', CHIP='#e2e8f0', CHIP_TEXT='#0f172a',
        PAGE='#121212'),
}
globals().update(_PALETTE[THEME])
# names used by modules written for the first style
WHITE = CELL                                         # noqa: F821

plt.rcParams.update({
    'svg.fonttype': 'path',      # text as paths: no font needed in the browser
    'svg.hashsalt': 'cfs',       # stable ids, so a rebuild gives the same file
    'font.family': SANS,
    'font.size': 11,
    'text.color': TEXT,                              # noqa: F821
    'axes.labelcolor': TEXT,                         # noqa: F821
    'axes.edgecolor': EDGE,                          # noqa: F821
    'axes.facecolor': 'none',
    'figure.facecolor': 'none',
    'xtick.color': MUTED,                            # noqa: F821
    'ytick.color': MUTED,                            # noqa: F821
    'xtick.labelcolor': TEXT,                        # noqa: F821
    'ytick.labelcolor': TEXT,                        # noqa: F821
    'grid.color': EDGE,                              # noqa: F821
    'legend.frameon': False,
    'legend.labelcolor': TEXT,                       # noqa: F821
    'axes.spines.top': False,
    'axes.spines.right': False,
})


def new_fig(width, height, xlim, ylim):
    """A blank figure whose data units are cells: one cell is 1 wide."""
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig, ax


def rbox(ax, x, y, w, h, fc, ec=None, lw=0.0, r=0.1, z=2, ls='-'):
    """A rounded box with its lower-left corner at (x, y)."""
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f'round,pad=0,rounding_size={r}',
                                fc=fc, ec=ec if ec else 'none', lw=lw, ls=ls,
                                zorder=z))


def cells(ax, x0, y0, values, fills=None, edges=None, w=1.0, h=0.7,
          fs=11, mono=True, color=None, lw=0.9, gap=0.07):
    """Draw a grid of rounded cells; values is a list of rows of strings.

    (x0, y0) is the top-left corner of the first cell; rows go down.
    fills / edges: same shape as values (None = neutral cell / no edge).
    An edge colour draws a 2 pt outline in that colour (a highlight).
    Returns a function centre(i, j) -> (x, y) of a cell.
    """
    color = color or TEXT                            # noqa: F821
    rows = [list(r) for r in values]
    r = min(0.12, 0.18 * min(w, h))
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            fc = fills[i][j] if fills is not None and fills[i][j] else CELL  # noqa: F821
            if fc == 'white':
                fc = CELL                            # noqa: F821
            ec = edges[i][j] if edges is not None and edges[i][j] else None
            rbox(ax, x0 + j * w + gap / 2, y0 - (i + 1) * h + gap / 2,
                 w - gap, h - gap, fc, ec=ec, lw=2.0 if ec else 0, r=r)
            ax.text(x0 + j * w + w / 2, y0 - i * h - h / 2, v,
                    ha='center', va='center', fontsize=fs, color=color,
                    family=MONO if mono else SANS, zorder=3)

    def centre(i, j):
        return x0 + j * w + w / 2, y0 - i * h - h / 2
    return centre


def arrow(ax, start, end, color=None, lw=1.6, style='-|>', ls='-', rad=0.0,
          ms=11):
    """A straight (or curved, rad != 0) arrow from start to end."""
    if style == '->':
        style = '-|>'
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style,
                                 mutation_scale=ms, color=color or TEXT,  # noqa: F821
                                 lw=lw, ls=ls, zorder=4, capstyle='round',
                                 joinstyle='round', shrinkA=1, shrinkB=1,
                                 connectionstyle=f'arc3,rad={rad}'))


def text(ax, x, y, s, color=None, fs=11, ha='center', va='center',
         mono=False, weight='normal', rotation=0):
    if weight == 'bold' and not mono:
        weight = 'semibold'
    ax.text(x, y, s, color=color or TEXT, fontsize=fs, ha=ha, va=va,  # noqa: F821
            family=MONO if mono else SANS, weight=weight,
            rotation=rotation, zorder=5)


def pill(ax, x, y, s, fg, bg, fs=10, mono=False, ha='center', va='center',
         rotation=0):
    """A label inside a rounded coloured capsule (axis names, shapes)."""
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=fg, zorder=6,
            family=MONO if mono else SANS,
            weight='bold' if mono else 'semibold',   # the mono font has no semibold
            rotation=rotation,
            bbox=dict(boxstyle='round,pad=0.32,rounding_size=0.55', fc=bg,
                      ec='none'))


def chip(ax, x, y, code, fs=11, ha='left', va='center'):
    """A line of code in a dark (light, in dark mode) rounded chip."""
    ax.text(x, y, code, ha=ha, va=va, fontsize=fs, family=MONO, zorder=6,
            color=CHIP_TEXT,                         # noqa: F821
            bbox=dict(boxstyle='round,pad=0.42,rounding_size=0.45',
                      fc=CHIP, ec='none'))           # noqa: F821


def save(fig, name):
    """Save course/figures/<name>.svg (light) or <name>-dark.svg (dark)."""
    OUT.mkdir(parents=True, exist_ok=True)
    stem = name if THEME == 'light' else f'{name}-dark'
    path = OUT / f'{stem}.svg'
    fig.savefig(path, format='svg', transparent=True, bbox_inches='tight',
                pad_inches=0.08, metadata={'Date': None})
    preview = os.environ.get('CFS_FIG_PREVIEW')   # optional PNG copies
    if preview:
        fig.savefig(pathlib.Path(preview) / f'{stem}.png', dpi=110,
                    facecolor=PAGE, bbox_inches='tight',  # noqa: F821
                    pad_inches=0.08)
    plt.close(fig)
    return path
