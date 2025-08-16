#!/usr/bin/env python3
"""
Binary Approach BOTN Generator - Use xlwings for one template, then binary copy approach
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

class BinaryApproachBOTNGenerator:
    """Create one perfect template with xlwings, then use that as the master template"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        self.master_template_path = self.base_path / "outputs" / "MASTER_BOTN_TEMPLATE.xlsx"
        
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
    
    def create_master_template_with_xlwings(self):
        """Create one perfect master template using xlwings with sample data"""
        
        if self.master_template_path.exists():
            logger.info("✅ Master template already exists, skipping creation")
            return True
        
        try:
            logger.info("🔧 Creating master template with xlwings...")
            
            # Copy original template
            shutil.copy2(self.template_path, self.master_template_path)
            
            # Open with xlwings and populate with sample data
            app = xw.App(visible=False, add_book=False)
            wb = app.books.open(str(self.master_template_path))
            inputs_sheet = wb.sheets['Inputs']
            
            # Sample data that shows the format
            sample_data = [
                "SAMPLE_SITE_NAME",           # A2
                "123 Sample Street",          # B2
                "Los Angeles County",         # C2
                "Los Angeles County",         # D2
                "CA",                         # E2
                "90210",                      # F2
                2000000,                      # G2
                "Large Family",               # H2
                0.8,                          # I2
                "4%",                         # J2
                36,                           # K2
                0.05,                         # L2
                0.06,                         # M2
                "Non-Elevator",               # N2
                100,                          # O2
                900,                          # P2
                250                           # Q2
            ]
            
            # Populate row 2
            for col_idx, value in enumerate(sample_data, 1):
                cell_address = f"{chr(64 + col_idx)}2"
                inputs_sheet.range(cell_address).value = value
            
            # Save and close
            wb.save()
            wb.close()
            app.quit()
            
            logger.info("✅ Master template created with xlwings")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create master template: {str(e)}")
            try:
                if 'wb' in locals():
                    wb.close()
                if 'app' in locals():
                    app.quit()
            except:
                pass
            return False
    
    def create_site_from_master(self, site_data):
        """Create site BOTN by copying master and using text replacement"""
        
        if not self.master_template_path.exists():
            logger.error("❌ Master template not found")
            return None
        
        site_name = str(site_data.get('Property Name', 'Site')).replace(' ', '_').replace('/', '_')
        if pd.isna(site_name) or site_name.lower() == 'nan':
            site_name = 'Site'
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"BINARY_BOTN_{site_name}_{timestamp}.xlsx"
        output_path = self.base_path / "outputs" / output_filename
        
        try:
            logger.info(f"🔧 Creating BOTN for: {site_name}")
            
            # Copy the master template (which has perfect xlwings formatting)
            shutil.copy2(self.master_template_path, output_path)
            
            # Now we have a choice:
            # Option 1: Use xlwings again (may prompt)
            # Option 2: Try openpyxl on the already-populated template
            # Option 3: Use binary search/replace
            
            # Let's try Option 2: openpyxl on already-populated template
            import openpyxl
            
            workbook = openpyxl.load_workbook(output_path, data_only=False)
            inputs_sheet = workbook['Inputs']
            
            # Determine purchase price
            site_price = self.clean_data_value(site_data.get('For Sale Price', 0))
            if site_price and site_price != '' and site_price != 0:
                purchase_price = float(site_price)
            else:
                purchase_price = 2000000  # Default
            
            # Replace the sample data with real site data
            inputs_sheet['A2'].value = self.clean_data_value(site_data.get('Property Name', ''))
            inputs_sheet['B2'].value = self.clean_data_value(site_data.get('Property Address', ''))
            inputs_sheet['C2'].value = self.get_template_county_format(self.clean_data_value(site_data.get('County Name', '')))
            inputs_sheet['D2'].value = self.get_cdlac_region(self.clean_data_value(site_data.get('County Name')))
            inputs_sheet['E2'].value = self.clean_data_value(site_data.get('State', ''))
            inputs_sheet['F2'].value = self.clean_data_value(site_data.get('Zip', ''))
            inputs_sheet['G2'].value = purchase_price
            # Keep H2-Q2 as they were (the user inputs from master template)
            
            workbook.save(output_path)
            workbook.close()
            
            logger.info(f"✅ Created: {output_filename}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error creating site BOTN: {str(e)}")
            return None
    
    def test_binary_approach(self):
        """Test the binary approach"""
        
        logger.info("\n" + "="*70)
        logger.info("🔬 TESTING BINARY/MASTER TEMPLATE APPROACH")
        logger.info("="*70)
        logger.info("Strategy: Create one perfect template with xlwings, then copy/modify")
        
        # Step 1: Create master template
        if not self.create_master_template_with_xlwings():
            logger.error("❌ Failed to create master template")
            return
        
        # Step 2: Load site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        test_site = df.iloc[0]  # First site
        
        logger.info(f"\n🏠 Testing with site: {test_site.get('Property Name')}")
        logger.info(f"📍 Address: {test_site.get('Property Address')}")
        
        # Step 3: Create site BOTN from master
        output_path = self.create_site_from_master(test_site)
        
        if output_path:
            logger.info(f"\n🎉 SUCCESS: Binary approach BOTN created!")
            logger.info(f"📁 File: {output_path}")
            logger.info(f"✅ This should preserve all dropdowns and formulas from xlwings master")
            logger.info(f"✅ Test by opening both master and site file in Excel")
        else:
            logger.error("\n❌ Failed binary approach test")

def main():
    generator = BinaryApproachBOTNGenerator()
    generator.test_binary_approach()

if __name__ == "__main__":
    main()