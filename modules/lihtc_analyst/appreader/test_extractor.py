#!/usr/bin/env python3
"""
Quick test version of LIHTC extractor - processes only a few files
"""

import pandas as pd
import json
from pathlib import Path

def test_single_file(file_path, county_filter=None):
    """Test extraction on a single file"""
    print(f"\n=== Testing file: {file_path.name} ===")
    
    try:
        excel_file = pd.ExcelFile(file_path)
        print(f"Sheets: {excel_file.sheet_names}")
        
        # Extract from Application tab
        app_df = pd.read_excel(file_path, sheet_name="Application", header=None)
        
        # Project Name (Row 18, Col H)
        project_name = app_df.iloc[17, 7] if len(app_df) > 17 and len(app_df.columns) > 7 else "Not found"
        print(f"Project Name: {project_name}")
        
        # Search for County
        county = "Not found"
        for row_idx in range(180, min(250, len(app_df))):
            for col_idx in range(min(25, len(app_df.columns))):
                cell = str(app_df.iloc[row_idx, col_idx]) if pd.notna(app_df.iloc[row_idx, col_idx]) else ""
                if "county" in cell.lower() and ":" in cell:
                    # Look for value in next column
                    if col_idx + 1 < len(app_df.columns):
                        county_val = app_df.iloc[row_idx, col_idx + 1]
                        if pd.notna(county_val):
                            county = str(county_val).strip()
                            break
            if county != "Not found":
                break
        
        print(f"County: {county}")
        
        # Check if county matches filter
        if county_filter and county_filter.lower() not in county.lower():
            print(f"County doesn't match filter '{county_filter}' - skipping")
            return None
        
        # Extract from Sources and Uses Budget
        su_df = pd.read_excel(file_path, sheet_name="Sources and Uses Budget", header=None)
        
        # Get costs (typically in column B)
        land_cost = su_df.iloc[3, 1] if len(su_df) > 3 and len(su_df.columns) > 1 else 0
        construction = su_df.iloc[37, 1] if len(su_df) > 37 and len(su_df.columns) > 1 else 0
        architectural = su_df.iloc[41, 1] if len(su_df) > 41 and len(su_df.columns) > 1 else 0
        
        print(f"Land Cost: ${land_cost:,.0f}")
        print(f"Construction: ${construction:,.0f}")
        print(f"Architectural: ${architectural:,.0f}")
        
        result = {
            "filename": file_path.name,
            "project_name": str(project_name),
            "county": county,
            "land_cost": float(land_cost) if pd.notna(land_cost) else 0,
            "construction_cost": float(construction) if pd.notna(construction) else 0,
            "architectural_cost": float(architectural) if pd.notna(architectural) else 0
        }
        
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    source_dir = Path("/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data")
    
    # Test with a few known files
    test_files = [
        "2024_4pct_R1_24-409.xlsx",  # Marina Towers - Solano County
        "2024_4pct_R1_24-408.xlsx",
        "2024_4pct_R1_24-410.xlsx"
    ]
    
    results = []
    county_filter = "Solano"
    
    print(f"Testing extraction for {county_filter} County")
    
    for filename in test_files:
        file_path = source_dir / filename
        if file_path.exists():
            result = test_single_file(file_path, county_filter)
            if result:
                results.append(result)
        else:
            print(f"File not found: {filename}")
    
    # Save results
    if results:
        output_file = Path("/Users/vitorfaroni/Documents/Automation/LIHTCApp/test_results.json")
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n=== Summary ===")
        print(f"Found {len(results)} projects in {county_filter} County")
        for result in results:
            print(f"- {result['project_name']} (${result['land_cost']:,.0f} land cost)")
        
        print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()