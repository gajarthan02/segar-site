#!/usr/bin/env bash
# Build the site and publish dist/ to the gh-pages branch (GitHub Pages).
set -euo pipefail
cd "$(dirname "$0")"
npx astro build
cd dist
rm -rf .git
git init -q -b gh-pages
git add -A
git commit -qm "Deploy $(date -u +%Y-%m-%dT%H:%MZ)"
git push -qf "$(git -C .. remote get-url origin)" gh-pages
rm -rf .git
echo "Published to gh-pages."
