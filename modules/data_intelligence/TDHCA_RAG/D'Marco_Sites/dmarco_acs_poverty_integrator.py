#!/usr/bin/env python3
"""
D'Marco Sites ACS Poverty Rate Integrator
Extracts census tracts from D'Marco analysis and adds ACS poverty rates
"""

import json
import pandas as pd
import requests
import time
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class DMarcoACSPovertyIntegrator:
    def __init__(self, base_dir: str = None):
        """Initialize the ACS poverty integrator"""
        if base_dir is None:
            base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites"
        
        self.base_dir = Path(base_dir)
        self.census_api_key = "06ece0121263282cd9ffd753215b007b8f9a3dfc"
        self.acs_cache = {}
        
        # Latest analysis file
        self.analysis_file = self.base_dir / "Production_Analysis_20250730" / "dmarco_production_analysis_20250730_134731.json"
        
    def extract_census_tracts(self) -> List[Dict]:
        """Extract unique census tracts from D'Marco analysis"""
        print(f"📊 Loading D'Marco analysis from: {self.analysis_file}")
        
        with open(self.analysis_file, 'r') as f:
            sites_data = json.load(f)
        
        print(f"✅ Loaded {len(sites_data)} sites")
        
        # Extract unique census tracts with their details
        tract_info = {}
        
        for site in sites_data:
            if 'census_tract' in site and site['census_tract']:
                tract_key = site['census_tract']
                
                if tract_key not in tract_info:
                    tract_info[tract_key] = {
                        'census_tract': site['census_tract'],
                        'census_county': site.get('census_county', ''),
                        'census_state': site.get('census_state', ''),
                        'site_count': 0,
                        'sites': []
                    }
                
                tract_info[tract_key]['site_count'] += 1
                tract_info[tract_key]['sites'].append({
                    'site_index': site.get('site_index'),
                    'site_name': site.get('site_name', ''),
                    'qct_designation': site.get('qct_designation', ''),
                    'basis_boost_eligible': site.get('basis_boost_eligible', '')
                })
        
        unique_tracts = list(tract_info.values())
        print(f"📍 Found {len(unique_tracts)} unique census tracts")
        
        return unique_tracts
    
    def parse_tract_fips(self, tract_string: str, county: str, state: str) -> Optional[str]:
        """Parse census tract string to get FIPS code"""
        try:
            # Extract tract number from "Census Tract XXXX.XX"
            if "Census Tract" in tract_string:
                tract_num = tract_string.replace("Census Tract ", "").strip()
                
                # Convert to 6-digit format (XXXXXX)
                if "." in tract_num:
                    parts = tract_num.split(".")
                    tract_fips = parts[0].zfill(4) + parts[1].ljust(2, '0')
                else:
                    tract_fips = tract_num.zfill(4) + "00"
                
                return tract_fips
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error parsing tract {tract_string}: {e}")
            return None
    
    def get_county_fips(self, county_name: str, state: str = "Texas") -> Optional[str]:
        """Get county FIPS code for Texas counties"""
        # Texas county FIPS codes (partial list for common counties)
        texas_counties = {
            "Harris County": "201",
            "Dallas County": "113", 
            "Tarrant County": "439",
            "Bexar County": "029",
            "Travis County": "453",
            "Collin County": "085",
            "Fort Bend County": "157",
            "Denton County": "121",
            "Montgomery County": "339",
            "Williamson County": "491"
        }
        
        return texas_counties.get(county_name)
    
    def get_acs_poverty_rate(self, county_fips: str, tract_fips: str) -> Optional[float]:
        """Get ACS poverty rate for census tract"""
        try:
            # Texas state FIPS code
            state_fips = "48"
            
            # ACS 5-Year Estimates API endpoint
            url = "https://api.census.gov/data/2022/acs/acs5"
            
            params = {
                'get': 'B17001_002E,B17001_001E',  # Poverty count, total population
                'for': f'tract:{tract_fips}',
                'in': f'state:{state_fips} county:{county_fips}',
                'key': self.census_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if len(data) > 1:  # Header + data row
                    row = data[1]
                    poverty_count = float(row[0]) if row[0] and row[0] != '-999999999' else 0
                    total_pop = float(row[1]) if row[1] and row[1] != '-999999999' else 0
                    
                    if total_pop > 0:
                        poverty_rate = (poverty_count / total_pop) * 100
                        return round(poverty_rate, 2)
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error getting ACS data for tract {tract_fips}: {e}")
            return None
    
    def integrate_poverty_data(self) -> Dict:
        """Integrate ACS poverty data with D'Marco sites"""
        print("🔍 Starting ACS poverty data integration...")
        
        # Extract census tracts
        tract_info = self.extract_census_tracts()
        
        # Get poverty rates for each tract
        poverty_results = {}
        
        for tract in tract_info:
            print(f"\n📊 Processing: {tract['census_tract']} in {tract['census_county']}")
            
            # Parse tract FIPS
            tract_fips = self.parse_tract_fips(
                tract['census_tract'], 
                tract['census_county'], 
                tract['census_state']
            )
            
            if not tract_fips:
                print(f"❌ Could not parse tract FIPS for {tract['census_tract']}")
                continue
            
            # Get county FIPS
            county_fips = self.get_county_fips(tract['census_county'])
            
            if not county_fips:
                print(f"❌ Could not find county FIPS for {tract['census_county']}")
                continue
            
            print(f"🎯 Querying ACS for tract {tract_fips} in county {county_fips}")
            
            # Get poverty rate
            poverty_rate = self.get_acs_poverty_rate(county_fips, tract_fips)
            
            if poverty_rate is not None:
                print(f"✅ Poverty rate: {poverty_rate}%")
                
                poverty_results[tract['census_tract']] = {
                    'tract_name': tract['census_tract'],
                    'county': tract['census_county'],
                    'state': tract['census_state'],
                    'tract_fips': tract_fips,
                    'county_fips': county_fips,
                    'poverty_rate': poverty_rate,
                    'site_count': tract['site_count'],
                    'sites': tract['sites']
                }
            else:
                print(f"❌ Failed to get poverty rate for {tract['census_tract']}")
            
            # Rate limiting
            time.sleep(0.2)
        
        return poverty_results
    
    def update_sites_with_poverty(self, poverty_data: Dict) -> List[Dict]:
        """Update original sites data with poverty rates"""
        print("🔄 Updating sites with poverty data...")
        
        # Load original analysis
        with open(self.analysis_file, 'r') as f:
            sites_data = json.load(f)
        
        updated_sites = []
        
        for site in sites_data:
            updated_site = site.copy()
            
            # Add poverty data if available
            tract_name = site.get('census_tract')
            if tract_name and tract_name in poverty_data:
                poverty_info = poverty_data[tract_name]
                
                updated_site.update({
                    'acs_poverty_rate': poverty_info['poverty_rate'],
                    'tract_fips': poverty_info['tract_fips'],
                    'county_fips': poverty_info['county_fips'],
                    'poverty_data_source': 'ACS_2022_5_YEAR',
                    'poverty_analysis_status': 'SUCCESS'
                })
            else:
                updated_site.update({
                    'acs_poverty_rate': None,
                    'tract_fips': None,
                    'county_fips': None,
                    'poverty_data_source': None,
                    'poverty_analysis_status': 'FAILED'
                })
            
            updated_sites.append(updated_site)
        
        return updated_sites
    
    def generate_poverty_summary(self, poverty_data: Dict) -> Dict:
        """Generate summary of poverty analysis"""
        total_tracts = len(poverty_data)
        total_sites = sum(tract['site_count'] for tract in poverty_data.values())
        
        poverty_rates = [tract['poverty_rate'] for tract in poverty_data.values()]
        
        if poverty_rates:
            avg_poverty = sum(poverty_rates) / len(poverty_rates)
            min_poverty = min(poverty_rates)
            max_poverty = max(poverty_rates)
        else:
            avg_poverty = min_poverty = max_poverty = 0
        
        # QCT analysis
        qct_sites = 0
        for tract_data in poverty_data.values():
            for site in tract_data['sites']:
                if site.get('qct_designation') == 'QCT':
                    qct_sites += 1
        
        summary = {
            'analysis_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_census_tracts': total_tracts,
            'total_sites_analyzed': total_sites,
            'poverty_statistics': {
                'average_poverty_rate': round(avg_poverty, 2),
                'minimum_poverty_rate': round(min_poverty, 2),
                'maximum_poverty_rate': round(max_poverty, 2)
            },
            'qct_correlation': {
                'qct_eligible_sites': qct_sites,
                'total_sites': total_sites,
                'qct_percentage': round((qct_sites / total_sites) * 100, 1) if total_sites > 0 else 0
            },
            'poverty_data_source': 'US_Census_ACS_2022_5_Year_Estimates'
        }
        
        return summary
    
    def save_results(self, updated_sites: List[Dict], poverty_data: Dict, summary: Dict):
        """Save all results to files"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Save updated sites analysis
        sites_file = self.base_dir / f"DMarco_Sites_With_Poverty_{timestamp}.json"
        with open(sites_file, 'w') as f:
            json.dump(updated_sites, f, indent=2)
        print(f"💾 Saved updated sites to: {sites_file}")
        
        # Save poverty data lookup
        poverty_file = self.base_dir / f"Census_Tract_Poverty_Data_{timestamp}.json"
        with open(poverty_file, 'w') as f:
            json.dump(poverty_data, f, indent=2)
        print(f"💾 Saved poverty lookup to: {poverty_file}")
        
        # Save summary
        summary_file = self.base_dir / f"Poverty_Analysis_Summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"💾 Saved summary to: {summary_file}")
        
        return sites_file, poverty_file, summary_file
    
    def run_complete_analysis(self):
        """Run complete poverty integration analysis"""
        print("🚀 Starting D'Marco ACS Poverty Integration")
        print("=" * 60)
        
        try:
            # Get poverty data for all tracts
            poverty_data = self.integrate_poverty_data()
            
            if not poverty_data:
                print("❌ No poverty data retrieved. Exiting.")
                return
            
            # Update sites with poverty data
            updated_sites = self.update_sites_with_poverty(poverty_data)
            
            # Generate summary
            summary = self.generate_poverty_summary(poverty_data)
            
            # Save results
            sites_file, poverty_file, summary_file = self.save_results(
                updated_sites, poverty_data, summary
            )
            
            # Print final summary
            print("\n" + "=" * 60)
            print("📊 POVERTY INTEGRATION COMPLETE")
            print("=" * 60)
            print(f"✅ Census tracts analyzed: {summary['total_census_tracts']}")
            print(f"✅ Sites updated: {summary['total_sites_analyzed']}")
            print(f"✅ Average poverty rate: {summary['poverty_statistics']['average_poverty_rate']}%")
            print(f"✅ QCT eligible sites: {summary['qct_correlation']['qct_eligible_sites']}")
            print(f"✅ Results saved to: {sites_file.name}")
            
            return {
                'success': True,
                'sites_file': str(sites_file),
                'poverty_file': str(poverty_file),
                'summary_file': str(summary_file),
                'summary': summary
            }
            
        except Exception as e:
            print(f"💥 Error in poverty analysis: {e}")
            return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    integrator = DMarcoACSPovertyIntegrator()
    results = integrator.run_complete_analysis()
    
    if results['success']:
        print(f"\n🎯 Integration complete! Check {results['sites_file']} for updated data.")
    else:
        print(f"\n❌ Integration failed: {results['error']}")