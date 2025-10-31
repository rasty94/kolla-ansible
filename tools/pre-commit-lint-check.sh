#!/bin/bash
# Pre-commit script to check Kolla-Ansible specific linting rules

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Running Kolla-Ansible custom lint checks...${NC}"

# Check for unnamed tasks in modified files
UNNAMED_TASKS=$(git diff --cached --name-only --diff-filter=ACM | \
    grep -E 'ansible/.*\.ya?ml$' | \
    xargs -I {} sh -c 'grep -l "^\s*-\s\+import_tasks:" {} || grep -l "^\s*-\s\+include_tasks:" {} || true' | \
    xargs -I {} sh -c 'grep -B1 "^\s*-\s\+import_tasks:" {} | grep -c "name:" || echo "0"' | \
    awk '{if($1==0) count++} END {print count+0}')

if [ "$UNNAMED_TASKS" -gt 0 ]; then
    echo -e "${YELLOW}Warning: Found $UNNAMED_TASKS potential unnamed tasks${NC}"
    echo -e "${YELLOW}Consider adding descriptive names to import_tasks/include_tasks${NC}"
    # Don't fail, just warn for now
fi

# Check for tasks that should be handlers
POTENTIAL_HANDLERS=$(git diff --cached --name-only --diff-filter=ACM | \
    grep -E 'ansible/.*\.ya?ml$' | \
    xargs grep -i "restart\|reload" 2>/dev/null | wc -l || echo "0")

if [ "$POTENTIAL_HANDLERS" -gt 5 ]; then
    echo -e "${YELLOW}Warning: Found $POTENTIAL_HANDLERS lines with restart/reload${NC}"
    echo -e "${YELLOW}Consider using handlers for restart/reload operations${NC}"
fi

# Check for commands without changed_when
COMMANDS_NO_CHANGED=$(git diff --cached --name-only --diff-filter=ACM | \
    grep -E 'ansible/.*\.ya?ml$' | \
    xargs grep -E "^\s*-\s+(command|shell):" 2>/dev/null | \
    wc -l || echo "0")

if [ "$COMMANDS_NO_CHANGED"" -gt 0 ]; then
    echo -e "${YELLOW}Warning: Found $COMMANDS_NO_CHANGED command/shell tasks${NC}"
    echo -e "${YELLOW}Ensure they have appropriate changed_when conditions${NC}"
fi

echo -e "${GREEN}✓ Custom lint checks completed${NC}"

exit 0
