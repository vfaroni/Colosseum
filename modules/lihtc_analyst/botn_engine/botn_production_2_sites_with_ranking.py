#!/usr/bin/env python3
"""
Production 2-Site BOTN Generator with Sources & Uses Gap Ranking
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

class Production2SiteBOTNWithRanking:
    """Production 2-site BOTN generator with Sources & Uses gap ranking"""
    
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
        """Get your production parameters"""
        logger.info("\n" + "="*70)
        logger.info("🎯 PRODUCTION PARAMETERS - 2 SITES WITH RANKING")
        logger.info("="*70)
        logger.info("Using your specified production parameters:")
        
        # Your exact choices
        user_inputs = {
            'housing_type': 'Large Family',           
            'credit_pricing': 0.8,                   
            'credit_type': '4%',                     
            'loan_term': 36,                         
            'cap_rate': 0.05,                        
            'interest_rate': 0.06,                   
            'elevator': 'Non-Elevator',              
            'purchase_price': 5000000,               
            'units': 100,                            
            'unit_size': 900,                        
            'hard_cost': 250                         
        }
        
        logger.info("\n📋 YOUR PRODUCTION PARAMETERS:")
        logger.info(f"  Housing Type: {user_inputs['housing_type']}")
        logger.info(f"  Credit Pricing: {user_inputs['credit_pricing']}")
        logger.info(f"  Credit Type: {user_inputs['credit_type']}")
        logger.info(f"  Default Purchase Price: ${user_inputs['purchase_price']:,}")
        logger.info(f"  Units: {user_inputs['units']}")
        
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
            
            output_filename = f"RANKED_{site_name}_{timestamp}_{idx:03d}.xlsx"
            output_path = self.base_path / "outputs" / output_filename
            
            # Copy template
            shutil.copy2(self.template_path, output_path)
            output_paths.append(output_path)
            logger.info(f"  📋 Prepared: {output_filename}")
        
        return output_paths
    
    def read_sources_uses_gap(self, file_path):
        """Read Sources & Uses gap from cell C8"""
        try:
            app = xw.App(visible=False, add_book=False)
            app.display_alerts = False
            
            wb = app.books.open(str(file_path))
            sources_uses_sheet = wb.sheets['Sources & Uses']
            
            # Read cell C8 (the gap)
            gap_value = sources_uses_sheet.range('C8').value
            
            wb.close()
            app.quit()
            
            return gap_value if gap_value is not None else 0
            
        except Exception as e:
            logger.error(f"❌ Error reading gap from {file_path.name}: {str(e)}")
            try:
                if 'wb' in locals():
                    wb.close()
                if 'app' in locals():
                    app.quit()
            except:
                pass
            return 0
    
    def generate_and_rank_sites(self):
        """Generate BOTNs for 2 sites and rank by Sources & Uses gap"""
        
        logger.info("\n" + "="*70)
        logger.info("🏭 PRODUCTION + RANKING - 2 SITES")
        logger.info("="*70)
        logger.info("Generating BOTNs and ranking by Sources & Uses gap (cell C8)")
        
        # Get your production parameters
        user_inputs = self.get_user_inputs()
        
        # Load site data - exactly 2 sites
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        sites_to_process = df.head(2)
        
        logger.info(f"\n📊 SITES TO PROCESS:")
        site_info = []
        for idx, (_, site) in enumerate(sites_to_process.iterrows()):
            site_name = site.get('Property Name', f'Site_{idx}')
            site_address = site.get('Property Address', 'N/A')
            site_price = site.get('For Sale Price', 'N/A')
            site_info.append({
                'index': idx,
                'name': site_name,
                'address': site_address,
                'price': site_price
            })
            logger.info(f"  {idx + 1}. {site_name}")
            logger.info(f"     📍 {site_address}")
            logger.info(f"     💰 Price: ${site_price:,}" if isinstance(site_price, (int, float)) else f"     💰 Price: {site_price}")
        
        # Step 1: Prepare files
        output_paths = self.prepare_files(sites_to_process)
        
        # Step 2: Generate BOTNs
        logger.info(f"\n🔧 Step 2: Generating BOTNs...")
        
        successful_outputs = []
        start_time = time.time()
        
        try:
            # Start Excel application
            app = xw.App(visible=False, add_book=False)
            app.display_alerts = False
            app.screen_updating = False
            
            logger.info("✅ Excel session started!")
            
            # Process each file
            for idx, ((_, site), output_path) in enumerate(zip(sites_to_process.iterrows(), output_paths)):
                logger.info(f"\n--- GENERATING SITE {idx + 1}/2 ---")
                
                try:
                    # Open file
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
                    
                    # Set values
                    inputs_sheet.range("A2:Q2").value = row_2_data
                    
                    # Save and close
                    wb.save()
                    wb.close()
                    
                    successful_outputs.append({
                        'path': output_path,
                        'site_info': site_info[idx],
                        'purchase_price': purchase_price
                    })
                    
                    logger.info(f"✅ Site {idx + 1}: Generated successfully")
                    
                except Exception as e:
                    logger.error(f"❌ Site {idx + 1} failed: {str(e)}")
                    try:
                        if 'wb' in locals():
                            wb.close()
                    except:
                        pass
            
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
        
        # Step 3: Read Sources & Uses gaps and rank
        logger.info(f"\n🔧 Step 3: Reading Sources & Uses gaps for ranking...")
        
        ranking_data = []
        
        for output_info in successful_outputs:
            logger.info(f"📊 Reading gap from: {output_info['path'].name}")
            
            # Give Excel a moment to settle
            time.sleep(2)
            
            gap_value = self.read_sources_uses_gap(output_info['path'])
            
            ranking_data.append({
                'site_name': output_info['site_info']['name'],
                'site_address': output_info['site_info']['address'],
                'purchase_price': output_info['purchase_price'],
                'sources_uses_gap': gap_value,
                'file_path': output_info['path'],
                'file_name': output_info['path'].name
            })
            
            logger.info(f"  💰 Sources & Uses Gap (C8): ${gap_value:,}" if isinstance(gap_value, (int, float)) else f"  💰 Gap: {gap_value}")
        
        # Step 4: Sort by gap (smallest gap first - better funding balance ranks higher)
        ranking_data.sort(key=lambda x: abs(x['sources_uses_gap']) if isinstance(x['sources_uses_gap'], (int, float)) else float('inf'), reverse=False)
        
        # Display final results and ranking
        total_time = end_time - start_time
        
        logger.info("\n" + "="*70)
        logger.info("🏆 FINAL RESULTS WITH SOURCES & USES GAP RANKING")
        logger.info("="*70)
        logger.info(f"✅ BOTNs Generated: {len(successful_outputs)}/2")
        logger.info(f"⏱️  Total Time: {total_time:.2f} seconds")
        
        logger.info(f"\n📊 SITE RANKING BY SOURCES & USES GAP (Cell C8):")
        logger.info("Ranked by smallest gap (best funding balance first):")
        
        for rank, site_data in enumerate(ranking_data, 1):
            gap = site_data['sources_uses_gap']
            gap_display = f"${gap:,}" if isinstance(gap, (int, float)) else str(gap)
            
            logger.info(f"\n🥇 RANK {rank}: {site_data['site_name']}")
            logger.info(f"   📍 Address: {site_data['site_address']}")
            logger.info(f"   💰 Purchase Price: ${site_data['purchase_price']:,}")
            logger.info(f"   📊 Sources & Uses Gap: {gap_display}")
            logger.info(f"   📁 File: {site_data['file_name']}")
        
        # Summary
        if len(ranking_data) == 2:
            best_site = ranking_data[0]
            logger.info(f"\n🎯 RECOMMENDATION:")
            logger.info(f"🥇 BEST SITE: {best_site['site_name']}")
            logger.info(f"   Reason: Smallest Sources & Uses gap (${best_site['sources_uses_gap']:,})" if isinstance(best_site['sources_uses_gap'], (int, float)) else f"   Gap: {best_site['sources_uses_gap']}")
            logger.info(f"   This site has the best funding balance and is most viable")
        
        return len(successful_outputs) == 2, ranking_data

def main():
    generator = Production2SiteBOTNWithRanking()
    success, ranking_data = generator.generate_and_rank_sites()
    
    if success:
        logger.info("\n🏆 PRODUCTION + RANKING SUCCESSFUL!")
        logger.info(f"📊 {len(ranking_data)} sites ranked by Sources & Uses gap")
        logger.info("✅ Ready for decision making based on funding gaps")
    else:
        logger.error("\n🔧 PRODUCTION + RANKING ISSUES")

if __name__ == "__main__":
    main()