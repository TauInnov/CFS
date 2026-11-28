"""Week 13 figures: Git (zones, history, remotes, branches, a conflict).

A commit is a circle. Git hashes change on every build, so no figure
shows one: a commit is named by the page's own Python name for it
(oldest_first[0]) or by the code line it changed. The commit messages
of the pages are Hebrew, and figure text is English, so the figures
show the code each commit changed instead of its message.
Colours: main (and "your" commits) blue, the partner amber, the new
commit or the merge (the result) green, a bug or a conflict marker red.
A place (a zone, a computer, a file) is a rounded grey box without a
frame; a command is a code chip; a branch name is a capsule in its colour.
"""
from matplotlib.patches import Circle, Polygon

from cfsfig import (AX0, AX0_FILL, AX1, AX1_FILL, BAD, BAD_FILL, CELL, FADED,
                    GREY, GREY_FILL, MUTED, PAGE, RES, RES_FILL, TEXT, arrow,
                    chip, new_fig, pill, rbox, save, text)

MAIN, MAIN_FILL = AX0, AX0_FILL
PART, PART_FILL = AX1, AX1_FILL

# the code of the pages, as written there
# 13.1: projectile.py is built in three commits (cells 7, 10, 13)
P13_1 = ['v0, theta_deg', 'R', 'print']        # the names each commit adds
# 13.2: the line of pendulum.py that the three commits hold (cells 3, 5, 7)
T_GOOD = 'T = 2 * np.pi * np.sqrt(L / constants.g)'
T_BAD = 'T = 2 * np.pi * np.sqrt(L) / constants.g'
T_LINES = [T_GOOD, T_BAD, T_BAD]                # oldest first
DIFF_CMD = 'git diff {oldest_first[0]} {oldest_first[1]} -- pendulum.py'
# 13.4: cooling.py after the conflict (cell 15, the output of cat)
K_MAIN = 'k = 0.10    # cooling constant (1/min)'
K_PART = 'k = 0.12    # cooling constant (1/min)'
CONFLICT = [
    'T0 = 90.0   # initial temperature (C)',
    '<<<<<<< HEAD',
    K_MAIN,
    '=======',
    K_PART,
    '>>>>>>> partner',
    'n = 10      # minutes',
    'T = 20 + (T0 - 20) * (1 - k)**n',
    'print(f"T after {n} min: {T:.1f} C")',
]


def fig_for(xlim, ylim, width=6.3):
    """new_fig whose axes fill the figure: one data unit is square."""
    height = width * (ylim[1] - ylim[0]) / (xlim[1] - xlim[0])
    fig, ax = new_fig(width, height, xlim, ylim)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    return fig, ax


def commit(ax, x, y, color, fill, label='', r=0.3, fs=10):
    """A commit: a circle in its role colour, on its role fill."""
    ax.add_patch(Circle((x, y), r, fc=fill, ec=color, lw=2.2, zorder=4))
    if label:
        text(ax, x, y, label, color, fs=fs, weight='bold')


def link(ax, p, q, color=None, r=0.3):
    """A line between two commits, from edge to edge."""
    (x0, y0), (x1, y1) = p, q
    d = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    ax.plot([x0 + r * ux, x1 - r * ux], [y0 + r * uy, y1 - r * uy],
            color=color or FADED, lw=2.2, zorder=3, solid_capstyle='round')


def box(ax, x0, y0, x1, y1, fc=None, r=0.25, z=1):
    """A rounded box without a frame, from the top-left (x0, y0) to the
    bottom-right (x1, y1)."""
    rbox(ax, x0, y1, x1 - x0, y0 - y1, fc or GREY_FILL, r=r, z=z)


def tag(ax, x, y, s, color, fill):
    """A branch name in a capsule of its colour, its left edge at x."""
    pill(ax, x + 0.1, y, s, color, fill, fs=10, mono=True, ha='left')


def file_icon(ax, x, y, name, w=0.5, h=0.65):
    """A page with a folded corner at (x, y), its name on the right."""
    c = 0.16
    pts = [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2),
           (x + w / 2, y + h / 2 - c), (x + w / 2 - c, y + h / 2),
           (x - w / 2, y + h / 2)]
    ax.add_patch(Polygon(pts, closed=True, fc=PAGE, ec=MUTED, lw=1.3,
                         joinstyle='round', zorder=3))
    ax.plot([x + w / 2 - c, x + w / 2 - c, x + w / 2],
            [y + h / 2, y + h / 2 - c, y + h / 2 - c], color=MUTED, lw=1.0,
            solid_joinstyle='round', zorder=4)
    for k in range(3):
        yy = y + 0.12 - k * 0.14
        ax.plot([x - w / 2 + 0.1, x + w / 2 - 0.1], [yy, yy], color=FADED,
                lw=0.9, solid_capstyle='round', zorder=4)
    text(ax, x + w / 2 + 0.2, y, name, mono=True, ha='left', fs=10)


# ---------------------------------------------------------------- 13.1
def fig_13_1_three_zones():
    """Working directory, staging area, repository; git add, git commit."""
    fig, ax = fig_for((-0.2, 8.4), (-8.05, 0.2), width=4.0)
    x0, x1 = 0.0, 7.6
    xm = (x0 + x1) / 2
    # the three zones, top to bottom
    zones = [(0.0, -1.55, 'working directory'),
             (-2.65, -4.2, 'staging area'),
             (-5.3, -7.95, 'repository')]
    for top, bot, title in zones:
        box(ax, x0, top, x1, bot)
        text(ax, x0 + 0.3, top - 0.38, title, ha='left', fs=11,
             weight='bold')
    text(ax, x0 + 2.65, -5.3 - 0.38, '(made by git init)', GREY, ha='left',
         fs=10)
    file_icon(ax, xm - 1.2, -0.95, 'projectile.py')
    file_icon(ax, xm - 1.2, -3.6, 'projectile.py')
    # the two commands
    arrow(ax, (xm, -1.62), (xm, -2.58), TEXT, lw=2)
    chip(ax, xm + 0.4, -2.1, 'git add projectile.py', fs=10)
    arrow(ax, (xm, -4.27), (xm, -5.23), RES, lw=2)
    chip(ax, xm + 0.4, -4.75, 'git commit -m "..."', fs=10)
    # the history: three commits, the newest in green
    y = -6.65
    xs = [1.4, 3.8, 6.2]
    for k, xk in enumerate(xs):
        new = k == len(xs) - 1
        commit(ax, xk, y, RES if new else MAIN, RES_FILL if new else MAIN_FILL,
               str(k + 1))
        text(ax, xk, y - 0.65, P13_1[k], GREY, mono=True, fs=10)
        if k:
            link(ax, (xs[k - 1], y), (xk, y))
    text(ax, xs[-1] + 0.45, y, 'new', RES, ha='left', fs=10)
    return save(fig, '13_1_three_zones')


# ---------------------------------------------------------------- 13.2
def fig_13_2_log_diff():
    """The three commits in git log order; git diff of the first two."""
    fig, ax = fig_for((-0.2, 11.6), (-6.15, 0.55), width=6.0)
    h = 1.25
    xh, xo, xc, xt = 0.45, 2.3, 3.95, 4.6
    text(ax, xh, 0.2, 'hashes', GREY, mono=True, fs=10)
    text(ax, xo, 0.2, 'oldest_first', mono=True, fs=10)
    text(ax, xt, 0.2, 'pendulum.py', mono=True, ha='left', fs=10)
    n = len(T_LINES)
    ys = []
    for row in range(n):              # git log order: the newest on top
        k = n - 1 - row               # its place in oldest_first
        y = -0.6 - row * h
        ys.append(y)
        text(ax, xh, y, f'[{row}]', GREY, mono=True, fs=10)
        text(ax, xo, y, f'[{k}]', mono=True, fs=10)
        commit(ax, xc, y, MAIN, MAIN_FILL)
        bad = T_LINES[k] != T_LINES[0]
        box(ax, xt - 0.15, y + 0.26, xt + 6.75, y - 0.26,
            BAD_FILL if bad else CELL, r=0.1)
        text(ax, xt, y, T_LINES[k], BAD if bad else TEXT, mono=True,
             ha='left', fs=10)
        if row:
            link(ax, (xc, ys[row - 1]), (xc, y))
    text(ax, xt + 0.1, ys[1] - 0.52, 'the bug enters here', BAD, ha='left',
         fs=10)
    # git diff between the first two commits
    yd = ys[-1] - 1.3
    chip(ax, 0.05, yd, DIFF_CMD, fs=10)
    lines = [('-' + T_LINES[0], GREY_FILL, TEXT),
             ('+' + T_LINES[1], BAD_FILL, BAD)]
    for m, (s, fc, col) in enumerate(lines):
        yy = yd - 0.85 - m * 0.6
        box(ax, -0.1, yy + 0.26, 7.15, yy - 0.26, fc, r=0.1)
        text(ax, 0.05, yy, s, col, mono=True, ha='left', fs=10)
    text(ax, 7.4, yd - 0.85, 'oldest_first[0]', GREY, mono=True, ha='left',
         fs=10)
    text(ax, 7.4, yd - 1.45, 'oldest_first[1]', BAD, mono=True, ha='left',
         fs=10)
    return save(fig, '13_2_log_diff')


# ---------------------------------------------------------------- 13.3
def fig_13_3_push_clone_pull():
    """my_laptop, GitHub and new_computer; push, clone, push, pull."""
    fig, ax = fig_for((-0.1, 14.1), (-6.6, 1.3), width=6.3)
    places = {
        'hub': (7.0, 0.0, 'GitHub', 'origin_on_github'),
        'mine': (2.35, -4.1, 'my laptop', 'my_laptop'),
        'new': (11.65, -4.1, 'a new computer', 'new_computer'),
    }
    bw, bh = 4.5, 2.1
    for cx, cy, title, folder in places.values():
        box(ax, cx - bw / 2, cy + bh / 2, cx + bw / 2, cy - bh / 2, r=0.3)
        text(ax, cx, cy + 0.62, title, fs=11, weight='bold')
        text(ax, cx, cy + 0.1, folder, GREY, mono=True, fs=10)
        # every repository ends with both commits: the history is copied
        commit(ax, cx - 0.55, cy - 0.55, MAIN, MAIN_FILL, r=0.24)
        commit(ax, cx + 0.55, cy - 0.55, PART, PART_FILL, r=0.24)
        link(ax, (cx - 0.55, cy - 0.55), (cx + 0.55, cy - 0.55), r=0.24)
    # laptop <-> GitHub: 1 push (up), 4 pull (down)
    arrow(ax, (3.2, -2.95), (5.3, -1.15), MAIN, lw=2)
    arrow(ax, (4.75, -1.15), (2.65, -2.95), PART, lw=2)
    text(ax, 3.55, -1.55, '1  git push', MAIN, mono=True, ha='right',
         fs=10)
    text(ax, 3.05, -2.15, '4  git pull', PART, mono=True, ha='right',
         fs=10)
    # GitHub <-> new computer: 2 clone (down), 3 push (up)
    arrow(ax, (8.7, -1.15), (10.8, -2.95), MAIN, lw=2)
    arrow(ax, (11.35, -2.95), (9.25, -1.15), PART, lw=2)
    text(ax, 10.45, -1.55, '2  git clone', MAIN, mono=True, ha='left',
         fs=10)
    text(ax, 10.95, -2.15, '3  git push', PART, mono=True, ha='left', fs=10)
    # the key
    commit(ax, 3.6, -6.05, MAIN, MAIN_FILL, r=0.2)
    text(ax, 3.95, -6.05, 'first commit', ha='left', fs=10)
    commit(ax, 8.0, -6.05, PART, PART_FILL, r=0.2)
    text(ax, 8.35, -6.05, "partner's commit", ha='left', fs=10)
    return save(fig, '13_3_push_clone_pull')


# ---------------------------------------------------------------- 13.4
def fig_13_4_branch_merge():
    """Four steps: branch, a commit on main, a commit on partner, the merge."""
    ph = 2.45                            # the height of one step
    fig, ax = fig_for((-0.1, 14.3), (-4 * ph - 0.1, 0.2), width=6.3)
    xa, xb, xm = 6.3, 8.8, 11.3          # base, the two new commits, merge
    steps = [
        (['git branch partner'], 'main'),
        (['git commit'], 'main'),
        (['git checkout -q partner', 'git commit'], 'partner'),
        (['git checkout -q main', 'git merge partner',
          'git commit -q --no-edit'], 'main'),
    ]
    for s, (cmds, head) in enumerate(steps):
        top = -s * ph
        if s:
            ax.plot([0, 14.2], [top, top], color=GREY_FILL, lw=1.2,
                    solid_capstyle='round')
        chip(ax, 0.2, top - 0.3, '\n'.join(cmds), fs=10, va='top')
        ym, yp = top - 0.85, top - 1.6       # the main and partner lines
        commit(ax, xa, ym, MAIN, MAIN_FILL)
        text(ax, xa, ym + 0.5, 'k = 0.05', GREY, mono=True, fs=10)
        main_tip, part_tip = (xa, ym), (xa, ym)
        if s >= 1:
            commit(ax, xb, ym, MAIN, MAIN_FILL)
            link(ax, (xa, ym), (xb, ym), MAIN)
            text(ax, xb, ym + 0.5, 'k = 0.10', MAIN, mono=True, fs=10)
            main_tip = (xb, ym)
        if s >= 2:
            commit(ax, xb, yp, PART, PART_FILL)
            link(ax, (xa, ym), (xb, yp), PART)
            text(ax, xb, yp - 0.52, 'k = 0.12', PART, mono=True, fs=10)
            part_tip = (xb, yp)
        if s >= 3:
            commit(ax, xm, ym, RES, RES_FILL)
            link(ax, (xb, ym), (xm, ym), MAIN)
            link(ax, (xb, yp), (xm, ym), PART)
            text(ax, xm, ym + 0.5, 'k = 0.12', RES, mono=True, fs=10)
            main_tip = (xm, ym)
        # the branch names; HEAD marks the branch you are on
        mlabel = 'HEAD -> main' if head == 'main' else 'main'
        plabel = 'HEAD -> partner' if head == 'partner' else 'partner'
        tag(ax, main_tip[0] + 0.5, ym, mlabel, MAIN, MAIN_FILL)
        tag(ax, part_tip[0] + 0.5, yp, plabel, PART, PART_FILL)
        if part_tip == (xa, ym):          # partner is still the first commit
            ax.plot([xa + 0.15, xa + 0.47], [ym - 0.28, yp + 0.05],
                    color=PART, lw=1.4, solid_capstyle='round')
    return save(fig, '13_4_branch_merge')


def fig_13_4_conflict():
    """The k line on both branches, and the conflict markers in cooling.py."""
    fig, ax = fig_for((-0.2, 12.4), (-7.0, 0.5), width=5.6)
    x0, x1 = 1.85, 9.35
    # the same line on the two branches
    for m, (name, line, col, fill) in enumerate(
            [('main', K_MAIN, MAIN, MAIN_FILL),
             ('partner', K_PART, PART, PART_FILL)]):
        y = -m * 0.65
        text(ax, x0 - 0.15, y, name, col, mono=True, ha='right', fs=10)
        box(ax, x0, y + 0.27, x1, y - 0.27, fill, r=0.1)
        text(ax, x0 + 0.15, y, line, mono=True, ha='left', fs=10)
    arrow(ax, (5.5, -0.95), (5.5, -1.8), TEXT, lw=2)
    chip(ax, 5.85, -1.38, 'git merge partner', fs=10)
    # cooling.py with the markers
    lh = 0.52
    ytop = -2.0
    box(ax, x0, ytop, x1, ytop - len(CONFLICT) * lh - 0.1, CELL, r=0.2)
    text(ax, x0 - 0.15, ytop - 0.3, 'cooling.py', mono=True, ha='right',
         fs=10)
    for i, line in enumerate(CONFLICT):
        y = ytop - 0.05 - i * lh - lh / 2
        if line == K_MAIN:
            col, fill = TEXT, MAIN_FILL
        elif line == K_PART:
            col, fill = TEXT, PART_FILL
        elif line[:7] in ('<<<<<<<', '=======', '>>>>>>>'):
            col, fill = BAD, None
        else:
            col, fill = GREY, None
        if fill:
            box(ax, x0 + 0.07, y + lh / 2 - 0.03, x1 - 0.07,
                y - lh / 2 + 0.03, fill, r=0.08, z=2)
        text(ax, x0 + 0.15, y, line, col, mono=True, ha='left', fs=10,
             weight='bold' if col == BAD else 'normal')

    def yline(i):
        return ytop - 0.05 - i * lh - lh / 2

    # brackets: HEAD .. ======= is main, ======= .. partner is partner
    xbk = x1 + 0.15
    for (ya, yb, col, label) in [
            (yline(1) + 0.12, yline(3) + 0.06, MAIN, 'main (HEAD)'),
            (yline(3) - 0.06, yline(5) - 0.12, PART, 'partner')]:
        ax.plot([xbk, xbk + 0.15, xbk + 0.15, xbk], [ya, ya, yb, yb],
                color=col, lw=1.6, zorder=4, solid_capstyle='round',
                solid_joinstyle='round')
        text(ax, xbk + 0.35, (ya + yb) / 2, label, col, ha='left', fs=10)
    text(ax, xbk + 0.35, yline(7), 'the same', GREY, ha='left', fs=10)
    text(ax, xbk + 0.35, yline(7) - 0.45, 'in both', GREY, ha='left', fs=10)
    return save(fig, '13_4_conflict')


FIGURES = [fig_13_1_three_zones, fig_13_2_log_diff, fig_13_3_push_clone_pull,
           fig_13_4_branch_merge, fig_13_4_conflict]
