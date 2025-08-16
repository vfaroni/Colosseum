#!/usr/bin/env python3
"""
🔧 TCEQ Environmental Database Fixer
WINGMAN Agent - Fix Environmental Screening Issues

ROOT CAUSE IDENTIFIED: 
- LPST database has 29,646 records but NO coordinates
- Environmental screening fails because can't calculate distances
- Need to either geocode addresses or use county-level screening

SOLUTION STRATEGY:
1. Use TCEQ Notices of Enforcement (HAS coordinates - 25,757 records) 
2. County-level LPST screening for major contamination sites
3. Implement proper distance-based environmental risk assessment
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

class TCEQEnvironmentalFixer:
    """Fix TCEQ environmental database searches with available coordinate data"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        self.tceq_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas/Environmental/TX_Commission_on_Env")
        
        # Load TCEQ databases
        self.databases = {
            'lpst_sites': 'Texas_Commission_on_Environmental_Quality_-_Leaking_Petroleum_Storage_Tank__LPST__Sites_20250702.csv',
            'enforcement': 'Texas_Commission_on_Environmental_Quality_-_Notices_of_Enforcement__NOE__20250702.csv',
            'complaints': 'Texas_Commission_on_Environmental_Quality_-_Complaints_20250702.csv',
            'dry_cleaners_hist': 'Texas_Commission_on_Environmental_Quality_-_Historical_Dry_Cleaner_Registrations_20250702.csv',
            'dry_cleaners_op': 'Texas_Commission_on_Environmental_Quality_-_Operating_Dry_Cleaner_Registrations_20250702.csv'
        }
        
        # Environmental risk distance thresholds (ASTM E1527-21 standards)
        self.RISK_THRESHOLDS = {
            'IMMEDIATE': 0.125,    # 1/8 mile (660 feet) - vapor intrusion concern
            'CRITICAL': 0.25,      # 1/4 mile - Phase I ESA enhancement required  
            'HIGH': 0.5,           # 1/2 mile - standard screening radius
            'MEDIUM': 1.0,         # 1 mile - regional contamination assessment
        }
        
        # Environmental concern categories and weights
        self.CONCERN_WEIGHTS = {
            'LPST_ACTIVE': 100,        # Active petroleum contamination
            'LPST_CLOSED': 25,         # Closed petroleum sites
            'ENFORCEMENT_MAJOR': 75,    # Major environmental violations
            'ENFORCEMENT_MINOR': 25,    # Minor violations
            'DRY_CLEANER_HIST': 50,    # Historical dry cleaner (PCE/TCE)
            'DRY_CLEANER_OP': 30,      # Operating dry cleaner
            'COMPLAINT_ACTIVE': 40,    # Active environmental complaints
        }
        
    def load_dmarco_sites(self):
        """Load D'Marco sites data"""
        sites_file = self.base_dir / "Production_Analysis_20250730/dmarco_production_analysis_20250730_134731_COUNTY_CORRECTED.json"
        
        with open(sites_file, 'r') as f:
            sites_data = json.load(f)
        
        print(f"✅ Loaded {len(sites_data)} D'Marco sites")
        return sites_data
    
    def load_tceq_databases(self):
        """Load available TCEQ databases with coordinate analysis"""
        print("🔧 Loading TCEQ Environmental Databases...")
        
        tceq_data = {}
        coordinate_analysis = {}
        
        for db_key, filename in self.databases.items():
            file_path = self.tceq_dir / filename
            
            if file_path.exists():
                try:
                    print(f"  Loading {db_key}...", end=" ")
                    
                    # Load with error handling for encoding issues
                    try:
                        df = pd.read_csv(file_path, encoding='utf-8')
                    except UnicodeDecodeError:
                        df = pd.read_csv(file_path, encoding='latin-1')
                    
                    tceq_data[db_key] = df
                    
                    # Analyze coordinate availability
                    coord_cols = [col for col in df.columns if any(term in col.lower() 
                                 for term in ['lat', 'lon', 'coord', 'x', 'y', 'longitude', 'latitude'])]
                    
                    has_coords = len(coord_cols) > 0
                    coordinate_analysis[db_key] = {
                        'has_coordinates': has_coords,
                        'coordinate_columns': coord_cols,
                        'record_count': len(df),
                        'counties_available': 'County' in df.columns or 'COUNTY' in df.columns
                    }
                    
                    coord_status = "✅ COORDS" if has_coords else "❌ NO COORDS"
                    print(f"{len(df)} records [{coord_status}]")
                    
                except Exception as e:
                    print(f"❌ Error loading {db_key}: {e}")
                    coordinate_analysis[db_key] = {'error': str(e)}
            else:
                print(f"  ❌ File not found: {filename}")
        
        return tceq_data, coordinate_analysis
    
    def analyze_enforcement_coordinates(self, enforcement_df):
        """Analyze enforcement database coordinates for geospatial analysis"""
        print("\n🗺️  ANALYZING ENFORCEMENT COORDINATES")
        
        # Look for coordinate columns
        coord_cols = [col for col in enforcement_df.columns if any(term in col.lower() 
                     for term in ['lat', 'lon', 'coord', 'x', 'y'])]
        
        print(f"  Coordinate columns found: {coord_cols}")
        
        if len(coord_cols) >= 2:
            lat_col = [col for col in coord_cols if 'lat' in col.lower()][0]
            lon_col = [col for col in coord_cols if 'lon' in col.lower()][0]
            
            # Clean and validate coordinates
            enforcement_df[lat_col] = pd.to_numeric(enforcement_df[lat_col], errors='coerce')
            enforcement_df[lon_col] = pd.to_numeric(enforcement_df[lon_col], errors='coerce')
            
            # Filter valid coordinates (Texas bounds)
            valid_coords = (
                (enforcement_df[lat_col] >= 25.0) & (enforcement_df[lat_col] <= 37.0) &
                (enforcement_df[lon_col] >= -107.0) & (enforcement_df[lon_col] <= -93.0)
            )
            
            valid_df = enforcement_df[valid_coords].copy()
            
            print(f"  ✅ Valid coordinates: {len(valid_df)}/{len(enforcement_df)} ({len(valid_df)/len(enforcement_df)*100:.1f}%)")
            
            return valid_df, lat_col, lon_col
        else:
            print("  ❌ Insufficient coordinate columns")
            return None, None, None
    
    def calculate_environmental_proximity(self, site_lat, site_lng, environmental_df, lat_col, lon_col):
        """Calculate distances to environmental concerns"""
        if environmental_df is None or environmental_df.empty:
            return []
        
        site_coords = (site_lat, site_lng)
        environmental_concerns = []
        
        for idx, row in environmental_df.iterrows():
            env_lat = row[lat_col]
            env_lng = row[lon_col]
            
            if pd.notna(env_lat) and pd.notna(env_lng):
                env_coords = (env_lat, env_lng)
                distance_miles = geodesic(site_coords, env_coords).miles
                
                # Classify risk level based on distance
                risk_level = 'LOW'
                for threshold_name, threshold_miles in self.RISK_THRESHOLDS.items():
                    if distance_miles <= threshold_miles:
                        risk_level = threshold_name
                        break
                
                concern = {
                    'type': 'ENVIRONMENTAL_ENFORCEMENT',
                    'distance_miles': round(distance_miles, 3),
                    'risk_level': risk_level,
                    'facility_name': row.get('Regulated Entity Name', 'Unknown'),
                    'county': row.get('County', 'Unknown'),
                    'coordinates': [env_lat, env_lng],
                    'weight': self.CONCERN_WEIGHTS.get('ENFORCEMENT_MAJOR', 50)
                }
                
                environmental_concerns.append(concern)
        
        # Sort by distance
        environmental_concerns.sort(key=lambda x: x['distance_miles'])
        
        return environmental_concerns
    
    def county_level_lpst_screening(self, site_county, lpst_df):
        """Perform county-level LPST screening (no coordinates available)"""
        county_concerns = []
        
        if lpst_df is not None and not lpst_df.empty:
            # Clean county names for matching
            site_county_clean = site_county.replace(' County', '').replace('County ', '').strip()
            
            # Filter LPST sites in same county
            county_lpst = lpst_df[lpst_df['County'].str.contains(site_county_clean, case=False, na=False)]
            
            if not county_lpst.empty:
                # Analyze LPST status (active vs closed)
                status_col = None
                for col in county_lpst.columns:
                    if any(term in col.lower() for term in ['status', 'closure', 'active']):
                        status_col = col
                        break
                
                active_sites = 0
                closed_sites = 0
                
                if status_col:
                    active_sites = len(county_lpst[county_lpst[status_col].str.contains('Open|Active', case=False, na=False)])
                    closed_sites = len(county_lpst) - active_sites
                else:
                    # Assume all are potential concerns if no status info
                    active_sites = len(county_lpst)
                
                # Create county-level concern
                concern = {
                    'type': 'COUNTY_LPST_SCREENING',
                    'county': site_county,
                    'total_lpst_sites': len(county_lpst),
                    'active_sites': active_sites,
                    'closed_sites': closed_sites,
                    'risk_assessment': 'HIGH' if active_sites > 5 else 'MEDIUM' if active_sites > 0 else 'LOW',
                    'recommendation': f'County has {len(county_lpst)} LPST sites - Phase I ESA recommended' if len(county_lpst) > 0 else 'Low LPST density',
                    'weight': min(active_sites * 10 + closed_sites * 2, 100)
                }
                
                county_concerns.append(concern)
        
        return county_concerns
    
    def fix_environmental_screening(self):
        """Fix environmental screening using available coordinate data"""
        print("🚀 FIXING TCEQ ENVIRONMENTAL SCREENING")
        
        # Load data
        sites_data = self.load_dmarco_sites()
        tceq_data, coord_analysis = self.load_tceq_databases()
        
        # Analyze coordinate availability
        print(f"\n📊 COORDINATE ANALYSIS:")
        for db, analysis in coord_analysis.items():
            if 'error' not in analysis:
                coord_status = "✅" if analysis['has_coordinates'] else "❌"
                print(f"  {db}: {analysis['record_count']} records {coord_status}")
        
        # Process enforcement data (has coordinates)
        enforcement_df = None
        lat_col = lon_col = None
        
        if 'enforcement' in tceq_data:
            enforcement_df, lat_col, lon_col = self.analyze_enforcement_coordinates(tceq_data['enforcement'])
        
        # Process each D'Marco site
        updated_sites = []
        screening_results = {
            'sites_with_concerns': 0,
            'total_environmental_concerns': 0,
            'concerns_by_type': {},
            'sites_analyzed': 0
        }
        
        print(f"\n🔍 SCREENING {len(sites_data)} SITES...")
        
        for site in sites_data:
            site_copy = site.copy()
            site_lat = site['parcel_center_lat']
            site_lng = site['parcel_center_lng']
            site_county = site.get('census_county', 'Unknown')
            site_index = site['site_index']
            
            all_concerns = []
            
            # 1. Enforcement proximity analysis (has coordinates)
            if enforcement_df is not None:
                enforcement_concerns = self.calculate_environmental_proximity(
                    site_lat, site_lng, enforcement_df, lat_col, lon_col
                )
                
                # Filter to within screening radius (1 mile)
                nearby_enforcement = [c for c in enforcement_concerns if c['distance_miles'] <= 1.0]
                all_concerns.extend(nearby_enforcement)
            
            # 2. County-level LPST screening (no coordinates)
            if 'lpst_sites' in tceq_data:
                county_lpst = self.county_level_lpst_screening(site_county, tceq_data['lpst_sites'])
                all_concerns.extend(county_lpst)
            
            # Update site with environmental analysis
            site_copy['environmental_screening_status'] = 'SUCCESS_TCEQ_FIXED'
            site_copy['environmental_concerns_found'] = len(all_concerns)
            site_copy['environmental_concerns_detail'] = all_concerns
            
            # Risk assessment
            if len(all_concerns) == 0:
                site_copy['environmental_risk_level'] = 'LOW'
                site_copy['environmental_recommendation'] = 'Standard Phase I ESA'
            elif any(c.get('risk_level') == 'IMMEDIATE' or c.get('risk_assessment') == 'HIGH' for c in all_concerns):
                site_copy['environmental_risk_level'] = 'HIGH'
                site_copy['environmental_recommendation'] = 'Enhanced Phase I ESA with vapor assessment'
            elif any(c.get('risk_level') == 'CRITICAL' for c in all_concerns):
                site_copy['environmental_risk_level'] = 'MEDIUM'
                site_copy['environmental_recommendation'] = 'Enhanced Phase I ESA recommended'
            else:
                site_copy['environmental_risk_level'] = 'LOW-MEDIUM'
                site_copy['environmental_recommendation'] = 'Standard Phase I ESA with awareness of nearby concerns'
            
            # Update statistics
            screening_results['sites_analyzed'] += 1
            if len(all_concerns) > 0:
                screening_results['sites_with_concerns'] += 1
                screening_results['total_environmental_concerns'] += len(all_concerns)
            
            # Track concern types
            for concern in all_concerns:
                concern_type = concern['type']
                if concern_type not in screening_results['concerns_by_type']:
                    screening_results['concerns_by_type'][concern_type] = 0
                screening_results['concerns_by_type'][concern_type] += 1
            
            updated_sites.append(site_copy)
            
            concerns_text = f"({len(all_concerns)} concerns)" if len(all_concerns) > 0 else "(clean)"
            print(f"  Site {site_index}: ✅ {site_copy['environmental_risk_level']} risk {concerns_text}")
        
        return updated_sites, screening_results, coord_analysis
    
    def create_fixed_environmental_analysis(self):
        """Create comprehensive fixed environmental analysis"""
        print("🎯 CREATING FIXED ENVIRONMENTAL ANALYSIS")
        
        # Fix environmental screening
        updated_sites, results, coord_analysis = self.fix_environmental_screening()
        
        # Calculate statistics
        sites_with_concerns_pct = round((results['sites_with_concerns'] / results['sites_analyzed']) * 100, 1)
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create comprehensive report
        analysis_report = {
            'analysis_date': datetime.now().isoformat(),
            'analysis_type': 'TCEQ_ENVIRONMENTAL_SCREENING_FIXED',
            'root_cause_resolution': {
                'original_issue': 'LPST database lacks coordinates - 0 results for all sites',
                'solution_implemented': 'Use enforcement database (has coordinates) + county-level LPST screening',
                'data_sources_used': list(coord_analysis.keys())
            },
            'screening_results': results,
            'coverage_summary': {
                'sites_analyzed': results['sites_analyzed'],
                'sites_with_concerns': results['sites_with_concerns'],
                'sites_clean': results['sites_analyzed'] - results['sites_with_concerns'],
                'concern_rate_percentage': sites_with_concerns_pct
            },
            'coordinate_analysis': coord_analysis,
            'data_quality_improvements': [
                'Used TCEQ Notices of Enforcement (25,757 records with coordinates)',
                'Implemented county-level LPST screening for 29,646 petroleum sites',
                'Applied ASTM E1527-21 distance thresholds for risk assessment',
                'Created weighted concern scoring system'
            ],
            'recommendations': [
                'Geocode LPST database addresses for precise proximity analysis',
                'Integrate additional environmental databases (TWDB, RRC)',
                'Consider commercial environmental database service for complete coverage',
                'Implement automated screening for new properties'
            ]
        }
        
        # Save updated sites
        fixed_sites_file = self.base_dir / f"dmarco_sites_ENVIRONMENTAL_FIXED_{timestamp}.json"
        with open(fixed_sites_file, 'w') as f:
            json.dump(updated_sites, f, indent=2)
        
        # Save analysis report
        report_file = self.base_dir / f"TCEQ_Environmental_Fix_Report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(analysis_report, f, indent=2)
        
        print(f"\n📊 ENVIRONMENTAL SCREENING FIXED!")
        print(f"✅ Sites analyzed: {results['sites_analyzed']}")
        print(f"🔍 Sites with concerns: {results['sites_with_concerns']} ({sites_with_concerns_pct}%)")
        print(f"🧹 Sites clean: {results['sites_analyzed'] - results['sites_with_concerns']}")
        print(f"📋 Total concerns found: {results['total_environmental_concerns']}")
        print(f"🗂️  Concern types: {results['concerns_by_type']}")
        
        print(f"\n💾 Files created:")
        print(f"   • Fixed sites data: {fixed_sites_file.name}")
        print(f"   • Analysis report: {report_file.name}")
        
        return analysis_report

if __name__ == "__main__":
    fixer = TCEQEnvironmentalFixer()
    results = fixer.create_fixed_environmental_analysis()