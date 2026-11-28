"""Week 11 figures: pandas tables (DataFrame, Series, masks, groupby, index).

A pandas table is drawn as the arrays of weeks 7-10 with names added:
rounded cells, an index column with a grey fill and muted labels, column
names in bold above the cells, values monospace and written as pandas
prints them. A NaN cell is red; a label with no value is a dashed slot.
"""
import csv
import io
import math
import pathlib

import numpy as np

from cfsfig import (AX0, AX0_FILL, AX0_FILL2, AX1, AX1_FILL, BAD, BAD_FILL,
                    CELL, FADED, GREY, GREY_FILL, MONO, MUTED, OUT, RES,
                    RES_FILL, SEL, SEL_FILL, TEXT, arrow, cells, chip,
                    new_fig, pill, rbox, save, text)

WEEK = OUT.parent / 'weeks' / 'week_11'
NAN = float('nan')
GAP = 0.07          # the gap between two cells, as in cfsfig.cells


def fig_for(xlim, ylim, width=6.3):
    """new_fig whose axes fill the figure, so one data unit is
    width / (xlim span) inches in both directions."""
    height = width * (ylim[1] - ylim[0]) / (xlim[1] - xlim[0])
    fig, ax = new_fig(width, height, xlim, ylim)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    return fig, ax


# ------------------------------------------------------------ the data
def read_log(source):
    """Read a launch log (path or text) into {column: list}, '' -> NaN."""
    if isinstance(source, pathlib.Path):
        source = source.read_text()
    rows = list(csv.DictReader(io.StringIO(source)))
    out = {}
    for name in rows[0]:
        vals = [r[name] for r in rows]
        if all(v and '.' not in v for v in vals):
            out[name] = [int(v) for v in vals]
        else:
            out[name] = [float(v) if v else NAN for v in vals]
    return out


def shown(vals):
    """The column as pandas prints it: one number of decimals for all."""
    if all(isinstance(v, int) for v in vals):
        return [str(v) for v in vals]
    ok = [v for v in vals if not math.isnan(v)]
    d = next((d for d in range(1, 7)
              if all(abs(round(v, d) - v) < 1e-9 for v in ok)), 6)
    return ['NaN' if math.isnan(v) else f'{v:.{d}f}' for v in vals]


LOG = read_log(WEEK / 'launch_log.csv')     # df = pd.read_csv(...), 30 rows

# 11.1 and 11.2: the six runs of the first table
TABLE6 = {
    'run_id': [1, 2, 3, 4, 5, 6],
    'angle_deg': [15, 15, 15, 15, 15, 15],
    'v0_measured': [20.3, 19.0, 20.8, 20.9, 18.0, 18.7],
    'range_measured': [21.1, 18.2, 22.0, 22.1, 16.9, 18.1],
}
# 11.2: small = pd.DataFrame(...) with a missing range
SMALL3 = {
    'run_id': [1, 2, 3],
    'v0_measured': [20.3, 19.0, 20.8],
    'range_measured': [21.1, NAN, 22.0],
}
# 11.4: runs = pd.read_csv(log)
RUNS = read_log('run_id,range_measured\n1,39.5\n2,\n3,40.0\n4,40.5\n')
# 11.5: small = pd.DataFrame(...), two angles
SMALL8 = {
    'angle_deg': [45, 45, 45, 45, 60, 60, 60, 60],
    'range_measured': [9, 9, 9, 13, 17, 21, 21, 21],
}


# ------------------------------------------------------------ drawing
def table(ax, x0, y0, cols, widths, rows, index=None, index_w=0.9, h=0.55,
          fs=10, fills=None, colors=None, header=True, index_name=''):
    """A pandas-style table; (x0, y0) is the top-left of the first column.

    cols: column names (bold, above the cells); widths: their widths;
    rows: rows of strings; index: the index labels (grey cells left of
    x0), or None. fills / colors: per value cell, None = neutral cell /
    TEXT. 'NaN' is red, '...' has no cell, None is an empty dashed slot.
    Returns (xc, yc): column centres and row centres.
    """
    xs = list(np.cumsum([x0] + list(widths)))
    xc = [(a + b) / 2 for a, b in zip(xs, xs[1:])]
    r = min(0.12, 0.18 * h)
    xi = x0 - index_w                        # the index column's left edge

    def cell(x, w, yt, fc, ec=None, lw=0.0, ls='-', inset=0.0):
        rbox(ax, x + GAP / 2, yt - h + GAP / 2, w - GAP - inset, h - GAP,
             fc, ec=ec, lw=lw, r=r, ls=ls)

    def value(x, y, s, color, weight='normal'):
        ax.text(x, y, s, ha='center', va='center', fontsize=fs,
                family=MONO, color=color, weight=weight, zorder=3)

    top = y0
    if header:
        if index is not None and index_name:
            value(xi + (index_w - 0.06) / 2, y0 - h / 2 - 0.03, index_name,
                  TEXT, 'bold')
        for j, c in enumerate(cols):
            value(xc[j], y0 - h / 2 - 0.03, c, TEXT, 'bold')
        top = y0 - h
    yc = []
    for i, row in enumerate(rows):
        yt = top - i * h
        yc.append(yt - h / 2)
        if index is not None:
            if index[i] != '...':
                cell(xi, index_w, yt, GREY_FILL, inset=0.06)
            value(xi + (index_w - 0.06) / 2, yt - h / 2, index[i], MUTED)
        for j, v in enumerate(row):
            fc = fills[i][j] if fills and fills[i][j] else CELL
            col = colors[i][j] if colors and colors[i][j] else TEXT
            if v == 'NaN':
                fc, col = BAD_FILL, BAD
            if v is None:          # no value under this label: empty slot
                cell(xs[j], widths[j], yt, 'none', ec=FADED, lw=0.9,
                     ls=(0, (2, 2)))
                continue
            if v == '...':
                value(xc[j], yt - h / 2, v, MUTED)
                continue
            cell(xs[j], widths[j], yt, fc)
            value(xc[j], yt - h / 2, v, col)
    return xc, yc


def outline(ax, x0, y0, x1, y1, color, lw=2.0):
    """A rounded coloured frame around the cells (x0, y0)-(x1, y1)."""
    rbox(ax, x0 + 0.01, y1 + 0.01, x1 - x0 - 0.02, y0 - y1 - 0.02, 'none',
         ec=color, lw=lw, r=0.12, z=4)


def vbracket(ax, x, y0, y1, color, right=True, d=0.15):
    """A square bracket along x from y0 (top) to y1 (bottom)."""
    s = d if right else -d
    ax.plot([x, x + s, x + s, x], [y0 - 0.05, y0 - 0.05, y1 + 0.05,
                                   y1 + 0.05], color=color, lw=1.6, zorder=4,
            solid_capstyle='round', solid_joinstyle='round')


def hbracket(ax, x0, x1, y, color, up=False, d=0.12):
    """A square bracket along y from x0 to x1, its ends down (or up)."""
    s = d if up else -d
    ax.plot([x0 + 0.05, x0 + 0.05, x1 - 0.05, x1 - 0.05],
            [y + s, y, y, y + s], color=color, lw=1.4, zorder=4,
            solid_capstyle='round', solid_joinstyle='round')


# ---------------------------------------------------------------- 11.1
def fig_11_1_arrays_vs_table():
    """Four separate arrays (position 2 in each) vs one table (df.loc[2])."""
    names = list(TABLE6)
    w = [1.5, 1.9, 2.3, 2.7]
    h = 0.5
    gap = 0.45
    fig, ax = fig_for((-1.6, 10.3), (-8.45, 0.75), width=6.0)
    # top: four separate NumPy arrays
    text(ax, -1.5, 0.45, 'NumPy: four separate arrays', ha='left', fs=11,
         weight='bold')
    y0 = -0.45
    x = 0.0
    for name, wj in zip(names, w):
        text(ax, x + wj / 2, y0 + 0.22, name, mono=True, fs=10)
        vals = shown(TABLE6[name])
        cells(ax, x, y0, [[v] for v in vals], w=wj, h=h, fs=10,
              fills=[[SEL_FILL if i == 2 else None] for i in range(6)],
              edges=[[SEL if i == 2 else None] for i in range(6)])
        x += wj + gap
    for i in range(6):
        text(ax, -0.15, y0 - i * h - h / 2, str(i), AX0 if i != 2 else SEL,
             ha='right', mono=True, fs=10)
    pill(ax, -1.1, y0 - 3 * h, 'position', AX0, AX0_FILL, fs=10,
         rotation=90)
    text(ax, 4.6, y0 - 6 * h - 0.35,
         'run_id[2], angle_deg[2], v0_measured[2], range_measured[2]', SEL,
         mono=True, fs=10)
    # bottom: one DataFrame
    yb = -4.75
    text(ax, -1.5, yb + 0.35, 'pandas: one table', ha='left', fs=11,
         weight='bold')
    rows = list(zip(*[shown(TABLE6[n]) for n in names]))
    fills = [[SEL_FILL if i == 2 else None] * 4 for i in range(6)]
    table(ax, 0, yb, names, w, rows, index=[str(i) for i in range(6)],
          h=h, fills=fills)
    outline(ax, -0.9, yb - 3 * h, sum(w), yb - 4 * h, SEL)
    text(ax, sum(w) + 0.15, yb - 3.5 * h, 'df.loc[2]', SEL, mono=True,
         ha='left', fs=10)
    return save(fig, '11_1_arrays_vs_table')


# ---------------------------------------------------------------- 11.2
def fig_11_2_anatomy():
    """small: columns, index, values; small["range_measured"], a Series."""
    names = list(SMALL3)
    w = [1.4, 2.3, 2.9]
    h = 0.55
    W = sum(w)
    fig, ax = fig_for((-1.0, 11.75), (-3.65, 1.6), width=6.3)
    rows = list(zip(*[shown(SMALL3[n]) for n in names]))
    fills = [[None, None, SEL_FILL] for _ in range(3)]
    table(ax, 0, 0, names, w, rows, index=['0', '1', '2'], index_w=0.8,
          h=h, fills=fills)
    outline(ax, w[0] + w[1], 0, W, -4 * h, SEL)
    text(ax, -0.8, 1.3, 'DataFrame', ha='left', fs=11, weight='bold')
    text(ax, 1.65, 1.3, 'small', ha='left', mono=True, fs=11)
    # the three parts
    hbracket(ax, 0, W, 0.14, MUTED)
    text(ax, W / 2, 0.42, 'columns', fs=10)
    hbracket(ax, -0.8, -0.06, -4 * h - 0.17, MUTED, up=True)
    text(ax, -0.43, -4 * h - 0.47, 'index', GREY, fs=10)
    hbracket(ax, 0, W, -4 * h - 0.17, MUTED, up=True)
    text(ax, W / 2, -4 * h - 0.47, 'values', fs=10)
    # the Series: one column with its index
    xs = W + 2.6
    arrow(ax, (W + 0.12, -2.5 * h), (xs - 0.95, -2.5 * h), SEL)
    table(ax, xs, -h, ['range_measured'], [1.3],
          [[v] for v in shown(SMALL3['range_measured'])],
          index=['0', '1', '2'], index_w=0.8, h=h, header=False)
    text(ax, xs + 0.25, 1.3, 'Series', SEL, fs=11, weight='bold')
    text(ax, xs + 0.25, 0.75, 'small["range_measured"]', SEL, mono=True,
         fs=10)
    text(ax, xs + 1.3, -4 * h - 0.85, 'Name: range_measured, dtype: float64',
         MUTED, mono=True, fs=10, ha='right')
    return save(fig, '11_2_anatomy')


def fig_11_2_col_vs_cols():
    """df["angle_deg"] (a 1-D Series) vs df[["angle_deg"]] (a DataFrame)."""
    h = 0.5
    vals = [[v] for v in shown(TABLE6['angle_deg'])]
    idx = [str(i) for i in range(6)]
    cw = 1.8
    fig, ax = fig_for((-2.3, 10.6), (-5.45, 1.35), width=5.6)
    # left: the Series, no header row; its name is kept apart
    chip(ax, 0.45, 1.0, 'df["angle_deg"]', fs=11, ha='center')
    table(ax, 0, -h, ['angle_deg'], [cw], vals, index=idx, h=h,
          header=False)
    text(ax, 0.45, -7 * h - 0.35, 'Name: angle_deg', GREY, mono=True,
         fs=10)
    arrow(ax, (-1.25, -h), (-1.25, -7 * h), AX0, lw=2)
    pill(ax, -1.75, -4 * h, 'axis 0', AX0, AX0_FILL, fs=10, rotation=90)
    text(ax, 0.45, -7 * h - 1.0, 'Series', RES, fs=11, weight='bold')
    pill(ax, 0.45, -7 * h - 1.6, 'shape (6,)', RES, RES_FILL, fs=11,
         mono=True)
    # right: the DataFrame, with a header row
    x0 = 7.2
    chip(ax, x0 + 0.45, 1.0, 'df[["angle_deg"]]', fs=11, ha='center')
    table(ax, x0, 0, ['angle_deg'], [cw], vals, index=idx, h=h)
    arrow(ax, (x0 - 1.25, -h), (x0 - 1.25, -7 * h), AX0, lw=2)
    pill(ax, x0 - 1.75, -4 * h, 'axis 0', AX0, AX0_FILL, fs=10, rotation=90)
    arrow(ax, (x0, 0.3), (x0 + cw, 0.3), AX1, lw=2)
    pill(ax, x0 + cw + 0.2, 0.3, 'axis 1', AX1, AX1_FILL, fs=10, ha='left')
    text(ax, x0 + 0.45, -7 * h - 1.0, 'DataFrame', RES, fs=11,
         weight='bold')
    pill(ax, x0 + 0.45, -7 * h - 1.6, 'shape (6, 1)', RES, RES_FILL, fs=11,
         mono=True)
    return save(fig, '11_2_col_vs_cols')


# ---------------------------------------------------------------- 11.4
def fig_11_4_mask():
    """mask_45 next to the rows of df; df[mask_45] keeps the True rows."""
    names = ['run_id', 'angle_deg', 'v0_measured', 'range_measured']
    w = [1.35, 1.9, 2.3, 2.85]
    W = sum(w)
    h = 0.5
    col = {n: shown(LOG[n]) for n in names}
    mask = [a == 45 for a in LOG['angle_deg']]     # df["angle_deg"] == 45
    win = list(range(10, 20))                       # rows 10..19 of 30
    fig, ax = fig_for((-2.7, 11.25), (-6.6, 0.95), width=6.3)
    dots = [['...'] * 4]
    rows = dots + [[col[n][i] for n in names] for i in win] + dots
    idx = ['...'] + [str(i) for i in win] + ['...']
    fills = [[None] * 4] + [[SEL_FILL if mask[i] else GREY_FILL] * 4
                            for i in win] + [[None] * 4]
    colors = [[None] * 4] + [[TEXT if mask[i] else GREY] * 4
                             for i in win] + [[None] * 4]
    table(ax, 0, 0, names, w, rows, index=idx, index_w=0.8, h=h,
          fills=fills, colors=colors)
    # the mask column, left of the index
    xm = -2.6
    mrows = [['...']] + [[str(mask[i])] for i in win] + [['...']]
    mf = [[None]] + [[SEL_FILL if mask[i] else GREY_FILL] for i in win] \
        + [[None]]
    mc = [[None]] + [[SEL if mask[i] else GREY] for i in win] + [[None]]
    table(ax, xm, 0, ['mask_45'], [1.5], mrows, h=h, fills=mf, colors=mc)
    chip(ax, xm + 0.04, 0.6, 'mask_45 = df["angle_deg"] == 45', fs=10)
    # the rows kept by df[mask_45]
    k0 = 1 + win.index(12)
    k1 = 1 + win.index(17)
    y_top = -h - k0 * h
    y_bot = -h - (k1 + 1) * h
    outline(ax, -0.8, y_top, W, y_bot, SEL)
    vbracket(ax, W + 0.15, y_top, y_bot, RES)
    text(ax, W + 0.45, (y_top + y_bot) / 2 + 0.25, 'df[mask_45]', RES,
         mono=True, ha='left', fs=10)
    text(ax, W + 0.45, (y_top + y_bot) / 2 - 0.25,
         f'{sum(mask)} rows', RES, ha='left', fs=10)
    return save(fig, '11_4_mask')


def fig_11_4_dropna():
    """runs with a NaN cell; runs.dropna() drops that row, keeps the labels."""
    names = list(RUNS)
    w = [1.4, 2.9]
    W = sum(w)
    h = 0.55
    col = {n: shown(RUNS[n]) for n in names}
    rows = list(zip(*[col[n] for n in names]))
    bad = [any(v == 'NaN' for v in r) for r in rows]
    keep = [k for k in range(len(rows)) if not bad[k]]
    fig, ax = fig_for((-1.1, 12.1), (-3.5, 1.0), width=6.2)
    text(ax, W / 2 - 0.45, 0.6, 'runs', mono=True, fs=11)
    colors = [[GREY if b else None] * 2 for b in bad]
    fills = [[GREY_FILL if b else None] * 2 for b in bad]
    table(ax, 0, 0, names, w, rows, index=[str(i) for i in range(len(rows))],
          h=h, fills=fills, colors=colors)
    for i in [k for k in range(len(rows)) if bad[k]]:
        yr = -h - i * h - h / 2
        ax.plot([-0.95, W + 0.05], [yr, yr], color=BAD, lw=1.8, zorder=5,
                solid_capstyle='round')
    text(ax, W / 2 - 0.45, -5 * h - 0.4, f'{len(rows)} rows', GREY, fs=10)
    # the result
    x0 = 7.6
    chip(ax, x0 + W / 2 - 0.45, 0.6, 'runs_clean = runs.dropna()', fs=10,
         ha='center')
    table(ax, x0, 0, names, w, [rows[k] for k in keep],
          index=[str(k) for k in keep], h=h,
          fills=[[RES_FILL] * 2 for _ in keep])
    arrow(ax, (W + 0.3, -2.5 * h), (x0 - 1.2, -2.5 * h), RES)
    text(ax, x0 + W / 2 - 0.45, -(len(keep) + 1) * h - 0.4,
         f'{len(keep)} rows; the labels stay: '
         + ', '.join(str(k) for k in keep), GREY, fs=10)
    return save(fig, '11_4_dropna')


# ---------------------------------------------------------------- 11.5
def fig_11_5_groupby():
    """small split by angle_deg; mean, std and count per group, combined."""
    ang = SMALL8['angle_deg']
    rng = SMALL8['range_measured']
    groups = sorted(set(ang))
    tint = {groups[0]: AX0_FILL, groups[1]: AX0_FILL2}
    stats = []
    for a in groups:             # .agg(["mean", "std", "count"]), std: N-1
        v = np.array([r for r, b in zip(rng, ang) if b == a], float)
        stats.append(shown([v.mean()]) + shown([v.std(ddof=1)])
                     + [str(len(v))])
    h = 0.5
    w = [1.85, 2.95]
    W = sum(w)
    fig, ax = fig_for((-0.9, 13.2), (-6.05, 1.3), width=6.3)
    text(ax, W / 2 - 0.4, 1.0, 'small', mono=True, fs=11)
    rows = list(zip(shown(ang), shown(rng)))
    fills = [[tint[a]] * 2 for a in ang]
    table(ax, 0, 0, ['angle_deg', 'range_measured'], w, rows,
          index=[str(i) for i in range(len(ang))], index_w=0.8, h=h,
          fills=fills)
    # split: one bracket per group
    xb = W + 0.12
    mids = []
    for a in groups:
        ii = [i for i, b in enumerate(ang) if b == a]
        yt, yb = -h - ii[0] * h, -h - (ii[-1] + 1) * h
        vbracket(ax, xb, yt, yb, AX0)
        mids.append((yt + yb) / 2)
    # apply + combine: the stats table, one row per group
    x0 = 9.3
    sw = [1.3, 1.1, 1.4]
    ys = (mids[0] + mids[1]) / 2 + 0.75
    xc, yc = table(ax, x0, ys, ['mean', 'std', 'count'], sw, stats,
                   index=[str(a) for a in groups], index_w=1.9,
                   index_name='angle_deg', h=h,
                   fills=[[RES_FILL] * 3 for _ in groups])
    for ym, yt in zip(mids, yc):
        arrow(ax, (xb + 0.35, ym), (x0 - 2.0, yt), AX0)
    text(ax, x0 + sum(sw) / 2 - 0.95, ys - 3 * h - 0.35, 'stats', RES,
         mono=True, fs=11)
    # the three steps
    xa = (xb + x0 - 1.9) / 2 + 0.2          # the middle of the arrows
    text(ax, xb + 0.05, 1.0, 'split', GREY, fs=10, weight='bold')
    text(ax, xa + 0.5, 1.0, 'apply', GREY, fs=10, weight='bold')
    text(ax, xa + 0.45, mids[0] + 0.45, 'mean, std, count', RES, fs=10)
    text(ax, x0 + sum(sw) / 2 - 0.95, 1.0, 'combine', GREY, fs=10,
         weight='bold')
    chip(ax, -0.75, -len(ang) * h - h - 0.95,
         'stats = small.groupby("angle_deg")["range_measured"].agg(\n'
         '    ["mean", "std", "count"])', fs=10)
    return save(fig, '11_5_groupby')


# ---------------------------------------------------------------- 11.7
def fig_11_7_index_alignment():
    """s1 - s2 lines up by index label (all NaN); to_numpy() by position."""
    ang = LOG['angle_deg']
    rng = LOG['range_measured']
    lab1 = [i for i, a in enumerate(ang) if a == 45]     # index 12 ... 17
    lab2 = [i for i, a in enumerate(ang) if a == 60]     # index 18 ... 23
    r = shown(rng)
    labels = sorted(set(lab1) | set(lab2))
    rows = []
    for k in labels:
        a = r[k] if k in lab1 else None
        b = r[k] if k in lab2 else None
        rows.append([a, b, 'NaN'])
    h = 0.5
    w = [1.5, 1.5, 1.7]
    fig, ax = fig_for((-1.3, 13.4), (-6.7, 1.75), width=6.3)
    chip(ax, 1.85, 1.3, 'diff_wrong = s1 - s2', fs=10, ha='center')
    text(ax, 1.85, 0.68, 'lines up by index label', BAD, fs=10)
    table(ax, 0, 0, ['s1', 's2', 's1 - s2'], w, rows,
          index=[str(k) for k in labels], h=h,
          fills=[[SEL_FILL if v and v != 'NaN' else None for v in rw]
                 for rw in rows])
    # right: by position
    x0 = 7.4
    d = np.array([rng[i] for i in lab1]) - np.array([rng[i] for i in lab2])
    prow = [[r[i], r[j], f'{v:.3f}'] for i, j, v in zip(lab1, lab2, d)]
    chip(ax, x0 + 2.3, 1.3, 's1.to_numpy() - s2.to_numpy()', fs=10,
         ha='center')
    text(ax, x0 + 2.3, 0.68, 'lines up by position', RES, fs=10)
    xc, yc = table(ax, x0, 0, ['s1', 's2', 'diff_right'], [1.5, 1.5, 1.9],
                   prow, h=h,
                   fills=[[SEL_FILL, SEL_FILL, RES_FILL] for _ in prow])
    for i, y in enumerate(yc):
        text(ax, x0 - 0.15, y, str(i), AX0, mono=True, ha='right', fs=10)
    text(ax, x0 + 2.3, -7 * h - 0.4, 'the labels are dropped:', GREY,
         fs=10)
    text(ax, x0 + 2.3, -7 * h - 0.9, 'positions 0 ... 5', GREY, fs=10)
    return save(fig, '11_7_index_alignment')


FIGURES = [fig_11_1_arrays_vs_table, fig_11_2_anatomy, fig_11_2_col_vs_cols,
           fig_11_4_mask, fig_11_4_dropna, fig_11_5_groupby,
           fig_11_7_index_alignment]
