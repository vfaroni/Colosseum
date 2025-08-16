#!/usr/bin/env python3
"""
Run Production Batch - 50 Sites with Sensible Defaults
Uses production-ready settings for LIHTC development analysis
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

class ProductionRunner:
    """Production runner with optimal LIHTC settings"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        self.production_path = self.base_path / "Production 1"
        self.source_file = "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415_BACKUP_20250801_093840.xlsx"
        
        self.production_path.mkdir(exist_ok=True)
    
    def get_production_defaults(self):
        """Get optimal production defaults for LIHTC development"""
        
        settings = {
            'housing_type': 'Large Family',  # Most common and flexible
            'credit_pricing': 0.80,         # 80 cents - market standard
            'credit_type': '4%',            # 4% credits - more predictable
            'loan_term': 36,                # 36 months construction
            'cap_rate': 0.05,              # 5% cap rate
            'interest_rate': 0.06,         # 6% interest rate
            'elevator': 'Non-Elevator',    # Cost-effective default
            'purchase_price': 2500000,     # $2.5M default for CA market
            'units': 80,                   # 80 units - efficient scale
            'unit_size': 950,              # 950 SF - competitive size
            'hard_cost': 275               # $275/SF - current CA market
        }
        
        print("🏭 PRODUCTION SETTINGS FOR ALL 50 SITES:")
        print(f"   Housing Type: {settings['housing_type']}")
        print(f"   Credit Pricing: {settings['credit_pricing']} (80 cents)")
        print(f"   Credit Type: {settings['credit_type']}")
        print(f"   Construction Loan: {settings['loan_term']} months")
        print(f"   Cap Rate: {settings['cap_rate']*100}%")
        print(f"   Interest Rate: {settings['interest_rate']*100}%")
        print(f"   Elevator: {settings['elevator']}")
        print(f"   Default Units: {settings['units']}")
        print(f"   Unit Size: {settings['unit_size']} SF")
        print(f"   Hard Cost: ${settings['hard_cost']}/SF")
        print(f"   Default Purchase Price: ${settings['purchase_price']:,}")
        print()
        
        return settings
    
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
        """Calculate comprehensive development opportunity score"""
        score = 0
        factors = []
        
        # Price factor (35 points max) - Most important for ROI
        price = self.clean_data_value(site.get('For Sale Price', 0))
        if price and price > 0:
            if price < 1500000:
                score += 35
                factors.append(f"Excellent Price (${price/1000000:.1f}M)")
            elif price < 3000000:
                score += 25
                factors.append(f"Good Price (${price/1000000:.1f}M)")
            elif price < 5000000:
                score += 15
                factors.append(f"Fair Price (${price/1000000:.1f}M)")
            elif price < 10000000:
                score += 8
                factors.append(f"High Price (${price/1000000:.1f}M)")
            else:
                score += 3
                factors.append(f"Very High Price (${price/1000000:.1f}M)")
        else:
            score += 20
            factors.append("Price TBD")
        
        # County/Market factor (25 points max)
        county = str(self.clean_data_value(site.get('County Name', ''))).strip()
        if county:
            if county == 'Los Angeles':
                score += 25
                factors.append("LA County - Prime Market")
            elif county in ['Orange', 'San Diego']:
                score += 22
                factors.append(f"{county} County - Premium Market")
            elif county in ['Riverside', 'San Bernardino']:
                score += 18
                factors.append(f"{county} County - Growth Market")
            elif county in ['Fresno', 'Kern', 'Tulare']:
                score += 15
                factors.append(f"{county} County - Value Market")
            else:
                score += 12
                factors.append(f"{county} County")
        
        # Location within county (15 points max)
        market = str(self.clean_data_value(site.get('Market Name', ''))).strip()
        submarket = str(self.clean_data_value(site.get('Submarket Name', ''))).strip()
        
        location_keywords = ['metro', 'central', 'downtown', 'transit', 'corridor', 'station']
        if any(word in market.lower() for word in location_keywords) or any(word in submarket.lower() for word in location_keywords):
            score += 15
            factors.append("Transit-Oriented Location")
        elif 'freeway' in market.lower() or 'highway' in market.lower():
            score += 12
            factors.append("Highway Access")
        else:
            score += 8
            factors.append("Standard Location")
        
        # Development readiness (15 points max)
        prop_name = str(self.clean_data_value(site.get('Property Name', ''))).lower()
        if 'entitled' in prop_name or 'approved' in prop_name:
            score += 15
            factors.append("Pre-Entitled Site")
        elif 'development' in prop_name and 'opportunity' in prop_name:
            score += 12
            factors.append("Development Opportunity")
        elif any(word in prop_name for word in ['land', 'site', 'lot']):
            score += 10
            factors.append("Developable Land")
        else:
            score += 8
            factors.append("Property for Development")
        
        # Size factor (10 points max)
        try:
            # Extract acreage from property name
            acres_match = re.search(r'(\d+\.?\d*)\s*(?:acre|ac\b)', prop_name)
            if acres_match:
                acres = float(acres_match.group(1))
                if 2 <= acres <= 4:
                    score += 10
                    factors.append(f"Optimal Size ({acres} acres)")
                elif 1 <= acres <= 6:
                    score += 8
                    factors.append(f"Good Size ({acres} acres)")
                elif acres <= 10:
                    score += 6
                    factors.append(f"Large Size ({acres} acres)")
                else:
                    score += 4
                    factors.append(f"Very Large ({acres} acres)")
            else:
                score += 6
                factors.append("Size TBD")
        except:
            score += 6
            factors.append("Size TBD")
        
        return min(score, 100), factors
    
    def create_ranking_spreadsheet(self, sites_data, settings):
        """Create comprehensive ranking spreadsheet"""
        
        ranked_sites = []
        
        for i, site in enumerate(sites_data):
            score, factors = self.calculate_development_score(site)
            
            site_price = self.clean_data_value(site.get('For Sale Price', 0))
            purchase_price = float(site_price) if site_price and site_price != 0 else settings['purchase_price']
            
            # Calculate price per unit estimate
            price_per_unit = purchase_price / settings['units'] if settings['units'] > 0 else 0
            
            ranked_sites.append({
                'Rank': 0,
                'Property_Name': self.clean_data_value(site.get('Property Name', '')),
                'Property_Address': self.clean_data_value(site.get('Property Address', '')),
                'County': self.clean_data_value(site.get('County Name', '')),
                'Market': self.clean_data_value(site.get('Market Name', '')),
                'Submarket': self.clean_data_value(site.get('Submarket Name', '')),
                'Purchase_Price': purchase_price,
                'Price_Per_Unit': price_per_unit,
                'Development_Score': score,
                'Score_Factors': '; '.join(factors),
                'Broker_Company': self.clean_data_value(site.get('Sale Company Name', '')),
                'Broker_Contact': self.clean_data_value(site.get('Sale Company Contact', '')),
                'Broker_Phone': self.clean_data_value(site.get('Sale Company Phone', '')),
                'Company_Address': self.clean_data_value(site.get('Sale Company Address', '')),
                'Housing_Type': settings['housing_type'],
                'Credit_Type': settings['credit_type'],
                'Units': settings['units'],
                'Unit_Size_SF': settings['unit_size'],
                'Hard_Cost_SF': settings['hard_cost'],
                'Estimated_Total_Cost': settings['units'] * settings['unit_size'] * settings['hard_cost'] + purchase_price
            })
        
        # Sort by development score
        ranked_sites.sort(key=lambda x: x['Development_Score'], reverse=True)
        
        # Assign ranks
        for i, site in enumerate(ranked_sites, 1):
            site['Rank'] = i
        
        # Create Excel file
        df = pd.DataFrame(ranked_sites)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = self.production_path / f"Production_1_Site_Rankings_Broker_Contacts_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Site Rankings', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Site Rankings']
            
            # Formats
            header_format = workbook.add_format({
                'bold': True, 'text_wrap': True, 'valign': 'top',
                'fg_color': '#4472C4', 'font_color': 'white', 'border': 1
            })
            
            price_format = workbook.add_format({'num_format': '$#,##0'})
            score_format = workbook.add_format({'num_format': '0', 'fg_color': '#D5E8D4', 'bold': True})
            cost_format = workbook.add_format({'num_format': '$#,##0', 'fg_color': '#FFF2CC'})
            
            # Apply formatting
            for col_num, column in enumerate(df.columns):
                worksheet.write(0, col_num, column, header_format)
            
            # Column widths and formatting
            worksheet.set_column('A:A', 6)   # Rank
            worksheet.set_column('B:B', 35)  # Property Name
            worksheet.set_column('C:C', 40)  # Address
            worksheet.set_column('D:D', 12)  # County
            worksheet.set_column('E:E', 18)  # Market
            worksheet.set_column('F:F', 18)  # Submarket
            worksheet.set_column('G:G', 15, price_format)     # Purchase Price
            worksheet.set_column('H:H', 12, price_format)     # Price Per Unit
            worksheet.set_column('I:I', 10, score_format)     # Score
            worksheet.set_column('J:J', 50)  # Score Factors
            worksheet.set_column('K:K', 25)  # Broker Company
            worksheet.set_column('L:L', 25)  # Broker Contact
            worksheet.set_column('M:M', 15)  # Broker Phone
            worksheet.set_column('N:N', 35)  # Company Address
            worksheet.set_column('O:Q', 12)  # Housing, Credit, Units
            worksheet.set_column('R:S', 10)  # Unit Size, Hard Cost
            worksheet.set_column('T:T', 18, cost_format)      # Total Cost
        
        return excel_path, ranked_sites
    
    def run_production(self):
        """Run full production batch"""
        
        print("\n" + "="*70)
        print("🏭 PRODUCTION BATCH: 50 SITES WITH RANKING & BROKER CONTACTS")
        print("="*70)
        
        # Get settings
        settings = self.get_production_defaults()
        
        # Load data
        source_path = self.sites_path / self.source_file
        if not source_path.exists():
            logger.error(f"❌ Source file not found: {source_path}")
            return
        
        df = pd.read_excel(source_path)
        
        # Get first 50 valid sites
        valid_sites = []
        for idx in range(len(df)):
            if len(valid_sites) >= 50:
                break
            site = df.iloc[idx]
            site_name = site.get('Property Name', '')
            if not pd.isna(site_name) and str(site_name).lower() != 'nan' and site_name.strip():
                valid_sites.append(site)
        
        logger.info(f"\n🎯 Processing {len(valid_sites)} sites from {len(df)} total available")
        
        # Create ranking spreadsheet
        logger.info(f"📊 Creating development opportunity rankings...")
        ranking_file, ranked_sites = self.create_ranking_spreadsheet(valid_sites, settings)
        logger.info(f"✅ Ranking spreadsheet created: {ranking_file.name}")
        
        # Create BOTN files
        logger.info(f"\n🔧 Creating BOTN files for all sites...")
        
        file_info = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, site in enumerate(valid_sites):
            site_name = str(site.get('Property Name', f'Site_{i}'))
            clean_name = re.sub(r'[<>:"/\\|?*]', '_', site_name)[:40]
            
            output_filename = f"PROD1_BOTN_{clean_name}_{timestamp}_{i:03d}.xlsx"
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
        logger.info(f"🔧 Processing files with Excel (this may take several minutes)...")
        
        successful = []
        failed = []
        
        try:
            app = xw.App(visible=False, add_book=False)  # Try invisible for batch
            app.display_alerts = False
            app.screen_updating = False
            
            logger.info("✅ Excel session started")
            
            for i, info in enumerate(file_info, 1):
                try:
                    if i % 10 == 1:  # Log every 10th file
                        logger.info(f"📝 Processing files {i}-{min(i+9, len(file_info))} of {len(file_info)}...")
                    
                    wb = app.books.open(str(info['path']), update_links=False)
                    inputs_sheet = wb.sheets['Inputs']
                    
                    site = info['site']
                    
                    # Calculate purchase price
                    site_price = self.clean_data_value(site.get('For Sale Price', 0))
                    purchase_price = float(site_price) if site_price and site_price != 0 else settings['purchase_price']
                    
                    # Populate all inputs efficiently
                    inputs_sheet.range('A2').value = self.clean_data_value(site.get('Property Name', ''))
                    inputs_sheet.range('B2').value = self.clean_data_value(site.get('Property Address', ''))
                    inputs_sheet.range('C2').value = self.format_county_name(site.get('County Name', ''))
                    inputs_sheet.range('D2').value = self.get_cdlac_region(site.get('County Name', ''))
                    inputs_sheet.range('E2').value = self.clean_data_value(site.get('State', 'CA'))
                    inputs_sheet.range('F2').value = self.clean_data_value(site.get('Zip', ''))
                    inputs_sheet.range('G2').value = purchase_price
                    inputs_sheet.range('H2').value = settings['housing_type']
                    inputs_sheet.range('I2').value = settings['credit_pricing']
                    inputs_sheet.range('J2').value = settings['credit_type']
                    inputs_sheet.range('K2').value = settings['loan_term']
                    inputs_sheet.range('L2').value = settings['cap_rate']
                    inputs_sheet.range('M2').value = settings['interest_rate']
                    inputs_sheet.range('N2').value = settings['elevator']
                    inputs_sheet.range('O2').value = settings['units']
                    inputs_sheet.range('P2').value = settings['unit_size']
                    inputs_sheet.range('Q2').value = settings['hard_cost']
                    
                    wb.save()
                    wb.close()
                    
                    successful.append(info)
                    
                except Exception as e:
                    logger.error(f"❌ Failed file {i}: {str(e)}")
                    failed.append({'info': info, 'error': str(e)})
                    try:
                        if 'wb' in locals():
                            wb.close()
                    except:
                        pass
            
            app.quit()
            logger.info("🔧 Excel session closed")
            
        except Exception as e:
            logger.error(f"❌ Excel session error: {str(e)}")
        
        # Results
        success_rate = len(successful) / len(file_info) * 100 if file_info else 0
        
        logger.info(f"\n🏆 PRODUCTION BATCH COMPLETE!")
        logger.info("="*70)
        logger.info(f"✅ Successful BOTN files: {len(successful)}")
        logger.info(f"❌ Failed BOTN files: {len(failed)}")
        logger.info(f"📈 Success rate: {success_rate:.1f}%")
        logger.info(f"📊 Ranking file: {ranking_file.name}")
        logger.info(f"📁 All files in: {self.production_path}")
        
        # Show top 10
        if ranked_sites:
            logger.info(f"\n🏆 TOP 10 DEVELOPMENT OPPORTUNITIES:")
            for site in ranked_sites[:10]:
                price = f"${site['Purchase_Price']:,.0f}" if site['Purchase_Price'] > 0 else "TBD"
                logger.info(f"   {site['Rank']:2d}. {site['Property_Name'][:40]} (Score: {site['Development_Score']}) - {price}")
                logger.info(f"       📞 {site['Broker_Company']} - {site['Broker_Contact']}")
        
        return {
            'success_rate': success_rate,
            'ranking_file': ranking_file,
            'top_sites': ranked_sites[:10],
            'total_processed': len(successful)
        }

def main():
    runner = ProductionRunner()
    results = runner.run_production()
    
    if results and results['success_rate'] >= 90:
        print(f"\n🎉 PRODUCTION SUCCESS! {results['total_processed']} sites processed")
        print(f"📊 Check your ranking spreadsheet for complete broker contact information")
        print(f"🏆 Ready to reach out to brokers for top development opportunities!")
    elif results and results['success_rate'] >= 80:
        print(f"\n✅ Good results! {results['success_rate']:.1f}% success rate")
    else:
        print(f"\n⚠️ Some processing issues detected")

if __name__ == "__main__":
    main()