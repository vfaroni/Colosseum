# 🏛️ COLOSSEUM LIHTC Platform - Development Best Practices

**"Where Housing Battles Are Won"**

*Required reading for all agents - Updated daily by development team*

---

## 🎯 **CORE DEVELOPMENT PRINCIPLES**

### **1. Roman Engineering Standards**
- **Build to Last**: Code for 2000+ year reliability (like Roman architecture)
- **Systematic Excellence**: Follow established patterns and conventions
- **Imperial Scale**: Design for 54-jurisdiction expansion from day one
- **Competitive Advantage**: Every feature must beat existing LIHTC solutions

### **2. Agent Coordination Protocol**
- **STRIKE LEADER**: Issues detailed mission briefs with context and success criteria
- **WINGMAN**: Delivers completion reports with performance data and recommendations  
- **TOWER**: Provides strategic oversight and risk assessment for all activities
- **SECRETARY**: Manages deal flow and administrative automation seamlessly

---

## 🔧 **TECHNICAL STANDARDS**

### **Git Workflow**
```bash
# Always create feature branches
git checkout -b feature/agent-name/feature-description

# Commit message format
git commit -m "[MODULE] Clear description of changes

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Pull from main before starting daily work
git pull origin main

# Merge to main only after testing
```

### **Python Code Standards**
- **Always use `python3`** - Never use `python` command
- **Type hints required** for all function signatures
- **Docstrings mandatory** for all public functions and classes
- **Error handling** - Graceful degradation, never crash silently
- **Performance first** - Profile before optimizing, but design for scale

### **File Organization**
```
modules/
├── lihtc_analyst/          # Core LIHTC analysis
├── data_intelligence/      # Data processing and APIs
└── integration/           # System connections
```

### **API Integration**
- **Cache all external API calls** - Respect rate limits, preserve data
- **Fallback strategies** - Always have Plan B for data sources
- **Official sources only** - HUD, Census, FEMA, state agencies
- **Error logging** - Comprehensive tracking for debugging

---

## 📊 **DATA QUALITY STANDARDS**

### **LIHTC Compliance Requirements**
- **Federal Authority Hierarchy**: IRC Section 42 > CFR > Revenue Procedures > State QAP
- **HUD Methodology**: Verified against Novogradac calculator (100% accuracy required)
- **QCT/DDA Verification**: All 4 HUD datasets integrated (Metro/Non-Metro × QCT/DDA)
- **Distance Measurements**: Truncated to 2 decimal places (never rounded up)

### **Geospatial Data Standards**
- **Coordinate System**: WGS84 (EPSG:4326) for all spatial data
- **Accuracy Requirements**: ±10 meter precision for LIHTC compliance
- **Source Attribution**: Complete metadata for all geospatial datasets
- **Backup Sources**: Minimum 2 independent data sources for critical measurements

---

## 🧪 **TESTING REQUIREMENTS**

### **Test-Driven Development**
```bash
# Run tests before committing
python3 -m pytest tests/

# Specific test modules
python3 -m pytest tests/test_qct_dda_analyzer.py -v

# Coverage requirements: 80% minimum
python3 -m pytest --cov=src tests/
```

### **Integration Testing**
- **End-to-end workflows** - Test complete Vitor 7-step process
- **Cross-jurisdictional** - Validate across CA, TX, and 2+ other states
- **Performance benchmarks** - Sub-200ms response times for API calls
- **Error scenarios** - Test graceful handling of API failures and bad data

---

## 🏛️ **ROMAN-THEMED DEVELOPMENT**

### **Naming Conventions**
- **Variables**: `snake_case` for Python, clear descriptive names
- **Functions**: Action verbs that describe business purpose
- **Classes**: Roman architectural terms where appropriate (`BasilicaEngine`, `ForumAnalytics`)
- **Latin Mottos**: Used sparingly for inspiration, not confusion

### **Documentation Standards**
- **README files**: Include Roman theme context and business value
- **Code comments**: Explain *why*, not *what* (self-documenting code)
- **API documentation**: Professional grade for client handoffs
- **Change logs**: Roman-themed but professionally informative

---

## 💰 **BUSINESS VALUE FOCUS**

### **Revenue-First Development**
- **Every feature** must demonstrate competitive advantage over existing tools
- **Time savings** - Quantify hours saved vs manual processes
- **Accuracy improvements** - Measure precision gains vs industry standard
- **Market differentiation** - How does this beat Novogradac/RentSpree/etc?

### **Client Success Metrics**
- **Developer wins** - Track successful LIHTC awards using our tools
- **Processing speed** - Applications completed faster with our system
- **Error reduction** - Fewer QAP compliance issues in submissions
- **Cost savings** - Reduced consultant fees through automation

---

## 🔍 **CODE REVIEW CHECKLIST**

### **Before Committing**
- [ ] All tests pass locally
- [ ] Code follows naming conventions
- [ ] Performance implications considered
- [ ] Error handling implemented
- [ ] Documentation updated
- [ ] Roman theme maintained (where appropriate)

### **Pull Request Requirements**
- [ ] Clear description of changes and business impact
- [ ] Testing strategy documented
- [ ] Breaking changes highlighted
- [ ] Integration with existing agent workflows confirmed
- [ ] Performance benchmarks included (if applicable)

---

## 🚨 **CRITICAL REMINDERS**

### **Never Repeat These Mistakes**
1. **Wrong HUD Methodology** - Always use verified Novogradac-matching calculations
2. **Manual QCT/DDA Lookup** - Use comprehensive HUD datasets, not website scraping
3. **Coordinate Rounding** - CTCAC measurements must be truncated, never rounded up
4. **Missing Agent QA** - All multi-agent deliverables must be validated before integration

### **Production Safety**
- **API Keys**: Never commit to repository, use environment variables
- **Large Files**: Use Git LFS for datasets >100MB
- **Sensitive Data**: PII and confidential info stays local, never committed
- **Backup Strategy**: Critical analysis results backed up to multiple locations

---

## 🏛️ **TEAM PHILOSOPHY**

**"Small team, nimble execution, professional quality, maximum business impact"**

### **Our Competitive Advantages**
1. **Most Comprehensive Data**: 54 jurisdictions + federal integration
2. **Highest Accuracy**: Verified against industry gold standards
3. **Roman Reliability**: Built to last and scale like imperial infrastructure
4. **Developer Focus**: Tools made by developers, for developers

### **Success Metrics**
- **Technical Excellence**: Code quality and performance as primary metrics
- **Business Impact**: Every feature tied to market differentiation
- **Client Success**: Developer wins using our tools in the field
- **Team Velocity**: Rapid iteration without sacrificing quality

---

**🏛️ Vincere Habitatio - "To Conquer Housing" 🏛️**

*Updated: Daily by Strike Leader*  
*Next Review: Before each development session*