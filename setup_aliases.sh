#!/bin/bash
# 🏛️ COLOSSEUM Agent Aliases Setup - Dual User System
# Creates easy terminal commands for agent context loading

echo "🏛️ Setting up Colosseum dual-user agent aliases..."

# Get the directory where this script is located
COLOSSEUM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create alias commands that work in VS Code terminal
echo "
# 🏛️ COLOSSEUM Dual-User Agent Aliases - Add to your ~/.zshrc

# BILL'S AGENTS (Red Strike Leader, Blue Wingman, Green Tower, Yellow Secretary)
alias bill-strike='python3 \"$COLOSSEUM_DIR/launchers/launch_bill_strike_leader.py\"'
alias bill-wingman='python3 \"$COLOSSEUM_DIR/launchers/launch_bill_wingman.py\"'
alias bill-tower='python3 \"$COLOSSEUM_DIR/launchers/launch_bill_tower.py\"' 
alias bill-secretary='python3 \"$COLOSSEUM_DIR/launchers/launch_bill_secretary.py\"'

# VITOR'S AGENTS (Same color coding)
alias vitor-strike='python3 \"$COLOSSEUM_DIR/launchers/launch_vitor_strike_leader.py\"'
alias vitor-wingman='python3 \"$COLOSSEUM_DIR/launchers/launch_vitor_wingman.py\"'
alias vitor-tower='python3 \"$COLOSSEUM_DIR/launchers/launch_vitor_tower.py\"'
alias vitor-secretary='python3 \"$COLOSSEUM_DIR/launchers/launch_vitor_secretary.py\"'

# OVERSIGHT AGENTS (Cross-user coordination)
alias tower-oversight='python3 \"$COLOSSEUM_DIR/launchers/launch_oversight_tower.py\"'
alias secretary-oversight='python3 \"$COLOSSEUM_DIR/launchers/launch_oversight_secretary.py\"'

# LEGACY COMPATIBILITY (Default to Bill's agents)
alias strike='python3 \"$COLOSSEUM_DIR/launchers/launch_bill_strike_leader.py\"'
alias wingman='python3 \"$COLOSSEUM_DIR/launchers/launch_wingman.py\"'
alias tower='python3 \"$COLOSSEUM_DIR/launchers/launch_tower.py\"'
alias secretary='python3 \"$COLOSSEUM_DIR/launchers/launch_secretary.py\"'
alias unhinged='python3 \"$COLOSSEUM_DIR/launchers/launch_unhinged_mode.py\"'

# Quick directory navigation
alias colosseum='cd \"$COLOSSEUM_DIR\"'
alias bill-agents='cd \"$COLOSSEUM_DIR/agents/BILL\"'
alias vitor-agents='cd \"$COLOSSEUM_DIR/agents/VITOR\"'
alias oversight='cd \"$COLOSSEUM_DIR/oversight\"'
alias shared='cd \"$COLOSSEUM_DIR/shared_intelligence\"'
"

echo "✅ Dual-user alias commands created above!"
echo ""
echo "🎯 USAGE INSTRUCTIONS:"
echo "1. Copy the aliases above to your ~/.zshrc file"
echo "2. Run: source ~/.zshrc"
echo "3. Then you can use these commands:"
echo ""
echo "📱 BILL'S AGENTS:"
echo "   • bill-strike    → Bill's Strike Leader (RED banner, auto-updates CLAUDE.md)"
echo "   • bill-wingman   → Bill's Wingman (BLUE banner)"
echo "   • bill-tower     → Bill's Tower (GREEN banner)"
echo "   • bill-secretary → Bill's Secretary (YELLOW banner)"
echo ""
echo "👨‍💻 VITOR'S AGENTS:"
echo "   • vitor-strike    → Vitor's Strike Leader (RED banner, auto-updates CLAUDE.md)"
echo "   • vitor-wingman   → Vitor's Wingman (BLUE banner)"
echo "   • vitor-tower     → Vitor's Tower (GREEN banner)"
echo "   • vitor-secretary → Vitor's Secretary (YELLOW banner)"
echo ""
echo "🏗️ OVERSIGHT AGENTS:"
echo "   • tower-oversight     → Strategic oversight across both users"
echo "   • secretary-oversight → Administrative tracking across both users"
echo ""
echo "🚀 After loading agent context, launch Claude Code normally"
echo "   Claude will automatically know which user and agent you're operating as!"