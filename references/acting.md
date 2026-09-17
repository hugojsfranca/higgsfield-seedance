# Acting: directing performance in a Seedance prompt

Read this for any shot where people act, react or speak. It's adapted from Higgsfield's ACTING SYSTEM guide for Seedance 2.0. The main changes for this plugin:
- acting is scaled to what a 4–15 s clip can show;
- face and eye acting is kept for faces the frame can actually read;
- dialogue is fitted to generated lip-sync;
- voices are handled the way the CLI works.

## Contents

- [The core idea](#the-core-idea)
- [Plan the psychology, write the behaviour](#plan-the-psychology-write-the-behaviour)
- [How much acting a clip holds](#how-much-acting-a-clip-holds)
- [Act for the frame you have](#act-for-the-frame-you-have)
- [The body](#the-body)
- [Business and the interrupted action](#business-and-the-interrupted-action)
- [Distance and status](#distance-and-status)
- [Listening and reacting](#listening-and-reacting)
- [Eye life](#eye-life)
- [States, not transitions](#states-not-transitions)
- [Dialogue and voice](#dialogue-and-voice)
- [Ensembles](#ensembles)
- [The character acting profile](#the-character-acting-profile)
- [Rewriting the profile into a clip](#rewriting-the-profile-into-a-clip)
- [Worked example](#worked-example)
- [Failure atlas](#failure-atlas)
- [Self-check](#self-check)

## The core idea

Acting is behaviour under pressure, not a display of emotion. A person wants something from someone, something is in the way, and they act to get it. The emotion is a by-product of that struggle. The model renders what bodies do, so a prompt that names a feeling ("she looks nervous") gets a generic face. A prompt that names the behaviour ("her thumb works at the strap of her bag; she answers a beat too fast") gets a person.

## Plan the psychology, write the behaviour

Work out five things for every character in the shot. They are the writer's tools and belong in the bible or the shot notes, not in the prompt:

| Tool | Question | Example |
|---|---|---|
| **Objective** | What do they want from whom, right now? A verb, never a state. | "get him to take the night shift" (not "be frustrated") |
| **Obstacle and stakes** | What's in the way, and what happens if they fail? | he's already refused twice; if he says no, she works it herself |
| **Tactic** | How are they trying, right now? Change it when it fails. | plead → shame → bargain |
| **Beat** | How long does one tactic last? A beat ends when the tactic succeeds, fails, new information lands or power shifts. | one beat per timed segment |
| **Subtext** | What they mean versus what they say | "Fine." means "we're done talking" |

Then translate each one into something a camera can see: posture, tempo, breath, hands, gaze target, distance, the line itself. Only the translation goes into the prompt. Every beat change has to be visible as a pause, a change of posture, a change of tempo, a new gaze target or a change of distance.

## How much acting a clip holds

Seedance reliably delivers about one main action per 4 s (prompt rule 2), and segments shorter than about 2 s get merged or dropped. Scale the performance to the clip:

| Clip | Performance it can carry |
|---|---|
| 4–5 s | One state, plus at most one small timed change: a stop, a look, one breath, one short line |
| 6–8 s | Two beats: one visible shift between them |
| 10–15 s | Two or three beats, each under its own timestamp |
| 15–30 s, several shots | One beat per shot segment |

A per-clip performance paragraph runs about 30–80 words. The full character profile (below) stays in the bible. Pasting it whole into a short clip asks for more beats than the clip can show.

## Act for the frame you have

What the model can render depends on how big the face is.

- **Readable face** (at least ~8% of frame height, turned no more than ~45°): face and eye acting are available. On Higgsfield these shots usually route to Seedance 2.0, because 2.5 refuses most readable faces in reference and start frames (see *Faces* in the prompt skill).
- **Small, turned, lowered or seen from behind:** act with the body only. Use centre of gravity, tempo, business, distance and silhouette. Eye-life lines here are wasted words.
- **The tighter the shot, the less movement.** In a close-up, give the eyes and one small physical detail, not gestures.

## The body

Set these for every character. They read at any size.

- **Centre of gravity:** high (chest and chin up: confidence, aggression, status) or low (shoulders dropped, slouch: fatigue, fear, submission).
- **Tempo:** quick and ragged (nerves) or slow and economical (control). The most dangerous person in a room usually moves least.
- **Openness:** squared shoulders and open hands, or crossed arms and a dropped head.
- **Breath:** high and fast, or low and slow. Match it to what just happened: someone who has run can't speak in a steady voice.
- **Biography:** age, build and posture should tell the backstory, such as a dockworker's forward-rolled shoulders or an officer's over-corrected spine.

## Business and the interrupted action

Give almost every character a physical task: coiling a cable, counting stock, wiping a counter. Business keeps hands truthful, fills pauses and leaks subtext (how someone counts money says more than what they say).

**The interrupted action is the strongest accent.** A character who stops the task on a line turns that line into an event. Make the stop a single timed moment ("at about 3 s the cloth stops mid-wipe"). When the edit keeps only a short window of the clip, time the stop inside that window.

## Distance and status

- **Distance is the relationship.** Intimate is under 0.5 m, personal 0.5–1.2 m, social 1.2–3.5 m, public beyond that. Give it in metres (shot direction: measurable blocking). A change of distance is a change of beat, and needs a reason: toward something or away from something.
- **Status is behaviour.** High status is a still head, slow movement, long looks, pauses before answering, taking up space. Low status is fidgeting, touching one's own face or hair, quick glances for permission. The strongest moments are status breaks: the boss who flinches for one beat, the junior who stops smiling.
- **Motivated moves** that read on screen: closing in, turning away, standing while the other sits, sitting down mid-conflict, stopping in a doorway, starting to pack up.

## Listening and reacting

The performance lives between the lines. Write the listener, not just the speaker:

- **The reaction starts before the other line ends.** The listener's face or body already answers, timed inside the speaker's segment.
- **Thought before word.** A short visible pause before a hard answer: a breath, a glance down, the business stopping.
- **The assessment moment.** When news, a threat or an insult lands, give it time: a held look, a slow blink, an exhale.
- **Answer the energy.** Loudness is met with louder or with pointed quiet. It's never ignored.

## Eye life

Only for readable faces. Dead, fixed eyes are the clearest tell of generated acting.

- **Give the gaze targets,** and let it move between them: the other person's hands, their face, the door. Name each target; never the camera (the linter flags camera-gaze wording).
- **Blinks follow state:** quick bursts under stress, slow lids in control, a long blink on a decision.
- **The eyes lead.** They reach the target a moment before the head turns.
- **Stillness is a choice:** a character who barely blinks still shifts their gaze slowly and deliberately.

## States, not transitions

Video models render states well and processes badly. Write the character already in the action ("mid-stride", "arm already raised with the rope") rather than the process of getting there ("reaches into the bag, pulls out the rope, lifts it"). This is the same idea as prompt rule 14: the first visible frame already contains the person in position, mid-action. Chain states beat by beat under timestamps. A single discrete change, such as a stop, a turn of the head or one step, is fine when it's timed.

## Dialogue and voice

- **Quote the exact line** and keep to about 2–2.5 words per second of its window (prompt rule 6). Rough, natural speech ("Look — I can't, alright?") goes inside the quotation marks, where the model will say it word for word.
- **One speaker at a time.** Overlapping lines lip-sync badly. Write "only her lips move for the line; he listens" and give the listener a reaction instead.
- **Quiet is stronger than loud.** The character who owns the scene lowers their voice.
- **A pause needs content:** an assessment, a decision, the business stopping. Otherwise cut it.
- **Voice line:** give each speaking character one locked voice description in the bible (formula below) and paste it word for word into the audio part of every clip where they speak. Leave it out when they're silent. A text description narrows the voice but doesn't guarantee the same voice across clips. When continuity matters, pass the same recording with `--audio-references` on every clip, or record the lines in post (see *Faces* in the prompt skill).

Voice line formula, one or two sentences:

```
[Age]-year-old [origin or accent]. [Timbre and register]; [pace and delivery]; [how it shifts under pressure].
```

## Ensembles

- **Reactions travel in a wave.** One person reacts first, the next half a second later, a third barely. Give the first two or three reactors their own times ("at 2 s the woman at frame left looks up; at 2.5 s the man beside her"), and let everyone else keep their business or hold still. Identical simultaneous reactions look fake, and it's hard to keep more than one mover per beat under control (prompt rule 10).
- **The reaction is worth more than the action.** After an event, the most valuable frame is the face of whoever saw it.
- **Freeze at the threat.** Constant small background movement that stops all at once is strong punctuation.
- **The strong are still and quiet; the weak fidget.** Tension is played by the people around the dangerous one.
- **Wear accumulates.** A character worn down across a film carries it forward: heavier, slower, greyer. They don't reset between scenes.

## The character acting profile

Every recurring character who acts gets one profile in the bible, next to their wardrobe line. It's the permanent source of truth about how they behave. Keep it to about 80–130 words of observable behaviour, in this order:

```
[NAME] acting profile. [Age, build and posture as biography]. [Engine: the drive behind the physicality, one clause].
Signature tic: [tic] when [trigger]. Stress tic: [tic] when [trigger]. Mask: [default face or manner];
it cracks when [trigger]: [what changes in posture, face, tempo]. Gait: the "[named walk]", [weight, step,
torso, arms]. Softens only for [one person, animal or thing].
```

- **Only observable behaviour.** Every inner state gets a body marker.
- **Every tic has a trigger.** A tic without one is decoration.
- **Name the gait** in quotes, then unpack it: weight, step length, torso, arms.
- **Mask and crack:** every profile carries one "it cracks when…" clause. Playing two truths at once is what separates a person from a puppet.
- **One softening target at most.**
- **No wardrobe, camera, colour or light.** Those live in the bible's wardrobe line and in each shot. The profile has to survive a costume change.
- **Voice** is kept separately, as the voice line.

## Rewriting the profile into a clip

The profile is who the character is. Each clip gets a rewrite, never a paste:

1. **Only characters in frame** get performance text.
2. **Keep the constant core:** the same tics with the same triggers, the same gait, the same voice line.
3. **Pick what this clip can show** (see *How much acting a clip holds*) for this posture, action and beat.
4. **Transform, don't delete.** A pacer who is seated keeps the restless energy in a foot, a pen or a cuff.
5. **Write it as prose inside the timed segments,** attached to the person's description or `@Image N` anchor line. No bullet lists or headers inside the prompt.

## Worked example

An invented character, written the way the bible holds her:

```
ODILE acting profile. Late fifties, compact and broad through the shoulders, weight carried low and wide
after thirty years on a moving deck; knees stay soft even on dry land. Engine: she keeps things running and
trusts nobody else to. Signature tic: two fingers tap on the nearest rail or table edge while she listens,
faster as her patience runs out. Stress tic: she tugs her cuff down over her watch when the schedule slips.
Mask: a flat, squinting, unimpressed face; it cracks when someone younger thanks her: the squint drops, she
looks out at the water and busies her hands. Gait: the "deck roll", short planted steps, arms slightly out
from the body, torso level while the hips take the sway. Softens only for the ferry's old dog.
```

Voice line: `A woman in her late fifties with a coastal working accent. Low, dry and clipped; short sentences with pauses where others would argue; she gets quieter, never louder, when she means it.`

**Clip 1: readable face, Seedance 2.0, 6 s.** Lint with `--model seedance_2_0 --duration 6`.

```
Late afternoon on the open car deck of a small ferry. A deckhand in her late fifties, weathered skin, grey
hair tied back under a navy knit cap, orange work jacket, stands at the steel rail at frame left, torso
turned toward a young crew member at frame right, 1.5 metres from her. Single continuous take. 29° diagonal
field of view, camera 4 metres away at shoulder height, framing her from the waist up, her face about a
fifth of the frame height; the young man is soft in the foreground at frame right, seen from behind.
0–2 s: The first visible frame already contains both of them in position. He is mid-sentence, hands open.
Her eyes stay on his hands, then lift to his face before he finishes; two fingers tap slowly on the rail.
2–4.5 s: The tapping stops. One slow breath through the nose. She says: "Then you'll do the ropes yourself."
Only her lips move for the line; he stays silent. Her line must finish before the video ends.
4.5–6 s: Her gaze moves out to the water, one slow blink, her hand resting flat on the rail. The take ends
held on this frame.
Low sun from frame right behind her puts a rim of light along her cap and shoulder; the side of her face
toward the camera stays in soft shade; no flat front light. Sound: engine hum, gulls, water against the
hull. Her voice: a woman in her late fifties with a coastal working accent, low, dry and clipped, quieter
when she means it. No music, no subtitles.
```

What the rewrite did:
- **Beats:** the 6 s hold two beats (listening, then refusing), each on its own timestamp.
- **Interrupted action:** the tapping stops on the line.
- **Eye life:** the eyes lead the thought (hands, then face, then water), because the face is readable.
- **Voice:** the voice line sits in the audio part of the prompt.
- **Left out:** the gait, which a standing shot can't show.

**Clip 2: small figure, Seedance 2.5, 4 s.** Lint with `--duration 4`.

```
A ferry car deck at dusk. Single continuous take, 63° diagonal field of view, camera fixed 12 metres behind
her at head height. The first visible frame already contains a deckhand in an orange work jacket and navy
knit cap, small in frame at the centre, seen from behind, mid-stride as she walks away from the camera
toward the loading ramp.
0–4 s: She walks with short planted steps, arms slightly out from her body, torso level while her hips take
the sway of the deck. At about 2 s, without breaking stride, she pushes a loose coil of rope straight with
the side of her boot. The clip ends with her smaller in frame, still walking.
Warm dusk light from frame right throws long shadows toward frame left. Sound: engine hum and water. No
music.
```

Here the face is never readable, so everything is body: the named gait unpacked, and one timed piece of business. There's no eye life.

## Failure atlas

| Symptom | What it looks like | Fix in the prompt |
|---|---|---|
| Indicated emotion | Brows and grimaces "showing" a feeling | Remove the feeling word; write the objective's behaviour and give the hands business |
| Playing the ending | The character acts the outcome from the first frame | Write only what they know at each timestamp |
| Waiting for the cue | A blank face while the other person talks | Time the listener's reaction inside the speaker's segment |
| One tactic throughout | All pleading, or all shouting | A new visible tactic at each beat |
| Gesture illustrates the word | "Big" with arms spread | Gesture before the thought, against the words, or none |
| Emotion from nowhere | Tears or rage with no trigger | Build restraint first, then the break, on its own beat |
| Body false to biography | A labourer with a dancer's posture | Set centre of gravity, tempo and wear in the profile |
| Too clean to be real | Polished sentences from a rough character | Roughen the quoted line itself |
| Signalled threat | Menacing pauses and slow turns | Keep it mundane; no wind-up |
| Synchronised crowd | Everyone reacts at once | Stagger two or three reactors with times |
| Empty pause | Silence where nothing happens | Fill it with an assessment or business, or cut it |
| Instant recovery | Composure snaps back after a blow | Carry the state into the next beat |
| Busy close-up | Big facial movement in a tight shot | Eyes and one small detail only |
| Dead eyes | Fixed stare, no blinks | Eye-life lines, for readable faces |
| Too many beats | Four tactic changes in a 4 s clip | Scale to the table above |
| Psychology in the prompt | "She wants him to feel guilty" | Keep it in the notes; write the behaviour |
| Eye detail on a wide | Blink and catchlight lines on a small figure | Act with the body instead |
| Overlapping dialogue | Two mouths moving at once | One speaker per beat; the other reacts |

## Self-check

Before a shot with people ships:
- [ ] Each character in frame has a planned objective and obstacle, translated into behaviour. No emotion words left (the linter flags common ones).
- [ ] The beat count fits the duration, and each change is visible and timed.
- [ ] Every character has business or a clear physical state; any interrupted action is timed.
- [ ] Distances are in metres, and every change of distance is motivated.
- [ ] Listeners react inside the speaker's segment.
- [ ] Eye life is written only where the face is readable, with named gaze targets.
- [ ] States, not transitions: everyone is already mid-action in the first frame.
- [ ] One speaker per beat. Lines are quoted and within the word budget. The voice line is pasted for anyone who speaks.
- [ ] Tics keep their triggers, and the mask has its crack.
- [ ] No wardrobe, camera or colour inside the performance text.

Scale: 0 is a mannequin (words, no behaviour); 2 has a guessable objective but one tactic and late reactions; 3 listens and changes beats; 4 is alive, with continuous behaviour, contrasting tactics, subtext and reactions ahead of lines; 5 plays two truths at once (apologises and defends, helps and resents). Aim hero shots at 4 or above, and rewrite anything at 2 or below.
