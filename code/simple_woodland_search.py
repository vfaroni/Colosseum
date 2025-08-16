#!/usr/bin/env python3
"""
Simple Woodland Search - Look for any instance of "woodland" and its context
"""

import pandas as pd
import openpyxl
import os
from datetime import datetime

def simple_woodland_search():
    """Simple search for any instance of 'woodland' in the Excel files"""
    
    excel_files = [
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/DMarco_LIHTC_Investment_Opportunities_20250703_172130_Reference.xlsx",
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/DMarco_LIHTC_Investment_Opportunities_20250703_172422_Reference.xlsx",
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/DMarco_Quality_KML_20250703_173814_Reference.xlsx",
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/DMarco_Quality_KML_20250704_095500_Reference.xlsx",
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/DMarco_Quality_KML_20250704_102112_Reference.xlsx",
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/DMarco_Quality_KML_20250704_112036_Reference.xlsx",
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/FINAL_195_Sites_Complete_With_Poverty_20250621_213537.xlsx",
        "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/Enhanced_Anchor_Analysis_With_Priority_Sheets_20250703_001634.xlsx"
    ]
    
    print("SIMPLE WOODLAND SEARCH RESULTS")
    print("=" * 60)
    print(f"Generated: {datetime.now()}")
    print()
    
    all_matches = []
    
    for file_path in excel_files:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        print(f"Searching: {os.path.basename(file_path)}")
        
        try:
            # Get worksheet names
            excel_file = pd.ExcelFile(file_path)
            worksheet_names = excel_file.sheet_names
            
            for sheet_name in worksheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                    df_str = df.astype(str)
                    
                    # Search for 'woodland' in any cell
                    for row_idx in range(len(df_str)):
                        for col_idx in range(len(df_str.columns)):
                            cell_value = df_str.iloc[row_idx, col_idx]
                            
                            if pd.isna(cell_value) or cell_value.strip() == '' or cell_value == 'nan':
                                continue
                                
                            if 'woodland' in cell_value.lower():
                                # Convert to Excel cell reference
                                col_letters = ""
                                col_num = col_idx + 1
                                while col_num > 0:
                                    col_num -= 1
                                    col_letters = chr(col_num % 26 + ord('A')) + col_letters
                                    col_num //= 26
                                cell_ref = f"{col_letters}{row_idx + 1}"
                                
                                match = {
                                    'file': os.path.basename(file_path),
                                    'worksheet': sheet_name,
                                    'cell': cell_ref,
                                    'content': cell_value.strip()
                                }
                                all_matches.append(match)
                                
                except Exception as e:
                    print(f"  Error in worksheet {sheet_name}: {e}")
                    continue
                    
            excel_file.close()
            
        except Exception as e:
            print(f"  Error processing file: {e}")
            continue
    
    print(f"\nTOTAL MATCHES FOUND: {len(all_matches)}")
    print("-" * 60)
    
    # Group matches by type
    hud_metro_matches = []
    other_matches = []
    
    for match in all_matches:
        if 'houston-the woodlands-sugar land' in match['content'].lower() or 'hud metro fmr area' in match['content'].lower():
            hud_metro_matches.append(match)
        else:
            other_matches.append(match)
    
    print(f"\nHUD METRO AREA MATCHES: {len(hud_metro_matches)}")
    if hud_metro_matches:
        print("Sample HUD Metro matches:")
        for match in hud_metro_matches[:3]:
            print(f"  {match['file']} | {match['worksheet']} | {match['cell']} | {match['content'][:80]}...")
    
    print(f"\nOTHER 'WOODLAND' MATCHES: {len(other_matches)}")
    if other_matches:
        print("All other matches:")
        for match in other_matches:
            print(f"  {match['file']} | {match['worksheet']} | {match['cell']} | {match['content']}")
    else:
        print("  No non-HUD Metro woodland matches found")
    
    print("\n" + "=" * 60)
    print("SUMMARY CONCLUSION:")
    if other_matches:
        print(f"Found {len(other_matches)} non-HUD Metro 'woodland' references")
    else:
        print("All 'woodland' references appear to be HUD Metro area geographic designations")
        print("No specific 'Hotel Woodland', 'Woodland Hotel', or related hospitality/development")
        print("references were found in the analyzed Excel files.")
    
    return all_matches

if __name__ == "__main__":
    simple_woodland_search()