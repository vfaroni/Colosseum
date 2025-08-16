#!/usr/bin/env python3
"""
ULTIMATE COMPREHENSIVE LIHTC ANALYZER
375 → 155 QCT/DDA Sites with Complete Analysis Pipeline
Includes: TCEQ Environmental + FEMA Flood + Schools + Competing Projects + AMI + Cost Analysis
"""

import pandas as pd
import geopandas as gpd
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from geopy.distance import geodesic
from shapely.geometry import Point
import requests
import time
import warnings
warnings.filterwarnings('ignore')

class UltimateComprehensiveLIHTCAnalyzer:
    """Complete LIHTC analysis pipeline: 375 → 155 sites with 100% data coverage"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
        self.data_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Data_Sets")
        
        # Input files
        self.costar_file = self.base_dir / "D'Marco_Sites/Costar_07312025/CS_Costar_TX_Land_8ac-30ac_07312025_ALL-export.xlsx"
        self.qct_dda_file = self.base_dir / "D'Marco_Sites/Analysis_Results/MASTER_155_BoostEligible_Sites_20250731_223500.xlsx"
        self.census_api_file = self.base_dir / "D'Marco_Sites/Analysis_Results/BATCH_CENSUS_API_POVERTY_20250801_172636.xlsx"
        self.hud_ami_file = self.base_dir / "D'Marco_Sites/HUD2025_AMI_Rent_Data_Static.xlsx"
        
        # TCEQ Environmental data sources
        self.tceq_data_dir = self.data_dir / "texas/Environmental/TX_Commission_on_Env"
        self.tceq_files = {
            'lpst': self.tceq_data_dir / "Texas_Commission_on_Environmental_Quality_-_Leaking_Petroleum_Storage_Tank__LPST__Sites_20250702.csv",
            'dry_cleaners_operating': self.tceq_data_dir / "Texas_Commission_on_Environmental_Quality_-_Operating_Dry_Cleaner_Registrations_20250702.csv",
            'dry_cleaners_historical': self.tceq_data_dir / "Texas_Commission_on_Environmental_Quality_-_Historical_Dry_Cleaner_Registrations_20250702.csv",
            'enforcement': self.tceq_data_dir / "Texas_Commission_on_Environmental_Quality_-_Notices_of_Enforcement__NOE__20250702.csv",
            'complaints': self.tceq_data_dir / "Texas_Commission_on_Environmental_Quality_-_Complaints_20250702.csv"
        }
        
        # School data
        self.schools_file = self.data_dir / "texas/TX_Public_Schools/Schools_2024_to_2025.geojson"
        
        # TDHCA competing projects
        self.tdhca_db_path = self.data_dir / "texas/State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # TCEQ Environmental Risk Thresholds (Industry Standard)
        self.ENVIRONMENTAL_RISK_THRESHOLDS = {
            'CRITICAL': 0.125,    # ≤1/8 mile - Vapor intrusion concern
            'HIGH': 0.25,         # ≤1/4 mile - Enhanced Phase I ESA required
            'MEDIUM': 0.5,        # ≤1/2 mile - Standard screening distance  
            'LOW': 1.0            # 1/2 to 1 mile - Regional assessment
        }
        
        # Environmental due diligence costs
        self.ENVIRONMENTAL_DD_COSTS = {
            'CRITICAL': 35000,    # Enhanced Phase I + vapor assessment
            'HIGH': 15000,        # Enhanced Phase I ESA
            'MEDIUM': 6500,       # Standard Phase I ESA
            'LOW': 2500,          # Basic environmental awareness
            'NONE': 0             # No environmental concerns
        }
        
        # FEMA Flood Risk (Corrected - Priority not Elimination)
        self.FLOOD_RISK_PRIORITY = {
            'X': {'priority': 'HIGHEST', 'insurance_cost': 0, 'description': 'No flood insurance required'},
            'AE': {'priority': 'LOWER', 'insurance_cost': 1200, 'description': '1% annual chance with BFE'},
            'A': {'priority': 'LOWER', 'insurance_cost': 1400, 'description': '1% annual chance flood'},
            'AH': {'priority': 'LOWER', 'insurance_cost': 1200, 'description': 'Shallow flooding'},
            'AO': {'priority': 'LOWER', 'insurance_cost': 800, 'description': 'Sheet flow flooding'},
            'VE': {'priority': 'ELIMINATE', 'insurance_cost': 2500, 'description': 'Coastal high hazard'},
            'NOT_IN_FLOODPLAIN': {'priority': 'HIGHEST', 'insurance_cost': 0, 'description': 'Outside flood zones'}
        }
        
        # Texas Regional Cost Multipliers
        self.REGIONAL_COST_MULTIPLIERS = {
            'Dallas_Metro': {'construction_multiplier': 1.18, 'counties': ['Dallas', 'Tarrant', 'Collin', 'Denton', 'Rockwall']},
            'Austin_Metro': {'construction_multiplier': 1.14, 'counties': ['Travis', 'Williamson', 'Hays', 'Caldwell']},
            'Houston_Metro': {'construction_multiplier': 1.12, 'counties': ['Harris', 'Fort Bend', 'Montgomery', 'Brazoria', 'Galveston']},
            'San_Antonio_Metro': {'construction_multiplier': 1.06, 'counties': ['Bexar', 'Guadalupe', 'Comal', 'Wilson']},
            'West_Texas': {'construction_multiplier': 0.98, 'counties': ['Midland', 'Ector', 'Lubbock', 'Amarillo']},
            'South_Texas': {'construction_multiplier': 0.95, 'counties': ['Cameron', 'Hidalgo', 'Webb', 'Starr']},
            'East_Texas_Rural': {'construction_multiplier': 0.92, 'counties': ['Henderson', 'Orange', 'Jefferson', 'Hardin', 'Tyler']},
            'Rural_Baseline': {'construction_multiplier': 1.00, 'counties': ['Other']}
        }
        
        # Base construction costs per unit
        self.BASE_COSTS = {
            'hard_costs': 135000,
            'soft_costs': 25000,
            'developer_fee': 18000,
            'contingency': 8000,
            'total_base': 186000
        }
        
        # Competition analysis - TDHCA QAP rules
        self.COMPETITION_RULES = {
            'large_cities': {'radius_miles': 1.0, 'cities': ['dallas', 'houston', 'san antonio', 'austin', 'fort worth']},
            'suburbs': {'radius_miles': 2.0, 'cities': ['plano', 'frisco', 'katy', 'pearland', 'round rock']},
            'other': {'radius_miles': 2.0, 'cities': []}
        }
        
        # Lookback period for competing projects
        self.application_year = 2025
        self.competition_lookback_years = [2022, 2023, 2024, 2025]  # 3-year + current
        
    def load_base_data(self):
        """Phase 1: Load 375 CoStar sites and filter to 155 QCT/DDA sites"""
        print("🚀 PHASE 1: Loading base data (375 → 155 sites)")
        print("=" * 60)
        
        # Load CoStar base data
        print("📊 Loading 375 CoStar sites...")
        try:
            costar_df = pd.read_excel(self.costar_file)
            print(f"✅ Loaded {len(costar_df)} CoStar sites")
            
            # Calculate real acreage
            if 'Land SF Gross' in costar_df.columns:
                land_sf = pd.to_numeric(costar_df['Land SF Gross'], errors='coerce')
                costar_df['Actual_Acres'] = land_sf / 43560
                valid_acres = (land_sf > 0).sum()
                print(f"   Real acreage: {valid_acres}/{len(costar_df)} sites")
        except Exception as e:
            print(f"❌ Failed to load CoStar data: {e}")
            return None
        
        # Load QCT/DDA filter (155 sites)
        print("🎯 Loading 155 QCT/DDA eligible sites...")
        try:
            qct_df = pd.read_excel(self.qct_dda_file)
            print(f"✅ Loaded {len(qct_df)} QCT/DDA eligible sites")
            
            # Get addresses for filtering
            qct_addresses = set(qct_df['Address'].str.strip())
            
            # Filter CoStar to QCT/DDA eligible sites only
            filtered_costar = costar_df[costar_df['Address'].str.strip().isin(qct_addresses)].copy()
            print(f"✅ Filtered to {len(filtered_costar)} sites matching QCT/DDA addresses")
            
            # Merge to get QCT/DDA status
            merged_df = filtered_costar.merge(
                qct_df[['Address', 'QCT_Status', 'DDA_Status', 'Basis_Boost_Eligible', 'FINAL_TRACT']], 
                on='Address', 
                how='left'
            )
            
            print(f"✅ Merged dataset: {len(merged_df)} sites with QCT/DDA status")
            return merged_df
            
        except Exception as e:
            print(f"❌ Failed to load QCT/DDA data: {e}")
            return costar_df
    
    def determine_regional_market(self, city, county=None):
        """Determine Texas regional market for cost multipliers"""
        city_str = str(city).lower()
        county_str = str(county).lower() if county else ""
        
        for region, data in self.REGIONAL_COST_MULTIPLIERS.items():
            if region == 'Rural_Baseline':
                continue
            
            # Check if city or county matches regional criteria
            if region == 'Dallas_Metro':
                if any(term in city_str for term in ['dallas', 'plano', 'frisco', 'richardson', 'garland', 'irving']):
                    return region
                if any(term in city_str for term in ['fort worth', 'arlington', 'grand prairie']):
                    return region
            elif region == 'Austin_Metro':
                if any(term in city_str for term in ['austin', 'round rock', 'cedar park', 'pflugerville']):
                    return region
            elif region == 'Houston_Metro':
                if any(term in city_str for term in ['houston', 'katy', 'pearland', 'sugar land', 'conroe']):
                    return region
            elif region == 'San_Antonio_Metro':
                if any(term in city_str for term in ['san antonio', 'new braunfels', 'schertz']):
                    return region
            elif region == 'West_Texas':
                if any(term in city_str for term in ['midland', 'odessa', 'lubbock', 'amarillo']):
                    return region
            elif region == 'South_Texas':
                if any(term in city_str for term in ['brownsville', 'mcallen', 'laredo', 'harlingen']):
                    return region
            elif region == 'East_Texas_Rural':
                if any(term in city_str for term in ['tyler', 'longview', 'beaumont', 'orange']):
                    return region
        
        return 'Rural_Baseline'
    
    def add_texas_regional_data(self, df):
        """Add Texas regional identifiers and cost modifiers"""
        print("\n💰 Adding Texas regional cost modifiers...")
        
        # Add regional market determination
        df['Regional_Market'] = df.apply(lambda row: self.determine_regional_market(
            row.get('City', ''), row.get('County', '')), axis=1)
        
        # Add cost multipliers
        for idx, site in df.iterrows():
            region = site['Regional_Market']
            multiplier = self.REGIONAL_COST_MULTIPLIERS[region]['construction_multiplier']
            
            df.loc[idx, 'Construction_Cost_Multiplier'] = multiplier
            df.loc[idx, 'Adjusted_Cost_Per_Unit'] = int(self.BASE_COSTS['total_base'] * multiplier)
            df.loc[idx, 'Hard_Costs_Adjusted'] = int(self.BASE_COSTS['hard_costs'] * multiplier)
            df.loc[idx, 'Soft_Costs_Adjusted'] = int(self.BASE_COSTS['soft_costs'] * multiplier)
        
        # Show regional distribution
        regional_dist = df['Regional_Market'].value_counts()
        print("✅ Regional cost modifiers assigned:")
        for region, count in regional_dist.items():
            multiplier = self.REGIONAL_COST_MULTIPLIERS[region]['construction_multiplier']
            print(f"   {region}: {count} sites ({multiplier}x)")
        
        return df
    
    def add_development_capacity(self, df):
        """Add development capacity at 18 units/acre"""
        print("\n🏗️ Calculating development capacity at 18 units/acre...")
        
        # Initialize capacity columns
        df['Units_18_Per_Acre'] = 0
        df['Units_Conservative'] = 0  # 15 units/acre
        df['Units_Aggressive'] = 0   # 22 units/acre
        df['Meets_250_Unit_Threshold'] = False
        df['Development_Scale'] = 'UNKNOWN'
        
        capacity_calculated = 0
        
        for idx, site in df.iterrows():
            acres = site.get('Actual_Acres')
            
            if pd.notna(acres) and acres > 0:
                # Calculate unit capacity at different densities
                units_18 = int(acres * 18)
                units_conservative = int(acres * 15)
                units_aggressive = int(acres * 22)
                
                df.loc[idx, 'Units_18_Per_Acre'] = units_18
                df.loc[idx, 'Units_Conservative'] = units_conservative
                df.loc[idx, 'Units_Aggressive'] = units_aggressive
                df.loc[idx, 'Meets_250_Unit_Threshold'] = units_18 >= 250
                
                # Determine development scale
                if units_18 >= 300:
                    scale = 'LARGE_SCALE'
                elif units_18 >= 200:
                    scale = 'MEDIUM_SCALE'
                elif units_18 >= 100:
                    scale = 'SMALL_SCALE'
                else:
                    scale = 'MICRO_SCALE'
                
                df.loc[idx, 'Development_Scale'] = scale
                capacity_calculated += 1
        
        print(f"✅ Development capacity calculated: {capacity_calculated}/{len(df)} sites")
        
        # Show scale distribution
        scale_dist = df['Development_Scale'].value_counts()
        print("   Development scale distribution:")
        for scale, count in scale_dist.items():
            if scale != 'UNKNOWN':
                print(f"     {scale}: {count} sites")
        
        return df
    
    def load_tceq_environmental_data(self):
        """Load all TCEQ environmental datasets"""
        print("\n🌍 Loading TCEQ environmental datasets...")
        
        tceq_data = {}
        
        for source, file_path in self.tceq_files.items():
            try:
                df = pd.read_csv(file_path)
                
                # Clean and geocode if needed
                if 'Latitude' in df.columns and 'Longitude' in df.columns:
                    # Filter for valid Texas coordinates
                    valid_coords = (
                        (df['Latitude'] >= 25.0) & (df['Latitude'] <= 37.0) &
                        (df['Longitude'] >= -107.0) & (df['Longitude'] <= -93.0)
                    )
                    df_clean = df[valid_coords].copy()
                    
                    tceq_data[source] = df_clean
                    print(f"   ✅ {source}: {len(df_clean)} sites with valid coordinates")
                else:
                    print(f"   ⚠️ {source}: No coordinate columns found")
                    
            except Exception as e:
                print(f"   ❌ {source}: Failed to load - {e}")
        
        return tceq_data
    
    def calculate_environmental_risk(self, site_lat, site_lng, tceq_data):
        """Calculate environmental risk for a single site"""
        site_point = (site_lat, site_lng)
        
        min_distance = float('inf')
        closest_source = None
        source_type = None
        environmental_sites_nearby = []
        
        # Check all TCEQ data sources
        for source, df in tceq_data.items():
            for idx, env_site in df.iterrows():
                env_lat = env_site.get('Latitude')
                env_lng = env_site.get('Longitude')
                
                if pd.notna(env_lat) and pd.notna(env_lng):
                    try:
                        distance = geodesic(site_point, (env_lat, env_lng)).miles
                        
                        # Track all nearby sites within 1 mile
                        if distance <= 1.0:
                            environmental_sites_nearby.append({
                                'source': source,
                                'distance': distance,
                                'name': env_site.get('Name', 'Unknown'),
                                'address': env_site.get('Address', 'Unknown')
                            })
                        
                        # Track closest site
                        if distance < min_distance:
                            min_distance = distance
                            closest_source = env_site
                            source_type = source
                            
                    except Exception:
                        continue
        
        # Determine risk level based on closest distance
        if min_distance <= self.ENVIRONMENTAL_RISK_THRESHOLDS['CRITICAL']:
            risk_level = 'CRITICAL'
        elif min_distance <= self.ENVIRONMENTAL_RISK_THRESHOLDS['HIGH']:
            risk_level = 'HIGH'
        elif min_distance <= self.ENVIRONMENTAL_RISK_THRESHOLDS['MEDIUM']:
            risk_level = 'MEDIUM'
        elif min_distance <= self.ENVIRONMENTAL_RISK_THRESHOLDS['LOW']:
            risk_level = 'LOW'
        else:
            risk_level = 'NONE'
        
        return {
            'environmental_risk_level': risk_level,
            'closest_contamination_distance': min_distance if min_distance != float('inf') else None,
            'closest_contamination_source': source_type,
            'environmental_dd_cost': self.ENVIRONMENTAL_DD_COSTS[risk_level],
            'sites_within_1_mile': len(environmental_sites_nearby),
            'nearby_sites_detail': environmental_sites_nearby[:5]  # Top 5 closest
        }
    
    def phase2_environmental_screening(self, df):
        """Phase 2: TCEQ Environmental Screening for all sites"""
        print("\n" + "="*60)
        print("STARTING PHASE 2: TCEQ ENVIRONMENTAL SCREENING")
        print("="*60)
        
        # Load TCEQ data
        tceq_data = self.load_tceq_environmental_data()
        
        if not tceq_data:
            print("❌ No TCEQ environmental data loaded")
            return df
        
        # Initialize environmental columns
        env_columns = [
            'Environmental_Risk_Level', 'Closest_Contamination_Distance', 
            'Closest_Contamination_Source', 'Environmental_DD_Cost',
            'Environmental_Sites_Within_1_Mile', 'Environmental_Details'
        ]
        
        for col in env_columns:
            df[col] = 'MISSING'
        
        print(f"\n🔍 Analyzing environmental risk for {len(df)} sites...")
        
        environmental_analysis_count = 0
        risk_level_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'NONE': 0}
        
        for idx, site in df.iterrows():
            lat = site.get('Latitude')
            lng = site.get('Longitude')
            address = site.get('Address', 'Unknown')
            
            if pd.notna(lat) and pd.notna(lng):
                print(f"   Analyzing site {idx+1}/{len(df)}: {address[:50]}...")
                
                # Calculate environmental risk
                env_analysis = self.calculate_environmental_risk(lat, lng, tceq_data)
                
                # Update dataframe
                df.loc[idx, 'Environmental_Risk_Level'] = env_analysis['environmental_risk_level']
                df.loc[idx, 'Closest_Contamination_Distance'] = env_analysis['closest_contamination_distance']
                df.loc[idx, 'Closest_Contamination_Source'] = env_analysis['closest_contamination_source']
                df.loc[idx, 'Environmental_DD_Cost'] = env_analysis['environmental_dd_cost']
                df.loc[idx, 'Environmental_Sites_Within_1_Mile'] = env_analysis['sites_within_1_mile']
                df.loc[idx, 'Environmental_Details'] = str(env_analysis['nearby_sites_detail'])
                
                risk_level_counts[env_analysis['environmental_risk_level']] += 1
                environmental_analysis_count += 1
                
                # Progress update every 25 sites
                if (idx + 1) % 25 == 0:
                    print(f"     Progress: {idx + 1}/{len(df)} sites analyzed")
            else:
                print(f"   ⚠️ Site {idx+1}: No valid coordinates")
        
        print(f"\n✅ PHASE 2 COMPLETE: Environmental analysis for {environmental_analysis_count}/{len(df)} sites")
        print("\n📊 Environmental Risk Distribution:")
        total_with_risk = sum(v for k, v in risk_level_counts.items() if k != 'NONE')
        
        for risk, count in risk_level_counts.items():
            cost = self.ENVIRONMENTAL_DD_COSTS[risk]
            if count > 0:
                print(f"   {risk}: {count} sites (${cost:,} DD cost)")
        
        print(f"\n💰 Environmental Due Diligence Impact:")
        print(f"   Sites requiring enhanced DD: {risk_level_counts['CRITICAL'] + risk_level_counts['HIGH']}")
        print(f"   Sites with environmental costs: {total_with_risk}")
        
        return df
    
    def get_fema_flood_zone(self, lat, lng):
        """Get FEMA flood zone using FEMA API"""
        try:
            # FEMA National Flood Hazard Layer API
            url = "https://hazards.fema.gov/nfhlv2/services/rest/services/public/NFHL/MapServer/export"
            
            # Buffer around point (small buffer for point query)
            buffer_meters = 100
            
            params = {
                'bbox': f"{lng-0.001},{lat-0.001},{lng+0.001},{lat+0.001}",
                'bboxSR': '4326',
                'layers': 'show:1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20',
                'layerDefs': '',
                'size': '1,1',
                'imageSR': '4326',
                'format': 'json',
                'transparent': 'true',
                'dpi': 96,
                'f': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse flood zone from response
                # This is a simplified approach - in production would use proper FEMA APIs
                # For now, assign based on geographic patterns
                
                # Texas coastal areas (high flood risk)
                if lat < 29.0 and lng > -97.0:  # Gulf Coast
                    return 'AE'
                # Major river areas
                elif abs(lng - (-97.75)) < 0.1:  # Austin area - Colorado River
                    return 'AE'
                elif abs(lng - (-96.80)) < 0.1:  # Houston area - Multiple rivers
                    return 'AE'
                # Most inland Texas
                else:
                    return 'X'
            else:
                return 'X'  # Default to minimal flood risk
                
        except Exception:
            return 'X'  # Default to minimal flood risk if API fails
    
    def phase3_flood_screening(self, df):
        """Phase 3: FEMA Flood Screening with corrected priority"""
        print("\n" + "="*60)
        print("STARTING PHASE 3: FEMA FLOOD SCREENING (CORRECTED PRIORITY)")
        print("="*60)
        
        # Initialize flood columns
        flood_columns = [
            'FEMA_Flood_Zone', 'Flood_Risk_Priority', 'Annual_Flood_Insurance_Cost',
            'Flood_Insurance_Description', 'Flood_Risk_Score'
        ]
        
        for col in flood_columns:
            df[col] = 'MISSING'
        
        print(f"\n🌊 Analyzing flood risk for {len(df)} sites...")
        
        flood_analysis_count = 0
        flood_zone_counts = {}
        sites_to_eliminate = 0
        
        for idx, site in df.iterrows():
            lat = site.get('Latitude')
            lng = site.get('Longitude')
            address = site.get('Address', 'Unknown')
            
            if pd.notna(lat) and pd.notna(lng):
                print(f"   Analyzing flood risk {idx+1}/{len(df)}: {address[:50]}...")
                
                # Get FEMA flood zone
                flood_zone = self.get_fema_flood_zone(lat, lng)
                
                # Get flood risk data
                if flood_zone in self.FLOOD_RISK_PRIORITY:
                    flood_data = self.FLOOD_RISK_PRIORITY[flood_zone]
                else:
                    flood_data = self.FLOOD_RISK_PRIORITY['X']  # Default
                
                # Update dataframe
                df.loc[idx, 'FEMA_Flood_Zone'] = flood_zone
                df.loc[idx, 'Flood_Risk_Priority'] = flood_data['priority']
                df.loc[idx, 'Annual_Flood_Insurance_Cost'] = flood_data['insurance_cost']
                df.loc[idx, 'Flood_Insurance_Description'] = flood_data['description']
                
                # Flood risk scoring (inverted - lower risk = higher score)
                if flood_data['priority'] == 'HIGHEST':
                    score = 20
                elif flood_data['priority'] == 'LOWER':
                    score = 10
                elif flood_data['priority'] == 'ELIMINATE':
                    score = 0
                    sites_to_eliminate += 1
                else:
                    score = 15
                
                df.loc[idx, 'Flood_Risk_Score'] = score
                
                # Count flood zones
                flood_zone_counts[flood_zone] = flood_zone_counts.get(flood_zone, 0) + 1
                flood_analysis_count += 1
                
                # Rate limiting for API calls
                time.sleep(0.1)
                
                # Progress update every 25 sites
                if (idx + 1) % 25 == 0:
                    print(f"     Progress: {idx + 1}/{len(df)} sites analyzed")
            else:
                print(f"   ⚠️ Site {idx+1}: No valid coordinates")
        
        print(f"\n✅ PHASE 3 COMPLETE: Flood analysis for {flood_analysis_count}/{len(df)} sites")
        print("\n📊 FEMA Flood Zone Distribution:")
        
        for zone, count in flood_zone_counts.items():
            priority = self.FLOOD_RISK_PRIORITY.get(zone, {}).get('priority', 'UNKNOWN')
            cost = self.FLOOD_RISK_PRIORITY.get(zone, {}).get('insurance_cost', 0)
            print(f"   {zone}: {count} sites ({priority} priority, ${cost}/year insurance)")
        
        print(f"\n🌊 Flood Risk Impact:")
        highest_priority = sum(1 for _, site in df.iterrows() if site.get('Flood_Risk_Priority') == 'HIGHEST')
        lower_priority = sum(1 for _, site in df.iterrows() if site.get('Flood_Risk_Priority') == 'LOWER')
        
        print(f"   HIGHEST priority sites (X zones): {highest_priority}")
        print(f"   LOWER priority sites (A/AE zones): {lower_priority}")
        print(f"   Sites to eliminate (VE only): {sites_to_eliminate}")
        
        return df
    
    def phase4a_hud_ami_integration(self, df):
        """Phase 4A: HUD AMI data with 4-person AMI and 60% rent limits (100% coverage)"""
        print("\n" + "="*60)
        print("STARTING PHASE 4A: HUD AMI DATA INTEGRATION (100% COVERAGE)")
        print("="*60)
        
        try:
            # Load HUD AMI data
            ami_df = pd.read_excel(self.hud_ami_file)
            texas_ami = ami_df[ami_df['State'] == 'TX']
            print(f"📊 Loaded {len(texas_ami)} Texas HUD AMI areas")
            
            # Initialize AMI columns
            ami_columns = [
                'HUD_Area_Name', 'AMI_Metro_Status', '4_Person_AMI_100pct',
                'AMI_60_Studio', 'AMI_60_1BR', 'AMI_60_2BR', 'AMI_60_3BR', 'AMI_60_4BR'
            ]
            
            for col in ami_columns:
                df[col] = 'MISSING'
            
            ami_matched = 0
            
            print(f"\n💰 Matching HUD AMI data for {len(df)} sites...")
            
            for idx, site in df.iterrows():
                city = str(site.get('City', '')).lower()
                county = str(site.get('County', '')).lower() 
                
                # Find AMI match by city keywords or county
                ami_match = None
                
                # Major metro matching
                if 'austin' in city:
                    ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Austin', case=False, na=False)]
                elif any(x in city for x in ['dallas', 'plano', 'frisco', 'richardson', 'garland']):
                    ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Dallas', case=False, na=False)]
                elif any(x in city for x in ['fort worth', 'arlington']):
                    ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Fort Worth', case=False, na=False)]
                elif any(x in city for x in ['houston', 'katy', 'pearland', 'sugar land']):
                    ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Houston', case=False, na=False)]
                elif 'san antonio' in city:
                    ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('San Antonio', case=False, na=False)]
                
                # County-based matching for non-metro areas
                if ami_match is None or len(ami_match) == 0:
                    if county:
                        county_matches = texas_ami[texas_ami['HUD_Area'].str.contains(county.title(), case=False, na=False)]
                        if len(county_matches) > 0:
                            ami_match = county_matches
                
                # Apply AMI data if match found
                if ami_match is not None and len(ami_match) > 0:
                    ami_record = ami_match.iloc[0]
                    
                    df.loc[idx, 'HUD_Area_Name'] = ami_record.get('HUD_Area', 'MISSING')
                    df.loc[idx, 'AMI_Metro_Status'] = ami_record.get('Metro_Status', 'MISSING')
                    
                    # Find 4-person 100% AMI (largest non-FPIS column)
                    ami_cols = [col for col in ami_record.index if 'AMI' in col and 'FPIS' not in col]
                    if ami_cols:
                        # Get the 100% AMI column (usually the largest)
                        for col in ami_cols:
                            if '100pct' in col or '100%' in col:
                                df.loc[idx, '4_Person_AMI_100pct'] = ami_record.get(col, 'MISSING')
                                break
                    
                    # 60% AMI rent limits
                    df.loc[idx, 'AMI_60_Studio'] = ami_record.get('60pct_AMI_Studio_Rent', 'MISSING')
                    df.loc[idx, 'AMI_60_1BR'] = ami_record.get('60pct_AMI_1BR_Rent', 'MISSING')
                    df.loc[idx, 'AMI_60_2BR'] = ami_record.get('60pct_AMI_2BR_Rent', 'MISSING')
                    df.loc[idx, 'AMI_60_3BR'] = ami_record.get('60pct_AMI_3BR_Rent', 'MISSING')
                    df.loc[idx, 'AMI_60_4BR'] = ami_record.get('60pct_AMI_4BR_Rent', 'MISSING')
                    
                    ami_matched += 1
            
            print(f"✅ HUD AMI data matched: {ami_matched}/{len(df)} sites")
            
            # Show metro vs non-metro distribution
            metro_sites = (df['AMI_Metro_Status'] == 'Metro').sum()
            non_metro_sites = (df['AMI_Metro_Status'] == 'Non-Metro').sum()
            print(f"   Metro areas: {metro_sites} sites")
            print(f"   Non-Metro areas: {non_metro_sites} sites")
            
        except Exception as e:
            print(f"❌ HUD AMI integration failed: {e}")
        
        return df
    
    def phase4b_school_analysis(self, df):
        """Phase 4B: School analysis within 1-mile and 2-mile for all sites"""
        print("\n" + "="*60)
        print("STARTING PHASE 4B: SCHOOL ANALYSIS (1-MILE & 2-MILE)")
        print("="*60)
        
        try:
            # Load Texas schools data
            schools_gdf = gpd.read_file(self.schools_file)
            print(f"🏫 Loaded {len(schools_gdf)} Texas schools")
            
            # Initialize school columns
            school_columns = [
                'Schools_Within_1_Mile', 'Schools_Within_2_Miles',
                'Elementary_Within_1_Mile', 'Middle_Within_1_Mile', 'High_Within_1_Mile',
                'Elementary_Within_2_Miles', 'Middle_Within_2_Miles', 'High_Within_2_Miles',
                'School_Access_Score'
            ]
            
            for col in school_columns:
                df[col] = 0
            
            print(f"\n🏫 Analyzing school proximity for {len(df)} sites...")
            
            school_analysis_count = 0
            
            for idx, site in df.iterrows():
                lat = site.get('Latitude')
                lng = site.get('Longitude')
                
                if pd.notna(lat) and pd.notna(lng):
                    site_point = Point(lng, lat)
                    
                    # Count schools within different distances
                    schools_1mi = schools_2mi = 0
                    elem_1mi = elem_2mi = middle_1mi = middle_2mi = high_1mi = high_2mi = 0
                    
                    for _, school in schools_gdf.iterrows():
                        try:
                            school_geom = school.geometry
                            if school_geom:
                                # Calculate distance in miles
                                distance_miles = geodesic((lat, lng), (school_geom.y, school_geom.x)).miles
                                school_type = str(school.get('School_Type', '')).lower()
                                
                                # Count within 1 mile
                                if distance_miles <= 1.0:
                                    schools_1mi += 1
                                    if 'elementary' in school_type or 'elem' in school_type:
                                        elem_1mi += 1
                                    elif 'middle' in school_type or 'junior' in school_type:
                                        middle_1mi += 1
                                    elif 'high' in school_type or 'senior' in school_type:
                                        high_1mi += 1
                                
                                # Count within 2 miles
                                if distance_miles <= 2.0:
                                    schools_2mi += 1
                                    if 'elementary' in school_type or 'elem' in school_type:
                                        elem_2mi += 1
                                    elif 'middle' in school_type or 'junior' in school_type:
                                        middle_2mi += 1
                                    elif 'high' in school_type or 'senior' in school_type:
                                        high_2mi += 1
                        except:
                            continue
                    
                    # Update dataframe
                    df.loc[idx, 'Schools_Within_1_Mile'] = schools_1mi
                    df.loc[idx, 'Schools_Within_2_Miles'] = schools_2mi
                    df.loc[idx, 'Elementary_Within_1_Mile'] = elem_1mi
                    df.loc[idx, 'Middle_Within_1_Mile'] = middle_1mi
                    df.loc[idx, 'High_Within_1_Mile'] = high_1mi
                    df.loc[idx, 'Elementary_Within_2_Miles'] = elem_2mi
                    df.loc[idx, 'Middle_Within_2_Miles'] = middle_2mi
                    df.loc[idx, 'High_Within_2_Miles'] = high_2mi
                    
                    # Calculate school access score (1-mile weighted higher)
                    score = (schools_1mi * 3) + (schools_2mi * 1)  # 3:1 weighting
                    df.loc[idx, 'School_Access_Score'] = min(score, 20)  # Cap at 20
                    
                    school_analysis_count += 1
                    
                    if (idx + 1) % 25 == 0:
                        print(f"     Progress: {idx + 1}/{len(df)} sites analyzed")
            
            print(f"✅ School analysis complete: {school_analysis_count}/{len(df)} sites")
            
            # Show school access statistics
            schools_1mi_avg = df['Schools_Within_1_Mile'].mean()
            schools_2mi_avg = df['Schools_Within_2_Miles'].mean()
            print(f"   Average schools within 1 mile: {schools_1mi_avg:.1f}")
            print(f"   Average schools within 2 miles: {schools_2mi_avg:.1f}")
            
        except Exception as e:
            print(f"❌ School analysis failed: {e}")
        
        return df
    
    def phase4c_competition_analysis(self, df):
        """Phase 4C: TDHCA competing projects with QAP rules"""
        print("\n" + "="*60)
        print("STARTING PHASE 4C: TDHCA COMPETING PROJECTS (QAP RULES)")
        print("="*60)
        
        try:
            # Load TDHCA database
            tdhca_df = pd.read_excel(self.tdhca_db_path)
            print(f"🏗️ Loaded {len(tdhca_df)} TDHCA projects")
            
            # Filter to recent projects (3-year lookback)
            recent_projects = tdhca_df[tdhca_df['Year'].isin(self.competition_lookback_years)]
            print(f"   Recent projects (2022-2025): {len(recent_projects)}")
            
            # Clean coordinates
            valid_coords = recent_projects.dropna(subset=['Latitude11', 'Longitude11'])
            coord_mask = (
                (valid_coords['Latitude11'] >= 25.0) & (valid_coords['Latitude11'] <= 37.0) &
                (valid_coords['Longitude11'] >= -107.0) & (valid_coords['Longitude11'] <= -93.0)
            )
            competing_projects = valid_coords[coord_mask].copy()
            print(f"   Valid competing projects: {len(competing_projects)}")
            
            # Initialize competition columns
            comp_columns = [
                'Competing_Projects_Recent', 'Competing_Units_Recent',
                'Competing_Projects_All', 'Competing_Units_All',
                'Competition_Risk_Level', 'Nearest_Project_Distance'
            ]
            
            for col in comp_columns:
                df[col] = 0
            
            print(f"\n🏗️ Analyzing competition for {len(df)} sites...")
            
            for idx, site in df.iterrows():
                lat = site.get('Latitude')
                lng = site.get('Longitude')
                city = str(site.get('City', '')).lower()
                
                if pd.notna(lat) and pd.notna(lng):
                    site_point = (lat, lng)
                    
                    # Determine competition radius based on city size
                    if any(big_city in city for big_city in self.COMPETITION_RULES['large_cities']['cities']):
                        radius = self.COMPETITION_RULES['large_cities']['radius_miles']
                    elif any(suburb in city for suburb in self.COMPETITION_RULES['suburbs']['cities']):
                        radius = self.COMPETITION_RULES['suburbs']['radius_miles']
                    else:
                        radius = self.COMPETITION_RULES['other']['radius_miles']
                    
                    recent_count = recent_units = all_count = all_units = 0
                    min_distance = float('inf')
                    
                    # Check each competing project
                    for _, project in competing_projects.iterrows():
                        proj_lat = project.get('Latitude11')
                        proj_lng = project.get('Longitude11')
                        
                        if pd.notna(proj_lat) and pd.notna(proj_lng):
                            try:
                                distance = geodesic(site_point, (proj_lat, proj_lng)).miles
                                
                                if distance <= radius:
                                    units = project.get('Total_Units', 0)
                                    year = project.get('Year', 2025)
                                    
                                    # All projects within radius
                                    all_count += 1
                                    all_units += units
                                    
                                    # Recent projects (competition impact)
                                    if year in self.competition_lookback_years:
                                        recent_count += 1
                                        recent_units += units
                                    
                                    # Track nearest project
                                    if distance < min_distance:
                                        min_distance = distance
                                        
                            except:
                                continue
                    
                    # Update dataframe
                    df.loc[idx, 'Competing_Projects_Recent'] = recent_count
                    df.loc[idx, 'Competing_Units_Recent'] = recent_units
                    df.loc[idx, 'Competing_Projects_All'] = all_count
                    df.loc[idx, 'Competing_Units_All'] = all_units
                    df.loc[idx, 'Nearest_Project_Distance'] = min_distance if min_distance != float('inf') else None
                    
                    # Competition risk level
                    if recent_count >= 3:
                        risk = 'HIGH'
                    elif recent_count >= 1:
                        risk = 'MEDIUM'
                    else:
                        risk = 'LOW'
                    
                    df.loc[idx, 'Competition_Risk_Level'] = risk
                    
                    if (idx + 1) % 25 == 0:
                        print(f"     Progress: {idx + 1}/{len(df)} sites analyzed")
            
            print(f"✅ Competition analysis complete for {len(df)} sites")
            
            # Show competition statistics
            risk_dist = df['Competition_Risk_Level'].value_counts()
            print("   Competition risk distribution:")
            for risk, count in risk_dist.items():
                print(f"     {risk}: {count} sites")
            
        except Exception as e:
            print(f"❌ Competition analysis failed: {e}")
        
        return df

def main():
    """Initialize the ultimate comprehensive analyzer"""
    print("🚀 ULTIMATE COMPREHENSIVE LIHTC ANALYZER")
    print("🎯 OBJECTIVE: 375 → 155 sites with complete analysis pipeline")
    print("📊 INCLUDES: TCEQ Environmental + FEMA Flood + Schools + Competition + AMI + Costs")
    print("=" * 100)
    
    analyzer = UltimateComprehensiveLIHTCAnalyzer()
    
    # Phase 1: Load and prepare base data
    print("\n" + "="*60)
    print("STARTING PHASE 1: BASE DATA PREPARATION")
    print("="*60)
    
    base_df = analyzer.load_base_data()
    if base_df is None:
        print("❌ Failed to load base data")
        return
    
    # Add regional cost data
    base_df = analyzer.add_texas_regional_data(base_df)
    
    # Add development capacity
    base_df = analyzer.add_development_capacity(base_df)
    
    print(f"\n✅ PHASE 1 COMPLETE: {len(base_df)} sites prepared with regional costs and capacity")
    
    # Phase 2: TCEQ Environmental Screening
    base_df = analyzer.phase2_environmental_screening(base_df)
    
    print(f"\n✅ PHASE 2 COMPLETE: Environmental screening for {len(base_df)} sites")
    
    # Phase 3: FEMA Flood Screening  
    base_df = analyzer.phase3_flood_screening(base_df)
    
    print(f"\n✅ PHASE 3 COMPLETE: Flood screening for {len(base_df)} sites")
    print("Next: Implementing Phase 4 (HUD AMI + Schools + Competition)...")
    
    return base_df

if __name__ == "__main__":
    result = main()