# 🏛️ Universal Colosseum Command - Setup Guide

## Quick Installation

### 1. Install the Command
```bash
cd "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/config"
./install_colosseum_command.sh
```

### 2. Restart Terminal or Source Config
```bash
# For Zsh (default on macOS)
source ~/.zshrc

# For Bash
source ~/.bash_profile
```

### 3. Test the Command
```bash
colosseum
```

## How It Works

### Hardware Auto-Detection
The command automatically detects your system:

**M4 Beast (128GB)** → Full Beast Mode + Collaborative Options
```
🔥 STRIKE LEADER BEAST - 96GB exclusive (Maximum Strategic Power)
🔥 WINGMAN BEAST - 96GB exclusive (Maximum Analytical Power)  
⚡ THREE AGENT COLLABORATIVE - Strike Leader (30GB) + Wingman (55GB) + Tower (25GB)
⚡ TWO AGENT SPLIT - Strike Leader (60GB) + Wingman (60GB)
⚡ SINGLE AGENT FOCUS - Choose one agent with 80GB
```

**M4 Standard** → Enhanced Collaborative Mode
```
⚡ TWO AGENT OPTIMAL - Strike Leader + Wingman balanced
⚡ THREE AGENT LIGHT - All three agents with reduced memory
⚡ SINGLE AGENT FOCUS - Choose one agent with maximum memory
```

**M1/M2/M3** → Optimized Collaborative Mode
```
🚀 SINGLE AGENT OPTIMIZED - Best performance for your memory
🚀 TWO AGENT LIGHT - Strike Leader + Wingman (reduced memory)
🚀 THREE AGENT MINIMAL - All three agents (light mode)
```

### Agent Roles
**Strike Leader**: Strategic coordination across 54 LIHTC jurisdictions
**Wingman**: Deep QAP analysis + 2,159 definition intelligence  
**Tower**: Quality assurance and oversight

## Usage Examples

### Basic Usage
```bash
# From any directory
colosseum

# Follow the prompts to select configuration
# Claude Code launches automatically in Colosseum directory
```

### What Happens
1. **Hardware Detection**: Identifies M4 Beast, M1, etc.
2. **Smart Suggestions**: Recommends optimal configurations
3. **User Choice**: Select your preferred setup
4. **Auto-Navigation**: Changes to Colosseum directory
5. **Claude Code Launch**: Starts with proper agent context

## Beast Mode (M4 Beast Only)

### Strike Leader Beast (96GB)
- Complete 54-jurisdiction strategic analysis
- Portfolio-level optimization
- Crisis response capabilities  
- Master deal pipeline coordination

### Wingman Beast (96GB)
- Complete QAP extraction (200+ pages)
- All 2,159 LIHTC definitions loaded
- Advanced BOTN calculations
- Deep legal hierarchy analysis

## Configuration Files

### Main Configuration
- `colosseum-config.json` - Hardware profiles and agent capabilities
- `universal_colosseum_launcher.sh` - Main launcher script
- `m1_configurations.json` - M1/M2/M3 optimizations

### Agent Contexts
- `strike_leader_beast_context.md` - Beast Mode strategic context
- `wingman_beast_context.md` - Beast Mode analytical context
- `claude_code_integration.md` - Claude Code integration guide

## Troubleshooting

### Command Not Found
```bash
# Re-run installer
cd "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/config"
./install_colosseum_command.sh

# Restart terminal or source config
source ~/.zshrc  # or ~/.bash_profile
```

### Claude Code Not Found
The launcher will notify you if Claude Code isn't in PATH. You can:
1. Install Claude Code in PATH
2. Manually start Claude Code from the Colosseum directory

### Permission Issues
```bash
# Make scripts executable
chmod +x "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/config/"*.sh
```

## Advanced Features

### Environment Variables
When Claude Code launches, these are set:
- `COLOSSEUM_AGENT_ROLE` - Selected agent configuration
- `COLOSSEUM_AGENT_CONFIG` - Human-readable configuration
- `COLOSSEUM_HARDWARE_TYPE` - Detected hardware
- `COLOSSEUM_MEMORY_SIZE` - Available memory

### Custom Configurations
Edit `colosseum-config.json` to customize:
- Memory allocations
- Model selections  
- Beast Mode thresholds
- Performance targets

## Next Steps

1. **Install**: Run the installer script
2. **Test**: Type `colosseum` from any directory
3. **Configure**: Choose your optimal agent setup
4. **Dominate**: Start conquering LIHTC markets! 🏛️

---

**Mission**: Vincere Habitatio - To Conquer Housing

**From anywhere to everywhere** - The Colosseum command brings the full power of the LIHTC platform to your fingertips, regardless of your hardware or location.