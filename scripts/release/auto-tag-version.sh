#!/bin/bash
set -euo pipefail

FIRST_LINE=$(echo "$COMMIT_MSG" | head -n 1)

git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

if [[ "$FIRST_LINE" == release:* ]]; then
BUMP="patch"
if [[ "$FIRST_LINE" =~ \((major|minor|patch)\)$ ]]; then
    BUMP="${BASH_REMATCH[1]}"
fi

LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
V_NUM="${LATEST_TAG#v}"
IFS='.' read -r -a VERSION_PARTS <<< "$V_NUM"
MAJOR="${VERSION_PARTS[0]:-0}"
MINOR="${VERSION_PARTS[1]:-0}"
PATCH="${VERSION_PARTS[2]:-0}"

if [ "$BUMP" == "major" ]; then
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
elif [ "$BUMP" == "minor" ]; then
    MINOR=$((MINOR + 1))
    PATCH=0
else
    PATCH=$((PATCH + 1))
fi

NEW_TAG="v${MAJOR}.${MINOR}.${PATCH}"
git tag "$NEW_TAG"
git push origin "$NEW_TAG"
gh release create "$NEW_TAG" --title "$NEW_TAG" --generate-notes

elif [[ "$FIRST_LINE" == tag:* ]]; then
TAG_NAME=$(echo "$FIRST_LINE" | sed 's/^tag:[[:space:]]*//')
git tag "$TAG_NAME"
git push origin "$TAG_NAME"
fi
