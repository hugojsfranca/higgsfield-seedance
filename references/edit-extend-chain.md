# Edit, extend, and chain past 30 seconds

## Contents

- [Extension (forward and backward)](#extension-forward-and-backward)
- [Video edit](#video-edit)
- [Chaining past 30 s](#chaining-past-30-s)
- [Resolution and cost across a chain](#resolution-and-cost-across-a-chain)

Every mode here accepts a previous Higgsfield job ID wherever a video goes (`--video <job_id>`), so you rarely need to download anything.

---

## Extension (forward and backward)

`--mode video_extension` with `--extension_mode forward` adds footage after the source's last frame. `backward` adds footage before its first frame. `--duration` is the length of the new footage and is billed at the normal rate for the resolution.

```bash
higgsfield generate create seedance_2_5 --mode video_extension --extension_mode forward \
  --video <job_id_or_path> --duration 10 --resolution 720p --aspect_ratio 16:9 \
  --wait --wait-timeout 30m < continuation.txt
```

**Write the continuation, not a recap.** A recap restarts the shot. The prompt describes only what happens next:

- *Forward:* start from the exact moment the source ends. Name what is moving and keep it moving at the same speed and in the same direction (camera and subject), then add the new beats. "The truck keeps its speed along the same road; the camera holds its position above and behind it. 0–4s: the road bends toward a distribution hub..."
- *Backward:* end on the exact moment the source begins. Describe what leads into that first frame, and close the prompt on that state: "...the ship's bow settles into the frame exactly as the source opens."

Match the source's resolution and aspect ratio, restate the wardrobe and color anchors from the original prompt, and time-segment the new footage like any other prompt.

**Long sources:** the ByteDance API allows about 30 s of reference video per job, and it's unverified whether Higgsfield enforces the same limit. If a long source is rejected, or the result drifts, feed only the tail:

```bash
ffmpeg -v error -sseof -10 -i source.mp4 -c:v libx264 -crf 16 -c:a aac tail.mp4   # last 10 s
```

---

## Video edit

`--mode video_edit` takes exactly one `--video` and changes something inside it. Add `--image-references` when the edit brings in a specific new subject. Billing appears to follow the source clip's length.

The prompt names the change and pins everything that stays. Without the "keep" line the model feels free to re-stage the shot.

```
Replace the white articulated truck in @Video 1 with the red electric truck from
@Image 1. Keep the road, the fields, the camera move, the sunrise lighting and the
timing exactly as in @Video 1.
```

```
Turn the season in @Video 1 to deep winter: snow covers the fields and the road
shoulders, breath-like exhaust from the truck, cold blue morning light. The truck, its
path, the camera move and the timing stay exactly as in @Video 1.
```

One edit per job. For a replacement plus a relight plus a style change, run them as successive edits, feeding each result's job ID into the next.

---

## Chaining past 30 s

One generation caps at 30 s. Longer films come from two chaining methods that solve different problems. Pick one by what has to survive the cut:

| Must survive the cut | Method | Why |
|---|---|---|
| **Motion**: chases, dances, continuous camera moves | **Extension** (`video_extension`, `forward`) | The model sees the moving footage, so speed and direction carry over. A single frozen frame keeps composition but not motion. |
| **Composition at a scene break**: location change, time jump, chapter cut | **First/last-frame chain**: the previous clip's last frame becomes the next clip's `--start-image` (`omni_reference`) | Locks the opening composition exactly. On one reported two-clip chain (on the ByteDance API), the new clip's first frame differed from the wired frame by only ~2.6 mean pixel values. |

A first/last-frame chain is also the fix when a run of extensions starts drifting: pull the last *good* frame and chain from there, and the drift stops compounding.

**Extracting the last frame:**

```bash
bash <plugin-root>/scripts/last_frame.sh <job_id|url|path> chain_01.png
higgsfield generate create seedance_2_5 --mode omni_reference --start-image ./chain_01.png \
  --duration 30 --resolution 720p --aspect_ratio 16:9 --wait --wait-timeout 30m < part2.txt
```

`last_frame.sh` takes a job ID (it looks up the result URL), a URL or a local file.

**Plan the break frames.** A chain frame with a large, readable face gets refused, consistently rather than at random. Stage the last beat of each clip so people are small, turned away, helmeted or out of focus, and describe the character in text in every clip, word for word. Prompt rule 9 ("keep the clip self-contained") pays off here: a clip that ends on a well-described held frame is easy to chain from.

**The part-2 prompt** follows the first/last-frame rules: describe the journey onward from the start frame, not the frame itself.

---

## Resolution and cost across a chain

- **Decide the final resolution before you chain.** Each clip in a chain starts from the previous clip's actual frames. A chain built on 480p drafts can't be re-rendered at 1080p piece by piece, because every re-render is a new take and the joins will no longer match. So either build the final chain at 720p or 1080p once the prompts are proven on 480p single clips, or build it at 480p/720p and upscale every clip with the same settings: `bytedance_video_upscale --preset aigc --resolution 1080p` (or `2k` / `4k`).
- **Cost planning** (September 2026 estimates): a 30 s clip is about 75 credits at 480p, 195 at 720p and 270 at 1080p. A 90 s three-clip chain at 720p is about 585 credits plus retries. Always price the whole plan with `higgsfield generate cost` and tell the user the total before starting.
- **Joining clips:** once all the parts exist, concatenate them locally:

```bash
printf "file '%s'\n" part1.mp4 part2.mp4 part3.mp4 > list.txt
ffmpeg -v error -f concat -safe 0 -i list.txt -c copy film.mp4
```

(Re-encode instead of `-c copy` if the clips differ in resolution or codec settings.)
