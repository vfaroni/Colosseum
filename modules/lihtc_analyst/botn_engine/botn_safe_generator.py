#!/usr/bin/env python3
"""
Safe BOTN Generator - Preserves Excel integrity and avoids corruption
"""

import pandas as pd
import openpyxl
from pathlib import Path
import logging
from datetime import datetime
import shutil
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafeBOTNGenerator:
    """Safe BOTN generator that preserves Excel file integrity"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        
    def process_user_inputs(self, raw_inputs):
        """Process and normalize user inputs with proper data types"""
        processed = {}
        
        input_mapping = {
            8: ('Housing Type', raw_inputs[0]),
            9: ('Credit Pricing', raw_inputs[1]),
            10: ('Credit Type', raw_inputs[2]),
            11: ('Construction Loan Term', raw_inputs[3]),
            12: ('Market Cap Rate', raw_inputs[4]),
            13: ('Financing Interest Rate', raw_inputs[5]),
            14: ('Elevator', raw_inputs[6]),
            15: ('# Units', raw_inputs[7]),
            16: ('Avg Unit Size', raw_inputs[8]),
            17: ('Hard Cost/SF', raw_inputs[9])
        }
        
        for col_num, (field_name, raw_value) in input_mapping.items():
            processed_value = self.normalize_input(field_name, raw_value)
            processed[col_num] = processed_value
            logger.info(f"Processed {field_name}: '{raw_value}' → {processed_value}")
        
        return processed
    
    def normalize_input(self, field_name, raw_value):
        """Normalize input values with correct data types for Excel"""
        raw_str = str(raw_value).strip()
        
        if 'Housing Type' in field_name:
            return raw_str.title()
        elif 'Credit Pricing' in field_name:
            if 'cent' in raw_str.lower():
                number = re.findall(r'\d+', raw_str)[0]
                return float(number) / 100
            elif '%' in raw_str:
                number = float(re.findall(r'[\d.]+', raw_str)[0])
                return number / 100
            else:
                return float(raw_str)
        elif 'Credit Type' in field_name:
            # Keep as string but normalize format
            if '%' in raw_str:
                return raw_str  # "4%" stays "4%"
            else:
                return f"{raw_str}%"  # Add % if missing
        elif 'Loan Term' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)
        elif 'Rate' in field_name:
            if '%' in raw_str:
                number = float(re.findall(r'[\d.]+', raw_str)[0])
                return number / 100
            else:
                return float(raw_str)
        elif 'Elevator' in field_name:
            # Match template format
            if raw_str.lower() in ['no', 'none', 'false']:
                return "Non-Elevator"
            else:
                return "Elevator"
        elif 'Units' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)
        elif 'Unit Size' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)
        elif 'Hard Cost' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)
        else:
            return raw_str
    
    def get_cdlac_region(self, county_name):
        """Get CDLAC region using dropdown values"""
        cdlac_regions = {
            'San Francisco': 'San Francisco County',
            'Alameda': 'East Bay Region', 'Contra Costa': 'East Bay Region',
            'San Mateo': 'South & West Bay Region', 'Santa Clara': 'South & West Bay Region',
            'Santa Cruz': 'South & West Bay Region',
            'Lake': 'Northern Region', 'Marin': 'Northern Region', 'Napa': 'Northern Region',
            'Solano': 'Northern Region', 'Sonoma': 'Northern Region', 'Butte': 'Northern Region', 
            'Colusa': 'Northern Region', 'El Dorado': 'Northern Region', 'Glenn': 'Northern Region', 
            'Nevada': 'Northern Region', 'Placer': 'Northern Region', 'Sacramento': 'Northern Region', 
            'Sutter': 'Northern Region', 'Tehama': 'Northern Region', 'Yolo': 'Northern Region', 
            'Yuba': 'Northern Region', 'Alpine': 'Northern Region', 'Amador': 'Northern Region', 
            'Calaveras': 'Northern Region', 'Del Norte': 'Northern Region', 'Humboldt': 'Northern Region', 
            'Inyo': 'Northern Region', 'Lassen': 'Northern Region', 'Madera': 'Northern Region', 
            'Mariposa': 'Northern Region', 'Mendocino': 'Northern Region', 'Modoc': 'Northern Region', 
            'Mono': 'Northern Region', 'Plumas': 'Northern Region', 'Shasta': 'Northern Region', 
            'Sierra': 'Northern Region', 'Siskiyou': 'Northern Region', 'Tuolumne': 'Northern Region', 
            'Trinity': 'Northern Region',
            'Fresno': 'Central Valley Region', 'Kern': 'Central Valley Region', 'Kings': 'Central Valley Region', 
            'Merced': 'Central Valley Region', 'San Joaquin': 'Central Valley Region', 
            'Stanislaus': 'Central Valley Region', 'Tulare': 'Central Valley Region',
            'Monterey': 'Central Coast Region', 'San Benito': 'Central Coast Region', 
            'San Luis Obispo': 'Central Coast Region', 'Santa Barbara': 'Central Coast Region', 
            'Ventura': 'Central Coast Region',
            'Los Angeles': 'Los Angeles County',
            'Orange': 'Orange County',
            'Riverside': 'Inland Empire Region', 'San Bernardino': 'Inland Empire Region',
            'San Diego': 'San Diego County', 'Imperial': 'San Diego County'
        }
        return cdlac_regions.get(county_name, None)
    
    def create_safe_botn(self, site_data, user_inputs):
        """Create BOTN using safe approach that preserves Excel integrity"""
        try:
            # Step 1: Create temporary copy of template
            temp_file = self.base_path / f"temp_botn_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            shutil.copy2(self.template_path, temp_file)
            
            # Step 2: Load the copy (preserves all Excel features)
            workbook = openpyxl.load_workbook(temp_file)
            inputs_sheet = workbook['Inputs']
            
            # Step 3: Prepare all data with correct types
            complete_mapping = {
                1: str(site_data.get('Property Name', '')),
                2: str(site_data.get('Property Address', '')),
                3: str(site_data.get('County Name', '')),
                4: str(self.get_cdlac_region(site_data.get('County Name'))),
                5: str(site_data.get('State', '')),
                6: site_data.get('Zip', ''),  # Keep as is - could be int or string
                7: float(site_data.get('For Sale Price', 0)) if site_data.get('For Sale Price') else 0,
                **user_inputs
            }
            
            # Step 4: Apply data with proper Excel formatting
            for col_num, value in complete_mapping.items():
                if value is not None:
                    cell = inputs_sheet.cell(row=2, column=col_num)
                    cell.value = value
                    
                    # Apply proper number formatting for specific fields
                    if col_num == 7:  # Purchase Price
                        cell.number_format = '#,##0'
                    elif col_num in [9, 12, 13]:  # Rate fields (Credit Pricing, Market Cap, Interest Rate)
                        cell.number_format = '0.00'
            
            # Step 5: Generate final filename
            site_name = str(site_data.get('Property Name', 'Site')).replace(' ', '_').replace('/', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"BOTN_SAFE_{site_name}_{timestamp}.xlsx"
            output_path = self.base_path / "outputs" / output_filename
            
            # Step 6: Save final file
            workbook.save(output_path)
            workbook.close()
            
            # Step 7: Clean up temp file
            temp_file.unlink()
            
            logger.info(f"✅ SAFE BOTN CREATED: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating safe BOTN: {str(e)}")
            # Clean up temp file if it exists
            if 'temp_file' in locals() and temp_file.exists():
                temp_file.unlink()
            return None
    
    def generate_safe_botn(self):
        """Generate BOTN using safe approach"""
        
        # User inputs from previous session
        user_inputs_raw = [
            "new Construction", "80 cents", "4%", "36 months", "5%", "6%", 
            "No", "100 units", "900SF", "250/SF"
        ]
        
        # Process inputs
        processed_inputs = self.process_user_inputs(user_inputs_raw)
        
        # Load site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        test_site = df.iloc[0]
        
        # Display results
        logger.info("\n" + "="*70)
        logger.info("🛡️  SAFE BOTN GENERATION")
        logger.info("="*70)
        logger.info(f"🏠 Site: {test_site.get('Property Name')}")
        logger.info(f"📍 Address: {test_site.get('Property Address')}")
        logger.info(f"🔧 Approach: Template copying + proper data types")
        
        # Create safe BOTN
        output_path = self.create_safe_botn(test_site, processed_inputs)
        
        if output_path:
            logger.info(f"\n🎉 SUCCESS: Safe BOTN created!")
            logger.info(f"📁 File: {output_path}")
            logger.info(f"🛡️  This should open without Excel corruption errors")
        else:
            logger.error("\n❌ Failed to create safe BOTN")

def main():
    generator = SafeBOTNGenerator()
    generator.generate_safe_botn()

if __name__ == "__main__":
    main()