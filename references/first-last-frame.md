# First & last frame prompting

A start frame (and optionally an end frame) pins the opening composition and the destination. That flips the usual prompt economy: **the frames carry what things look like, so the prompt carries only the journey between them.** With strong frames the prompt can be one line. Every sentence you add should describe motion, transformation or sound, never what the frames already show.

## On Higgsfield

- Mode must be `omni_reference`. `--start-image` is the anchor and `--end-image` is optional.
- Refer to the frames in words: "the start frame", "the end frame". Numbering (`Image 1`, `Image 2`) for directly wired frames is unverified on Higgsfield, so words avoid ambiguity, especially if you also attach `--image-references`. In that case number only the references (`@Image 1` = first `--image-references`).
- Point attribute locks at the frame: "the juice color strictly matching the end frame".

```bash
higgsfield generate create seedance_2_5 --mode omni_reference \
  --start-image ./fruit_character.png --end-image ./juice_bottle.png \
  --duration 8 --resolution 480p --aspect_ratio 9:16 \
  --wait --wait-timeout 30m < prompt.txt
```

## What the prompt does, by kind of change

1. **The frames differ in time or place: name the transition type.** One line is often enough.
   - `City skylines transition from day to sunset, time-lapse photography.`
   - `The FPV perspective is dynamically shuttled, seamlessly connecting to show the transition of time and space.`
2. **The subject changes state: stage the metamorphosis in order.** Naming the stages lets the model sequence them, with the end frame as the destination.
   - `The girl lowers her head, and when she looks up, her body deforms, her hair swells, and she transforms into a wolf. The camera zooms out.`
3. **Both frames share a world and the journey is cinematic: choreograph the camera.**
   - `The camera quickly zooms in to a close-up of the knight's face. The knight unsheathes his sword, a cold light flashes. The camera rotates around the knight, then quickly pulls away — the picture switches to the dragon rising into the air. The knight and the dragon clash fiercely, tight movements, rapid rhythm.`
4. **The frames are nearly identical and the clip is atmosphere: keep micro-motion gentle.**
   - `A bird lands on the grass, and the surrounding flowers sway gently in the breeze.`

## Worked example: product story between two frames

The start frame is a cartoon fruit character and the end frame is the filled juice bottle. The prompt narrates everything in between, locks the juice color to the end frame, quotes the voiceover line and lists the sound effects:

```
A lighthearted, playful cartoon-style video. The fruit from the start frame blinks. An
empty glass bottle — the bottle from the end frame, still empty — slides in from one
side and stops in front of the fruit. The fruit performs a simple magical gesture.
Sparkling magic appears, and juice materializes directly inside the bottle, the color
strictly matching the end frame. As the bottle fills, it grows larger and moves to the
center. The fruit runs off-screen, and the final shot holds on the filled bottle exactly
as in the end frame. A friendly voiceover says, "Squeezed this morning. Gone by noon."
The voiceover must finish before the video ends. Include soft blink sounds, magic
sparkle audio, a light juice-fill sound, glass clinks, and a quick running sound.
```

## Craft rules

- **Don't describe what the frames show, only what changes between them.** Restating the start frame invites the model to reinvent it. This fits with SKILL.md rule 14 (lock the first frame): lock only what the action depends on (who, where, which hand) in about 25 words, and add "as in the start frame".
- **The end frame is a target state, not a guaranteed final pixel.** End the prompt with the subject arriving at that state and holding: "the final shot holds on the filled bottle".
- **Quote the voiceover line exactly and add** `The voiceover must finish before the video ends.` An empty quote or a `[your line here]` slot is a decision nobody has made yet. Fill it, or ask the user, before generating.
- **When audio is on, list the sound effects by event.** Listed sounds land on their actions, and unlisted ones get invented or skipped.
- **Keep to one transformation per clip.** A morph plus a location change plus a style shift in one short clip produces mush. Chain clips instead (see `edit-extend-chain.md`).
- **Start frames with a large, readable human face are likely to be refused.** Use frames where people are small, turned away or covered, and describe the person in text.
- **Keep both frames at one field of view.** If they differ (a crane from 63° to 37°), name only the landing FOV, prefer 6 s, and allow a re-roll, because the model may zoom or morph between them.

## A 4 s start-frame skeleton

About 185 words, which suits one action from a keyframe:

| Part | Words | Example |
|---|---|---|
| First-frame lock | ~25 | "The first visible frame already contains her at the bench, the module in her left hand, as in the start frame." |
| References and anchor lines | ~40 | "@Image 1: the grey actuator module, in her left hand. 100% matches the reference." |
| Optics | ~25 | "About 47° diagonal field of view, camera 1.2 m away at chest height, on her left." |
| Action, timed if the edit keeps a short slice | ~40 | "At about 1 s she turns the module a quarter turn toward the lamp." |
| Light | ~25 | "Warm task lamp from frame left, cool daylight from behind camera; the far side of her face in soft shadow." |
| Locks | ~20 | "Plain unmarked surfaces. Real time, constant speed." |
| Style anchor | ~10 | "Natural colour, fine grain." |
