# Cinema Studio on the CLI

Higgsfield's Cinema Studio engines, run from the `higgsfield` CLI: what each one takes, what it costs, how to set its look controls, and what's still unverified. Schemas and prices were checked with `higgsfield model get` / `workflow get` and `higgsfield generate cost` on 17 September 2026. Option names come from Higgsfield's Cinema Studio 4.0 pages. If the CLI disagrees, trust the CLI.

## Contents

- [Engines](#engines)
- [Which engine](#which-engine)
- [Defaults that bite](#defaults-that-bite)
- [Cinema Studio 4.0 controls](#cinema-studio-40-controls)
- [Cinema Studio 3.5 controls](#cinema-studio-35-controls)
- [Cinema Studio 3.0 controls](#cinema-studio-30-controls)
- [Stills](#stills)
- [Controls and the prompt](#controls-and-the-prompt)
- [Folders and projects](#folders-and-projects)
- [Commands](#commands)
- [Unverified: first tests](#unverified-first-tests)

## Engines

All of them run with `higgsfield generate create <job_type>` and price with `higgsfield generate cost <job_type>`. Credits are per second of video, or per image.

| Engine (`job_type`) | Modes | Length | Resolution | Credits | Look controls | Folder |
|---|---|---|---|---|---|---|
| Cinema Studio 4.0 (`cinematic_studio_video_4_0`) | `t2v`, `omni_reference`, `video_edit`, `video_extension` (as Seedance 2.5) | 4–30 s | 480p, 720p, 1080p | 3 / 6.5 / 9 per s | genre, era, tempo, camera body, lens, aperture, light, palette (IDs) | no |
| Cinema Studio 3.5 (`cinematic_studio_video_3_5`) | none; references and start/end frames directly | 4–30 s | 480p, 720p, 1080p | 3.5 / 5 / 10 per s | genre, camera style, light scheme, colour grading (names), or a style prompt | no |
| Cinema Studio 3.0 (`cinematic_studio_3_0`) | none | 4–30 s | 480p, 720p, 1080p, 4K | 3.5 / 5 / 10 / 24 per s | genre and speed ramp (names), preset ID | yes |
| Cinema Studio Image 2.5 (`cinematic_studio_2_5`) | image | — | 1k, 2k, 4k | 2 (4 at 4k) per image | `mode` (default `auto`), up to 14 references | yes |
| Cinematic Studio Image (`cinematic_studio_image`) | image | — | 1k, 2k, 4k | 2 per image | camera body, lens and focal length (IDs, required), aperture | no |
| Soul Cinema Studio (`soul_cinema_studio`) | image | — | 1.5k, 2k | 0.12 | `style_id`, Soul ID (`custom_reference_id`) | no |
| Cinematic Studio Soul Location / Soul Cast | image | — | — | 0.12 | as Soul Location / Soul Cast | no |

For comparison, `seedance_2_5` costs the same as 4.0 (3 / 6.5 / 9 per s), and `seedance_2_0` costs 3 per s at 480p, 4.5 at 720p and 3.5 in `fast` mode at 720p. The older `cinematic_studio_video` and `cinematic_studio_video_v2` (a Kling-based engine with `kling_element_ids`) are left out of this plugin's routing.

## Which engine

| The shot needs | Use |
|---|---|
| Known Seedance behaviour and this plugin's tested rules, nothing more | `seedance_2_5` (same price as 4.0) |
| Cinema Studio's looks (genre, era, tempo, camera body, lens, aperture, light, palette) plus Seedance 2.5's modes: edit, extend, start and end frames, 30 s | Cinema Studio 4.0 |
| Named look presets without looking up IDs (camera style, light scheme, colour grading), or a native multi-shot sequence | Cinema Studio 3.5 |
| No automatic speed ramps (`--speedramp linear`), 4K, or filing into a folder | Cinema Studio 3.0 |
| Cinematic stills filed into a folder, up to 4K | Cinema Studio Image 2.5 |
| Stills with a named camera body, lens and focal length | Cinematic Studio Image |

**Faces:** none of these engines has been tested for readable faces. Route face shots as the generate skill describes, and test one clip before planning face shots on a Cinema Studio engine.

**Consistency:** pick one engine and one set of look controls per sequence, and record them in the film bible. Mixing engines inside a sequence needs grade-matching, the same as mixing Seedance 2.0 and 2.5.

## Defaults that bite

- **`prompt_language` defaults to `zh` on 3.5 and 3.0.** Always pass `--prompt_language en` with an English prompt.
- **Generated audio defaults are different.** 3.5 and 3.0 default `generate_audio` to `false`; 4.0 and Seedance 2.5 default to `true`. Always pass `--generate_audio true` or `false` explicitly.
- **`enhance_prompt` defaults to `false` on 3.5 and 3.0.** Leave it off. Turning it on rewrites the prompt you wrote and linted.
- **`bitrate_mode`** exists only on 4.0 (and Seedance 2.5). Use `high`.
- **3.5 look controls:** `camera_style`, `light_scheme` and `color_grading` can't be combined with `style_prompt`. Use one or the other.
- **Media limits:** 3.5 and 3.0 take at most 15 media items in total (references plus start and end frames). 4.0 is assumed to follow Seedance 2.5's limits (30 images, 50 media), which is unverified.
- **Price checks don't validate IDs.** `generate cost` checks names such as `--genre noir` on 3.5 and 3.0, but accepts any string as a 4.0 ID. A wrong ID only fails when the job is created, so check each new ID with a cheap 4 s job first.
- **`generate cost` is not free on Soul Cast.** `higgsfield generate cost cinematic_studio_soul_cast` (and `soul_cast`) creates a real job and charges about 0.12 credits, measured on 17 September 2026. Price that engine by reading the rate here instead of running `cost`. Every other engine's `cost` call in this file was free.
- **Transient failures happen.** A first Image 2.5 job failed with no reason and was refunded; the same command succeeded on the retry. Failed jobs are refunded (verified).

## Cinema Studio 4.0 controls

The controls are IDs that the CLI can't list: `--genre_id`, `--era_id`, `--pacing_id`, `--camera_model_id`, `--camera_lens_id`, `--camera_aperture_id`, plus `--light` (`preset`, `custom` or `user`), `--light_id`, `--light_custom` and `--color_palette` (an object).

**Getting the IDs:** every job made in the Cinema Studio web app records the controls it used. Set the controls you want on one shot in the web app and generate it. Then harvest them:

```bash
python3 <plugin-root>/scripts/studio_ids.py harvest          # reads your recent jobs, stores name → ID
python3 <plugin-root>/scripts/studio_ids.py list camera_lens
python3 <plugin-root>/scripts/studio_ids.py find genre Noir  # prints the ID, or exits 1
```

The catalog lives in `~/.config/higgsfield-seedance/cinema-studio-ids.json` and grows each time you use a new option on the web.

**The options** named on Higgsfield's 4.0 pages:

| Control | Options |
|---|---|
| Genre | General, Action, Epic, Drama, Comedy, Horror, Noir. Genre steers lighting, camera energy, staging and pacing. |
| Era | Auto, 60s, 80s, 90s, 2000s, 2020s. Era regrades stock, halation and colour. |
| Tempo (pacing) | Auto, Chaotic, Dynamic, Calm, Single Shot. Tempo is editing style and cut speed. |
| Camera body | Auto, Modern, 35mm Film, 8mm Film, DV Camcorder |
| Lens | Auto, Clean Sharp, Anamorphic, Vintage Anamorphic, Warm Vintage, Halation Vintage |
| Aperture | Auto, f/1.4 Wide Open, f/4 Moderate, f/11 Deep Focus |
| Light | Auto, Silhouette, Practicals, Window, Overhead Fall, Contre-jour, Soft Cross |
| Colour palette | 50+ presets, e.g. Film Colors, Black Gloss, Candy Pink, Lime Jam, Nostalgic Blue |

**Camera moves:** Higgsfield describes 4.0's 30+ camera moves as hash tags typed into the prompt, stackable and run in order. Examples are Static shot, Handheld, Dolly in, Dolly out, Pan left, Pan right, Tilt up, Crane up, Tracking, Side tracking, Drone orbit, Arc left, Arc right, Whip pan, Rack focus, Dolly zoom, Crush zoom, Snorricam, Robot arm, POV, Bullet time, Helicopter shot and Aerial pullback. The exact tag syntax isn't documented. Until one test settles it, direct the camera in words as the prompt skill describes; that works on every engine.

## Cinema Studio 3.5 controls

| Flag | Values |
|---|---|
| `--genre` | `auto`, `action`, `horror`, `comedy`, `noir`, `drama`, `epic` |
| `--camera_style` | `classic_static`, `silent_machine`, `one_take`, `epic_scale`, `intimate_observer`, `impossible_camera`, `documentary_snap`, `raw_chaos`, `dreamy_flow` |
| `--light_scheme` | `soft_cross`, `contre_jour`, `overhead_fall`, `window`, `practicals`, `silhouette` |
| `--color_grading` | `naturalistic_clean`, `bleached_warm`, `hyper_neon`, `teal_orange_epic`, `sodium_decay`, `cold_steel`, `bleach_bypass`, `classic_bw` |
| `--style_prompt` | free text, instead of the three style axes |
| `--multi_shots`, `--multi_shot_mode` (`auto`/`custom`), `--multi_prompt` | native multi-shot; the `multi_prompt` array format is unverified |

3.5 also accepts camera body, lens, focal length and aperture IDs in the web app. They aren't in its CLI schema.

## Cinema Studio 3.0 controls

| Flag | Values |
|---|---|
| `--genre` | `auto`, `action`, `horror`, `comedy`, `noir`, `drama`, `epic` |
| `--speedramp` | `auto`, `linear`, `slowmo`, `speedup`, `fast_to_slowmo`, `slowmo_to_fast`, `super_slowmo`, `impact` |
| `--preset_id` | a preset ID (source unverified) |
| `--folder_id` | see [Folders and projects](#folders-and-projects) |
| `--resolution` | up to `4k` |
| `--multi_shots`, `--multi_shot_mode`, `--multi_prompt` | as 3.5 |

`--speedramp linear` is the one CLI route to real-time motion with no automatic speed ramps. Seedance 2.5 and Cinema Studio 4.0 always run their speed ramp on `auto`.

## Stills

- **Cinema Studio Image 2.5** (`cinematic_studio_2_5`): cinematic stills with up to 14 references, 2 credits at 1k or 2k and 4 at 4k, `--batch_size` for variants, and `--folder_id`. It's a good fit for keyframes when the project lives in Cinema Studio. The prompt rules in `image-prompts.md` apply.
- **Cinematic Studio Image** (`cinematic_studio_image`): requires `--camera_model_id`, `--camera_lens_id` and `--camera_focal_length_id`, so harvest those first.
- **Soul Cinema Studio** (`soul_cinema_studio`): the Soul Cinematic look with `--style_id` (harvestable, e.g. "General") and a Soul ID through `--custom_reference_id`.

## Controls and the prompt

Let the controls carry the look, and let the prompt carry what only words can: blocking, action timing, the diagonal field of view and camera distance, light direction and the performance. Never let the two disagree.

- **Grade and palette:** with a palette or `color_grading` set, drop colour-grade words from the style block. "Warm golden grade" against `cold_steel` gives mud.
- **Light:** a light preset or scheme fixes the light's character. Keep the prompt's light direction consistent with it (Contre-jour means the source is behind the subject, facing the camera), or leave the control on Auto and direct the light in words.
- **Lens and aperture:** the lens control sets the rendering character (anamorphic, vintage, halation). The prompt still gives the field of view and distance, which set the framing. f/11 Deep Focus contradicts "background dissolved into bokeh".
- **Tempo:** Single Shot or Calm suits a single continuous take. Don't ask for cuts in the prompt while tempo says Single Shot.
- **Genre and era:** set them once per sequence. Genre also changes staging and pacing, so check that the performance direction (`acting.md`) still fits.
- **Speed:** with `--speedramp linear` on 3.0, "real-time, constant speed" in the prompt is redundant but harmless.

The linter covers the Cinema Studio video engines: `preflight.py --model cinematic_studio_video_4_0` applies Seedance 2.5's mode and media rules, and `--model cinematic_studio_video_3_5` or `cinematic_studio_3_0` checks the 4–30 s range and the 15-item media limit, without modes.

## Folders and projects

**Verified on 17 September 2026:** a CLI job with `--folder_id` lands inside that folder of the Cinema Studio project, and shows up there in the web app (a failed one shows as "Failed — credits refunded", with Retry and Delete). A job without `--folder_id` stays in the account's general history, outside the project.

- **Which engines:** Cinema Studio 3.0 and Cinema Studio Image 2.5 accept `--folder_id` (so do Marketing Studio and some utility models). Cinema Studio 4.0, 3.5, Seedance and the other image models don't, so their jobs can't be filed into a project from the CLI.
- **Finding the ID:** the CLI has no folder listing. Ask the user for it, or read it from the project page in their browser: each folder row in the left-hand Folders list carries its ID as a `data-id` attribute, and folder URLs use `/generate/<mode>/<model>/folders/<folderId>`.
- **Plan around it:** if everything must live in the project, route the stills to Image 2.5 and the video to Cinema Studio 3.0. Anything made on 4.0, 3.5 or Seedance has to be uploaded into the project by hand.
- **Workspaces** (`higgsfield workspace`) are billing and team contexts, not projects.

## Commands

```bash
# Cinema Studio 4.0: price, then create (Seedance 2.5 modes; control IDs from studio_ids.py)
higgsfield generate cost cinematic_studio_video_4_0 --mode omni_reference --start-image ./kf.png \
  --duration 4 --resolution 480p --aspect_ratio 16:9 --prompt "$(cat prompt.txt)"
higgsfield generate create cinematic_studio_video_4_0 --mode omni_reference --start-image ./kf.png \
  --duration 4 --resolution 480p --aspect_ratio 16:9 --bitrate_mode high --generate_audio false \
  --genre_id "$(python3 <plugin-root>/scripts/studio_ids.py find genre Drama)" \
  --prompt "$(cat prompt.txt)" --wait --wait-timeout 30m --json

# Cinema Studio 3.5: named look presets
higgsfield generate create cinematic_studio_video_3_5 --duration 8 --resolution 720p --aspect_ratio 16:9 \
  --genre drama --camera_style intimate_observer --light_scheme window --color_grading naturalistic_clean \
  --prompt_language en --generate_audio true --prompt "$(cat prompt.txt)" --wait --wait-timeout 30m --json

# Cinema Studio 3.0: no speed ramps, filed into a folder
higgsfield generate create cinematic_studio_3_0 --start-image ./kf.png --duration 6 --resolution 720p \
  --speedramp linear --genre drama --prompt_language en --generate_audio false --folder_id <folder_id> \
  --prompt "$(cat prompt.txt)" --wait --wait-timeout 30m --json

# Cinema Studio Image 2.5 keyframe
higgsfield generate create cinematic_studio_2_5 --resolution 2k --aspect_ratio 16:9 \
  --image-references ./portrait.png --prompt "$(cat still.txt)" --wait --json
```

`--prompt "$(cat file)"` sends exactly the text you linted. Seedance jobs also accept the prompt on standard input; that hasn't been checked for the Cinema Studio engines.

## Unverified: first tests

Run these before building a film on Cinema Studio, one at a time and each after the user approves its cost:

| Test | Settles | Cost |
|---|---|---|
| The same approved Seedance 2.5 prompt on 4.0 at 480p, 4 s, controls on Auto | Whether 4.0 with no controls behaves like `seedance_2_5` (its jobs report `model: default`) | 12 |
| — | Folder filing: **done** (17 September 2026), see above | — |
| One 4.0 clip with harvested genre, lens and light IDs | That harvested IDs work from the CLI, and how much they change the shot | 12 |
| A 4.0 prompt with one camera-move tag | The tag syntax | 12 |
| 3.0 with `--speedramp linear` on a move that ramped on 2.5 | That linear really removes the ramp | 14 |
| A 4.0 start frame with a readable face | Face refusal behaviour on 4.0 | 12 |

Also still unknown: which underlying model 3.0 and 3.5 use; the formats of `--color_palette`, `--light_custom` and `--multi_prompt`; and whether 4.0's reference limit is 50 as on the web.
