#!/usr/bin/env python3
"""
Extract all Excel financial data from Fir Tree Park
Save to JSON and Markdown for Credit Committee Report
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import numpy as np

# Base directory
BASE_DIR = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Deals (Good Clean)/Fir_Tree-Shelton_WA/Due_Diligence")
OUTPUT_DIR = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/lihtc_analyst/fir_tree_output")

def extract_excel_files():
    """Extract all Excel files and save to JSON/MD"""
    
    excel_files = [
        "1736071 fi p211 Annual Budget (final).xlsx",
        "FTR - 12 Month Statement - 05.25.xlsx",
        "Fir Tree Trial Balance 1.2025 - 3.2025.xlsx",
        "Aging Detail Report 06_16_2025.xlsx",
        "Fir Tree Occupancy Report -06262024.xlsx"
    ]
    
    all_data = {}
    
    for file_name in excel_files:
        file_path = BASE_DIR / file_name
        
        if file_path.exists():
            print(f"\n📊 Processing: {file_name}")
            print("-" * 50)
            
            try:
                # Read all sheets
                excel_file = pd.ExcelFile(file_path)
                sheets_data = {}
                
                for sheet_name in excel_file.sheet_names:
                    print(f"  Reading sheet: {sheet_name}")
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    # Convert to JSON-serializable format
                    # Replace NaN with None for JSON
                    df = df.replace({np.nan: None})
                    
                    # Store both as dict and summary stats
                    sheets_data[sheet_name] = {
                        "shape": df.shape,
                        "columns": list(df.columns),
                        "data": df.to_dict('records'),
                        "summary": {
                            "rows": len(df),
                            "cols": len(df.columns),
                            "numeric_cols": list(df.select_dtypes(include=['number']).columns)
                        }
                    }
                    
                    # Print summary
                    print(f"    Shape: {df.shape}")
                    print(f"    Columns: {', '.join(df.columns[:5])}..." if len(df.columns) > 5 else f"    Columns: {', '.join(df.columns)}")
                    
                    # Look for key financial data
                    if any(col for col in df.columns if 'total' in str(col).lower() or 'revenue' in str(col).lower()):
                        print(f"    💰 Found financial columns!")
                
                all_data[file_name] = sheets_data
                
            except Exception as e:
                print(f"  ❌ Error processing {file_name}: {e}")
                all_data[file_name] = {"error": str(e)}
        else:
            print(f"  ⚠️ File not found: {file_name}")
            all_data[file_name] = {"error": "File not found"}
    
    # Save to JSON
    json_output = OUTPUT_DIR / "excel_financial_data.json"
    with open(json_output, 'w') as f:
        json.dump(all_data, f, indent=2, default=str)
    print(f"\n✅ Saved JSON to: {json_output}")
    
    # Create summary markdown
    create_summary_markdown(all_data)
    
    return all_data

def create_summary_markdown(data):
    """Create markdown summary of Excel data"""
    
    md_content = """# FIR TREE PARK - EXCEL DATA EXTRACTION SUMMARY
**Extraction Date**: {date}
**Files Processed**: {file_count}

## FILES OVERVIEW

""".format(
        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        file_count=len(data)
    )
    
    for file_name, file_data in data.items():
        md_content += f"\n### 📊 {file_name}\n"
        
        if isinstance(file_data, dict) and "error" not in file_data:
            for sheet_name, sheet_data in file_data.items():
                if isinstance(sheet_data, dict) and "summary" in sheet_data:
                    md_content += f"\n**Sheet: {sheet_name}**\n"
                    md_content += f"- Rows: {sheet_data['summary']['rows']}\n"
                    md_content += f"- Columns: {sheet_data['summary']['cols']}\n"
                    
                    # Show first few column names
                    cols = sheet_data['columns'][:10]
                    md_content += f"- Key Columns: {', '.join(cols)}\n"
                    
                    # Extract any totals or key numbers
                    if sheet_data.get('data'):
                        extract_key_financials(sheet_data['data'], md_content)
        else:
            md_content += f"- Status: {file_data.get('error', 'Unknown error')}\n"
    
    # Save markdown
    md_output = OUTPUT_DIR / "excel_extraction_summary.md"
    with open(md_output, 'w') as f:
        f.write(md_content)
    print(f"✅ Saved Markdown to: {md_output}")

def extract_key_financials(data, md_content):
    """Extract key financial numbers from data"""
    # This would need to be customized based on actual data structure
    pass

def analyze_budget_file():
    """Special analysis of the Annual Budget file"""
    
    budget_file = BASE_DIR / "1736071 fi p211 Annual Budget (final).xlsx"
    
    if budget_file.exists():
        print("\n" + "="*60)
        print("📊 DETAILED BUDGET ANALYSIS")
        print("="*60)
        
        # Read the budget file
        excel_file = pd.ExcelFile(budget_file)
        
        budget_data = {}
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(budget_file, sheet_name=sheet_name)
            
            print(f"\n📋 Sheet: {sheet_name}")
            print(f"Shape: {df.shape}")
            
            # Look for revenue/expense categories
            if df.shape[0] > 0:
                # Try to identify financial rows
                for idx, row in df.iterrows():
                    row_str = str(row.values)
                    if any(keyword in row_str.lower() for keyword in ['revenue', 'income', 'expense', 'total', 'net']):
                        print(f"  Found financial row {idx}: {row.values[:3]}...")
                        
                        # Extract numeric values
                        numeric_vals = [v for v in row.values if isinstance(v, (int, float)) and pd.notna(v)]
                        if numeric_vals:
                            print(f"    Values: {numeric_vals[:5]}")
            
            budget_data[sheet_name] = df.to_dict('records')
        
        # Save budget analysis
        budget_output = OUTPUT_DIR / "annual_budget_analysis.json"
        with open(budget_output, 'w') as f:
            json.dump(budget_data, f, indent=2, default=str)
        print(f"\n✅ Budget analysis saved to: {budget_output}")
        
        return budget_data
    
    return None

def analyze_trial_balance():
    """Extract Trial Balance data for Q1 2025"""
    
    tb_file = BASE_DIR / "Fir Tree Trial Balance 1.2025 - 3.2025.xlsx"
    
    if tb_file.exists():
        print("\n" + "="*60)
        print("📊 Q1 2025 TRIAL BALANCE ANALYSIS")
        print("="*60)
        
        df = pd.read_excel(tb_file)
        
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Look for account balances
        if 'Account' in df.columns or 'Description' in df.columns:
            # Find key accounts
            key_accounts = ['cash', 'revenue', 'expense', 'hap', 'rent']
            
            for account in key_accounts:
                matching_rows = df[df.apply(lambda row: account in str(row.values).lower(), axis=1)]
                if not matching_rows.empty:
                    print(f"\n{account.upper()} Accounts:")
                    print(matching_rows.head())
        
        # Save trial balance
        tb_output = OUTPUT_DIR / "trial_balance_q1_2025.json"
        df.to_json(tb_output, orient='records', default_handler=str)
        print(f"\n✅ Trial Balance saved to: {tb_output}")
        
        return df.to_dict('records')
    
    return None

def main():
    """Run all extractions"""
    
    print("="*60)
    print("🏦 FIR TREE PARK - EXCEL DATA EXTRACTION")
    print("="*60)
    
    # Extract all Excel files
    all_data = extract_excel_files()
    
    # Special analysis of budget
    budget_data = analyze_budget_file()
    
    # Analyze trial balance
    tb_data = analyze_trial_balance()
    
    print("\n" + "="*60)
    print("✅ EXTRACTION COMPLETE")
    print("="*60)
    print("\nOutputs created:")
    print("1. excel_financial_data.json - All Excel data")
    print("2. excel_extraction_summary.md - Summary report")
    print("3. annual_budget_analysis.json - Budget details")
    print("4. trial_balance_q1_2025.json - Q1 2025 Trial Balance")
    
    return all_data

if __name__ == "__main__":
    main()