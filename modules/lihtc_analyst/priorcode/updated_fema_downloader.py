#!/usr/bin/env python3
"""
Updated FEMA Flood Map Downloader - Uses Working ArcGIS REST API
Downloads FEMA NFHL flood hazard data for CA, NM, and TX using the working API endpoint
"""

import requests
import geopandas as gpd
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import time
import math

class UpdatedFEMADownloader:
    def __init__(self, base_dir: str = None):
        """Initialize the updated FEMA downloader using working API endpoint"""
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path("./state_flood_data")
        
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Working FEMA API endpoint
        self.api_base = "https://msc.fema.gov/arcgis/rest/services/NFHL_Print/NFHL/MapServer/14"
        
        # State configurations
        self.states = {
            'CA': {'name': 'California', 'fips_prefix': '06'},
            'NM': {'name': 'New Mexico', 'fips_prefix': '35'}, 
            'TX': {'name': 'Texas', 'fips_prefix': '48'}
        }
        
        # Create state directories
        for state_code in self.states.keys():
            state_dir = self.base_dir / state_code
            (state_dir / 'raw_data').mkdir(parents=True, exist_ok=True)
            (state_dir / 'processed').mkdir(parents=True, exist_ok=True)
            (state_dir / 'merged').mkdir(parents=True, exist_ok=True)
    
    def get_record_count(self, state_code: str) -> int:
        """Get total number of flood zone records for a state"""
        fips_prefix = self.states[state_code]['fips_prefix']
        
        params = {
            'where': f"DFIRM_ID LIKE '{fips_prefix}%'",
            'returnCountOnly': 'true',
            'f': 'json'
        }
        
        try:
            response = requests.get(f"{self.api_base}/query", params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return data.get('count', 0)
        except Exception as e:
            print(f"Error getting count for {state_code}: {e}")
            return 0
        
        return 0
    
    def download_state_chunks(self, state_code: str, chunk_size: int = 2000) -> list:
        """Download flood data for a state in chunks"""
        state_name = self.states[state_code]['name']
        fips_prefix = self.states[state_code]['fips_prefix']
        
        print(f"\n🏗️ Downloading FEMA flood data for {state_name}...")
        
        # Get total record count
        total_records = self.get_record_count(state_code)
        print(f"   Total records to download: {total_records:,}")
        
        if total_records == 0:
            print(f"   ❌ No records found for {state_name}")
            return []
        
        # Calculate number of chunks needed
        num_chunks = math.ceil(total_records / chunk_size)
        print(f"   Will download in {num_chunks} chunks of {chunk_size} records each")
        
        all_features = []
        
        # Download in chunks
        for chunk_num in range(num_chunks):
            offset = chunk_num * chunk_size
            
            params = {
                'where': f"DFIRM_ID LIKE '{fips_prefix}%'",
                'outFields': 'DFIRM_ID,FLD_ZONE,ZONE_SUBTY,SFHA_TF,STATIC_BFE,V_DATUM,SOURCE_CIT',
                'returnGeometry': 'true',
                'geometryPrecision': 6,
                'outSR': '4326',  # WGS84
                'resultOffset': offset,
                'resultRecordCount': chunk_size,
                'f': 'geojson'
            }
            
            try:
                print(f"   📥 Downloading chunk {chunk_num + 1}/{num_chunks} (offset {offset:,})...")
                
                response = requests.get(f"{self.api_base}/query", params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'features' in data and data['features']:
                        all_features.extend(data['features'])
                        print(f"   ✅ Downloaded {len(data['features'])} features")
                    else:
                        print(f"   ⚠️ No features in chunk {chunk_num + 1}")
                        
                    # Rate limiting
                    time.sleep(1)
                    
                else:
                    print(f"   ❌ Chunk {chunk_num + 1} failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error downloading chunk {chunk_num + 1}: {e}")
                continue
        
        print(f"   📊 Downloaded {len(all_features):,} total features for {state_name}")
        return all_features
    
    def save_state_data(self, state_code: str, features: list):
        """Save downloaded features to files"""
        if not features:
            print(f"   ❌ No features to save for {state_code}")
            return None
            
        state_name = self.states[state_code]['name']
        state_dir = self.base_dir / state_code
        
        # Save raw GeoJSON
        raw_file = state_dir / 'raw_data' / f'{state_code}_flood_zones_raw.geojson'
        geojson_data = {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "FEMA NFHL via ArcGIS REST API",
                "download_date": datetime.now().isoformat(),
                "state": state_name,
                "total_features": len(features)
            }
        }
        
        with open(raw_file, 'w') as f:
            json.dump(geojson_data, f)
        print(f"   💾 Saved raw data: {raw_file}")
        
        # Convert to GeoDataFrame and save as GeoPackage
        try:
            gdf = gpd.GeoDataFrame.from_features(features, crs='EPSG:4326')
            
            # Clean up data
            gdf = gdf.dropna(subset=['geometry'])
            gdf['State'] = state_code
            gdf['State_Name'] = state_name
            gdf['Download_Date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Save to GeoPackage
            gpkg_file = state_dir / 'processed' / f'{state_code}_flood_zones.gpkg'
            gdf.to_file(gpkg_file, driver='GPKG', layer='flood_hazard_zones')
            print(f"   💾 Saved GeoPackage: {gpkg_file}")
            
            # Create summary
            self.create_state_summary(state_code, gdf)
            
            return gpkg_file
            
        except Exception as e:
            print(f"   ❌ Error processing data for {state_code}: {e}")
            return None
    
    def create_state_summary(self, state_code: str, gdf: gpd.GeoDataFrame):
        """Create summary statistics for a state"""
        state_dir = self.base_dir / state_code
        state_name = self.states[state_code]['name']
        
        # Zone summary
        zone_summary = gdf['FLD_ZONE'].value_counts()
        
        # Risk categorization
        high_risk_zones = ['A', 'AE', 'AH', 'AO', 'V', 'VE']
        high_risk_count = gdf[gdf['FLD_ZONE'].isin(high_risk_zones)].shape[0]
        moderate_risk_count = gdf[gdf['FLD_ZONE'] == 'X'].shape[0]
        other_count = len(gdf) - high_risk_count - moderate_risk_count
        
        # SFHA summary
        sfha_count = gdf[gdf['SFHA_TF'] == 'T'].shape[0]
        
        summary = {
            'state': state_name,
            'state_code': state_code,
            'total_flood_zones': len(gdf),
            'high_risk_zones': high_risk_count,
            'moderate_risk_zones': moderate_risk_count,
            'other_zones': other_count,
            'sfha_zones': sfha_count,
            'zone_breakdown': zone_summary.to_dict(),
            'download_date': datetime.now().isoformat(),
            'data_source': 'FEMA NFHL via ArcGIS REST API'
        }
        
        # Save summary
        summary_file = state_dir / f'{state_code}_flood_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Flood Zone Summary for {state_name}:")
        print(f"   Total zones: {len(gdf):,}")
        print(f"   High Risk (A/V zones): {high_risk_count:,} ({high_risk_count/len(gdf)*100:.1f}%)")
        print(f"   Moderate Risk (X zones): {moderate_risk_count:,} ({moderate_risk_count/len(gdf)*100:.1f}%)")
        print(f"   SFHA zones: {sfha_count:,} ({sfha_count/len(gdf)*100:.1f}%)")
        
        print(f"\n   Top 5 flood zones:")
        for zone, count in zone_summary.head(5).items():
            print(f"   - Zone {zone}: {count:,} polygons")
    
    def download_all_states(self):
        """Download flood data for all configured states"""
        print("\n" + "="*70)
        print("FEMA FLOOD DATA DOWNLOAD - CA, NM, TX")
        print("Using Working ArcGIS REST API Endpoint")
        print("="*70)
        print(f"Base directory: {self.base_dir}")
        
        results = {}
        
        for state_code, state_info in self.states.items():
            print(f"\n{'='*50}")
            print(f"Processing {state_info['name']} ({state_code})")
            print(f"{'='*50}")
            
            # Download state data
            features = self.download_state_chunks(state_code)
            
            # Save data
            if features:
                gpkg_file = self.save_state_data(state_code, features)
                results[state_code] = {
                    'success': True,
                    'records': len(features),
                    'file': gpkg_file
                }
            else:
                results[state_code] = {
                    'success': False,
                    'records': 0,
                    'file': None
                }
        
        # Final summary
        print("\n" + "="*70)
        print("DOWNLOAD COMPLETE!")
        print("="*70)
        
        total_records = 0
        for state_code, result in results.items():
            state_name = self.states[state_code]['name']
            if result['success']:
                print(f"\n✅ {state_name}: {result['records']:,} flood zones")
                print(f"   File: {result['file']}")
                total_records += result['records']
            else:
                print(f"\n❌ {state_name}: Download failed")
        
        print(f"\n📊 Total flood zones downloaded: {total_records:,}")
        print(f"✅ All data saved to: {self.base_dir}")
        
        # Create master README
        self.create_readme()
        
        return results
    
    def create_readme(self):
        """Create README file with dataset information"""
        readme_content = f"""# FEMA Flood Map Data (Updated API)

## Overview
This directory contains FEMA National Flood Hazard Layer (NFHL) data downloaded using the working ArcGIS REST API endpoint for:
- California (CA)
- New Mexico (NM) 
- Texas (TX)

## Data Source
- **API Endpoint**: https://msc.fema.gov/arcgis/rest/services/NFHL_Print/NFHL/MapServer/14
- **Download Date**: {datetime.now().strftime('%Y-%m-%d')}
- **Source**: FEMA Map Service Center

## Data Organization
```
state_flood_data/
├── CA/
│   ├── raw_data/
│   │   └── CA_flood_zones_raw.geojson      # Raw API response
│   ├── processed/
│   │   └── CA_flood_zones.gpkg             # Cleaned GeoPackage
│   ├── merged/                             # For future aggregations
│   └── CA_flood_summary.json               # Statistics
├── NM/
│   └── [same structure]
└── TX/
    └── [same structure]
```

## Flood Zone Categories

### High Risk Zones (Special Flood Hazard Area - SFHA)
- **A**: 100-year floodplain, no BFE determined
- **AE**: 100-year floodplain with Base Flood Elevation
- **AH**: Shallow flooding (1-3 feet typical)
- **AO**: Sheet flow flooding
- **V**: Coastal high hazard area
- **VE**: Coastal high hazard with BFE

### Moderate/Minimal Risk
- **X**: 500-year floodplain or protected by levees
- **X (shaded)**: Areas of 0.2% annual chance flood

### Other
- **D**: Undetermined risk
- **AREA NOT INCLUDED**: No flood hazard analysis performed

## Key Fields
- **FLD_ZONE**: Flood zone designation (A, AE, X, etc.)
- **ZONE_SUBTY**: Zone subtype details
- **SFHA_TF**: Special Flood Hazard Area flag (T/F)
- **STATIC_BFE**: Base Flood Elevation
- **DFIRM_ID**: Digital FIRM identifier

## Usage for LIHTC Analysis
Properties in high-risk zones (A, AE, AH, AO, V, VE) should be carefully evaluated for LIHTC development due to:
- Mandatory flood insurance requirements
- Increased construction costs (15-25%)
- Limited investor interest
- Additional environmental reviews

## Technical Notes
- **CRS**: EPSG:4326 (WGS84)
- **Download Method**: ArcGIS REST API chunks of 2,000 records
- **File Formats**: GeoJSON (raw), GeoPackage (processed)
- **Update Frequency**: Data should be refreshed annually

## Usage Examples

### Python/GeoPandas
```python
import geopandas as gpd

# Load Texas flood zones
tx_floods = gpd.read_file('TX/processed/TX_flood_zones.gpkg')

# Filter high-risk zones
high_risk = tx_floods[tx_floods['FLD_ZONE'].isin(['A', 'AE', 'AH', 'AO', 'V', 'VE'])]

# Spatial analysis with property data
properties = gpd.read_file('your_properties.geojson')
flood_risk = gpd.sjoin(properties, tx_floods[['FLD_ZONE', 'geometry']], 
                      how='left', predicate='intersects')
```

### QGIS
1. Layer → Add Layer → Add Vector Layer
2. Navigate to state's processed/ directory
3. Select the .gpkg file
4. Style by FLD_ZONE field using FEMA standard colors
"""
        
        readme_file = self.base_dir / 'README.md'
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        print(f"📄 Created README: {readme_file}")


def quick_flood_check_updated(property_file: str, state_code: str):
    """
    Quick flood zone check using the updated data format
    """
    base_dir = Path("./state_flood_data")
    flood_file = base_dir / state_code / 'processed' / f'{state_code}_flood_zones.gpkg'
    
    if not flood_file.exists():
        print(f"❌ No flood data found for {state_code}")
        print(f"Expected file: {flood_file}")
        return
    
    print(f"🔍 Loading flood data for {state_code}...")
    
    # Load properties
    if property_file.endswith('.csv'):
        properties = pd.read_csv(property_file)
    else:
        properties = pd.read_excel(property_file)
    
    # Convert to GeoDataFrame (assuming Longitude/Latitude columns)
    geometry = gpd.points_from_xy(properties['Longitude'], properties['Latitude'])
    properties_gdf = gpd.GeoDataFrame(properties, geometry=geometry, crs='EPSG:4326')
    
    # Load flood zones
    flood_zones = gpd.read_file(flood_file)
    
    print(f"✅ Loaded {len(flood_zones):,} flood zones")
    
    # Spatial join
    properties_with_flood = gpd.sjoin(properties_gdf, 
                                     flood_zones[['FLD_ZONE', 'ZONE_SUBTY', 'SFHA_TF', 'geometry']], 
                                     how='left', predicate='intersects')
    
    # Add risk category
    high_risk_zones = ['A', 'AE', 'AH', 'AO', 'V', 'VE']
    properties_with_flood['Flood_Risk'] = properties_with_flood['FLD_ZONE'].apply(
        lambda x: 'HIGH' if x in high_risk_zones else ('MODERATE' if x == 'X' else 'LOW/NONE')
    )
    
    # Summary
    print(f"\n📊 Flood Risk Summary:")
    risk_summary = properties_with_flood['Flood_Risk'].value_counts()
    for risk, count in risk_summary.items():
        print(f"   {risk}: {count} properties")
    
    # Zone summary
    print(f"\n🗺️ Flood Zone Summary:")
    zone_summary = properties_with_flood['FLD_ZONE'].value_counts()
    for zone, count in zone_summary.head(10).items():
        print(f"   Zone {zone}: {count} properties")
    
    # Save results
    output_file = property_file.replace('.xlsx', '_with_flood.xlsx').replace('.csv', '_with_flood.csv')
    properties_with_flood.drop('geometry', axis=1).to_excel(output_file, index=False)
    print(f"\n✅ Results saved to: {output_file}")
    
    return properties_with_flood


if __name__ == "__main__":
    # Initialize updated downloader
    downloader = UpdatedFEMADownloader()
    
    print("🚀 Updated FEMA Downloader Ready!")
    print("\nThis version uses the working ArcGIS REST API endpoint")
    print("Data source: https://msc.fema.gov/arcgis/rest/services/NFHL_Print/NFHL/MapServer/14")
    
    print("\nTo download all states:")
    print("   results = downloader.download_all_states()")
    
    print("\nTo download specific state:")
    print("   features = downloader.download_state_chunks('TX')")
    print("   downloader.save_state_data('TX', features)")
    
    print("\nTo check properties against flood zones:")
    print("   quick_flood_check_updated('properties.xlsx', 'TX')")