#!/usr/bin/env python3
"""Lint a Seedance 2.5 prompt against the settings you plan to submit on Higgsfield.

Usage:
  python3 preflight.py PROMPT_FILE --duration SECONDS [--model seedance_2_5|seedance_2_0] [--mode MODE]
      [--images N] [--videos N] [--audios N] [--start-image] [--end-image]
      [--extension-mode forward|backward] [--no-audio] [--fix]
  python3 preflight.py PROMPT_FILE --image [--sheet | --edit] [--fix]

  --images/--videos/--audios  how many --image-references / --video-references /
                              --audio-references you will attach (for video_edit and
                              video_extension, count the source clip in --videos)
  --no-audio                  you will pass --generate_audio false
  --fix                       rewrite PROMPT_FILE with non-standard whitespace normalized
  --image                     lint a still-image (keyframe/asset) prompt: skips video-only checks, adds
                              checks for asset IDs, cross-references, "no X" lists, settings written into
                              the prose, keyword stacking and illustration triggers
  --sheet                     with --image: the still is meant to be a multi-panel approval sheet
  --edit                      with --image: an edit prompt (CHANGE / PRESERVE EXACTLY blocks, removals allowed)

Prints ERROR / WARN / OK lines and exits 1 if there is any ERROR. Standard library only.
The checks are heuristics: fix every ERROR, judge each WARN.
"""

import argparse
import re
import sys
from pathlib import Path

MODES = ("t2v", "omni_reference", "video_edit", "video_extension")
MODES_20 = ("std", "fast")

# Characters that sneak in from Docs/Notion/Slack pastes. Mapped to their plain replacement.
ODD_WHITESPACE = {
    "\u00a0": " ", "\u2002": " ", "\u2003": " ", "\u2007": " ", "\u2009": " ",
    "\u200a": " ", "\u202f": " ", "\u205f": " ", "\u3000": " ",
    "\u200b": "", "\u200c": "", "\u200d": "", "\u2060": "", "\ufeff": "",
    "\u2028": "\n", "\u2029": "\n",
}

DASH = r"(?:-|–|—|to)"
SECONDS_RANGE = re.compile(
    rf"(?<![\d:.,])(\d{{1,2}}(?:\.\d+)?)\s*(?:s|sec|secs|seconds)?\s*{DASH}\s*"
    rf"(\d{{1,2}}(?:\.\d+)?)\s*(?:s|sec|secs|seconds)\b",
    re.I,
)
CLOCK_RANGE = re.compile(
    rf"(?<![\d.])(\d{{1,2}}):(\d{{2}}(?:\.\d+)?)\s*{DASH}\s*(\d{{1,2}}):(\d{{2}}(?:\.\d+)?)"
)

AT_REF = re.compile(r"@\s?(image|video|audio)\s?(\d+)", re.I)
BARE_IMAGE_REF = re.compile(r"(?<![@\w])(?<!@ )image\s?(\d+)\b", re.I)
BARE_CALLOUT = re.compile(
    r"(?:^|[.!?]\s+)(?:reference|ref\.?|use|see|like)\s+@\s?(?:image|video|audio)\s?\d+\s*(?:[.!?]|$)",
    re.I | re.M,
)
QUOTE = re.compile(r'"([^"]{0,500})"|“([^”]{0,500})”', re.S)
VO_CUE = re.compile(
    r"\b(voice[- ]?over|vo|narrat\w*|say|says|said|saying|speak|speaks|spoken|speaking|dialogue|announces|whispers|shouts|asks|replies|sings)\b",
    re.I,
)
ONSCREEN_CUE = re.compile(
    r"\b(text|title|caption|subtitle|card|logo|reads|lettering|sign|graphic|words?|headline|label|engraved)\b",
    re.I,
)
MUSIC_CUE = re.compile(r"\b(beat-?sync\w*|on (?:the|every) (?:heavy |musical )?beats?|beats? of the (?:music|track|song)|"
                       r"bgm|music|musical|rhythm|downbeat|tempo|soundtrack)\b", re.I)
SOUND_CUE = re.compile(r"\b(sfx|sound|sounds|audio|voice[- ]?over|says)\b", re.I)
ENDING_CUE = re.compile(
    r"ends? held|take ends|holds? on|final (?:shot|frame|image)|freeze[- ]frame|comes to rest|"
    r"cut to (?:pure )?black|ends (?:on|with)|still (?:gliding|moving|rolling|tracking|travell?ing)",
    re.I,
)
VO_FINISH = re.compile(r"finish(?:es)? before the (?:video|clip|take) ends", re.I)
EXCLUSION_HEADER = re.compile(
    r"^\s*(?:negatives?|negative prompt|avoid|exclusions?|do not include|don't include|must not)\b",
    re.I | re.M,
)
NEG_WORD = re.compile(r"\b(?:no|without|never|avoid)\b", re.I)
PLACEHOLDER = re.compile(
    r"\[(?:your|insert|add|placeholder|todo|tbd|line|text|vo|voiceover|brand)[^\]]*\]|\b(?:TBD|TODO|lorem ipsum)\b",
    re.I,
)
SCENE_DEF = re.compile(r"^\s*(?:scene|shot)\s+(\d+)\s*[:.\-–—|,]", re.I | re.M)
SCENE_REF = re.compile(r"\b(?:scene|shot)\s+(\d+)\b", re.I)
# Case-sensitive on purpose: proper-noun spellings only, and no words that double as ordinary
# nouns (apple, amazon, evergreen) so "apple flavour" or "close-ups" don't trip it.
BRANDS = re.compile(
    r"\b(Boeing|BOEING|Airbus|AIRBUS|Embraer|Maersk|MAERSK|MSC|CMA CGM|Hapag-Lloyd|COSCO|FedEx|DHL|UPS|Volvo|"
    r"Scania|Mercedes|Kenworth|Peterbilt|Freightliner|Tesla|iPhone|Nike|Adidas|Coca-Cola|Pepsi|Starbucks|McDonald'?s|"
    r"SAP|Salesforce|ServiceNow|Microsoft Teams|Slack|Workday|Jira)\b"
)
GAZE = re.compile(
    r"\b(?:look\w*|gaz\w*|star\w*|glanc\w*)\s+(?:up\s+|straight\s+|directly\s+)?(?:at|into|to|toward|towards)\s+"
    r"(?:the\s+)?(?:camera|lens|viewer)|eye contact|camera gaze|direct gaze",
    re.I,
)
CROSS_CLIP = re.compile(r"\b(?:next|previous|following|prior|other)\s+(?:clip|video|generation)\b", re.I)
CONTEXT_LEAK = re.compile(r"\b(?:same as (?:before|above|the (?:previous|last|other))|as above|as before|previously|"
                          r"continues from|continuing from|from the (?:last|previous) (?:shot|clip|scene))\b", re.I)
LENS_MM = re.compile(r"\b(\d{2,3})\s?mm\b", re.I)
LENS_FOV = re.compile(r"\d{1,3}\s?(?:°|degrees?)\s+(?:diagonal\s+)?field of view|field of view", re.I)
TRANSITION_FX = re.compile(r"\b(?:cross-?fade|dissolve|fade[- ](?:to|in|out|through)|fades? to black)\b", re.I)
MM_TO_FOV = {16: 107, 18: 100, 20: 94, 24: 84, 28: 75, 35: 63, 40: 57, 50: 47, 65: 37, 70: 34, 85: 29, 100: 24, 135: 18, 200: 12, 300: 8}
ASSET_ID = re.compile(r"\b(?:CH|OBJ|ENV)_?\d{2}[A-Za-z]?\b|\bKF_S\d{2}_[A-Z]\w*")
IMG_CROSSREF = re.compile(r"\bsame (?:as|exact)\b|previous (?:image|keyframe|shot|frame)|reference sheet|turnaround|"
                          r"character sheet|model sheet", re.I)
NO_ITEM = re.compile(r"\bno\s+[a-z]", re.I)
_R = r"(?:toward|towards|to|facing)\s+frame\s+right|walk\w*\s+(?:to\s+the\s+)?right\b"
_L = r"(?:toward|towards|to|facing)\s+frame\s+left|walk\w*\s+(?:to\s+the\s+)?left\b"
_NEAR = r"[^.]{0,40}(?:faces?|toward|towards|nearer|near side|closest|to)\s+(?:the\s+)?(?:camera|lens)"
SIDE_RULES = [
    (re.compile(_R, re.I), re.compile(r"\bleft\s+(?:side|shoulder|hand|arm|cheek|ear)" + _NEAR, re.I),
     "moves or faces frame right, so the RIGHT side is toward the lens, not the left"),
    (re.compile(_L, re.I), re.compile(r"\bright\s+(?:side|shoulder|hand|arm|cheek|ear)" + _NEAR, re.I),
     "moves or faces frame left, so the LEFT side is toward the lens, not the right"),
    (re.compile(r"(?:over|behind|past)\s+(?:his|her|their)\s+left\s+shoulder", re.I),
     re.compile(r"left\s+shoulder[^.]{0,60}\bleft\s+edge", re.I),
     "camera just outside the LEFT shoulder puts that shoulder at frame RIGHT (or keep it out of frame)"),
    (re.compile(r"(?:over|behind|past)\s+(?:his|her|their)\s+right\s+shoulder", re.I),
     re.compile(r"right\s+shoulder[^.]{0,60}\bright\s+edge", re.I),
     "camera just outside the RIGHT shoulder puts that shoulder at frame LEFT (or keep it out of frame)"),
]
# Still-image checks (adapted from Higgsfield's LIRA guide)
PARAM_IN_PROSE = re.compile(r"--ar\b|(?<![\d:.])(?:1:1|16:9|9:16|4:3|3:4|3:2|2:3|21:9|9:21|4:5|5:4)(?![\d:])|"
                            r"\b(?:1\.5|[248])k\b|\b(?:1080|2160|4320)p\b", re.I)
KEYWORD_STACK = re.compile(r"\b(?:masterpiece|best quality|high quality|ultra[- ]?detailed|highly detailed|8k uhd|"
                           r"trending on artstation|award[- ]winning|hyper[- ]?detailed|ultra[- ]?realistic)\b", re.I)
ILLUSTRATION = re.compile(r"\b(?:painterly|concept art|digital painting|illustration|illustrated|3d render|cgi)\b", re.I)
# Video performance check (adapted from Higgsfield's ACTING guide): an emotion named instead of behaviour
_EMOTIONS = (r"sad|angry|nervous|anxious|happy|worried|scared|afraid|frightened|upset|guilty|ashamed|confident|"
             r"determined|emotional|excited|furious|shocked|surprised|relieved|frustrated|heartbroken|desperate")
EMOTION_LABEL = re.compile(rf"\b(?:looks?|appears?|seems?|feels?|becomes?|grows?|is|are)\s+(?:very\s+|visibly\s+|"
                           rf"clearly\s+|increasingly\s+|deeply\s+)?(?:{_EMOTIONS})\b|\b(?:{_EMOTIONS})\s+"
                           rf"(?:expression|face|look)\b|\bexpression of (?:\w+ )?(?:{_EMOTIONS})\b", re.I)
WORD = re.compile(r"[A-Za-z0-9À-ÿ]+(?:['’\-][A-Za-z0-9À-ÿ]+)*")

VO_WORDS_PER_SEC = 2.5       # whole-clip budget
VO_SEGMENT_WORDS_PER_SEC = 3.0  # looser per-segment ceiling
MIN_SEGMENT = 1.5


def words(s):
    return len(WORD.findall(s))


def fmt(x):
    return f"{x:g}"


def find_segments(text):
    segs = []
    for m in SECONDS_RANGE.finditer(text):
        a, b = float(m.group(1)), float(m.group(2))
        if b > a:
            segs.append((a, b, m.start()))
    for m in CLOCK_RANGE.finditer(text):
        a = int(m.group(1)) * 60 + float(m.group(2))
        b = int(m.group(3)) * 60 + float(m.group(4))
        if b > a:
            segs.append((a, b, m.start()))
    segs.sort(key=lambda s: s[2])
    return segs


def classify_quotes(text):
    """Return [(content, start, kind)] where kind is 'vo', 'text' or 'other'."""
    out = []
    for m in QUOTE.finditer(text):
        content = m.group(1) if m.group(1) is not None else m.group(2)
        window = text[max(0, m.start() - 160):m.start()]
        context = re.split(r"(?<=[.!?])\s+|\n\s*\n", window)[-1]
        vo = list(VO_CUE.finditer(context))
        onscreen = list(ONSCREEN_CUE.finditer(context))
        if vo and (not onscreen or vo[-1].start() > onscreen[-1].start()):
            kind = "vo"
        elif onscreen:
            kind = "text"
        else:
            kind = "other"
        out.append((content, m.start(), kind))
    return out


def main():
    ap = argparse.ArgumentParser(description="Lint a Seedance 2.5 prompt before submitting it on Higgsfield.")
    ap.add_argument("prompt_file")
    ap.add_argument("--duration", type=float, help="clip length in seconds (required unless --image)")
    ap.add_argument("--model", default="seedance_2_5", choices=("seedance_2_5", "seedance_2_0"))
    ap.add_argument("--mode", choices=MODES + MODES_20,
                    help="2.5: t2v (default) | omni_reference | video_edit | video_extension; 2.0: std (default) | fast")
    ap.add_argument("--images", type=int, default=0)
    ap.add_argument("--videos", type=int, default=0)
    ap.add_argument("--audios", type=int, default=0)
    ap.add_argument("--start-image", action="store_true")
    ap.add_argument("--end-image", action="store_true")
    ap.add_argument("--extension-mode", choices=("forward", "backward"))
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--image", action="store_true", help="lint a still-image prompt instead of a video prompt")
    ap.add_argument("--sheet", action="store_true", help="with --image: an intentional multi-panel approval sheet")
    ap.add_argument("--edit", action="store_true", help="with --image: an image-edit prompt (CHANGE / PRESERVE EXACTLY)")
    a = ap.parse_args()
    if (a.sheet or a.edit) and not a.image:
        ap.error("--sheet and --edit only apply with --image")
    if not a.image and a.duration is None:
        ap.error("--duration is required for video prompts (use --image for still prompts)")
    if a.mode is None:
        a.mode = "std" if a.model == "seedance_2_0" else "t2v"
    if (a.model == "seedance_2_0") != (a.mode in MODES_20):
        ap.error(f"mode {a.mode} doesn't belong to {a.model}")

    path = Path(a.prompt_file)
    raw = path.read_text(encoding="utf-8")
    errors, warns, oks = [], [], []

    # --- whitespace hygiene -------------------------------------------------
    odd = sum(raw.count(ch) for ch in ODD_WHITESPACE)
    text = raw
    if odd:
        cleaned = raw
        for ch, rep in ODD_WHITESPACE.items():
            cleaned = cleaned.replace(ch, rep)
        if a.fix:
            path.write_text(cleaned, encoding="utf-8")
            oks.append(f"normalized {odd} non-standard whitespace character(s) in {path.name}")
        else:
            warns.append(f"{odd} non-standard whitespace character(s) (non-breaking/zero-width spaces, "
                         "usually from a Docs/Notion paste); re-run with --fix")
        text = cleaned
    text = text.strip()
    n_words = words(text)

    if a.image:
        unq = QUOTE.sub('""', text)
        img_checks = [(ASSET_ID, "asset ID")] + ([] if (a.sheet or a.edit) else [(IMG_CROSSREF, "cross-reference/sheet wording")])
        for rx, why in img_checks:
            hit = rx.search(text)
            if hit:
                warns.append(f"{why} '{hit.group(0)}' can be printed as a caption or point at nothing; write it out")
        note = re.search(r"\([^)]*\b(?:note|tbd|todo|production|optional|see|e\.g\.|i\.e\.|placeholder|version|v\d|"
                         r"(?:CH|OBJ|ENV)\d{2})\b[^)]*\)", text, re.I)
        if note:
            warns.append(f"'{note.group(0)[:60]}' reads like a production note and can end up in the image; fold it in or drop it")
        nos = NO_ITEM.findall(unq)
        if not a.edit and (len(nos) >= 2 or EXCLUSION_HEADER.search(unq)):
            warns.append(f"{len(nos)} 'no X' phrases; negative lists summon what they name. State what IS there (prompt rule 5)")
        if a.edit:
            if not re.search(r"^\s*CHANGE\s*:", text, re.M) or not re.search(r"PRESERVE EXACTLY", text):
                warns.append("edit prompt without a CHANGE: line and a PRESERVE EXACTLY list; the model will repaint "
                             "more than you asked (template in references/image-prompts.md)")
            elif len(re.findall(r"^\s*CHANGE\s*:", text, re.M)) > 1:
                warns.append("more than one CHANGE block; make one change per pass")
            removal = re.search(r"\bremove\b[^.\n]*", text, re.I)
            if removal and not re.search(r"\b(?:fill|replace|continu\w*|behind|in its place|where it was)\b", removal.group(0), re.I):
                warns.append(f"'{removal.group(0)[:60]}': say what fills the gap (e.g. 'continuous brick wall behind')")
        param = PARAM_IN_PROSE.search(unq)
        if param:
            warns.append(f"'{param.group(0)}' in the prompt text; aspect ratio and resolution are CLI flags, not prose")
        stack = KEYWORD_STACK.search(unq)
        if stack:
            warns.append(f"'{stack.group(0)}' is keyword stacking and does nothing; name the lens, light and materials instead")
        illo = ILLUSTRATION.search(unq)
        if illo and not a.edit:
            warns.append(f"'{illo.group(0)}' pulls a photoreal still toward illustration; if it should look photographed, "
                         "use photo anchors (camera, film stock, real materials) instead")
        for hit in (BRANDS.search(unq), GAZE.search(unq), PLACEHOLDER.search(text)):
            if hit:
                warns.append(f"'{hit.group(0)}': brand, gaze wording or placeholder; rewrite")
        if n_words > 330:
            warns.append(f"{n_words} words; aim for 80–150 on a simple still and at most about 330 with bible and spec lines "
                         "(past that, details start dropping out)")
        print(f"Preflight {path.name}: {n_words} words · still image")
        for w in warns:
            print(f"WARN   {w}")
        for o in oks:
            print(f"OK     {o}")
        if not warns:
            print("OK     no issues found")
        return 0

    # --- duration and mode rules (mirror the Higgsfield schema) -------------
    d = a.duration
    hi = 15 if a.model == "seedance_2_0" else 30
    if d != int(d) or not 4 <= d <= hi:
        errors.append(f"duration {fmt(d)} s is invalid: {a.model} takes whole seconds from 4 to {hi}")
    frames = int(a.start_image) + int(a.end_image)
    media = a.images + a.videos + a.audios + frames
    if a.model == "seedance_2_0":
        if a.images + (int(a.start_image) + int(a.end_image)) > 9:
            errors.append(f"{a.images + int(a.start_image) + int(a.end_image)} images (incl. start/end frames) exceeds Seedance 2.0's limit of 9")
        if a.videos > 3 or a.audios > 3 or media > 12:
            errors.append("Seedance 2.0 allows at most 3 videos, 3 audios and 12 reference files in total")
        if a.audios and not (a.images or a.videos or a.start_image or a.end_image):
            errors.append("Seedance 2.0 audio references need at least one image, video or start/end frame")
    if a.model == "seedance_2_5" and a.mode == "t2v" and media:
        errors.append("mode t2v rejects all media; use omni_reference for references or start/end frames")
    if a.mode == "omni_reference" and not media:
        errors.append("mode omni_reference needs at least one reference or a start/end frame; use t2v for text only")
    if a.mode == "video_edit" and a.videos != 1:
        errors.append("mode video_edit needs exactly one video (--videos 1)")
    if a.mode == "video_extension":
        if a.videos < 1:
            errors.append("mode video_extension needs at least one source video")
        if not a.extension_mode:
            errors.append("mode video_extension needs an extension mode (here --extension-mode; on the CLI --extension_mode forward|backward)")
    elif a.extension_mode:
        errors.append("extension_mode is only allowed with mode video_extension")
    if frames and a.model == "seedance_2_5" and a.mode != "omni_reference":
        errors.append("start/end frames are only allowed in mode omni_reference")
    if a.model == "seedance_2_5" and a.images + frames > 30:
        errors.append(f"{a.images + frames} images (incl. start/end frames) exceeds the limit of 30")
    if a.model == "seedance_2_5" and media > 50:
        errors.append(f"{media} media items exceeds the limit of 50")

    # --- @ references -------------------------------------------------------
    refs = {"image": set(), "video": set(), "audio": set()}
    for m in AT_REF.finditer(text):
        refs[m.group(1).lower()].add(int(m.group(2)))
    attached = {"image": a.images, "video": a.videos, "audio": a.audios}
    source_video_mode = a.mode in ("video_edit", "video_extension")
    for kind, called in refs.items():
        n = attached[kind]
        label = kind.capitalize()
        over = sorted(i for i in called if i > n)
        if over:
            errors.append(f"prompt calls out @{label} {', '.join(map(str, over))} but only {n} {kind} "
                          f"reference(s) will be attached")
        unused = [i for i in range(1, n + 1) if i not in called]
        if unused and not (kind == "video" and source_video_mode):
            warns.append(f"attached but never called out: " + ", ".join(f"@{label} {i}" for i in unused)
                         + " (say what each reference governs, or don't attach it)")
    if BARE_CALLOUT.search(text):
        warns.append("bare callout such as 'Reference @Video 1.' found; name what it governs "
                     "(camera movement? rhythm? impact? style?)")
    if frames and BARE_IMAGE_REF.findall(text):
        warns.append("start/end frames are attached and the prompt says 'Image N' without @; refer to the frames in words "
                     "('the start frame') and number only the --image-references as @Image 1, 2…")

    # --- timestamps and beat density ---------------------------------------
    segs = find_segments(text)
    music_paced = bool(MUSIC_CUE.search(text)) and (a.audios > 0 or not a.no_audio)
    scene_labels = SCENE_DEF.findall(text)
    if segs:
        ordered = sorted(segs, key=lambda s: (s[0], s[1]))
        first, last_end = ordered[0][0], max(s[1] for s in ordered)
        if first > 0.5:
            warns.append(f"first timestamp starts at {fmt(first)} s; 0–{fmt(first)} s is unscripted")
        for (a0, b0, _), (a1, b1, _) in zip(ordered, ordered[1:]):
            if a1 - b0 > 0.3:
                warns.append(f"gap between {fmt(b0)} s and {fmt(a1)} s is unscripted")
            elif b0 - a1 > 0.3:
                warns.append(f"segments {fmt(a0)}–{fmt(b0)} s and {fmt(a1)}–{fmt(b1)} s overlap")
        if last_end > d + 0.05:
            errors.append(f"timestamps run to {fmt(last_end)} s but the duration is {fmt(d)} s")
        elif last_end < d - 1.0:
            warns.append(f"timestamps stop at {fmt(last_end)} s of {fmt(d)} s; the unscripted tail is where "
                         "endings drift. Extend the last segment to the full duration")
        short = [f"{fmt(s[0])}–{fmt(s[1])} s" for s in ordered if s[1] - s[0] < MIN_SEGMENT]
        if short:
            warns.append(f"segments under {fmt(MIN_SEGMENT)} s tend to be merged or dropped: {', '.join(short)}")
        if len(ordered) > d / 2:
            lo, hi = max(1, int(d // 3)), max(2, round(d / 2.5))
            warns.append(f"{len(ordered)} segments in {fmt(d)} s is dense; aim for ~{lo}–{hi} "
                         "beats with one action each")
        if not errors or all("timestamps run" not in e for e in errors):
            oks.append(f"{len(ordered)} timed segment(s) covering {fmt(first)}–{fmt(last_end)} s "
                       f"(shortest {fmt(min(s[1] - s[0] for s in ordered))} s)")
    else:
        if scene_labels and len(scene_labels) > d / 2:
            warns.append(f"{len(scene_labels)} scenes in {fmt(d)} s is dense; the model will merge or skip some")
        if d >= 20 and not music_paced:
            warns.append(f"no timestamps in a {fmt(d)} s prompt; add a time range per segment "
                         "(mandatory at 20 s+ unless a music reference paces the cuts)")
        elif d >= 20:
            oks.append("no timestamps, but the cuts are paced by music; fine for beat-synced montages")
        elif d >= 10:
            warns.append(f"no timestamps in a {fmt(d)} s prompt; time ranges keep beats from merging")

    # --- quotes, voiceover, on-screen text ---------------------------------
    quotes = classify_quotes(text)
    straight = text.count('"')
    if straight % 2:
        warns.append("odd number of straight double quotes; a quoted line may be unbalanced")
    for content, _, _ in quotes:
        if not content.strip():
            errors.append('empty quotation marks (""): fill in the exact words or remove them')
    if PLACEHOLDER.search(text):
        errors.append(f"placeholder left in the prompt: '{PLACEHOLDER.search(text).group(0)}'")

    vo_quotes = [(c, pos) for c, pos, k in quotes if k == "vo" and c.strip()]
    unquoted = QUOTE.sub('""', text)
    vo_mentioned = bool(VO_CUE.search(unquoted))
    if vo_mentioned and not vo_quotes and not a.no_audio:   # with audio off, unquoted speech is just mouth movement
        warns.append("voiceover/speech is mentioned but no line is quoted; the model will improvise the words")
    if vo_quotes:
        total_vo = sum(words(c) for c, _ in vo_quotes)
        budget = VO_WORDS_PER_SEC * max(d - 1, 1)
        if total_vo > budget:
            warns.append(f"voiceover is {total_vo} words; ~{int(budget)} fit in {fmt(d)} s at "
                         f"{fmt(VO_WORDS_PER_SEC)} words/s with the last second clear")
        else:
            oks.append(f"voiceover {total_vo} words (budget ~{int(budget)})")
        if not VO_FINISH.search(text):
            warns.append("add: 'The voiceover must finish before the video ends.'")
        if segs:
            spans = sorted(segs, key=lambda s: s[2])
            for i, (s0, s1, pos) in enumerate(spans):
                end_pos = spans[i + 1][2] if i + 1 < len(spans) else len(text)
                seg_words = sum(words(c) for c, qpos in vo_quotes if pos <= qpos < end_pos)
                if seg_words > VO_SEGMENT_WORDS_PER_SEC * (s1 - s0):
                    warns.append(f"segment {fmt(s0)}–{fmt(s1)} s carries {seg_words} voiceover words; "
                                 f"~{int(VO_SEGMENT_WORDS_PER_SEC * (s1 - s0))} fit")

    # --- exclusion lists ----------------------------------------------------
    if EXCLUSION_HEADER.search(unquoted):
        warns.append("a Negatives/Avoid section lists things to exclude; naming them tends to summon them. "
                     "Turn each into a positive statement inside the segment where it matters")
    else:
        for sent in re.split(r"(?<=[.!?])\s+|\n\s*\n", unquoted):
            s = sent.strip()
            if len(NEG_WORD.findall(s)) >= 3 or (re.match(r"(?:no|avoid|without)\b", s, re.I) and s.count(",") >= 2):
                warns.append(f"reads like an exclusion list: '{s[:80]}...'; rewrite as what IS there")
                break

    # --- audio consistency --------------------------------------------------
    if a.no_audio and a.audios == 0:
        if vo_quotes:
            warns.append("voiceover lines are quoted but generated audio is off (--no-audio)")
        elif MUSIC_CUE.search(text) or SOUND_CUE.search(text):
            warns.append("beat/music/sound language with generated audio off and no audio reference does nothing")

    # --- self-containment and ending ---------------------------------------
    defined = {int(x) for x in scene_labels}
    dangling = sorted({int(x) for x in SCENE_REF.findall(text)} - defined)
    if dangling:
        warns.append(f"refers to scene/shot {', '.join(map(str, dangling))} which this prompt never defines; "
                     "the model only sees this clip. Describe the final frame instead")
    if CROSS_CLIP.search(text):
        warns.append(f"mentions '{CROSS_CLIP.search(text).group(0)}'; the model can't see other generations")
    if d >= 8 and not ENDING_CUE.search(text) and a.mode != "video_edit":
        warns.append("ending isn't pinned; restate the final state in the last segment: 'The take ends held on this frame.' "
                     "for a hold, or the final composition with the motion still running for a cut on movement")
    leak = CONTEXT_LEAK.search(text)
    if leak:
        warns.append(f"'{leak.group(0)}' points at something the model can't see; state it outright")
    lonely = [m.group(1) for m in LENS_MM.finditer(text)
              if not LENS_FOV.search(text[max(0, m.start() - 120):m.end() + 120])]
    for rx_move, rx_side, why in SIDE_RULES:
        if rx_move.search(text) and rx_side.search(text):
            warns.append(f"side conflict: {why} (Sides table in references/shot-direction.md)")
    aid = ASSET_ID.search(text)
    if aid:
        warns.append(f"asset ID '{aid.group(0)}' in the prompt text; the model sees words, not your IDs. Describe it or use @Image N")
    if lonely:
        conv = ", ".join(f"{v} mm ≈ {MM_TO_FOV[min(MM_TO_FOV, key=lambda k: abs(k - int(v)))]}°" for v in dict.fromkeys(lonely))
        warns.append(f"lens given only in millimetres ({conv}); add a diagonal field of view, camera distance and "
                     "the visible optical result (see references/shot-direction.md)")
    fx = TRANSITION_FX.search(text)
    if fx:
        warns.append(f"'{fx.group(0)}': the model may render a transition effect; use hard cuts unless a dissolve is wanted")
    gaze = GAZE.search(QUOTE.sub('""', text))
    if gaze:
        warns.append(f"mentions '{gaze.group(0)}'; even as a prohibition it can summon the look. "
                     "Give the eyes a target instead ('eyes on the pallet trucks')")
    brand = BRANDS.search(QUOTE.sub('""', text))
    if brand:
        warns.append(f"real brand/model name '{brand.group(0)}' can pull in real liveries or logos and trigger ip_detected; "
                     "describe the type instead")
    emo = EMOTION_LABEL.search(QUOTE.sub('""', text))
    if emo:
        warns.append(f"'{emo.group(0)}' names an emotion; write the behaviour that shows it (breath, tempo, business, "
                     "gaze target, distance), see references/acting.md")

    if d and n_words / d > 75:
        warns.append(f"{n_words} words for a {fmt(d)} s clip; check the extra words are control (position, lens, light) "
                     "rather than extra events, which the clip can't show")
    elif n_words > 800:
        warns.append(f"{n_words} words is very long; the strongest examples run 150–400")

    # --- report -------------------------------------------------------------
    media_desc = f"{a.model} · images={a.images} videos={a.videos} audios={a.audios}" + (
        " +start" if a.start_image else "") + (" +end" if a.end_image else "")
    print(f"Preflight {path.name}: {n_words} words · {fmt(d)} s · {a.mode} · {media_desc}"
          + (" · audio off" if a.no_audio else ""))
    for e in errors:
        print(f"ERROR  {e}")
    for w in warns:
        print(f"WARN   {w}")
    for o in oks:
        print(f"OK     {o}")
    if not errors and not warns:
        print("OK     no issues found")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
