#!/usr/bin/env python3
import nbformat
import uuid
import sys

def unique_id(cell):
    # give every cell a fresh, string-typed id so nbformat is happy
    cell.id = uuid.uuid4().hex

def merge(nb_paths, out_path):
    # read the first notebook as the “base”
    merged = nbformat.read(nb_paths[0], as_version=4)
    for p in nb_paths[1:]:
        nb = nbformat.read(p, as_version=4)
        for cell in nb.cells:
            unique_id(cell)
            merged.cells.append(cell)
    # (optional) add a divider
    merged.cells.insert(len(merged.cells)-len(nb.cells),
                        nbformat.v4.new_markdown_cell("----"))
    nbformat.write(merged, out_path)
    print(f"Written merged notebook to {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit("Usage: merge_notebooks.py A.ipynb B.ipynb [C.ipynb …] OUTPUT.ipynb")
    *sources, out = sys.argv[1:]
    merge(sources, out)