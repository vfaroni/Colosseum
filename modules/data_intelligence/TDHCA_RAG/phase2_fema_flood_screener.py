#!/usr/bin/env python3
"""
Phase 2: FEMA Flood Zone Screening for 155 Qualified Sites
Priority 1 - Eliminate high-risk flood sites before detailed analysis
"""

import pandas as pd
import requests
import time
import json
from datetime import datetime
from pathlib import Path

class Phase2FEMAFloodScreener:
    """Screen 155 qualified sites for flood risk - eliminate high-risk sites first"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
        
        # Input: MASTER file with 155 qualified sites
        self.master_file = self.base_dir / "D'Marco_Sites/Analysis_Results/MASTER_155_BoostEligible_Sites_20250731_223500.xlsx"
        
        # FEMA flood zone risk levels - high risk sites get eliminated
        self.flood_risk_levels = {
            'A': 'HIGH_RISK',      # 1% annual chance flood zone
            'AE': 'HIGH_RISK',     # 1% annual chance with BFE
            'AH': 'HIGH_RISK',     # 1% annual chance shallow flooding
            'AO': 'HIGH_RISK',     # 1% annual chance sheet flow
            'AR': 'HIGH_RISK',     # 1% annual chance with restored studies
            'V': 'VERY_HIGH_RISK', # 1% annual chance coastal
            'VE': 'VERY_HIGH_RISK',# 1% annual chance coastal with BFE
            'X': 'LOW_RISK',       # Outside 1% and 0.2% flood zones
            'X500': 'MODERATE_RISK', # 0.2% annual chance (500-year)
            'D': 'UNDETERMINED'    # Undetermined flood hazard
        }
        
        # Sites in HIGH_RISK and VERY_HIGH_RISK zones will be flagged for elimination/lower priority
        self.elimination_zones = ['HIGH_RISK', 'VERY_HIGH_RISK']
        
    def load_master_sites(self):
        """Load the 155 qualified sites from MASTER Excel file"""
        print(f"📊 Loading MASTER file: {self.master_file}")
        
        try:
            df = pd.read_excel(self.master_file)
            print(f"✅ Loaded {len(df)} qualified sites")
            print(f"📋 Columns available: {list(df.columns)[:10]}...")  # Show first 10 columns
            
            # Use known coordinate column names
            lat_col = 'Latitude'
            lng_col = 'Longitude'
            
            if lat_col not in df.columns or lng_col not in df.columns:
                print("❌ Could not find Latitude/Longitude columns")
                print(f"Available columns: {list(df.columns)}")
                return None
            
            print(f"📍 Using coordinates: {lat_col}, {lng_col}")
            
            # Check for valid coordinates
            valid_coords = df[(df[lat_col].notna()) & (df[lng_col].notna()) & 
                            (df[lat_col] != 0) & (df[lng_col] != 0)]
            print(f"✅ Sites with valid coordinates: {len(valid_coords)}/{len(df)}")
            return df, lat_col, lng_col
            
        except Exception as e:
            print(f"❌ Error loading MASTER file: {e}")
            return None
    
    def get_fema_flood_zone(self, lat, lng, site_id):
        """Get FEMA flood zone using FEMA NFHL REST API"""
        try:
            # FEMA Web Map Service endpoint
            base_url = "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer"
            identify_url = f"{base_url}/identify"
            
            params = {
                'geometry': f'{lng},{lat}',
                'geometryType': 'esriGeometryPoint',
                'sr': '4326',
                'layers': 'all:28',  # NFHL Flood Zones layer
                'tolerance': '0',
                'mapExtent': f'{lng-0.01},{lat-0.01},{lng+0.01},{lat+0.01}',
                'imageDisplay': '400,400,96',
                'returnGeometry': 'false',
                'f': 'json'
            }
            
            response = requests.get(identify_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'results' in data and len(data['results']) > 0:
                    # Get first result with flood zone
                    result = data['results'][0]
                    attributes = result.get('attributes', {})
                    
                    flood_zone = attributes.get('FLD_ZONE', attributes.get('ZONE', 'X'))
                    risk_level = self.flood_risk_levels.get(flood_zone, 'UNKNOWN')
                    
                    return {
                        'site_id': site_id,
                        'flood_zone': flood_zone,
                        'risk_level': risk_level,
                        'eliminate_flag': risk_level in self.elimination_zones,  
                        'data_source': 'FEMA_NFHL_API',
                        'status': 'SUCCESS'
                    }
                else:
                    # No flood data found - assume Zone X (low risk)
                    return {
                        'site_id': site_id,
                        'flood_zone': 'X', 
                        'risk_level': 'LOW_RISK',
                        'eliminate_flag': False,
                        'data_source': 'FEMA_DEFAULT_LOW_RISK',
                        'status': 'NO_DATA_ASSUMED_SAFE'
                    }
            
            return None
            
        except Exception as e:
            print(f"⚠️ FEMA API error for site {site_id} ({lat}, {lng}): {e}")
            return None
    
    def screen_all_sites(self, df, lat_col, lng_col):
        """Screen all 155 sites for flood risk"""
        print("\n🌊 SCREENING ALL 155 SITES FOR FLOOD ZONES")
        print("=" * 60)
        
        flood_results = []
        elimination_count = 0
        viable_count = 0
        
        for idx, row in df.iterrows():
            site_id = idx  # Use DataFrame index as site ID
            lat = row[lat_col]
            lng = row[lng_col]
            address = row.get('Address', 'Unknown')
            
            # Skip sites with invalid coordinates
            if pd.isna(lat) or pd.isna(lng) or lat == 0 or lng == 0:
                print(f"🏠 Site {site_id}: {address[:50]}... - SKIPPING (No valid coordinates)")
                flood_results.append({
                    'site_id': site_id,
                    'flood_zone': 'NO_COORDINATES',
                    'risk_level': 'UNKNOWN', 
                    'eliminate_flag': False,
                    'data_source': 'NO_COORDINATES',
                    'status': 'SKIPPED_NO_COORDS'
                })
                viable_count += 1
                continue
            
            print(f"🏠 Site {site_id}: {address[:50]}...")
            print(f"   📍 Coordinates: {lat:.4f}, {lng:.4f}")
            
            # Get flood zone
            flood_data = self.get_fema_flood_zone(lat, lng, site_id)
            
            if flood_data:
                flood_results.append(flood_data)
                
                # Display result
                zone = flood_data['flood_zone']
                risk = flood_data['risk_level'] 
                eliminate = flood_data['eliminate_flag']
                
                if eliminate:
                    print(f"   🚫 ELIMINATE: Zone {zone} ({risk}) - High flood risk!")
                    elimination_count += 1
                else:
                    print(f"   ✅ VIABLE: Zone {zone} ({risk})")
                    viable_count += 1
            else:
                # API failed - assume moderate risk, don't eliminate
                flood_results.append({
                    'site_id': site_id,
                    'flood_zone': 'UNKNOWN',
                    'risk_level': 'UNKNOWN', 
                    'eliminate_flag': False,
                    'data_source': 'API_FAILED',
                    'status': 'FAILED_ASSUME_VIABLE'
                })
                print(f"   ⚠️ API FAILED: Assuming viable (don't eliminate)")
                viable_count += 1
            
            # Rate limiting - be nice to FEMA API
            time.sleep(1.0)
        
        print(f"\n📊 FLOOD SCREENING COMPLETE:")
        print(f"   🚫 Sites to eliminate: {elimination_count}")
        print(f"   ✅ Viable sites: {viable_count}")
        print(f"   🎯 Elimination rate: {elimination_count/len(df)*100:.1f}%")
        
        return flood_results
    
    def create_screening_results(self, df, flood_results):
        """Create screening results with elimination recommendations"""
        
        # Convert flood results to DataFrame for merging
        flood_df = pd.DataFrame(flood_results)
        
        # Add flood data to original DataFrame using index
        df['site_id_merge'] = df.index
        flood_df['site_id_merge'] = flood_df['site_id']
        
        # Merge flood data
        enhanced_df = df.merge(flood_df[['site_id_merge', 'flood_zone', 'risk_level', 'eliminate_flag', 'data_source', 'status']], 
                              on='site_id_merge', how='left')
        
        # Create summary statistics
        total_sites = len(enhanced_df)
        eliminate_sites = len(enhanced_df[enhanced_df['eliminate_flag'] == True])
        viable_sites = total_sites - eliminate_sites
        
        # Risk level distribution
        risk_distribution = enhanced_df['risk_level'].value_counts().to_dict()
        zone_distribution = enhanced_df['flood_zone'].value_counts().to_dict()
        
        summary = {
            'analysis_date': datetime.now().isoformat(),
            'total_sites_analyzed': total_sites,
            'sites_recommended_for_elimination': eliminate_sites,
            'viable_sites_remaining': viable_sites,  
            'elimination_rate_percent': round((eliminate_sites/total_sites)*100, 1),
            'flood_risk_distribution': risk_distribution,
            'flood_zone_distribution': zone_distribution,
            'elimination_criteria': {
                'high_risk_zones': ['A', 'AE', 'AH', 'AO', 'AR'],
                'very_high_risk_zones': ['V', 'VE'],
                'insurance_cost_impact': 'High risk zones require $1,500-3,000/unit annual flood insurance'
            }
        }
        
        return enhanced_df, summary
    
    def save_screening_results(self, enhanced_df, summary):
        """Save flood screening results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save enhanced data with flood screening
        excel_file = self.base_dir / f"D'Marco_Sites/Analysis_Results/Phase2_Flood_Screened_Sites_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # All sites with flood analysis
            enhanced_df.to_excel(writer, sheet_name='All_Sites_Flood_Analysis', index=False)
            
            # Viable sites (recommended to keep)
            viable_sites = enhanced_df[enhanced_df['eliminate_flag'] != True]
            viable_sites.to_excel(writer, sheet_name='Viable_Sites_After_Flood', index=False)
            
            # Eliminated sites (high flood risk)
            eliminated_sites = enhanced_df[enhanced_df['eliminate_flag'] == True]
            if len(eliminated_sites) > 0:
                eliminated_sites.to_excel(writer, sheet_name='Eliminated_High_Flood_Risk', index=False)
            
            # Summary statistics
            summary_df = pd.DataFrame([summary])
            summary_df.to_excel(writer, sheet_name='Flood_Screening_Summary', index=False)
        
        # Save summary JSON
        summary_file = self.base_dir / f"D'Marco_Sites/Analysis_Results/Phase2_Flood_Screening_Summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 FLOOD SCREENING RESULTS SAVED:")
        print(f"   📊 Excel analysis: {excel_file.name}")
        print(f"   📋 Summary report: {summary_file.name}")
        print(f"   ✅ Viable sites for next phase: {summary['viable_sites_remaining']}")
        
        return excel_file, summary_file, viable_sites
    
    def run_flood_screening(self):
        """Run complete flood screening analysis"""
        print("🌊 PHASE 2: FEMA FLOOD SCREENING - 155 QUALIFIED SITES")
        print("🎯 OBJECTIVE: Eliminate high-risk flood sites before detailed analysis")
        print("=" * 80)
        
        # Load sites
        site_data = self.load_master_sites()
        if not site_data:
            print("❌ Could not load MASTER sites file")
            return None
        
        df, lat_col, lng_col = site_data
        
        # Screen all sites for flood risk
        flood_results = self.screen_all_sites(df, lat_col, lng_col)
        
        # Create screening results  
        enhanced_df, summary = self.create_screening_results(df, flood_results)
        
        # Save results
        excel_file, summary_file, viable_sites = self.save_screening_results(enhanced_df, summary)
        
        print("\n" + "=" * 80)
        print("🌊 FLOOD SCREENING PHASE COMPLETE!")
        print("=" * 80)
        print(f"📊 Original sites: {summary['total_sites_analyzed']}")
        print(f"🚫 High flood risk (eliminate): {summary['sites_recommended_for_elimination']}")
        print(f"✅ Viable sites remaining: {summary['viable_sites_remaining']}")
        print(f"📈 Sites saved from elimination: {summary['viable_sites_remaining']} ({100-summary['elimination_rate_percent']:.1f}%)")
        
        return {
            'success': True,
            'excel_file': str(excel_file),
            'summary_file': str(summary_file),
            'viable_sites_count': summary['viable_sites_remaining'],
            'elimination_count': summary['sites_recommended_for_elimination'],
            'summary': summary
        }

if __name__ == "__main__":
    screener = Phase2FEMAFloodScreener()
    results = screener.run_flood_screening()
    
    if results and results['success']:
        print(f"\n🎯 NEXT PHASE: Highway access screening on {results['viable_sites_count']} flood-viable sites")
        print(f"💾 Results saved to: {results['excel_file']}")
    else:
        print("\n❌ Flood screening failed")