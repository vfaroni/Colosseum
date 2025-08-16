#!/usr/bin/env python3
"""
Careful OpenPyXL BOTN Generator - Minimal template modification to avoid corruption
"""

import pandas as pd
import shutil
import openpyxl
from pathlib import Path
import logging
from datetime import datetime
import re
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CarefulOpenpyxlBOTNGenerator:
    """Generate BOTN using openpyxl with minimal template modification"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        
    def get_cdlac_region(self, county_name):
        """Get CDLAC region"""
        if not county_name or pd.isna(county_name) or str(county_name).lower() == 'nan':
            return 'Northern Region'
            
        cdlac_regions = {
            'Los Angeles': 'Los Angeles County',
            'Orange': 'Orange County',
            'Riverside': 'Inland Empire Region', 'San Bernardino': 'Inland Empire Region',
            'San Diego': 'San Diego County',
            'Fresno': 'Central Valley Region', 'Kern': 'Central Valley Region',
        }
        return cdlac_regions.get(str(county_name), 'Northern Region')
    
    def get_template_county_format(self, county_name):
        """Convert county name to match template format"""
        if not county_name or pd.isna(county_name) or str(county_name).lower() == 'nan':
            return 'Los Angeles County'
            
        county_str = str(county_name).strip()
        
        if county_str.endswith(' County'):
            return county_str
        
        return f"{county_str} County"
    
    def clean_data_value(self, value):
        """Clean data values"""
        if pd.isna(value) or value is None:
            return ''
        if isinstance(value, (int, float)):
            if np.isnan(value) or np.isinf(value):
                return 0
        if str(value).lower() == 'nan':
            return ''
        return value
    
    def create_careful_botn(self, site_data):
        """Create BOTN using careful openpyxl approach"""
        
        site_name = str(site_data.get('Property Name', 'Site')).replace(' ', '_').replace('/', '_')
        if pd.isna(site_name) or site_name.lower() == 'nan':
            site_name = 'Site'
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"CAREFUL_BOTN_{site_name}_{timestamp}.xlsx"
        output_path = self.base_path / "outputs" / output_filename
        
        try:
            logger.info("🔧 Step 1: Copying template...")
            shutil.copy2(self.template_path, output_path)
            
            logger.info("🔧 Step 2: Opening with openpyxl (read_only=False, keep_vba=True)...")
            # Try to preserve more of the original file structure
            workbook = openpyxl.load_workbook(output_path, keep_vba=True, data_only=False, keep_links=False)
            inputs_sheet = workbook['Inputs']
            
            logger.info("🔧 Step 3: Populating ONLY essential data in row 2...")
            
            # Test user inputs
            user_inputs = {
                'housing_type': 'Large Family',
                'credit_pricing': 0.8,
                'credit_type': '4%',
                'loan_term': 36,
                'cap_rate': 0.05,
                'interest_rate': 0.06,
                'elevator': 'Non-Elevator',
                'purchase_price': 2000000,
                'units': 100,
                'unit_size': 900,
                'hard_cost': 250
            }
            
            # Determine purchase price
            site_price = self.clean_data_value(site_data.get('For Sale Price', 0))
            if site_price and site_price != '' and site_price != 0:
                purchase_price = float(site_price)
            else:
                purchase_price = user_inputs['purchase_price']
            
            # ONLY set the values, don't touch any formatting or validation
            inputs_sheet['A2'].value = self.clean_data_value(site_data.get('Property Name', ''))
            inputs_sheet['B2'].value = self.clean_data_value(site_data.get('Property Address', ''))
            inputs_sheet['C2'].value = self.get_template_county_format(self.clean_data_value(site_data.get('County Name', '')))
            inputs_sheet['D2'].value = self.get_cdlac_region(self.clean_data_value(site_data.get('County Name')))
            inputs_sheet['E2'].value = self.clean_data_value(site_data.get('State', ''))
            inputs_sheet['F2'].value = self.clean_data_value(site_data.get('Zip', ''))
            inputs_sheet['G2'].value = purchase_price
            inputs_sheet['H2'].value = user_inputs['housing_type']
            inputs_sheet['I2'].value = user_inputs['credit_pricing']
            inputs_sheet['J2'].value = user_inputs['credit_type']
            inputs_sheet['K2'].value = user_inputs['loan_term']
            inputs_sheet['L2'].value = user_inputs['cap_rate']
            inputs_sheet['M2'].value = user_inputs['interest_rate']
            inputs_sheet['N2'].value = user_inputs['elevator']
            inputs_sheet['O2'].value = user_inputs['units']
            inputs_sheet['P2'].value = user_inputs['unit_size']
            inputs_sheet['Q2'].value = user_inputs['hard_cost']
            
            logger.info("🔧 Step 4: Saving with minimal changes...")
            # Save with template='yes' to preserve as much as possible
            workbook.save(output_path)
            workbook.close()
            
            logger.info(f"✅ Careful BOTN created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return None
    
    def test_careful_approach(self):
        """Test the careful openpyxl approach"""
        
        # Load site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        test_site = df.iloc[0]  # First site
        
        logger.info("\n" + "="*70)
        logger.info("🔬 TESTING CAREFUL OPENPYXL APPROACH")
        logger.info("="*70)
        logger.info(f"🏠 Site: {test_site.get('Property Name')}")
        logger.info(f"📍 Address: {test_site.get('Property Address')}")
        logger.info(f"🔧 Method: Openpyxl with keep_vba=True, minimal changes")
        logger.info(f"🎯 Goal: Preserve template, avoid corruption")
        
        # Create BOTN
        output_path = self.create_careful_botn(test_site)
        
        if output_path:
            logger.info(f"\n🎉 SUCCESS: Careful BOTN created!")
            logger.info(f"📁 File: {output_path}")
            logger.info(f"✅ Test by opening in Excel - should have no corruption warnings")
            logger.info(f"✅ Check if dropdowns still work")
            logger.info(f"✅ Verify all calculations function")
        else:
            logger.error("\n❌ Failed to create careful BOTN")

def main():
    generator = CarefulOpenpyxlBOTNGenerator()
    generator.test_careful_approach()

if __name__ == "__main__":
    main()