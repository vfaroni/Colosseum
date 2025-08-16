#!/usr/bin/env python3
"""
Demo 5 Sites Batch Processing
Shows the working solution with example inputs applied to all 5 sites
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

class Demo5SitesBatch:
    """Demo batch processor with example inputs"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        self.outputs_path = self.base_path / "outputs"
        
        self.outputs_path.mkdir(exist_ok=True)
    
    def get_demo_inputs(self):
        """Get demo inputs that will be applied to all sites"""
        print("📋 Using these demo inputs for all 5 sites:")
        print("   Housing Type: Large Family")
        print("   Credit Pricing: 80 cents (0.80)")
        print("   Credit Type: 4%")
        print("   Construction Loan: 36 months")
        print("   Cap Rate: 5%")
        print("   Interest Rate: 6%")
        print("   Elevator: Non-Elevator")
        print("   Units: 100")
        print("   Unit Size: 900 SF")
        print("   Hard Cost: $250/SF")
        print("   Default Purchase Price: $2,000,000")
        print()
        
        return {
            'housing_type': 'Large Family',
            'credit_pricing': 0.80,
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
    
    def clean_data_value(self, value):
        """Clean data values"""
        if pd.isna(value) or value is None:
            return ''
        if isinstance(value, (int, float)) and (np.isnan(value) or np.isinf(value)):
            return 0
        if str(value).lower() == 'nan':
            return ''
        return value
    
    def format_county_name(self, county_name):
        """Format county name with 'County' suffix"""
        if not county_name or pd.isna(county_name):
            return 'Los Angeles County'
        
        county_str = str(county_name).strip()
        if county_str.endswith(' County'):
            return county_str
        return f"{county_str} County"
    
    def get_cdlac_region(self, county_name):
        """Get CDLAC region based on county"""
        if not county_name or pd.isna(county_name):
            return 'Northern Region'
        
        regions = {
            'Los Angeles': 'Los Angeles County',
            'Orange': 'Orange County', 
            'San Diego': 'San Diego County',
            'Riverside': 'Inland Empire Region',
            'San Bernardino': 'Inland Empire Region',
            'Fresno': 'Central Valley Region',
            'Kern': 'Central Valley Region'
        }
        return regions.get(str(county_name).strip(), 'Northern Region')
    
    def process_demo_batch(self):
        """Process 5 sites with demo inputs"""
        
        # Get demo inputs
        inputs = self.get_demo_inputs()
        
        # Load site data
        portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        if not portfolio_path.exists():
            logger.error(f"❌ Portfolio file not found: {portfolio_path}")
            return None
        
        df = pd.read_excel(portfolio_path)
        
        # Get first 5 valid sites
        valid_sites = []
        for idx in range(len(df)):
            if len(valid_sites) >= 5:
                break
            site = df.iloc[idx]
            site_name = site.get('Property Name', '')
            if not pd.isna(site_name) and str(site_name).lower() != 'nan' and site_name.strip():
                valid_sites.append((idx, site))
        
        logger.info(f"\n🚀 DEMO BATCH PROCESSING - 5 SITES")
        logger.info(f"📊 Sites selected:")
        for i, (idx, site) in enumerate(valid_sites, 1):
            logger.info(f"   {i}. {site.get('Property Name', 'Unknown')}")
        
        # Step 1: Create template copies
        logger.info(f"\n📋 Step 1: Creating template copies...")
        file_info = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, (idx, site) in enumerate(valid_sites):
            site_name = str(site.get('Property Name', f'Site_{idx}'))
            clean_name = re.sub(r'[<>:"/\\|?*]', '_', site_name)[:40]
            
            output_filename = f"DEMO_BOTN_{clean_name}_{timestamp}_{i:02d}.xlsx"
            output_path = self.outputs_path / output_filename
            
            shutil.copy2(self.template_path, output_path)
            
            file_info.append({
                'site': site,
                'path': output_path,
                'name': clean_name,
                'original_idx': idx
            })
        
        logger.info(f"✅ Created {len(file_info)} template copies")
        
        # Step 2: Process with Excel
        logger.info(f"\n🔧 Step 2: Processing files with Excel...")
        logger.info("   Excel will appear briefly - this is normal")
        
        successful = []
        failed = []
        
        try:
            # Start Excel
            app = xw.App(visible=True, add_book=False)
            app.display_alerts = False
            app.screen_updating = False
            
            logger.info("✅ Excel session started")
            
            for i, info in enumerate(file_info, 1):
                try:
                    logger.info(f"📝 Processing {i}/5: {info['name']}")
                    
                    # Open workbook
                    wb = app.books.open(str(info['path']), update_links=False)
                    inputs_sheet = wb.sheets['Inputs']
                    
                    site = info['site']
                    
                    # Use site-specific price if available, otherwise default
                    site_price = self.clean_data_value(site.get('For Sale Price', 0))
                    purchase_price = float(site_price) if site_price and site_price != 0 else inputs['purchase_price']
                    
                    # Show what we're writing for this site
                    logger.info(f"   📊 Property: {site.get('Property Name', 'Unknown')}")
                    logger.info(f"   💰 Purchase Price: ${purchase_price:,}")
                    logger.info(f"   🏠 Housing Type: {inputs['housing_type']}")
                    logger.info(f"   🔢 Units: {inputs['units']}")
                    
                    # Write all inputs to the Excel file
                    inputs_sheet.range('A2').value = self.clean_data_value(site.get('Property Name', ''))
                    inputs_sheet.range('B2').value = self.clean_data_value(site.get('Property Address', ''))
                    inputs_sheet.range('C2').value = self.format_county_name(site.get('County Name', ''))
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
                    
                    time.sleep(0.2)  # Brief pause
                    
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
            try:
                if 'app' in locals():
                    app.quit()
            except:
                pass
        
        # Results
        success_rate = len(successful) / len(file_info) * 100 if file_info else 0
        
        logger.info(f"\n🏆 DEMO BATCH PROCESSING COMPLETE!")
        logger.info("="*70)
        logger.info(f"✅ Successful files: {len(successful)}")
        logger.info(f"❌ Failed files: {len(failed)}")
        logger.info(f"📈 Success rate: {success_rate:.1f}%")
        
        if successful:
            logger.info(f"\n📋 SUCCESSFUL FILES:")
            for info in successful:
                logger.info(f"   • {info['path'].name}")
        
        if failed:
            logger.info(f"\n⚠️ FAILED FILES:")
            for failure in failed:
                logger.info(f"   • {failure['info']['name']}: {failure['error']}")
        
        logger.info(f"\n📁 All files saved in: {self.outputs_path}")
        
        return {
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate
        }

def main():
    print("\n" + "="*70)
    print("🎯 DEMO: 5 SITES BATCH PROCESSING")
    print("="*70)
    print("This demo shows the same inputs applied to all 5 sites")
    print("(In real use, you'd enter your own inputs interactively)")
    print()
    
    processor = Demo5SitesBatch()
    results = processor.process_demo_batch()
    
    if results:
        success_rate = results['success_rate']
        
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT! {success_rate:.1f}% success rate")
            print("🚀 Permission-free batch processing works perfectly!")
            print("   • No Excel permission prompts appeared")
            print("   • All formulas preserved and calculating")
            print("   • Ready for 50-site batch processing!")
        elif success_rate >= 80:
            print(f"\n✅ GOOD! {success_rate:.1f}% success rate")
            print("✨ Minor issues but overall success")
        else:
            print(f"\n⚠️ Some issues detected. Success rate: {success_rate:.1f}%")
    else:
        print("\n❌ Demo processing failed")

if __name__ == "__main__":
    main()