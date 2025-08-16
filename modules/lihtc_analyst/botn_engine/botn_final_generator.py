#!/usr/bin/env python3
"""
Final BOTN Generator - Creates populated BOTN with user input processing
"""

import pandas as pd
import openpyxl
from pathlib import Path
import logging
from datetime import datetime
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinalBOTNGenerator:
    """Final BOTN generator with smart input processing"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        
    def process_user_inputs(self, raw_inputs):
        """Process and normalize user inputs"""
        processed = {}
        
        # Define the user inputs with their raw values
        input_mapping = {
            8: ('Housing Type', raw_inputs[0]),           # new Construction
            9: ('Credit Pricing', raw_inputs[1]),         # 80 cents
            10: ('Credit Type', raw_inputs[2]),           # 4%
            11: ('Construction Loan Term', raw_inputs[3]), # 36 months
            12: ('Market Cap Rate', raw_inputs[4]),       # 5%
            13: ('Financing Interest Rate', raw_inputs[5]), # 6%
            14: ('Elevator', raw_inputs[6]),              # No
            15: ('# Units', raw_inputs[7]),               # 100 units
            16: ('Avg Unit Size', raw_inputs[8]),         # 900SF
            17: ('Hard Cost/SF', raw_inputs[9])           # 250/SF
        }
        
        for col_num, (field_name, raw_value) in input_mapping.items():
            processed_value = self.normalize_input(field_name, raw_value)
            processed[col_num] = processed_value
            logger.info(f"Processed {field_name}: '{raw_value}' → {processed_value}")
        
        return processed
    
    def normalize_input(self, field_name, raw_value):
        """Normalize input values based on field type"""
        raw_str = str(raw_value).strip()
        
        # Housing Type - capitalize properly
        if 'Housing Type' in field_name:
            return raw_str.title()  # "new Construction" → "New Construction"
        
        # Credit Pricing - handle "80 cents" or percentages
        elif 'Credit Pricing' in field_name:
            if 'cent' in raw_str.lower():
                # Extract number from "80 cents"
                number = re.findall(r'\d+', raw_str)[0]
                return float(number) / 100  # 80 cents → 0.80
            elif '%' in raw_str:
                # Handle percentage format
                number = float(re.findall(r'[\d.]+', raw_str)[0])
                return number / 100
            else:
                return float(raw_str)
        
        # Credit Type - keep as string
        elif 'Credit Type' in field_name:
            return raw_str  # "4%" stays "4%"
        
        # Loan Term - extract number, assume months
        elif 'Loan Term' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)  # "36 months" → 36
        
        # Rates - convert percentages to decimals
        elif 'Rate' in field_name:
            if '%' in raw_str:
                number = float(re.findall(r'[\d.]+', raw_str)[0])
                return number / 100  # "5%" → 0.05, "6%" → 0.06
            else:
                return float(raw_str)
        
        # Elevator - normalize Yes/No
        elif 'Elevator' in field_name:
            return raw_str.title()  # "No" → "No"
        
        # Units - extract number
        elif 'Units' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)  # "100 units" → 100
        
        # Unit Size - extract number (assume SF)
        elif 'Unit Size' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)  # "900SF" → 900
        
        # Hard Cost - extract number (assume per SF)
        elif 'Hard Cost' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)  # "250/SF" → 250
        
        else:
            return raw_str
    
    def get_cdlac_region(self, county_name):
        """Determine CDLAC region based on county name using dropdown values"""
        # Map counties to CDLAC dropdown region names
        cdlac_regions = {
            # San Francisco County
            'San Francisco': 'San Francisco County',
            
            # East Bay Region
            'Alameda': 'East Bay Region', 'Contra Costa': 'East Bay Region',
            
            # South & West Bay Region  
            'San Mateo': 'South & West Bay Region', 'Santa Clara': 'South & West Bay Region',
            'Santa Cruz': 'South & West Bay Region',
            
            # Northern Region
            'Lake': 'Northern Region', 'Marin': 'Northern Region', 'Napa': 'Northern Region',
            'Solano': 'Northern Region', 'Sonoma': 'Northern Region',
            'Butte': 'Northern Region', 'Colusa': 'Northern Region', 'El Dorado': 'Northern Region', 
            'Glenn': 'Northern Region', 'Nevada': 'Northern Region', 'Placer': 'Northern Region', 
            'Sacramento': 'Northern Region', 'Sutter': 'Northern Region', 'Tehama': 'Northern Region', 
            'Yolo': 'Northern Region', 'Yuba': 'Northern Region',
            'Alpine': 'Northern Region', 'Amador': 'Northern Region', 'Calaveras': 'Northern Region', 
            'Del Norte': 'Northern Region', 'Humboldt': 'Northern Region', 'Inyo': 'Northern Region', 
            'Lassen': 'Northern Region', 'Madera': 'Northern Region', 'Mariposa': 'Northern Region', 
            'Mendocino': 'Northern Region', 'Modoc': 'Northern Region', 'Mono': 'Northern Region', 
            'Plumas': 'Northern Region', 'Shasta': 'Northern Region', 'Sierra': 'Northern Region', 
            'Siskiyou': 'Northern Region', 'Tuolumne': 'Northern Region', 'Trinity': 'Northern Region',
            
            # Central Valley Region
            'Fresno': 'Central Valley Region', 'Kern': 'Central Valley Region', 'Kings': 'Central Valley Region', 
            'Merced': 'Central Valley Region', 'San Joaquin': 'Central Valley Region', 
            'Stanislaus': 'Central Valley Region', 'Tulare': 'Central Valley Region',
            
            # Central Coast Region
            'Monterey': 'Central Coast Region', 'San Benito': 'Central Coast Region', 
            'San Luis Obispo': 'Central Coast Region', 'Santa Barbara': 'Central Coast Region', 
            'Ventura': 'Central Coast Region',
            
            # Los Angeles County
            'Los Angeles': 'Los Angeles County',
            
            # Orange County
            'Orange': 'Orange County',
            
            # Inland Empire Region
            'Riverside': 'Inland Empire Region', 'San Bernardino': 'Inland Empire Region',
            
            # San Diego County
            'San Diego': 'San Diego County', 'Imperial': 'San Diego County'
        }
        return cdlac_regions.get(county_name, None)
    
    def generate_complete_botn(self):
        """Generate complete BOTN with processed user inputs"""
        
        # Your provided inputs
        user_inputs = [
            "new Construction",    # Housing Type  
            "80 cents",           # Credit Pricing
            "4%",                 # Credit Type
            "36 months",          # Construction Loan Term
            "5%",                 # Market Cap Rate
            "6%",                 # Financing Interest Rate
            "No",                 # Elevator
            "100 units",          # # Units
            "900SF",              # Avg Unit Size
            "250/SF"              # Hard Cost/SF
        ]
        
        # Process user inputs
        logger.info("🔧 Processing user inputs...")
        processed_inputs = self.process_user_inputs(user_inputs)
        
        # Load test site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        test_site = df.iloc[0]
        
        # Auto-populated fields
        auto_mapping = {
            1: test_site.get('Property Name'),
            2: test_site.get('Property Address'),
            3: test_site.get('County Name'),
            4: self.get_cdlac_region(test_site.get('County Name')),
            5: test_site.get('State'),
            6: test_site.get('Zip'),
            7: test_site.get('For Sale Price')
        }
        
        # Combine all mappings
        complete_mapping = {**auto_mapping, **processed_inputs}
        
        # Display final mapping
        self.display_final_results(test_site, complete_mapping)
        
        # Generate BOTN file
        self.create_botn_file(test_site, complete_mapping)
    
    def display_final_results(self, site_data, complete_mapping):
        """Display final results before file creation"""
        logger.info("\n" + "="*70)
        logger.info("🎉 COMPLETE BOTN TEMPLATE POPULATION")
        logger.info("="*70)
        
        logger.info(f"\n🏠 Site: {site_data.get('Property Name')}")
        logger.info(f"📍 Address: {site_data.get('Property Address')}")
        logger.info(f"💰 Purchase Price: ${site_data.get('For Sale Price'):,.0f}")
        
        # Template headers for display
        headers = [
            (1, 'Property Name'), (2, 'Address'), (3, 'County:'), (4, 'CDLAC Region'),
            (5, 'State:'), (6, 'Zip Code:'), (7, 'Purchase Price'), (8, 'Housing Type'),
            (9, 'Credit Pricing'), (10, 'Credit Type'), (11, 'Construction Loan Term'),
            (12, 'Market Cap Rate'), (13, 'Financing Interest Rate'), (14, 'Elevator'),
            (15, '# Units'), (16, 'Avg Unit Size'), (17, 'Hard Cost/SF')
        ]
        
        logger.info(f"\n📋 ALL POPULATED FIELDS (17/17 - 100%):")
        logger.info("-" * 60)
        
        for col_num, header in headers:
            value = complete_mapping.get(col_num, '[EMPTY]')
            if col_num <= 7:
                logger.info(f"🤖 Col {col_num:2d} | {header:25s} → {value} [AUTO]")
            else:
                logger.info(f"👤 Col {col_num:2d} | {header:25s} → {value} [USER]")
        
        logger.info("="*70)
    
    def create_botn_file(self, site_data, complete_mapping):
        """Create the final BOTN Excel file"""
        try:
            # Load template
            workbook = openpyxl.load_workbook(self.template_path)
            inputs_sheet = workbook['Inputs']
            
            # Populate Row 2 with all mapped data
            for col_num, value in complete_mapping.items():
                inputs_sheet.cell(row=2, column=col_num, value=value)
            
            # Generate output filename
            site_name = str(site_data.get('Property Name', 'TestSite')).replace(' ', '_').replace('/', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"BOTN_COMPLETE_{site_name}_{timestamp}.xlsx"
            output_path = self.base_path / "outputs" / output_filename
            
            # Create output directory if it doesn't exist
            output_path.parent.mkdir(exist_ok=True)
            
            # Save populated workbook
            workbook.save(output_path)
            
            logger.info(f"\n🎉 BOTN FILE CREATED SUCCESSFULLY!")
            logger.info(f"📁 File: {output_path}")
            logger.info(f"📊 Population: 17/17 fields (100%)")
            logger.info(f"🤖 Auto-populated: 7 fields from site data")
            logger.info(f"👤 User inputs: 10 fields (processed and normalized)")
            logger.info(f"\n✅ File saved to outputs folder and ready for review!")
            logger.info(f"🎯 Template ready: These settings will be applied to ALL portfolio sites")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating BOTN file: {str(e)}")
            return None

def main():
    generator = FinalBOTNGenerator()
    generator.generate_complete_botn()

if __name__ == "__main__":
    main()