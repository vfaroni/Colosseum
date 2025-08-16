#!/usr/bin/env python3
"""
KCEC Real-time Weather Scraper
Scrapes hourly precipitation data from weather.gov
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
from datetime import datetime
import json
import os

class KCECRealtimeScraper:
    def __init__(self, data_dir="weather_data"):
        self.data_dir = data_dir
        self.station = "KCEC"
        os.makedirs(data_dir, exist_ok=True)
        
    def scrape_with_requests(self):
        """Try to get data using direct API calls (if available)"""
        # Weather.gov often has JSON endpoints for their data
        # Try multiple possible endpoints
        
        endpoints = [
            f"https://api.weather.gov/stations/{self.station}/observations/latest",
            f"https://api.weather.gov/stations/{self.station}/observations?limit=168",  # Last 7 days hourly
        ]
        
        all_data = []
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, headers={"User-Agent": "KCEC Weather Scraper"})
                response.raise_for_status()
                
                data = response.json()
                
                if "features" in data:
                    # Multiple observations
                    for feature in data["features"]:
                        obs = self._parse_observation(feature["properties"])
                        if obs:
                            all_data.append(obs)
                elif "properties" in data:
                    # Single observation
                    obs = self._parse_observation(data["properties"])
                    if obs:
                        all_data.append(obs)
                        
            except Exception as e:
                print(f"Error with endpoint {endpoint}: {e}")
                continue
                
        if all_data:
            df = pd.DataFrame(all_data)
            filename = f"{self.data_dir}/realtime_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            print(f"Saved {len(all_data)} observations to {filename}")
            return df
        else:
            print("No data retrieved via API")
            return None
            
    def _parse_observation(self, properties):
        """Parse observation data from weather.gov API"""
        try:
            timestamp = properties.get("timestamp", "")
            
            # Look for precipitation data in various possible fields
            precip_value = None
            
            # Check different possible precipitation fields
            if "precipitationLastHour" in properties and properties["precipitationLastHour"]:
                precip_value = properties["precipitationLastHour"]["value"]
                unit = properties["precipitationLastHour"]["unitCode"]
            elif "precipitationLast3Hours" in properties and properties["precipitationLast3Hours"]:
                precip_value = properties["precipitationLast3Hours"]["value"]
                unit = properties["precipitationLast3Hours"]["unitCode"]
            elif "precipitationLast6Hours" in properties and properties["precipitationLast6Hours"]:
                precip_value = properties["precipitationLast6Hours"]["value"]
                unit = properties["precipitationLast6Hours"]["unitCode"]
                
            if precip_value is not None:
                # Convert to inches if needed
                if unit == "unit:mm":
                    precip_inches = precip_value / 25.4
                else:
                    precip_inches = precip_value
                    
                return {
                    "timestamp": timestamp,
                    "precipitation_inches": precip_inches,
                    "temperature_f": properties.get("temperature", {}).get("value", None),
                    "humidity": properties.get("relativeHumidity", {}).get("value", None),
                    "wind_speed_mph": properties.get("windSpeed", {}).get("value", None)
                }
        except Exception as e:
            print(f"Error parsing observation: {e}")
            
        return None
        
    def scrape_with_selenium(self):
        """Fallback method using Selenium for JavaScript-rendered content"""
        # This requires Chrome/Chromium and chromedriver to be installed
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            driver = webdriver.Chrome(options=chrome_options)
            
            url = f"https://www.weather.gov/wrh/timeseries?site={self.station}"
            driver.get(url)
            
            # Wait for page to load
            wait = WebDriverWait(driver, 10)
            
            # Look for precipitation data elements
            # This would need to be customized based on actual page structure
            precip_elements = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "precip-value"))
            )
            
            data = []
            for element in precip_elements:
                # Extract timestamp and value
                # This is a placeholder - adjust based on actual HTML
                pass
                
            driver.quit()
            
            if data:
                df = pd.DataFrame(data)
                filename = f"{self.data_dir}/realtime_selenium_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False)
                return df
                
        except Exception as e:
            print(f"Selenium scraping failed: {e}")
            print("Make sure Chrome and chromedriver are installed")
            
        return None

def main():
    scraper = KCECRealtimeScraper()
    
    # Try API method first (preferred)
    df = scraper.scrape_with_requests()
    
    if df is None:
        print("Trying Selenium method...")
        df = scraper.scrape_with_selenium()
        
    if df is not None:
        print(f"Successfully retrieved {len(df)} observations")
    else:
        print("Failed to retrieve data")

if __name__ == "__main__":
    main()