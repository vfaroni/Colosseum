#!/bin/bash
# Colosseum M4 Beast Startup Script - Enhanced with Beast Mode
# Version 1.1 - Beast Mode Integration

echo "🏛️ Initializing Colosseum LIHTC Platform on M4 Beast"

# Set environment variables
export COLOSSEUM_HOME="/Users/$(whoami)/colosseum-workspace"
export COLOSSEUM_MACHINE="M4_BEAST"
export COLOSSEUM_MEMORY="128GB"
export CLAUDE_CODE_PROJECT="COLOSSEUM_LIHTC"
export COLOSSEUM_CONFIG_PATH="/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/config"

# Beast Mode detection and configuration
detect_beast_mode() {
    if [[ "$AGENT_ROLE" == *"_BEAST" ]]; then
        echo "🔥 BEAST MODE DETECTED: $AGENT_ROLE"
        export BEAST_MODE="true"
        export EXCLUSIVE_MODE="true"
        export MEMORY_ALLOCATION="96GB"
        
        # Check if other agents are running
        if pgrep -f "ollama.*11434\|ollama.*11435\|ollama.*11437" > /dev/null; then
            echo "⚠️  WARNING: Other agents detected running. Beast Mode requires exclusive access."
            echo "🛑 Stopping other agent processes..."
            pkill -f "ollama.*1143[4-7]"
            sleep 2
        fi
        
        # Configure Beast Mode ports
        case $AGENT_ROLE in
            "STRIKE_LEADER_BEAST")
                export OLLAMA_HOST="127.0.0.1:11440"
                export BEAST_PORT="11440"
                ;;
            "WINGMAN_BEAST")
                export OLLAMA_HOST="127.0.0.1:11441"
                export BEAST_PORT="11441"
                ;;
        esac
        
        echo "🚀 Beast Mode configured: $MEMORY_ALLOCATION memory on port $BEAST_PORT"
    else
        export BEAST_MODE="false"
        export EXCLUSIVE_MODE="false"
    fi
}

# Check which agent role to assume
if [ -z "$AGENT_ROLE" ]; then
    echo "Select agent role:"
    echo "1) Strike Leader (Strategic Coordination - 30GB)"
    echo "2) Wingman (Deep Analysis - 55GB)" 
    echo "3) Tower (Quality Assurance - 25GB)"
    echo "4) 🔥 STRIKE LEADER BEAST (Maximum Strategic - 96GB)"
    echo "5) 🔥 WINGMAN BEAST (Maximum Analytical - 96GB)"
    read -p "Enter choice (1-5): " choice
    
    case $choice in
        1) export AGENT_ROLE="STRIKE_LEADER";;
        2) export AGENT_ROLE="WINGMAN";;
        3) export AGENT_ROLE="TOWER";;
        4) export AGENT_ROLE="STRIKE_LEADER_BEAST";;
        5) export AGENT_ROLE="WINGMAN_BEAST";;
        *) echo "Invalid choice"; exit 1;;
    esac
fi

# Detect and configure Beast Mode
detect_beast_mode

# Load agent-specific configuration
if [ "$BEAST_MODE" = "true" ]; then
    export AGENT_CONFIG="$COLOSSEUM_CONFIG_PATH/agent-contexts/${AGENT_ROLE,,}_context.md"
else
    # For collaborative mode, use existing contexts or create basic ones
    export AGENT_CONFIG="$COLOSSEUM_CONFIG_PATH/agent-contexts/${AGENT_ROLE,,}_context.md"
fi

export COLOSSEUM_CONFIG="$COLOSSEUM_CONFIG_PATH/colosseum-config.json"

# Configure based on mode
if [ "$BEAST_MODE" = "true" ]; then
    # Beast Mode Configuration
    case $AGENT_ROLE in
        "STRIKE_LEADER_BEAST")
            export MODEL="llama3.1:70b-instruct-q4_K_M"
            export MEMORY_LIMIT="96GB"
            export CONTEXT_WINDOW="131072"
            export BEAST_TYPE="strategic"
            ;;
        "WINGMAN_BEAST")
            export MODEL="llama3.1:70b-instruct-q4_K_M"
            export MEMORY_LIMIT="96GB"
            export CONTEXT_WINDOW="131072"
            export BEAST_TYPE="analytical"
            ;;
    esac
else
    # Collaborative Mode Configuration
    case $AGENT_ROLE in
        "STRIKE_LEADER")
            export OLLAMA_HOST="127.0.0.1:11434"
            export MODEL="llama3.1:34b-instruct-q4_K_M"
            export MEMORY_LIMIT="30GB"
            export CONTEXT_WINDOW="8192"
            ;;
        "WINGMAN")
            export OLLAMA_HOST="127.0.0.1:11435"
            export MODEL="llama3.1:70b-instruct-q4_K_M"
            export MEMORY_LIMIT="55GB"
            export CONTEXT_WINDOW="16384"
            ;;
        "TOWER")
            export OLLAMA_HOST="127.0.0.1:11437"
            export MODEL="mixtral:8x7b-instruct-q4_K_M"
            export MEMORY_LIMIT="25GB"
            export CONTEXT_WINDOW="4096"
            ;;
    esac
fi

# Memory monitoring function
monitor_memory() {
    if [ "$BEAST_MODE" = "true" ]; then
        local threshold=95
    else
        local threshold=90
    fi
    
    local memory_usage=$(memory_pressure | grep "System-wide memory free percentage" | awk '{print 100-$5}')
    if [ "${memory_usage%.*}" -gt "$threshold" ]; then
        echo "⚠️  Memory usage high: ${memory_usage}%. Consider optimization."
    fi
}

# Ensure Ollama is running with correct model
if ! curl -s $OLLAMA_HOST/api/tags | grep -q "$MODEL"; then
    echo "📥 Loading $MODEL..."
    if [ "$BEAST_MODE" = "true" ]; then
        echo "🔥 Beast Mode: Loading with maximum memory allocation..."
        OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=1 ollama pull $MODEL
    else
        ollama pull $MODEL
    fi
fi

# Create workspace structure
mkdir -p $COLOSSEUM_HOME/{missions,reports,shared,cache,outputs,beast-mode}

# Beast Mode specific directories
if [ "$BEAST_MODE" = "true" ]; then
    mkdir -p $COLOSSEUM_HOME/beast-mode/{analysis,reports,monitoring}
fi

# Display configuration
if [ "$BEAST_MODE" = "true" ]; then
    echo "
🔥 BEAST MODE ACTIVATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Project: Colosseum LIHTC Platform
🤖 Agent: $AGENT_ROLE (BEAST MODE)
💻 Machine: M4 Beast (128GB)
🧠 Model: $MODEL
🔗 Endpoint: $OLLAMA_HOST
💾 Memory: $MEMORY_LIMIT (EXCLUSIVE)
🎯 Context: $CONTEXT_WINDOW tokens
📁 Workspace: $COLOSSEUM_HOME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 EXCLUSIVE MODE: Maximum Performance
🎯 Mission: Where Housing Battles Are Won
📊 Coverage: 54 US Jurisdictions
🚀 Focus: Maximum $BEAST_TYPE Power

Type 'beast-help' for Beast Mode commands
"
else
    echo "
✅ Colosseum Configuration Loaded
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Project: Colosseum LIHTC Platform
🤖 Agent: $AGENT_ROLE
💻 Machine: M4 Beast (128GB)
🧠 Model: $MODEL
🔗 Endpoint: $OLLAMA_HOST
💾 Memory: $MEMORY_LIMIT
📁 Workspace: $COLOSSEUM_HOME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mission: Where Housing Battles Are Won
Coverage: 54 US Jurisdictions
Focus: CA, TX, AZ, NM, HI

Type 'help' for Colosseum commands
"
fi

# Set command aliases
alias qap-extract='python $COLOSSEUM_HOME/scripts/qap_extractor.py'
alias botn='python $COLOSSEUM_HOME/scripts/botn_calculator.py'
alias env-screen='python $COLOSSEUM_HOME/scripts/environmental_screener.py'
alias transit-check='python $COLOSSEUM_HOME/scripts/transit_analyzer.py'
alias pipeline-status='python $COLOSSEUM_HOME/scripts/pipeline_tracker.py'
alias deploy-agent='$COLOSSEUM_HOME/scripts/deploy_agent.sh'
alias mission-create='$COLOSSEUM_HOME/scripts/create_mission.sh'
alias report-analyze='python $COLOSSEUM_HOME/scripts/analyze_reports.py'

# Beast Mode specific aliases
if [ "$BEAST_MODE" = "true" ]; then
    alias beast-monitor='python $COLOSSEUM_HOME/scripts/beast_monitor.py'
    alias beast-analyze='python $COLOSSEUM_HOME/scripts/beast_analyzer.py'
    alias beast-extract='python $COLOSSEUM_HOME/scripts/beast_extractor.py'
    alias beast-define='python $COLOSSEUM_HOME/scripts/beast_definitions.py'
    alias beast-botn='python $COLOSSEUM_HOME/scripts/beast_botn.py'
    alias beast-health='python $COLOSSEUM_HOME/scripts/beast_health_check.py'
    alias beast-optimize='python $COLOSSEUM_HOME/scripts/beast_optimizer.py'
    alias beast-help='cat $COLOSSEUM_CONFIG_PATH/beast-mode-help.md'
fi

# Load mission if specified
if [ ! -z "$MISSION_ID" ]; then
    echo "📋 Loading mission: $MISSION_ID"
    if [ -f "$COLOSSEUM_HOME/missions/$MISSION_ID.md" ]; then
        cat $COLOSSEUM_HOME/missions/$MISSION_ID.md
    else
        echo "⚠️  Mission file not found: $MISSION_ID"
    fi
fi

# Start memory monitoring (background)
if [ "$BEAST_MODE" = "true" ]; then
    echo "🔍 Starting Beast Mode memory monitoring..."
    (while true; do monitor_memory; sleep 30; done) &
    export MONITOR_PID=$!
fi

# Final Beast Mode status
if [ "$BEAST_MODE" = "true" ]; then
    echo "🔥 Beast Mode Ready - Maximum power deployed!"
    echo "💡 Use 'beast-help' for specialized commands"
else
    echo "✅ Collaborative Mode Ready"
    echo "💡 Use 'help' for standard commands"
fi