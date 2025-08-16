#!/usr/bin/env python3
"""
Interactive BOTN Generator - Prompts user for correct inputs matching template dropdowns
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

class InteractiveBOTNGenerator:
    """Generate BOTN with correct template dropdown options"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        
    def get_user_inputs(self):
        """Get user inputs with correct dropdown options"""
        
        print("\n" + "="*70)
        print("🏠 BOTN INPUT CONFIGURATION")
        print("="*70)
        print("Please provide the following inputs that will be applied to all sites:")
        print()
        
        # Housing Type - must match dropdown exactly
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
        
        # Credit Pricing
        credit_pricing = input("\n2. Credit Pricing (I2) - e.g., '80 cents', '0.85', '75%': ").strip()
        
        # Credit Type - must match dropdown
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
        
        # Other inputs
        loan_term = input("\n4. Construction Loan Term (K2) - e.g., '36 months', '24': ").strip()
        cap_rate = input("\n5. Market Cap Rate (L2) - e.g., '5%', '0.05': ").strip()
        interest_rate = input("\n6. Financing Interest Rate (M2) - e.g., '6%', '0.06': ").strip()
        
        # Elevator - must match dropdown
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
        
        # Purchase price assumption
        purchase_price = input("\n8. Purchase Price Assumption (G2) - for sites with missing prices, e.g., '$2000000', '1.5M': ").strip()
        
        # Remaining numeric inputs
        units = input("\n9. Number of Units (O2) - e.g., '100 units', '75': ").strip()
        unit_size = input("\n10. Average Unit Size (P2) - e.g., '900SF', '850': ").strip()
        hard_cost = input("\n11. Hard Cost per SF (Q2) - e.g., '250/SF', '300': ").strip()
        
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
            # Housing Type should be used exactly as provided (already matches dropdown)
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
            # Elevator should be used exactly as provided (already matches dropdown)
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
            # Handle various formats: $2000000, 2M, 1.5M, 2000000
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
    
    def create_interactive_botn(self, site_data, user_inputs):
        """Create BOTN with interactive inputs"""
        
        site_name = str(site_data.get('Property Name', 'Site')).replace(' ', '_').replace('/', '_')
        if pd.isna(site_name) or site_name.lower() == 'nan':
            site_name = 'Site'
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"INTERACTIVE_BOTN_{site_name}_{timestamp}.xlsx"
        output_path = self.base_path / "outputs" / output_filename
        
        try:
            logger.info("🔧 Step 1: Copying original template...")
            shutil.copy2(self.template_path, output_path)
            
            logger.info("🔧 Step 2: Opening with xlwings...")
            app = xw.App(visible=False, add_book=False)
            wb = app.books.open(str(output_path))
            inputs_sheet = wb.sheets['Inputs']
            
            logger.info("🔧 Step 3: Populating ONLY Inputs row 2...")
            
            # Determine purchase price - use site price if available, otherwise use assumption
            site_price = self.clean_data_value(site_data.get('For Sale Price', 0))
            if site_price and site_price != '' and site_price != 0:
                purchase_price = float(site_price)
            else:
                purchase_price = float(user_inputs.get('purchase_price', 0))
            
            # Prepare row 2 data
            row_2_data = [
                self.clean_data_value(site_data.get('Property Name', '')),                    # A2
                self.clean_data_value(site_data.get('Property Address', '')),                 # B2
                self.get_template_county_format(self.clean_data_value(site_data.get('County Name', ''))),  # C2 - Proper county format
                self.get_cdlac_region(self.clean_data_value(site_data.get('County Name'))),   # D2
                self.clean_data_value(site_data.get('State', '')),                            # E2
                self.clean_data_value(site_data.get('Zip', '')),                              # F2
                purchase_price,           # G2 - Purchase Price (site price or assumption)
                user_inputs.get(8, ''),   # H2 - Housing Type
                user_inputs.get(9, 0),    # I2 - Credit Pricing
                user_inputs.get(10, ''),  # J2 - Credit Type
                user_inputs.get(11, 0),   # K2 - Construction Loan Term
                user_inputs.get(12, 0),   # L2 - Market Cap Rate
                user_inputs.get(13, 0),   # M2 - Financing Interest Rate
                user_inputs.get(14, ''),  # N2 - Elevator
                user_inputs.get(15, 0),   # O2 - Units
                user_inputs.get(16, 0),   # P2 - Avg Unit Size
                user_inputs.get(17, 0)    # Q2 - Hard Cost/SF
            ]
            
            # Populate row 2
            for col_idx, value in enumerate(row_2_data, 1):
                cell_address = f"{chr(64 + col_idx)}2"
                inputs_sheet.range(cell_address).value = value
                logger.info(f"Set {cell_address}: {value}")
            
            logger.info("🔧 Step 4: Saving with Excel...")
            wb.save()
            wb.close()
            app.quit()
            
            logger.info(f"✅ Interactive BOTN created: {output_path}")
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
    
    def generate_interactive_botn(self):
        """Generate BOTN with interactive user inputs"""
        
        # Get user inputs interactively
        user_inputs_raw = self.get_user_inputs()
        
        # Process inputs
        processed_inputs = self.process_user_inputs(user_inputs_raw)
        
        # Load site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        test_site = df.iloc[0]
        
        # Display info
        logger.info("\n" + "="*70)
        logger.info("🎯 INTERACTIVE BOTN GENERATION")
        logger.info("="*70)
        logger.info(f"🏠 Site: {test_site.get('Property Name')}")
        logger.info(f"📍 Address: {test_site.get('Property Address')}")
        logger.info(f"🏛️ County: {self.get_template_county_format(test_site.get('County Name'))}")
        logger.info(f"🎯 CDLAC Region: {self.get_cdlac_region(test_site.get('County Name'))}")
        
        # Create BOTN
        output_path = self.create_interactive_botn(test_site, processed_inputs)
        
        if output_path:
            logger.info(f"\n🎉 SUCCESS: Interactive BOTN created!")
            logger.info(f"📁 File: {output_path}")
            logger.info(f"✅ Features:")
            logger.info(f"   • Correct Housing Type dropdown match")
            logger.info(f"   • Proper county formatting")
            logger.info(f"   • All template features preserved")
        else:
            logger.error("\n❌ Failed to create interactive BOTN")

def main():
    generator = InteractiveBOTNGenerator()
    generator.generate_interactive_botn()

if __name__ == "__main__":
    main()