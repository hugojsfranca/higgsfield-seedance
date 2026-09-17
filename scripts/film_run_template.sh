#!/usr/bin/env bash
# Run-script template for one act of a Seedance or Cinema Studio film on Higgsfield (see references/film-planning.md).
# Copy it next to the act's prompts/ and keyframes/ folders, fill in CLIPS, and run the stages in order.
#
#   ./run.sh lint                 lint every prompt (free, local)
#   ./run.sh cost                 price every clip with `higgsfield generate cost` (free; uploads start frames)
#   ./run.sh canary S03_A         one clip alone, the first of any new risk type
#   ./run.sh clips [ids...]       the rest (or just the listed ids); asks before spending
#   ./run.sh upscale <job_id>     keep a take at 1080p (bytedance_video_upscale, aigc preset)
#   ./run.sh gate G1              record that the user approved gate G1 (later stages check for it)
#   DRY=1 ./run.sh clips          print every command instead of running it
#   RES=720p ./run.sh clips S09_B hero re-render (a new take, not the draft)
#
# Conventions: numbered takes that never overwrite a job record; assets found only through the
# manifest resolver; inputs checked before any paid step; y/N before spending; bash 3.2-safe.
set -euo pipefail
cd "$(dirname "$0")"

SKILL_DIR="${SKILL_DIR:-../../higgsfield-seedance}"   # pin: set to the plugin folder (or copy) these prompts were written under
STUDIO_IDS="$SKILL_DIR/scripts/studio_ids.py"
PREFLIGHT="$SKILL_DIR/scripts/preflight.py"
MANIFEST="${MANIFEST:-../assets/manifest.csv}"
RES="${RES:-480p}"
REQUIRED_GATE="${REQUIRED_GATE:-G1}"                       # paid clip stages need this approval marker

# clip_id | model | mode (- for Cinema Studio 3.5/3.0) | seconds | start frame (asset ID[:view] or -) |
# refs (comma list of ID[:view] or -) | audio on/off | look controls (- or flags; @kind:Name looks up a harvested ID,
# with _ for spaces, e.g. @camera_model:35mm_Film; catalog from scripts/studio_ids.py harvest)
CLIPS="
S03_A|seedance_2_5|omni_reference|4|KF_S03_A|OBJ01:main|off|-
S03_C|seedance_2_0|std|4|KF_S03_C|CH04:portrait|off|-
S04_A|cinematic_studio_video_4_0|omni_reference|4|KF_S04_A|-|off|--genre_id @genre:Drama --camera_lens_id @camera_lens:Anamorphic
S04_B|cinematic_studio_3_0|-|6|KF_S04_B|-|off|--speedramp linear --genre drama
"

run() { if [[ "${DRY:-0}" == 1 ]]; then printf 'DRY:'; printf ' %q' "$@"; echo; else "$@"; fi; }
confirm() { [[ "${DRY:-0}" == 1 ]] && return 0; read -r -p "$1 [y/N] " ok; [[ "$ok" == [yY] ]]; }
field() { echo "$1" | cut -d'|' -f"$2"; }
row_of() { echo "$CLIPS" | grep -E "^$1\|" || { echo "unknown clip $1" >&2; exit 1; }; }
assets() { python3 "$SKILL_DIR/scripts/assets.py" --manifest "$MANIFEST" "$@"; }
next_take() { local n=1; while [[ -e "jobs/${1}_${RES}_t${n}.json" ]]; do n=$((n + 1)); done; echo "jobs/${1}_${RES}_t${n}.json"; }
need_gate() { [[ "${DRY:-0}" == 1 || -e "gates/$1.ok" ]] || { echo "gate $1 not approved yet (./run.sh gate $1)" >&2; exit 1; }; }

uses_stdin() { [[ "$1" == seedance_* ]]; }   # Seedance takes the prompt on stdin; Cinema Studio gets --prompt (stdin untested there)

build_flags() {   # fills the global FLAGS array for one clip row; exits the script if an asset or control ID won't resolve
  local row="$1" model mode secs start refs audio looks r path word kind name id
  model=$(field "$row" 2); mode=$(field "$row" 3); secs=$(field "$row" 4); start=$(field "$row" 5); refs=$(field "$row" 6)
  audio=$(field "$row" 7); looks=$(field "$row" 8)
  FLAGS=(--duration "$secs" --resolution "$RES" --aspect_ratio 16:9)
  case "$model" in
    seedance_2_5|cinematic_studio_video_4_0) FLAGS+=(--mode "$mode" --bitrate_mode high) ;;
    seedance_2_0) FLAGS+=(--mode "$mode") ;;
    cinematic_studio_video_3_5|cinematic_studio_3_0) FLAGS+=(--prompt_language en) ;;   # these default to zh
    *) echo "unknown model $model" >&2; exit 1 ;;
  esac
  if [[ "$audio" == off ]]; then FLAGS+=(--generate_audio false); else FLAGS+=(--generate_audio true); fi
  if [[ -n "$looks" && "$looks" != "-" ]]; then
    for word in $looks; do
      if [[ "$word" == @*:* ]]; then
        kind=${word#@}; kind=${kind%%:*}; name=${word#*:}; name=${name//_/ }
        id=$(python3 "$STUDIO_IDS" find "$kind" "$name") || { echo "no harvested $kind '$name'; use it once in the web app, then: python3 $STUDIO_IDS harvest" >&2; exit 1; }
        FLAGS+=("$id")
      else
        FLAGS+=("$word")
      fi
    done
  fi
  if [[ "$start" != "-" ]]; then
    path=$(assets resolve "$start") || { echo "start frame $start isn't in the manifest; approve and record it first" >&2; exit 1; }
    FLAGS+=(--start-image "$path")
  fi
  if [[ "$refs" != "-" ]]; then
    for r in $(echo "$refs" | tr ',' ' '); do
      path=$(assets resolve "$r") || { echo "reference $r isn't in the manifest; approve and record it first" >&2; exit 1; }
      FLAGS+=(--image-references "$path")
    done
  fi
}

make_clip() {
  local id="$1" row model out
  row=$(row_of "$id"); model=$(field "$row" 2)
  [[ -f "prompts/$id.txt" ]] || { echo "missing prompts/$id.txt" >&2; exit 1; }
  build_flags "$row"
  mkdir -p jobs clips
  out=$(next_take "$id")
  uses_stdin "$model" || FLAGS+=(--prompt "$(cat "prompts/$id.txt")")
  if [[ "${DRY:-0}" == 1 ]]; then
    run higgsfield generate create "$model" "${FLAGS[@]}" --wait --wait-timeout 30m --json
    return 0
  fi
  if uses_stdin "$model"; then
    higgsfield generate create "$model" "${FLAGS[@]}" --wait --wait-timeout 30m --json < "prompts/$id.txt" > "$out"
  else
    higgsfield generate create "$model" "${FLAGS[@]}" --wait --wait-timeout 30m --json < /dev/null > "$out"
  fi
  url=$(python3 -c '
import json, sys
try:
    d = json.load(open(sys.argv[1])); d = d[0] if isinstance(d, list) else d; print(d.get("result_url") or "")
except (ValueError, IndexError, AttributeError):
    print("")' "$out")
  [[ -n "$url" ]] || { echo "$id: no result (refused or failed); see $out" >&2; return 1; }
  curl -fsSL -o "clips/$(basename "$out" .json).mp4" "$url" || { echo "$id: download failed; the job record is in $out" >&2; return 1; }
  echo "$id -> clips/$(basename "$out" .json).mp4"
}

case "${1:-}" in
  lint)
    echo "$CLIPS" | while IFS= read -r row; do
      [[ -z "$row" ]] && continue
      id=$(field "$row" 1); model=$(field "$row" 2); mode=$(field "$row" 3); secs=$(field "$row" 4)
      extra=(); [[ "$mode" != "-" ]] && extra+=(--mode "$mode")
      [[ $(field "$row" 5) != "-" ]] && extra+=(--start-image)
      n=$(field "$row" 6 | tr ',' '\n' | grep -vc '^-$' || true); extra+=(--images "$n")
      [[ $(field "$row" 7) == off ]] && extra+=(--no-audio)
      python3 "$PREFLIGHT" "prompts/$id.txt" --model "$model" --duration "$secs" "${extra[@]}" || true
    done
    ;;
  cost)
    echo "$CLIPS" | while IFS= read -r row; do
      [[ -z "$row" ]] && continue
      id=$(field "$row" 1); model=$(field "$row" 2); build_flags "$row"
      printf "%s: " "$id"
      if uses_stdin "$model"; then run higgsfield generate cost "$model" "${FLAGS[@]}" < "prompts/$id.txt"
      else run higgsfield generate cost "$model" "${FLAGS[@]}" --prompt "$(cat "prompts/$id.txt")" < /dev/null; fi
    done
    ;;
  canary)
    need_gate G0
    confirm "Run test clip $2 at $RES?" || exit 0
    make_clip "$2"
    ;;
  clips)
    shift; need_gate "$REQUIRED_GATE"
    ids="$*"; [[ -z "$ids" ]] && ids=$(echo "$CLIPS" | grep -v '^$' | cut -d'|' -f1 | tr '\n' ' ')
    confirm "Generate $(echo $ids | wc -w | tr -d ' ') clip(s) at $RES?" || exit 0
    for id in $ids; do make_clip "$id" || echo "$id failed; continuing" >&2; done
    ;;
  upscale)
    confirm "Upscale job $2 to 1080p?" || exit 0
    run higgsfield generate create bytedance_video_upscale --video "$2" --preset aigc --resolution 1080p --wait
    ;;
  gate)
    mkdir -p gates && date > "gates/$2.ok" && echo "gate $2 recorded"
    ;;
  *)
    sed -n '2,13p' "$0"; exit 2
    ;;
esac
