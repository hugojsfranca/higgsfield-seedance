# higgsfield-seedance

A Claude Code plugin for making **ByteDance Seedance 2.5** (and 2.0) videos on [Higgsfield](https://higgsfield.ai) through the `higgsfield` CLI.

Most bad Seedance results come from how the prompt is built, not from the settings: beats that merge or vanish, left and right flipped, lenses drifting, invented lettering, endings that freeze. The plugin directs the shot first, then writes a prompt that holds up over a long take, lints it locally and prices it for free before any credits are spent.

## Actions

| Command | What it does | Spends credits? |
|---|---|---|
| `/higgsfield-seedance:generate` | Brief → model and mode → prompt → lint → free price check → run → deliver | Yes, after showing you the cost |
| `/higgsfield-seedance:prompt` | Write, fix, review or lint a video or keyframe prompt | Never |
| `/higgsfield-seedance:plan` | Plan a multi-scene film: shot list, asset bible, face tests, budget, gates, run scripts | No (planning only) |
| `/higgsfield-seedance:edit` | Edit, extend, chain, join or upscale an existing clip | Yes, after showing you the cost |

You can type a command with a description after it (`/higgsfield-seedance:generate a 12 s aerial of a cargo ship at dawn`), or just describe what you want and Claude picks the right action.

## Install

### From GitHub

```bash
claude plugin marketplace add hugojsfranca/higgsfield-seedance
claude plugin install higgsfield-seedance@hugojsfranca
```

Start a new Claude Code session. To pick up later changes:

```bash
claude plugin marketplace update hugojsfranca && claude plugin update higgsfield-seedance@hugojsfranca
```

### For local development

Clone the repo anywhere and link it into your skills folder. Claude Code loads it as a plugin (`higgsfield-seedance@skills-dir`), and edits take effect in the next session with no reinstall:

```bash
git clone https://github.com/hugojsfranca/higgsfield-seedance.git
ln -s "$PWD/higgsfield-seedance" ~/.claude/skills/higgsfield-seedance
```

Check it with `claude plugin details higgsfield-seedance`. Don't use both install methods at once, or the actions appear twice.

## Requirements

- **Higgsfield CLI**, signed in: `curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh`, then `higgsfield auth login`.
- **python3** for the linter and planning tools. They use only the standard library.
- **ffmpeg** for last frames, trims and joins.

## What's inside

| Path | Purpose |
|---|---|
| `.claude-plugin/` | Plugin manifest, and a marketplace file so this repo installs directly |
| `skills/generate/` | Routing (2.5 vs 2.0), brief, modes, one take vs one clip per shot, price, run, deliver, errors |
| `skills/prompt/` | Shot direction, prompt shape, the 17 rules, faces, keyframe prompts, preflight |
| `skills/plan/` | Film workflow: brief review, routing, shot list, asset bible, budget, gates, review |
| `skills/edit/` | Edit, extend, chain, upscale and join |
| `references/prompt-patterns.md` | Five prompt shapes with worked examples, and camera language |
| `references/shot-direction.md` | Blocking, gaze, screen direction, optics, lighting, cut types, dialogue |
| `references/first-last-frame.md` | Start/end-frame transitions |
| `references/edit-extend-chain.md` | Edit and extension prompts, chaining past 30 s |
| `references/film-planning.md` | Pipeline and gates, shot-list format, asset bible, face tests, budget, resolution strategy |
| `scripts/preflight.py` | Lints a video or keyframe prompt against the settings you plan to submit |
| `scripts/shotlist_check.py` | Validates a film shot list: timing, durations, modes, missing prompts, credit estimate |
| `scripts/optics.py` | Frame size for a lens at a distance, to sanity-check scale in a prompt |
| `scripts/assets.py` | Records approved reference images and resolves asset IDs to exactly one file |
| `scripts/film_run_template.sh` | Staged run script for one act: lint, cost, canary, clips, upscale, gates |
| `scripts/last_frame.sh` | Extracts a clip's last frame for chaining |

The scripts also run on their own:

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

## License

[MIT](LICENSE)
