#!/usr/bin/env python3
"""
New Mexico Poverty Data Census Tract Downloader
Downloads poverty rate data from Census ACS and creates QGIS-ready geospatial layers
"""

import requests
import pandas as pd
import geopandas as gpd
import os
import time
import tempfile
import ssl
import urllib.request
import urllib3
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 🔐 Your correct Census API Key
API_KEY = '06ece0121263282cd9ffd753215b007b8f9a3dfc'

# Set your output path
OUTPUT_DIR = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Poverty Rate Census Tracts (ACS)'
os.makedirs(OUTPUT_DIR, exist_ok=True)

STATE_FIPS = {
    'NM': '35',
    'CA': '06',
    'TX': '48',
    'AZ': '04',
    'HI': '15'
}

def fetch_poverty_data(state_abbr, year=2022):
    """
    Fetch poverty data from Census ACS API
    Using 2022 data as 2023 might not be fully available yet
    """
    print(f"📊 Fetching poverty data for {state_abbr}...")
    
    state_fips = STATE_FIPS[state_abbr]
    
    # Use 2022 ACS 5-year estimates (most recent complete dataset)
    url = f'https://api.census.gov/data/{year}/acs/acs5'
    
    # Census variables:
    # B17001_002E = Income in the past 12 months below poverty level
    # B17001_001E = Total population for whom poverty status is determined
    params = {
        'get': 'NAME,B17001_001E,B17001_002E',
        'for': 'tract:*',
        'in': f'state:{state_fips}',
        'key': API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if len(data) < 2:
            raise ValueError("No data returned from Census API")
        
        # Create DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])
        
        # Create GEOID (state + county + tract)
        df['GEOID'] = df['state'] + df['county'] + df['tract']
        
        # Calculate poverty percentage with error handling
        df['total_pop'] = pd.to_numeric(df['B17001_001E'], errors='coerce')
        df['poverty_pop'] = pd.to_numeric(df['B17001_002E'], errors='coerce')
        
        # Calculate poverty rate, handling division by zero
        df['poverty_rate'] = 0.0
        mask = (df['total_pop'] > 0) & (df['total_pop'].notna()) & (df['poverty_pop'].notna())
        df.loc[mask, 'poverty_rate'] = (df.loc[mask, 'poverty_pop'] / df.loc[mask, 'total_pop']) * 100
        
        # Round to 2 decimal places
        df['poverty_rate'] = df['poverty_rate'].round(2)
        
        # Clean up columns
        result_df = df[['GEOID', 'NAME', 'total_pop', 'poverty_pop', 'poverty_rate']].copy()
        
        print(f"✅ Successfully downloaded data for {len(result_df)} census tracts")
        print(f"   Average poverty rate: {result_df['poverty_rate'].mean():.1f}%")
        print(f"   Max poverty rate: {result_df['poverty_rate'].max():.1f}%")
        
        return result_df
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return None

def manual_download_instructions(state_abbr, year=2023):
    """
    Provide manual download instructions if automated download fails
    """
    state_fips = STATE_FIPS[state_abbr]
    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TRACT/tl_{year}_{state_fips}_tract.zip"
    
    manual_file = Path(OUTPUT_DIR) / f"tl_{year}_{state_fips}_tract.zip"
    
    print(f"\n📝 MANUAL DOWNLOAD INSTRUCTIONS:")
    print(f"1. Open this URL in your web browser:")
    print(f"   {url}")
    print(f"2. Right-click the file and 'Save As' to this EXACT location:")
    print(f"   {manual_file}")
    print(f"3. Make sure the filename is exactly: tl_{year}_{state_fips}_tract.zip")
    print(f"4. Re-run this script")
    print(f"\nThe script will automatically detect and use the manual download.")
    print(f"\n💡 TIP: You can also drag/drop the downloaded file to:")
    print(f"   {OUTPUT_DIR}")
    
    return str(manual_file)

def download_with_requests(url, output_file):
    """
    Download file using requests library with SSL verification disabled
    """
    try:
        print(f"📥 Downloading with requests (SSL disabled): {url}")
        
        # Disable SSL verification for this specific download
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.get(url, verify=False, stream=True, timeout=60)
        response.raise_for_status()
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"✅ Successfully downloaded: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Requests download failed: {e}")
        return False

def load_tract_geometries(state_abbr, year=2023):
    """
    Load census tract geometries with multiple download methods
    """
    print(f"🗺️ Loading census tract geometries for {state_abbr}...")
    
    state_fips = STATE_FIPS[state_abbr]
    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TRACT/tl_{year}_{state_fips}_tract.zip"
    manual_file = Path(OUTPUT_DIR) / f"tl_{year}_{state_fips}_tract.zip"
    
    # Check if manual download exists first
    if manual_file.exists():
        print(f"📁 Found existing file: {manual_file}")
        try:
            gdf = gpd.read_file(str(manual_file))
            gdf['GEOID'] = gdf['GEOID'].astype(str)
            if gdf.crs is None or gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs('EPSG:4326')
            print(f"✅ Successfully loaded {len(gdf)} census tract geometries (existing file)")
            return gdf
        except Exception as e:
            print(f"❌ Error reading existing file: {e}")
            # Delete corrupted file and try downloading again
            manual_file.unlink()
    
    # Try multiple download methods
    download_methods = [
        ("Direct GeoPandas", lambda: gpd.read_file(url)),
        ("Requests with SSL disabled", lambda: download_and_read_with_requests(url, manual_file)),
        ("urllib with SSL context", lambda: download_with_urllib_ssl_context(url, manual_file))
    ]
    
    for method_name, method_func in download_methods:
        try:
            print(f"🔄 Trying: {method_name}")
            gdf = method_func()
            
            if gdf is not None:
                # Ensure GEOID is string type for consistent merging
                gdf['GEOID'] = gdf['GEOID'].astype(str)
                
                # Convert to a more standard CRS if needed (WGS84)
                if gdf.crs is None or gdf.crs.to_epsg() != 4326:
                    gdf = gdf.to_crs('EPSG:4326')
                
                print(f"✅ Successfully loaded {len(gdf)} census tract geometries ({method_name})")
                return gdf
                
        except Exception as e:
            print(f"⚠️ {method_name} failed: {e}")
            continue
    
    # If all methods fail, provide manual instructions
    print(f"\n❌ All automatic download methods failed.")
    manual_download_instructions(state_abbr, year)
    return None

def download_and_read_with_requests(url, output_file):
    """
    Download with requests and then read with geopandas
    """
    if download_with_requests(url, output_file):
        return gpd.read_file(str(output_file))
    else:
        raise Exception("Download failed")

def download_with_urllib_ssl_context(url, output_file):
    """
    Download using urllib with custom SSL context
    """
    try:
        print(f"📥 Downloading with urllib (custom SSL): {url}")
        
        # Create SSL context that doesn't verify certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(url, context=ssl_context, timeout=60) as response:
            with open(output_file, 'wb') as f:
                f.write(response.read())
        
        print(f"✅ Successfully downloaded: {output_file}")
        return gpd.read_file(str(output_file))
        
    except Exception as e:
        print(f"❌ urllib SSL download failed: {e}")
        raise e

def create_poverty_layer(state_abbr, data_year=2022, geometry_year=2023):
    """
    Create complete poverty rate layer by merging Census data with geometries
    """
    print(f"\n🚀 Creating poverty layer for {state_abbr}...")
    
    # Fetch poverty data
    poverty_df = fetch_poverty_data(state_abbr, data_year)
    if poverty_df is None:
        return None
    
    # Load geometries
    tract_gdf = load_tract_geometries(state_abbr, geometry_year)
    if tract_gdf is None:
        return None
    
    # Merge data
    print("🔗 Merging poverty data with geometries...")
    merged_gdf = tract_gdf.merge(poverty_df, on='GEOID', how='left')
    
    # Fill any missing poverty rates with 0 (though this shouldn't happen)
    merged_gdf['poverty_rate'] = merged_gdf['poverty_rate'].fillna(0)
    
    # Add useful columns for QGIS styling
    merged_gdf['poverty_category'] = pd.cut(
        merged_gdf['poverty_rate'], 
        bins=[0, 10, 20, 30, 40, 100], 
        labels=['Very Low (0-10%)', 'Low (10-20%)', 'Moderate (20-30%)', 'High (30-40%)', 'Very High (40%+)']
    )
    
    # Create output filename
    output_file = Path(OUTPUT_DIR) / f'poverty_tracts_{state_abbr}_{data_year}.gpkg'
    
    # Save as GeoPackage (better than GeoJSON for QGIS)
    merged_gdf.to_file(output_file, driver='GPKG')
    
    print(f"✅ Poverty layer saved: {output_file}")
    print(f"   Total tracts: {len(merged_gdf)}")
    print(f"   Tracts with data: {len(merged_gdf[merged_gdf['poverty_rate'] > 0])}")
    print(f"   Average poverty rate: {merged_gdf['poverty_rate'].mean():.1f}%")
    
    # Also save a summary CSV
    summary_file = Path(OUTPUT_DIR) / f'poverty_summary_{state_abbr}_{data_year}.csv'
    summary_df = merged_gdf[['GEOID', 'NAME_y', 'total_pop', 'poverty_pop', 'poverty_rate', 'poverty_category']].copy()
    summary_df.to_csv(summary_file, index=False)
    print(f"📊 Summary CSV saved: {summary_file}")
    
    return merged_gdf

def create_qgis_style_file(state_abbr, data_year=2022):
    """
    Create a QGIS style file (.qml) for easy symbology
    """
    qml_content = """<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.0" styleCategories="AllStyleCategories">
  <renderer-v2 attr="poverty_rate" type="graduatedSymbol">
    <ranges>
      <range render="true" lower="0" upper="10" symbol="0" label="Very Low (0-10%)" />
      <range render="true" lower="10" upper="20" symbol="1" label="Low (10-20%)" />
      <range render="true" lower="20" upper="30" symbol="2" label="Moderate (20-30%)" />
      <range render="true" lower="30" upper="40" symbol="3" label="High (30-40%)" />
      <range render="true" lower="40" upper="100" symbol="4" label="Very High (40%+)" />
    </ranges>
    <symbols>
      <symbol type="fill" name="0" alpha="0.7">
        <layer class="SimpleFill">
          <prop k="color" v="255,255,204,179"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.1"/>
        </layer>
      </symbol>
      <symbol type="fill" name="1" alpha="0.7">
        <layer class="SimpleFill">
          <prop k="color" v="255,237,160,179"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.1"/>
        </layer>
      </symbol>
      <symbol type="fill" name="2" alpha="0.7">
        <layer class="SimpleFill">
          <prop k="color" v="254,178,76,179"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.1"/>
        </layer>
      </symbol>
      <symbol type="fill" name="3" alpha="0.7">
        <layer class="SimpleFill">
          <prop k="color" v="253,141,60,179"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.1"/>
        </layer>
      </symbol>
      <symbol type="fill" name="4" alpha="0.7">
        <layer class="SimpleFill">
          <prop k="color" v="227,26,28,179"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.1"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
</qgis>"""
    
    style_file = Path(OUTPUT_DIR) / f'poverty_tracts_{state_abbr}_{data_year}.qml'
    with open(style_file, 'w') as f:
        f.write(qml_content)
    
    print(f"🎨 QGIS style file created: {style_file}")

def main():
    """Main execution function"""
    print("🏠 Multi-State Poverty Data Census Tract Downloader")
    print("=" * 70)
    
    # States to process
    states = ['TX']  # Add 'NM' or 'CA','TX' to run multiple if you want to refresh New Mexico
    
    for state in states:
        print(f"\n{'='*50}")
        print(f"🎯 Processing {state}")
        print(f"{'='*50}")
        
        result = create_poverty_layer(state)
        
        if result is not None:
            create_qgis_style_file(state)
            print(f"\n✅ SUCCESS! {state} poverty data ready for QGIS!")
        else:
            print(f"\n❌ Failed to process {state}")
        
        print(f"\n⏸️ Pausing 2 seconds between states...")
        time.sleep(2)        
        print(f"\n📁 Files created in: {OUTPUT_DIR}")
        print("   • poverty_tracts_NM_2022.gpkg (Main geospatial layer)")
        print("   • poverty_summary_NM_2022.csv (Summary data)")
        print("   • poverty_tracts_NM_2022.qml (QGIS style file)")
        print("\n🗺️ To add to QGIS:")
        print("   1. Open QGIS")
        print("   2. Add the .gpkg file as a layer")
        print("   3. Right-click layer → Properties → Symbology → Load Style")
        print("   4. Select the .qml file for instant styling")
    else:
        print("\n❌ Failed to create poverty layer. Check error messages above.")

if __name__ == "__main__":
    main()

# Optional: Uncomment to also create data for other states
# print("\n" + "="*60)
# create_poverty_layer('CA')
# create_qgis_style_file('CA')