# Colosseum M4 Beast Configuration Suite

## 1. Main Configuration File: `.claude-code/colosseum-config.json`

```json
{
  "project": "COLOSSEUM_LIHTC_PLATFORM",
  "machine": "M4_BEAST",
  "version": "1.0.0",
  "lastUpdated": "2024-08-02",
  
  "systemContext": {
    "description": "Revolutionary Low-Income Housing Tax Credit (LIHTC) analysis platform transforming affordable housing development into systematic competitive advantage",
    "mission": "Where Housing Battles Are Won - providing imperial intelligence across all 54 US jurisdictions",
    "currentPhase": "Multi-State QAP Expansion",
    "primaryDeveloper": "Structured Consultants LLC"
  },
  
  "hardwareProfile": {
    "model": "MacBook Pro M4 Max",
    "memory": "128GB unified",
    "availableForLLM": "96GB",
    "cores": {
      "performance": 12,
      "efficiency": 4,
      "gpu": 40
    }
  },
  
  "agentCapabilities": {
    "STRIKE_LEADER": {
      "llmModel": "llama3.1:34b-instruct-q4_K_M",
      "endpoint": "http://localhost:11434",
      "primaryTasks": [
        "Multi-state QAP strategy coordination",
        "Cross-jurisdictional opportunity analysis",
        "Resource allocation for 54 jurisdictions",
        "Complex deal structure optimization"
      ],
      "memoryAllocation": "30GB",
      "contextWindow": 8192
    },
    "WINGMAN": {
      "llmModel": "llama3.1:70b-instruct-q4_K_M",
      "endpoint": "http://localhost:11435",
      "primaryTasks": [
        "Deep QAP analysis and extraction",
        "Legal hierarchy intelligence (Federal > State > Local)",
        "BOTN (Back-of-the-Napkin) calculations",
        "Regulatory compliance verification"
      ],
      "memoryAllocation": "55GB",
      "contextWindow": 16384
    },
    "ANALYSIS": {
      "llmModel": "mixtral:8x7b-instruct-q4_K_M",
      "endpoint": "http://localhost:11437",
      "primaryTasks": [
        "Financial modeling and projections",
        "Environmental screening analysis",
        "Transit compliance verification",
        "Market analysis integration"
      ],
      "memoryAllocation": "25GB",
      "contextWindow": 4096
    }
  },
  
  "colosseumModules": {
    "QAP_RAG": {
      "status": "active",
      "coverage": ["CA", "TX", "AZ", "NM", "HI"],
      "totalChunks": 27344,
      "chunkSize": 300,
      "overlap": 75,
      "embeddingModel": "BAAI/bge-large-en-v1.5"
    },
    "BOTN_ENGINE": {
      "status": "active",
      "features": [
        "130% basis boost optimization",
        "QCT/DDA verification with HUD 2025",
        "Multi-state tax credit calculations",
        "Sources and uses automation"
      ]
    },
    "ENVIRONMENTAL": {
      "status": "active",
      "databases": ["EPA", "TCEQ", "DTSC", "ADEQ"],
      "thresholds": {
        "cleanupSites": 500,
        "hazardousWaste": 1000,
        "leakingTanks": 500
      }
    },
    "TRANSIT": {
      "status": "active",
      "compliance": "CTCAC",
      "gtfsIntegration": true,
      "peakHourValidation": true
    }
  },
  
  "workflowOptimizations": {
    "parallelProcessing": {
      "enabled": true,
      "maxConcurrentQAPs": 3,
      "chunkBatchSize": 50
    },
    "caching": {
      "qapCache": "/Users/shared/colosseum-cache/qaps/",
      "embeddingCache": "/Users/shared/colosseum-cache/embeddings/",
      "ttlHours": 168
    },
    "escalationRules": {
      "claudeAI": {
        "complexityThreshold": 0.85,
        "multiStateAnalysis": true,
        "regulatoryInterpretation": true,
        "tokenThreshold": 12000
      }
    }
  },
  
  "localLLMIntegration": {
    "framework": "ollama",
    "alternativeFramework": "mlx",
    "modelPriority": {
      "reasoning": ["llama3.1:70b", "mixtral:8x7b", "llama3.1:34b"],
      "extraction": ["llama3.1:34b", "llama3.2:13b"],
      "validation": ["llama3.2:13b", "llama3.2:8b"]
    }
  }
}
```

## 2. Agent-Specific Context: `.claude-code/agent-contexts/`

### `strike_leader_context.md`

```markdown
# Strike Leader Context - Colosseum LIHTC Platform

You are the Strike Leader for the Colosseum LIHTC Platform, operating on the M4 Beast (128GB). Your role is strategic coordination across all 54 US jurisdictions for affordable housing development.

## Core Responsibilities

1. **Multi-State Strategy Coordination**
   - Analyze QAP updates across CA, TX, AZ, NM, HI
   - Identify cross-jurisdictional opportunities
   - Coordinate resource allocation between states
   - Track competitive landscapes

2. **Deal Pipeline Management**
   - Maintain pipeline of 100+ potential projects
   - Prioritize based on tax credit availability
   - Coordinate with local developers
   - Track success rates by jurisdiction

3. **Resource Orchestration**
   - Deploy Wingman agents for deep analysis
   - Coordinate with Tower for QA
   - Escalate complex issues to Claude.ai
   - Manage computational resources

## Current Priorities

1. **California 2024 QAP Changes**
   - New workforce housing bonus (10 points)
   - Transit proximity increase (5→8 points)
   - Sustainability requirements (5 points)

2. **Texas Expansion**
   - Extract and analyze 2024 QAP
   - Map QCT/DDA changes
   - Environmental database integration

3. **Cross-State Optimization**
   - Compare scoring matrices CA vs TX
   - Identify arbitrage opportunities
   - Develop multi-state strategies

## Key Metrics to Track

- QAP extraction accuracy: >99%
- Analysis time per state: <2 hours
- Cross-reference validation: 100%
- Deal identification rate: 15-20/week

## Integration Points

- **Wingman**: Deploy for deep QAP analysis
- **Analysis**: Financial modeling requests
- **Tower (M1)**: Validation checkpoints
- **Claude.ai**: Regulatory interpretation

## Command Shortcuts

- `qap:extract [state]` - Start QAP extraction
- `pipeline:status` - Current deal pipeline
- `deploy:wingman [task]` - Launch analysis
- `escalate:claude [issue]` - Complex problems
```

### `wingman_context.md`

```markdown
# Wingman Context - Deep Analysis Engine

You are Wingman, the primary analysis engine running on M4 Beast with the 70B model. Your role is deep technical analysis for the Colosseum LIHTC Platform.

## Core Capabilities

1. **QAP Document Processing**
   - Extract structured data from 100+ page PDFs
   - Preserve legal citation hierarchy
   - Identify scoring criteria changes
   - Map point allocations

2. **Regulatory Intelligence**
   - Federal IRC Section 42 compliance
   - State-specific requirements
   - Local overlays and preferences
   - Legal precedent analysis

3. **BOTN Calculations**
   - Instant feasibility analysis
   - 130% basis boost scenarios
   - QCT/DDA optimization
   - Multi-layered financing

## Technical Specifications

- **Model**: Llama 3.1 70B (Q4_K_M)
- **Context**: 16,384 tokens
- **Memory**: 55GB allocated
- **Optimal batch**: 10-15 documents

## Current Task Queue

1. **California QAP 2024**
   - Status: 85% complete
   - Remaining: Environmental crosswalk
   - Priority: HIGH

2. **Texas QAP Extraction**
   - Status: Pending
   - Estimated: 4 hours
   - Priority: MEDIUM

3. **Arizona DDA Updates**
   - Status: In queue
   - Dependencies: HUD data refresh
   - Priority: MEDIUM

## Processing Patterns

### QAP Extraction Pipeline
```python
1. PDF ingestion → OCR if needed
2. Section identification → Legal hierarchy
3. Criteria extraction → Point mapping
4. Cross-validation → Previous years
5. Change detection → Impact analysis
```

### Optimization Strategies
- Chunk documents at section boundaries
- Preserve legal references inline
- Parallel process non-dependent sections
- Cache intermediate representations

## Quality Checkpoints

- Extraction accuracy: >99.5%
- Citation preservation: 100%
- Point calculation variance: <0.1%
- Processing time/page: <3 seconds

## Escalation Triggers

- Ambiguous legal language → Claude.ai
- Multi-state conflicts → Strike Leader
- Calculation anomalies → Tower validation
- Missing dependencies → Secretary fetch
```

### `analysis_context.md`

```markdown
# Analysis Agent Context - Financial & Compliance Engine

You are the Analysis Agent running Mixtral 8x7B on M4 Beast. Your role is financial modeling, environmental screening, and compliance verification for Colosseum.

## Core Functions

1. **Financial Modeling**
   - Sources & uses optimization
   - Tax credit pricing analysis
   - Debt sizing calculations
   - Investor return projections

2. **Environmental Screening**
   - EPA database queries
   - State-specific searches
   - Risk threshold analysis
   - Phase I ESA cost estimates

3. **Transit Analysis**
   - GTFS route validation
   - Peak hour verification
   - Distance measurements
   - CTCAC compliance

## Integration APIs

### Environmental Databases
- EPA: `https://api.epa.gov/v1/`
- TCEQ: `https://tceq.texas.gov/api/`
- DTSC: `https://dtsc.ca.gov/api/`
- Buffer distances: 500-1000ft

### Transit Systems
- GTFS feeds: 147 agencies
- Update frequency: Daily
- Cache duration: 7 days
- Validation rules: CTCAC 2023

### Financial Data
- Tax credit prices: Weekly
- Interest rates: Daily
- Construction costs: Monthly
- Basis limits: Annual

## Optimization Parameters

```json
{
  "financial": {
    "iterations": 1000,
    "convergence": 0.001,
    "constraints": "standard",
    "outputs": ["IRR", "DSCR", "DY"]
  },
  "environmental": {
    "searchRadius": "1000ft",
    "databases": ["all"],
    "riskThreshold": "moderate"
  },
  "transit": {
    "peakHours": "6-9am, 4-7pm",
    "walkTime": "15min",
    "frequency": "30min"
  }
}
```

## Current Workload

1. **Project Queue**: 47 active
2. **Avg Runtime**: 4.3 min/project
3. **Cache Hit Rate**: 73%
4. **API Calls/Day**: 2,847

## Performance Metrics

- Model accuracy: 94.7%
- False positive rate: 2.1%
- Processing speed: 285 projects/day
- Memory efficiency: 87%
```

## 3. Startup Configuration: `.claude-code/startup.sh`

```bash
#!/bin/bash
# Colosseum M4 Beast Startup Script

echo "🏛️ Initializing Colosseum LIHTC Platform on M4 Beast"

# Set environment variables
export COLOSSEUM_HOME="/Users/$(whoami)/colosseum-workspace"
export COLOSSEUM_MACHINE="M4_BEAST"
export COLOSSEUM_MEMORY="128GB"
export CLAUDE_CODE_PROJECT="COLOSSEUM_LIHTC"

# Check which agent role to assume
if [ -z "$AGENT_ROLE" ]; then
    echo "Select agent role:"
    echo "1) Strike Leader (Strategic Coordination)"
    echo "2) Wingman (Deep Analysis)"
    echo "3) Analysis (Financial/Compliance)"
    read -p "Enter choice (1-3): " choice
    
    case $choice in
        1) export AGENT_ROLE="STRIKE_LEADER";;
        2) export AGENT_ROLE="WINGMAN";;
        3) export AGENT_ROLE="ANALYSIS";;
        *) echo "Invalid choice"; exit 1;;
    esac
fi

# Load agent-specific configuration
export AGENT_CONFIG="$HOME/.claude-code/agent-contexts/${AGENT_ROLE,,}_context.md"
export COLOSSEUM_CONFIG="$HOME/.claude-code/colosseum-config.json"

# Start appropriate Ollama instance
case $AGENT_ROLE in
    "STRIKE_LEADER")
        export OLLAMA_HOST="127.0.0.1:11434"
        export MODEL="llama3.1:34b-instruct-q4_K_M"
        export MEMORY_LIMIT="30GB"
        ;;
    "WINGMAN")
        export OLLAMA_HOST="127.0.0.1:11435"
        export MODEL="llama3.1:70b-instruct-q4_K_M"
        export MEMORY_LIMIT="55GB"
        ;;
    "ANALYSIS")
        export OLLAMA_HOST="127.0.0.1:11437"
        export MODEL="mixtral:8x7b-instruct-q4_K_M"
        export MEMORY_LIMIT="25GB"
        ;;
esac

# Ensure Ollama is running with correct model
if ! curl -s $OLLAMA_HOST/api/tags | grep -q "$MODEL"; then
    echo "Loading $MODEL..."
    ollama pull $MODEL
fi

# Create workspace structure
mkdir -p $COLOSSEUM_HOME/{missions,reports,shared,cache,outputs}

# Display configuration
echo "
✅ Colosseum Configuration Loaded
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Project: Colosseum LIHTC Platform
🤖 Agent: $AGENT_ROLE
💻 Machine: M4 Beast (128GB)
🧠 Model: $MODEL
🔗 Endpoint: $OLLAMA_HOST
📁 Workspace: $COLOSSEUM_HOME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mission: Where Housing Battles Are Won
Coverage: 54 US Jurisdictions
Focus: CA, TX, AZ, NM, HI

Type 'help' for Colosseum commands
"

# Set command aliases
alias qap-extract='python $COLOSSEUM_HOME/scripts/qap_extractor.py'
alias botn='python $COLOSSEUM_HOME/scripts/botn_calculator.py'
alias env-screen='python $COLOSSEUM_HOME/scripts/environmental_screener.py'
alias transit-check='python $COLOSSEUM_HOME/scripts/transit_analyzer.py'
alias pipeline-status='python $COLOSSEUM_HOME/scripts/pipeline_tracker.py'
alias deploy-agent='$COLOSSEUM_HOME/scripts/deploy_agent.sh'
alias mission-create='$COLOSSEUM_HOME/scripts/create_mission.sh'
alias report-analyze='python $COLOSSEUM_HOME/scripts/analyze_reports.py'

# Load mission if specified
if [ ! -z "$MISSION_ID" ]; then
    echo "Loading mission: $MISSION_ID"
    cat $COLOSSEUM_HOME/missions/$MISSION_ID.md
fi
```

## 4. Quick Reference Card: `.claude-code/colosseum-quick-ref.md`

```markdown
# Colosseum Quick Reference - M4 Beast

## System Overview
- **Platform**: Colosseum LIHTC Analysis System
- **Coverage**: 54 US jurisdictions
- **Focus States**: CA, TX, AZ, NM, HI
- **Database**: 27,344+ regulatory chunks

## Agent Roles & Models
| Agent | Model | Memory | Purpose |
|-------|-------|---------|----------|
| Strike Leader | Llama 34B | 30GB | Strategic coordination |
| Wingman | Llama 70B | 55GB | Deep QAP analysis |
| Analysis | Mixtral 8x7B | 25GB | Financial/Environmental |

## Key Commands
```bash
# QAP Operations
qap-extract CA 2024          # Extract California 2024 QAP
qap-compare CA 2023 2024     # Compare QAP years
qap-search "workforce"       # Search across QAPs

# Financial Analysis  
botn --project "Oak Plaza"   # Quick feasibility
botn --detailed --state CA   # Full underwriting
optimize-sources --tcc 50M   # Source optimization

# Environmental
env-screen --address "123 Main St"
env-screen --coords 34.0522,-118.2437
env-report --radius 1000ft

# Transit
transit-check --gtfs --peak
transit-routes --address "456 Oak Ave"
transit-score --ctcac 2024

# Deal Pipeline
pipeline-status --active
pipeline-add --csv deals.csv
pipeline-score --state CA

# Multi-Agent
deploy-agent WINGMAN "analyze Texas QAP"
mission-create "Q3 Pipeline Review"
coordinate-agents pipeline_review.yaml
```

## Performance Benchmarks
- QAP Extraction: ~100 pages/min
- BOTN Calculation: <30 seconds
- Environmental Screen: <10 seconds
- Transit Analysis: <15 seconds
- Full Project Analysis: ~5 minutes

## Escalation Thresholds
- Complexity > 0.85 → Claude.ai
- Multi-state analysis → Claude.ai  
- Ambiguous regulations → Strike Leader
- Memory > 90% → Reduce batch size
- API errors > 3 → Check connectivity

## File Locations
- Missions: `./missions/`
- Reports: `./reports/`
- Cache: `./cache/qaps/`
- Outputs: `./outputs/`
- Shared: `./shared/`

## Resource Monitoring
```bash
# Check memory usage
colosseum-monitor --memory

# Check model status
colosseum-monitor --models

# Check API health
colosseum-monitor --apis

# Full system check
colosseum-monitor --all
```

## Integration Endpoints
- Ollama Strike: http://localhost:11434
- Ollama Wingman: http://localhost:11435
- Ollama Analysis: http://localhost:11437
- ChromaDB: http://localhost:8000
- Monitor Dashboard: http://localhost:8080

Remember: "Vincere Habitatio" - To Conquer Housing 🏛️
```

## 5. Environment Variables: `.claude-code/.env`

```bash
# Colosseum M4 Beast Environment Configuration

# System Identity
COLOSSEUM_INSTANCE=M4_BEAST_001
COLOSSEUM_VERSION=1.0.0
MACHINE_MEMORY=128GB
MACHINE_TYPE=M4_MAX

# Agent Configuration
DEFAULT_AGENT_ROLE=STRIKE_LEADER
AGENT_MEMORY_LIMITS={"STRIKE_LEADER":"30GB","WINGMAN":"55GB","ANALYSIS":"25GB"}
CONCURRENT_AGENTS_MAX=3

# Model Endpoints
OLLAMA_ENDPOINTS={"STRIKE_LEADER":"http://localhost:11434","WINGMAN":"http://localhost:11435","ANALYSIS":"http://localhost:11437"}
MLX_ENABLED=true
MLX_PATH=/opt/homebrew/bin/mlx

# Colosseum Platform
COLOSSEUM_WORKSPACE=/Users/shared/colosseum-workspace
QAP_DATABASE_PATH=/Users/shared/colosseum-data/qaps
CACHE_PATH=/Users/shared/colosseum-cache
REPORT_OUTPUT_PATH=/Users/shared/colosseum-reports

# API Keys (encrypted)
EPA_API_KEY=encrypted:...
HUD_API_KEY=encrypted:...
CENSUS_API_KEY=encrypted:...
GOOGLE_MAPS_API_KEY=encrypted:...

# Performance Settings
CHUNK_BATCH_SIZE=50
PARALLEL_WORKERS=8
CACHE_TTL_HOURS=168
MAX_RETRIES=3
REQUEST_TIMEOUT=30

# Integration Settings
CHROMA_HOST=localhost
CHROMA_PORT=8000
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379

# Feature Flags
ENABLE_MLX_FALLBACK=true
ENABLE_RESPONSE_CACHING=true
ENABLE_PARALLEL_QAP=true
ENABLE_AUTO_ESCALATION=true
ENABLE_MEMORY_MONITORING=true

# Monitoring
METRICS_ENABLED=true
METRICS_PORT=8080
LOG_LEVEL=INFO
LOG_PATH=/Users/shared/colosseum-logs
ALERT_THRESHOLD_MEMORY=0.90
ALERT_THRESHOLD_LATENCY=30
```

## Implementation Instructions

1. **Create the directory structure**:
```bash
mkdir -p ~/.claude-code/agent-contexts
mkdir -p ~/colosseum-workspace/{missions,reports,shared,cache,outputs}
```

2. **Copy all configuration files** to their respective locations

3. **Make the startup script executable**:
```bash
chmod +x ~/.claude-code/startup.sh
```

4. **Add to your shell profile** (`.zshrc` or `.bash_profile`):
```bash
# Colosseum LIHTC Platform
alias colosseum='~/.claude-code/startup.sh'
export COLOSSEUM_HOME="$HOME/colosseum-workspace"
```

5. **Start Claude Code** with Colosseum context:
```bash
# Option 1: Interactive role selection
colosseum

# Option 2: Direct role assignment
AGENT_ROLE=WINGMAN colosseum

# Option 3: With specific mission
AGENT_ROLE=STRIKE_LEADER MISSION_ID=CA_QAP_2024 colosseum
```

Now when Claude Code starts on your M4 Beast, it will:
- Read the Colosseum configuration
- Understand its assigned role
- Know the platform's capabilities
- Have access to optimized commands
- Understand resource limits
- Know when to escalate to Claude.ai

This configuration maximizes your M4 Beast's capabilities while maintaining clear separation of concerns between agents and machines.
