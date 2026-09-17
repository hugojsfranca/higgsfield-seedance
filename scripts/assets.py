#!/usr/bin/env python3
"""Asset manifest for a film: record approved picks, resolve IDs to exactly one file.

Usage:
  python3 assets.py record CH01 portrait assets/CH01_portrait.png   # after the user approves a pick
  python3 assets.py resolve CH01:portrait                            # prints one path, or exits 1
  python3 assets.py resolve ENV05                                     # fine if ENV05 has a single entry
  python3 assets.py list
Options: --manifest PATH (default: assets/manifest.csv, relative to the current folder)

Paths are stored relative to the manifest's folder and printed relative to the current folder.
Run scripts should find files only through `resolve`, so candidates, stray extensions and
two-variant places can never be picked up by accident. Standard library only.
"""
import argparse
import csv
import os
import sys
from pathlib import Path


def load(manifest):
    if not manifest.exists():
        return []
    with open(manifest, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser(description="Record and resolve approved film assets.")
    ap.add_argument("--manifest", default="assets/manifest.csv")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("id"), r.add_argument("view"), r.add_argument("file")
    q = sub.add_parser("resolve")
    q.add_argument("ref", help="ID or ID:view")
    sub.add_parser("list")
    a = ap.parse_args()

    manifest = Path(a.manifest)
    base = manifest.parent
    rows = load(manifest)

    if a.cmd == "record":
        f = Path(a.file)
        if not f.exists():
            sys.exit(f"no such file: {f}")
        rel = os.path.relpath(f.resolve(), base.resolve())
        rows = [x for x in rows if not (x["id"] == a.id and x["view"] == a.view)]
        rows.append({"id": a.id, "view": a.view, "file": rel})
        base.mkdir(parents=True, exist_ok=True)
        with open(manifest, "w", newline="", encoding="utf-8") as out:
            w = csv.DictWriter(out, fieldnames=["id", "view", "file"])
            w.writeheader()
            w.writerows(sorted(rows, key=lambda x: (x["id"], x["view"])))
        print(f"{a.id}:{a.view} → {rel}")
        return 0

    if a.cmd == "list":
        for x in rows:
            print(f"{x['id']}:{x['view']}\t{x['file']}")
        return 0

    ident, _, view = a.ref.partition(":")
    hits = [x for x in rows if x["id"] == ident and (not view or x["view"] == view)]
    if len(hits) != 1:
        views = ", ".join(f"{x['id']}:{x['view']}" for x in rows if x["id"] == ident) or "none recorded"
        print(f"cannot resolve '{a.ref}' to exactly one asset (have: {views})", file=sys.stderr)
        return 1
    path = base / hits[0]["file"]
    if not path.exists():
        print(f"manifest points at a missing file: {path}", file=sys.stderr)
        return 1
    print(os.path.relpath(path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
