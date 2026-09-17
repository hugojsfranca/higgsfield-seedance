# Seedance on Higgsfield: a Claude skill

A skill for Claude that writes, checks, prices and runs **ByteDance Seedance 2.5** (and 2.0) video prompts on [Higgsfield](https://higgsfield.ai) through the `higgsfield` CLI.

Most bad Seedance results come from how the prompt is built, not from the settings: beats that merge or vanish, left and right flipped, lenses drifting, invented lettering, endings that freeze. The skill directs the shot first, then writes a prompt that holds up over a long take, lints it locally and prices it for free before any credits are spent.

## What it covers

- **Single clips up to 30 s** on Seedance 2.5: timestamped beats, cuts inside one take, voiceover and on-screen text.
- **Reference-driven video** with `@Image` / `@Video` / `@Audio`, and start/end-frame transitions.
- **Editing and extending** existing clips, forward or backward.
- **Routing to Seedance 2.0** for readable faces and other cases where it's the better model.
- **Multi-scene films:** shot list, asset bible, reference library, face tests, screen plates, budget scenarios and approval gates.

It asks before anything paid. Every run is linted and priced first, and staged run scripts ask y/N before they spend.

## Install

### Claude Code

Clone the repo into your skills folder. The folder name should match the skill's `name`.

```bash
git clone https://github.com/hugojsfranca/higgsfield-seedance-skill.git ~/.claude/skills/higgsfield-seedance-2-5
```

Start a new Claude Code session. The skill loads when you ask for a Seedance or Higgsfield video.

### Claude.ai / Claude desktop

Zip the folder without `.git` and upload it under **Settings → Capabilities → Skills**:

```bash
cd ~/.claude/skills && zip -r higgsfield-seedance-2-5.zip higgsfield-seedance-2-5 -x '*/.git/*' '*/evals/*' '*.DS_Store'
```

## Requirements

- **Higgsfield CLI**, signed in: `curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh`, then log in.
- **python3** for the linter and planning tools. They use only the standard library.
- **ffmpeg** for extracting last frames when chaining clips.

## What's inside

| Path | Purpose |
|---|---|
| `SKILL.md` | Routing (2.5 vs 2.0), the brief, modes, prompt rules, faces, preflight, run and delivery |
| `references/prompt-patterns.md` | Five prompt shapes with examples, and camera language |
| `references/shot-direction.md` | Blocking, gaze, screen direction, optics, lighting, cut types, dialogue |
| `references/first-last-frame.md` | Start/end-frame transitions and chaining |
| `references/edit-extend-chain.md` | Editing and extending clips |
| `references/film-planning.md` | Multi-scene pipeline: gates, shot list, asset bible, budget, resolution strategy |
| `scripts/preflight.py` | Lints a video or keyframe prompt against the settings you plan to submit |
| `scripts/shotlist_check.py` | Validates a film shot list: timing, durations, modes, missing prompts, credit estimate |
| `scripts/optics.py` | Frame size for a lens at a distance, to sanity-check scale in a prompt |
| `scripts/assets.py` | Records approved reference images and resolves asset IDs to exactly one file |
| `scripts/film_run_template.sh` | Staged run script for one act: lint, cost, canary, clips, upscale, gates |
| `scripts/last_frame.sh` | Extracts a clip's last frame for chaining |

Run the scripts on their own:

```bash
python3 scripts/preflight.py prompt.txt --duration 12 --mode omni_reference --start-image
python3 scripts/shotlist_check.py shotlist.csv --prompts prompts --keyframes keyframes
python3 scripts/optics.py 85mm 3m
```

## Notes

- Model facts (modes, durations, limits, rates) were checked against `higgsfield model get` in September 2026. If the CLI disagrees, trust the CLI.
- The linter's checks are heuristics: fix every ERROR and judge each WARN.

## Credits

- Built from the Seedance 2.5 prompting skill by [InstaSD](https://www.instasd.com/post/seedance-2-5-claude-prompting-skill) (v1.1), then substantially reworked and extended for Higgsfield. Some examples in `references/prompt-patterns.md` come from that skill.
- `references/shot-direction.md` is adapted from Higgsfield's CINEDANCE V4 prompt-director guide for Seedance.
