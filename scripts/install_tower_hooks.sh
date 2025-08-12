#!/bin/bash
# 🏛️ TOWER PROTOCOL ENFORCEMENT - INSTALLATION SCRIPT
# Mission: VITOR-TOWER-ENFORCEMENT-002
# 
# Installs mandatory testing and documentation hooks across all Colosseum agents

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "🏛️ TOWER PROTOCOL ENFORCEMENT - HOOK INSTALLATION"
echo "============================================================"
echo "Installing mandatory testing and documentation protocols..."
echo ""

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Create pre-commit hook
cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash
# 🏛️ TOWER PRE-COMMIT ENFORCEMENT
# MANDATORY testing requirements - NO EXCEPTIONS

echo "🏛️ TOWER ENFORCEMENT: Validating commit against Roman Engineering Standards..."

# Get the repository root
REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPTS_DIR="$REPO_ROOT/scripts"

# Check if enforcement script exists
if [[ ! -f "$SCRIPTS_DIR/enforce_testing_protocols.py" ]]; then
    echo "❌ TOWER ENFORCEMENT SCRIPT NOT FOUND"
    echo "   Expected: $SCRIPTS_DIR/enforce_testing_protocols.py"
    echo "   Install TOWER enforcement system first"
    exit 1
fi

# Run TOWER testing enforcement
echo "Running mandatory testing protocols..."
python3 "$SCRIPTS_DIR/enforce_testing_protocols.py" --pre-commit

TESTING_RESULT=$?

if [[ $TESTING_RESULT -eq 0 ]]; then
    echo ""
    echo "✅ TOWER APPROVAL: All testing requirements satisfied"
    echo "🏛️ Roman Engineering Standards maintained"
    echo "   Commit authorized - proceed with confidence"
else
    echo ""
    echo "❌ TOWER ENFORCEMENT: Testing requirements not satisfied"
    echo "🚨 COMMIT BLOCKED until compliance achieved"
    echo ""
    echo "Required actions:"
    echo "  1. Add/fix unit tests for your code changes"
    echo "  2. Ensure all tests pass before committing"
    echo "  3. For major features, add integration/e2e tests"
    echo "  4. Run: python3 scripts/enforce_testing_protocols.py"
    echo ""
    echo "TOWER maintains Roman Engineering excellence - no exceptions."
    exit 1
fi
EOF

# Create commit-msg hook for documentation enforcement
cat > "$HOOKS_DIR/commit-msg" << 'EOF'
#!/bin/bash
# 🏛️ TOWER COMMIT MESSAGE ENFORCEMENT
# Ensures professional commit standards

COMMIT_MSG_FILE="$1"
COMMIT_MSG="$(cat "$COMMIT_MSG_FILE")"

echo "🏛️ TOWER: Validating commit message standards..."

# Check commit message length (subject line)
SUBJECT_LINE="$(echo "$COMMIT_MSG" | head -1)"
SUBJECT_LENGTH=${#SUBJECT_LINE}

if [[ $SUBJECT_LENGTH -lt 10 ]]; then
    echo "❌ COMMIT MESSAGE TOO SHORT"
    echo "   Minimum 10 characters required for professional standards"
    echo "   Current: $SUBJECT_LENGTH characters"
    exit 1
fi

if [[ $SUBJECT_LENGTH -gt 72 ]]; then
    echo "❌ COMMIT MESSAGE TOO LONG"  
    echo "   Maximum 72 characters for subject line"
    echo "   Current: $SUBJECT_LENGTH characters"
    exit 1
fi

# Check for professional language (basic validation)
if echo "$SUBJECT_LINE" | grep -qE "(fix|Fix|add|Add|update|Update|implement|Implement|enhance|Enhance)"; then
    echo "✅ Professional commit message format detected"
else
    echo "⚠️  Consider using professional commit prefixes (Fix, Add, Update, Implement, etc.)"
fi

echo "✅ TOWER APPROVAL: Commit message meets standards"
EOF

# Create post-commit hook for documentation checks
cat > "$HOOKS_DIR/post-commit" << 'EOF'
#!/bin/bash
# 🏛️ TOWER POST-COMMIT DOCUMENTATION CHECK
# Validates mission documentation requirements

echo "🏛️ TOWER: Post-commit documentation validation..."

REPO_ROOT="$(git rev-parse --show-toplevel)"
COMMIT_HASH="$(git rev-parse --short HEAD)"
COMMIT_MSG="$(git log -1 --pretty=%B)"

# Check if this commit represents mission completion
if echo "$COMMIT_MSG" | grep -qiE "(mission|complete|final|finish|done)"; then
    echo ""
    echo "🎯 MISSION COMPLETION DETECTED"
    echo "   Commit: $COMMIT_HASH"
    echo "   Message: $(echo "$COMMIT_MSG" | head -1)"
    echo ""
    echo "📋 TOWER DOCUMENTATION REQUIREMENT:"
    echo "   Mission completion requires proper documentation in:"
    echo "   agents/[USER]/[AGENT]/reports/[MISSION]_COMPLETE.md"
    echo ""
    echo "   Verify documentation is filed correctly:"
    echo "   - Mission objectives achieved"
    echo "   - Technical details documented" 
    echo "   - Business impact quantified"
    echo "   - Roman Engineering standards followed"
    echo ""
fi

# Check for agent directory structure compliance
if [[ -d "$REPO_ROOT/agents" ]]; then
    echo "✅ Agent directory structure detected"
    
    # Count recent mission reports
    RECENT_REPORTS=$(find "$REPO_ROOT/agents" -name "*COMPLETE*.md" -newer "$REPO_ROOT/.git/COMMIT_EDITMSG" 2>/dev/null | wc -l)
    
    if [[ $RECENT_REPORTS -gt 0 ]]; then
        echo "✅ Recent mission reports detected: $RECENT_REPORTS"
    fi
else
    echo "⚠️  No agent directory structure found"
fi

echo "🏛️ TOWER: Post-commit validation complete"
EOF

# Make hooks executable
chmod +x "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/commit-msg" 
chmod +x "$HOOKS_DIR/post-commit"

echo "✅ TOWER ENFORCEMENT HOOKS INSTALLED"
echo ""
echo "Installed hooks:"
echo "  📋 pre-commit    - Mandatory testing enforcement"
echo "  ✍️  commit-msg   - Professional commit message standards"
echo "  📊 post-commit   - Documentation requirement reminders"
echo ""
echo "🏛️ ROMAN ENGINEERING PROTOCOLS NOW ACTIVE"
echo ""
echo "All future commits will be validated against:"
echo "  ✅ Unit testing requirements (MANDATORY)"
echo "  ✅ Feature testing standards (recommended)"
echo "  ✅ End-to-end testing for major features (recommended)"
echo "  ✅ Professional commit message standards"
echo "  ✅ Mission documentation requirements"
echo ""
echo "🚨 NON-COMPLIANCE WILL BLOCK COMMITS"
echo "🎯 Excellence is not optional - it's systematic"
echo ""
echo "To test enforcement:"
echo "  python3 scripts/enforce_testing_protocols.py"
echo ""
echo "Vincere Habitatio - To Conquer Housing through Systematic Excellence"