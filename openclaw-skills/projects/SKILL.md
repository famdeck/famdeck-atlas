---
name: projects
description: "Manage the atlas project registry — list, add, show, edit, remove, link, and refresh projects. Use whenever the user wants to work with registered projects: view what's registered, add or remove a project, update its config or links, or refresh caches. Do NOT use for code exploration across projects or for initializing atlas for the first time."
metadata: {"openclaw":{"emoji":"🗺️"}}
---

# Atlas Project Management

Manage the central project registry and per-project configs.

## Parse Arguments

Parse `$ARGUMENTS` for subcommand and options:

| Subcommand | Syntax | Description |
|---|---|---|
| `list` (default) | `[--group <name>] [--tag <name>]` | List all projects, optionally filtered |
| `add` | `[--path <path>] [slug]` | Register a project |
| `show` | `[slug]` | Show project details |
| `edit` | `[slug]` | Edit project config |
| `remove` | `<slug>` | Remove from registry |
| `link` | `<name> <url> [--project <slug>]` | Add/update a link |
| `refresh` | `[slug]` | Refresh cache (all or one) |

Slug can be positional or via `--project <slug>`.

## File Paths

- **Registry**: `~/.claude/atlas/registry.yaml`
- **Cache**: `~/.claude/atlas/cache/projects/<slug>.yaml`
- **Project config**: `<project-path>/.claude/atlas.yaml`

## list (default)

1. Read registry, then read each project's cached config from `~/.claude/atlas/cache/projects/<slug>.yaml`.
2. Apply `--group` / `--tag` filters if given.
3. If most caches are missing, suggest running `refresh`.

Output as table: Slug, Group, Tags, Summary.

## add

1. Determine path (`--path` or cwd). Verify `.git/` exists.
2. Auto-detect repo URL from `.git/config` remote origin.
3. Suggest slug from directory name (lowercase kebab-case). Confirm with user. Warn if slug already exists.
4. Append to registry:
   ```yaml
   <slug>:
     path: <path>
     repo: <repo-url>
   ```
5. Handle `.claude/atlas.yaml`:
   - **Exists** — validate `summary` (<100 chars), cache it
   - **Missing** — offer to create with auto-detected name/tags/links, then cache

Confirm: `Registered: <slug> → <path>`

## show

1. Resolve slug (from arg or detect from cwd via registry path matching).
2. Read registry entry + cached config.
3. Display: name, slug, path, repo, group, tags, links, notes.

## edit

1. Resolve slug. Read `<project-path>/.claude/atlas.yaml` from disk (not cache).
2. Present current content, ask what to change.
3. Apply edits, refresh cache.

## remove

1. Require slug. Confirm with user.
2. Remove from `registry.yaml`. Delete cache file if present.

## link

1. Resolve project slug (from arg or cwd).
2. Read `.claude/atlas.yaml`, add/update entry under `links:`.
3. Refresh cache.

## refresh

1. If slug given, refresh that project only; otherwise refresh all.
2. For each: check path exists, read `.claude/atlas.yaml`, update cache with `_cache_meta`. Warn on missing paths or configs.

Output: table of projects with status (cached / path not found / no config).

## Schema Reference

### Registry (`registry.yaml`)

```yaml
projects:
  <slug>:                        # lowercase kebab-case, unique
    path: <absolute-or-tilde>    # required, ~ expansion supported
    repo: <url>                  # required, HTTPS or SSH
    additional_paths: [<path>]   # optional, monorepo children
```

### Project Config (`atlas.yaml`)

```yaml
name: <string>              # required, human-readable
summary: <string>           # required, <100 chars
tags: [<string>, ...]       # optional
group: <string>             # optional
links:                      # optional
  docs: <url>
  ci: <url>
docs:                       # optional
  context7_id: <string>
  local: <path>
  readme: <path>
notes: |                    # optional, free-form
  Build: npm run build
metadata:                   # optional, arbitrary key-value
  team: <string>
```

### Cache (`cache/projects/<slug>.yaml`)

```yaml
_cache_meta:
  source: <absolute-path>
  cached_at: "<ISO-8601>"
  repo: <repo-url>
# ... copy of atlas.yaml fields
```

### Path Matching (project detection from cwd)

1. Exact: `$PWD == project.path`
2. Child: `$PWD` starts with `project.path/`
3. Additional paths: same rules
4. Deepest match wins
