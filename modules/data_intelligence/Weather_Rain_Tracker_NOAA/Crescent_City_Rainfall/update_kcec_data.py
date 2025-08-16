#!/usr/bin/env python3
"""
KCEC Data Update Script
Simple script to download the latest weather data and create an Excel export
"""

from kcec_excel_export import KCECExcelExporter
from datetime import datetime, timedelta
import os
import json

def update_kcec_data():
    """Update KCEC data with latest information"""
    
    print("KCEC Weather Data Update")
    print("=" * 40)
    
    exporter = KCECExcelExporter()
    
    # Load NOAA token from config if available
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            if config.get("noaa_token"):
                exporter.set_noaa_token(config["noaa_token"])
                print("✓ NOAA token loaded from config")
            else:
                print("⚠ No NOAA token in config - will use existing data only")
    else:
        print("⚠ No config file found - will use existing data only")
    
    # Get current date range for export
    end_date = datetime.now().strftime("%Y-%m-%d")
    print(f"Creating export through {end_date}")
    
    # Create Excel export with all available data
    output_file = exporter.create_excel_format_export(end_date=end_date)
    
    if output_file:
        print(f"\n✓ SUCCESS: Excel export created")
        print(f"📁 File: {output_file}")
        
        # Get file info
        file_size = os.path.getsize(output_file)
        print(f"📊 Size: {file_size:,} bytes")
        
        return output_file
    else:
        print("❌ FAILED: Could not create Excel export")
        return None

if __name__ == "__main__":
    update_kcec_data()