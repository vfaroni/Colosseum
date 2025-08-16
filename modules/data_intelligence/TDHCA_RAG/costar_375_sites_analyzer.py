#!/usr/bin/env python3
"""
CoStar 375 Sites Texas Land Analysis - Phase 1 QCT/DDA Screening
Analyzes CoStar export, adds Census Tracts, then runs comprehensive QCT/DDA analysis
"""

import pandas as pd
import json
import requests
import time
from datetime import datetime
from comprehensive_qct_dda_analyzer import ComprehensiveQCTDDAAnalyzer

class CoStar375SitesAnalyzer:
    """Analyze 375 CoStar Texas land sites with comprehensive QCT/DDA screening"""
    
    def __init__(self):
        self.costar_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/Costar_07312025/CS_Costar_TX_Land_8ac-30ac_07312025_ALL-export.xlsx"
        # Save to Colosseum data intelligence module
        self.output_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/Analysis_Results/"
        self.qct_dda_analyzer = ComprehensiveQCTDDAAnalyzer()
        # Use existing Census API key from CLAUDE.md
        self.census_api_key = "06ece0121263282cd9ffd753215b007b8f9a3dfc"
        
    def analyze_costar_structure(self):
        """First, analyze what's in the CoStar export"""
        print("🔍 ANALYZING COSTAR EXPORT STRUCTURE...")
        
        try:
            # Read the Excel file
            df = pd.read_excel(self.costar_file)
            
            print(f"✅ Loaded {len(df)} records from CoStar export")
            print(f"📊 Columns ({len(df.columns)}): {list(df.columns)}")
            print(f"📏 Data shape: {df.shape}")
            
            # Check for key location fields
            location_fields = []
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['lat', 'lon', 'address', 'city', 'county', 'zip', 'tract', 'fips']):
                    location_fields.append(col)
            
            print(f"🗺️ Location-related fields found: {location_fields}")
            
            # Sample first few records
            print("\n📋 SAMPLE DATA (First 3 records):")
            for i in range(min(3, len(df))):
                print(f"\nRecord {i+1}:")
                for field in location_fields[:8]:  # Show key fields
                    if field in df.columns:
                        print(f"  {field}: {df.iloc[i][field]}")
            
            return df, location_fields
            
        except Exception as e:
            print(f"❌ Error reading CoStar file: {e}")
            return None, None
    
    def add_census_tracts(self, df):
        """Add Census Tract information using Census Geocoding API"""
        print("\n🏛️ ADDING CENSUS TRACT DATA...")
        
        # Check if we already have tract info
        tract_fields = [col for col in df.columns if 'tract' in col.lower() or 'fips' in col.lower()]
        if tract_fields:
            print(f"⚠️ Found existing tract fields: {tract_fields}")
            response = input("Continue with Census Tract lookup anyway? (y/n): ")
            if response.lower() != 'y':
                return df
        
        # Initialize new columns
        df['Census_Tract_FIPS'] = ''
        df['Census_Tract_ID'] = ''
        df['Census_County_FIPS'] = ''
        df['Census_State_FIPS'] = ''
        df['Geocoding_Status'] = ''
        
        # Determine coordinate columns
        lat_col = None
        lon_col = None
        for col in df.columns:
            if 'lat' in col.lower() and not lat_col:
                lat_col = col
            elif 'lon' in col.lower() and not lon_col:
                lon_col = col
        
        if not lat_col or not lon_col:
            print("❌ Cannot find latitude/longitude columns for Census geocoding")
            return df
        
        print(f"📍 Using coordinates: {lat_col}, {lon_col}")
        
        successful_lookups = 0
        failed_lookups = 0
        
        for idx, row in df.iterrows():
            lat = row[lat_col]
            lon = row[lon_col]
            
            if pd.isna(lat) or pd.isna(lon):
                df.at[idx, 'Geocoding_Status'] = 'Missing Coordinates'
                failed_lookups += 1
                continue
            
            try:
                # Census Geocoding API call
                url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
                params = {
                    'x': lon,
                    'y': lat,
                    'benchmark': 'Public_AR_Current',
                    'vintage': 'Current_Current',
                    'format': 'json'
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('result', {}).get('geographies', {}).get('Census Tracts'):
                        tract_info = data['result']['geographies']['Census Tracts'][0]
                        
                        df.at[idx, 'Census_Tract_FIPS'] = tract_info.get('GEOID', '')
                        df.at[idx, 'Census_Tract_ID'] = tract_info.get('TRACT', '')
                        df.at[idx, 'Census_County_FIPS'] = tract_info.get('COUNTY', '')
                        df.at[idx, 'Census_State_FIPS'] = tract_info.get('STATE', '')
                        df.at[idx, 'Geocoding_Status'] = 'Success'
                        successful_lookups += 1
                        
                        print(f"✅ {idx+1}/{len(df)}: {tract_info.get('GEOID', 'Unknown')}")
                    else:
                        df.at[idx, 'Geocoding_Status'] = 'No Tract Found'
                        failed_lookups += 1
                        print(f"⚠️ {idx+1}/{len(df)}: No tract data returned")
                else:
                    df.at[idx, 'Geocoding_Status'] = f'API Error {response.status_code}'
                    failed_lookups += 1
                    print(f"❌ {idx+1}/{len(df)}: API Error {response.status_code}")
                
                # Rate limiting - Census API allows 1 request per second
                time.sleep(1.1)
                
            except Exception as e:
                df.at[idx, 'Geocoding_Status'] = f'Error: {str(e)[:50]}'
                failed_lookups += 1
                print(f"❌ {idx+1}/{len(df)}: {str(e)[:50]}")
        
        print(f"\n📊 CENSUS TRACT LOOKUP RESULTS:")
        print(f"✅ Successful: {successful_lookups}")
        print(f"❌ Failed: {failed_lookups}")
        print(f"📈 Success Rate: {successful_lookups/(successful_lookups+failed_lookups)*100:.1f}%")
        
        return df
    
    def run_qct_dda_analysis(self, df):
        """Run comprehensive QCT/DDA analysis on all sites"""
        print("\n🎯 RUNNING COMPREHENSIVE QCT/DDA ANALYSIS...")
        
        # Initialize QCT/DDA columns
        qct_dda_columns = [
            'QCT_Status', 'DDA_Status', 'Metro_Classification', 
            'Basis_Boost_Eligible', '130_Percent_Basis', 'AMI_Source',
            'Industry_Classification', 'QCT_Poverty_Rate', 'DDA_Rent_Ratio',
            'Analysis_Status'
        ]
        
        for col in qct_dda_columns:
            df[col] = ''
        
        # Determine coordinate columns
        lat_col = None
        lon_col = None
        for col in df.columns:
            if 'lat' in col.lower() and not lat_col:
                lat_col = col
            elif 'lon' in col.lower() and not lon_col:
                lon_col = col
        
        qct_eligible_count = 0
        dda_eligible_count = 0
        dual_eligible_count = 0
        
        for idx, row in df.iterrows():
            lat = row[lat_col]
            lon = row[lon_col]
            
            if pd.isna(lat) or pd.isna(lon):
                df.at[idx, 'Analysis_Status'] = 'Missing Coordinates'
                continue
            
            try:
                # Use comprehensive analyzer (covers all 4 HUD databases)
                result = self.qct_dda_analyzer.lookup_qct_status(lat, lon)
                
                # Extract results
                qct_status = result.get('qct_status', 'Not QCT')
                dda_status = result.get('dda_status', 'Not DDA')
                metro_type = result.get('metro_classification', 'Unknown')
                basis_boost = result.get('basis_boost_eligible', False)
                
                # Populate columns
                df.at[idx, 'QCT_Status'] = qct_status
                df.at[idx, 'DDA_Status'] = dda_status
                df.at[idx, 'Metro_Classification'] = metro_type
                df.at[idx, 'Basis_Boost_Eligible'] = 'YES' if basis_boost else 'NO'
                df.at[idx, '130_Percent_Basis'] = '130%' if basis_boost else '100%'
                
                # Determine AMI source
                if 'Metro' in metro_type:
                    df.at[idx, 'AMI_Source'] = 'Regional MSA AMI'
                else:
                    df.at[idx, 'AMI_Source'] = 'County AMI'
                
                # Industry classification
                if 'QCT' in qct_status and 'DDA' in dda_status:
                    classification = f"{metro_type} QCT + DDA"
                    dual_eligible_count += 1
                elif 'QCT' in qct_status:
                    classification = f"{metro_type} QCT"
                    qct_eligible_count += 1
                elif 'DDA' in dda_status:
                    classification = f"{metro_type} DDA"
                    dda_eligible_count += 1
                else:
                    classification = "No QCT/DDA"
                
                df.at[idx, 'Industry_Classification'] = classification
                df.at[idx, 'Analysis_Status'] = 'Success'
                
                # Additional data if available
                if 'poverty_rate' in result:
                    df.at[idx, 'QCT_Poverty_Rate'] = result['poverty_rate']
                if 'rent_ratio' in result:
                    df.at[idx, 'DDA_Rent_Ratio'] = result['rent_ratio']
                
                print(f"✅ {idx+1}/{len(df)}: {classification}")
                
            except Exception as e:
                df.at[idx, 'Analysis_Status'] = f'Error: {str(e)[:50]}'
                print(f"❌ {idx+1}/{len(df)}: {str(e)[:50]}")
        
        # Summary statistics
        total_eligible = qct_eligible_count + dda_eligible_count + dual_eligible_count
        
        print(f"\n📊 QCT/DDA ANALYSIS RESULTS:")
        print(f"🎯 QCT Only: {qct_eligible_count}")
        print(f"🎯 DDA Only: {dda_eligible_count}")
        print(f"🎯 QCT + DDA: {dual_eligible_count}")
        print(f"✅ Total Eligible: {total_eligible}")
        print(f"📈 Eligibility Rate: {total_eligible/len(df)*100:.1f}%")
        
        return df
    
    def apply_density_screening(self, df):
        """Apply Texas LIHTC density and unit count screening"""
        print("\n🏗️ APPLYING DENSITY & UNIT COUNT SCREENING...")
        
        # Find acres column
        acres_col = None
        for col in df.columns:
            if 'acre' in col.lower() or 'size' in col.lower():
                acres_col = col
                break
        
        if not acres_col:
            print("⚠️ Cannot find acres column - skipping density screening")
            return df
        
        print(f"📏 Using acres column: {acres_col}")
        
        # Add density analysis columns
        df['Max_Units_17_Acre'] = ''
        df['Max_Units_18_Acre'] = ''
        df['Density_Viable'] = ''
        df['Unit_Count_Assessment'] = ''
        
        viable_count = 0
        
        for idx, row in df.iterrows():
            try:
                acres = float(row[acres_col])
                
                max_units_17 = int(acres * 17)
                max_units_18 = int(acres * 18)
                
                df.at[idx, 'Max_Units_17_Acre'] = max_units_17
                df.at[idx, 'Max_Units_18_Acre'] = max_units_18
                
                # Texas market study requirement: 250+ units
                if max_units_18 >= 250:
                    df.at[idx, 'Density_Viable'] = 'YES'
                    viable_count += 1
                    
                    if max_units_18 >= 400:
                        df.at[idx, 'Unit_Count_Assessment'] = 'EXCELLENT (400+ units)'
                    elif max_units_18 >= 300:
                        df.at[idx, 'Unit_Count_Assessment'] = 'STRONG (300+ units)'
                    else:
                        df.at[idx, 'Unit_Count_Assessment'] = 'VIABLE (250+ units)'
                else:
                    df.at[idx, 'Density_Viable'] = 'NO - Too Small'
                    df.at[idx, 'Unit_Count_Assessment'] = f'UNDERSIZED ({max_units_18} units < 250 minimum)'
                
            except (ValueError, TypeError):
                df.at[idx, 'Density_Viable'] = 'ERROR - Invalid Acres'
                df.at[idx, 'Unit_Count_Assessment'] = 'Cannot Calculate'
        
        print(f"✅ Density Viable Sites: {viable_count}/{len(df)} ({viable_count/len(df)*100:.1f}%)")
        
        return df
    
    def export_results(self, df):
        """Export comprehensive analysis results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export full analysis
        excel_file = f"{self.output_path}CoStar_375_Sites_QCT_DDA_Analysis_{timestamp}.xlsx"
        df.to_excel(excel_file, index=False)
        print(f"💾 Full analysis saved: {excel_file}")
        
        # Create QCT/DDA eligible sites subset
        eligible_df = df[df['Basis_Boost_Eligible'] == 'YES'].copy()
        eligible_file = f"{self.output_path}CoStar_375_QCT_DDA_Eligible_Sites_{timestamp}.xlsx"
        eligible_df.to_excel(eligible_file, index=False)
        print(f"🎯 QCT/DDA eligible sites saved: {eligible_file}")
        
        # Create density viable + QCT/DDA eligible subset
        viable_eligible_df = df[(df['Basis_Boost_Eligible'] == 'YES') & (df['Density_Viable'] == 'YES')].copy()
        prime_file = f"{self.output_path}CoStar_375_PRIME_Investment_Sites_{timestamp}.xlsx"
        viable_eligible_df.to_excel(prime_file, index=False)
        print(f"🏆 PRIME investment sites saved: {prime_file}")
        
        # Summary statistics
        print(f"\n📊 FINAL ANALYSIS SUMMARY:")
        print(f"📋 Total Sites Analyzed: {len(df)}")
        print(f"🎯 QCT/DDA Eligible: {len(eligible_df)}")
        print(f"🏗️ Density Viable (250+ units): {len(df[df['Density_Viable'] == 'YES'])}")
        print(f"🏆 PRIME Sites (QCT/DDA + Density): {len(viable_eligible_df)}")
        
        return excel_file, eligible_file, prime_file
    
    def run_phase1_analysis(self):
        """Execute complete Phase 1 analysis workflow"""
        print("🚀 STARTING PHASE 1: COSTAR 375 SITES QCT/DDA ANALYSIS")
        print("=" * 60)
        
        # Step 1: Analyze CoStar structure
        df, location_fields = self.analyze_costar_structure()
        if df is None:
            return None
        
        # Step 2: Add Census Tracts if needed
        df = self.add_census_tracts(df)
        
        # Step 3: Run QCT/DDA analysis
        df = self.run_qct_dda_analysis(df)
        
        # Step 4: Apply density screening
        df = self.apply_density_screening(df)
        
        # Step 5: Export results
        files = self.export_results(df)
        
        print("\n🎯 PHASE 1 COMPLETE - Ready for M4 Beast Phase 2 Analysis")
        
        return df, files

if __name__ == "__main__":
    analyzer = CoStar375SitesAnalyzer()
    results = analyzer.run_phase1_analysis()