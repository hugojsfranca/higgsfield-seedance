#!/usr/bin/env python3
"""Keep a local catalog of Cinema Studio control IDs, harvested from your own job history.

Cinema Studio 4.0 and Cinematic Studio Image take their camera body, lens, aperture, focal length, genre,
era, tempo, light and colour-palette controls as IDs (camera_model_id, genre_id, ...). The CLI can't list
them, but every job made in the Cinema Studio web app records the ones it used. This script reads your
history with `higgsfield generate list --json` and remembers each ID with its name.

Usage:
  python3 studio_ids.py harvest [--size 100] [--from jobs.json]   merge IDs from recent jobs (or a saved list)
  python3 studio_ids.py list [KIND]                                show the catalog, or one kind
  python3 studio_ids.py find KIND NAME                             print the ID for a name, or exit 1
Options: --catalog PATH (default: $HIGGSFIELD_STUDIO_IDS, else ~/.config/higgsfield-seedance/cinema-studio-ids.json)

Kinds and the flag each one feeds: camera_model (--camera_model_id), camera_lens (--camera_lens_id),
camera_aperture (--camera_aperture_id), camera_focal_length (--camera_focal_length_id), genre (--genre_id),
era (--era_id), pacing (--pacing_id), light (light settings), color_palette (--color_palette), style (--style_id).
Read-only: it never creates jobs or spends credits. Standard library only.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_CATALOG = Path(os.environ.get("HIGGSFIELD_STUDIO_IDS") or
                       Path.home() / ".config" / "higgsfield-seedance" / "cinema-studio-ids.json")
KINDS = {
    "camera_model": "camera_model", "camera_model_id": "camera_model",
    "camera_lens": "camera_lens", "camera_lens_id": "camera_lens",
    "camera_aperture": "camera_aperture", "camera_aperture_id": "camera_aperture",
    "camera_focal_length": "camera_focal_length", "camera_focal_length_id": "camera_focal_length",
    "genre": "genre", "genre_id": "genre", "genre_control": "genre",
    "era": "era", "era_id": "era", "era_control": "era",
    "pacing": "pacing", "pacing_id": "pacing",
    "light_preset": "light", "light_id": "light",
    "color_palette": "color_palette", "color_signature": "color_palette", "color_signature_id": "color_palette",
    "style": "style", "style_id": "style",
}
NAME_KEYS = ("name", "title", "label", "display_name", "slug")


def load(path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"updated": None, "kinds": {}}


def save(path, cat):
    path.parent.mkdir(parents=True, exist_ok=True)
    cat["updated"] = datetime.datetime.now().isoformat(timespec="seconds")
    path.write_text(json.dumps(cat, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def record(cat, kind, id_, name, extra, job):
    entry = cat["kinds"].setdefault(kind, {}).setdefault(id_, {"name": None, "seen": 0})
    if name and not entry.get("name"):
        entry["name"] = name
    entry.update({k: v for k, v in extra.items() if v is not None})
    entry["seen"] += 1
    entry["last_job_type"] = job.get("job_type")
    entry["last_seen"] = (job.get("created_at") or "")[:10]


def walk(cat, key, value, job, found):
    kind = KINDS.get(key)
    if isinstance(value, dict):
        if kind and isinstance(value.get("id"), str) and value["id"]:
            name = next((value[k] for k in NAME_KEYS if isinstance(value.get(k), str) and value[k]), None)
            record(cat, kind, value["id"], name, {"type": value.get("type")}, job)
            found.append((kind, value["id"], name))
        for k, v in value.items():
            if k != "id":
                walk(cat, k, v, job, found)
    elif isinstance(value, list):
        for v in value:
            walk(cat, key, v, job, found)
    elif kind and key.endswith("_id") and isinstance(value, str) and value:
        known = cat["kinds"].get(kind, {}).get(value)
        record(cat, kind, value, None, {}, job)
        found.append((kind, value, (known or {}).get("name")))


def harvest(a, cat):
    if a.from_file:
        data = json.loads(Path(a.from_file).read_text(encoding="utf-8"))
    else:
        run = subprocess.run(["higgsfield", "generate", "list", "--size", str(a.size), "--json"],
                             capture_output=True, text=True)
        if run.returncode != 0:
            sys.exit(f"higgsfield generate list failed: {run.stderr.strip() or run.stdout.strip()}")
        data = json.loads(run.stdout)
    jobs = data if isinstance(data, list) else (data.get("items") or data.get("jobs") or [])
    found = []
    for job in jobs:
        walk(cat, "", job.get("params") or {}, job, found)
    uniq = {(k, i): n for k, i, n in found}
    print(f"scanned {len(jobs)} jobs; {len(uniq)} control IDs seen")
    for (kind, id_), name in sorted(uniq.items()):
        print(f"  {kind:<20} {name or '(no name recorded)':<28} {id_}")
    if not uniq:
        print("  none yet: set the camera, lens, genre, era, tempo, light or palette on a shot in the Cinema Studio "
              "web app, generate it, then harvest again")


def main():
    ap = argparse.ArgumentParser(description="Catalog Cinema Studio control IDs from your job history.")
    ap.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("harvest")
    h.add_argument("--size", type=int, default=100, help="how many recent jobs to read (max 100)")
    h.add_argument("--from", dest="from_file", help="a saved `higgsfield generate list --json` output")
    ls = sub.add_parser("list")
    ls.add_argument("kind", nargs="?")
    f = sub.add_parser("find")
    f.add_argument("kind")
    f.add_argument("name")
    a = ap.parse_args()

    cat = load(a.catalog)
    if a.cmd == "harvest":
        harvest(a, cat)
        save(a.catalog, cat)
        print(f"catalog: {a.catalog}")
    elif a.cmd == "list":
        kinds = [a.kind] if a.kind else sorted(cat["kinds"])
        if not kinds:
            print("catalog is empty; run: python3 studio_ids.py harvest")
        for kind in kinds:
            print(kind)
            for id_, e in sorted(cat["kinds"].get(kind, {}).items(), key=lambda kv: (kv[1].get("name") or "")):
                print(f"  {e.get('name') or '(no name recorded)':<28} {id_}  seen {e['seen']}x, last {e.get('last_seen')}")
    elif a.cmd == "find":
        wanted = a.name.strip().lower()
        for id_, e in cat["kinds"].get(a.kind, {}).items():
            if (e.get("name") or "").lower() == wanted or id_ == a.name:
                print(id_)
                return 0
        print(f"no {a.kind} named '{a.name}' in {a.catalog}; harvest after using it once in the web app",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
