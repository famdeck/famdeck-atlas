#!/usr/bin/env python3
"""Atlas PreToolUse hook: hint when Glob/Grep searches outside the current project.

When Claude tries to search directories above the project root, suggest using
Atlas MCP tools instead. Does NOT block — just outputs a hint (exit 0).
"""
import json
import sys
from pathlib import Path

ATLAS_DIR = Path.home() / ".claude" / "atlas"
REGISTRY = ATLAS_DIR / "registry.yaml"


def count_registered() -> int:
    """Quick count of registered projects."""
    if not REGISTRY.is_file():
        return 0
    return REGISTRY.read_text(encoding="utf-8").count("\n    path:")


def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_input = input_data.get("tool_input", {})

    # Glob uses 'path', Grep uses 'path' too
    search_path = tool_input.get("path", "")
    if not search_path:
        return  # Using cwd default — fine

    cwd = Path.cwd().resolve()
    search = Path(search_path).expanduser().resolve()

    # If searching within the current project, no hint needed
    try:
        search.relative_to(cwd)
        return
    except ValueError:
        pass

    # Also OK if cwd is under the search path by only 1 level (searching project root from subdir)
    try:
        rel = cwd.relative_to(search)
        if len(rel.parts) <= 1:
            return
    except ValueError:
        pass

    # Searching outside the project — hint toward Atlas
    n = count_registered()
    if n > 0:
        print(
            f"Atlas has {n} registered projects — consider using "
            f"atlas_search_projects(query=\"...\") instead of filesystem search "
            f"to find project paths. For issues use /relay:issue."
        )


if __name__ == "__main__":
    main()
