#!/usr/bin/env python3
"""
Working Permission-Free BOTN Batch Processor
Simplified approach that works reliably on macOS
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

class WorkingPermissionFreeBOTN:
    """Working permission-free BOTN processor"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        self.outputs_path = self.base_path / "outputs"
        
        self.outputs_path.mkdir(exist_ok=True)
    
    def get_simple_inputs(self):
        """Get simplified inputs for testing"""
        print("\n" + "="*60)
        print("🏠 SIMPLIFIED BATCH BOTN INPUTS")
        print("="*60)
        print("Using simplified inputs for testing:")
        print()
        
        # Simple defaults for testing
        inputs = {
            'housing_type': 'Large Family',
            'credit_pricing': 0.80,  # 80 cents
            'credit_type': '4%',
            'loan_term': 36,
            'cap_rate': 0.05,
            'interest_rate': 0.06,
            'elevator': 'Non-Elevator',
            'purchase_price': 2000000,
            'units': 100,
            'unit_size': 900,
            'hard_cost': 250
        }
        
        print(f"Housing Type: {inputs['housing_type']}")
        print(f"Credit Pricing: {inputs['credit_pricing']}")
        print(f"Credit Type: {inputs['credit_type']}")
        print(f"Units: {inputs['units']}")
        print(f"Purchase Price: ${inputs['purchase_price']:,}")
        
        return inputs
    
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
    
    def get_county_with_suffix(self, county_name):
        """Add County suffix if needed"""
        if not county_name or pd.isna(county_name):
            return 'Los Angeles County'
        
        county_str = str(county_name).strip()
        if county_str.endswith(' County'):
            return county_str
        return f"{county_str} County"
    
    def get_cdlac_region(self, county_name):
        """Get CDLAC region"""
        if not county_name or pd.isna(county_name):
            return 'Northern Region'
            
        cdlac_regions = {
            'Los Angeles': 'Los Angeles County',
            'Orange': 'Orange County',
            'San Diego': 'San Diego County',
            'Riverside': 'Inland Empire Region',
            'San Bernardino': 'Inland Empire Region',
        }
        return cdlac_regions.get(str(county_name), 'Northern Region')
    
    def process_batch_working(self, num_sites=5):
        """Process batch with working approach"""
        
        # Get inputs
        inputs = self.get_simple_inputs()
        
        # Load site data
        portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        if not portfolio_path.exists():
            logger.error(f"❌ Portfolio file not found: {portfolio_path}")
            return
        
        df = pd.read_excel(portfolio_path)
        
        # Get valid sites
        valid_sites = []
        for idx in range(len(df)):
            if len(valid_sites) >= num_sites:
                break
            site = df.iloc[idx]
            site_name = site.get('Property Name', '')
            if not pd.isna(site_name) and str(site_name).lower() != 'nan' and site_name.strip():
                valid_sites.append((idx, site))
        
        logger.info(f"\n🚀 Processing {len(valid_sites)} sites with working approach")
        
        # Step 1: Create template copies (fast)
        logger.info("📋 Creating template copies...")
        file_info = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, (idx, site) in enumerate(valid_sites):
            site_name = str(site.get('Property Name', f'Site_{idx}'))
            # Clean filename
            clean_name = re.sub(r'[<>:"/\\|?*]', '_', site_name)[:30]
            
            output_filename = f"WORKING_BOTN_{clean_name}_{timestamp}_{i:02d}.xlsx"
            output_path = self.outputs_path / output_filename
            
            shutil.copy2(self.template_path, output_path)
            
            file_info.append({
                'site': site,
                'path': output_path,
                'name': clean_name
            })
        
        logger.info(f"✅ Created {len(file_info)} template copies")
        
        # Step 2: Process with Excel (visible for now to avoid hanging)
        logger.info("🔧 Processing with Excel...")
        
        successful = []
        failed = []
        
        try:
            # Start Excel once for all files
            app = xw.App(visible=False, add_book=False)  # Try invisible first
            app.display_alerts = False
            app.screen_updating = False
            
            logger.info("✅ Excel session started")
            
            for i, info in enumerate(file_info, 1):
                try:
                    logger.info(f"📝 Processing {i}/{len(file_info)}: {info['name']}")
                    
                    # Open workbook
                    wb = app.books.open(str(info['path']), update_links=False)
                    inputs_sheet = wb.sheets['Inputs']
                    
                    site = info['site']
                    
                    # Get site-specific purchase price or use default
                    site_price = self.clean_data_value(site.get('For Sale Price', 0))
                    purchase_price = float(site_price) if site_price and site_price != 0 else inputs['purchase_price']
                    
                    # Populate key inputs
                    inputs_sheet.range('A2').value = self.clean_data_value(site.get('Property Name', ''))
                    inputs_sheet.range('B2').value = self.clean_data_value(site.get('Property Address', ''))
                    inputs_sheet.range('C2').value = self.get_county_with_suffix(site.get('County Name', ''))
                    inputs_sheet.range('D2').value = self.get_cdlac_region(site.get('County Name', ''))
                    inputs_sheet.range('E2').value = self.clean_data_value(site.get('State', 'CA'))
                    inputs_sheet.range('F2').value = self.clean_data_value(site.get('Zip', ''))
                    inputs_sheet.range('G2').value = purchase_price
                    inputs_sheet.range('H2').value = inputs['housing_type']
                    inputs_sheet.range('I2').value = inputs['credit_pricing']
                    inputs_sheet.range('J2').value = inputs['credit_type']
                    inputs_sheet.range('K2').value = inputs['loan_term']
                    inputs_sheet.range('L2').value = inputs['cap_rate']
                    inputs_sheet.range('M2').value = inputs['interest_rate']
                    inputs_sheet.range('N2').value = inputs['elevator']
                    inputs_sheet.range('O2').value = inputs['units']
                    inputs_sheet.range('P2').value = inputs['unit_size']
                    inputs_sheet.range('Q2').value = inputs['hard_cost']
                    
                    # Save and close
                    wb.save()
                    wb.close()
                    
                    successful.append(info)
                    logger.info(f"   ✅ Success: {info['name']}")
                    
                except Exception as e:
                    logger.error(f"   ❌ Failed {info['name']}: {str(e)}")
                    failed.append({'info': info, 'error': str(e)})
                    
                    try:
                        if 'wb' in locals():
                            wb.close()
                    except:
                        pass
            
            # Close Excel
            app.quit()
            logger.info("🔧 Excel session closed")
            
        except Exception as e:
            logger.error(f"❌ Excel session error: {str(e)}")
        
        # Summary
        logger.info(f"\n🏆 BATCH PROCESSING COMPLETE!")
        logger.info(f"✅ Successful: {len(successful)}")
        logger.info(f"❌ Failed: {len(failed)}")
        logger.info(f"📈 Success rate: {len(successful)/len(file_info)*100:.1f}%")
        
        if successful:
            logger.info(f"\n📋 SUCCESSFUL FILES:")
            for info in successful:
                logger.info(f"   • {info['path'].name}")
        
        if failed:
            logger.info(f"\n⚠️ FAILED FILES:")
            for failure in failed:
                logger.info(f"   • {failure['info']['name']}: {failure['error']}")
        
        logger.info(f"\n📁 Files saved in: {self.outputs_path}")
        
        return {
            'successful': successful,
            'failed': failed,
            'success_rate': len(successful)/len(file_info)*100
        }


def main():
    processor = WorkingPermissionFreeBOTN()
    
    print("\n" + "="*60)
    print("🎯 WORKING PERMISSION-FREE BOTN PROCESSOR")
    print("="*60)
    
    num_sites = 5  # Start with 5 for testing
    print(f"Processing {num_sites} sites for validation...")
    
    results = processor.process_batch_working(num_sites)
    
    if results and results['success_rate'] >= 80:
        print(f"\n🎉 SUCCESS! {results['success_rate']:.1f}% success rate")
        print("Ready to scale to 50 sites!")
    else:
        print(f"\n⚠️ Some issues detected. Success rate: {results['success_rate']:.1f}%")


if __name__ == "__main__":
    main()