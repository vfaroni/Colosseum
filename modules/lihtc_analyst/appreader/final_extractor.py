#!/usr/bin/env python3
"""
Final LIHTC 4% Application Data Extractor
Based on actual field coordinate analysis
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
        """Safely get cell value from dataframe (0-indexed)"""
        try:
            if row < len(df) and col < len(df.columns):
                value = df.iloc[row, col]
                if pd.notna(value):
                    return str(value).strip()
        except:
            pass
        return None
    
    def extract_application_data(self, file_path):
        """Extract data from Application tab using known coordinates"""
        try:
            df = pd.read_excel(file_path, sheet_name="Application", header=None)
            
            data = {}
            
            # Project Name - Row 18, Column H (indices 17, 7)
            data['project_name'] = self.get_cell_value(df, 17, 7) or "Not found"
            
            # County - Row 189, Column T (indices 188, 19) - offset +3 from Q
            data['county'] = self.get_cell_value(df, 188, 19) or "Not found"
            
            # City - Row 189, Column G (indices 188, 6) - offset +3 from D
            data['city'] = self.get_cell_value(df, 188, 6) or "Not found"
            
            # Search for other fields in likely locations
            # General Contractor - usually around row 295
            gc_found = False
            for row in range(290, min(310, len(df))):
                for col in range(20, min(30, len(df.columns))):
                    cell = self.get_cell_value(df, row, col)
                    if cell and "general contractor" in cell.lower():
                        # Check adjacent cells for value
                        for offset in [1, 2, 3, 4]:
                            if col + offset < len(df.columns):
                                value = self.get_cell_value(df, row, col + offset)
                                if value and not value.endswith(':') and len(value) > 3:
                                    data['general_contractor'] = value
                                    gc_found = True
                                    break
                        if gc_found:
                            break
                if gc_found:
                    break
            
            if not gc_found:
                data['general_contractor'] = "Not found"
            
            # New Construction - search for checkbox or field
            new_const = "Not specified"
            for row in range(0, min(100, len(df))):
                for col in range(min(30, len(df.columns))):
                    cell = self.get_cell_value(df, row, col)
                    if cell and "new construction" in cell.lower():
                        # Look for nearby checkbox or yes/no
                        for r_offset in [-1, 0, 1]:
                            for c_offset in [-2, -1, 1, 2, 3]:
                                if (0 <= row + r_offset < len(df) and 
                                    0 <= col + c_offset < len(df.columns)):
                                    check_cell = self.get_cell_value(df, row + r_offset, col + c_offset)
                                    if check_cell:
                                        if any(x in check_cell.lower() for x in ['yes', 'x', '✓', 'true']):
                                            new_const = "Yes"
                                        elif any(x in check_cell.lower() for x in ['no', 'false']):
                                            new_const = "No"
            
            data['new_construction'] = new_const
            
            # Total Number of Units - search in various locations
            units = 0
            unit_keywords = ["total number of units", "total units", "# of units", "unit count"]
            for keyword in unit_keywords:
                for row in range(0, min(300, len(df))):
                    for col in range(min(30, len(df.columns))):
                        cell = self.get_cell_value(df, row, col)
                        if cell and keyword in cell.lower():
                            # Search nearby for numeric value
                            for r_offset in [-1, 0, 1]:
                                for c_offset in [-2, -1, 1, 2, 3, 4, 5]:
                                    if (0 <= row + r_offset < len(df) and 
                                        0 <= col + c_offset < len(df.columns)):
                                        value_cell = self.get_cell_value(df, row + r_offset, col + c_offset)
                                        if value_cell:
                                            try:
                                                num_value = int(float(value_cell.replace(',', '')))
                                                if 1 <= num_value <= 2000:  # Reasonable range for units
                                                    units = num_value
                                                    break
                                            except:
                                                pass
                                if units > 0:
                                    break
                            if units > 0:
                                break
                    if units > 0:
                        break
                if units > 0:
                    break
            
            data['total_units'] = units
            
            # Total Square Footage - search for square footage fields
            sqft = 0
            sqft_keywords = ["square footage", "sq ft", "sq. ft.", "total sq"]
            for keyword in sqft_keywords:
                for row in range(0, min(300, len(df))):
                    for col in range(min(30, len(df.columns))):
                        cell = self.get_cell_value(df, row, col)
                        if cell and keyword in cell.lower() and "low income" in cell.lower():
                            # Search nearby for numeric value
                            for r_offset in [-1, 0, 1]:
                                for c_offset in [-2, -1, 1, 2, 3, 4, 5]:
                                    if (0 <= row + r_offset < len(df) and 
                                        0 <= col + c_offset < len(df.columns)):
                                        value_cell = self.get_cell_value(df, row + r_offset, col + c_offset)
                                        if value_cell:
                                            try:
                                                num_value = int(float(value_cell.replace(',', '')))
                                                if 5000 <= num_value <= 5000000:  # Reasonable range for sqft
                                                    sqft = num_value
                                                    break
                                            except:
                                                pass
                                if sqft > 0:
                                    break
                            if sqft > 0:
                                break
                    if sqft > 0:
                        break
                if sqft > 0:
                    break
            
            data['total_sqft_low_income'] = sqft
            
            return data
            
        except Exception as e:
            logging.error(f"Error extracting application data from {file_path.name}: {str(e)}")
            return {}
    
    def extract_sources_uses_data(self, file_path):
        """Extract data from Sources and Uses Budget tab using known coordinates"""
        try:
            df = pd.read_excel(file_path, sheet_name="Sources and Uses Budget", header=None)
            
            data = {}
            
            # Based on analysis, costs are in column B (index 1)
            try:
                data['land_cost'] = float(df.iloc[3, 1]) if pd.notna(df.iloc[3, 1]) else 0  # Row 4
            except:
                data['land_cost'] = 0
            
            try:
                data['total_new_construction'] = float(df.iloc[37, 1]) if pd.notna(df.iloc[37, 1]) else 0  # Row 38
            except:
                data['total_new_construction'] = 0
            
            try:
                data['total_architectural'] = float(df.iloc[41, 1]) if pd.notna(df.iloc[41, 1]) else 0  # Row 42
            except:
                data['total_architectural'] = 0
            
            try:
                data['total_survey_engineering'] = float(df.iloc[42, 1]) if pd.notna(df.iloc[42, 1]) else 0  # Row 43
            except:
                data['total_survey_engineering'] = 0
            
            try:
                data['local_impact_fees'] = float(df.iloc[84, 1]) if pd.notna(df.iloc[84, 1]) else 0  # Row 85
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
    
    def extract_by_county(self, target_county, max_files=None):
        """Extract data for all 4% applications in a specific county"""
        logging.info(f"Starting extraction for county: {target_county}")
        
        # Find all 4pct files
        files = list(self.source_dir.glob("*4pct*.xlsx"))
        logging.info(f"Found {len(files)} 4% application files")
        
        if max_files:
            files = files[:max_files]
            logging.info(f"Limited to first {max_files} files for testing")
        
        # Process each file
        for file_path in files:
            try:
                result = self.process_file(file_path)
                
                # Check if county matches
                county = result['application_data'].get('county', '').lower()
                if target_county.lower() in county:
                    self.results.append(result)
                    logging.info(f"✓ Found matching project in {target_county}: {result['application_data'].get('project_name')}")
                
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
        
        # Generate summary
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
            return summary
        else:
            print(f"No projects found in {county_name} County")
            return f"No projects found in {county_name} County"

def main():
    source_directory = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    output_directory = "/Users/vitorfaroni/Documents/Automation/LIHTCApp/output"
    
    # Get parameters
    if len(sys.argv) > 1:
        county = sys.argv[1]
    else:
        county = input("Enter the county name to extract (e.g., 'San Francisco'): ")
    
    # Optional: limit files for testing
    max_files = None
    if len(sys.argv) > 2:
        try:
            max_files = int(sys.argv[2])
        except:
            pass
    
    # Create extractor and run
    extractor = LIHTC4PctExtractor(source_directory)
    extractor.extract_by_county(county, max_files)
    extractor.save_results(output_directory, county.replace(' ', '_'))

if __name__ == "__main__":
    main()