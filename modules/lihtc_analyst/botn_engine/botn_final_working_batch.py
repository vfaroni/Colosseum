#!/usr/bin/env python3
"""
Final Working BOTN Batch Processor
Processes multiple sites efficiently with proven approach
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

class FinalWorkingBOTNBatch:
    """Final working batch processor for BOTN files"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        self.outputs_path = self.base_path / "outputs"
        
        self.outputs_path.mkdir(exist_ok=True)
    
    def get_batch_inputs(self):
        """Get user inputs for batch processing"""
        print("\n" + "="*70)
        print("🏠 FINAL WORKING BATCH BOTN PROCESSOR")
        print("="*70)
        print("Enter inputs that will be applied to ALL sites:")
        print()
        
        # Housing Type
        print("1. Housing Type:")
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
            choice = input("   Choose (a/b/c/d): ").lower().strip()
            if choice in housing_options:
                housing_type = housing_options[choice]
                break
            print("   Please enter a, b, c, or d")
        
        # Other inputs with defaults
        credit_pricing = input("\n2. Credit Pricing (e.g. '80 cents', '0.85'): ").strip() or "80 cents"
        
        print("\n3. Credit Type:")
        print("   a) 4%")
        print("   b) 9%")
        credit_choice = input("   Choose (a/b): ").lower().strip()
        credit_type = '4%' if credit_choice == 'a' else '9%'
        
        loan_term = input("\n4. Construction Loan Term (months): ").strip() or "36"
        cap_rate = input("\n5. Market Cap Rate (%): ").strip() or "5"
        interest_rate = input("\n6. Financing Interest Rate (%): ").strip() or "6"
        
        print("\n7. Elevator:")
        print("   a) Elevator")
        print("   b) Non-Elevator")
        elevator_choice = input("   Choose (a/b): ").lower().strip()
        elevator = 'Elevator' if elevator_choice == 'a' else 'Non-Elevator'
        
        purchase_price = input("\n8. Default Purchase Price (e.g. '2M', '2000000'): ").strip() or "2000000"
        units = input("\n9. Number of Units: ").strip() or "100"
        unit_size = input("\n10. Average Unit Size (SF): ").strip() or "900"
        hard_cost = input("\n11. Hard Cost per SF: ").strip() or "250"
        
        return {
            'housing_type': housing_type,
            'credit_pricing': self.parse_credit_pricing(credit_pricing),
            'credit_type': credit_type,
            'loan_term': int(re.findall(r'\d+', loan_term)[0]),
            'cap_rate': float(re.findall(r'[\d.]+', cap_rate)[0]) / 100,
            'interest_rate': float(re.findall(r'[\d.]+', interest_rate)[0]) / 100,
            'elevator': elevator,
            'purchase_price': self.parse_purchase_price(purchase_price),
            'units': int(units),
            'unit_size': int(unit_size),
            'hard_cost': int(hard_cost)
        }
    
    def parse_credit_pricing(self, price_str):
        """Parse credit pricing string"""
        if 'cent' in price_str.lower():
            number = re.findall(r'\d+', price_str)[0]
            return float(number) / 100
        elif '%' in price_str:
            number = float(re.findall(r'[\d.]+', price_str)[0])
            return number / 100
        else:
            return float(price_str)
    
    def parse_purchase_price(self, price_str):
        """Parse purchase price string"""
        price_str = price_str.replace('$', '').replace(',', '').upper()
        if 'M' in price_str:
            number = float(re.findall(r'[\d.]+', price_str)[0])
            return int(number * 1000000)
        else:
            return int(re.findall(r'\d+', price_str)[0])
    
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
    
    def process_batch(self, num_sites=50):
        """Process batch of sites"""
        
        # Get user inputs
        try:
            inputs = self.get_batch_inputs()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Input cancelled")
            return
        
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
        
        logger.info(f"\n🚀 FINAL WORKING BATCH PROCESSING")
        logger.info(f"📊 Sites to process: {len(valid_sites)}")
        logger.info(f"🏠 Housing Type: {inputs['housing_type']}")
        logger.info(f"💰 Default Purchase Price: ${inputs['purchase_price']:,}")
        logger.info(f"🔢 Units per property: {inputs['units']}")
        
        # Step 1: Create all template copies (fast)
        logger.info("\n📋 Step 1: Creating template copies...")
        file_info = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, (idx, site) in enumerate(valid_sites):
            site_name = str(site.get('Property Name', f'Site_{idx}'))
            # Clean filename
            clean_name = re.sub(r'[<>:"/\\|?*]', '_', site_name)[:40]
            
            output_filename = f"FINAL_BOTN_{clean_name}_{timestamp}_{i:03d}.xlsx"
            output_path = self.outputs_path / output_filename
            
            shutil.copy2(self.template_path, output_path)
            
            file_info.append({
                'site': site,
                'path': output_path,
                'name': clean_name,
                'original_idx': idx
            })
            
            if (i + 1) % 10 == 0:
                logger.info(f"   Created {i + 1}/{len(valid_sites)} copies...")
        
        logger.info(f"✅ Created {len(file_info)} template copies")
        
        # Step 2: Process all files with single Excel session
        logger.info("\n🔧 Step 2: Processing files with Excel...")
        logger.info("   Excel will appear briefly - this is normal for batch processing")
        
        successful = []
        failed = []
        
        try:
            # Start Excel (visible to avoid hanging issues)
            app = xw.App(visible=True, add_book=False)
            app.display_alerts = False
            app.screen_updating = False  # This helps with speed
            
            logger.info("✅ Excel session started")
            
            for i, info in enumerate(file_info, 1):
                try:
                    logger.info(f"📝 Processing {i}/{len(file_info)}: {info['name']}")
                    
                    # Open workbook
                    wb = app.books.open(str(info['path']), update_links=False)
                    inputs_sheet = wb.sheets['Inputs']
                    
                    site = info['site']
                    
                    # Determine purchase price (site-specific or default)
                    site_price = self.clean_data_value(site.get('For Sale Price', 0))
                    purchase_price = float(site_price) if site_price and site_price != 0 else inputs['purchase_price']
                    
                    # Populate all input fields efficiently
                    data = [
                        self.clean_data_value(site.get('Property Name', '')),      # A2
                        self.clean_data_value(site.get('Property Address', '')),  # B2
                        self.format_county_name(site.get('County Name', '')),     # C2
                        self.get_cdlac_region(site.get('County Name', '')),       # D2
                        self.clean_data_value(site.get('State', 'CA')),           # E2
                        self.clean_data_value(site.get('Zip', '')),               # F2
                        purchase_price,                                           # G2
                        inputs['housing_type'],                                   # H2
                        inputs['credit_pricing'],                                 # I2
                        inputs['credit_type'],                                    # J2
                        inputs['loan_term'],                                      # K2
                        inputs['cap_rate'],                                       # L2
                        inputs['interest_rate'],                                  # M2
                        inputs['elevator'],                                       # N2
                        inputs['units'],                                          # O2
                        inputs['unit_size'],                                      # P2
                        inputs['hard_cost']                                       # Q2
                    ]
                    
                    # Write all data at once for efficiency
                    for col, value in enumerate(data, 1):
                        inputs_sheet.range(2, col).value = value
                    
                    # Save and close
                    wb.save()
                    wb.close()
                    
                    successful.append(info)
                    
                    # Progress update every 5 files
                    if i % 5 == 0:
                        logger.info(f"   ✅ Completed {i}/{len(file_info)} files")
                    
                    # Brief pause to prevent Excel overload
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"   ❌ Failed {info['name']}: {str(e)}")
                    failed.append({'info': info, 'error': str(e)})
                    
                    # Try to close workbook if it's open
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
        
        # Final summary
        success_rate = len(successful) / len(file_info) * 100 if file_info else 0
        
        logger.info(f"\n🏆 FINAL BATCH PROCESSING COMPLETE!")
        logger.info("="*70)
        logger.info(f"✅ Successful files: {len(successful)}")
        logger.info(f"❌ Failed files: {len(failed)}")
        logger.info(f"📈 Success rate: {success_rate:.1f}%")
        
        if successful:
            logger.info(f"\n📋 SAMPLE SUCCESSFUL FILES:")
            for info in successful[:5]:
                logger.info(f"   • {info['path'].name}")
            if len(successful) > 5:
                logger.info(f"   ... and {len(successful) - 5} more")
        
        if failed:
            logger.info(f"\n⚠️ FAILED FILES:")
            for failure in failed[:3]:
                logger.info(f"   • {failure['info']['name']}: {failure['error']}")
        
        logger.info(f"\n📁 All files saved in: {self.outputs_path}")
        
        return {
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate
        }

def main():
    processor = FinalWorkingBOTNBatch()
    
    print("\n" + "="*70)
    print("🎯 FINAL WORKING BOTN BATCH PROCESSOR")
    print("="*70)
    print("Choose batch size:")
    print("1. Test with 5 sites")
    print("2. Process 10 sites")
    print("3. Process 50 sites")
    print("4. Custom number")
    
    while True:
        choice = input("\nEnter choice (1/2/3/4): ").strip()
        if choice == '1':
            num_sites = 5
            break
        elif choice == '2':
            num_sites = 10
            break
        elif choice == '3':
            num_sites = 50
            break
        elif choice == '4':
            try:
                num_sites = int(input("Enter number of sites: "))
                if num_sites > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")
        else:
            print("Please choose 1, 2, 3, or 4.")
    
    results = processor.process_batch(num_sites)
    
    if results and results['success_rate'] >= 90:
        print(f"\n🎉 EXCELLENT! {results['success_rate']:.1f}% success rate")
        print("🚀 Permission-free batch processing is working perfectly!")
    elif results and results['success_rate'] >= 80:
        print(f"\n✅ GOOD! {results['success_rate']:.1f}% success rate")
        print("✨ Minor issues but overall success")
    else:
        print(f"\n⚠️ Some issues detected. Success rate: {results.get('success_rate', 0):.1f}%")

if __name__ == "__main__":
    main()