#!/usr/bin/env bash
# Release gate: every preset and renovate.json must pass Renovate's own
# validator. CI (.github/workflows/ci.yml) runs exactly this script.
#
# The validator comes from npm when node is installed (CI's job image has it),
# otherwise from Renovate's container image through podman.
set -euo pipefail
cd "$(dirname "$0")/.."

# renovate: datasource=npm depName=renovate
RENOVATE_VERSION=44.216.6

mapfile -t configs < <(git ls-files '*.json')

if command -v npx > /dev/null; then
  npx --yes --package "renovate@$RENOVATE_VERSION" -- \
    renovate-config-validator --strict --no-global "${configs[@]}"
elif command -v podman > /dev/null; then
  podman run --rm --network=host -v "$PWD:/repo:ro,z" -w /repo \
    --entrypoint renovate-config-validator \
    "docker.io/renovate/renovate:$RENOVATE_VERSION" --strict --no-global "${configs[@]}"
else
  echo "FAIL: neither npx nor podman is installed" >&2
  exit 1
fi
