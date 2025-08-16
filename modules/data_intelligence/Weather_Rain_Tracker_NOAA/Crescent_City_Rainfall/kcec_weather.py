#!/usr/bin/env python3
"""
KCEC Weather Data Collection Wrapper
Simple interface for weather data collection
"""

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
    
    choice = input("\nSelect option (1-6): ").strip()
    
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