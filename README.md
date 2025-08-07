# 🏟️ COLOSSEUM LIHTC Platform

**"Where Housing Battles Are Won"**

A comprehensive LIHTC (Low-Income Housing Tax Credit) analysis and development platform built for affordable housing developers competing in the modern tax credit arena.

## 🎯 Mission

Colosseum provides developers with imperial intelligence across all 54 US jurisdictions, transforming the complex battlefield of affordable housing development into systematic competitive advantage.

## 🏗️ Architecture

### 🤖 Agent Coordination System
- **STRIKE_LEADER**: Strategic coordination & planning
- **WINGMAN**: Technical implementation & performance optimization  
- **TOWER**: Quality assurance & strategic oversight
- **SECRETARY**: Deal flow management & administrative automation

### 🧠 Intelligence Hub
- **think_tank/**: Strategic intelligence and shared knowledge
- **opus_research_library/**: Organized research library with master catalog
- **agents/**: Multi-agent coordination and mission management

### 📦 Core Modules
- **lihtc_analyst/**: Complete LIHTC platform including BOTN engine, pipeline management
- **data_intelligence/**: CoStar processing, transit analysis, environmental screening
- **integration/**: API endpoints, data transformers, workflow automation

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- API keys configured in `config/api_keys.json`
- Access to `/Data_Sets/` directory (symlinked as `data_sets/`)

### Launch Options
```bash
# Complete ecosystem
python3 launchers/launch_all_agents.py

# Individual agents
python3 launchers/launch_strike_leader.py
python3 launchers/launch_wingman.py
python3 launchers/launch_tower.py
python3 launchers/launch_secretary.py

# Development environment
python3 launchers/launch_development_session.py
```

## 📊 Vitor's 7-Step Workflow Integration

1. **Upload CoStar CSV** → `modules/data_intelligence/costar_processor/`
2. **Filter Sites** → `modules/integration/api_endpoints/filter_api.py`
3. **Environmental Check** → `modules/data_intelligence/environmental_screening/`
4. **Transit Analysis** → `modules/data_intelligence/transit_analysis/`
5. **BOTN Calculator** → `modules/lihtc_analyst/botn_engine/`
6. **Full Underwriting** → `modules/lihtc_analyst/full_underwriting/`
7. **Deal Execution** → `modules/lihtc_analyst/broker_outreach/` + `pipeline_manager/`

## 🎯 Target Markets

### California Priorities
- Transit distance and frequency (highest scoring weight)
- Highest/High Resource Area mapping
- Wildfire risk zones (insurance impact analysis)
- FEMA flood mapping integration

### Texas Priorities  
- QCT/DDA optimization strategies
- TCEQ environmental screening protocols
- Transit requirements (different from CA)
- Opportunity zone benefit analysis

## 🛠️ Development

### Test-Driven Development
```bash
# Run tests
python3 -m pytest tests/

# Specific test modules
python3 -m pytest tests/test_costar_processor.py
python3 -m pytest tests/test_transit_analysis.py
```

### Agent Communication Protocol
- File-based coordination via mission briefs and completion reports
- Real-time status updates in `agents/coordination/shared_status/`
- Daily standups documented in `agents/coordination/daily_standups/`

## 📚 Documentation

- **API Reference**: `docs/API_REFERENCE.md`
- **Workflow Guide**: `docs/WORKFLOW_GUIDE.md`  
- **QAP Cheat Sheet**: `docs/QAP_CHEATSHEET.md`
- **Best Practices**: `docs/best_practices.md`

## 🏛️ Roman Theme

Colosseum draws inspiration from Roman architectural excellence and systematic organization:
- **Colosseum**: Where gladiators (developers) compete for victory (tax credits)
- **Imperial Scale**: 54 jurisdictions under unified command
- **Systematic Excellence**: Like Roman engineering, built to last and perform

## 📈 Business Value

- **Competitive Intelligence**: Beat competitors with superior data analysis
- **Risk Mitigation**: Environmental and regulatory screening before investment
- **Deal Flow Management**: Automated broker outreach and pipeline tracking
- **Professional Underwriting**: Complete sources & uses with investor packages

## 🔧 Configuration

Key configuration files:
- `config/api_keys.json`: Service credentials
- `config/ca_qap_rules.json`: California-specific requirements
- `config/tx_requirements.json`: Texas-specific configurations
- `config/environment_settings.json`: Dev/prod environment settings

## 📊 Data Integration

- **Federal Sources**: HUD, Census, FEMA, EPA integration
- **State QAPs**: All 54 jurisdictions with 96.4% coverage
- **Environmental**: TCEQ, EnviroStor, GeoTracker databases
- **Transit**: GTFS feeds, HQTA designations, distance calculations

---

**Built by Structured Consultants LLC**  
*Transforming affordable housing development through superior intelligence*

**Vincere Habitatio** - *"To Conquer Housing"*