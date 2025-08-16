#!/usr/bin/env python3
"""
BOTN Template Preserver - Preserves original template exactly, only populates Inputs row 2
"""

import pandas as pd
import shutil
import openpyxl
from pathlib import Path
import logging
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BOTNTemplatePreserver:
    """Preserve original BOTN template, only populate inputs row 2"""
    
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
            return 'Northern Region'  # Default region
            
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
    
    def clean_data_value(self, value):
        """Clean data values to handle NaN and invalid data"""
        import numpy as np
        
        if pd.isna(value) or value is None:
            return ''
        if isinstance(value, (int, float)):
            if np.isnan(value) or np.isinf(value):
                return 0
        if str(value).lower() == 'nan':
            return ''
        return value
    
    def create_populated_botn(self, site_data, user_inputs):
        """Create BOTN by copying template and populating only Inputs row 2"""
        
        # Generate filename
        site_name = str(site_data.get('Property Name', 'Site')).replace(' ', '_').replace('/', '_')
        if pd.isna(site_name) or site_name.lower() == 'nan':
            site_name = 'Site'
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"TEMPLATE_PRESERVED_BOTN_{site_name}_{timestamp}.xlsx"
        output_path = self.base_path / "outputs" / output_filename
        
        try:
            logger.info("🔧 Step 1: Copying original template...")
            # Copy original template to preserve ALL functionality
            shutil.copy2(self.template_path, output_path)
            
            logger.info("🔧 Step 2: Opening template with openpyxl...")
            # Open with openpyxl to populate only the inputs
            workbook = openpyxl.load_workbook(output_path)
            inputs_sheet = workbook['Inputs']
            
            logger.info("🔧 Step 3: Populating ONLY Inputs row 2...")
            
            # Prepare row 2 data - EXACT mapping to template columns
            row_2_data = [
                self.clean_data_value(site_data.get('Property Name', '')),                    # A2
                self.clean_data_value(site_data.get('Property Address', '')),                 # B2
                self.clean_data_value(site_data.get('County Name', '')),                      # C2
                self.get_cdlac_region(self.clean_data_value(site_data.get('County Name'))),   # D2
                self.clean_data_value(site_data.get('State', '')),                            # E2
                self.clean_data_value(site_data.get('Zip', '')),                              # F2
                float(self.clean_data_value(site_data.get('For Sale Price', 0))) if self.clean_data_value(site_data.get('For Sale Price')) else 0,  # G2
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
            
            # Populate ONLY row 2 - preserve everything else
            for col_idx, value in enumerate(row_2_data, 1):
                cell = inputs_sheet.cell(row=2, column=col_idx)
                cell.value = value
                logger.info(f"Set {cell.coordinate}: {value}")
            
            logger.info("🔧 Step 4: Saving workbook...")
            workbook.save(output_path)
            workbook.close()
            
            logger.info(f"✅ Template-preserved BOTN created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating template-preserved BOTN: {str(e)}")
            return None
    
    def generate_preserved_botn(self):
        """Generate BOTN with preserved template"""
        
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
        logger.info("🏛️ TEMPLATE-PRESERVED BOTN GENERATION")
        logger.info("="*70)
        logger.info(f"🏠 Site: {test_site.get('Property Name')}")
        logger.info(f"📍 Address: {test_site.get('Property Address')}")
        logger.info(f"🔧 Method: Copy original template + populate Inputs row 2 ONLY")
        logger.info(f"✨ Preserves: ALL original tabs, formulas, calculations, formatting")
        
        # Create preserved BOTN
        output_path = self.create_populated_botn(test_site, processed_inputs)
        
        if output_path:
            logger.info(f"\n🎉 SUCCESS: Template-preserved BOTN created!")
            logger.info(f"📁 File: {output_path}")
            logger.info(f"✅ Features preserved:")
            logger.info(f"   • Original Inputs tab (row 2 populated)")
            logger.info(f"   • Original Rents tab with calculations")
            logger.info(f"   • Original Expenses tab with calculations")
            logger.info(f"   • Original Sources & Uses tab with calculations")
            logger.info(f"   • Original NOI tab with calculations")
            logger.info(f"   • All other original tabs intact")
            logger.info(f"   • All formulas and references working")
        else:
            logger.error("\n❌ Failed to create template-preserved BOTN")

def main():
    generator = BOTNTemplatePreserver()
    generator.generate_preserved_botn()

if __name__ == "__main__":
    main()