#!/bin/bash
# 🏛️ TOWER COMPLIANCE MASTER CHECK
# Mission: VITOR-TOWER-ENFORCEMENT-002
# 
# Complete compliance validation for agents

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🏛️ TOWER COMPLIANCE VALIDATION SYSTEM"
echo "======================================================"
echo "Checking all Roman Engineering protocol compliance..."
echo ""

# Check if hooks are installed
echo "📋 1. CHECKING GIT HOOK INSTALLATION"
echo "------------------------------------"
if [[ -f "$REPO_ROOT/.git/hooks/pre-commit" ]]; then
    echo "✅ Pre-commit hook installed"
else
    echo "❌ Pre-commit hook missing"
    echo "   Run: ./scripts/install_tower_hooks.sh"
fi

if [[ -f "$REPO_ROOT/.git/hooks/commit-msg" ]]; then
    echo "✅ Commit message hook installed"
else
    echo "❌ Commit message hook missing"
fi

if [[ -f "$REPO_ROOT/.git/hooks/post-commit" ]]; then
    echo "✅ Post-commit hook installed"
else
    echo "❌ Post-commit hook missing"
fi

echo ""

# Check testing compliance
echo "🧪 2. CHECKING TESTING PROTOCOLS"
echo "---------------------------------"
python3 "$SCRIPT_DIR/enforce_testing_protocols.py" || echo "⚠️  Testing protocol issues detected"

echo ""

# Check mission documentation compliance  
echo "📊 3. CHECKING MISSION DOCUMENTATION"
echo "------------------------------------"
python3 "$SCRIPT_DIR/check_mission_compliance.py" || echo "⚠️  Mission documentation issues detected"

echo ""

# Overall compliance status
echo "🏛️ TOWER COMPLIANCE SUMMARY"
echo "=============================="

HOOKS_SCORE=0
if [[ -f "$REPO_ROOT/.git/hooks/pre-commit" ]]; then ((HOOKS_SCORE+=34)); fi
if [[ -f "$REPO_ROOT/.git/hooks/commit-msg" ]]; then ((HOOKS_SCORE+=33)); fi  
if [[ -f "$REPO_ROOT/.git/hooks/post-commit" ]]; then ((HOOKS_SCORE+=33)); fi

echo "Git Hooks: $HOOKS_SCORE/100"

# Test if testing enforcement passes
if python3 "$SCRIPT_DIR/enforce_testing_protocols.py" --pre-commit >/dev/null 2>&1; then
    echo "Testing Protocols: 100/100"
    TESTING_SCORE=100
else
    echo "Testing Protocols: 0/100"
    TESTING_SCORE=0
fi

# Test if mission compliance passes
if python3 "$SCRIPT_DIR/check_mission_compliance.py" >/dev/null 2>&1; then
    echo "Mission Documentation: 100/100"  
    MISSION_SCORE=100
else
    echo "Mission Documentation: 60/100"
    MISSION_SCORE=60
fi

OVERALL_SCORE=$(( (HOOKS_SCORE + TESTING_SCORE + MISSION_SCORE) / 3 ))

echo ""
echo "OVERALL COMPLIANCE: $OVERALL_SCORE/100"

if [[ $OVERALL_SCORE -ge 90 ]]; then
    echo "🏆 EXCELLENT: Roman Engineering standards exceeded"
    echo "✅ All agents are operating with systematic excellence"
elif [[ $OVERALL_SCORE -ge 70 ]]; then
    echo "⚠️  ACCEPTABLE: Minor improvements needed"
    echo "🎯 Focus on addressing identified issues"
else
    echo "🚨 CRITICAL: Immediate systematic enforcement required"
    echo "❌ Multiple protocol violations require attention"
fi

echo ""
echo "🏛️ Vincere Habitatio - To Conquer Housing through Systematic Excellence"

exit 0