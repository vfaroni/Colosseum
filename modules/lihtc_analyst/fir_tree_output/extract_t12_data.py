#!/usr/bin/env python3
"""
Extract T12 actual data from Fir Tree Park 5-month statement
This will give us 2025 YTD data to include in the analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime

def extract_t12_data():
    """Extract and analyze T12 data from the Excel file"""
    
    print("🏛️ FIR TREE PARK - T12 DATA EXTRACTION")
    print("=" * 50)
    
    t12_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Deals (Good Clean)/Fir_Tree-Shelton_WA/Due_Diligence/FTR - 12 Month Statement - 05.25.xlsx"
    
    try:
        # Read Excel file - try different sheet names
        xl_file = pd.ExcelFile(t12_path)
        print(f"📊 Available sheets: {xl_file.sheet_names}")
        
        # Try to find the main financial sheet
        for sheet_name in xl_file.sheet_names:
            print(f"\n📋 Reading sheet: '{sheet_name}'")
            try:
                df = pd.read_excel(t12_path, sheet_name=sheet_name)
                print(f"   Dimensions: {df.shape}")
                print(f"   Columns: {list(df.columns)}")
                
                # Display first few rows to understand structure
                print(f"\n📝 Sample data from '{sheet_name}':")
                print(df.head(10).to_string())
                print("\n" + "="*80)
                
            except Exception as e:
                print(f"   ❌ Error reading sheet: {e}")
                continue
        
        # Try to extract financial data from the most likely sheet
        main_sheet = xl_file.sheet_names[0] if xl_file.sheet_names else None
        
        if main_sheet:
            print(f"\n🔍 ANALYZING MAIN SHEET: {main_sheet}")
            df = pd.read_excel(t12_path, sheet_name=main_sheet)
            
            # Look for revenue and expense patterns
            revenue_keywords = ['rental', 'income', 'revenue', 'hap', 'assistance', 'gross']
            expense_keywords = ['expense', 'admin', 'utility', 'maintenance', 'insurance', 'management']
            
            # Search for financial line items
            financial_data = {}
            
            for idx, row in df.iterrows():
                for col in df.columns:
                    cell_value = str(row[col]).lower()
                    
                    # Look for revenue items
                    for keyword in revenue_keywords:
                        if keyword in cell_value and any(str(val).replace(',', '').replace('$', '').replace('-', '').replace('(', '').replace(')', '').strip().isdigit() for val in row.values if pd.notna(val)):
                            print(f"💰 Found revenue item: {cell_value} in row {idx}")
                            
                    # Look for expense items  
                    for keyword in expense_keywords:
                        if keyword in cell_value and any(str(val).replace(',', '').replace('$', '').replace('-', '').replace('(', '').replace(')', '').strip().isdigit() for val in row.values if pd.notna(val)):
                            print(f"💸 Found expense item: {cell_value} in row {idx}")
            
            # Generate summary
            print(f"\n📈 T12 DATA ANALYSIS COMPLETE")
            print(f"   File: {t12_path}")
            print(f"   Date: May 2025 (5 months YTD)")
            print(f"   Sheets analyzed: {len(xl_file.sheet_names)}")
            
    except Exception as e:
        print(f"❌ Error extracting T12 data: {e}")

if __name__ == "__main__":
    extract_t12_data()