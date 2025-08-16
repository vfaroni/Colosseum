#!/usr/bin/env python3
"""
Production Batch 2 - Sites 51-100 with City Names and Acreage
Enhanced version with city extraction and acreage parsing
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

class ProductionBatch2:
    """Production batch 2 with enhanced city and acreage features"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "botntemplate" / "CABOTNTemplate.xlsx"
        self.sites_path = self.base_path / "Sites"
        self.production_path = self.base_path / "Production 2"
        self.source_file = "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415_BACKUP_20250801_093840.xlsx"
        
        self.production_path.mkdir(exist_ok=True)
    
    def extract_city_name(self, site):
        """Extract city name from available site data"""
        # Try multiple fields for city information
        
        # First try direct city field if available
        for field in ['City', 'Property City', 'City Name']:
            if field in site and not pd.isna(site[field]):
                city = str(site[field]).strip()
                if city and city.lower() != 'nan':
                    return city
        
        # Extract from address
        address = str(self.clean_data_value(site.get('Property Address', '')))
        if address:
            # Look for common CA city patterns in address
            city_match = re.search(r',\s*([A-Za-z\s]+),?\s*CA', address)
            if city_match:
                return city_match.group(1).strip()
        
        # Extract from market name
        market = str(self.clean_data_value(site.get('Market Name', '')))
        if market and market != 'nan':
            # Clean market name to get city
            market_clean = market.replace(', CA', '').strip()
            if market_clean:
                return market_clean
        
        # Extract from submarket
        submarket = str(self.clean_data_value(site.get('Submarket Name', '')))
        if submarket and submarket != 'nan':
            return submarket.strip()
        
        # Default based on county
        county = str(self.clean_data_value(site.get('County Name', '')))
        county_cities = {
            'Los Angeles': 'Los Angeles',
            'Orange': 'Anaheim',
            'San Diego': 'San Diego',
            'Riverside': 'Riverside',
            'San Bernardino': 'San Bernardino',
            'Fresno': 'Fresno',
            'Kern': 'Bakersfield'
        }
        return county_cities.get(county, 'TBD')
    
    def extract_acreage(self, site):
        """Extract acreage from property name and other fields"""
        
        # Check property name first
        prop_name = str(self.clean_data_value(site.get('Property Name', ''))).lower()
        
        # Pattern 1: "X.X acres" or "X.X ac"
        acres_match = re.search(r'(\d+\.?\d*)\s*(?:acres?|ac\b)', prop_name)
        if acres_match:
            return float(acres_match.group(1))
        
        # Pattern 2: "X+/- acres" 
        acres_plus_minus = re.search(r'(\d+\.?\d*)\s*[+\-\/±]\s*acres?', prop_name)
        if acres_plus_minus:
            return float(acres_plus_minus.group(1))
        
        # Pattern 3: Size in description or other fields
        for field in ['Property Description', 'Property Details']:
            if field in site and not pd.isna(site[field]):
                desc = str(site[field]).lower()
                desc_match = re.search(r'(\d+\.?\d*)\s*(?:acres?|ac\b)', desc)
                if desc_match:
                    return float(desc_match.group(1))
        
        # Pattern 4: Extract from property size field if available
        if 'Size' in site or 'Property Size' in site:
            size_field = site.get('Size', site.get('Property Size', ''))
            if not pd.isna(size_field):
                size_str = str(size_field).lower()
                size_match = re.search(r'(\d+\.?\d*)', size_str)
                if size_match and ('ac' in size_str or 'acre' in size_str):
                    return float(size_match.group(1))
        
        return None  # No acreage found
    
    def get_production_settings(self):
        """Get enhanced production settings"""
        
        settings = {
            'housing_type': 'Large Family',
            'credit_pricing': 0.80,
            'credit_type': '4%',
            'loan_term': 36,
            'cap_rate': 0.05,
            'interest_rate': 0.06,
            'elevator': 'Non-Elevator',
            'purchase_price': 2500000,
            'units': 80,
            'unit_size': 950,
            'hard_cost': 275
        }
        
        print("🏭 PRODUCTION BATCH 2 SETTINGS (Sites 51-100):")
        print("   Enhanced with City Names and Acreage Information")
        print(f"   Housing Type: {settings['housing_type']}")
        print(f"   Credit Pricing: {settings['credit_pricing']} (80 cents)")
        print(f"   Credit Type: {settings['credit_type']}")
        print(f"   Units: {settings['units']} per property")
        print(f"   Hard Cost: ${settings['hard_cost']}/SF")
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
    
    def calculate_enhanced_score(self, site):
        """Calculate enhanced development score with acreage factor"""
        score = 0
        factors = []
        
        # Price factor (35 points max)
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
            else:
                score += 8
                factors.append(f"High Price (${price/1000000:.1f}M)")
        else:
            score += 20
            factors.append("Price TBD")
        
        # County factor (25 points max)
        county = str(self.clean_data_value(site.get('County Name', ''))).strip()
        if county == 'Los Angeles':
            score += 25
            factors.append("LA County - Prime")
        elif county in ['Orange', 'San Diego']:
            score += 22
            factors.append(f"{county} County - Premium")
        elif county in ['Riverside', 'San Bernardino']:
            score += 18
            factors.append(f"{county} County - Growth")
        else:
            score += 15
            factors.append(f"{county} County")
        
        # Acreage factor (20 points max) - Enhanced scoring
        acreage = self.extract_acreage(site)
        if acreage:
            if 2.0 <= acreage <= 4.0:
                score += 20
                factors.append(f"Optimal Size ({acreage} ac)")
            elif 1.5 <= acreage <= 6.0:
                score += 17
                factors.append(f"Good Size ({acreage} ac)")
            elif 1.0 <= acreage <= 8.0:
                score += 14
                factors.append(f"Workable Size ({acreage} ac)")
            elif acreage < 1.0:
                score += 8
                factors.append(f"Small Site ({acreage} ac)")
            else:
                score += 10
                factors.append(f"Large Site ({acreage} ac)")
        else:
            score += 10
            factors.append("Size TBD")
        
        # Development readiness (15 points max)
        prop_name = str(self.clean_data_value(site.get('Property Name', ''))).lower()
        if 'entitled' in prop_name or 'approved' in prop_name:
            score += 15
            factors.append("Pre-Entitled")
        elif 'development' in prop_name and 'opportunity' in prop_name:
            score += 12
            factors.append("Development Ready")
        else:
            score += 8
            factors.append("Standard Site")
        
        # Location quality (5 points max)
        city = self.extract_city_name(site)
        prime_cities = ['los angeles', 'san diego', 'anaheim', 'irvine', 'santa monica', 'pasadena']
        if city.lower() in prime_cities:
            score += 5
            factors.append(f"Prime City ({city})")
        else:
            score += 3
            factors.append(f"City: {city}")
        
        return min(score, 100), factors, acreage, city
    
    def create_enhanced_ranking_spreadsheet(self, sites_data, settings):
        """Create enhanced ranking spreadsheet with city and acreage"""
        
        ranked_sites = []
        
        for i, site in enumerate(sites_data):
            score, factors, acreage, city = self.calculate_enhanced_score(site)
            
            site_price = self.clean_data_value(site.get('For Sale Price', 0))
            purchase_price = float(site_price) if site_price and site_price != 0 else settings['purchase_price']
            
            # Calculate price per acre if acreage available
            price_per_acre = purchase_price / acreage if acreage and acreage > 0 else 0
            
            ranked_sites.append({
                'Rank': 0,
                'Property_Name': self.clean_data_value(site.get('Property Name', '')),
                'City': city,
                'Property_Address': self.clean_data_value(site.get('Property Address', '')),
                'County': self.clean_data_value(site.get('County Name', '')),
                'Market': self.clean_data_value(site.get('Market Name', '')),
                'Acres': acreage if acreage else 'TBD',
                'Purchase_Price': purchase_price,
                'Price_Per_Acre': price_per_acre if price_per_acre > 0 else 'N/A',
                'Development_Score': score,
                'Score_Factors': '; '.join(factors),
                'Broker_Company': self.clean_data_value(site.get('Sale Company Name', '')),
                'Broker_Contact': self.clean_data_value(site.get('Sale Company Contact', '')),
                'Broker_Phone': self.clean_data_value(site.get('Sale Company Phone', '')),
                'Company_Address': self.clean_data_value(site.get('Sale Company Address', '')),
                'Housing_Type': settings['housing_type'],
                'Credit_Type': settings['credit_type'],
                'Units': settings['units'],
                'Hard_Cost_SF': settings['hard_cost']
            })
        
        # Sort by development score
        ranked_sites.sort(key=lambda x: x['Development_Score'], reverse=True)
        
        # Assign ranks
        for i, site in enumerate(ranked_sites, 1):
            site['Rank'] = i
        
        # Create Excel file
        df = pd.DataFrame(ranked_sites)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = self.production_path / f"Production_2_Sites_51-100_Rankings_with_Cities_Acres_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sites 51-100 Rankings', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Sites 51-100 Rankings']
            
            # Enhanced formatting
            header_format = workbook.add_format({
                'bold': True, 'text_wrap': True, 'valign': 'top',
                'fg_color': '#2E8B57', 'font_color': 'white', 'border': 1
            })
            
            price_format = workbook.add_format({'num_format': '$#,##0'})
            score_format = workbook.add_format({'num_format': '0', 'fg_color': '#90EE90', 'bold': True})
            acres_format = workbook.add_format({'num_format': '0.0', 'fg_color': '#F0E68C'})
            
            # Apply formatting
            for col_num, column in enumerate(df.columns):
                worksheet.write(0, col_num, column, header_format)
            
            # Column setup
            worksheet.set_column('A:A', 6)   # Rank
            worksheet.set_column('B:B', 35)  # Property Name
            worksheet.set_column('C:C', 15)  # City
            worksheet.set_column('D:D', 40)  # Address
            worksheet.set_column('E:E', 12)  # County
            worksheet.set_column('F:F', 18)  # Market
            worksheet.set_column('G:G', 8, acres_format)      # Acres
            worksheet.set_column('H:H', 15, price_format)     # Purchase Price
            worksheet.set_column('I:I', 12, price_format)     # Price Per Acre
            worksheet.set_column('J:J', 10, score_format)     # Score 
            worksheet.set_column('K:K', 50)  # Score Factors
            worksheet.set_column('L:L', 25)  # Broker Company
            worksheet.set_column('M:M', 25)  # Broker Contact
            worksheet.set_column('N:N', 15)  # Broker Phone
            worksheet.set_column('O:O', 35)  # Company Address
        
        return excel_path, ranked_sites
    
    def run_batch_2(self):
        """Run production batch 2 for sites 51-100"""
        
        print("\n" + "="*70)
        print("🏭 PRODUCTION BATCH 2: SITES 51-100 WITH CITIES & ACRES")
        print("="*70)
        
        settings = self.get_production_settings()
        
        # Load data
        source_path = self.sites_path / self.source_file
        df = pd.read_excel(source_path)
        
        # Get sites 51-100
        valid_sites = []
        site_count = 0
        for idx in range(len(df)):
            site = df.iloc[idx]
            site_name = site.get('Property Name', '')
            if not pd.isna(site_name) and str(site_name).lower() != 'nan' and site_name.strip():
                site_count += 1
                if 51 <= site_count <= 100:  # Sites 51-100
                    valid_sites.append(site)
        
        logger.info(f"\n🎯 Processing sites 51-100 ({len(valid_sites)} sites)")
        
        # Create ranking spreadsheet
        logger.info(f"📊 Creating enhanced rankings with cities and acreage...")
        ranking_file, ranked_sites = self.create_enhanced_ranking_spreadsheet(valid_sites, settings)
        logger.info(f"✅ Enhanced ranking spreadsheet: {ranking_file.name}")
        
        # Create BOTN files
        logger.info(f"\n🔧 Creating BOTN files with enhanced data...")
        
        file_info = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, site in enumerate(valid_sites):
            site_name = str(site.get('Property Name', f'Site_{i+51}'))
            clean_name = re.sub(r'[<>:"/\\|?*]', '_', site_name)[:40]
            
            output_filename = f"PROD2_BOTN_{clean_name}_{timestamp}_{i+51:03d}.xlsx"
            output_path = self.production_path / output_filename
            
            shutil.copy2(self.template_path, output_path)
            
            file_info.append({
                'site': site,
                'path': output_path,
                'name': clean_name,
                'site_num': i + 51
            })
        
        logger.info(f"✅ Created {len(file_info)} template copies")
        
        # Process with Excel
        successful = []
        failed = []
        
        try:
            app = xw.App(visible=False, add_book=False)
            app.display_alerts = False
            app.screen_updating = False
            
            for i, info in enumerate(file_info, 1):
                try:
                    if i % 10 == 1:
                        logger.info(f"📝 Processing files {i}-{min(i+9, len(file_info))} of {len(file_info)}...")
                    
                    wb = app.books.open(str(info['path']), update_links=False)
                    inputs_sheet = wb.sheets['Inputs']
                    
                    site = info['site']
                    
                    # Enhanced data population
                    site_price = self.clean_data_value(site.get('For Sale Price', 0))
                    purchase_price = float(site_price) if site_price and site_price != 0 else settings['purchase_price']
                    city = self.extract_city_name(site)
                    
                    # Populate enhanced inputs
                    inputs_sheet.range('A2').value = self.clean_data_value(site.get('Property Name', ''))
                    inputs_sheet.range('B2').value = f"{self.clean_data_value(site.get('Property Address', ''))}, {city}"  # Include city
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
                    failed.append({'info': info, 'error': str(e)})
                    try:
                        if 'wb' in locals():
                            wb.close()
                    except:
                        pass
            
            app.quit()
            
        except Exception as e:
            logger.error(f"❌ Excel error: {str(e)}")
        
        # Results
        success_rate = len(successful) / len(file_info) * 100 if file_info else 0
        
        logger.info(f"\n🏆 PRODUCTION BATCH 2 COMPLETE!")
        logger.info("="*70)
        logger.info(f"✅ Successful: {len(successful)}")
        logger.info(f"❌ Failed: {len(failed)}")
        logger.info(f"📈 Success rate: {success_rate:.1f}%")
        logger.info(f"📊 Enhanced ranking file: {ranking_file.name}")
        logger.info(f"📁 All files in: {self.production_path}")
        
        # Show top 10 with enhanced info
        if ranked_sites:
            logger.info(f"\n🏆 TOP 10 SITES 51-100 WITH CITIES & ACRES:")
            for site in ranked_sites[:10]:
                price = f"${site['Purchase_Price']:,.0f}" if site['Purchase_Price'] > 0 else "TBD"
                acres = f"{site['Acres']} ac" if isinstance(site['Acres'], float) else site['Acres']
                logger.info(f"   {site['Rank']:2d}. {site['Property_Name'][:35]} ({site['City']})")
                logger.info(f"       💰 {price} | 🏞️ {acres} | Score: {site['Development_Score']}")
                logger.info(f"       📞 {site['Broker_Company']} - {site['Broker_Contact']}")
        
        return {
            'success_rate': success_rate,
            'ranking_file': ranking_file,
            'top_sites': ranked_sites[:10],
            'total_processed': len(successful)
        }

def main():
    batch2 = ProductionBatch2()
    results = batch2.run_batch_2()
    
    if results and results['success_rate'] >= 90:
        print(f"\n🎉 BATCH 2 SUCCESS! {results['total_processed']} sites processed")
        print(f"🏙️ Enhanced with city names and acreage information")
        print(f"📊 Check Production 2 folder for complete results!")
    else:
        print(f"\n⚠️ Some issues detected")

if __name__ == "__main__":
    main()