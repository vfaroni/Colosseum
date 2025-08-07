#!/usr/bin/env python3
"""
🏛️ COLOSSEUM Agent Status Display
Shows active work for all agents
"""

import os
from pathlib import Path

def read_file_content(file_path):
    """Safely read file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def get_active_files(agent_dir, folder_name):
    """Get non-archived files from missions or reports folder"""
    folder_path = agent_dir / folder_name
    if not folder_path.exists():
        return []
    
    active_files = []
    for file_path in folder_path.iterdir():
        # Skip directories (like archive folders) and hidden files
        if file_path.is_file() and not file_path.name.startswith('.'):
            # Skip if file is inside an archive directory
            if 'archive' not in str(file_path).lower():
                active_files.append(file_path)
    
    return sorted(active_files, key=lambda x: x.stat().st_mtime, reverse=True)

def display_agent_summary(agent_name, agent_dir):
    """Display summary of agent's active work"""
    
    active_missions = get_active_files(agent_dir, "missions")
    active_reports = get_active_files(agent_dir, "reports")
    
    # Agent header
    print(f"\n🤖 {agent_name}")
    print("─" * 40)
    
    # Missions summary
    if active_missions:
        print(f"📋 {len(active_missions)} Active Mission(s):")
        for mission in active_missions[:3]:  # Show max 3
            print(f"   • {mission.name}")
        if len(active_missions) > 3:
            print(f"   • ... and {len(active_missions) - 3} more")
    else:
        print("📋 No active missions")
    
    # Reports summary  
    if active_reports:
        print(f"📊 {len(active_reports)} Recent Report(s):")
        for report in active_reports[:3]:  # Show max 3
            print(f"   • {report.name}")
        if len(active_reports) > 3:
            print(f"   • ... and {len(active_reports) - 3} more")
    else:
        print("📊 No recent reports")

def main():
    """Display status for all agents"""
    
    # Get current directory (should be Colosseum)
    colosseum_dir = Path.cwd()
    vitor_agents_dir = colosseum_dir / "agents" / "VITOR"
    
    print("\n" + "=" * 60)
    print("🏛️  COLOSSEUM - AGENT STATUS OVERVIEW")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not vitor_agents_dir.exists():
        print("❌ Error: VITOR agents directory not found")
        print(f"   Current directory: {colosseum_dir}")
        return
    
    agents = ["STRIKE_LEADER", "WINGMAN", "TOWER"]
    
    # Display status for each agent
    for agent_name in agents:
        agent_dir = vitor_agents_dir / agent_name
        if agent_dir.exists():
            display_agent_summary(agent_name, agent_dir)
        else:
            print(f"\n🤖 {agent_name}")
            print("─" * 40)
            print("❌ Agent directory not found")
    
    # Show launch commands
    print("\n" + "=" * 60)
    print("🚀 TO LAUNCH AGENTS:")
    print("=" * 60)
    print("🎯 python3 launchers/launch_vitor_strike_leader_enhanced.py")
    print("⚡ python3 launchers/launch_vitor_wingman_enhanced.py") 
    print("🏗️  python3 launchers/launch_vitor_tower_enhanced.py")
    print("\nOr use the interactive selector:")
    print("🎮 python3 agent_selector.py")
    print("=" * 60)

if __name__ == "__main__":
    main()