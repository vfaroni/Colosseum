#!/usr/bin/env python3
"""
Search all CoStar files for 9481 Marbach Rd
"""

import pandas as pd
from pathlib import Path
import re

def search_costar_files():
    # Major CoStar files to check
    costar_files = [
        # Original Texas exports
        "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/Costar_07312025/CS_Costar_TX_Land_8ac-30ac_07312025_ALL-export.xlsx",
        
        # Analysis results
        "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/Analysis_Results/CoStar_375_COMPLETE_4Dataset_FINAL_20250731_223132.xlsx",
        "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/Analysis_Results/CoStar_375_QCT_DDA_ELIGIBLE_Sites_20250731_185133.xlsx",
        
        # Combined exports
        "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport_AllLand_Combined_20250727_184937.xlsx",
        "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/botn_engine/Sites/Combined_CostarExport_Final.xlsx",
        
        # Individual exports
        "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport-8.xlsx",
        "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport-9.xlsx",
        "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport-10.xlsx",
        "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport-11.xlsx",
        "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport-12.xlsx",
        "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport-13.xlsx",
        "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport-14.xlsx",
        "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport-15.xlsx",
    ]
    
    print("🔍 SEARCHING ALL COSTAR FILES FOR 9481 MARBACH RD")
    print("=" * 60)
    
    found_in_files = []
    search_patterns = [
        r'9481.*[Mm]arbach',
        r'[Mm]arbach.*9481',
        r'9481\s*[Mm]arbach',
        r'[Mm]arbach\s*9481'
    ]
    
    for file_path in costar_files:
        file_obj = Path(file_path)
        if not file_obj.exists():
            print(f"⚠️  File not found: {file_obj.name}")
            continue
            
        try:
            print(f"\n📂 Searching: {file_obj.name}")
            df = pd.read_excel(file_path)
            print(f"   Records: {len(df)}")
            
            # Check all text columns for the address
            text_columns = df.select_dtypes(include=['object']).columns
            
            found_matches = []
            for col in text_columns:
                for idx, value in df[col].items():
                    if pd.notna(value):
                        value_str = str(value)
                        for pattern in search_patterns:
                            if re.search(pattern, value_str, re.IGNORECASE):
                                found_matches.append({
                                    'row': idx,
                                    'column': col,
                                    'value': value_str,
                                    'pattern_matched': pattern
                                })
            
            if found_matches:
                print(f"   ✅ FOUND {len(found_matches)} MATCHES!")
                found_in_files.append({
                    'file': file_path,
                    'matches': found_matches
                })
                
                for match in found_matches:
                    print(f"      Row {match['row']:3d} | {match['column']:<20} | {match['value'][:60]}")
                    
                    # Get full row data for context
                    full_row = df.iloc[match['row']]
                    print(f"      Full row data:")
                    for col_name, col_value in full_row.items():
                        if pd.notna(col_value) and str(col_value).strip():
                            print(f"         {col_name}: {col_value}")
                    print()
            else:
                print(f"   ❌ No matches found")
                
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
            continue
    
    # Summary
    print(f"\n📊 SEARCH SUMMARY:")
    print(f"Files searched: {len([f for f in costar_files if Path(f).exists()])}")
    print(f"Files with matches: {len(found_in_files)}")
    
    if found_in_files:
        print(f"\n🎯 MATCHES FOUND IN:")
        for result in found_in_files:
            file_name = Path(result['file']).name
            print(f"   • {file_name}: {len(result['matches'])} matches")
    else:
        print(f"\n❌ NO MATCHES FOUND")
        print(f"The 9481 Marbach Rd site does not appear to be in our CoStar datasets")
        print(f"This suggests it may be:")
        print(f"   • A new listing not captured in our exports")
        print(f"   • Listed after our data collection dates")
        print(f"   • Not meeting our search criteria (size, price, etc.)")

if __name__ == "__main__":
    search_costar_files()