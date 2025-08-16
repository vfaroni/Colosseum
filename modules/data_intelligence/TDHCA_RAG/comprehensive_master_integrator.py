#!/usr/bin/env python3
"""
COMPREHENSIVE MASTER INTEGRATOR
Combines ALL data sources: CoStar + Census API + TDHCA + Schools + HUD AMI + Ranking
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class ComprehensiveMasterIntegrator:
    """Master integration of ALL LIHTC analysis components"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
        
        # All data sources
        self.costar_file = self.base_dir / "D'Marco_Sites/Costar_07312025/CS_Costar_TX_Land_8ac-30ac_07312025_ALL-export.xlsx"
        self.census_api_file = self.base_dir / "D'Marco_Sites/Analysis_Results/BATCH_CENSUS_API_POVERTY_20250801_172636.xlsx"
        self.qct_dda_file = self.base_dir / "D'Marco_Sites/Analysis_Results/MASTER_155_BoostEligible_Sites_20250731_223500.xlsx"
        self.hud_ami_file = self.base_dir / "D'Marco_Sites/HUD2025_AMI_Rent_Data_Static.xlsx"
        self.school_analysis = self.base_dir / "D'Marco_Sites/DMarco_School_Amenities_Analysis_20250730_172649.xlsx"
        self.competing_projects_file = self.base_dir / "D'Marco_Sites/DMarco_Competition_Details_20250730_150629.xlsx"
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def load_costar_base_data(self):
        """Load original CoStar data as base"""
        print("📊 Loading CoStar base data...")
        
        try:
            costar_df = pd.read_excel(self.costar_file)
            print(f"✅ CoStar data: {len(costar_df)} sites")
            
            # Calculate real acreage from Land SF Gross
            if 'Land SF Gross' in costar_df.columns:
                land_sf = pd.to_numeric(costar_df['Land SF Gross'], errors='coerce')
                costar_df['Actual_Acres'] = land_sf / 43560
                
                valid_acres = (land_sf > 0).sum()
                print(f"   Real acreage available: {valid_acres}/{len(costar_df)} sites")
            
            return costar_df
            
        except Exception as e:
            print(f"❌ Failed to load CoStar data: {e}")
            return None
    
    def integrate_census_api_poverty(self, master_df):
        """Add Census API poverty data"""
        print("🏘️ Integrating Census API poverty data...")
        
        try:
            census_df = pd.read_excel(self.census_api_file, sheet_name='Sites_with_Census_API_Data')
            print(f"📊 Census API data: {len(census_df)} sites")
            
            # Add poverty columns
            master_df['ACS_Poverty_Rate'] = 'MISSING'
            master_df['Poverty_Count'] = 'MISSING'
            master_df['Total_Population'] = 'MISSING'
            master_df['Census_Data_Source'] = 'MISSING'
            
            # Match by address
            successful_matches = 0
            for idx, site in master_df.iterrows():
                site_address = str(site.get('Address', '')).strip()
                
                census_match = census_df[census_df['Address'] == site_address]
                if len(census_match) > 0 and census_match.iloc[0]['Census_API_Status'] == 'SUCCESS':
                    match = census_match.iloc[0]
                    master_df.loc[idx, 'ACS_Poverty_Rate'] = match['Census_API_Poverty_Rate']
                    master_df.loc[idx, 'Poverty_Count'] = match['Census_Poverty_Count']
                    master_df.loc[idx, 'Total_Population'] = match['Census_Total_Population']
                    master_df.loc[idx, 'Census_Data_Source'] = 'CENSUS_API_ACS_2022_5_YEAR'
                    successful_matches += 1
            
            print(f"✅ Census API poverty matched: {successful_matches}/{len(master_df)} sites")
            return master_df
            
        except Exception as e:
            print(f"❌ Census API integration error: {e}")
            return master_df
    
    def integrate_qct_dda_data(self, master_df):
        """Add QCT/DDA boost eligibility"""
        print("🎯 Integrating QCT/DDA boost eligibility...")
        
        try:
            qct_df = pd.read_excel(self.qct_dda_file)
            print(f"📊 QCT/DDA data: {len(qct_df)} sites")
            
            # Add QCT/DDA columns
            master_df['QCT_Status'] = 'MISSING'
            master_df['DDA_Status'] = 'MISSING'
            master_df['Basis_Boost_Eligible'] = 'MISSING'
            master_df['FINAL_TRACT'] = 'MISSING'
            
            # Match by address
            qct_matches = 0
            for idx, site in master_df.iterrows():
                site_address = str(site.get('Address', '')).strip()
                
                qct_match = qct_df[qct_df['Address'] == site_address]
                if len(qct_match) > 0:
                    match = qct_match.iloc[0]
                    master_df.loc[idx, 'QCT_Status'] = match.get('QCT_Status', 'MISSING')
                    master_df.loc[idx, 'DDA_Status'] = match.get('DDA_Status', 'MISSING')
                    master_df.loc[idx, 'Basis_Boost_Eligible'] = match.get('Basis_Boost_Eligible', 'MISSING')
                    master_df.loc[idx, 'FINAL_TRACT'] = match.get('FINAL_TRACT', 'MISSING')
                    qct_matches += 1
            
            print(f"✅ QCT/DDA data matched: {qct_matches}/{len(master_df)} sites")
            return master_df
            
        except Exception as e:
            print(f"❌ QCT/DDA integration error: {e}")
            return master_df
    
    def integrate_hud_ami_rents(self, master_df):
        """Add HUD AMI 60% rent limits"""
        print("💰 Integrating HUD AMI 60% rent limits...")
        
        try:
            ami_df = pd.read_excel(self.hud_ami_file)
            texas_ami = ami_df[ami_df['State'] == 'TX']
            print(f"📊 Texas HUD AMI areas: {len(texas_ami)}")
            
            # Add AMI columns
            ami_columns = ['AMI_60_Studio', 'AMI_60_1BR', 'AMI_60_2BR', 'AMI_60_3BR', 'AMI_60_4BR']
            for col in ami_columns:
                master_df[col] = 'MISSING'
            master_df['HUD_Area_Name'] = 'MISSING'
            master_df['AMI_Metro_Status'] = 'MISSING'
            
            # Match by city
            ami_matches = 0
            for idx, site in master_df.iterrows():
                city = str(site.get('City', '')).lower()
                
                ami_match = None
                if 'austin' in city:
                    ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Austin', case=False, na=False)]
                elif any(term in city for term in ['dallas', 'plano', 'frisco', 'richardson', 'garland']):
                    ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Dallas', case=False, na=False)]
                elif 'fort worth' in city or 'arlington' in city:
                    ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Fort Worth', case=False, na=False)]
                elif 'houston' in city or 'katy' in city or 'pearland' in city:
                    ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Houston', case=False, na=False)]
                elif 'san antonio' in city:
                    ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('San Antonio', case=False, na=False)]
                
                if ami_match is not None and len(ami_match) > 0:
                    ami_record = ami_match.iloc[0]
                    master_df.loc[idx, 'AMI_60_Studio'] = ami_record.get('60pct_AMI_Studio_Rent', 'MISSING')
                    master_df.loc[idx, 'AMI_60_1BR'] = ami_record.get('60pct_AMI_1BR_Rent', 'MISSING')
                    master_df.loc[idx, 'AMI_60_2BR'] = ami_record.get('60pct_AMI_2BR_Rent', 'MISSING')
                    master_df.loc[idx, 'AMI_60_3BR'] = ami_record.get('60pct_AMI_3BR_Rent', 'MISSING')
                    master_df.loc[idx, 'AMI_60_4BR'] = ami_record.get('60pct_AMI_4BR_Rent', 'MISSING')
                    master_df.loc[idx, 'HUD_Area_Name'] = ami_record.get('HUD_Area', 'MISSING')
                    master_df.loc[idx, 'AMI_Metro_Status'] = ami_record.get('Metro_Status', 'MISSING')
                    ami_matches += 1
            
            print(f"✅ HUD AMI rents matched: {ami_matches}/{len(master_df)} sites")
            return master_df
            
        except Exception as e:
            print(f"❌ HUD AMI integration error: {e}")
            return master_df
    
    def integrate_school_data(self, master_df):
        """Add school analysis data"""
        print("🏫 Integrating school analysis data...")
        
        try:
            school_df = pd.read_excel(self.school_analysis)
            print(f"📊 School analysis data: {len(school_df)} sites")
            
            # Add school columns
            school_columns = [
                'Schools_Within_3_Miles', 'Elementary_Schools', 'Middle_Schools', 
                'High_Schools', 'School_Amenity_Score', 'School_Rating'
            ]
            
            for col in school_columns:
                master_df[col] = 'MISSING'
            
            # Match by address or index (simplified for now)
            school_matches = 0
            for idx, site in master_df.iterrows():
                if idx < len(school_df):
                    school_record = school_df.iloc[idx]
                    
                    for col in school_columns:
                        if col in school_df.columns:
                            value = school_record.get(col)
                            if pd.notna(value):
                                master_df.loc[idx, col] = value
                                school_matches += 1
                                break
            
            print(f"✅ School data integrated: {school_matches} data points")
            return master_df
            
        except Exception as e:
            print(f"❌ School integration error: {e}")
            return master_df
    
    def integrate_competing_projects(self, master_df):
        """Add TDHCA competing projects data"""
        print("🏗️ Integrating TDHCA competing projects (last 3 years)...")
        
        try:
            competing_df = pd.read_excel(self.competing_projects_file)
            print(f"📊 Competing projects data: {len(competing_df)} sites")
            
            # Add competing projects columns
            master_df['Competing_Projects_Within_10_Miles'] = 'MISSING'
            master_df['Total_Competing_Units'] = 'MISSING'
            master_df['Competition_Risk_Level'] = 'MISSING'
            master_df['Nearest_Competing_Project_Distance'] = 'MISSING'
            
            # Match by address
            competing_matches = 0
            for idx, site in master_df.iterrows():
                site_address = str(site.get('Address', '')).strip()
                
                competing_match = competing_df[competing_df['Address'] == site_address]
                if len(competing_match) > 0:
                    match = competing_match.iloc[0]
                    master_df.loc[idx, 'Competing_Projects_Within_10_Miles'] = match.get('Competing_Projects_Within_10_Miles', 'MISSING')
                    master_df.loc[idx, 'Total_Competing_Units'] = match.get('Total_Competing_Units', 'MISSING')
                    master_df.loc[idx, 'Competition_Risk_Level'] = match.get('Competition_Risk_Level', 'MISSING')
                    master_df.loc[idx, 'Nearest_Competing_Project_Distance'] = match.get('Nearest_Competing_Project_Distance', 'MISSING')
                    competing_matches += 1
            
            print(f"✅ Competing projects matched: {competing_matches}/{len(master_df)} sites")
            return master_df
            
        except Exception as e:
            print(f"❌ Competing projects integration error: {e}")
            return master_df
    
    def calculate_comprehensive_ranking(self, master_df):
        """Calculate comprehensive LIHTC development ranking"""
        print("📊 Calculating comprehensive LIHTC ranking...")
        
        # Initialize scoring columns
        master_df['QCT_DDA_Score'] = 0
        master_df['Poverty_Score'] = 0
        master_df['AMI_Rent_Score'] = 0
        master_df['School_Score'] = 0
        master_df['Competition_Score'] = 0
        master_df['Size_Score'] = 0
        master_df['Total_LIHTC_Score'] = 0
        master_df['LIHTC_Rank'] = 0
        master_df['Development_Tier'] = 'UNRANKED'
        
        scored_sites = 0
        
        for idx, site in master_df.iterrows():
            total_score = 0
            
            # 1. QCT/DDA Basis Boost (25 points max)
            if site.get('Basis_Boost_Eligible') == 'YES':
                qct_dda_score = 25
            else:
                qct_dda_score = 0
            master_df.loc[idx, 'QCT_DDA_Score'] = qct_dda_score
            total_score += qct_dda_score
            
            # 2. Poverty Rate (20 points max - lower poverty = higher score)
            poverty_rate = site.get('ACS_Poverty_Rate')
            if poverty_rate != 'MISSING' and pd.notna(poverty_rate):
                try:
                    poverty_pct = float(poverty_rate)
                    if poverty_pct <= 10:
                        poverty_score = 20
                    elif poverty_pct <= 20:
                        poverty_score = 15
                    elif poverty_pct <= 30:
                        poverty_score = 10
                    else:
                        poverty_score = 5
                except:
                    poverty_score = 0
            else:
                poverty_score = 0
            master_df.loc[idx, 'Poverty_Score'] = poverty_score
            total_score += poverty_score
            
            # 3. AMI Rent Potential (20 points max)
            ami_2br = site.get('AMI_60_2BR')
            if ami_2br != 'MISSING' and pd.notna(ami_2br):
                try:
                    rent_2br = float(str(ami_2br).replace('$', '').replace(',', ''))
                    if rent_2br >= 1400:
                        ami_score = 20
                    elif rent_2br >= 1200:
                        ami_score = 15
                    elif rent_2br >= 1000:
                        ami_score = 10
                    else:
                        ami_score = 5
                except:
                    ami_score = 0
            else:
                ami_score = 0
            master_df.loc[idx, 'AMI_Rent_Score'] = ami_score
            total_score += ami_score
            
            # 4. School Quality (15 points max)
            school_rating = site.get('School_Rating')
            if school_rating != 'MISSING' and pd.notna(school_rating):
                try:
                    rating = float(school_rating)
                    if rating >= 8:
                        school_score = 15
                    elif rating >= 6:
                        school_score = 10
                    elif rating >= 4:
                        school_score = 5
                    else:
                        school_score = 0
                except:
                    school_score = 0
            else:
                school_score = 0
            master_df.loc[idx, 'School_Score'] = school_score
            total_score += school_score
            
            # 5. Competition Risk (10 points max - lower competition = higher score)
            competition_risk = site.get('Competition_Risk_Level')
            if competition_risk == 'LOW':
                competition_score = 10
            elif competition_risk == 'MEDIUM':
                competition_score = 6
            elif competition_risk == 'HIGH':
                competition_score = 2
            else:
                competition_score = 0
            master_df.loc[idx, 'Competition_Score'] = competition_score
            total_score += competition_score
            
            # 6. Site Size (10 points max)
            acres = site.get('Actual_Acres')
            if acres != 'MISSING' and pd.notna(acres):
                try:
                    size = float(acres)
                    if size >= 20:
                        size_score = 10
                    elif size >= 15:
                        size_score = 8
                    elif size >= 10:
                        size_score = 6
                    else:
                        size_score = 4
                except:
                    size_score = 0
            else:
                size_score = 0
            master_df.loc[idx, 'Size_Score'] = size_score
            total_score += size_score
            
            master_df.loc[idx, 'Total_LIHTC_Score'] = total_score
            
            if total_score > 0:
                scored_sites += 1
        
        # Rank sites by total score
        master_df['LIHTC_Rank'] = master_df['Total_LIHTC_Score'].rank(method='dense', ascending=False)
        
        # Assign development tiers
        for idx, site in master_df.iterrows():
            score = site['Total_LIHTC_Score']
            if score >= 70:
                tier = 'TIER_1_PREMIUM'
            elif score >= 50:
                tier = 'TIER_2_STRONG'
            elif score >= 30:
                tier = 'TIER_3_VIABLE'
            elif score >= 15:
                tier = 'TIER_4_MARGINAL'
            else:
                tier = 'TIER_5_WEAK'
            
            master_df.loc[idx, 'Development_Tier'] = tier
        
        print(f"✅ Comprehensive ranking complete: {scored_sites}/{len(master_df)} sites scored")
        
        # Show tier distribution
        tier_counts = master_df['Development_Tier'].value_counts()
        print("   Tier distribution:")
        for tier, count in tier_counts.items():
            print(f"     {tier}: {count} sites")
        
        return master_df
    
    def save_comprehensive_results(self, master_df):
        """Save comprehensive integrated results"""
        results_dir = self.base_dir / "D'Marco_Sites/Analysis_Results"
        
        excel_file = results_dir / f"COMPREHENSIVE_MASTER_INTEGRATION_{self.timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main comprehensive data
            master_df.to_excel(writer, sheet_name='Comprehensive_Analysis', index=False)
            
            # Top 25 ranked sites
            top_25 = master_df.nlargest(25, 'Total_LIHTC_Score')
            top_25.to_excel(writer, sheet_name='Top_25_Sites', index=False)
            
            # Tier 1 Premium sites only
            tier_1 = master_df[master_df['Development_Tier'] == 'TIER_1_PREMIUM']
            tier_1.to_excel(writer, sheet_name='Tier_1_Premium', index=False)
            
            # QCT/DDA eligible sites
            boost_eligible = master_df[master_df['Basis_Boost_Eligible'] == 'YES']
            boost_eligible.to_excel(writer, sheet_name='QCT_DDA_Boost_Eligible', index=False)
            
            # Data completeness summary
            completeness_data = []
            key_fields = {
                'ACS_Poverty_Rate': 'Census API Poverty',
                'AMI_60_2BR': 'HUD AMI 60% 2BR Rent',
                'Schools_Within_3_Miles': 'School Analysis',
                'Actual_Acres': 'CoStar Acreage'
            }
            
            for field, description in key_fields.items():
                complete_count = (master_df[field] != 'MISSING').sum()
                completeness_pct = (complete_count / len(master_df)) * 100
                completeness_data.append({
                    'Data_Source': description,
                    'Complete_Sites': complete_count,
                    'Total_Sites': len(master_df),
                    'Completeness_Pct': f"{completeness_pct:.1f}%"
                })
            
            completeness_df = pd.DataFrame(completeness_data)
            completeness_df.to_excel(writer, sheet_name='Data_Completeness', index=False)
        
        print(f"\n💾 COMPREHENSIVE MASTER INTEGRATION SAVED:")
        print(f"   📊 Excel: {excel_file.name}")
        print(f"   📈 Total sites: {len(master_df)}")
        
        # Summary stats
        tier_1_count = (master_df['Development_Tier'] == 'TIER_1_PREMIUM').sum()
        boost_eligible_count = (master_df['Basis_Boost_Eligible'] == 'YES').sum()
        complete_data_count = (
            (master_df['ACS_Poverty_Rate'] != 'MISSING') &
            (master_df['AMI_60_2BR'] != 'MISSING') &
            (master_df['Schools_Within_3_Miles'] != 'MISSING')
        ).sum()
        
        print(f"   🏆 Tier 1 Premium sites: {tier_1_count}")
        print(f"   🎯 QCT/DDA boost eligible: {boost_eligible_count}")
        print(f"   ✅ Sites with complete data: {complete_data_count}")
        
        return excel_file

def main():
    """Execute comprehensive master integration"""
    print("🚀 COMPREHENSIVE MASTER INTEGRATOR")
    print("🎯 OBJECTIVE: Integrate ALL data sources with ranking")
    print("📊 SOURCES: CoStar + Census API + QCT/DDA + HUD AMI + Schools + TDHCA Competing Projects")
    print("=" * 100)
    
    integrator = ComprehensiveMasterIntegrator()
    
    # Load CoStar base data
    master_df = integrator.load_costar_base_data()
    if master_df is None:
        print("❌ Failed to load base CoStar data")
        return
    
    # Integrate all data sources
    master_df = integrator.integrate_census_api_poverty(master_df)
    master_df = integrator.integrate_qct_dda_data(master_df)
    master_df = integrator.integrate_hud_ami_rents(master_df)
    master_df = integrator.integrate_school_data(master_df)
    master_df = integrator.integrate_competing_projects(master_df)
    
    # Calculate comprehensive ranking
    master_df = integrator.calculate_comprehensive_ranking(master_df)
    
    # Save comprehensive results
    excel_file = integrator.save_comprehensive_results(master_df)
    
    print(f"\n✅ COMPREHENSIVE MASTER INTEGRATION COMPLETE")
    print(f"📁 Results: {excel_file.name}")
    print(f"\n🚀 COMPLETE LIHTC ANALYSIS WITH ALL DATA SOURCES INTEGRATED")

if __name__ == "__main__":
    main()