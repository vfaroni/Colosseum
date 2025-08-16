#!/usr/bin/env python3
"""
Test 5 Sites XLWings - Pre-configured test of batch processing
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

class Test5SitesXLWings:
    """Test batch processing with 5 sites using pre-configured inputs"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        
    def get_test_inputs(self):
        """Pre-configured test inputs"""
        return [
            "Large Family",   # Housing Type
            "80 cents",       # Credit Pricing
            "4%",             # Credit Type
            "36 months",      # Construction Loan Term
            "5%",             # Market Cap Rate
            "6%",             # Financing Interest Rate
            "Non-Elevator",   # Elevator
            "2000000",        # Purchase Price Assumption
            "100",            # Number of Units
            "900",            # Average Unit Size
            "250"             # Hard Cost per SF
        ]
    
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
            'Los Angeles': 'Los Angeles County',
            'Orange': 'Orange County',
            'Riverside': 'Inland Empire Region', 'San Bernardino': 'Inland Empire Region',
            'San Diego': 'San Diego County', 'Imperial': 'San Diego County',
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
    
    def test_5_sites_batch(self):
        """Test batch processing with 5 sites"""
        
        # Use pre-configured test inputs
        user_inputs_raw = self.get_test_inputs()
        processed_inputs = self.process_user_inputs(user_inputs_raw)
        
        # Load site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        
        # Get first 5 valid sites
        sites_to_process = []
        for idx in range(len(df)):
            if len(sites_to_process) >= 5:
                break
            site = df.iloc[idx]
            site_name = site.get('Property Name', '')
            if not pd.isna(site_name) and str(site_name).lower() != 'nan' and site_name.strip():
                sites_to_process.append((idx, site))
        
        logger.info("\n" + "="*70)
        logger.info("🧪 TESTING XLWINGS BATCH PROCESSING - 5 SITES")
        logger.info("="*70)
        logger.info(f"📊 Sites to process: {len(sites_to_process)}")
        logger.info(f"🏠 Housing Type: {processed_inputs.get(8)}")
        logger.info(f"💰 Purchase Price Assumption: ${processed_inputs.get('purchase_price'):,}")
        logger.info("⚠️  Excel may prompt for permission once or a few times...")
        
        # Show sites to be processed
        logger.info(f"\n📋 SITES TO PROCESS:")
        for idx, (original_idx, site) in enumerate(sites_to_process, 1):
            logger.info(f"   {idx}. {site.get('Property Name')} - {site.get('County Name', 'Unknown')} County")
        
        # Create template copies first
        logger.info(f"\n🔧 Step 1: Creating template copies...")
        file_mappings = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for idx, (original_idx, site) in enumerate(sites_to_process):
            site_name = str(site.get('Property Name', f'Site_{original_idx}')).replace(' ', '_').replace('/', '_')
            if pd.isna(site_name) or site_name.lower() == 'nan':
                site_name = f'Site_{original_idx}'
            
            output_filename = f"TEST5_BOTN_{site_name}_{timestamp}_{idx:03d}.xlsx"
            output_path = self.base_path / "outputs" / output_filename
            
            # Copy template
            shutil.copy2(self.template_path, output_path)
            
            file_mappings.append({
                'site': site,
                'original_idx': original_idx,
                'file_path': output_path,
                'site_name': site_name
            })
        
        logger.info(f"✅ Created {len(file_mappings)} template copies")
        
        # Populate with Excel
        logger.info(f"\n🔧 Step 2: Opening Excel and populating files...")
        successful_files = []
        failed_files = []
        app = None
        
        try:
            # Open Excel once
            app = xw.App(visible=False, add_book=False)
            logger.info("✅ Excel application opened")
            
            for idx, file_info in enumerate(file_mappings):
                try:
                    logger.info(f"📝 Processing {idx + 1}/{len(file_mappings)}: {file_info['site_name']}")
                    
                    # Open workbook
                    wb = app.books.open(str(file_info['file_path']))
                    inputs_sheet = wb.sheets['Inputs']
                    
                    # Determine purchase price
                    site_price = self.clean_data_value(file_info['site'].get('For Sale Price', 0))
                    if site_price and site_price != '' and site_price != 0:
                        purchase_price = float(site_price)
                    else:
                        purchase_price = float(processed_inputs.get('purchase_price', 0))
                    
                    # Prepare row 2 data
                    row_2_data = [
                        self.clean_data_value(file_info['site'].get('Property Name', '')),
                        self.clean_data_value(file_info['site'].get('Property Address', '')),
                        self.get_template_county_format(self.clean_data_value(file_info['site'].get('County Name', ''))),
                        self.get_cdlac_region(self.clean_data_value(file_info['site'].get('County Name'))),
                        self.clean_data_value(file_info['site'].get('State', '')),
                        self.clean_data_value(file_info['site'].get('Zip', '')),
                        purchase_price,
                        processed_inputs.get(8, ''),   # Housing Type
                        processed_inputs.get(9, 0),    # Credit Pricing
                        processed_inputs.get(10, ''),  # Credit Type
                        processed_inputs.get(11, 0),   # Construction Loan Term
                        processed_inputs.get(12, 0),   # Market Cap Rate
                        processed_inputs.get(13, 0),   # Financing Interest Rate
                        processed_inputs.get(14, ''),  # Elevator
                        processed_inputs.get(15, 0),   # Units
                        processed_inputs.get(16, 0),   # Avg Unit Size
                        processed_inputs.get(17, 0)    # Hard Cost/SF
                    ]
                    
                    # Populate row 2
                    for col_idx, value in enumerate(row_2_data, 1):
                        cell_address = f"{chr(64 + col_idx)}2"
                        inputs_sheet.range(cell_address).value = value
                    
                    # Save and close
                    wb.save()
                    wb.close()
                    
                    successful_files.append(file_info)
                    logger.info(f"   ✅ Success: {file_info['site_name']}")
                    
                except Exception as e:
                    logger.error(f"   ❌ Failed {file_info['site_name']}: {str(e)}")
                    failed_files.append(file_info)
                    try:
                        if 'wb' in locals():
                            wb.close()
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"❌ Excel session error: {str(e)}")
        
        finally:
            if app:
                try:
                    app.quit()
                    logger.info("🔧 Excel application closed")
                except:
                    pass
        
        # Final summary
        logger.info(f"\n🏆 TEST BATCH PROCESSING COMPLETE!")
        logger.info("="*70)
        logger.info(f"✅ Successful sites: {len(successful_files)}")
        logger.info(f"❌ Failed sites: {len(failed_files)}")
        
        if successful_files:
            logger.info(f"\n📋 SUCCESSFUL SITES:")
            for file_info in successful_files:
                logger.info(f"   • {file_info['site_name']}")
        
        if failed_files:
            logger.info(f"\n⚠️ FAILED SITES:")
            for file_info in failed_files:
                logger.info(f"   • {file_info['site_name']}")
        
        if len(successful_files) == 5:
            logger.info(f"\n🎉 PERFECT! All 5 sites processed successfully!")
            logger.info(f"   Ready to scale up to 50 sites!")
        elif len(successful_files) >= 3:
            logger.info(f"\n👍 GOOD! {len(successful_files)}/5 sites successful!")
            logger.info(f"   This approach should work for larger batches!")
        else:
            logger.info(f"\n⚠️  Only {len(successful_files)}/5 sites successful.")
            logger.info(f"   May need to try alternative approach.")

def main():
    tester = Test5SitesXLWings()
    tester.test_5_sites_batch()

if __name__ == "__main__":
    main()