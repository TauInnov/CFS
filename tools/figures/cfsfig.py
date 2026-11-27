"""Shared drawing style for the course's explanatory figures (weeks 7-13).

One visual language for every week:
- an array is drawn as cells holding the real values of the page's example;
- axis 0 (run, angle, k) is always vertical, in blue;
- axis 1 (time, repetition) is always horizontal, in orange;
- the result of an operation is green;
- every text in a figure is English.

Figures are saved as SVG (text as paths, white background) into
course/figures/, and pages show them with the {image} directive.
Run tools/figures/make_figures.py to rebuild all of them.
"""
import os
import pathlib

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt                      # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[2] / 'course' / 'figures'

# colours: line colour and a light fill for each role
AX0, AX0_FILL = '#3b6fb6', '#dce7f5'     # axis 0: run, angle, k (vertical)
AX1, AX1_FILL = '#d9822b', '#fbe6d0'     # axis 1: time, repetition (horizontal)
RES, RES_FILL = '#2e8b57', '#e1f0e6'     # the result of an operation
SEL, SEL_FILL = '#7b52ab', '#e9e0f4'     # a third highlight (a selection)
BAD, BAD_FILL = '#c0392b', '#f6dcd9'     # an error, a wrong value
GREY, GREY_FILL = '#666666', '#eeeeee'   # neutral, "not selected", False
EDGE = '#555555'
TEXT = '#222222'

MONO = 'DejaVu Sans Mono'
SANS = 'DejaVu Sans'

plt.rcParams.update({
    'svg.fonttype': 'path',      # text as paths: no font needed in the browser
    'svg.hashsalt': 'cfs',       # stable ids, so a rebuild gives the same file
    'font.family': SANS,
    'font.size': 11,
})


def new_fig(width, height, xlim, ylim):
    """A blank figure whose data units are cells: one cell is 1 wide."""
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig, ax


def cells(ax, x0, y0, values, fills=None, edges=None, w=1.0, h=0.7,
          fs=11, mono=True, color=TEXT, lw=0.9):
    """Draw a grid of cells; values is a list of rows of strings.

    (x0, y0) is the top-left corner of the first cell; rows go down.
    fills / edges: same shape as values (None = white / grey edge).
    Returns a function centre(i, j) -> (x, y) of a cell.
    """
    rows = [list(r) for r in values]
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            fc = fills[i][j] if fills is not None and fills[i][j] else 'white'
            ec = edges[i][j] if edges is not None and edges[i][j] else EDGE
            elw = 2.0 if edges is not None and edges[i][j] else lw
            ax.add_patch(Rectangle((x0 + j * w, y0 - (i + 1) * h), w, h,
                                   fc=fc, ec=ec, lw=elw, zorder=2))
            ax.text(x0 + j * w + w / 2, y0 - i * h - h / 2, v,
                    ha='center', va='center', fontsize=fs, color=color,
                    family=MONO if mono else SANS, zorder=3)

    def centre(i, j):
        return x0 + j * w + w / 2, y0 - i * h - h / 2
    return centre


def arrow(ax, start, end, color=TEXT, lw=1.6, style='->', ls='-', rad=0.0,
          ms=14):
    """A straight (or curved, rad != 0) arrow from start to end."""
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style,
                                 mutation_scale=ms, color=color, lw=lw,
                                 ls=ls, zorder=4,
                                 connectionstyle=f'arc3,rad={rad}'))


def text(ax, x, y, s, color=TEXT, fs=11, ha='center', va='center',
         mono=False, weight='normal', rotation=0):
    ax.text(x, y, s, color=color, fontsize=fs, ha=ha, va=va,
            family=MONO if mono else SANS, weight=weight,
            rotation=rotation, zorder=5)


def save(fig, name):
    """Save course/figures/<name>.svg (white background, no date)."""
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f'{name}.svg'
    fig.savefig(path, format='svg', facecolor='white', bbox_inches='tight',
                pad_inches=0.08, metadata={'Date': None})
    preview = os.environ.get('CFS_FIG_PREVIEW')   # optional PNG copies
    if preview:
        fig.savefig(pathlib.Path(preview) / f'{name}.png', dpi=110,
                    facecolor='white', bbox_inches='tight', pad_inches=0.08)
    plt.close(fig)
    return path
