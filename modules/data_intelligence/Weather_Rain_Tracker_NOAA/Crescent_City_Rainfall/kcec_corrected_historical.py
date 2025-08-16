#!/usr/bin/env python3
"""
KCEC Historical Data - CORRECTED VERSION
Uses the correct station ID and proper unit conversions
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import time

# CORRECTED Configuration
NOAA_TOKEN = 'oaLvXPjjAWoSCizEBvNoHPNhATmdDmQA'
CORRECT_STATION_ID = "GHCND:USW00024286"  # CRESCENT CITY MCNAMARA AIRPORT
START_DATE = "2024-05-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")

def test_data_format():
    """Test what the actual data format looks like"""
    print("Testing data format with correct KCEC station...")
    print("=" * 60)
    
    # Test with a known rainy period
    url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
    params = {
        "datasetid": "GHCND",
        "stationid": CORRECT_STATION_ID,
        "datatypeid": "PRCP,TMAX,TMIN",
        "startdate": "2024-01-01",
        "enddate": "2024-01-10",
        "limit": 50,
        "units": "standard"
    }
    
    headers = {"token": NOAA_TOKEN}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if "results" in data:
            print(f"Found {len(data['results'])} records")
            
            # Group by type
            by_type = {}
            for item in data["results"]:
                dtype = item["datatype"]
                if dtype not in by_type:
                    by_type[dtype] = []
                by_type[dtype].append(item)
            
            for dtype, items in by_type.items():
                print(f"\n{dtype} samples:")
                for item in items[:3]:
                    value = item["value"]
                    date = item["date"]
                    print(f"  {date}: {value}")
                    
                    if dtype == "PRCP":
                        print(f"    If in inches: {value}\"")
                        print(f"    If in tenths of mm: {value/10/25.4:.4f}\"")
                        print(f"    If in mm: {value/25.4:.4f}\"")
                    elif dtype in ["TMAX", "TMIN"]:
                        print(f"    If in F: {value}°F")
                        print(f"    If in C: {value * 9/5 + 32:.1f}°F")
                        
        else:
            print("No data found")
            
    except Exception as e:
        print(f"Error: {e}")

def categorize_precipitation(inches):
    """Categorize precipitation amount"""
    if inches >= 1.0:
        return "Very Heavy", True, True, True, True
    elif inches >= 0.5:
        return "Heavy", True, True, True, False
    elif inches >= 0.25:
        return "Moderate", True, True, False, False
    elif inches >= 0.01:
        return "Light", True, False, False, False
    elif inches > 0:
        return "Trace", False, False, False, False
    else:
        return "None", False, False, False, False

def get_corrected_historical_data():
    """Get historical data with corrected conversions"""
    print(f"\nFetching CORRECTED KCEC data from {START_DATE} to {END_DATE}")
    print("Using station: CRESCENT CITY MCNAMARA AIRPORT")
    print("=" * 60)
    
    base_url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
    headers = {"token": NOAA_TOKEN}
    
    # Get data in monthly chunks
    start = datetime.strptime(START_DATE, "%Y-%m-%d")
    end = datetime.strptime(END_DATE, "%Y-%m-%d")
    
    all_results = []
    current = start
    
    while current <= end:
        # Calculate end of current month
        if current.month == 12:
            month_end = current.replace(year=current.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = current.replace(month=current.month + 1, day=1) - timedelta(days=1)
        
        if month_end > end:
            month_end = end
            
        month_start_str = current.strftime("%Y-%m-%d")
        month_end_str = month_end.strftime("%Y-%m-%d")
        
        print(f"  Fetching {month_start_str} to {month_end_str}")
        
        params = {
            "datasetid": "GHCND",
            "stationid": CORRECT_STATION_ID,
            "datatypeid": "PRCP,TMAX,TMIN,AWND",
            "startdate": month_start_str,
            "enddate": month_end_str,
            "limit": 1000,
            "units": "standard"
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if "results" in data:
                all_results.extend(data["results"])
                print(f"    Got {len(data['results'])} records")
            else:
                print(f"    No data for this period")
                
            time.sleep(0.5)  # Be nice to the API
            
        except Exception as e:
            print(f"    Error fetching {month_start_str}: {e}")
            
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)
    
    print(f"\nTotal records retrieved: {len(all_results)}")
    
    # Process results by date with CORRECTED conversions
    daily_data = {}
    
    for item in all_results:
        date = item["date"]
        datatype = item["datatype"]
        value = item["value"]
        
        if date not in daily_data:
            daily_data[date] = {
                "date": date,
                "precipitation_inches": 0,
                "max_temp_f": None,
                "min_temp_f": None,
                "avg_wind_mph": None
            }
        
        if datatype == "PRCP":
            # CORRECTED: With units=standard, precipitation appears to be in inches already
            daily_data[date]["precipitation_inches"] = value
        elif datatype == "TMAX":
            # CORRECTED: With units=standard, temperature is in Fahrenheit already
            daily_data[date]["max_temp_f"] = round(value)
        elif datatype == "TMIN":
            # CORRECTED: With units=standard, temperature is in Fahrenheit already
            daily_data[date]["min_temp_f"] = round(value)
        elif datatype == "AWND":
            # Wind speed: convert from m/s to mph
            daily_data[date]["avg_wind_mph"] = round(value * 2.237, 1)
    
    # Convert to list and add categorization
    results = []
    for date_str, data in sorted(daily_data.items()):
        inches = data["precipitation_inches"]
        category, measurable, moderate, heavy, very_heavy = categorize_precipitation(inches)
        
        # Work suitability assessment
        work_suitable = (
            inches < 0.1 and 
            (data["min_temp_f"] is None or data["min_temp_f"] > 40) and
            (data["max_temp_f"] is None or data["max_temp_f"] < 90)
        )
        
        results.append({
            "Date": date_str,
            "Total_Inches": round(inches, 4),
            "Category": category,
            "Measurable_0.01": "Yes" if measurable else "No",
            "Light_0.01": "Yes" if (measurable and not moderate) else "No",
            "Moderate_0.25": "Yes" if (moderate and not heavy) else "No", 
            "Heavy_0.5": "Yes" if (heavy and not very_heavy) else "No",
            "Very_Heavy_1.0": "Yes" if very_heavy else "No",
            "Max_Temp_F": data["max_temp_f"],
            "Min_Temp_F": data["min_temp_f"],
            "Avg_Wind_MPH": data["avg_wind_mph"],
            "Work_Suitable": "Yes" if work_suitable else "No",
            "Timestamp": datetime.now().isoformat()
        })
    
    return results

def create_summary_stats(data):
    """Create summary statistics"""
    if not data:
        return
        
    df = pd.DataFrame(data)
    
    # Calculate statistics
    total_days = len(df)
    days_with_measurable = len(df[df['Measurable_0.01'] == 'Yes'])
    days_with_moderate_plus = len(df[df['Moderate_0.25'] == 'Yes']) + len(df[df['Heavy_0.5'] == 'Yes']) + len(df[df['Very_Heavy_1.0'] == 'Yes'])
    total_precipitation = df['Total_Inches'].sum()
    max_daily = df['Total_Inches'].max()
    work_days_suitable = len(df[df['Work_Suitable'] == 'Yes'])
    
    print("\n" + "="*60)
    print("CORRECTED KCEC PRECIPITATION SUMMARY")
    print("Station: CRESCENT CITY MCNAMARA AIRPORT")
    print(f"Period: {START_DATE} to {END_DATE}")
    print("="*60)
    print(f"Total days analyzed: {total_days}")
    print(f"Total precipitation: {total_precipitation:.2f} inches")
    print(f"Average daily: {total_precipitation/total_days:.3f} inches")
    print(f"Maximum daily: {max_daily:.2f} inches")
    print()
    print(f"Days with measurable precipitation (≥0.01\"): {days_with_measurable} ({days_with_measurable/total_days*100:.1f}%)")
    print(f"Days with work-impacting rain (≥0.25\"): {days_with_moderate_plus} ({days_with_moderate_plus/total_days*100:.1f}%)")
    print(f"Days suitable for outdoor work: {work_days_suitable} ({work_days_suitable/total_days*100:.1f}%)")
    
    # Show some examples of rainy days
    rainy_days = df[df['Total_Inches'] > 0.1].head(10)
    if not rainy_days.empty:
        print(f"\nTop 10 rainiest days:")
        for _, row in rainy_days.iterrows():
            print(f"  {row['Date']}: {row['Total_Inches']}\" ({row['Category']})")

def main():
    """Main execution"""
    print("CORRECTED KCEC Historical Weather Data Collection")
    print("Using the CORRECT station: CRESCENT CITY MCNAMARA AIRPORT")
    print("-" * 50)
    
    # First test the data format
    test_data_format()
    
    # Get corrected historical data
    data = get_corrected_historical_data()
    
    if data:
        # Save to CSV
        df = pd.DataFrame(data)
        filename = f"kcec_corrected_historical_{START_DATE}_to_{END_DATE}.csv"
        df.to_csv(filename, index=False)
        print(f"\n✓ Corrected data saved to {filename}")
        
        # Create summary
        create_summary_stats(data)
        
        # Save JSON for n8n
        with open("kcec_corrected_data_for_n8n.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"✓ JSON format saved for n8n import")
        
    else:
        print("✗ Failed to retrieve data")

if __name__ == "__main__":
    main()