#!/usr/bin/env python3
"""
Analyze Hayden's rainfall data in detail
"""

import os
import pandas as pd
from datetime import datetime
import numpy as np

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "weather_data")

def analyze_hayden_data():
    """Detailed analysis of Hayden's rain data"""
    excel_file = os.path.join(DATA_DIR, "ACG_Weather_Data", "Hayden_Rain_Info_2024.xlsx")
    
    print(f"Analyzing Hayden's data from: {excel_file}")
    
    # Read Excel file - try different sheets
    xl = pd.ExcelFile(excel_file)
    print(f"\nSheets in Excel file: {xl.sheet_names}")
    
    # Read all sheets
    for sheet_name in xl.sheet_names:
        print(f"\n{'='*60}")
        print(f"Sheet: {sheet_name}")
        print('='*60)
        
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"\nFirst 10 rows:")
        print(df.head(10))
        
        # Try to understand the date column
        if 'Day' in df.columns:
            print(f"\nDate range in 'Day' column:")
            print(f"First: {df['Day'].iloc[0]}")
            print(f"Last: {df['Day'].iloc[-1]}")
            
            # Check if it's actually 2024 data
            if pd.api.types.is_datetime64_any_dtype(df['Day']):
                years = df['Day'].dt.year.unique()
                print(f"Years in data: {years}")
        
        # Analyze precipitation
        precip_col = None
        for col in df.columns:
            if 'precip' in col.lower() or 'rain' in col.lower():
                precip_col = col
                break
        
        if precip_col:
            print(f"\nPrecipitation column: {precip_col}")
            
            # Convert to numeric, handling any non-numeric values
            df[precip_col] = pd.to_numeric(df[precip_col], errors='coerce')
            
            # Basic stats
            total_days = len(df)
            rainy_days = (df[precip_col] > 0).sum()
            measurable_days = (df[precip_col] >= 0.01).sum()
            total_rain = df[precip_col].sum()
            
            print(f"\nRainfall Statistics:")
            print(f"Total days: {total_days}")
            print(f"Days with any rain (>0): {rainy_days}")
            print(f"Days with measurable rain (≥0.01\"): {measurable_days}")
            print(f"Total rainfall: {total_rain:.2f} inches")
            print(f"Average on rainy days: {(total_rain/rainy_days if rainy_days > 0 else 0):.2f} inches")
            
            # Distribution
            print(f"\nRainfall Distribution:")
            print(f"Light (0.01-0.25\"): {((df[precip_col] >= 0.01) & (df[precip_col] < 0.25)).sum()} days")
            print(f"Moderate (0.25-0.5\"): {((df[precip_col] >= 0.25) & (df[precip_col] < 0.5)).sum()} days")
            print(f"Heavy (0.5-1.0\"): {((df[precip_col] >= 0.5) & (df[precip_col] < 1.0)).sum()} days")
            print(f"Very Heavy (≥1.0\"): {(df[precip_col] >= 1.0).sum()} days")
            
            # Monthly breakdown if we can parse dates
            if 'Day' in df.columns:
                try:
                    df['Date'] = pd.to_datetime(df['Day'])
                    df['Month'] = df['Date'].dt.month
                    
                    monthly = df.groupby('Month').agg({
                        precip_col: ['sum', lambda x: (x > 0).sum()]
                    })
                    monthly.columns = ['Total_Inches', 'Rainy_Days']
                    
                    print(f"\nMonthly Breakdown:")
                    print("-" * 40)
                    for month, row in monthly.iterrows():
                        try:
                            month_name = datetime(2024, int(month), 1).strftime('%B')
                            print(f"{month_name:10} | {row['Total_Inches']:6.2f}\" | Rainy days: {int(row['Rainy_Days']):2d}")
                        except:
                            print(f"Month {month:2d} | {row['Total_Inches']:6.2f}\" | Rainy days: {int(row['Rainy_Days']):2d}")
                except Exception as e:
                    print(f"\nCould not parse dates: {e}")
    
    return xl

if __name__ == "__main__":
    print("Detailed Analysis of Hayden's Rainfall Data")
    print("="*60)
    
    analyze_hayden_data()