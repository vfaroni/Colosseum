#!/usr/bin/env python3
"""
D'Marco Sites HUD AMI Integration
Connects 2025 HUD AMI data for proper rent calculations
"""

import json
import pandas as pd
import time
import math
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class DMarcoHUDAMIIntegrator:
    def __init__(self, base_dir: str = None):
        """Initialize the HUD AMI integrator"""
        if base_dir is None:
            base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites"
        
        self.base_dir = Path(base_dir)
        
        # Use latest analysis with flood data
        self.analysis_file = self.base_dir / "DMarco_Sites_With_Flood_20250730_144920.json"
        
        # HUD AMI data file (it's right there in the same directory!)
        self.ami_file = self.base_dir / "HUD2025_AMI_Rent_Data_Static.xlsx"
        
        self.ami_data = None
        
    def load_hud_ami_data(self) -> pd.DataFrame:
        """Load the HUD 2025 AMI static data"""
        print(f"📊 Loading HUD 2025 AMI data from: {self.ami_file}")
        
        try:
            # Load the Excel file
            ami_df = pd.read_excel(self.ami_file)
            print(f"✅ Loaded {len(ami_df)} AMI areas")
            
            # Display columns to understand structure
            print(f"📋 Columns: {list(ami_df.columns)}")
            
            return ami_df
            
        except Exception as e:
            print(f"❌ Error loading AMI data: {e}")
            return None
    
    def find_ami_area(self, county: str, state: str = "TX") -> Optional[Dict]:
        """Find matching AMI area for county"""
        if self.ami_data is None:
            return None
        
        # Clean county name for matching
        clean_county = county.replace(" County", "").strip()
        
        # Search for matching area
        possible_matches = []
        
        for idx, row in self.ami_data.iterrows():
            area_name = str(row.get('Area Name', ''))
            
            # Check for county name in area name
            if clean_county.lower() in area_name.lower() and state.upper() in area_name.upper():
                possible_matches.append({
                    'area_name': area_name,
                    'metro_code': row.get('Metro Code', ''),
                    'area_code': row.get('Area Code', ''),
                    'row_data': row.to_dict()
                })
        
        # Return best match (first one for now)
        if possible_matches:
            return possible_matches[0]
        
        return None
    
    def calculate_lihtc_rents(self, ami_data: Dict, income_limits: Dict) -> Dict:
        """Calculate LIHTC rents using CLAUDE.md methodology"""
        try:
            # LIHTC rent = (Income Limit * 0.30) / 12, rounded DOWN using math.floor()
            
            # Household sizes for unit types (CLAUDE.md specification)
            household_sizes = {
                'Studio': 1.0,
                '1BR': 1.5,  # Interpolate between 1 & 2 person
                '2BR': 3.0,  # Use 3-person directly
                '3BR': 4.5,  # Interpolate between 4 & 5 person  
                '4BR': 6.0   # Use 6-person directly
            }
            
            # Calculate rents for each unit type and income level
            rent_calculations = {}
            
            for income_level in ['50%', '60%']:
                level_key = f"{income_level}_AMI"
                rent_calculations[level_key] = {}
                
                for unit_type, household_size in household_sizes.items():
                    # Get income limits for household size
                    if household_size == 1.0:
                        annual_income = income_limits.get('1_person', 0)
                    elif household_size == 1.5:
                        # Interpolate between 1 and 2 person
                        income_1p = income_limits.get('1_person', 0)
                        income_2p = income_limits.get('2_person', 0)
                        annual_income = income_1p + 0.5 * (income_2p - income_1p)
                    elif household_size == 3.0:
                        annual_income = income_limits.get('3_person', 0)
                    elif household_size == 4.5:
                        # Interpolate between 4 and 5 person
                        income_4p = income_limits.get('4_person', 0)
                        income_5p = income_limits.get('5_person', 0)
                        annual_income = income_4p + 0.5 * (income_5p - income_4p)
                    elif household_size == 6.0:
                        annual_income = income_limits.get('6_person', 0)
                    else:
                        continue
                    
                    # Calculate monthly rent (rounded DOWN per CLAUDE.md)
                    if annual_income > 0:
                        monthly_rent = math.floor((annual_income * 0.30) / 12)
                        rent_calculations[level_key][unit_type] = {
                            'household_size': household_size,
                            'annual_income_limit': annual_income,
                            'monthly_rent_limit': monthly_rent
                        }
            
            return rent_calculations
            
        except Exception as e:
            print(f"⚠️ Error calculating rents: {e}")
            return {}
    
    def integrate_ami_data(self) -> List[Dict]:
        """Integrate HUD AMI data with D'Marco sites"""
        print("💰 Starting HUD AMI data integration...")
        
        # Load HUD AMI data
        self.ami_data = self.load_hud_ami_data()
        
        if self.ami_data is None:
            print("❌ Could not load AMI data")
            return []
        
        # Load analysis with flood data
        with open(self.analysis_file, 'r') as f:
            sites_data = json.load(f)
        
        print(f"✅ Loaded {len(sites_data)} sites with flood data")
        
        updated_sites = []
        
        for i, site in enumerate(sites_data, 1):
            print(f"\n💰 Processing site {i}/{len(sites_data)}: {site.get('site_name', 'Unknown')}")
            
            county = site.get('census_county', '')
            
            if not county:
                print(f"❌ No county data for site {i}")
                
                updated_site = site.copy()
                updated_site.update({
                    'ami_analysis_status': 'NO_COUNTY_DATA',
                    'ami_area_name': None,
                    'ami_method': 'NO_COUNTY_AVAILABLE'
                })
                
                updated_sites.append(updated_site)
                continue
            
            print(f"🏛️ County: {county}")
            
            # Find AMI area
            ami_match = self.find_ami_area(county)
            
            if not ami_match:
                print(f"❌ No AMI area found for {county}")
                
                updated_site = site.copy()
                updated_site.update({
                    'ami_analysis_status': 'NO_AMI_MATCH',
                    'ami_area_name': county,
                    'ami_method': 'COUNTY_NOT_FOUND_IN_HUD_DATA'
                })
                
                updated_sites.append(updated_site)
                continue
            
            print(f"✅ Found AMI area: {ami_match['area_name']}")
            
            # Extract income limits from row data
            row_data = ami_match['row_data']
            
            # Build income limits dictionary (assuming standard HUD column names)
            income_limits_50 = {}
            income_limits_60 = {}
            
            # Try to find income limit columns (common patterns)
            for col_name, value in row_data.items():
                if pd.notna(value) and isinstance(value, (int, float)):
                    # 50% AMI columns
                    if '50%' in str(col_name) or '50 percent' in str(col_name).lower():
                        if '1 person' in str(col_name).lower() or '1person' in str(col_name).lower():
                            income_limits_50['1_person'] = value
                        elif '2 person' in str(col_name).lower() or '2person' in str(col_name).lower():
                            income_limits_50['2_person'] = value
                        elif '3 person' in str(col_name).lower() or '3person' in str(col_name).lower():
                            income_limits_50['3_person'] = value
                        elif '4 person' in str(col_name).lower() or '4person' in str(col_name).lower():
                            income_limits_50['4_person'] = value
                        elif '5 person' in str(col_name).lower() or '5person' in str(col_name).lower():
                            income_limits_50['5_person'] = value  
                        elif '6 person' in str(col_name).lower() or '6person' in str(col_name).lower():
                            income_limits_50['6_person'] = value
                    
                    # 60% AMI columns  
                    if '60%' in str(col_name) or '60 percent' in str(col_name).lower():
                        if '1 person' in str(col_name).lower() or '1person' in str(col_name).lower():
                            income_limits_60['1_person'] = value
                        elif '2 person' in str(col_name).lower() or '2person' in str(col_name).lower():
                            income_limits_60['2_person'] = value
                        elif '3 person' in str(col_name).lower() or '3person' in str(col_name).lower():
                            income_limits_60['3_person'] = value
                        elif '4 person' in str(col_name).lower() or '4person' in str(col_name).lower():
                            income_limits_60['4_person'] = value
                        elif '5 person' in str(col_name).lower() or '5person' in str(col_name).lower():
                            income_limits_60['5_person'] = value
                        elif '6 person' in str(col_name).lower() or '6person' in str(col_name).lower():
                            income_limits_60['6_person'] = value
            
            # Calculate rent limits
            rent_calculations_50 = self.calculate_lihtc_rents(ami_match, income_limits_50)
            rent_calculations_60 = self.calculate_lihtc_rents(ami_match, income_limits_60)
            
            # Update site with AMI data
            updated_site = site.copy()
            updated_site.update({
                'ami_analysis_status': 'SUCCESS',
                'ami_area_name': ami_match['area_name'],
                'ami_metro_code': ami_match['metro_code'],
                'ami_area_code': ami_match['area_code'],
                'income_limits_50_ami': income_limits_50,
                'income_limits_60_ami': income_limits_60,
                'lihtc_rent_limits_50_ami': rent_calculations_50,
                'lihtc_rent_limits_60_ami': rent_calculations_60,
                'ami_4_person_100_pct': income_limits_50.get('4_person', 0) * 2 if income_limits_50.get('4_person') else None,  # 50% * 2 = 100%
                'ami_method': 'HUD_2025_STATIC_DATA'
            })
            
            print(f"💰 4-Person 100% AMI: ${updated_site.get('ami_4_person_100_pct', 0):,}")
            
            updated_sites.append(updated_site)
        
        return updated_sites
    
    def generate_ami_summary(self, updated_sites: List[Dict]) -> Dict:
        """Generate AMI integration summary"""
        total_sites = len(updated_sites)
        successful_sites = sum(1 for site in updated_sites if site.get('ami_analysis_status') == 'SUCCESS')
        
        # Calculate AMI statistics
        ami_4p_values = []
        for site in updated_sites:
            ami_4p = site.get('ami_4_person_100_pct')
            if ami_4p and ami_4p > 0:
                ami_4p_values.append(ami_4p)
        
        if ami_4p_values:
            avg_ami_4p = sum(ami_4p_values) / len(ami_4p_values)
            min_ami_4p = min(ami_4p_values)
            max_ami_4p = max(ami_4p_values)
        else:
            avg_ami_4p = min_ami_4p = max_ami_4p = 0
        
        # AMI area distribution
        ami_areas = {}
        for site in updated_sites:
            area = site.get('ami_area_name')
            if area:
                ami_areas[area] = ami_areas.get(area, 0) + 1
        
        summary = {
            'analysis_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_sites_analyzed': total_sites,
            'successful_ami_integration': successful_sites,
            'success_rate': round((successful_sites / total_sites) * 100, 1) if total_sites > 0 else 0,
            'ami_statistics_4_person_100_pct': {
                'average': round(avg_ami_4p, 0),
                'minimum': round(min_ami_4p, 0),
                'maximum': round(max_ami_4p, 0),
                'count': len(ami_4p_values)
            },
            'ami_area_distribution': ami_areas,
            'data_source': 'HUD_2025_AMI_Rent_Data_Static.xlsx'
        }
        
        return summary
    
    def save_results(self, updated_sites: List[Dict], summary: Dict):
        """Save AMI integration results"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Save updated sites with AMI data
        sites_file = self.base_dir / f"DMarco_Sites_Complete_Analysis_{timestamp}.json"
        with open(sites_file, 'w') as f:
            json.dump(updated_sites, f, indent=2)
        print(f"💾 Saved complete analysis to: {sites_file}")
        
        # Save AMI summary
        summary_file = self.base_dir / f"AMI_Analysis_Summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"💾 Saved AMI summary to: {summary_file}")
        
        return sites_file, summary_file
    
    def run_complete_analysis(self):
        """Run complete AMI integration analysis"""
        print("💰 Starting D'Marco HUD AMI Integration")
        print("=" * 60)
        
        try:
            # Integrate AMI data
            updated_sites = self.integrate_ami_data()
            
            if not updated_sites:
                print("❌ No sites processed. Exiting.")
                return
            
            # Generate summary
            summary = self.generate_ami_summary(updated_sites)
            
            # Save results
            sites_file, summary_file = self.save_results(updated_sites, summary)
            
            # Print final summary
            print("\n" + "=" * 60)
            print("💰 AMI INTEGRATION COMPLETE")
            print("=" * 60)
            print(f"✅ Sites analyzed: {summary['total_sites_analyzed']}")
            print(f"✅ Successful AMI integration: {summary['successful_ami_integration']}")
            print(f"✅ Success rate: {summary['success_rate']}%")
            print(f"✅ Average 4-person 100% AMI: ${summary['ami_statistics_4_person_100_pct']['average']:,}")
            print(f"✅ Results saved to: {sites_file.name}")
            
            return {
                'success': True,
                'sites_file': str(sites_file),
                'summary_file': str(summary_file),
                'summary': summary
            }
            
        except Exception as e:
            print(f"💥 Error in AMI analysis: {e}")
            return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    integrator = DMarcoHUDAMIIntegrator()
    results = integrator.run_complete_analysis()
    
    if results['success']:
        print(f"\n💰 AMI integration complete! Check {results['sites_file']} for updated data.")
    else:
        print(f"\n❌ AMI integration failed: {results['error']}")