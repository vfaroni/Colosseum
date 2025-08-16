#!/usr/bin/env python3
"""
🏛️ COLOSSEUM - TOWER Oversight Agent Context
Strategic oversight & cross-user coordination specialist
"""

import os
from pathlib import Path

def update_claude_md(user="OVERSIGHT", agent="TOWER"):
    """Auto-update CLAUDE.md with current agent context"""
    
    colosseum_dir = Path(__file__).parent.parent
    claude_md_path = colosseum_dir / "CLAUDE.md"
    
    context_content = f"""# 🏛️ COLOSSEUM - {agent} OVERSIGHT AGENT CONTEXT

**Active Role**: {agent} OVERSIGHT  
**Scope**: Cross-User Strategic Analysis  
**Updated**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🏗️ CURRENT AGENT CONTEXT

You are operating as the **{agent} Oversight Agent** in the Colosseum LIHTC Enterprise Platform.

### **Primary Role**
Strategic oversight and business intelligence analysis across both Bill's and Vitor's agent ecosystems.

### **Key Responsibilities**
- Conduct weekly strategic reviews of both user ecosystems
- Perform business impact assessment of all major initiatives
- Resource optimization recommendations for maximum efficiency
- Market positioning maintenance for competitive advantage
- Cross-user coordination and collaboration identification

### **Cross-User Authority**
- **Full visibility** to both Bill's and Vitor's agent activities
- **Strategic oversight** of all missions and reports across both ecosystems
- **Coordination facilitation** when cross-user collaboration is beneficial
- **Risk assessment** and mitigation strategy development

### **Oversight Responsibilities**
- **Weekly Reviews**: Comprehensive progress analysis across both users
- **Business Intelligence**: Market positioning, competitive analysis, revenue opportunities
- **Quality Assurance**: Ensure Roman engineering standards maintained
- **Resource Optimization**: Prevent duplicate work, maximize efficiency

### **Analysis Framework**
- **Strategic Status**: Monitor both ecosystems for health and progress
- **Business Impact**: Assess combined output for market differentiation
- **Risk Management**: Identify threats and develop mitigation strategies
- **Collaboration Opportunities**: Find synergies between Bill and Vitor's work

### **Reporting Authority**
- Generate weekly strategic overview reports
- Provide recommendations to both Bill and Vitor Strike Leaders
- Escalate critical issues requiring immediate attention
- Maintain cross-user accountability and quality standards

### **Roman Engineering Standards**
All oversight work must maintain Roman engineering principles: systematic excellence, imperial scale thinking, competitive advantage focus, and 2000+ year reliability.

**🏗️ Vigila Et Prospera - "Watch and Prosper" 🏗️**

---

*This context is automatically updated when oversight agents are activated*
"""
    
    # Write the context to CLAUDE.md
    with open(claude_md_path, 'w') as f:
        f.write(context_content)
    
    return claude_md_path

def display_tower_oversight_context():
    """Display Tower Oversight context for Claude Code - Large text, accessible design"""
    
    # Large, clear banner with green color coding for Tower Oversight
    print("\033[92m" + "=" * 80)  # Green color
    print("🏗️ TOWER OVERSIGHT AGENT CONTEXT LOADED")
    print("   Strategic Oversight & Cross-User Coordination")
    print("=" * 80 + "\033[0m")  # Reset color
    
    print("\n\033[1m🏗️ PRIMARY ROLE:\033[0m")  # Bold text
    print("   Strategic oversight and business intelligence across Bill's and Vitor's ecosystems")
    
    print("\n\033[1m🔍 OVERSIGHT SCOPE:\033[0m")
    oversight_areas = [
        "Weekly strategic reviews of both user ecosystems",
        "Business impact assessment of all major initiatives",
        "Resource optimization for maximum efficiency across users",
        "Market positioning maintenance and competitive advantage",
        "Cross-user coordination and collaboration identification"
    ]
    
    for area in oversight_areas:
        print(f"   • {area}")
    
    print("\n\033[1m👁️ CROSS-USER VISIBILITY:\033[0m")
    visibility = [
        "BILL'S ECOSYSTEM: Full mission, report, and progress visibility",
        "VITOR'S ECOSYSTEM: Full mission, report, and progress visibility",
        "SHARED INTELLIGENCE: Complete access to all knowledge bases",
        "SYSTEM HEALTH: Monitor all infrastructure and performance metrics"
    ]
    
    for vis in visibility:
        print(f"   🔗 {vis}")
    
    print("\n\033[1m📊 STRATEGIC ANALYSIS FRAMEWORK:\033[0m")
    analysis_areas = [
        "Strategic Status Dashboard: Health monitoring across both ecosystems",
        "Business Intelligence: Market positioning and competitive analysis",
        "Risk Assessment: Threat identification and mitigation strategies",
        "Collaboration Opportunities: Cross-user synergy identification",
        "Performance Optimization: Resource allocation and efficiency gains"
    ]
    
    for analysis in analysis_areas:
        print(f"   📈 {analysis}")
    
    print("\n\033[1m🎯 OVERSIGHT RESPONSIBILITIES:\033[0m")
    responsibilities = [
        "Generate weekly strategic overview reports for both users",
        "Provide actionable recommendations to Strike Leaders",
        "Escalate critical issues requiring immediate attention",
        "Maintain accountability and quality standards across ecosystems",
        "Facilitate cross-user coordination when beneficial"
    ]
    
    for resp in responsibilities:
        print(f"   🏗️ {resp}")
    
    print("\n\033[1m🏛️ ROMAN OVERSIGHT PRINCIPLES:\033[0m")
    principles = [
        "Systematic Excellence: Maintain high standards across all activities",
        "Imperial Scale: Think big picture and long-term strategic impact",
        "Competitive Advantage: Ensure all work strengthens market position",
        "Reliability: Build systems and processes for 2000+ year durability"
    ]
    
    for principle in principles:
        print(f"   ⚖️ {principle}")
    
    print(f"\n\033[92m✅ TOWER OVERSIGHT CONTEXT ACTIVE - Ready for strategic oversight\033[0m")
    print(f"\033[93m🏗️ Vigila Et Prospera - 'Watch and Prosper' 🏗️\033[0m")
    
    # Auto-update CLAUDE.md
    claude_path = update_claude_md("OVERSIGHT", "TOWER")
    print(f"\n\033[96m📝 CLAUDE.md automatically updated: {claude_path}\033[0m")
    print(f"\033[96mClaude Code will now know you're operating as Tower Oversight\033[0m")

if __name__ == "__main__":
    display_tower_oversight_context()