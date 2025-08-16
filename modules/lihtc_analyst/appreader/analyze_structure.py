#!/usr/bin/env python3
"""
Analyze the structure of 4% LIHTC applications to identify field locations
"""

import pandas as pd
import json
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_excel_structure(file_path):
    """Analyze the structure of a single Excel file"""
    try:
        # Load the Excel file
        excel_file = pd.ExcelFile(file_path)
        
        structure = {
            "filename": file_path.name,
            "sheets": excel_file.sheet_names,
            "application_tab": {},
            "sources_uses_tab": {}
        }
        
        # Check for Application tab
        app_tab_names = ["Application", "application", "App", "APPLICATION"]
        app_sheet = None
        for name in app_tab_names:
            if name in excel_file.sheet_names:
                app_sheet = name
                break
        
        if app_sheet:
            df = pd.read_excel(file_path, sheet_name=app_sheet, header=None)
            structure["application_tab"]["found"] = True
            structure["application_tab"]["sheet_name"] = app_sheet
            
            # Search for key fields in the Application tab
            fields_to_find = {
                "Project Name": None,
                "City": None,
                "County": None,
                "General Contractor": None,
                "New Construction": None,
                "Total Number of Units": None,
                "Total Square Footage": None,
                "Low Income Units": None
            }
            
            # Search for each field
            for row_idx in range(min(300, len(df))):  # Check first 300 rows
                for col_idx in range(min(30, len(df.columns))):  # Check first 30 columns
                    cell_value = str(df.iloc[row_idx, col_idx]).strip()
                    
                    for field in fields_to_find:
                        if field.lower() in cell_value.lower() and fields_to_find[field] is None:
                            fields_to_find[field] = {
                                "label_location": f"Row {row_idx + 1}, Col {chr(65 + col_idx)}",
                                "label_text": cell_value,
                                "row": row_idx + 1,
                                "col": col_idx + 1
                            }
                            
                            # Check adjacent cells for data
                            if col_idx + 1 < len(df.columns):
                                data_value = df.iloc[row_idx, col_idx + 1]
                                if pd.notna(data_value) and str(data_value).strip() and not str(data_value).endswith(':'):
                                    fields_to_find[field]["data_value"] = str(data_value).strip()
                                    fields_to_find[field]["data_location"] = f"Row {row_idx + 1}, Col {chr(65 + col_idx + 1)}"
            
            structure["application_tab"]["fields"] = fields_to_find
        
        # Check for Sources and Uses Budget tab
        su_tab_names = ["Sources and Uses Budget", "Sources & Uses Budget", "Sources and Uses", "Sources & Uses", "SOURCES AND USES BUDGET"]
        su_sheet = None
        for name in su_tab_names:
            if name in excel_file.sheet_names:
                su_sheet = name
                break
        
        if su_sheet:
            df = pd.read_excel(file_path, sheet_name=su_sheet, header=None)
            structure["sources_uses_tab"]["found"] = True
            structure["sources_uses_tab"]["sheet_name"] = su_sheet
            
            # Search for cost categories
            cost_fields = {
                "Land Cost or Value": None,
                "Total New Construction Costs": None,
                "Total Architectural Costs": None,
                "Total Survey and Engineering": None,
                "Local Development Impact Fees": None,
                "Architectural": None,
                "Survey": None,
                "Engineering": None,
                "Impact Fees": None
            }
            
            for row_idx in range(min(200, len(df))):
                for col_idx in range(min(20, len(df.columns))):
                    cell_value = str(df.iloc[row_idx, col_idx]).strip()
                    
                    for field in cost_fields:
                        if field.lower() in cell_value.lower() and cost_fields[field] is None:
                            cost_fields[field] = {
                                "label_location": f"Row {row_idx + 1}, Col {chr(65 + col_idx)}",
                                "label_text": cell_value,
                                "row": row_idx + 1,
                                "col": col_idx + 1
                            }
                            
                            # Look for numeric values in adjacent columns
                            for offset in range(1, 6):
                                if col_idx + offset < len(df.columns):
                                    value = df.iloc[row_idx, col_idx + offset]
                                    if pd.notna(value) and isinstance(value, (int, float)):
                                        cost_fields[field]["data_value"] = value
                                        cost_fields[field]["data_location"] = f"Row {row_idx + 1}, Col {chr(65 + col_idx + offset)}"
                                        break
            
            structure["sources_uses_tab"]["fields"] = cost_fields
        
        return structure
        
    except Exception as e:
        logging.error(f"Error analyzing {file_path}: {str(e)}")
        return None

def main():
    # Define the source directory
    source_dir = Path("/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data")
    
    # Use the test file mentioned in the handoff document
    test_file = source_dir / "2024_4pct_R1_24-409.xlsx"
    
    if test_file.exists():
        logging.info(f"Analyzing test file: {test_file}")
        structure = analyze_excel_structure(test_file)
        
        if structure:
            # Save the analysis
            output_file = Path("/Users/vitorfaroni/Documents/Automation/LIHTCApp/structure_analysis.json")
            with open(output_file, 'w') as f:
                json.dump(structure, f, indent=2)
            
            logging.info(f"Analysis saved to: {output_file}")
            
            # Print summary
            print("\n=== Structure Analysis Summary ===")
            print(f"File: {structure['filename']}")
            print(f"Sheets found: {', '.join(structure['sheets'])}")
            
            if structure['application_tab'].get('found'):
                print(f"\nApplication Tab: {structure['application_tab']['sheet_name']}")
                print("Fields found:")
                for field, info in structure['application_tab']['fields'].items():
                    if info and 'data_value' in info:
                        print(f"  - {field}: {info['label_location']} → {info.get('data_value', 'No data')}")
            
            if structure['sources_uses_tab'].get('found'):
                print(f"\nSources & Uses Budget Tab: {structure['sources_uses_tab']['sheet_name']}")
                print("Cost categories found:")
                for field, info in structure['sources_uses_tab']['fields'].items():
                    if info and 'data_value' in info:
                        print(f"  - {field}: {info['label_location']} → ${info.get('data_value', 0):,.0f}")
    else:
        logging.error(f"Test file not found: {test_file}")

if __name__ == "__main__":
    main()