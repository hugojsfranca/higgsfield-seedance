---
name: higgsfield-seedance-2-5
description: >-
  Generate videos with ByteDance Seedance 2.5 on Higgsfield (seedance_2_5): writes the prompt
  with the model's craft rules, lints it, prices it and runs it through the higgsfield CLI.
  Covers one-go films up to 30 s with cuts, beat-synced edits, voiceover and on-screen text;
  @Image/@Video/@Audio reference-driven video; first/last-frame transitions; editing a clip;
  extending a clip forward or backward. Use whenever the user mentions Seedance 2.5, wants a
  single Higgsfield video longer than 15 seconds, a match-cut brand film, timestamped tutorial,
  continuous-shot chapter film or start-to-end-frame transformation, wants to edit or extend a
  Higgsfield video, plan a multi-scene film with recurring characters, or asks to fix a Seedance
  prompt, even without naming the model. Not for
  talking-head videos driven by a person's photo (Seedance 2.0 or Marketing Studio via
  higgsfield-generate), native 4K, or multi-block narrated explainers (higgsfield-video-explainer).
compatibility: Requires the higgsfield CLI (logged in), python3 for the preflight linter, and ffmpeg for chaining.
---

# Seedance 2.5 on Higgsfield

This skill does two jobs: it writes a Seedance 2.5 prompt that survives a long, multi-beat generation, and it runs that prompt through the `higgsfield` CLI. The writing matters more than the command. A 30-second take holds 8–12 beats, and most bad results come from prompt structure rather than settings: beats that merge or vanish, invented lettering, endings that drift.

Model facts here were checked against the live schema (`higgsfield model get seedance_2_5`) in September 2026. If the CLI disagrees with this file, trust the CLI and re-run `model get`.

*Skill version 2026-09-11 (4th revision). It adds multi-scene film planning, shot direction adapted from Higgsfield's CINEDANCE guide, and Seedance 2.0 routing. Stamp approved prompt sets with this date, so a later rule change doesn't silently invalidate them.*

**Planning a multi-scene film,** or anything with recurring characters or objects? Read `references/film-planning.md` first. It covers the shot list, asset bible, reference library, face tests, screen plates, budget scenarios, approval gates and a shot-list checker (`scripts/shotlist_check.py`).

## 0. Bootstrap

- `higgsfield` must be on PATH. If not: `curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh`
- If `higgsfield account status` reports an expired session or no auth, ask the user to run `higgsfield auth login` and wait for them.

## 1. Is Seedance 2.5 the right model?

Seedance 2.5 earns its place for: one-go films longer than 15 s (Seedance 2.0 stops at 15 s), heavy multi-reference work (up to 30 images plus videos and audio), editing an existing clip, and extending a clip forward or backward. Route elsewhere when:

- **Someone talks to camera and the face comes from a photo.** Face references are unreliable on 2.5 (see *Faces*). Use Seedance 2.0 or Marketing Studio avatars via `higgsfield-generate`.
- **The user needs native 4K.** Seedance 2.0. (2.5 renders up to 1080p and can be upscaled, see §7.)
- **It's an ad and no model was named.** `higgsfield-generate` routes ads to Marketing Studio by default. Stay here if the user asked for Seedance 2.5 or the ad needs a 2.5 strength (length, many references, edit, extend).
- **It's a narrated explainer assembled from many blocks.** Use `higgsfield-video-explainer`.
- **It's a ≤15 s shot that needs no 2.5 feature and cost matters.** Seedance 2.0 at 720p is cheaper (about 4.5 vs 6.5 credits/s).

A film can mix models. Readable faces on 2.0 and everything else on 2.5 is a normal plan: grade-match in post and keep the wardrobe lines and light direction identical.

### Seedance 2.0 at a glance (for shots routed there)

Checked against `higgsfield model get seedance_2_0` in September 2026:
- **Job type and modes:** `seedance_2_0`, with `--mode std` or `fast` (fast renders at 480p or 720p only).
- **Length and resolution:** 4–15 s, and 480p up to 4K.
- **Frames and references:** `--start-image` and `--end-image` are allowed in any mode, alongside up to 9 images in total (the frames count) and 12 reference files overall.
- **Audio:** `--generate_audio` exists, and audio references need at least one image or video.
- **Cost:** about 4.5 credits/s at 720p (check 480p with `cost`).
- **Faces:** in testing, 2.0 accepted a photo of the user's own face as a reference. Still check the first clip before relying on it.

The prompt rules in §4 apply unchanged; Higgsfield wrote its CINEDANCE guide for this model. Lint 2.0 prompts with `preflight.py --model seedance_2_0`.

For face shots on 2.0:
- **Anchor line:** attach the master portrait of every readable face in frame as `--image-references`, each with an anchor line built from the bible: "@Image 1: <bible line>. 100% matches the reference for face, hair and build." Never write "matching @Image 1" inside @Image 1's own line; that's circular.
- **Route by the keyframe,** not by the storyboard's label. A "face" shot whose blocking turns the face away belongs on 2.5.
- **Test numbering:** `@Image` numbering beside a start frame is unverified on 2.0 too, so let the first 2.0 clip double as that test.

## 2. Pin the brief

Before writing, know: purpose and format, duration (4–30 s, integer), aspect ratio (`16:9`, `9:16`, `1:1`, `4:3`, `3:4`, `21:9`, `auto`), audio (generated or not, plus any music reference), assets (paths or Higgsfield IDs, and what each is for), exact on-screen text, exact voiceover lines, and final resolution.

Default what you can (16:9, generated audio on, 480p draft) and ask only for what you can't sensibly default, one question at a time. Voiceover and on-screen text are the user's words. If they didn't supply them, draft them and show them before spending credits.

**When the clip is one scene of a longer film**, the voiceover and music usually belong to the edit: one narrator and one score across all scenes, and lines that run past this clip's cut. Default to generated location sound only, with no voiceover in the prompt, and say so. Keep copy marked "added in post" out of the prompt, but keep the empty space the brief reserves for it. If a narrator talks over the scene, keep the generated sound to ambience. An on-camera line, such as a radio call, will clash with the voiceover, so write "his voice stays under the yard noise" instead of scripting words.

**Check the brief against the camera.** Briefs often ask for details the stated camera can't see, such as a driver "visible through the windscreen" from a camera above and behind the truck. Flag each conflict, pick the reading that protects the shot's main job (usually the composition an edit depends on), and tell the user what you chose.

**Keyframes first, when composition matters.** If the brief includes static keyframe prompts, or depends on exact compositions (match-cut geometry, space reserved for titles), ask whether keyframe images exist. If they don't, suggest making them first with an image model via `higgsfield-generate`. Get the stills approved, then animate each one with `--start-image`. A still locks composition far more reliably than text, and it's the cheapest place to iterate.
- **Which image model:** GPT Image 2 (about 6.5 credits) for exact objects and structure. Nano Banana 2 (`nano_banana_flash`, about 2) when references must carry over, because it takes `--image-references`. Soul Location (about 0.12) for people-free places; it takes a prompt only.
- **Recurring characters:** approve a master portrait first, then build every other view and every keyframe with that portrait attached as `--image-references`. A text description holds wardrobe, but not a face.
- **Positive phrasing applies to image prompts too (rule 5).** Keep separate prefixes for people, objects and places, so a "real people at work" line doesn't land on an empty plate.
- **Write each keyframe prompt as if it were the only one.** The image model can't see "the previous keyframe's composition", so repeat the shared framing spec word for word in every keyframe prompt.
- **Keep faces in keyframes small, lowered or turned.** That gives Seedance 2.5 the best chance of accepting them as start frames.

## 3. Pick the mode

The mode decides which inputs are legal and what the prompt has to do.

| Situation | `--mode` | Media flags | The prompt describes |
|---|---|---|---|
| Text only | `t2v` (default) | none (the API rejects any media) | everything |
| Any reference image/video/audio, and/or a start or end frame | `omni_reference` | `--image-references`, `--video-references`, `--audio-references` (all repeatable), `--start-image`, `--end-image` | staging and motion; the references carry the subject |
| Change something inside an existing clip | `video_edit` | exactly one `--video`, plus optional `--image-references` for a replacement | the change, and what stays untouched |
| Add footage after the last frame or before the first | `video_extension` plus `--extension_mode forward` or `backward` | at least one `--video` | only the new footage |

Hard limits: `--start-image` and `--end-image` only work in `omni_reference`. At most 30 images (start and end frames count) and 50 media items in total. Every media flag takes a local path (uploaded automatically) or a Higgsfield upload ID or job ID. That means a previous generation's job ID can go straight into `--video` for an edit or extension, with no download needed.

First/last-frame clips, edits and extensions each have their own prompt logic. Read `references/first-last-frame.md` or `references/edit-extend-chain.md` before writing one.

### One take, or one clip per shot?

Seedance 2.5 can cut between shots inside one generation, but that doesn't always make it the right plan.

- **Generate one clip per shot** (4 s minimum each) when the shots are separate places or times joined by hard cuts, when the edit will trim each shot to 2–3 s or less, when each shot has its own keyframe, or when you'll want to re-roll one shot without the others. A failed shot then costs one re-roll, not the whole scene, and the editor gets spare footage around every cut point. Example: three 1.3 s shots in a 4 s scene become three 4 s clips, 30 credits at 480p.
- **Generate one multi-shot take** when continuity across the cuts is the point (the same subject, grade or motion carrying through), when the model's own cutting rhythm is wanted (beat-synced montages), or when the scene runs 15–30 s with segments of 2 s or more.
- **Either way, write for the edit.** Start the action on the first frame and keep it going through the last, so the editor can choose the cut points. When clips will be trimmed, give the user a cut map: which window of each clip goes into the scene, and which match cut it serves. For example, the centred truck roof exists only in the last second of its clip. When the edit keeps under about 1.5 s of a clip, time any single event inside that window ("the tab snaps flat at about 1 s"). Otherwise a drop, hand-off or snap can land at 3.5 s, outside the slice.
- **Camera moves shrink with the trim.** A 30° orbit across a 4 s clip shows about 6° in a 0.8 s cut. If a move has to read on screen, make it faster or the shot longer, and tell the user.
- **Plan wipes where they can happen.** An in-camera wipe needs a body passing between the lens and the subject, which a high or overhead camera rarely gets. Instead, stage crossings along the edge of frame for the editor to cut on, or treat the wipe as an edit effect.
- **Keep screen direction consistent** across shots that cut together (vehicles, pans and props all flowing toward frame right, say), unless the brief wants a reversal.

## 4. Write the prompt

### Direct the shot first

Before writing, strip the brief to this one shot and ask where it will fail: an empty first frame, left and right flipped, the lens drifting, flat light, a prop in the wrong hand, a person arriving late. `references/shot-direction.md` covers the full diagnosis and the tools for each risk. It's adapted from Higgsfield's own Seedance guide (CINEDANCE V4) and covers blocking, gaze, location maps, field-of-view optics, physics, lighting locks, cut types, dialogue and a self-check. Read it before writing any shot with people, props or a demanding camera.

### Shape

For a single shot, write in this order and skip what adds nothing:

```
scene context → active references (@Image N + anchor line) → location map → first frame and blocking
→ format mode (single take / defined cuts) → optics → camera → action timing → physics
→ lighting → audio (voiceover, sound events) → positive constraints → one style anchor, last
```

Durations, aspect ratio, resolution, mode and generated audio are CLI flags. Don't repeat them in the prompt text.

For anything 15 s or longer with several beats, start from a pattern in `references/prompt-patterns.md`: beat-synced match-cut, single-throughline educational, timestamped tutorial, commercial with @Video dynamics, or continuous-shot chapters. Each one has a full worked example, and the file also has a camera-language table.

### Rules that change the output

Each of these came from generations that went wrong without it.

1. **Segment by time and keep each segment whole.** From 10 s up, give every segment a time range and one clear action. From 20 s up it's mandatory, unless a music reference drives the cuts. Put a segment's camera, action, light and text together under its timestamp. If the prompt splits camera, lighting and action into separate attribute blocks (WHO / WHERE / CAMERA / LIGHTING, each listing every shot), the model has to match list items up by position, and it pairs them wrong. If the user writes in that style, regroup it by time. There's a before/after in the patterns file.
2. **Budget the beats.** A 30 s take holds 8–12 beats, not 20. Segments shorter than about 2 s tend to get merged or dropped. Give the hero moment the longest window, and make the ranges run continuously from 0 to exactly the duration. An unscripted tail is where the model starts improvising. A 4 s clip reliably delivers one main action. In a Higgsfield test (September 2026), "pallets load, then the parked freighter starts to taxi" produced the loading and dropped the taxi. If the edit needs a particular action, make it the clip's first and only beat.
3. **Say what every reference governs.** Use `@Image 1`, `@Video 1`, `@Audio 1`, numbered separately per type in the order you attach them. Tie each one to the thing it controls: "the garment in @Image 2", "reference @Video 1's camera movement", "BGM references @Audio 1". A bare "reference @Video 1" is noise. Every callout must be attached, and every attachment should be called out.
4. **Let references carry the subject.** Don't re-describe what an attached image already shows, because the text competes with the picture and wins, wrongly. Give each referenced person or object one minimal anchor line: role, current state, the details this shot depends on, and which hand holds what. For example: "@Image 1: the red toolbox, carried in his left hand. 100% matches the reference." A project's character bible overrides the hands and props in this skill's examples. For products, add this line verbatim: `If this description and the reference image disagree about the product, THE REFERENCE IMAGE WINS.` A location reference supplies geography, not framing, so set the camera yourself.
5. **Say what's there, not what isn't.** A negative list summons what it names: "no denim" has produced denim. Turn every exclusion of an object into a positive statement, e.g. "no fictional aircraft markings" becomes "plain unmarked white aircraft livery". Short negations aimed at failure modes are fine if they sit right after the positive state they protect: "Faces stay in shadow; no flat front light." "Hard cuts only; no dissolves." "No subtitles, no music." Repeat that statement in each segment where the thing appears, and for every surface that could carry lettering: hull, tail, trailer, uniform. Keep real brand and model names out ("Boeing 777F", a shipping line): they pull in real liveries and logos and can trigger `ip_detected`. Describe the type instead ("a wide-body twin-engine freighter").
6. **Quote every word the video must show or say.** Put on-screen text and voiceover in quotation marks, word for word, or the model invents lettering. Text that must be exactly right (dates, prices, names, legal lines) is safer added in the edit, because a garbled "October 2" costs a whole re-roll. Keep voiceover to about 2–2.5 words per second of its window, leave the last second silent, and add: `The voiceover must finish before the video ends.`
7. **List sounds by event** when audio is on: "soft blink, magic sparkle, juice-fill gurgle, glass clink". Listed sounds land on their actions, and unlisted ones get invented or skipped. Beat-sync language does nothing with `--generate_audio false` and no audio reference.
8. **Pin the ending, and match it to the cut.** Endings drift the most, so restate the final state inside the last segment and give the landing its own beat, with no other camera business stacked into it.
   - If the scene ends on a hold (a logo card, a final product shot), close with "The take ends held on this frame." For an end plate behind a card, let any camera drift settle by about 3 s, then lock off. Describe the space for the type as a positive ("clear, evenly graded sky at frame left and top"). Give the card about 3 s on screen.
   - If the shot cuts out on movement (a match cut on motion, a tracking camera), don't say "held", because it can freeze the move. Describe the final composition with the motion still running: "ends with the trailer roof centred on the vertical axis, the camera still gliding forward at the truck's speed."
9. **Keep the clip self-contained.** The model only sees this generation. Lines like "transition to Scene 2", "match the next clip", "same as before", "as above" or "continues from" point at nothing, and scene numbers and script headers are just noise. Describe the actual final frame instead, since that's also what a later clip will chain from. The same goes for image prompts. Asset IDs (`OBJ01`), "same as the previous image", "reference sheet", "turnaround" and production notes in brackets can come out printed as captions or as multi-panel sheets.
10. **Give small things room.** A micro-action (a zipper lifted two teeth, a brim tugged down) needs its own timestamp. An asymmetric detail needs its side stated in frame terms: "crest on his right chest, frame left as he faces camera". Convert body sides with the Sides table in `references/shot-direction.md`. Walking toward frame right shows the right side, not the left. Anyone lying down needs the whole body anchored ("in frame from head to bare feet"). Keep one mover per beat and say what stays still.
11. **Write people in words.** Give age, hair, build, wardrobe and one distinguishing detail, and repeat the wardrobe line in each segment where the person appears. A text description holds one character for a full 30 s take. Character names are only labels to the model; the description carries the identity. When a start frame already shows the person, a short "keeps her charcoal jacket and tablet unchanged" anchor is enough. See *Faces*.
12. **Frame fine detail close.** Small lettering and logo textures won't read in a wide shot at any resolution. Move the camera closer for the beat where they have to read.
13. **Clean the text.** Prompts pasted from Docs or Notion carry non-breaking spaces and glued words ("afreight", "trucktravelling"). Normalize the spaces and fix the words. The preflight script's `--fix` flag handles the spaces.
14. **Lock the first frame and the blocking.** For any clip that will be trimmed, write "The first visible frame already contains [who] in position." Place people in measurable terms, e.g. "within 1 metre of the trailer, hand on the door", not "near the trailer". Give the body and the eyes separate directions: "back to camera, eyes on the gallery opposite".
15. **Direct the lens by what it shows.** Give a diagonal field of view, a camera distance and the visible result, not just millimetres. Higgsfield's guide reports Seedance follows these better. Rough equivalents: 24 mm ≈ 84°, 35 mm ≈ 63°, 50 mm ≈ 47°, 85 mm ≈ 29°, 135 mm ≈ 18°. Keep portrait, environment and macro in separate beats so the lens doesn't drift.
16. **Give the light a direction.** Name the source, where it comes from relative to the camera, and which side of the subject falls into shadow or rim. Treat it as a constraint that must hold, since flat front light is the default failure.
17. **Screens are plates for post.** Any screen that will carry UI stays "plain dark glass with a soft even glow" in both the keyframe and the prompt, and the model never draws the interface. Keep it trackable: frame over the shoulder opposite the gesturing hand, keep all four corners in frame, keep the camera locked or slow, and allow one gesture per clip. A drag plus a tap needs 6 s or two clips. Keep finger speed unhurried so it can be rotoscoped. Deliver a tap map with the prompts: each contact point in screen terms, its clip time, and the UI it drives. A static UI moment is cheaper as a still with a push in post.

End with a global style block stated once: grade, focus, motion blur, render quality. For example: `Top-tier cinematic color grading. Subject in razor-sharp focus, backgrounds with motion blur. Photorealistic materials, global illumination.` Keep the block to what's true of every shot. A global "practical light only" contradicts a sunrise segment, so per-shot light belongs in the segments.

### Faces

On the ByteDance API, Seedance 2.5 refuses most reference images that show a readable human face, AI-generated faces included, and it never accepts photos of real people. Treat that as true on Higgsfield until tested (see the last section). In practice:

- Describe people in text by default (rule 11). That's enough to hold a character within one generation.
- **Count a face as readable** when it's at least ~8% of the frame height and turned no more than ~45° from the camera. Before routing a film's face shots, test once on 2.5 with a profile frame, a three-quarter frame and a small figure seen from behind (about 10 credits each). The test table and routing rules are in `references/film-planning.md`.
- To keep the same character across separate generations, reuse the exact same description each time. Frame any chain frame so the face is small, turned away or covered, so the next clip rebuilds the face from text.
- If the user needs a specific real person (themselves, a presenter), use the approved identity routes in `higgsfield-generate`: Seedance 2.0 with an image the user has rights to, Soul ID, or Marketing Studio avatars. Don't disguise a face (overlays, filters, stylization tricks) to get it past the refusal. That dodges a deliberate safeguard and puts the account at risk.
- Seedance 2.0 caps at 15 s per clip. If speech has to run longer and is split across clips, each clip invents its own voice, and the join will be audible. Either keep the speech within one take, pass the same voice recording to every clip with `--audio-references`, or record the voiceover once and lay it in during the edit. Tell the user which one you chose.

## 5. Preflight

Save the prompt to a file and lint it against the settings you plan to use:

```bash
python3 <this-skill-dir>/scripts/preflight.py prompt.txt --mode omni_reference --duration 30 \
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
- **Framing claims:** `scripts/optics.py 70mm 120m` prints the frame width and height, to check phrases like "fills the middle third".
- **Films:** `scripts/assets.py` records approved asset picks and resolves IDs to exactly one file. `scripts/film_run_template.sh` is the run-script pattern for each act: numbered takes, dry run, approval gates and asset lookup through the manifest.
- **A whole film:** run `python3 <this-skill-dir>/scripts/shotlist_check.py shotlist.csv --film-seconds N --prompts <dirs> --keyframes <dirs>`. It checks that timings run continuously, durations and modes are legal for each model, IDs are unique, slice windows are noted, and every prompt and keyframe file exists. It also gives a first-pass credit estimate.

## 6. Price, confirm, generate

`generate cost` is free and validates the whole command on the server without submitting anything:

```bash
higgsfield generate cost seedance_2_5 --mode t2v --duration 30 --resolution 480p --aspect_ratio 16:9 < prompt.txt
```

Estimated rates (September 2026; `generate cost` is authoritative):

| Model | Estimate |
|---|---|
| Seedance 2.5 | 480p ≈ 2.5 credits/s, 720p ≈ 6.5, 1080p ≈ 9 (a 30 s take ≈ 75 / 195 / 270) |
| Seedance 2.0 | 720p ≈ 4.5 credits/s (check other resolutions with `cost`) |
| GPT Image 2 / Nano Banana 2 (`nano_banana_flash`) / Soul Location | ≈ 6.5 / 2 / 0.12 per image at default size |
| `bytedance_video_upscale` | a fraction of a credit per clip |

Generated audio and bitrate mode don't change the price. Extensions are billed on the new footage's duration, and edits appear to be billed on the source clip's length.

When several clips share a risk (a face in every start frame, an untested camera move), submit one first as a test, check it, then run the rest.

Before the first paid generation in a session, show the user the final prompt, the settings and the cost estimate, and wait for a go-ahead. Skip this only if they've told you to just run it. After that, iterate without asking again unless the cost jumps (a switch to 1080p or 30 s, say). Then submit:

```bash
higgsfield generate create seedance_2_5 \
  --mode omni_reference \
  --image-references ./product.png \
  --audio-references ./track.mp3 \
  --duration 30 --resolution 480p --aspect_ratio 9:16 \
  --wait --wait-timeout 30m < prompt.txt
```

- Pipe the prompt in from the file rather than using `--prompt "..."`, because prompts full of quoted voiceover lines break shell quoting.
- If you hand the user a script, make its paths relative to the script's own folder (`cd "$(dirname "$0")"`), not absolute paths from this session, so it still runs after files move.
- Media flags are repeatable, and their order sets the @ numbering.
- Add `--generate_audio false` only when the edit will supply all the sound.
- Use `--bitrate_mode high` by default. It's free, and finished footage almost always gets graded or upscaled.
- Long takes can outlast the default 10-minute wait, hence `--wait-timeout 30m`. If it still times out, the job keeps running, and `higgsfield generate wait <job_id>` picks it up again. For scale, a 4 s 480p clip took about 2.5 minutes, and three submitted in parallel finished together.
- On success, `--wait` prints only the result URL. Add `--json` to get the job object (`id`, `result_url`, and the params actually used), which you need to chain, extend or upscale by job ID.
- Output is 24 fps with an AAC audio track: 854×480 at 480p, 16:9.

## 7. Deliver, then offer the next move

Give the result URL and a one-line summary (mode, duration, resolution, credits). Don't paste raw JSON or IDs unless the user asks. Then offer whichever next moves fit:

- **Iterate on the prompt** at 480p, where it's cheap. Change one thing per round so you know what fixed it.
- **Keep this exact take at a higher resolution by upscaling it.** Higgsfield exposes no seed, so re-running the same prompt at 720p or 1080p gives a *different* take. A 480p draft tests the prompt, not the take. To upscale: `higgsfield generate create bytedance_video_upscale --video <job_id> --preset aigc --resolution 1080p --wait` (also `2k` or `4k`; estimates come to a fraction of a credit). Upscales from 720p look better than from 480p, so once the prompt is locked, render the final at 720p or 1080p and upscale from there if needed. For a whole film, where budget rules, the planned path is to keep the approved 480p takes and upscale them all. Test one upscale on an existing take first. Re-render at 720p only the hero UI plates, the end plate and shots held on screen for about 1.2 s or longer.
- **Extend, chain or edit.** See `references/edit-extend-chain.md`.
- **Download.** `curl -L -o out.mp4 "<result_url>"`. The URL is also available from `higgsfield generate get <job_id> --json` (`result_url`).

## Errors

| Symptom | Fix |
|---|---|
| `mode 't2v' does not accept reference media` | Switch to `omni_reference`. |
| `start_image and end_image are only allowed for mode 'omni_reference'` | Switch the mode. |
| `Unknown params: genre` / `multi_shots` / `multi_prompt` / `speedramp` / `reference_elements` | These are web-app fields, not CLI params. Drop them. Named @tags from the web app (reference elements) don't exist on the CLI; references are numbered `@Image N` by attachment order. Note that `speedramp` runs on `auto` for CLI jobs and can't be switched off. If the brief rules out speed ramps, write "real-time, constant speed" into the prompt and check the result. |
| `duration: Input should be ≥ 4` / `≤ 30` | Keep it between 4 and 30 s. For longer films, chain (see the chain reference). |
| Status `nsfw` / `ip_detected`, or a refusal on an input image | Change the input: a face in a reference, a real person, a trademark or a branded character are the usual causes. Resubmitting the same inputs won't help. |
| Status `failed` with no content reason | Retry once unchanged. If it fails again, simplify (fewer references, shorter duration) to find the cause. |
| `Session expired` / `Not authenticated` | Ask the user to run `higgsfield auth login`. |

## Unverified on Higgsfield: check before relying on it

These points come from other Seedance 2.5 platforms and haven't been confirmed on Higgsfield. When one matters for a job, test it once at 480p / 4 s (about 10 credits) and tell the user what you found:

- `@Image N` numbering follows the order of the `--image-references` flags. How start and end frames are numbered alongside image references is unknown. When you mix them, refer to the frames in words ("the start frame", "the end frame") and number only the references.
- Face-reference refusal rates on Higgsfield's Seedance 2.5.
- Whether refused or failed jobs refund their credits.
- For `video_extension`: whether the output contains the source plus the new footage or only the new part, and the longest source it accepts. The ByteDance API allows roughly 30 s of reference video per job, and the chain reference explains how to trim.
