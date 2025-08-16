#!/usr/bin/env python3
"""
Texas Geographic Downloader - Download Texas FEMA data by geographic regions
Break Texas into manageable chunks and download geometry data separately
"""

import requests
import geopandas as gpd
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import time
import math

class TexasGeographicDownloader:
    def __init__(self):
        self.api_base = "https://msc.fema.gov/arcgis/rest/services/NFHL_Print/NFHL/MapServer/14"
        self.base_dir = Path("./state_flood_data")
        self.tx_dir = self.base_dir / 'TX' / 'geographic_regions'
        self.tx_dir.mkdir(parents=True, exist_ok=True)
        
        # Texas geographic regions based on major metropolitan areas
        self.texas_regions = {
            'East_Texas': {
                'name': 'East Texas',
                'counties': [
                    '48001',  # Anderson
                    '48183',  # Gregg (Longview)
                    '48213',  # Henderson
                    '48423',  # Smith (Tyler)
                    '48347',  # Nacogdoches
                    '48073',  # Cherokee
                    '48405',  # Rusk
                    '48203',  # Harrison
                    '48249',  # Jim Wells
                    '48315',  # Marion
                ],
                'description': 'Tyler, Longview, Marshall area'
            },
            'Houston_Metro': {
                'name': 'Houston Metropolitan Area',
                'counties': [
                    '48201',  # Harris (Houston)
                    '48157',  # Fort Bend (Sugar Land)
                    '48339',  # Montgomery (The Woodlands)
                    '48039',  # Brazoria (Pearland)
                    '48167',  # Galveston
                    '48291',  # Liberty
                    '48473',  # Waller
                    '48015',  # Austin (not Austin city)
                ],
                'description': 'Houston, Sugar Land, The Woodlands, Galveston'
            },
            'Dallas_Fort_Worth': {
                'name': 'Dallas-Fort Worth Metroplex',
                'counties': [
                    '48113',  # Dallas
                    '48439',  # Tarrant (Fort Worth)
                    '48085',  # Collin (Plano)
                    '48121',  # Denton
                    '48397',  # Rockwall
                    '48251',  # Johnson
                    '48367',  # Parker
                    '48257',  # Kaufman
                ],
                'description': 'Dallas, Fort Worth, Plano, Denton'
            },
            'Austin_Central': {
                'name': 'Austin-Central Texas',
                'counties': [
                    '48453',  # Travis (Austin)
                    '48491',  # Williamson (Round Rock)
                    '48055',  # Caldwell
                    '48209',  # Hays (San Marcos)
                    '48027',  # Bell (Killeen)
                    '48099',  # Coryell
                    '48053',  # Burnet
                ],
                'description': 'Austin, Round Rock, San Marcos, Killeen'
            },
            'San_Antonio': {
                'name': 'San Antonio Area',
                'counties': [
                    '48029',  # Bexar (San Antonio)
                    '48091',  # Comal (New Braunfels)
                    '48187',  # Guadalupe
                    '48013',  # Atascosa
                    '48493',  # Wilson
                    '48325',  # Medina
                ],
                'description': 'San Antonio, New Braunfels'
            },
            'South_Texas': {
                'name': 'South Texas',
                'counties': [
                    '48094',  # Cameron (Brownsville)
                    '48215',  # Hidalgo (McAllen)
                    '48479',  # Webb (Laredo)
                    '48355',  # Nueces (Corpus Christi)
                    '48469',  # Victoria
                    '48131',  # Duval
                ],
                'description': 'Brownsville, McAllen, Laredo, Corpus Christi'
            },
            'West_Texas': {
                'name': 'West Texas',
                'counties': [
                    '48141',  # El Paso
                    '48329',  # Midland
                    '48135',  # Ector (Odessa)
                    '48303',  # Lubbock
                    '48375',  # Potter (Amarillo)
                    '48381',  # Randall (Canyon)
                    '48441',  # Taylor (Abilene)
                    '48451',  # Tom Green (San Angelo)
                ],
                'description': 'El Paso, Midland, Odessa, Lubbock, Amarillo'
            },
            'North_Texas': {
                'name': 'North Texas',
                'counties': [
                    '48181',  # Grayson (Sherman)
                    '48231',  # Hunt
                    '48485',  # Wichita (Wichita Falls)
                    '48077',  # Clay
                    '48139',  # Ellis
                    '48143',  # Erath
                ],
                'description': 'Sherman, Wichita Falls area'
            },
            'Southeast_Texas': {
                'name': 'Southeast Texas (Golden Triangle)',
                'counties': [
                    '48245',  # Jefferson (Beaumont)
                    '48361',  # Orange
                    '48123',  # DeWitt
                    '48239',  # Jackson
                    '48285',  # Lavaca
                ],
                'description': 'Beaumont, Port Arthur, Orange'
            }
        }
    
    def get_region_record_count(self, region_counties: list) -> int:
        """Get total record count for a region"""
        # Create WHERE clause for multiple counties
        county_conditions = [f"DFIRM_ID LIKE '{county}%'" for county in region_counties]
        where_clause = " OR ".join(county_conditions)
        
        params = {
            'where': f"({where_clause})",
            'returnCountOnly': 'true',
            'f': 'json'
        }
        
        try:
            response = requests.get(f"{self.api_base}/query", params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return data.get('count', 0)
        except Exception as e:
            print(f"Error getting count: {e}")
            return 0
        
        return 0
    
    def download_region_geometry(self, region_key: str, region_info: dict) -> bool:
        """Download geometry data for a specific region"""
        region_name = region_info['name']
        counties = region_info['counties']
        
        print(f"\n🏗️ Downloading {region_name}")
        print(f"   Counties: {len(counties)}")
        print(f"   Description: {region_info['description']}")
        
        # Get record count
        total_records = self.get_region_record_count(counties)
        print(f"   Total records: {total_records:,}")
        
        if total_records == 0:
            print(f"   ⚠️ No records found for {region_name}")
            return False
        
        if total_records > 20000:
            print(f"   ⚠️ Region too large ({total_records:,} records), skipping geometry download")
            return False
        
        # Create WHERE clause
        county_conditions = [f"DFIRM_ID LIKE '{county}%'" for county in counties]
        where_clause = " OR ".join(county_conditions)
        
        all_features = []
        chunk_size = 1000  # Smaller chunks for geometry
        num_chunks = math.ceil(total_records / chunk_size)
        
        print(f"   Downloading in {num_chunks} chunks...")
        
        for chunk_num in range(num_chunks):
            offset = chunk_num * chunk_size
            
            params = {
                'where': f"({where_clause})",
                'outFields': 'DFIRM_ID,FLD_ZONE,ZONE_SUBTY,SFHA_TF,STATIC_BFE,V_DATUM,SOURCE_CIT',
                'returnGeometry': 'true',
                'geometryPrecision': 6,
                'outSR': '4326',
                'resultOffset': offset,
                'resultRecordCount': chunk_size,
                'f': 'geojson'
            }
            
            try:
                print(f"   📥 Chunk {chunk_num + 1}/{num_chunks} (offset {offset:,})...")
                
                response = requests.get(f"{self.api_base}/query", params=params, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'features' in data and data['features']:
                        chunk_features = data['features']
                        
                        # Add region info to each feature
                        for feature in chunk_features:
                            feature['properties']['TX_Region'] = region_key
                            feature['properties']['Region_Name'] = region_name
                        
                        all_features.extend(chunk_features)
                        print(f"   ✅ Downloaded {len(chunk_features)} features")
                    else:
                        print(f"   ⚠️ No features in chunk {chunk_num + 1}")
                        
                else:
                    print(f"   ❌ Chunk {chunk_num + 1} failed: HTTP {response.status_code}")
                    
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Error downloading chunk {chunk_num + 1}: {e}")
                continue
        
        if all_features:
            # Save region data
            self.save_region_data(region_key, region_name, all_features)
            print(f"   ✅ Saved {len(all_features):,} features for {region_name}")
            return True
        else:
            print(f"   ❌ No features downloaded for {region_name}")
            return False
    
    def save_region_data(self, region_key: str, region_name: str, features: list):
        """Save region data to files"""
        region_dir = self.tx_dir / region_key
        region_dir.mkdir(exist_ok=True)
        
        # Save GeoJSON
        geojson_file = region_dir / f'{region_key}_flood_zones.geojson'
        geojson_data = {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "FEMA NFHL via ArcGIS REST API",
                "download_date": datetime.now().isoformat(),
                "region": region_name,
                "region_key": region_key,
                "total_features": len(features)
            }
        }
        
        with open(geojson_file, 'w') as f:
            json.dump(geojson_data, f)
        
        # Save GeoPackage
        try:
            gdf = gpd.GeoDataFrame.from_features(features, crs='EPSG:4326')
            
            gpkg_file = region_dir / f'{region_key}_flood_zones.gpkg'
            gdf.to_file(gpkg_file, driver='GPKG', layer='flood_hazard_zones')
            
            print(f"   💾 Saved: {gpkg_file}")
            
            # Create region summary
            self.create_region_summary(region_key, region_name, gdf)
            
        except Exception as e:
            print(f"   ❌ Error saving GeoPackage: {e}")
    
    def create_region_summary(self, region_key: str, region_name: str, gdf: gpd.GeoDataFrame):
        """Create summary for a region"""
        zone_summary = gdf['FLD_ZONE'].value_counts()
        
        high_risk_zones = ['A', 'AE', 'AH', 'AO', 'V', 'VE']
        high_risk_count = gdf[gdf['FLD_ZONE'].isin(high_risk_zones)].shape[0]
        moderate_risk_count = gdf[gdf['FLD_ZONE'] == 'X'].shape[0]
        sfha_count = gdf[gdf['SFHA_TF'] == 'T'].shape[0]
        
        summary = {
            'region': region_name,
            'region_key': region_key,
            'total_flood_zones': len(gdf),
            'high_risk_zones': high_risk_count,
            'moderate_risk_zones': moderate_risk_count,
            'sfha_zones': sfha_count,
            'zone_breakdown': zone_summary.to_dict(),
            'counties_included': gdf['DFIRM_ID'].str[:5].unique().tolist(),
            'download_date': datetime.now().isoformat()
        }
        
        region_dir = self.tx_dir / region_key
        summary_file = region_dir / f'{region_key}_summary.json'
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def download_all_regions(self):
        """Download all Texas regions"""
        print("\n" + "="*70)
        print("TEXAS GEOGRAPHIC REGION DOWNLOADER")
        print("="*70)
        
        successful_regions = []
        failed_regions = []
        
        # First, analyze all regions
        print("\n📊 Analyzing regions...")
        for region_key, region_info in self.texas_regions.items():
            count = self.get_region_record_count(region_info['counties'])
            print(f"   {region_info['name']}: {count:,} records")
            
            if count > 15000:
                print(f"      ⚠️ Large region - may need further subdivision")
        
        # Download each region
        for region_key, region_info in self.texas_regions.items():
            if self.download_region_geometry(region_key, region_info):
                successful_regions.append(region_key)
            else:
                failed_regions.append(region_key)
        
        # Summary
        print(f"\n" + "="*70)
        print("REGIONAL DOWNLOAD COMPLETE!")
        print("="*70)
        
        print(f"\n✅ Successful regions: {len(successful_regions)}")
        for region in successful_regions:
            print(f"   - {self.texas_regions[region]['name']}")
        
        if failed_regions:
            print(f"\n❌ Failed regions: {len(failed_regions)}")
            for region in failed_regions:
                print(f"   - {self.texas_regions[region]['name']}")
        
        return successful_regions, failed_regions
    
    def merge_all_regions(self):
        """Merge all downloaded regional data into a single Texas file"""
        print("\n🔨 Merging all Texas regions...")
        
        all_gdfs = []
        region_files = list(self.tx_dir.glob("*/*/gpkg"))
        
        for region_dir in self.tx_dir.iterdir():
            if region_dir.is_dir():
                gpkg_files = list(region_dir.glob("*.gpkg"))
                if gpkg_files:
                    try:
                        gdf = gpd.read_file(gpkg_files[0])
                        all_gdfs.append(gdf)
                        print(f"   ✅ Loaded {len(gdf):,} features from {region_dir.name}")
                    except Exception as e:
                        print(f"   ❌ Error loading {region_dir.name}: {e}")
        
        if all_gdfs:
            print(f"\n   Merging {len(all_gdfs)} regional datasets...")
            merged_gdf = gpd.GeoDataFrame(pd.concat(all_gdfs, ignore_index=True))
            
            # Save merged file
            merged_file = self.base_dir / 'TX' / 'processed' / 'TX_flood_zones_merged_geometry.gpkg'
            merged_gdf.to_file(merged_file, driver='GPKG', layer='flood_hazard_zones')
            
            print(f"\n✅ Merged Texas GeoPackage created: {merged_file}")
            print(f"   Total features: {len(merged_gdf):,}")
            
            # Create merged summary
            self.create_merged_summary(merged_gdf)
            
            return merged_file
        else:
            print("\n❌ No regional data found to merge")
            return None
    
    def create_merged_summary(self, gdf: gpd.GeoDataFrame):
        """Create summary for merged Texas data"""
        zone_summary = gdf['FLD_ZONE'].value_counts()
        region_summary = gdf['TX_Region'].value_counts()
        
        high_risk_zones = ['A', 'AE', 'AH', 'AO', 'V', 'VE']
        high_risk_count = gdf[gdf['FLD_ZONE'].isin(high_risk_zones)].shape[0]
        moderate_risk_count = gdf[gdf['FLD_ZONE'] == 'X'].shape[0]
        sfha_count = gdf[gdf['SFHA_TF'] == 'T'].shape[0]
        
        summary = {
            'state': 'Texas',
            'state_code': 'TX',
            'data_type': 'Merged Regional Geometry',
            'total_flood_zones': len(gdf),
            'high_risk_zones': high_risk_count,
            'moderate_risk_zones': moderate_risk_count,
            'sfha_zones': sfha_count,
            'zone_breakdown': zone_summary.to_dict(),
            'region_breakdown': region_summary.to_dict(),
            'regions_included': len(region_summary),
            'download_date': datetime.now().isoformat()
        }
        
        summary_file = self.base_dir / 'TX' / 'TX_merged_geometry_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Merged Texas Summary:")
        print(f"   Total zones: {len(gdf):,}")
        print(f"   High Risk: {high_risk_count:,} ({high_risk_count/len(gdf)*100:.1f}%)")
        print(f"   Moderate Risk: {moderate_risk_count:,} ({moderate_risk_count/len(gdf)*100:.1f}%)")
        print(f"   Regions: {len(region_summary)}")


if __name__ == "__main__":
    downloader = TexasGeographicDownloader()
    
    print("🎯 Texas Geographic Region Downloader")
    print("="*50)
    
    # Download all regions
    successful, failed = downloader.download_all_regions()
    
    # Merge if any successful downloads
    if successful:
        merged_file = downloader.merge_all_regions()
        
        print(f"\n🎉 Texas geometric data download complete!")
        if merged_file:
            print(f"✅ Merged file: {merged_file}")
    else:
        print("\n❌ No regions downloaded successfully")