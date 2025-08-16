#!/usr/bin/env python3
"""
Verify the export format matches the user's Excel requirements
"""

from kcec_excel_export import KCECExcelExporter
import pandas as pd

def verify_format():
    """Create a sample export and show the format"""
    
    exporter = KCECExcelExporter()
    
    # Create export for just the first few days to verify format
    output_file = exporter.create_excel_format_export("2024-01-01", "2024-01-10")
    
    if output_file:
        print(f"Sample export created: {output_file}")
        
        # Read the Excel file and show the structure
        df = pd.read_excel(output_file)
        
        print("\nColumn structure:")
        for i, col in enumerate(df.columns):
            print(f"Column {chr(65+i)}: {col}")
        
        print("\nFirst 10 rows:")
        print(df.head(10).to_string(index=False))
        
        print("\nData types:")
        print(df.dtypes)
        
        # Save as CSV for easy viewing
        csv_file = output_file.replace('.xlsx', '.csv')
        df.to_csv(csv_file, index=False)
        print(f"\nCSV version saved: {csv_file}")
        
    return output_file

if __name__ == "__main__":
    verify_format()