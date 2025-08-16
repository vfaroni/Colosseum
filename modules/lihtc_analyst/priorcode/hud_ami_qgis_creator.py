#!/usr/bin/env python3
"""
HUD AMI to QGIS Converter
Creates national and state-specific HUD AMI datasets with county boundaries
"""

import os
import requests
import pandas as pd
import geopandas as gpd
import zipfile
import tempfile
from pathlib import Path
import urllib3
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HudAmiQgisCreator:
    def __init__(self, hud_ami_file_path, base_data_dir):
        """Initialize HUD AMI to QGIS converter"""
        self.hud_ami_file = Path(hud_ami_file_path)
        self.base_data_dir = Path(base_data_dir)
        
        # Create HUD AMI directory structure
        self.hud_dir = self.base_data_dir / "HUD_AMI_Geographic"
        self.hud_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.national_dir = self.hud_dir / "National"
        self.states_dir = self.hud_dir / "States"
        self.national_dir.mkdir(exist_ok=True)
        self.states_dir.mkdir(exist_ok=True)
        
        # Data containers
        self.ami_data = None
        self.county_boundaries = None
        
        print(f"🏗️ HUD AMI to QGIS Converter initialized")
        print(f"   HUD AMI File: {self.hud_ami_file}")
        print(f"   Output Directory: {self.hud_dir}")
        print(f"   National Data: {self.national_dir}")
        print(f"   State Data: {self.states_dir}")
    
    def load_hud_ami_data(self):
        """Load and process HUD AMI data"""
        print(f"\n📊 Loading HUD AMI data...")
        
        try:
            # Load the AMI data
            df = pd.read_excel(self.hud_ami_file, sheet_name="MTSP2025-Static")
            print(f"✅ Loaded {len(df)} total AMI records")
            
            # Clean and prepare data
            df['fips'] = df['fips'].astype(str).str.zfill(5)  # Ensure 5-digit FIPS
            df['county_fips'] = df['fips'].str[:5]  # Extract county FIPS
            
            # Create comprehensive AMI dataset
            ami_columns = {
                'fips': 'fips',
                'county_fips': 'county_fips', 
                'stusps': 'state_abbr',
                'County_Name': 'county_name',
                'hud_area_name': 'hud_area_name',
                'metro': 'is_metro',
                'median2025': 'median_ami_2025',
                
                # Income limits (4-person household focus)
                'lim50_25p4': 'income_50pct_4p',
                'lim60_25p4': 'income_60pct_4p', 
                'lim80_25p4': 'income_80pct_4p',
                
                # Rent limits (key bedroom counts)
                'Studio 50%': 'rent_studio_50pct',
                '1BR 50%': 'rent_1br_50pct',
                '2BR 50%': 'rent_2br_50pct',
                '3BR 50%': 'rent_3br_50pct',
                
                'Studio 60%': 'rent_studio_60pct',
                '1BR 60%': 'rent_1br_60pct', 
                '2BR 60%': 'rent_2br_60pct',
                '3BR 60%': 'rent_3br_60pct',
                
                'Studio 80%': 'rent_studio_80pct',
                '1BR 80%': 'rent_1br_80pct',
                '2BR 80%': 'rent_2br_80pct',
                '3BR 80%': 'rent_3br_80pct'
            }
            
            # Select and rename columns
            available_cols = {old: new for old, new in ami_columns.items() if old in df.columns}
            self.ami_data = df[list(available_cols.keys())].rename(columns=available_cols)
            
            # Add derived fields for analysis
            self.ami_data['ami_category'] = pd.cut(
                self.ami_data['median_ami_2025'],
                bins=[0, 50000, 75000, 100000, 125000, float('inf')],
                labels=['Very Low (<$50K)', 'Low ($50-75K)', 'Moderate ($75-100K)', 'High ($100-125K)', 'Very High (>$125K)']
            )
            
            self.ami_data['metro_status'] = self.ami_data['is_metro'].map({1: 'Metropolitan', 0: 'Non-Metropolitan'})
            
            print(f"✅ Processed AMI data: {len(self.ami_data)} records")
            print(f"   States included: {sorted(self.ami_data['state_abbr'].unique())}")
            print(f"   Metro areas: {self.ami_data['is_metro'].sum()}")
            print(f"   Non-metro areas: {(~self.ami_data['is_metro'].astype(bool)).sum()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading HUD AMI data: {e}")
            return False
    
    def download_county_boundaries(self):
        """Download US county boundaries from Census TIGER"""
        print(f"\n🗺️ Downloading US county boundaries...")
        
        # Census TIGER URL for 2023 counties
        tiger_url = "https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip"
        
        try:
            # Download with SSL bypass
            print(f"📥 Downloading: {tiger_url}")
            response = requests.get(tiger_url, verify=False, stream=True, timeout=120)
            response.raise_for_status()
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_file.write(chunk)
            temp_file.close()
            
            print(f"✅ Downloaded county boundaries")
            
            # Read shapefile from zip
            counties_gdf = gpd.read_file(temp_file.name)
            
            # Clean up temp file
            os.unlink(temp_file.name)
            
            # Process county data
            counties_gdf['county_fips'] = counties_gdf['GEOID'].astype(str)
            counties_gdf['state_fips'] = counties_gdf['STATEFP'].astype(str)
            counties_gdf['county_name_census'] = counties_gdf['NAME'].astype(str)
            
            # Ensure WGS84 projection
            if counties_gdf.crs != 'EPSG:4326':
                counties_gdf = counties_gdf.to_crs('EPSG:4326')
            
            # Simplify geometries for better performance (optional)
            counties_gdf['geometry'] = counties_gdf.geometry.simplify(0.01, preserve_topology=True)
            
            self.county_boundaries = counties_gdf
            
            print(f"✅ Processed {len(counties_gdf)} county boundaries")
            print(f"   CRS: {counties_gdf.crs}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error downloading county boundaries: {e}")
            return False
    
    def merge_ami_with_boundaries(self):
        """Merge HUD AMI data with county boundaries"""
        print(f"\n🔗 Merging AMI data with county boundaries...")
        
        if self.ami_data is None or self.county_boundaries is None:
            print("❌ Missing AMI data or county boundaries")
            return None
        
        try:
            # Merge on county FIPS codes
            merged_gdf = self.county_boundaries.merge(
                self.ami_data,
                on='county_fips',
                how='left'  # Keep all counties, even those without AMI data
            )
            
            print(f"✅ Merged data: {len(merged_gdf)} counties")
            
            # Check merge success
            has_ami_data = merged_gdf['median_ami_2025'].notna().sum()
            print(f"   Counties with AMI data: {has_ami_data}")
            print(f"   Counties without AMI data: {len(merged_gdf) - has_ami_data}")
            
            # Add data quality flag
            merged_gdf['has_ami_data'] = merged_gdf['median_ami_2025'].notna()
            
            return merged_gdf
            
        except Exception as e:
            print(f"❌ Error merging data: {e}")
            return None
    
    def create_national_dataset(self, merged_gdf):
        """Create and save national HUD AMI dataset"""
        print(f"\n🇺🇸 Creating national HUD AMI dataset...")
        
        try:
            # Save national dataset
            national_file = self.national_dir / "us_counties_hud_ami_2025.gpkg"
            merged_gdf.to_file(national_file, driver='GPKG')
            
            print(f"✅ National dataset saved: {national_file}")
            print(f"   Size: {len(merged_gdf)} counties")
            
            # Create national summary
            summary_stats = {
                'total_counties': len(merged_gdf),
                'counties_with_ami': merged_gdf['has_ami_data'].sum(),
                'median_ami_national': merged_gdf['median_ami_2025'].median(),
                'states_covered': merged_gdf['state_abbr'].nunique(),
                'metro_counties': merged_gdf['is_metro'].sum(),
                'non_metro_counties': len(merged_gdf) - merged_gdf['is_metro'].sum()
            }
            
            # Save summary
            summary_file = self.national_dir / "national_ami_summary.txt"
            with open(summary_file, 'w') as f:
                f.write("National HUD AMI Dataset Summary\n")
                f.write("=" * 40 + "\n\n")
                for key, value in summary_stats.items():
                    f.write(f"{key.replace('_', ' ').title()}: {value:,}\n")
            
            # Create national styling
            self.create_ami_styles(national_file)
            
            print(f"📊 National summary saved: {summary_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating national dataset: {e}")
            return False
    
    def create_state_datasets(self, merged_gdf, states=['NM']):
        """Create state-specific datasets"""
        print(f"\n🗺️ Creating state-specific datasets...")
        
        state_files = {}
        
        for state_abbr in states:
            try:
                print(f"  📍 Processing {state_abbr}...")
                
                # Filter for state
                state_gdf = merged_gdf[merged_gdf['state_abbr'] == state_abbr].copy()
                
                if len(state_gdf) == 0:
                    print(f"  ⚠️ No data found for {state_abbr}")
                    continue
                
                # Save state dataset
                state_file = self.states_dir / f"{state_abbr.lower()}_counties_hud_ami_2025.gpkg"
                state_gdf.to_file(state_file, driver='GPKG')
                
                state_files[state_abbr] = state_file
                
                print(f"  ✅ {state_abbr} dataset saved: {state_file}")
                print(f"     Counties: {len(state_gdf)}")
                print(f"     With AMI data: {state_gdf['has_ami_data'].sum()}")
                
                if state_gdf['has_ami_data'].any():
                    avg_ami = state_gdf['median_ami_2025'].mean()
                    print(f"     Average AMI: ${avg_ami:,.0f}")
                
                # Create state-specific styling
                self.create_ami_styles(state_file, state_name=state_abbr)
                
                # Create state summary
                state_summary = self.create_state_summary(state_gdf, state_abbr)
                
            except Exception as e:
                print(f"  ❌ Error processing {state_abbr}: {e}")
                continue
        
        return state_files
    
    def create_state_summary(self, state_gdf, state_abbr):
        """Create detailed state summary"""
        try:
            summary_file = self.states_dir / f"{state_abbr.lower()}_ami_summary.txt"
            
            with open(summary_file, 'w') as f:
                f.write(f"{state_abbr} HUD AMI Dataset Summary\n")
                f.write("=" * 40 + "\n\n")
                
                f.write(f"Total Counties: {len(state_gdf)}\n")
                f.write(f"Counties with AMI Data: {state_gdf['has_ami_data'].sum()}\n")
                
                if state_gdf['has_ami_data'].any():
                    ami_data = state_gdf[state_gdf['has_ami_data']]
                    
                    f.write(f"\nAMI STATISTICS:\n")
                    f.write(f"Average Median AMI: ${ami_data['median_ami_2025'].mean():,.0f}\n")
                    f.write(f"Highest AMI: ${ami_data['median_ami_2025'].max():,.0f}\n")
                    f.write(f"Lowest AMI: ${ami_data['median_ami_2025'].min():,.0f}\n")
                    
                    f.write(f"\nRENT LIMITS (1-Bedroom at 60% AMI):\n")
                    f.write(f"Average: ${ami_data['rent_1br_60pct'].mean():.0f}\n")
                    f.write(f"Highest: ${ami_data['rent_1br_60pct'].max():.0f}\n")
                    f.write(f"Lowest: ${ami_data['rent_1br_60pct'].min():.0f}\n")
                    
                    f.write(f"\nMETRO STATUS:\n")
                    metro_counts = ami_data['metro_status'].value_counts()
                    for status, count in metro_counts.items():
                        f.write(f"{status}: {count} counties\n")
                    
                    f.write(f"\nCOUNTIES BY AMI LEVEL:\n")
                    ami_categories = ami_data['ami_category'].value_counts()
                    for category, count in ami_categories.items():
                        f.write(f"{category}: {count} counties\n")
            
            print(f"  📊 {state_abbr} summary saved: {summary_file}")
            return summary_file
            
        except Exception as e:
            print(f"  ⚠️ Error creating {state_abbr} summary: {e}")
            return None
    
    def create_ami_styles(self, gpkg_file, state_name=None):
        """Create QGIS style files for AMI visualization"""
        base_name = gpkg_file.stem
        qml_dir = gpkg_file.parent
        
        # Style 1: Median AMI levels
        ami_qml = qml_dir / f"{base_name}_median_ami.qml"
        ami_style = '''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.0" styleCategories="AllStyleCategories">
  <renderer-v2 attr="median_ami_2025" type="graduatedSymbol">
    <ranges>
      <range render="true" lower="0" upper="50000" symbol="0" label="Very Low (<$50K)" />
      <range render="true" lower="50000" upper="75000" symbol="1" label="Low ($50-75K)" />
      <range render="true" lower="75000" upper="100000" symbol="2" label="Moderate ($75-100K)" />
      <range render="true" lower="100000" upper="125000" symbol="3" label="High ($100-125K)" />
      <range render="true" lower="125000" upper="500000" symbol="4" label="Very High (>$125K)" />
    </ranges>
    <symbols>
      <symbol type="fill" name="0" alpha="0.8">
        <layer class="SimpleFill">
          <prop k="color" v="215,48,39,204"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.2"/>
        </layer>
      </symbol>
      <symbol type="fill" name="1" alpha="0.8">
        <layer class="SimpleFill">
          <prop k="color" v="244,109,67,204"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.2"/>
        </layer>
      </symbol>
      <symbol type="fill" name="2" alpha="0.8">
        <layer class="SimpleFill">
          <prop k="color" v="253,174,97,204"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.2"/>
        </layer>
      </symbol>
      <symbol type="fill" name="3" alpha="0.8">
        <layer class="SimpleFill">
          <prop k="color" v="171,217,233,204"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.2"/>
        </layer>
      </symbol>
      <symbol type="fill" name="4" alpha="0.8">
        <layer class="SimpleFill">
          <prop k="color" v="69,117,180,204"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.2"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
</qgis>'''
        
        with open(ami_qml, 'w') as f:
            f.write(ami_style)
        
        # Style 2: Metro vs Non-Metro
        metro_qml = qml_dir / f"{base_name}_metro_status.qml"
        metro_style = '''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.0" styleCategories="AllStyleCategories">
  <renderer-v2 attr="metro_status" type="categorizedSymbol">
    <categories>
      <category render="true" value="Metropolitan" symbol="0" label="Metropolitan Areas" />
      <category render="true" value="Non-Metropolitan" symbol="1" label="Non-Metropolitan Areas" />
    </categories>
    <symbols>
      <symbol type="fill" name="0" alpha="0.8">
        <layer class="SimpleFill">
          <prop k="color" v="27,158,119,204"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.2"/>
        </layer>
      </symbol>
      <symbol type="fill" name="1" alpha="0.8">
        <layer class="SimpleFill">
          <prop k="color" v="217,95,2,204"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.2"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
</qgis>'''
        
        with open(metro_qml, 'w') as f:
            f.write(metro_style)
        
        # Style 3: Rent Limits (1BR at 60% AMI)
        rent_qml = qml_dir / f"{base_name}_rent_limits.qml"
        rent_style = '''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.0" styleCategories="AllStyleCategories">
  <renderer-v2 attr="rent_1br_60pct" type="graduatedSymbol">
    <ranges>
      <range render="true" lower="0" upper="800" symbol="0" label="Low Rent (<$800)" />
      <range render="true" lower="800" upper="1200" symbol="1" label="Moderate Rent ($800-1200)" />
      <range render="true" lower="1200" upper="1600" symbol="2" label="High Rent ($1200-1600)" />
      <range render="true" lower="1600" upper="2000" symbol="3" label="Very High Rent ($1600-2000)" />
      <range render="true" lower="2000" upper="10000" symbol="4" label="Extremely High Rent (>$2000)" />
    </ranges>
    <symbols>
      <symbol type="fill" name="0" alpha="0.8">
        <layer class="SimpleFill">
          <prop k="color" v="255,255,204,204"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.2"/>
        </layer>
      </symbol>
      <symbol type="fill" name="1" alpha="0.8">
        <layer class="SimpleFill">
          <prop k="color" v="161,218,180,204"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.2"/>
        </layer>
      </symbol>
      <symbol type="fill" name="2" alpha="0.8">
        <layer class="SimpleFill">
          <prop k="color" v="65,182,196,204"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.2"/>
        </layer>
      </symbol>
      <symbol type="fill" name="3" alpha="0.8">
        <layer class="SimpleFill">
          <prop k="color" v="44,127,184,204"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.2"/>
        </layer>
      </symbol>
      <symbol type="fill" name="4" alpha="0.8">
        <layer class="SimpleFill">
          <prop k="color" v="37,52,148,204"/>
          <prop k="outline_color" v="128,128,128,255"/>
          <prop k="outline_width" v="0.2"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
</qgis>'''
        
        with open(rent_qml, 'w') as f:
            f.write(rent_style)
        
        print(f"  🎨 Created 3 style files for {base_name}")
        return [ami_qml, metro_qml, rent_qml]
    
    def create_comprehensive_report(self, national_file, state_files):
        """Create comprehensive analysis report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.hud_dir / f"hud_ami_qgis_report_{timestamp}.txt"
        
        report = f"""HUD AMI to QGIS Conversion Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
=====================================================

OVERVIEW:
This process converted HUD AMI Excel data into QGIS-ready geospatial datasets
by merging with US Census county boundaries.

FILES CREATED:

NATIONAL DATASET:
• {national_file.name} - Complete US counties with AMI data
• {national_file.stem}_median_ami.qml - AMI level styling
• {national_file.stem}_metro_status.qml - Metro vs non-metro styling  
• {national_file.stem}_rent_limits.qml - Rent limit styling

STATE DATASETS:
"""
        
        for state, file_path in state_files.items():
            report += f"• {file_path.name} - {state} counties with AMI data\n"
            report += f"• {file_path.stem}_*.qml - Three styling options\n"
        
        report += f"""

QGIS USAGE INSTRUCTIONS:

1. LOAD DATA:
   - Open QGIS
   - Add Vector Layer → Select .gpkg files
   - National file for comprehensive analysis
   - State files for focused analysis

2. APPLY STYLING:
   - Right-click layer → Properties → Symbology
   - Click "Style" (bottom) → Load Style
   - Select appropriate .qml file:
     * _median_ami.qml: Color by AMI levels
     * _metro_status.qml: Metro vs non-metro
     * _rent_limits.qml: Color by 1BR rent limits

3. ANALYSIS CAPABILITIES:
   - Visualize AMI levels across regions
   - Compare metro vs non-metro AMI patterns
   - Identify high/low rent limit areas
   - Layer with poverty data for gap analysis
   - Overlay with LIHTC projects
   - Buffer analysis around infrastructure

4. DATA FIELDS AVAILABLE:
   - median_ami_2025: Median AMI for area
   - rent_*br_*pct: Rent limits by bedroom/AMI %
   - income_*pct_4p: Income limits for 4-person household
   - is_metro: Metropolitan area flag
   - ami_category: AMI level categorization
   - has_ami_data: Data availability flag

LIHTC APPLICATION:
• Identify opportunity zones with favorable AMI levels
• Compare local AMI to poverty rates
• Analyze rent limit feasibility for developments
• Evaluate metro vs non-metro development strategies
• Layer with QCT/DDA boundaries for comprehensive scoring

NEXT STEPS:
• Load both national and state files into QGIS
• Experiment with different styling options
• Create custom symbology for specific analysis needs
• Combine with existing infrastructure and poverty datasets
"""
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"📋 Comprehensive report saved: {report_file}")
        return report_file

def main():
    """Main execution function"""
    print("🏠 HUD AMI to QGIS Converter")
    print("=" * 50)
    
    # File paths
    hud_ami_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx"
    base_data_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets"
    
    # Initialize converter
    converter = HudAmiQgisCreator(hud_ami_file, base_data_dir)
    
    try:
        # Step 1: Load HUD AMI data
        if not converter.load_hud_ami_data():
            return
        
        # Step 2: Download county boundaries
        if not converter.download_county_boundaries():
            return
        
        # Step 3: Merge data
        merged_gdf = converter.merge_ami_with_boundaries()
        if merged_gdf is None:
            return
        
        # Step 4: Create national dataset
        if not converter.create_national_dataset(merged_gdf):
            return
        
        # Step 5: Create state datasets (focus on New Mexico)
        state_files = converter.create_state_datasets(merged_gdf, states=['NM', 'CA', 'TX', 'AZ', 'HI'])
        
        # Step 6: Create comprehensive report
        national_file = converter.national_dir / "us_counties_hud_ami_2025.gpkg"
        report_file = converter.create_comprehensive_report(national_file, state_files)
        
        print("\n" + "=" * 50)
        print("✅ HUD AMI TO QGIS CONVERSION COMPLETE!")
        print("=" * 50)
        
        print(f"\n📁 Files created in: {converter.hud_dir}")
        print(f"🇺🇸 National dataset: {national_file}")
        
        for state, file_path in state_files.items():
            print(f"🗺️ {state} dataset: {file_path}")
        
        print(f"\n🎨 Multiple .qml style files created for each dataset")
        print(f"📋 Comprehensive report: {report_file}")
        
        print(f"\n🗺️ READY FOR QGIS:")
        print("   1. Open QGIS and add .gpkg files")
        print("   2. Load .qml styles for instant visualization")
        print("   3. Layer with poverty data and infrastructure")
        print("   4. Analyze AMI patterns for LIHTC opportunities")
        
    except Exception as e:
        print(f"\n❌ Error during conversion: {e}")
        print("Check file paths and network connection.")

if __name__ == "__main__":
    main()
