#!/bin/bash
# Colosseum Universal Command Installer
# Installs the 'colosseum' command to work from any directory on M1, M4, or other Macs

# ANSI color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER_PATH="$SCRIPT_DIR/universal_colosseum_launcher.sh"

echo -e "${BLUE}🏛️ Installing Universal Colosseum Command${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check if launcher exists
if [ ! -f "$LAUNCHER_PATH" ]; then
    echo -e "${RED}❌ Error: Launcher script not found at $LAUNCHER_PATH${NC}"
    exit 1
fi

# Detect shell
SHELL_NAME=$(basename "$SHELL")
echo -e "${YELLOW}🔍 Detected shell: $SHELL_NAME${NC}"

# Determine config file
case $SHELL_NAME in
    "zsh")
        CONFIG_FILE="$HOME/.zshrc"
        ;;
    "bash")
        if [[ "$OSTYPE" == "darwin"* ]]; then
            CONFIG_FILE="$HOME/.bash_profile"
        else
            CONFIG_FILE="$HOME/.bashrc"
        fi
        ;;
    "fish")
        CONFIG_FILE="$HOME/.config/fish/config.fish"
        ;;
    *)
        echo -e "${YELLOW}⚠️  Unknown shell. Defaulting to .bashrc${NC}"
        CONFIG_FILE="$HOME/.bashrc"
        ;;
esac

echo -e "${YELLOW}📝 Config file: $CONFIG_FILE${NC}"

# Create backup of config file
if [ -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_FILE" "${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${GREEN}✅ Backup created: ${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)${NC}"
fi

# Check if alias already exists
if grep -q "alias colosseum=" "$CONFIG_FILE" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Existing 'colosseum' alias found. Removing old version...${NC}"
    # Remove existing colosseum alias lines
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' '/alias colosseum=/d' "$CONFIG_FILE"
        sed -i '' '/# Colosseum LIHTC Platform/d' "$CONFIG_FILE"
    else
        sed -i '/alias colosseum=/d' "$CONFIG_FILE"
        sed -i '/# Colosseum LIHTC Platform/d' "$CONFIG_FILE"
    fi
fi

# Add the alias based on shell type
echo -e "\n${YELLOW}📝 Adding colosseum command to $CONFIG_FILE...${NC}"

if [[ $SHELL_NAME == "fish" ]]; then
    # Fish shell syntax
    cat >> "$CONFIG_FILE" << EOF

# Colosseum LIHTC Platform Universal Command
function colosseum
    bash "$LAUNCHER_PATH"
end
EOF
else
    # Bash/Zsh syntax
    cat >> "$CONFIG_FILE" << EOF

# Colosseum LIHTC Platform Universal Command
alias colosseum='bash "$LAUNCHER_PATH"'
EOF
fi

echo -e "${GREEN}✅ Colosseum command installed successfully!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Test the installation
echo -e "\n${YELLOW}🧪 Testing installation...${NC}"

# Source the config file to test
if [[ $SHELL_NAME == "fish" ]]; then
    echo -e "${YELLOW}Fish shell detected. Please run 'source $CONFIG_FILE' or restart your terminal.${NC}"
else
    source "$CONFIG_FILE"
    if command -v colosseum &> /dev/null; then
        echo -e "${GREEN}✅ Test successful! 'colosseum' command is available.${NC}"
    else
        echo -e "${RED}❌ Test failed. Please restart your terminal or run 'source $CONFIG_FILE'${NC}"
    fi
fi

echo -e "\n${GREEN}🎉 INSTALLATION COMPLETE!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📋 USAGE:${NC}"
echo -e "   • Type ${GREEN}colosseum${NC} from any directory"
echo -e "   • Auto-detects your hardware (M4 Beast, M1, etc.)"
echo -e "   • Suggests optimal agent configurations"  
echo -e "   • Launches Claude Code in Colosseum directory"
echo -e ""
echo -e "${YELLOW}🔄 Next Steps:${NC}"
echo -e "   1. Restart your terminal or run: ${GREEN}source $CONFIG_FILE${NC}"
echo -e "   2. Type: ${GREEN}colosseum${NC}"
echo -e "   3. Enjoy LIHTC domination! 🏛️"

# Show current setup
echo -e "\n${BLUE}📊 CURRENT SETUP:${NC}"
echo -e "   • Launcher: $LAUNCHER_PATH"
echo -e "   • Config: $CONFIG_FILE"
echo -e "   • Shell: $SHELL_NAME"
echo -e "   • Backup: ${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"