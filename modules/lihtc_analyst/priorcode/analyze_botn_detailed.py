#!/usr/bin/env python3
"""
Detailed Analysis of BOTN Workforce Housing Underwriting Template
Uses pandas to read and analyze Excel data more effectively
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import numpy as np

class DetailedBOTNAnalyzer:
    def __init__(self, template_path):
        self.template_path = template_path
        self.sheets_data = {}
        self.analysis = {
            'overview': {},
            'inputs_analysis': {},
            'outputs_analysis': {},
            'data_sheets': {},
            'financial_model_structure': {}
        }
        
    def load_all_sheets(self):
        """Load all sheets using pandas"""
        try:
            print(f"Loading Excel file: {self.template_path}")
            
            # Get all sheet names
            xl_file = pd.ExcelFile(self.template_path)
            sheet_names = xl_file.sheet_names
            
            print(f"Found {len(sheet_names)} sheets: {', '.join(sheet_names)}")
            
            # Load each sheet
            for sheet_name in sheet_names:
                print(f"\nLoading sheet: {sheet_name}")
                try:
                    # Try different approaches for different sheets
                    if sheet_name in ['Inputs', 'Output']:
                        # These might have complex layouts
                        self.sheets_data[sheet_name] = pd.read_excel(
                            self.template_path, 
                            sheet_name=sheet_name,
                            header=None  # Don't assume first row is header
                        )
                    else:
                        # Data sheets likely have headers
                        self.sheets_data[sheet_name] = pd.read_excel(
                            self.template_path, 
                            sheet_name=sheet_name
                        )
                    
                    shape = self.sheets_data[sheet_name].shape
                    print(f"  Loaded {shape[0]} rows x {shape[1]} columns")
                    
                except Exception as e:
                    print(f"  Error loading sheet {sheet_name}: {e}")
                    
            self.analysis['overview'] = {
                'file_name': Path(self.template_path).name,
                'sheets': sheet_names,
                'sheet_count': len(sheet_names),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            return False
    
    def analyze_inputs_sheet_detailed(self):
        """Detailed analysis of Inputs sheet"""
        try:
            if 'Inputs' not in self.sheets_data:
                print("Inputs sheet not loaded")
                return
                
            df = self.sheets_data['Inputs']
            print("\n=== DETAILED INPUTS ANALYSIS ===")
            
            # Find non-empty cells in first few columns
            inputs_info = []
            
            for idx, row in df.iterrows():
                # Look at first 5 columns
                for col_idx in range(min(5, len(df.columns))):
                    cell_value = row.iloc[col_idx]
                    if pd.notna(cell_value) and str(cell_value).strip():
                        inputs_info.append({
                            'row': idx,
                            'column': col_idx,
                            'value': str(cell_value),
                            'type': type(cell_value).__name__
                        })
                        
                        # Print first 20 non-empty values
                        if len(inputs_info) <= 20:
                            print(f"Row {idx}, Col {col_idx}: {cell_value}")
            
            self.analysis['inputs_analysis'] = {
                'non_empty_cells': len(inputs_info),
                'sample_inputs': inputs_info[:50]
            }
            
            # Try to identify input categories
            self.identify_input_categories(df)
            
        except Exception as e:
            print(f"Error analyzing Inputs sheet: {e}")
    
    def identify_input_categories(self, df):
        """Try to identify categories in inputs sheet"""
        try:
            categories = []
            
            # Look for cells that might be headers (text in column A with empty column B)
            for idx, row in df.iterrows():
                col_a = row.iloc[0] if len(row) > 0 else None
                col_b = row.iloc[1] if len(row) > 1 else None
                
                if pd.notna(col_a) and isinstance(col_a, str) and pd.isna(col_b):
                    # Likely a category header
                    categories.append({
                        'row': idx,
                        'category': str(col_a).strip()
                    })
            
            print(f"\nIdentified {len(categories)} potential input categories:")
            for cat in categories[:15]:
                print(f"  Row {cat['row']}: {cat['category']}")
                
            self.analysis['inputs_analysis']['categories'] = categories
            
        except Exception as e:
            print(f"Error identifying categories: {e}")
    
    def analyze_outputs_sheet_detailed(self):
        """Detailed analysis of Output sheet"""
        try:
            if 'Output' not in self.sheets_data:
                print("Output sheet not loaded")
                return
                
            df = self.sheets_data['Output']
            print("\n=== DETAILED OUTPUT ANALYSIS ===")
            
            # Look for financial metrics keywords
            financial_keywords = [
                'revenue', 'income', 'expense', 'noi', 'cash flow', 'debt', 
                'equity', 'return', 'irr', 'yield', 'cap rate', 'dscr', 'ltv',
                'occupancy', 'rent', 'unit', 'cost', 'value', 'price'
            ]
            
            found_metrics = []
            
            # Scan first column for labels
            for idx, row in df.iterrows():
                label = row.iloc[0] if len(row) > 0 else None
                
                if pd.notna(label) and isinstance(label, str):
                    label_lower = str(label).lower()
                    
                    # Check for financial keywords
                    for keyword in financial_keywords:
                        if keyword in label_lower:
                            # Get numeric values from the row
                            numeric_values = []
                            for col_idx in range(1, min(len(row), 15)):
                                val = row.iloc[col_idx]
                                if pd.notna(val) and isinstance(val, (int, float)):
                                    numeric_values.append(float(val))
                            
                            found_metrics.append({
                                'row': idx,
                                'label': str(label),
                                'keyword': keyword,
                                'numeric_count': len(numeric_values),
                                'sample_values': numeric_values[:5]
                            })
                            break
            
            print(f"\nFound {len(found_metrics)} financial metrics:")
            for metric in found_metrics[:20]:
                print(f"  Row {metric['row']}: {metric['label']} ({metric['numeric_count']} values)")
                
            self.analysis['outputs_analysis'] = {
                'financial_metrics_found': len(found_metrics),
                'metrics': found_metrics
            }
            
        except Exception as e:
            print(f"Error analyzing Output sheet: {e}")
    
    def analyze_data_sheets(self):
        """Analyze the data reference sheets"""
        try:
            print("\n=== DATA SHEETS ANALYSIS ===")
            
            data_sheets = ['FY25_FMRs', 'SAFMRs', 'Section8-FY25', 'Counties']
            
            for sheet_name in data_sheets:
                if sheet_name in self.sheets_data:
                    df = self.sheets_data[sheet_name]
                    
                    print(f"\n{sheet_name}:")
                    print(f"  Shape: {df.shape}")
                    
                    # Get column info
                    if not df.empty:
                        print(f"  Columns: {list(df.columns)[:10]}")
                        
                        # Get data types
                        dtypes = df.dtypes.value_counts()
                        print(f"  Data types: {dict(dtypes)}")
                        
                        # Sample data
                        print(f"  First few rows:")
                        print(df.head(3).to_string(max_cols=8))
                        
                    self.analysis['data_sheets'][sheet_name] = {
                        'rows': df.shape[0],
                        'columns': df.shape[1],
                        'column_names': list(df.columns)[:20],
                        'data_types': dict(df.dtypes.value_counts())
                    }
                    
        except Exception as e:
            print(f"Error analyzing data sheets: {e}")
    
    def identify_model_structure(self):
        """Try to identify the financial model structure"""
        try:
            print("\n=== FINANCIAL MODEL STRUCTURE ===")
            
            structure = {
                'model_type': 'Workforce Housing Underwriting',
                'key_components': [],
                'data_flow': []
            }
            
            # Based on sheet names and content
            if 'FY25_FMRs' in self.sheets_data:
                structure['key_components'].append('HUD Fair Market Rent Integration')
            if 'SAFMRs' in self.sheets_data:
                structure['key_components'].append('Small Area Fair Market Rent Analysis')
            if 'Section8-FY25' in self.sheets_data:
                structure['key_components'].append('Section 8 Payment Standards')
                
            # Check for specific calculations in Output
            if 'outputs_analysis' in self.analysis:
                metrics = self.analysis['outputs_analysis'].get('metrics', [])
                
                # Categorize metrics
                revenue_metrics = [m for m in metrics if any(k in m['label'].lower() for k in ['revenue', 'income', 'rent'])]
                expense_metrics = [m for m in metrics if 'expense' in m['label'].lower()]
                return_metrics = [m for m in metrics if any(k in m['label'].lower() for k in ['return', 'irr', 'yield'])]
                
                if revenue_metrics:
                    structure['key_components'].append(f'Revenue Analysis ({len(revenue_metrics)} metrics)')
                if expense_metrics:
                    structure['key_components'].append(f'Expense Modeling ({len(expense_metrics)} metrics)')
                if return_metrics:
                    structure['key_components'].append(f'Return Calculations ({len(return_metrics)} metrics)')
            
            self.analysis['financial_model_structure'] = structure
            
            print(f"Model Type: {structure['model_type']}")
            print(f"Key Components:")
            for component in structure['key_components']:
                print(f"  - {component}")
                
        except Exception as e:
            print(f"Error identifying model structure: {e}")
    
    def create_summary_report(self):
        """Create a comprehensive summary report"""
        try:
            print("\n=== CREATING SUMMARY REPORT ===")
            
            # Create markdown report
            report_lines = [
                f"# BOTN Workforce Housing Underwriting Template Analysis",
                f"**File**: {self.analysis['overview']['file_name']}",
                f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "## Overview",
                f"- Total Sheets: {self.analysis['overview']['sheet_count']}",
                f"- Sheet Names: {', '.join(self.analysis['overview']['sheets'])}",
                "",
                "## Model Structure",
            ]
            
            if 'financial_model_structure' in self.analysis:
                structure = self.analysis['financial_model_structure']
                report_lines.append(f"**Model Type**: {structure['model_type']}")
                report_lines.append("**Key Components**:")
                for comp in structure['key_components']:
                    report_lines.append(f"- {comp}")
            
            report_lines.extend([
                "",
                "## Data Sources",
                "The model integrates the following HUD data sources:",
                "- **FY25 FMRs**: Fair Market Rents for fiscal year 2025",
                "- **SAFMRs**: Small Area Fair Market Rents by ZIP code",
                "- **Section 8 Standards**: Payment standards for housing vouchers",
                "- **Counties**: County-level data mapping",
                "",
                "## Key Findings",
            ])
            
            # Add metrics summary
            if 'outputs_analysis' in self.analysis and 'financial_metrics_found' in self.analysis['outputs_analysis']:
                count = self.analysis['outputs_analysis']['financial_metrics_found']
                report_lines.append(f"- Identified {count} financial calculation metrics")
            
            # Save report
            report_path = Path(self.template_path).parent / f"BOTN_Analysis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_path, 'w') as f:
                f.write('\n'.join(report_lines))
            
            print(f"Report saved to: {report_path}")
            
            # Save detailed JSON analysis
            json_path = Path(self.template_path).parent / f"BOTN_Detailed_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_path, 'w') as f:
                json.dump(self.analysis, f, indent=2, default=str)
            
            print(f"Detailed analysis saved to: {json_path}")
            
        except Exception as e:
            print(f"Error creating summary report: {e}")

def main():
    """Main analysis function"""
    template_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Workforce_Housing/BOTN_Proformas/Workforce BOTN 05.12.25.xlsx'
    
    analyzer = DetailedBOTNAnalyzer(template_path)
    
    if analyzer.load_all_sheets():
        analyzer.analyze_inputs_sheet_detailed()
        analyzer.analyze_outputs_sheet_detailed()
        analyzer.analyze_data_sheets()
        analyzer.identify_model_structure()
        analyzer.create_summary_report()
        
        print("\n=== ANALYSIS COMPLETE ===")

if __name__ == "__main__":
    main()