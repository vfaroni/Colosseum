#!/usr/bin/env python3
"""
Add State (California) and Federal holiday columns to the KCEC dataset
"""

import os
import pandas as pd
from datetime import datetime, date
import glob

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "weather_data")

def get_federal_holidays():
    """Get federal holidays for 2024 and 2025"""
    
    federal_holidays = {
        # 2024 Federal Holidays
        '2024-01-01': 'New Year\'s Day',
        '2024-01-15': 'Martin Luther King Jr. Day',
        '2024-02-19': 'Presidents\' Day',
        '2024-05-27': 'Memorial Day',
        '2024-06-19': 'Juneteenth',
        '2024-07-04': 'Independence Day',
        '2024-09-02': 'Labor Day',
        '2024-10-14': 'Columbus Day',
        '2024-11-11': 'Veterans Day',
        '2024-11-28': 'Thanksgiving Day',
        '2024-12-25': 'Christmas Day',
        
        # 2025 Federal Holidays
        '2025-01-01': 'New Year\'s Day',
        '2025-01-20': 'Martin Luther King Jr. Day',
        '2025-02-17': 'Presidents\' Day',
        '2025-05-26': 'Memorial Day',
        '2025-06-19': 'Juneteenth',
        '2025-07-04': 'Independence Day',
        '2025-09-01': 'Labor Day',
        '2025-10-13': 'Columbus Day',
        '2025-11-11': 'Veterans Day',
        '2025-11-27': 'Thanksgiving Day',
        '2025-12-25': 'Christmas Day'
    }
    
    return federal_holidays

def get_california_holidays():
    """Get California state holidays for 2024 and 2025"""
    
    # California has all federal holidays plus some additional ones
    ca_holidays = {
        # 2024 California Holidays (includes all federal plus CA-specific)
        '2024-01-01': 'New Year\'s Day',
        '2024-01-15': 'Martin Luther King Jr. Day',
        '2024-02-19': 'Presidents\' Day',
        '2024-03-31': 'César Chávez Day',  # CA specific
        '2024-05-27': 'Memorial Day',
        '2024-06-19': 'Juneteenth',
        '2024-07-04': 'Independence Day',
        '2024-09-02': 'Labor Day',
        '2024-10-14': 'Columbus Day',
        '2024-11-11': 'Veterans Day',
        '2024-11-28': 'Thanksgiving Day',
        '2024-11-29': 'Day After Thanksgiving',  # CA specific
        '2024-12-25': 'Christmas Day',
        
        # 2025 California Holidays
        '2025-01-01': 'New Year\'s Day',
        '2025-01-20': 'Martin Luther King Jr. Day',
        '2025-02-17': 'Presidents\' Day',
        '2025-03-31': 'César Chávez Day',  # CA specific
        '2025-05-26': 'Memorial Day',
        '2025-06-19': 'Juneteenth',
        '2025-07-04': 'Independence Day',
        '2025-09-01': 'Labor Day',
        '2025-10-13': 'Columbus Day',
        '2025-11-11': 'Veterans Day',
        '2025-11-27': 'Thanksgiving Day',
        '2025-11-28': 'Day After Thanksgiving',  # CA specific
        '2025-12-25': 'Christmas Day'
    }
    
    return ca_holidays

def add_holiday_columns():
    """Add holiday columns to the final KCEC dataset"""
    
    print("Adding Federal and California State Holiday columns...")
    
    # Find the most recent final dataset
    pattern = os.path.join(DATA_DIR, "kcec_complete_FINAL_*_20250623_192113.csv")
    files = glob.glob(pattern)
    
    if not files:
        print("ERROR: Final dataset not found")
        return None
    
    dataset_file = files[0]
    print(f"Reading: {dataset_file}")
    
    # Read the dataset
    df = pd.read_csv(dataset_file)
    print(f"Original records: {len(df)}")
    
    # Get holiday dictionaries
    federal_holidays = get_federal_holidays()
    ca_holidays = get_california_holidays()
    
    # Add holiday columns
    df['Federal_Holiday'] = 0
    df['Federal_Holiday_Name'] = ''
    df['CA_State_Holiday'] = 0
    df['CA_State_Holiday_Name'] = ''
    
    # Process each row
    federal_count = 0
    ca_count = 0
    
    for index, row in df.iterrows():
        date_str = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
        
        # Check federal holidays
        if date_str in federal_holidays:
            df.at[index, 'Federal_Holiday'] = 1
            df.at[index, 'Federal_Holiday_Name'] = federal_holidays[date_str]
            federal_count += 1
        
        # Check California holidays
        if date_str in ca_holidays:
            df.at[index, 'CA_State_Holiday'] = 1
            df.at[index, 'CA_State_Holiday_Name'] = ca_holidays[date_str]
            ca_count += 1
    
    print(f"Federal holidays found: {federal_count}")
    print(f"California holidays found: {ca_count}")
    
    # Reorder columns to put holidays at the end
    # Get all columns except the new holiday ones
    base_columns = [col for col in df.columns if not col.startswith(('Federal_Holiday', 'CA_State_Holiday'))]
    
    # Add holiday columns at the end
    final_columns = base_columns + ['Federal_Holiday', 'Federal_Holiday_Name', 'CA_State_Holiday', 'CA_State_Holiday_Name']
    df_final = df[final_columns]
    
    # Save updated dataset
    start_date = pd.to_datetime(df_final['Date']).min().strftime('%Y-%m-%d')
    end_date = pd.to_datetime(df_final['Date']).max().strftime('%Y-%m-%d')
    
    output_file = os.path.join(DATA_DIR, f"kcec_complete_with_holidays_{start_date}_to_{end_date}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df_final.to_csv(output_file, index=False)
    
    print(f"Updated dataset with holidays saved: {output_file}")
    
    # Show sample of holiday data
    print(f"\nSample of holiday data:")
    holiday_sample = df_final[df_final['Federal_Holiday'] == 1][['Date', 'Day_of_Week', 'Federal_Holiday_Name', 'CA_State_Holiday_Name', 'Total_Inches', 'Contract_0.10']].head(10)
    print(holiday_sample)
    
    # Show holiday summary by year
    df_final['Year'] = pd.to_datetime(df_final['Date']).dt.year
    
    print(f"\nHoliday Summary by Year:")
    for year in [2024, 2025]:
        year_data = df_final[df_final['Year'] == year]
        federal_year = year_data['Federal_Holiday'].sum()
        ca_year = year_data['CA_State_Holiday'].sum()
        
        print(f"{year}: {federal_year} Federal holidays, {ca_year} CA holidays")
    
    # Show rain on holidays
    holiday_rain = df_final[df_final['Federal_Holiday'] == 1]
    rainy_holidays = holiday_rain['Contract_0.10'].sum()
    total_holidays = len(holiday_rain)
    
    print(f"\nRain on Federal Holidays:")
    print(f"Contract rain days (≥0.10\"): {rainy_holidays}/{total_holidays} federal holidays ({rainy_holidays/total_holidays*100:.1f}%)")
    
    # List all holidays with their rain status
    print(f"\nAll Federal Holidays with Rain Status:")
    print(f"{'Date':12} | {'Holiday':25} | {'Rain':>5} | {'Inches':>7}")
    print("-" * 55)
    
    for _, row in holiday_rain.iterrows():
        date_str = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
        holiday_name = row['Federal_Holiday_Name'][:24]  # Truncate long names
        rain_status = "Yes" if row['Contract_0.10'] == 1 else "No"
        inches = row['Total_Inches']
        
        print(f"{date_str:12} | {holiday_name:25} | {rain_status:>5} | {inches:7.2f}")
    
    return output_file

def main():
    """Main function to add holiday columns"""
    
    print("Adding Federal and California State Holiday Columns")
    print("="*60)
    
    # Add holiday columns
    final_file = add_holiday_columns()
    if final_file is None:
        print("Failed to add holiday columns")
        return
    
    print(f"\n" + "="*60)
    print("FINAL DATASET WITH HOLIDAYS READY!")
    print(f"File: {final_file}")
    print("Added columns:")
    print("  - Federal_Holiday (1/0)")
    print("  - Federal_Holiday_Name")
    print("  - CA_State_Holiday (1/0)")
    print("  - CA_State_Holiday_Name")
    print("Includes: New Year's, MLK Day, Presidents' Day, César Chávez Day (CA),")
    print("         Memorial Day, Juneteenth, Independence Day, Labor Day,")
    print("         Columbus Day, Veterans Day, Thanksgiving, Day After Thanksgiving (CA), Christmas")
    print("="*60)

if __name__ == "__main__":
    main()