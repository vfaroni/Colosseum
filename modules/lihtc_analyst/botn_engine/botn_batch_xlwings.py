#!/usr/bin/env python3
"""
Batch XLWings BOTN Generator - Process multiple sites with one Excel session
"""

import pandas as pd
import shutil
import xlwings as xw
from pathlib import Path
import logging
from datetime import datetime
import re
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchXLWingsBOTNGenerator:
    """Process multiple BOTNs with single Excel session to minimize permission prompts"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        
    def process_user_inputs(self, raw_inputs):
        """Process and normalize user inputs"""
        processed = {}
        
        input_mapping = {
            'purchase_price': ('Purchase Price Assumption', raw_inputs[7]),
            8: ('Housing Type', raw_inputs[0]),
            9: ('Credit Pricing', raw_inputs[1]),
            10: ('Credit Type', raw_inputs[2]),
            11: ('Construction Loan Term', raw_inputs[3]),
            12: ('Market Cap Rate', raw_inputs[4]),
            13: ('Financing Interest Rate', raw_inputs[5]),
            14: ('Elevator', raw_inputs[6]),
            15: ('# Units', raw_inputs[8]),
            16: ('Avg Unit Size', raw_inputs[9]),
            17: ('Hard Cost/SF', raw_inputs[10])
        }
        
        for col_num, (field_name, raw_value) in input_mapping.items():
            processed_value = self.normalize_input(field_name, raw_value)
            processed[col_num] = processed_value
            logger.info(f"Processed {field_name}: '{raw_value}' → {processed_value}")
        
        return processed
    
    def normalize_input(self, field_name, raw_value):
        """Normalize input values"""
        raw_str = str(raw_value).strip()
        
        if 'Housing Type' in field_name:
            return raw_str
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
            return raw_str
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
            return raw_str
        elif 'Units' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)
        elif 'Unit Size' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)
        elif 'Hard Cost' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)
        elif 'Purchase Price' in field_name:
            raw_str = raw_str.replace('$', '').replace(',', '').upper()
            if 'M' in raw_str:
                number = float(re.findall(r'[\d.]+', raw_str)[0])
                return int(number * 1000000)
            else:
                number = re.findall(r'\d+', raw_str)[0]
                return int(number)
        else:
            return raw_str
    
    def get_cdlac_region(self, county_name):
        """Get CDLAC region"""
        if not county_name or pd.isna(county_name) or str(county_name).lower() == 'nan':
            return 'Northern Region'
            
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
    
    def process_site_with_excel(self, app, site_data, user_inputs, site_index):
        """Process single site using existing Excel app"""
        
        site_name = str(site_data.get('Property Name', f'Site_{site_index}')).replace(' ', '_').replace('/', '_')
        if pd.isna(site_name) or site_name.lower() == 'nan':
            site_name = f'Site_{site_index}'
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"BATCH_BOTN_{site_name}_{timestamp}.xlsx"
        output_path = self.base_path / "outputs" / output_filename
        
        try:
            logger.info(f"🔧 Processing: {site_name}")
            
            # Copy template
            shutil.copy2(self.template_path, output_path)
            
            # Open with existing Excel app (should not prompt again)
            wb = app.books.open(str(output_path))
            inputs_sheet = wb.sheets['Inputs']
            
            # Determine purchase price
            site_price = self.clean_data_value(site_data.get('For Sale Price', 0))
            if site_price and site_price != '' and site_price != 0:
                purchase_price = float(site_price)
            else:
                purchase_price = float(user_inputs.get('purchase_price', 0))
            
            # Prepare row 2 data
            row_2_data = [
                self.clean_data_value(site_data.get('Property Name', '')),
                self.clean_data_value(site_data.get('Property Address', '')),
                self.get_template_county_format(self.clean_data_value(site_data.get('County Name', ''))),
                self.get_cdlac_region(self.clean_data_value(site_data.get('County Name'))),
                self.clean_data_value(site_data.get('State', '')),
                self.clean_data_value(site_data.get('Zip', '')),
                purchase_price,
                user_inputs.get(8, ''),   # Housing Type
                user_inputs.get(9, 0),    # Credit Pricing
                user_inputs.get(10, ''),  # Credit Type
                user_inputs.get(11, 0),   # Construction Loan Term
                user_inputs.get(12, 0),   # Market Cap Rate
                user_inputs.get(13, 0),   # Financing Interest Rate
                user_inputs.get(14, ''),  # Elevator
                user_inputs.get(15, 0),   # Units
                user_inputs.get(16, 0),   # Avg Unit Size
                user_inputs.get(17, 0)    # Hard Cost/SF
            ]
            
            # Populate row 2
            for col_idx, value in enumerate(row_2_data, 1):
                cell_address = f"{chr(64 + col_idx)}2"
                inputs_sheet.range(cell_address).value = value
            
            # Save and close this workbook (but keep Excel app open)
            wb.save()
            wb.close()
            
            logger.info(f"✅ Created: {output_filename}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error processing {site_name}: {str(e)}")
            try:
                if 'wb' in locals():
                    wb.close()
            except:
                pass
            return None
    
    def generate_batch_botn(self, num_sites=5):
        """Generate BOTNs for multiple sites with single Excel session"""
        
        # Predefined inputs for testing
        user_inputs_raw = [
            "Large Family",   # Housing Type
            "80 cents",       # Credit Pricing
            "4%",             # Credit Type
            "36 months",      # Construction Loan Term
            "5%",             # Market Cap Rate
            "6%",             # Financing Interest Rate
            "Non-Elevator",   # Elevator
            "2000000",        # Purchase Price Assumption
            "100 units",      # Number of Units
            "900SF",          # Average Unit Size
            "250/SF"          # Hard Cost per SF
        ]
        
        # Process inputs
        processed_inputs = self.process_user_inputs(user_inputs_raw)
        
        # Load site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        
        # Get first N valid sites
        sites_to_process = []
        for idx in range(len(df)):
            if len(sites_to_process) >= num_sites:
                break
            site = df.iloc[idx]
            site_name = site.get('Property Name', '')
            if not pd.isna(site_name) and str(site_name).lower() != 'nan' and site_name.strip():
                sites_to_process.append((idx, site))
        
        logger.info("\n" + "="*70)
        logger.info("🚀 BATCH BOTN GENERATION - SINGLE EXCEL SESSION")
        logger.info("="*70)
        logger.info(f"📊 Sites to process: {len(sites_to_process)}")
        logger.info("⚠️  Excel will ask for permission ONCE, then process all sites")
        
        # Open Excel once
        app = None
        successful_sites = []
        failed_sites = []
        
        try:
            logger.info("🔧 Opening Excel application (may prompt for permission)...")
            app = xw.App(visible=False, add_book=False)
            
            logger.info("✅ Excel opened! Processing sites without additional prompts...")
            
            # Process all sites with the same Excel session
            for idx, (original_idx, site) in enumerate(sites_to_process, 1):
                logger.info(f"\n🏗️ Site {idx}/{len(sites_to_process)}: {site.get('Property Name')}")
                
                output_path = self.process_site_with_excel(app, site, processed_inputs, original_idx + 1)
                
                if output_path:
                    successful_sites.append({
                        'name': site.get('Property Name'),
                        'path': output_path
                    })
                else:
                    failed_sites.append({
                        'name': site.get('Property Name'),
                        'index': original_idx + 1
                    })
            
        except Exception as e:
            logger.error(f"❌ Excel session error: {str(e)}")
        
        finally:
            # Clean up Excel
            if app:
                try:
                    app.quit()
                    logger.info("🔧 Excel application closed")
                except:
                    pass
        
        # Final summary
        logger.info(f"\n🏆 BATCH PROCESSING COMPLETE!")
        logger.info("="*70)
        logger.info(f"✅ Successful sites: {len(successful_sites)}")
        logger.info(f"❌ Failed sites: {len(failed_sites)}")
        
        if successful_sites:
            logger.info(f"\n📋 SUCCESSFUL SITES:")
            for site in successful_sites:
                logger.info(f"   • {site['name']}")
        
        if failed_sites:
            logger.info(f"\n⚠️ FAILED SITES:")
            for site in failed_sites:
                logger.info(f"   • {site['name']} (index {site['index']})")

def main():
    generator = BatchXLWingsBOTNGenerator()
    generator.generate_batch_botn(num_sites=3)  # Test with 3 sites first

if __name__ == "__main__":
    main()