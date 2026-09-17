# Image prompts on Higgsfield

Models, rules, building blocks and templates for stills: character references, location plates, props, Seedance keyframes and image edits. Adapted from Higgsfield's LIRA image-prompt guide. The model table and prices were checked against the CLI (`higgsfield model get`, `higgsfield generate cost`) in September 2026, and the rules are reconciled with what the Seedance clips need from their stills.

## Contents

- [Models on the CLI](#models-on-the-cli)
- [Routing](#routing)
- [Rules for generation prompts](#rules-for-generation-prompts)
- [Building blocks](#building-blocks)
- [Templates](#templates)
- [Edits](#edits)
- [Checklist](#checklist)
- [Unverified](#unverified)

## Models on the CLI

Prices are `generate cost` estimates from one account in September 2026; plans can differ, so always price before running.

| Model (`job_type`) | References | Aspect ratios | Size flag | Credits | Best for |
|---|---|---|---|---|---|
| Soul 2.0 (`text2image_soul_v2`) | 1 image, or a Soul ID via `--soul-id` | 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3 (**no 21:9**) | `--quality 1.5k` or `2k` | ~0.12 | Characters, portraits, casting, fashion and UGC looks |
| Soul Cinematic (`soul_cinematic`; "Soul Cinema" in the web app) | 1 image, or `--soul-id` | as Soul 2.0 **plus 21:9** | `--quality 1.5k` or `2k` | ~0.12 | Cinematic stills and mood frames, 21:9 plates, a Soul ID character inside a scene |
| Soul Location (`soul_location`) | none (prompt only) | as above plus 21:9 and 9:21 | none | ~0.12 | People-free locations and environment plates |
| Soul Cast (`soul_cast`) | none; prompt optional, `--budget` | 16:9 only | none | ~0.12 at budget 50 | A quick invented persona (the web app's AI Cast) |
| Nano Banana Pro (`nano_banana_pro`) | up to 14 images | all common plus 21:9, 4:5, 5:4 | `--resolution 1k`/`2k`/`4k` | 2 (4 at 4k) | First choice for edits; reference-driven keyframes and views; props with legible text |
| Nano Banana 2 (`nano_banana_flash`) | images; inpaint with `--is_inpaint` and a mask | as Pro plus `auto` | `--resolution` (default 1k) | 1.5 (2 at 2k) | Cheap reference-driven drafts and views |
| Seedream 4.5 (`seedream_v4_5`) | up to 14 images | 1:1, 4:3, 16:9, 3:2, 21:9, 3:4, 9:16, 2:3 | `--quality basic` or `high` | 1 | A texture pass on a finished still |
| GPT Image 2 (`gpt_image_2`) | images; inpaint with a mask; `--background transparent` | all common plus `auto` | `--quality low`/`medium`/`high`, `--resolution` | 6.5 (high, 2k) / 2 (medium) / 0.5 (low, 1k) | Exact objects, structure and typography; new views of a location; a last-resort local fix |

Newer models also appear in `higgsfield model list` (GPT Image 2.5, Seedream 5.0 Lite and Pro, Nano Banana 2 Lite). They haven't been tested for this workflow, so check `model get` and run one test before routing work to them.

## Routing

| Task | Model | Notes |
|---|---|---|
| Invented character, master portrait | Soul 2.0, or Soul Cinematic for a film look | Approve it before making anything else of that character |
| A real person the user has rights to (themselves, a consenting presenter) | Soul ID: `higgsfield soul-id create --name <name> --soul-2 --image <5–20 photos>`, then `--soul-id <id>` | Only with the person's consent. Soul IDs are per model (`--soul-2` or `--soul-cinematic`) |
| Quick invented persona to cast from | Soul Cast | 16:9 sheet; use it to explore, then make a master portrait |
| More views of an approved character | Nano Banana Pro with the portrait as `--image-references` | Soul models take one reference; to hold a face there, use a Soul ID |
| Location plate with no people | Soul Location | Prompt only, cheap; add people afterwards with Nano Banana Pro using the plate as a reference |
| Cinematic frame, 21:9, or a Soul ID character in a place | Soul Cinematic | One reference image at most |
| Prop or product | GPT Image 2 (exact geometry, lettering) or Nano Banana Pro | Neutral surface, stated positively |
| Seedance keyframe built from references | Nano Banana Pro at 2k | Same price as Nano Banana 2 at 2k; use Nano Banana 2 at 1k for cheap drafts |
| Any edit of a finished still | Nano Banana Pro first | See [Edits](#edits) |
| Tired, plasticky AI textures | Seedream 4.5 texture pass | Not for moving or replacing things |
| A tiny local fix Nano Banana Pro couldn't make | GPT Image 2, ideally with a mask | Keep the change as small as possible |
| Reverse angle or new view of a location | GPT Image 2, or Nano Banana Pro with every object's new side written out | Reverse angles swap every frame side |
| The still needs rebuilding | Regenerate it; don't edit | |

## Rules for generation prompts

1. **Prose, not keyword stacks.** "Masterpiece, 8k, trending" does nothing. Write one coherent description of the scene. CAPS blocks belong only in edit prompts.
2. **Tight beats long.** 80–150 words for a simple still. With bible lines and a shared framing spec, stay under about 330 words (about 2,000 characters). Past that, details drop out. Keep a style prefix to one register line, not a paragraph of quality boilerplate.
3. **Say what's there.** No image model here has a negative-prompt field, and "no people" summons people. Write "empty deserted deck, still air". Edit prompts are the exception: "remove the lamppost" works, as long as it's paired with what fills the gap.
4. **Settings are flags.** Aspect ratio, resolution and quality go on the command, never in the prose ("16:9", "4K", "--ar"). Composition words like "wide panoramic frame" are fine.
5. **Technical light and real materials.** Name the source, its direction, the ratio or falloff and the colour temperature ("soft key from frame left at 45°, gentle falloff into shadow"). Name the material and its finish ("worn grey painted steel", "oxidised copper").
6. **Palette in proportions.** "About 60% steel grey, 30% sea blue, 10% warm orange." Take the split from the brief, the scene or the user's references, and never invent one over them.
7. **Composition.** Rule of thirds is a good default for single stills. Skip it when the composition is already specified: centred match-cut geometry, symmetrical overheads, space reserved for type, screen plates, sheets.
8. **Camera in plain words.** "Camera high above the room, looking diagonally down at 45°" beats CCTV or fisheye jargon. For a Seedance keyframe, also give the clip's diagonal field of view, camera distance and height, because the video starts from this frame and must keep the same field of view. Keep shallow-focus and bokeh language for people and objects; empty plates stay deep and readable.
9. **Photoreal anchors.** "Photograph", "cinematic film still", real camera and film-stock register, real materials. "Painterly", "concept art", "illustration" and "reference sheet" pull toward drawings. Fix drift by strengthening the photo anchors, not by adding "not a cartoon".
10. **Text.** Put the exact words in quotes with font, weight and colour ("the sign reads 'PIER 4' in bold white condensed sans-serif"). Text that must be exactly right in the final film is safer added in post.
11. **People.** Identity comes from a Soul ID or a reference image; prose only reinforces it (same wardrobe line, same marks). Never name a real person; describe features.
12. **Brands.** No product brands, logos or IP. Camera and film-stock names used as a look register (a cinema camera, a film stock) are fine in stills. In video prompts, lenses are still directed by field of view.
13. **Stills for Seedance clips:**
    - Keep readable faces small, lowered or turned in any frame that starts a Seedance 2.5 clip.
    - Put people already mid-action (states, not transitions; see `acting.md`).
    - Write every keyframe as if it were the only prompt: no asset IDs, no "same as the previous image".
    - Copy shared framing specs word for word.
    - Keep screens as plain dark glass with a soft even glow.
14. **One photograph per prompt,** unless a multi-panel approval sheet is the goal. Seedance references and keyframes are always single images.

## Building blocks

Keep these identical across a project so the stills match each other.

**Register lines (pick one per project).** Soul models already carry film texture, so keep the line short there.
- Film grain: `Photorealistic cinematic film still, large-format digital cinema camera with anamorphic lenses, fine 35mm film grain, soft highlight roll-off.`
- Clean modern: `Clean modern digital cinema capture, crisp natural detail, minimal grain, true-to-life colour, medium contrast.`
- Commercial realism: `Live-action commercial photograph at a real working location, natural directional light, authentic textures and everyday wear.`

**Palette line:** `Palette of about 60% [dominant], 30% [secondary], 10% [accent]; [restrained grading, soft contrast, deep blacks].`

**Style anchor:** one at most, as mood ("naturalistic light in the manner of Roger Deakins"). Drop it if it pulls a look you don't want. A list of cinematographers adds noise.

**Positive rewrites:**

| Instead of | Write |
|---|---|
| no people | empty deserted deck, still air |
| no acne | clean dry skin |
| no logos | plain unbranded surfaces, blank matte labels |
| not cartoon | photograph, real materials, natural light |
| no text on the truck | plain unlettered white trailer |

## Templates

Aspect ratio and size are flags on every one of these. Lint generation prompts with `preflight.py --image`, sheets with `--image --sheet` and edits with `--image --edit`.

### Master portrait: Soul 2.0 or Soul Cinematic

`[subject: age, build, face features, hair, one mark] + [wardrobe line from the bible] + [plain background] + [framing and pose] + [light] + [texture] + [palette] + [register]`

```
Studio photograph of a woman in her late fifties with weathered skin, grey hair tied back, deep squint lines
and a small scar through her left eyebrow, wearing an orange waterproof work jacket over a navy knit jumper.
Head and shoulders against a plain mid-grey studio wall, her face three-quarters toward frame left, eyes on a
point just past the left edge of frame. Soft key light from frame left at 45 degrees with gentle falloff into
shadow on the right side of her face, a faint rim on her hair. Natural skin texture and real fabric weave.
Palette of about 60% cool grey, 30% navy, 10% safety orange. Clean modern digital cinema capture, crisp
natural detail, minimal grain.
```

### More views of an approved character: Nano Banana Pro

Attach the approved portrait with `--image-references`. Ask for one view per image, and record each approved view in the manifest as its own file.

```
The woman in the reference portrait, with an identical face, grey hair and scar, shown full length from head
to boots in left profile, standing relaxed with her weight on both feet, wearing an orange waterproof work
jacket over a navy knit jumper, dark work trousers and black rubber boots. Plain mid-grey studio wall, soft
even light from frame left. One single photograph, clean modern digital capture, natural skin and fabric
texture.
```

### Approval sheet: Soul 2.0

For casting and approval only. Never attach a sheet to a Seedance clip, because multi-panel references can come back as multi-panel frames. Once the sheet is approved, generate the single views. The fast path is Soul Cast.

```
Three studio photographs of the same real person side by side on a plain mid-grey backdrop, a film character
sheet: a full-length front photograph on the left, a full-length back photograph in the middle and a close
head-and-shoulders portrait on the right, the same person in all three. A woman in her late fifties with
weathered skin, grey hair tied back and a small scar through her left eyebrow, wearing an orange waterproof
work jacket, navy knit jumper and dark work trousers, identical in all three panels. She stands relaxed
with her arms at her sides in the left and middle panels; in the portrait her face is calm and her eyes are
on a point just past frame left. Soft directional studio light from one side with natural falloff.
```

### Location plate: Soul Location or Soul Cinematic

`[camera position and angle] + [place] + [architecture and materials] + [light: source, direction, temperature] + [depth] + [palette] + [register] + [emptiness, stated positively]`

```
Camera at head height at the stern of a small car ferry, looking forward along the empty car deck toward the
closed bow ramp, 84° diagonal field of view. Worn grey painted steel deck with faded yellow lane lines, white
bulkheads with rust at the seams, coiled mooring ropes on steel bollards along the right rail. Low late
afternoon sun from frame right throws long shadows across the lanes toward frame left and warms the rails.
The deck recedes to the ramp, with the harbour visible above it. Palette of about 60% steel grey, 30% sea
blue, 10% warm gold. Photorealistic cinematic film still. The deck is empty and still, every surface plain
and unlettered.
```

### Seedance keyframe: Nano Banana Pro with references

Order: `register line → camera (field of view, distance, height, side) → who is where, mid-action → bible lines word for word → location in frame terms → light → palette → one image`. Refer to attached references in words ("the woman in the portrait reference"), not by number.

```
Photorealistic cinematic film still. 63° diagonal field of view, camera fixed 12 metres behind her at head
height. The deckhand from the portrait reference, small in frame at the centre and seen from behind,
mid-stride as she walks away from the camera along the car deck toward the loading ramp: a woman in her late
fifties in an orange waterproof work jacket, navy knit jumper and navy knit cap. The car deck from the
location reference: worn grey painted steel with faded yellow lane lines, coiled ropes on bollards along the
right rail, a loose coil of rope on the deck just ahead of her right boot. Warm dusk light from frame right,
long shadows toward frame left. Palette of about 60% steel grey, 30% sea blue, 10% warm orange. One single
photograph.
```

### Prop: GPT Image 2 or Nano Banana Pro

```
Photorealistic three-quarter overhead product photograph of a dented stainless-steel thermos flask with a
worn black rubber grip band and a scratched cup lid, standing on a plain grey concrete surface. Soft
directional light from frame left with a gentle shadow to the right, crisp reflections along the dents.
Plain unbranded steel, blank matte grip band. Clean modern digital capture, true-to-life colour.
```

Separate states (clean, damaged, wet) are separate assets. Describe device-like props by material and function rather than weapon or explosive terms, which can trip safety filters.

## Edits

**Order:**
1. Nano Banana Pro for every edit first.
2. Seedream 4.5 for textures only.
3. GPT Image 2 for the smallest local fix, if Nano Banana Pro couldn't make it.

An edit is post-processing of the original: change the minimum and lock everything else. If the still needs rebuilding, regenerate it instead.

```
Edit the image: [one-line goal].

CHANGE: [the single thing that changes, described precisely].

PRESERVE EXACTLY:
- [face, hair and expression]
- [wardrobe and props, and which hand holds what]
- [pose, positions, camera angle and framing]
- [background, light direction and every existing shadow]
- [colour grade, palette, contrast and grain]

ONLY CHANGE: [the one change]. 100% identical otherwise.
```

Worked example:

```
Edit the image: swap her knit cap for a waxed rain hat.

CHANGE: the navy knit cap on her head becomes a yellow waxed rain hat with the brim turned down at the back.

PRESERVE EXACTLY:
- her face, grey hair, scar and expression
- the orange work jacket and navy knit jumper
- her pose, the camera angle and the framing
- the grey studio wall, the light from frame left and every existing shadow
- colour grade, palette, contrast and grain

ONLY CHANGE: the hat. 100% identical otherwise.
```

- **One change per pass.** If the user says it changed too much, lock more and change less.
- **Removals name the fill:** "Remove the lamppost at frame left; the brick wall continues behind it."
- **Texture pass (Seedream 4.5):** the goal is reviving tired AI textures. CHANGE names the surfaces (skin pores, fabric weave, deck grime), and PRESERVE locks composition, identity, light and grade.
- **GPT Image 2** tends to touch the whole frame, so make its CHANGE as narrow as possible and its PRESERVE list exhaustive. Use a mask when you can (see *Unverified*).
- **A new view of a location** (a reverse angle, say): write every major object's new side, because a reverse angle swaps all of them. "In the main view the bollards are along frame right; in this reverse view they run along frame left, and the bow ramp is now behind the camera, with the stern rail ahead." Without this, Nano Banana Pro scrambles the geometry.

## Checklist

- [ ] Model chosen by the routing table, and priced with `generate cost`
- [ ] Aspect ratio and size on the command, not in the prose
- [ ] Prose, 80–150 words (up to ~330 with bible and spec lines), one register line
- [ ] Positive phrasing; edits pair every removal with its fill
- [ ] Light with a direction and falloff; materials with a finish
- [ ] Palette split taken from the brief or references
- [ ] Composition stated (thirds by default, unless the shot specifies otherwise)
- [ ] Keyframes: the clip's field of view, distance and height; people mid-action; faces small or turned for 2.5
- [ ] Identity from a Soul ID or reference; no real names, brands or IP
- [ ] One photograph per prompt (sheets only for approval)
- [ ] Linted with `preflight.py --image` (`--sheet` / `--edit` where relevant)

## Unverified

Test once before relying on these:
- **Inpaint masks:** the mask format for `--is_inpaint` on GPT Image 2 and Nano Banana 2. The schema lists `mask` as an object; check `higgsfield model get gpt_image_2` and run one cheap test.
- **Numbered references:** how Nano Banana Pro maps several attached references to wording in the prompt. That's why the templates refer to references in words.
- **Seedream 4.5's role:** LIRA keeps it to texture passes, but Higgsfield's own `higgsfield-generate` skill also routes face edits and scene swaps to it.
- **Palettes:** whether percentage palettes are followed equally by every model.
- **Soul Cast:** what `--budget` controls.
