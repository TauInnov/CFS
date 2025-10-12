import argparse, json, subprocess
from pathlib import Path
import nbformat as nbf
import yaml
import copy

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

    seen_sources = set()
    for p in files:
        p = Path(p)
        src_nb = nbf.read(p, as_version=4)
        nb.cells.append(banner(f"From: {p.name}", str(p)))
        for cell in src_nb.cells:
            # --- preserve ALL metadata (including tags) ---
            cell_copy = copy.deepcopy(cell)

            meta = getattr(cell_copy, "metadata", {}) or {}
            # add traceability without clobbering existing keys
            if "origin_path" not in meta:
                meta["origin_path"] = str(p)
            if "origin_cell_id" not in meta:
                # nbformat ≥4.5 usually has "id"; guard if missing
                ocid = cell_copy.get("id", None)
                if ocid is not None:
                    meta["origin_cell_id"] = ocid
            cell_copy.metadata = meta

            # optional de-dup of identical code cells
            if cell_copy.cell_type == "code":
                sig = ("code", cell_copy.source.strip())
                if sig in seen_sources:
                    continue
                seen_sources.add(sig)

            # >>> append the *copy*, not the original
            nb.cells.append(cell_copy)

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
