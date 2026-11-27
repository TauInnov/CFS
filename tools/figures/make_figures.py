"""Rebuild every explanatory figure into course/figures/.

usage: python tools/figures/make_figures.py [week ...]   e.g. 7 9
Each week module (week7.py, week9.py, ...) has a list FIGURES of
functions; each function draws and saves one figure.
"""
import importlib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

weeks = sys.argv[1:] or sorted(p.stem[4:] for p in HERE.glob('week*.py'))
for wk in weeks:
    mod = importlib.import_module(f'week{wk}')
    for draw in mod.FIGURES:
        print(draw())
