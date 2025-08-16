#!/usr/bin/env python3
"""
Phase 2: Highway Access Screening for Flood-Viable Sites
Priority 2 - Eliminate sites isolated from major roads
"""

import pandas as pd
import geopandas as gpd
import json
from datetime import datetime
from pathlib import Path
from shapely.geometry import Point
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

class Phase2HighwayAccessScreener:
    """Screen flood-viable sites for highway access - eliminate isolated sites"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
        self.data_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Data_Sets/texas")
        
        # Input: Viable sites from flood screening  
        self.flood_screened_file = None  # Will be set to latest flood screening result
        
        # Texas highway datasets
        self.highway_datasets = {
            'interstate': self.data_dir / 'TxDOT_Roadways/texas_interstate_highways.gpkg',
            'us_highways': self.data_dir / 'TxDOT_Roadways/texas_us_highway_highways.gpkg', 
            'major_highways': self.data_dir / 'TxDOT_Roadways/texas_major_highways.gpkg',
            'state_highways': self.data_dir / 'TxDOT_Roadways/texas_state_highway_highways.gpkg'
        }
        
        # Distance thresholds for highway access (miles)
        self.ACCESS_THRESHOLDS = {
            'excellent': 0.5,    # Within 1/2 mile of major highway
            'good': 1.0,         # Within 1 mile
            'fair': 2.0,         # Within 2 miles  
            'poor': 3.0,         # Within 3 miles
            'isolated': 999      # Beyond 3 miles - ELIMINATE
        }
        
        # Highway importance weighting (for scoring when multiple highway types present)
        self.HIGHWAY_WEIGHTS = {
            'interstate': 100,      # Interstates are most important
            'us_highways': 80,      # US highways  
            'major_highways': 60,   # Major state highways
            'state_highways': 40    # Other state highways
        }
        
        # Sites beyond this distance get flagged for elimination
        self.ELIMINATION_DISTANCE = 3.0  # miles
    
    def find_latest_flood_screening_file(self):
        """Find the latest flood screening results file"""
        results_dir = self.base_dir / "D'Marco_Sites/Analysis_Results"
        
        # Look for latest Phase2_Flood_Screened_Sites file
        flood_files = list(results_dir.glob("Phase2_Flood_Screened_Sites_*.xlsx"))
        
        if not flood_files:
            print("❌ No flood screening results found!")
            return None
        
        # Get the most recent file
        latest_file = max(flood_files, key=lambda x: x.stat().st_mtime)
        self.flood_screened_file = latest_file
        
        print(f"📊 Using flood screening results: {latest_file.name}")
        return latest_file
    
    def load_viable_sites_from_flood_screening(self):
        """Load viable sites from flood screening results"""
        if not self.find_latest_flood_screening_file():
            return None
        
        print(f"📊 Loading viable sites from: {self.flood_screened_file}")
        
        # Load the "Viable_Sites_After_Flood" sheet
        try:
            df = pd.read_excel(self.flood_screened_file, sheet_name='Viable_Sites_After_Flood')
            print(f"✅ Loaded {len(df)} flood-viable sites for highway screening")
            
            # Verify coordinate columns exist
            if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
                print("❌ Missing coordinate columns in flood screening results")
                return None
            
            # Check for valid coordinates
            valid_coords = df[(df['Latitude'].notna()) & (df['Longitude'].notna()) & 
                            (df['Latitude'] != 0) & (df['Longitude'] != 0)]
            print(f"✅ Sites with valid coordinates: {len(valid_coords)}/{len(df)}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading viable sites: {e}")
            return None
    
    def load_highway_datasets(self):
        """Load Texas highway datasets"""
        print("🛣️ LOADING TEXAS HIGHWAY DATASETS")
        
        loaded_highways = {}
        
        for highway_type, file_path in self.highway_datasets.items():
            if file_path.exists():
                try:
                    gdf = gpd.read_file(file_path)
                    
                    # Ensure WGS84 for distance calculations
                    if gdf.crs != 'EPSG:4326':
                        gdf = gdf.to_crs('EPSG:4326')
                    
                    loaded_highways[highway_type] = gdf
                    print(f"  ✅ {highway_type}: {len(gdf)} highway segments loaded")
                    
                except Exception as e:
                    print(f"  ❌ Error loading {highway_type}: {e}")
            else:
                print(f"  ⚠️ {highway_type}: File not found - {file_path}")
        
        if not loaded_highways:
            print("❌ No highway datasets loaded! Cannot proceed with screening.")
            return None
        
        return loaded_highways
    
    def find_nearest_highway(self, site_lat, site_lng, highway_gdfs):
        """Find nearest highway of any type to the site"""
        site_point = Point(site_lng, site_lat)
        
        nearest_highways = []
        
        for highway_type, highway_gdf in highway_gdfs.items():
            min_distance = float('inf')
            closest_highway = None
            
            for idx, highway in highway_gdf.iterrows():
                try:
                    # Calculate distance to highway geometry
                    if highway.geometry.geom_type in ['LineString', 'MultiLineString']:
                        # For line geometries, find closest point on line
                        closest_point_on_line = highway.geometry.interpolate(
                            highway.geometry.project(site_point)
                        )
                        highway_coords = (closest_point_on_line.y, closest_point_on_line.x)
                    else:
                        # For other geometries, use centroid
                        centroid = highway.geometry.centroid
                        highway_coords = (centroid.y, centroid.x)
                    
                    # Calculate distance in miles
                    distance = geodesic((site_lat, site_lng), highway_coords).miles
                    
                    if distance < min_distance:
                        min_distance = distance
                        closest_highway = {
                            'highway_type': highway_type,
                            'distance_miles': round(distance, 2),
                            'name': highway.get('ROUTE_NAME', highway.get('ROADWAY', highway.get('NAME', 'Unnamed'))),
                            'weight': self.HIGHWAY_WEIGHTS.get(highway_type, 50),
                            'coordinates': highway_coords
                        }
                
                except Exception as e:
                    continue
            
            if closest_highway:
                nearest_highways.append(closest_highway)
        
        # Return the closest highway overall (by distance, then by importance weight)
        if nearest_highways:
            # Sort by distance first, then by weight (higher weight = more important)
            nearest_highways.sort(key=lambda x: (x['distance_miles'], -x['weight']))
            return nearest_highways[0]
        
        return None
    
    def classify_highway_access(self, nearest_highway):
        """Classify highway access level"""
        if not nearest_highway:
            return {
                'access_level': 'isolated',
                'eliminate_flag': True,
                'score': 0,
                'description': 'No major highways found within search radius'
            }
        
        distance = nearest_highway['distance_miles']
        
        if distance <= self.ACCESS_THRESHOLDS['excellent']:
            access_level = 'excellent'
            score = 25
            eliminate_flag = False
        elif distance <= self.ACCESS_THRESHOLDS['good']:
            access_level = 'good'
            score = 20
            eliminate_flag = False
        elif distance <= self.ACCESS_THRESHOLDS['fair']:
            access_level = 'fair'
            score = 15
            eliminate_flag = False
        elif distance <= self.ACCESS_THRESHOLDS['poor']:
            access_level = 'poor'
            score = 10
            eliminate_flag = False
        else:
            access_level = 'isolated'
            score = 0
            eliminate_flag = True
        
        return {
            'access_level': access_level,
            'eliminate_flag': eliminate_flag,
            'score': score,
            'description': f'{distance:.2f} miles to {nearest_highway["highway_type"]} ({nearest_highway["name"]})'
        }
    
    def screen_highway_access(self, df, highway_gdfs):
        """Screen all viable sites for highway access"""
        print("\n🛣️ SCREENING HIGHWAY ACCESS FOR ALL VIABLE SITES")
        print("=" * 60)
        
        # Initialize highway access columns
        df['nearest_highway_type'] = ''
        df['nearest_highway_name'] = ''
        df['nearest_highway_distance'] = 0.0
        df['highway_access_level'] = ''
        df['highway_access_score'] = 0
        df['highway_eliminate_flag'] = False
        df['highway_access_description'] = ''
        
        elimination_count = 0
        viable_count = 0
        
        for idx, row in df.iterrows():
            site_id = idx
            lat = row['Latitude']
            lng = row['Longitude']
            address = row.get('Address', 'Unknown')
            
            # Skip sites with invalid coordinates
            if pd.isna(lat) or pd.isna(lng) or lat == 0 or lng == 0:
                print(f"🏠 Site {site_id:3d}: {address[:45]:45} - SKIPPING (No coordinates)")
                df.at[idx, 'highway_eliminate_flag'] = False  # Don't eliminate for missing coords
                df.at[idx, 'highway_access_description'] = 'No coordinates available'
                viable_count += 1
                continue
            
            # Find nearest highway
            nearest_highway = self.find_nearest_highway(lat, lng, highway_gdfs)
            
            # Classify access level
            access_classification = self.classify_highway_access(nearest_highway)
            
            # Update DataFrame
            if nearest_highway:
                df.at[idx, 'nearest_highway_type'] = nearest_highway['highway_type']
                df.at[idx, 'nearest_highway_name'] = nearest_highway['name']
                df.at[idx, 'nearest_highway_distance'] = nearest_highway['distance_miles']
            
            df.at[idx, 'highway_access_level'] = access_classification['access_level']
            df.at[idx, 'highway_access_score'] = access_classification['score']
            df.at[idx, 'highway_eliminate_flag'] = access_classification['eliminate_flag']
            df.at[idx, 'highway_access_description'] = access_classification['description']
            
            # Count results
            if access_classification['eliminate_flag']:
                elimination_count += 1
                print(f"🚫 Site {site_id:3d}: {address[:40]:40} | {access_classification['access_level']:10} | ELIMINATE - {access_classification['description']}")
            else:
                viable_count += 1  
                print(f"✅ Site {site_id:3d}: {address[:40]:40} | {access_classification['access_level']:10} | VIABLE - {access_classification['description']}")
        
        print(f"\n📊 HIGHWAY ACCESS SCREENING COMPLETE:")
        print(f"   🚫 Sites flagged for elimination: {elimination_count} ({elimination_count/len(df)*100:.1f}%)")
        print(f"   ✅ Viable sites after highway screening: {viable_count} ({viable_count/len(df)*100:.1f}%)")
        
        return df, elimination_count, viable_count
    
    def create_highway_analysis_summary(self, df):
        """Create detailed highway access analysis summary"""
        
        # Access level distribution
        access_distribution = df['highway_access_level'].value_counts().to_dict()
        
        # Highway type distribution
        highway_type_distribution = df['nearest_highway_type'].value_counts().to_dict()
        
        # Distance statistics
        distances = df[df['nearest_highway_distance'] > 0]['nearest_highway_distance']
        
        if len(distances) > 0:
            distance_stats = {
                'average_distance': round(distances.mean(), 2),
                'min_distance': round(distances.min(), 2),
                'max_distance': round(distances.max(), 2),
                'median_distance': round(distances.median(), 2)
            }
        else:
            distance_stats = {'average_distance': 0, 'min_distance': 0, 'max_distance': 0, 'median_distance': 0}
        
        # Elimination analysis
        eliminated_sites = df[df['highway_eliminate_flag'] == True]
        viable_sites = df[df['highway_eliminate_flag'] == False]
        
        # Geographic distribution
        eliminated_by_city = eliminated_sites['City'].value_counts().to_dict() if len(eliminated_sites) > 0 else {}
        viable_by_city = viable_sites['City'].value_counts().to_dict()
        
        summary = {
            'analysis_date': datetime.now().isoformat(),
            'input_source': 'Flood-viable sites from Phase 2 flood screening',
            'total_sites_analyzed': len(df),
            'elimination_results': {
                'sites_flagged_for_elimination': len(eliminated_sites),
                'viable_sites_remaining': len(viable_sites),
                'elimination_rate_percent': round(len(eliminated_sites)/len(df)*100, 1)
            },
            'access_level_distribution': access_distribution,
            'highway_type_distribution': highway_type_distribution,
            'distance_statistics': distance_stats,
            'geographic_distribution': {
                'eliminated_sites_by_city': eliminated_by_city,
                'viable_sites_by_city': viable_by_city
            },
            'screening_criteria': {
                'excellent_access': f'≤ {self.ACCESS_THRESHOLDS["excellent"]} miles',
                'good_access': f'≤ {self.ACCESS_THRESHOLDS["good"]} miles',
                'fair_access': f'≤ {self.ACCESS_THRESHOLDS["fair"]} miles', 
                'poor_access': f'≤ {self.ACCESS_THRESHOLDS["poor"]} miles',
                'isolated_elimination_threshold': f'> {self.ELIMINATION_DISTANCE} miles',
                'highway_importance_ranking': 'Interstate > US Highways > Major Highways > State Highways'
            }
        }
        
        return summary
    
    def save_highway_screening_results(self, df, summary):
        """Save highway access screening results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save enhanced Excel with highway screening
        excel_file = self.base_dir / f"D'Marco_Sites/Analysis_Results/Phase2_Highway_Screened_Sites_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # All sites with highway analysis  
            df.to_excel(writer, sheet_name='All_Sites_Highway_Analysis', index=False)
            
            # Final viable sites (survived both flood AND highway screening)
            final_viable = df[df['highway_eliminate_flag'] == False]
            final_viable.to_excel(writer, sheet_name='Final_Viable_Sites', index=False)
            print(f"✅ Final viable sites: {len(final_viable)} sites")
            
            # Highway eliminated sites
            highway_eliminated = df[df['highway_eliminate_flag'] == True]
            if len(highway_eliminated) > 0:
                highway_eliminated.to_excel(writer, sheet_name='Eliminated_Poor_Highway_Access', index=False)
                print(f"🚫 Highway eliminated sites: {len(highway_eliminated)} sites")
            
            # Access level summary
            access_summary = df['highway_access_level'].value_counts().reset_index()
            access_summary.columns = ['Access_Level', 'Site_Count']
            access_summary.to_excel(writer, sheet_name='Access_Level_Summary', index=False)
            
            # Best access sites (excellent + good)
            best_access = df[df['highway_access_level'].isin(['excellent', 'good'])]
            if len(best_access) > 0:
                best_access.to_excel(writer, sheet_name='Best_Highway_Access_Sites', index=False)
        
        # Save summary JSON
        summary_file = self.base_dir / f"D'Marco_Sites/Analysis_Results/Phase2_Highway_Screening_Summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 HIGHWAY SCREENING RESULTS SAVED:")
        print(f"   📊 Excel analysis: {excel_file.name}")
        print(f"   📋 Summary report: {summary_file.name}")
        
        return excel_file, summary_file, final_viable
    
    def run_highway_screening(self):
        """Run complete highway access screening"""
        print("🛣️ PHASE 2: HIGHWAY ACCESS SCREENING")
        print("🎯 OBJECTIVE: Eliminate sites isolated from major roads")
        print("=" * 80)
        
        # Load flood-viable sites
        df = self.load_viable_sites_from_flood_screening()
        if df is None:
            print("❌ Could not load flood-viable sites")
            return None
        
        # Load highway datasets
        highway_gdfs = self.load_highway_datasets()
        if highway_gdfs is None:
            print("❌ Could not load highway datasets")
            return None
        
        # Screen highway access
        enhanced_df, elimination_count, viable_count = self.screen_highway_access(df, highway_gdfs)
        
        # Create analysis summary
        summary = self.create_highway_analysis_summary(enhanced_df)
        
        # Save results
        excel_file, summary_file, final_viable_sites = self.save_highway_screening_results(enhanced_df, summary)
        
        print("\n" + "=" * 80)
        print("🛣️ HIGHWAY ACCESS SCREENING COMPLETE!")
        print("=" * 80)
        print(f"📊 Flood-viable sites analyzed: {summary['total_sites_analyzed']}")
        print(f"🚫 Poor highway access (eliminated): {summary['elimination_results']['sites_flagged_for_elimination']}")
        print(f"✅ Final viable sites: {summary['elimination_results']['viable_sites_remaining']}")
        print(f"📈 Overall success rate: {100-summary['elimination_results']['elimination_rate_percent']:.1f}% sites have good highway access")
        print(f"🎯 Average distance to nearest highway: {summary['distance_statistics']['average_distance']} miles")
        
        return {
            'success': True,
            'excel_file': str(excel_file),
            'summary_file': str(summary_file),
            'final_viable_count': summary['elimination_results']['viable_sites_remaining'],
            'highway_elimination_count': summary['elimination_results']['sites_flagged_for_elimination'],
            'final_viable_sites_df': final_viable_sites,
            'summary': summary
        }

if __name__ == "__main__":
    screener = Phase2HighwayAccessScreener()
    results = screener.run_highway_screening()
    
    if results and results['success']:
        print(f"\n🎯 READY FOR DETAILED ANALYSIS: {results['final_viable_count']} sites passed both flood and highway screening")
        print(f"💾 Final results: {results['excel_file']}")
        print(f"\n📋 NEXT STEPS: Run AMI analysis, competition screening, and environmental assessment on final viable sites")
    else:
        print("\n❌ Highway screening failed")