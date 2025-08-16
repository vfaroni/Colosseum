#!/usr/bin/env python3
import pandas as pd
import os

def examine_excel_content(file_path):
    """Examine the content structure of Excel files to understand what data they contain"""
    print(f"\n{'='*80}")
    print(f"EXAMINING CONTENT: {os.path.basename(file_path)}")
    print(f"{'='*80}")
    
    if not os.path.exists(file_path):
        print(f"❌ FILE NOT FOUND: {file_path}")
        return
    
    try:
        xl = pd.ExcelFile(file_path)
        
        for sheet_name in xl.sheet_names:
            print(f"\n📄 Sheet: '{sheet_name}'")
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                print(f"   Columns: {list(df.columns)}")
                
                # Show first few rows to understand content
                print(f"\n   First 3 rows of data:")
                for idx in range(min(3, len(df))):
                    print(f"   Row {idx + 1}:")
                    for col in df.columns:
                        value = df.iloc[idx][col]
                        if pd.notna(value):
                            print(f"      {col}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
                    print()
                
                # Check for any cells that contain "wood" (broader search)
                wood_matches = []
                for row_idx in range(len(df)):
                    for col_idx, col_name in enumerate(df.columns):
                        cell_value = df.iloc[row_idx, col_idx]
                        if pd.notna(cell_value):
                            cell_str = str(cell_value).lower()
                            if 'wood' in cell_str:
                                excel_col = chr(65 + col_idx) if col_idx < 26 else chr(64 + col_idx//26) + chr(65 + col_idx%26)
                                excel_row = row_idx + 2
                                cell_ref = f"{excel_col}{excel_row}"
                                wood_matches.append({
                                    'cell_ref': cell_ref,
                                    'column': col_name,
                                    'content': str(cell_value)
                                })
                
                if wood_matches:
                    print(f"   🌳 Found {len(wood_matches)} cells containing 'wood':")
                    for match in wood_matches:
                        print(f"      📍 {match['cell_ref']} ({match['column']}): {match['content']}")
                else:
                    print(f"   ❌ No cells containing 'wood' found")
                    
            except Exception as e:
                print(f"   ⚠️ Error reading sheet '{sheet_name}': {str(e)}")
                
    except Exception as e:
        print(f"❌ ERROR reading file: {str(e)}")

# File paths to examine
files_to_examine = [
    "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/Priority Sites 7.24.25.xlsx",
    "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/D'Marco_Site_Visit/Crexi Properties based on Brents Logistic Recomendations.xlsx",
    "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/D'Marco_Site_Visit/For Bill Region 9.xlsx"
]

print("🔍 CONTENT EXAMINATION")
print("=" * 80)

for file_path in files_to_examine:
    examine_excel_content(file_path)

print("\n" + "=" * 80)
print("🏁 EXAMINATION COMPLETE")
print("=" * 80)