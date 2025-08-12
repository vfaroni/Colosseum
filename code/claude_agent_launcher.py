#!/usr/bin/env python3
"""
🏛️ COLOSSEUM Agent Launcher for Claude Code
Shows status and provides easy launch commands
"""

import os
from pathlib import Path

def get_active_files(agent_dir, folder_name):
    """Get non-archived files from missions or reports folder"""
    folder_path = agent_dir / folder_name
    if not folder_path.exists():
        return []
    
    active_files = []
    for file_path in folder_path.iterdir():
        if file_path.is_file() and not file_path.name.startswith('.'):
            if 'archive' not in str(file_path).lower():
                active_files.append(file_path)
    
    return sorted(active_files, key=lambda x: x.stat().st_mtime, reverse=True)

def display_agent_summary(agent_name, agent_dir):
    """Display summary of agent's active work"""
    
    active_missions = get_active_files(agent_dir, "missions")
    active_reports = get_active_files(agent_dir, "reports")
    
    print(f"\n🤖 {agent_name}")
    print("─" * 40)
    
    if active_missions:
        print(f"📋 {len(active_missions)} Active Mission(s):")
        for mission in active_missions[:2]:
            print(f"   • {mission.name}")
        if len(active_missions) > 2:
            print(f"   • ... and {len(active_missions) - 2} more")
    else:
        print("📋 No active missions")
    
    if active_reports:
        print(f"📊 {len(active_reports)} Recent Report(s):")
        for report in active_reports[:2]:
            print(f"   • {report.name}")
        if len(active_reports) > 2:
            print(f"   • ... and {len(active_reports) - 2} more")
    else:
        print("📊 No recent reports")

def main():
    """Display status and launch options"""
    
    colosseum_dir = Path.cwd()
    vitor_agents_dir = colosseum_dir / "agents" / "VITOR"
    
    print("\n" + "=" * 60)
    print("🏛️  COLOSSEUM - AGENT STATUS & LAUNCHER")
    print("=" * 60)
    
    if not vitor_agents_dir.exists():
        print("❌ Error: VITOR agents directory not found")
        return
    
    agents = ["STRIKE_LEADER", "WINGMAN", "TOWER"]
    
    # Display status for each agent
    for agent_name in agents:
        agent_dir = vitor_agents_dir / agent_name
        if agent_dir.exists():
            display_agent_summary(agent_name, agent_dir)
    
    print("\n" + "=" * 60)
    print("🚀 QUICK LAUNCH COMMANDS:")
    print("=" * 60)
    print("To work as STRIKE_LEADER (Strategic coordination):")
    print("   python3 launchers/launch_vitor_strike_leader_enhanced.py")
    print("\nTo work as WINGMAN (Technical implementation):")
    print("   python3 launchers/launch_vitor_wingman_enhanced.py") 
    print("\nTo work as TOWER (QA oversight & admin):")
    print("   python3 launchers/launch_vitor_tower_enhanced.py")
    
    print("\n" + "─" * 60)
    print("💡 TIP: Copy and paste any launch command above to start working!")
    print("🎮 Or run: python3 agent_selector.py for interactive selection")
    print("=" * 60)

if __name__ == "__main__":
    main()