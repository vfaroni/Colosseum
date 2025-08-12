#!/usr/bin/env python3
"""
🏛️ COLOSSEUM Agent Selector
Interactive agent selection with active mission/report review
"""

import os
import sys
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
            if 'archive' not in file_path.parts:
                active_files.append(file_path)
    
    return sorted(active_files, key=lambda x: x.stat().st_mtime, reverse=True)

def display_file_summary(file_path):
    """Display a summary of the file content"""
    content = read_file_content(file_path)
    
    print(f"\n📄 {file_path.name}")
    print("─" * 50)
    
    # Show first few lines for context
    lines = content.split('\n')
    for i, line in enumerate(lines[:10]):  # Show first 10 lines
        if line.strip():  # Skip empty lines
            print(f"   {line[:80]}")  # Truncate long lines
            if i >= 5:  # Show max 6 meaningful lines
                break
    
    if len(lines) > 10:
        print("   ...")
    
    print()

def launch_agent(agent_name):
    """Launch the appropriate enhanced agent launcher"""
    launcher_path = Path(__file__).parent / "launchers" / f"launch_vitor_{agent_name.lower()}_enhanced.py"
    
    if launcher_path.exists():
        print(f"\n🚀 Launching {agent_name} agent...")
        os.system(f"python3 '{launcher_path}'")
    else:
        print(f"⚠️  Launcher not found: {launcher_path}")

def main():
    """Main agent selection interface"""
    
    # Get current directory (should be Colosseum)
    colosseum_dir = Path.cwd()
    vitor_agents_dir = colosseum_dir / "agents" / "VITOR"
    
    print("\n" + "=" * 60)
    print("🏛️  COLOSSEUM AGENT SELECTOR")
    print("   Choose your agent to review active work")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not vitor_agents_dir.exists():
        print("❌ Error: Not in Colosseum directory or VITOR agents not found")
        print(f"   Current directory: {colosseum_dir}")
        print(f"   Expected VITOR agents at: {vitor_agents_dir}")
        sys.exit(1)
    
    agents = {
        "1": ("STRIKE_LEADER", "Strategic coordination & mission assignment"),
        "2": ("WINGMAN", "Technical implementation & coding"),
        "3": ("TOWER", "Quality assurance & administrative support")
    }
    
    # Display agent options
    print("\nSelect your agent:")
    for key, (name, description) in agents.items():
        print(f"   {key}. {name} - {description}")
    
    print("\n   0. Exit")
    
    # Get user selection
    try:
        choice = input("\nEnter your choice (0-3): ").strip()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    
    if choice == "0":
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    if choice not in agents:
        print("❌ Invalid choice. Please select 1, 2, 3, or 0.")
        return main()  # Restart selection
    
    agent_name, agent_description = agents[choice]
    agent_dir = vitor_agents_dir / agent_name
    
    print(f"\n🎯 Selected: {agent_name}")
    print(f"   {agent_description}")
    
    # Check if agent directory exists
    if not agent_dir.exists():
        print(f"❌ Agent directory not found: {agent_dir}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print(f"📋 ACTIVE WORK REVIEW - {agent_name}")
    print("=" * 60)
    
    # Review active missions
    active_missions = get_active_files(agent_dir, "missions")
    if active_missions:
        print(f"\n🎯 ACTIVE MISSIONS ({len(active_missions)}):")
        for mission_file in active_missions:
            display_file_summary(mission_file)
    else:
        print("\n✅ No active missions found")
    
    # Review active reports
    active_reports = get_active_files(agent_dir, "reports")
    if active_reports:
        print(f"\n📊 RECENT REPORTS ({len(active_reports)}):")
        for report_file in active_reports:
            display_file_summary(report_file)
    else:
        print("\n📝 No recent reports found")
    
    # Summary
    total_active = len(active_missions) + len(active_reports)
    if total_active == 0:
        print(f"\n✨ {agent_name} has no active work - ready for new missions!")
    else:
        print(f"\n📈 {agent_name} has {len(active_missions)} active missions and {len(active_reports)} recent reports")
    
    # Ask if user wants to launch the agent
    print(f"\n🚀 Ready to launch {agent_name} agent?")
    launch_choice = input("   Press Enter to launch, or 'q' to quit: ").strip().lower()
    
    if launch_choice != 'q':
        launch_agent(agent_name)
    else:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()