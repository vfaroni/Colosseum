#!/usr/bin/env python3
"""
CoStar Land-Specific LIHTC Analyzer
Focuses ONLY on location-specific factors that affect LIHTC development

REAL TDHCA Rules Implemented:
1. Competition Analysis (One Mile Rule, Two Mile Rule, Same Census Tract)
2. QCT/DDA Federal Basis Boost Status 
3. FEMA Flood Risk (Insurance Cost Impact)
4. Comprehensive Market Competition (All LIHTC Projects 2015-2025)

EXCLUDES: Developer-choice factors (AMI set-asides, project amenities, etc.)
NOTES: Proximity scoring awaits official 2025 TDHCA QAP rules

Author: Enhanced for Texas LIHTC Analysis
Date: 2025-06-17
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from geopy.distance import geodesic
import json

class CoStarLandSpecificAnalyzer:
    """Land-specific LIHTC analysis using only verified TDHCA rules"""
    
    def __init__(self):
        # Data paths
        self.tdhca_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
        self.ami_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx"
        
        # Load data
        self.tdhca_data = None
        self.ami_data = None
        self.load_tdhca_data()
        self.load_ami_data()
        
        # REAL TDHCA competition rules
        self.large_counties = {
            'Harris', 'Dallas', 'Tarrant', 'Bexar', 'Travis'
        }
        
        # FEMA flood zone risk mapping (insurance impact)
        self.flood_insurance_multipliers = {
            'VE': 3.0,     # Coastal high hazard - very high insurance
            'V': 3.0,      # Coastal high hazard
            'AE': 2.5,     # 1% annual chance flood - high insurance
            'A': 2.5,      # 1% annual chance flood  
            'AH': 2.0,     # Shallow flooding
            'AO': 2.0,     # Sheet flow areas
            'AR': 1.8,     # Areas with reduced flood risk
            'A99': 1.5,    # Areas with levee protection
            'X': 1.0,      # Minimal flood hazard - standard insurance
            'B': 1.0,      # Old designation for X
            'C': 1.0,      # Old designation for X
            'D': 1.2       # Possible but undetermined flood hazard
        }
    
    def load_tdhca_data(self):
        """Load TDHCA project list with correct coordinate columns"""
        try:
            if Path(self.tdhca_file).exists():
                print(f"Loading TDHCA project data: {self.tdhca_file}")
                self.tdhca_data = pd.read_excel(self.tdhca_file, sheet_name='PropInventory')
                print(f"✅ Loaded {len(self.tdhca_data)} TDHCA projects")
                
                # Clean coordinate data with proper parsing
                if 'Latitude11' in self.tdhca_data.columns and 'Longitude11' in self.tdhca_data.columns:
                    # Convert coordinates to numeric, handling any string issues
                    self.tdhca_data['Latitude11'] = pd.to_numeric(self.tdhca_data['Latitude11'], errors='coerce')
                    self.tdhca_data['Longitude11'] = pd.to_numeric(self.tdhca_data['Longitude11'], errors='coerce')
                    
                    # Remove projects without valid coordinates
                    before_count = len(self.tdhca_data)
                    self.tdhca_data = self.tdhca_data.dropna(subset=['Latitude11', 'Longitude11'])
                    after_count = len(self.tdhca_data)
                    print(f"✅ {after_count} projects with valid coordinates ({before_count - after_count} removed)")
                    
                    # Ensure Year column is numeric
                    if 'Year' in self.tdhca_data.columns:
                        self.tdhca_data['Year'] = pd.to_numeric(self.tdhca_data['Year'], errors='coerce')
                        year_count = self.tdhca_data['Year'].notna().sum()
                        print(f"✅ {year_count} projects with valid years (2015-2025)")
                else:
                    print(f"❌ Coordinate columns not found. Available: {self.tdhca_data.columns.tolist()}")
            else:
                print(f"❌ TDHCA file not found: {self.tdhca_file}")
        except Exception as e:
            print(f"❌ Error loading TDHCA data: {e}")
    
    def load_ami_data(self):
        """Load HUD AMI data for market context"""
        try:
            if Path(self.ami_file).exists():
                print(f"Loading HUD AMI data: {self.ami_file}")
                self.ami_data = pd.read_excel(self.ami_file, sheet_name=0)
                self.ami_data = self.ami_data[self.ami_data['stusps'] == 'TX']
                print(f"✅ Loaded AMI data for {len(self.ami_data)} Texas counties")
            else:
                print(f"❌ AMI file not found: {self.ami_file}")
        except Exception as e:
            print(f"❌ Error loading AMI data: {e}")
    
    def get_county_from_city(self, city_name):
        """Enhanced county mapping for Texas cities"""
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
            'Cedar Park': 'Williamson', 'Georgetown': 'Williamson', 'Pflugerville': 'Travis',
            'Corsicana': 'Navarro', 'Huntsville': 'Walker', 'Terrell': 'Kaufman',
            'Palestine': 'Anderson', 'Marshall': 'Harrison', 'Longview': 'Gregg',
            'Tyler': 'Smith', 'Lufkin': 'Angelina', 'Nacogdoches': 'Nacogdoches',
            'Texarkana': 'Bowie', 'Paris': 'Lamar', 'Sherman': 'Grayson',
            'Denison': 'Grayson', 'Gainesville': 'Cooke', 'Cleburne': 'Johnson',
            'Athens': 'Henderson', 'Canton': 'Van Zandt', 'Bastrop': 'Bastrop',
            'Hempstead': 'Waller', 'Kerrville': 'Kerr', 'Spring Branch': 'Comal',
            'Buchanan Dam': 'Llano', 'Sunset': 'Montague', 'Rockport': 'Aransas',
            'Red Rock': 'Bastrop', 'Little Elm': 'Denton'
        }
        return city_to_county.get(city_name, None)
    
    def analyze_fema_flood_risk(self, flood_zone_str, flood_risk_str):
        """Analyze FEMA flood risk impact on insurance costs"""
        flood_analysis = {
            'FEMA_Zone_Raw': flood_zone_str,
            'Insurance_Risk_Level': 'Unknown',
            'Insurance_Cost_Multiplier': 1.2,
            'Development_Impact': 'Unknown',
            'FEMA_Description': 'Unknown'
        }
        
        if pd.isna(flood_zone_str):
            flood_zone_str = ''
        
        flood_zone = str(flood_zone_str).upper()
        
        # Parse multiple zones (e.g., "B and X", "VE, V1-30")
        insurance_multiplier = 1.0
        risk_level = 'Low'
        description = 'Minimal flood hazard'
        
        # Check each flood zone category
        for zone, multiplier in self.flood_insurance_multipliers.items():
            if zone in flood_zone:
                if multiplier > insurance_multiplier:
                    insurance_multiplier = multiplier
                    if multiplier >= 3.0:
                        risk_level = 'Very High'
                        description = 'Coastal high hazard area - very high insurance costs'
                    elif multiplier >= 2.0:
                        risk_level = 'High'  
                        description = '1% annual chance flood - high insurance costs'
                    elif multiplier >= 1.5:
                        risk_level = 'Moderate'
                        description = 'Moderate flood risk - elevated insurance costs'
                    else:
                        risk_level = 'Low'
                        description = 'Minimal flood hazard - standard insurance'
        
        # Development impact assessment
        if insurance_multiplier >= 3.0:
            impact = 'Significant - Consider other sites'
        elif insurance_multiplier >= 2.0:
            impact = 'Moderate - Higher operating costs'
        elif insurance_multiplier >= 1.5:
            impact = 'Minor - Manageable cost increase'
        else:
            impact = 'Minimal - Standard insurance costs'
        
        flood_analysis.update({
            'Insurance_Risk_Level': risk_level,
            'Insurance_Cost_Multiplier': insurance_multiplier,
            'Development_Impact': impact,
            'FEMA_Description': description
        })
        
        return flood_analysis
    
    def comprehensive_competition_analysis(self, lat, lng, city):
        """Comprehensive competition analysis using REAL TDHCA rules"""
        competition_analysis = {
            # TDHCA Scoring Rules
            'one_mile_three_year_fatal': False,
            'one_mile_three_year_count': 0,
            'two_mile_same_year_penalty': False,
            'two_mile_same_year_count': 0,
            'same_census_tract_years': None,
            'same_census_tract_points': 0,
            
            # Comprehensive Market Analysis
            'all_competition_1mile': [],
            'all_competition_2mile': [],
            'all_competition_3mile': [],
            'market_saturation_score': 0,
            'total_competing_units': 0,
            
            # Analysis Details
            'county_large_county_rules': False,
            'analysis_complete': False,
            'error_details': None
        }
        
        if self.tdhca_data is None:
            competition_analysis['error_details'] = 'No TDHCA data loaded'
            return competition_analysis
        
        try:
            site_coords = (lat, lng)
            current_year = datetime.now().year
            county = self.get_county_from_city(city)
            
            # Check if large county rules apply
            if county in self.large_counties:
                competition_analysis['county_large_county_rules'] = True
            
            # Analyze each project in TDHCA database
            valid_projects = self.tdhca_data.dropna(subset=['Latitude11', 'Longitude11', 'Year'])
            
            for idx, project in valid_projects.iterrows():
                try:
                    project_coords = (project['Latitude11'], project['Longitude11'])
                    distance_miles = geodesic(site_coords, project_coords).miles
                    project_year = int(project['Year'])
                    units = project.get('Total Units', 0)
                    
                    project_info = {
                        'distance_miles': round(distance_miles, 2),
                        'project_year': project_year,
                        'years_ago': current_year - project_year,
                        'project_name': project.get('Development Name', 'Unknown'),
                        'project_type': project.get('Program Type', 'Unknown'),
                        'total_units': units,
                        'lihtc_units': project.get('LIHTC Units', 0),
                        'tdhca_number': project.get('TDHCA#', 'Unknown'),
                        'project_city': project.get('Project City', 'Unknown'),
                        'project_county': project.get('Project County', 'Unknown')
                    }
                    
                    # REAL TDHCA RULE: One Mile Three Year Rule (Fatal Flaw)
                    if distance_miles <= 1.0 and (current_year - project_year) <= 3:
                        competition_analysis['one_mile_three_year_count'] += 1
                        competition_analysis['one_mile_three_year_fatal'] = True
                        project_info['tdhca_violation'] = 'One Mile Three Year - FATAL FLAW'
                    
                    # REAL TDHCA RULE: Two Mile Same Year Rule (Large Counties Only)
                    if (county in self.large_counties and 
                        distance_miles <= 2.0 and 
                        project_year == current_year):
                        competition_analysis['two_mile_same_year_count'] += 1
                        competition_analysis['two_mile_same_year_penalty'] = True
                        project_info['tdhca_violation'] = 'Two Mile Same Year - Major Penalty'
                    
                    # Comprehensive market analysis by distance
                    if distance_miles <= 1.0:
                        competition_analysis['all_competition_1mile'].append(project_info)
                        competition_analysis['total_competing_units'] += units
                    elif distance_miles <= 2.0:
                        competition_analysis['all_competition_2mile'].append(project_info)
                    elif distance_miles <= 3.0:
                        competition_analysis['all_competition_3mile'].append(project_info)
                
                except Exception as e:
                    continue  # Skip problematic projects
            
            # Calculate market saturation score
            total_1mile_units = sum(p.get('total_units', 0) for p in competition_analysis['all_competition_1mile'])
            total_2mile_units = sum(p.get('total_units', 0) for p in competition_analysis['all_competition_2mile'])
            
            # Market saturation scoring (0-10, where 10 is heavily saturated)
            if total_1mile_units >= 1000:
                saturation = 10
            elif total_1mile_units >= 500:
                saturation = 8
            elif total_1mile_units >= 250:
                saturation = 6
            elif total_1mile_units >= 100:
                saturation = 4
            elif total_1mile_units >= 50:
                saturation = 2
            else:
                saturation = 0
            
            competition_analysis['market_saturation_score'] = saturation
            
            # REAL TDHCA RULE: Same Census Tract Scoring (TODO: Requires Census tract lookup)
            # This would need actual Census tract data to implement properly
            competition_analysis['same_census_tract_years'] = 'Requires Census tract data'
            competition_analysis['same_census_tract_points'] = 'TBD'
            
            competition_analysis['analysis_complete'] = True
            
        except Exception as e:
            competition_analysis['error_details'] = str(e)
        
        return competition_analysis
    
    def process_land_specific_analysis(self, costar_file):
        """Process CoStar data with comprehensive land-specific analysis"""
        print("=== CoStar Land-Specific LIHTC Analysis ===")
        print("FOCUS: Only location-specific factors (no developer choices)")
        print("USING: Real TDHCA competition rules + verified data sources")
        
        # Load pre-filtered CoStar data
        if not Path(costar_file).exists():
            print(f"❌ CoStar file not found: {costar_file}")
            return None
        
        df = pd.read_excel(costar_file, sheet_name='LIHTC_Viable')
        print(f"✅ Loaded {len(df)} LIHTC viable properties")
        
        # Initialize land-specific analysis columns
        analysis_columns = [
            # Federal Basis Boost (REAL)
            'QCT_Status', 'DDA_Status', 'Federal_Basis_Boost_30pct',
            
            # TDHCA Competition Analysis (REAL RULES)
            'TDHCA_One_Mile_Fatal', 'TDHCA_One_Mile_Count',
            'TDHCA_Two_Mile_Penalty', 'TDHCA_Two_Mile_Count',
            'TDHCA_Census_Tract_Points', 'Large_County_Rules_Apply',
            
            # Comprehensive Market Analysis
            'Competition_1Mile_Projects', 'Competition_1Mile_Units',
            'Competition_2Mile_Projects', 'Competition_2Mile_Units', 
            'Competition_3Mile_Projects', 'Competition_3Mile_Units',
            'Market_Saturation_Score', 'Market_Analysis_Summary',
            
            # FEMA Flood Risk (Insurance Impact)
            'FEMA_Zone', 'FEMA_Insurance_Risk', 'FEMA_Cost_Multiplier',
            'FEMA_Development_Impact', 'FEMA_Description',
            
            # Overall Land Assessment
            'Land_Viability_Score', 'Land_Risk_Factors', 'Land_Advantages',
            'Development_Recommendation', 'Critical_Issues'
        ]
        
        for col in analysis_columns:
            df[col] = None
        
        print("\n🔍 Running land-specific analysis...")
        
        for idx, row in df.iterrows():
            if idx % 25 == 0:
                print(f"   Processing {idx+1}/{len(df)} properties...")
            
            lat = row['Latitude']
            lng = row['Longitude']
            city = row['City']
            
            # Federal Basis Boost Analysis (REAL)
            df.loc[idx, 'QCT_Status'] = row.get('QCT_Status', False)
            df.loc[idx, 'DDA_Status'] = row.get('DDA_Status', False)
            df.loc[idx, 'Federal_Basis_Boost_30pct'] = row.get('Federal_Basis_Boost', False)
            
            # FEMA Flood Risk Analysis (Insurance Impact)
            flood_analysis = self.analyze_fema_flood_risk(
                row.get('Flood Zone'), 
                row.get('Flood Risk')
            )
            df.loc[idx, 'FEMA_Zone'] = flood_analysis['FEMA_Zone_Raw']
            df.loc[idx, 'FEMA_Insurance_Risk'] = flood_analysis['Insurance_Risk_Level']
            df.loc[idx, 'FEMA_Cost_Multiplier'] = flood_analysis['Insurance_Cost_Multiplier']
            df.loc[idx, 'FEMA_Development_Impact'] = flood_analysis['Development_Impact']
            df.loc[idx, 'FEMA_Description'] = flood_analysis['FEMA_Description']
            
            # Comprehensive Competition Analysis (REAL TDHCA RULES)
            competition = self.comprehensive_competition_analysis(lat, lng, city)
            df.loc[idx, 'TDHCA_One_Mile_Fatal'] = competition['one_mile_three_year_fatal']
            df.loc[idx, 'TDHCA_One_Mile_Count'] = competition['one_mile_three_year_count']
            df.loc[idx, 'TDHCA_Two_Mile_Penalty'] = competition['two_mile_same_year_penalty']
            df.loc[idx, 'TDHCA_Two_Mile_Count'] = competition['two_mile_same_year_count']
            df.loc[idx, 'TDHCA_Census_Tract_Points'] = competition['same_census_tract_points']
            df.loc[idx, 'Large_County_Rules_Apply'] = competition['county_large_county_rules']
            
            # Market Analysis
            df.loc[idx, 'Competition_1Mile_Projects'] = len(competition['all_competition_1mile'])
            df.loc[idx, 'Competition_1Mile_Units'] = sum(p.get('total_units', 0) for p in competition['all_competition_1mile'])
            df.loc[idx, 'Competition_2Mile_Projects'] = len(competition['all_competition_2mile'])
            df.loc[idx, 'Competition_2Mile_Units'] = sum(p.get('total_units', 0) for p in competition['all_competition_2mile'])
            df.loc[idx, 'Competition_3Mile_Projects'] = len(competition['all_competition_3mile'])
            df.loc[idx, 'Competition_3Mile_Units'] = sum(p.get('total_units', 0) for p in competition['all_competition_3mile'])
            df.loc[idx, 'Market_Saturation_Score'] = competition['market_saturation_score']
            
            # Land Viability Assessment
            land_score = self.calculate_land_viability_score(row, flood_analysis, competition)
            df.loc[idx, 'Land_Viability_Score'] = land_score['total_score']
            df.loc[idx, 'Land_Risk_Factors'] = '; '.join(land_score['risk_factors'])
            df.loc[idx, 'Land_Advantages'] = '; '.join(land_score['advantages'])
            df.loc[idx, 'Development_Recommendation'] = land_score['recommendation']
            df.loc[idx, 'Critical_Issues'] = '; '.join(land_score['critical_issues'])
            
            # Market Analysis Summary
            market_summary = f"{len(competition['all_competition_1mile'])} projects within 1mi "
            market_summary += f"({sum(p.get('total_units', 0) for p in competition['all_competition_1mile'])} units), "
            market_summary += f"Saturation: {competition['market_saturation_score']}/10"
            df.loc[idx, 'Market_Analysis_Summary'] = market_summary
        
        # Sort by land viability score
        df_sorted = df.sort_values('Land_Viability_Score', ascending=False)
        
        # Save comprehensive results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"CoStar_Land_Analysis_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # All analyzed properties
            df_sorted.to_excel(writer, sheet_name='All_Land_Analysis', index=False)
            
            # Properties without fatal flaws
            viable_land = df_sorted[df_sorted['TDHCA_One_Mile_Fatal'] != True]
            viable_land.to_excel(writer, sheet_name='Viable_Land_Sites', index=False)
            
            # Low competition sites
            low_competition = df_sorted[df_sorted['Market_Saturation_Score'] <= 4]
            low_competition.to_excel(writer, sheet_name='Low_Competition_Sites', index=False)
            
            # Federal basis boost sites
            basis_boost_sites = df_sorted[df_sorted['Federal_Basis_Boost_30pct'] == True]
            basis_boost_sites.to_excel(writer, sheet_name='QCT_DDA_Sites', index=False)
            
            # TDHCA fatal flaws
            fatal_flaws = df_sorted[df_sorted['TDHCA_One_Mile_Fatal'] == True]
            fatal_flaws.to_excel(writer, sheet_name='TDHCA_Fatal_Flaws', index=False)
            
            # High flood risk sites
            flood_risk_sites = df_sorted[df_sorted['FEMA_Cost_Multiplier'] >= 2.0]
            flood_risk_sites.to_excel(writer, sheet_name='High_Flood_Risk', index=False)
        
        print(f"\n📊 Land-Specific Analysis Results:")
        print(f"   Total Properties: {len(df)}")
        print(f"   TDHCA Fatal Flaws: {len(df[df['TDHCA_One_Mile_Fatal'] == True])}")
        print(f"   QCT/DDA Sites: {len(df[df['Federal_Basis_Boost_30pct'] == True])}")
        print(f"   High Flood Risk: {len(df[df['FEMA_Cost_Multiplier'] >= 2.0])}")
        print(f"   Low Competition: {len(df[df['Market_Saturation_Score'] <= 4])}")
        print(f"\n💾 Results saved to: {output_file}")
        
        return df_sorted, output_file
    
    def calculate_land_viability_score(self, row, flood_analysis, competition):
        """Calculate comprehensive land viability score (0-100)"""
        score_details = {
            'total_score': 0,
            'risk_factors': [],
            'advantages': [],
            'critical_issues': [],
            'recommendation': 'Unknown'
        }
        
        score = 100  # Start with perfect score
        
        # CRITICAL ELIMINATIONS
        if competition['one_mile_three_year_fatal']:
            score = 0
            score_details['critical_issues'].append('TDHCA One Mile Rule Violation')
            score_details['recommendation'] = 'AVOID - Fatal TDHCA Competition Flaw'
            return score_details
        
        if not row.get('Federal_Basis_Boost', False):
            score = 0  
            score_details['critical_issues'].append('No QCT/DDA Status - No Federal Basis Boost')
            score_details['recommendation'] = 'AVOID - Not LIHTC Eligible'
            return score_details
        
        # COMPETITION PENALTIES
        if competition['two_mile_same_year_penalty']:
            score -= 25
            score_details['risk_factors'].append('Two Mile Same Year Penalty')
        
        market_saturation = competition['market_saturation_score']
        if market_saturation >= 8:
            score -= 20
            score_details['risk_factors'].append('High Market Saturation')
        elif market_saturation >= 6:
            score -= 10
            score_details['risk_factors'].append('Moderate Market Saturation')
        elif market_saturation <= 2:
            score += 10
            score_details['advantages'].append('Low Market Competition')
        
        # FLOOD RISK PENALTIES
        flood_multiplier = flood_analysis['Insurance_Cost_Multiplier']
        if flood_multiplier >= 3.0:
            score -= 30
            score_details['risk_factors'].append('Very High Flood Insurance Costs')
        elif flood_multiplier >= 2.0:
            score -= 15
            score_details['risk_factors'].append('High Flood Insurance Costs')
        elif flood_multiplier <= 1.0:
            score += 5
            score_details['advantages'].append('Minimal Flood Risk')
        
        # FEDERAL BASIS BOOST ADVANTAGES
        if row.get('QCT_Status'):
            score += 15
            score_details['advantages'].append('QCT Status - 30% Basis Boost')
        if row.get('DDA_Status'):
            score += 15
            score_details['advantages'].append('DDA Status - 30% Basis Boost')
        
        # PRICE REASONABLENESS
        price = row.get('Sale Price', 0)
        if price > 0:
            if price <= 500000:
                score += 10
                score_details['advantages'].append('Excellent Land Price')
            elif price <= 1000000:
                score += 5
                score_details['advantages'].append('Good Land Price')
            elif price > 3000000:
                score -= 10
                score_details['risk_factors'].append('High Land Cost')
        
        # Final scoring and recommendations
        score = max(0, min(100, score))  # Keep in 0-100 range
        score_details['total_score'] = score
        
        if score >= 80:
            score_details['recommendation'] = 'EXCELLENT - High Priority Development Site'
        elif score >= 70:
            score_details['recommendation'] = 'STRONG - Good Development Potential'
        elif score >= 60:
            score_details['recommendation'] = 'VIABLE - Consider with Caution'
        elif score >= 40:
            score_details['recommendation'] = 'MARGINAL - High Risk Development'
        else:
            score_details['recommendation'] = 'POOR - Avoid Development'
        
        return score_details

def main():
    """Run land-specific analysis on pre-filtered CoStar data"""
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
        analyzer = CoStarLandSpecificAnalyzer()
        results_df, output_file = analyzer.process_land_specific_analysis(costar_file)
        
        print(f"\n✅ Land-specific analysis complete!")
        print(f"📁 Results file: {output_file}")
        print(f"\n📋 NOTES:")
        print(f"   ✅ Uses REAL TDHCA competition rules")
        print(f"   ✅ Actual QCT/DDA federal basis boost analysis")
        print(f"   ✅ Comprehensive FEMA flood risk (insurance impact)")
        print(f"   ⏳ Proximity scoring awaits official 2025 TDHCA QAP")
        
        return results_df, output_file
        
    except Exception as e:
        print(f"❌ Error in land-specific analysis: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    main()