#!/usr/bin/env bash
# Publish only after build/package verification has succeeded.
set -euo pipefail

tag=$1
assets=$2
[[ -f "$assets/SHA256SUMS" && -f "$assets/release.json" ]]
(cd "$assets" && sha256sum --check SHA256SUMS)

# A failed upload leaves a draft that the same tag's rerun can complete.
if draft=$(gh release view "$tag" --json isDraft --jq .isDraft 2>/dev/null); then
    if [[ "$draft" != true ]]; then
        echo "Release $tag is already published; refusing to replace its assets." >&2
        exit 1
    fi
else
    gh release create "$tag" --draft --verify-tag --title "$tag" --generate-notes
fi
gh release upload "$tag" "$assets"/* --clobber
prerelease=false
[[ "$tag" != *-* ]] || prerelease=true
gh release edit "$tag" --draft=false --prerelease="$prerelease"
