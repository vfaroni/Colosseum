#!/usr/bin/env python3
"""
Extract specific financial line items from Fir Tree T12
Focus on the exact line items we need for the HTML report
"""

import pandas as pd
import numpy as np

def extract_specific_t12():
    """Extract specific financial metrics from T12"""
    
    print("🏛️ FIR TREE PARK - SPECIFIC T12 LINE ITEMS")
    print("=" * 50)
    
    t12_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Deals (Good Clean)/Fir_Tree-Shelton_WA/Due_Diligence/FTR - 12 Month Statement - 05.25.xlsx"
    
    try:
        df = pd.read_excel(t12_path, sheet_name='Report1')
        
        print(f"📅 PERIOD: Jun 2024 - May 2025")
        print(f"📊 2025 YTD: Jan - May 2025 (5 months)")
        print()
        
        # Show the structure first
        print("📋 DATAFRAME STRUCTURE:")
        for idx in range(min(30, len(df))):
            row = df.iloc[idx]
            line_item = str(row.iloc[0]) if pd.notna(row.iloc[0]) else 'NaN'
            total_val = str(row.iloc[-1]) if pd.notna(row.iloc[-1]) else 'NaN'
            print(f"Row {idx:2d}: {line_item:<40} | Total: {total_val}")
        print()
        
        # Calculate 2025 YTD for specific rows
        jan_col_idx = 9  # Jan 2025
        may_col_idx = 13  # May 2025
        total_col_idx = -1  # Last column
        
        def extract_row_data(row_idx):
            """Extract data from a specific row"""
            if row_idx >= len(df):
                return None
                
            row = df.iloc[row_idx]
            
            # Get total
            total = row.iloc[total_col_idx] if pd.notna(row.iloc[total_col_idx]) else 0
            
            # Calculate 2025 YTD (Jan-May)
            ytd_2025 = 0
            for col_idx in range(jan_col_idx, may_col_idx + 1):
                val = row.iloc[col_idx] if pd.notna(row.iloc[col_idx]) else 0
                try:
                    ytd_2025 += float(val)
                except (ValueError, TypeError):
                    pass
            
            annualized_2025 = ytd_2025 * (12/5) if ytd_2025 else 0
            
            return {
                'total_12_months': float(total) if total and str(total).replace('-','').replace(',','').replace('$','').replace(' ','').replace('(','').replace(')','').replace('.','').isdigit() else 0,
                'ytd_2025_5_months': ytd_2025,
                'annualized_2025': annualized_2025
            }
        
        # Key rows based on the output structure
        key_rows = {
            'Gross Potential Rent': 8,  # Total Gross Potential Rent
            'Net Rental Income': 15,    # Net Rental Income  
            'Total Income': 24,         # Total Income
            'Total Operating Expenses': 104,  # Total Operating Expenses
            'Net Operating Income': 106,      # Net Operating Income
        }
        
        results = {}
        print("💰 EXTRACTED FINANCIAL DATA:")
        print("="*40)
        
        for metric_name, row_idx in key_rows.items():
            data = extract_row_data(row_idx)
            if data:
                results[metric_name] = data
                print(f"{metric_name}:")
                print(f"   12-Month Total: ${data['total_12_months']:,.0f}")
                print(f"   2025 YTD (5mo): ${data['ytd_2025_5_months']:,.0f}")  
                print(f"   2025 Annualized: ${data['annualized_2025']:,.0f}")
                print()
        
        # Generate HTML-ready summary
        if results:
            print("📊 HTML INTEGRATION DATA:")
            print("="*30)
            
            # Revenue data
            if 'Total Income' in results:
                income_data = results['Total Income']
                print(f"2025 Total Revenue (Annualized): ${income_data['annualized_2025']:,.0f}")
                print(f"2025 YTD Revenue (5 months): ${income_data['ytd_2025_5_months']:,.0f}")
            
            # NOI data  
            if 'Net Operating Income' in results:
                noi_data = results['Net Operating Income']
                print(f"2025 NOI (Annualized): ${noi_data['annualized_2025']:,.0f}")
                print(f"2025 YTD NOI (5 months): ${noi_data['ytd_2025_5_months']:,.0f}")
            
            # Calculate per unit monthly figures
            units = 60
            if 'Total Income' in results:
                monthly_income_per_unit = results['Total Income']['annualized_2025'] / 12 / units
                print(f"2025 Revenue per unit/month: ${monthly_income_per_unit:.0f}")
            
            if 'Net Operating Income' in results:
                monthly_noi_per_unit = results['Net Operating Income']['annualized_2025'] / 12 / units
                print(f"2025 NOI per unit/month: ${monthly_noi_per_unit:.0f}")
        
        # Save results
        import json
        with open('/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/lihtc_analyst/fir_tree_output/t12_final_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    extract_specific_t12()