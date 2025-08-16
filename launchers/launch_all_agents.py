#!/usr/bin/env python3
"""
🏛️ COLOSSEUM LIHTC Platform - Complete Agent Ecosystem Launcher
"Where Housing Battles Are Won"

Launches all agents in coordinated fashion for complete LIHTC development workflow.
"""

import subprocess
import sys
import time
from pathlib import Path

def print_banner():
    """Display Colosseum launch banner"""
    print("""
🏛️ ═══════════════════════════════════════════════════════════════════
   COLOSSEUM LIHTC PLATFORM - COMPLETE ECOSYSTEM LAUNCH
   "Where Housing Battles Are Won"
   
   🤖 Activating all agents for maximum competitive advantage
   ⚔️ Strike Leader + Wingman + Tower + Secretary coordination
   📊 Complete LIHTC analysis and development pipeline
═══════════════════════════════════════════════════════════════════ 🏛️
""")

def launch_agent(agent_name, script_path):
    """Launch individual agent with status reporting"""
    print(f"🚀 Launching {agent_name}...")
    try:
        # Start agent in background
        process = subprocess.Popen([sys.executable, script_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        time.sleep(2)  # Allow startup time
        
        if process.poll() is None:  # Still running
            print(f"✅ {agent_name} operational (PID: {process.pid})")
            return process
        else:
            print(f"❌ {agent_name} failed to start")
            return None
    except Exception as e:
        print(f"❌ Error launching {agent_name}: {e}")
        return None

def main():
    """Launch complete Colosseum agent ecosystem"""
    print_banner()
    
    # Define launch sequence
    agents = [
        ("STRIKE LEADER", "launch_strike_leader.py"),
        ("WINGMAN", "launch_wingman.py"),
        ("TOWER", "launch_tower.py"),
        ("SECRETARY", "launch_secretary.py")
    ]
    
    launched_processes = []
    launcher_dir = Path(__file__).parent
    
    print("🏛️ AGENT ACTIVATION SEQUENCE:")
    print("=" * 50)
    
    for agent_name, script_name in agents:
        script_path = launcher_dir / script_name
        if script_path.exists():
            process = launch_agent(agent_name, str(script_path))
            if process:
                launched_processes.append((agent_name, process))
        else:
            print(f"⚠️  {agent_name} launcher not found: {script_path}")
    
    print("\n🏛️ COLOSSEUM STATUS SUMMARY:")
    print("=" * 50)
    
    if launched_processes:
        print(f"✅ {len(launched_processes)} agents operational")
        for agent_name, process in launched_processes:
            print(f"   🤖 {agent_name}: PID {process.pid}")
        
        print("\n🎯 COLOSSEUM READY FOR LIHTC DOMINATION!")
        print("   📊 Complete analysis pipeline active")
        print("   🗺️ Amenity mapping systems online")
        print("   📈 Economic viability analyzers ready")
        print("   🔍 Environmental screening operational")
        
        print("\n⚔️ May victory be yours in the housing battles!")
        
    else:
        print("❌ No agents successfully launched")
        print("   Check individual launcher scripts for issues")
    
    return len(launched_processes)

if __name__ == "__main__":
    launched_count = main()
    sys.exit(0 if launched_count > 0 else 1)