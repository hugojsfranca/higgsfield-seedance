#!/usr/bin/env bash
# Open the storyboard and place the interfaces on the plates.
#
#   ./place-screens.sh
#
# Starts a small local server (the page needs one to read the frames reliably), refreshes the
# storyboard data from the shot list and whatever frames exist, and opens the page in your browser.
# Press ctrl-C here when you are done; your placements are kept in the browser as you go, and
# "Download screens.json" saves them.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-8788}"

python3 ui/composite.py --tool

if curl -fsS "http://localhost:$PORT/" >/dev/null 2>&1; then
  echo "reusing the server already on port $PORT"
else
  python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
  SERVER=$!
  trap 'kill $SERVER 2>/dev/null || true' EXIT
  for _ in $(seq 1 40); do
    curl -fsS "http://localhost:$PORT/" >/dev/null 2>&1 && break
    sleep 0.25
  done
  echo "server started on port $PORT (pid $SERVER)"
fi

URL="http://localhost:$PORT/ui/corners.html?v=$(date +%s)"   # the query defeats a stale cached page
echo "opening $URL"
command -v open >/dev/null && open "$URL" || echo "open it yourself: $URL"
echo
echo "When you are done: Download screens.json into ui/, then run"
echo "  python3 ui/composite.py --pull --all   # takes the newest screens.json from Downloads"
echo
echo "ctrl-C to stop the server."
if [[ -n "${SERVER:-}" ]]; then wait $SERVER; fi
