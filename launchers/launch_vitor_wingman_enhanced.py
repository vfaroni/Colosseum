#!/usr/bin/env python3
"""
⚡ COLOSSEUM - Vitor's Enhanced WINGMAN Agent Context  
Technical implementation with automatic TDD workflow enforcement
"""

import os
from pathlib import Path

def load_agent_rules():
    """Load and return the complete agent rules for automatic enforcement"""
    
    vitor_agents_dir = Path(__file__).parent.parent / "agents" / "VITOR"
    rules_path = vitor_agents_dir / "rules.md"
    
    if rules_path.exists():
        with open(rules_path, 'r') as f:
            return f.read()
    else:
        return "⚠️ WARNING: Agent rules not found at expected location"

def update_vitor_claude_md(user="VITOR", agent="WINGMAN"):
    """Update VITOR's local CLAUDE.md with current agent context"""
    
    vitor_agents_dir = Path(__file__).parent.parent / "agents" / "VITOR"
    claude_md_path = vitor_agents_dir / "CLAUDE.md"
    
    context_update = f"""
---

## 🎯 CURRENT SESSION CONTEXT (Updated {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

**Active Agent**: {user}'s {agent}  
**Session Focus**: Technical implementation with mandatory TDD workflow

### **Current Agent Role**
You are operating as **{user}'s {agent} Agent** with full TDD enforcement active.

### **Session Reminders**
- MANDATORY: Create git branch before any coding (never work on main)
- MANDATORY: Write test_plan.md with contracts before implementation
- MANDATORY: Write failing tests first using pytest
- MANDATORY: Run validate_workflow.py before mission completion
- MANDATORY: Create PR for all code changes (no direct commits)

### **Code Quality Standards Active**
- Type hints required for all functions
- Docstrings mandatory for all functions  
- >90% test coverage required
- Error handling with try/except blocks
- python3 command only (never python)

**Ready for technical implementation with full TDD enforcement** ✅

---
"""
    
    # Append session context to existing CLAUDE.md
    if claude_md_path.exists():
        with open(claude_md_path, 'a') as f:
            f.write(context_update)
    
    return claude_md_path

def display_vitor_wingman_enhanced_context():
    """Display enhanced Vitor's Wingman context with TDD enforcement"""
    
    # Large, clear banner with green color coding for Wingman
    print("\033[92m" + "=" * 80)  # Green color
    print("⚡ VITOR'S ENHANCED WINGMAN AGENT CONTEXT LOADED")
    print("   Technical Implementation with MANDATORY TDD Workflow")
    print("=" * 80 + "\033[0m")  # Reset color
    
    print("\n\033[1m⚡ PRIMARY ROLE:\033[0m")  # Bold text
    print("   Technical implementation specialist with automatic TDD workflow enforcement")
    
    print("\n\033[1m🚨 MANDATORY TDD WORKFLOW (NO EXCEPTIONS):\033[0m")
    tdd_steps = [
        "1. Git Branch: feature/bugfix branch creation (NEVER main)",
        "2. Test Plan: test_plan.md with contracts BEFORE any code",
        "3. Tests First: Write failing tests using pytest framework",
        "4. Implementation: Minimal code to make tests pass",
        "5. Refactor: Improve code while keeping tests passing",
        "6. Validation: validate_workflow.py MUST pass", 
        "7. Pull Request: Review required before merge (no direct commits)"
    ]
    
    for step in tdd_steps:
        print(f"   🔐 {step}")
    
    print("\n\033[1m💻 CODE QUALITY STANDARDS (MANDATORY):\033[0m")
    quality_standards = [
        "Type Hints: All function parameters and returns typed",
        "Docstrings: All functions need '''Description''' docstrings",
        "Error Handling: try/except blocks for anticipated failures",
        "Test Coverage: Minimum 90% code coverage required",
        "Python Command: Always use 'python3' (never 'python')",
        "Function Focus: Single responsibility principle",
        "Variable Names: Meaningful, descriptive naming"
    ]
    
    for standard in quality_standards:
        print(f"   📏 {standard}")
    
    print("\n\033[1m🧪 TESTING REQUIREMENTS (MANDATORY):\033[0m")
    testing_requirements = [
        "Test Framework: Use pytest (preferred) or unittest",
        "Test Types: Unit tests, integration tests, E2E tests",
        "Test Plan: Create test_plan.md with contracts defined",
        "Test Coverage: >90% coverage with html reports",
        "Test Categories: Positive cases, negative cases, edge cases"
    ]
    
    for req in testing_requirements:
        print(f"   🧪 {req}")
    
    print("\n\033[1m🔧 TECHNICAL IMPLEMENTATION FOCUS:\033[0m")
    tech_focus = [
        "7-Step Workflow: Specialization in LIHTC development process",
        "CoStar Processing: Advanced filtering and data validation",
        "Environmental Screening: Risk assessment and compliance",
        "Transit Analysis: California requirements expertise", 
        "BOTN Generation: Economic modeling automation",
        "Data Integration: Central Data_Sets repository usage"
    ]
    
    for focus in tech_focus:
        print(f"   ⚙️ {focus}")
    
    print("\n\033[1m🤖 AGENT COORDINATION:\033[0m")
    coordination = [
        "STRIKE_LEADER: Receive detailed mission briefs with success criteria",
        "TOWER: Submit deliverables for quality validation",
        "Cross-Agent: Coordinate technical implementations",
        "BILL's WINGMAN: Collaborate on cross-user technical projects"
    ]
    
    for coord in coordination:
        print(f"   🔗 {coord}")
    
    print("\n\033[1m📁 DATA & FILE MANAGEMENT:\033[0m")
    file_management = [
        "Data Location: ALL data in central Data_Sets directory",
        "No Local Data: Never save data in project or temp directories",
        "Mission Filing: Use missions/ and reports/ folders only",
        "Archive System: Move completed missions to archive/ subfolder",
        "Metadata: Document all geospatial data with .md or .json files"
    ]
    
    for mgmt in file_management:
        print(f"   📁 {mgmt}")
    
    print("\n\033[1m⚠️ CRITICAL VIOLATIONS (AUTO-BLOCKED):\033[0m")
    violations = [
        "Working on main branch: BLOCKED by validation script",
        "Coding without tests: BLOCKED by mission templates",
        "No test plan: BLOCKED by validate_workflow.py",
        "Direct commits: BLOCKED by PR requirement",
        "Low test coverage: BLOCKED by quality gates",
        "Data outside Data_Sets: BLOCKED by TOWER oversight"
    ]
    
    for violation in violations:
        print(f"   🚫 {violation}")
    
    print("\n\033[1m🔍 VALIDATION COMMANDS (MANDATORY):\033[0m")
    commands = [
        "pytest --cov=. --cov-report=html  # Test with coverage",
        "python3 validate_workflow.py      # Workflow compliance", 
        "git checkout -b feature/task-name # Create branch",
        "git status                        # Check working state"
    ]
    
    for cmd in commands:
        print(f"   💻 {cmd}")
    
    print(f"\n\033[92m✅ ENHANCED WINGMAN CONTEXT ACTIVE - TDD workflow automatically enforced\033[0m")
    print(f"\033[93m⚡ Codigo, Testa, Victoria - 'Code, Test, Victory' ⚡\033[0m")
    
    # Auto-update VITOR's local CLAUDE.md
    claude_path = update_vitor_claude_md("VITOR", "WINGMAN")
    print(f"\n\033[96m📝 VITOR's CLAUDE.md updated with session context: {claude_path}\033[0m")
    print(f"\033[96mAll TDD workflow and code quality standards now AUTO-ENFORCED\033[0m")
    
    # Validate that rules and validation tools are available
    vitor_agents_dir = Path(__file__).parent.parent / "agents" / "VITOR"
    validate_script = vitor_agents_dir / "validate_workflow.py"
    rules_file = vitor_agents_dir / "rules.md"
    wingman_template = vitor_agents_dir / "WINGMAN_MISSION_TEMPLATE.md"
    
    print(f"\n\033[95m🔍 DEVELOPMENT TOOLS STATUS:\033[0m")
    if rules_file.exists():
        print(f"\033[95m✅ Agent rules loaded and ready: {rules_file}\033[0m")
    else:
        print(f"\033[91m❌ WARNING: Rules file not found: {rules_file}\033[0m")
        
    if validate_script.exists():
        print(f"\033[95m✅ Workflow validation script ready: {validate_script}\033[0m")
    else:
        print(f"\033[91m❌ WARNING: Validation script not found: {validate_script}\033[0m")
        
    if wingman_template.exists():
        print(f"\033[95m✅ Mission template available: {wingman_template}\033[0m")
    else:
        print(f"\033[91m❌ WARNING: Mission template not found: {wingman_template}\033[0m")

if __name__ == "__main__":
    display_vitor_wingman_enhanced_context()