#!/usr/bin/env python3
"""
KCEC Weather Data Collection Setup Script
Sets up the environment and dependencies for weather data collection
"""

import os
import sys
import subprocess
import json

def check_python_version():
    """Ensure Python 3.7+ is installed"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")

def install_dependencies():
    """Install required Python packages"""
    packages = [
        "requests",
        "pandas",
        "beautifulsoup4",
        "selenium",
        "schedule",
        "lxml"
    ]
    
    print("\nInstalling required packages...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            return False
    return True

def create_directory_structure():
    """Create necessary directories"""
    directories = [
        "weather_data",
        "weather_data/current",
        "weather_data/archive",
        "weather_data/reports"
    ]
    
    print("\nCreating directory structure...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created {directory}")

def create_config_file():
    """Create configuration file with user input"""
    config = {
        "data_dir": "weather_data",
        "noaa_token": "",
        "email_notifications": False,
        "email_to": "",
        "email_from": "kcec-weather@localhost",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_username": "",
        "smtp_password": ""
    }
    
    print("\nConfiguration Setup")
    print("-" * 50)
    
    # NOAA Token
    print("\nNOAA API Token (required for historical data):")
    print("Get a free token at: https://www.ncdc.noaa.gov/cdo-web/token")
    token = input("Enter your NOAA token (or press Enter to skip): ").strip()
    if token:
        config["noaa_token"] = token
    
    # Email notifications
    email_setup = input("\nSet up email notifications? (y/n): ").lower()
    if email_setup == 'y':
        config["email_notifications"] = True
        config["email_to"] = input("Email address to send reports to: ").strip()
        
        smtp_setup = input("Configure SMTP settings? (y/n): ").lower()
        if smtp_setup == 'y':
            config["smtp_server"] = input(f"SMTP server [{config['smtp_server']}]: ").strip() or config["smtp_server"]
            config["smtp_port"] = int(input(f"SMTP port [{config['smtp_port']}]: ").strip() or config["smtp_port"])
            config["smtp_username"] = input("SMTP username: ").strip()
            config["smtp_password"] = input("SMTP password: ").strip()
    
    # Save config
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    print("\n✓ Configuration saved to config.json")
    
    return config

def create_wrapper_script():
    """Create a simple wrapper script for easy execution"""
    wrapper_content = """#!/usr/bin/env python3
\"\"\"
KCEC Weather Data Collection Wrapper
Simple interface for weather data collection
\"\"\"

import sys
import os
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kcec_weather_downloader import KCECWeatherDownloader
from kcec_realtime_scraper import KCECRealtimeScraper
from kcec_weekly_automation import KCECWeeklyAutomation

def main():
    print("KCEC Weather Data Collection")
    print("-" * 40)
    print("1. Download last 7 days of data")
    print("2. Download specific date range")
    print("3. Get current real-time data")
    print("4. Run weekly automation once")
    print("5. View latest summary")
    print("6. Exit")
    
    choice = input("\\nSelect option (1-6): ").strip()
    
    if choice == "1":
        # Last 7 days
        automation = KCECWeeklyAutomation()
        automation.run_once()
        
    elif choice == "2":
        # Specific date range
        start = input("Start date (YYYY-MM-DD): ").strip()
        end = input("End date (YYYY-MM-DD): ").strip()
        
        downloader = KCECWeatherDownloader()
        # Load token from config
        import json
        with open("config.json", "r") as f:
            config = json.load(f)
        if config.get("noaa_token"):
            downloader.set_noaa_token(config["noaa_token"])
        
        downloader.download_noaa_historical(start, end)
        
    elif choice == "3":
        # Real-time data
        scraper = KCECRealtimeScraper()
        scraper.scrape_with_requests()
        
    elif choice == "4":
        # Run automation
        automation = KCECWeeklyAutomation()
        automation.run_once()
        
    elif choice == "5":
        # View summary
        import glob
        summaries = glob.glob("weather_data/summary_*.txt")
        if summaries:
            latest = max(summaries, key=os.path.getmtime)
            with open(latest, "r") as f:
                print(f.read())
        else:
            print("No summaries found")
            
    elif choice == "6":
        sys.exit(0)
    else:
        print("Invalid option")

if __name__ == "__main__":
    main()
"""
    
    with open("kcec_weather.py", "w") as f:
        f.write(wrapper_content)
    
    # Make executable
    os.chmod("kcec_weather.py", 0o755)
    print("✓ Created wrapper script: kcec_weather.py")

def setup_automation():
    """Set up automation options"""
    print("\nAutomation Setup")
    print("-" * 50)
    print("\nChoose automation method:")
    print("1. Cron (Linux/macOS)")
    print("2. Task Scheduler (Windows)")
    print("3. Manual execution")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        print("\nTo set up cron job for weekly execution:")
        print("1. Run: crontab -e")
        print("2. Add this line (runs every Monday at 9 AM):")
        print(f"0 9 * * 1 {sys.executable} {os.path.abspath('kcec_weekly_automation.py')} --run-once")
        print("\nOr run this command:")
        print(f"(crontab -l 2>/dev/null; echo '0 9 * * 1 {sys.executable} {os.path.abspath('kcec_weekly_automation.py')} --run-once') | crontab -")
        
    elif choice == "2":
        print("\nFor Windows Task Scheduler:")
        print("1. Open Task Scheduler")
        print("2. Create Basic Task")
        print("3. Set trigger: Weekly, Monday, 9:00 AM")
        print(f"4. Set action: Start a program")
        print(f"5. Program: {sys.executable}")
        print(f"6. Arguments: {os.path.abspath('kcec_weekly_automation.py')} --run-once")
        
    else:
        print("\nManual execution:")
        print(f"Run: python3 kcec_weather.py")
        print("Or for automation: python3 kcec_weekly_automation.py --run-once")

def main():
    print("KCEC Weather Data Collection Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    if not install_dependencies():
        print("\nError: Failed to install some dependencies")
        print("Please install them manually using pip")
        sys.exit(1)
    
    # Create directories
    create_directory_structure()
    
    # Create config
    create_config_file()
    
    # Create wrapper script
    create_wrapper_script()
    
    # Set up automation
    setup_automation()
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("\nNext steps:")
    print("1. Get a NOAA API token at https://www.ncdc.noaa.gov/cdo-web/token")
    print("2. Update config.json with your token")
    print("3. Run: python3 kcec_weather.py")
    print("\nFor help with Chrome/Selenium setup for real-time scraping:")
    print("- Install Chrome browser")
    print("- Download chromedriver from https://chromedriver.chromium.org/")

if __name__ == "__main__":
    main()