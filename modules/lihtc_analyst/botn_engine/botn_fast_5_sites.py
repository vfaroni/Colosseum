#!/usr/bin/env python3
"""
Fast 5-Site BOTN Generator - Scale the successful single permission approach to 5 sites
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

class Fast5SiteBOTNGenerator:
    """Generate 5 BOTNs using the fast xlwings approach that worked for single site"""
    
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
    
    def get_user_inputs(self):
        """Get user inputs for all sites"""
        logger.info("\n" + "="*70)
        logger.info("🎯 USER INPUT COLLECTION FOR 5-SITE BATCH")
        logger.info("="*70)
        logger.info("These inputs will be applied to all 5 sites consistently")
        
        # For testing, use pre-configured inputs
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
        
        logger.info(f"📋 Housing Type: {user_inputs['housing_type']}")
        logger.info(f"💰 Credit Pricing: {user_inputs['credit_pricing']}")
        logger.info(f"🏦 Credit Type: {user_inputs['credit_type']}")
        logger.info(f"📅 Loan Term: {user_inputs['loan_term']} months")
        logger.info(f"📊 Cap Rate: {user_inputs['cap_rate']}")
        logger.info(f"💸 Interest Rate: {user_inputs['interest_rate']}")
        logger.info(f"🏢 Elevator: {user_inputs['elevator']}")
        logger.info(f"💵 Default Purchase Price: ${user_inputs['purchase_price']:,}")
        logger.info(f"🏠 Units: {user_inputs['units']}")
        logger.info(f"📏 Unit Size: {user_inputs['unit_size']} sq ft")
        logger.info(f"🔨 Hard Cost: ${user_inputs['hard_cost']}/sq ft")
        
        return user_inputs
    
    def create_one_site_fast(self, site_data, user_inputs, site_index):
        """Create one site BOTN as fast as possible - same approach that worked"""
        
        site_name = str(site_data.get('Property Name', 'Site')).replace(' ', '_').replace('/', '_')
        if pd.isna(site_name) or site_name.lower() == 'nan':
            site_name = f'Site_{site_index}'
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"FAST5_{site_name}_{timestamp}_{site_index:03d}.xlsx"
        output_path = self.base_path / "outputs" / output_filename
        
        try:
            logger.info(f"🔧 Processing Site {site_index + 1}/5: {site_name}")
            
            # Copy template
            shutil.copy2(self.template_path, output_path)
            
            # Open Excel with minimal settings - EXACT same approach that worked
            app = xw.App(visible=False, add_book=False)
            app.display_alerts = False  # Disable alerts
            app.screen_updating = False  # Disable screen updates
            
            wb = app.books.open(str(output_path))
            inputs_sheet = wb.sheets['Inputs']
            
            # Determine purchase price
            site_price = self.clean_data_value(site_data.get('For Sale Price', 0))
            if site_price and site_price != '' and site_price != 0:
                purchase_price = float(site_price)
            else:
                purchase_price = user_inputs['purchase_price']
            
            # Populate row 2 as fast as possible - EXACT same approach
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
            
            # Set all values at once using range - EXACT same approach
            range_address = "A2:Q2"
            inputs_sheet.range(range_address).value = row_2_data
            
            # Save and close immediately - EXACT same approach
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
    
    def generate_5_sites_fast(self):
        """Generate BOTNs for 5 sites using the fast approach that worked"""
        
        logger.info("\n" + "="*70)
        logger.info("🚀 FAST 5-SITE BOTN GENERATION")
        logger.info("="*70)
        logger.info("Strategy: Use EXACT same approach that worked for 1 site, repeat 5 times")
        
        # Get user inputs
        user_inputs = self.get_user_inputs()
        
        # Load site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        
        # Select first 5 sites
        sites_to_process = df.head(5)
        
        logger.info(f"\n📊 Processing {len(sites_to_process)} sites:")
        for idx, (_, site) in enumerate(sites_to_process.iterrows()):
            logger.info(f"  {idx + 1}. {site.get('Property Name', f'Site_{idx}')}")
        
        successful_outputs = []
        start_time = time.time()
        
        # Process each site individually - same as single site approach
        for idx, (_, site) in enumerate(sites_to_process.iterrows()):
            logger.info(f"\n--- PROCESSING SITE {idx + 1}/5 ---")
            
            site_start_time = time.time()
            output_path = self.create_one_site_fast(site, user_inputs, idx)
            site_end_time = time.time()
            
            if output_path:
                successful_outputs.append(output_path)
                logger.info(f"⚡ Site {idx + 1} completed in {site_end_time - site_start_time:.2f} seconds")
            else:
                logger.error(f"❌ Site {idx + 1} failed")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Report results
        logger.info("\n" + "="*70)
        logger.info("📈 5-SITE GENERATION RESULTS")
        logger.info("="*70)
        logger.info(f"✅ Successful: {len(successful_outputs)}/5 sites")
        logger.info(f"⏱️  Total Time: {total_time:.2f} seconds")
        logger.info(f"⚡ Average per Site: {total_time/5:.2f} seconds")
        
        if len(successful_outputs) == 5:
            logger.info(f"\n🎉 ALL 5 SITES GENERATED SUCCESSFULLY!")
            logger.info(f"✅ Ready to scale to 50 sites using same approach")
            logger.info(f"📁 Files created in: {self.base_path / 'outputs'}")
        else:
            logger.error(f"\n❌ Only {len(successful_outputs)}/5 sites successful")
            logger.error(f"🔍 Check errors above for failed sites")
        
        return len(successful_outputs) == 5

def main():
    generator = Fast5SiteBOTNGenerator()
    success = generator.generate_5_sites_fast()
    
    if success:
        logger.info("\n🎯 NEXT STEP: Scale this approach to 50 sites")
    else:
        logger.error("\n🔧 NEXT STEP: Debug failed sites before scaling")

if __name__ == "__main__":
    main()