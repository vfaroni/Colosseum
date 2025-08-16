#!/usr/bin/env python3
"""
Test Second Site - Test BOTN generation with a different site
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

class SecondSiteTest:
    """Test with second site in portfolio"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        
    def process_user_inputs(self, raw_inputs):
        """Process and normalize user inputs"""
        processed = {}
        
        input_mapping = {
            8: ('Housing Type', raw_inputs[0]),
            9: ('Credit Pricing', raw_inputs[1]),
            10: ('Credit Type', raw_inputs[2]),
            11: ('Construction Loan Term', raw_inputs[3]),
            12: ('Market Cap Rate', raw_inputs[4]),
            13: ('Financing Interest Rate', raw_inputs[5]),
            14: ('Elevator', raw_inputs[6]),
            15: ('# Units', raw_inputs[7]),
            16: ('Avg Unit Size', raw_inputs[8]),
            17: ('Hard Cost/SF', raw_inputs[9])
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
            return raw_str.title()
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
            if raw_str.lower() in ['no', 'none', 'false']:
                return "Non-Elevator"
            else:
                return "Elevator"
        elif 'Units' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)
        elif 'Unit Size' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)
        elif 'Hard Cost' in field_name:
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
        """Convert county name to match template dropdown format"""
        if not county_name or pd.isna(county_name) or str(county_name).lower() == 'nan':
            return 'Los Angeles County'  # Default
            
        county_str = str(county_name).strip()
        
        # If it already ends with "County", return as-is
        if county_str.endswith(' County'):
            return county_str
        
        # Add "County" to the name
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
    
    def test_second_site(self):
        """Test BOTN generation with second site"""
        
        # User inputs
        user_inputs_raw = [
            "new Construction", "80 cents", "4%", "36 months", "5%", "6%", 
            "No", "100 units", "900SF", "250/SF"
        ]
        
        # Process inputs
        processed_inputs = self.process_user_inputs(user_inputs_raw)
        
        # Load site data and get second site
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        
        # Find first non-NaN site after index 0
        test_site = None
        site_index = 0
        
        for idx in range(1, min(10, len(df))):  # Check first 10 sites after the first one
            site = df.iloc[idx]
            site_name = site.get('Property Name', '')
            if not pd.isna(site_name) and str(site_name).lower() != 'nan' and site_name.strip():
                test_site = site
                site_index = idx
                break
        
        if test_site is None:
            logger.error("Could not find a valid second site to test")
            return
        
        # Display info
        logger.info("\n" + "="*70)
        logger.info("🧪 TESTING SECOND SITE BOTN GENERATION")
        logger.info("="*70)
        logger.info(f"🏠 Site #{site_index + 1}: {test_site.get('Property Name')}")
        logger.info(f"📍 Address: {test_site.get('Property Address')}")
        logger.info(f"🏛️ County: {test_site.get('County Name')} → {self.get_template_county_format(test_site.get('County Name'))}")
        logger.info(f"🎯 CDLAC Region: {self.get_cdlac_region(test_site.get('County Name'))}")
        price_value = self.clean_data_value(test_site.get('For Sale Price', 0))
        if price_value and price_value != '':
            logger.info(f"💰 Price: ${float(price_value):,.0f}")
        else:
            logger.info(f"💰 Price: Not specified")
        
        # Generate filename
        site_name = str(test_site.get('Property Name', 'Site')).replace(' ', '_').replace('/', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"TEST_SITE_{site_index + 1}_{site_name}_{timestamp}.xlsx"
        output_path = self.base_path / "outputs" / output_filename
        
        try:
            logger.info("\n🔧 Step 1: Copying original template...")
            shutil.copy2(self.template_path, output_path)
            
            logger.info("🔧 Step 2: Opening with xlwings...")
            app = xw.App(visible=False, add_book=False)
            wb = app.books.open(str(output_path))
            inputs_sheet = wb.sheets['Inputs']
            
            logger.info("🔧 Step 3: Populating ONLY Inputs row 2...")
            
            # Prepare row 2 data
            row_2_data = [
                self.clean_data_value(test_site.get('Property Name', '')),                    # A2
                self.clean_data_value(test_site.get('Property Address', '')),                 # B2
                self.get_template_county_format(self.clean_data_value(test_site.get('County Name', ''))),  # C2 - Proper county format
                self.get_cdlac_region(self.clean_data_value(test_site.get('County Name'))),   # D2
                self.clean_data_value(test_site.get('State', '')),                            # E2
                self.clean_data_value(test_site.get('Zip', '')),                              # F2
                float(self.clean_data_value(test_site.get('For Sale Price', 0))) if self.clean_data_value(test_site.get('For Sale Price')) else 0,  # G2
                processed_inputs.get(8, ''),   # H2 - Housing Type
                processed_inputs.get(9, 0),    # I2 - Credit Pricing
                processed_inputs.get(10, ''),  # J2 - Credit Type
                processed_inputs.get(11, 0),   # K2 - Construction Loan Term
                processed_inputs.get(12, 0),   # L2 - Market Cap Rate
                processed_inputs.get(13, 0),   # M2 - Financing Interest Rate
                processed_inputs.get(14, ''),  # N2 - Elevator
                processed_inputs.get(15, 0),   # O2 - Units
                processed_inputs.get(16, 0),   # P2 - Avg Unit Size
                processed_inputs.get(17, 0)    # Q2 - Hard Cost/SF
            ]
            
            # Populate row 2
            for col_idx, value in enumerate(row_2_data, 1):
                cell_address = f"{chr(64 + col_idx)}2"  # A2, B2, C2, etc.
                inputs_sheet.range(cell_address).value = value
                logger.info(f"Set {cell_address}: {value}")
            
            logger.info("🔧 Step 4: Saving with Excel...")
            wb.save()
            wb.close()
            app.quit()
            
            logger.info(f"\n🎉 SUCCESS: Second site BOTN created!")
            logger.info(f"📁 File: {output_path}")
            logger.info(f"✅ Ready for mass processing!")
            
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            try:
                if 'wb' in locals():
                    wb.close()
                if 'app' in locals():
                    app.quit()
            except:
                pass

def main():
    tester = SecondSiteTest()
    tester.test_second_site()

if __name__ == "__main__":
    main()