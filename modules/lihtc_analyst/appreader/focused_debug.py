#!/usr/bin/env python3
"""
Focused debug for specific correct values
"""

import pandas as pd
from pathlib import Path

def search_exact_value(df, target_value, sheet_name, description):
    """Search for exact value in dataframe"""
    print(f"\n=== Searching for {description}: {target_value:,} ===")
    
    found_any = False
    
    for row in range(len(df)):
        for col in range(len(df.columns)):
            cell_value = df.iloc[row, col]
            
            # Try different comparisons
            if pd.notna(cell_value):
                # Direct numeric comparison
                try:
                    if isinstance(cell_value, (int, float)) and int(cell_value) == target_value:
                        print(f"✅ EXACT MATCH at Row {row+1}, Col {col+1}: {cell_value}")
                        print_context(df, row, col)
                        found_any = True
                        continue
                except:
                    pass
                
                # String comparison (remove commas)
                cell_str = str(cell_value).replace(',', '').replace('$', '').strip()
                if cell_str == str(target_value):
                    print(f"✅ STRING MATCH at Row {row+1}, Col {col+1}: {cell_value}")
                    print_context(df, row, col)
                    found_any = True
                    continue
    
    if not found_any:
        print(f"❌ {description} NOT FOUND")

def print_context(df, row, col):
    """Print context around a cell"""
    print("   Context:")
    for r_offset in [-1, 0, 1]:
        row_str = ""
        for c_offset in [-2, -1, 0, 1, 2]:
            ctx_row, ctx_col = row + r_offset, col + c_offset
            if 0 <= ctx_row < len(df) and 0 <= ctx_col < len(df.columns):
                ctx_value = df.iloc[ctx_row, ctx_col]
                if pd.notna(ctx_value):
                    marker = ">>>" if r_offset == 0 and c_offset == 0 else "   "
                    row_str += f"{marker}R{ctx_row+1}C{ctx_col+1}:{str(ctx_value)[:20]:<20} "
        if row_str.strip():
            print(f"     {row_str}")

def debug_marina_towers():
    """Debug Marina Towers with correct values"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    marina_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    print("🏢 MARINA TOWERS - FINDING CORRECT VALUES")
    print("="*60)
    
    # Application sheet
    app_df = pd.read_excel(marina_file, sheet_name="Application", header=None)
    
    # We know 155 units is correct - find the right 155
    search_exact_value(app_df, 155, "Application", "Total Units (155)")
    
    # We know 145,830 total project sq ft is correct
    search_exact_value(app_df, 145830, "Application", "Total Project Structures Sq Ft")
    
    # Sources and Uses Budget sheet  
    sources_df = pd.read_excel(marina_file, sheet_name="Sources and Uses Budget", header=None)
    
    # Look for the architectural cost we know is right: 286,750
    search_exact_value(sources_df, 286750, "Sources and Uses", "Architectural Cost")
    
    # Look for survey/engineering: 40,000
    search_exact_value(sources_df, 40000, "Sources and Uses", "Survey & Engineering")
    
    # Look for soft cost contingency: 75,000
    search_exact_value(sources_df, 75000, "Sources and Uses", "Soft Cost Contingency")

def debug_pacific_street():
    """Debug Pacific Street with correct values"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    pacific_file = Path(source_dir) / "2024_4pct_R1_24-553.xlsx"
    
    print(f"\n\n🏢 PACIFIC STREET - FINDING CORRECT VALUES")
    print("="*60)
    
    # Application sheet
    app_df = pd.read_excel(pacific_file, sheet_name="Application", header=None)
    
    # Look for 168 units
    search_exact_value(app_df, 168, "Application", "Total Units (168)")
    
    # Sources and Uses Budget sheet
    sources_df = pd.read_excel(pacific_file, sheet_name="Sources and Uses Budget", header=None)
    
    # Look for the values you specified
    search_exact_value(sources_df, 30129084, "Sources and Uses", "Total New Construction Cost")
    search_exact_value(sources_df, 294000, "Sources and Uses", "Architectural Cost")
    search_exact_value(sources_df, 450450, "Sources and Uses", "Survey & Engineering")
    search_exact_value(sources_df, 9817498, "Sources and Uses", "Development Impact Fees")
    search_exact_value(sources_df, 360947, "Sources and Uses", "Soft Cost Contingency")

def main():
    debug_marina_towers()
    debug_pacific_street()

if __name__ == "__main__":
    main()