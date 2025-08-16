#!/usr/bin/env python3
"""
FEMA Multi-State Flood Map Downloader
Downloads and organizes FEMA flood data for CA, NM, and TX
"""

import requests
import zipfile
import os
from pathlib import Path
import geopandas as gpd
import pandas as pd
from datetime import datetime
import time
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

class FEMAMultiStateDownloader:
    def __init__(self, base_dir: str = None):
        """Initialize FEMA multi-state downloader"""
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/FEMA_Flood_Maps")
        
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # State configurations
        self.states = {
            'CA': {
                'name': 'California',
                'fips_prefix': '06',
                'major_counties': {
                    '06001': 'Alameda',        # Oakland
                    '06013': 'Contra Costa',   # Richmond
                    '06019': 'Fresno',
                    '06029': 'Kern',          # Bakersfield
                    '06037': 'Los Angeles',
                    '06041': 'Marin',
                    '06047': 'Merced',
                    '06053': 'Monterey',
                    '06055': 'Napa',
                    '06059': 'Orange',
                    '06065': 'Riverside',
                    '06067': 'Sacramento',
                    '06071': 'San Bernardino',
                    '06073': 'San Diego',
                    '06075': 'San Francisco',
                    '06077': 'San Joaquin',
                    '06079': 'San Luis Obispo',
                    '06081': 'San Mateo',
                    '06083': 'Santa Barbara',
                    '06085': 'Santa Clara',    # San Jose
                    '06087': 'Santa Cruz',
                    '06095': 'Solano',
                    '06097': 'Sonoma',
                    '06099': 'Stanislaus',
                    '06101': 'Sutter',
                    '06107': 'Tulare',
                    '06111': 'Ventura',
                    '06113': 'Yolo'
                }
            },
            'NM': {
                'name': 'New Mexico',
                'fips_prefix': '35',
                'major_counties': {
                    '35001': 'Bernalillo',     # Albuquerque
                    '35013': 'Dona Ana',       # Las Cruces
                    '35015': 'Eddy',          # Carlsbad
                    '35025': 'Lea',           # Hobbs
                    '35028': 'Los Alamos',
                    '35031': 'McKinley',      # Gallup
                    '35043': 'Sandoval',      # Rio Rancho
                    '35045': 'San Juan',      # Farmington
                    '35049': 'Santa Fe',
                    '35055': 'Taos',
                    '35061': 'Valencia'
                }
            },
            'TX': {
                'name': 'Texas',
                'fips_prefix': '48',
                'major_counties': {
                    '48001': 'Anderson',
                    '48013': 'Atascosa',
                    '48015': 'Austin',
                    '48027': 'Bell',          # Killeen
                    '48029': 'Bexar',         # San Antonio
                    '48039': 'Brazoria',      # Pearland
                    '48041': 'Brazos',        # College Station
                    '48055': 'Caldwell',
                    '48061': 'Cameron',       # Brownsville
                    '48085': 'Collin',        # Plano
                    '48091': 'Comal',         # New Braunfels
                    '48099': 'Coryell',
                    '48113': 'Dallas',
                    '48121': 'Denton',
                    '48135': 'Ector',         # Odessa
                    '48141': 'El Paso',
                    '48157': 'Fort Bend',     # Sugar Land
                    '48167': 'Galveston',
                    '48181': 'Grayson',       # Sherman
                    '48183': 'Gregg',         # Longview
                    '48187': 'Guadalupe',
                    '48201': 'Harris',        # Houston
                    '48209': 'Hays',          # San Marcos
                    '48213': 'Henderson',
                    '48215': 'Hidalgo',       # McAllen
                    '48231': 'Hunt',
                    '48245': 'Jefferson',     # Beaumont
                    '48251': 'Johnson',
                    '48257': 'Kaufman',
                    '48303': 'Lubbock',
                    '48309': 'McLennan',      # Waco
                    '48329': 'Midland',
                    '48339': 'Montgomery',    # The Woodlands
                    '48347': 'Nacogdoches',
                    '48355': 'Nueces',        # Corpus Christi
                    '48361': 'Orange',
                    '48367': 'Parker',
                    '48375': 'Potter',        # Amarillo
                    '48381': 'Randall',       # Canyon
                    '48397': 'Rockwall',
                    '48423': 'Smith',         # Tyler
                    '48439': 'Tarrant',       # Fort Worth
                    '48441': 'Taylor',        # Abilene
                    '48451': 'Tom Green',     # San Angelo
                    '48453': 'Travis',        # Austin
                    '48469': 'Victoria',
                    '48479': 'Webb',          # Laredo
                    '48485': 'Wichita',       # Wichita Falls
                    '48491': 'Williamson',    # Round Rock
                    '48493': 'Wilson'
                }
            }
        }
        
        # Create state directories
        for state_code, state_info in self.states.items():
            state_dir = self.base_dir / state_code
            state_dir.mkdir(exist_ok=True)
            
            # Create subdirectories
            (state_dir / 'temp_downloads').mkdir(exist_ok=True)
            (state_dir / 'county_data').mkdir(exist_ok=True)
            (state_dir / 'merged').mkdir(exist_ok=True)
            (state_dir / 'styles').mkdir(exist_ok=True)
    
    def download_county_data(self, state_code: str, fips_code: str, county_name: str) -> bool:
        """
        Download FEMA data for a single county
        """
        state_dir = self.base_dir / state_code
        temp_dir = state_dir / 'temp_downloads'
        county_dir = state_dir / 'county_data' / f"{fips_code}_{county_name.replace(' ', '_')}"
        
        # Skip if already downloaded
        if county_dir.exists() and any(county_dir.glob('**/S_*')):
            print(f"   ✅ Already downloaded: {county_name} ({fips_code})")
            return True
        
        county_dir.mkdir(parents=True, exist_ok=True)
        
        # Try different URL patterns
        url_patterns = [
            f"https://hazards.fema.gov/nfhlv2/output/County/NFHL_{fips_code}_GeoDatabase.zip",
            f"https://hazards.fema.gov/nfhlv2/output/County/{fips_code}_NFHL.zip",
            f"https://msc.fema.gov/portal/NFHL/NFHL_{fips_code}.zip"
        ]
        
        for url in url_patterns:
            try:
                print(f"   📥 Downloading {county_name} County ({fips_code})...")
                response = requests.get(url, stream=True, timeout=30)
                
                if response.status_code == 200:
                    zip_path = temp_dir / f"NFHL_{fips_code}.zip"
                    
                    # Download
                    with open(zip_path, 'wb') as f:
                        for chunk in response.iter_content(8192):
                            if chunk:
                                f.write(chunk)
                    
                    # Extract
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(county_dir)
                    
                    # Clean up zip
                    zip_path.unlink()
                    
                    print(f"   ✅ Downloaded: {county_name}")
                    return True
                    
            except Exception as e:
                continue
        
        print(f"   ⚠️ Failed to download: {county_name}")
        return False
    
    def download_state_counties(self, state_code: str, parallel: bool = True):
        """
        Download all counties for a state
        """
        state_info = self.states[state_code]
        state_name = state_info['name']
        counties = state_info['major_counties']
        
        print(f"\n🏗️ Downloading FEMA data for {state_name} ({len(counties)} counties)")
        
        successful = []
        failed = []
        
        if parallel:
            # Parallel download (faster but more resource intensive)
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_county = {
                    executor.submit(self.download_county_data, state_code, fips, county): (fips, county)
                    for fips, county in counties.items()
                }
                
                for future in as_completed(future_to_county):
                    fips, county = future_to_county[future]
                    try:
                        if future.result():
                            successful.append(county)
                        else:
                            failed.append(county)
                    except Exception as e:
                        print(f"   ❌ Error downloading {county}: {e}")
                        failed.append(county)
                    
                    # Rate limiting
                    time.sleep(1)
        else:
            # Sequential download (slower but more stable)
            for fips, county in counties.items():
                if self.download_county_data(state_code, fips, county):
                    successful.append(county)
                else:
                    failed.append(county)
                time.sleep(2)
        
        print(f"\n📊 {state_name} Download Summary:")
        print(f"   ✅ Successful: {len(successful)} counties")
        print(f"   ❌ Failed: {len(failed)} counties")
        
        if failed:
            print(f"   Failed counties: {', '.join(failed)}")
        
        return successful, failed
    
    def create_state_geopackage(self, state_code: str):
        """
        Merge all county data for a state into a single GeoPackage
        """
        state_info = self.states[state_code]
        state_name = state_info['name']
        state_dir = self.base_dir / state_code
        county_data_dir = state_dir / 'county_data'
        
        print(f"\n🔨 Creating merged GeoPackage for {state_name}...")
        
        all_flood_zones = []
        counties_processed = 0
        
        # Process each county
        for county_dir in county_data_dir.glob("*_*"):
            if county_dir.is_dir():
                county_name = county_dir.name.split('_', 1)[1].replace('_', ' ')
                
                # Look for flood hazard areas
                patterns = [
                    "**/S_FLD_HAZ_AR.shp",
                    "**/S_Fld_Haz_Ar.shp",
                    "**/S_FLD_HAZ_AR.gdb",
                    "**/*.gdb"
                ]
                
                found = False
                for pattern in patterns:
                    files = list(county_dir.glob(pattern))
                    if files:
                        try:
                            if pattern.endswith('.gdb'):
                                # Try to read from geodatabase
                                gdf = gpd.read_file(files[0], layer='S_Fld_Haz_Ar')
                            else:
                                # Read shapefile
                                gdf = gpd.read_file(files[0])
                            
                            # Add county info
                            gdf['County'] = county_name
                            gdf['State'] = state_code
                            
                            # Keep only essential columns
                            keep_cols = ['FLD_ZONE', 'ZONE_SUBTY', 'STATIC_BFE', 
                                       'County', 'State', 'geometry']
                            available_cols = [col for col in keep_cols if col in gdf.columns]
                            gdf = gdf[available_cols]
                            
                            all_flood_zones.append(gdf)
                            counties_processed += 1
                            found = True
                            break
                            
                        except Exception as e:
                            continue
                
                if not found:
                    print(f"   ⚠️ No flood data found for {county_name}")
        
        if all_flood_zones:
            print(f"   Merging data from {counties_processed} counties...")
            
            # Merge all counties
            merged = gpd.GeoDataFrame(pd.concat(all_flood_zones, ignore_index=True))
            
            # Ensure consistent CRS (WGS84)
            merged = merged.to_crs('EPSG:4326')
            
            # Save to GeoPackage
            output_path = state_dir / 'merged' / f"{state_code}_FEMA_Flood_Zones.gpkg"
            merged.to_file(output_path, driver='GPKG', layer='flood_hazard_areas')
            
            print(f"\n✅ {state_name} GeoPackage created: {output_path}")
            print(f"   Total flood zones: {len(merged):,}")
            print(f"   Counties included: {counties_processed}")
            print(f"   File size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
            
            # Create summary statistics
            self.create_state_summary(state_code, merged)
            
            return output_path
        else:
            print(f"   ❌ No flood zone data found for {state_name}")
            return None
    
    def create_state_summary(self, state_code: str, gdf: gpd.GeoDataFrame):
        """
        Create summary statistics for a state
        """
        state_dir = self.base_dir / state_code
        
        # Zone summary
        zone_summary = gdf['FLD_ZONE'].value_counts()
        
        # County summary
        county_summary = gdf['County'].value_counts()
        
        # Risk summary
        high_risk_zones = ['A', 'AE', 'AH', 'AO', 'V', 'VE']
        high_risk_count = gdf[gdf['FLD_ZONE'].isin(high_risk_zones)].shape[0]
        moderate_risk_count = gdf[gdf['FLD_ZONE'] == 'X'].shape[0]
        
        summary = {
            'state': self.states[state_code]['name'],
            'total_flood_zones': len(gdf),
            'counties_included': len(county_summary),
            'high_risk_zones': high_risk_count,
            'moderate_risk_zones': moderate_risk_count,
            'zone_breakdown': zone_summary.to_dict(),
            'counties': county_summary.to_dict(),
            'generated_date': datetime.now().isoformat()
        }
        
        # Save summary
        summary_path = state_dir / f"{state_code}_flood_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Flood Zone Summary for {self.states[state_code]['name']}:")
        print(f"   High Risk Zones (A/V): {high_risk_count:,} ({high_risk_count/len(gdf)*100:.1f}%)")
        print(f"   Moderate Risk (X): {moderate_risk_count:,} ({moderate_risk_count/len(gdf)*100:.1f}%)")
        
        print(f"\n   Top flood zones:")
        for zone, count in zone_summary.head(5).items():
            print(f"   - Zone {zone}: {count:,} polygons")
    
    def create_qgis_styles(self):
        """
        Create QGIS style files for all states
        """
        qml_content = '''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.28.0" styleCategories="Symbology|Labeling">
  <renderer-v2 type="categorizedSymbol" attr="FLD_ZONE" symbollevels="0" enableorderby="0">
    <categories>
      <category symbol="0" value="A" label="A - 100-year flood (High Risk)" render="true"/>
      <category symbol="1" value="AE" label="AE - 100-year flood with BFE (High Risk)" render="true"/>
      <category symbol="2" value="AH" label="AH - Shallow flooding (High Risk)" render="true"/>
      <category symbol="3" value="AO" label="AO - Sheet flow (High Risk)" render="true"/>
      <category symbol="4" value="V" label="V - Coastal high hazard (High Risk)" render="true"/>
      <category symbol="5" value="VE" label="VE - Coastal high hazard with BFE (High Risk)" render="true"/>
      <category symbol="6" value="X" label="X - 500-year/Minimal risk (Moderate Risk)" render="true"/>
      <category symbol="7" value="D" label="D - Undetermined risk" render="true"/>
      <category symbol="8" value="" label="Other zones" render="true"/>
    </categories>
    <symbols>
      <symbol name="0" type="fill" clip_to_extent="1" alpha="1">
        <layer enabled="1" class="SimpleFill">
          <prop v="255,0,0,180" k="color"/>
          <prop v="solid" k="style"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="0.1" k="outline_width"/>
        </layer>
      </symbol>
      <symbol name="1" type="fill" clip_to_extent="1" alpha="1">
        <layer enabled="1" class="SimpleFill">
          <prop v="255,85,0,180" k="color"/>
          <prop v="solid" k="style"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="0.1" k="outline_width"/>
        </layer>
      </symbol>
      <symbol name="2" type="fill" clip_to_extent="1" alpha="1">
        <layer enabled="1" class="SimpleFill">
          <prop v="255,170,0,180" k="color"/>
          <prop v="solid" k="style"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="0.1" k="outline_width"/>
        </layer>
      </symbol>
      <symbol name="3" type="fill" clip_to_extent="1" alpha="1">
        <layer enabled="1" class="SimpleFill">
          <prop v="255,255,0,180" k="color"/>
          <prop v="solid" k="style"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="0.1" k="outline_width"/>
        </layer>
      </symbol>
      <symbol name="4" type="fill" clip_to_extent="1" alpha="1">
        <layer enabled="1" class="SimpleFill">
          <prop v="170,0,255,180" k="color"/>
          <prop v="solid" k="style"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="0.1" k="outline_width"/>
        </layer>
      </symbol>
      <symbol name="5" type="fill" clip_to_extent="1" alpha="1">
        <layer enabled="1" class="SimpleFill">
          <prop v="85,0,255,180" k="color"/>
          <prop v="solid" k="style"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="0.1" k="outline_width"/>
        </layer>
      </symbol>
      <symbol name="6" type="fill" clip_to_extent="1" alpha="1">
        <layer enabled="1" class="SimpleFill">
          <prop v="190,232,255,120" k="color"/>
          <prop v="solid" k="style"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="0.1" k="outline_width"/>
        </layer>
      </symbol>
      <symbol name="7" type="fill" clip_to_extent="1" alpha="1">
        <layer enabled="1" class="SimpleFill">
          <prop v="204,204,204,120" k="color"/>
          <prop v="solid" k="style"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="0.1" k="outline_width"/>
        </layer>
      </symbol>
      <symbol name="8" type="fill" clip_to_extent="1" alpha="1">
        <layer enabled="1" class="SimpleFill">
          <prop v="225,225,225,120" k="color"/>
          <prop v="solid" k="style"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="0.1" k="outline_width"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
</qgis>'''
        
        # Create style for each state
        for state_code in self.states.keys():
            style_dir = self.base_dir / state_code / 'styles'
            style_path = style_dir / 'FEMA_Flood_Zones.qml'
            
            with open(style_path, 'w') as f:
                f.write(qml_content)
            
            print(f"   🎨 Created QGIS style for {state_code}: {style_path}")
    
    def download_all_states(self, parallel: bool = False):
        """
        Download FEMA data for all configured states
        """
        print("\n" + "="*70)
        print("FEMA FLOOD MAP DOWNLOAD - CA, NM, TX")
        print("="*70)
        print(f"Base directory: {self.base_dir}")
        
        # Create overview README
        self.create_readme()
        
        # Download each state
        state_results = {}
        
        for state_code, state_info in self.states.items():
            print(f"\n{'='*50}")
            print(f"Processing {state_info['name']}")
            print(f"{'='*50}")
            
            # Download counties
            successful, failed = self.download_state_counties(state_code, parallel=parallel)
            
            # Create merged GeoPackage
            if successful:
                gpkg_path = self.create_state_geopackage(state_code)
                state_results[state_code] = {
                    'successful': len(successful),
                    'failed': len(failed),
                    'geopackage': gpkg_path
                }
            
            # Clean up temp downloads
            temp_dir = self.base_dir / state_code / 'temp_downloads'
            shutil.rmtree(temp_dir, ignore_errors=True)
            temp_dir.mkdir(exist_ok=True)
        
        # Create QGIS styles
        print("\n🎨 Creating QGIS styles...")
        self.create_qgis_styles()
        
        # Final summary
        print("\n" + "="*70)
        print("DOWNLOAD COMPLETE!")
        print("="*70)
        
        for state_code, results in state_results.items():
            state_name = self.states[state_code]['name']
            print(f"\n{state_name}:")
            print(f"   Downloaded: {results['successful']} counties")
            if results.get('geopackage'):
                print(f"   GeoPackage: {results['geopackage']}")
        
        print(f"\n✅ All data saved to: {self.base_dir}")
        
        return state_results
    
    def create_readme(self):
        """
        Create README file with dataset information
        """
        readme_content = f"""# FEMA Flood Map Data

## Overview
This directory contains FEMA National Flood Hazard Layer (NFHL) data for:
- California (CA)
- New Mexico (NM)
- Texas (TX)

## Data Organization
```
FEMA_Flood_Maps/
├── CA/
│   ├── merged/
│   │   └── CA_FEMA_Flood_Zones.gpkg    # All CA counties merged
│   ├── county_data/                     # Individual county data
│   ├── styles/
│   │   └── FEMA_Flood_Zones.qml        # QGIS style file
│   └── CA_flood_summary.json           # Statistics
├── NM/
│   └── [same structure]
└── TX/
    └── [same structure]
```

## Flood Zone Categories

### High Risk Zones (Mandatory Insurance)
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

## Usage in QGIS
1. Open QGIS
2. Layer → Add Layer → Add Vector Layer
3. Navigate to state's merged/ directory
4. Select the .gpkg file
5. Apply the style from styles/ directory

## Usage for LIHTC Analysis
Properties in zones A, AE, AH, AO, V, VE should generally be avoided for LIHTC development due to:
- Mandatory flood insurance requirements
- Increased construction costs (15-25%)
- Limited investor interest
- Additional environmental reviews

## Data Source
FEMA Map Service Center: https://msc.fema.gov/
Downloaded: {datetime.now().strftime('%Y-%m-%d')}

## Update Frequency
FEMA updates flood maps on a rolling basis. Consider refreshing this data annually.
"""
        
        readme_path = self.base_dir / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"📄 Created README: {readme_path}")


# Utility function for quick property analysis
def quick_flood_check(property_file: str, state_code: str):
    """
    Quick flood zone check for a list of properties
    """
    base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/FEMA_Flood_Maps")
    flood_gpkg = base_dir / state_code / 'merged' / f"{state_code}_FEMA_Flood_Zones.gpkg"
    
    if not flood_gpkg.exists():
        print(f"❌ No flood data found for {state_code}")
        return
    
    # Load properties
    if property_file.endswith('.csv'):
        properties = pd.read_csv(property_file)
    else:
        properties = pd.read_excel(property_file)
    
    # Convert to GeoDataFrame
    geometry = gpd.points_from_xy(properties['Longitude'], properties['Latitude'])
    properties_gdf = gpd.GeoDataFrame(properties, geometry=geometry, crs='EPSG:4326')
    
    # Load flood zones
    flood_zones = gpd.read_file(flood_gpkg)
    
    # Spatial join
    properties_with_flood = gpd.sjoin(properties_gdf, flood_zones[['FLD_ZONE', 'geometry']], 
                                     how='left', predicate='intersects')
    
    # Add risk category
    high_risk = ['A', 'AE', 'AH', 'AO', 'V', 'VE']
    properties_with_flood['Flood_Risk'] = properties_with_flood['FLD_ZONE'].apply(
        lambda x: 'HIGH' if x in high_risk else ('MODERATE' if x == 'X' else 'LOW/NONE')
    )
    
    # Summary
    print(f"\n📊 Flood Risk Summary:")
    print(properties_with_flood['Flood_Risk'].value_counts())
    
    # Save results
    output_file = property_file.replace('.xlsx', '_with_flood.xlsx').replace('.csv', '_with_flood.csv')
    properties_with_flood.drop('geometry', axis=1).to_excel(output_file, index=False)
    print(f"\n✅ Results saved to: {output_file}")
    
    return properties_with_flood


if __name__ == "__main__":
    # Initialize downloader
    downloader = FEMAMultiStateDownloader()
    
    # Option 1: Download everything (will take several hours)
    # downloader.download_all_states(parallel=True)
    
    # Option 2: Download specific state
    # downloader.download_state_counties('TX', parallel=True)
    # downloader.create_state_geopackage('TX')
    
    # Option 3: Download specific county
    # downloader.download_county_data('TX', '48201', 'Harris')
    
    print("\n✅ FEMA Multi-State Downloader Ready!")
    print("\nTo download all states, run:")
    print("   downloader.download_all_states(parallel=True)")
    print("\nTo download one state:")
    print("   downloader.download_state_counties('TX')")
    print("   downloader.create_state_geopackage('TX')")