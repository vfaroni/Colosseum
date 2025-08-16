#!/usr/bin/env python3
"""
Texas FEMA Data Solutions - Handle Large Dataset
"""

import requests
import geopandas as gpd
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import time

class TexasFEMADownloader:
    def __init__(self):
        self.api_base = "https://msc.fema.gov/arcgis/rest/services/NFHL_Print/NFHL/MapServer/14"
        self.base_dir = Path("./state_flood_data")
        
        # Major Texas counties for targeted download
        self.major_tx_counties = {
            '48201': 'Harris',        # Houston
            '48029': 'Bexar',         # San Antonio  
            '48113': 'Dallas',        # Dallas
            '48439': 'Tarrant',       # Fort Worth
            '48453': 'Travis',        # Austin
            '48085': 'Collin',        # Plano
            '48121': 'Denton',        # Denton
            '48157': 'Fort Bend',     # Sugar Land
            '48339': 'Montgomery',    # The Woodlands
            '48491': 'Williamson',    # Round Rock
        }
    
    def solution_1_county_by_county(self):
        """Download major Texas counties individually"""
        print("🏗️ Solution 1: Download Major Texas Counties")
        
        all_features = []
        successful_counties = []
        
        for fips, county_name in self.major_tx_counties.items():
            print(f"\n📥 Downloading {county_name} County ({fips})...")
            
            params = {
                'where': f"DFIRM_ID LIKE '{fips}%'",
                'outFields': 'DFIRM_ID,FLD_ZONE,ZONE_SUBTY,SFHA_TF,STATIC_BFE',
                'returnGeometry': 'true',
                'outSR': '4326',
                'f': 'geojson'
            }
            
            try:
                response = requests.get(f"{self.api_base}/query", params=params, timeout=45)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'features' in data and data['features']:
                        county_features = data['features']
                        
                        # Add county info to each feature
                        for feature in county_features:
                            feature['properties']['County_FIPS'] = fips
                            feature['properties']['County_Name'] = county_name
                        
                        all_features.extend(county_features)
                        successful_counties.append(county_name)
                        print(f"   ✅ {len(county_features):,} flood zones downloaded")
                    else:
                        print(f"   ⚠️ No flood zones found")
                        
                else:
                    print(f"   ❌ Failed: HTTP {response.status_code}")
                    
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        if all_features:
            # Save major counties data
            self.save_texas_data(all_features, "TX_major_counties")
            print(f"\n✅ Downloaded {len(all_features):,} flood zones from {len(successful_counties)} counties")
            return all_features
        else:
            print("\n❌ No data downloaded")
            return []
    
    def solution_2_attributes_only(self):
        """Download all Texas data without geometry (fast)"""
        print("\n🏗️ Solution 2: Download All Texas Attributes (No Geometry)")
        
        # Get total count
        count_params = {
            'where': "DFIRM_ID LIKE '48%'",
            'returnCountOnly': 'true',
            'f': 'json'
        }
        
        response = requests.get(f"{self.api_base}/query", params=count_params, timeout=15)
        if response.status_code != 200:
            print("❌ Failed to get record count")
            return []
        
        total_records = response.json().get('count', 0)
        print(f"   Total Texas records: {total_records:,}")
        
        # Download in chunks without geometry
        chunk_size = 2000
        all_records = []
        
        for offset in range(0, total_records, chunk_size):
            print(f"   📥 Downloading records {offset:,} - {min(offset + chunk_size, total_records):,}")
            
            params = {
                'where': "DFIRM_ID LIKE '48%'",
                'outFields': 'DFIRM_ID,FLD_ZONE,ZONE_SUBTY,SFHA_TF,STATIC_BFE,V_DATUM,SOURCE_CIT',
                'returnGeometry': 'false',  # No geometry - much faster
                'resultOffset': offset,
                'resultRecordCount': chunk_size,
                'f': 'json'
            }
            
            try:
                response = requests.get(f"{self.api_base}/query", params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'features' in data:
                        records = [f['attributes'] for f in data['features']]
                        all_records.extend(records)
                        print(f"   ✅ Downloaded {len(records)} records")
                    else:
                        print(f"   ⚠️ No records in chunk")
                else:
                    print(f"   ❌ Chunk failed: HTTP {response.status_code}")
                    
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        if all_records:
            # Save as CSV and Excel
            df = pd.DataFrame(all_records)
            df['State'] = 'TX'
            df['Download_Date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Save files
            csv_file = self.base_dir / 'TX' / 'processed' / 'TX_flood_zones_attributes.csv'
            xlsx_file = self.base_dir / 'TX' / 'processed' / 'TX_flood_zones_attributes.xlsx'
            
            df.to_csv(csv_file, index=False)
            df.to_excel(xlsx_file, index=False)
            
            print(f"\n✅ Saved {len(all_records):,} Texas records")
            print(f"   CSV: {csv_file}")
            print(f"   Excel: {xlsx_file}")
            
            # Create summary
            self.create_texas_summary(df)
            
            return all_records
        else:
            print("\n❌ No records downloaded")
            return []
    
    def solution_3_small_chunks(self):
        """Download Texas with very small geometry chunks"""
        print("\n🏗️ Solution 3: Download Texas in Very Small Chunks (50 records each)")
        
        # Get total count
        count_params = {
            'where': "DFIRM_ID LIKE '48%'",
            'returnCountOnly': 'true', 
            'f': 'json'
        }
        
        response = requests.get(f"{self.api_base}/query", params=count_params, timeout=15)
        total_records = response.json().get('count', 0)
        
        print(f"   Total records: {total_records:,}")
        print(f"   Estimated download time: {total_records/50*2/60:.1f} minutes")
        
        chunk_size = 50  # Very small chunks
        max_chunks = 20  # Limit for testing
        
        all_features = []
        
        for i in range(min(max_chunks, total_records // chunk_size)):
            offset = i * chunk_size
            print(f"   📥 Chunk {i+1}/{max_chunks}: records {offset} - {offset + chunk_size}")
            
            params = {
                'where': "DFIRM_ID LIKE '48%'",
                'outFields': 'DFIRM_ID,FLD_ZONE,ZONE_SUBTY,SFHA_TF',
                'returnGeometry': 'true',
                'geometryPrecision': 4,  # Lower precision
                'outSR': '4326',
                'resultOffset': offset,
                'resultRecordCount': chunk_size,
                'f': 'geojson'
            }
            
            try:
                response = requests.get(f"{self.api_base}/query", params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'features' in data:
                        all_features.extend(data['features'])
                        print(f"   ✅ Downloaded {len(data['features'])} features")
                    else:
                        print(f"   ⚠️ No features")
                else:
                    print(f"   ❌ Failed: HTTP {response.status_code}")
                    break
                    
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                break
        
        if all_features:
            self.save_texas_data(all_features, "TX_sample_geometry")
            print(f"\n✅ Downloaded {len(all_features):,} features as sample")
            return all_features
        else:
            print("\n❌ No features downloaded")
            return []
    
    def save_texas_data(self, features, suffix=""):
        """Save Texas features to files"""
        tx_dir = self.base_dir / 'TX'
        
        # Save GeoJSON
        geojson_file = tx_dir / 'raw_data' / f'TX_flood_zones_{suffix}.geojson'
        geojson_data = {
            "type": "FeatureCollection", 
            "features": features,
            "metadata": {
                "source": "FEMA NFHL via ArcGIS REST API",
                "download_date": datetime.now().isoformat(),
                "state": "Texas",
                "total_features": len(features)
            }
        }
        
        with open(geojson_file, 'w') as f:
            json.dump(geojson_data, f)
        
        # Save GeoPackage
        try:
            gdf = gpd.GeoDataFrame.from_features(features, crs='EPSG:4326')
            gdf['State'] = 'TX'
            gdf['Download_Date'] = datetime.now().strftime('%Y-%m-%d')
            
            gpkg_file = tx_dir / 'processed' / f'TX_flood_zones_{suffix}.gpkg'
            gdf.to_file(gpkg_file, driver='GPKG', layer='flood_hazard_zones')
            
            print(f"   💾 Saved: {gpkg_file}")
            return gpkg_file
            
        except Exception as e:
            print(f"   ❌ Error saving GeoPackage: {e}")
            return geojson_file
    
    def create_texas_summary(self, df):
        """Create summary for Texas attributes data"""
        tx_dir = self.base_dir / 'TX'
        
        zone_summary = df['FLD_ZONE'].value_counts()
        
        high_risk_zones = ['A', 'AE', 'AH', 'AO', 'V', 'VE']
        high_risk_count = df[df['FLD_ZONE'].isin(high_risk_zones)].shape[0]
        moderate_risk_count = df[df['FLD_ZONE'] == 'X'].shape[0]
        sfha_count = df[df['SFHA_TF'] == 'T'].shape[0]
        
        summary = {
            'state': 'Texas',
            'state_code': 'TX',
            'total_flood_zones': len(df),
            'high_risk_zones': high_risk_count,
            'moderate_risk_zones': moderate_risk_count,
            'sfha_zones': sfha_count,
            'zone_breakdown': zone_summary.to_dict(),
            'download_date': datetime.now().isoformat(),
            'data_source': 'FEMA NFHL via ArcGIS REST API (Attributes Only)'
        }
        
        summary_file = tx_dir / 'TX_flood_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Texas Flood Zone Summary:")
        print(f"   Total zones: {len(df):,}")
        print(f"   High Risk: {high_risk_count:,} ({high_risk_count/len(df)*100:.1f}%)")
        print(f"   Moderate Risk: {moderate_risk_count:,} ({moderate_risk_count/len(df)*100:.1f}%)")
        print(f"   SFHA zones: {sfha_count:,} ({sfha_count/len(df)*100:.1f}%)")


if __name__ == "__main__":
    downloader = TexasFEMADownloader()
    
    print("🎯 Texas FEMA Data Download Solutions")
    print("="*50)
    print("1. Major Counties Only (with geometry)")
    print("2. All Texas Attributes (no geometry) - RECOMMENDED")
    print("3. Small Sample with Geometry")
    
    # Recommended approach
    print("\n🚀 Running Solution 2 (All Attributes)...")
    downloader.solution_2_attributes_only()