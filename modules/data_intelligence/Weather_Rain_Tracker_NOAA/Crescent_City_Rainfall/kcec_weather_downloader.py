#!/usr/bin/env python3
"""
KCEC Weather Data Downloader
Downloads precipitation data from NOAA and weather.gov for KCEC station
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import time
from bs4 import BeautifulSoup
import re

class KCECWeatherDownloader:
    def __init__(self, data_dir="weather_data"):
        self.data_dir = data_dir
        self.station_id = "KCEC"
        self.noaa_token = None  # You'll need to get a free token from NOAA
        os.makedirs(data_dir, exist_ok=True)
        
    def set_noaa_token(self, token):
        """Set NOAA API token - get one free at https://www.ncdc.noaa.gov/cdo-web/token"""
        self.noaa_token = token
        
    def download_noaa_historical(self, start_date, end_date):
        """Download historical daily precipitation from NOAA CDO API"""
        if not self.noaa_token:
            print("Error: NOAA token required. Get one at https://www.ncdc.noaa.gov/cdo-web/token")
            return None
            
        # NOAA CDO API endpoint
        base_url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
        
        # Parameters for precipitation data
        params = {
            "datasetid": "GHCND",  # Daily summaries dataset
            "stationid": f"GHCND:USW00093814",  # KCEC station ID
            "datatypeid": "PRCP",  # Precipitation
            "startdate": start_date,
            "enddate": end_date,
            "limit": 1000,
            "units": "standard"
        }
        
        headers = {"token": self.noaa_token}
        
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if "results" in data:
                # Convert to DataFrame
                df = pd.DataFrame(data["results"])
                df["date"] = pd.to_datetime(df["date"])
                df["precipitation_inches"] = df["value"] / 10 / 25.4  # Convert from tenths of mm to inches
                
                # Save to CSV
                filename = f"{self.data_dir}/noaa_historical_{start_date}_{end_date}.csv"
                df[["date", "precipitation_inches"]].to_csv(filename, index=False)
                print(f"Saved historical data to {filename}")
                return df
            else:
                print("No data found for the specified date range")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error downloading NOAA data: {e}")
            return None
            
    def download_realtime_hourly(self):
        """Scrape real-time hourly precipitation from weather.gov"""
        url = "https://www.weather.gov/wrh/timeseries?site=KCEC"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # This is a basic scraper - the actual implementation would need to be 
            # adjusted based on the exact HTML structure of the weather.gov page
            # which can change over time
            
            # Look for precipitation data in the page
            precip_data = []
            
            # Find table or data elements containing precipitation info
            # This is a placeholder - you'll need to inspect the actual page structure
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    # Extract timestamp and precipitation values
                    # This would need to be customized based on actual page structure
                    pass
            
            # Save scraped data
            if precip_data:
                df = pd.DataFrame(precip_data)
                filename = f"{self.data_dir}/realtime_hourly_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False)
                print(f"Saved real-time data to {filename}")
                return df
            else:
                print("No real-time data found")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error downloading real-time data: {e}")
            return None
            
    def download_weekly_update(self):
        """Download the past week's data"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        print(f"Downloading data for {start_date} to {end_date}")
        
        # Download historical daily data
        historical = self.download_noaa_historical(start_date, end_date)
        
        # Download current hourly data
        hourly = self.download_realtime_hourly()
        
        return historical, hourly

def main():
    # Example usage
    downloader = KCECWeatherDownloader()
    
    # You need to set your NOAA token first
    # Get one free at https://www.ncdc.noaa.gov/cdo-web/token
    # downloader.set_noaa_token("YOUR_TOKEN_HERE")
    
    # Download last week's data
    # historical, hourly = downloader.download_weekly_update()
    
    # Or download specific date range
    # df = downloader.download_noaa_historical("2024-01-01", "2024-01-31")
    
    print("KCEC Weather Downloader ready.")
    print("1. Get a free NOAA token at https://www.ncdc.noaa.gov/cdo-web/token")
    print("2. Set the token using: downloader.set_noaa_token('YOUR_TOKEN')")
    print("3. Run downloader.download_weekly_update() to get the past week's data")

if __name__ == "__main__":
    main()