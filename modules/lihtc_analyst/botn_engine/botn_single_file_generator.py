#!/usr/bin/env python3
"""
Single File BOTN Generator - Process one site at a time to minimize prompts
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

class SingleFileBOTNGenerator:
    """Generate BOTN for one site at a time with minimal prompts"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        
    def get_user_inputs(self):
        """Get user inputs with correct dropdown options"""
        
        print("\n" + "="*70)
        print("🏠 BOTN INPUT CONFIGURATION")
        print("="*70)
        print("Please provide the following inputs:")
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
        
        # Other inputs
        credit_pricing = input("\n2. Credit Pricing (I2) - e.g., '80 cents', '0.85': ").strip()
        
        print("\n3. Credit Type (J2) - Choose from:")
        print("   a) 4%")
        print("   b) 9%")
        
        credit_options = {'a': '4%', 'b': '9%'}
        while True:
            choice = input("   Enter choice (a/b): ").lower().strip()
            if choice in credit_options:
                credit_type = credit_options[choice]
                break
            print("   Invalid choice. Please enter a or b.")
        
        loan_term = input("\n4. Construction Loan Term (K2) - e.g., '36 months': ").strip()
        cap_rate = input("\n5. Market Cap Rate (L2) - e.g., '5%': ").strip()
        interest_rate = input("\n6. Financing Interest Rate (M2) - e.g., '6%': ").strip()
        
        print("\n7. Elevator (N2) - Choose from:")
        print("   a) Elevator")
        print("   b) Non-Elevator")
        
        elevator_options = {'a': 'Elevator', 'b': 'Non-Elevator'}
        while True:
            choice = input("   Enter choice (a/b): ").lower().strip()
            if choice in elevator_options:
                elevator = elevator_options[choice]
                break
            print("   Invalid choice. Please enter a or b.")
        
        purchase_price = input("\n8. Purchase Price Assumption (G2) - e.g., '2M': ").strip()
        units = input("\n9. Number of Units (O2) - e.g., '100 units': ").strip()
        unit_size = input("\n10. Average Unit Size (P2) - e.g., '900SF': ").strip()
        hard_cost = input("\n11. Hard Cost per SF (Q2) - e.g., '250/SF': ").strip()
        
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
    
    def choose_site(self):
        """Let user choose which site to process"""
        
        # Load site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        
        # Get first 10 valid sites
        valid_sites = []
        for idx in range(min(20, len(df))):
            site = df.iloc[idx]
            site_name = site.get('Property Name', '')
            if not pd.isna(site_name) and str(site_name).lower() != 'nan' and site_name.strip():
                valid_sites.append((idx, site))
                if len(valid_sites) >= 10:
                    break
        
        print("\n" + "="*70)
        print("🏠 SELECT SITE TO PROCESS")
        print("="*70)
        print("Choose a site:")
        
        for i, (idx, site) in enumerate(valid_sites, 1):
            county = site.get('County Name', 'Unknown')
            address = site.get('Property Address', 'No address')
            print(f"   {i}) {site.get('Property Name')} - {county} County")
            print(f"      {address}")
        
        while True:
            try:
                choice = int(input(f"\nEnter choice (1-{len(valid_sites)}): ").strip())
                if 1 <= choice <= len(valid_sites):
                    return valid_sites[choice - 1]
                print(f"Invalid choice. Please enter 1-{len(valid_sites)}.")
            except ValueError:
                print("Please enter a number.")
    
    def create_single_botn(self, site_data, user_inputs, site_index):
        """Create BOTN for single site"""
        
        site_name = str(site_data.get('Property Name', f'Site_{site_index}')).replace(' ', '_').replace('/', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"SINGLE_BOTN_{site_name}_{timestamp}.xlsx"
        output_path = self.base_path / "outputs" / output_filename
        
        try:
            logger.info("🔧 Step 1: Copying template...")
            shutil.copy2(self.template_path, output_path)
            
            logger.info("🔧 Step 2: Opening with xlwings...")
            app = xw.App(visible=False, add_book=False)
            wb = app.books.open(str(output_path))
            inputs_sheet = wb.sheets['Inputs']
            
            logger.info("🔧 Step 3: Populating data...")
            
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
                logger.info(f"Set {cell_address}: {value}")
            
            logger.info("🔧 Step 4: Saving...")
            wb.save()
            wb.close()
            app.quit()
            
            logger.info(f"✅ Success: {output_path}")
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
    
    def run_interactive(self):
        """Run interactive single-site generation"""
        
        print("🎯 SINGLE SITE BOTN GENERATOR")
        print("This will process one site at a time to minimize permission prompts.")
        print()
        
        # Choose site
        site_index, site_data = self.choose_site()
        
        # Get user inputs
        try:
            user_inputs_raw = self.get_user_inputs()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Input cancelled")
            return
        
        # Process inputs
        processed_inputs = self.process_user_inputs(user_inputs_raw)
        
        # Display summary
        logger.info("\n" + "="*70)
        logger.info("🎯 GENERATING SINGLE BOTN")
        logger.info("="*70)
        logger.info(f"🏠 Site: {site_data.get('Property Name')}")
        logger.info(f"📍 Address: {site_data.get('Property Address')}")
        logger.info(f"🏛️ County: {self.get_template_county_format(site_data.get('County Name'))}")
        
        # Create BOTN
        output_path = self.create_single_botn(site_data, processed_inputs, site_index + 1)
        
        if output_path:
            logger.info(f"\n🎉 SUCCESS!")
            logger.info(f"📁 File: {output_path}")
            logger.info(f"✅ Template preserved with correct dropdown values")
        else:
            logger.error("\n❌ Failed to create BOTN")

def main():
    generator = SingleFileBOTNGenerator()
    generator.run_interactive()

if __name__ == "__main__":
    main()