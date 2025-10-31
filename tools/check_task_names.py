#!/usr/bin/env python3
"""
Pre-commit hook to check that Ansible tasks have descriptive names.

This ensures that import_tasks, include_tasks, import_role, and include_role
all have descriptive names, which is required after fixing unnamed-task issue.
"""

import sys
import yaml
from pathlib import Path


def check_file(file_path: Path) -> tuple[bool, list[str]]:
    """Check if file has unnamed tasks."""
    errors = []
    
    try:
        with open(file_path, 'r') as f:
            content = yaml.safe_load(f)
        
        if not isinstance(content, list):
            return True, []
        
        for idx, task in enumerate(content):
            if not isinstance(task, dict):
                continue
            
            # Check if task uses import/include without name
            task_modules = ['import_tasks', 'include_tasks', 'import_role', 'include_role']
            has_unnamed_import = any(module in task for module in task_modules)
            has_name = 'name' in task
            
            if has_unnamed_import and not has_name:
                module_name = next((m for m in task_modules if m in task), 'unknown')
                errors.append(
                    f"Line ~{idx * 3 + 1}: Task uses '{module_name}' without a name"
                )
    
    except yaml.YAMLError as e:
        errors.append(f"YAML parsing error: {e}")
    except Exception as e:
        errors.append(f"Error: {e}")
    
    return len(errors) == 0, errors


def main():
    """Main entry point."""
    files_to_check = sys.argv[1:]
    
    if not files_to_check:
        print("No files to check")
        return 0
    
    all_passed = True
    
    for file_path in files_to_check:
        path = Path(file_path)
        if not path.exists():
            continue
        
        passed, errors = check_file(path)
        
        if not passed:
            all_passed = False
            print(f"\n❌ {file_path}:")
            for error in errors:
                print(f"  {error}")
    
    if not all_passed:
        print("\n❌ Some tasks are missing names. Please add descriptive names.")
        print("   Use: python3 tools/fix_ansible_lint.py --fix")
        return 1
    
    print("✓ All tasks have proper names")
    return 0


if __name__ == "__main__":
    sys.exit(main())
