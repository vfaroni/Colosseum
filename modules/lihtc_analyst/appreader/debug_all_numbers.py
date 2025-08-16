#!/usr/bin/env python3
"""
Debug ALL number extractions to find correct coordinates
"""

import pandas as pd
from pathlib import Path

def debug_specific_values(file_path, target_values, file_description):
    """Debug specific target values in a file"""
    print(f"\n{'='*80}")
    print(f"DEBUGGING {file_description}: {file_path.name}")
    print(f"{'='*80}")
    
    # Search both Application and Sources & Uses Budget sheets
    sheets_to_check = ["Application", "Sources and Uses Budget"]
    
    for sheet_name in sheets_to_check:
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            print(f"\n--- {sheet_name} Sheet ({len(df)} rows x {len(df.columns)} cols) ---")
            
            for target_name, target_value in target_values.items():
                print(f"\nSearching for {target_name}: {target_value}")
                found_locations = []
                
                # Search for the exact value (with and without commas)
                search_values = [
                    str(target_value),
                    str(target_value).replace(',', ''),
                    f"{target_value:,}" if isinstance(target_value, int) else str(target_value)
                ]
                
                for row in range(len(df)):
                    for col in range(len(df.columns)):
                        cell_value = str(df.iloc[row, col]) if pd.notna(df.iloc[row, col]) else ""
                        
                        # Check if cell contains our target value
                        for search_val in search_values:
                            if search_val in cell_value.replace(',', ''):
                                found_locations.append({
                                    'row': row,
                                    'col': col,
                                    'value': cell_value,
                                    'location': f"Row {row+1}, Col {chr(65+col) if col < 26 else f'Col{col}'}"
                                })
                                
                                location_str = f"Row {row+1}, Col {chr(65+col) if col < 26 else f'Col{col}'}"
                                print(f"  Found at {location_str}: '{cell_value}'")
                                
                                # Get context (surrounding cells)
                                print("    Context:")
                                for r_offset in [-1, 0, 1]:
                                    for c_offset in [-2, -1, 0, 1, 2]:
                                        ctx_row, ctx_col = row + r_offset, col + c_offset
                                        if (0 <= ctx_row < len(df) and 0 <= ctx_col < len(df.columns) and 
                                            not (r_offset == 0 and c_offset == 0)):
                                            ctx_value = str(df.iloc[ctx_row, ctx_col]) if pd.notna(df.iloc[ctx_row, ctx_col]) else ""
                                            if ctx_value and len(ctx_value) > 2:
                                                print(f"      R{ctx_row+1}C{ctx_col}: {ctx_value[:50]}")
                                break
                
                if not found_locations:
                    print(f"  ❌ NOT FOUND in {sheet_name}")
        
        except Exception as e:
            print(f"Error reading {sheet_name}: {e}")

def main():
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    
    # Marina Towers - correct values
    marina_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    marina_targets = {
        "Total Units": 155,
        "Total Project Structures Sq Ft": 145830,
        "Total New Construction Cost": 0,  # Should be 0 for rehab
        "Total Architectural Cost": 286750,
        "Total Survey Engineering": 40000,
        "Local Impact Fees": 0,
        "Soft Cost Contingency": 75000
    }
    
    # Pacific Street - correct values you provided
    pacific_file = Path(source_dir) / "2024_4pct_R1_24-553.xlsx"
    pacific_targets = {
        "Total Units": 168,
        "Total Project Structures Sq Ft": 145830,  # You said Marina should be this, checking Pacific too
        "Total New Construction Cost": 30129084,
        "Total Architectural Cost": 294000,
        "Total Survey Engineering": 450450,
        "Development Impact Fees": 9817498,
        "Soft Cost Contingency": 360947
    }
    
    if marina_file.exists():
        debug_specific_values(marina_file, marina_targets, "MARINA TOWERS")
    
    if pacific_file.exists():
        debug_specific_values(pacific_file, pacific_targets, "PACIFIC STREET APARTMENTS")

if __name__ == "__main__":
    main()