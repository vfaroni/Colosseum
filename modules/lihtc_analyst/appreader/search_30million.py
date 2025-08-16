#!/usr/bin/env python3
"""
Search for the 30 million construction cost value
"""

import pandas as pd
from pathlib import Path

def search_large_values():
    """Search for values around 30 million"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    pacific_file = Path(source_dir) / "2024_4pct_R1_24-553.xlsx"
    
    print("🔍 SEARCHING FOR VALUES AROUND 30 MILLION")
    print("="*50)
    
    sources_df = pd.read_excel(pacific_file, sheet_name="Sources and Uses Budget", header=None)
    
    target = 30129084
    print(f"Target: {target:,}")
    
    # Search for values between 25M and 35M
    found_large = []
    
    for row in range(len(sources_df)):
        for col in range(len(sources_df.columns)):
            cell_value = sources_df.iloc[row, col]
            
            if pd.notna(cell_value):
                try:
                    if isinstance(cell_value, str):
                        clean_val = cell_value.replace(',', '').replace('$', '').replace('(', '').replace(')', '')
                        num_val = float(clean_val)
                    else:
                        num_val = float(cell_value)
                    
                    # Look for values between 25M and 35M
                    if 25000000 <= num_val <= 35000000:
                        found_large.append({
                            'value': num_val,
                            'row': row + 1,
                            'col': col + 1,
                            'original': cell_value
                        })
                        
                        print(f"Found large value: ${num_val:,.0f} at Row {row+1}, Col {col+1}")
                        
                        # Get context
                        print("  Context:")
                        for r_offset in [-2, -1, 0, 1, 2]:
                            for c_offset in [-2, -1, 0, 1, 2]:
                                ctx_row, ctx_col = row + r_offset, col + c_offset
                                if (0 <= ctx_row < len(sources_df) and 0 <= ctx_col < len(sources_df.columns) and
                                    not (r_offset == 0 and c_offset == 0)):
                                    ctx_value = sources_df.iloc[ctx_row, ctx_col]
                                    if pd.notna(ctx_value) and str(ctx_value).strip():
                                        marker = ">>>" if r_offset == 0 and c_offset == 0 else "   "
                                        print(f"    {marker}R{ctx_row+1}C{ctx_col+1}: {str(ctx_value)[:40]}")
                        print()
                        
                except:
                    pass
    
    if not found_large:
        print("No values found between 25M and 35M")
        
        # Try broader search for any value containing parts of our target
        print(f"\nSearching for partial matches to {target}")
        target_str = str(target)
        
        for row in range(len(sources_df)):
            for col in range(len(sources_df.columns)):
                cell_value = str(sources_df.iloc[row, col]) if pd.notna(sources_df.iloc[row, col]) else ""
                
                # Check if cell contains significant digits from our target
                if '30129' in cell_value or '129084' in cell_value:
                    print(f"Partial match at Row {row+1}, Col {col+1}: {cell_value}")

def search_total_project_cost():
    """Search for total project cost line items"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    pacific_file = Path(source_dir) / "2024_4pct_R1_24-553.xlsx"
    
    print("\n🔍 SEARCHING FOR TOTAL PROJECT COST RELATED ITEMS")
    print("="*60)
    
    sources_df = pd.read_excel(pacific_file, sheet_name="Sources and Uses Budget", header=None)
    
    keywords = [
        "Total Project Cost", "Grand Total", "Total Cost", "Project Total",
        "Total Development Cost", "Total Uses", "Total Source"
    ]
    
    for row in range(len(sources_df)):
        for col in range(len(sources_df.columns)):
            cell_value = str(sources_df.iloc[row, col]) if pd.notna(sources_df.iloc[row, col]) else ""
            
            for keyword in keywords:
                if keyword.lower() in cell_value.lower() and len(cell_value) < 100:
                    print(f"Found '{keyword}' at Row {row+1}, Col {col+1}: {cell_value}")
                    
                    # Check nearby cells for large numbers
                    for r_offset in [-1, 0, 1]:
                        for c_offset in [1, 2, 3, 4, 5]:
                            check_row, check_col = row + r_offset, col + c_offset
                            if 0 <= check_row < len(sources_df) and 0 <= check_col < len(sources_df.columns):
                                check_val = sources_df.iloc[check_row, check_col]
                                if pd.notna(check_val):
                                    try:
                                        if isinstance(check_val, str):
                                            clean_val = check_val.replace(',', '').replace('$', '')
                                            num_val = float(clean_val)
                                        else:
                                            num_val = float(check_val)
                                        
                                        if num_val > 10000000:  # Over $10M
                                            print(f"    -> Large value nearby: R{check_row+1}C{check_col+1}: ${num_val:,.0f}")
                                    except:
                                        pass

if __name__ == "__main__":
    search_large_values()
    search_total_project_cost()