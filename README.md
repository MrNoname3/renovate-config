# renovate-config

Shared [Renovate](https://docs.renovatebot.com/) presets for the repositories on
this forge. A repository's `renovate.json` extends one of them and keeps only
the rules that are its own.

| Preset | Extend with | What it holds |
|---|---|---|
| `default.json` | `local>MrNoname3/renovate-config` | `base`, plus automerge of patch, pin and digest updates and of minor GitHub Actions updates, after a 3-day soak |
| `base.json` | `local>MrNoname3/renovate-config:base` | `config:recommended`, Actions pinned by digest, the dependency dashboard and the `dependencies` label; no automerge |
| `ansible.json` | `local>MrNoname3/renovate-config:ansible` | the regex manager for `# renovate:` comments in role defaults |

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "local>MrNoname3/renovate-config",
    "local>MrNoname3/renovate-config:ansible"
  ]
}
```

A rule in the repository's own `packageRules` comes after the preset's, so it
wins: `"automerge": false` on a file pattern takes those files out of the
automerge.

The Renovate bot account reads this repository when it resolves a preset, so it
needs read access here. A change to a preset takes effect in every repository on
Renovate's next run; nothing has to be copied.

`./scripts/check.sh` runs Renovate's validator over every JSON file here, with
`npx` or, without node, Renovate's container image through podman. CI runs the
same script, and `main` requires it to pass.

## Labels

The labels these presets put on pull requests (`labels`, `addLabels`) must
exist in the repository: on Gitea, Renovate does not create them.
repo-template's `forge.toml` lists them, and its Sync workflow creates them in
every repository with a `renovate.json`.
