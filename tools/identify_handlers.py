#!/usr/bin/env python3
"""
Script to identify tasks that should be converted to handlers.

This script analyzes Ansible tasks and identifies patterns that indicate
a task should be converted to a handler instead.

Common patterns:
- Tasks with "restart" in the name
- Tasks with "reload" in the name  
- Tasks that use kolla_container with action: restart_container
- Tasks that use systemd module with state: restarted/reloaded
- Tasks executed conditionally based on config changes

Usage:
    python tools/identify_handlers.py --output handlers-report.txt
    python tools/identify_handlers.py --role keystone --output keystone-handlers.txt
"""

import argparse
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


class HandlerIdentifier:
    """Identify tasks that should be handlers."""

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.ansible_path = self.base_path / "ansible"
        self.candidates = []
        self.stats = defaultdict(int)

    def find_yaml_files(self, role: str = None) -> List[Path]:
        """Find task YAML files."""
        if role:
            pattern = f"roles/{role}/tasks/**/*.yml"
        else:
            pattern = "roles/*/tasks/**/*.yml"
        
        return sorted(self.ansible_path.glob(pattern))

    def is_handler_candidate(self, task: Dict, file_path: Path) -> Tuple[bool, str]:
        """Check if task should be a handler."""
        if not isinstance(task, dict):
            return False, ""

        reasons = []

        # Check task name
        name = task.get("name", "").lower()
        if any(keyword in name for keyword in ["restart", "reload", "reconfigure", "stop and start"]):
            reasons.append(f"Name contains action keyword: '{name}'")

        # Check for kolla_container restart actions
        if "kolla_container" in task:
            container_config = task["kolla_container"]
            if isinstance(container_config, dict):
                action = container_config.get("action", "")
                if any(a in action for a in ["restart", "stop", "start"]):
                    reasons.append(f"kolla_container action: {action}")

        # Check for systemd restart/reload
        if "systemd" in task or "service" in task:
            module = "systemd" if "systemd" in task else "service"
            config = task[module]
            if isinstance(config, dict):
                state = config.get("state", "")
                if state in ["restarted", "reloaded"]:
                    reasons.append(f"{module} state: {state}")

        # Check if task has when condition with config change patterns
        when_clause = task.get("when", "")
        if isinstance(when_clause, str):
            if any(pattern in when_clause.lower() for pattern in 
                   ["changed", "modified", "config", "update"]):
                reasons.append(f"Conditional on change: {when_clause}")

        # Check for docker_container (legacy)
        if "docker_container" in task:
            container_config = task["docker_container"]
            if isinstance(container_config, dict):
                state = container_config.get("state", "")
                if state in ["restarted", "started"]:
                    reasons.append(f"docker_container state: {state}")

        return len(reasons) > 0, "; ".join(reasons)

    def analyze_file(self, file_path: Path) -> List[Dict]:
        """Analyze a file for handler candidates."""
        candidates = []

        try:
            with open(file_path, "r") as f:
                content = yaml.safe_load(f)

            if not isinstance(content, list):
                return candidates

            for idx, task in enumerate(content):
                is_candidate, reason = self.is_handler_candidate(task, file_path)
                if is_candidate:
                    task_name = task.get("name", f"Task #{idx}")
                    
                    # Try to find the line number (approximate)
                    with open(file_path, "r") as f:
                        lines = f.readlines()
                        line_num = 0
                        for i, line in enumerate(lines):
                            if task_name in line or (f"- name:" in line and i < len(lines) - 1):
                                line_num = i + 1
                                break

                    candidates.append({
                        "file": str(file_path.relative_to(self.base_path)),
                        "task": task_name,
                        "line": line_num,
                        "reason": reason,
                        "role": file_path.parts[-3],  # Extract role name
                    })
                    self.stats["total_candidates"] += 1
                    self.stats[file_path.parts[-3]] += 1  # Count per role

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return candidates

    def generate_report(self, output_file: str = None):
        """Generate a report of handler candidates."""
        yaml_files = self.find_yaml_files()
        
        print(f"Analyzing {len(yaml_files)} task files...")

        for file_path in yaml_files:
            candidates = self.analyze_file(file_path)
            self.candidates.extend(candidates)

        # Generate report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("HANDLER CANDIDATES REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"\nTotal candidates found: {len(self.candidates)}")
        report_lines.append(f"\nTop 10 roles with most candidates:")
        
        sorted_roles = sorted(self.stats.items(), key=lambda x: x[1], reverse=True)
        for role, count in sorted_roles[:10]:
            if role != "total_candidates":
                report_lines.append(f"  - {role}: {count}")

        report_lines.append("\n" + "=" * 80)
        report_lines.append("DETAILED CANDIDATES")
        report_lines.append("=" * 80)

        # Group by role
        by_role = defaultdict(list)
        for candidate in self.candidates:
            by_role[candidate["role"]].append(candidate)

        for role in sorted(by_role.keys()):
            report_lines.append(f"\n### Role: {role}")
            report_lines.append("-" * 80)
            
            for candidate in by_role[role]:
                report_lines.append(f"\nFile: {candidate['file']}:{candidate['line']}")
                report_lines.append(f"Task: {candidate['task']}")
                report_lines.append(f"Reason: {candidate['reason']}")
                report_lines.append("")

        report = "\n".join(report_lines)

        if output_file:
            with open(output_file, "w") as f:
                f.write(report)
            print(f"\n✓ Report written to {output_file}")
        else:
            print(report)

    def suggest_conversion(self, candidate: Dict) -> str:
        """Suggest how to convert a task to a handler."""
        task_name = candidate["task"]
        
        # Generate handler name (simplified)
        handler_name = task_name.replace("Restart", "restart").replace("Reload", "reload")
        handler_name = re.sub(r'\s+container.*', '', handler_name).strip()
        
        suggestion = f"""
# Original task (in {candidate['file']}):
# {task_name}

# Suggested conversion:

# 1. Add to handlers/main.yml:
handlers:
  - name: {handler_name}
    # ... original task content ...

# 2. Replace task with notify:
- name: Copy configuration
  template:
    src: config.j2
    dest: /etc/config
  notify: {handler_name}
"""
        return suggestion


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Identify handler candidates in Kolla-Ansible")
    parser.add_argument("--role", help="Analyze specific role only")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--top", type=int, default=20, help="Show top N candidates")

    args = parser.parse_args()

    identifier = HandlerIdentifier()
    identifier.generate_report(output_file=args.output)


if __name__ == "__main__":
    main()
