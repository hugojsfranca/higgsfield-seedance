#!/usr/bin/env python3
"""Validate a film shot list before writing or running prompts (see references/film-planning.md).

Usage:
  python3 shotlist_check.py shotlist.csv [--prompts DIR ...] [--keyframes DIR ...] [--film-seconds N]

Columns expected: scene, shot, film_in, film_out, film_seconds, clip_id, model, mode, clip_seconds,
start_keyframe, cut_note (others are ignored). A model of "post" marks a reused slice or a still; rows whose
cut_note or start_keyframe says "approved" are existing takes and need no prompt file.
Prints ERROR / WARN / OK lines; exits 1 if there is any ERROR. Standard library only.
"""
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

MODES_25 = {"t2v", "omni_reference", "video_edit", "video_extension"}
LIMITS = {"seedance_2_5": (4, 30), "seedance_2_0": (4, 15), "cinematic_studio_video_4_0": (4, 30),
          "cinematic_studio_video_3_5": (4, 30), "cinematic_studio_3_0": (4, 30)}
MODES = {"seedance_2_5": MODES_25, "cinematic_studio_video_4_0": MODES_25, "seedance_2_0": {"std", "fast"},
         "cinematic_studio_video_3_5": set(), "cinematic_studio_3_0": set()}   # empty set: the engine takes no mode
LIKE_25 = ("seedance_2_5", "cinematic_studio_video_4_0")
# Draft rates per second (2.5-like and 3.x at 480p, 2.0 at 720p) from `generate cost` on 17 September 2026.
DRAFT_RATE = {"seedance_2_5": 3.0, "seedance_2_0": 4.5, "cinematic_studio_video_4_0": 3.0,
              "cinematic_studio_video_3_5": 3.5, "cinematic_studio_3_0": 3.5}
EMPTY = re.compile(r"^\s*(?:|none.*|-|n/?a)\s*$", re.I)
WINDOW = re.compile(r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)")
TIMED = re.compile(r"\bat (?:about |around )?\d+(?:\.\d+)? ?s(?:ec\w*)?\b|\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?\s*s\b|by (?:about )?\d+(?:\.\d+)? ?s\b", re.I)
CLOCK = ["night", "pre-dawn", "blue hour", "dawn", "sunrise", "early morning", "morning", "mid-morning", "late morning",
         "midday", "noon", "early afternoon", "afternoon", "late afternoon", "golden hour", "sunset", "dusk", "evening"]


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser(description="Validate a Seedance film shot list.")
    ap.add_argument("shotlist")
    ap.add_argument("--prompts", nargs="+", help="folder(s) holding <clip_id>.txt prompt files")
    ap.add_argument("--keyframes", nargs="+", help="folder(s) holding <start_keyframe>.txt keyframe prompts")
    ap.add_argument("--film-seconds", type=float, help="expected film length")
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.shotlist, encoding="utf-8")))
    errors, warns, oks = [], [], []
    need = {"film_in", "film_out", "clip_id", "model", "clip_seconds"}
    missing_cols = need - set(rows[0].keys() if rows else [])
    if missing_cols:
        print(f"ERROR  missing columns: {', '.join(sorted(missing_cols))}")
        return 1

    # --- film timing -----------------------------------------------------------
    timed = sorted(((num(r["film_in"]), num(r["film_out"]), r) for r in rows), key=lambda t: (t[0] or 0))
    prev_out = 0.0
    for fin, fout, r in timed:
        cid = r["clip_id"]
        if fin is None or fout is None:
            errors.append(f"{cid}: film_in/film_out not numeric")
            continue
        if abs(fin - prev_out) > 0.05:
            errors.append(f"{cid}: starts at {fin:g} s but the previous row ends at {prev_out:g} s (gap or overlap)")
        fs = num(r.get("film_seconds"))
        if fs is not None and abs(fs - (fout - fin)) > 0.05:
            warns.append(f"{cid}: film_seconds {fs:g} ≠ film_out − film_in ({fout - fin:g})")
        prev_out = fout
    if a.film_seconds is not None and abs(prev_out - a.film_seconds) > 0.05:
        errors.append(f"timeline ends at {prev_out:g} s, expected {a.film_seconds:g} s")
    else:
        oks.append(f"{len(rows)} rows, timeline runs continuously to {prev_out:g} s")

    # --- clips -------------------------------------------------------------------
    ids = Counter(r["clip_id"] for r in rows if (r.get("model") or "").strip() != "post")
    for cid, n in ids.items():
        if n > 1:
            errors.append(f"clip_id {cid} is used by {n} generated rows")
    gen_seconds, by_model, no_window = defaultdict(float), Counter(), []
    for r in rows:
        cid, model = r["clip_id"], (r.get("model") or "").strip()
        mode = (r.get("mode") or "").strip()
        secs = num(r.get("clip_seconds")) or 0
        start = r.get("start_keyframe") or ""
        by_model[model] += 1
        if model == "post":
            continue
        if model not in LIMITS:
            warns.append(f"{cid}: model '{model}' isn't one this plugin routes to; check `higgsfield model get {model}`")
            continue
        lo, hi = LIMITS[model]
        if secs != int(secs) or not lo <= secs <= hi:
            errors.append(f"{cid}: {secs:g} s is outside {model}'s {lo}–{hi} s range (whole seconds)")
        gen_seconds[model] += secs
        if mode and not EMPTY.match(mode) and mode not in MODES[model]:
            errors.append(f"{cid}: mode '{mode}' isn't valid for {model} "
                          f"({', '.join(sorted(MODES[model])) or 'it takes no mode; leave the column empty'})")
        if model in LIKE_25 and mode == "t2v" and not EMPTY.match(start):
            errors.append(f"{cid}: t2v can't take a start frame ({start}); use omni_reference")
        if model in LIKE_25 and mode == "omni_reference" and EMPTY.match(start) and EMPTY.match(r.get("object_refs") or ""):
            errors.append(f"{cid}: omni_reference needs a start frame or references")
        win = WINDOW.search(r.get("cut_note") or "")
        if not win:
            no_window.append(cid)
        elif a.prompts and float(win.group(2)) - float(win.group(1)) < 1.2:
            pf = next((Path(d) / f"{cid}.txt" for d in a.prompts if (Path(d) / f"{cid}.txt").exists()), None)
            if pf and not TIMED.search(pf.read_text(encoding="utf-8")):
                warns.append(f"{cid}: the edit keeps only {win.group(0)} s but the prompt times nothing; "
                             "time the event inside the window ('at about 1 s')")
        approved = "approved" in ((r.get("cut_note") or "") + start).lower()
        if a.prompts and not approved and not any((Path(d) / f"{cid}.txt").exists() for d in a.prompts):
            errors.append(f"{cid}: no prompt file {cid}.txt in {', '.join(a.prompts)}")
        frames = [f for f in (start, r.get("end_keyframe") or "") if not EMPTY.match(f)]
        for f in frames:
            if "/" in f or f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")) or re.search(r"\s\+\s|\bend\b", f):
                warns.append(f"{cid}: keyframe field '{f}' should hold one asset ID (use end_keyframe for an end frame)")
        if a.keyframes and not approved and frames:
            for kf in (t for f in frames for t in re.split(r"[;,|+ ]+", f.strip()) if t and t.lower() != "end"):
                if kf and not any((Path(d) / f"{kf}.txt").exists() for d in a.keyframes):
                    errors.append(f"{cid}: no keyframe prompt {kf}.txt in {', '.join(a.keyframes)}")
    if rows and "time" in rows[0]:
        last = {}
        for r in sorted(rows, key=lambda x: num(x["film_in"]) or 0):
            t = (r.get("time") or "").lower()
            idx = max((i for i, k in enumerate(CLOCK) if k in t), default=None, key=lambda i: len(CLOCK[i]))
            if idx is None:
                continue
            sc = r.get("scene")
            if sc in last and idx < last[sc][0]:
                warns.append(f"{r['clip_id']}: time '{r['time']}' runs backward within scene {sc} (after '{last[sc][1]}')")
            last[sc] = (idx, r["time"])
    if no_window:
        warns.append(f"{len(no_window)} generated rows have no slice window in cut_note (e.g. 'use 1.5–2.8'): "
                     + ", ".join(no_window[:12]) + (" …" if len(no_window) > 12 else ""))

    # --- summary -----------------------------------------------------------------
    est = sum(DRAFT_RATE[m] * s for m, s in gen_seconds.items())
    oks.append("rows by model: " + ", ".join(f"{m} {n}" for m, n in by_model.items()))
    oks.append("generated seconds: " + ", ".join(f"{m} {s:g}" for m, s in gen_seconds.items()))
    oks.append(f"first-pass video estimate ≈ {est:.0f} credits (2.5, 4.0 and 3.x at 480p, 2.0 at 720p; before re-rolls, "
               "stills and finals; confirm with `higgsfield generate cost`)")

    for e in errors:
        print(f"ERROR  {e}")
    for w in warns:
        print(f"WARN   {w}")
    for o in oks:
        print(f"OK     {o}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
