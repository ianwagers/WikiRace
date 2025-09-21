# WikiRace Scripts

This directory contains utility scripts for maintaining the WikiRace project.

## Documentation Automation

### `update_context.py`
Automatically updates the `.cursorrules` file with current project information.

**Usage:**
```bash
# Update context if needed
python scripts/update_context.py

# Check if update is needed (useful for CI/CD)
python scripts/update_context.py --check
```

**Features:**
- Analyzes project structure and generates statistics
- Updates project context based on current codebase
- Detects recent git changes
- Backs up existing context file before updating

### `setup_git_hooks.py`
Installs git hooks to automatically update documentation on commits.

**Usage:**
```bash
python scripts/setup_git_hooks.py
```

**What it does:**
- Installs a pre-commit hook that runs `update_context.py`
- Automatically adds updated documentation to commits
- Ensures documentation stays synchronized with code changes

## Other Scripts

### `install_pyqt6.py`
Installs PyQt6 dependencies for the WikiRace application.

### `setup_environment.py`
Sets up the development environment and virtual environment.

## Automation Benefits

With these scripts installed:

1. **Automatic Documentation**: The `.cursorrules` file is automatically updated whenever significant changes are made to the project
2. **Git Integration**: Documentation updates are automatically included in commits
3. **Project Statistics**: Real-time statistics about the codebase are maintained
4. **Consistency**: Ensures documentation always reflects the current state of the project

## Manual Usage

Even with automation, you can manually run the update script:

```bash
# Force update the context
python scripts/update_context.py

# Check if an update is needed without updating
python scripts/update_context.py --check
```

The git hook will automatically run before each commit, but you can disable it by:

```bash
# Skip hooks for a specific commit
git commit --no-verify -m "Your commit message"
```
