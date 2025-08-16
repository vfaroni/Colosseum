#!/usr/bin/env python3
"""
KCEC Historical Data Backfill
Collects precipitation data from May 1, 2024 to present with detailed categorization
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import time

# Configuration
NOAA_TOKEN = 'oaLvXPjjAWoSCizEBvNoHPNhATmdDmQA'
STATION_ID = "GHCND:USW00093814"
START_DATE = "2024-05-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")

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

def get_historical_data():
    """Get all historical data from NOAA in monthly chunks"""
    print(f"Fetching KCEC precipitation data from {START_DATE} to {END_DATE}")
    
    # NOAA API endpoint
    base_url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
    headers = {"token": NOAA_TOKEN}
    
    # Generate monthly date ranges
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
        
        # Don't go past our end date
        if month_end > end:
            month_end = end
            
        month_start_str = current.strftime("%Y-%m-%d")
        month_end_str = month_end.strftime("%Y-%m-%d")
        
        print(f"  Fetching {month_start_str} to {month_end_str}")
        
        # Request data for this month
        params = {
            "datasetid": "GHCND",
            "stationid": STATION_ID,
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
                
            # Small delay to be nice to the API
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Error fetching {month_start_str}: {e}")
            
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)
    
    if not all_results:
        print("No data found")
        return None
            
    # Process results by date
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
            # Convert from tenths of mm to inches
            daily_data[date]["precipitation_inches"] = round(value / 10 / 25.4, 4)
        elif datatype == "TMAX":
            # Convert from Celsius to Fahrenheit
            daily_data[date]["max_temp_f"] = round(value * 9/5 + 32)
        elif datatype == "TMIN":
            # Convert from Celsius to Fahrenheit  
            daily_data[date]["min_temp_f"] = round(value * 9/5 + 32)
        elif datatype == "AWND":
            # Convert from m/s to mph
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
            "Total_Inches": inches,
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

def save_to_csv(data):
    """Save data to CSV file"""
    if not data:
        return None
        
    df = pd.DataFrame(data)
    filename = f"kcec_historical_{START_DATE}_to_{END_DATE}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved {len(data)} records to {filename}")
    
    return filename

def create_summary_stats(data):
    """Create summary statistics"""
    if not data:
        return
        
    df = pd.DataFrame(data)
    
    # Calculate statistics
    total_days = len(df)
    days_with_measurable = len(df[df['Measurable_0.01'] == 'Yes'])
    days_with_moderate = len(df[df['Moderate_0.25'] == 'Yes']) + len(df[df['Heavy_0.5'] == 'Yes']) + len(df[df['Very_Heavy_1.0'] == 'Yes'])
    total_precipitation = df['Total_Inches'].sum()
    max_daily = df['Total_Inches'].max()
    work_days_suitable = len(df[df['Work_Suitable'] == 'Yes'])
    
    # Monthly breakdown
    df['Month'] = pd.to_datetime(df['Date']).dt.to_period('M')
    monthly_stats = df.groupby('Month').agg({
        'Total_Inches': ['sum', 'count'],
        'Measurable_0.01': lambda x: (x == 'Yes').sum(),
        'Work_Suitable': lambda x: (x == 'Yes').sum()
    }).round(2)
    
    print("\n" + "="*60)
    print("KCEC PRECIPITATION SUMMARY - May 1, 2024 to Present")
    print("="*60)
    print(f"Total days analyzed: {total_days}")
    print(f"Total precipitation: {total_precipitation:.2f} inches")
    print(f"Average daily: {total_precipitation/total_days:.3f} inches")
    print(f"Maximum daily: {max_daily:.2f} inches")
    print()
    print(f"Days with measurable precipitation (≥0.01\"): {days_with_measurable} ({days_with_measurable/total_days*100:.1f}%)")
    print(f"Days with work-impacting rain (≥0.25\"): {days_with_moderate} ({days_with_moderate/total_days*100:.1f}%)")
    print(f"Days suitable for outdoor work: {work_days_suitable} ({work_days_suitable/total_days*100:.1f}%)")
    print()
    print("Monthly Breakdown:")
    print(monthly_stats)

def main():
    """Main execution function"""
    print("KCEC Historical Weather Data Collection")
    print("-" * 50)
    
    # Get historical data
    data = get_historical_data()
    
    if data:
        # Save to CSV
        filename = save_to_csv(data)
        
        # Create summary
        create_summary_stats(data)
        
        print(f"\n✓ Historical data collection complete!")
        print(f"✓ {len(data)} days of data saved to {filename}")
        print(f"✓ Ready to import into Google Sheets or n8n")
        
        # Create JSON for n8n import
        with open("historical_data_for_n8n.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"✓ JSON format saved for n8n import")
        
    else:
        print("✗ Failed to retrieve historical data")

if __name__ == "__main__":
    main()