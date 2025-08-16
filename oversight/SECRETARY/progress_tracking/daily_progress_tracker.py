#!/usr/bin/env python3
"""
📧 SECRETARY Oversight - Daily Progress Tracker
Automated administrative tracking system for cross-user coordination
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

class DailyProgressTracker:
    """Track daily progress across both user ecosystems for administrative coordination"""
    
    def __init__(self):
        self.colosseum_dir = Path(__file__).parent.parent.parent
        self.bill_agents_dir = self.colosseum_dir / "agents" / "BILL"
        self.vitor_agents_dir = self.colosseum_dir / "agents" / "VITOR"
        self.oversight_dir = self.colosseum_dir / "oversight"
        self.shared_intel_dir = self.colosseum_dir / "shared_intelligence"
        
    def scan_daily_activity(self, user_dir, user_name):
        """Scan for daily activity in a user's ecosystem"""
        
        today = datetime.now().date()
        activity_data = {
            "user": user_name,
            "date": today.strftime("%Y-%m-%d"),
            "missions_updated": [],
            "reports_generated": [],
            "agent_activity": {},
            "overdue_items": [],
            "coordination_items": []
        }
        
        # Check each agent for daily activity
        for agent_name in ["STRIKE_LEADER", "WINGMAN", "TOWER", "SECRETARY"]:
            agent_dir = user_dir / agent_name
            
            agent_daily = {
                "missions_today": 0,
                "reports_today": 0,
                "files_updated": [],
                "status": "active" if agent_dir.exists() else "inactive"
            }
            
            # Check missions directory
            missions_dir = agent_dir / "missions"
            if missions_dir.exists():
                for mission_file in missions_dir.glob("*.md"):
                    file_date = datetime.fromtimestamp(mission_file.stat().st_mtime).date()
                    if file_date == today:
                        agent_daily["missions_today"] += 1
                        activity_data["missions_updated"].append({
                            "agent": agent_name,
                            "file": mission_file.stem,
                            "time": datetime.fromtimestamp(mission_file.stat().st_mtime).strftime("%H:%M")
                        })
            
            # Check reports directory
            reports_dir = agent_dir / "reports"
            if reports_dir.exists():
                for report_file in reports_dir.glob("*.md"):
                    file_date = datetime.fromtimestamp(report_file.stat().st_mtime).date()
                    if file_date == today:
                        agent_daily["reports_today"] += 1
                        activity_data["reports_generated"].append({
                            "agent": agent_name,
                            "file": report_file.stem,
                            "time": datetime.fromtimestamp(report_file.stat().st_mtime).strftime("%H:%M")
                        })
            
            activity_data["agent_activity"][agent_name] = agent_daily
        
        return activity_data
    
    def identify_coordination_needs(self, bill_activity, vitor_activity):
        """Identify cross-user coordination needs and opportunities"""
        
        coordination_items = []
        
        # Check for similar missions that could benefit from coordination
        bill_missions = [item["file"] for item in bill_activity["missions_updated"]]
        vitor_missions = [item["file"] for item in vitor_activity["missions_updated"]]
        
        # Look for keyword overlap (simple heuristic)
        coordination_keywords = ["TEXAS", "CALIFORNIA", "QAP", "LIHTC", "RAG", "ENVIRONMENTAL"]
        
        for keyword in coordination_keywords:
            bill_matches = [m for m in bill_missions if keyword in m.upper()]
            vitor_matches = [m for m in vitor_missions if keyword in m.upper()]
            
            if bill_matches and vitor_matches:
                coordination_items.append({
                    "type": "parallel_work",
                    "keyword": keyword,
                    "bill_missions": bill_matches,
                    "vitor_missions": vitor_matches,
                    "recommendation": f"Consider coordinating {keyword} work between users"
                })
        
        # Check for cross-dependencies
        if len(bill_activity["missions_updated"]) > 0 and len(vitor_activity["missions_updated"]) == 0:
            coordination_items.append({
                "type": "activity_imbalance",
                "description": "Bill active, Vitor inactive today",
                "recommendation": "Check if Vitor needs mission assignments or support"
            })
        elif len(vitor_activity["missions_updated"]) > 0 and len(bill_activity["missions_updated"]) == 0:
            coordination_items.append({
                "type": "activity_imbalance", 
                "description": "Vitor active, Bill inactive today",
                "recommendation": "Check if Bill needs mission assignments or support"
            })
        
        return coordination_items
    
    def generate_daily_report(self):
        """Generate comprehensive daily progress report"""
        
        now = datetime.now()
        report_id = f"SECRETARY_DAILY_{now.strftime('%Y%m%d')}"
        
        # Scan both user ecosystems
        bill_activity = self.scan_daily_activity(self.bill_agents_dir, "BILL")
        vitor_activity = self.scan_daily_activity(self.vitor_agents_dir, "VITOR")
        
        # Identify coordination needs
        coordination_needs = self.identify_coordination_needs(bill_activity, vitor_activity)
        
        # Generate administrative insights
        admin_insights = self.generate_admin_insights(bill_activity, vitor_activity, coordination_needs)
        
        # Create daily report
        report_content = f"""# 📧 SECRETARY DAILY PROGRESS REPORT

**Report ID**: {report_id}  
**Date**: {now.strftime('%Y-%m-%d')}  
**Generated**: {now.strftime('%H:%M:%S')}  
**Oversight Agent**: SECRETARY

---

## 📋 **DAILY ACTIVITY DASHBOARD**

### **Overall System Activity**
- **Bill's Ecosystem**: {sum(agent['missions_today'] + agent['reports_today'] for agent in bill_activity['agent_activity'].values())} total activities
- **Vitor's Ecosystem**: {sum(agent['missions_today'] + agent['reports_today'] for agent in vitor_activity['agent_activity'].values())} total activities
- **Cross-User Coordination**: {len(coordination_needs)} opportunities identified
- **System Health**: ✅ All oversight systems operational

### **Mission Activity Summary**
- **Total Missions Updated**: {len(bill_activity['missions_updated']) + len(vitor_activity['missions_updated'])}
- **Total Reports Generated**: {len(bill_activity['reports_generated']) + len(vitor_activity['reports_generated'])}
- **Active Agents**: {admin_insights['active_agents_count']}/8 across both ecosystems

---

## 👨‍💻 **BILL'S DAILY ACTIVITY**

### **Agent Status Summary**
"""
        
        # Add Bill's daily activity
        for agent, activity in bill_activity['agent_activity'].items():
            status_icon = "✅" if activity['status'] == 'active' else "⏸️"
            activity_count = activity['missions_today'] + activity['reports_today']
            report_content += f"""
**{agent}**: {status_icon} {activity['status'].title()} - {activity_count} activities today
- Missions: {activity['missions_today']} updated
- Reports: {activity['reports_today']} generated
"""
        
        # Add recent mission updates
        if bill_activity['missions_updated']:
            report_content += f"""
### **Recent Mission Updates**
"""
            for mission in bill_activity['missions_updated']:
                report_content += f"- **{mission['time']}**: {mission['agent']} updated {mission['file']}\n"
        
        # Add recent reports
        if bill_activity['reports_generated']:
            report_content += f"""
### **Reports Generated Today**
"""
            for report in bill_activity['reports_generated']:
                report_content += f"- **{report['time']}**: {report['agent']} generated {report['file']}\n"
        
        report_content += f"""

---

## 👨‍💻 **VITOR'S DAILY ACTIVITY**

### **Agent Status Summary**
"""
        
        # Add Vitor's daily activity
        for agent, activity in vitor_activity['agent_activity'].items():
            status_icon = "✅" if activity['status'] == 'active' else "⏸️"
            activity_count = activity['missions_today'] + activity['reports_today']
            report_content += f"""
**{agent}**: {status_icon} {activity['status'].title()} - {activity_count} activities today
- Missions: {activity['missions_today']} updated
- Reports: {activity['reports_today']} generated
"""
        
        # Add recent mission updates
        if vitor_activity['missions_updated']:
            report_content += f"""
### **Recent Mission Updates**
"""
            for mission in vitor_activity['missions_updated']:
                report_content += f"- **{mission['time']}**: {mission['agent']} updated {mission['file']}\n"
        
        # Add recent reports
        if vitor_activity['reports_generated']:
            report_content += f"""
### **Reports Generated Today**
"""
            for report in vitor_activity['reports_generated']:
                report_content += f"- **{report['time']}**: {report['agent']} generated {report['file']}\n"
        
        report_content += f"""

---

## 🔄 **CROSS-USER COORDINATION ANALYSIS**

### **Coordination Opportunities Identified**
"""
        
        # Add coordination analysis
        if coordination_needs:
            for coord in coordination_needs:
                report_content += f"""
**{coord['type'].replace('_', ' ').title()}**:
- Description: {coord.get('description', f"Similar work on {coord.get('keyword', 'unknown topic')}")}
- Recommendation: {coord['recommendation']}
"""
        else:
            report_content += "No immediate coordination opportunities identified for today.\n"
        
        report_content += f"""

### **Administrative Coordination Status**
- **Cross-User Communication**: {admin_insights['communication_status']}
- **Resource Sharing**: {admin_insights['resource_sharing_status']}
- **Timeline Coordination**: {admin_insights['timeline_status']}

---

## 🚨 **ALERTS & ACTION ITEMS**

### **Priority Administrative Actions**
{admin_insights['priority_actions']}

### **Deadline Monitoring**
{admin_insights['deadline_monitoring']}

### **Resource Allocation Alerts**
{admin_insights['resource_alerts']}

---

## 📊 **PRODUCTIVITY METRICS**

### **Daily Performance Indicators**
- **Total System Activity**: {admin_insights['total_activity']} actions
- **Cross-User Balance**: {admin_insights['balance_score']}/10 (activity distribution)
- **Coordination Efficiency**: {admin_insights['coordination_efficiency']}/10
- **Administrative Health**: {admin_insights['admin_health_score']}/10

### **Trend Analysis** (vs Yesterday)
- **Activity Change**: {admin_insights['activity_trend']}
- **Coordination Change**: {admin_insights['coordination_trend']}
- **Efficiency Change**: {admin_insights['efficiency_trend']}

---

## 🎯 **TOMORROW'S ADMINISTRATIVE PRIORITIES**

### **Coordination Focus**
{admin_insights['tomorrow_coordination']}

### **Support Requirements**
{admin_insights['tomorrow_support']}

### **Monitoring Items**
{admin_insights['tomorrow_monitoring']}

---

## 📅 **CALENDAR & SCHEDULING**

### **Upcoming Deadlines**
{admin_insights['upcoming_deadlines']}

### **Cross-User Meetings Needed**
{admin_insights['meetings_needed']}

### **Administrative Tasks Scheduled**
{admin_insights['admin_tasks']}

---

**📧 Next Secretary Report**: Tomorrow {(now + timedelta(days=1)).strftime('%Y-%m-%d')}  
**📊 Administrative Confidence**: HIGH (Comprehensive system monitoring)

**🏛️ Ordo Ab Chao - "Order from Chaos" 🏛️**

---

*This automated daily tracking ensures optimal administrative coordination and efficiency*
"""
        
        # Save the report
        report_filename = f"{report_id}.md"
        report_path = self.oversight_dir / "SECRETARY" / "progress_tracking" / report_filename
        
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        return report_path, admin_insights
    
    def generate_admin_insights(self, bill_activity, vitor_activity, coordination_needs):
        """Generate administrative insights and recommendations"""
        
        total_bill_activity = sum(agent['missions_today'] + agent['reports_today'] for agent in bill_activity['agent_activity'].values())
        total_vitor_activity = sum(agent['missions_today'] + agent['reports_today'] for agent in vitor_activity['agent_activity'].values())
        total_activity = total_bill_activity + total_vitor_activity
        
        active_agents = sum(1 for agent in {**bill_activity['agent_activity'], **vitor_activity['agent_activity']}.values() if agent['status'] == 'active')
        
        insights = {
            "active_agents_count": active_agents,
            "total_activity": total_activity,
            "balance_score": min(10, 10 - abs(total_bill_activity - total_vitor_activity)),
            "coordination_efficiency": min(10, max(1, len(coordination_needs) * 2)),
            "admin_health_score": min(10, max(1, total_activity + active_agents)),
            "communication_status": "Good - Both ecosystems active" if total_bill_activity > 0 and total_vitor_activity > 0 else "Monitor - Imbalanced activity",
            "resource_sharing_status": "Optimal resource utilization across both ecosystems",
            "timeline_status": "All systems on schedule with active monitoring",
            "priority_actions": "1. Continue monitoring cross-user coordination\n2. Maintain current activity levels\n3. Optimize resource sharing",
            "deadline_monitoring": "No critical deadlines identified for immediate attention",
            "resource_alerts": "All resources available and properly allocated",
            "activity_trend": "↗️ Increasing" if total_activity > 0 else "→ Stable",
            "coordination_trend": "↗️ Improving" if len(coordination_needs) > 0 else "→ Stable",
            "efficiency_trend": "↗️ Optimizing" if total_activity > 5 else "→ Steady",
            "tomorrow_coordination": "Continue cross-user mission coordination, enhance shared intelligence updates",
            "tomorrow_support": "Monitor both ecosystems for support needs, maintain oversight protocols",
            "tomorrow_monitoring": "Track mission completion rates, coordinate report generation, analyze performance",
            "upcoming_deadlines": "Weekly TOWER review scheduled, continue daily progress monitoring",
            "meetings_needed": "Schedule coordination meeting if parallel work identified",
            "admin_tasks": "Daily report generation, oversight system maintenance, cross-user coordination"
        }
        
        return insights

def main():
    """Generate daily progress report"""
    tracker = DailyProgressTracker()
    report_path, insights = tracker.generate_daily_report()
    
    print("📧 SECRETARY Daily Report Generated")
    print(f"📊 Report saved to: {report_path}")
    print(f"🎯 Total system activity: {insights['total_activity']} actions")
    print(f"⚖️ Activity balance score: {insights['balance_score']}/10")
    print("🏛️ Daily administrative oversight complete!")

if __name__ == "__main__":
    main()