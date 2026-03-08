---
name: init
description: "Set up atlas for first-time use — creates the project registry, registers the session hook, and scans for git repos to register. Invoke when atlas is not yet configured, no registry exists, the user wants to start using atlas, or needs to re-scan for projects. Do NOT trigger for managing already-registered projects (use atlas:project-manager) or for looking up project info."
argument-hint: "[--scan <path>]"
---

# Atlas Initialization

Set up atlas for first-time use: create directories, register the session hook, discover and register projects.

## Parse Arguments

Parse `$ARGUMENTS`:
- `--scan <path>`: directory to scan for projects (default: cwd)

## Step 1: Create Directories and Registry

```bash
mkdir -p ~/.claude/atlas/cache/projects/
```

If `~/.claude/atlas/registry.yaml` does not exist, create it:

```yaml
# Atlas project registry — maps project slugs to filesystem paths.
# Managed by atlas:project-manager. See knowledge/schema.md for format.

projects:
```

Leave existing registry untouched.

## Step 2: Register SessionStart Hook

Plugin SessionStart hooks don't surface output due to bug #16538. Register directly in `~/.claude/settings.local.json` as a workaround.

1. Resolve the plugin root (ancestor directory containing `.claude-plugin/plugin.json`). The hook script is at `<plugin-root>/hooks/scripts/session-start.py`.
2. Read `~/.claude/settings.local.json` (create `{}` if missing).
3. Add the hook idempotently — check if a hook with that command already exists before adding:

```bash
jq --arg script "python3 <ABSOLUTE_PATH>/hooks/scripts/session-start.py" '
  .hooks //= {} |
  .hooks.SessionStart //= [] |
  if (.hooks.SessionStart | map(select(.hooks[]?.command == $script)) | length) > 0
  then .
  else .hooks.SessionStart += [{
    "matcher": "*",
    "hooks": [{"type": "command", "command": $script, "timeout": 5}]
  }]
  end
' ~/.claude/settings.local.json > /tmp/atlas-settings.json \
  && mv /tmp/atlas-settings.json ~/.claude/settings.local.json
```

## Step 3: Scan for Projects

Scan the target directory for git repos up to 3 levels deep:

```bash
find <scan-path> -maxdepth 3 -name ".git" -type d 2>/dev/null
```

For each repo found, collect:
- **path**: parent of `.git/`
- **slug**: directory name as lowercase kebab-case
- **repo**: remote origin URL from `.git/config`
- **has atlas.yaml**: whether `<path>/.claude/atlas.yaml` exists

Present as a table, then ask the user (via `AskUserQuestion`): Register all (default) / Let me choose / Skip.

## Step 4: Register Selected Projects

For each project to register, append to `~/.claude/atlas/registry.yaml`:

```yaml
  <slug>:
    path: <path>
    repo: <repo-url>
```

Handle the project config:
- **`.claude/atlas.yaml` exists** — cache to `~/.claude/atlas/cache/projects/<slug>.yaml` (prepend `_cache_meta`). Warn if `summary` is missing.
- **Missing** — offer to create a minimal one: auto-detect `name` from `package.json`/`Cargo.toml`/`build.gradle`/directory name, ask for `summary` (<100 chars), auto-detect `tags` from language files, guess CI link from repo URL. Write it and cache.

## Output

```
Atlas initialized!
  Registry:           ~/.claude/atlas/registry.yaml
  Projects registered: N
  Hook registered:    yes (in ~/.claude/settings.local.json)

  Next steps:
  - Start a new Claude session to activate the session hook
  - Use atlas:project-manager to add more projects
  - Use atlas:project-manager edit <slug> to customize configs
```
