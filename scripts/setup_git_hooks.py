#!/usr/bin/env python3
"""
Git Hooks Setup Script for WikiRace

This script installs git hooks to automatically update documentation
when changes are committed to the repository.

Usage:
    python scripts/setup_git_hooks.py
"""

import os
import shutil
import stat
from pathlib import Path

def setup_git_hooks():
    """Set up git hooks for automatic documentation updates"""
    project_root = Path(__file__).parent.parent
    hooks_source_dir = project_root / ".githooks"
    git_hooks_dir = project_root / ".git" / "hooks"
    
    # Check if we're in a git repository
    if not git_hooks_dir.parent.exists():
        print("❌ Not in a git repository. Git hooks not installed.")
        return False
    
    # Create hooks directory if it doesn't exist
    git_hooks_dir.mkdir(exist_ok=True)
    
    # Check if source hooks exist
    if not hooks_source_dir.exists():
        print("❌ Source hooks directory not found.")
        return False
    
    installed_hooks = []
    
    # Install each hook
    for hook_file in hooks_source_dir.iterdir():
        if hook_file.is_file():
            dest_path = git_hooks_dir / hook_file.name
            
            # Copy the hook
            shutil.copy2(hook_file, dest_path)
            
            # Make it executable
            current_mode = dest_path.stat().st_mode
            dest_path.chmod(current_mode | stat.S_IEXEC)
            
            installed_hooks.append(hook_file.name)
            print(f"✅ Installed {hook_file.name} hook")
    
    if installed_hooks:
        print(f"\n🎉 Successfully installed {len(installed_hooks)} git hook(s):")
        for hook in installed_hooks:
            print(f"   - {hook}")
        
        print("\n📋 These hooks will automatically:")
        print("   - Update .cursorrules file when project changes")
        print("   - Keep documentation synchronized with code")
        print("   - Add updated documentation to commits")
        
        print("\n💡 To manually update context: python scripts/update_context.py")
        print("💡 To check if update needed: python scripts/update_context.py --check")
        
        return True
    else:
        print("❌ No hooks were installed.")
        return False

def main():
    """Main entry point"""
    print("🔧 WikiRace Git Hooks Setup")
    print("=" * 40)
    
    if setup_git_hooks():
        print("\n✅ Git hooks setup complete!")
    else:
        print("\n❌ Git hooks setup failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
