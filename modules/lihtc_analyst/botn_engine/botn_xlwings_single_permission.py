#!/usr/bin/env python3
"""
XLWings Single Permission - Try to get permission once and process multiple files quickly
"""

import pandas as pd
import shutil
import xlwings as xw
from pathlib import Path
import logging
from datetime import datetime
import re
import numpy as np
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XLWingsSinglePermissionBOTN:
    """Try to minimize permission prompts by processing files very quickly"""
    
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
    
    def create_one_site_fast(self, site_data):
        """Create one site BOTN as fast as possible"""
        
        site_name = str(site_data.get('Property Name', 'Site')).replace(' ', '_').replace('/', '_')
        if pd.isna(site_name) or site_name.lower() == 'nan':
            site_name = 'Site'
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"FAST_BOTN_{site_name}_{timestamp}.xlsx"
        output_path = self.base_path / "outputs" / output_filename
        
        try:
            logger.info(f"🔧 Processing: {site_name}")
            
            # Copy template
            shutil.copy2(self.template_path, output_path)
            
            # Open Excel with minimal settings
            app = xw.App(visible=False, add_book=False)
            app.display_alerts = False  # Disable alerts
            app.screen_updating = False  # Disable screen updates
            
            wb = app.books.open(str(output_path))
            inputs_sheet = wb.sheets['Inputs']
            
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
            
            # Populate row 2 as fast as possible
            row_2_data = [
                self.clean_data_value(site_data.get('Property Name', '')),
                self.clean_data_value(site_data.get('Property Address', '')),
                self.get_template_county_format(self.clean_data_value(site_data.get('County Name', ''))),
                self.get_cdlac_region(self.clean_data_value(site_data.get('County Name'))),
                self.clean_data_value(site_data.get('State', '')),
                self.clean_data_value(site_data.get('Zip', '')),
                purchase_price,
                user_inputs['housing_type'],
                user_inputs['credit_pricing'],
                user_inputs['credit_type'],
                user_inputs['loan_term'],
                user_inputs['cap_rate'],
                user_inputs['interest_rate'],
                user_inputs['elevator'],
                user_inputs['units'],
                user_inputs['unit_size'],
                user_inputs['hard_cost']
            ]
            
            # Set all values at once using range
            range_address = "A2:Q2"
            inputs_sheet.range(range_address).value = row_2_data
            
            # Save and close immediately
            wb.save()
            wb.close()
            app.quit()
            
            logger.info(f"✅ Created: {output_filename}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            try:
                if 'wb' in locals():
                    wb.close()
                if 'app' in locals():
                    app.quit()
            except:
                pass
            return None
    
    def test_single_permission_approach(self):
        """Test if we can process one site with minimal permissions"""
        
        # Load site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        test_site = df.iloc[0]  # First site
        
        logger.info("\n" + "="*70)
        logger.info("⚡ TESTING FAST XLWINGS SINGLE PERMISSION")
        logger.info("="*70)
        logger.info(f"🏠 Site: {test_site.get('Property Name')}")
        logger.info(f"📍 Address: {test_site.get('Property Address')}")
        logger.info(f"🔧 Strategy: Fast processing, minimal Excel interaction")
        
        start_time = time.time()
        output_path = self.create_one_site_fast(test_site)
        end_time = time.time()
        
        if output_path:
            logger.info(f"\n🎉 SUCCESS: Fast BOTN created in {end_time - start_time:.2f} seconds!")
            logger.info(f"📁 File: {output_path}")
            logger.info(f"✅ If this worked without prompts, we can scale to 50 sites")
            logger.info(f"✅ Test by opening in Excel - should have all features preserved")
        else:
            logger.error(f"\n❌ Failed fast approach")

def main():
    generator = XLWingsSinglePermissionBOTN()
    generator.test_single_permission_approach()

if __name__ == "__main__":
    main()