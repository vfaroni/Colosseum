#!/usr/bin/env python3
"""
Complete script to populate the Rehabilitation Summary Excel file with construction cost data.
This script can handle multiple input formats including markdown files, CSV files, or 
direct dictionary input.
"""

import openpyxl
from pathlib import Path
import re
import csv
from typing import Dict, List, Tuple, Optional
import argparse

class RehabExcelPopulator:
    def __init__(self, excel_path: Path):
        self.excel_path = excel_path
        self.output_path = excel_path.parent / excel_path.name.replace("RAWFILE", "POPULATED")
        self.workbook = None
        self.sheet = None
        
        # Define the row mapping for each rehabilitation item
        self.row_mapping = {
            # SITE (rows 7-21)
            "Carports/Garages": 7,
            "Drainage": 8,
            "Fencing": 9,
            "Landscaping/Topography": 10,
            "Lighting": 11,
            "Parking/Roadways": 12,
            "Recreation Areas": 13,
            "Sidewalks/Pedestrian Areas": 14,
            "Signage": 15,
            "Trash Facilities": 16,
            "Maintenance Shed": 17,
            "Utilities": 18,
            "Site Other 1": 19,  # Other (Specify)
            "Site Other 2": 20,  # Other (Specify)
            "Site Other 3": 21,  # Other (Specify)
            
            # STRUCTURE FRAMES AND ENVELOPES (rows 23-36)
            "Balconies/Patios": 23,
            "Doors and Frames": 24,
            "Elevated Walkways": 25,
            "Facades/Siding/Exterior Walls": 26,
            "Foundation/Substructure": 27,
            "Insulation": 28,
            "Painting": 29,
            "Roofing": 30,
            "Stairs/Landings": 31,
            "Superstructure": 32,
            "Windows and Frames": 33,
            "Structure Other 1": 34,  # Other (Specify)
            "Structure Other 2": 35,  # Other (Specify)
            "Structure Other 3": 36,  # Other (Specify)
            
            # COMMON AREAS (rows 38-43)
            "Community Room": 38,
            "Laundry Facilities": 39,
            "Management Office": 40,
            "Common Other 1": 41,  # Other (Specify)
            "Common Other 2": 42,  # Other (Specify)
            "Common Other 3": 43,  # Other (Specify)
            
            # MECHANICAL / ELECTRICAL / PLUMBING (rows 45-54)
            "Electrical Systems": 45,
            "Elevators": 46,
            "Fire Alarm/Suppression": 47,
            "Hot and Cold Water Distribution": 48,
            "HVAC/Heating/Cooling": 49,
            "Plumbing and Sewage Systems": 50,
            "Water Heaters": 51,
            "MEP Other 1": 52,  # Other (Specify)
            "MEP Other 2": 53,  # Other (Specify)
            "MEP Other 3": 54,  # Other (Specify)
            
            # UNIT INTERIORS (rows 56-71)
            "Appliances": 56,
            "Cabinets": 57,
            "Carpeting": 58,
            "Ceilings/Walls": 59,
            "Countertops": 60,
            "Doors": 61,
            "Flooring": 62,
            "Lighting": 63,
            "Painting": 64,
            "Sinks/Faucets": 65,
            "Smoke/Heat/CO2 Detectors": 66,
            "Toilets, Tubs and Showers": 67,
            "Window Coverings": 68,
            "Unit Other 1": 69,  # Other (Specify)
            "Unit Other 2": 70,  # Other (Specify)
            "Unit Other 3": 71,  # Other (Specify)
            
            # CODE COMPLIANCE (rows 73-77)
            "Fire Safety": 73,
            "Building Safety": 74,
            "Code Other 1": 75,  # Other (Specify)
            "Code Other 2": 76,  # Other (Specify)
            "Code Other 3": 77,  # Other (Specify)
            
            # ACCESSIBILITY / ADA COMPLIANCE (rows 79-83)
            "Public Area Accessibility": 79,
            "Unit Accessibility": 80,
            "ADA Other 1": 81,  # Other (Specify)
            "ADA Other 2": 82,  # Other (Specify)
            "ADA Other 3": 83,  # Other (Specify)
            
            # TOTAL COSTS (row 85)
            "TOTAL COSTS (From CNA)": 85,
        }
    
    def load_excel(self):
        """Load the Excel file."""
        print(f"Loading Excel file: {self.excel_path}")
        self.workbook = openpyxl.load_workbook(self.excel_path)
        self.sheet = self.workbook.active
        print(f"Loaded worksheet: '{self.sheet.title}'")
    
    def parse_markdown_file(self, markdown_path: Path) -> Dict[str, Tuple[str, str, str, str]]:
        """
        Parse construction cost data from a markdown file.
        Expected format:
        - **Item Name**: description | Units: X | Percentage: X% | Useful Life: X years
        """
        data = {}
        
        with open(markdown_path, 'r') as f:
            content = f.read()
        
        # Pattern to match markdown list items with construction data
        pattern = r'- \*\*([^*]+)\*\*: ([^|]+) \| Units: ([^|]+) \| Percentage: ([^|]+) \| Useful Life: ([^\n]+)'
        
        matches = re.findall(pattern, content)
        for match in matches:
            item_name = match[0].strip()
            description = match[1].strip()
            units = match[2].strip()
            percentage = match[3].strip()
            useful_life = match[4].strip()
            
            # Find the matching key in our row mapping
            for key in self.row_mapping.keys():
                if item_name.lower() in key.lower() or key.lower() in item_name.lower():
                    data[key] = (description, units, percentage, useful_life)
                    break
        
        return data
    
    def parse_csv_file(self, csv_path: Path) -> Dict[str, Tuple[str, str, str, str]]:
        """
        Parse construction cost data from a CSV file.
        Expected columns: Item, Description, Units, Percentage, Useful Life
        """
        data = {}
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                item_name = row.get('Item', '').strip()
                description = row.get('Description', '').strip()
                units = row.get('Units', '').strip()
                percentage = row.get('Percentage', '').strip()
                useful_life = row.get('Useful Life', '').strip()
                
                # Find the matching key in our row mapping
                for key in self.row_mapping.keys():
                    if item_name.lower() in key.lower() or key.lower() in item_name.lower():
                        data[key] = (description, units, percentage, useful_life)
                        break
        
        return data
    
    def populate_excel(self, data: Dict[str, Tuple[str, str, str, str]]):
        """Populate the Excel file with construction cost data."""
        if not self.workbook:
            self.load_excel()
        
        # Column mapping
        col_description = 'B'  # Comments/Brief Description (merged with C)
        col_units = 'D'        # Number of Units
        col_percentage = 'E'   # Percentage
        col_useful_life = 'F'  # Estimated Remaining Useful Life
        
        populated_count = 0
        
        # Populate data based on row mapping
        for item_name, row_num in self.row_mapping.items():
            if item_name in data:
                description, units, percentage, useful_life = data[item_name]
                
                # Populate the cells
                if description and description.lower() != '[description]':
                    self.sheet[f'{col_description}{row_num}'] = description
                if units and units.lower() not in ['[x]', '']:
                    self.sheet[f'{col_units}{row_num}'] = units
                if percentage and percentage.lower() not in ['[x%]', '']:
                    self.sheet[f'{col_percentage}{row_num}'] = percentage
                if useful_life and useful_life.lower() not in ['[x years]', '']:
                    self.sheet[f'{col_useful_life}{row_num}'] = useful_life
                
                populated_count += 1
                print(f"Populated row {row_num}: {item_name}")
        
        # Save the file
        self.workbook.save(self.output_path)
        print(f"\nFile saved as: {self.output_path}")
        print(f"Total items populated: {populated_count}")
    
    def populate_from_dict(self, data: Dict[str, Tuple[str, str, str, str]]):
        """Directly populate from a dictionary."""
        self.populate_excel(data)

def main():
    parser = argparse.ArgumentParser(description='Populate Rehabilitation Summary Excel file')
    parser.add_argument('--markdown', type=str, help='Path to markdown file with construction data')
    parser.add_argument('--csv', type=str, help='Path to CSV file with construction data')
    parser.add_argument('--demo', action='store_true', help='Run with demo data')
    
    args = parser.parse_args()
    
    # Excel file path
    excel_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CA_9p_2025_R2_Perris/9_Percent_Applications/TAB_08__Rehabilitation_Credit_Applications/Exhbit-B-RAWFILE_Att-8-Rehab Summary.xlsx")
    
    # Create populator instance
    populator = RehabExcelPopulator(excel_file)
    
    if args.markdown:
        # Parse markdown file
        markdown_path = Path(args.markdown)
        if markdown_path.exists():
            data = populator.parse_markdown_file(markdown_path)
            populator.populate_from_dict(data)
        else:
            print(f"Error: Markdown file not found: {markdown_path}")
    
    elif args.csv:
        # Parse CSV file
        csv_path = Path(args.csv)
        if csv_path.exists():
            data = populator.parse_csv_file(csv_path)
            populator.populate_from_dict(data)
        else:
            print(f"Error: CSV file not found: {csv_path}")
    
    elif args.demo:
        # Demo data
        demo_data = {
            # SITE
            "Carports/Garages": ("Replace carport roofing and repair structural elements", "12", "100%", "15 years"),
            "Drainage": ("Improve site drainage system", "", "100%", "20 years"),
            "Fencing": ("Replace perimeter chain-link fencing", "", "100%", "15 years"),
            "Landscaping/Topography": ("Refresh landscaping and repair irrigation", "", "100%", "10 years"),
            "Lighting": ("LED retrofit for all site lighting", "", "100%", "20 years"),
            "Parking/Roadways": ("Resurface parking areas and restripe", "", "100%", "15 years"),
            
            # STRUCTURE
            "Roofing": ("Replace composition shingle roofing", "60", "100%", "20 years"),
            "Windows and Frames": ("Replace single-pane windows with dual-pane", "60", "100%", "25 years"),
            "Painting": ("Exterior painting of all buildings", "60", "100%", "7 years"),
            
            # MECHANICAL
            "HVAC/Heating/Cooling": ("Replace HVAC units", "60", "100%", "15 years"),
            "Water Heaters": ("Replace tank water heaters", "60", "100%", "10 years"),
            "Electrical Systems": ("Upgrade electrical panels", "60", "100%", "30 years"),
            
            # UNIT INTERIORS
            "Appliances": ("Replace refrigerators and ranges", "60", "100%", "10 years"),
            "Flooring": ("Replace vinyl flooring with LVP", "60", "100%", "15 years"),
            "Cabinets": ("Reface kitchen cabinets", "60", "100%", "20 years"),
            
            # ACCESSIBILITY
            "Unit Accessibility": ("ADA upgrades to 7 units", "7", "11%", "40 years"),
            "Public Area Accessibility": ("ADA path of travel improvements", "", "100%", "40 years"),
        }
        
        populator.populate_from_dict(demo_data)
        print("\nDemo data populated successfully!")
    
    else:
        print("Please specify an input source: --markdown, --csv, or --demo")
        parser.print_help()

if __name__ == "__main__":
    main()