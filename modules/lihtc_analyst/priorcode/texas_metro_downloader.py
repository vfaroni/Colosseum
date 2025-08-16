#!/usr/bin/env python3
"""
Texas Metro Area Downloader - Download Houston and Dallas by individual counties
Then append to existing merged geometry file
"""

import requests
import geopandas as gpd
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import time

class TexasMetroDownloader:
    def __init__(self):
        self.api_base = "https://msc.fema.gov/arcgis/rest/services/NFHL_Print/NFHL/MapServer/14"
        self.base_dir = Path("./state_flood_data")
        self.metro_dir = self.base_dir / 'TX' / 'metro_counties'
        self.metro_dir.mkdir(parents=True, exist_ok=True)
        
        # Break down metro areas by individual counties
        self.metro_counties = {
            'Houston_Metro': {
                '48201': 'Harris',           # Houston - largest
                '48157': 'Fort Bend',        # Sugar Land
                '48339': 'Montgomery',       # The Woodlands
                '48039': 'Brazoria',         # Pearland
                '48167': 'Galveston',        
                '48291': 'Liberty',
                '48473': 'Waller',
                '48015': 'Austin',           # Not Austin city, but Austin County
            },
            'Dallas_Fort_Worth': {
                '48113': 'Dallas',           # Dallas - largest
                '48439': 'Tarrant',          # Fort Worth - second largest
                '48085': 'Collin',           # Plano
                '48121': 'Denton',
                '48397': 'Rockwall',
                '48251': 'Johnson',
                '48367': 'Parker',
                '48257': 'Kaufman',
            }
        }
    
    def get_county_record_count(self, county_fips: str) -> int:
        """Get record count for a single county"""
        params = {
            'where': f"DFIRM_ID LIKE '{county_fips}%'",
            'returnCountOnly': 'true',
            'f': 'json'
        }
        
        try:
            response = requests.get(f"{self.api_base}/query", params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return data.get('count', 0)
        except Exception as e:
            print(f"Error getting count for {county_fips}: {e}")
            return 0
        
        return 0
    
    def download_county_geometry(self, county_fips: str, county_name: str, metro_name: str) -> list:
        """Download geometry for a single county"""
        print(f"\n📥 Downloading {county_name} County ({county_fips})...")
        
        # Get record count
        total_records = self.get_county_record_count(county_fips)
        print(f"   Total records: {total_records:,}")
        
        if total_records == 0:
            print(f"   ⚠️ No records found")
            return []
        
        all_features = []
        chunk_size = 500  # Smaller chunks for reliability
        num_chunks = (total_records + chunk_size - 1) // chunk_size
        
        for chunk_num in range(num_chunks):
            offset = chunk_num * chunk_size
            
            params = {
                'where': f"DFIRM_ID LIKE '{county_fips}%'",
                'outFields': 'DFIRM_ID,FLD_ZONE,ZONE_SUBTY,SFHA_TF,STATIC_BFE,V_DATUM,SOURCE_CIT',
                'returnGeometry': 'true',
                'geometryPrecision': 6,
                'outSR': '4326',
                'resultOffset': offset,
                'resultRecordCount': chunk_size,
                'f': 'geojson'
            }
            
            try:
                print(f"   Chunk {chunk_num + 1}/{num_chunks} (offset {offset:,})...", end='')
                
                response = requests.get(f"{self.api_base}/query", params=params, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'features' in data and data['features']:
                        chunk_features = data['features']
                        
                        # Add county and metro info
                        for feature in chunk_features:
                            feature['properties']['County_FIPS'] = county_fips
                            feature['properties']['County_Name'] = county_name
                            feature['properties']['Metro_Area'] = metro_name
                        
                        all_features.extend(chunk_features)
                        print(f" ✅ ({len(chunk_features)} features)")
                    else:
                        print(f" ⚠️ (no features)")
                        
                else:
                    print(f" ❌ (HTTP {response.status_code})")
                    
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f" ❌ (Error: {e})")
                continue
        
        if all_features:
            # Save county data
            self.save_county_data(county_fips, county_name, metro_name, all_features)
            print(f"   ✅ Total: {len(all_features):,} features saved")
        
        return all_features
    
    def save_county_data(self, county_fips: str, county_name: str, metro_name: str, features: list):
        """Save county data to files"""
        county_dir = self.metro_dir / f"{county_fips}_{county_name.replace(' ', '_')}"
        county_dir.mkdir(exist_ok=True)
        
        # Save GeoJSON
        geojson_file = county_dir / f'{county_fips}_flood_zones.geojson'
        geojson_data = {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "FEMA NFHL via ArcGIS REST API",
                "download_date": datetime.now().isoformat(),
                "county": county_name,
                "county_fips": county_fips,
                "metro_area": metro_name,
                "total_features": len(features)
            }
        }
        
        with open(geojson_file, 'w') as f:
            json.dump(geojson_data, f)
        
        # Save GeoPackage
        try:
            gdf = gpd.GeoDataFrame.from_features(features, crs='EPSG:4326')
            
            gpkg_file = county_dir / f'{county_fips}_flood_zones.gpkg'
            gdf.to_file(gpkg_file, driver='GPKG', layer='flood_hazard_zones')
            
        except Exception as e:
            print(f"   ❌ Error saving GeoPackage: {e}")
    
    def download_metro_area(self, metro_key: str):
        """Download all counties in a metro area"""
        counties = self.metro_counties[metro_key]
        metro_name = metro_key.replace('_', ' ')
        
        print(f"\n🏗️ Downloading {metro_name}")
        print(f"   Counties: {len(counties)}")
        
        all_metro_features = []
        successful_counties = []
        failed_counties = []
        
        for county_fips, county_name in counties.items():
            features = self.download_county_geometry(county_fips, county_name, metro_name)
            
            if features:
                all_metro_features.extend(features)
                successful_counties.append(county_name)
            else:
                failed_counties.append(county_name)
        
        print(f"\n📊 {metro_name} Summary:")
        print(f"   Successful counties: {len(successful_counties)}")
        print(f"   Failed counties: {len(failed_counties)}")
        print(f"   Total features: {len(all_metro_features):,}")
        
        return all_metro_features, successful_counties, failed_counties
    
    def append_to_merged_file(self, new_features: list, metro_name: str):
        """Append new features to existing merged file"""
        merged_file = self.base_dir / 'TX' / 'processed' / 'TX_flood_zones_merged_geometry.gpkg'
        
        if not merged_file.exists():
            print(f"❌ Merged file not found: {merged_file}")
            return False
        
        try:
            print(f"\n🔨 Appending {len(new_features):,} features to merged file...")
            
            # Load existing data
            print("   Loading existing merged data...")
            existing_gdf = gpd.read_file(merged_file)
            existing_count = len(existing_gdf)
            print(f"   Existing features: {existing_count:,}")
            
            # Create GeoDataFrame from new features
            print("   Processing new features...")
            new_gdf = gpd.GeoDataFrame.from_features(new_features, crs='EPSG:4326')
            new_gdf['State'] = 'TX'
            new_gdf['Download_Date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Add region info if not present
            if 'TX_Region' not in new_gdf.columns:
                new_gdf['TX_Region'] = metro_name
            if 'Region_Name' not in new_gdf.columns:
                new_gdf['Region_Name'] = metro_name
            
            # Ensure matching columns
            for col in existing_gdf.columns:
                if col not in new_gdf.columns and col != 'geometry':
                    new_gdf[col] = None
            
            # Match column order
            new_gdf = new_gdf[existing_gdf.columns]
            
            # Append
            print("   Merging datasets...")
            merged_gdf = gpd.GeoDataFrame(
                pd.concat([existing_gdf, new_gdf], ignore_index=True),
                crs=existing_gdf.crs
            )
            
            # Save updated file
            print("   Saving updated merged file...")
            merged_gdf.to_file(merged_file, driver='GPKG', layer='flood_hazard_zones')
            
            new_total = len(merged_gdf)
            print(f"   ✅ Updated merged file: {new_total:,} total features (+{new_total - existing_count:,})")
            
            # Update summary
            self.update_merged_summary(merged_gdf)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error appending to merged file: {e}")
            return False
    
    def update_merged_summary(self, gdf: gpd.GeoDataFrame):
        """Update summary for merged Texas data"""
        zone_summary = gdf['FLD_ZONE'].value_counts()
        
        # Count regions
        if 'TX_Region' in gdf.columns:
            region_summary = gdf['TX_Region'].value_counts()
        else:
            region_summary = pd.Series()
        
        high_risk_zones = ['A', 'AE', 'AH', 'AO', 'V', 'VE']
        high_risk_count = gdf[gdf['FLD_ZONE'].isin(high_risk_zones)].shape[0]
        moderate_risk_count = gdf[gdf['FLD_ZONE'] == 'X'].shape[0]
        
        sfha_count = 0
        if 'SFHA_TF' in gdf.columns:
            sfha_count = gdf[gdf['SFHA_TF'] == 'T'].shape[0]
        
        summary = {
            'state': 'Texas',
            'state_code': 'TX',
            'data_type': 'Merged Regional Geometry (Updated)',
            'total_flood_zones': len(gdf),
            'high_risk_zones': high_risk_count,
            'moderate_risk_zones': moderate_risk_count,
            'sfha_zones': sfha_count,
            'zone_breakdown': zone_summary.to_dict(),
            'region_breakdown': region_summary.to_dict() if len(region_summary) > 0 else {},
            'regions_included': len(region_summary),
            'last_updated': datetime.now().isoformat()
        }
        
        summary_file = self.base_dir / 'TX' / 'TX_merged_geometry_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Updated Texas Summary:")
        print(f"   Total zones: {len(gdf):,}")
        print(f"   High Risk: {high_risk_count:,} ({high_risk_count/len(gdf)*100:.1f}%)")
        print(f"   Moderate Risk: {moderate_risk_count:,} ({moderate_risk_count/len(gdf)*100:.1f}%)")
        if len(region_summary) > 0:
            print(f"   Regions: {len(region_summary)}")
    
    def process_all_metros(self):
        """Process Houston and Dallas metro areas"""
        print("\n" + "="*70)
        print("TEXAS METRO AREA DOWNLOADER")
        print("="*70)
        
        # First Houston
        print("\n1️⃣ Processing Houston Metropolitan Area...")
        houston_features, houston_success, houston_failed = self.download_metro_area('Houston_Metro')
        
        if houston_features:
            success = self.append_to_merged_file(houston_features, 'Houston Metro')
            if success:
                print("✅ Houston metro data appended successfully!")
            else:
                print("❌ Failed to append Houston data")
        
        # Then Dallas-Fort Worth
        print("\n2️⃣ Processing Dallas-Fort Worth Metroplex...")
        dfw_features, dfw_success, dfw_failed = self.download_metro_area('Dallas_Fort_Worth')
        
        if dfw_features:
            success = self.append_to_merged_file(dfw_features, 'Dallas Fort Worth')
            if success:
                print("✅ Dallas-Fort Worth data appended successfully!")
            else:
                print("❌ Failed to append Dallas-Fort Worth data")
        
        # Final summary
        print("\n" + "="*70)
        print("METRO DOWNLOAD COMPLETE!")
        print("="*70)
        
        print(f"\nHouston Metro: {len(houston_features):,} features from {len(houston_success)} counties")
        print(f"Dallas-Fort Worth: {len(dfw_features):,} features from {len(dfw_success)} counties")
        
        return {
            'Houston': {'features': len(houston_features), 'counties': houston_success},
            'Dallas_Fort_Worth': {'features': len(dfw_features), 'counties': dfw_success}
        }


if __name__ == "__main__":
    downloader = TexasMetroDownloader()
    
    print("🎯 Texas Metro Area Downloader")
    print("Will download Houston and Dallas-Fort Worth by individual counties")
    print("and append to existing merged geometry file")
    
    results = downloader.process_all_metros()