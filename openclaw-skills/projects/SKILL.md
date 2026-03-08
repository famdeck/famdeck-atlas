---
name: projects
description: "Manage the atlas project registry — add, list, show, edit, remove, link, and refresh projects. Triggers: 'list projects', 'show project', 'add project', 'register project', 'remove project', 'project details', 'project info', 'refresh projects', 'project links', 'what projects', 'my projects', 'atlas projects'. Use when viewing, searching, or modifying the project registry."
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

## Subcommand: list

1. Read registry, then read each project's cached config from `~/.claude/atlas/cache/projects/<slug>.yaml`.
2. Apply `--group` / `--tag` filters if given.
3. If most caches are empty, suggest `/projects refresh`.

Output as table: Slug, Group, Tags, Summary.

## Subcommand: add

1. Determine path (`--path` or cwd). Verify `.git/` exists.
2. Auto-detect repo URL from `.git/config` remote origin.
3. Suggest slug from directory name (lowercase kebab-case), confirm with user. Warn if slug already exists.
4. Append to registry:
   ```yaml
   <slug>:
     path: <path>
     repo: <repo-url>
   ```
5. If `.claude/atlas.yaml` exists: validate `summary` (<100 chars), cache it. If missing: offer to create with auto-detected name, summary, tags, links — then cache.

Confirm: `Registered: <slug> -> <path>`

## Subcommand: show

1. Resolve slug (from arg or detect from cwd via registry path matching).
2. Read registry entry + cached config.
3. Display: name, slug, path, repo, group, tags, links, notes.

## Subcommand: edit

1. Resolve slug. Read `<project-path>/.claude/atlas.yaml` from disk (not cache).
2. Present current content, ask what to change.
3. Apply edits, then refresh cache.

## Subcommand: remove

1. Require slug. Confirm with user.
2. Remove from `registry.yaml`. Delete cache file if present.

## Subcommand: link

1. Resolve project slug.
2. Read `.claude/atlas.yaml`, add/update entry under `links:`.
3. Refresh cache.

## Subcommand: refresh

1. If slug given, refresh that project only; otherwise refresh all.
2. For each: check path exists, read `.claude/atlas.yaml`, update cache with `_cache_meta`. Warn on missing paths or configs.

Output: list of projects with status (cached / path not found / no config).

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
