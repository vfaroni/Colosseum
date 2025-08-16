#!/usr/bin/env python3
"""
Quick test to find unit mix and rent data in CTCAC files
"""

import pandas as pd

def search_unit_data():
    file_path = '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data/2025_4pct_R1_25-464.xlsx'
    
    print("🔍 SEARCHING FOR UNIT MIX AND RENT DATA")
    print("=" * 50)
    
    # Load Application tab
    app_df = pd.read_excel(file_path, sheet_name='Application', header=None)
    print(f"📊 Application tab size: {app_df.shape}")
    
    # Search for unit and rent related data
    search_terms = ['bedroom', 'unit', 'ami', 'rent', 'gross', 'utility', 'studio', '1 br', '2 br']
    
    matches = []
    for idx in range(min(300, len(app_df))):
        for col in range(min(20, len(app_df.columns))):
            cell_value = str(app_df.iloc[idx, col])
            if cell_value != 'nan' and cell_value != '':
                cell_lower = cell_value.lower()
                if any(term in cell_lower for term in search_terms):
                    matches.append((idx, col, cell_value))
    
    print(f"\n📋 FOUND {len(matches)} POTENTIAL MATCHES:")
    for i, (row, col, value) in enumerate(matches[:25]):
        print(f"Row {row:3d}, Col {col:2d}: {value}")
        if i > 0 and i % 5 == 0:
            print()
    
    # Look for specific unit mix table structure
    print("\n🏠 LOOKING FOR UNIT MIX TABLE STRUCTURE:")
    for idx in range(50, min(200, len(app_df))):
        row_data = app_df.iloc[idx, :10].values
        row_str = ' '.join([str(x) for x in row_data if str(x) != 'nan'])
        if 'bedroom' in row_str.lower() or 'unit' in row_str.lower():
            print(f"Row {idx}: {row_str}")

if __name__ == "__main__":
    search_unit_data()