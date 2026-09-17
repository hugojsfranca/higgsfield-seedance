# Seedance 2.5 prompt patterns

Five patterns cover most 15–30 s jobs. Pick one, then adapt the worked example: keep its structure and replace its content. Each example lists the Higgsfield settings it assumes.

## Contents

- [Picking a pattern](#picking-a-pattern)
- [1. Beat-synced match-cut](#1-beat-synced-match-cut)
- [2. Single-throughline educational](#2-single-throughline-educational)
- [3. Timestamped tutorial](#3-timestamped-tutorial)
- [4. Commercial with @Video dynamics references](#4-commercial-with-video-dynamics-references)
- [5. Continuous-shot chapters](#5-continuous-shot-chapters)
- [Regrouping attribute-block prompts by time](#regrouping-attribute-block-prompts-by-time)
- [Camera language](#camera-language)

## Picking a pattern

| The brief | Pattern |
|---|---|
| Brand or product film, one hero object, music-driven | 1. Match-cut |
| A topic across eras, stages or places, linked by one object | 2. Throughline |
| How-to, installation, product guide, steps with narration | 3. Tutorial |
| Commercial where reference clips set camera, impact or type motion | 4. Commercial with @Video |
| One camera, one protagonist, chapters that change mood or style | 5. Continuous shot |
| Two fixed frames, get from A to B | `first-last-frame.md` |

---

## 1. Beat-synced match-cut

One subject stays fixed dead-center and razor-sharp for the whole film while the background swaps on every heavy beat. Give each scene one line: setting, light, and the single thing happening. End on a finale accent and a quoted logo card.

Here the music does the pacing, so numbered scenes can stand in for timestamps. This only works with a music reference (`--audio-references`) or generated audio on.

*Settings: `omni_reference`, 1 image (the engraved logo), 1 audio (the BGM), 20–30 s.*

```
A fast-paced, cinematic match-cut short film synchronized to a dynamic electronic beat.
A flawless crystal ball remains fixed dead-center in frame throughout, with a glowing
"seedance" logo engraved inside (reference @Image 1). The crystal ball stays in
razor-sharp focus while backgrounds seamlessly switch at high speed on every heavy beat:
Scene 1: Macro close-up. Cinematic water splashes around the crystal ball, refracting
complex light patterns.
Scene 2: Morning vintage café. The ball sits on a raw wood tabletop, backed by rising
coffee steam and a blurred stream of commuters outside the window.
Scene 3: Evening golden hour. A skater youth tosses and catches the ball one-handed,
streetscape rushing backward, stunning sunset backlighting.
Scene 4: Frenzied music festival. A hand raises the ball high, refracting stage lasers.
Scene 5: Family party dinner table. The ball rests at center, blurred figures clinking
glasses and reaching for food.
Scene 6: Dim movie theater. Two hands cradle the ball as faint screen light flows
across its surface.
Scene 7: The ball sits atop a heavily vibrating speaker diaphragm, then transitions on
the musical climax to the spinning center of a DJ turntable.
Scene 8: Outdoor camping night. Warm campfire glow and swaying string-light bokeh.
Toss finale: On the final musical accent, the ball is tossed high above the frame.
Instant cut to pure black — a minimalist white-on-black "seedance" appears at center
(reference @Image 1). The take ends held on this frame.
Beat-synced editing tightly locked to the BGM rhythm (BGM references @Audio 1).
Top-tier cinematic color grading. Photorealistic glass refraction and transmission
materials, complex ray tracing, global illumination. Subject in razor-sharp focus,
backgrounds with intense motion blur — maximum visual impact.
```

---

## 2. Single-throughline educational

One object travels the whole film and links every scene. Each era gets its own art style anchored by a reference, and short quoted voiceover lines carry the facts. Without quoted lines the model invents the narration.

*Settings: `omni_reference`, 3 style images, generated audio on, 30 s.*

```
A 30-second educational short about the 3,000-year evolution of football. A single
ball is the visual throughline — it rolls, travels and transforms, linking
civilizations and eras. Tight pacing, premium visuals.
0–5s: An ancient ball emerges slowly from black, its surface worn with age. It rolls
into a Warring States period courtyard in China, ink-wash painting style (reference
@Image 1); figures in ancient robes play cuju, the ball bouncing at their feet.
Voiceover: "Three thousand years ago, China played cuju."
5–10s: The ball rolls forward into an ancient Greek plaza, classical oil-painting style
(reference @Image 2) — stone columns, robed players kicking the ball.
Voiceover: "Greece had its own ball games."
10–15s: Medieval Europe, the oil-painting style held — a muddy village square, common
folk chasing a leather ball, lively and raw. Voiceover: "Medieval villages played rough."
15–21s: The ball is kicked forward and the image switches to black-and-white
documentary style (reference @Image 3). England, 1863 — gentlemen, clubs, a grass
pitch; the ball takes its standard modern shape for the first time.
Voiceover: "In 1863, England wrote the rules."
21–26s: The modern era arrives fast, in full color: the ball spins in the air as
floodlights, stadiums, crowds and trophies interweave.
26–30s: The ball comes to rest at center field in a packed modern stadium, crowd noise
swelling. On-screen text: "One ball, connecting the world." The take ends held on this
frame.
Voiceover concise and measured. The voiceover must finish before the video ends.
Grand, epic scale; each era's style holds until the ball carries us out of it.
```

---

## 3. Timestamped tutorial

This is the strictest structure, built for product guides and how-tos. Each step gets one action, one voiceover sentence, and any on-screen text in quotes. The Requirements lines protect the details the viewer must see.

*Settings: `omni_reference`, 1 product image, generated audio on, 30 s.*

```
A 30-second tutorial video on the installation and use of a capsule coffee machine
(machine references @Image 1).
0–2s | Opening title text: "seedance Capsule Coffee Machine Installation and User Guide"
2–5s | Step 1: Installing the Water Tank
Shot: Medium shot, slight high-angle. Position: back of the machine.
Action: Align the water tank with the slots, push straight down until it clicks locked.
Requirements: clearly show the tank's bottom clips aligning with the slots; the water
level line visible through the transparent tank.
Voiceover: "First, install the water tank until it clicks."
5–9s | Step 2: Installing the Drip Tray
Shot: Close-up, front view. Action: slide the tray into the bottom rails until flush.
Voiceover: "Next, slide the drip tray into the bottom rails."
9–13s | Step 3: Installing the Used Capsule Container
Shot: Close-up, slight low-angle. Action: align with the grooves, push flush.
Voiceover: "Then, insert the used capsule collection container."
13–18s | Step 4: First-Time Water Filling
Shot: Close-up, side profile. Action: open the lid, pour clean water to the MAX line.
Requirements: highlight the water level indicator; pouring clearly visible.
Voiceover: "Pour clean water up to the MAX line." (On-screen graphic highlights MAX.)
18–25s | Step 5: Powering On
Shot: Medium, front. Action: plug in, press power; indicator goes flashing → solid.
Voiceover: "Press power. A solid light means it's ready."
25–30s | Step 6: Initial Flushing — No Capsule
Shot: Medium to close-up, front-side; cup under the spout. Action: press extract with
the capsule slot empty; hot water flushes the pipes into the cup. On-screen text:
"No capsule needed". The take ends held on the full cup under the spout.
Voiceover: "Press extract without a capsule for the first flush."
Voiceover calm and clear, one sentence per step. The voiceover must finish before the
video ends.
If this description and the reference image disagree about the product, THE REFERENCE
IMAGE WINS.
```

---

## 4. Commercial with @Video dynamics references

Reference clips carry composition, camera dynamics, impact feel and text motion, and each one is named at the moment it applies. Only call out clips that are actually attached, in attachment order.

*Settings: `omni_reference`, 1 image, 5 videos, generated audio on, 15–20 s.*

```
Bright and colorful commercial style — fruit-flavored cookies as the star: strawberry,
apple, grape, and orange. Strawberry flavor references @Image 1. Cookies and their
fruits arranged in highly ordered geometric arrays; clean, premium, rhythmically driven.
The opening quickly establishes visual focus with fruit, referencing the composition of
@Video 1, with the music dropping on the downbeat. Different flavored cookies line up
in neat formations, cutting to close-ups, referencing the dynamics and camera movement
of @Video 2. At the climax, a cookie is snapped in half — instantly entering slow motion
as the fruit filling bursts open, crumbs scatter, juicy impact and particle explosion
amplified, referencing the impact feel of @Video 3. A horizontal array creates a rhythmic
parabolic motion, referencing the movement in @Video 4, then returns to fast-paced
editing. Ending text "One bite of crispness, a heart full of delight" — words split and
cut into frame in rapid succession with strong rhythmic text motion and a product
freeze-frame, referencing @Video 5. Final brand moment: cookies and fruit disperse
outward in all directions — youthful, energetic, share-worthy.
```

---

## 5. Continuous-shot chapters

State the single-camera rule in the first sentence. Split the film into roughly 5 s chapters; each gets a theme, a style (which may change mid-chapter) and one event. End on a snap.

The protagonist is written in words, not wired from a photo (see *Faces* in the prompt skill), and is kept mostly in profile or from behind, which also makes the final frame safe to chain from.

*Settings: `omni_reference`, 7 images, generated audio on, 30 s.*

```
One continuous shot — the camera steadily follows a slim person in a long black wool
coat and black boots, short dark hair, seen in profile and from behind, moving left to
right through six interconnected rooms, each a different color tone and atmosphere.
Every room shares the same structure: white walls, herringbone wood flooring, French
floor-to-ceiling windows, white sheer curtains (reference @Image 1), but the view
outside and the atmosphere change completely. The protagonist walks at a constant pace
through each open doorway; the black coat stays the same in every room.
0–5s, Room One — American comic-style fight. The protagonist engages a caped comic
villain (reference @Image 2); the opponent is defeated.
5–10s, Room Two — warmth, felt-craft style. Sunflower field outside (reference
@Image 3); a painter works at an easel on a sunflower painting (reference @Image 4). As
the protagonist enters, they too transform into felt-craft style.
10–15s, Room Three — sadness, black-and-white stop-motion. Rain outside; a person sits
alone hugging their knees, a phone glowing with an unanswered call. The protagonist
switches the light off — then on: the room bursts into full color, flowers blooming to
fill the space.
15–20s, Room Four — joy, underwater room (reference @Image 5). The protagonist swims
in among coral reefs and schools of fish.
20–25s, Room Five — surprise. Fireworks fill the night sky outside (reference
@Image 6); colorful reflections dance across the room.
25–30s, Final Room — completely blank white. The protagonist stands at center and snaps
their fingers — crisp snap SFX — cut to black, the word "seedance" at center
(reference @Image 7). The take ends held on this frame.
```

---

## Regrouping attribute-block prompts by time

Many house prompt formats list each attribute once for the whole clip, with every shot inside it. The model then has to line up "second item under CAMERA" with "second item under ACTION", and it often doesn't. Regroup the same content under timestamps, and turn the Negatives section into positive statements inside the segments where they apply.

**Before (attribute blocks):**

```
Shot Breakdown
0:00 to 0:01.5: Coffee cherries on the branch
0:01.5 to 0:03: Beans roasting
0:03 to 0:04: Espresso pouring
CAMERA: 100 mm macro; 50 mm overhead; 85 mm side profile.
LIGHTING: Soft morning sun; orange drum glow; warm café tungsten.
ACTION: A hand picks a red cherry; beans tumble in the drum; crema forms in the cup.
TRANSITION: Match the cup's rim to the circular logo in Scene 2.
Negatives: No logos, no fake brands, no CGI steam, no plastic cups.
```

**After (grouped by time, positives only, self-contained):**

```
A 10-second origin-to-cup sequence, three shots, warm and tactile.
0–3s: 100 mm macro on a coffee branch in soft morning sun; a hand picks one ripe red
cherry, dew on the skin.
3–6s: 50 mm overhead into a roasting drum lit by an orange glow; the beans tumble and
darken from green to deep brown.
6–10s: 85 mm side profile in warm café tungsten light; espresso pours into a plain white
ceramic cup and a golden crema forms; natural wisps of steam. The final frame holds on
the round rim of the cup, centered. The take ends held on this frame.
All surfaces unbranded: plain drum, plain white ceramic cup.
```

The segments grew from 1–1.5 s to 3–4 s (the clip grew to 10 s to make room), the cross-clip TRANSITION became a described final frame, and the Negatives became "unbranded, plain, ceramic" statements.

---

## Camera language

| Term | Meaning |
|---|---|
| Push in / Pull back | Camera moves toward / away from the subject |
| Pan / Tilt | Horizontal / vertical rotation |
| Track / Follow shot | Camera follows the subject's movement |
| Orbit | Camera circles the subject |
| One-take / Oner | Continuous shot, no cuts |
| Locked-off / Fixed | No camera movement at all |
| Hitchcock (dolly) zoom | Push in while zooming out; vertigo effect |
| Whip pan | Very fast pan with motion blur |
| Bird's eye / Overhead | Straight-down view |
| First-person POV / FPV | Subjective camera; an FPV "shuttle" suits time/space transitions |

Shot sizes: extreme close-up · close-up · medium close-up · medium · full shot · wide/establishing. Lens lengths (28 mm, 50 mm, 85 mm, 100 mm macro) are understood and are a compact way to set both framing and compression.
