#!/usr/bin/env python3
"""
Debug field locations in LIHTC applications
"""

import pandas as pd
from pathlib import Path

def debug_application_fields(file_path):
    """Debug specific fields in the Application tab"""
    print(f"\n=== Debugging: {file_path.name} ===")
    
    try:
        df = pd.read_excel(file_path, sheet_name="Application", header=None)
        print(f"Application tab size: {len(df)} rows x {len(df.columns)} columns")
        
        # Project Name
        project_name = df.iloc[17, 7] if len(df) > 17 and len(df.columns) > 7 else "Not found"
        print(f"Project Name (Row 18, Col H): {project_name}")
        
        # Search for county in different areas
        print("\nSearching for County field...")
        county_found = False
        
        # Check rows 180-250 as mentioned in structure analysis
        for row_idx in range(180, min(250, len(df))):
            for col_idx in range(min(30, len(df.columns))):
                cell = str(df.iloc[row_idx, col_idx]) if pd.notna(df.iloc[row_idx, col_idx]) else ""
                if "county" in cell.lower():
                    print(f"  Found 'county' at Row {row_idx+1}, Col {chr(65+col_idx)}: '{cell}'")
                    
                    # Check adjacent cells for value
                    for offset in [1, 2, 3, -1, -2]:
                        if 0 <= col_idx + offset < len(df.columns):
                            adj_cell = df.iloc[row_idx, col_idx + offset]
                            if pd.notna(adj_cell) and not str(adj_cell).endswith(':'):
                                print(f"    Adjacent value (offset {offset}): '{adj_cell}'")
                    
                    # Check cell below
                    if row_idx + 1 < len(df):
                        below_cell = df.iloc[row_idx + 1, col_idx]
                        if pd.notna(below_cell):
                            print(f"    Cell below: '{below_cell}'")
                    
                    county_found = True
        
        if not county_found:
            print("  County field not found in rows 180-250")
            
            # Try broader search
            print("  Searching entire sheet...")
            for row_idx in range(0, min(300, len(df))):
                for col_idx in range(min(30, len(df.columns))):
                    cell = str(df.iloc[row_idx, col_idx]) if pd.notna(df.iloc[row_idx, col_idx]) else ""
                    if "county" in cell.lower() and len(cell) < 50:  # Avoid long text
                        print(f"  Found 'county' at Row {row_idx+1}, Col {chr(65+col_idx)}: '{cell}'")
                        
                        # Check adjacent cells
                        for offset in [1, 2, 3]:
                            if col_idx + offset < len(df.columns):
                                adj_cell = df.iloc[row_idx, col_idx + offset]
                                if pd.notna(adj_cell) and not str(adj_cell).endswith(':') and len(str(adj_cell)) > 2:
                                    print(f"    Potential county value (offset {offset}): '{adj_cell}'")
        
        # Look for city as well
        print("\nSearching for City field...")
        for row_idx in range(150, min(200, len(df))):
            for col_idx in range(min(30, len(df.columns))):
                cell = str(df.iloc[row_idx, col_idx]) if pd.notna(df.iloc[row_idx, col_idx]) else ""
                if "city" in cell.lower() and ":" in cell:
                    print(f"  Found 'city' at Row {row_idx+1}, Col {chr(65+col_idx)}: '{cell}'")
                    
                    # Check adjacent cells
                    for offset in [1, 2, 3]:
                        if col_idx + offset < len(df.columns):
                            adj_cell = df.iloc[row_idx, col_idx + offset]
                            if pd.notna(adj_cell) and not str(adj_cell).endswith(':'):
                                print(f"    City value (offset {offset}): '{adj_cell}'")
                                
    except Exception as e:
        print(f"Error: {e}")

def main():
    source_dir = Path("/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data")
    
    # Test files
    test_files = [
        "2024_4pct_R1_24-409.xlsx",  # Marina Towers
        "2024_4pct_R1_24-408.xlsx",  # Parnow Friendship House
    ]
    
    for filename in test_files:
        file_path = source_dir / filename
        if file_path.exists():
            debug_application_fields(file_path)
        else:
            print(f"File not found: {filename}")

if __name__ == "__main__":
    main()