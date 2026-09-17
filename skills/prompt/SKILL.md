---
name: prompt
description: >-
  Write, fix, review or lint a ByteDance Seedance 2.5 or 2.0 video prompt for Higgsfield, or a
  keyframe image prompt for one, without spending any credits. Directs the shot first (blocking,
  body-to-frame sides, field-of-view optics, light direction), applies the craft rules that stop
  beats merging, sides flipping, lenses drifting, invented lettering and frozen endings, and runs
  the local preflight linter. Use when the user pastes a Seedance or Higgsfield prompt to improve,
  asks why a generation went wrong, wants prompts drafted to run later, wants a side-by-side
  before/after, or says not to run anything or not to use credits. The generate, plan and edit
  skills in this plugin also use it whenever they write a prompt.
argument-hint: "[prompt text, prompt file or shot brief]"
compatibility: Requires python3 for the preflight linter.
---

# Write and lint a Seedance prompt

This skill writes a Seedance prompt that survives a long, multi-beat generation, or fixes one that didn't. It never spends credits. To price and run the result, hand over to `higgsfield-seedance:generate` (or `:edit` for an existing clip).

*Rules version 2026-09-11 (4th revision). Stamp approved prompt sets with this date, so a later rule change doesn't silently invalidate them.*

`${CLAUDE_PLUGIN_ROOT}` is the plugin's folder, two levels above this skill's folder. Shared references live in `${CLAUDE_PLUGIN_ROOT}/references/` and scripts in `${CLAUDE_PLUGIN_ROOT}/scripts/`.

## 1. Know the settings first

The prompt depends on the settings it will run with. When another skill in this plugin called this one, they come from there. Otherwise ask, or default to Seedance 2.5, `t2v`, 16:9, generated audio on:

- **Model:** `seedance_2_5` (4–30 s) or `seedance_2_0` (4–15 s, modes `std`/`fast`).
- **Mode, and what the prompt must do in it:** `t2v` describes everything. `omni_reference` describes staging and motion while the references carry the subject. `video_edit` describes the change and what stays untouched. `video_extension` describes only the new footage.
- **Duration,** and the attachments in flag order (they set the `@Image N` / `@Video N` / `@Audio N` numbering), start or end frames, and whether audio is generated.
- **How the clip will be used:** trimmed to a short window, cut on motion, chained from its last frame, or held under a title card.

First/last-frame clips have their own logic in `${CLAUDE_PLUGIN_ROOT}/references/first-last-frame.md`, and edits and extensions in `${CLAUDE_PLUGIN_ROOT}/references/edit-extend-chain.md`. Read the matching file before writing one.

## 2. Check the brief

- **Voiceover and on-screen text are the user's words.** If they didn't supply them, draft them and show them before anything is generated.
- **When the clip is one scene of a longer film**, the voiceover and music usually belong to the edit: one narrator and one score across all scenes, and lines that run past this clip's cut. Default to generated location sound only, with no voiceover in the prompt, and say so. Keep copy marked "added in post" out of the prompt, but keep the empty space the brief reserves for it. If a narrator talks over the scene, keep the generated sound to ambience. An on-camera line, such as a radio call, will clash with the voiceover, so write "his voice stays under the yard noise" instead of scripting words.
- **Check the brief against the camera.** Briefs often ask for details the stated camera can't see, such as a driver "visible through the windscreen" from a camera above and behind the truck. Flag each conflict, pick the reading that protects the shot's main job (usually the composition an edit depends on), and tell the user what you chose.

## 3. Direct the shot first

Before writing, strip the brief to this one shot and ask where it will fail: an empty first frame, left and right flipped, the lens drifting, flat light, a prop in the wrong hand, a person arriving late. `${CLAUDE_PLUGIN_ROOT}/references/shot-direction.md` covers the full diagnosis and the tools for each risk. It's adapted from Higgsfield's own Seedance guide (CINEDANCE V4) and covers blocking, gaze, location maps, field-of-view optics, physics, lighting locks, cut types, dialogue and a self-check. Read it before writing any shot with people, props or a demanding camera.

## 4. Shape

For a single shot, write in this order and skip what adds nothing:

```
scene context → active references (@Image N + anchor line) → location map → first frame and blocking
→ format mode (single take / defined cuts) → optics → camera → action timing → physics
→ lighting → audio (voiceover, sound events) → positive constraints → one style anchor, last
```

Durations, aspect ratio, resolution, mode and generated audio are CLI flags. Don't repeat them in the prompt text.

For anything 15 s or longer with several beats, start from a pattern in `${CLAUDE_PLUGIN_ROOT}/references/prompt-patterns.md`: beat-synced match-cut, single-throughline educational, timestamped tutorial, commercial with @Video dynamics, or continuous-shot chapters. Each one has a full worked example, and the file also has a camera-language table.

## 5. Rules that change the output

Each of these came from generations that went wrong without it.

1. **Segment by time and keep each segment whole.** From 10 s up, give every segment a time range and one clear action. From 20 s up it's mandatory, unless a music reference drives the cuts. Put a segment's camera, action, light and text together under its timestamp. If the prompt splits camera, lighting and action into separate attribute blocks (WHO / WHERE / CAMERA / LIGHTING, each listing every shot), the model has to match list items up by position, and it pairs them wrong. If the user writes in that style, regroup it by time. There's a before/after in the patterns file.
2. **Budget the beats.** A 30 s take holds 8–12 beats, not 20. Segments shorter than about 2 s tend to get merged or dropped. Give the hero moment the longest window, and make the ranges run continuously from 0 to exactly the duration. An unscripted tail is where the model starts improvising. A 4 s clip reliably delivers one main action. In a Higgsfield test (September 2026), "pallets load, then the parked freighter starts to taxi" produced the loading and dropped the taxi. If the edit needs a particular action, make it the clip's first and only beat.
3. **Say what every reference governs.** Use `@Image 1`, `@Video 1`, `@Audio 1`, numbered separately per type in the order you attach them. Tie each one to the thing it controls: "the garment in @Image 2", "reference @Video 1's camera movement", "BGM references @Audio 1". A bare "reference @Video 1" is noise. Every callout must be attached, and every attachment should be called out.
4. **Let references carry the subject.** Don't re-describe what an attached image already shows, because the text competes with the picture and wins, wrongly. Give each referenced person or object one minimal anchor line: role, current state, the details this shot depends on, and which hand holds what. For example: "@Image 1: the red toolbox, carried in his left hand. 100% matches the reference." A project's character bible overrides the hands and props in this plugin's examples. For products, add this line verbatim: `If this description and the reference image disagree about the product, THE REFERENCE IMAGE WINS.` A location reference supplies geography, not framing, so set the camera yourself.
5. **Say what's there, not what isn't.** A negative list summons what it names: "no denim" has produced denim. Turn every exclusion of an object into a positive statement, e.g. "no fictional aircraft markings" becomes "plain unmarked white aircraft livery". Short negations aimed at failure modes are fine if they sit right after the positive state they protect: "Faces stay in shadow; no flat front light." "Hard cuts only; no dissolves." "No subtitles, no music." Repeat that statement in each segment where the thing appears, and for every surface that could carry lettering: hull, tail, trailer, uniform. Keep real brand and model names out ("Boeing 777F", a shipping line): they pull in real liveries and logos and can trigger `ip_detected`. Describe the type instead ("a wide-body twin-engine freighter").
6. **Quote every word the video must show or say.** Put on-screen text and voiceover in quotation marks, word for word, or the model invents lettering. Text that must be exactly right (dates, prices, names, legal lines) is safer added in the edit, because a garbled "October 2" costs a whole re-roll. Keep voiceover to about 2–2.5 words per second of its window, leave the last second silent, and add: `The voiceover must finish before the video ends.`
7. **List sounds by event** when audio is on: "soft blink, magic sparkle, juice-fill gurgle, glass clink". Listed sounds land on their actions, and unlisted ones get invented or skipped. Beat-sync language does nothing with `--generate_audio false` and no audio reference.
8. **Pin the ending, and match it to the cut.** Endings drift the most, so restate the final state inside the last segment and give the landing its own beat, with no other camera business stacked into it.
   - If the scene ends on a hold (a logo card, a final product shot), close with "The take ends held on this frame." For an end plate behind a card, let any camera drift settle by about 3 s, then lock off. Describe the space for the type as a positive ("clear, evenly graded sky at frame left and top"). Give the card about 3 s on screen.
   - If the shot cuts out on movement (a match cut on motion, a tracking camera), don't say "held", because it can freeze the move. Describe the final composition with the motion still running: "ends with the trailer roof centred on the vertical axis, the camera still gliding forward at the truck's speed."
9. **Keep the clip self-contained.** The model only sees this generation. Lines like "transition to Scene 2", "match the next clip", "same as before", "as above" or "continues from" point at nothing, and scene numbers and script headers are just noise. Describe the actual final frame instead, since that's also what a later clip will chain from. The same goes for image prompts. Asset IDs (`OBJ01`), "same as the previous image", "reference sheet", "turnaround" and production notes in brackets can come out printed as captions or as multi-panel sheets.
10. **Give small things room.** A micro-action (a zipper lifted two teeth, a brim tugged down) needs its own timestamp. An asymmetric detail needs its side stated in frame terms: "crest on his right chest, frame left as he faces camera". Convert body sides with the Sides table in `shot-direction.md`. Walking toward frame right shows the right side, not the left. Anyone lying down needs the whole body anchored ("in frame from head to bare feet"). Keep one mover per beat and say what stays still.
11. **Write people in words.** Give age, hair, build, wardrobe and one distinguishing detail, and repeat the wardrobe line in each segment where the person appears. A text description holds one character for a full 30 s take. Character names are only labels to the model; the description carries the identity. When a start frame already shows the person, a short "keeps her charcoal jacket and tablet unchanged" anchor is enough. See *Faces*.
12. **Frame fine detail close.** Small lettering and logo textures won't read in a wide shot at any resolution. Move the camera closer for the beat where they have to read.
13. **Clean the text.** Prompts pasted from Docs or Notion carry non-breaking spaces and glued words ("afreight", "trucktravelling"). Normalize the spaces and fix the words. The preflight script's `--fix` flag handles the spaces.
14. **Lock the first frame and the blocking.** For any clip that will be trimmed, write "The first visible frame already contains [who] in position." Place people in measurable terms, e.g. "within 1 metre of the trailer, hand on the door", not "near the trailer". Give the body and the eyes separate directions: "back to camera, eyes on the gallery opposite".
15. **Direct the lens by what it shows.** Give a diagonal field of view, a camera distance and the visible result, not just millimetres. Higgsfield's guide reports Seedance follows these better. Rough equivalents: 24 mm ≈ 84°, 35 mm ≈ 63°, 50 mm ≈ 47°, 85 mm ≈ 29°, 135 mm ≈ 18°. Keep portrait, environment and macro in separate beats so the lens doesn't drift.
16. **Give the light a direction.** Name the source, where it comes from relative to the camera, and which side of the subject falls into shadow or rim. Treat it as a constraint that must hold, since flat front light is the default failure.
17. **Screens are plates for post.** Any screen that will carry UI stays "plain dark glass with a soft even glow" in both the keyframe and the prompt, and the model never draws the interface. Keep it trackable: frame over the shoulder opposite the gesturing hand, keep all four corners in frame, keep the camera locked or slow, and allow one gesture per clip. A drag plus a tap needs 6 s or two clips. Keep finger speed unhurried so it can be rotoscoped. Deliver a tap map with the prompts: each contact point in screen terms, its clip time, and the UI it drives. A static UI moment is cheaper as a still with a push in post.

End with a global style block stated once: grade, focus, motion blur, render quality. For example: `Top-tier cinematic color grading. Subject in razor-sharp focus, backgrounds with motion blur. Photorealistic materials, global illumination.` Keep the block to what's true of every shot. A global "practical light only" contradicts a sunrise segment, so per-shot light belongs in the segments.

## 6. Faces

On the ByteDance API, Seedance 2.5 refuses most reference images that show a readable human face, AI-generated faces included, and it never accepts photos of real people. Treat that as true on Higgsfield until tested. In practice:

- Describe people in text by default (rule 11). That's enough to hold a character within one generation.
- **Count a face as readable** when it's at least ~8% of the frame height and turned no more than ~45° from the camera. Before routing a film's face shots, test once on 2.5 with a profile frame, a three-quarter frame and a small figure seen from behind (about 10 credits each). The test table and routing rules are in `${CLAUDE_PLUGIN_ROOT}/references/film-planning.md`.
- To keep the same character across separate generations, reuse the exact same description each time. Frame any chain frame so the face is small, turned away or covered, so the next clip rebuilds the face from text.
- If the user needs a specific real person (themselves, a presenter), use the approved identity routes in `higgsfield-generate`: Seedance 2.0 with an image the user has rights to, Soul ID, or Marketing Studio avatars. Don't disguise a face (overlays, filters, stylization tricks) to get it past the refusal. That dodges a deliberate safeguard and puts the account at risk.
- Seedance 2.0 caps at 15 s per clip. If speech has to run longer and is split across clips, each clip invents its own voice, and the join will be audible. Either keep the speech within one take, pass the same voice recording to every clip with `--audio-references`, or record the voiceover once and lay it in during the edit. Tell the user which one you chose.

## 7. Keyframe and image prompts

Stills that become start frames follow the same discipline:
- **Positive phrasing applies to image prompts too (rule 5).** Keep separate prefixes for people, objects and places, so a "real people at work" line doesn't land on an empty plate.
- **Write each keyframe prompt as if it were the only one.** The image model can't see "the previous keyframe's composition", so repeat the shared framing spec word for word in every keyframe prompt.
- **Keep faces in keyframes small, lowered or turned.** That gives Seedance 2.5 the best chance of accepting them as start frames.
- **Lint them with `--image`** (see below).

## 8. Preflight

Save the prompt to a file and lint it against the settings you plan to use:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py prompt.txt --mode omni_reference --duration 30 \
  --images 2 --videos 1 --audios 1 [--start-image] [--end-image] [--extension-mode forward] [--no-audio] [--fix]
```

It checks for:
- mode and media conflicts
- @-callouts beyond what's attached, and attachments that are never called out
- timestamps that overrun, fall short of the duration, overlap, or are too short
- exclusion lists
- empty or placeholder voiceover quotes
- voiceover over the word budget
- audio language while audio is off
- dangling scene references and context leaks ("same as before", "as above", "continues from")
- lenses given only in millimetres, with no field of view
- fade or dissolve wording
- camera-gaze wording and real brand names
- an unpinned ending
- non-breaking spaces (`--fix` rewrites the file)

Fix every ERROR. WARNs are judgment calls: a beat-synced montage can skip timestamps on purpose.

- **Seedance 2.0 shots:** add `--model seedance_2_0` (modes `std`/`fast`, 4–15 s, up to 9 images).
- **Keyframe and asset prompts:** use `--image`. It skips the video checks and flags asset IDs, "same as" cross-references, notes in brackets, "no X" lists and gaze wording.
- **Framing claims:** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/optics.py 70mm 120m` prints the frame width and height, to check phrases like "fills the middle third".

## 9. Fixing an existing prompt

- Lint it as it stands first, so the user sees what the linter caught.
- Diagnose it against §3 and the rules, and name the rule behind each change.
- Keep the user's voiceover and on-screen text word for word. If a line breaks the word budget (rule 6), flag it and offer a shorter version rather than rewriting it silently.
- When the user asks for a side-by-side, show the original and the rewrite with a short list of what changed and why.

## 10. Hand back

Deliver the prompt file path, the lint result, and the choices you made (conflicts resolved, defaults applied, anything dropped from the brief). Add a cut map or tap map when the clip will be trimmed or composited. Then offer the next step: price and run it with `higgsfield-seedance:generate`, which shows the cost before spending anything.
