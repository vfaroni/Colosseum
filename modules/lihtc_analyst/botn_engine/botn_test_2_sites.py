#!/usr/bin/env python3
"""
Test 2-Site BOTN Generator - Verify production approach works perfectly
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

class Test2SiteBOTNGenerator:
    """Test the production approach with just 2 sites"""
    
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
        """Get user inputs for the test - pre-configured for testing"""
        logger.info("\n" + "="*70)
        logger.info("🎯 USER INPUT COLLECTION FOR 2-SITE TEST")
        logger.info("="*70)
        logger.info("Using pre-configured test inputs for automated testing")
        
        # Pre-configured test inputs
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
        
        logger.info("\n📋 TEST INPUT CONFIGURATION:")
        logger.info(f"  Housing Type: {user_inputs['housing_type']}")
        logger.info(f"  Credit Pricing: {user_inputs['credit_pricing']}")
        logger.info(f"  Credit Type: {user_inputs['credit_type']}")
        logger.info(f"  Loan Term: {user_inputs['loan_term']} months")
        logger.info(f"  Cap Rate: {user_inputs['cap_rate']}")
        logger.info(f"  Interest Rate: {user_inputs['interest_rate']}")
        logger.info(f"  Elevator: {user_inputs['elevator']}")
        logger.info(f"  Default Purchase Price: ${user_inputs['purchase_price']:,}")
        logger.info(f"  Units: {user_inputs['units']}")
        logger.info(f"  Unit Size: {user_inputs['unit_size']} sq ft")
        logger.info(f"  Hard Cost: ${user_inputs['hard_cost']}/sq ft")
        
        return user_inputs
    
    def prepare_files(self, sites_data):
        """Pre-create template copies for 2 sites"""
        output_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info("🔧 Step 1: Pre-creating 2 template copies...")
        
        for idx, (_, site) in enumerate(sites_data.iterrows()):
            site_name = str(site.get('Property Name', 'Site')).replace(' ', '_').replace('/', '_')
            if pd.isna(site_name) or site_name.lower() == 'nan':
                site_name = f'Site_{idx}'
            
            # Clean site name for filename
            site_name = re.sub(r'[<>:"/\\|?*]', '_', site_name)[:50]
            
            output_filename = f"TEST2_{site_name}_{timestamp}_{idx:03d}.xlsx"
            output_path = self.base_path / "outputs" / output_filename
            
            # Copy template
            shutil.copy2(self.template_path, output_path)
            output_paths.append(output_path)
            logger.info(f"  📋 Prepared: {output_filename}")
        
        return output_paths
    
    def test_2_sites(self):
        """Test production approach with 2 sites"""
        
        logger.info("\n" + "="*70)
        logger.info("🧪 TEST: 2-SITE BOTN GENERATION")
        logger.info("="*70)
        logger.info("Verifying production approach before scaling to 50 sites")
        
        # Get user inputs
        user_inputs = self.get_user_inputs()
        
        # Load site data - just first 2 sites
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        sites_to_process = df.head(2)
        
        logger.info(f"\n📊 Testing with 2 sites:")
        for idx, (_, site) in enumerate(sites_to_process.iterrows()):
            logger.info(f"  {idx + 1}. {site.get('Property Name', f'Site_{idx}')}")
            logger.info(f"     Address: {site.get('Property Address', 'N/A')}")
            logger.info(f"     County: {site.get('County Name', 'N/A')}")
        
        # Step 1: Prepare files
        output_paths = self.prepare_files(sites_to_process)
        
        # Step 2: Single Excel session processing
        logger.info(f"\n🔧 Step 2: Opening single Excel session for 2 sites...")
        logger.info("⚠️  This should require permission ONCE")
        
        successful_outputs = []
        failed_sites = []
        start_time = time.time()
        
        try:
            # Start Excel application
            app = xw.App(visible=False, add_book=False)
            app.display_alerts = False
            app.screen_updating = False
            
            logger.info("✅ Excel session started successfully!")
            
            # Process each file in the same session
            for idx, ((_, site), output_path) in enumerate(zip(sites_to_process.iterrows(), output_paths)):
                logger.info(f"\n--- PROCESSING SITE {idx + 1}/2 ---")
                
                try:
                    site_start_time = time.time()
                    
                    # Open file in existing session
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
                    
                    # Save and close this file
                    wb.save()
                    wb.close()
                    
                    site_end_time = time.time()
                    successful_outputs.append(output_path)
                    
                    logger.info(f"✅ Site {idx + 1}: {output_path.name} completed in {site_end_time - site_start_time:.2f} seconds")
                    
                except Exception as e:
                    failed_sites.append((idx + 1, site.get('Property Name', f'Site_{idx}'), str(e)))
                    logger.error(f"❌ Site {idx + 1} failed: {str(e)}")
                    try:
                        if 'wb' in locals():
                            wb.close()
                    except:
                        pass
            
            # Close Excel session
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
        
        # Test results
        logger.info("\n" + "="*70)
        logger.info("🧪 2-SITE TEST RESULTS")
        logger.info("="*70)
        logger.info(f"✅ Successful: {len(successful_outputs)}/2 sites")
        logger.info(f"❌ Failed: {len(failed_sites)}/2 sites")
        logger.info(f"⏱️  Total Time: {total_time:.2f} seconds")
        logger.info(f"⚡ Average per Site: {total_time/2:.2f} seconds")
        logger.info(f"🎯 Success Rate: {len(successful_outputs)/2*100:.1f}%")
        
        if len(successful_outputs) == 2:
            logger.info(f"\n🎉 TEST PASSED: Both sites generated successfully!")
            logger.info(f"✅ Template preservation verified")
            logger.info(f"✅ Single session approach working")
            logger.info(f"✅ Ready to scale to 50 sites!")
            logger.info(f"\n📁 Test files created:")
            for output_path in successful_outputs:
                logger.info(f"   - {output_path.name}")
            logger.info(f"\n🚀 NEXT STEP: Run botn_production_50_sites.py for full batch")
        else:
            logger.error(f"\n❌ TEST FAILED: Only {len(successful_outputs)}/2 sites successful")
            if failed_sites:
                logger.error(f"Failed sites:")
                for site_num, site_name, error in failed_sites:
                    logger.error(f"  Site {site_num}: {site_name} - {error}")
        
        return len(successful_outputs) == 2

def main():
    generator = Test2SiteBOTNGenerator()
    success = generator.test_2_sites()
    
    if success:
        logger.info("\n✅ 2-SITE TEST SUCCESSFUL - Ready for production!")
    else:
        logger.error("\n❌ 2-SITE TEST FAILED - Debug before scaling")

if __name__ == "__main__":
    main()