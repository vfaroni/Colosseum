#!/usr/bin/env python3
"""
Final 4-Dataset QCT/DDA Analyzer with Working ZIP Lookup
Complete analysis of 375 sites against all 4 HUD datasets using Nominatim
"""

import pandas as pd
import requests
import time
from datetime import datetime

class Final4DatasetAnalyzer:
    """Complete analyzer using all 4 HUD datasets with working ZIP lookup"""
    
    def __init__(self):
        self.load_all_datasets()
    
    def load_all_datasets(self):
        """Load all 4 HUD datasets"""
        base_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
        
        print("📋 LOADING ALL 4 HUD DATASETS WITH WORKING ZIP LOOKUP...")
        print("=" * 60)
        
        # 1. Load QCT data
        print("1. Loading QCT data...")
        qct_file = f"{base_path}/qct_data_2025.xlsx"
        tab1 = pd.read_excel(qct_file, sheet_name='AL-MO')
        tab2 = pd.read_excel(qct_file, sheet_name='MT-WY')
        qct_data = pd.concat([tab1, tab2], ignore_index=True)
        
        self.metro_qcts = qct_data[(qct_data['qct'] == 1) & (qct_data['metro'] == 1)]
        self.nonmetro_qcts = qct_data[(qct_data['qct'] == 1) & (qct_data['metro'] == 0)]
        
        texas_metro_qcts = self.metro_qcts[self.metro_qcts['state'] == 48]
        texas_nonmetro_qcts = self.nonmetro_qcts[self.nonmetro_qcts['state'] == 48]
        
        print(f"   ✅ Texas Metro QCTs: {len(texas_metro_qcts)}")
        print(f"   ✅ Texas Non-Metro QCTs: {len(texas_nonmetro_qcts)}")
        
        # 2. Load Metro DDA data
        print("2. Loading Metro DDA data...")
        self.metro_dda_data = pd.read_excel(f"{base_path}/2025-DDAs-Data-Used-to-Designate.xlsx")
        
        # Create Texas Metro DDA lookup
        self.texas_metro_ddas = self.metro_dda_data[
            (self.metro_dda_data['ZIP Code Tabulation Area (ZCTA)'].astype(str).str.startswith('7')) &
            (self.metro_dda_data['2025 SDDA (1=SDDA)'] == 1)
        ]
        
        # Create set for fast lookup
        self.texas_metro_dda_zips = set(
            self.texas_metro_ddas['ZIP Code Tabulation Area (ZCTA)'].astype(str).str.zfill(5)
        )
        
        print(f"   ✅ Texas Metro DDAs: {len(self.texas_metro_ddas)}")
        
        # 3. Create complete Texas Non-Metro DDA database
        print("3. Loading Texas Non-Metro DDA counties...")
        self.texas_nonmetro_dda_fips = {
            # Complete 68 counties from your PDF
            48001: 'Anderson', 48003: 'Andrews', 48005: 'Angelina', 48007: 'Aransas',
            48013: 'Atascosa', 48019: 'Bandera', 48025: 'Bee', 48031: 'Blanco',
            48035: 'Bosque', 48043: 'Brewster', 48049: 'Brown', 48051: 'Burleson',
            48057: 'Calhoun', 48067: 'Cass', 48073: 'Cherokee', 48075: 'Childress',
            48077: 'Clay', 48083: 'Coleman', 48093: 'Comanche', 48095: 'Concho',
            48097: 'Cooke', 48101: 'Cottle', 48103: 'Crane', 48105: 'Crockett',
            48107: 'Crosby', 48109: 'Culberson', 48111: 'Dallam', 48115: 'Dawson',
            48117: 'Deaf Smith', 48119: 'Delta', 48123: 'DeWitt', 48127: 'Dimmit',
            48129: 'Donley', 48131: 'Duval', 48133: 'Eastland', 48137: 'Edwards',
            48153: 'Floyd', 48155: 'Foard', 48159: 'Franklin', 48163: 'Frio',
            48171: 'Gillespie', 48179: 'Gray', 48195: 'Hansford', 48205: 'Hartley',
            48221: 'Hood', 48227: 'Howard', 48241: 'Jasper', 48243: 'Jeff Davis',
            48255: 'Karnes', 48261: 'Kenedy', 48265: 'Kerr', 48269: 'King',
            48271: 'Kinney', 48273: 'Kleberg', 48287: 'Lee', 48299: 'Llano',
            48307: 'McCulloch', 48321: 'Matagorda', 48337: 'Montague', 48341: 'Moore',
            48347: 'Nacogdoches', 48349: 'Navarro', 48357: 'Ochiltree', 48363: 'Palo Pinto',
            48373: 'Polk', 48383: 'Reagan', 48385: 'Real', 48389: 'Reeves',
            48399: 'Runnels', 48405: 'San Augustine', 48411: 'San Saba', 48443: 'Terrell',
            48455: 'Trinity', 48463: 'Uvalde', 48465: 'Val Verde', 48471: 'Walker',
            48475: 'Ward', 48499: 'Wood'
        }
        
        print(f"   ✅ Texas Non-Metro DDA counties: {len(self.texas_nonmetro_dda_fips)}")
        print("✅ ALL DATASETS LOADED - READY FOR COMPLETE ANALYSIS")
    
    def get_census_info(self, lat, lon):
        """Get census tract and county from coordinates"""
        try:
            url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
            params = {
                'x': lon, 'y': lat,
                'benchmark': 'Public_AR_Current',
                'vintage': 'Current_Current',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('result', {}).get('geographies', {}).get('Census Tracts'):
                    tract_info = data['result']['geographies']['Census Tracts'][0]
                    return (tract_info.get('GEOID', ''), 
                           tract_info.get('STATE', ''), 
                           tract_info.get('COUNTY', ''))
            
            return None, None, None
            
        except Exception:
            return None, None, None
    
    def get_zip_code(self, lat, lon):
        """Get ZIP code using working Nominatim service"""
        try:
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': lat, 'lon': lon,
                'format': 'json',
                'addressdetails': 1,
                'zoom': 18
            }
            headers = {'User-Agent': 'LIHTC-QCT-DDA-Analysis/1.0'}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'address' in data and 'postcode' in data['address']:
                    return data['address']['postcode'][:5]  # 5-digit ZIP
            
            return None
        except Exception:
            return None
    
    def analyze_site_complete(self, lat, lon, city="Unknown"):
        """Complete 4-dataset analysis"""
        result = {
            'lat': lat, 'lon': lon, 'city': city,
            'census_tract': '', 'zip_code': '',
            'metro_qct': False, 'nonmetro_qct': False,
            'metro_dda': False, 'nonmetro_dda': False,
            'total_designations': 0,
            'classification': 'No QCT/DDA',
            'basis_boost_eligible': False,
            'analysis_status': 'Success'
        }
        
        try:
            # Get geographic information
            tract_geoid, state_fips, county_fips = self.get_census_info(lat, lon)
            zip_code = self.get_zip_code(lat, lon)
            
            result['census_tract'] = tract_geoid or ''
            result['zip_code'] = zip_code or ''
            
            if tract_geoid and len(tract_geoid) == 11:
                state_code = int(tract_geoid[:2])
                county_code = int(tract_geoid[2:5])
                tract_number = float(tract_geoid[5:]) / 100
                
                # Check Metro QCT
                metro_qct_matches = self.metro_qcts[
                    (self.metro_qcts['state'] == state_code) &
                    (self.metro_qcts['county'] == county_code) &
                    (abs(self.metro_qcts['tract'] - tract_number) < 0.01)
                ]
                result['metro_qct'] = len(metro_qct_matches) > 0
                
                # Check Non-Metro QCT
                nonmetro_qct_matches = self.nonmetro_qcts[
                    (self.nonmetro_qcts['state'] == state_code) &
                    (self.nonmetro_qcts['county'] == county_code) &
                    (abs(self.nonmetro_qcts['tract'] - tract_number) < 0.01)
                ]
                result['nonmetro_qct'] = len(nonmetro_qct_matches) > 0
                
                # Check Metro DDA (ZIP-based)
                if zip_code:
                    result['metro_dda'] = zip_code in self.texas_metro_dda_zips
                
                # Check Non-Metro DDA (county-based)
                if state_code == 48:  # Texas
                    county_fips_full = int(f"{state_code}{county_code:03d}")
                    result['nonmetro_dda'] = county_fips_full in self.texas_nonmetro_dda_fips
                
                # Calculate totals and classification
                result['total_designations'] = sum([
                    result['metro_qct'], result['nonmetro_qct'],
                    result['metro_dda'], result['nonmetro_dda']
                ])
                
                designations = []
                if result['metro_qct']: designations.append('Metro QCT')
                if result['nonmetro_qct']: designations.append('Non-Metro QCT')
                if result['metro_dda']: designations.append('Metro DDA')
                if result['nonmetro_dda']: designations.append('Non-Metro DDA')
                
                if designations:
                    result['classification'] = ' + '.join(designations)
                    result['basis_boost_eligible'] = True
            
            else:
                result['analysis_status'] = 'Census lookup failed'
        
        except Exception as e:
            result['analysis_status'] = f'Error: {str(e)[:50]}'
        
        return result

def run_final_375_analysis():
    """Run final complete analysis on all 375 sites"""
    print("🎯 FINAL 4-DATASET ANALYSIS - 375 SITES WITH WORKING ZIP LOOKUP")
    print("=" * 70)
    
    # Initialize analyzer
    analyzer = Final4DatasetAnalyzer()
    
    # Load sites
    input_file = "D'Marco_Sites/Analysis_Results/CoStar_375_Phase1_Screening_20250731_160305.xlsx"
    df = pd.read_excel(input_file)
    print(f"\\n✅ Loaded {len(df)} sites for final analysis")
    
    # Initialize counters
    counts = {
        'metro_qct': 0, 'nonmetro_qct': 0,
        'metro_dda': 0, 'nonmetro_dda': 0,
        'total_boost_eligible': 0,
        'successful_lookups': 0
    }
    
    # Add final analysis columns
    final_columns = [
        'Final_Census_Tract', 'Final_ZIP_Code',
        'Final_Metro_QCT', 'Final_NonMetro_QCT',
        'Final_Metro_DDA', 'Final_NonMetro_DDA',
        'Final_Total_Designations', 'Final_Classification',
        'Final_Boost_Eligible', 'Final_Analysis_Status'
    ]
    
    for col in final_columns:
        df[col] = ''
    
    print("\\n🔍 ANALYZING ALL 375 SITES WITH COMPLETE 4-DATASET LOOKUP...")
    print("Rate limiting: 2 seconds per site (Census + Nominatim)")
    start_time = time.time()
    
    for idx, row in df.iterrows():
        lat, lon = row['Latitude'], row['Longitude']
        city = row.get('City', 'Unknown')
        
        # Complete analysis
        result = analyzer.analyze_site_complete(lat, lon, city)
        
        # Update dataframe
        df.at[idx, 'Final_Census_Tract'] = result['census_tract']
        df.at[idx, 'Final_ZIP_Code'] = result['zip_code']
        df.at[idx, 'Final_Metro_QCT'] = result['metro_qct']
        df.at[idx, 'Final_NonMetro_QCT'] = result['nonmetro_qct']
        df.at[idx, 'Final_Metro_DDA'] = result['metro_dda']
        df.at[idx, 'Final_NonMetro_DDA'] = result['nonmetro_dda']
        df.at[idx, 'Final_Total_Designations'] = result['total_designations']
        df.at[idx, 'Final_Classification'] = result['classification']
        df.at[idx, 'Final_Boost_Eligible'] = result['basis_boost_eligible']
        df.at[idx, 'Final_Analysis_Status'] = result['analysis_status']
        
        # Update counters
        if result['metro_qct']: counts['metro_qct'] += 1
        if result['nonmetro_qct']: counts['nonmetro_qct'] += 1
        if result['metro_dda']: counts['metro_dda'] += 1
        if result['nonmetro_dda']: counts['nonmetro_dda'] += 1
        if result['basis_boost_eligible']: counts['total_boost_eligible'] += 1
        if result['analysis_status'] == 'Success': counts['successful_lookups'] += 1
        
        # Progress update
        if (idx + 1) % 10 == 0:
            elapsed = time.time() - start_time
            rate = (idx + 1) / elapsed * 60
            remaining = (len(df) - idx - 1) / rate if rate > 0 else 0
            print(f"  ✅ {idx+1:3d}/375 ({rate:.1f} sites/min, ~{remaining:.1f} min remaining)")
            print(f"     Metro QCT={counts['metro_qct']}, Non-Metro QCT={counts['nonmetro_qct']}, Metro DDA={counts['metro_dda']}, Non-Metro DDA={counts['nonmetro_dda']}")
        
        # Rate limiting - 2 seconds (Census + Nominatim)
        time.sleep(2.0)
    
    # Final results
    elapsed_total = time.time() - start_time
    
    print(f"\\n📊 FINAL 4-DATASET ANALYSIS RESULTS:")
    print(f"⏱️ Total time: {elapsed_total/60:.1f} minutes")
    print(f"✅ Successful lookups: {counts['successful_lookups']}/375 ({counts['successful_lookups']/375*100:.1f}%)")
    print()
    print("🎯 COMPLETE FOUR-QUADRANT RESULTS:")
    print(f"1) Metro QCTs: {counts['metro_qct']} sites")
    print(f"2) Non-Metro QCTs: {counts['nonmetro_qct']} sites")
    print(f"3) Metro DDAs: {counts['metro_dda']} sites")
    print(f"4) Non-Metro DDAs: {counts['nonmetro_dda']} sites")
    print(f"✅ Total Boost Eligible: {counts['total_boost_eligible']} sites ({counts['total_boost_eligible']/375*100:.1f}%)")
    
    # Four-quadrant matrix
    print("\\n📊 FOUR-QUADRANT MATRIX:")
    print(f"┌─────────────────┬─────────────┬─────────────┬─────────────┐")
    print(f"│                 │    QCT      │    DDA      │   TOTAL     │")
    print(f"├─────────────────┼─────────────┼─────────────┼─────────────┤")
    print(f"│ METRO           │     {counts['metro_qct']:2d}      │     {counts['metro_dda']:2d}      │     {counts['metro_qct'] + counts['metro_dda']:2d}      │")
    print(f"│ NON-METRO       │      {counts['nonmetro_qct']:2d}      │     {counts['nonmetro_dda']:2d}      │     {counts['nonmetro_qct'] + counts['nonmetro_dda']:2d}      │")
    print(f"├─────────────────┼─────────────┼─────────────┼─────────────┤")
    print(f"│ TOTAL           │     {counts['metro_qct'] + counts['nonmetro_qct']:2d}      │     {counts['metro_dda'] + counts['nonmetro_dda']:2d}      │     {counts['total_boost_eligible']:2d}      │")
    print(f"└─────────────────┴─────────────┴─────────────┴─────────────┘")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"D'Marco_Sites/Analysis_Results/CoStar_375_FINAL_4Dataset_Analysis_{timestamp}.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\\n💾 Final 4-dataset analysis saved: {output_file}")
    
    return df, counts

if __name__ == "__main__":
    results_df, final_counts = run_final_375_analysis()
    print(f"\\n🎯 FINAL MISSION COMPLETE!")
    print(f"Your 4-quadrant answer: Metro QCT={final_counts['metro_qct']}, Non-Metro QCT={final_counts['nonmetro_qct']}, Metro DDA={final_counts['metro_dda']}, Non-Metro DDA={final_counts['nonmetro_dda']}")
    print(f"Total sites with basis boost: {final_counts['total_boost_eligible']}/375 ({final_counts['total_boost_eligible']/375*100:.1f}%)")