#!/usr/bin/env python3
"""
Extract and analyze key data from BOTN Workforce Housing Underwriting Template
Focus on understanding the model structure and calculations
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

def analyze_botn_template():
    """Main analysis function"""
    template_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Workforce_Housing/BOTN_Proformas/Workforce BOTN 05.12.25.xlsx'
    
    print("=== BOTN WORKFORCE HOUSING UNDERWRITING TEMPLATE ANALYSIS ===\n")
    
    # Load key sheets
    try:
        # Load Inputs sheet
        inputs_df = pd.read_excel(template_path, sheet_name='Inputs', header=None)
        print("INPUTS SHEET STRUCTURE:")
        print(f"Dimensions: {inputs_df.shape[0]} rows x {inputs_df.shape[1]} columns\n")
        
        # Extract key input parameters
        print("KEY INPUT PARAMETERS:")
        for i in range(min(20, len(inputs_df))):
            row = inputs_df.iloc[i]
            if pd.notna(row[0]) and pd.notna(row[1]):
                print(f"  {row[0]}: {row[1]}")
        
        # Load Output sheet
        print("\n\nOUTPUT SHEET ANALYSIS:")
        output_df = pd.read_excel(template_path, sheet_name='Output', header=None)
        print(f"Dimensions: {output_df.shape[0]} rows x {output_df.shape[1]} columns\n")
        
        # Find rows with calculations (multiple numeric values)
        print("IDENTIFIED CALCULATION SECTIONS:")
        calc_rows = []
        for i in range(len(output_df)):
            row = output_df.iloc[i]
            numeric_count = sum(1 for val in row[1:15] if pd.notna(val) and isinstance(val, (int, float)))
            if numeric_count >= 3 and pd.notna(row[0]):
                label = str(row[0]).strip()
                calc_rows.append((i, label, numeric_count))
                if len(calc_rows) <= 20:
                    print(f"  Row {i}: {label} ({numeric_count} numeric values)")
        
        # Analyze FMR data structure
        print("\n\nFAIR MARKET RENT DATA ANALYSIS:")
        fmr_df = pd.read_excel(template_path, sheet_name='FY25_FMRs', header=1)
        print(f"FMR Data: {len(fmr_df)} counties/areas")
        
        # Get column names
        print("FMR Columns:", list(fmr_df.columns)[:15])
        
        # Sample FMR data
        print("\nSample FMR Data (first 5 rows):")
        print(fmr_df.head().to_string(max_cols=8))
        
        # Analyze SAFMR data
        print("\n\nSMALL AREA FMR ANALYSIS:")
        safmr_df = pd.read_excel(template_path, sheet_name='SAFMRs')
        print(f"SAFMR Data: {len(safmr_df)} ZIP codes")
        print("SAFMR Columns:", list(safmr_df.columns)[:10])
        
        # Counties data
        print("\n\nCOUNTIES DATA ANALYSIS:")
        counties_df = pd.read_excel(template_path, sheet_name='Counties', header=1)
        print(f"Counties: {len(counties_df)} entries")
        
        # Extract county-specific data
        if len(counties_df) > 0:
            print("\nSample County Data:")
            for i in range(min(5, len(counties_df))):
                row = counties_df.iloc[i]
                if pd.notna(row[0]):
                    print(f"  {row[0]}")
        
        # Create summary
        print("\n\n=== MODEL SUMMARY ===")
        print("This appears to be a comprehensive workforce housing underwriting model that:")
        print("1. Takes property inputs (location, unit mix, financing terms)")
        print("2. Integrates HUD Fair Market Rent data at multiple geographic levels:")
        print("   - County-level FMRs")
        print("   - ZIP code-level Small Area FMRs")
        print("   - Section 8 payment standards")
        print("3. Calculates financial projections based on:")
        print("   - Affordable housing rent limits (LIHTC, Section 8, etc.)")
        print("   - Unit mix and bedroom distribution")
        print("   - Market-specific rent data")
        print("4. Supports analysis for California and Texas markets")
        
        # Save extracted data
        output_dir = Path(template_path).parent
        
        # Export key data to CSV for further analysis
        print("\n\nEXPORTING KEY DATA:")
        
        # Export calculation rows
        calc_df = pd.DataFrame(calc_rows, columns=['Row', 'Label', 'NumericValues'])
        calc_path = output_dir / 'BOTN_Calculations_Identified.csv'
        calc_df.to_csv(calc_path, index=False)
        print(f"  Saved calculation rows to: {calc_path}")
        
        # Export input parameters
        inputs_list = []
        for i in range(len(inputs_df)):
            row = inputs_df.iloc[i]
            if pd.notna(row[0]) and pd.notna(row[1]):
                inputs_list.append({
                    'Parameter': str(row[0]),
                    'Value': str(row[1])
                })
        
        if inputs_list:
            inputs_export = pd.DataFrame(inputs_list)
            inputs_path = output_dir / 'BOTN_Input_Parameters.csv'
            inputs_export.to_csv(inputs_path, index=False)
            print(f"  Saved input parameters to: {inputs_path}")
        
        print("\n=== ANALYSIS COMPLETE ===")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_botn_template()