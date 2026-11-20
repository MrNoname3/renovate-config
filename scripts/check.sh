#!/usr/bin/env bash
# Release gate: every preset and renovate.json must pass Renovate's own
# validator, as repository config. CI (.github/workflows/ci.yml) runs exactly
# this script, inside Renovate's image, where the validator is installed.
#
# Elsewhere the validator comes from npm when npx is installed, otherwise from
# Renovate's image through podman; both at the version below.
set -euo pipefail
cd "$(dirname "$0")/.."

# renovate: datasource=docker depName=docker.io/renovate/renovate
RENOVATE_VERSION=44.251.0

mapfile -t configs < <(git ls-files '*.json')
args=(--strict --no-global "${configs[@]}")

if command -v renovate-config-validator > /dev/null; then
  renovate-config-validator --version
  renovate-config-validator "${args[@]}"
elif command -v npx > /dev/null; then
  npx --yes --package "renovate@$RENOVATE_VERSION" -- renovate-config-validator "${args[@]}"
elif command -v podman > /dev/null; then
  podman run --rm -v "$PWD:/repo:ro,z" -w /repo --entrypoint renovate-config-validator \
    "docker.io/renovate/renovate:$RENOVATE_VERSION" "${args[@]}"
else
  echo "FAIL: none of renovate-config-validator, npx or podman is installed" >&2
  exit 1
fi
