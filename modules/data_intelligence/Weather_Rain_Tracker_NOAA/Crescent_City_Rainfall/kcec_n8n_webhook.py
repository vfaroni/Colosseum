#!/usr/bin/env python3
"""
KCEC Weather Data Collection for n8n
Designed to work as a webhook endpoint or scheduled task in n8n
"""

import json
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Configuration
NOAA_TOKEN = os.environ.get('NOAA_TOKEN', 'oaLvXPjjAWoSCizEBvNoHPNhATmdDmQA')
STATION_ID = "GHCND:USW00093814"  # KCEC station ID for NOAA
WEATHER_GOV_STATION = "KCEC"

def get_noaa_historical_data(start_date=None, end_date=None):
    """Get historical precipitation data from NOAA"""
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    base_url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
    
    params = {
        "datasetid": "GHCND",
        "stationid": STATION_ID,
        "datatypeid": "PRCP",
        "startdate": start_date,
        "enddate": end_date,
        "limit": 1000,
        "units": "standard"
    }
    
    headers = {"token": NOAA_TOKEN}
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if "results" in data:
            results = []
            for item in data["results"]:
                results.append({
                    "date": item["date"],
                    "precipitation_inches": round(item["value"] / 10 / 25.4, 4),  # Convert from tenths of mm to inches
                    "station": "KCEC",
                    "data_source": "NOAA"
                })
            return {"success": True, "data": results}
        else:
            return {"success": True, "data": [], "message": "No data available for this date range"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_realtime_data():
    """Get real-time data from weather.gov"""
    try:
        # Get latest observation
        url = f"https://api.weather.gov/stations/{WEATHER_GOV_STATION}/observations/latest"
        response = requests.get(url, headers={"User-Agent": "KCEC Weather Bot"})
        response.raise_for_status()
        
        data = response.json()
        properties = data.get("properties", {})
        
        result = {
            "timestamp": properties.get("timestamp"),
            "temperature_f": None,
            "humidity": None,
            "precipitation_last_hour_inches": None,
            "station": "KCEC",
            "data_source": "weather.gov"
        }
        
        # Temperature
        if properties.get("temperature", {}).get("value") is not None:
            result["temperature_f"] = round(properties["temperature"]["value"] * 9/5 + 32, 1)
        
        # Humidity
        if properties.get("relativeHumidity", {}).get("value") is not None:
            result["humidity"] = properties["relativeHumidity"]["value"]
        
        # Precipitation
        if properties.get("precipitationLastHour", {}).get("value") is not None:
            # Convert mm to inches
            result["precipitation_last_hour_inches"] = round(properties["precipitationLastHour"]["value"] / 25.4, 4)
        
        return {"success": True, "data": result}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/webhook/weather/daily', methods=['POST', 'GET'])
def daily_weather_webhook():
    """Webhook endpoint for n8n to get yesterday's weather data"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Get historical data for yesterday
    historical = get_noaa_historical_data(yesterday, yesterday)
    
    # Get current conditions
    realtime = get_realtime_data()
    
    response = {
        "timestamp": datetime.now().isoformat(),
        "historical_data": historical,
        "current_conditions": realtime
    }
    
    return jsonify(response)

@app.route('/webhook/weather/range', methods=['POST'])
def range_weather_webhook():
    """Webhook endpoint for n8n to get weather data for a date range"""
    data = request.get_json()
    
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({"success": False, "error": "start_date and end_date required"}), 400
    
    historical = get_noaa_historical_data(start_date, end_date)
    
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "date_range": {
            "start": start_date,
            "end": end_date
        },
        "data": historical
    })

@app.route('/webhook/weather/current', methods=['GET'])
def current_weather_webhook():
    """Get current weather conditions"""
    realtime = get_realtime_data()
    
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "current_conditions": realtime
    })

# Standalone functions for n8n Code node
def get_kcec_weather_for_n8n(date_range_days=7):
    """
    Standalone function that can be used in n8n Code node
    Returns weather data in a format ready for n8n processing
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=date_range_days)
    
    # Get historical data
    historical = get_noaa_historical_data(
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )
    
    # Get current conditions
    current = get_realtime_data()
    
    # Format for n8n
    output = {
        "execution_time": datetime.now().isoformat(),
        "station": "KCEC - Crescent City, Jack McNamara Field Airport",
        "summary": {
            "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "total_days": date_range_days
        }
    }
    
    if historical["success"] and historical.get("data"):
        total_precip = sum(d["precipitation_inches"] for d in historical["data"])
        days_with_rain = sum(1 for d in historical["data"] if d["precipitation_inches"] > 0)
        
        output["summary"]["total_precipitation_inches"] = round(total_precip, 4)
        output["summary"]["days_with_precipitation"] = days_with_rain
        output["summary"]["average_daily_precipitation"] = round(total_precip / date_range_days, 4)
    
    output["historical_data"] = historical
    output["current_conditions"] = current
    
    return output

if __name__ == "__main__":
    # For testing locally
    print("KCEC Weather API for n8n")
    print("-" * 40)
    print("Available endpoints:")
    print("GET  /webhook/weather/daily - Get yesterday's data")
    print("POST /webhook/weather/range - Get data for date range")
    print("GET  /webhook/weather/current - Get current conditions")
    print("")
    print("Starting Flask server on port 5000...")
    app.run(debug=True, port=5000)