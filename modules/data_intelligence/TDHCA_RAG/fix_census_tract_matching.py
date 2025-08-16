#!/usr/bin/env python3
"""
FIX CENSUS TRACT MATCHING
Proper FIPS alignment for ACS poverty data matching
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path

class CensusTractFIPSMatcher:
    """Fix census tract matching using proper FIPS codes"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
        self.qct_dda_file = self.base_dir / "D'Marco_Sites/Analysis_Results/MASTER_155_BoostEligible_Sites_20250731_223500.xlsx"
        self.acs_poverty_file = self.base_dir / "D'Marco_Sites/DMarco_Sites_With_Poverty_20250730_144749.json"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def create_poverty_fips_lookup(self):
        """Create lookup table with proper full FIPS codes"""
        print("🔍 Creating poverty data FIPS lookup...")
        
        try:
            with open(self.acs_poverty_file, 'r') as f:
                poverty_sites = json.load(f)
            
            poverty_lookup = {}
            
            for site in poverty_sites:
                acs_rate = site.get('acs_poverty_rate')
                county_fips = site.get('county_fips')
                tract_fips = site.get('tract_fips')
                census_tract = site.get('census_tract')
                
                if acs_rate is not None and county_fips and tract_fips:
                    # Construct full FIPS: State (48) + County + Tract
                    # Pad county to 3 digits, tract to 6 digits
                    county_padded = str(county_fips).zfill(3)
                    tract_padded = str(tract_fips).zfill(6)
                    full_fips = f"48{county_padded}{tract_padded}"
                    
                    poverty_lookup[full_fips] = {
                        'acs_poverty_rate': acs_rate,
                        'census_tract': census_tract,
                        'county_fips': county_fips,
                        'tract_fips': tract_fips,
                        'full_fips': full_fips,
                        'poverty_data_source': 'ACS_2022_5_YEAR_ACTUAL'
                    }
            
            print(f"✅ Created FIPS lookup for {len(poverty_lookup)} census tracts")
            
            # Show sample matches
            if len(poverty_lookup) > 0:
                sample_keys = list(poverty_lookup.keys())[:3]
                print(f"   Sample full FIPS codes: {sample_keys}")
                
                for key in sample_keys:
                    data = poverty_lookup[key]
                    print(f"     {key}: {data['acs_poverty_rate']}% poverty, {data['census_tract']}")
            
            return poverty_lookup
            
        except Exception as e:
            print(f"❌ Failed to create FIPS lookup: {e}")
            return {}
    
    def match_poverty_to_qct_sites(self):
        """Match poverty data to QCT sites using proper FIPS"""
        print("🔗 Matching poverty data to QCT sites using FIPS...")
        
        # Load QCT data
        try:
            qct_df = pd.read_excel(self.qct_dda_file)
            print(f"📊 Loaded {len(qct_df)} QCT/DDA sites")
        except Exception as e:
            print(f"❌ Failed to load QCT data: {e}")
            return None
        
        # Create poverty lookup
        poverty_lookup = self.create_poverty_fips_lookup()
        if not poverty_lookup:
            print("❌ No poverty lookup created")
            return None
        
        # Add poverty data columns
        qct_df['ACS_Poverty_Rate_REAL'] = 'MISSING'
        qct_df['Poverty_Data_Source_REAL'] = 'MISSING'
        qct_df['Census_Tract_Name_REAL'] = 'MISSING'
        qct_df['Full_FIPS_Code'] = 'MISSING'
        qct_df['FIPS_Match_Status'] = 'NO_MATCH'
        
        matches_found = 0
        
        for idx, site in qct_df.iterrows():
            final_tract = site.get('FINAL_TRACT')
            
            if final_tract and pd.notna(final_tract):
                # Current tract is already full FIPS format
                full_fips_str = str(int(final_tract))
                qct_df.loc[idx, 'Full_FIPS_Code'] = full_fips_str
                
                # Look for exact match
                if full_fips_str in poverty_lookup:
                    poverty_data = poverty_lookup[full_fips_str]
                    
                    qct_df.loc[idx, 'ACS_Poverty_Rate_REAL'] = poverty_data['acs_poverty_rate']
                    qct_df.loc[idx, 'Poverty_Data_Source_REAL'] = poverty_data['poverty_data_source']
                    qct_df.loc[idx, 'Census_Tract_Name_REAL'] = poverty_data['census_tract']
                    qct_df.loc[idx, 'FIPS_Match_Status'] = 'EXACT_MATCH'
                    matches_found += 1
                else:
                    qct_df.loc[idx, 'FIPS_Match_Status'] = 'NO_POVERTY_DATA'
        
        print(f"✅ FIPS matching complete: {matches_found}/{len(qct_df)} sites matched")
        
        if matches_found > 0:
            # Show matched poverty rate statistics
            matched_rates = qct_df[qct_df['FIPS_Match_Status'] == 'EXACT_MATCH']['ACS_Poverty_Rate_REAL']
            unique_rates = matched_rates.nunique()
            rate_range = f"{matched_rates.min():.1f}% - {matched_rates.max():.1f}%"
            print(f"   Matched rates: {unique_rates} unique, range: {rate_range}")
        
        return qct_df
    
    def integrate_with_fixed_poverty_matching(self):
        """Create integration with properly matched poverty data"""
        print("🔧 Creating integration with FIXED poverty matching...")
        
        # Get matched data
        matched_df = self.match_poverty_to_qct_sites()
        if matched_df is None:
            return None
        
        # Load other real data sources (from previous integrator)
        print("\n📊 Adding other real data sources...")
        
        # Add real acreage from CoStar
        try:
            costar_df = pd.read_excel(self.base_dir / "D'Marco_Sites/Costar_07312025/CS_Costar_TX_Land_8ac-30ac_07312025_ALL-export.xlsx")
            
            matched_df['Actual_Lot_Size_Acres'] = 'MISSING'
            matched_df['Acreage_Source'] = 'MISSING'
            
            if 'Land SF Gross' in costar_df.columns:
                acreage_matches = 0
                for idx, site in matched_df.iterrows():
                    site_address = str(site.get('Address', '')).strip()
                    
                    costar_match = costar_df[costar_df['Address'] == site_address]
                    if len(costar_match) > 0:
                        match = costar_match.iloc[0]
                        land_sf = pd.to_numeric(match.get('Land SF Gross'), errors='coerce')
                        
                        if pd.notna(land_sf) and land_sf > 0:
                            acres = land_sf / 43560
                            matched_df.loc[idx, 'Actual_Lot_Size_Acres'] = acres
                            matched_df.loc[idx, 'Acreage_Source'] = 'COSTAR_LAND_SF_GROSS'
                            acreage_matches += 1
                
                print(f"✅ Real acreage matched: {acreage_matches}/{len(matched_df)} sites")
        
        except Exception as e:
            print(f"⚠️ Acreage matching error: {e}")
        
        # Add real HUD AMI data
        try:
            ami_df = pd.read_excel(self.base_dir / "D'Marco_Sites/HUD2025_AMI_Rent_Data_Static.xlsx")
            texas_ami = ami_df[ami_df['State'] == 'TX']
            
            ami_columns = ['AMI_60_Studio', 'AMI_60_1BR', 'AMI_60_2BR', 'AMI_60_3BR', 'AMI_60_4BR']
            for col in ami_columns:
                matched_df[col] = 'MISSING'
            matched_df['AMI_Area_Name'] = 'MISSING'
            matched_df['AMI_Data_Source'] = 'MISSING'
            
            ami_matches = 0
            for idx, site in matched_df.iterrows():
                city = str(site.get('City', '')).lower()
                
                ami_match = None
                if 'austin' in city:
                    ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Austin', case=False, na=False)]
                elif any(term in city for term in ['dallas', 'plano', 'frisco']):
                    ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Dallas', case=False, na=False)]
                elif 'fort worth' in city:
                    ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Fort Worth', case=False, na=False)]
                elif 'houston' in city:
                    ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Houston', case=False, na=False)]
                elif 'san antonio' in city:
                    ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('San Antonio', case=False, na=False)]
                
                if ami_match is not None and len(ami_match) > 0:
                    ami_record = ami_match.iloc[0]
                    
                    matched_df.loc[idx, 'AMI_60_Studio'] = ami_record.get('60pct_AMI_Studio_Rent', 'MISSING')
                    matched_df.loc[idx, 'AMI_60_1BR'] = ami_record.get('60pct_AMI_1BR_Rent', 'MISSING')
                    matched_df.loc[idx, 'AMI_60_2BR'] = ami_record.get('60pct_AMI_2BR_Rent', 'MISSING')
                    matched_df.loc[idx, 'AMI_60_3BR'] = ami_record.get('60pct_AMI_3BR_Rent', 'MISSING')
                    matched_df.loc[idx, 'AMI_60_4BR'] = ami_record.get('60pct_AMI_4BR_Rent', 'MISSING')
                    matched_df.loc[idx, 'AMI_Area_Name'] = ami_record.get('HUD_Area', 'MISSING')
                    matched_df.loc[idx, 'AMI_Data_Source'] = 'HUD_2025_ACTUAL'
                    ami_matches += 1
            
            print(f"✅ Real AMI data matched: {ami_matches}/{len(matched_df)} sites")
            
        except Exception as e:
            print(f"⚠️ AMI matching error: {e}")
        
        return matched_df
    
    def save_fixed_integration(self, integrated_df):
        """Save integration with fixed poverty matching"""
        results_dir = self.base_dir / "D'Marco_Sites/Analysis_Results"
        
        excel_file = results_dir / f"FIXED_POVERTY_MATCHING_{self.timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main integrated data
            integrated_df.to_excel(writer, sheet_name='Fixed_Poverty_Integration', index=False)
            
            # Sites with matched poverty data
            poverty_matched = integrated_df[integrated_df['FIPS_Match_Status'] == 'EXACT_MATCH']
            poverty_matched.to_excel(writer, sheet_name='Sites_with_Real_Poverty', index=False)
            
            # Sites with complete data (poverty + acreage + AMI)
            complete_data = integrated_df[
                (integrated_df['FIPS_Match_Status'] == 'EXACT_MATCH') &
                (integrated_df['Acreage_Source'] == 'COSTAR_LAND_SF_GROSS') &
                (integrated_df['AMI_Data_Source'] == 'HUD_2025_ACTUAL')
            ]
            complete_data.to_excel(writer, sheet_name='Complete_Real_Data_Sites', index=False)
            
            # FIPS matching summary
            fips_summary = integrated_df['FIPS_Match_Status'].value_counts()
            summary_df = pd.DataFrame({'Match_Status': fips_summary.index, 'Count': fips_summary.values})
            summary_df.to_excel(writer, sheet_name='FIPS_Matching_Summary', index=False)
        
        print(f"\n💾 FIXED POVERTY MATCHING SAVED:")
        print(f"   📊 Excel: {excel_file.name}")
        print(f"   📈 Sites: {len(integrated_df)} total")
        
        # Summary statistics
        poverty_matched_count = (integrated_df['FIPS_Match_Status'] == 'EXACT_MATCH').sum()
        acreage_matched_count = (integrated_df['Acreage_Source'] == 'COSTAR_LAND_SF_GROSS').sum()
        ami_matched_count = (integrated_df['AMI_Data_Source'] == 'HUD_2025_ACTUAL').sum()
        
        print(f"   🎯 Real poverty data: {poverty_matched_count}/{len(integrated_df)} sites")
        print(f"   📏 Real acreage data: {acreage_matched_count}/{len(integrated_df)} sites")
        print(f"   💰 Real AMI data: {ami_matched_count}/{len(integrated_df)} sites")
        
        return excel_file

def main():
    """Execute fixed census tract matching"""
    print("🔧 FIXING CENSUS TRACT MATCHING")
    print("🎯 OBJECTIVE: Proper FIPS alignment for ACS poverty data")
    print("📊 METHOD: State (48) + County FIPS + Tract FIPS = Full FIPS code")
    print("=" * 80)
    
    matcher = CensusTractFIPSMatcher()
    
    # Create integration with fixed poverty matching
    integrated_df = matcher.integrate_with_fixed_poverty_matching()
    
    if integrated_df is None:
        print("❌ Fixed integration failed")
        return
    
    # Save results
    excel_file = matcher.save_fixed_integration(integrated_df)
    
    print(f"\n✅ FIXED POVERTY MATCHING COMPLETE")
    print(f"📁 Results: {excel_file.name}")
    print(f"\n🚀 REAL ACS POVERTY DATA NOW PROPERLY MATCHED")

if __name__ == "__main__":
    main()