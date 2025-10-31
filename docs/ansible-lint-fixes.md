# Ansible-Lint Fixes Roadmap

## Current State Analysis (31 Oct 2025)

### Statistics
- **Total YAML files**: 1,176
- **Files with issues**: 736 (62.6%)
- **Unnamed tasks**: 997
- **Potential handlers**: 536
- **Commands without changed_when**: 0 (already fixed!)

### Rules Currently Disabled (28 total)

#### HIGH PRIORITY (Must Fix)
1. ✅ `no-changed-when` - ALREADY CLEAN!
2. 🚧 `unnamed-task` - 997 occurrences (FIXME: mgoddard)
3. 🚧 `no-handler` - 536 potential handlers (TODO: mnasiadka)

#### MEDIUM PRIORITY (Should Fix)
4. `key-order[task]` - Inconsistent task key ordering
5. `no-free-form` - Free-form commands should use proper syntax
6. `var-naming[no-role-prefix]` - Variables should have role prefixes
7. `risky-file-permissions` - File permissions should be explicit
8. `command-instead-of-shell` - Use command module when possible
9. `command-instead-of-module` - Use native modules instead of shell commands

#### LOW PRIORITY (Nice to Have)
10. `risky-shell-pipe` - Shell pipes can hide errors
11. `ignore-errors` - Avoid ignore_errors when possible
12. `jinja[spacing]` - Jinja template spacing consistency

#### KEEP DISABLED (Project Decisions)
- `experimental` - Experimental rules may be unstable
- `package-latest` - Latest is intentional in some cases
- `no-tabs` - Tabs handling is inconsistent
- `fqcn-builtins` - Agreed at Zed PTG to skip for now
- `name[template]` - Allow Jinja in names
- `fqcn[action]` - Skip FQCN for actions
- `role-name` - Role naming is legacy
- `name[play]` - Play names can be dynamic

## Phased Implementation Plan

### Phase 1: Quick Wins (Week 1-2) ✅ READY TO START

**Goal**: Fix unnamed-task (997 occurrences)

**Approach**:
1. Use automated script (`tools/fix_ansible_lint.py`)
2. Focus on import_tasks, include_tasks, import_role, include_role
3. Generate descriptive names based on module and parameters

**Expected Impact**:
- Remove 1 rule from skip_list
- Improve code readability significantly
- Enable easier code navigation

**Commands**:
```bash
# Check what would be fixed
./tools/fix_ansible_lint.py --check

# Apply fixes to specific roles first (test)
./tools/fix_ansible_lint.py --fix --roles keystone,neutron,nova

# Apply fixes to all
./tools/fix_ansible_lint.py --fix
```

### Phase 2: Handler Conversion (Week 3-4)

**Goal**: Convert repetitive tasks to handlers (536 occurrences)

**Common Patterns to Convert**:
```yaml
# BEFORE: Repetitive task
- name: Restart {{ service_name }} container
  kolla_container:
    action: restart_container
    name: "{{ service_name }}"
  when: config_changed

# AFTER: Handler
handlers:
  - name: Restart container
    kolla_container:
      action: restart_container
      name: "{{ service_name }}"

tasks:
  - name: Copy config
    template: ...
    notify: Restart container
```

**Keywords to search**:
- restart
- reload  
- reconfigure
- stop_container
- start_container

**Script**: `tools/identify_handlers.py`

### Phase 3: Code Quality (Week 5-6)

**Goal**: Fix medium priority issues

1. **key-order[task]**: Standardize task key order
   ```yaml
   # Standard order:
   - name: ...
     module: ...
     params: ...
     when: ...
     register: ...
     tags: ...
     become: ...
   ```

2. **risky-file-permissions**: Add explicit modes
   ```yaml
   # BEFORE
   - file:
       path: /etc/config
       state: directory
   
   # AFTER
   - file:
       path: /etc/config
       state: directory
       mode: "0755"
   ```

3. **var-naming[no-role-prefix]**: Add role prefixes
   ```yaml
   # BEFORE
   vars:
     api_port: 8080
   
   # AFTER
   vars:
     keystone_api_port: 8080
   ```

### Phase 4: Command Improvements (Week 7-8)

**Goal**: Replace shell commands with native modules

Examples:
```yaml
# BEFORE
- shell: mkdir -p /path/to/dir

# AFTER
- file:
    path: /path/to/dir
    state: directory

# BEFORE  
- shell: systemctl restart service

# AFTER
- systemd:
    name: service
    state: restarted
```

**Script**: `tools/replace_shell_commands.py`

## Progress Tracking

### Week 1-2 (Nov 1-14, 2025)
- [ ] Run fix_ansible_lint.py --stats to baseline
- [ ] Fix unnamed-task in core roles (keystone, neutron, nova, glance, cinder)
- [ ] Fix unnamed-task in remaining roles
- [ ] Remove `unnamed-task` from .ansible-lint skip_list
- [ ] Run full test suite
- [ ] Create PR for review

### Week 3-4 (Nov 15-28, 2025)
- [ ] Identify handler patterns with identify_handlers.py
- [ ] Convert top 50 repetitive tasks to handlers
- [ ] Update remaining tasks to use notify
- [ ] Remove `no-handler` from skip_list (partial)
- [ ] Run full test suite
- [ ] Create PR for review

### Week 5-6 (Nov 29 - Dec 12, 2025)
- [ ] Fix key-order issues in top 20 roles
- [ ] Add explicit file permissions
- [ ] Add role prefixes to variables
- [ ] Run full test suite
- [ ] Create PR for review

### Week 7-8 (Dec 13-26, 2025)
- [ ] Replace shell commands with native modules
- [ ] Final cleanup of risky patterns
- [ ] Update documentation
- [ ] Final test suite run
- [ ] Create final PR

## Testing Strategy

### Pre-Commit Checks
```bash
# Run ansible-lint before commit
ansible-lint ansible/

# Run specific checks
ansible-lint --strict ansible/roles/keystone/
```

### CI Integration
- Add GitHub Action for ansible-lint
- Block PRs that introduce new violations
- Generate reports on each commit

### Test Coverage
- Unit tests: Ensure fixes don't break logic
- Integration tests: Full deployment test
- Smoke tests: Basic functionality verification

## Metrics & Success Criteria

### Before (Current State)
- Rules disabled: 28
- Unnamed tasks: 997
- Files with issues: 736
- Code quality score: ~60%

### After (Target State)
- Rules disabled: 15 (-13)
- Unnamed tasks: 0 (-997)
- Files with issues: <200 (-536)
- Code quality score: >85% (+25%)

### KPIs
1. **Maintainability**: Time to understand code -40%
2. **Onboarding**: New developer setup time -50%
3. **Bug fixes**: Lint-prevented bugs +30%
4. **PR velocity**: Review time -30%

## Tools Created

1. **fix_ansible_lint.py**: Auto-fix unnamed tasks and basic issues
2. **identify_handlers.py**: Find repetitive tasks → handler candidates  
3. **replace_shell_commands.py**: Suggest native module replacements
4. **validate_fixes.py**: Verify fixes don't break functionality

## Documentation Updates

- [ ] Update CONTRIBUTING.rst with ansible-lint requirements
- [ ] Add pre-commit hook setup instructions
- [ ] Document naming conventions
- [ ] Create ansible best practices guide

## Rollout Strategy

### Phase 1: Opt-in (Week 1-2)
- Tools available but not enforced
- Developers can run locally
- CI generates warnings only

### Phase 2: Soft Enforcement (Week 3-6)
- CI fails on new violations
- Existing violations allowed
- PR review includes lint check

### Phase 3: Full Enforcement (Week 7-8)
- All violations must be fixed
- No exceptions without justification
- Automated fixes in CI

## Risk Mitigation

### Risk: Breaking existing deployments
**Mitigation**: 
- Extensive testing before merge
- Feature flags for new behaviors
- Rollback plan ready

### Risk: Too much churn in codebase
**Mitigation**:
- Phased rollout
- Small, focused PRs
- Clear communication

### Risk: Team bandwidth
**Mitigation**:
- Automated fixes where possible
- Clear documentation
- Pair programming sessions

## Getting Started

```bash
# 1. Setup
cd /path/to/kolla-ansible
python3 -m venv .lint-venv
source .lint-venv/bin/activate
pip install ansible-lint pyyaml

# 2. Baseline
./tools/fix_ansible_lint.py --stats

# 3. Fix (dry run)
./tools/fix_ansible_lint.py --check

# 4. Fix (apply)
./tools/fix_ansible_lint.py --fix

# 5. Verify
ansible-lint ansible/

# 6. Test
tox -e ansible-lint
tox -e linters
```

## Support & Questions

- GitHub Issues: Tag with `code-quality` label
- Slack: #kolla-ansible-dev
- Weekly sync: Thursdays 10am UTC

---

**Last Updated**: 31 October 2025
**Owner**: @rasty94
**Status**: 🚧 IN PROGRESS - Phase 1
