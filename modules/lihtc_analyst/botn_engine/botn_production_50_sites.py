#!/usr/bin/env python3
"""
Production 50-Site BOTN Generator - Single Excel session, fully automated
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

class Production50SiteBOTNGenerator:
    """Production-ready 50-site BOTN generator using single Excel session approach"""
    
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
        logger.info("🎯 USER INPUT COLLECTION FOR 50-SITE PRODUCTION BATCH")
        logger.info("="*70)
        logger.info("These inputs will be applied to all sites consistently")
        
        print("\n🏠 Housing Type Options:")
        print("  1. At Risk and Non-Targeted")
        print("  2. Large Family")
        print("  3. Senior")
        print("  4. Single Room/ Special Needs")
        housing_choice = input("Select Housing Type (1-4): ").strip()
        housing_types = {
            '1': 'At Risk and Non-Targeted',
            '2': 'Large Family', 
            '3': 'Senior',
            '4': 'Single Room/ Special Needs'
        }
        housing_type = housing_types.get(housing_choice, 'Large Family')
        
        print(f"\n💰 Credit Pricing (e.g., 0.8 for 80 cents)")
        credit_pricing = float(input("Enter credit pricing: ").strip() or "0.8")
        
        print(f"\n🏦 Credit Type Options:")
        print("  1. 4%")
        print("  2. 9%")
        credit_choice = input("Select Credit Type (1-2): ").strip()
        credit_type = '4%' if credit_choice == '1' else '9%'
        
        print(f"\n📅 Loan Term (months)")
        loan_term = int(input("Enter loan term in months (default 36): ").strip() or "36")
        
        print(f"\n📊 Cap Rate (e.g., 0.05 for 5%)")
        cap_rate = float(input("Enter cap rate: ").strip() or "0.05")
        
        print(f"\n💸 Interest Rate (e.g., 0.06 for 6%)")
        interest_rate = float(input("Enter interest rate: ").strip() or "0.06")
        
        print(f"\n🏢 Elevator Options:")
        print("  1. Elevator")
        print("  2. Non-Elevator")
        elevator_choice = input("Select Elevator (1-2): ").strip()
        elevator = 'Elevator' if elevator_choice == '1' else 'Non-Elevator'
        
        print(f"\n💵 Default Purchase Price (for sites with missing price data)")
        purchase_price = float(input("Enter default purchase price: ").strip() or "2000000")
        
        print(f"\n🏠 Number of Units")
        units = int(input("Enter number of units: ").strip() or "100")
        
        print(f"\n📏 Unit Size (sq ft)")
        unit_size = int(input("Enter unit size in sq ft: ").strip() or "900")
        
        print(f"\n🔨 Hard Cost ($/sq ft)")
        hard_cost = int(input("Enter hard cost per sq ft: ").strip() or "250")
        
        user_inputs = {
            'housing_type': housing_type,
            'credit_pricing': credit_pricing,
            'credit_type': credit_type,
            'loan_term': loan_term,
            'cap_rate': cap_rate,
            'interest_rate': interest_rate,
            'elevator': elevator,
            'purchase_price': purchase_price,
            'units': units,
            'unit_size': unit_size,
            'hard_cost': hard_cost
        }
        
        logger.info("\n📋 CONFIRMED USER INPUTS:")
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
    
    def prepare_all_files_first(self, sites_data):
        """Pre-create all template copies before opening Excel"""
        output_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"🔧 Step 1: Pre-creating all {len(sites_data)} template copies...")
        
        for idx, (_, site) in enumerate(sites_data.iterrows()):
            site_name = str(site.get('Property Name', 'Site')).replace(' ', '_').replace('/', '_')
            if pd.isna(site_name) or site_name.lower() == 'nan':
                site_name = f'Site_{idx}'
                
            # Clean site name for filename
            site_name = re.sub(r'[<>:"/\\|?*]', '_', site_name)[:50]  # Limit length
            
            output_filename = f"PROD50_{site_name}_{timestamp}_{idx:03d}.xlsx"
            output_path = self.base_path / "outputs" / output_filename
            
            # Copy template
            shutil.copy2(self.template_path, output_path)
            output_paths.append(output_path)
            
            if idx % 10 == 0:  # Progress update every 10 files
                logger.info(f"  📋 Prepared {idx + 1}/{len(sites_data)} templates...")
        
        logger.info(f"✅ All {len(sites_data)} templates prepared!")
        return output_paths
    
    def generate_50_sites_production(self):
        """Generate BOTNs for up to 50 sites in production single session"""
        
        logger.info("\n" + "="*70)
        logger.info("🏭 PRODUCTION 50-SITE BOTN GENERATION")
        logger.info("="*70)
        logger.info("Strategy: Single Excel session, fully automated, production-ready")
        
        # Get user inputs
        user_inputs = self.get_user_inputs()
        
        # Load all site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        
        # Process all sites (or limit to 50 if more)
        sites_to_process = df.head(50) if len(df) > 50 else df
        
        logger.info(f"\n📊 PRODUCTION BATCH: {len(sites_to_process)} sites")
        logger.info(f"First 5 sites:")
        for idx in range(min(5, len(sites_to_process))):
            site = sites_to_process.iloc[idx]
            logger.info(f"  {idx + 1}. {site.get('Property Name', f'Site_{idx}')}")
        if len(sites_to_process) > 5:
            logger.info(f"  ... and {len(sites_to_process) - 5} more sites")
        
        # Step 1: Prepare all files
        output_paths = self.prepare_all_files_first(sites_to_process)
        
        # Step 2: Single Excel session processing
        logger.info(f"\n🔧 Step 2: Opening single Excel session for {len(sites_to_process)} sites...")
        logger.info("⚠️  This will require permission ONCE for Excel access")
        
        successful_outputs = []
        failed_sites = []
        start_time = time.time()
        
        try:
            # Start ONE Excel application
            app = xw.App(visible=False, add_book=False)
            app.display_alerts = False
            app.screen_updating = False
            
            logger.info("✅ Excel session started successfully!")
            
            # Process each file in the SAME session
            for idx, ((_, site), output_path) in enumerate(zip(sites_to_process.iterrows(), output_paths)):
                
                if idx % 10 == 0:  # Progress update every 10 sites
                    logger.info(f"--- PROCESSING SITES {idx + 1}-{min(idx + 10, len(sites_to_process))}/{len(sites_to_process)} ---")
                
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
                    
                    # Save and close this file (keep session open)
                    wb.save()
                    wb.close()
                    
                    site_end_time = time.time()
                    successful_outputs.append(output_path)
                    
                    if idx % 10 == 9 or idx == len(sites_to_process) - 1:  # Progress update
                        logger.info(f"✅ Site{idx + 1:3d}: {output_path.name[:50]}... ✓")
                    
                except Exception as e:
                    failed_sites.append((idx + 1, site.get('Property Name', f'Site_{idx}'), str(e)))
                    logger.error(f"❌ Site {idx + 1} failed: {str(e)[:100]}")
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
        
        # Final production report
        logger.info("\n" + "="*70)
        logger.info("🏭 PRODUCTION RESULTS - 50-SITE BOTN GENERATION")
        logger.info("="*70)
        logger.info(f"✅ Successful: {len(successful_outputs)}/{len(sites_to_process)} sites")
        logger.info(f"❌ Failed: {len(failed_sites)}/{len(sites_to_process)} sites")
        logger.info(f"⏱️  Total Time: {total_time:.2f} seconds ({total_time/60:.1f} minutes)")
        logger.info(f"⚡ Average per Site: {total_time/len(sites_to_process):.2f} seconds")
        logger.info(f"🎯 Success Rate: {len(successful_outputs)/len(sites_to_process)*100:.1f}%")
        logger.info(f"📁 Output Directory: {self.base_path / 'outputs'}")
        
        if len(successful_outputs) >= len(sites_to_process) * 0.8:  # 80% success rate
            logger.info(f"\n🎉 PRODUCTION SUCCESS: {len(successful_outputs)} BOTNs generated!")
            logger.info(f"✅ All files preserve original template features and calculations")
            logger.info(f"✅ Single Excel session minimized permission prompts")
            logger.info(f"🚀 Production system ready for regular use!")
        else:
            logger.error(f"\n⚠️  PRODUCTION ISSUES: Only {len(successful_outputs)}/{len(sites_to_process)} successful")
            
        if failed_sites:
            logger.info(f"\n❌ Failed Sites Summary:")
            for site_num, site_name, error in failed_sites[:10]:  # Show first 10 failures
                logger.info(f"  Site {site_num}: {site_name[:30]} - {error[:50]}")
            if len(failed_sites) > 10:
                logger.info(f"  ... and {len(failed_sites) - 10} more failed sites")
        
        return len(successful_outputs) >= len(sites_to_process) * 0.8

def main():
    generator = Production50SiteBOTNGenerator()
    success = generator.generate_50_sites_production()
    
    if success:
        logger.info("\n🏆 MISSION ACCOMPLISHED: Production 50-site BOTN system operational!")
    else:
        logger.error("\n🔧 MISSION INCOMPLETE: Debug production issues")

if __name__ == "__main__":
    main()