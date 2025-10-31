#!/usr/bin/env python3
"""
Script to automatically fix ansible-lint issues in Kolla-Ansible.

This script addresses the following issues:
1. unnamed-task: Adds descriptive names to tasks without names
2. no-changed-when: Adds changed_when to command/shell tasks
3. no-handler: Identifies tasks that should be handlers

Usage:
    python tools/fix_ansible_lint.py --check  # Dry run
    python tools/fix_ansible_lint.py --fix    # Apply fixes
    python tools/fix_ansible_lint.py --stats  # Show statistics
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


class AnsibleLintFixer:
    """Fix common ansible-lint issues in Kolla-Ansible."""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.stats = defaultdict(int)
        self.base_path = Path(__file__).parent.parent
        self.ansible_path = self.base_path / "ansible"

    def find_yaml_files(self) -> List[Path]:
        """Find all YAML files in ansible directory."""
        patterns = ["**/*.yml", "**/*.yaml"]
        files = []
        for pattern in patterns:
            files.extend(self.ansible_path.rglob(pattern))
        return sorted(files)

    def generate_task_name(self, task: Dict) -> str:
        """Generate descriptive name based on task module."""
        # Map modules to descriptive prefixes
        module_prefixes = {
            "import_tasks": "Import",
            "include_tasks": "Include",
            "import_role": "Import role",
            "include_role": "Include role",
            "set_fact": "Set fact",
            "debug": "Debug",
            "assert": "Assert",
            "fail": "Fail",
            "block": "Execute block",
            "template": "Copy template",
            "copy": "Copy",
            "file": "Manage file",
            "command": "Run command",
            "shell": "Run shell",
            "service": "Manage service",
            "systemd": "Manage systemd service",
            "docker_container": "Manage container",
            "kolla_container": "Manage Kolla container",
            "wait_for": "Wait for",
            "stat": "Check file stat",
            "find": "Find files",
            "lineinfile": "Manage line in file",
            "replace": "Replace in file",
            "get_url": "Download",
            "git": "Manage git repository",
            "pip": "Install pip package",
            "package": "Install package",
            "apt": "Install apt package",
            "yum": "Install yum package",
            "dnf": "Install dnf package",
            "meta": "Meta",
        }

        # Find the module being used
        for module, prefix in module_prefixes.items():
            if module in task:
                value = task[module]
                
                # Generate descriptive name based on module
                if module in ["import_tasks", "include_tasks"]:
                    return f"{prefix} {value}"
                elif module in ["import_role", "include_role"]:
                    if isinstance(value, dict):
                        role_name = value.get("name", "unknown")
                    else:
                        role_name = value
                    return f"{prefix} {role_name}"
                elif module == "set_fact":
                    if isinstance(value, dict):
                        fact_names = ", ".join(value.keys())
                        return f"{prefix} {fact_names}"
                    return f"{prefix}"
                elif module == "meta":
                    return f"{prefix} {value}"
                elif module in ["template", "copy"]:
                    if isinstance(value, dict):
                        dest = value.get("dest", "")
                        if dest:
                            dest_name = Path(dest).name
                            return f"{prefix} {dest_name}"
                return prefix

        # Default fallback
        return "Execute task"

    def fix_unnamed_tasks(self, content: str, file_path: Path) -> Tuple[str, int]:
        """Add names to tasks without names using regex."""
        fixes = 0
        lines = content.split("\n")
        modified_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            modified_lines.append(line)
            
            # Pattern: Line starts with "- " followed by an Ansible module (not "name:")
            # Common patterns: "- import_tasks:", "- include_tasks:", etc.
            if re.match(r'^(\s*)- (import_tasks|include_tasks|import_role|include_role|import_playbook):', line):
                # Get indentation
                indent_match = re.match(r'^(\s*)- ', line)
                base_indent = len(indent_match.group(1)) if indent_match else 0
                name_indent = base_indent + 2
                
                # Check if next line is NOT "name:"
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if not re.match(r'^\s*name:', next_line):
                        # Extract module and value
                        match = re.match(r'^.*- (import_tasks|include_tasks|import_role|include_role|import_playbook):\s*(.+?)$', line)
                        if match:
                            module = match.group(1)
                            value = match.group(2).strip()
                            # Remove quotes if present
                            value = value.strip('\'"')
                            
                            # Generate appropriate name
                            if module in ["import_tasks", "include_tasks"]:
                                task_name = f"Import {value}"
                            elif module in ["import_role", "include_role"]:
                                task_name = f"Include role {value}"
                            elif module == "import_playbook":
                                task_name = f"Import playbook {value}"
                            else:
                                task_name = f"Execute {module}"
                            
                            # Escape quotes in task_name for YAML
                            task_name_escaped = task_name.replace('"', '\\"')
                            
                            # Insert name line
                            name_line = " " * name_indent + f'name: "{task_name_escaped}"'
                            modified_lines.append(name_line)
                            fixes += 1

            i += 1

        if fixes > 0:
            self.stats["unnamed_tasks_fixed"] += fixes
            return "\n".join(modified_lines), fixes

        return content, 0

    def fix_no_changed_when(self, content: str, file_path: Path) -> Tuple[str, int]:
        """Add changed_when to command/shell tasks."""
        fixes = 0
        lines = content.split("\n")
        modified_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            modified_lines.append(line)
            
            # Check if this is a command or shell task
            if re.match(r'\s*-\s+(command|shell):', line):
                # Check if there's already a changed_when
                has_changed_when = False
                indent = len(line) - len(line.lstrip())
                
                # Look ahead for changed_when
                j = i + 1
                while j < len(lines) and len(lines[j]) > indent:
                    if "changed_when:" in lines[j]:
                        has_changed_when = True
                        break
                    if lines[j].strip().startswith("-"):
                        break
                    j += 1
                
                if not has_changed_when:
                    # Add changed_when: false (conservative approach)
                    indent_str = " " * (indent + 2)
                    modified_lines.append(f"{indent_str}changed_when: false")
                    fixes += 1
                    self.stats["no_changed_when_fixed"] += 1
            
            i += 1
        
        if fixes > 0:
            return "\n".join(modified_lines), fixes
        
        return content, 0

    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze a file for potential issues."""
        try:
            with open(file_path, "r") as f:
                content = f.read()

            issues = {
                "unnamed_tasks": 0,
                "no_changed_when": 0,
                "potential_handlers": 0,
            }

            # Count unnamed tasks (simplified)
            unnamed = len(re.findall(r'^\s*-\s+(import_tasks|include_tasks|import_role|include_role):', 
                                    content, re.MULTILINE))
            issues["unnamed_tasks"] = unnamed

            # Count command/shell without changed_when
            commands = re.findall(r'^\s*-\s+(command|shell):', content, re.MULTILINE)
            changed_whens = len(re.findall(r'changed_when:', content))
            issues["no_changed_when"] = max(0, len(commands) - changed_whens)

            # Identify potential handlers (tasks with notify or restart patterns)
            if "restart" in content.lower() or "reload" in content.lower():
                issues["potential_handlers"] += content.lower().count("restart")

            return issues

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return {}

    def process_file(self, file_path: Path) -> bool:
        """Process a single file."""
        try:
            with open(file_path, "r") as f:
                original_content = f.read()

            modified_content = original_content
            total_fixes = 0

            # Apply fixes
            modified_content, fixes = self.fix_unnamed_tasks(modified_content, file_path)
            total_fixes += fixes

            # Note: no_changed_when fix disabled for now as it needs more context
            # modified_content, fixes = self.fix_no_changed_when(modified_content, file_path)
            # total_fixes += fixes

            if total_fixes > 0:
                if not self.dry_run:
                    with open(file_path, "w") as f:
                        f.write(modified_content)
                    print(f"✓ Fixed {total_fixes} issues in {file_path}")
                else:
                    print(f"[DRY RUN] Would fix {total_fixes} issues in {file_path}")
                return True

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False

        return False

    def show_stats(self):
        """Show statistics about issues found."""
        print("\n" + "=" * 60)
        print("ANSIBLE-LINT ISSUES STATISTICS")
        print("=" * 60)

        yaml_files = self.find_yaml_files()
        print(f"\nTotal YAML files: {len(yaml_files)}")

        all_issues = defaultdict(int)
        files_with_issues = 0

        for file_path in yaml_files:
            issues = self.analyze_file(file_path)
            if any(issues.values()):
                files_with_issues += 1
                for key, value in issues.items():
                    all_issues[key] += value

        print(f"Files with issues: {files_with_issues}")
        print(f"\nIssues breakdown:")
        print(f"  - Unnamed tasks: {all_issues['unnamed_tasks']}")
        print(f"  - Command/shell without changed_when: {all_issues['no_changed_when']}")
        print(f"  - Potential handlers: {all_issues['potential_handlers']}")

        print("\n" + "=" * 60)

    def run(self, check_only: bool = False, show_stats: bool = False):
        """Run the fixer."""
        if show_stats:
            self.show_stats()
            return

        yaml_files = self.find_yaml_files()
        print(f"Found {len(yaml_files)} YAML files")

        if check_only:
            print("\n[CHECK MODE] Analyzing files...")
            self.show_stats()
        else:
            print("\n[FIX MODE] Processing files...")
            files_modified = 0
            for file_path in yaml_files:
                if self.process_file(file_path):
                    files_modified += 1

            print(f"\n✓ Modified {files_modified} files")
            print(f"✓ Fixed {sum(self.stats.values())} total issues")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fix ansible-lint issues in Kolla-Ansible")
    parser.add_argument("--check", action="store_true", help="Check only, don't modify files")
    parser.add_argument("--fix", action="store_true", help="Apply fixes to files")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")

    args = parser.parse_args()

    if not any([args.check, args.fix, args.stats]):
        parser.print_help()
        sys.exit(1)

    dry_run = args.check or args.dry_run
    fixer = AnsibleLintFixer(dry_run=dry_run)

    if args.stats:
        fixer.show_stats()
    else:
        fixer.run(check_only=args.check, show_stats=args.stats)


if __name__ == "__main__":
    main()
