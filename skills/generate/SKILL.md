---
name: generate
description: >-
  Make a video with ByteDance Seedance 2.5 (or 2.0) on Higgsfield: route the shot to the right
  model, pin the brief, pick the mode, write and lint the prompt, price it for free, then run it
  through the higgsfield CLI once the user has seen the cost. Covers one-go clips up to 30 s with
  cuts, beat-synced edits, voiceover and on-screen text; @Image/@Video/@Audio reference-driven
  video; start/end-frame transformations. Use whenever the user wants to generate, render or run a
  Seedance or Higgsfield video, a single Higgsfield video longer than 15 seconds, a match-cut brand
  film, timestamped tutorial or continuous-shot chapter film, even without naming the model. For a
  prompt only (no credits) use higgsfield-seedance:prompt; for keyframes and reference stills,
  higgsfield-seedance:image; for a multi-scene film,
  higgsfield-seedance:plan; to change, extend, chain or upscale an existing clip,
  higgsfield-seedance:edit. Not for talking-head videos driven by a person's photo (Seedance 2.0 or
  Marketing Studio via higgsfield-generate), native 4K, or multi-block narrated explainers
  (higgsfield-video-explainer).
argument-hint: "[what the video should show]"
compatibility: Requires the higgsfield CLI (logged in) and python3 for the preflight linter.
---

# Generate a Seedance video on Higgsfield

This skill takes a brief to a finished clip: it picks the model and mode, gets the prompt written and linted, prices it, and runs it through the `higgsfield` CLI. The writing matters more than the command. A 30-second take holds 8–12 beats, and most bad results come from prompt structure rather than settings: beats that merge or vanish, invented lettering, endings that drift.

Model facts here were checked against the live schemas (`higgsfield model get seedance_2_5` and `seedance_2_0`) in September 2026. If the CLI disagrees with this file, trust the CLI and re-run `model get`.

`${CLAUDE_PLUGIN_ROOT}` is the plugin's folder, two levels above this skill's folder. Shared references live in `${CLAUDE_PLUGIN_ROOT}/references/` and scripts in `${CLAUDE_PLUGIN_ROOT}/scripts/`.

The other actions in this plugin:
- `higgsfield-seedance:prompt` writes, fixes and lints prompts without spending credits. Step 4 below uses it.
- `higgsfield-seedance:image` makes the stills: keyframes, character and location references, props, and image edits.
- `higgsfield-seedance:plan` plans a multi-scene film, or anything with recurring characters or objects. Switch to it before generating clip by clip.
- `higgsfield-seedance:edit` edits, extends, chains or upscales a clip that already exists.

## 0. Bootstrap

- `higgsfield` must be on PATH. If not: `curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh`
- If `higgsfield account status` reports an expired session or no auth, ask the user to run `higgsfield auth login` and wait for them.

## 1. Is Seedance 2.5 the right model?

Seedance 2.5 earns its place for: one-go films longer than 15 s (Seedance 2.0 stops at 15 s), heavy multi-reference work (up to 30 images plus videos and audio), editing an existing clip, and extending a clip forward or backward. Route elsewhere when:

- **Someone talks to camera and the face comes from a photo.** Face references are unreliable on 2.5 (see *Faces* in the prompt skill). Use Seedance 2.0 or Marketing Studio avatars via `higgsfield-generate`.
- **The user needs native 4K.** Seedance 2.0. (2.5 renders up to 1080p and can be upscaled, see §6.)
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

The prompt skill's rules apply unchanged; Higgsfield wrote its CINEDANCE guide for this model. Lint 2.0 prompts with `preflight.py --model seedance_2_0`.

For face shots on 2.0:
- **Anchor line:** attach the master portrait of every readable face in frame as `--image-references`, each with an anchor line built from the bible: "@Image 1: <bible line>. 100% matches the reference for face, hair and build." Never write "matching @Image 1" inside @Image 1's own line; that's circular.
- **Route by the keyframe,** not by the storyboard's label. A "face" shot whose blocking turns the face away belongs on 2.5.
- **Test numbering:** `@Image` numbering beside a start frame is unverified on 2.0 too, so let the first 2.0 clip double as that test.
- **Acting:** a readable face can carry face and eye acting, so these are the shots where the performance rules matter most (prompt rule 18 and `${CLAUDE_PLUGIN_ROOT}/references/acting.md`).

## 2. Pin the brief

Before writing, know: purpose and format, duration (4–30 s, integer), aspect ratio (`16:9`, `9:16`, `1:1`, `4:3`, `3:4`, `21:9`, `auto`), audio (generated or not, plus any music reference), assets (paths or Higgsfield IDs, and what each is for), exact on-screen text, exact voiceover lines, and final resolution.

Default what you can (16:9, generated audio on, 480p draft) and ask only for what you can't sensibly default, one question at a time. Voiceover and on-screen text are the user's words. If they didn't supply them, draft them and show them before spending credits.

**Keyframes first, when composition matters.** If the brief includes static keyframe prompts, or depends on exact compositions (match-cut geometry, space reserved for titles), ask whether keyframe images exist. If they don't, suggest making them first with `higgsfield-seedance:image`. Get the stills approved, then animate each one with `--start-image`. A still locks composition far more reliably than text, and it's the cheapest place to iterate.
- **Which image model** (details and routing in `${CLAUDE_PLUGIN_ROOT}/references/image-prompts.md`):
  - Nano Banana Pro (`nano_banana_pro`, about 2 credits at 2k) for keyframes and views built from references.
  - GPT Image 2 (about 6.5 at high quality) for exact objects, structure and lettering.
  - Soul 2.0 or Soul Cinematic (about 0.12) for character portraits and cinematic frames.
  - Soul Location (about 0.12) for people-free places; it takes a prompt only.
- **Recurring characters:** approve a master portrait first, then build every other view and every keyframe with that portrait attached as `--image-references`. A text description holds wardrobe, but not a face.

## 3. Pick the mode

The mode decides which inputs are legal and what the prompt has to do.

| Situation | `--mode` | Media flags | The prompt describes |
|---|---|---|---|
| Text only | `t2v` (default) | none (the API rejects any media) | everything |
| Any reference image/video/audio, and/or a start or end frame | `omni_reference` | `--image-references`, `--video-references`, `--audio-references` (all repeatable), `--start-image`, `--end-image` | staging and motion; the references carry the subject |
| Change something inside an existing clip | `video_edit` | exactly one `--video`, plus optional `--image-references` for a replacement | the change, and what stays untouched |
| Add footage after the last frame or before the first | `video_extension` plus `--extension_mode forward` or `backward` | at least one `--video` | only the new footage |

Hard limits: `--start-image` and `--end-image` only work in `omni_reference`. At most 30 images (start and end frames count) and 50 media items in total. Every media flag takes a local path (uploaded automatically) or a Higgsfield upload ID or job ID. That means a previous generation's job ID can go straight into `--video` for an edit or extension, with no download needed.

For `video_edit` and `video_extension`, switch to `higgsfield-seedance:edit`. First/last-frame clips have their own prompt logic in `${CLAUDE_PLUGIN_ROOT}/references/first-last-frame.md`.

### One take, or one clip per shot?

Seedance 2.5 can cut between shots inside one generation, but that doesn't always make it the right plan.

- **Generate one clip per shot** (4 s minimum each) when the shots are separate places or times joined by hard cuts, when the edit will trim each shot to 2–3 s or less, when each shot has its own keyframe, or when you'll want to re-roll one shot without the others. A failed shot then costs one re-roll, not the whole scene, and the editor gets spare footage around every cut point. Example: three 1.3 s shots in a 4 s scene become three 4 s clips, 30 credits at 480p.
- **Generate one multi-shot take** when continuity across the cuts is the point (the same subject, grade or motion carrying through), when the model's own cutting rhythm is wanted (beat-synced montages), or when the scene runs 15–30 s with segments of 2 s or more.
- **Either way, write for the edit.** Start the action on the first frame and keep it going through the last, so the editor can choose the cut points. When clips will be trimmed, give the user a cut map: which window of each clip goes into the scene, and which match cut it serves. For example, the centred truck roof exists only in the last second of its clip. When the edit keeps under about 1.5 s of a clip, time any single event inside that window ("the tab snaps flat at about 1 s"). Otherwise a drop, hand-off or snap can land at 3.5 s, outside the slice.
- **Camera moves shrink with the trim.** A 30° orbit across a 4 s clip shows about 6° in a 0.8 s cut. If a move has to read on screen, make it faster or the shot longer, and tell the user.
- **Plan wipes where they can happen.** An in-camera wipe needs a body passing between the lens and the subject, which a high or overhead camera rarely gets. Instead, stage crossings along the edge of frame for the editor to cut on, or treat the wipe as an edit effect.
- **Keep screen direction consistent** across shots that cut together (vehicles, pans and props all flowing toward frame right, say), unless the brief wants a reversal.

## 4. Write and lint the prompt

Load `higgsfield-seedance:prompt` with the Skill tool and follow it. If the Skill tool isn't available, read `${CLAUDE_PLUGIN_ROOT}/skills/prompt/SKILL.md`. Give it the brief and the settings decided above: model, mode, duration, the attachments in flag order, audio on or off, and how the clip will be used (trimmed, chained, held on a card).

Save the prompt to a file. Don't price or run anything until it lints with no ERROR:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py prompt.txt --mode omni_reference --duration 30 \
  --images 2 --videos 1 --audios 1 [--start-image] [--end-image] [--no-audio] [--model seedance_2_0]
```

## 5. Price, confirm, generate

`generate cost` is free and validates the whole command on the server without submitting anything:

```bash
higgsfield generate cost seedance_2_5 --mode t2v --duration 30 --resolution 480p --aspect_ratio 16:9 < prompt.txt
```

Estimated rates (September 2026; `generate cost` is authoritative):

| Model | Estimate |
|---|---|
| Seedance 2.5 | 480p ≈ 2.5 credits/s, 720p ≈ 6.5, 1080p ≈ 9 (a 30 s take ≈ 75 / 195 / 270) |
| Seedance 2.0 | 720p ≈ 4.5 credits/s (check other resolutions with `cost`) |
| Stills (full table in `references/image-prompts.md`) | Nano Banana Pro ≈ 2 (4 at 4k); Nano Banana 2 ≈ 1.5 (2 at 2k); GPT Image 2 ≈ 6.5 high / 2 medium; Seedream 4.5 ≈ 1; Soul 2.0, Soul Cinematic, Soul Location ≈ 0.12 per image |
| `bytedance_video_upscale` | a fraction of a credit per clip |

Generated audio and bitrate mode don't change the price. Extensions are billed on the new footage's duration, and edits appear to be billed on the source clip's length.

When several clips share a risk (a face in every start frame, an untested camera move), submit one first as a test, check it, then run the rest.

Before the first paid generation in a session, show the user the final prompt, the settings and the cost estimate, and wait for a go-ahead. Skip this only if they've told you to just run it. After that, iterate without asking again unless the cost jumps (a switch to 1080p or 30 s, say). Then submit:

```bash
higgsfield generate create seedance_2_5 \
  --mode omni_reference \
  --image-references ./product.png \
  --audio-references ./track.mp3 \
  --duration 30 --resolution 480p --aspect_ratio 9:16 --bitrate_mode high \
  --wait --wait-timeout 30m --json < prompt.txt
```

- Pipe the prompt in from the file rather than using `--prompt "..."`, because prompts full of quoted voiceover lines break shell quoting.
- If you hand the user a script, make its paths relative to the script's own folder (`cd "$(dirname "$0")"`), not absolute paths from this session, so it still runs after files move.
- Media flags are repeatable, and their order sets the @ numbering.
- Add `--generate_audio false` only when the edit will supply all the sound.
- Use `--bitrate_mode high` by default. It's free, and finished footage almost always gets graded or upscaled.
- Long takes can outlast the default 10-minute wait, hence `--wait-timeout 30m`. If it still times out, the job keeps running, and `higgsfield generate wait <job_id>` picks it up again. For scale, a 4 s 480p clip took about 2.5 minutes, and three submitted in parallel finished together.
- On success, `--wait` alone prints only the result URL. `--json` returns the job object (`id`, `result_url`, and the params actually used), which you need to chain, extend or upscale by job ID.
- Output is 24 fps with an AAC audio track: 854×480 at 480p, 16:9.

## 6. Deliver, then offer the next move

Give the result URL and a one-line summary (mode, duration, resolution, credits). Don't paste raw JSON or IDs unless the user asks. Then offer whichever next moves fit:

- **Iterate on the prompt** at 480p, where it's cheap. Change one thing per round so you know what fixed it.
- **Keep this exact take at a higher resolution by upscaling it** (`higgsfield-seedance:edit`). Higgsfield exposes no seed, so re-running the same prompt at 720p or 1080p gives a *different* take. A 480p draft tests the prompt, not the take. Upscales from 720p look better than from 480p, so once the prompt is locked, render the final at 720p or 1080p and upscale from there if needed.
- **Extend, chain or edit** with `higgsfield-seedance:edit`.
- **Download.** `curl -L -o out.mp4 "<result_url>"`. The URL is also available from `higgsfield generate get <job_id> --json` (`result_url`).

## Errors

| Symptom | Fix |
|---|---|
| `mode 't2v' does not accept reference media` | Switch to `omni_reference`. |
| `start_image and end_image are only allowed for mode 'omni_reference'` | Switch the mode. |
| `Unknown params: genre` / `multi_shots` / `multi_prompt` / `speedramp` / `reference_elements` | These are web-app fields, not CLI params. Drop them. Named @tags from the web app (reference elements) don't exist on the CLI; references are numbered `@Image N` by attachment order. Note that `speedramp` runs on `auto` for CLI jobs and can't be switched off. If the brief rules out speed ramps, write "real-time, constant speed" into the prompt and check the result. |
| `duration: Input should be ≥ 4` / `≤ 30` | Keep it between 4 and 30 s. For longer films, chain (`higgsfield-seedance:edit`). |
| Status `nsfw` / `ip_detected`, or a refusal on an input image | Change the input: a face in a reference, a real person, a trademark or a branded character are the usual causes. Resubmitting the same inputs won't help. |
| Status `failed` with no content reason | Retry once unchanged. If it fails again, simplify (fewer references, shorter duration) to find the cause. |
| `Session expired` / `Not authenticated` | Ask the user to run `higgsfield auth login`. |

## Unverified on Higgsfield: check before relying on it

These points come from other Seedance 2.5 platforms and haven't been confirmed on Higgsfield. When one matters for a job, test it once at 480p / 4 s (about 10 credits) and tell the user what you found:

- `@Image N` numbering follows the order of the `--image-references` flags. How start and end frames are numbered alongside image references is unknown. When you mix them, refer to the frames in words ("the start frame", "the end frame") and number only the references.
- Face-reference refusal rates on Higgsfield's Seedance 2.5.
- Whether refused or failed jobs refund their credits.
