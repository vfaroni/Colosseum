#!/usr/bin/env python3
"""
D'Marco's Dashboard Launcher
Quick start script with helpful instructions
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'streamlit': 'streamlit',
        'pandas': 'pandas',
        'plotly': 'plotly',
        'openpyxl': 'openpyxl'
    }
    
    missing = []
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing.append(pip_name)
    
    if missing:
        print("❌ Missing required packages:")
        print(f"   Please run: pip3 install {' '.join(missing)}")
        return False
    
    print("✅ All dependencies installed")
    return True

def print_welcome():
    """Print welcome message and instructions"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         🏗️  D'Marco's Deal Dashboard - Texas LIHTC         ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Welcome D'Marco! This dashboard helps you:
    ✅ Track hot leads and prioritize outreach
    ✅ Add notes with #tags for easy searching
    ✅ View properties on an interactive map
    ✅ Learn LIHTC basics as you work
    
    📱 Mobile-friendly - use on your phone in the field!
    """)

def print_quick_guide():
    """Print quick usage guide"""
    print("""
    🚀 QUICK START GUIDE:
    
    1️⃣ HOT LEADS TAB - Your daily priority list
       • Red = Contact TODAY! 
       • Orange = Follow up within 3 days
       • Blue = Check weekly
    
    2️⃣ ADDING NOTES - Track every interaction
       • Click "📝 Add Note" on any property
       • Use quick tags like #motivated-seller
       • Notes save automatically
    
    3️⃣ CONTACTING BROKERS
       • Click "📞 Contact" to see broker info
       • Best practice: Text first, then call
       • Log every interaction in notes
    
    4️⃣ MAP VIEW - Visual property exploration
       • Red pins = Hot leads
       • Click pins for details
       • Plan efficient site visits
    
    5️⃣ LEARNING CENTER - Build your knowledge
       • What's QCT? What's DDA? It's all there!
       • Conversation starters for brokers
       • TDHCA rules simplified
    """)

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    dashboard_path = Path(__file__).parent / "dmarco_dashboard.py"
    
    print("\n🚀 Launching dashboard...")
    print("📍 Access at: http://localhost:8501")
    print("💡 Tip: Bookmark this URL on your phone!")
    print("\n⏹️  Press Ctrl+C to stop the dashboard\n")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(dashboard_path)])
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped. Great work today!")
        print_daily_tip()

def print_daily_tip():
    """Print a helpful tip"""
    import random
    tips = [
        "💡 TIP: Always ask brokers about seller motivation - it's key!",
        "💡 TIP: Properties in QCT/DDA areas get 30% more tax credits",
        "💡 TIP: The One Mile Rule is a fatal flaw - always check!",
        "💡 TIP: Text brokers after 3pm for best response rates",
        "💡 TIP: Use #motivated-seller tag to quickly find hot opportunities"
    ]
    print(f"\n{random.choice(tips)}\n")

def main():
    """Main launcher function"""
    print_welcome()
    
    if not check_dependencies():
        sys.exit(1)
    
    print_quick_guide()
    
    response = input("\n Ready to start? (y/n): ")
    if response.lower() == 'y':
        launch_dashboard()
    else:
        print("\n No problem! Run this script when you're ready.")
        print_daily_tip()

if __name__ == "__main__":
    main()