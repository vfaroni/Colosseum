# ⚡ WINGMAN TECHNICAL MISSION TEMPLATE

**Mission ID**: VITOR-WINGMAN-[MISSION_NUMBER]  
**Agent**: WINGMAN  
**Date Assigned**: [YYYY-MM-DD]  
**Mission Type**: [FEATURE_DEVELOPMENT/BUG_FIX/PERFORMANCE_OPTIMIZATION/INTEGRATION]  
**Priority**: [HIGH/MEDIUM/LOW]  
**Estimated Complexity**: [SIMPLE/MEDIUM/COMPLEX]

---

## 🎯 MISSION OBJECTIVE

**Primary Goal**: [Specific technical objective]  
**Technical Context**: [How this fits into the 7-step workflow or system architecture]  
**Success Definition**: [Specific, measurable technical success criteria]

---

## 📋 MANDATORY TDD COMPLIANCE CHECKLIST

**CRITICAL**: All development workflow steps must be completed in order

### Step 1: Plan and Branch (MANDATORY)
- [ ] **Git Branch Created**: Branch name: `_________________`
- [ ] **Branch Type**: [feature/bugfix/hotfix] + descriptive name
- [ ] **Current Branch Verified**: NOT working on main/master
- [ ] **Branch Pushed**: `git push -u origin [branch-name]`

### Step 2: Define Contracts and Tests First (TDD MANDATORY)
- [ ] **test_plan.md Created**: Location: `_________________`
- [ ] **Feature Description**: Clear overview of code/module purpose
- [ ] **Contracts Defined**: Inputs, outputs, error handling specified
- [ ] **Test Cases Documented**: Positive, negative, and edge cases listed
- [ ] **Test Files Created**: Using pytest framework: `_________________`
- [ ] **Initial Test Run**: Tests failing (no code implemented yet) ✅

### Step 3: Implement Code (MANDATORY STANDARDS)
- [ ] **Minimal Code**: Only enough code to make tests pass
- [ ] **Meaningful Names**: Variables and functions clearly named
- [ ] **Docstrings Added**: All functions have """Description""" docstrings
- [ ] **Type Hints**: All functions have type hints (e.g., `def func(x: int) -> str:`)
- [ ] **Error Handling**: try/except blocks for anticipated failures
- [ ] **Single Responsibility**: Functions focused on one task
- [ ] **Test Validation**: Tests pass after implementation

### Step 4: Refactor and E2E Tests (MANDATORY)
- [ ] **Code Refactored**: Improved readability without changing behavior
- [ ] **Tests Still Pass**: All existing tests continue to pass
- [ ] **E2E Tests Added**: Full workflow tests for larger features
- [ ] **Integration Tests**: Testing how parts work together
- [ ] **Performance Validated**: Performance targets met

### Step 5: Test and Review (MANDATORY - NO COMMITS WITHOUT APPROVAL)
- [ ] **All Tests Run**: `pytest` or `python3 -m unittest` executed
- [ ] **Test Results**: Attached below with pass/fail counts
- [ ] **Code Quality Check**: `validate_workflow.py` executed successfully
- [ ] **Pull Request Created**: PR URL: `_________________`
- [ ] **PR Description**: Includes changes, test results, test_plan.md link
- [ ] **Review Assigned**: Business partner assigned for review
- [ ] **Review Approved**: Approval date: `_________________`

---

## 🔧 TECHNICAL SPECIFICATIONS

### System Architecture Context:
- **Module Location**: [Specific directory and files to be modified]
- **Dependencies**: [List any new dependencies needed]
- **Integration Points**: [APIs, databases, services that will be affected]
- **Backward Compatibility**: [Compatibility requirements with existing code]

### Environment Setup:
- **Python Version**: Python 3.x (use `python3` command only)
- **Virtual Environment**: [Specific venv requirements]
- **Required Packages**: [List packages needed for implementation]
- **Development Tools**: [Testing frameworks, linting tools, etc.]

### Performance Requirements:
- **Response Time**: [Specific performance targets]
- **Memory Usage**: [Memory constraints or requirements]
- **Throughput**: [Processing capacity requirements]
- **Scalability**: [Scale requirements and considerations]

---

## 🧪 TESTING REQUIREMENTS

### Test Plan Structure (test_plan.md):
```markdown
# Test Plan for Module: [MODULE_NAME]

## Feature Description
[Brief overview of what the code/module does]

## Contracts
- Input: [Expected input format and validation]
- Output: [Expected output format and structure]
- Errors: [Error conditions and handling]

## Test Cases
### Unit Tests (Small, focused tests)
- Test 1: [Positive case - normal scenario]
- Test 2: [Negative case - error condition]  
- Test 3: [Edge case - boundary condition]

### Integration Tests (How parts work together)
- Integration Test 1: [Component interaction test]
- Integration Test 2: [End-to-end workflow test]
```

### Test Implementation Requirements:
- **Framework**: Use pytest (preferred) or unittest
- **File Location**: `tests/test_[module_name].py`
- **Coverage Target**: Minimum 90% code coverage
- **Test Types**: Unit tests, integration tests, E2E tests as appropriate

### Test Categories Required:
- [ ] **Unit Tests**: Individual function testing
- [ ] **Integration Tests**: Component interaction testing
- [ ] **E2E Tests**: Complete workflow testing (for larger features)
- [ ] **Error Tests**: Error condition and exception handling
- [ ] **Performance Tests**: Response time and resource usage

---

## 📊 CODE QUALITY STANDARDS

### Python Best Practices (MANDATORY):
- [ ] **PEP 8 Compliance**: Code follows Python style guide
- [ ] **Function Documentation**: All functions have docstrings
- [ ] **Type Annotations**: All function parameters and returns typed
- [ ] **Error Handling**: Graceful error handling with try/except
- [ ] **Variable Naming**: Clear, descriptive variable names
- [ ] **Function Size**: Functions kept small and focused
- [ ] **Import Organization**: Imports properly organized and minimal

### Code Quality Validation:
```bash
# Required quality checks
pytest --cov=. --cov-report=html  # Test coverage
python3 validate_workflow.py      # Workflow compliance
pylint src/                       # Code quality (if available)
black --check src/               # Code formatting (if available)
```

### Security Requirements:
- [ ] **No Hardcoded Secrets**: Use environment variables for sensitive data
- [ ] **Input Validation**: All user inputs validated and sanitized  
- [ ] **SQL Injection Prevention**: Parameterized queries for database access
- [ ] **XSS Prevention**: Proper output encoding for web interfaces
- [ ] **Error Information**: No sensitive information in error messages

---

## 🔗 INTEGRATION REQUIREMENTS

### Data Integration:
- **Data Sources**: [Data inputs and their locations]
- **Data Validation**: [Required validation of input data]
- **Data Output**: [Expected output format and destination]
- **Data_Sets Compliance**: All data saved in `/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets`

### System Integration:
- **API Compatibility**: [APIs that must remain compatible]
- **Database Integration**: [Database interactions required]
- **File System**: [File system requirements and access patterns]
- **Third-party Services**: [External service integrations]

### Cross-Agent Compatibility:
- **TOWER Validation**: Code ready for TOWER quality validation
- **STRIKE_LEADER Coordination**: Alignment with strategic objectives  
- **BILL Agent Integration**: Compatibility with BILL's parallel systems
- **Colosseum Platform**: Integration with overall platform architecture

---

## 📝 TECHNICAL DELIVERABLES

### Code Deliverables:
- [ ] **Source Code**: Clean, documented, tested implementation
- [ ] **Test Suite**: Comprehensive test coverage (>90%)
- [ ] **Documentation**: Updated README and inline documentation
- [ ] **Configuration**: Any configuration files or environment setup

### Documentation Deliverables:
- [ ] **test_plan.md**: Complete test plan with contracts
- [ ] **README Updates**: Updated setup and usage instructions
- [ ] **API Documentation**: If creating/modifying APIs
- [ ] **Architecture Notes**: Any architectural decisions or changes

### Validation Deliverables:
- [ ] **Test Results**: Complete test output showing all tests pass
- [ ] **Coverage Report**: Code coverage report (>90% target)
- [ ] **Performance Results**: Performance metrics if applicable
- [ ] **Quality Report**: Output from validate_workflow.py

---

## ⚠️ RISK ASSESSMENT & MITIGATION

### Technical Risks:
1. **Risk**: [Specific technical risk]
   - **Impact**: [High/Medium/Low]
   - **Mitigation**: [Specific strategy to address risk]

2. **Risk**: [Integration or compatibility risk]
   - **Impact**: [High/Medium/Low]  
   - **Mitigation**: [Specific strategy to address risk]

### Development Risks:
- **Timeline Risk**: [Risk of delays and mitigation strategies]
- **Quality Risk**: [Risk of quality issues and prevention measures]
- **Integration Risk**: [Risk of integration problems and testing approach]
- **Performance Risk**: [Risk of performance issues and optimization plan]

---

## 🚨 EMERGENCY PROCEDURES

### Development Failures:
- **Build Failures**: [Steps to take if build/tests fail]
- **Integration Issues**: [Process for handling integration problems]
- **Performance Problems**: [Response to performance degradation]
- **Security Issues**: [Immediate response to security concerns]

### Rollback Procedures:
1. **Immediate Stop**: Halt development if critical issues found
2. **Branch Isolation**: Ensure problematic code doesn't reach main
3. **State Recovery**: Revert to last working state if needed
4. **Issue Documentation**: Document problems for future prevention

---

## 📅 IMPLEMENTATION TIMELINE

### Development Phases:
- **Phase 1 - Planning** (Day 1): Branch creation, test plan, initial tests
- **Phase 2 - Implementation** (Day 2-N): Code development with continuous testing
- **Phase 3 - Validation** (Final Day): Quality checks, PR creation, review
- **Phase 4 - Integration** (Post-approval): Merge and deployment

### Key Milestones:
- [ ] **Test Plan Complete**: test_plan.md with all contracts defined
- [ ] **Initial Tests Written**: Tests created and failing appropriately  
- [ ] **MVP Implementation**: Minimal viable implementation passing tests
- [ ] **Quality Validation**: All quality standards met
- [ ] **Peer Review**: Code review completed and approved

---

## ✅ COMPLETION REPORT TEMPLATE

### Technical Results:
- **Branch**: [Final branch name and PR link]
- **Tests**: [Test results - X passed, Y total, Z% coverage]  
- **Quality**: [validate_workflow.py output - PASS/FAIL]
- **Performance**: [Performance metrics achieved]

### Code Quality Metrics:
- **Test Coverage**: ___% (Target: >90%)
- **Code Quality Score**: [Pylint score or equivalent]
- **Documentation**: [Completion status of documentation]
- **Security**: [Security review completion status]

### Integration Status:
- **System Integration**: [Integration test results]
- **Data Validation**: [Data quality validation results]  
- **API Compatibility**: [API compatibility test results]
- **Cross-Agent**: [TOWER validation status]

### Business Impact:
- **Feature Delivered**: [Specific functionality delivered]
- **Performance Improvement**: [Quantified performance gains]
- **Quality Enhancement**: [Quality improvements achieved]
- **User Experience**: [UX improvements delivered]

---

## 🔄 POST-IMPLEMENTATION ACTIONS

### Immediate Actions:
- [ ] **PR Merge**: Merge approved PR to main branch
- [ ] **Branch Cleanup**: Delete feature branch after successful merge
- [ ] **Documentation Update**: Update any affected documentation
- [ ] **Deployment**: Deploy to appropriate environment if needed

### Follow-up Actions:
- [ ] **Performance Monitoring**: Monitor system performance post-deployment
- [ ] **User Feedback**: Collect feedback on new functionality
- [ ] **Bug Monitoring**: Watch for any issues with new code
- [ ] **Optimization**: Identify opportunities for further improvement

---

**Template Version**: 1.0  
**Last Updated**: 2025-08-06  
**Mandatory Usage**: All WINGMAN missions must use this template  
**TDD Enforcement**: Automatic validation via validate_workflow.py

---

**Colosseum Motto**: *"Vincere Habitatio"* - "To Conquer Housing"  
**Wingman Motto**: *"Codigo, Testa, Victoria"* - "Code, Test, Victory"