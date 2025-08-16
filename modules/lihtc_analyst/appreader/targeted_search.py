#!/usr/bin/env python3
"""
Targeted search for specific fields in Marina Towers
"""

import pandas as pd
import re
from pathlib import Path

def search_total_residential_sqft():
    """Specifically search for 91,612 residential square footage"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    test_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    df = pd.read_excel(test_file, sheet_name="Application", header=None)
    
    print("=== SEARCHING FOR 91,612 RESIDENTIAL SQUARE FOOTAGE ===")
    
    # Search for the specific value 91,612 or variations
    target_values = ['91612', '91,612', '91612.0']
    
    for row in range(len(df)):
        for col in range(len(df.columns)):
            cell_value = str(df.iloc[row, col]) if pd.notna(df.iloc[row, col]) else ""
            
            # Check if this cell contains our target value
            for target in target_values:
                if target in cell_value.replace(',', ''):
                    print(f"Found {target} at Row {row+1}, Col {chr(65+col)}: '{cell_value}'")
                    
                    # Check surrounding context
                    context = []
                    for r_offset in [-2, -1, 0, 1, 2]:
                        for c_offset in [-3, -2, -1, 0, 1, 2, 3]:
                            ctx_row, ctx_col = row + r_offset, col + c_offset
                            if 0 <= ctx_row < len(df) and 0 <= ctx_col < len(df.columns):
                                ctx_value = str(df.iloc[ctx_row, ctx_col]) if pd.notna(df.iloc[ctx_row, ctx_col]) else ""
                                if ctx_value and len(ctx_value) > 2:
                                    context.append(f"R{ctx_row+1}C{chr(65+ctx_col)}: {ctx_value}")
                    
                    print("Context:")
                    for ctx in context[:10]:  # Show first 10 context items
                        print(f"  {ctx}")
                    print()

def search_new_construction_na():
    """Search for N/A in Type of Credit section"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    test_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    df = pd.read_excel(test_file, sheet_name="Application", header=None)
    
    print("=== SEARCHING FOR N/A IN TYPE OF CREDIT SECTION ===")
    
    # First find Type of Credit section
    credit_section_row = None
    for row in range(len(df)):
        for col in range(len(df.columns)):
            cell_value = str(df.iloc[row, col]) if pd.notna(df.iloc[row, col]) else ""
            if "type of credit requested" in cell_value.lower():
                credit_section_row = row
                print(f"Found 'Type of Credit Requested' at Row {row+1}, Col {chr(65+col)}: {cell_value}")
                break
        if credit_section_row:
            break
    
    if credit_section_row:
        # Search in the next 30 rows for N/A
        search_start = credit_section_row
        search_end = min(len(df), credit_section_row + 30)
        
        print(f"\\nSearching rows {search_start+1} to {search_end} for N/A values:")
        
        for row in range(search_start, search_end):
            for col in range(len(df.columns)):
                cell_value = str(df.iloc[row, col]) if pd.notna(df.iloc[row, col]) else ""
                
                if cell_value.strip().upper() in ['N/A', 'NA', 'NOT APPLICABLE']:
                    print(f"Found N/A at Row {row+1}, Col {chr(65+col)}: '{cell_value}'")
                    
                    # Check surrounding context for "new construction"
                    found_new_construction = False
                    context = []
                    for r_offset in [-3, -2, -1, 0, 1, 2, 3]:
                        for c_offset in [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]:
                            ctx_row, ctx_col = row + r_offset, col + c_offset
                            if 0 <= ctx_row < len(df) and 0 <= ctx_col < len(df.columns):
                                ctx_value = str(df.iloc[ctx_row, ctx_col]) if pd.notna(df.iloc[ctx_row, ctx_col]) else ""
                                if "new construction" in ctx_value.lower():
                                    found_new_construction = True
                                if ctx_value and len(ctx_value) > 2:
                                    context.append(f"R{ctx_row+1}C{chr(65+ctx_col)}: {ctx_value}")
                    
                    if found_new_construction:
                        print("  *** FOUND N/A NEAR 'NEW CONSTRUCTION' ***")
                    
                    print("  Context:")
                    for ctx in context[:8]:
                        print(f"    {ctx}")
                    print()

def search_construction_costs():
    """Search for large construction costs"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    test_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    df = pd.read_excel(test_file, sheet_name="Sources and Uses Budget", header=None)
    
    print("=== SEARCHING FOR LARGE CONSTRUCTION COSTS ===")
    
    # Look for values over $10M (since we know it should be substantial)
    large_values = []
    
    for row in range(len(df)):
        for col in range(len(df.columns)):
            cell_value = str(df.iloc[row, col]) if pd.notna(df.iloc[row, col]) else ""
            
            try:
                # Try to extract numeric value
                clean_val = cell_value.replace(',', '').replace('$', '').replace('(', '').replace(')', '')
                if clean_val:
                    num_value = float(clean_val)
                    if num_value > 10000000:  # Over $10M
                        large_values.append({
                            'value': num_value,
                            'location': f"Row {row+1}, Col {chr(65+col)}",
                            'original': cell_value
                        })
            except:
                pass
    
    print(f"Found {len(large_values)} values over $10M:")
    for item in large_values:
        print(f"  ${item['value']:,.0f} at {item['location']} (original: '{item['original']}')")
        
        # Get context for each large value
        row_num = int(item['location'].split(' ')[1]) - 1
        col_num = ord(item['location'].split(' ')[3]) - 65
        
        print("    Context:")
        for r_offset in [-2, -1, 0, 1, 2]:
            for c_offset in [-3, -2, -1, 0, 1, 2]:
                ctx_row, ctx_col = row_num + r_offset, col_num + c_offset
                if 0 <= ctx_row < len(df) and 0 <= ctx_col < len(df.columns):
                    ctx_value = str(df.iloc[ctx_row, ctx_col]) if pd.notna(df.iloc[ctx_row, ctx_col]) else ""
                    if ctx_value and len(ctx_value) > 2 and 'construction' in ctx_value.lower():
                        print(f"      R{ctx_row+1}C{chr(65+ctx_col)}: {ctx_value}")
        print()

def main():
    print("🔍 TARGETED SEARCH FOR MARINA TOWERS MISSING FIELDS")
    print("="*60)
    
    search_total_residential_sqft()
    print("\\n" + "="*60)
    search_new_construction_na()
    print("\\n" + "="*60)
    search_construction_costs()

if __name__ == "__main__":
    main()