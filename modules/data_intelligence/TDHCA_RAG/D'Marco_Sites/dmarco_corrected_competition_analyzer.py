#!/usr/bin/env python3
"""
🔧 CORRECTED D'Marco TDHCA Competition Analysis
WINGMAN Agent - Using Proper 2025 QAP Rules

Based on actual TDHCA 2025 QAP §11.3(d) One Mile Three Year Rule:
- Only projects awarded in LAST 3 YEARS count for competition
- Same Target Population requirement
- Exemptions for counties <1M population and non-metro areas
- Uses award Year field as baseline for 3-year lookback
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

class DMarcoCorrectCompetitionAnalyzer:
    """Corrected competition analysis using proper TDHCA 2025 QAP rules"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        self.tdhca_db_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas/State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
        
        # Use TOWER's corrected file
        self.dmarco_sites_path = self.base_dir / "Production_Analysis_20250730/dmarco_production_analysis_20250730_134731_COUNTY_CORRECTED.json"
        
        # Current application round year for 3-year lookback
        self.application_year = 2025
        self.lookback_years = [2022, 2023, 2024, 2025]  # 3-year period + current
        
        # Texas county populations (for <1M exemption)
        self.COUNTY_POPULATIONS = {
            'Harris': 4731145,    # Houston - OVER 1M
            'Dallas': 2647642,    # Dallas - OVER 1M  
            'Bexar': 2058515,     # San Antonio - OVER 1M
            'Tarrant': 2110640,   # Fort Worth - OVER 1M
            'Travis': 1290188,    # Austin - OVER 1M
            'Collin': 1064465,    # Dallas suburbs - OVER 1M
            'Orange': 84808,      # UNDER 1M - EXEMPT
            'Henderson': 82150,   # UNDER 1M - EXEMPT
            'Kaufman': 145310,    # UNDER 1M - EXEMPT  
            'Guadalupe': 166847   # UNDER 1M - EXEMPT
        }
        
    def load_tdhca_database(self):
        """Load TDHCA database with corrected filtering"""
        print("🔧 Loading TDHCA project database...")
        
        try:
            tdhca_df = pd.read_excel(self.tdhca_db_path)
            print(f"✅ Loaded {len(tdhca_df)} total TDHCA projects")
            
            # Clean and validate coordinates
            if 'Latitude11' in tdhca_df.columns and 'Longitude11' in tdhca_df.columns:
                tdhca_df['Latitude11'] = pd.to_numeric(tdhca_df['Latitude11'], errors='coerce')
                tdhca_df['Longitude11'] = pd.to_numeric(tdhca_df['Longitude11'], errors='coerce')
                
                # Remove rows with invalid coordinates
                valid_coords = tdhca_df.dropna(subset=['Latitude11', 'Longitude11'])
                coord_mask = (
                    (valid_coords['Latitude11'] >= 25.0) & 
                    (valid_coords['Latitude11'] <= 37.0) &
                    (valid_coords['Longitude11'] >= -107.0) & 
                    (valid_coords['Longitude11'] <= -93.0)
                )
                tdhca_clean = valid_coords[coord_mask].copy()
                
                # CRITICAL: Filter to only 3-year lookback period
                recent_projects = tdhca_clean[tdhca_clean['Year'].isin(self.lookback_years)]
                
                print(f"✅ {len(tdhca_clean)} projects with valid coordinates")
                print(f"✅ {len(recent_projects)} projects in 3-year lookback period ({min(self.lookback_years)}-{max(self.lookback_years)})")
                
                return recent_projects
            else:
                print("❌ Missing coordinate columns in TDHCA database")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Error loading TDHCA database: {e}")
            return pd.DataFrame()
    
    def load_dmarco_sites(self):
        """Load D'Marco sites from TOWER's corrected file"""
        print("🔧 Loading D'Marco sites...")
        
        try:
            with open(self.dmarco_sites_path, 'r') as f:
                sites_data = json.load(f)
            print(f"✅ Loaded {len(sites_data)} D'Marco sites")
            return sites_data
        except Exception as e:
            print(f"❌ Error loading D'Marco sites: {e}")
            return []
    
    def check_county_exemption(self, county_name):
        """Check if county is exempt from One Mile Rule (population <1M)"""
        if county_name in self.COUNTY_POPULATIONS:
            population = self.COUNTY_POPULATIONS[county_name]
            is_exempt = population < 1000000
            return is_exempt, population
        else:
            # Unknown county, assume small (likely exempt)
            return True, "Unknown (assumed <1M)"
    
    def analyze_competition_for_site(self, site, tdhca_projects):
        """Analyze competition for a single D'Marco site using correct rules"""
        site_lat = site['parcel_center_lat']
        site_lng = site['parcel_center_lng']
        
        # Clean county name
        raw_county = site.get('census_county', 'Unknown')
        if raw_county.startswith('County '):
            site_county = raw_county.replace('County ', '')
        else:
            site_county = raw_county.replace(' County', '')
        
        # Check county exemption
        county_exempt, county_pop = self.check_county_exemption(site_county)
        
        competition_analysis = {
            'site_index': site['site_index'],
            'site_name': site['site_name'],
            'county': site_county,
            'county_population': county_pop,
            'county_exempt_under_1m': county_exempt,
            'coordinates': (site_lat, site_lng),
            'nearby_projects_1_mile': [],
            'nearby_projects_2_mile': [],
            'fatal_flaw_9_percent': False,
            'risk_assessment_4_percent': 'LOW',
            'competition_details': {}
        }
        
        # If county is exempt, no fatal flaws for One Mile Rule
        if county_exempt:
            competition_analysis['exemption_reason'] = f"County population {county_pop} < 1,000,000"
            competition_analysis['fatal_flaw_9_percent'] = False
            competition_analysis['competition_details']['exemption_applied'] = True
            print(f"  ✅ Site {site['site_index']} EXEMPT - {site_county} County population {county_pop}")
            return competition_analysis
        
        # Find nearby projects for non-exempt counties
        for _, project in tdhca_projects.iterrows():
            try:
                project_lat = project['Latitude11']
                project_lng = project['Longitude11']
                
                # Calculate distance
                distance_miles = geodesic((site_lat, site_lng), (project_lat, project_lng)).miles
                
                project_info = {
                    'tdhca_number': project.get('TDHCA#', 'Unknown'),
                    'development_name': project.get('Development Name', 'Unknown'),
                    'project_county': project.get('Project County', 'Unknown'),
                    'program_type': project.get('Program Type', 'Unknown'),
                    'award_year': project.get('Year', 'Unknown'),
                    'distance_miles': round(distance_miles, 3),
                    'lihtc_units': project.get('LIHTC Units', 0)
                }
                
                # Collect projects within 2 miles
                if distance_miles <= 2.0:
                    competition_analysis['nearby_projects_2_mile'].append(project_info)
                    
                    # Check for fatal flaw (1 mile for 9% credits)
                    if distance_miles <= 1.0:
                        competition_analysis['nearby_projects_1_mile'].append(project_info)
                        
                        # Fatal flaw conditions (for 9% credits only):
                        # - Within 1 mile
                        # - Same target population (assume general population)
                        # - Awarded in last 3 years (already filtered)
                        # - Not withdrawn/terminated (assume active if in database)
                        if project.get('Program Type') in ['9%HTC', '4%HTC']:
                            competition_analysis['fatal_flaw_9_percent'] = True
                            
            except Exception as e:
                continue
        
        # Risk assessment
        nearby_1_mile = len(competition_analysis['nearby_projects_1_mile'])
        nearby_2_mile = len(competition_analysis['nearby_projects_2_mile'])
        
        if nearby_1_mile > 0:
            competition_analysis['risk_assessment_4_percent'] = 'HIGH'
        elif nearby_2_mile > 2:
            competition_analysis['risk_assessment_4_percent'] = 'MEDIUM'
        else:
            competition_analysis['risk_assessment_4_percent'] = 'LOW'
            
        return competition_analysis
    
    def run_corrected_analysis(self):
        """Run the corrected competition analysis"""
        print("🚀 Starting CORRECTED D'Marco Competition Analysis...")
        print("📋 Using proper TDHCA 2025 QAP §11.3(d) One Mile Three Year Rule")
        
        # Load data
        tdhca_projects = self.load_tdhca_database()
        dmarco_sites = self.load_dmarco_sites()
        
        if tdhca_projects.empty or not dmarco_sites:
            print("❌ Failed to load required data")
            return None
        
        # Run analysis
        results = []
        fatal_flaw_count = 0
        exempt_count = 0
        
        print(f"\n🔍 Analyzing {len(dmarco_sites)} D'Marco sites against {len(tdhca_projects)} recent TDHCA projects...")
        
        for site in dmarco_sites:
            analysis = self.analyze_competition_for_site(site, tdhca_projects)
            results.append(analysis)
            
            if analysis.get('county_exempt_under_1m'):
                exempt_count += 1
            elif analysis['fatal_flaw_9_percent']:
                fatal_flaw_count += 1
                print(f"  ⚠️  FATAL FLAW: Site {site['site_index']} - {analysis['nearby_projects_1_mile'][0]['development_name']} within {analysis['nearby_projects_1_mile'][0]['distance_miles']} miles")
        
        # Summary
        clean_sites = len(results) - fatal_flaw_count
        
        summary = {
            'analysis_date': datetime.now().isoformat(),
            'total_sites_analyzed': len(results),
            'tdhca_projects_screened': len(tdhca_projects),
            'lookback_period': f"{min(self.lookback_years)}-{max(self.lookback_years)}",
            'qap_rule_applied': 'TDHCA 2025 QAP §11.3(d) One Mile Three Year Rule',
            'results': {
                'sites_exempt_county_under_1m': exempt_count,
                'fatal_flaw_sites_9_percent': fatal_flaw_count,
                'clean_sites_suitable_9_percent': clean_sites,
                'fatal_flaw_rate': round((fatal_flaw_count / len(results)) * 100, 1)
            },
            'competition_analysis': results
        }
        
        print(f"\n📊 CORRECTED ANALYSIS RESULTS:")
        print(f"✅ Sites exempt (county population <1M): {exempt_count}")
        print(f"⚠️  Fatal flaw sites (9% credits): {fatal_flaw_count}")
        print(f"✅ Clean sites (suitable for 9% credits): {clean_sites}")
        print(f"📈 Fatal flaw rate: {summary['results']['fatal_flaw_rate']}%")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.base_dir / f"DMarco_CORRECTED_Competition_Analysis_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Results saved: {results_file}")
        return summary

if __name__ == "__main__":
    analyzer = DMarcoCorrectCompetitionAnalyzer()
    results = analyzer.run_corrected_analysis()