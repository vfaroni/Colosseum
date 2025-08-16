#!/usr/bin/env python3
"""
Single Session 5-Site BOTN Generator - One Excel session, process all files
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

class SingleSessionBOTNGenerator:
    """Generate 5 BOTNs using ONE Excel session to avoid repeated permission prompts"""
    
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
    
    def prepare_all_files_first(self, sites_data):
        """Pre-create all template copies before opening Excel"""
        output_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info("🔧 Step 1: Pre-creating all template copies...")
        
        for idx, (_, site) in enumerate(sites_data.iterrows()):
            site_name = str(site.get('Property Name', 'Site')).replace(' ', '_').replace('/', '_')
            if pd.isna(site_name) or site_name.lower() == 'nan':
                site_name = f'Site_{idx}'
                
            output_filename = f"SESSION5_{site_name}_{timestamp}_{idx:03d}.xlsx"
            output_path = self.base_path / "outputs" / output_filename
            
            # Copy template
            shutil.copy2(self.template_path, output_path)
            output_paths.append(output_path)
            logger.info(f"  📋 Prepared: {output_filename}")
        
        return output_paths
    
    def generate_5_sites_single_session(self):
        """Generate 5 BOTNs in a single Excel session"""
        
        logger.info("\n" + "="*70)
        logger.info("⚡ SINGLE SESSION 5-SITE BOTN GENERATION")
        logger.info("="*70)
        logger.info("Strategy: ONE Excel session, process all 5 files sequentially")
        
        # User inputs (pre-configured for testing)
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
        
        # Load site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        sites_to_process = df.head(5)
        
        logger.info(f"📊 Sites to process:")
        for idx, (_, site) in enumerate(sites_to_process.iterrows()):
            logger.info(f"  {idx + 1}. {site.get('Property Name', f'Site_{idx}')}")
        
        # Step 1: Prepare all files
        output_paths = self.prepare_all_files_first(sites_to_process)
        
        # Step 2: Open ONE Excel session and process all files
        logger.info("\n🔧 Step 2: Opening single Excel session (permission needed ONCE)...")
        
        successful_outputs = []
        start_time = time.time()
        
        try:
            # Start ONE Excel application
            app = xw.App(visible=False, add_book=False)
            app.display_alerts = False
            app.screen_updating = False
            
            logger.info("✅ Excel session started successfully!")
            
            # Process each file in the SAME session
            for idx, ((_, site), output_path) in enumerate(zip(sites_to_process.iterrows(), output_paths)):
                logger.info(f"\n--- PROCESSING SITE {idx + 1}/5 IN SAME SESSION ---")
                
                try:
                    site_start_time = time.time()
                    
                    # Open file in existing session (should not prompt for permission)
                    wb = app.books.open(str(output_path))
                    inputs_sheet = wb.sheets['Inputs']
                    
                    # Determine purchase price
                    site_price = self.clean_data_value(site.get('For Sale Price', 0))
                    if site_price and site_price != '' and site_price != 0:
                        purchase_price = float(site_price)
                    else:
                        purchase_price = user_inputs['purchase_price']
                    
                    # Populate row 2
                    row_2_data = [
                        self.clean_data_value(site.get('Property Name', '')),
                        self.clean_data_value(site.get('Property Address', '')),
                        self.get_template_county_format(self.clean_data_value(site.get('County Name', ''))),
                        self.get_cdlac_region(self.clean_data_value(site.get('County Name'))),
                        self.clean_data_value(site.get('State', '')),
                        self.clean_data_value(site.get('Zip', '')),
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
                    
                    # Set all values at once
                    inputs_sheet.range("A2:Q2").value = row_2_data
                    
                    # Save and close this file (but keep session open)
                    wb.save()
                    wb.close()
                    
                    site_end_time = time.time()
                    successful_outputs.append(output_path)
                    
                    logger.info(f"✅ Site {idx + 1}: {output_path.name} completed in {site_end_time - site_start_time:.2f} seconds")
                    
                except Exception as e:
                    logger.error(f"❌ Site {idx + 1} failed: {str(e)}")
                    try:
                        if 'wb' in locals():
                            wb.close()
                    except:
                        pass
            
            # Close Excel session after ALL files processed
            app.quit()
            logger.info("✅ Excel session closed")
            
        except Exception as e:
            logger.error(f"❌ Excel session failed: {str(e)}")
            try:
                if 'app' in locals():
                    app.quit()
            except:
                pass
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Report results
        logger.info("\n" + "="*70)
        logger.info("📈 SINGLE SESSION RESULTS")
        logger.info("="*70)
        logger.info(f"✅ Successful: {len(successful_outputs)}/5 sites")
        logger.info(f"⏱️  Total Time: {total_time:.2f} seconds")
        logger.info(f"⚡ Average per Site: {total_time/5:.2f} seconds")
        logger.info(f"🎯 Permission Prompts: Should be only 1 (for Excel session)")
        
        if len(successful_outputs) == 5:
            logger.info(f"\n🎉 ALL 5 SITES GENERATED IN SINGLE SESSION!")
            logger.info(f"✅ This approach eliminates repeated permission prompts")
            logger.info(f"🚀 Ready to scale to 50 sites using same single-session approach")
        else:
            logger.error(f"\n❌ Only {len(successful_outputs)}/5 sites successful")
        
        return len(successful_outputs) == 5

def main():
    generator = SingleSessionBOTNGenerator()
    success = generator.generate_5_sites_single_session()
    
    if success:
        logger.info("\n🎯 SUCCESS: Single session approach works - ready for 50 sites!")
    else:
        logger.error("\n🔧 ISSUE: Debug single session approach before scaling")

if __name__ == "__main__":
    main()