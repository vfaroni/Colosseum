#!/bin/bash
# Mission Completion Git Integration Script
# Automatically commits and pushes mission completions to GitHub

COLOSSEUM_DIR="/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum"
SCRIPT_DIR="$COLOSSEUM_DIR/scripts"

# Function to display usage
usage() {
    echo "🏛️ COLOSSEUM MISSION COMPLETION - GitHub Integration"
    echo ""
    echo "Usage: $0 <mission_name> <mission_summary> <business_impact>"
    echo ""
    echo "Examples:"
    echo "  $0 \"BOTN Restructure\" \"Professional Python organization\" \"Enterprise competitive advantage\""
    echo "  $0 \"Email Secretary\" \"Service architecture implementation\" \"Administrative automation enhancement\""
    echo ""
    echo "🎯 Vincere Habitatio - Systematic Excellence"
    exit 1
}

# Check arguments
if [ $# -lt 3 ]; then
    usage
fi

MISSION_NAME="$1"
MISSION_SUMMARY="$2"
BUSINESS_IMPACT="$3"

echo "🏛️ COLOSSEUM MISSION COMPLETION WORKFLOW"
echo "========================================="
echo "Mission: $MISSION_NAME"
echo "Summary: $MISSION_SUMMARY"
echo "Impact: $BUSINESS_IMPACT"
echo ""

# Change to Colosseum directory
cd "$COLOSSEUM_DIR" || {
    echo "❌ Error: Cannot access Colosseum directory"
    exit 1
}

# Run the Python automation script
python3 "$SCRIPT_DIR/automated_github_commit.py" "$MISSION_NAME" "$MISSION_SUMMARY" "$BUSINESS_IMPACT"

exit $?