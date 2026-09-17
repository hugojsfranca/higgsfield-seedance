---
name: edit
description: >-
  Change, extend, chain, join or upscale an existing Higgsfield video with ByteDance Seedance 2.5:
  video_edit (replace a subject, change the season or light while keeping the shot),
  video_extension forward or backward, first/last-frame chaining past the 30 s limit, stitching
  parts together, and 1080p / 2K / 4K upscales that keep the exact take. Use when the user has a
  clip, file or Higgsfield job ID and wants it altered, made longer, continued into a next part,
  joined with others or made higher resolution, or when a chain of clips starts drifting.
argument-hint: "[job ID or video file] [what to change]"
compatibility: Requires the higgsfield CLI (logged in); ffmpeg for last frames, trims and joins.
---

# Edit, extend, chain or upscale a Higgsfield clip

This skill works on footage that already exists. `${CLAUDE_PLUGIN_ROOT}` is the plugin's folder, two levels above this skill's folder. **Read `${CLAUDE_PLUGIN_ROOT}/references/edit-extend-chain.md` before writing any prompt here.** It has the command shapes, prompt examples and chaining rules.

## 0. Bootstrap

- `higgsfield` must be on PATH. If not: `curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh`
- If `higgsfield account status` reports an expired session or no auth, ask the user to run `higgsfield auth login` and wait for them.

## 1. Identify the source

- **A job ID is best.** It goes straight into `--video` with no download. `higgsfield generate get <job_id> --json` shows its resolution, aspect ratio, duration and the prompt it was made with.
- **A local file or URL** also works; local paths upload automatically.
- **Match the source:** use its resolution and aspect ratio, and carry over its wardrobe and colour anchors from the original prompt.

## 2. Pick the operation

| The user wants | Operation |
|---|---|
| Something inside the clip changed (a replaced subject, a new season or light) with the shot kept | `--mode video_edit`, exactly one `--video`, plus `--image-references` for a specific new subject |
| More footage after the last frame, or before the first | `--mode video_extension --extension_mode forward` or `backward`, at least one `--video`; `--duration` is the new footage only |
| To go past 30 s with **motion** carrying across the join (chases, dances, continuous camera moves) | Extension, forward |
| To go past 30 s with a **new composition** at the join (location change, time jump, chapter) | First/last-frame chain: the last frame becomes the next clip's `--start-image` in `omni_reference` |
| The same take at a higher resolution | Upscale (§5) |
| Several parts as one file | Join (§6) |

These edit and extension modes exist on `seedance_2_5` only. A run of extensions that starts drifting is fixed by chaining from the last *good* frame instead.

## 3. Write the prompt

Write it with `higgsfield-seedance:prompt` (load it with the Skill tool, or read `${CLAUDE_PLUGIN_ROOT}/skills/prompt/SKILL.md`), using the logic for this operation:

- **Edit:** name the one change, then pin everything that stays ("Keep the road, the fields, the camera move, the sunrise lighting and the timing exactly as in @Video 1"). Without the keep line the model re-stages the shot. One edit per job: run a replacement, a relight and a style change as successive edits, feeding each result's job ID into the next.
- **Extension:** write the continuation, not a recap. Forward starts from the exact moment the source ends and keeps what's moving at the same speed and direction. Backward ends on the exact moment the source begins. Time-segment the new footage like any other prompt.
- **Chain part:** follow `${CLAUDE_PLUGIN_ROOT}/references/first-last-frame.md`. Describe the journey onward from the start frame, not the frame itself. Stage each clip's last beat so faces are small, turned away or covered, since a chain frame with a large readable face gets refused.

Extract a last frame for chaining:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/last_frame.sh <job_id|url|path> chain_01.png
```

Lint with the real settings, e.g. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py continuation.txt --mode video_extension --extension-mode forward --duration 10 --videos 1`.

## 4. Price, confirm, run

- **Price first, for free:** `higgsfield generate cost seedance_2_5 <same flags> < prompt.txt`. Extensions are billed on the new footage's duration; edits appear to be billed on the source clip's length. For a chain, price the whole plan and tell the user the total before starting.
- **Confirm:** before the first paid job in a session, show the prompt, settings and cost, and wait for a go-ahead.
- **Run:** pipe the prompt from its file, and add `--bitrate_mode high --wait --wait-timeout 30m --json` so you get the job ID for the next step.
- **Long sources:** if a long source is rejected or the result drifts, feed only its tail (the trim command is in the reference).
- **Decide the final resolution before chaining.** Every re-render is a new take, so a chain built on 480p drafts can't be re-rendered at 1080p piece by piece. Either build the final chain at 720p or 1080p once the prompts are proven, or build it at 480p/720p and upscale every clip with the same settings.

## 5. Upscale

Higgsfield exposes no seed, so re-running a prompt at a higher resolution gives a different take. To keep this exact take:

```bash
higgsfield generate create bytedance_video_upscale --video <job_id> --preset aigc --resolution 1080p --wait
```

`--resolution` also takes `2k` or `4k`. Estimates come to a fraction of a credit per clip. Upscales from 720p look better than from 480p. Test one upscale before planning a whole film around it.

## 6. Join and deliver

```bash
printf "file '%s'\n" part1.mp4 part2.mp4 part3.mp4 > list.txt
ffmpeg -v error -f concat -safe 0 -i list.txt -c copy film.mp4
```

Re-encode instead of `-c copy` if the parts differ in resolution or codec settings.

Give the result URL and a one-line summary (operation, duration, resolution, credits), then offer the next move: another edit, the next chain part, an upscale, or a download (`curl -L -o out.mp4 "<result_url>"`).

## Unverified on Higgsfield

Test once at 480p (about 10 credits) when it matters, and tell the user what you found:
- whether a `video_extension` result contains the source plus the new footage or only the new part;
- the longest source video Higgsfield accepts (the ByteDance API allows about 30 s of reference video per job);
- whether refused or failed jobs refund their credits.
