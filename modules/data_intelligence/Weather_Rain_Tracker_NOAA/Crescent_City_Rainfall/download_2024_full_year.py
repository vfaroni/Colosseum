#!/usr/bin/env python3
"""
Download KCEC weather data for full year 2024
To fill in missing data from Jan 1 - Apr 30, 2024
"""

import json
import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kcec_weather_downloader import KCECWeatherDownloader

def main():
    print("Downloading KCEC weather data for Jan 1 - Apr 30, 2024")
    print("-" * 50)
    
    # Initialize downloader
    downloader = KCECWeatherDownloader()
    
    # Load NOAA token from config
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        with open(config_path, "r") as f:
            config = json.load(f)
        
        if config.get("noaa_token"):
            downloader.set_noaa_token(config["noaa_token"])
            print(f"NOAA token loaded from config")
        else:
            print("ERROR: No NOAA token found in config.json")
            print("Please add your NOAA API token to config.json")
            print("Get a free token at: https://www.ncdc.noaa.gov/cdo-web/token")
            sys.exit(1)
    except FileNotFoundError:
        print("ERROR: config.json not found")
        print("Please run setup_kcec_weather.py first")
        sys.exit(1)
    
    # Download data for Jan 1 - Apr 30, 2024
    start_date = "2024-01-01"
    end_date = "2024-04-30"
    
    print(f"Downloading data from {start_date} to {end_date}")
    filepath = downloader.download_noaa_historical(start_date, end_date)
    
    if filepath:
        print(f"\nData successfully downloaded to: {filepath}")
        
        # Also create a combined file with all 2024 data
        print("\nCombining with existing May-Dec 2024 data...")
        
        # Read the new data
        import csv
        new_data = []
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            new_data = list(reader)
        
        # Read existing data
        existing_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kcec_corrected_historical_2024-05-01_to_2025-06-11.csv")
        if os.path.exists(existing_file):
            existing_data = []
            with open(existing_file, 'r') as f:
                reader = csv.DictReader(f)
                # Only get 2024 data
                for row in reader:
                    if row['Date'].startswith('2024'):
                        existing_data.append(row)
            
            # Combine and sort by date
            all_data = new_data + existing_data
            all_data.sort(key=lambda x: x['Date'])
            
            # Write combined file
            output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"kcec_full_year_2024_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            with open(output_file, 'w', newline='') as f:
                if all_data:
                    writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
                    writer.writeheader()
                    writer.writerows(all_data)
            
            print(f"Combined 2024 data saved to: {output_file}")
            print(f"Total days in 2024: {len(all_data)}")
            
            # Count rainy days
            rainy_days = sum(1 for row in all_data if float(row.get('Total_Inches', 0)) > 0)
            print(f"Rainy days in 2024: {rainy_days}")
        
    else:
        print("ERROR: Failed to download data")

if __name__ == "__main__":
    main()