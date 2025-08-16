#!/usr/bin/env python3
"""
CoStar TDHCA Scoring and Competition Analyzer
Adds comprehensive TDHCA scoring, competition analysis, and HUD AMI rent data 
to pre-filtered CoStar properties WITHOUT Google API calls

Features:
1. TDHCA 4% vs 9% scoring analysis
2. Competition analysis (One Mile Three Year Rule, Two Mile Same Year Rule)
3. Same Census Tract scoring
4. HUD AMI and LIHTC rent calculations
5. Deal viability recommendations

Author: Enhanced for Texas LIHTC Analysis
Date: 2025-06-17
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from geopy.distance import geodesic
import json

class CoStarTDHCAAnalyzer:
    """Comprehensive TDHCA scoring without Google API dependency"""
    
    def __init__(self):
        # Data paths
        self.tdhca_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
        self.ami_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx"
        
        # Load data
        self.tdhca_data = None
        self.ami_data = None
        self.load_tdhca_data()
        self.load_ami_data()
        
        # Large counties for Two Mile Rule (population > 1M)
        self.large_counties = {
            'Harris', 'Dallas', 'Tarrant', 'Bexar', 'Travis'
        }
        
        # City population thresholds for scoring
        self.city_populations = {
            'Houston': 2304580, 'San Antonio': 1434625, 'Dallas': 1304379,
            'Austin': 961855, 'Fort Worth': 918915, 'El Paso': 678815,
            'Arlington': 394266, 'Corpus Christi': 317863, 'Plano': 285494,
            'Laredo': 255205, 'Lubbock': 257141, 'Garland': 246018,
            'Irving': 256684, 'Amarillo': 200393, 'Grand Prairie': 196100,
            'Brownsville': 186738, 'McKinney': 195308, 'Pasadena': 151950,
            'Mesquite': 150108, 'McAllen': 142210, 'Killeen': 153095,
            'Carrollton': 133434, 'Waco': 138486, 'Denton': 139869,
            'Midland': 132524, 'Abilene': 125182, 'Beaumont': 115282
        }
    
    def load_tdhca_data(self):
        """Load TDHCA project list for competition analysis"""
        try:
            if Path(self.tdhca_file).exists():
                print(f"Loading TDHCA project data: {self.tdhca_file}")
                self.tdhca_data = pd.read_excel(self.tdhca_file)
                print(f"✅ Loaded {len(self.tdhca_data)} TDHCA projects")
                
                # Clean and prepare data
                if 'Latitude' in self.tdhca_data.columns and 'Longitude' in self.tdhca_data.columns:
                    # Remove projects without coordinates
                    self.tdhca_data = self.tdhca_data.dropna(subset=['Latitude', 'Longitude'])
                    print(f"✅ {len(self.tdhca_data)} projects with coordinates")
            else:
                print(f"❌ TDHCA file not found: {self.tdhca_file}")
        except Exception as e:
            print(f"❌ Error loading TDHCA data: {e}")
    
    def load_ami_data(self):
        """Load HUD AMI and rent data"""
        try:
            if Path(self.ami_file).exists():
                print(f"Loading HUD AMI data: {self.ami_file}")
                self.ami_data = pd.read_excel(self.ami_file, sheet_name=0)
                
                # Filter for Texas only
                self.ami_data = self.ami_data[self.ami_data['stusps'] == 'TX']
                print(f"✅ Loaded AMI data for {len(self.ami_data)} Texas counties")
            else:
                print(f"❌ AMI file not found: {self.ami_file}")
        except Exception as e:
            print(f"❌ Error loading AMI data: {e}")
    
    def get_county_from_city(self, city_name):
        """Estimate county from city name (basic mapping for major cities)"""
        city_to_county = {
            'Houston': 'Harris', 'Dallas': 'Dallas', 'San Antonio': 'Bexar',
            'Austin': 'Travis', 'Fort Worth': 'Tarrant', 'El Paso': 'El Paso',
            'Arlington': 'Tarrant', 'Corpus Christi': 'Nueces', 'Plano': 'Collin',
            'Laredo': 'Webb', 'Lubbock': 'Lubbock', 'Garland': 'Dallas',
            'Irving': 'Dallas', 'Amarillo': 'Potter', 'Grand Prairie': 'Dallas',
            'Brownsville': 'Cameron', 'McKinney': 'Collin', 'Pasadena': 'Harris',
            'Mesquite': 'Dallas', 'McAllen': 'Hidalgo', 'Killeen': 'Bell',
            'Carrollton': 'Dallas', 'Waco': 'McLennan', 'Denton': 'Denton',
            'Midland': 'Midland', 'Abilene': 'Taylor', 'Beaumont': 'Jefferson',
            'Round Rock': 'Williamson', 'Richardson': 'Dallas', 'League City': 'Galveston',
            'Sugar Land': 'Fort Bend', 'Pearland': 'Brazoria', 'College Station': 'Brazos',
            'The Woodlands': 'Montgomery', 'Flower Mound': 'Denton', 'Baytown': 'Harris',
            'Missouri City': 'Fort Bend', 'Lewisville': 'Denton', 'Allen': 'Collin',
            'Frisco': 'Collin', 'Conroe': 'Montgomery', 'Atascocita': 'Harris',
            'Cedar Park': 'Williamson', 'Georgetown': 'Williamson', 'Pflugerville': 'Travis'
        }
        return city_to_county.get(city_name, None)
    
    def get_ami_data_for_county(self, county_name):
        """Get AMI and rent data for a specific county"""
        if self.ami_data is None or county_name is None:
            return None
        
        # Try exact match first
        county_data = self.ami_data[
            self.ami_data['county_town_name'].str.contains(county_name, case=False, na=False)
        ]
        
        if len(county_data) > 0:
            return county_data.iloc[0].to_dict()
        
        return None
    
    def calculate_4pct_scoring(self, row):
        """Calculate 4% credit deal scoring (Tax-Exempt Bond Deals)"""
        score_details = {
            'deal_type': '4% Bond Deal',
            'total_score': 0,
            'scoring_breakdown': {},
            'eligibility_status': 'VIABLE',
            'fatal_flaws': []
        }
        
        # Basic eligibility requirements
        if not row.get('Federal_Basis_Boost', False):
            score_details['eligibility_status'] = 'INELIGIBLE'
            score_details['fatal_flaws'].append('No QCT/DDA status - no federal basis boost')
            return score_details
        
        # Population-based scoring (simplified without Google data)
        city = row.get('City', '')
        city_pop = self.city_populations.get(city, 0)
        
        if city_pop >= 200000:  # Major city
            population_score = 3
            score_details['scoring_breakdown']['Major City Bonus'] = 3
        elif city_pop >= 50000:  # Medium city
            population_score = 2
            score_details['scoring_breakdown']['Medium City'] = 2
        else:  # Small city/rural
            population_score = 1
            score_details['scoring_breakdown']['Small City/Rural'] = 1
        
        score_details['total_score'] += population_score
        
        # Market demand (basic scoring without amenity analysis)
        county = self.get_county_from_city(city)
        if county in self.large_counties:
            market_score = 2
            score_details['scoring_breakdown']['Large County Market'] = 2
        else:
            market_score = 1
            score_details['scoring_breakdown']['Standard Market'] = 1
        
        score_details['total_score'] += market_score
        
        # Federal basis boost value
        if row.get('QCT_Status'):
            score_details['scoring_breakdown']['QCT Basis Boost'] = 'Eligible (30%)'
        if row.get('DDA_Status'):
            score_details['scoring_breakdown']['DDA Basis Boost'] = 'Eligible (30%)'
        
        # Determine overall viability
        total = score_details['total_score']
        if total >= 4:
            score_details['eligibility_status'] = 'STRONG'
        elif total >= 3:
            score_details['eligibility_status'] = 'VIABLE'
        else:
            score_details['eligibility_status'] = 'MARGINAL'
        
        return score_details
    
    def calculate_9pct_scoring(self, row):
        """Calculate 9% credit deal scoring (Competitive Deals)"""
        score_details = {
            'deal_type': '9% Competitive Deal',
            'total_score': 0,
            'scoring_breakdown': {},
            'eligibility_status': 'VIABLE',
            'fatal_flaws': []
        }
        
        # Basic eligibility requirements
        if not row.get('Federal_Basis_Boost', False):
            score_details['eligibility_status'] = 'INELIGIBLE'
            score_details['fatal_flaws'].append('No QCT/DDA status - reduced competitiveness')
        
        # Population and market scoring
        city = row.get('City', '')
        city_pop = self.city_populations.get(city, 0)
        
        # Market demand scoring (0-5 points)
        if city_pop >= 500000:  # Major metro
            market_score = 5
            score_details['scoring_breakdown']['Major Metro Market'] = 5
        elif city_pop >= 200000:  # Mid-size city
            market_score = 4
            score_details['scoring_breakdown']['Mid-Size City Market'] = 4
        elif city_pop >= 50000:  # Small city
            market_score = 3
            score_details['scoring_breakdown']['Small City Market'] = 3
        else:  # Rural bonus
            market_score = 4  # Rural areas get bonus points
            score_details['scoring_breakdown']['Rural Bonus'] = 4
        
        score_details['total_score'] += market_score
        
        # Same Census Tract scoring (placeholder - requires Census tract lookup)
        # This would need to be enhanced with actual Census tract data
        census_tract_score = 3  # Assume moderate scoring
        score_details['scoring_breakdown']['Same Census Tract (Est.)'] = f'{census_tract_score} (estimated)'
        score_details['total_score'] += census_tract_score
        
        # Site characteristics (basic scoring)
        if row.get('Overall_Flood_Risk') == 'Low':
            site_score = 2
            score_details['scoring_breakdown']['Low Flood Risk'] = 2
            score_details['total_score'] += site_score
        elif row.get('Overall_Flood_Risk') == 'High':
            site_penalty = -1
            score_details['scoring_breakdown']['High Flood Risk Penalty'] = -1
            score_details['total_score'] += site_penalty
        
        # Determine competitiveness
        total = score_details['total_score']
        if total >= 25:
            score_details['eligibility_status'] = 'HIGHLY COMPETITIVE'
        elif total >= 20:
            score_details['eligibility_status'] = 'COMPETITIVE'
        elif total >= 15:
            score_details['eligibility_status'] = 'POSSIBLE'
        elif total >= 10:
            score_details['eligibility_status'] = 'WEAK'
        else:
            score_details['eligibility_status'] = 'VERY WEAK'
        
        return score_details
    
    def analyze_competition(self, lat, lng, city):
        """Analyze nearby TDHCA competition projects"""
        competition_analysis = {
            'one_mile_three_year_violations': 0,
            'two_mile_same_year_violations': 0,
            'nearby_projects': [],
            'competition_penalty': 0,
            'fatal_competition_flaw': False
        }
        
        if self.tdhca_data is None:
            return competition_analysis
        
        try:
            site_coords = (lat, lng)
            current_year = datetime.now().year
            
            # Check each competing project
            for idx, project in self.tdhca_data.iterrows():
                if pd.isna(project['Latitude']) or pd.isna(project['Longitude']):
                    continue
                
                project_coords = (project['Latitude'], project['Longitude'])
                distance_miles = geodesic(site_coords, project_coords).miles
                
                # Get project year (assuming there's a year column)
                project_year = None
                for col in ['Year', 'Application_Year', 'Award_Year', 'year']:
                    if col in project.keys() and not pd.isna(project[col]):
                        project_year = int(project[col])
                        break
                
                if project_year is None:
                    continue
                
                project_info = {
                    'distance_miles': round(distance_miles, 2),
                    'project_year': project_year,
                    'project_name': project.get('Project_Name', 'Unknown'),
                    'project_type': project.get('Credit_Type', 'Unknown')
                }
                
                # One Mile Three Year Rule (Both 4% and 9%)
                if distance_miles <= 1.0 and (current_year - project_year) <= 3:
                    competition_analysis['one_mile_three_year_violations'] += 1
                    project_info['violation_type'] = 'One Mile Three Year'
                    competition_analysis['nearby_projects'].append(project_info)
                
                # Two Mile Same Year Rule (9% only, large counties)
                county = self.get_county_from_city(city)
                if (county in self.large_counties and 
                    distance_miles <= 2.0 and 
                    project_year == current_year):
                    competition_analysis['two_mile_same_year_violations'] += 1
                    project_info['violation_type'] = 'Two Mile Same Year'
                    if project_info not in competition_analysis['nearby_projects']:
                        competition_analysis['nearby_projects'].append(project_info)
                
                # General nearby projects (within 3 miles)
                elif distance_miles <= 3.0:
                    project_info['violation_type'] = 'Nearby (No violation)'
                    competition_analysis['nearby_projects'].append(project_info)
            
            # Determine penalties
            if competition_analysis['one_mile_three_year_violations'] > 0:
                competition_analysis['fatal_competition_flaw'] = True
                competition_analysis['competition_penalty'] = -1000  # Fatal flaw
            elif competition_analysis['two_mile_same_year_violations'] > 0:
                competition_analysis['competition_penalty'] = -10  # Major penalty for 9%
            else:
                # Minor penalty for nearby competition
                nearby_count = len([p for p in competition_analysis['nearby_projects'] 
                                 if p['violation_type'] == 'Nearby (No violation)'])
                competition_analysis['competition_penalty'] = min(-2 * nearby_count, -6)
            
        except Exception as e:
            print(f"❌ Error analyzing competition for {lat}, {lng}: {e}")
        
        return competition_analysis
    
    def process_costar_with_tdhca_analysis(self, costar_file):
        """Process CoStar data with comprehensive TDHCA analysis"""
        print("=== CoStar TDHCA Scoring & Competition Analysis ===")
        
        # Load pre-filtered CoStar data
        if not Path(costar_file).exists():
            print(f"❌ CoStar file not found: {costar_file}")
            return None
        
        df = pd.read_excel(costar_file, sheet_name='LIHTC_Viable')
        print(f"✅ Loaded {len(df)} LIHTC viable properties")
        
        # Initialize new analysis columns
        analysis_columns = [
            '4Pct_Total_Score', '4Pct_Status', '4Pct_Breakdown',
            '9Pct_Total_Score', '9Pct_Status', '9Pct_Breakdown',
            'Competition_1Mile_3Yr', 'Competition_2Mile_SameYr', 'Competition_Fatal_Flaw',
            'Nearby_Projects_Count', 'Competition_Details',
            'County_Est', 'AMI_4Person', 'Rent_1BR_60', 'Rent_2BR_60', 'Rent_3BR_60', 'Rent_4BR_60',
            'Annual_Revenue_Est', 'Deal_Recommendation', 'Analysis_Summary'
        ]
        
        for col in analysis_columns:
            df[col] = None
        
        print("\n🔍 Running TDHCA analysis...")
        
        for idx, row in df.iterrows():
            if idx % 25 == 0:
                print(f"   Processing {idx+1}/{len(df)} properties...")
            
            lat = row['Latitude']
            lng = row['Longitude']
            city = row['City']
            
            # 4% Credit Analysis
            score_4pct = self.calculate_4pct_scoring(row)
            df.loc[idx, '4Pct_Total_Score'] = score_4pct['total_score']
            df.loc[idx, '4Pct_Status'] = score_4pct['eligibility_status']
            df.loc[idx, '4Pct_Breakdown'] = json.dumps(score_4pct['scoring_breakdown'])
            
            # 9% Credit Analysis
            score_9pct = self.calculate_9pct_scoring(row)
            df.loc[idx, '9Pct_Total_Score'] = score_9pct['total_score']
            df.loc[idx, '9Pct_Status'] = score_9pct['eligibility_status']
            df.loc[idx, '9Pct_Breakdown'] = json.dumps(score_9pct['scoring_breakdown'])
            
            # Competition Analysis
            competition = self.analyze_competition(lat, lng, city)
            df.loc[idx, 'Competition_1Mile_3Yr'] = competition['one_mile_three_year_violations']
            df.loc[idx, 'Competition_2Mile_SameYr'] = competition['two_mile_same_year_violations']
            df.loc[idx, 'Competition_Fatal_Flaw'] = competition['fatal_competition_flaw']
            df.loc[idx, 'Nearby_Projects_Count'] = len(competition['nearby_projects'])
            df.loc[idx, 'Competition_Details'] = json.dumps(competition['nearby_projects'])
            
            # County and AMI Analysis
            county = self.get_county_from_city(city)
            df.loc[idx, 'County_Est'] = county
            
            if county:
                ami_data = self.get_ami_data_for_county(county)
                if ami_data:
                    df.loc[idx, 'AMI_4Person'] = ami_data.get('lim50_25p4', 0)
                    df.loc[idx, 'Rent_1BR_60'] = ami_data.get('1BR 60%', 0)
                    df.loc[idx, 'Rent_2BR_60'] = ami_data.get('2BR 60%', 0)
                    df.loc[idx, 'Rent_3BR_60'] = ami_data.get('3BR 60%', 0)
                    df.loc[idx, 'Rent_4BR_60'] = ami_data.get('4BR 60%', 0)
                    
                    # Estimate annual revenue (simplified unit mix)
                    rent_1br = ami_data.get('1BR 60%', 0)
                    rent_2br = ami_data.get('2BR 60%', 0)
                    if rent_1br > 0 and rent_2br > 0:
                        # Assume 50% 1BR, 50% 2BR for 100-unit project
                        annual_revenue = (50 * rent_1br * 12) + (50 * rent_2br * 12)
                        df.loc[idx, 'Annual_Revenue_Est'] = annual_revenue
            
            # Overall Deal Recommendation
            if competition['fatal_competition_flaw']:
                recommendation = 'AVOID - Competition Fatal Flaw'
            elif score_4pct['eligibility_status'] in ['STRONG', 'VIABLE'] and score_9pct['eligibility_status'] in ['HIGHLY COMPETITIVE', 'COMPETITIVE']:
                recommendation = 'EXCELLENT - Both 4% and 9% viable'
            elif score_4pct['eligibility_status'] in ['STRONG', 'VIABLE']:
                recommendation = 'GOOD - 4% Bond Deal recommended'
            elif score_9pct['eligibility_status'] in ['HIGHLY COMPETITIVE', 'COMPETITIVE', 'POSSIBLE']:
                recommendation = 'CONSIDER - 9% Deal potential'
            else:
                recommendation = 'MARGINAL - Limited potential'
            
            df.loc[idx, 'Deal_Recommendation'] = recommendation
            
            # Analysis Summary
            summary = f"4%: {score_4pct['eligibility_status']} ({score_4pct['total_score']}pts), "
            summary += f"9%: {score_9pct['eligibility_status']} ({score_9pct['total_score']}pts), "
            if competition['fatal_competition_flaw']:
                summary += "FATAL COMPETITION FLAW"
            else:
                summary += f"Competition: {len(competition['nearby_projects'])} nearby"
            
            df.loc[idx, 'Analysis_Summary'] = summary
        
        # Sort by deal quality
        df['Sort_Score'] = df.apply(lambda row: self.calculate_sort_score(row), axis=1)
        df_sorted = df.sort_values('Sort_Score', ascending=False)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"CoStar_TDHCA_Analysis_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # All analyzed properties
            df_sorted.to_excel(writer, sheet_name='All_Analysis', index=False)
            
            # Top recommendations
            top_deals = df_sorted[~df_sorted['Deal_Recommendation'].str.contains('AVOID', na=False)].head(50)
            top_deals.to_excel(writer, sheet_name='Top_50_Deals', index=False)
            
            # 4% focused deals
            good_4pct = df_sorted[df_sorted['4Pct_Status'].isin(['STRONG', 'VIABLE'])]
            good_4pct.to_excel(writer, sheet_name='Good_4Pct_Deals', index=False)
            
            # 9% competitive deals
            good_9pct = df_sorted[df_sorted['9Pct_Status'].isin(['HIGHLY COMPETITIVE', 'COMPETITIVE', 'POSSIBLE'])]
            good_9pct.to_excel(writer, sheet_name='Good_9Pct_Deals', index=False)
        
        print(f"\n📊 TDHCA Analysis Results:")
        print(f"   Total Analyzed: {len(df)}")
        print(f"   Competition Fatal Flaws: {len(df[df['Competition_Fatal_Flaw'] == True])}")
        print(f"   Strong 4% Deals: {len(df[df['4Pct_Status'] == 'STRONG'])}")
        print(f"   Competitive 9% Deals: {len(df[df['9Pct_Status'].isin(['HIGHLY COMPETITIVE', 'COMPETITIVE'])])}")
        print(f"\n💾 Results saved to: {output_file}")
        
        return df_sorted, output_file
    
    def calculate_sort_score(self, row):
        """Calculate sorting score for ranking deals"""
        score = 0
        
        # Avoid fatal flaws
        if row.get('Competition_Fatal_Flaw'):
            return -1000
        
        # Reward good 4% deals
        if row.get('4Pct_Status') == 'STRONG':
            score += 100
        elif row.get('4Pct_Status') == 'VIABLE':
            score += 75
        
        # Reward competitive 9% deals
        if row.get('9Pct_Status') == 'HIGHLY COMPETITIVE':
            score += 150
        elif row.get('9Pct_Status') == 'COMPETITIVE':
            score += 125
        elif row.get('9Pct_Status') == 'POSSIBLE':
            score += 100
        
        # Consider sale status
        sale_status = str(row.get('Sale Status', '')).lower()
        if 'active' in sale_status:
            score += 25
        elif 'contract' in sale_status:
            score -= 15
        
        # Consider pricing
        price = row.get('Sale Price', 0)
        if price > 0 and price < 1000000:  # Under $1M
            score += 10
        elif price > 5000000:  # Over $5M
            score -= 10
        
        return score

def main():
    """Run TDHCA analysis on pre-filtered CoStar data"""
    # Look for the latest pre-filtered file
    import glob
    costar_files = glob.glob("CoStar_Texas_PreFiltered_*.xlsx")
    
    if not costar_files:
        print("❌ No pre-filtered CoStar file found. Run costar_texas_prefilter.py first.")
        return None
    
    # Use the most recent file
    costar_file = max(costar_files, key=lambda x: Path(x).stat().st_mtime)
    print(f"Using CoStar file: {costar_file}")
    
    try:
        analyzer = CoStarTDHCAAnalyzer()
        results_df, output_file = analyzer.process_costar_with_tdhca_analysis(costar_file)
        
        print(f"\n✅ TDHCA analysis complete!")
        print(f"📁 Results file: {output_file}")
        
        return results_df, output_file
        
    except Exception as e:
        print(f"❌ Error in TDHCA analysis: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    main()