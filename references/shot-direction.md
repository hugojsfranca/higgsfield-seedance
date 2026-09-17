# Shot direction

Adapted from Higgsfield's own prompt-director guide for Seedance 2.0 ("CINEDANCE V4"). The guide treats a prompt as direction for one shot: who stands where, what the lens shows, where the light comes from, and what happens when. It applies directly to shots routed to Seedance 2.0. It should carry over to Seedance 2.5 as the same model family, but that hasn't been separately verified. This file condenses the guide and reconciles it with what this plugin learned in testing.

## Contents

- [Diagnose before writing](#diagnose-before-writing)
- [Prompt architecture](#prompt-architecture)
- [First frame and blocking](#first-frame-and-blocking)
- [Gaze and body orientation](#gaze-and-body-orientation)
- [Sides: body to frame](#sides-body-to-frame)
- [Location references as maps](#location-references-as-maps)
- [Optics: field of view, not millimetres](#optics-field-of-view-not-millimetres)
- [Camera as operator behaviour](#camera-as-operator-behaviour)
- [Physics anchors](#physics-anchors)
- [Lighting as a priority lock](#lighting-as-a-priority-lock)
- [Format mode and cut types](#format-mode-and-cut-types)
- [Dialogue](#dialogue)
- [Reference hierarchy](#reference-hierarchy)
- [Negations: local locks, not lists](#negations-local-locks-not-lists)
- [Density and style anchors](#density-and-style-anchors)
- [Self-check](#self-check)

## Diagnose before writing

First strip the brief down to this one shot. Keep the active people, references, props and vehicles, the action, the first visible frame, the layout, the light direction and the audio. Drop scene numbers, headers, other scenes, production notes, and anything not visible or audible in this shot.

Then ask where the shot will fail, and add a short lock for each real risk:
- The first frame opens empty, or on an establishing view instead of the subject.
- A required person appears late, far from the landmark, or twice.
- A gaze or body orientation reverses, left and right flip, or the camera picks the wrong side.
- The lens drifts to a comfortable middle, or the light goes flat and frontal.
- Prose overwrites the reference, or a stale @reference slips in.
- A prop lands in the wrong hand, motion floats, or dialogue starts late.
- A location reference gets copied as framing instead of geography.
- An internal cut resets continuity.

## Prompt architecture

Write in this order, skipping sections that add nothing:

1. **Scene context:** one or two sentences on what happens in this shot.
2. **Active references:** each @reference with its role and a minimal anchor line.
3. **Location map:** camera position and facing, foreground, midground and background, and landmarks.
4. **First frame and spatial blocking:** who is where, facing what, from frame one.
5. **Format mode:** a single continuous take, or a controlled multi-shot with every cut defined.
6. **Optics:** field of view, camera distance and the visible optical result.
7. **Camera:** height, side, movement and focus.
8. **Action timing:** time blocks, one action each.
9. **Physics:** weight, contact, and cloth and hair delay wherever motion matters.
10. **Lighting:** source, direction relative to camera, and what the exposure favours.
11. **Audio:** sound events and dialogue rules.
12. **Positive constraints:** the states that must hold, such as wardrobe, plain surfaces and real-time speed.

Put placement before style, optics before aesthetics, and treat light as a constraint rather than decoration. Uppercase section labels (SCENE CONTEXT, LOCATION MAP, …) are fine and help long prompts. Short shots can use plain paragraphs in the same order.

Settings passed as CLI flags (duration, aspect ratio, resolution, mode, generated audio) don't belong in the text. Only prompt-level settings do: single take or multi-shot, real time or slow motion, and dialogue and subtitle rules.

## First frame and blocking

When the shot must open on its subjects, which is always the case for clips that will be trimmed, say so: "The first visible frame already contains her at the railing, tablet in hand; the spatial relationship reads immediately."

For each important subject, give:
- screen position (e.g. screen-left third)
- world position
- distance to the landmark or the other person
- the way the body faces
- where the eyes go
- the direction of movement
- the depth layer

Replace weak words with measurable ones. Instead of "near the car", write "within 1 metre of the car, one hand on the bonnet". Other examples: "back against the wall", "standing directly under the sign", "at the kerb edge", "boots on the yellow bay line".

## Gaze and body orientation

Body and eyes are separate instructions. Examples:
- "Torso faces the gallery; eyes stay on the people moving up there."
- "Back to camera."
- "Profile to screen-left."
- "Looks past the lens toward the coordinator."

Give the eyes a target rather than saying where they shouldn't look.

## Sides: body to frame

The most common geometry error in a long film is writing a body side where a frame side belongs. In one dry run it happened five times, e.g. "walking toward frame right, her left side to camera": walking right shows the right side. Convert with this table:

| Pose as the camera sees it | Their left side and hand | Their right side and hand |
|---|---|---|
| Facing the camera | frame right | frame left |
| Back to camera | frame left | frame right |
| Profile facing, or walking toward, frame left | toward the lens | away from the lens |
| Profile facing, or walking toward, frame right | away from the lens | toward the lens |
| Back three-quarters, facing away and to frame right | far side | near side |
| Over the left shoulder, camera just outside it | shoulder low at frame right, hair at the right edge, left wrist lower left | the gesturing right hand enters from frame right |
| Over the right shoulder | the mirror of the row above: the subject sits in the left third | |

- **Moving shots:** under an orbit or a turn, state sides for the first frame and the landing only.
- **Reverse angles:** a reverse angle swaps every frame side. Keep each set's map in body terms ("lamp on her left, tray on her right") and convert it for each shot.
- **Props in the left hand:** a left-hand prop moving left to right rides on the far side of the body. For each hero prop, decide whether to accept that or move the camera.
- **Over-the-shoulder:** put the gaze target on the side away from the camera. Pick one OTS convention for the film. Reference views, such as hands sheets, either match it or keep the shoulder out of frame.

## Location references as maps

A location image supplies geography, materials, atmosphere and landmark positions. Say what you're taking from it ("the plant-room layout and cable trays from @Image 2") and set your own camera. Otherwise the model copies the reference's framing.

## Optics: field of view, not millimetres

Higgsfield's guide reports that Seedance follows a diagonal field of view, a camera distance and a described optical result better than millimetres, f-stops or lens brands. You can keep the brief's mm, but add all three controls:

| Brief says (full frame) | Diagonal FOV | 16:9 frame width | Rough distance, medium framing | What it looks like |
|---|---|---|---|---|
| 16 mm | 107° | 2.35 × distance | 0.5–0.8 m | foreground looms, environment reaches every edge, lines stay straight |
| 24 mm | 84° | 1.57 × | 1–1.5 m | wide, strong but natural perspective, context readable |
| 28 mm | 75° | 1.34 × | 1–2 m | wide environmental |
| 35 mm | 63° | 1.07 × | 2–3 m | natural wide-normal |
| 50 mm | 47° | 0.76 × | 3–5 m | human-eye perspective, no distortion |
| 65–70 mm | 34–37° | 0.53–0.58 × | 4–6 m | gentle compression, portrait-friendly |
| 85 mm | 29° | 0.45 × | 4–6 m | short-tele portrait: background compresses into soft bokeh |
| 100 mm | 24° | 0.37 × | 35–40 cm for one connector face, 70–80 cm for two side by side | tight detail or macro, as its own beat |
| 135 mm | 18° | 0.28 × | 6–8 m | strong compression, focus thin enough to isolate the eyes |
| 300 mm | 8° | 0.12 × | 20–25 m | observation from far away: background a colour wash, soft foreground occlusion |

The guide gives distances for 16, 24, 50, 85, 135 and 300 mm; the rest are interpolated.

**Check every size claim against the frame width.** Width = distance × the factor above (height = width × 0.56). A 70 mm lens at 120 m frames about 64 m, so a 64 m aircraft fills the frame and can't sit "across the middle third". A 100 mm lens at 35 cm frames about 13 cm, which is too narrow for two 8 cm parts. `scripts/optics.py 70mm 120m` prints the numbers.

- **Choose by content.** Environment and action suit 47–107°. Portraits suit 29° or 18°. Detail suits 29° or 18°, as its own beat. Distant observation suits 8°.
- **Don't mix content types in one beat.** Portrait, environment and macro in the same beat makes the lens drift. Give each internal shot its own FOV and cut hard between them.
- **Back each lens with visible results.** For telephoto, give at least four: background compressed flat, only the subject sharp, creamy bokeh, framing by reach rather than proximity, haze between camera and subject, soft foreground occlusion. For wide, give at least three: foreground looms, environment to the edges, deep focus, straight lines stay straight.
- **Avoid these phrasings:** "ultra-wide", "tight wide framing", "zoom out while wide", compound camera moves in one shot, and lists of lens brands or f-stops.

## Camera as operator behaviour

Write what an operator does: "camera at hip height, 2 m from her, on the shadow side, drifting 30° clockwise". Specify height, distance, side, subject size and screen placement, movement, and focus. Handheld means breath, micro-settling and weight shifts, not digital shake.

## Physics anchors

Add these where motion sells the realism:
- **Walking:** heel contact, weight transfer, hip shift, toe push-off.
- **Objects:** carried objects pull the arm and swing with inertia, and doors resist on the hinge.
- **Vehicles:** they have mass and suspension.
- **Cloth, hair and liquids:** cloth and hair lag behind the body, and liquids drip and pool with viscosity.
- **Particles:** they follow the wind.

Show cause before effect, and don't let anything float.

## Lighting as a priority lock

Name the source, its direction relative to the camera, which side of the subject is in shadow or rim, how bright the background is, and what the exposure favours. For example: "Morning sun from camera-right, behind her; the camera stays on the shadow side; rim light along her shoulders; exposure for the window." For backlight: the subject stands between the camera and the bright background, the face may fall into shadow, and detail comes only from rim and bounce. Flat front light is the default failure. Say where the light isn't coming from only after you've said where it is.

## Format mode and cut types

Default to a single continuous take and say so.

Use a controlled multi-shot only when the brief needs cuts. Then define every cut: each shot's duration, camera, first-frame subjects, blocking and action, and the cut type (HARD, MATCH, INSERT, REVERSE, WHIP or SMASH). Never let the model invent cuts. Write "Hard cuts only; no fades or dissolves" unless a transition is wanted. Between clips, identical framing across a change of place reads as a jump cut: declare it a match cut, or change the shot size or angle. Across internal cuts, keep the characters, geography, screen direction, gaze targets, light direction, wardrobe and prop states the same.

## Dialogue

For the performance around the line (what the speaker wants, the listener's reaction, voice lines), see `acting.md`.

- **Only the quoted line is spoken.** Lips stay still otherwise, and there are no ad-libs, narration, subtitles or offscreen voices unless written.
- **Speech on the first beat:** "the line begins within the first 0.3 seconds".
- **Breathing room:** "one second of silence before and after the line".
- **A line from earlier that only sets mood:** "Prior audio context only, not visual content: '…'".

## Reference hierarchy

Each type of reference controls different things:
- **Identity:** face, body, age, costume and anchors.
- **Location:** architecture, geography, atmosphere and landmarks.
- **Prop:** shape, scale, material, state and hand contact.
- **Vehicle:** model, decals, doors and damage.

A style reference never overrides identity, blocking, action, optics or light.

When a reference also fixes framing or light (an approved still, a relit plate), the text must agree with it. Copy its distance, lens and light side into the prompt. When a reference carries only appearance, say which aspect to take ("hands and cuffs only"), because the model otherwise inherits its framing too.

Give each referenced person or object one minimal anchor line, for example: "@Image 1: 30-year-old courier, short red hair, yellow rain jacket, parcel under her left arm. 100% matches the reference." The image is the source of truth. A project's character bible decides hands and props, whatever an example here says.

## Negations: local locks, not lists

This skill found that lists of unwanted things summon them ("no denim" produced denim), and Higgsfield's guide agrees: no standalone negative block by default. What does work is a short negation placed right after the positive state it protects, aimed at a failure mode rather than an object. Examples: "Faces stay in shadow; no flat front light." "Hard cuts only; no dissolves." "No subtitles, no music." Name concrete objects only in positive terms: "plain unmarked fuselage", not "no airline logos".

## Density and style anchors

Spend words where control matters: identity anchors, blocking, first frame, gaze, hands and props, timing, optics, light, physics and dialogue. Spend few on beauty adjectives, background extras, or anything the reference already shows. Style comes last, as one compact anchor ("Kodak Vision3 500T, natural light, real grain", "Lubezki natural-light handheld"), never a chain of names.

## Self-check

Run this in addition to `scripts/preflight.py`. Before submitting, confirm:
- Every @reference is used and none is stale.
- The first frame is right.
- Every position, facing and gaze is clear, and every body side has been converted to a frame side with the Sides table.
- Landmark distances are physical, and every size claim fits the frame width at the stated distance.
- The light side matches the reference plate and any neighbouring shot at the same hour.
- The camera side and FOV are chosen by content and protected from drift.
- The light has a direction.
- Props are in the right hands.
- The actions fit the time.
- Dialogue is exactly the quoted line.
- Nothing mentions other scenes.
