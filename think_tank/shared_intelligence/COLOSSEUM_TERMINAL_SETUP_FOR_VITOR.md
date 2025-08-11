# 🏛️ COLOSSEUM TERMINAL SETUP GUIDE FOR VITOR

**Purpose**: Enable Vitor to run "colosseum" from anywhere in terminal to launch Claude Code with full platform context  
**Author**: Bill's Strike Leader  
**Date**: August 6, 2025  

---

## 🚀 QUICK SETUP (5 Minutes)

### Step 1: Add to Shell Profile

Add this to your `.zshrc` (Mac) or `.bashrc` (Linux):

```bash
# 🏛️ Colosseum LIHTC Platform
alias colosseum='cd /Users/vitor/Library/CloudStorage/Dropbox-HERR/Vitor/Colosseum && python3 launchers/launch_vitor_strike_leader_enhanced.py && code .'

# Optional: Different agent contexts
alias colosseum-wingman='cd /Users/vitor/Library/CloudStorage/Dropbox-HERR/Vitor/Colosseum && python3 launchers/launch_vitor_wingman_enhanced.py && code .'
alias colosseum-tower='cd /Users/vitor/Library/CloudStorage/Dropbox-HERR/Vitor/Colosseum && python3 launchers/launch_vitor_tower_enhanced.py && code .'

# Quick access to your 7-step workflow
alias botn='cd /Users/vitor/Library/CloudStorage/Dropbox-HERR/Vitor/Colosseum/modules/lihtc_analyst/botn_engine'
alias transit='cd /Users/vitor/Library/CloudStorage/Dropbox-HERR/Vitor/Colosseum/modules/data_intelligence/transit_analysis'
```

### Step 2: Reload Shell

```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Step 3: Test It!

From anywhere in terminal:
```bash
colosseum
```

This will:
1. Navigate to your Colosseum directory
2. Display your Strike Leader context
3. Launch Claude Code with the project

---

## 🎯 ADVANCED SETUP WITH STARTUP SCRIPT

### Create Colosseum Startup Script

Save as `~/.colosseum/startup.sh`:

```bash
#!/bin/bash
# 🏛️ Colosseum Multi-Agent Startup Script for Vitor

# Configuration
COLOSSEUM_HOME="/Users/vitor/Library/CloudStorage/Dropbox-HERR/Vitor/Colosseum"
CLAUDE_CODE_PROJECT="COLOSSEUM_LIHTC"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Display banner
display_banner() {
    echo -e "${PURPLE}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║              🏛️  COLOSSEUM LIHTC PLATFORM  🏛️                 ║"
    echo "║           Where Housing Battles Are Won                       ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Agent selection
select_agent() {
    echo -e "${CYAN}${BOLD}Select Agent Context:${NC}"
    echo "1) 🎯 Strike Leader - Strategic Coordination"
    echo "2) 🚀 Wingman - Technical Implementation"  
    echo "3) 🏰 Tower - Quality Assurance"
    echo "4) 📝 Secretary - Administrative"
    echo "5) 🔥 All Agents - Complete Ecosystem"
    
    read -p "Enter choice (1-5) [default: 1]: " choice
    choice=${choice:-1}
    
    case $choice in
        1) AGENT="strike_leader";;
        2) AGENT="wingman";;
        3) AGENT="tower";;
        4) AGENT="secretary";;
        5) AGENT="all";;
        *) AGENT="strike_leader";;
    esac
}

# Launch agent
launch_agent() {
    cd "$COLOSSEUM_HOME"
    
    case $AGENT in
        "strike_leader")
            echo -e "${RED}${BOLD}🎯 Launching Strike Leader...${NC}"
            python3 launchers/launch_vitor_strike_leader_enhanced.py
            ;;
        "wingman")
            echo -e "${GREEN}${BOLD}🚀 Launching Wingman...${NC}"
            python3 launchers/launch_vitor_wingman_enhanced.py
            ;;
        "tower")
            echo -e "${BLUE}${BOLD}🏰 Launching Tower...${NC}"
            python3 launchers/launch_vitor_tower_enhanced.py
            ;;
        "secretary")
            echo -e "${YELLOW}${BOLD}📝 Launching Secretary...${NC}"
            python3 launchers/launch_secretary.py
            ;;
        "all")
            echo -e "${PURPLE}${BOLD}🔥 Launching All Agents...${NC}"
            python3 launchers/launch_all_agents.py
            ;;
    esac
    
    # Launch Claude Code
    echo -e "${CYAN}${BOLD}Launching Claude Code...${NC}"
    code .
}

# Main execution
display_banner
select_agent
launch_agent

# Set environment for Claude Code
export COLOSSEUM_AGENT=$AGENT
export COLOSSEUM_USER="VITOR"
export COLOSSEUM_7STEP="ACTIVE"

echo -e "${GREEN}${BOLD}✅ Colosseum Ready - $AGENT context loaded${NC}"
echo -e "${YELLOW}Vincere Habitatio - 'To Conquer Housing'${NC}"
```

### Make it executable:
```bash
chmod +x ~/.colosseum/startup.sh
```

### Update your shell alias:
```bash
# In .zshrc or .bashrc
alias colosseum='~/.colosseum/startup.sh'
```

---

## 🔧 VITOR'S 7-STEP WORKFLOW SHORTCUTS

Add these to your shell profile for rapid access:

```bash
# 7-Step Workflow Shortcuts
alias step1-costar='cd $COLOSSEUM_HOME/modules/data_intelligence/costar_processor'
alias step2-filter='cd $COLOSSEUM_HOME/modules/integration/api_endpoints'
alias step3-enviro='cd $COLOSSEUM_HOME/modules/data_intelligence/environmental_screening'
alias step4-transit='cd $COLOSSEUM_HOME/modules/data_intelligence/transit_analysis'
alias step5-botn='cd $COLOSSEUM_HOME/modules/lihtc_analyst/botn_engine'
alias step6-underwrite='cd $COLOSSEUM_HOME/modules/lihtc_analyst/full_underwriting'
alias step7-execute='cd $COLOSSEUM_HOME/modules/lihtc_analyst/broker_outreach'

# Quick BOTN operations
alias botn-run='python3 $COLOSSEUM_HOME/modules/lihtc_analyst/botn_engine/botn_comprehensive_generator.py'
alias botn-test='python3 $COLOSSEUM_HOME/modules/lihtc_analyst/botn_engine/botn_test_10_sites.py'

# Transit analysis
alias transit-ctcac='python3 $COLOSSEUM_HOME/modules/lihtc_analyst/botn_engine/ultimate_ctcac_transit_processor.py'
alias transit-validate='python3 $COLOSSEUM_HOME/modules/lihtc_analyst/botn_engine/transit_portfolio_analyzer.py'

# Environmental screening  
alias env-screen='python3 $COLOSSEUM_HOME/modules/data_intelligence/environmental_screening/comprehensive_environmental_analyzer.py'

# Pipeline management
alias pipeline='python3 $COLOSSEUM_HOME/modules/workforce_analyst/AcquisitionAnalyst.py'
```

---

## 💻 CLAUDE CODE INTEGRATION

### Create `.claude-code/config.json` in your Colosseum directory:

```json
{
  "project": "COLOSSEUM_LIHTC_PLATFORM",
  "user": "VITOR",
  "version": "1.0.0",
  
  "systemContext": {
    "description": "LIHTC platform with Vitor's 7-step workflow integration",
    "primaryFocus": "Back-of-the-Napkin calculations and deal flow automation",
    "currentPhase": "Transit scoring enhancement and pipeline optimization"
  },
  
  "workflowIntegration": {
    "step1": "modules/data_intelligence/costar_processor",
    "step2": "modules/integration/api_endpoints/filter_api.py",
    "step3": "modules/data_intelligence/environmental_screening",
    "step4": "modules/data_intelligence/transit_analysis",
    "step5": "modules/lihtc_analyst/botn_engine",
    "step6": "modules/lihtc_analyst/full_underwriting",
    "step7": "modules/lihtc_analyst/broker_outreach"
  },
  
  "agentRoles": {
    "STRIKE_LEADER": "Strategic coordination and workflow optimization",
    "WINGMAN": "BOTN engine development and transit analysis",
    "TOWER": "Quality assurance and pipeline validation",
    "SECRETARY": "Deal flow automation and CRM integration"
  },
  
  "customCommands": {
    "botn": "Run BOTN calculation for current project",
    "transit": "Analyze transit compliance for site",
    "pipeline": "Show current deal pipeline status",
    "env-check": "Run environmental screening"
  }
}
```

---

## 🚨 TROUBLESHOOTING

### If "colosseum" command not found:
```bash
# Check if alias exists
alias | grep colosseum

# Reload shell profile
source ~/.zshrc  # or ~/.bashrc

# Check shell type
echo $SHELL
```

### If Python scripts fail:
```bash
# Ensure Python 3 is installed
python3 --version

# Install required packages
pip3 install -r $COLOSSEUM_HOME/requirements.txt
```

### If Claude Code doesn't launch:
```bash
# Check if 'code' command is installed
which code

# If not, install from VS Code:
# Command Palette (Cmd+Shift+P) → "Shell Command: Install 'code' command in PATH"
```

---

## 🎯 POWER USER TIPS

### 1. Quick Mission Creation
```bash
# Create function in .zshrc
colosseum-mission() {
    local mission_name=$1
    cd $COLOSSEUM_HOME/agents/VITOR/STRIKE_LEADER/missions
    echo "# MISSION: $mission_name" > "${mission_name}_MISSION.md"
    echo "Created mission: $mission_name"
    code "${mission_name}_MISSION.md"
}

# Usage
colosseum-mission "TRANSIT_SCORING_FIX"
```

### 2. Daily Workflow Alias
```bash
# Your daily BOTN workflow
alias vitor-daily='colosseum && echo "Loading Vitor daily workflow..." && code modules/lihtc_analyst/botn_engine'
```

### 3. Quick Context Switch
```bash
# Switch between Bill and Vitor contexts
alias colosseum-bill='cd /Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill\ Rice/Colosseum && python3 launchers/launch_bill_strike_leader.py && code .'
alias colosseum-vitor='cd /Users/vitor/Library/CloudStorage/Dropbox-HERR/Vitor/Colosseum && python3 launchers/launch_vitor_strike_leader_enhanced.py && code .'
```

---

## 📋 COMPLETE SETUP CHECKLIST

- [ ] Add aliases to shell profile (.zshrc or .bashrc)
- [ ] Create ~/.colosseum directory
- [ ] Save startup.sh script
- [ ] Make startup.sh executable
- [ ] Create .claude-code/config.json in Colosseum directory
- [ ] Reload shell with `source ~/.zshrc`
- [ ] Test with `colosseum` command
- [ ] Verify Claude Code launches with context

---

## 🏆 EXPECTED RESULT

When you type `colosseum` from anywhere:

1. **Terminal shows**:
   ```
   ╔═══════════════════════════════════════════════════════════════╗
   ║              🏛️  COLOSSEUM LIHTC PLATFORM  🏛️                 ║
   ║           Where Housing Battles Are Won                       ║
   ╚═══════════════════════════════════════════════════════════════╝
   
   🎯 STRIKE LEADER AGENT CONTEXT LOADED
   Strategic Coordination & LIHTC Platform Leadership
   ```

2. **Claude Code opens** with:
   - Colosseum project loaded
   - Agent context active
   - Ready for BOTN operations

3. **You can immediately**:
   - Run BOTN calculations
   - Check transit scoring
   - Manage pipeline
   - Execute 7-step workflow

---

**Questions?** The corrected transit scoring code is in:
`/agents/BILL/STRIKE_LEADER/transit_fixes_for_vitor/corrected_ultimate_ctcac_transit_processor.py`

*Built for conquering the affordable housing development arena* 🏛️