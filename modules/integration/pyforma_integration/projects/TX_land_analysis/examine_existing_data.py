#!/usr/bin/env python3
"""
Examine existing 195-site data structure to understand what we're working with
"""

import pandas as pd
import numpy as np

def examine_195_sites_data():
    """Load and examine the structure of existing 195 sites data"""
    
    # Path to the most complete/recent file
    excel_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/FINAL_195_Sites_Complete_With_Poverty_20250621_213537.xlsx"
    
    print(f"Examining: {excel_file}")
    print("=" * 80)
    
    try:
        # Get all sheet names
        xl_file = pd.ExcelFile(excel_file)
        print(f"Available sheets: {xl_file.sheet_names}")
        
        # Load the main sheet (likely the first one or 'All_195_Sites_Final')
        main_sheet = 'All_195_Sites_Final' if 'All_195_Sites_Final' in xl_file.sheet_names else xl_file.sheet_names[0]
        df = pd.read_excel(excel_file, sheet_name=main_sheet)
        
        print(f"\nLoaded sheet: {main_sheet}")
        print(f"Shape: {df.shape} (rows, columns)")
        
        print(f"\nColumn names:")
        for i, col in enumerate(df.columns):
            print(f"  {i:2d}: {col}")
        
        print(f"\nData types:")
        print(df.dtypes)
        
        print(f"\nFirst few rows of key columns:")
        key_columns = []
        
        # Look for key columns we'll need for pyforma
        column_keywords = {
            'site': ['site', 'property', 'name', 'address'],
            'county': ['county'],
            'acres': ['acres', 'size', 'area'],
            'coordinates': ['lat', 'lon', 'latitude', 'longitude'],
            'rent': ['rent', 'ami', 'revenue'],
            'cost': ['cost', 'construction', 'expense'],
            'economics': ['revenue', 'ratio', 'score', 'economic']
        }
        
        for category, keywords in column_keywords.items():
            found_cols = []
            for col in df.columns:
                if any(keyword.lower() in col.lower() for keyword in keywords):
                    found_cols.append(col)
            if found_cols:
                print(f"\n{category.upper()} columns: {found_cols}")
                key_columns.extend(found_cols[:2])  # Take first 2 from each category
        
        # Show sample data for key columns
        if key_columns:
            sample_cols = key_columns[:8]  # Limit to 8 columns for readability
            print(f"\nSample data for key columns:")
            print(df[sample_cols].head(3).to_string())
        
        # Summary statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print(f"\nSummary statistics for numeric columns:")
            print(df[numeric_cols].describe())
        
        return df, True
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None, False

def identify_pyforma_inputs(df):
    """Identify which columns we can use for pyforma inputs"""
    
    if df is None:
        return
    
    print("\n" + "=" * 80)
    print("PYFORMA INPUT MAPPING")
    print("=" * 80)
    
    # Map to pyforma requirements
    pyforma_mapping = {
        'parcel_size_acres': None,  # Need to convert to sqft
        'county': None,            # For HUD AMI lookup
        'coordinates': [],         # For market analysis
        'existing_revenue': None,   # To compare with pyforma
        'existing_costs': None,     # To compare with pyforma
        'economic_score': None      # Existing economic analysis
    }
    
    # Find relevant columns
    for col in df.columns:
        col_lower = col.lower()
        
        if 'acres' in col_lower and 'parcel' in col_lower:
            pyforma_mapping['parcel_size_acres'] = col
        elif 'county' in col_lower:
            pyforma_mapping['county'] = col
        elif 'lat' in col_lower or 'longitude' in col_lower:
            pyforma_mapping['coordinates'].append(col)
        elif 'revenue' in col_lower and 'ratio' not in col_lower:
            pyforma_mapping['existing_revenue'] = col
        elif 'cost' in col_lower and 'ratio' not in col_lower:
            pyforma_mapping['existing_costs'] = col
        elif 'economic' in col_lower and 'score' in col_lower:
            pyforma_mapping['economic_score'] = col
    
    print("Column mapping for pyforma:")
    for key, value in pyforma_mapping.items():
        print(f"  {key}: {value}")
    
    # Check data availability
    print(f"\nData availability check:")
    required_for_pyforma = ['parcel_size_acres', 'county']
    missing_required = []
    
    for req in required_for_pyforma:
        if pyforma_mapping[req] is None:
            missing_required.append(req)
        else:
            col = pyforma_mapping[req]
            null_count = df[col].isnull().sum()
            print(f"  ✅ {req} ({col}): {len(df) - null_count}/{len(df)} sites have data")
    
    if missing_required:
        print(f"  ❌ Missing required columns: {missing_required}")
    
    return pyforma_mapping

if __name__ == "__main__":
    print("EXAMINING EXISTING 195 SITES DATA")
    print("=" * 80)
    
    df, success = examine_195_sites_data()
    
    if success:
        pyforma_mapping = identify_pyforma_inputs(df)
        print(f"\n🎉 Data examination complete! Ready for pyforma integration.")
    else:
        print(f"❌ Data examination failed.")