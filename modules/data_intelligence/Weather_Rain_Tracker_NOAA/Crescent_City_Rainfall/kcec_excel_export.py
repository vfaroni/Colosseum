#!/usr/bin/env python3
"""
KCEC Excel Export Script
Creates Excel-compatible weather data export matching the exact format needed for contract analysis
Based on existing KCEC complete dataset with holidays, temperature, and wind data
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import glob

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "weather_data")

class KCECExcelExporter:
    def __init__(self):
        self.data_dir = DATA_DIR
        self.noaa_token = None
        self.station_id = "GHCND:USW00024286"  # CRESCENT CITY MCNAMARA AIRPORT
        
        # Load config if available
        config_path = os.path.join(BASE_DIR, "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.noaa_token = config.get("noaa_token")
    
    def set_noaa_token(self, token):
        """Set NOAA API token"""
        self.noaa_token = token
    
    def get_federal_holidays(self):
        """Get federal holidays for 2024, 2025, and 2026"""
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
            '2025-12-25': 'Christmas Day',
            
            # 2026 Federal Holidays
            '2026-01-01': 'New Year\'s Day',
            '2026-01-19': 'Martin Luther King Jr. Day',
            '2026-02-16': 'Presidents\' Day',
            '2026-05-25': 'Memorial Day',
            '2026-06-19': 'Juneteenth',
            '2026-07-04': 'Independence Day',
            '2026-09-07': 'Labor Day',
            '2026-10-12': 'Columbus Day',
            '2026-11-11': 'Veterans Day',
            '2026-11-26': 'Thanksgiving Day',
            '2026-12-25': 'Christmas Day'
        }
        return federal_holidays
    
    def get_california_holidays(self):
        """Get California state holidays for 2024, 2025, and 2026"""
        ca_holidays = {
            # 2024 California Holidays
            '2024-01-01': 'New Year\'s Day',
            '2024-01-15': 'Martin Luther King Jr. Day',
            '2024-02-19': 'Presidents\' Day',
            '2024-03-31': 'César Chávez Day',
            '2024-05-27': 'Memorial Day',
            '2024-06-19': 'Juneteenth',
            '2024-07-04': 'Independence Day',
            '2024-09-02': 'Labor Day',
            '2024-10-14': 'Columbus Day',
            '2024-11-11': 'Veterans Day',
            '2024-11-28': 'Thanksgiving Day',
            '2024-11-29': 'Day After Thanksgiving',
            '2024-12-25': 'Christmas Day',
            
            # 2025 California Holidays
            '2025-01-01': 'New Year\'s Day',
            '2025-01-20': 'Martin Luther King Jr. Day',
            '2025-02-17': 'Presidents\' Day',
            '2025-03-31': 'César Chávez Day',
            '2025-05-26': 'Memorial Day',
            '2025-06-19': 'Juneteenth',
            '2025-07-04': 'Independence Day',
            '2025-09-01': 'Labor Day',
            '2025-10-13': 'Columbus Day',
            '2025-11-11': 'Veterans Day',
            '2025-11-27': 'Thanksgiving Day',
            '2025-11-28': 'Day After Thanksgiving',
            '2025-12-25': 'Christmas Day',
            
            # 2026 California Holidays
            '2026-01-01': 'New Year\'s Day',
            '2026-01-19': 'Martin Luther King Jr. Day',
            '2026-02-16': 'Presidents\' Day',
            '2026-03-31': 'César Chávez Day',
            '2026-05-25': 'Memorial Day',
            '2026-06-19': 'Juneteenth',
            '2026-07-04': 'Independence Day',
            '2026-09-07': 'Labor Day',
            '2026-10-12': 'Columbus Day',
            '2026-11-11': 'Veterans Day',
            '2026-11-26': 'Thanksgiving Day',
            '2026-11-27': 'Day After Thanksgiving',
            '2026-12-25': 'Christmas Day'
        }
        return ca_holidays
    
    def download_latest_data(self, start_date=None, end_date=None):
        """Download latest weather data from NOAA"""
        if not self.noaa_token:
            print("ERROR: NOAA token required. Set with set_noaa_token() or add to config.json")
            return None
            
        if not start_date:
            # Default to last 30 days
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        elif not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"Downloading KCEC data from {start_date} to {end_date}")
        
        base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
        headers = {"token": self.noaa_token}
        
        all_data = {}
        
        # Get precipitation, temperature, and wind data
        params = {
            "datasetid": "GHCND",
            "stationid": self.station_id,
            "datatypeid": "PRCP,TMAX,TMIN,AWND",
            "startdate": start_date,
            "enddate": end_date,
            "units": "standard",
            "limit": 1000
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data:
                for item in data["results"]:
                    date = item["date"][:10]
                    datatype = item["datatype"]
                    value = item["value"] if item["value"] else None
                    
                    if date not in all_data:
                        all_data[date] = {}
                    
                    if datatype == "PRCP":
                        # PRCP comes in hundredths of inches in standard units
                        all_data[date]["Total_Inches"] = round(value / 100, 2) if value else 0.0
                    elif datatype == "TMAX":
                        all_data[date]["High_Temp_F"] = int(round(value)) if value else None
                    elif datatype == "TMIN":
                        all_data[date]["Low_Temp_F"] = int(round(value)) if value else None
                    elif datatype == "AWND":
                        all_data[date]["Avg_Wind_MPH"] = round(value, 1) if value else None
                
                print(f"Downloaded data for {len(all_data)} days")
                return all_data
            else:
                print("No data found for specified date range")
                return None
                
        except Exception as e:
            print(f"Error downloading data: {e}")
            return None
    
    def create_excel_format_export(self, start_date=None, end_date=None, output_file=None):
        """Create Excel-compatible export matching the exact format shown in screenshot"""
        
        # Try to use existing complete dataset first
        pattern = os.path.join(self.data_dir, "kcec_complete_with_holidays_*.csv")
        files = glob.glob(pattern)
        
        if files:
            # Use most recent complete dataset
            dataset_file = max(files, key=os.path.getctime)
            print(f"Using existing complete dataset: {dataset_file}")
            df = pd.read_csv(dataset_file)
            
            # Convert Date column to datetime for filtering, and remove any rows with null dates
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date'])  # Remove rows with invalid dates
            
            # Filter by date range if specified
            if start_date:
                df = df[df['Date'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['Date'] <= pd.to_datetime(end_date)]
        else:
            # Download new data if no existing dataset
            print("No existing complete dataset found. Downloading new data...")
            weather_data = self.download_latest_data(start_date, end_date)
            if not weather_data:
                return None
                
            # Create DataFrame from downloaded data
            df = self.create_dataframe_from_weather_data(weather_data)
        
        # Create the exact Excel format matching the user's spreadsheet
        excel_df = pd.DataFrame()
        
        # Column A: Date (YYYY-MM-DD format)
        excel_df['Date'] = df['Date']
        
        # Column B: Year
        excel_df['Year'] = df['Date'].dt.year.astype(float)
        
        # Column C: Month  
        excel_df['Month'] = df['Date'].dt.month.astype(float)
        
        # Column D: Day
        excel_df['Day'] = df['Date'].dt.day.astype(float)
        
        # Column E: Month_Name
        excel_df['Month_Name'] = df['Date'].dt.strftime('%B')
        
        # Column F: Day_of_Week
        excel_df['Day_of_Week'] = df['Date'].dt.strftime('%A')
        
        # Column G: Total_Inches (precipitation)
        total_inches = df.get('Total_Inches', 0).fillna(0)
        excel_df['Total_Inches'] = total_inches.astype(float)
        
        # Column H: High_Temp_F
        excel_df['High_Temp_F'] = df.get('High_Temp_F', 0).fillna(0).astype(float)
        
        # Column I: Low_Temp_F  
        excel_df['Low_Temp_F'] = df.get('Low_Temp_F', 0).fillna(0).astype(float)
        
        # Column J: Avg_Wind_MPH
        excel_df['Avg_Wind_MPH'] = df.get('Avg_Wind_MPH', 0).fillna(0).astype(float)
        
        # Column K: Category (Light/Moderate/Heavy/Very Heavy based on precipitation)
        excel_df['Category'] = None
        precip_numeric = total_inches
        excel_df.loc[precip_numeric >= 1.0, 'Category'] = 'Very Heavy'
        excel_df.loc[(precip_numeric >= 0.5) & (precip_numeric < 1.0), 'Category'] = 'Heavy'
        excel_df.loc[(precip_numeric >= 0.25) & (precip_numeric < 0.5), 'Category'] = 'Moderate'
        excel_df.loc[(precip_numeric >= 0.01) & (precip_numeric < 0.25), 'Category'] = 'Light'
        
        # Columns L-P: Threshold indicators (1 or 0)
        excel_df['Measurable_0.01'] = (precip_numeric >= 0.01).astype(int)
        excel_df['Contract_0.10'] = (precip_numeric >= 0.10).astype(int)
        excel_df['Normal_0.25'] = (precip_numeric >= 0.25).astype(int)
        excel_df['Heavy_0.50'] = (precip_numeric >= 0.50).astype(int)
        excel_df['Very_Heavy_1.0'] = (precip_numeric >= 1.0).astype(int)
        
        # Column Q: Work_Suitable_Area (1 if precipitation < 0.10", 0 otherwise)
        excel_df['Work_Suitable_Area'] = (precip_numeric < 0.10).astype(float)
        
        # Columns R-U: Holiday information
        federal_holidays = self.get_federal_holidays()
        ca_holidays = self.get_california_holidays()
        
        excel_df['Federal_Holiday'] = 0.0
        excel_df['Federal_Holiday_Name'] = None
        excel_df['CA_State_Holiday'] = 0.0
        excel_df['CA_State_Holiday_Name'] = None
        
        for idx, row in excel_df.iterrows():
            # Convert date back for holiday lookup using original df Date column
            original_date = df.iloc[idx]['Date']
            if pd.isna(original_date):
                continue
            date_str = original_date.strftime('%Y-%m-%d')
            
            if date_str in federal_holidays:
                excel_df.at[idx, 'Federal_Holiday'] = 1.0
                excel_df.at[idx, 'Federal_Holiday_Name'] = federal_holidays[date_str]
            
            if date_str in ca_holidays:
                excel_df.at[idx, 'CA_State_Holiday'] = 1.0
                excel_df.at[idx, 'CA_State_Holiday_Name'] = ca_holidays[date_str]
        
        # Save to Excel file
        if not output_file:
            start_str = str(excel_df['Date'].iloc[0]).replace('/', '_')
            end_str = str(excel_df['Date'].iloc[-1]).replace('/', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(self.data_dir, f"KCEC_Excel_Export_{start_str}_to_{end_str}_{timestamp}.xlsx")
        
        # Write to Excel with proper formatting
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            excel_df.to_excel(writer, sheet_name='KCEC_Weather_Data', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['KCEC_Weather_Data']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 20)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"Excel export saved: {output_file}")
        print(f"Records exported: {len(excel_df)}")
        
        # Show sample of exported data
        print("\nSample of exported data:")
        print(excel_df[['Date', 'Day_of_Week', 'Total_Inches', 'High_Temp_F', 'Low_Temp_F', 'Category', 'Contract_0.10']].head(10))
        
        return output_file
    
    def create_dataframe_from_weather_data(self, weather_data):
        """Create DataFrame from weather data dictionary"""
        dates = sorted(weather_data.keys())
        
        data = []
        for date_str in dates:
            row = weather_data[date_str]
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            data.append({
                'Date': date_obj,
                'Total_Inches': row.get('Total_Inches', 0),
                'High_Temp_F': row.get('High_Temp_F'),
                'Low_Temp_F': row.get('Low_Temp_F'),
                'Avg_Wind_MPH': row.get('Avg_Wind_MPH')
            })
        
        return pd.DataFrame(data)
    
    def update_existing_dataset(self, days_back=7):
        """Update existing dataset with recent data"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        print(f"Updating dataset with data from {start_date} to {end_date}")
        
        # Download recent data
        new_data = self.download_latest_data(start_date, end_date)
        if not new_data:
            print("No new data downloaded")
            return None
        
        # Create export with recent data
        output_file = self.create_excel_format_export(start_date, end_date)
        
        return output_file

def main():
    """Main function for Excel export"""
    print("KCEC Weather Data Excel Exporter")
    print("=" * 50)
    
    exporter = KCECExcelExporter()
    
    print("Available options:")
    print("1. Export existing complete dataset to Excel format")
    print("2. Download and export recent data (last 30 days)")
    print("3. Export specific date range")
    print("4. Update with latest data (last 7 days)")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        # Export existing complete dataset
        output_file = exporter.create_excel_format_export()
        if output_file:
            print(f"\nSUCCESS: Excel export created at {output_file}")
        
    elif choice == "2":
        # Download and export recent data
        if not exporter.noaa_token:
            token = input("Enter NOAA API token (get free at https://www.ncdc.noaa.gov/cdo-web/token): ").strip()
            exporter.set_noaa_token(token)
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        output_file = exporter.create_excel_format_export(start_date, end_date)
        if output_file:
            print(f"\nSUCCESS: Excel export created at {output_file}")
    
    elif choice == "3":
        # Export specific date range
        start_date = input("Enter start date (YYYY-MM-DD): ").strip()
        end_date = input("Enter end date (YYYY-MM-DD): ").strip()
        
        output_file = exporter.create_excel_format_export(start_date, end_date)
        if output_file:
            print(f"\nSUCCESS: Excel export created at {output_file}")
    
    elif choice == "4":
        # Update with latest data
        if not exporter.noaa_token:
            token = input("Enter NOAA API token: ").strip()
            exporter.set_noaa_token(token)
        
        output_file = exporter.update_existing_dataset()
        if output_file:
            print(f"\nSUCCESS: Updated Excel export created at {output_file}")
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()