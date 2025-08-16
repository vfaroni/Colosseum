#!/usr/bin/env python3
"""
CoStar TDHCA Scoring and Competition Analyzer - FIXED VERSION
Corrected competition analysis, AMI data, and FEMA flood zones

Fixes:
1. TDHCA coordinates are in 'Latitude11' and 'Longitude11' columns
2. AMI_4Person should be 100% AMI (median2025), not 50% AMI
3. FEMA flood zone interpretation from CoStar data
4. Enhanced 4% vs 9% scoring algorithms

Author: Enhanced for Texas LIHTC Analysis
Date: 2025-06-17
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from geopy.distance import geodesic
import json

class CoStarTDHCAAnalyzerFixed:
    """Fixed version with correct competition analysis and AMI data"""
    
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
        
        # Enhanced city population mapping
        self.city_populations = {
            'Houston': 2304580, 'San Antonio': 1434625, 'Dallas': 1304379,
            'Austin': 961855, 'Fort Worth': 918915, 'El Paso': 678815,
            'Arlington': 394266, 'Corpus Christi': 317863, 'Plano': 285494,
            'Laredo': 255205, 'Lubbock': 257141, 'Garland': 246018,
            'Irving': 256684, 'Amarillo': 200393, 'Grand Prairie': 196100,
            'Brownsville': 186738, 'McKinney': 195308, 'Pasadena': 151950,
            'Mesquite': 150108, 'McAllen': 142210, 'Killeen': 153095,
            'Carrollton': 133434, 'Waco': 138486, 'Denton': 139869,
            'Midland': 132524, 'Abilene': 125182, 'Beaumont': 115282,
            'Round Rock': 133372, 'Richardson': 121323, 'League City': 114424,
            'Sugar Land': 111026, 'Pearland': 125410, 'College Station': 120511,
            'Baytown': 83701, 'Missouri City': 74259, 'Lewisville': 111822,
            'Allen': 109642, 'Frisco': 200509, 'Conroe': 98081,
            'Cedar Park': 77595, 'Georgetown': 75420, 'Pflugerville': 65191
        }
    
    def load_tdhca_data(self):
        """Load TDHCA project list with FIXED coordinate column names"""
        try:
            if Path(self.tdhca_file).exists():
                print(f"Loading TDHCA project data: {self.tdhca_file}")
                self.tdhca_data = pd.read_excel(self.tdhca_file, sheet_name='PropInventory')
                print(f"✅ Loaded {len(self.tdhca_data)} TDHCA projects")
                
                # FIXED: Use correct coordinate column names
                if 'Latitude11' in self.tdhca_data.columns and 'Longitude11' in self.tdhca_data.columns:
                    # Remove projects without coordinates
                    before_count = len(self.tdhca_data)
                    self.tdhca_data = self.tdhca_data.dropna(subset=['Latitude11', 'Longitude11'])
                    after_count = len(self.tdhca_data)
                    print(f"✅ {after_count} projects with coordinates ({before_count - after_count} removed)")
                    
                    # Ensure Year column is numeric
                    if 'Year' in self.tdhca_data.columns:
                        self.tdhca_data['Year'] = pd.to_numeric(self.tdhca_data['Year'], errors='coerce')
                        year_count = self.tdhca_data['Year'].notna().sum()
                        print(f"✅ {year_count} projects with valid years")
                else:
                    print(f"❌ Coordinate columns not found. Available columns: {self.tdhca_data.columns.tolist()}")
            else:
                print(f"❌ TDHCA file not found: {self.tdhca_file}")
        except Exception as e:
            print(f"❌ Error loading TDHCA data: {e}")
    
    def load_ami_data(self):
        """Load HUD AMI data"""
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
        """Enhanced county mapping for major Texas cities"""
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
            'Corsicana': 'Navarro', 'Athens': 'Henderson', 'Canton': 'Van Zandt'
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
    
    def interpret_fema_flood_zone(self, flood_zone_str, flood_risk_str):
        """Enhanced FEMA flood zone interpretation"""
        flood_analysis = {
            'FEMA_Zone_Raw': flood_zone_str,
            'FEMA_Risk_Level': 'Unknown',
            'FEMA_Description': 'Unknown',
            'Risk_Score': 5  # Default moderate risk
        }
        
        if pd.isna(flood_zone_str):
            flood_zone_str = ''
        
        flood_zone = str(flood_zone_str).upper()
        
        # High Risk Zones (Special Flood Hazard Areas)
        if any(zone in flood_zone for zone in ['AE', 'A1-30', 'AH', 'AO', 'AR', 'A99']):
            flood_analysis['FEMA_Risk_Level'] = 'HIGH'
            flood_analysis['FEMA_Description'] = '1% annual chance flood (100-year flood)'
            flood_analysis['Risk_Score'] = 10
        elif 'A' in flood_zone and 'X' not in flood_zone:
            flood_analysis['FEMA_Risk_Level'] = 'HIGH'
            flood_analysis['FEMA_Description'] = '1% annual chance flood zone'
            flood_analysis['Risk_Score'] = 10
        elif any(zone in flood_zone for zone in ['VE', 'V1-30', 'V']):
            flood_analysis['FEMA_Risk_Level'] = 'VERY HIGH'
            flood_analysis['FEMA_Description'] = 'Coastal high hazard area'
            flood_analysis['Risk_Score'] = 15
        
        # Moderate Risk Zones
        elif '0.2' in flood_zone or 'SHADED X' in flood_zone:
            flood_analysis['FEMA_Risk_Level'] = 'MODERATE'
            flood_analysis['FEMA_Description'] = '0.2% annual chance flood (500-year flood)'
            flood_analysis['Risk_Score'] = 3
        
        # Low Risk Zones
        elif 'X' in flood_zone or 'B' in flood_zone or 'C' in flood_zone:
            flood_analysis['FEMA_Risk_Level'] = 'LOW'
            flood_analysis['FEMA_Description'] = 'Minimal flood hazard'
            flood_analysis['Risk_Score'] = 1
        
        # Check CoStar Risk field as backup
        if not pd.isna(flood_risk_str):
            risk_str = str(flood_risk_str).lower()
            if 'yes' in risk_str and flood_analysis['FEMA_Risk_Level'] == 'Unknown':
                flood_analysis['FEMA_Risk_Level'] = 'MODERATE'
                flood_analysis['FEMA_Description'] = 'CoStar indicates flood risk'
                flood_analysis['Risk_Score'] = 5
            elif 'no' in risk_str and flood_analysis['FEMA_Risk_Level'] == 'Unknown':
                flood_analysis['FEMA_Risk_Level'] = 'LOW'
                flood_analysis['FEMA_Description'] = 'CoStar indicates no flood risk'
                flood_analysis['Risk_Score'] = 1
        
        return flood_analysis
    
    def calculate_enhanced_4pct_scoring(self, row):
        """Enhanced 4% credit deal scoring based on TDHCA criteria"""
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
        
        # Market Demand Analysis (0-5 points)
        city = row.get('City', '')
        city_pop = self.city_populations.get(city, 0)
        county = self.get_county_from_city(city)
        
        market_score = 0
        if city_pop >= 500000:  # Major metro
            market_score = 5
            score_details['scoring_breakdown']['Major Metro Market'] = 5
        elif city_pop >= 200000:  # Large city
            market_score = 4
            score_details['scoring_breakdown']['Large City Market'] = 4
        elif city_pop >= 50000:  # Medium city
            market_score = 3
            score_details['scoring_breakdown']['Medium City Market'] = 3
        elif county in self.large_counties:  # Large county suburb
            market_score = 4
            score_details['scoring_breakdown']['Large County Suburb'] = 4
        else:  # Small city/rural
            market_score = 2
            score_details['scoring_breakdown']['Small City/Rural'] = 2
        
        score_details['total_score'] += market_score
        
        # Site and Development Characteristics (0-7 points)
        site_score = 0
        
        # Flood risk scoring
        flood_risk = row.get('FEMA_Risk_Level', 'Unknown')
        if flood_risk == 'LOW':
            site_score += 3
            score_details['scoring_breakdown']['Low Flood Risk'] = 3
        elif flood_risk == 'MODERATE':
            site_score += 1
            score_details['scoring_breakdown']['Moderate Flood Risk'] = 1
        elif flood_risk in ['HIGH', 'VERY HIGH']:
            site_score -= 2
            score_details['scoring_breakdown']['High Flood Risk Penalty'] = -2
        
        # Price reasonableness
        price = row.get('Sale Price', 0)
        if price > 0:
            if price <= 500000:  # Very affordable
                site_score += 2
                score_details['scoring_breakdown']['Excellent Price'] = 2
            elif price <= 1000000:  # Reasonable
                site_score += 1
                score_details['scoring_breakdown']['Good Price'] = 1
            elif price > 3000000:  # Expensive
                site_score -= 1
                score_details['scoring_breakdown']['High Price Penalty'] = -1
        
        # Acreage appropriateness
        acreage = row.get('Size (SF)', 0)
        if acreage > 0:
            acres = acreage / 43560
            if 1 <= acres <= 10:  # Ideal for LIHTC
                site_score += 2
                score_details['scoring_breakdown']['Ideal Acreage'] = 2
            elif acres > 20:  # Too large
                site_score -= 1
                score_details['scoring_breakdown']['Oversized Penalty'] = -1
        
        score_details['total_score'] += max(0, site_score)  # Don't go negative
        
        # Federal Basis Boost (Key Advantage)
        basis_boost_value = 0
        if row.get('QCT_Status'):
            basis_boost_value = 3
            score_details['scoring_breakdown']['QCT 30% Basis Boost'] = 3
        if row.get('DDA_Status'):
            basis_boost_value = max(basis_boost_value, 3)
            score_details['scoring_breakdown']['DDA 30% Basis Boost'] = 3
        
        score_details['total_score'] += basis_boost_value
        
        # Determine overall viability for 4% deals
        total = score_details['total_score']
        if total >= 10:
            score_details['eligibility_status'] = 'EXCELLENT'
        elif total >= 8:
            score_details['eligibility_status'] = 'STRONG'
        elif total >= 6:
            score_details['eligibility_status'] = 'VIABLE'
        elif total >= 4:
            score_details['eligibility_status'] = 'MARGINAL'
        else:
            score_details['eligibility_status'] = 'WEAK'
        
        return score_details
    
    def calculate_enhanced_9pct_scoring(self, row):
        """Enhanced 9% credit deal scoring based on TDHCA QAP"""
        score_details = {
            'deal_type': '9% Competitive Deal',
            'total_score': 0,
            'scoring_breakdown': {},
            'eligibility_status': 'VIABLE',
            'fatal_flaws': []
        }
        
        # QCT/DDA provides significant advantage but not required
        if not row.get('Federal_Basis_Boost', False):
            score_details['scoring_breakdown']['No QCT/DDA'] = 'Reduced competitiveness'
        
        # Market Demand (0-5 points) - More competitive for 9%
        city = row.get('City', '')
        city_pop = self.city_populations.get(city, 0)
        county = self.get_county_from_city(city)
        
        market_score = 0
        if city_pop < 50000:  # Rural bonus for 9%
            market_score = 5
            score_details['scoring_breakdown']['Rural Area Bonus'] = 5
        elif 50000 <= city_pop < 200000:
            market_score = 4
            score_details['scoring_breakdown']['Small City Market'] = 4
        elif 200000 <= city_pop < 500000:
            market_score = 3
            score_details['scoring_breakdown']['Mid-Size City Market'] = 3
        else:  # Major metro - most competitive
            market_score = 2
            score_details['scoring_breakdown']['Major Metro (Competitive)'] = 2
        
        score_details['total_score'] += market_score
        
        # Same Census Tract Scoring (0-5 points) - Placeholder
        # This would require actual Census tract analysis
        census_tract_score = 3  # Assume moderate scoring
        score_details['scoring_breakdown']['Census Tract (Est.)'] = f'{census_tract_score} (estimated)'
        score_details['total_score'] += census_tract_score
        
        # Site and Development Characteristics (0-10 points)
        site_score = 0
        
        # Enhanced flood risk analysis for 9%
        flood_risk = row.get('FEMA_Risk_Level', 'Unknown')
        if flood_risk == 'LOW':
            site_score += 4
            score_details['scoring_breakdown']['Low Flood Risk'] = 4
        elif flood_risk == 'MODERATE':
            site_score += 2
            score_details['scoring_breakdown']['Moderate Flood Risk'] = 2
        elif flood_risk in ['HIGH', 'VERY HIGH']:
            site_score -= 3
            score_details['scoring_breakdown']['High Flood Risk Penalty'] = -3
        
        # QCT/DDA Bonus for 9%
        if row.get('QCT_Status'):
            site_score += 3
            score_details['scoring_breakdown']['QCT Scoring Advantage'] = 3
        if row.get('DDA_Status'):
            site_score += 3
            score_details['scoring_breakdown']['DDA Scoring Advantage'] = 3
        
        # Development feasibility
        price = row.get('Sale Price', 0)
        if price > 0:
            if price <= 750000:  # Very feasible
                site_score += 2
                score_details['scoring_breakdown']['Excellent Feasibility'] = 2
            elif price <= 1500000:  # Feasible
                site_score += 1
                score_details['scoring_breakdown']['Good Feasibility'] = 1
            elif price > 3000000:  # Challenging
                site_score -= 2
                score_details['scoring_breakdown']['Feasibility Challenge'] = -2
        
        score_details['total_score'] += max(0, site_score)
        
        # Determine competitiveness for 9% deals
        total = score_details['total_score']
        if total >= 15:
            score_details['eligibility_status'] = 'HIGHLY COMPETITIVE'
        elif total >= 12:
            score_details['eligibility_status'] = 'COMPETITIVE'
        elif total >= 9:
            score_details['eligibility_status'] = 'POSSIBLE'
        elif total >= 6:
            score_details['eligibility_status'] = 'CHALLENGING'
        else:
            score_details['eligibility_status'] = 'VERY WEAK'
        
        return score_details
    
    def analyze_competition_fixed(self, lat, lng, city):
        """FIXED competition analysis with correct TDHCA coordinate columns"""
        competition_analysis = {
            'one_mile_three_year_violations': 0,
            'two_mile_same_year_violations': 0,
            'nearby_projects': [],
            'competition_penalty': 0,
            'fatal_competition_flaw': False,
            'competition_details': {}
        }
        
        if self.tdhca_data is None:
            competition_analysis['competition_details']['error'] = 'No TDHCA data loaded'
            return competition_analysis
        
        try:
            site_coords = (lat, lng)
            current_year = datetime.now().year
            
            # FIXED: Use correct coordinate column names
            valid_projects = self.tdhca_data.dropna(subset=['Latitude11', 'Longitude11', 'Year'])
            
            if len(valid_projects) == 0:
                competition_analysis['competition_details']['error'] = 'No valid projects with coordinates and years'
                return competition_analysis
            
            competition_analysis['competition_details']['total_projects_checked'] = len(valid_projects)
            
            # Check each competing project
            for idx, project in valid_projects.iterrows():
                project_coords = (project['Latitude11'], project['Longitude11'])
                distance_miles = geodesic(site_coords, project_coords).miles
                project_year = int(project['Year'])
                
                project_info = {
                    'distance_miles': round(distance_miles, 2),
                    'project_year': project_year,
                    'project_name': project.get('Development Name', 'Unknown'),
                    'project_type': project.get('Program Type', 'Unknown'),
                    'tdhca_number': project.get('TDHCA#', 'Unknown')
                }
                
                # One Mile Three Year Rule (Both 4% and 9%)
                if distance_miles <= 1.0 and (current_year - project_year) <= 3:
                    competition_analysis['one_mile_three_year_violations'] += 1
                    project_info['violation_type'] = 'One Mile Three Year - FATAL FLAW'
                    competition_analysis['nearby_projects'].append(project_info)
                
                # Two Mile Same Year Rule (9% only, large counties)
                county = self.get_county_from_city(city)
                if (county in self.large_counties and 
                    distance_miles <= 2.0 and 
                    project_year == current_year):
                    competition_analysis['two_mile_same_year_violations'] += 1
                    project_info['violation_type'] = 'Two Mile Same Year - Major Penalty'
                    if project_info not in competition_analysis['nearby_projects']:
                        competition_analysis['nearby_projects'].append(project_info)
                
                # General nearby projects (within 3 miles for context)
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
                competition_analysis['competition_penalty'] = min(-1 * nearby_count, -5)
            
            competition_analysis['competition_details']['analysis_complete'] = True
            
        except Exception as e:
            print(f"❌ Error analyzing competition for {lat}, {lng}: {e}")
            competition_analysis['competition_details']['error'] = str(e)
        
        return competition_analysis
    
    def process_costar_with_fixed_analysis(self, costar_file):
        """Process CoStar data with FIXED analysis"""
        print("=== CoStar TDHCA Analysis - FIXED VERSION ===")
        
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
            'County_Est', 'AMI_4Person_100pct', 'AMI_4Person_50pct',
            'Rent_1BR_60', 'Rent_2BR_60', 'Rent_3BR_60', 'Rent_4BR_60',
            'Annual_Revenue_Est', 'FEMA_Risk_Level', 'FEMA_Description', 'FEMA_Risk_Score',
            'Deal_Recommendation', 'Analysis_Summary'
        ]
        
        for col in analysis_columns:
            df[col] = None
        
        print("\n🔍 Running FIXED TDHCA analysis...")
        
        for idx, row in df.iterrows():
            if idx % 25 == 0:
                print(f"   Processing {idx+1}/{len(df)} properties...")
            
            lat = row['Latitude']
            lng = row['Longitude']
            city = row['City']
            
            # Enhanced FEMA flood zone analysis
            flood_analysis = self.interpret_fema_flood_zone(
                row.get('Flood Zone'), 
                row.get('Flood Risk')
            )
            df.loc[idx, 'FEMA_Risk_Level'] = flood_analysis['FEMA_Risk_Level']
            df.loc[idx, 'FEMA_Description'] = flood_analysis['FEMA_Description']
            df.loc[idx, 'FEMA_Risk_Score'] = flood_analysis['Risk_Score']
            
            # Add flood analysis to row for scoring
            row_with_flood = row.copy()
            row_with_flood['FEMA_Risk_Level'] = flood_analysis['FEMA_Risk_Level']
            
            # Enhanced 4% Credit Analysis
            score_4pct = self.calculate_enhanced_4pct_scoring(row_with_flood)
            df.loc[idx, '4Pct_Total_Score'] = score_4pct['total_score']
            df.loc[idx, '4Pct_Status'] = score_4pct['eligibility_status']
            df.loc[idx, '4Pct_Breakdown'] = json.dumps(score_4pct['scoring_breakdown'])
            
            # Enhanced 9% Credit Analysis
            score_9pct = self.calculate_enhanced_9pct_scoring(row_with_flood)
            df.loc[idx, '9Pct_Total_Score'] = score_9pct['total_score']
            df.loc[idx, '9Pct_Status'] = score_9pct['eligibility_status']
            df.loc[idx, '9Pct_Breakdown'] = json.dumps(score_9pct['scoring_breakdown'])
            
            # FIXED Competition Analysis
            competition = self.analyze_competition_fixed(lat, lng, city)
            df.loc[idx, 'Competition_1Mile_3Yr'] = competition['one_mile_three_year_violations']
            df.loc[idx, 'Competition_2Mile_SameYr'] = competition['two_mile_same_year_violations']
            df.loc[idx, 'Competition_Fatal_Flaw'] = competition['fatal_competition_flaw']
            df.loc[idx, 'Nearby_Projects_Count'] = len(competition['nearby_projects'])
            df.loc[idx, 'Competition_Details'] = json.dumps(competition['nearby_projects'])
            
            # County and FIXED AMI Analysis
            county = self.get_county_from_city(city)
            df.loc[idx, 'County_Est'] = county
            
            if county:
                ami_data = self.get_ami_data_for_county(county)
                if ami_data:
                    # FIXED: Use median2025 for 100% AMI (industry standard)
                    df.loc[idx, 'AMI_4Person_100pct'] = ami_data.get('median2025', 0)
                    df.loc[idx, 'AMI_4Person_50pct'] = ami_data.get('lim50_25p4', 0)
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
            elif (score_4pct['eligibility_status'] in ['EXCELLENT', 'STRONG'] and 
                  score_9pct['eligibility_status'] in ['HIGHLY COMPETITIVE', 'COMPETITIVE']):
                recommendation = 'EXCELLENT - Both 4% and 9% viable'
            elif score_4pct['eligibility_status'] in ['EXCELLENT', 'STRONG']:
                recommendation = 'STRONG - 4% Bond Deal recommended'
            elif score_4pct['eligibility_status'] == 'VIABLE':
                recommendation = 'GOOD - 4% Bond Deal viable'
            elif score_9pct['eligibility_status'] in ['HIGHLY COMPETITIVE', 'COMPETITIVE']:
                recommendation = 'CONSIDER - 9% Deal competitive'
            elif score_9pct['eligibility_status'] == 'POSSIBLE':
                recommendation = 'CONSIDER - 9% Deal possible'
            else:
                recommendation = 'MARGINAL - Limited potential'
            
            df.loc[idx, 'Deal_Recommendation'] = recommendation
            
            # Enhanced Analysis Summary
            summary = f"4%: {score_4pct['eligibility_status']} ({score_4pct['total_score']}pts), "
            summary += f"9%: {score_9pct['eligibility_status']} ({score_9pct['total_score']}pts), "
            summary += f"Flood: {flood_analysis['FEMA_Risk_Level']}, "
            if competition['fatal_competition_flaw']:
                summary += f"FATAL: {competition['one_mile_three_year_violations']} competing projects"
            else:
                summary += f"Competition: {len(competition['nearby_projects'])} nearby"
            
            df.loc[idx, 'Analysis_Summary'] = summary
        
        # Enhanced sorting with new scoring
        df['Sort_Score'] = df.apply(lambda row: self.calculate_enhanced_sort_score(row), axis=1)
        df_sorted = df.sort_values('Sort_Score', ascending=False)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"CoStar_TDHCA_Analysis_FIXED_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # All analyzed properties
            df_sorted.to_excel(writer, sheet_name='All_Analysis', index=False)
            
            # Top recommendations (no fatal flaws)
            viable_deals = df_sorted[df_sorted['Competition_Fatal_Flaw'] != True]
            top_deals = viable_deals.head(50)
            top_deals.to_excel(writer, sheet_name='Top_50_Deals', index=False)
            
            # Excellent/Strong 4% deals
            strong_4pct = df_sorted[df_sorted['4Pct_Status'].isin(['EXCELLENT', 'STRONG'])]
            strong_4pct.to_excel(writer, sheet_name='Strong_4Pct_Deals', index=False)
            
            # Competitive 9% deals
            competitive_9pct = df_sorted[df_sorted['9Pct_Status'].isin(['HIGHLY COMPETITIVE', 'COMPETITIVE', 'POSSIBLE'])]
            competitive_9pct.to_excel(writer, sheet_name='Competitive_9Pct_Deals', index=False)
            
            # Competition fatal flaws
            fatal_flaws = df_sorted[df_sorted['Competition_Fatal_Flaw'] == True]
            fatal_flaws.to_excel(writer, sheet_name='Competition_Fatal_Flaws', index=False)
        
        print(f"\n📊 FIXED TDHCA Analysis Results:")
        print(f"   Total Analyzed: {len(df)}")
        print(f"   Competition Fatal Flaws: {len(df[df['Competition_Fatal_Flaw'] == True])}")
        print(f"   Excellent/Strong 4% Deals: {len(df[df['4Pct_Status'].isin(['EXCELLENT', 'STRONG'])])}")
        print(f"   Competitive 9% Deals: {len(df[df['9Pct_Status'].isin(['HIGHLY COMPETITIVE', 'COMPETITIVE'])])}")
        print(f"   FEMA High Risk: {len(df[df['FEMA_Risk_Level'].isin(['HIGH', 'VERY HIGH'])])}")
        print(f"\n💾 Results saved to: {output_file}")
        
        return df_sorted, output_file
    
    def calculate_enhanced_sort_score(self, row):
        """Enhanced sorting score for ranking deals"""
        score = 0
        
        # Eliminate fatal flaws immediately
        if row.get('Competition_Fatal_Flaw'):
            return -1000
        
        # Reward excellent deals heavily
        if row.get('4Pct_Status') == 'EXCELLENT':
            score += 200
        elif row.get('4Pct_Status') == 'STRONG':
            score += 150
        elif row.get('4Pct_Status') == 'VIABLE':
            score += 100
        
        # Reward competitive 9% deals
        if row.get('9Pct_Status') == 'HIGHLY COMPETITIVE':
            score += 175
        elif row.get('9Pct_Status') == 'COMPETITIVE':
            score += 125
        elif row.get('9Pct_Status') == 'POSSIBLE':
            score += 75
        
        # Consider sale status
        sale_status = str(row.get('Sale Status', '')).lower()
        if 'active' in sale_status:
            score += 30
        elif 'available' in sale_status:
            score += 25
        elif 'contract' in sale_status:
            score -= 20
        elif 'sold' in sale_status:
            score -= 50
        
        # Flood risk considerations
        flood_risk = row.get('FEMA_Risk_Level', 'Unknown')
        if flood_risk == 'LOW':
            score += 15
        elif flood_risk == 'MODERATE':
            score += 5
        elif flood_risk in ['HIGH', 'VERY HIGH']:
            score -= 25
        
        # Price considerations
        price = row.get('Sale Price', 0)
        if price > 0:
            if price < 750000:  # Very affordable
                score += 20
            elif price < 1500000:  # Reasonable
                score += 10
            elif price > 3000000:  # Very expensive
                score -= 20
        
        # Federal basis boost bonus
        if row.get('Federal_Basis_Boost'):
            score += 10
        
        return score

def main():
    """Run FIXED TDHCA analysis on pre-filtered CoStar data"""
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
        analyzer = CoStarTDHCAAnalyzerFixed()
        results_df, output_file = analyzer.process_costar_with_fixed_analysis(costar_file)
        
        print(f"\n✅ FIXED TDHCA analysis complete!")
        print(f"📁 Results file: {output_file}")
        
        return results_df, output_file
        
    except Exception as e:
        print(f"❌ Error in FIXED TDHCA analysis: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    main()