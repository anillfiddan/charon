#!/bin/bash
# Charon sitesini derler ve GitHub Pages'e (anillfiddan/charon, gh-pages dalı) yayınlar.
set -e
cd "$(dirname "$0")"
export GH_TOKEN=$(gh auth token -u anillfiddan)
H=(-c credential.helper= -c "credential.helper=!gh auth git-credential")
ID=(-c user.name=anillfiddan -c user.email=anillfiddan@users.noreply.github.com)
python3 build.py >/dev/null
git add -A && (git "${ID[@]}" commit -q -m "Güncelleme $(date '+%d.%m.%Y %H:%M')" || true)
git "${H[@]}" push -q origin main
T=$(mktemp -d); cp -R site/. "$T"/; cd "$T"
git init -q -b gh-pages && git add -A && git "${ID[@]}" commit -q -m "Yayın $(date '+%d.%m.%Y %H:%M')"
git "${H[@]}" push -q -f https://github.com/anillfiddan/charon.git gh-pages
gh api -X POST repos/anillfiddan/charon/pages/builds >/dev/null
echo "Yayınlandı: https://anillfiddan.github.io/charon/ (1-2 dk içinde güncellenir)"
