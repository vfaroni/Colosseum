#!/usr/bin/env python3
"""
Broad search for Pacific Street values with partial matching
"""

import pandas as pd
from pathlib import Path

def search_partial_values(df, target_values, sheet_name):
    """Search for values that are close to targets"""
    print(f"\n=== {sheet_name} Sheet - Searching for Similar Values ===")
    
    for description, target in target_values.items():
        print(f"\nSearching for {description} (target: {target:,})")
        
        found_close = []
        
        for row in range(len(df)):
            for col in range(len(df.columns)):
                cell_value = df.iloc[row, col]
                
                if pd.notna(cell_value):
                    try:
                        # Try to convert to number
                        if isinstance(cell_value, str):
                            clean_val = cell_value.replace(',', '').replace('$', '').replace('(', '').replace(')', '')
                            num_val = float(clean_val)
                        else:
                            num_val = float(cell_value)
                        
                        # Check if it's close to our target (within 10% or exact match)
                        if num_val == target:
                            print(f"  ✅ EXACT: Row {row+1}, Col {col+1}: {cell_value}")
                            print_context(df, row, col)
                        elif target > 1000 and abs(num_val - target) / target < 0.1:  # Within 10%
                            print(f"  🔍 CLOSE: Row {row+1}, Col {col+1}: {cell_value} (diff: {num_val - target:,.0f})")
                        elif target <= 1000 and abs(num_val - target) <= 50:  # Within 50 for small numbers
                            print(f"  🔍 CLOSE: Row {row+1}, Col {col+1}: {cell_value} (diff: {num_val - target:.0f})")
                            
                    except:
                        pass

def search_construction_cost_keywords(df):
    """Search for construction cost related keywords"""
    print(f"\n=== Searching for Construction Cost Keywords ===")
    
    keywords = [
        "Total New Construction", "New Construction Cost", "Construction Cost",
        "Hard Cost", "Construction", "Building Cost"
    ]
    
    for row in range(len(df)):
        for col in range(len(df.columns)):
            cell_value = str(df.iloc[row, col]) if pd.notna(df.iloc[row, col]) else ""
            
            for keyword in keywords:
                if keyword.lower() in cell_value.lower() and len(cell_value) < 100:
                    print(f"  Found '{keyword}' at Row {row+1}, Col {col+1}: {cell_value}")
                    
                    # Check nearby cells for large numbers
                    for r_offset in [-1, 0, 1]:
                        for c_offset in [1, 2, 3, 4]:
                            check_row, check_col = row + r_offset, col + c_offset
                            if 0 <= check_row < len(df) and 0 <= check_col < len(df.columns):
                                check_val = df.iloc[check_row, check_col]
                                if pd.notna(check_val):
                                    try:
                                        if isinstance(check_val, str):
                                            clean_val = check_val.replace(',', '').replace('$', '')
                                            num_val = float(clean_val)
                                        else:
                                            num_val = float(check_val)
                                        
                                        if num_val > 1000000:  # Over $1M
                                            print(f"    -> Large value nearby: R{check_row+1}C{check_col+1}: {check_val:,}")
                                    except:
                                        pass

def print_context(df, row, col):
    """Print context around a cell"""
    print("     Context:")
    for r_offset in [-1, 0, 1]:
        for c_offset in [-2, -1, 0, 1, 2]:
            ctx_row, ctx_col = row + r_offset, col + c_offset
            if 0 <= ctx_row < len(df) and 0 <= ctx_col < len(df.columns):
                ctx_value = df.iloc[ctx_row, ctx_col]
                if pd.notna(ctx_value) and str(ctx_value).strip():
                    marker = ">>>" if r_offset == 0 and c_offset == 0 else "   "
                    print(f"       {marker}R{ctx_row+1}C{ctx_col+1}: {str(ctx_value)[:30]}")

def main():
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    pacific_file = Path(source_dir) / "2024_4pct_R1_24-553.xlsx"
    
    print("🔍 PACIFIC STREET - BROAD SEARCH FOR CORRECT VALUES")
    print("="*70)
    
    # Pacific Street target values
    pacific_targets = {
        "Total Units": 168,
        "Total New Construction Cost": 30129084,
        "Architectural Cost": 294000,
        "Survey & Engineering": 450450,
        "Development Impact Fees": 9817498,
        "Soft Cost Contingency": 360947
    }
    
    # Application sheet
    print("\\n📋 APPLICATION SHEET")
    app_df = pd.read_excel(pacific_file, sheet_name="Application", header=None)
    app_targets = {"Total Units": 168}
    search_partial_values(app_df, app_targets, "Application")
    
    # Sources and Uses Budget sheet
    print("\\n💰 SOURCES AND USES BUDGET SHEET")
    sources_df = pd.read_excel(pacific_file, sheet_name="Sources and Uses Budget", header=None)
    sources_targets = {k: v for k, v in pacific_targets.items() if k != "Total Units"}
    search_partial_values(sources_df, sources_targets, "Sources and Uses Budget")
    
    # Search for construction cost keywords
    search_construction_cost_keywords(sources_df)

if __name__ == "__main__":
    main()