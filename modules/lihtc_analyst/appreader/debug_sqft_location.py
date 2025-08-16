#!/usr/bin/env python3
"""
Debug the exact location of 91,612 square footage
"""

import pandas as pd
from pathlib import Path

def debug_sqft_location():
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    test_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    df = pd.read_excel(test_file, sheet_name="Application", header=None)
    
    print("=== DEBUGGING 91,612 LOCATION ===")
    
    # Search for 91612 in the entire sheet
    found_locations = []
    
    for row in range(len(df)):
        for col in range(len(df.columns)):
            cell_value = str(df.iloc[row, col]) if pd.notna(df.iloc[row, col]) else ""
            
            if '91612' in cell_value.replace(',', ''):
                found_locations.append({
                    'row': row,
                    'col': col,
                    'value': cell_value,
                    'location': f"Row {row+1}, Col {chr(65+col)}"
                })
                print(f"Found 91612 at Row {row+1}, Col {chr(65+col)}: '{cell_value}'")
    
    print(f"\\nFound {len(found_locations)} locations with 91612")
    
    # Check each location and its context
    for i, loc in enumerate(found_locations):
        print(f"\\n--- Location {i+1}: {loc['location']} ---")
        print(f"Value: {loc['value']}")
        
        # Get surrounding context (3x3 grid)
        print("Context (3x3 grid):")
        for r_offset in [-1, 0, 1]:
            row_values = []
            for c_offset in [-1, 0, 1]:
                ctx_row = loc['row'] + r_offset
                ctx_col = loc['col'] + c_offset
                
                if 0 <= ctx_row < len(df) and 0 <= ctx_col < len(df.columns):
                    ctx_value = str(df.iloc[ctx_row, ctx_col]) if pd.notna(df.iloc[ctx_row, ctx_col]) else ""
                    if ctx_value:
                        row_values.append(f"{chr(65+ctx_col)}{ctx_row+1}:{ctx_value[:20]}")
                    else:
                        row_values.append(f"{chr(65+ctx_col)}{ctx_row+1}:empty")
                else:
                    row_values.append("---")
            print("  " + " | ".join(row_values))
    
    # Try direct access to the coordinates we found earlier
    print("\\n=== TESTING DIRECT ACCESS ===")
    test_coords = [(441, 0), (442, 0)]  # Row 442-443, Col A
    
    for row, col in test_coords:
        if row < len(df) and col < len(df.columns):
            value = df.iloc[row, col]
            print(f"Row {row+1}, Col {chr(65+col)}: {value} (type: {type(value)})")
        else:
            print(f"Row {row+1}, Col {chr(65+col)}: OUT OF BOUNDS")

if __name__ == "__main__":
    debug_sqft_location()