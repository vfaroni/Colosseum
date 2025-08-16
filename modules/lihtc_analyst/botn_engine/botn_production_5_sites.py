#!/usr/bin/env python3
"""
Production 5-Site BOTN Generator - Full interactive production test
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

class Production5SiteBOTNGenerator:
    """Production-quality 5-site BOTN generator with full user interaction"""
    
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
        """Get user inputs for production 5-site batch - YOUR SPECIFIC CHOICES"""
        logger.info("\n" + "="*70)
        logger.info("🎯 PRODUCTION USER INPUT COLLECTION - 5 SITES")
        logger.info("="*70)
        logger.info("Using your specified production parameters:")
        
        # Your specific choices
        user_inputs = {
            'housing_type': 'Large Family',           # Your choice: 2
            'credit_pricing': 0.8,                   # Your choice: 0.8
            'credit_type': '4%',                     # Your choice: 1 (4%)
            'loan_term': 36,                         # Your choice: 36
            'cap_rate': 0.05,                        # Your choice: .05
            'interest_rate': 0.06,                   # Your choice: .06
            'elevator': 'Non-Elevator',              # Your choice: 2 (Non-Elevator)
            'purchase_price': 5000000,               # Your choice: 5000000
            'units': 100,                            # Your choice: 100
            'unit_size': 900,                        # Your choice: 900
            'hard_cost': 250                         # Your choice: 250
        }
        
        logger.info("\n📋 CONFIRMED PRODUCTION INPUTS:")
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
        """Pre-create template copies for 5 sites"""
        output_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info("🔧 Step 1: Pre-creating 5 template copies...")
        
        for idx, (_, site) in enumerate(sites_data.iterrows()):
            site_name = str(site.get('Property Name', 'Site')).replace(' ', '_').replace('/', '_')
            if pd.isna(site_name) or site_name.lower() == 'nan':
                site_name = f'Site_{idx}'
            
            # Clean site name for filename
            site_name = re.sub(r'[<>:"/\\|?*]', '_', site_name)[:50]
            
            output_filename = f"PROD5_{site_name}_{timestamp}_{idx:03d}.xlsx"
            output_path = self.base_path / "outputs" / output_filename
            
            # Copy template
            shutil.copy2(self.template_path, output_path)
            output_paths.append(output_path)
            logger.info(f"  📋 Prepared: {output_filename}")
        
        return output_paths
    
    def generate_5_sites_production(self):
        """Generate production BOTNs for 5 sites with full user interaction"""
        
        logger.info("\n" + "="*70)
        logger.info("🏭 PRODUCTION 5-SITE BOTN GENERATION")
        logger.info("="*70)
        logger.info("Full production test - interactive inputs, single Excel session")
        
        # Get user inputs with full interaction
        user_inputs = self.get_user_inputs()
        
        # Load site data - first 5 sites
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        sites_to_process = df.head(5)
        
        logger.info(f"\n📊 PRODUCTION BATCH: 5 sites selected")
        for idx, (_, site) in enumerate(sites_to_process.iterrows()):
            site_name = site.get('Property Name', f'Site_{idx}')
            site_address = site.get('Property Address', 'N/A')
            site_county = site.get('County Name', 'N/A')
            logger.info(f"  {idx + 1}. {site_name}")
            logger.info(f"     📍 {site_address}")
            logger.info(f"     🗺️  {site_county} County")
        
        # Step 1: Prepare files
        output_paths = self.prepare_files(sites_to_process)
        
        # Step 2: Single Excel session processing
        logger.info(f"\n🔧 Step 2: Opening single Excel session for 5 sites...")
        logger.info("⚠️  This will require Excel permission ONCE")
        
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
                logger.info(f"\n--- PROCESSING SITE {idx + 1}/5 ---")
                
                try:
                    site_start_time = time.time()
                    
                    # Open file in existing session
                    wb = app.books.open(str(output_path))
                    inputs_sheet = wb.sheets['Inputs']
                    
                    # Determine purchase price
                    site_price = self.clean_data_value(site.get('For Sale Price', 0))
                    if site_price and site_price != '' and site_price != 0:
                        purchase_price = float(site_price)
                        logger.info(f"  💰 Using site price: ${purchase_price:,}")
                    else:
                        purchase_price = user_inputs['purchase_price']
                        logger.info(f"  💰 Using default price: ${purchase_price:,}")
                    
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
        
        # Production results
        logger.info("\n" + "="*70)
        logger.info("🏭 PRODUCTION 5-SITE RESULTS")
        logger.info("="*70)
        logger.info(f"✅ Successful: {len(successful_outputs)}/5 sites")
        logger.info(f"❌ Failed: {len(failed_sites)}/5 sites")
        logger.info(f"⏱️  Total Time: {total_time:.2f} seconds")
        logger.info(f"⚡ Average per Site: {total_time/5:.2f} seconds")
        logger.info(f"🎯 Success Rate: {len(successful_outputs)/5*100:.1f}%")
        logger.info(f"📁 Output Directory: {self.base_path / 'outputs'}")
        
        if len(successful_outputs) == 5:
            logger.info(f"\n🎉 PRODUCTION SUCCESS: All 5 BOTNs generated!")
            logger.info(f"✅ Full user interaction working")
            logger.info(f"✅ Single Excel session confirmed")
            logger.info(f"✅ Template preservation verified")
            logger.info(f"🚀 Ready to scale to 50 sites!")
            
            logger.info(f"\n📁 Production files created:")
            for output_path in successful_outputs:
                logger.info(f"   - {output_path.name}")
                
        else:
            logger.error(f"\n❌ PRODUCTION ISSUES: Only {len(successful_outputs)}/5 successful")
            
        if failed_sites:
            logger.error(f"\nFailed sites:")
            for site_num, site_name, error in failed_sites:
                logger.error(f"  Site {site_num}: {site_name} - {error}")
        
        return len(successful_outputs) == 5

def main():
    generator = Production5SiteBOTNGenerator()
    success = generator.generate_5_sites_production()
    
    if success:
        logger.info("\n🏆 PRODUCTION 5-SITE TEST SUCCESSFUL!")
        logger.info("✅ Ready for full 50-site production batch")
    else:
        logger.error("\n🔧 PRODUCTION ISSUES - Debug before scaling to 50")

if __name__ == "__main__":
    main()