# CFS: Computers for Physics (self-study site)

Self-study site for the course *Computers for Physics* (Tel Aviv University, 03211121). Students read it on their own during the week. It is built with Jupyter Book 1 (Sphinx) and published to GitHub Pages from the `gh-pages` branch.

## Repository layout

| Path | What it is |
|---|---|
| `_toc.yml`, `_config.yml` | Table of contents (weeks and their pages) and build settings. Notebooks are executed again on every build. |
| `course/weeks/` | One page per week (objectives and the list of topics), plus the sub-pages of weeks 7 to 12. |
| `vendor/virtual-pyprog/` | The teaching notebooks (lists, loops, functions, ...), originally a git subtree from the CS department. They are edited in place here. |
| `exercises/` | Practice notebooks for download or Colab. They are not site pages. |
| `tools/scripts/` | Helper scripts: `build.sh`, `clean.sh`, `commit_push.sh`, `publish.sh`, `update_and_build.sh`. |
| `_build/` | Build output. It is tracked in git but out of date. Do not commit it (`commit_push.sh` skips it). |

## Build environment

Use a fresh virtual environment. `requirements.txt` pins the versions that were checked together on a full-site build:

```
python -m venv .venv
.venv\Scripts\activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Why the pins matter:

- `jupyter-book<2`: Jupyter Book 2 is a different tool and cannot build this site.
- `sphinx-external-toc==1.0.1`: version 1.1.0 crashes on the numbered table of contents.
- `pandas<3`: pandas 3 changes the printed output that the pages show (for example dtype `object` becomes `str`).
- `scipy`: used by the week 7 and week 9 pages and by the git pages of week 12.
- `pydata-sphinx-theme`, `sphinx-book-theme`, `myst-nb`: the theme and notebook packages. Upgrade them together, on a separate branch, and compare every page with the live site before merging.

## Build

```
jupyter-book build .
```

The output is in `_build/html`. Open `_build/html/index.html` to look at it.

The build prints execution errors for a few notebooks (`0_2_python`, `2_4_logical-operators-in-ifs`, `3_1_builtin-functions`, `4_4_nested_lists`, `7_1_while-examples`, `12_2_dicts`, `13_1_files`). They were already there before the theme upgrade. The details are in `_build/html/reports`.

## Publish

`tools/scripts/publish.sh` runs `ghp-import -n -p -f _build/html`, which replaces the content of the `gh-pages` branch and goes live after a minute or two.

- Publish only from a machine with a Hebrew font and a normal internet connection. Figures with Hebrew labels are drawn at build time, and a machine without a Hebrew font produces empty boxes in them.
- Look at the build before publishing, with the pages you changed and one figure page (for example week 8).
- Do not publish a build made on a branch that is not merged.

## Editing a week

1. Edit the notebooks under `vendor/virtual-pyprog/` (and the week page under `course/weeks/` if the objectives change).
2. Build, then check the pages in the browser: quizzes, the solution dropdowns, Hebrew text next to code.
3. Commit and push to `main`, then publish.

`tools/scripts/update_and_build.sh` pulls the upstream version of `vendor/virtual-pyprog` and regenerates the week notebooks from `course/map.yml`. This can overwrite local edits, so run it only on a clean branch and check `git diff` afterwards.
