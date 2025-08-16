#!/usr/bin/env python3
"""
LIHTC 4% Application Data Extractor
Extracts specific fields from Application and Sources & Uses Budget tabs
"""

import pandas as pd
import json
import csv
from pathlib import Path
import logging
from datetime import datetime
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extraction.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class LIHTC4PctExtractor:
    def __init__(self, source_directory):
        self.source_dir = Path(source_directory)
        self.results = []
        self.errors = []
        
    def get_cell_value(self, df, row, col):
        """Safely get cell value from dataframe"""
        try:
            if row < len(df) and col < len(df.columns):
                value = df.iloc[row, col]
                if pd.notna(value):
                    return str(value).strip()
        except:
            pass
        return None
    
    def find_field_value(self, df, search_terms, start_row=0, end_row=300, search_cols=30):
        """Search for a field label and return its value"""
        for row_idx in range(start_row, min(end_row, len(df))):
            for col_idx in range(min(search_cols, len(df.columns))):
                cell_value = self.get_cell_value(df, row_idx, col_idx)
                if cell_value:
                    # Check if any search term is in the cell
                    for term in search_terms:
                        if term.lower() in cell_value.lower():
                            # Look for value in adjacent cells (right and below)
                            # First check cells to the right
                            for offset in range(1, 8):
                                if col_idx + offset < len(df.columns):
                                    value = self.get_cell_value(df, row_idx, col_idx + offset)
                                    if value and not value.endswith(':') and len(value) > 2:
                                        return value, row_idx + 1, col_idx + 1
                            # Then check cell below
                            if row_idx + 1 < len(df):
                                value = self.get_cell_value(df, row_idx + 1, col_idx)
                                if value and not value.endswith(':'):
                                    return value, row_idx + 2, col_idx + 1
        return None, None, None
    
    def extract_application_data(self, file_path):
        """Extract data from Application tab"""
        try:
            excel_file = pd.ExcelFile(file_path)
            
            # Find Application sheet
            app_sheet = None
            for sheet in excel_file.sheet_names:
                if 'application' in sheet.lower() and 'checklist' not in sheet.lower():
                    app_sheet = sheet
                    break
            
            if not app_sheet:
                logging.warning(f"No Application tab found in {file_path.name}")
                return {}
            
            df = pd.read_excel(file_path, sheet_name=app_sheet, header=None)
            
            data = {}
            
            # Project Name - typically in row 18, column H (index 7)
            project_name = self.get_cell_value(df, 17, 7)  # Row 18, Col H
            if not project_name:
                # Try searching for it
                project_name, _, _ = self.find_field_value(df, ["PROJECT NAME"], 0, 30)
            data['project_name'] = project_name or "Not found"
            
            # City - search for city field
            city, _, _ = self.find_field_value(df, ["City:", "CITY"], 150, 250)
            data['city'] = city or "Not found"
            
            # County - search for county field
            county, _, _ = self.find_field_value(df, ["County:", "COUNTY"], 180, 250)
            data['county'] = county or "Not found"
            
            # General Contractor
            gc, _, _ = self.find_field_value(df, ["General Contractor", "GENERAL CONTRACTOR"], 280, 350)
            data['general_contractor'] = gc or "Not found"
            
            # New Construction - search for checkbox or yes/no field
            new_const, _, _ = self.find_field_value(df, ["New Construction", "NEW CONSTRUCTION"], 0, 300)
            if new_const:
                data['new_construction'] = "Yes" if any(x in new_const.lower() for x in ['yes', 'x', '✓', 'true']) else "No"
            else:
                data['new_construction'] = "Not specified"
            
            # Total Number of Units - search various possible labels
            units, _, _ = self.find_field_value(df, 
                ["Total Number of Units", "Total Units", "TOTAL UNITS", "Total # of Units"], 
                0, 300)
            try:
                data['total_units'] = int(float(units)) if units else 0
            except:
                data['total_units'] = 0
            
            # Total Square Footage of Low Income Units
            sqft, _, _ = self.find_field_value(df, 
                ["Total Square Footage", "Low Income Units", "Square Footage", "SQUARE FOOTAGE", "sq ft", "sq. ft."], 
                0, 300)
            try:
                data['total_sqft_low_income'] = int(float(sqft.replace(',', ''))) if sqft else 0
            except:
                data['total_sqft_low_income'] = 0
            
            return data
            
        except Exception as e:
            logging.error(f"Error extracting application data from {file_path.name}: {str(e)}")
            return {}
    
    def extract_sources_uses_data(self, file_path):
        """Extract data from Sources and Uses Budget tab"""
        try:
            excel_file = pd.ExcelFile(file_path)
            
            # Find Sources and Uses sheet
            su_sheet = None
            for sheet in excel_file.sheet_names:
                if any(term in sheet.lower() for term in ['sources and uses', 'sources & uses']):
                    su_sheet = sheet
                    break
            
            if not su_sheet:
                logging.warning(f"No Sources and Uses tab found in {file_path.name}")
                return {}
            
            df = pd.read_excel(file_path, sheet_name=su_sheet, header=None)
            
            data = {}
            
            # Based on our analysis, data is typically in column B (index 1)
            # Land Cost - Row 4
            try:
                land_cost = df.iloc[3, 1]  # Row 4, Col B
                data['land_cost'] = float(land_cost) if pd.notna(land_cost) else 0
            except:
                data['land_cost'] = 0
            
            # Total New Construction Costs - Row 38
            try:
                construction = df.iloc[37, 1]  # Row 38, Col B
                data['total_new_construction'] = float(construction) if pd.notna(construction) else 0
            except:
                data['total_new_construction'] = 0
            
            # Total Architectural Costs - Row 42
            try:
                architectural = df.iloc[41, 1]  # Row 42, Col B
                data['total_architectural'] = float(architectural) if pd.notna(architectural) else 0
            except:
                data['total_architectural'] = 0
            
            # Total Survey and Engineering - Row 43
            try:
                survey_eng = df.iloc[42, 1]  # Row 43, Col B
                data['total_survey_engineering'] = float(survey_eng) if pd.notna(survey_eng) else 0
            except:
                data['total_survey_engineering'] = 0
            
            # Local Development Impact Fees - Row 85
            try:
                impact_fees = df.iloc[84, 1]  # Row 85, Col B
                data['local_impact_fees'] = float(impact_fees) if pd.notna(impact_fees) else 0
            except:
                data['local_impact_fees'] = 0
            
            return data
            
        except Exception as e:
            logging.error(f"Error extracting sources/uses data from {file_path.name}: {str(e)}")
            return {}
    
    def process_file(self, file_path):
        """Process a single Excel file"""
        logging.info(f"Processing: {file_path.name}")
        
        result = {
            'filename': file_path.name,
            'application_data': self.extract_application_data(file_path),
            'sources_uses_data': self.extract_sources_uses_data(file_path)
        }
        
        return result
    
    def extract_by_county(self, target_county):
        """Extract data for all 4% applications in a specific county"""
        logging.info(f"Starting extraction for county: {target_county}")
        
        # Find all 4pct files
        files = list(self.source_dir.glob("*4pct*.xlsx"))
        logging.info(f"Found {len(files)} 4% application files")
        
        # Process each file
        for file_path in files:
            try:
                result = self.process_file(file_path)
                
                # Check if county matches
                county = result['application_data'].get('county', '').lower()
                if target_county.lower() in county:
                    self.results.append(result)
                    logging.info(f"Found matching project in {target_county}: {result['application_data'].get('project_name')}")
                
            except Exception as e:
                error_msg = f"Error processing {file_path.name}: {str(e)}"
                logging.error(error_msg)
                self.errors.append(error_msg)
        
        logging.info(f"Extraction complete. Found {len(self.results)} projects in {target_county}")
        return self.results
    
    def save_results(self, output_dir, county_name):
        """Save extraction results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON
        json_file = output_path / f"{county_name}_extraction_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump({
                'county': county_name,
                'extraction_date': timestamp,
                'total_projects': len(self.results),
                'projects': self.results,
                'errors': self.errors
            }, f, indent=2)
        
        # Save CSV summary
        csv_file = output_path / f"{county_name}_summary_{timestamp}.csv"
        with open(csv_file, 'w', newline='') as f:
            if self.results:
                fieldnames = [
                    'filename', 'project_name', 'city', 'county', 'general_contractor',
                    'new_construction', 'total_units', 'total_sqft_low_income',
                    'land_cost', 'total_new_construction', 'total_architectural',
                    'total_survey_engineering', 'local_impact_fees'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in self.results:
                    row = {'filename': result['filename']}
                    row.update(result['application_data'])
                    row.update(result['sources_uses_data'])
                    writer.writerow(row)
        
        # Generate summary statistics
        if self.results:
            total_units = sum(r['application_data'].get('total_units', 0) for r in self.results)
            total_land_cost = sum(r['sources_uses_data'].get('land_cost', 0) for r in self.results)
            total_construction = sum(r['sources_uses_data'].get('total_new_construction', 0) for r in self.results)
            
            summary = f"""
Extraction Summary for {county_name} County
==========================================
Total Projects: {len(self.results)}
Total Units: {total_units:,}
Total Land Cost: ${total_land_cost:,.0f}
Total Construction Cost: ${total_construction:,.0f}

Files saved:
- JSON: {json_file}
- CSV: {csv_file}
"""
            print(summary)
            
            # Save summary
            summary_file = output_path / f"{county_name}_summary_{timestamp}.txt"
            with open(summary_file, 'w') as f:
                f.write(summary)

def main():
    # Configuration
    source_directory = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    output_directory = "/Users/vitorfaroni/Documents/Automation/LIHTCApp/output"
    
    # Get county from command line or use default
    if len(sys.argv) > 1:
        county = sys.argv[1]
    else:
        county = input("Enter the county name to extract (e.g., 'San Francisco'): ")
    
    # Create extractor and run
    extractor = LIHTC4PctExtractor(source_directory)
    extractor.extract_by_county(county)
    extractor.save_results(output_directory, county.replace(' ', '_'))

if __name__ == "__main__":
    main()