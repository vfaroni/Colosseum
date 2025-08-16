#!/usr/bin/env python3
"""
Analysis of value discrepancies between expected and actual values
"""

import pandas as pd
from pathlib import Path

def analyze_discrepancies():
    """Analyze what's actually in the files vs expected values"""
    
    print("🔍 VALUE DISCREPANCY ANALYSIS")
    print("="*80)
    print("Comparing YOUR expected values vs what's ACTUALLY in the Excel files")
    print("="*80)
    
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    
    # MARINA TOWERS ANALYSIS
    print("\\n🏢 MARINA TOWERS (24-409)")
    print("-" * 40)
    
    marina_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    print("YOUR EXPECTED VALUES vs ACTUAL VALUES FOUND:")
    
    # Marina - Check what we actually found
    app_df = pd.read_excel(marina_file, sheet_name="Application", header=None)
    sources_df = pd.read_excel(marina_file, sheet_name="Sources and Uses Budget", header=None)
    
    # Total Units - we found 155 at Row 884, Col 29
    actual_units = app_df.iloc[883, 28]  # 0-indexed
    print(f"Total Units:")
    print(f"  Expected: 155")
    print(f"  Found in file: {actual_units} at Row 884, Col 29")
    print(f"  Status: {'✅ MATCH' if actual_units == 155 else '❌ MISMATCH'}")
    
    # Total Project Structures - you said should be 145,830
    print(f"\\nTotal Project Structures Sq Ft:")
    print(f"  Expected: 145,830")
    
    # Let me find the largest square footage value
    max_sqft = 0
    max_location = ""
    for row in range(len(app_df)):
        for col in range(len(app_df.columns)):
            try:
                val = app_df.iloc[row, col]
                if pd.notna(val) and isinstance(val, (int, float)) and 100000 <= val <= 200000:
                    if val > max_sqft:
                        max_sqft = val
                        max_location = f"Row {row+1}, Col {col+1}"
            except:
                pass
    
    print(f"  Largest sqft value found: {max_sqft:,.0f} at {max_location}")
    print(f"  Status: {'✅ MATCH' if max_sqft == 145830 else '❌ DIFFERENT'}")
    
    # Construction cost - should be $0 for rehab
    construction_cost = sources_df.iloc[37, 1]  # Row 38, Col B
    print(f"\\nTotal New Construction Cost:")
    print(f"  Expected: $0 (rehab project)")
    print(f"  Found in file: ${construction_cost:,.0f} at Row 38, Col B")
    print(f"  Status: {'✅ MATCH' if construction_cost == 0 else '❌ MISMATCH'}")
    
    # Architectural - we found 286,750 at Row 42, Col 2
    arch_cost = sources_df.iloc[41, 1]  # Row 42, Col B
    print(f"\\nTotal Architectural Cost:")
    print(f"  Expected: 286,750")
    print(f"  Found in file: ${arch_cost:,.0f} at Row 42, Col B")
    print(f"  Status: {'✅ MATCH' if arch_cost == 286750 else '❌ MISMATCH'}")
    
    # PACIFIC STREET ANALYSIS
    print("\\n\\n🏢 PACIFIC STREET (24-553)")
    print("-" * 40)
    
    pacific_file = Path(source_dir) / "2024_4pct_R1_24-553.xlsx"
    
    app_df_p = pd.read_excel(pacific_file, sheet_name="Application", header=None)
    sources_df_p = pd.read_excel(pacific_file, sheet_name="Sources and Uses Budget", header=None)
    
    print("YOUR EXPECTED VALUES vs ACTUAL VALUES FOUND:")
    
    # Total Units - you said should be 168
    print(f"Total Units:")
    print(f"  Expected: 168")
    
    # Search for 168 in reasonable unit locations
    found_168 = False
    for row in range(400, 500):  # Likely unit section
        for col in range(25, 35):  # Likely columns
            try:
                val = app_df_p.iloc[row, col]
                if pd.notna(val) and val == 168:
                    print(f"  Found 168 at Row {row+1}, Col {col+1}")
                    found_168 = True
                    break
            except:
                pass
        if found_168:
            break
    
    if not found_168:
        print(f"  168 NOT FOUND in expected unit locations")
    
    # Construction Cost - you said should be 30,129,084
    actual_construction = sources_df_p.iloc[37, 1]  # Row 38, Col B
    print(f"\\nTotal New Construction Cost:")
    print(f"  Expected: $30,129,084")
    print(f"  Found in file: ${actual_construction:,.0f} at Row 38, Col B")
    print(f"  Difference: ${30129084 - actual_construction:,.0f}")
    print(f"  Status: {'✅ MATCH' if actual_construction == 30129084 else '❌ MAJOR DIFFERENCE'}")
    
    # Check total project cost
    total_project = sources_df_p.iloc[104, 1]  # Row 105, Col B
    print(f"\\nTotal Project Cost (Row 105):")
    print(f"  Found in file: ${total_project:,.0f}")
    print(f"  Comparison to your expected construction: ${abs(total_project - 30129084):,.0f} difference")
    
    # Architectural - you said should be 294,000
    actual_arch = sources_df_p.iloc[41, 1]  # Row 42, Col B  
    print(f"\\nTotal Architectural Cost:")
    print(f"  Expected: $294,000")
    print(f"  Found in file: ${actual_arch:,.0f} at Row 42, Col B")
    print(f"  Difference: ${abs(294000 - actual_arch):,.0f}")
    print(f"  Status: {'✅ CLOSE' if abs(actual_arch - 294000) < 50000 else '❌ DIFFERENT'}")
    
    print("\\n" + "="*80)
    print("CONCLUSION:")
    print("="*80)
    print("It appears there are significant discrepancies between your expected")
    print("values and what's actually in the Excel files. This could be due to:")
    print("1. Different versions of the files")
    print("2. Values from different sections/tabs")
    print("3. Calculated vs. raw values")
    print("4. Updated vs. original applications")
    print("\\nI recommend you double-check the source of your expected values.")

if __name__ == "__main__":
    analyze_discrepancies()