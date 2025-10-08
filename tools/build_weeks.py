import argparse, json, subprocess
from pathlib import Path
import nbformat as nbf
import yaml

def git_sha(path):
    try:
        out = subprocess.check_output(
            ["git","-C", str(path), "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return out
    except Exception:
        return None

def banner(title, subtitle=None):
    md = f"# {title}\n"
    if subtitle: md += f"\n> {subtitle}\n"
    c = nbf.v4.new_markdown_cell(md)
    c.metadata["keep"] = True
    return c

def merge_files(out_path, title, files, src_root):
    nb = nbf.v4.new_notebook()
    sha = git_sha(src_root)
    nb.metadata.update({
        "kernelspec": {"name":"python3","display_name":"Python 3","language":"python"},
        "provenance": {"vendor_root": str(src_root), "vendor_sha": sha, "sources": files}
    })
    nb.cells.append(banner(title, f"Built from {len(files)} upstream notebooks"
                                  + (f" @ {sha}" if sha else "")))

    seen_sources = set()  # optional: de-dup identical code cells
    for p in files:
        p = Path(p)
        src_nb = nbf.read(p, as_version=4)
        nb.cells.append(banner(f"From: {p.name}", str(p)))
        for cell in src_nb.cells:
            # tag origin so you can trace any cell back
            cell.metadata = dict(cell.metadata) or {}
            cell.metadata["origin_path"] = str(p)
            cell.metadata["origin_cell_id"] = cell.get("id")
            if cell.cell_type == "code":
                sig = ("code", cell.source.strip())
                if sig in seen_sources:   # skip exact duplicates
                    continue
                seen_sources.add(sig)
            nb.cells.append(cell)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, out_path)
    print(f"Wrote {out_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True)
    ap.add_argument("--outdir", default="course/weeks")
    ap.add_argument("--srcroot", default="vendor/virtual-pyprog")
    args = ap.parse_args()

    cfg = yaml.safe_load(Path(args.map).read_text())
    for week, spec in cfg.items():
        title = spec.get("title", week)
        files = spec["files"]
        out_path = Path(args.outdir) / f"{week}.ipynb"
        merge_files(out_path, title, files, Path(args.srcroot))

if __name__ == "__main__":
    main()
