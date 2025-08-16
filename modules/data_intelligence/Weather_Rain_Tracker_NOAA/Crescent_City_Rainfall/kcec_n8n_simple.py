#!/usr/bin/env python3
"""
KCEC Weather Data Collection - Simple version for n8n
Can be called directly from n8n Execute Command node or via HTTP Request
"""

import json
import requests
from datetime import datetime, timedelta
import sys

# Configuration
NOAA_TOKEN = 'oaLvXPjjAWoSCizEBvNoHPNhATmdDmQA'
STATION_ID = "GHCND:USW00093814"  # KCEC station ID for NOAA
WEATHER_GOV_STATION = "KCEC"

def get_weather_data(days_back=1):
    """Get weather data for the specified number of days back"""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    # Prepare response
    response = {
        "execution_time": datetime.now().isoformat(),
        "station": "KCEC - Crescent City, Jack McNamara Field Airport",
        "date_range": {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d")
        },
        "precipitation_data": [],
        "current_conditions": {},
        "summary": {}
    }
    
    # Get NOAA historical data
    try:
        base_url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
        
        params = {
            "datasetid": "GHCND",
            "stationid": STATION_ID,
            "datatypeid": "PRCP",
            "startdate": start_date.strftime("%Y-%m-%d"),
            "enddate": end_date.strftime("%Y-%m-%d"),
            "limit": 1000,
            "units": "standard"
        }
        
        headers = {"token": NOAA_TOKEN}
        
        noaa_response = requests.get(base_url, params=params, headers=headers, timeout=30)
        noaa_response.raise_for_status()
        
        data = noaa_response.json()
        
        if "results" in data:
            for item in data["results"]:
                response["precipitation_data"].append({
                    "date": item["date"],
                    "precipitation_inches": round(item["value"] / 10 / 25.4, 4)
                })
        
    except Exception as e:
        response["errors"] = {"noaa_error": str(e)}
    
    # Get current conditions from weather.gov
    try:
        url = f"https://api.weather.gov/stations/{WEATHER_GOV_STATION}/observations/latest"
        weather_response = requests.get(url, headers={"User-Agent": "KCEC Weather Bot"}, timeout=30)
        weather_response.raise_for_status()
        
        weather_data = weather_response.json()
        properties = weather_data.get("properties", {})
        
        current = {
            "timestamp": properties.get("timestamp"),
            "temperature_f": None,
            "humidity_percent": None,
            "wind_speed_mph": None,
            "precipitation_last_hour_inches": None
        }
        
        # Parse values
        if properties.get("temperature", {}).get("value") is not None:
            current["temperature_f"] = round(properties["temperature"]["value"] * 9/5 + 32, 1)
        
        if properties.get("relativeHumidity", {}).get("value") is not None:
            current["humidity_percent"] = properties["relativeHumidity"]["value"]
            
        if properties.get("windSpeed", {}).get("value") is not None:
            current["wind_speed_mph"] = round(properties["windSpeed"]["value"] * 0.621371, 1)
        
        if properties.get("precipitationLastHour", {}).get("value") is not None:
            current["precipitation_last_hour_inches"] = round(properties["precipitationLastHour"]["value"] / 25.4, 4)
        
        response["current_conditions"] = current
        
    except Exception as e:
        if "errors" not in response:
            response["errors"] = {}
        response["errors"]["weather_gov_error"] = str(e)
    
    # Calculate summary
    if response["precipitation_data"]:
        total_precip = sum(d["precipitation_inches"] for d in response["precipitation_data"])
        days_with_rain = sum(1 for d in response["precipitation_data"] if d["precipitation_inches"] > 0)
        
        response["summary"] = {
            "total_precipitation_inches": round(total_precip, 4),
            "days_with_precipitation": days_with_rain,
            "days_checked": len(response["precipitation_data"]),
            "average_daily_precipitation": round(total_precip / max(len(response["precipitation_data"]), 1), 4)
        }
    
    return response

def main():
    """Main function for command-line usage"""
    # Check if days argument was provided
    days = 1
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print(json.dumps({"error": "Invalid days argument. Must be a number."}))
            sys.exit(1)
    
    # Get weather data
    result = get_weather_data(days)
    
    # Output as JSON for n8n to consume
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()