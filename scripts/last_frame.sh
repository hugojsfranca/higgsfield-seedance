#!/usr/bin/env bash
# Extract the last frame of a video as a PNG, for first/last-frame chaining on Seedance 2.5.
#
#   last_frame.sh <job_id | video_url | local_video> [out.png]
#
# A Higgsfield job ID is resolved to its result URL through the higgsfield CLI.
# Prints the path of the written PNG.
set -euo pipefail

src="${1:?usage: last_frame.sh <job_id|video_url|local_video> [out.png]}"
out="${2:-last_frame.png}"

command -v ffmpeg >/dev/null || { echo "ffmpeg not found (macOS: brew install ffmpeg)" >&2; exit 1; }

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

if [[ "$src" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
  src="$(higgsfield generate get "$src" --json | python3 -c '
import json, sys
d = json.load(sys.stdin)
d = d[0] if isinstance(d, list) else d
url = d.get("result_url")
if not url:
    sys.exit("job has no result_url yet (status: %s)" % d.get("status"))
print(url)
')"
fi

if [[ "$src" =~ ^https?:// ]]; then
  curl -fsSL -o "$tmpdir/src.mp4" "$src"
  src="$tmpdir/src.mp4"
fi

# Decode only the final second and keep overwriting one image, so the file ends up
# holding the very last decoded frame (more reliable than seeking to an exact timestamp).
ffmpeg -v error -y -sseof -1 -i "$src" -update 1 "$out"

[[ -s "$out" ]] || { echo "no frame extracted from $1" >&2; exit 1; }
echo "$out"
