#!/usr/bin/env python3
"""
Detailed Analysis of the 6 "The Woodlands" matches found
"""

import pandas as pd
import os
from datetime import datetime

def analyze_specific_woodland_matches():
    """Analyze the 6 specific 'The Woodlands' matches in detail"""
    
    matches_to_analyze = [
        {
            'file': '/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/FINAL_195_Sites_Complete_With_Poverty_20250621_213537.xlsx',
            'worksheet': 'All_195_Sites_Final',
            'cell': 'AI63'
        },
        {
            'file': '/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/FINAL_195_Sites_Complete_With_Poverty_20250621_213537.xlsx',
            'worksheet': 'Poverty_Very_Low',
            'cell': 'AI27'
        },
        {
            'file': '/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/FINAL_195_Sites_Complete_With_Poverty_20250621_213537.xlsx',
            'worksheet': 'Low_Poverty_Bonus_9pct',
            'cell': 'AI50'
        },
        {
            'file': '/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/FINAL_195_Sites_Complete_With_Poverty_20250621_213537.xlsx',
            'worksheet': 'Final_9pct_Exceptional',
            'cell': 'AI28'
        },
        {
            'file': '/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/Enhanced_Anchor_Analysis_With_Priority_Sheets_20250703_001634.xlsx',
            'worksheet': 'All_Sites_Enhanced_Ranking',
            'cell': 'AI187'
        },
        {
            'file': '/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/priorcode/Enhanced_Anchor_Analysis_With_Priority_Sheets_20250703_001634.xlsx',
            'worksheet': 'Fatal_Isolated_Sites',
            'cell': 'AI10'
        }
    ]
    
    print("DETAILED ANALYSIS OF 'THE WOODLANDS' MATCHES")
    print("=" * 80)
    print(f"Generated: {datetime.now()}")
    print()
    
    def cell_ref_to_indices(cell_ref):
        """Convert Excel cell reference (like AI63) to row/column indices"""
        col_str = ""
        row_str = ""
        
        for char in cell_ref:
            if char.isalpha():
                col_str += char
            else:
                row_str += char
        
        # Convert column letters to index
        col_idx = 0
        for char in col_str:
            col_idx = col_idx * 26 + (ord(char.upper()) - ord('A') + 1)
        col_idx -= 1  # Convert to 0-based
        
        row_idx = int(row_str) - 1  # Convert to 0-based
        
        return row_idx, col_idx
    
    for i, match in enumerate(matches_to_analyze, 1):
        print(f"\n📍 MATCH #{i}")
        print(f"File: {os.path.basename(match['file'])}")
        print(f"Worksheet: {match['worksheet']}")
        print(f"Cell: {match['cell']}")
        
        try:
            df = pd.read_excel(match['file'], sheet_name=match['worksheet'], header=None)
            row_idx, col_idx = cell_ref_to_indices(match['cell'])
            
            # Get the specific cell value
            cell_value = df.iloc[row_idx, col_idx]
            print(f"Cell Content: '{cell_value}'")
            
            # Get the entire row for context
            print(f"\nFULL ROW {row_idx + 1} CONTEXT:")
            row_data = []
            for c in range(len(df.columns)):
                val = df.iloc[row_idx, c]
                if not pd.isna(val) and str(val).strip() != '' and str(val).strip() != 'nan':
                    # Convert column index back to Excel column
                    col_letters = ""
                    col_num = c + 1
                    while col_num > 0:
                        col_num -= 1
                        col_letters = chr(col_num % 26 + ord('A')) + col_letters
                        col_num //= 26
                    
                    row_data.append(f"{col_letters}{row_idx + 1}: {str(val).strip()}")
            
            # Print row data in chunks for readability
            for j in range(0, len(row_data), 5):
                chunk = row_data[j:j+5]
                print("  " + " | ".join(chunk))
            
            # Get column header context (first few rows of the same column)
            print(f"\nCOLUMN {match['cell'][:-len(str(row_idx + 1))]} CONTEXT (first 5 rows):")
            for r in range(min(5, len(df))):
                val = df.iloc[r, col_idx]
                if not pd.isna(val) and str(val).strip() != '' and str(val).strip() != 'nan':
                    print(f"  Row {r+1}: {str(val).strip()}")
            
            # Look for nearby relevant data in surrounding cells
            print(f"\nSURROUNDING AREA CONTEXT:")
            for r in range(max(0, row_idx - 2), min(len(df), row_idx + 3)):
                for c in range(max(0, col_idx - 3), min(len(df.columns), col_idx + 4)):
                    val = df.iloc[r, c]
                    if not pd.isna(val) and str(val).strip() != '' and str(val).strip() != 'nan':
                        # Convert to Excel reference
                        col_letters = ""
                        col_num = c + 1
                        while col_num > 0:
                            col_num -= 1
                            col_letters = chr(col_num % 26 + ord('A')) + col_letters
                            col_num //= 26
                        
                        cell_ref = f"{col_letters}{r + 1}"
                        val_str = str(val).strip()
                        
                        # Highlight if it contains key terms
                        highlight = ""
                        if any(term in val_str.lower() for term in ['hotel', 'inn', 'resort', 'development', 'property', 'project', 'investment', 'llc', 'lp', 'corp']):
                            highlight = " ⭐"
                        
                        print(f"  {cell_ref}: {val_str}{highlight}")
            
            print("-" * 80)
            
        except Exception as e:
            print(f"Error analyzing match: {e}")
            print("-" * 80)
    
    print("\n🔍 ANALYSIS SUMMARY:")
    print("The 6 'The Woodlands' references appear to be:")
    print("1. Geographic location identifiers in LIHTC site analysis data")
    print("2. Part of site location/city information for development properties")
    print("3. NOT references to 'Hotel Woodland' or 'Woodland Hotel'")
    print("4. Likely referring to The Woodlands, Texas - a planned community near Houston")

if __name__ == "__main__":
    analyze_specific_woodland_matches()