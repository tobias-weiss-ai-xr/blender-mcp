# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-16
**Commit:** 7636d13
**Branch:** main

## OVERVIEW

BlenderMCP connects Blender to Claude AI through the Model Context Protocol (MCP). Two-component architecture: a Blender addon (socket server) + an MCP server (FastMCP).

## STRUCTURE

```
blender-mcp/
├── addon.py              # Blender addon - socket server + all command handlers (2635 lines)
├── main.py               # CLI entry point
├── src/blender_mcp/
│   ├── server.py         # FastMCP server - all MCP tools exposed (1185 lines)
│   ├── telemetry.py      # Anonymous usage telemetry
│   └── telemetry_decorator.py
└── assets/               # Documentation images
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add new MCP tool | `src/blender_mcp/server.py` | Add `@mcp.tool()` decorated function |
| Add new Blender command | `addon.py` → `_execute_command_internal()` | Register handler in dict |
| Fix socket issues | `addon.py` → `BlenderMCPServer` class | Server thread, client handler |
| Poly Haven integration | `addon.py` → `get_polyhaven_*` methods | Enabled via checkbox in Blender |
| Hyper3D/Sketchfab/Hunyuan | `addon.py` → respective handlers | Optional integrations |
| Telemetry changes | `src/blender_mcp/telemetry.py` | Supabase-backed |

## ARCHITECTURE

```
Claude Desktop/Cursor          Blender Application
       │                              │
       │  stdio                       │  TCP socket
       ▼                              ▼
┌─────────────────┐           ┌──────────────────┐
│  FastMCP Server │◄─────────►│ BlenderMCPServer │
│  (server.py)    │  :9876    │   (addon.py)     │
└─────────────────┘           └──────────────────┘
                                        │
                                        ▼
                                 Blender API (bpy)
```

**Protocol:** JSON over TCP. Commands: `{"type": "...", "params": {...}}`. Responses: `{"status": "success/error", "result": ...}`.

## CONVENTIONS

- **Package manager:** `uv` (not pip). Run: `uvx blender-mcp`
- **Entry point:** `blender_mcp.server:main` (defined in pyproject.toml)
- **Timeout:** 180s socket timeout (addon and server must match)
- **Response limiting:** Poly Haven limits to 20 assets per response
- **Threading:** Blender commands execute via `bpy.app.timers.register()` on main thread

## ANTI-PATTERNS (THIS PROJECT)

- **execute_blender_code is dangerous:** Allows arbitrary Python execution. ALWAYS save work before using.
- **Don't reconnect in send_command:** Let `get_blender_connection()` handle reconnection; invalidate socket on error instead
- **No CI/CD:** Manual releases via pyproject.toml version bump
- **No tests:** Project has no test suite

## UNIQUE STYLES

- **Telemetry decorator:** `@telemetry_tool("tool_name")` wraps all MCP tools for usage tracking
- **Optional integrations:** Poly Haven, Hyper3D, Sketchfab, Hunyuan3D are enabled via Blender UI checkboxes, not config
- **Blender addon pattern:** Uses `bpy.props` for UI, `bpy.app.timers` for thread-safe execution

## COMMANDS

```bash
# Run MCP server (for Claude Desktop/Cursor config)
uvx blender-mcp

# Install addon in Blender
# Edit > Preferences > Add-ons > Install... > select addon.py

# Build package
uv build

# Disable telemetry
DISABLE_TELEMETRY=true uvx blender-mcp
```

## ENVIRONMENT VARIABLES

| Variable | Default | Purpose |
|----------|---------|---------|
| `BLENDER_HOST` | localhost | Blender socket host |
| `BLENDER_PORT` | 9876 | Blender socket port |
| `DISABLE_TELEMETRY` | (unset) | Disable all telemetry |

## NOTES

- **Version:** 1.5.5 (in pyproject.toml and telemetry reads it)
- **Blender requirement:** 3.0+
- **Python requirement:** 3.10+
- **Free trial key embedded:** `RODIN_FREE_TRIAL_KEY` in addon.py for Hyper3D
- **No official website:** Per README, any website claiming to be official is unofficial
