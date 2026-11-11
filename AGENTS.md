# AGENTS.md

Instructions for coding agents working on this repository.

## A preset change reaches every repository at once

Every repository on the forge extends these presets, and Renovate reads them
afresh on each run: a broken preset stops Renovate everywhere. Run
`./scripts/check.sh` before pushing; CI runs the same script, and `main`
accepts nothing it has not passed.

A rule belongs here only when more than one repository uses it. A rule for one
repository stays in that repository's `renovate.json`.

## Keep it publishable

The repository is private but kept as if it were public: no host name,
address, user name or absolute home path goes into a commit, comment or
document. Write `<your-forge>` or `~/…` instead.
