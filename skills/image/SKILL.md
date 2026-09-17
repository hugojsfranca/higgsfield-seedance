---
name: image
description: >-
  Write, fix and run image prompts on Higgsfield, above all the stills a Seedance video is built
  from: keyframes (start and end frames), character master portraits and extra views, Soul ID
  characters, location plates, prop shots, approval sheets, and edits of a finished still. Routes
  each job to the right CLI model (Soul 2.0, Soul Cinematic, Soul Location, Soul Cast, Nano Banana
  Pro or 2, Seedream 4.5, GPT Image 2), writes positive photoreal prompts, lints them, prices them
  for free and generates after showing the cost. Use when the user wants a keyframe, reference
  image, character, location, prop or product still, a reverse angle of a location, or an edit or
  texture fix of an image, or asks to write or repair an image prompt, even without naming a
  model. For video, use higgsfield-seedance:generate.
argument-hint: "[what the image should show, or the image to edit and the change]"
compatibility: Requires the higgsfield CLI (logged in) and python3 for the preflight linter.
---

# Image prompts and stills on Higgsfield

This skill makes the stills a Seedance clip starts from, and any other image the user needs on Higgsfield. It's adapted from Higgsfield's LIRA image-prompt guide, with the models and prices checked against the CLI in September 2026.

`${CLAUDE_PLUGIN_ROOT}` is the plugin's folder, two levels above this skill's folder. **Read `${CLAUDE_PLUGIN_ROOT}/references/image-prompts.md` before writing anything but the simplest still.** It has the model table, routing, rules, building blocks, lint-clean templates and the edit method.

## 0. Bootstrap

- `higgsfield` must be on PATH. If not: `curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh`
- If `higgsfield account status` reports an expired session or no auth, ask the user to run `higgsfield auth login` and wait for them.

## 1. What is the still for?

The job decides the rules:

| Job | What changes |
|---|---|
| **Start or end frame for a Seedance 2.5 clip** | Readable faces small, lowered or turned; people already mid-action; the clip's field of view, distance and height written in; one single photograph |
| **Start frame for a Seedance 2.0 face shot** | The face can be readable; pair it with the master portrait as a reference on the clip |
| **Character reference** (master portrait, views, hands) | One view per image, recorded in the asset manifest; the master portrait is approved before any other view |
| **Location plate** | People-free unless the shot needs them; emptiness stated positively; deep focus |
| **Approval sheet** | Multi-panel is fine, but it's for human approval only and never attached to a clip |
| **Standalone image** | The general rules only |

If it's part of a film, check the bible for the character's wardrobe line, the location map and the shared framing spec, and copy them word for word.

## 2. Pick the model

Use the routing table in `image-prompts.md`. The defaults:
- **Invented character portrait:** Soul 2.0 (`text2image_soul_v2`), or Soul Cinematic (`soul_cinematic`) for a film look. For a real person the user has rights to, use a Soul ID.
- **Extra views and keyframes from references:** Nano Banana Pro (`nano_banana_pro`) at 2k. When the film is made in Cinema Studio, or the still should be filed into one of its folders, use Cinema Studio Image 2.5 (`cinematic_studio_2_5`, same price, `--folder_id`). See `${CLAUDE_PLUGIN_ROOT}/references/cinema-studio.md`.
- **People-free locations:** Soul Location (`soul_location`).
- **Props with exact geometry or lettering:** GPT Image 2 (`gpt_image_2`).
- **Edits:** Nano Banana Pro first; Seedream 4.5 (`seedream_v4_5`) only for textures; GPT Image 2 last.

Soul models take one reference image and no 21:9 on Soul 2.0. Nano Banana Pro takes up to 14. Check `higgsfield model get <job_type>` when a flag is in doubt.

**Faces and identity.** A real person's face goes only through routes built for it: a Soul ID trained on photos the user has rights to (`higgsfield soul-id create --name <name> --soul-2 --image ...`, 5–20 images, with the person's consent), then `--soul-id <id>`. Never name a real person in a prompt, and don't disguise a face to get a still past a refusal.

## 3. Write the prompt

Follow the 14 rules in `image-prompts.md`. The ones that matter most:
- **Prose, and short.** 80–150 words for a simple still, and at most ~330 with bible and spec lines. Use one register line, not a paragraph of quality boilerplate.
- **Positive phrasing.** No "no X" lists in generation prompts.
- **Settings as flags.** Aspect ratio and size never go in the text.
- **Light and materials.** Light with a source, direction and falloff; materials with a finish; a 60/30/10 palette taken from the brief or references.
- **Composition and camera.** Rule of thirds unless the composition is specified. Give the camera in plain words, plus the clip's field of view for keyframes.
- **Photo anchors, not illustration triggers.** Exact text in quotes with font and colour, or added in post.
- **Keyframes stand alone.** Write each one as the only prompt: no asset IDs, no "same as", and the shared spec copied word for word.
- **People in keyframes** are mid-action: states, not transitions. Their posture, tempo and business follow their acting profile (`${CLAUDE_PLUGIN_ROOT}/references/acting.md`) when the bible has one.

**Fixing a user's prompt:** lint it as it stands, name the rule behind each change, keep their subject and exact text, and show a short before/after when they ask for a comparison.

## 4. Edits

Use the CHANGE / PRESERVE EXACTLY template in `image-prompts.md`, with one change per pass. Pass the original as `--image-references`.
- **Nano Banana Pro** for every edit first.
- **Seedream 4.5** only to revive tired textures (skin, fabric, surfaces).
- **GPT Image 2** for a tiny local fix Nano Banana Pro couldn't make, with the narrowest CHANGE and the fullest PRESERVE list.
- **Reverse angles:** GPT Image 2, or Nano Banana Pro with every object's new side written out.
- **Needs rebuilding:** regenerate it.

## 5. Lint, price, run

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py still.txt --image          # generation prompt
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py sheet.txt --image --sheet  # intentional multi-panel sheet
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py edit.txt --image --edit    # CHANGE / PRESERVE EXACTLY edit
```

It flags asset IDs and cross-references, production notes, "no X" lists, gaze-at-camera wording, brands, settings written into the prose, keyword stacking, illustration triggers, overlong prompts, and edits that lack a CHANGE and PRESERVE EXACTLY block or leave a removal unfilled.

Price for free, then run once the user has seen the cost:

```bash
higgsfield generate cost nano_banana_pro --resolution 2k --aspect_ratio 16:9 --image-references ./portrait.png --prompt "$(cat still.txt)"
higgsfield generate create nano_banana_pro --resolution 2k --aspect_ratio 16:9 --image-references ./portrait.png \
  --prompt "$(cat still.txt)" --wait --json
```

- **Confirm before spending.** Before the first paid image in a session, show the prompt, model, settings and cost, and wait for a go-ahead. For a batch (a reference library, a set of keyframes), show the count and total first, and run one image alone before the rest.
- **Prompt text:** image models take the prompt as `--prompt`. Build it from the file as above so the linted text is what gets sent.
- **Soul models:** `--quality 2k`, plus `--soul-id <id>` (the schema's `custom_reference_id`) for a trained character.
- **Local files** upload automatically. `--json` returns the job ID and result URL.

## 6. Deliver

- **Result:** give the URL and a one-line summary (model, size, credits). For a set, give a contact sheet or a list the user can approve.
- **Film work:** after approval, record each pick in the manifest (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/assets.py record ID view file`), so run scripts resolve exactly one file.
- **Next step:** animate an approved keyframe with `higgsfield-seedance:generate`, or plan the rest of the library with `higgsfield-seedance:plan`.
