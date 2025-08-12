#!/usr/bin/env python3
"""
🏛️ TOWER MISSION COMPLIANCE CHECKER
Mission: VITOR-TOWER-ENFORCEMENT-002

Automated enforcement of mission documentation requirements.
Ensures all agents follow proper mission → report workflow.
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import re

class TowerMissionCompliance:
    """TOWER automated mission documentation enforcement"""
    
    def __init__(self):
        self.repo_root = self._find_repo_root()
        self.agents_dir = self.repo_root / 'agents'
        self.violations = []
        self.warnings = []
        
    def _find_repo_root(self):
        """Find git repository root"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.git').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def scan_agent_directories(self):
        """Scan all agent directories for compliance"""
        if not self.agents_dir.exists():
            self.violations.append("❌ CRITICAL: No agents directory found")
            return {}
        
        agents = {}
        for user_dir in self.agents_dir.iterdir():
            if user_dir.is_dir() and not user_dir.name.startswith('.'):
                agents[user_dir.name] = self._scan_user_agents(user_dir)
        
        return agents
    
    def _scan_user_agents(self, user_dir):
        """Scan individual user's agent directories"""
        user_agents = {}
        
        for agent_dir in user_dir.iterdir():
            if agent_dir.is_dir() and not agent_dir.name.startswith('.'):
                agent_info = self._analyze_agent_directory(agent_dir)
                user_agents[agent_dir.name] = agent_info
        
        return user_agents
    
    def _analyze_agent_directory(self, agent_dir):
        """Analyze individual agent directory for compliance"""
        missions_dir = agent_dir / 'missions'
        reports_dir = agent_dir / 'reports'
        
        agent_info = {
            'path': agent_dir,
            'has_missions_dir': missions_dir.exists(),
            'has_reports_dir': reports_dir.exists(),
            'missions': [],
            'reports': [],
            'violations': [],
            'compliance_score': 0
        }
        
        # Check directory structure
        if not missions_dir.exists():
            agent_info['violations'].append("Missing missions/ directory")
        else:
            agent_info['missions'] = self._scan_missions(missions_dir)
        
        if not reports_dir.exists():
            agent_info['violations'].append("Missing reports/ directory")
        else:
            agent_info['reports'] = self._scan_reports(reports_dir)
        
        # Check mission-report compliance
        self._check_mission_report_compliance(agent_info)
        
        # Calculate compliance score
        agent_info['compliance_score'] = self._calculate_compliance_score(agent_info)
        
        return agent_info
    
    def _scan_missions(self, missions_dir):
        """Scan missions directory"""
        missions = []
        
        for mission_file in missions_dir.glob('*.md'):
            if mission_file.name == 'MISSION_BRIEF_TEMPLATE.md':
                continue
                
            mission_info = {
                'name': mission_file.stem,
                'file': mission_file,
                'created': datetime.fromtimestamp(mission_file.stat().st_mtime),
                'has_completion_report': False
            }
            missions.append(mission_info)
        
        return missions
    
    def _scan_reports(self, reports_dir):
        """Scan reports directory"""
        reports = []
        
        for report_file in reports_dir.glob('*.md'):
            if 'TEMPLATE' in report_file.name.upper():
                continue
                
            report_info = {
                'name': report_file.stem,
                'file': report_file,
                'created': datetime.fromtimestamp(report_file.stat().st_mtime),
                'is_completion_report': 'COMPLETE' in report_file.name.upper()
            }
            reports.append(report_info)
        
        return reports
    
    def _check_mission_report_compliance(self, agent_info):
        """Check if missions have corresponding completion reports"""
        missions = agent_info['missions']
        reports = agent_info['reports']
        
        completion_reports = [r for r in reports if r['is_completion_report']]
        
        for mission in missions:
            # Look for corresponding completion report
            mission_name_base = mission['name'].replace('_MISSION', '').replace('MISSION_', '')
            
            corresponding_reports = []
            for report in completion_reports:
                report_name_base = report['name'].replace('_COMPLETE', '').replace('COMPLETE_', '')
                report_name_base = re.sub(r'_\d{8}.*', '', report_name_base)  # Remove timestamps
                
                if mission_name_base.upper() in report_name_base.upper() or \
                   report_name_base.upper() in mission_name_base.upper():
                    corresponding_reports.append(report)
            
            if corresponding_reports:
                mission['has_completion_report'] = True
            else:
                # Check if mission is recent (within 7 days) - grace period
                days_old = (datetime.now() - mission['created']).days
                if days_old > 7:
                    agent_info['violations'].append(f"Mission '{mission['name']}' lacks completion report (created {days_old} days ago)")
                else:
                    self.warnings.append(f"Recent mission '{mission['name']}' in {agent_info['path'].name} needs completion report soon")
    
    def _calculate_compliance_score(self, agent_info):
        """Calculate compliance score (0-100)"""
        score = 100
        
        # Deduct for missing directories
        if not agent_info['has_missions_dir']:
            score -= 25
        if not agent_info['has_reports_dir']:
            score -= 25
        
        # Deduct for mission compliance violations
        missions_count = len(agent_info['missions'])
        if missions_count > 0:
            missions_with_reports = sum(1 for m in agent_info['missions'] if m['has_completion_report'])
            mission_compliance_rate = missions_with_reports / missions_count
            score *= mission_compliance_rate
        
        # Deduct for structural violations
        score -= len(agent_info['violations']) * 10
        
        return max(0, int(score))
    
    def generate_compliance_report(self, agents_data):
        """Generate comprehensive compliance report"""
        print("\n🏛️ TOWER MISSION COMPLIANCE REPORT")
        print("=" * 70)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        total_agents = 0
        compliant_agents = 0
        total_violations = 0
        
        for user, user_agents in agents_data.items():
            print(f"👤 USER: {user.upper()}")
            print("-" * 40)
            
            for agent_name, agent_info in user_agents.items():
                total_agents += 1
                score = agent_info['compliance_score']
                status = "✅ COMPLIANT" if score >= 90 else "⚠️  ISSUES" if score >= 70 else "❌ NON-COMPLIANT"
                
                if score >= 90:
                    compliant_agents += 1
                
                print(f"  🤖 {agent_name}: {status} ({score}%)")
                
                # Show missions and reports count
                mission_count = len(agent_info['missions'])
                report_count = len([r for r in agent_info['reports'] if r['is_completion_report']])
                print(f"     📋 Missions: {mission_count}, Reports: {report_count}")
                
                # Show violations
                if agent_info['violations']:
                    total_violations += len(agent_info['violations'])
                    for violation in agent_info['violations']:
                        print(f"     ❌ {violation}")
                
                print()
        
        # Summary statistics
        compliance_rate = (compliant_agents / total_agents * 100) if total_agents > 0 else 0
        
        print("📊 COMPLIANCE SUMMARY")
        print("-" * 40)
        print(f"Total Agents: {total_agents}")
        print(f"Compliant Agents: {compliant_agents}")
        print(f"Compliance Rate: {compliance_rate:.1f}%")
        print(f"Total Violations: {total_violations}")
        
        # Overall status
        if compliance_rate >= 90:
            print("\n🏆 EXCELLENT: Roman Engineering standards maintained")
        elif compliance_rate >= 70:
            print("\n⚠️  WARNING: Some agents need attention")
        else:
            print("\n🚨 CRITICAL: Systematic enforcement required")
        
        # Show warnings
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   {warning}")
        
        return {
            'total_agents': total_agents,
            'compliant_agents': compliant_agents,
            'compliance_rate': compliance_rate,
            'total_violations': total_violations,
            'status': 'EXCELLENT' if compliance_rate >= 90 else 'WARNING' if compliance_rate >= 70 else 'CRITICAL'
        }
    
    def enforce_compliance(self):
        """Main compliance enforcement function"""
        print("🏛️ TOWER MISSION COMPLIANCE ENFORCEMENT")
        print("Scanning agent directories for protocol compliance...")
        
        agents_data = self.scan_agent_directories()
        
        if not agents_data:
            print("❌ No agent directories found - ensure proper agent structure exists")
            return False
        
        summary = self.generate_compliance_report(agents_data)
        
        # Save detailed report
        report_file = self.repo_root / 'tower_compliance_report.json'
        detailed_report = {
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'agents': agents_data,
            'violations': self.violations,
            'warnings': self.warnings
        }
        
        # Convert Path objects to strings for JSON serialization
        self._serialize_paths(detailed_report)
        
        with open(report_file, 'w') as f:
            json.dump(detailed_report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved: {report_file}")
        
        # Return success based on compliance rate
        return summary['compliance_rate'] >= 70
    
    def _serialize_paths(self, obj):
        """Convert Path objects to strings for JSON serialization"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, Path):
                    obj[key] = str(value)
                elif isinstance(value, (dict, list)):
                    self._serialize_paths(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, Path):
                    obj[i] = str(item)
                elif isinstance(item, (dict, list)):
                    self._serialize_paths(item)

def main():
    """Execute TOWER mission compliance check"""
    checker = TowerMissionCompliance()
    
    print("🏛️ TOWER MISSION COMPLIANCE CHECKER")
    print("Enforcing systematic mission documentation requirements...")
    print()
    
    success = checker.enforce_compliance()
    
    if success:
        print("\n✅ Mission documentation compliance acceptable")
        print("🏛️ Roman Engineering standards maintained")
    else:
        print("\n❌ Mission documentation compliance issues detected")
        print("🚨 Systematic enforcement required")
        print("\nRequired actions:")
        print("  1. Create missing missions/ and reports/ directories")
        print("  2. File completion reports for all completed missions")
        print("  3. Follow established mission → report workflow")
        print("  4. Use proper templates and naming conventions")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())