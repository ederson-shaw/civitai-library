#!/usr/bin/env bash
# publish v1 — gates + gh-pages deploy under ederson-shaw (per-command token, never gh auth switch)
# usage: bash tools/publish.sh   (refuses unless build_check2 passes)
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== gates =="
python3 tools/sitegen2.py > /dev/null
python3 tools/build_check2.py | tail -3
python3 tools/build_check2.py | grep -q "PASS (default)" || { echo "BLOCKED: build_check2 not green"; exit 1; }

echo "== remote =="
if ! git remote get-url origin &>/dev/null; then
  GH_TOKEN="$(gh auth token --user ederson-shaw)" gh repo create ederson-shaw/civitai-library \
    --public --source . --remote origin --description "civitai lora/workflow curation workbench"
fi
git config credential.helper '!f() { echo "username=ederson-shaw"; echo "password=$(gh auth token --user ederson-shaw)"; }; f'
git push -u origin main

echo "== gh-pages =="
git subtree split --prefix=site -b gh-pages-tmp
git push origin gh-pages-tmp:gh-pages
git branch -D gh-pages-tmp

echo "== pages on =="
GH_TOKEN="$(gh auth token --user ederson-shaw)" gh api repos/ederson-shaw/civitai-library/pages \
  -X POST -f "source[branch]=gh-pages" -f "source[path]=/" 2>/dev/null || echo "(pages already on or enabling)"

echo "LINK: https://ederson-shaw.github.io/civitai-library/"
