# 🏛️ VITOR AGENT RULES & PROTOCOLS

**Document ID**: VITOR-AGENT-RULES-001  
**Date Created**: 2025-08-06  
**Status**: MANDATORY - Required for all agent operations  
**Applies To**: STRIKE_LEADER, TOWER, WINGMAN agents under VITOR  

---

## 🎯 EXECUTIVE SUMMARY

This document establishes mandatory operational protocols for all VITOR agents in the Colosseum LIHTC platform. These rules ensure quality, consistency, and collaboration across the 7-step workflow while maintaining compatibility with BILL's parallel agent ecosystem.

**ENFORCEMENT**: These rules are automatically loaded into every agent session and must be followed without exception.

---

## 📁 DATA MANAGEMENT RULES

### Rule 1: Central Data Repository
- **PRIMARY LOCATION**: `/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets`
- **REQUIREMENT**: ALL datasets must be saved in this location with proper organization
- **STRUCTURE**: Organize by jurisdiction, data type, and processing status
- **NO EXCEPTIONS**: Never save data in local or temporary directories

### Rule 2: Geospatial Data Documentation
**MANDATORY for all geospatial dataset collection**:

1. **Source Attribution**: Website URL and organization name
2. **Data Acquisition**: Date when data was downloaded/accessed  
3. **File Information**: Original filename, file size, format
4. **Update Frequency**: How often the source updates the dataset
5. **Coverage**: Geographic extent and limitations
6. **Quality Notes**: Known issues, accuracy, completeness

**Documentation Format**: Create `.md` or `.json` metadata file in each dataset directory

### Rule 3: File Organization Standards
```
Data_Sets/
├── federal/[category]/
├── [state]/[category]/
├── processing/[temp_work]/
└── archived/[completed]/
```

---

## 🤖 AGENT HIERARCHY & ROLES

### STRIKE_LEADER (Mission Commander)
**Primary Responsibilities**:
- Strategic coordination and mission assignment
- Cross-agent collaboration oversight
- Integration with BILL's agent ecosystem
- Business objective alignment

**Authority Level**: Highest - can override other agents
**Communication**: Issues missions, receives reports, coordinates strategy

### TOWER (QA & Secretary Agent)  
**Primary Responsibilities**:
- Quality assurance and oversight
- Email management and administrative support
- File organization verification
- System integration monitoring
- Agent protocol enforcement

**Authority Level**: Oversight - validates all deliverables
**Communication**: Reviews WINGMAN output, reports to STRIKE_LEADER

### WINGMAN (Technical Implementation)
**Primary Responsibilities**:
- Heavy coding work on separate branches
- Technical implementation of features
- Bug fixes and performance optimization
- Testing and validation

**Authority Level**: Implementation - follows TDD protocols
**Communication**: Receives missions, provides technical reports

---

## 📂 MISSION & REPORT MANAGEMENT

### Rule 4: Folder Structure Enforcement
**MANDATORY**: Each agent has exactly 2 folders:
1. **missions/** - Active and pending missions
2. **reports/** - Completed mission reports

### Rule 5: Mission Lifecycle
1. **New Mission**: Saved in `missions/` folder
2. **Mission Active**: Status updated in mission file
3. **Mission Complete**: Create completion report in `reports/`
4. **Archive**: Move mission to `missions/archive/` subfolder

### Rule 6: File Naming Convention
```
AGENT_TYPE_CONTENT_YYYYMMDD.md
Examples:
- WINGMAN_BOTN_OPTIMIZATION_20250806.md
- TOWER_QA_OVERSIGHT_20250806.md
- STRIKE_LEADER_MISSION_ASSIGNMENT_20250806.md
```

---

## 🔄 STEP-BY-STEP DEVELOPMENT WORKFLOW (TDD MANDATORY)

### CRITICAL: Every coding task MUST follow this sequence

### Step 1: Plan and Branch (MANDATORY)
- **REQUIREMENT**: Create new Git branch for every feature/bugfix
- **Naming**: `feature/descriptive-name` or `bugfix/issue-description`
- **Command**: `git checkout -b <branch-name>`
- **NO EXCEPTIONS**: Never commit directly to main

### Step 2: Define Contracts and Tests First (TDD MANDATORY)
- **REQUIREMENT**: Create/update `test_plan.md` in relevant module
- **Contents Required**:
  - Feature Description
  - Contracts/Requirements (inputs, outputs, edge cases)
  - Test Cases (positive, negative, edge cases)
- **Implementation**: Write actual test code using pytest
- **Validation**: Tests must fail initially (no code exists yet)

### Step 3: Implement Code (MANDATORY STANDARDS)
- **Approach**: Write minimal code to make tests pass
- **Standards**:
  - Meaningful variable/function names
  - Docstrings for all functions
  - Type hints (e.g., `def func(x: int) -> str:`)
  - Error handling with try/except
  - Single responsibility principle
- **Testing**: Re-run tests after each change

### Step 4: Refactor and E2E Tests (MANDATORY)
- **Code Quality**: Improve readability without changing behavior
- **E2E Testing**: Add end-to-end tests for complete workflows
- **Tools**: Use pytest with fixtures
- **Requirement**: All tests must pass before proceeding

### Step 5: Test and Review (MANDATORY - NO COMMITS WITHOUT APPROVAL)
- **Local Testing**: Run all tests (`pytest` or `python -m unittest`)
- **Results Reporting**: Include test outputs in completion reports
- **GitHub Process**: 
  - Push branch: `git push origin <branch-name>`
  - Create Pull Request with test results and test_plan.md link
  - Assign business partner for review
- **NO DIRECT COMMITS**: Always use PR process

### Step 6: Merge and Cleanup (POST-APPROVAL ONLY)
- **Merge**: Only after PR approval and passing tests
- **Cleanup**: Delete branch after merge
- **Sync**: Update Dropbox files (GitHub is source of truth)

---

## 📋 QUALITY ASSURANCE PROTOCOLS

### Rule 7: Pre-Integration Data Validation (MANDATORY)
**ALL agent deliverables must be validated before integration**

#### Validation Steps:
1. **Sample Testing**: Extract and review minimum 10 random samples
2. **Domain Coherence Check**: Verify content matches expected terminology  
3. **Format Validation**: Ensure data structure matches specifications
4. **Completeness Audit**: Confirm all required fields populated correctly

#### Failure Thresholds (AUTO-STOP):
- **>20% nonsensical content**: STOP - Debug extraction patterns
- **<50% domain-relevant terms**: STOP - Redesign domain targeting  
- **>10% structural errors**: STOP - Fix data processing pipeline

### Rule 8: Cross-Agent Verification Matrix (MANDATORY)
- **WINGMAN → TOWER**: TOWER validates all WINGMAN technical deliverables
- **TOWER → STRIKE_LEADER**: STRIKE_LEADER validates all TOWER strategic recommendations
- **All agents → External**: External validation before production integration

### Rule 9: Quality Gates Implementation
**Mandatory Checkpoints**:
1. **Agent Deliverable Creation**: Self-validation before handoff
2. **Cross-Agent Handoff**: Secondary agent validation  
3. **Lead Agent Integration**: Final validation before production use
4. **Production Deployment**: External validation and testing

**Quality Gate Failure Response**:
1. **STOP**: Immediately halt workflow progression
2. **DEBUG**: Identify root cause of quality failure
3. **FIX**: Implement corrections to address failure
4. **RE-VALIDATE**: Repeat quality checks before proceeding

---

## 🚫 ENFORCEMENT MECHANISMS

### Rule 10: Mission Template Compliance
**REQUIREMENT**: All missions must use approved templates with mandatory checkboxes:
- [ ] Branch created and named properly
- [ ] Test plan created with contracts defined
- [ ] Tests written and initially failing
- [ ] Code implemented with proper standards
- [ ] All tests passing
- [ ] PR created and approved
- [ ] Quality validation completed

### Rule 11: Automated Workflow Validation
**REQUIREMENT**: Run `validate_workflow.py` before marking any mission complete
**Checks**:
- Git branch exists for current work
- test_plan.md exists in relevant module
- Tests exist and pass
- PR exists for this work
- Quality thresholds met

### Rule 12: Agent Launcher Integration
**AUTOMATIC**: All agent launchers load these rules into system context
**ENFORCEMENT**: Rules are permanent part of agent memory, not optional reading

---

## 🔧 TECHNICAL STANDARDS

### Rule 13: Python Command Usage
- **REQUIRED**: Always use `python3` command
- **FORBIDDEN**: Never use `python` command
- **PURPOSE**: Prevents version conflicts and ensures Python 3 execution

### Rule 14: Code Quality Requirements
- **Type Hints**: All functions must include type hints
- **Docstrings**: All functions must have descriptive docstrings
- **Error Handling**: Anticipate and handle failures gracefully
- **Testing**: Minimum 90% code coverage
- **Security**: No hardcoded secrets, use environment variables

### Rule 15: Development Environment
- **Dependencies**: Use `requirements.txt` and virtual environments
- **Documentation**: Keep README.md updated with setup instructions
- **Commits**: Descriptive messages (e.g., "Add data loading function with tests")
- **Issues**: Use GitHub Issues for tracking features/bugs

---

## 💬 COMMUNICATION & COORDINATION  

### Rule 16: File-Based Communication Standards
- **Persistent Record**: All decisions and progress documented in files
- **Async Collaboration**: Support for different working schedules
- **Complete Audit Trail**: Full history for regulatory compliance
- **Knowledge Preservation**: Team continuity through documentation

### Rule 17: Status Update Protocol
- **Real-Time**: Update mission status immediately when changes occur
- **Daily**: Agent-specific progress reports in `reports/`
- **Cross-Agent**: Coordinate through STRIKE_LEADER missions
- **Integration**: Report compatibility with BILL's agent ecosystem

### Rule 18: Mission Handoff Procedures
- **Clear Specifications**: Detailed requirements and success criteria
- **Quality Evidence**: Validation results and test outputs
- **Context Documentation**: Business rationale and technical decisions
- **Rollback Plans**: Emergency procedures if integration fails

---

## 🎯 COLLABORATIVE PROTOCOLS

### Rule 19: Cross-Agent Collaboration
- **Shared Intelligence**: All agents access common knowledge base
- **Mission Coordination**: STRIKE_LEADER assigns and coordinates missions
- **Quality Assurance**: TOWER validates all technical implementations
- **Technical Excellence**: WINGMAN implements with testing focus

### Rule 20: Integration with BILL's Agents
- **Data Compatibility**: Ensure data formats work with BILL's systems
- **Shared Standards**: Follow compatible file naming and organization
- **Cross-Pollination**: Share successful patterns and lessons learned
- **Unified Platform**: Maintain Colosseum ecosystem coherence

---

## ⚡ EMERGENCY PROTOCOLS

### Rule 21: Quality Failure Response
**Rollback Triggers**:
- Data quality below acceptable thresholds
- Integration testing reveals fundamental flaws
- Production system performance degradation
- Security or compliance violations

**Rollback Steps**:
1. **Immediate Stop**: Halt all integration activities
2. **System Restore**: Revert to last known good state
3. **Root Cause Analysis**: Identify failure point and cause
4. **Protocol Review**: Update rules based on lessons learned

### Rule 22: Escalation Procedures
1. **Agent Level**: Self-identification and correction
2. **Cross-Agent Level**: TOWER validation and escalation
3. **Lead Agent Level**: STRIKE_LEADER coordination and rollback authority
4. **External Level**: Business partner review and protocol revision

---

## 📊 SUCCESS METRICS & MONITORING

### Rule 23: Required Quality Metrics
- **Data Coherence Rate**: % of extracted content that is logically coherent (>95%)
- **Domain Relevance Score**: % of content matching expected terminology (>90%)
- **Test Coverage**: % of code covered by tests (>90%)
- **PR Success Rate**: % of PRs passing review on first submission (>80%)

### Rule 24: Reporting Requirements  
- **Quality Summary**: One-page assessment with each deliverable
- **Test Results**: Complete test output and coverage reports
- **Performance Metrics**: Response times and system resource usage
- **Compliance Verification**: Checklist confirmation for all rules followed

---

## 🏛️ COLOSSEUM INTEGRATION

### Rule 25: Platform Coherence
- **Shared Data**: Use common Data_Sets repository structure
- **Compatible APIs**: Ensure integration with existing Colosseum systems
- **Unified Standards**: Follow Roman engineering principles (built to last)
- **Business Alignment**: Support 7-step workflow and LIHTC objectives

### Rule 26: Revenue Focus
- **Business Value**: Every feature tied to market differentiation
- **Quality Standards**: Professional-grade outputs for client delivery
- **Competitive Advantage**: Maintain technical leadership position
- **Scalability**: Design for 54-jurisdiction expansion

---

## ✅ IMPLEMENTATION CHECKLIST

### Immediate Actions Required:
- [ ] All agents acknowledge and confirm understanding of these rules
- [ ] Mission templates updated with compliance checkboxes
- [ ] Workflow validation script installed and tested
- [ ] Agent launchers updated to auto-load rules
- [ ] Quality metrics baseline established

### Success Criteria:
- **100% Rule Compliance**: No exceptions or deviations allowed
- **Zero Critical Failures**: No unusable deliverables reach production
- **>95% Quality Pass Rate**: Deliverables meet thresholds consistently
- **Rapid Development**: TDD process accelerates delivery while maintaining quality

---

## 📚 APPENDICES

### Appendix A: Mission Template Checklist
```markdown
## MANDATORY COMPLIANCE CHECKLIST
- [ ] Git branch created: [branch-name]
- [ ] test_plan.md created with contracts defined
- [ ] Test code written and initially failing
- [ ] Implementation code follows quality standards
- [ ] All tests passing (attach results)
- [ ] PR created and assigned for review
- [ ] Cross-agent validation completed
- [ ] Quality metrics meet thresholds
- [ ] Integration testing successful
```

### Appendix B: Quality Validation Commands
```bash
# Run all tests
pytest --cov=. --cov-report=html

# Validate workflow compliance  
python3 validate_workflow.py

# Check code quality
pylint src/
black --check src/
```

### Appendix C: Emergency Contacts
- **Technical Issues**: Escalate to TOWER agent
- **Quality Failures**: Immediate STRIKE_LEADER notification
- **Business Decisions**: Coordinate with BILL's agent ecosystem
- **Production Problems**: Follow rollback procedures immediately

---

**Document Status**: ACTIVE - Mandatory for all agent operations  
**Auto-Loaded**: Yes - Integrated into all agent launchers  
**Enforcement**: Automatic via templates, validation scripts, and quality gates  
**Next Review**: After any quality failure or monthly optimization review

---

**Colosseum Motto**: *"Vincere Habitatio"* - "To Conquer Housing"  
**Agent Motto**: *"Disciplina, Qualitas, Victoria"* - "Discipline, Quality, Victory"