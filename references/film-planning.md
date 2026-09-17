# Planning a multi-scene film

Read this when a brief runs to more than a handful of clips, has recurring characters or objects, or has a budget that could run out. It comes from a full dry run of an 89 s, 22-scene corporate film: 83 shot-list rows, 71 generated clips and about 150 still images. Everything here is about keeping many generations consistent, affordable and in order. Shot-level craft is in `shot-direction.md`.

## Contents

- [The pipeline and its gates](#the-pipeline-and-its-gates)
- [The shot list](#the-shot-list)
- [The asset bible](#the-asset-bible)
- [Building the reference library](#building-the-reference-library)
- [Faces: threshold, tests and routing](#faces-threshold-tests-and-routing)
- [Screens made for compositing](#screens-made-for-compositing)
- [Budget](#budget)
- [Resolution strategy](#resolution-strategy)
- [Working at this scale](#working-at-this-scale)

## The pipeline and its gates

Each stage ends at a gate: the user approves before the next stage spends anything.

| Stage | Output | Gate |
|---|---|---|
| 0. Free prep | Scratch voiceover, temp music, an animatic from storyboard frames, locked scene durations. Every prompt drafted and linted. `generate cost` run for each model and setting. | Timing and open questions answered |
| 1. Canaries | Upscale test on an existing take. Face tests (below). One screen plate. One object-reference test, which also settles `@Image` numbering next to a start frame. | Routing, upscale path and reference behaviour locked |
| 2. Reference library | Character sheets, continuity objects, environment masters. | Contact sheets approved |
| 3. Keyframes | One still per clip, built from the library. | Per-act contact sheet and updated animatic |
| 4. Drafts | Clips in batches of about six. The first clip of each new risk type (a new camera move, a two-person shot, a vehicle) runs alone first. | Per-act rough cut |
| 5. Picture lock | Full edit with scratch VO and temp UI. | Last cheap point for changes |
| 6. Finals | Upscales, plus the few re-renders that earn native 720p or 1080p. | Large-screen check |
| 7. Post | UI compositing, copy, end card, grade, final VO, music, sound. | Delivery |

Hold back a credit floor (e.g. 500) that isn't touched until picture lock. If spend passes the plan by about 15% before lock, stop and re-plan with the user.

## The shot list

One row per generated clip. `scripts/shotlist_check.py` validates this format:

```
scene,shot,description,film_in,film_out,film_seconds,clip_id,model,mode,clip_seconds,start_keyframe,end_keyframe,object_refs,readable_face,audio,time,state,match,primary_action,cut_note
```

- **Timings:** `film_in` and `film_out` run continuously from 0 to the film's length. `film_seconds` is the slice used in the edit.
- **Durations:** `clip_seconds` is what gets generated. Seedance 2.5 takes 4–30, Seedance 2.0 takes 4–15.
- **Reuse:** a `model` of `post` (with `clip_seconds` 0) marks a slice reused from another clip, or a still with a push. Reuse cuts cost a lot, e.g. a later scene that reprises earlier overheads.
- **Actions:** `primary_action` is the clip's only action (prompt rule 2).
- **Cut notes:** `cut_note` names the slice window (`use 1.5–2.8`) and any match cut it serves. Leave no row without a window.
- **IDs, not paths:** `start_keyframe`, `end_keyframe` and `object_refs` hold asset IDs, never file paths. A first/last-frame clip puts its end frame in `end_keyframe`, not in the same field as the start. Mark existing approved takes with "approved" in `cut_note`.
- **Files:** name prompt files `prompts/<clip_id>.txt` and keyframes `keyframes/<start_keyframe>.txt`, with the approved still next to each as `.png`.
- **Time of day:** `time` carries the story clock (early morning … golden hour). The checker warns when it runs backward within a scene.
- **State:** `state` carries what a character carries or wears that can change: "gloves on; tablet under L arm; case in L hand". Restate it in every prompt and keyframe in range, so a hand-off shot doesn't drop the kit.
- **Cross-scene matches:** `match` names a shared spec ID (e.g. `S06C-depot`) for every match cut or echo between shots, especially when different writers own them. The planner keeps the spec texts in one `shared_specs.md`, and each keyframe copies its spec word for word.
- **Short windows:** when a window is under about 1.2 s, the prompt times the event inside it ("at about 1 s").

## The asset bible

A table of every recurring person, object and place, each with an ID, a filename and the exact line that goes into every prompt that uses it.

- **IDs and files:** `CH01` (the lead) → `assets/CH01_portrait.png`, `CH01_fullbody.png`, `CH01_profile_left.png`, `CH01_profile_right.png`, `CH01_hands.png`. Objects are `OBJ01…` and environments `ENV01…`.
- **One manifest, one resolver:** approved picks are recorded with `scripts/assets.py record ID view file`, which writes `assets/manifest.csv`. Every run script finds files only through `scripts/assets.py resolve ID[:view]`, which prints exactly one path or fails. Candidates, other extensions (`.jpg`, `.webp`) and two-variant places (a building by day and at golden hour; an atrium and an office floor) then can't be picked up by mistake. Give variants distinct view names.
- **Location maps:** give every recurring place a map in body or world terms:
  - landmark sides relative to the working position, e.g. the bench has the lamp on her left and the tray on her right;
  - vehicle orientation, e.g. the held trailer is backed onto the centre bay;
  - sun direction by time of day, e.g. the HQ is lit from the left in late morning and from the right at golden hour.
  Each shot restates the map converted to frame terms (Sides table in `shot-direction.md`). Reverse angles swap every frame side.
- **Hands:** set each character's dominant hand and which hand holds each prop, and convert body sides to frame sides in every prompt. The bible overrides any example in this plugin.
- **Wardrobe lines:** word for word in every keyframe prompt, never paraphrased.
- **Acting profile and voice line:** every character who acts or speaks gets an acting profile (about 80–130 words of observable behaviour: tics with triggers, a mask and its crack, a named gait) and one locked voice sentence. Each clip rewrites the profile for its moment, and anyone who speaks gets the voice line pasted word for word. Format and example in `acting.md`. Per-scene objectives and obstacles go in the scene notes.
- **Look-alikes:** props that could be confused get distinct looks, e.g. a grey component case, an orange adapter case and a black equipment case.
- **Cast and props:** drop characters and props no scene uses. Add anyone who recurs without a description, such as a security coordinator seen in six shots.

## Building the reference library

Write and run every still with the image skill. Models, prices, rules and templates are in `image-prompts.md`.

- **Characters:** make the master portrait first (Soul 2.0 or Soul Cinematic; a Soul ID only for a real person with consent) and get it approved. Then generate the other views from it as a reference, one view per image: `higgsfield generate create nano_banana_pro --resolution 2k --image-references assets/CH01_portrait.png --aspect_ratio 16:9 --prompt "..."`. A text description alone holds wardrobe but not a face. Multi-panel sheets are for approval only and never go into the manifest.
- **Objects:** use GPT Image 2 (or Nano Banana Pro) for exact geometry and legible structure. Use real product photos, with no people in them, whenever they exist.
- **Environments:** Soul Location makes people-free masters cheaply, but it takes a prompt only, with no references. Soul Cinematic suits 21:9 and cinematic plates. Add people afterwards with Nano Banana Pro, using the master as a reference. A reverse angle of a place goes to GPT Image 2, or to Nano Banana Pro with every object's new side written out.
- **Scene keyframes:** Nano Banana Pro at 2k (the same price as Nano Banana 2 at 2k) with the character, object and environment references attached. Refer to each reference in words ("the woman in the portrait reference"). Each prompt is written as if it were the only one (no "same as the previous image", no asset IDs in the text).
  - When a reference fixes framing or light (a relit plate, an approved still), copy its distance, lens and light side into the text.
  - When a reference carries only appearance, say what to take ("hands and cuffs only").
  - Attach a location plate beside a start frame only when the camera reveals space beyond the still.
- **Prefixes by asset type:** a single global "quality prefix" that says "real people at work" fights the people-free plates and object shots. Keep separate prefixes for people, objects and environments. Each is positive only: prompt rule 5 applies to image prompts too. For example, "no text, no logos, no CGI" becomes "every surface plain and unbranded; photographed on a real location".
- **Keep prefixes to one register line** (about 15–40 words). In the dry run, a 110-word boilerplate prefix pushed the median keyframe prompt to 336 words, and details start dropping out past about 330. Spend the words on the bible lines, the framing spec and the light instead.

## Faces: threshold, tests and routing

**Count a face as readable** when it's at least ~8% of the frame height and turned no more than ~45° from the camera. Treat anything smaller, lowered, turned further, or seen from behind as "small or turned".

**Test before committing**, at about 10 credits per 2.5 test:

| Test | Input | Decides |
|---|---|---|
| Profile | a profile keyframe on 2.5, 480p, 4 s | whether 2.5 accepts profile faces |
| Three-quarter | a three-quarter keyframe on 2.5 | whether 2.5 accepts frontal-ish faces |
| Same frames on 2.0 | the real clips at 720p, with the portrait as `--image-references` | whether 2.0 holds identity (these are keepable finals) |
| Small figure | a from-behind wide keyframe on 2.5 | whether 2.5 accepts any person in a start frame |

**Routing from the results:**
- Readable faces go to Seedance 2.0 (the start frame plus the master portrait) unless both 2.5 tests pass with good identity.
- Small or turned figures go to 2.5.
- If the small-figure test is refused, stop and re-plan every person shot.

Write each 2.5 face test as its own prompt variant (e.g. `S09_A_T1`) with no face reference attached. A face reference would spoil the test.

**Mixing models is normal.** Grade-match 2.0 and 2.5 clips in post, and keep light direction and wardrobe lines identical across both.

## Screens made for compositing

- The screen is "plain dark glass with a soft even glow" in every keyframe and prompt. The UI is added in post, and the model never draws an interface.
- **Keep it trackable:**
  - Frame over the shoulder opposite the gesturing hand, so only one fingertip crosses the glass.
  - Keep all four corners in frame.
  - Keep the camera locked or slow.
  - Allow one gesture per clip (a tap, or a single drag).
- **Use a still where you can.** When the UI moment is static, a still plus a slow push in post beats a generated clip.
- **Resolution:** hero UI plates earn 720p re-renders, because compositing needs clean edges.
- **Tap map:** deliver one with the prompts. For each gesture, give the contact point in screen terms, the clip time and the UI it drives. A drag plus a tap needs 6 s or two clips.

## Budget

Estimate every stage from one dated rate table, then confirm with `higgsfield generate cost`, which is free and authoritative.

| Model | Estimate (September 2026) |
|---|---|
| Seedance 2.5 | 2.5 / 6.5 / 9 credits per s at 480p / 720p / 1080p |
| Seedance 2.0 | ~4.5 per s at 720p (check 480p and 1080p with `cost`) |
| Nano Banana Pro (`nano_banana_pro`) | ~2 per image at 1k or 2k, ~4 at 4k |
| Nano Banana 2 (`nano_banana_flash`) | ~1.5 at 1k, ~2 at 2k |
| GPT Image 2 | ~6.5 at high quality, ~2 at medium, ~0.5 at low 1k |
| Seedream 4.5 | ~1 per image |
| Soul 2.0 / Soul Cinematic / Soul Location | ~0.12 per image |
| `bytedance_video_upscale` | a fraction of a credit per clip |

- **Re-roll allowances:** ×1.5 on 480p drafts, ×1.6 on keyframes, ×1.3 on sheets and objects, ×1.6 on clips made directly at final resolution.
- **Scenarios:** give at least two against the balance, e.g. "all 2.5 at 480p plus upscale" and "hybrid, faces on 2.0". Split the recommended one into per-act envelopes.
- **Reference point:** in the dry run, 71 clips (293 generated seconds) plus about 150 stills came to about 2,000 credits for the hybrid plan. Rendering everything natively at 720p would have been about 4,000.

## Resolution strategy

- **Default path:** draft at 480p, lock the prompt, keep the approved take, and upscale it with `bytedance_video_upscale --preset aigc --resolution 1080p` (or 4K).
- **Test the upscale first:** on an existing take, before planning around it.
- **Where native 720p or 1080p is worth it:** only hero UI plates, the end plate, and shots held on screen for about 1.2 s or longer.
- **Bitrate:** always use `--bitrate_mode high` for film work. It's free, and everything will be graded and upscaled.

## Working at this scale

- **Split the writing by act,** and keep one shared plan: routing, bible, shot list and rules for writers. Every writer reads the plan first.
- **Write files one at a time.** Long single responses hit output limits. Write the shot list and plan in appended sections, and one prompt file per step.
- **Stamp approved work** with the skill version it was written under, so a later rule change doesn't silently invalidate it.
- **Re-approval:** porting approved prompts to newer rules can change compositions (e.g. faces turned away to lower refusal risk). Flag that for re-approval rather than slipping it in.
- **One run-script pattern:** start every act's script from `scripts/film_run_template.sh`. It has numbered takes that never overwrite a job record, a `DRY=1` mode, input checks before any paid step, y/N gates, gate-marker files, the shared asset resolver and a pinned preflight path, and it's bash 3.2-safe.
- **Brief-change log:** every storyboard beat that's dropped, merged or changed goes into one list the user sees, not only into scene notes. That matters most for story payoffs, such as a case swap that pays off an earlier clearance check.
- **Review before spending:** after the writers finish, one reviewer checks continuity, sides, routing, optics size claims, scripts and budget across the whole film. In the dry run that caught five left/right contradictions, two impossible framings and two broken asset lookups, all free to fix.
