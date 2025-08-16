#!/usr/bin/env python3
"""
Find the exact column index for 91612
"""

import pandas as pd
from pathlib import Path

def find_column_index():
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    test_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    df = pd.read_excel(test_file, sheet_name="Application", header=None)
    
    print(f"Total columns: {len(df.columns)}")
    print("Column mapping for columns 20-30:")
    
    # Show column mappings
    for i in range(20, min(35, len(df.columns))):
        col_letter = chr(65 + i) if i < 26 else chr(65 + (i // 26) - 1) + chr(65 + (i % 26))
        print(f"Column {i}: {col_letter}")
    
    # Find 91612 and get its exact column index
    print("\\n=== SEARCHING FOR 91612 ===")
    
    for row in range(440, 445):  # Rows 441-445
        for col in range(len(df.columns)):
            cell_value = df.iloc[row, col]
            if pd.notna(cell_value) and str(cell_value) == '91612':
                col_letter = chr(65 + col) if col < 26 else f"Column{col}"
                print(f"Found 91612 at Row {row+1}, Column {col} ({col_letter}): {cell_value}")
                
                # Test access
                test_value = df.iloc[row, col]
                print(f"Direct access test: {test_value}")
                
                return row, col
    
    return None, None

if __name__ == "__main__":
    find_column_index()