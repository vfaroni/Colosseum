#!/bin/bash
# Universal Colosseum Launcher - Works from any directory on M4 Beast, M1, or other Macs
# Auto-detects hardware and suggests optimal agent configurations
# Version 1.0 - Universal Command Implementation

# ANSI color codes for better display
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Colosseum directory paths (adjust these for your setup)
COLOSSEUM_PATH="/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum"
CONFIG_PATH="$COLOSSEUM_PATH/config"

# Function to detect hardware type
detect_hardware() {
    local chip_info=$(system_profiler SPHardwareDataType | grep "Chip:")
    local memory_info=$(system_profiler SPHardwareDataType | grep "Memory:")
    
    if [[ $chip_info == *"Apple M4"* ]]; then
        if [[ $memory_info == *"128 GB"* ]]; then
            echo "M4_BEAST_128GB"
        else
            echo "M4_STANDARD"
        fi
    elif [[ $chip_info == *"Apple M1"* || $chip_info == *"Apple M2"* || $chip_info == *"Apple M3"* ]]; then
        echo "M1_M2_M3"
    else
        echo "OTHER_MAC"
    fi
}

# Function to get memory size
get_memory_size() {
    local memory_gb=$(system_profiler SPHardwareDataType | grep "Memory:" | awk '{print $2}' | sed 's/GB//')
    echo "$memory_gb"
}

# Function to display hardware info
display_hardware_info() {
    local hardware_type=$1
    local memory_size=$2
    
    echo -e "${CYAN}🏛️ COLOSSEUM LIHTC PLATFORM${NC}"
    echo -e "${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    case $hardware_type in
        "M4_BEAST_128GB")
            echo -e "${GREEN}🔥 HARDWARE: M4 Beast with ${memory_size}GB Memory${NC}"
            echo -e "${GREEN}💪 CAPABILITY: Full Beast Mode + Collaborative Mode${NC}"
            ;;
        "M4_STANDARD")
            echo -e "${BLUE}⚡ HARDWARE: M4 Standard with ${memory_size}GB Memory${NC}"
            echo -e "${BLUE}💪 CAPABILITY: Enhanced Collaborative Mode${NC}"
            ;;
        "M1_M2_M3")
            echo -e "${YELLOW}🚀 HARDWARE: Apple Silicon with ${memory_size}GB Memory${NC}"
            echo -e "${YELLOW}💪 CAPABILITY: Optimized Collaborative Mode${NC}"
            ;;
        "OTHER_MAC")
            echo -e "${PURPLE}💻 HARDWARE: Mac with ${memory_size}GB Memory${NC}"
            echo -e "${PURPLE}💪 CAPABILITY: Standard Mode${NC}"
            ;;
    esac
    echo -e "${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to suggest agent configurations based on hardware
suggest_configurations() {
    local hardware_type=$1
    local memory_size=$2
    
    echo -e "\n${WHITE}🎯 RECOMMENDED AGENT CONFIGURATIONS:${NC}"
    
    case $hardware_type in
        "M4_BEAST_128GB")
            echo -e "${GREEN}1)${NC} ${WHITE}🔥 STRIKE LEADER BEAST${NC} - 96GB exclusive (Maximum Strategic Power)"
            echo -e "${GREEN}2)${NC} ${WHITE}🔥 WINGMAN BEAST${NC} - 96GB exclusive (Maximum Analytical Power)"
            echo -e "${GREEN}3)${NC} ${WHITE}⚡ THREE AGENT COLLABORATIVE${NC} - Strike Leader (30GB) + Wingman (55GB) + Tower (25GB)"
            echo -e "${GREEN}4)${NC} ${WHITE}⚡ TWO AGENT SPLIT${NC} - Strike Leader (60GB) + Wingman (60GB)"
            echo -e "${GREEN}5)${NC} ${WHITE}⚡ SINGLE AGENT FOCUS${NC} - Choose one agent with 80GB"
            ;;
        "M4_STANDARD")
            echo -e "${BLUE}1)${NC} ${WHITE}⚡ TWO AGENT OPTIMAL${NC} - Strike Leader + Wingman balanced"
            echo -e "${BLUE}2)${NC} ${WHITE}⚡ THREE AGENT LIGHT${NC} - All three agents with reduced memory"
            echo -e "${BLUE}3)${NC} ${WHITE}⚡ SINGLE AGENT FOCUS${NC} - Choose one agent with maximum memory"
            ;;
        "M1_M2_M3")
            echo -e "${YELLOW}1)${NC} ${WHITE}🚀 SINGLE AGENT OPTIMIZED${NC} - Best performance for your memory"
            echo -e "${YELLOW}2)${NC} ${WHITE}🚀 TWO AGENT LIGHT${NC} - Strike Leader + Wingman (reduced memory)"
            echo -e "${YELLOW}3)${NC} ${WHITE}🚀 THREE AGENT MINIMAL${NC} - All three agents (light mode)"
            ;;
        "OTHER_MAC")
            echo -e "${PURPLE}1)${NC} ${WHITE}💻 SINGLE AGENT${NC} - Recommended for your hardware"
            echo -e "${PURPLE}2)${NC} ${WHITE}💻 TWO AGENT BASIC${NC} - If memory allows"
            ;;
    esac
}

# Function to get user choice and configure
configure_agents() {
    local hardware_type=$1
    local memory_size=$2
    
    echo -e "\n${WHITE}Select configuration (or 'q' to quit):${NC}"
    read -p "Choice: " choice
    
    if [[ $choice == "q" || $choice == "Q" ]]; then
        echo -e "${RED}Exiting Colosseum launcher.${NC}"
        exit 0
    fi
    
    case $hardware_type in
        "M4_BEAST_128GB")
            case $choice in
                1)
                    export AGENT_ROLE="STRIKE_LEADER_BEAST"
                    export AGENT_CONFIG="Beast Mode - Strike Leader (96GB)"
                    ;;
                2)
                    export AGENT_ROLE="WINGMAN_BEAST" 
                    export AGENT_CONFIG="Beast Mode - Wingman (96GB)"
                    ;;
                3)
                    export AGENT_ROLE="THREE_AGENT_COLLABORATIVE"
                    export AGENT_CONFIG="Collaborative - Strike Leader (30GB) + Wingman (55GB) + Tower (25GB)"
                    ;;
                4)
                    export AGENT_ROLE="TWO_AGENT_SPLIT"
                    export AGENT_CONFIG="Split Mode - Strike Leader (60GB) + Wingman (60GB)"
                    ;;
                5)
                    select_single_agent
                    return
                    ;;
                *)
                    echo -e "${RED}Invalid choice. Defaulting to Three Agent Collaborative.${NC}"
                    export AGENT_ROLE="THREE_AGENT_COLLABORATIVE"
                    export AGENT_CONFIG="Collaborative Mode (Default)"
                    ;;
            esac
            ;;
        "M4_STANDARD"|"M1_M2_M3")
            case $choice in
                1)
                    if [[ $hardware_type == "M4_STANDARD" ]]; then
                        export AGENT_ROLE="TWO_AGENT_OPTIMAL"
                        export AGENT_CONFIG="Two Agent Optimal"
                    else
                        select_single_agent
                        return
                    fi
                    ;;
                2)
                    export AGENT_ROLE="TWO_AGENT_LIGHT"
                    export AGENT_CONFIG="Two Agent Light Mode"
                    ;;
                3)
                    export AGENT_ROLE="THREE_AGENT_MINIMAL"
                    export AGENT_CONFIG="Three Agent Minimal"
                    ;;
                *)
                    echo -e "${RED}Invalid choice. Defaulting to recommended configuration.${NC}"
                    if [[ $hardware_type == "M4_STANDARD" ]]; then
                        export AGENT_ROLE="TWO_AGENT_OPTIMAL"
                        export AGENT_CONFIG="Two Agent Optimal (Default)"
                    else
                        select_single_agent
                        return
                    fi
                    ;;
            esac
            ;;
        "OTHER_MAC")
            case $choice in
                1|*)
                    select_single_agent
                    return
                    ;;
            esac
            ;;
    esac
}

# Function to select single agent
select_single_agent() {
    echo -e "\n${WHITE}Choose single agent:${NC}"
    echo -e "${GREEN}1)${NC} Strike Leader (Strategic Coordination)"
    echo -e "${GREEN}2)${NC} Wingman (Deep Analysis & Definitions)"  
    echo -e "${GREEN}3)${NC} Tower (Quality Assurance & Oversight)"
    
    read -p "Agent choice: " agent_choice
    
    case $agent_choice in
        1)
            export AGENT_ROLE="STRIKE_LEADER"
            export AGENT_CONFIG="Single Agent - Strike Leader"
            ;;
        2)
            export AGENT_ROLE="WINGMAN"
            export AGENT_CONFIG="Single Agent - Wingman"
            ;;
        3)
            export AGENT_ROLE="TOWER"
            export AGENT_CONFIG="Single Agent - Tower"
            ;;
        *)
            echo -e "${RED}Invalid choice. Defaulting to Wingman.${NC}"
            export AGENT_ROLE="WINGMAN"
            export AGENT_CONFIG="Single Agent - Wingman (Default)"
            ;;
    esac
}

# Function to launch Claude Code with configuration
launch_claude_code() {
    echo -e "\n${GREEN}🚀 LAUNCHING COLOSSEUM ENVIRONMENT${NC}"
    echo -e "${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Configuration:${NC} $AGENT_CONFIG"
    echo -e "${CYAN}Agent Role:${NC} $AGENT_ROLE"
    echo -e "${CYAN}Directory:${NC} $COLOSSEUM_PATH"
    echo -e "${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Navigate to Colosseum directory
    cd "$COLOSSEUM_PATH"
    
    # Export configuration for Claude Code
    export COLOSSEUM_AGENT_ROLE="$AGENT_ROLE"
    export COLOSSEUM_AGENT_CONFIG="$AGENT_CONFIG"
    export COLOSSEUM_HARDWARE_TYPE="$HARDWARE_TYPE"
    export COLOSSEUM_MEMORY_SIZE="$MEMORY_SIZE"
    
    # Launch Claude Code with Colosseum context
    echo -e "${GREEN}Starting Claude Code in Colosseum directory...${NC}"
    echo -e "${YELLOW}Context: LIHTC Platform with $AGENT_CONFIG${NC}"
    
    # Try to start Claude Code with multiple possible command names
    echo -e "${BLUE}Searching for Claude Code...${NC}"
    
    # Common Claude Code command variations (prioritize actual Claude commands)
    CC_COMMANDS=("claude" "claude-code" "claude_code")
    CC_FOUND=false
    
    for cmd in "${CC_COMMANDS[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            # Verify it's actually Claude Code, not the C compiler
            if [[ "$cmd" == "cc" ]]; then
                continue
            fi
            echo -e "${GREEN}Found Claude Code as: $cmd${NC}"
            echo -e "${GREEN}Launching...${NC}"
            "$cmd"
            CC_FOUND=true
            break
        fi
    done
    
    if [ "$CC_FOUND" = false ]; then
        echo -e "${YELLOW}⚠️  Claude Code not found in PATH with common names.${NC}"
        echo -e "${BLUE}📍 Current directory: $(pwd)${NC}"
        echo -e "${GREEN}✅ Colosseum environment ready!${NC}"
        echo -e ""
        echo -e "${WHITE}🎯 Agent Configuration:${NC} $AGENT_CONFIG"
        echo -e "${WHITE}🤖 Agent Role:${NC} $AGENT_ROLE"  
        echo -e "${WHITE}💻 Hardware:${NC} $HARDWARE_TYPE"
        echo -e ""
        echo -e "${YELLOW}💡 To start Claude Code manually:${NC}"
        echo -e "   1. Make sure you're in this directory: $(pwd)"
        echo -e "   2. Launch Claude Code with your preferred method"
        echo -e "   3. The environment variables are already set!"
        echo -e ""
        echo -e "${CYAN}🏛️ Ready for LIHTC domination!${NC}"
    fi
}

# Main execution
main() {
    clear
    
    # Detect hardware
    HARDWARE_TYPE=$(detect_hardware)
    MEMORY_SIZE=$(get_memory_size)
    
    # Display hardware info
    display_hardware_info "$HARDWARE_TYPE" "$MEMORY_SIZE"
    
    # Suggest configurations
    suggest_configurations "$HARDWARE_TYPE" "$MEMORY_SIZE"
    
    # Get user configuration choice
    configure_agents "$HARDWARE_TYPE" "$MEMORY_SIZE"
    
    # Launch Claude Code with configuration
    launch_claude_code
}

# Check if Colosseum directory exists
if [ ! -d "$COLOSSEUM_PATH" ]; then
    echo -e "${RED}Error: Colosseum directory not found at $COLOSSEUM_PATH${NC}"
    echo -e "${YELLOW}Please update COLOSSEUM_PATH in this script to match your setup.${NC}"
    exit 1
fi

# Run main function
main