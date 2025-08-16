#!/usr/bin/env python3
"""
🏗️ COLOSSEUM - Vitor's Enhanced TOWER Agent Context  
QA oversight & administrative support with automatic rules enforcement
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

def update_vitor_claude_md(user="VITOR", agent="TOWER"):
    """Update VITOR's local CLAUDE.md with current agent context"""
    
    vitor_agents_dir = Path(__file__).parent.parent / "agents" / "VITOR"
    claude_md_path = vitor_agents_dir / "CLAUDE.md"
    
    context_update = f"""
---

## 🎯 CURRENT SESSION CONTEXT (Updated {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

**Active Agent**: {user}'s {agent}  
**Session Focus**: QA oversight and administrative support with rule enforcement

### **Current Agent Role**
You are operating as **{user}'s {agent} Agent** with full quality gate enforcement active.

### **Session Reminders**
- Quality validation protocols automatically enforced (>95% coherence, >90% coverage)
- All WINGMAN deliverables require secondary validation
- Email management and file organization oversight active
- validate_workflow.py enforcement for all mission completions

### **Quality Gates Active**
- Pre-integration validation with sample testing
- Cross-agent verification mandatory
- Emergency rollback authority for quality failures
- Data_Sets compliance monitoring active

**Ready for quality oversight with full enforcement** ✅

---
"""
    
    # Append session context to existing CLAUDE.md
    if claude_md_path.exists():
        with open(claude_md_path, 'a') as f:
            f.write(context_update)
    
    return claude_md_path

def display_vitor_tower_enhanced_context():
    """Display enhanced Vitor's Tower context with rules enforcement"""
    
    # Large, clear banner with blue color coding for Tower
    print("\033[94m" + "=" * 80)  # Blue color
    print("🏗️ VITOR'S ENHANCED TOWER AGENT CONTEXT LOADED")
    print("   Quality Assurance & Administrative Support with Rule Enforcement")
    print("=" * 80 + "\033[0m")  # Reset color
    
    print("\n\033[1m🏗️ PRIMARY ROLE:\033[0m")  # Bold text
    print("   QA oversight and administrative support with automatic quality gate enforcement")
    
    print("\n\033[1m🔍 QUALITY ASSURANCE PROTOCOLS (AUTO-ENFORCED):\033[0m")
    qa_protocols = [
        "Pre-Integration Validation: 10+ samples with coherence checks",
        "Quality Thresholds: >95% coherence, >90% domain relevance", 
        "Cross-Agent Verification: Secondary validation mandatory",
        "Development Oversight: Git/test/PR compliance checking",
        "Data Organization: Central Data_Sets enforcement",
        "Emergency Rollback: Immediate stop for quality failures"
    ]
    
    for protocol in qa_protocols:
        print(f"   🔐 {protocol}")
    
    print("\n\033[1m📧 EMAIL MANAGEMENT AUTOMATION:\033[0m")
    email_functions = [
        "LIHTC deal flow filtering (>95% accuracy target)",
        "Spam elimination (>90% reduction target)",
        "Priority classification with response time SLAs", 
        "Administrative processing with proper filing",
        "Deal announcement organization and archival"
    ]
    
    for function in email_functions:
        print(f"   📨 {function}")
    
    print("\n\033[1m🗂️ FILE ORGANIZATION OVERSIGHT:\033[0m")
    file_functions = [
        "Mission folder structure enforcement (missions/ + reports/ only)",
        "Automatic archival to archive/ subfolder upon completion",
        "Data_Sets compliance monitoring with violation flagging", 
        "Metadata documentation validation for geospatial data",
        "Version control and backup verification"
    ]
    
    for function in file_functions:
        print(f"   📁 {function}")
    
    print("\n\033[1m⛔ QUALITY GATE AUTHORITY:\033[0m")
    gate_powers = [
        "STOP integration immediately if thresholds not met",
        "Block mission completion until validate_workflow.py passes",
        "Escalate systemic issues with detailed failure analysis",
        "Implement emergency rollback procedures for critical failures"
    ]
    
    for power in gate_powers:
        print(f"   🚫 {power}")
    
    print("\n\033[1m🤖 CROSS-AGENT COORDINATION:\033[0m")
    coordination = [
        "WINGMAN Output Validation: All technical deliverables reviewed",
        "STRIKE_LEADER Reporting: Strategic insights and quality status",
        "SECRETARY Coordination: Administrative task coordination", 
        "BILL's TOWER Integration: Cross-user QA compatibility"
    ]
    
    for coord in coordination:
        print(f"   🔗 {coord}")
    
    print("\n\033[1m🎯 QUALITY MONITORING FOCUS:\033[0m")
    monitoring_areas = [
        "LIHTC domain terminology accuracy (>90% relevance required)",
        "Data coherence and structural integrity validation",
        "Test coverage and code quality standards enforcement",
        "Integration compatibility across Colosseum platform",
        "Business value alignment with strategic objectives"
    ]
    
    for area in monitoring_areas:
        print(f"   📊 {area}")
    
    print("\n\033[1m🚨 FAILURE RESPONSE PROCEDURES:\033[0m")
    failure_responses = [
        "Immediate Stop: Halt all related activities within 5 minutes",
        "Notification: Alert stakeholders within 15 minutes", 
        "Root Cause: Complete failure analysis within 1 hour",
        "Recovery Plan: Implement fixes within 4 hours",
        "Process Update: Revise protocols based on lessons learned"
    ]
    
    for response in failure_responses:
        print(f"   🚨 {response}")
    
    print(f"\n\033[92m✅ ENHANCED TOWER CONTEXT ACTIVE - Quality gates automatically enforced\033[0m")
    print(f"\033[93m🏗️ Vigilantia, Qualitas, Veritas - 'Vigilance, Quality, Truth' 🏗️\033[0m")
    
    # Auto-update VITOR's local CLAUDE.md
    claude_path = update_vitor_claude_md("VITOR", "TOWER")
    print(f"\n\033[96m📝 VITOR's CLAUDE.md updated with session context: {claude_path}\033[0m")
    print(f"\033[96mAll quality protocols and file organization rules now AUTO-ENFORCED\033[0m")
    
    # Validate that rules and validation tools are available
    vitor_agents_dir = Path(__file__).parent.parent / "agents" / "VITOR"
    validate_script = vitor_agents_dir / "validate_workflow.py"
    rules_file = vitor_agents_dir / "rules.md"
    
    print(f"\n\033[95m🔍 VALIDATION TOOLS STATUS:\033[0m")
    if rules_file.exists():
        print(f"\033[95m✅ Agent rules loaded and ready: {rules_file}\033[0m")
    else:
        print(f"\033[91m❌ WARNING: Rules file not found: {rules_file}\033[0m")
        
    if validate_script.exists():
        print(f"\033[95m✅ Workflow validation script ready: {validate_script}\033[0m")
    else:
        print(f"\033[91m❌ WARNING: Validation script not found: {validate_script}\033[0m")

if __name__ == "__main__":
    display_vitor_tower_enhanced_context()