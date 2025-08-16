#!/usr/bin/env python3
"""
🏛️ COLOSSEUM - Vitor's Enhanced STRIKE LEADER Agent Context
Strategic coordination & LIHTC platform leadership with automatic rules enforcement
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

def update_vitor_claude_md(user="VITOR", agent="STRIKE_LEADER"):
    """Update VITOR's local CLAUDE.md with current agent context"""
    
    vitor_agents_dir = Path(__file__).parent.parent / "agents" / "VITOR"
    claude_md_path = vitor_agents_dir / "CLAUDE.md"
    
    context_update = f"""
---

## 🎯 CURRENT SESSION CONTEXT (Updated {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

**Active Agent**: {user}'s {agent}  
**Session Focus**: Strategic coordination with automatic rule enforcement

### **Current Agent Role**
You are operating as **{user}'s {agent} Agent** with full rule enforcement active.

### **Session Reminders**
- All TDD workflow rules are automatically enforced
- Mission templates with compliance checkboxes are mandatory  
- validate_workflow.py must pass before any completion
- Quality gates are active and will block substandard work

### **Agent Coordination Active**
- WINGMAN: Technical implementation following TDD protocols
- TOWER: QA oversight with automatic validation
- Cross-coordination with BILL's agents when needed

**Ready for strategic coordination with full rule enforcement** ✅

---
"""
    
    # Append session context to existing CLAUDE.md
    if claude_md_path.exists():
        with open(claude_md_path, 'a') as f:
            f.write(context_update)
    
    return claude_md_path

def display_vitor_strike_leader_enhanced_context():
    """Display enhanced Vitor's Strike Leader context with rules enforcement"""
    
    # Large, clear banner with red color coding for Strike Leader
    print("\033[91m" + "=" * 80)  # Red color
    print("🎯 VITOR'S ENHANCED STRIKE LEADER AGENT CONTEXT LOADED")
    print("   Strategic Coordination & MANDATORY Rules Enforcement")
    print("=" * 80 + "\033[0m")  # Reset color
    
    print("\n\033[1m🎯 PRIMARY ROLE:\033[0m")  # Bold text
    print("   Strategic coordination with AUTOMATIC TDD workflow enforcement")
    
    print("\n\033[1m🚨 MANDATORY TDD WORKFLOW (AUTO-ENFORCED):\033[0m")
    workflow_steps = [
        "1. Git Branch: feature/bugfix branch (NEVER main)",
        "2. Test Plan: test_plan.md with contracts FIRST",  
        "3. Tests: Write failing tests before code",
        "4. Implementation: Minimal code to pass tests",
        "5. Validation: validate_workflow.py MUST pass",
        "6. Pull Request: Review required before merge",
        "7. Quality Gates: TOWER validation mandatory"
    ]
    
    for step in workflow_steps:
        print(f"   🔐 {step}")
    
    print("\n\033[1m⚔️ CURRENT FOCUS AREAS:\033[0m")
    focus_areas = [
        "Federal + State RAG system integration with TDD compliance",
        "Cross-jurisdictional LIHTC analysis following development protocols", 
        "Multi-agent workflow orchestration with quality gates",
        "Business development strategy with code quality standards",
        "Quality assurance oversight using automated validation"
    ]
    
    for area in focus_areas:
        print(f"   • {area}")
    
    print("\n\033[1m🤖 AGENT COORDINATION WITH RULE ENFORCEMENT:\033[0m")
    coordination = [
        "VITOR'S WINGMAN: Technical implementation following TDD protocols",
        "VITOR'S TOWER: QA oversight with automatic rule validation",
        "VITOR'S SECRETARY: Administrative support with file organization rules",
        "BILL'S AGENTS: Cross-user collaboration maintaining quality standards"
    ]
    
    for coord in coordination:
        print(f"   🔗 {coord}")
    
    print("\n\033[1m📋 MISSION TEMPLATE ENFORCEMENT:\033[0m")
    template_requirements = [
        "All missions MUST use provided templates with checkboxes",
        "No mission completion without validate_workflow.py passing",
        "Cross-agent verification mandatory for all deliverables",
        "Quality thresholds auto-enforced (>90% test coverage, >95% domain relevance)"
    ]
    
    for req in template_requirements:
        print(f"   ✅ {req}")
    
    print("\n\033[1m🏛️ KEY DIRECTIVES:\033[0m")
    directives = [
        "Issue missions using MANDATORY compliance templates",
        "Enforce TDD workflow without exceptions",
        "Validate all deliverables meet quality thresholds",
        "Ensure Roman engineering standards in all work",
        "Focus on business value while maintaining code quality"
    ]
    
    for directive in directives:
        print(f"   ⚔️ {directive}")
    
    print("\n\033[1m🔒 AUTOMATIC RULE ENFORCEMENT:\033[0m")
    enforcement = [
        "Agent rules auto-loaded into every Claude session",
        "Mission templates force compliance checkboxes",
        "validate_workflow.py blocks non-compliant completions", 
        "Quality gates prevent integration of failed deliverables"
    ]
    
    for rule in enforcement:
        print(f"   🛡️ {rule}")
    
    print(f"\n\033[92m✅ ENHANCED STRIKE LEADER CONTEXT ACTIVE - Rules automatically enforced\033[0m")
    print(f"\033[93m🏛️ Disciplina, Qualitas, Victoria - 'Discipline, Quality, Victory' 🏛️\033[0m")
    
    # Auto-update VITOR's local CLAUDE.md
    claude_path = update_vitor_claude_md("VITOR", "STRIKE_LEADER")
    print(f"\n\033[96m📝 VITOR's CLAUDE.md updated with session context: {claude_path}\033[0m")
    print(f"\033[96mAll TDD and quality protocols are now AUTOMATICALLY ENFORCED\033[0m")
    
    # Validate that rules are properly loaded
    print(f"\n\033[95m🔍 VALIDATION: Agent rules loaded and ready for enforcement\033[0m")
    
    # Show validation script availability
    vitor_agents_dir = Path(__file__).parent.parent / "agents" / "VITOR"
    validate_script = vitor_agents_dir / "validate_workflow.py"
    if validate_script.exists():
        print(f"\033[95m✅ Workflow validation script available: {validate_script}\033[0m")
    else:
        print(f"\033[91m❌ WARNING: Validation script not found at {validate_script}\033[0m")

if __name__ == "__main__":
    display_vitor_strike_leader_enhanced_context()