#!/usr/bin/env python3
"""
Texas Complete County Downloader
Downloads all remaining Texas counties to achieve 100% geometry coverage
"""

import requests
import geopandas as gpd
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import time
import os

class TexasCompleteDownloader:
    def __init__(self):
        self.api_base = "https://msc.fema.gov/arcgis/rest/services/NFHL_Print/NFHL/MapServer/14"
        self.base_dir = Path("./state_flood_data")
        self.tx_dir = self.base_dir / 'TX'
        self.county_dir = self.tx_dir / 'county_downloads'
        self.county_dir.mkdir(parents=True, exist_ok=True)
        
        # Track progress
        self.progress_file = self.tx_dir / 'download_progress.json'
        self.load_progress()
        
        # Counties already downloaded (from previous runs)
        self.downloaded_counties = {
            # Houston Metro
            '48201', '48157', '48339', '48039', '48167', '48291', '48473', '48015',
            # Dallas (partial)
            '48113',
            # San Antonio Area  
            '48029', '48091', '48187', '48013', '48493', '48325',
            # Austin Central
            '48453', '48491', '48055', '48209', '48027', '48099', '48053',
            # South Texas
            '48061', '48215', '48479', '48355', '48469', '48131',
            # East Texas
            '48001', '48183', '48213', '48423', '48347', '48073', '48405', '48203', '48249', '48315',
            # West Texas counties
            '48141', '48329', '48135', '48303', '48375', '48381', '48441', '48451',
            # North Texas counties
            '48181', '48231', '48485', '48077', '48139', '48143',
            # Southeast Texas counties
            '48245', '48361', '48123', '48239', '48285'
        }
        
        # Priority counties (DFW that failed)
        self.priority_counties = {
            '48439': 'Tarrant',      # Fort Worth
            '48085': 'Collin',       # Plano
            '48121': 'Denton',
            '48397': 'Rockwall',
            '48251': 'Johnson',
            '48367': 'Parker',
            '48257': 'Kaufman',
        }
    
    def load_progress(self):
        """Load download progress from file"""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                'completed': [],
                'failed': [],
                'in_progress': None,
                'last_updated': None
            }
    
    def save_progress(self):
        """Save download progress to file"""
        self.progress['last_updated'] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def get_all_missing_counties(self):
        """Get all counties that need to be downloaded"""
        # Load attributes data to get all counties
        csv_file = self.tx_dir / 'processed' / 'TX_flood_zones_attributes.csv'
        if not csv_file.exists():
            print("❌ TX attributes file not found!")
            return []
        
        df = pd.read_csv(csv_file)
        df['County_FIPS'] = df['DFIRM_ID'].str[:5]
        
        # Get zone counts for each county
        county_stats = df.groupby('County_FIPS').agg({
            'FLD_ZONE': 'count',
            'SFHA_TF': lambda x: (x == 'T').sum()
        }).rename(columns={'FLD_ZONE': 'total_zones', 'SFHA_TF': 'high_risk_zones'})
        
        # Find missing counties
        all_counties = set(county_stats.index)
        completed = set(self.downloaded_counties) | set(self.progress['completed'])
        missing = all_counties - completed - set(self.progress['failed'])
        
        # Create list with zone counts
        missing_list = []
        for fips in missing:
            if fips in county_stats.index:
                missing_list.append({
                    'fips': fips,
                    'zones': county_stats.loc[fips, 'total_zones'],
                    'high_risk': county_stats.loc[fips, 'high_risk_zones']
                })
        
        # Sort by zone count (largest first)
        missing_list.sort(key=lambda x: x['zones'], reverse=True)
        
        return missing_list
    
    def download_county(self, county_fips: str, county_name: str = None, expected_zones: int = None):
        """Download a single county's flood data"""
        if county_name is None:
            county_name = county_fips
        
        print(f"\n📥 Downloading {county_name} ({county_fips})...")
        
        # Mark as in progress
        self.progress['in_progress'] = county_fips
        self.save_progress()
        
        # Get record count
        params = {
            'where': f"DFIRM_ID LIKE '{county_fips}%'",
            'returnCountOnly': 'true',
            'f': 'json'
        }
        
        try:
            response = requests.get(f"{self.api_base}/query", params=params, timeout=15)
            if response.status_code != 200:
                raise Exception(f"Count query failed: HTTP {response.status_code}")
            
            total_records = response.json().get('count', 0)
            print(f"   Total records: {total_records:,}")
            
            if total_records == 0:
                print(f"   ⚠️ No records found")
                return True  # Not a failure, just no data
            
            # Determine chunk size based on county size
            if total_records > 5000:
                chunk_size = 500
            elif total_records > 1000:
                chunk_size = 1000
            else:
                chunk_size = 2000
            
            all_features = []
            num_chunks = (total_records + chunk_size - 1) // chunk_size
            
            # Download chunks
            for chunk_num in range(num_chunks):
                offset = chunk_num * chunk_size
                
                params = {
                    'where': f"DFIRM_ID LIKE '{county_fips}%'",
                    'outFields': 'DFIRM_ID,FLD_ZONE,ZONE_SUBTY,SFHA_TF,STATIC_BFE,V_DATUM',
                    'returnGeometry': 'true',
                    'geometryPrecision': 6,
                    'outSR': '4326',
                    'resultOffset': offset,
                    'resultRecordCount': chunk_size,
                    'f': 'geojson'
                }
                
                # Retry logic
                for attempt in range(3):
                    try:
                        print(f"   Chunk {chunk_num + 1}/{num_chunks}...", end='')
                        response = requests.get(f"{self.api_base}/query", params=params, timeout=45)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if 'features' in data and data['features']:
                                chunk_features = data['features']
                                
                                # Add county info
                                for feature in chunk_features:
                                    feature['properties']['County_FIPS'] = county_fips
                                    feature['properties']['County_Name'] = county_name
                                
                                all_features.extend(chunk_features)
                                print(f" ✅ ({len(chunk_features)} features)")
                                break
                            else:
                                print(f" ⚠️ (no features)")
                                break
                        else:
                            raise Exception(f"HTTP {response.status_code}")
                            
                    except Exception as e:
                        if attempt < 2:
                            print(f" ⚠️ (retry {attempt + 1})")
                            time.sleep(5)
                        else:
                            print(f" ❌ ({e})")
                            
                # Rate limiting
                time.sleep(2)
            
            if all_features:
                # Save county data
                self.save_county_data(county_fips, county_name, all_features)
                print(f"   ✅ Saved {len(all_features):,} features")
                
                # Mark as completed
                self.progress['completed'].append(county_fips)
                self.progress['in_progress'] = None
                self.save_progress()
                
                return True
            else:
                raise Exception("No features downloaded")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            self.progress['failed'].append(county_fips)
            self.progress['in_progress'] = None
            self.save_progress()
            return False
    
    def save_county_data(self, county_fips: str, county_name: str, features: list):
        """Save county data to GeoPackage"""
        county_subdir = self.county_dir / f"{county_fips}_{county_name.replace(' ', '_')}"
        county_subdir.mkdir(exist_ok=True)
        
        # Save GeoJSON first (backup)
        geojson_file = county_subdir / f'{county_fips}_flood_zones.geojson'
        geojson_data = {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "county_fips": county_fips,
                "county_name": county_name,
                "download_date": datetime.now().isoformat(),
                "total_features": len(features)
            }
        }
        
        with open(geojson_file, 'w') as f:
            json.dump(geojson_data, f)
        
        # Save as GeoPackage
        try:
            gdf = gpd.GeoDataFrame.from_features(features, crs='EPSG:4326')
            gdf['State'] = 'TX'
            gdf['Download_Date'] = datetime.now().strftime('%Y-%m-%d')
            
            gpkg_file = county_subdir / f'{county_fips}_flood_zones.gpkg'
            gdf.to_file(gpkg_file, driver='GPKG', layer='flood_hazard_zones')
            
        except Exception as e:
            print(f"   ⚠️ GeoPackage save error: {e}")
    
    def download_priority_counties(self):
        """Download priority DFW counties first"""
        print("\n🎯 Phase 1: Priority Counties (Dallas-Fort Worth)")
        print("="*50)
        
        completed = 0
        for fips, name in self.priority_counties.items():
            if fips not in self.progress['completed'] and fips not in self.downloaded_counties:
                success = self.download_county(fips, name)
                if success:
                    completed += 1
                time.sleep(3)  # Extra delay between counties
        
        print(f"\n✅ Priority counties completed: {completed}/{len(self.priority_counties)}")
        return completed
    
    def download_remaining_counties(self):
        """Download all remaining counties by size"""
        missing = self.get_all_missing_counties()
        
        if not missing:
            print("\n✅ All counties already downloaded!")
            return
        
        # Categorize by size
        large = [c for c in missing if c['zones'] >= 2000]
        medium = [c for c in missing if 500 <= c['zones'] < 2000]
        small = [c for c in missing if c['zones'] < 500]
        
        print(f"\n📊 Remaining counties to download:")
        print(f"   Large (2000+ zones): {len(large)}")
        print(f"   Medium (500-2000 zones): {len(medium)}")
        print(f"   Small (<500 zones): {len(small)}")
        print(f"   Total: {len(missing)} counties, {sum(c['zones'] for c in missing):,} zones")
        
        # Download large counties
        if large:
            print("\n🎯 Phase 2: Large Counties (2000+ zones)")
            print("="*50)
            for county in large:
                self.download_county(county['fips'], expected_zones=county['zones'])
                time.sleep(5)  # Longer delay for large counties
        
        # Download medium counties
        if medium:
            print("\n🎯 Phase 3: Medium Counties (500-2000 zones)")
            print("="*50)
            for county in medium:
                self.download_county(county['fips'], expected_zones=county['zones'])
                time.sleep(3)
        
        # Download small counties in batches
        if small:
            print("\n🎯 Phase 4: Small Counties (<500 zones)")
            print("="*50)
            for county in small:
                self.download_county(county['fips'], expected_zones=county['zones'])
                time.sleep(2)
    
    def merge_all_counties(self):
        """Merge all downloaded counties into existing merged file"""
        print("\n🔨 Merging all county data...")
        
        # Load existing merged file
        merged_file = self.tx_dir / 'processed' / 'TX_flood_zones_merged_geometry.gpkg'
        if merged_file.exists():
            print("   Loading existing merged data...")
            merged_gdf = gpd.read_file(merged_file)
            existing_count = len(merged_gdf)
            print(f"   Existing features: {existing_count:,}")
        else:
            merged_gdf = None
            existing_count = 0
        
        # Find all county GeoPackages
        all_gdfs = []
        if merged_gdf is not None:
            all_gdfs.append(merged_gdf)
        
        # Add newly downloaded counties
        new_features = 0
        for county_dir in self.county_dir.iterdir():
            if county_dir.is_dir():
                gpkg_files = list(county_dir.glob("*.gpkg"))
                if gpkg_files:
                    try:
                        gdf = gpd.read_file(gpkg_files[0])
                        all_gdfs.append(gdf)
                        new_features += len(gdf)
                        print(f"   Added {county_dir.name}: {len(gdf):,} features")
                    except Exception as e:
                        print(f"   ❌ Error loading {county_dir.name}: {e}")
        
        if len(all_gdfs) > 1 or (len(all_gdfs) == 1 and new_features > 0):
            print(f"\n   Merging {len(all_gdfs)} datasets...")
            final_gdf = gpd.GeoDataFrame(pd.concat(all_gdfs, ignore_index=True))
            
            # Save complete file
            complete_file = self.tx_dir / 'processed' / 'TX_flood_zones_complete.gpkg'
            final_gdf.to_file(complete_file, driver='GPKG', layer='flood_hazard_zones')
            
            print(f"\n✅ Complete Texas GeoPackage created: {complete_file}")
            print(f"   Total features: {len(final_gdf):,} (added {len(final_gdf) - existing_count:,})")
            
            # Create final summary
            self.create_final_summary(final_gdf)
            
            return complete_file
        else:
            print("\n⚠️ No new data to merge")
            return None
    
    def create_final_summary(self, gdf: gpd.GeoDataFrame):
        """Create final summary of complete Texas data"""
        zone_summary = gdf['FLD_ZONE'].value_counts()
        
        high_risk_zones = ['A', 'AE', 'AH', 'AO', 'V', 'VE']
        high_risk_count = gdf[gdf['FLD_ZONE'].isin(high_risk_zones)].shape[0]
        moderate_risk_count = gdf[gdf['FLD_ZONE'] == 'X'].shape[0]
        
        # Count unique counties
        if 'County_FIPS' in gdf.columns:
            unique_counties = gdf['County_FIPS'].nunique()
        else:
            unique_counties = gdf['DFIRM_ID'].str[:5].nunique()
        
        summary = {
            'state': 'Texas',
            'state_code': 'TX',
            'data_type': 'Complete County Geometry',
            'total_flood_zones': len(gdf),
            'high_risk_zones': high_risk_count,
            'moderate_risk_zones': moderate_risk_count,
            'zone_breakdown': zone_summary.to_dict(),
            'counties_included': unique_counties,
            'completion_date': datetime.now().isoformat()
        }
        
        summary_file = self.tx_dir / 'TX_complete_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Final Texas Summary:")
        print(f"   Total zones: {len(gdf):,}")
        print(f"   Counties: {unique_counties}")
        print(f"   High Risk: {high_risk_count:,} ({high_risk_count/len(gdf)*100:.1f}%)")
        print(f"   Moderate Risk: {moderate_risk_count:,} ({moderate_risk_count/len(gdf)*100:.1f}%)")
    
    def run_complete_download(self):
        """Run the complete download process"""
        print("\n" + "="*70)
        print("TEXAS COMPLETE COUNTY DOWNLOADER")
        print("="*70)
        print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check for resumed download
        if self.progress['in_progress']:
            print(f"\n⚠️ Resuming from county: {self.progress['in_progress']}")
        
        # Download priority counties first
        self.download_priority_counties()
        
        # Download all remaining counties
        self.download_remaining_counties()
        
        # Merge everything
        complete_file = self.merge_all_counties()
        
        print("\n" + "="*70)
        print("DOWNLOAD COMPLETE!")
        print("="*70)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if complete_file:
            print(f"\n✅ Complete Texas flood data saved to:")
            print(f"   {complete_file}")


if __name__ == "__main__":
    downloader = TexasCompleteDownloader()
    downloader.run_complete_download()