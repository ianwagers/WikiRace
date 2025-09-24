# Contributing to WikiRace

## Rules and Guidelines
All behavior and guidelines are now encoded in `.cursor/rules/*.mdc` files.

## Rule Structure
- `00-core-project.mdc` - Always applies (project overview)
- `10-ui-pyqt.mdc` - Auto-attaches to `src/gui/**` and `src/logic/ThemeManager.py`
- `20-networking-socketio.mdc` - Auto-attaches to `src/logic/Network.py` and `server/socket_handlers.py`
- `30-api-fastapi.mdc` - Auto-attaches to `server/**` except socket handlers
- `31-deploy-uvicorn.mdc` - Auto-attaches to `server/start_server.py` and deployment docs
- `40-project-structure.mdc` - Auto-attaches to repo root and folders
- `50-testing-policy.mdc` - Auto-attaches to `tests/**` only (default OFF elsewhere)
- `60-contribution-style.mdc` - Auto-attaches to changed files
- `70-debug-logging.mdc` - Auto-attaches to `src/logic/**` and `server/**`
- `80-performance-and-jank.mdc` - Auto-attaches to `src/gui/**`
- `99-readme-short.mdc` - Manual attach

## Using Rules in Cursor
- Attach `00-core-project.mdc` and relevant scoped rules with @Cursor Rules
- Rules auto-attach based on file paths and globs
- Verify auto-attached rules show up in the Rules panel

## Development Philosophy
**PREFER DEBUGGING AND CODE CHANGES OVER TESTING SCRIPTS**
- Focus on fixing issues directly in the codebase
- Use existing functionality to debug problems
- Make targeted code changes to resolve issues
- When debugging, modify the actual application code to add logging, error handling, or fixes
