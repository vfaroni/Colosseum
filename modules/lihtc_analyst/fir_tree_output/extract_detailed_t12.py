#!/usr/bin/env python3
"""
Extract detailed T12 financial data from Fir Tree Park statement
Period: Jun 2024 - May 2025 (includes 5 months of 2025 actuals)
"""

import pandas as pd
import numpy as np

def extract_detailed_t12():
    """Extract detailed financial data from T12 statement"""
    
    print("🏛️ FIR TREE PARK - DETAILED T12 EXTRACTION")
    print("=" * 50)
    
    t12_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Deals (Good Clean)/Fir_Tree-Shelton_WA/Due_Diligence/FTR - 12 Month Statement - 05.25.xlsx"
    
    try:
        df = pd.read_excel(t12_path, sheet_name='Report1')
        
        # Clean up the dataframe
        df = df.dropna(how='all')
        
        print(f"📅 PERIOD: Jun 2024 - May 2025")
        print(f"📊 2025 YTD: Jan - May 2025 (5 months)")
        print()
        
        # Extract key financial metrics
        financial_data = {}
        
        # Find Total column index
        total_col = None
        for col in df.columns:
            if 'Total' in str(df[col].iloc[3]) or 'total' in str(col).lower():
                total_col = col
                break
        
        if not total_col:
            # Look for last column with data
            total_col = df.columns[-1]
        
        print(f"📈 TOTAL COLUMN: {total_col}")
        
        # Extract 2025 YTD (Jan-May) data
        jan_col = None
        may_col = None
        for col in df.columns:
            header = str(df[col].iloc[3]) if len(df) > 3 else ''
            if 'Jan 2025' in header:
                jan_col = col
            if 'May 2025' in header:
                may_col = col
        
        print(f"📅 2025 Columns: Jan={jan_col}, May={may_col}")
        print()
        
        # Key metrics to extract
        key_metrics = {
            'Total Gross Potential Rent': ['Total Gross Potential Rent', 'gross potential'],
            'Net Rental Income': ['Net Rental Income', 'net rental'],
            'Housing Assistance Payments': ['HAP', 'housing assistance', 'assistance payment'],
            'Total Income': ['Total Income', 'total income'],
            'Total Operating Expenses': ['Total Operating Expenses', 'total operating'],
            'Net Operating Income': ['Net Operating Income', 'NOI', 'net operating'],
            'Management Fees': ['Management', 'management fee', 'professional management'],
            'Utilities': ['Utilities', 'utility'],
            'Insurance': ['Insurance', 'property insurance'],
            'Repairs & Maintenance': ['Repairs', 'maintenance', 'repairs & maintenance']
        }
        
        # Search for metrics in the dataframe
        results = {}
        
        for row_idx, row in df.iterrows():
            first_col_value = str(row.iloc[0]).strip().lower()
            
            for metric_name, keywords in key_metrics.items():
                for keyword in keywords:
                    if keyword.lower() in first_col_value:
                        total_value = row[total_col] if pd.notna(row[total_col]) else 0
                        
                        # Calculate 2025 YTD (Jan-May)
                        ytd_2025 = 0
                        if jan_col and may_col:
                            jan_idx = df.columns.get_loc(jan_col)
                            may_idx = df.columns.get_loc(may_col)
                            for col_idx in range(jan_idx, may_idx + 1):
                                col_name = df.columns[col_idx]
                                val = row[col_name] if pd.notna(row[col_name]) else 0
                                try:
                                    ytd_2025 += float(val)
                                except (ValueError, TypeError):
                                    pass
                        
                        results[metric_name] = {
                            'total_12_months': total_value,
                            'ytd_2025_5_months': ytd_2025,
                            'annualized_2025': ytd_2025 * (12/5) if ytd_2025 else 0
                        }
                        
                        print(f"✅ {metric_name}:")
                        print(f"   12-Month Total: ${total_value:,.0f}")
                        print(f"   2025 YTD (5mo): ${ytd_2025:,.0f}")
                        print(f"   2025 Annualized: ${ytd_2025 * (12/5):,.0f}")
                        print()
                        break
        
        # Generate summary for HTML integration
        print("📋 SUMMARY FOR HTML REPORT:")
        print("="*40)
        
        if 'Total Income' in results and 'Total Operating Expenses' in results:
            income_ann = results['Total Income']['annualized_2025']
            expense_ann = results['Total Operating Expenses']['annualized_2025']
            noi_ann = income_ann - expense_ann
            
            print(f"2025 Annualized Revenue: ${income_ann:,.0f}")
            print(f"2025 Annualized Expenses: ${expense_ann:,.0f}")
            print(f"2025 Annualized NOI: ${noi_ann:,.0f}")
            print()
        
        # Save results for HTML integration
        import json
        with open('/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/lihtc_analyst/fir_tree_output/t12_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print("💾 T12 results saved to: t12_results.json")
        
        return results
        
    except Exception as e:
        print(f"❌ Error extracting detailed T12 data: {e}")
        import traceback
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    extract_detailed_t12()