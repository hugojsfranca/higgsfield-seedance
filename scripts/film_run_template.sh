#!/usr/bin/env bash
# Run-script template for one act of a Seedance film on Higgsfield (see references/film-planning.md).
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

SKILL_DIR="${SKILL_DIR:-../../higgsfield-seedance-2-5}"   # pin: set to the skill copy these prompts were written under
PREFLIGHT="$SKILL_DIR/scripts/preflight.py"
MANIFEST="${MANIFEST:-../assets/manifest.csv}"
RES="${RES:-480p}"
REQUIRED_GATE="${REQUIRED_GATE:-G1}"                       # paid clip stages need this approval marker

# clip_id | model | mode | seconds | start frame (asset ID[:view] or -) | refs (comma list of ID[:view] or -) | audio on/off
CLIPS="
S03_A|seedance_2_5|omni_reference|4|KF_S03_A|OBJ01:main|off
S03_C|seedance_2_0|std|4|KF_S03_C|CH04:portrait|off
"

run() { if [[ "${DRY:-0}" == 1 ]]; then printf 'DRY:'; printf ' %q' "$@"; echo; else "$@"; fi; }
confirm() { [[ "${DRY:-0}" == 1 ]] && return 0; read -r -p "$1 [y/N] " ok; [[ "$ok" == [yY] ]]; }
field() { echo "$1" | cut -d'|' -f"$2"; }
row_of() { echo "$CLIPS" | grep -E "^$1\|" || { echo "unknown clip $1" >&2; exit 1; }; }
assets() { python3 "$SKILL_DIR/scripts/assets.py" --manifest "$MANIFEST" "$@"; }
next_take() { local n=1; while [[ -e "jobs/${1}_${RES}_t${n}.json" ]]; do n=$((n + 1)); done; echo "jobs/${1}_${RES}_t${n}.json"; }
need_gate() { [[ "${DRY:-0}" == 1 || -e "gates/$1.ok" ]] || { echo "gate $1 not approved yet (./run.sh gate $1)" >&2; exit 1; }; }

build_flags() {   # fills the global FLAGS array for one clip row; exits the script if an asset won't resolve
  local row="$1" mode secs start refs audio r path
  mode=$(field "$row" 3); secs=$(field "$row" 4); start=$(field "$row" 5); refs=$(field "$row" 6); audio=$(field "$row" 7)
  FLAGS=(--mode "$mode" --duration "$secs" --resolution "$RES" --aspect_ratio 16:9 --bitrate_mode high)
  [[ "$audio" == off ]] && FLAGS+=(--generate_audio false)
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
  if [[ "${DRY:-0}" == 1 ]]; then
    run higgsfield generate create "$model" "${FLAGS[@]}" --wait --wait-timeout 30m --json
    return 0
  fi
  higgsfield generate create "$model" "${FLAGS[@]}" --wait --wait-timeout 30m --json < "prompts/$id.txt" > "$out"
  url=$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); d=d[0] if isinstance(d,list) else d; print(d.get("result_url") or "")' "$out")
  [[ -n "$url" ]] || { echo "$id: no result (refused or failed); see $out" >&2; return 1; }
  curl -fsSL -o "clips/$(basename "$out" .json).mp4" "$url"
  echo "$id -> clips/$(basename "$out" .json).mp4"
}

case "${1:-}" in
  lint)
    echo "$CLIPS" | while IFS= read -r row; do
      [[ -z "$row" ]] && continue
      id=$(field "$row" 1); model=$(field "$row" 2); mode=$(field "$row" 3); secs=$(field "$row" 4)
      extra=(); [[ $(field "$row" 5) != "-" ]] && extra+=(--start-image)
      n=$(field "$row" 6 | tr ',' '\n' | grep -vc '^-$' || true); extra+=(--images "$n")
      [[ $(field "$row" 7) == off ]] && extra+=(--no-audio)
      python3 "$PREFLIGHT" "prompts/$id.txt" --model "$model" --mode "$mode" --duration "$secs" "${extra[@]}" || true
    done
    ;;
  cost)
    echo "$CLIPS" | while IFS= read -r row; do
      [[ -z "$row" ]] && continue
      id=$(field "$row" 1); build_flags "$row"
      printf "%s: " "$id"; run higgsfield generate cost "$(field "$row" 2)" "${FLAGS[@]}" < "prompts/$id.txt"
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
