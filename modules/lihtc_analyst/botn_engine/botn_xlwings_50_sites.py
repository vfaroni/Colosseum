#!/usr/bin/env python3
"""
XLWings 50 Sites BOTN Generator - Optimized for batch processing
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

class XLWings50SitesBOTNGenerator:
    """Generate BOTNs for 50 sites with optimized xlwings approach"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        
    def get_batch_user_inputs(self):
        """Get user inputs for batch processing"""
        
        print("\n" + "="*70)
        print("🏠 BATCH BOTN CONFIGURATION - 50 SITES")
        print("="*70)
        print("These inputs will be applied to ALL 50 sites:")
        print()
        
        # Housing Type
        print("1. Housing Type (H2) - Choose from:")
        print("   a) At Risk and Non-Targeted")
        print("   b) Large Family")
        print("   c) Senior") 
        print("   d) Single Room/ Special Needs")
        
        housing_options = {
            'a': 'At Risk and Non-Targeted',
            'b': 'Large Family', 
            'c': 'Senior',
            'd': 'Single Room/ Special Needs'
        }
        
        while True:
            choice = input("   Enter choice (a/b/c/d): ").lower().strip()
            if choice in housing_options:
                housing_type = housing_options[choice]
                break
            print("   Invalid choice. Please enter a, b, c, or d.")
        
        # Quick inputs for batch processing
        credit_pricing = input("\n2. Credit Pricing - e.g., '80 cents', '0.85': ").strip() or "80 cents"
        
        print("\n3. Credit Type - Choose from:")
        print("   a) 4%")
        print("   b) 9%")
        
        credit_options = {'a': '4%', 'b': '9%'}
        while True:
            choice = input("   Enter choice (a/b): ").lower().strip()
            if choice in credit_options:
                credit_type = credit_options[choice]
                break
            print("   Invalid choice. Please enter a or b.")
        
        loan_term = input("\n4. Construction Loan Term - e.g., '36 months': ").strip() or "36 months"
        cap_rate = input("\n5. Market Cap Rate - e.g., '5%': ").strip() or "5%"
        interest_rate = input("\n6. Financing Interest Rate - e.g., '6%': ").strip() or "6%"
        
        print("\n7. Elevator - Choose from:")
        print("   a) Elevator")
        print("   b) Non-Elevator")
        
        elevator_options = {'a': 'Elevator', 'b': 'Non-Elevator'}
        while True:
            choice = input("   Enter choice (a/b): ").lower().strip()
            if choice in elevator_options:
                elevator = elevator_options[choice]
                break
            print("   Invalid choice. Please enter a or b.")
        
        purchase_price = input("\n8. Purchase Price Assumption - e.g., '2M': ").strip() or "2000000"
        units = input("\n9. Number of Units - e.g., '100': ").strip() or "100"
        unit_size = input("\n10. Average Unit Size - e.g., '900': ").strip() or "900"
        hard_cost = input("\n11. Hard Cost per SF - e.g., '250': ").strip() or "250"
        
        return [housing_type, credit_pricing, credit_type, loan_term, cap_rate, 
                interest_rate, elevator, purchase_price, units, unit_size, hard_cost]
    
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
            'Los Angeles': 'Los Angeles County',
            'Orange': 'Orange County',
            'Riverside': 'Inland Empire Region', 'San Bernardino': 'Inland Empire Region',
            'San Diego': 'San Diego County', 'Imperial': 'San Diego County',
            'Fresno': 'Central Valley Region', 'Kern': 'Central Valley Region', 'Kings': 'Central Valley Region', 
            'Merced': 'Central Valley Region', 'San Joaquin': 'Central Valley Region', 
            'Stanislaus': 'Central Valley Region', 'Tulare': 'Central Valley Region',
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
    
    def create_all_templates_first(self, sites_to_process):
        """Create all template copies first, then populate with Excel"""
        
        logger.info("🔧 Step 1: Creating all template copies...")
        
        file_mappings = []
        for idx, (original_idx, site) in enumerate(sites_to_process):
            site_name = str(site.get('Property Name', f'Site_{original_idx}')).replace(' ', '_').replace('/', '_')
            if pd.isna(site_name) or site_name.lower() == 'nan':
                site_name = f'Site_{original_idx}'
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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
            
            if (idx + 1) % 10 == 0:
                logger.info(f"   Created {idx + 1}/{len(sites_to_process)} template copies...")
        
        logger.info(f"✅ Created {len(file_mappings)} template copies")
        return file_mappings
    
    def populate_files_with_excel(self, file_mappings, user_inputs):
        """Populate all files using Excel with retry logic"""
        
        logger.info("🔧 Step 2: Opening Excel and populating files...")
        logger.info("⚠️  This may prompt for permission once or a few times...")
        
        successful_files = []
        failed_files = []
        app = None
        
        try:
            # Try to keep Excel session alive longer
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
                        purchase_price = float(user_inputs.get('purchase_price', 0))
                    
                    # Prepare row 2 data
                    row_2_data = [
                        self.clean_data_value(file_info['site'].get('Property Name', '')),
                        self.clean_data_value(file_info['site'].get('Property Address', '')),
                        self.get_template_county_format(self.clean_data_value(file_info['site'].get('County Name', ''))),
                        self.get_cdlac_region(self.clean_data_value(file_info['site'].get('County Name'))),
                        self.clean_data_value(file_info['site'].get('State', '')),
                        self.clean_data_value(file_info['site'].get('Zip', '')),
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
                    
                    # Populate row 2 quickly
                    for col_idx, value in enumerate(row_2_data, 1):
                        cell_address = f"{chr(64 + col_idx)}2"
                        inputs_sheet.range(cell_address).value = value
                    
                    # Save and close quickly
                    wb.save()
                    wb.close()
                    
                    successful_files.append(file_info)
                    
                    if (idx + 1) % 5 == 0:
                        logger.info(f"   ✅ Completed {idx + 1}/{len(file_mappings)} files")
                        time.sleep(0.1)  # Brief pause
                    
                except Exception as e:
                    logger.error(f"   ❌ Failed {file_info['site_name']}: {str(e)}")
                    failed_files.append(file_info)
                    try:
                        if 'wb' in locals():
                            wb.close()
                    except:
                        pass
                    continue
        
        except Exception as e:
            logger.error(f"❌ Excel session error: {str(e)}")
        
        finally:
            if app:
                try:
                    app.quit()
                    logger.info("🔧 Excel application closed")
                except:
                    pass
        
        return successful_files, failed_files
    
    def generate_50_sites_botn(self):
        """Generate BOTNs for 50 sites"""
        
        try:
            # Get user inputs
            user_inputs_raw = self.get_batch_user_inputs()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Input cancelled")
            return
        
        # Process inputs
        processed_inputs = self.process_user_inputs(user_inputs_raw)
        
        # Load site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        
        # Get first 5 valid sites for testing
        sites_to_process = []
        for idx in range(len(df)):
            if len(sites_to_process) >= 5:
                break
            site = df.iloc[idx]
            site_name = site.get('Property Name', '')
            if not pd.isna(site_name) and str(site_name).lower() != 'nan' and site_name.strip():
                sites_to_process.append((idx, site))
        
        logger.info("\n" + "="*70)
        logger.info("🧪 TESTING BATCH PROCESSING WITH 5 SITES")
        logger.info("="*70)
        logger.info(f"📊 Sites to process: {len(sites_to_process)}")
        logger.info(f"🏠 Housing Type: {processed_inputs.get(8)}")
        logger.info(f"💰 Purchase Price Assumption: ${processed_inputs.get('purchase_price'):,}")
        
        # Create all template copies first
        file_mappings = self.create_all_templates_first(sites_to_process)
        
        # Populate with Excel
        successful_files, failed_files = self.populate_files_with_excel(file_mappings, processed_inputs)
        
        # Final summary
        logger.info(f"\n🏆 BATCH PROCESSING COMPLETE!")
        logger.info("="*70)
        logger.info(f"✅ Successful sites: {len(successful_files)}")
        logger.info(f"❌ Failed sites: {len(failed_files)}")
        
        if successful_files:
            logger.info(f"\n📋 SAMPLE SUCCESSFUL SITES:")
            for file_info in successful_files[:5]:
                logger.info(f"   • {file_info['site_name']}")
            if len(successful_files) > 5:
                logger.info(f"   ... and {len(successful_files) - 5} more")
        
        if failed_files:
            logger.info(f"\n⚠️ FAILED SITES:")
            for file_info in failed_files[:5]:
                logger.info(f"   • {file_info['site_name']}")
            if len(failed_files) > 5:
                logger.info(f"   ... and {len(failed_files) - 5} more")
        
        logger.info(f"\n📁 All files saved in: {self.base_path / 'outputs'}")

def main():
    generator = XLWings50SitesBOTNGenerator()
    generator.generate_50_sites_botn()

if __name__ == "__main__":
    main()