#!/usr/bin/env bash
# Fetch the latest upstream data files from openai/math via the GitHub API.
# (Uses api.github.com instead of raw.githubusercontent.com, which is
# unreachable from some networks.)
set -euo pipefail
cd "$(dirname "$0")/.."

REPO="openai/math"
API="https://api.github.com/repos/$REPO/contents"

fetch() { # fetch <repo-path> <local-path>
  echo "fetching $1"
  curl -4 -sL --max-time 300 --retry 3 \
    -H "Accept: application/vnd.github.raw" \
    "$API/$1" -o "$2"
}

fetch "CONTENTS.md"                          "data/CONTENTS.md"
fetch "README.md"                            "data/README-upstream.md"
fetch "overview.tex"                         "data/overview.tex"
fetch "lean/formalization.yaml"              "data/formalization.yaml"
fetch "lean/README.md"                       "data/lean-README.md"
fetch "lean/ComparatorChallenges/README.md"  "data/comparator-README.md"

# reasoning traces listing (file names only, one per line)
curl -4 -sL --max-time 60 --retry 3 "$API/reasoning_traces" \
  | python3 -c "import json,sys; [print(x['name']) for x in json.load(sys.stdin)]" \
  > data/reasoning_traces.txt

# record the upstream commit we synced from
curl -4 -sL --max-time 30 "$(
  echo "https://api.github.com/repos/$REPO/commits?per_page=1"
)" | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['sha'][:12])" \
  > data/UPSTREAM.sha

echo "synced to upstream commit $(cat data/UPSTREAM.sha)"
