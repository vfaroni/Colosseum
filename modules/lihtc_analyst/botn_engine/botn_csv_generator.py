#!/usr/bin/env python3
"""
CSV BOTN Generator - Creates CSV data that can be copy-pasted into original template
"""

import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVBOTNGenerator:
    """Generate BOTN data as CSV for manual paste into original template"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
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
    
    def create_csv_data(self, site_data, user_inputs):
        """Create CSV data for manual paste"""
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        site_name = str(site_data.get('Property Name', 'Site')).replace(' ', '_').replace('/', '_')
        
        # Prepare complete data row
        complete_data = [
            str(site_data.get('Property Name', '')),
            str(site_data.get('Property Address', '')),
            str(site_data.get('County Name', '')),
            str(self.get_cdlac_region(site_data.get('County Name'))),
            str(site_data.get('State', '')),
            site_data.get('Zip', ''),
            float(site_data.get('For Sale Price', 0)) if site_data.get('For Sale Price') else 0,
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
        
        # Headers
        headers = [
            'Property Name', 'Address', 'County:', 'CDLAC Region', 'State:', 'Zip Code:', 
            'Purchase Price', 'Housing Type', 'Credit Pricing', 'Credit Type', 
            'Construciton Loan Term', 'Market Cap Rate', 'Financing Interest Rate', 
            'Elevator', '# Units', 'Avg Unit Size', 'Hard Cost/SF'
        ]
        
        # Create DataFrame
        df = pd.DataFrame([complete_data], columns=headers)
        
        # Save CSV files
        csv_path = self.base_path / "outputs" / f"BOTN_DATA_{site_name}_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        
        # Also save transposed version for easier copying
        transposed_path = self.base_path / "outputs" / f"BOTN_DATA_TRANSPOSED_{site_name}_{timestamp}.csv"
        df_transposed = df.T
        df_transposed.columns = ['Value']
        df_transposed.to_csv(transposed_path, header=True)
        
        return csv_path, transposed_path, df
    
    def generate_csv_botn(self):
        """Generate CSV BOTN data"""
        
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
        logger.info("📊 CSV BOTN DATA GENERATION")
        logger.info("="*70)
        logger.info(f"🏠 Site: {test_site.get('Property Name')}")
        logger.info(f"📍 Address: {test_site.get('Property Address')}")
        logger.info(f"🔧 Method: CSV export for manual paste into template")
        
        # Create CSV data
        csv_path, transposed_path, df = self.create_csv_data(test_site, processed_inputs)
        
        logger.info(f"\n✅ CSV files created:")
        logger.info(f"📁 Horizontal data: {csv_path}")
        logger.info(f"📁 Vertical data: {transposed_path}")
        
        # Display the data
        logger.info(f"\n📋 DATA TO PASTE INTO TEMPLATE:")
        logger.info("="*50)
        logger.info("Copy this data and paste into Row 2 of your template's Inputs tab:")
        logger.info("")
        
        # Print values in a format easy to copy
        data_row = df.iloc[0]
        for i, (col, value) in enumerate(data_row.items(), 1):
            logger.info(f"Cell {chr(64+i)}2: {value}")
        
        logger.info("\n" + "="*70)
        logger.info("📖 INSTRUCTIONS:")
        logger.info("1. Open your original CABOTNTemplate.xlsx file")
        logger.info("2. Go to the Inputs tab")
        logger.info("3. Copy the values above and paste into Row 2")
        logger.info("4. All calculations should work perfectly!")
        logger.info("5. All dropdowns will remain functional")
        logger.info("="*70)
        
def main():
    generator = CSVBOTNGenerator()
    generator.generate_csv_botn()

if __name__ == "__main__":
    main()