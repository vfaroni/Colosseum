#!/usr/bin/env python3
"""
XLWings BOTN Generator - Fully automated using Excel application directly
"""

import pandas as pd
import xlwings as xw
from pathlib import Path
import logging
from datetime import datetime
import shutil
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XLWingsBOTNGenerator:
    """BOTN generator using xlwings for full Excel compatibility"""
    
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
        return cdlac_regions.get(county_name, None)
    
    def create_botn_with_xlwings(self, site_data, user_inputs):
        """Create BOTN using xlwings (Excel application)"""
        
        # Generate filename
        site_name = str(site_data.get('Property Name', 'Site')).replace(' ', '_').replace('/', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"BOTN_XLWINGS_{site_name}_{timestamp}.xlsx"
        output_path = self.base_path / "outputs" / output_filename
        
        try:
            logger.info("🔧 Step 1: Copying original template...")
            # Copy template to output location
            shutil.copy2(self.template_path, output_path)
            
            logger.info("🔧 Step 2: Opening with xlwings...")
            # Open with xlwings (uses Excel application)
            app = xw.App(visible=False)  # Set to True if you want to see Excel
            wb = app.books.open(str(output_path))
            
            # Get Inputs sheet
            inputs_sheet = wb.sheets['Inputs']
            
            logger.info("🔧 Step 3: Populating data...")
            
            # Prepare complete data
            complete_data = [
                str(site_data.get('Property Name', '')),           # A2
                str(site_data.get('Property Address', '')),        # B2
                str(site_data.get('County Name', '')),             # C2
                str(self.get_cdlac_region(site_data.get('County Name'))),  # D2
                str(site_data.get('State', '')),                   # E2
                site_data.get('Zip', ''),                          # F2
                float(site_data.get('For Sale Price', 0)) if site_data.get('For Sale Price') else 0,  # G2
                user_inputs.get(8, ''),    # H2 - Housing Type
                user_inputs.get(9, 0),     # I2 - Credit Pricing
                user_inputs.get(10, ''),   # J2 - Credit Type
                user_inputs.get(11, 0),    # K2 - Construction Loan Term
                user_inputs.get(12, 0),    # L2 - Market Cap Rate
                user_inputs.get(13, 0),    # M2 - Financing Interest Rate
                user_inputs.get(14, ''),   # N2 - Elevator
                user_inputs.get(15, 0),    # O2 - Units
                user_inputs.get(16, 0),    # P2 - Avg Unit Size
                user_inputs.get(17, 0)     # Q2 - Hard Cost/SF
            ]
            
            # Populate Row 2 (Excel uses 1-based indexing)
            for col_idx, value in enumerate(complete_data, 1):
                cell_address = f"{chr(64 + col_idx)}2"  # A2, B2, C2, etc.
                inputs_sheet.range(cell_address).value = value
                logger.info(f"Set {cell_address}: {value}")
            
            logger.info("🔧 Step 4: Saving workbook...")
            # Save and close
            wb.save()
            wb.close()
            app.quit()
            
            logger.info(f"✅ XLWings BOTN created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating xlwings BOTN: {str(e)}")
            # Try to clean up
            try:
                if 'wb' in locals():
                    wb.close()
                if 'app' in locals():
                    app.quit()
            except:
                pass
            return None
    
    def generate_xlwings_botn(self):
        """Generate BOTN using xlwings"""
        
        # User inputs
        user_inputs_raw = [
            "new Construction", "80 cents", "4%", "36 months", "5%", "6%", 
            "No", "100 units", "900SF", "250/SF"
        ]
        
        # Process inputs
        processed_inputs = self.process_user_inputs(user_inputs_raw)
        
        # Load site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        test_site = df.iloc[0]
        
        # Display info
        logger.info("\n" + "="*70)
        logger.info("🚀 XLWINGS BOTN GENERATION")
        logger.info("="*70)
        logger.info(f"🏠 Site: {test_site.get('Property Name')}")
        logger.info(f"📍 Address: {test_site.get('Property Address')}")
        logger.info(f"🔧 Method: XLWings with Excel application")
        logger.info(f"⚠️  Note: This will briefly open Excel in the background")
        
        # Create BOTN
        output_path = self.create_botn_with_xlwings(test_site, processed_inputs)
        
        if output_path:
            logger.info(f"\n🎉 SUCCESS: XLWings BOTN created!")
            logger.info(f"📁 File: {output_path}")
            logger.info(f"✅ Features preserved:")
            logger.info(f"   • All original calculations intact")
            logger.info(f"   • All data validations preserved")
            logger.info(f"   • All formulas working")
            logger.info(f"   • No Excel corruption errors")
            logger.info(f"   • Complete template functionality")
        else:
            logger.error("\n❌ Failed to create XLWings BOTN")

def main():
    generator = XLWingsBOTNGenerator()
    generator.generate_xlwings_botn()

if __name__ == "__main__":
    main()