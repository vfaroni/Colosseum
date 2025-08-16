#!/usr/bin/env python3
"""
Production Batch Processor - Process 50 sites at a time with ranking and broker contacts
Creates BOTN files and comprehensive ranking spreadsheet
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

class ProductionBatchProcessor:
    """Production batch processor with ranking and broker contacts"""
    
    def __init__(self, batch_name="Production 1", start_index=0, batch_size=50):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        self.production_path = self.base_path / batch_name
        self.source_file = "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415_BACKUP_20250801_093840.xlsx"
        self.start_index = start_index
        self.batch_size = batch_size
        
        # Create production directory
        self.production_path.mkdir(exist_ok=True)
        self.outputs_path = self.production_path
        
    def get_production_inputs(self):
        """Get production inputs for batch processing"""
        print("\n" + "="*70)
        print("🏭 PRODUCTION BATCH PROCESSOR - 50 SITES")
        print("="*70)
        print("Enter inputs that will be applied to ALL 50 sites:")
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
    
    def calculate_development_score(self, site):
        """Calculate development opportunity score"""
        score = 0
        factors = []
        
        # Price factor (lower price = higher score)
        price = self.clean_data_value(site.get('For Sale Price', 0))
        if price and price > 0:
            if price < 1000000:
                score += 30
                factors.append("Excellent Price (<$1M)")
            elif price < 3000000:
                score += 20
                factors.append("Good Price (<$3M)")
            elif price < 5000000:
                score += 10
                factors.append("Fair Price (<$5M)")
            else:
                score += 5
                factors.append("High Price (>$5M)")
        else:
            score += 15
            factors.append("Price TBD")
        
        # County/Market factor
        county = str(self.clean_data_value(site.get('County Name', ''))).strip()
        if county:
            if county in ['Los Angeles', 'Orange', 'San Diego']:
                score += 25
                factors.append("Prime County")
            elif county in ['Riverside', 'San Bernardino', 'Fresno']:
                score += 20
                factors.append("Good County")
            else:
                score += 15
                factors.append("Developing County")
        
        # Size factor (acreage if available)
        try:
            # Look for size indicators in property name or other fields
            prop_name = str(self.clean_data_value(site.get('Property Name', ''))).lower()
            if any(term in prop_name for term in ['acre', 'ac ', ' ac']):
                acres_match = re.search(r'(\d+\.?\d*)\s*(?:acre|ac)', prop_name)
                if acres_match:
                    acres = float(acres_match.group(1))
                    if 2 <= acres <= 5:
                        score += 20
                        factors.append(f"Ideal Size ({acres} acres)")
                    elif 1 <= acres <= 8:
                        score += 15
                        factors.append(f"Good Size ({acres} acres)")
                    else:
                        score += 10
                        factors.append(f"Large Size ({acres} acres)")
                else:
                    score += 10
                    factors.append("Multi-acre site")
            else:
                score += 10
                factors.append("Size TBD")
        except:
            score += 10
            factors.append("Size TBD")
        
        # Development readiness factor
        prop_name = str(self.clean_data_value(site.get('Property Name', ''))).lower()
        if any(term in prop_name for term in ['development', 'opportunity', 'land']):
            score += 15
            factors.append("Development Ready")
        elif any(term in prop_name for term in ['zoned', 'entitled', 'approved']):
            score += 20
            factors.append("Pre-Entitled")
        else:
            score += 10
            factors.append("Standard Site")
        
        # Location quality
        market = str(self.clean_data_value(site.get('Market Name', ''))).strip()
        if market and any(term in market.lower() for term in ['metro', 'central', 'downtown', 'transit']):
            score += 10
            factors.append("Prime Location")
        else:
            score += 5
            factors.append("Standard Location")
        
        return min(score, 100), factors  # Cap at 100
    
    def create_ranking_spreadsheet(self, sites_data, inputs):
        """Create comprehensive ranking spreadsheet with broker contacts"""
        
        # Calculate scores for all sites
        ranked_sites = []
        for i, site in enumerate(sites_data):
            score, factors = self.calculate_development_score(site)
            
            # Get actual purchase price or default
            site_price = self.clean_data_value(site.get('For Sale Price', 0))
            purchase_price = float(site_price) if site_price and site_price != 0 else inputs['purchase_price']
            
            ranked_sites.append({
                'Rank': 0,  # Will be set after sorting
                'Property_Name': self.clean_data_value(site.get('Property Name', '')),
                'Property_Address': self.clean_data_value(site.get('Property Address', '')),
                'County': self.clean_data_value(site.get('County Name', '')),
                'Market': self.clean_data_value(site.get('Market Name', '')),
                'Submarket': self.clean_data_value(site.get('Submarket Name', '')),
                'Purchase_Price': purchase_price,
                'Development_Score': score,
                'Score_Factors': '; '.join(factors),
                'Sale_Company': self.clean_data_value(site.get('Sale Company Name', '')),
                'Broker_Contact': self.clean_data_value(site.get('Sale Company Contact', '')),
                'Company_Address': self.clean_data_value(site.get('Sale Company Address', '')),
                'Company_Phone': self.clean_data_value(site.get('Sale Company Phone', '')),
                'Housing_Type': inputs['housing_type'],
                'Credit_Type': inputs['credit_type'],
                'Units': inputs['units'],
                'BOTN_File': f"{self.production_path.name.replace(' ', '').upper()}_BOTN_{self.clean_data_value(site.get('Property Name', f'Site_{i}'))}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            })
        
        # Sort by development score (highest first)
        ranked_sites.sort(key=lambda x: x['Development_Score'], reverse=True)
        
        # Assign ranks
        for i, site in enumerate(ranked_sites, 1):
            site['Rank'] = i
        
        # Create DataFrame
        df = pd.DataFrame(ranked_sites)
        
        # Create Excel file with formatting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_name = self.production_path.name.replace(" ", "_")
        excel_path = self.production_path / f"{batch_name}_Site_Rankings_Broker_Contacts_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Site Rankings', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Site Rankings']
            
            # Create formats
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            price_format = workbook.add_format({'num_format': '$#,##0'})
            score_format = workbook.add_format({'num_format': '0', 'fg_color': '#E2EFDA'})
            
            # Format headers
            for col_num, column in enumerate(df.columns):
                worksheet.write(0, col_num, column, header_format)
            
            # Format data
            worksheet.set_column('A:A', 8)  # Rank
            worksheet.set_column('B:B', 30) # Property Name
            worksheet.set_column('C:C', 35) # Address
            worksheet.set_column('D:D', 15) # County
            worksheet.set_column('E:E', 20) # Market
            worksheet.set_column('F:F', 20) # Submarket
            worksheet.set_column('G:G', 15, price_format) # Price
            worksheet.set_column('H:H', 12, score_format) # Score
            worksheet.set_column('I:I', 40) # Score Factors
            worksheet.set_column('J:J', 25) # Sale Company
            worksheet.set_column('K:K', 25) # Broker Contact
            worksheet.set_column('L:L', 30) # Company Address
            worksheet.set_column('M:M', 15) # Phone
            worksheet.set_column('N:P', 15) # Housing, Credit, Units
            worksheet.set_column('Q:Q', 40) # BOTN File
            
            # Add summary sheet
            summary_data = {
                'Metric': [
                    'Total Sites Analyzed',
                    'Top Scoring Site',
                    'Average Score',
                    'Sites Above 80 Score',
                    'Sites Above 70 Score',
                    'Processing Date',
                    'Housing Type',
                    'Credit Type',
                    'Default Units'
                ],
                'Value': [
                    len(df),
                    df.iloc[0]['Property_Name'] if len(df) > 0 else 'N/A',
                    f"{df['Development_Score'].mean():.1f}",
                    len(df[df['Development_Score'] >= 80]),
                    len(df[df['Development_Score'] >= 70]),
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    inputs['housing_type'],
                    inputs['credit_type'],
                    inputs['units']
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        logger.info(f"📊 Ranking spreadsheet created: {excel_path.name}")
        return excel_path, ranked_sites
    
    def process_production_batch(self, num_sites=50):
        """Process production batch with ranking"""
        
        # Get user inputs
        try:
            inputs = self.get_production_inputs()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Input cancelled")
            return
        
        # Load source data
        source_path = self.sites_path / self.source_file
        if not source_path.exists():
            logger.error(f"❌ Source file not found: {source_path}")
            return
        
        df = pd.read_excel(source_path)
        
        # Get valid sites starting from specified index
        valid_sites = []
        for idx in range(self.start_index, len(df)):
            if len(valid_sites) >= self.batch_size:
                break
            site = df.iloc[idx]
            site_name = site.get('Property Name', '')
            if not pd.isna(site_name) and str(site_name).lower() != 'nan' and site_name.strip():
                valid_sites.append(site)
        
        logger.info(f"\n🏭 PRODUCTION BATCH PROCESSING")
        logger.info(f"📊 Processing {len(valid_sites)} sites from {len(df)} total")
        logger.info(f"🏠 Housing Type: {inputs['housing_type']}")
        logger.info(f"💰 Credit Type: {inputs['credit_type']}")
        logger.info(f"📁 Output Directory: {self.production_path}")
        
        # Create ranking spreadsheet first
        logger.info(f"\n📊 Creating site rankings and broker contact spreadsheet...")
        ranking_file, ranked_sites = self.create_ranking_spreadsheet(valid_sites, inputs)
        
        # Process BOTN files for top sites
        logger.info(f"\n🔧 Processing BOTN files for all {len(valid_sites)} sites...")
        
        # Create template copies
        file_info = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, site in enumerate(valid_sites):
            site_name = str(site.get('Property Name', f'Site_{i}'))
            clean_name = re.sub(r'[<>:"/\\|?*]', '_', site_name)[:40]
            
            batch_prefix = self.production_path.name.replace(" ", "").upper()
            output_filename = f"{batch_prefix}_BOTN_{clean_name}_{timestamp}_{i:03d}.xlsx"
            output_path = self.production_path / output_filename
            
            shutil.copy2(self.template_path, output_path)
            
            file_info.append({
                'site': site,
                'path': output_path,
                'name': clean_name,
                'rank': next((r['Rank'] for r in ranked_sites if r['Property_Name'] == site.get('Property Name', '')), i+1)
            })
        
        logger.info(f"✅ Created {len(file_info)} template copies")
        
        # Process with Excel
        successful = []
        failed = []
        
        try:
            app = xw.App(visible=True, add_book=False)
            app.display_alerts = False
            app.screen_updating = False
            
            for i, info in enumerate(file_info, 1):
                try:
                    logger.info(f"📝 Processing {i}/{len(file_info)} (Rank #{info['rank']}): {info['name']}")
                    
                    wb = app.books.open(str(info['path']), update_links=False)
                    inputs_sheet = wb.sheets['Inputs']
                    
                    site = info['site']
                    
                    # Calculate purchase price
                    site_price = self.clean_data_value(site.get('For Sale Price', 0))
                    purchase_price = float(site_price) if site_price and site_price != 0 else inputs['purchase_price']
                    
                    # Populate inputs
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
                    
                    wb.save()
                    wb.close()
                    
                    successful.append(info)
                    
                    if i % 10 == 0:
                        logger.info(f"   ✅ Completed {i}/{len(file_info)} files")
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"   ❌ Failed {info['name']}: {str(e)}")
                    failed.append({'info': info, 'error': str(e)})
                    try:
                        if 'wb' in locals():
                            wb.close()
                    except:
                        pass
            
            app.quit()
            
        except Exception as e:
            logger.error(f"❌ Excel session error: {str(e)}")
        
        # Final summary
        success_rate = len(successful) / len(file_info) * 100 if file_info else 0
        
        logger.info(f"\n🏆 PRODUCTION BATCH COMPLETE!")
        logger.info("="*70)
        logger.info(f"✅ Successful BOTN files: {len(successful)}")
        logger.info(f"❌ Failed BOTN files: {len(failed)}")
        logger.info(f"📈 Success rate: {success_rate:.1f}%")
        logger.info(f"📊 Ranking spreadsheet: {ranking_file.name}")
        logger.info(f"📁 All files in: {self.production_path}")
        
        # Show top 10 sites
        if ranked_sites:
            logger.info(f"\n🏆 TOP 10 DEVELOPMENT OPPORTUNITIES:")
            for site in ranked_sites[:10]:
                logger.info(f"   {site['Rank']:2d}. {site['Property_Name']} (Score: {site['Development_Score']}) - {site['Sale_Company']}")
        
        return {
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate,
            'ranking_file': ranking_file,
            'top_sites': ranked_sites[:10]
        }

def main():
    processor = ProductionBatchProcessor()
    
    print("\n" + "="*70)
    print("🏭 PRODUCTION BATCH PROCESSOR WITH RANKING")
    print("="*70)
    print("This will process 50 sites and create:")
    print("• 50 individual BOTN Excel files")
    print("• Comprehensive ranking spreadsheet with broker contacts")
    print("• Development opportunity scores for each site")
    print()
    
    results = processor.process_production_batch(num_sites=50)
    
    if results and results['success_rate'] >= 90:
        print(f"\n🎉 EXCELLENT! Production batch completed successfully!")
        print(f"📊 Check your ranking spreadsheet for broker contact information")
        print(f"🏆 Top site: {results['top_sites'][0]['Property_Name'] if results['top_sites'] else 'N/A'}")
    elif results and results['success_rate'] >= 80:
        print(f"\n✅ Good results! {results['success_rate']:.1f}% success rate")
    else:
        print(f"\n⚠️ Some issues detected")

if __name__ == "__main__":
    main()