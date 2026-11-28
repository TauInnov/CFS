"""Rebuild every explanatory figure into course/figures/, light and dark.

usage: python tools/figures/make_figures.py [week ...]   e.g. 7 9
Each week module (week4.py ... week13.py) has a list FIGURES of
functions; each function draws and saves one figure. The colours depend
on the theme (CFS_THEME), so every module runs once per theme, each run
in its own Python process.
"""
import importlib
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent

weeks = sys.argv[1:] or sorted((p.stem[4:] for p in HERE.glob('week*.py')),
                               key=int)
if 'CFS_THEME' not in os.environ:
    for theme in ('light', 'dark'):
        env = dict(os.environ, CFS_THEME=theme)
        subprocess.run([sys.executable, __file__, *weeks], env=env,
                       check=True)
    sys.exit(0)

sys.path.insert(0, str(HERE))
for wk in weeks:
    mod = importlib.import_module(f'week{wk}')
    for draw in mod.FIGURES:
        print(draw())
