---
name: studio
description: >-
  Make shots with Higgsfield Cinema Studio from the CLI: Cinema Studio 4.0 (Seedance 2.5's modes
  plus genre, era, tempo, camera body, lens, aperture, light and colour-palette controls), 3.5
  (named camera style, light scheme and colour grading, multi-shot), 3.0 (speed-ramp control, 4K,
  folders) and Cinema Studio Image 2.5 stills. Picks the engine, sets the look controls (harvesting
  4.0's control IDs from the user's own web-app jobs), writes and lints the prompt, prices it for
  free and generates after the user has seen the cost. Use whenever the user mentions Cinema Studio,
  its genres, eras, camera bodies, lenses, light presets or palettes, wants generations filed into a
  Cinema Studio folder, or needs real-time motion with no speed ramps. For plain Seedance 2.5 or 2.0
  clips use higgsfield-seedance:generate.
argument-hint: "[the shot, and the Cinema Studio look you want]"
compatibility: Requires the higgsfield CLI (logged in) and python3 for the linter and the ID catalog.
---

# Cinema Studio shots from Claude Code

This skill runs Higgsfield's Cinema Studio engines through the `higgsfield` CLI with the same discipline as the rest of the plugin: a directed, linted prompt, a free price check, and nothing paid without the user's go-ahead.

`${CLAUDE_PLUGIN_ROOT}` is the plugin's folder, two levels above this skill's folder. **Read `${CLAUDE_PLUGIN_ROOT}/references/cinema-studio.md` first.** It has the engines, prices, every control and its values, the defaults that bite, folder support, command examples and the list of first tests.

## 0. Bootstrap

- `higgsfield` must be on PATH. If not: `curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh`
- If `higgsfield account status` reports an expired session or no auth, ask the user to run `higgsfield auth login` and wait for them.

## 1. Pick the engine

| The shot needs | Engine |
|---|---|
| Cinema Studio looks (genre, era, tempo, camera body, lens, aperture, light, palette) with Seedance 2.5's modes: edit, extend, start/end frames, up to 30 s | Cinema Studio 4.0 (`cinematic_studio_video_4_0`), 3 credits/s at 480p |
| Named look presets with no ID lookup, or native multi-shot | Cinema Studio 3.5 (`cinematic_studio_video_3_5`), 3.5 credits/s at 480p |
| Real-time motion with no speed ramps, 4K, or filing into a folder | Cinema Studio 3.0 (`cinematic_studio_3_0`), 3.5 credits/s at 480p |
| A cinematic still or keyframe, optionally filed into a folder | Cinema Studio Image 2.5 (`cinematic_studio_2_5`), 2 credits |
| None of the above | `higgsfield-seedance:generate` with plain `seedance_2_5`, which costs the same as 4.0 and is the tested path |

Settle the rest of the brief (duration, aspect ratio, audio, references, final resolution) the way `higgsfield-seedance:generate` does in its §2 and §3, including one take versus one clip per shot. For a film, use the engine and look settings recorded in the bible.

## 2. Set the look controls

- **4.0:** controls are IDs. Look up each option the user wants in the local catalog:

  ```bash
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/studio_ids.py find genre Noir
  ```

  If it's missing, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/studio_ids.py harvest` (read-only, free). If it's still missing, tell the user: set that option once on any shot in the Cinema Studio web app and generate it, then harvest again. Meanwhile, leave that control on Auto and direct it in words.
- **3.5 and 3.0:** controls are names (tables in the reference). `generate cost` rejects invalid names for free.
- **Always**, on 3.5 and 3.0: `--prompt_language en`, an explicit `--generate_audio true|false`, and `enhance_prompt` left off. On 4.0: `--bitrate_mode high` and an explicit `--generate_audio`.
- **Record the choices.** For a film, write the engine and every control into the bible, so each shot of a sequence gets the same look.

## 3. Write and lint the prompt

Write it with `higgsfield-seedance:prompt` (load it with the Skill tool, or read `${CLAUDE_PLUGIN_ROOT}/skills/prompt/SKILL.md`), and tell it the engine and the controls you set.
- **Controls carry the look.** Keep the prompt on blocking, timing, field of view and distance, light direction and performance, and make sure nothing in the text contradicts a control (see *Controls and the prompt* in the reference).
- **Camera moves in words** until the 4.0 tag syntax has been tested.
- **Stills:** write them with `higgsfield-seedance:image`.

Lint with the engine as the model:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py prompt.txt --model cinematic_studio_video_4_0 --mode omni_reference --duration 4 --start-image
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py prompt.txt --model cinematic_studio_3_0 --duration 6 --start-image
```

## 4. Price, confirm, run

- **Price for free:** `higgsfield generate cost <job_type> <same flags> --prompt "$(cat prompt.txt)"`. It checks names on 3.5 and 3.0 but not 4.0's IDs, so the first clip with a newly harvested ID should be a 4 s, 480p test.
- **Confirm:** before the first paid job in a session, show the prompt, the engine, every control (by name, with its ID), the settings and the cost, and wait for a go-ahead. For a batch, show the count and total and run one clip alone first.
- **First tests:** anything the reference lists under *Unverified* that this shot depends on (tag syntax, folder filing, faces, how 4.0 compares with plain Seedance 2.5) gets its own small test first, with its cost stated.
- **Run:** `higgsfield generate create <job_type> ... --prompt "$(cat prompt.txt)" --wait --wait-timeout 30m --json`. Full examples are in the reference.
- **Folders:** only Cinema Studio 3.0 and Image 2.5 take `--folder_id`. Ask the user for the folder or project link, and treat filing as unverified until the folder test has passed.

## 5. Deliver

- **Result:** give the URL and a one-line summary (engine, controls, duration, resolution, credits), then offer the next move.
- **Iterate:** at 480p, changing one control or one prompt element per round.
- **Keep the take at a higher resolution:** upscale with `higgsfield-seedance:edit`; re-rendering gives a different take.
- **Edits and extensions** (4.0 only): same flow as `higgsfield-seedance:edit`, with `cinematic_studio_video_4_0` as the job type.
- **Harvest after web work:** when the user has been working in the web app, harvest again so new control IDs land in the catalog.
