#!/usr/bin/env python3
import pandas as pd
import os
import re

def search_woodland_in_excel(file_path):
    """Search for 'Woodland' (case insensitive) in all sheets of an Excel file"""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {os.path.basename(file_path)}")
    print(f"Full path: {file_path}")
    print(f"{'='*80}")
    
    if not os.path.exists(file_path):
        print(f"❌ FILE NOT FOUND: {file_path}")
        return
    
    try:
        # Read all sheets
        xl = pd.ExcelFile(file_path)
        print(f"📋 Found {len(xl.sheet_names)} worksheet(s): {xl.sheet_names}")
        
        found_matches = False
        
        for sheet_name in xl.sheet_names:
            print(f"\n📄 Analyzing sheet: '{sheet_name}'")
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                
                # Search for 'woodland' (case insensitive) in all cells
                sheet_matches = []
                
                for row_idx in range(len(df)):
                    for col_idx, col_name in enumerate(df.columns):
                        cell_value = df.iloc[row_idx, col_idx]
                        if pd.notna(cell_value):
                            cell_str = str(cell_value)
                            if re.search(r'woodland', cell_str, re.IGNORECASE):
                                # Convert to Excel-style cell reference
                                excel_col = chr(65 + col_idx) if col_idx < 26 else chr(64 + col_idx//26) + chr(65 + col_idx%26)
                                excel_row = row_idx + 2  # +2 because pandas is 0-indexed and Excel starts at 1, plus header row
                                cell_ref = f"{excel_col}{excel_row}"
                                
                                match_info = {
                                    'cell_ref': cell_ref,
                                    'column': col_name,
                                    'content': cell_str
                                }
                                sheet_matches.append(match_info)
                
                if sheet_matches:
                    found_matches = True
                    print(f"   🎯 FOUND {len(sheet_matches)} MATCH(ES) containing 'Woodland':")
                    for match in sheet_matches:
                        print(f"      📍 Cell {match['cell_ref']} (Column: {match['column']})")
                        print(f"         Content: {match['content']}")
                        print()
                else:
                    print(f"   ❌ No matches found for 'Woodland' in sheet '{sheet_name}'")
                    
            except Exception as e:
                print(f"   ⚠️ Error reading sheet '{sheet_name}': {str(e)}")
        
        if not found_matches:
            print(f"\n❌ NO MATCHES FOUND for 'Woodland' in entire file: {os.path.basename(file_path)}")
        else:
            print(f"\n✅ MATCHES FOUND in file: {os.path.basename(file_path)}")
            
    except Exception as e:
        print(f"❌ ERROR reading file: {str(e)}")

# File paths to analyze
files_to_search = [
    "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/Priority Sites 7.24.25.xlsx",
    "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/D'Marco_Site_Visit/Crexi Properties based on Brents Logistic Recomendations.xlsx",
    "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/D'Marco_Site_Visit/For Bill Region 9.xlsx"
]

print("🔍 WOODLAND SEARCH ANALYSIS")
print("=" * 80)
print("Searching for 'Woodland' (case insensitive) in Excel files...")

for file_path in files_to_search:
    search_woodland_in_excel(file_path)

print("\n" + "=" * 80)
print("🏁 SEARCH COMPLETE")
print("=" * 80)