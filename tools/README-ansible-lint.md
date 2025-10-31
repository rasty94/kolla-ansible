# Ansible-Lint Cleanup Tools

This directory contains tools to help fix ansible-lint warnings in Kolla-Ansible.

## Current Status (31 Oct 2025)

- **Total YAML files**: 1,176
- **Files with issues**: 736 (62.6%)
- **Unnamed tasks**: 997
- **Potential handlers**: 83
- **Commands without changed_when**: 0 ✅ ALREADY CLEAN!

## Quick Start

```bash
# 1. Activate virtual environment
cd /path/to/kolla-ansible
source venv/bin/activate  # or: venv/bin/python3

# 2. Check current status
python3 tools/fix_ansible_lint.py --stats

# 3. See what would be fixed (dry-run)
python3 tools/fix_ansible_lint.py --check

# 4. Apply fixes
python3 tools/fix_ansible_lint.py --fix

# 5. Identify handler candidates
python3 tools/identify_handlers.py --output handlers-report.txt

# 6. Verify fixes
ansible-lint ansible/

# 7. Run tests
tox -e linters
```

## Tools Description

### 1. fix_ansible_lint.py

Automatically fixes unnamed tasks by generating descriptive names based on the module used.

**Features:**
- Analyzes all YAML files in ansible/
- Generates contextual names for import_tasks, include_tasks, etc.
- Supports dry-run mode for safe testing
- Shows statistics and progress

**Usage:**
```bash
# Show statistics only
python3 tools/fix_ansible_lint.py --stats

# Dry run (show what would be fixed)
python3 tools/fix_ansible_lint.py --check

# Apply fixes
python3 tools/fix_ansible_lint.py --fix

# Fix specific role (not implemented yet)
# python3 tools/fix_ansible_lint.py --fix --role keystone
```

### 2. identify_handlers.py

Identifies tasks that should be converted to handlers based on common patterns.

**Patterns detected:**
- Tasks with "restart", "reload", "reconfigure" in name
- kolla_container with restart/stop/start actions
- systemd/service with restarted/reloaded state
- Tasks conditional on configuration changes

**Usage:**
```bash
# Generate full report
python3 tools/identify_handlers.py

# Save report to file
python3 tools/identify_handlers.py --output handlers-report.txt

# Analyze specific role
python3 tools/identify_handlers.py --role neutron --output neutron-handlers.txt

# Show top N candidates
python3 tools/identify_handlers.py --top 50
```

### 3. check_task_names.py

Pre-commit hook to ensure all tasks have descriptive names.

**Usage:**
```bash
# Check specific files
python3 tools/check_task_names.py ansible/roles/keystone/tasks/config.yml

# Used automatically by pre-commit
git commit -m "Fix tasks"  # Hook runs automatically
```

### 4. pre-commit-lint-check.sh

Custom pre-commit checks for Kolla-Ansible specific patterns.

**Checks:**
- Unnamed tasks in modified files
- Potential handlers (restart/reload patterns)
- Commands without changed_when

**Usage:**
```bash
# Run manually
./tools/pre-commit-lint-check.sh

# Used automatically by pre-commit
git commit  # Runs automatically
```

## Setting Up Pre-Commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files (first time)
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Update hooks to latest versions
pre-commit autoupdate
```

## Workflow

### Phase 1: Fix Unnamed Tasks (Week 1-2)

```bash
# 1. Baseline
python3 tools/fix_ansible_lint.py --stats > baseline.txt

# 2. Test on one role
python3 tools/fix_ansible_lint.py --check | grep "keystone"

# 3. Apply fixes
python3 tools/fix_ansible_lint.py --fix

# 4. Verify
ansible-lint ansible/roles/keystone/

# 5. Test deployment
kolla-ansible prechecks

# 6. Commit
git add ansible/roles/keystone/
git commit -m "Fix unnamed tasks in keystone role"
```

### Phase 2: Convert to Handlers (Week 3-4)

```bash
# 1. Identify candidates
python3 tools/identify_handlers.py --output handlers-report.txt

# 2. Review report
cat handlers-report.txt | less

# 3. Manual conversion (example for keystone)
# Edit ansible/roles/keystone/handlers/main.yml
# Edit ansible/roles/keystone/tasks/*.yml to use notify

# 4. Test
kolla-ansible deploy --tags keystone

# 5. Commit
git commit -m "Convert keystone tasks to handlers"
```

### Phase 3: Enable Lint Rules Progressively

```bash
# 1. Edit .ansible-lint
# Remove one rule from skip_list

# 2. Check what breaks
ansible-lint ansible/ 2>&1 | tee lint-errors.txt

# 3. Fix errors
# ... manual fixes or automated scripts ...

# 4. Verify
ansible-lint ansible/

# 5. Commit
git commit -m "Enable ansible-lint rule: unnamed-task"
```

## Testing

### Unit Tests
```bash
# Test the fix_ansible_lint.py tool
python3 -m pytest tests/test_fix_ansible_lint.py

# Test the identify_handlers.py tool
python3 -m pytest tests/test_identify_handlers.py
```

### Integration Tests
```bash
# Full linting suite
tox -e linters

# Ansible-lint only
tox -e ansible-lint

# Deployment test
kolla-ansible prechecks
kolla-ansible deploy --tags common,keystone
```

### Smoke Tests
```bash
# Check syntax
ansible-playbook --syntax-check ansible/site.yml

# Check inventory
ansible-inventory -i ansible/inventory/all-in-one --list

# Test connectivity
ansible -i ansible/inventory/all-in-one -m ping all
```

## Troubleshooting

### Tool fails with "yaml module not found"
```bash
# Install PyYAML
pip install pyyaml

# Or use venv python
venv/bin/python3 tools/fix_ansible_lint.py --stats
```

### Pre-commit hooks fail
```bash
# Update pre-commit
pre-commit autoupdate

# Clean and reinstall
pre-commit clean
pre-commit install

# Skip hooks temporarily (emergency only)
git commit --no-verify
```

### Ansible-lint shows errors after fixes
```bash
# Check which rules are failing
ansible-lint ansible/ --parseable

# Show only new errors (compare with baseline)
diff baseline.txt <(ansible-lint ansible/)

# Fix specific rule
ansible-lint --strict --profile=production ansible/
```

## Contributing

When adding new tools or improving existing ones:

1. Add docstrings and type hints
2. Include usage examples
3. Add tests
4. Update this README
5. Run linters: `tox -e linters`

## Related Documentation

- [Ansible-Lint Fixes Roadmap](../docs/ansible-lint-fixes.md)
- [Kolla-Ansible Contributing Guide](../CONTRIBUTING.rst)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [Ansible-Lint Rules](https://ansible-lint.readthedocs.io/rules/)

## Support

- GitHub Issues: Tag with `code-quality` label
- Kolla-Ansible IRC: #openstack-kolla
- Weekly sync: Check community calendar

## License

Apache License 2.0 - Same as Kolla-Ansible

---

**Last Updated**: 31 October 2025
**Maintainer**: @rasty94
