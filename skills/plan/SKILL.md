---
name: plan
description: >-
  Plan a multi-scene film or a series of Seedance clips on Higgsfield before spending credits:
  shot list with film timings and cut windows, asset bible and reference library for recurring
  characters, objects and places, character acting profiles and voice lines, keyframes-first
  workflow, face tests and Seedance 2.5 / 2.0
  routing, budget scenarios against the credit balance, approval gates, staged run scripts and a
  review pass. Use when a brief has several scenes, a storyboard or script, recurring characters
  or props, a runtime longer than one clip, or a budget that could run out, or when the user wants
  a dry run of a whole video before generating anything.
argument-hint: "[brief, storyboard or script]"
compatibility: Requires python3 for the checkers; the higgsfield CLI (logged in) for free price checks and later runs.
---

# Plan a multi-scene Seedance film

A film is dozens of generations that have to stay consistent, affordable and in order. This skill turns a brief or storyboard into a plan that can be run stage by stage. Planning spends nothing: every paid step waits behind a gate the user approves.

`${CLAUDE_PLUGIN_ROOT}` is the plugin's folder, two levels above this skill's folder. **Read `${CLAUDE_PLUGIN_ROOT}/references/film-planning.md` in full before starting.** This file is the workflow; that one has the tables, formats and numbers from a full 22-scene dry run.

## 1. Read the brief and flag problems

- **List every scene** with its intended duration, and check the durations add up to the runtime.
- **Voiceover:** keep it to about 2–2.5 words per second of each window, and flag lines that can't fit. In a film, the voiceover and music belong to the edit, not to the clips: generate location sound only unless a clip truly needs its own.
- **Camera conflicts:** details the stated camera can't see. Flag each one and say which reading protects the edit.
- **Brands and real interfaces:** real product names, logos and UIs stay out of prompts. Screens become plates for compositing.
- **Story payoffs:** note any beat whose removal would break a later payoff.
- **Who speaks on camera:** separate on-camera dialogue (lip-sync, a readable face, usually Seedance 2.0) from narration laid in during the edit. Flag scenes that ask for several beats of acting in a clip too short to hold them (`${CLAUDE_PLUGIN_ROOT}/references/acting.md`, *How much acting a clip holds*).
- **Brief-change log:** every beat you drop, merge or change goes into one list the user sees.

Collect open questions into the plan rather than asking them one at a time, and default what you sensibly can.

## 2. Route every shot

- **One take or one clip per shot:** follow *One take, or one clip per shot?* in `${CLAUDE_PLUGIN_ROOT}/skills/generate/SKILL.md`. Films trimmed to short windows are usually one 4 s clip per shot.
- **Faces:** a face is readable at ~8% of frame height or more, turned no more than ~45°. Plan the face tests from `film-planning.md`, then route readable faces to Seedance 2.0 (4–15 s, start frame plus master portrait) and small or turned figures to Seedance 2.5. Shots that depend on face or eye acting, or on lip-synced dialogue, need a readable face, so they follow the same route. Everything else acts with the body.
- **Reuse:** mark reprised slices and still-plus-push moments as `post` rows. Reuse is the biggest single saving.
- **Mixing models is normal:** grade-match in post and keep wardrobe lines and light direction identical.

## 3. Build the shot list

One CSV row per generated clip, in the column format in `film-planning.md`. Every row gets a cut window, one primary action, asset IDs rather than paths, the carried state and any shared match spec. Validate it:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/shotlist_check.py shotlist.csv --film-seconds N [--prompts <dirs>] [--keyframes <dirs>]
```

It checks that timings run continuously, durations and modes are legal for each model, IDs are unique, slice windows are noted and every prompt and keyframe file exists, and it gives a first-pass credit estimate.

## 4. Asset bible and reference library

- **IDs:** `CH01…` for characters, `OBJ01…` for objects and `ENV01…` for places, each with one exact prompt line used word for word everywhere.
- **Location maps, dominant hands, wardrobe lines and look-alike props** as described in `film-planning.md`.
- **Acting profile and voice line** for every character who acts or speaks: about 80–130 words of observable behaviour (tics with triggers, a mask and its crack, a named gait), plus one locked voice sentence. Format and example in `${CLAUDE_PLUGIN_ROOT}/references/acting.md`. Keep each character's objective per scene in the scene notes, not in prompts.
- **Stills:** make and run them with `higgsfield-seedance:image`, which routes each asset:
  - master portraits → Soul 2.0 or Soul Cinematic (about 0.12 credits), or a Soul ID for a real person with consent;
  - extra views and keyframes → Nano Banana Pro (about 2 at 2k);
  - people-free places → Soul Location (about 0.12);
  - exact objects → GPT Image 2 (about 6.5 at high quality).

  Keep each type prefix to one short register line.
- **Order:** approve each master portrait first, then build every other view and every keyframe with it attached as `--image-references`.
- **Manifest:** record each approved pick and resolve files only through it, so candidates never get picked up by mistake:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assets.py record CH01 portrait assets/CH01_portrait.png
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assets.py resolve CH01:portrait
```

## 5. Write the keyframes and prompts

- One keyframe still per clip, and one video prompt per clip, each in its own file (`keyframes/<id>.txt`, `prompts/<clip_id>.txt`).
- Write video prompts with `higgsfield-seedance:prompt` (load it with the Skill tool, or read `${CLAUDE_PLUGIN_ROOT}/skills/prompt/SKILL.md`). Its rule 18 rewrites each character's acting profile into the clip. Write keyframe prompts with `higgsfield-seedance:image`. Lint video prompts with the clip's real settings and stills with `--image`.
- Keep shared framing specs for match cuts in one `shared_specs.md` and copy them word for word.
- Screens are "plain dark glass with a soft even glow", with a tap map for each gesture.
- Stamp the prompt set with the rules version from the prompt skill.
- For a large film, split the writing by act, write one file per step (long single responses hit output limits), and keep one shared plan every writer reads first.

## 6. Budget

- Price every stage from the dated rate tables in `film-planning.md` (video) and `image-prompts.md` (stills), with the re-roll allowances.
- Read the balance with `higgsfield account status`, and confirm rates with `higgsfield generate cost` for each model and setting. Both are free.
- Give at least two scenarios against the balance (for example "all 2.5 at 480p plus upscale" and "hybrid, faces on 2.0"), recommend one, and split it into per-act envelopes.
- Hold back a credit floor until picture lock. If spend passes the plan by about 15% before lock, stop and re-plan with the user.

## 7. Gates and run scripts

- **Stages:** free prep → canaries → reference library → keyframes → drafts → picture lock → finals → post, each ending at a gate the user approves (table in `film-planning.md`).
- **Run scripts:** start each act's script from `${CLAUDE_PLUGIN_ROOT}/scripts/film_run_template.sh`. Copy it next to the act's `prompts/` and `keyframes/`, fill in its clip table, and set `SKILL_DIR` to the plugin folder (or a pinned copy of it). It lints, prices, runs a canary alone, then batches, with numbered takes, `DRY=1`, y/N confirmations and gate markers.
- **Resolution:** draft at 480p, keep the approved take and upscale it. Re-render natively at 720p only for hero UI plates, the end plate and shots held on screen for about 1.2 s or longer. Always `--bitrate_mode high`.
- **Paid runs** follow the confirmation rules in `higgsfield-seedance:generate`: show the prompt, settings and cost first.

## 8. Review before spending

Once everything is written, do one review pass across the whole film: continuity, left/right sides, routing, optics size claims (`scripts/optics.py`), asset lookups, run scripts and budget. Fix what it finds, re-run the checkers, and log the fixes.

## 9. Deliver the plan

Hand the user a folder they can run from:
- `plan.md` with routing, the asset bible, the brief-change log, budget scenarios, the run order and open questions;
- `shotlist.csv` passing `shotlist_check.py`;
- `assets/` with the reference prompts;
- one folder per act with `prompts/`, `keyframes/`, notes and its run script;
- the review and fix log.

End with the decisions the user must make before any credits are spent, and the cost of the first gated stage.
