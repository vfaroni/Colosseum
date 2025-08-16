#!/usr/bin/env python3
"""
Extract detailed 2025 expense data from T12 statement
Focus on expense categories with seasonal adjustments noted
"""

import pandas as pd
import numpy as np

def extract_t12_expenses():
    """Extract detailed expense breakdown from T12"""
    
    print("🏛️ FIR TREE PARK - 2025 EXPENSE EXTRACTION")
    print("=" * 50)
    
    t12_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Deals (Good Clean)/Fir_Tree-Shelton_WA/Due_Diligence/FTR - 12 Month Statement - 05.25.xlsx"
    
    try:
        df = pd.read_excel(t12_path, sheet_name='Report1')
        
        print(f"📅 PERIOD: Jan 1 - May 31, 2025 (5 months actual)")
        print(f"📊 Annualizing to 12-month projections")
        print()
        
        # Column indices for 2025 data
        jan_col_idx = 9   # Jan 2025  
        may_col_idx = 13  # May 2025
        total_col_idx = -1 # Total column
        
        def extract_expense_data(row_indices, category_name, seasonal_note=""):
            """Extract expense data for specific rows"""
            total_ytd_2025 = 0
            
            for row_idx in row_indices:
                if row_idx < len(df):
                    row = df.iloc[row_idx]
                    
                    # Sum Jan-May 2025
                    for col_idx in range(jan_col_idx, may_col_idx + 1):
                        val = row.iloc[col_idx] if pd.notna(row.iloc[col_idx]) else 0
                        try:
                            total_ytd_2025 += float(val)
                        except (ValueError, TypeError):
                            pass
            
            annualized_2025 = total_ytd_2025 * (12/5) if total_ytd_2025 else 0
            
            return {
                'category': category_name,
                'ytd_2025_5_months': total_ytd_2025,
                'annualized_2025': annualized_2025,
                'seasonal_note': seasonal_note
            }
        
        # Map expense categories to row ranges (based on T12 structure)
        expense_categories = {
            'Administrative': ([27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39], ""),
            'Utilities': ([40, 41, 42, 43, 44, 45], "⚠️ Seasonal - heating costs higher in winter months"),
            'Maintenance': ([46, 47, 48, 49, 50, 51, 52, 53], ""),
            'Management Fees': ([80, 81], ""),
            'Insurance': ([76, 77], "⚠️ May include annual premium payments"),
            'Taxes': ([70, 71, 72, 73], "⚠️ Property taxes typically paid semi-annually")
        }
        
        results = {}
        total_expenses_2025 = 0
        
        print("💸 2025 EXPENSE BREAKDOWN:")
        print("=" * 40)
        
        # Show raw data structure first for verification
        print("📋 T12 Structure Sample (rows 25-85):")
        for idx in range(25, min(85, len(df))):
            row = df.iloc[idx]
            line_item = str(row.iloc[0]) if pd.notna(row.iloc[0]) else 'NaN'
            jan_val = row.iloc[jan_col_idx] if pd.notna(row.iloc[jan_col_idx]) else 0
            may_val = row.iloc[may_col_idx] if pd.notna(row.iloc[may_col_idx]) else 0
            total_val = row.iloc[total_col_idx] if pd.notna(row.iloc[total_col_idx]) else 0
            
            if any([jan_val, may_val, total_val]):  # Only show rows with data
                print(f"Row {idx:2d}: {line_item:<40} | Jan: {jan_val:>8} | May: {may_val:>8} | Total: {total_val:>10}")
        
        # Extract key totals directly
        print(f"\n🎯 KEY EXPENSE TOTALS FROM T12:")
        
        # Total Operating Expenses (row 104 from previous analysis)
        if len(df) > 104:
            total_row = df.iloc[104]
            total_ytd = 0
            for col_idx in range(jan_col_idx, may_col_idx + 1):
                val = total_row.iloc[col_idx] if pd.notna(total_row.iloc[col_idx]) else 0
                try:
                    total_ytd += float(val)
                except:
                    pass
            
            total_annualized = total_ytd * (12/5)
            
            print(f"Total Operating Expenses:")
            print(f"   YTD (Jan-May 2025): ${total_ytd:,.0f}")
            print(f"   Annualized 2025: ${total_annualized:,.0f}")
            print(f"   Per unit/month: ${total_annualized/60/12:,.0f}")
        
        # Generate expense table data for HTML
        expense_html_data = f"""
        <h4>💸 2025 Operating Expense Analysis (Annualized)</h4>
        <div style="background: #fef3c7; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
            <strong>⚠️ IMPORTANT:</strong> 2025 figures are <strong>annualized projections</strong> based on Jan 1 - May 31, 2025 actual data.<br>
            Seasonal expenses (utilities, taxes, insurance) may vary significantly in actual 12-month performance.
        </div>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 35%;">Expense Category</th>
                    <th>2025 Annualized*</th>
                    <th style="width: 10%;">unit/mnth</th>
                    <th>2024 Actual</th>
                    <th style="width: 10%;">unit/mnth</th>
                    <th>$ Change</th>
                    <th>% Revenue</th>
                    <th>Seasonal Notes</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background: #fef2f2; font-weight: bold;">
                    <td><strong>📊 TOTAL EXPENSES</strong></td>
                    <td><strong>${total_annualized:,.0f}</strong></td>
                    <td><strong><span class="per-unit">${total_annualized/60/12:,.0f}</span></strong></td>
                    <td><strong>$438,795</strong></td>
                    <td><strong><span class="per-unit">$609</span></strong></td>
                    <td><strong><span class="positive-change">+${total_annualized-438795:,.0f}</span></strong></td>
                    <td><strong>88.5%</strong></td>
                    <td><strong>See seasonal notes below</strong></td>
                </tr>
            </tbody>
        </table>
        
        <p style="font-size: 0.875rem; color: #64748b; margin-top: 1rem;">
            <strong>*Seasonal Adjustment Notes:</strong><br>
            • <strong>Utilities:</strong> Jan-May includes heating season - summer costs typically lower<br>
            • <strong>Insurance:</strong> May include annual premium payments affecting monthly averages<br>
            • <strong>Property Taxes:</strong> Typically paid semi-annually, timing affects monthly projections<br>
            • <strong>Maintenance:</strong> Exterior work seasonal, emergency repairs unpredictable
        </p>
        """
        
        with open('/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/lihtc_analyst/fir_tree_output/t12_expenses_2025.html', 'w') as f:
            f.write(expense_html_data)
        
        print(f"\n📄 2025 expense analysis saved for HTML integration")
        
        return {
            'total_expenses_ytd': total_ytd,
            'total_expenses_annualized': total_annualized
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    extract_t12_expenses()