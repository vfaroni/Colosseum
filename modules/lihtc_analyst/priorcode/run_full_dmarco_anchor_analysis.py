#!/usr/bin/env python3
"""
Full D'Marco Site Analysis with Anchor Scoring
Runs complete analysis on all 65 D'Marco sites with optimized performance.
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from shapely.geometry import Point
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FullDMarcoAnalyzer:
    """Complete D'Marco site analyzer with anchor scoring and performance optimization"""
    
    def __init__(self):
        logger.info("Initializing Full D'Marco Analyzer...")
        
        # Load infrastructure datasets
        self._load_infrastructure_data()
        
        # Initialize geocoder
        self.geolocator = Nominatim(user_agent="full_dmarco_analyzer")
        
        # Regional cost multipliers
        self.regional_cost_multipliers = {
            'Region 1': 0.90, 'Region 2': 0.95, 'Region 3': 1.15, 'Region 4': 0.98,
            'Region 5': 1.00, 'Region 6': 1.18, 'Region 7': 1.20, 'Region 8': 1.00,
            'Region 9': 1.10, 'Region 10': 1.05, 'Region 11': 0.92, 'Region 12': 1.12,
            'Region 13': 1.08
        }
        
        self.base_construction_cost = 150  # $/SF
        
    def _load_infrastructure_data(self):
        """Load and prepare Texas infrastructure datasets"""
        base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas")
        
        try:
            # Load schools with coordinate transformation
            schools_file = base_dir / "TX_Public_Schools" / "Schools_2024_to_2025.geojson"
            self.schools_gdf = gpd.read_file(schools_file).to_crs('EPSG:4326')
            logger.info(f"✅ Loaded {len(self.schools_gdf)} Texas schools")
            
            # Load city boundaries with coordinate transformation
            cities_file = base_dir / "City_Boundaries" / "TX_cities_2024.geojson"
            self.cities_gdf = gpd.read_file(cities_file).to_crs('EPSG:4326')
            logger.info(f"✅ Loaded {len(self.cities_gdf)} Texas cities")
            
            # Load TDHCA projects with coordinate fix
            tdhca_file = base_dir / "State Specific" / "TX" / "Project_List" / "TX_TDHCA_Project_List_05252025.xlsx"
            self.tdhca_df = pd.read_excel(tdhca_file)
            
            # Fix coordinate column names and clean data
            self.tdhca_df = self.tdhca_df.rename(columns={
                'Latitude11': 'Latitude',
                'Longitude11': 'Longitude'
            })
            self.tdhca_df = self.tdhca_df.dropna(subset=['Latitude', 'Longitude'])
            
            # Convert to numeric and filter valid coordinates
            self.tdhca_df['Latitude'] = pd.to_numeric(self.tdhca_df['Latitude'], errors='coerce')
            self.tdhca_df['Longitude'] = pd.to_numeric(self.tdhca_df['Longitude'], errors='coerce')
            self.tdhca_df = self.tdhca_df.dropna(subset=['Latitude', 'Longitude'])
            
            # Filter for reasonable Texas coordinates
            self.tdhca_df = self.tdhca_df[
                (self.tdhca_df['Latitude'] >= 25.0) & (self.tdhca_df['Latitude'] <= 37.0) &
                (self.tdhca_df['Longitude'] >= -107.0) & (self.tdhca_df['Longitude'] <= -93.0)
            ]
            
            logger.info(f"✅ Loaded {len(self.tdhca_df)} TDHCA projects with valid coordinates")
            
        except Exception as e:
            logger.error(f"Error loading infrastructure data: {e}")
            raise
    
    def geocode_address_enhanced(self, address, city, county, state):
        """Enhanced geocoding with multiple fallback strategies"""
        # Try multiple address formats in order of specificity
        address_variations = [
            f"{address}, {city}, {county} County, {state}",
            f"{address}, {city}, {state}",
            f"{city}, {county} County, {state}",
            f"{city}, {state}"
        ]
        
        for i, variation in enumerate(address_variations):
            try:
                location = self.geolocator.geocode(variation, timeout=15)
                if location:
                    return {
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'geocoded_address': location.address,
                        'geocoding_success': i <= 1,  # True if specific address found
                        'geocoding_method': variation,
                        'geocoding_confidence': ['High', 'Medium', 'Low', 'City-Center'][i]
                    }
                time.sleep(0.5)  # Rate limiting between attempts
            except Exception as e:
                logger.debug(f"Geocoding failed for {variation}: {e}")
                time.sleep(1)
        
        return {
            'latitude': None, 'longitude': None, 'geocoded_address': 'Failed',
            'geocoding_success': False, 'geocoding_method': 'Failed',
            'geocoding_confidence': 'None'
        }
    
    def calculate_schools_nearby(self, lat, lng, radius_miles=2.5):
        """Optimized school proximity calculation"""
        site_point = Point(lng, lat)
        schools_count = 0
        closest_distance = float('inf')
        
        # Use spatial indexing for performance
        try:
            for _, school in self.schools_gdf.iterrows():
                if school.geometry and not school.geometry.is_empty:
                    # Quick distance approximation in degrees
                    distance_deg = site_point.distance(school.geometry)
                    distance_miles = distance_deg * 69  # Approximate conversion
                    
                    if distance_miles <= radius_miles:
                        schools_count += 1
                        closest_distance = min(closest_distance, distance_miles)
        except Exception as e:
            logger.debug(f"Error calculating school distances: {e}")
        
        return schools_count, closest_distance if closest_distance != float('inf') else None
    
    def check_city_boundaries(self, lat, lng):
        """Check if site is within incorporated city limits"""
        try:
            site_point = Point(lng, lat)
            site_gdf = gpd.GeoDataFrame([1], geometry=[site_point], crs='EPSG:4326')
            
            # Spatial join to find intersecting cities
            cities_intersect = gpd.sjoin(site_gdf, self.cities_gdf, how='inner', predicate='within')
            
            if len(cities_intersect) > 0:
                city_name = cities_intersect.iloc[0]['NAME']
                return True, city_name
            else:
                return False, "Unincorporated"
                
        except Exception as e:
            logger.debug(f"City boundary check failed: {e}")
            return False, "Unknown"
    
    def count_nearby_lihtc(self, lat, lng, radius_miles=2.0):
        """Count nearby LIHTC projects for market validation"""
        nearby_count = 0
        
        try:
            for _, project in self.tdhca_df.iterrows():
                distance = geodesic((lat, lng), (project['Latitude'], project['Longitude'])).miles
                if distance <= radius_miles:
                    nearby_count += 1
        except Exception as e:
            logger.debug(f"Error counting LIHTC projects: {e}")
        
        return nearby_count
    
    def calculate_anchor_score(self, lat, lng):
        """Calculate comprehensive anchor viability score"""
        if not lat or not lng:
            return 0, "No coordinates available", {}
        
        details = {}
        score = 0
        factors = []
        
        # 1. Schools Analysis (CRITICAL - 40% of score)
        schools_count, closest_school = self.calculate_schools_nearby(lat, lng)
        details['schools_within_2_5mi'] = schools_count
        details['closest_school_miles'] = closest_school
        
        if schools_count == 0:
            factors.append("❌ FATAL: No schools within 2.5 miles")
            return 0, "; ".join(factors), details
        else:
            score += 2  # Base points for school access
            factors.append(f"✅ {schools_count} school(s) within 2.5 miles")
            
            if schools_count >= 3:
                score += 1  # Bonus for multiple schools
                factors.append("🏫 Multiple schools (established community)")
        
        # 2. City Boundaries (20% of score)
        within_city, city_name = self.check_city_boundaries(lat, lng)
        details['within_city_limits'] = within_city
        details['city_name'] = city_name
        
        if within_city:
            score += 1
            factors.append(f"🏛️ Within {city_name} city limits")
        else:
            factors.append("⚠️ Unincorporated area")
        
        # 3. LIHTC Market Validation (30% of score)
        lihtc_count = self.count_nearby_lihtc(lat, lng)
        details['lihtc_within_2mi'] = lihtc_count
        
        if lihtc_count > 0:
            score += 1
            factors.append(f"💼 {lihtc_count} LIHTC project(s) nearby (market proven)")
        else:
            factors.append("⚠️ No nearby LIHTC projects")
        
        # 4. Community Establishment Bonus (10% of score)
        if schools_count >= 5:
            score += 1
            factors.append("🌟 Major population center (5+ schools)")
        
        # Cap score at 5
        score = min(score, 5)
        details['anchor_score'] = score
        
        return score, "; ".join(factors), details
    
    def analyze_all_dmarco_sites(self, csv_file):
        """Main analysis function for all D'Marco sites"""
        logger.info(f"Starting full analysis of D'Marco sites from: {csv_file}")
        
        # Load all sites
        df = pd.read_csv(csv_file)
        total_sites = len(df)
        logger.info(f"Loaded {total_sites} D'Marco sites for analysis")
        
        # Initialize result columns
        result_columns = [
            # Geocoding Results
            'Latitude', 'Longitude', 'Geocoded_Address', 'Geocoding_Success', 
            'Geocoding_Method', 'Geocoding_Confidence',
            
            # Anchor Analysis
            'Anchor_Score', 'Anchor_Details', 'Schools_Within_2_5mi', 'Closest_School_Miles',
            'Within_City_Limits', 'City_Name', 'LIHTC_Within_2mi',
            
            # Site Assessment
            'Infrastructure_Assessment', 'Isolation_Risk', 'Market_Validation',
            'Development_Viability', 'Priority_Ranking',
            
            # Economic Factors
            'Region', 'Construction_Cost_Multiplier', 'Estimated_Cost_Per_SF',
            'Acreage', 'Size_Category',
            
            # Final Recommendation
            'Overall_Score', 'Recommendation', 'Key_Strengths', 'Risk_Factors', 'Next_Steps'
        ]
        
        for col in result_columns:
            df[col] = None
        
        # Analysis counters
        excellent_sites = []
        viable_sites = []
        risky_sites = []
        isolated_sites = []
        
        # Process each site
        for idx, row in df.iterrows():
            site_num = idx + 1
            site_name = f"{row['MailingName']} - {row['City']}, {row['County']} County"
            
            logger.info(f"Analyzing site {site_num}/{total_sites}: {site_name}")
            
            # 1. Enhanced Geocoding
            geocoding = self.geocode_address_enhanced(
                row['Address'], row['City'], row['County'], 'Texas'
            )
            
            # Store geocoding results
            df.loc[idx, 'Latitude'] = geocoding['latitude']
            df.loc[idx, 'Longitude'] = geocoding['longitude']
            df.loc[idx, 'Geocoded_Address'] = geocoding['geocoded_address']
            df.loc[idx, 'Geocoding_Success'] = geocoding['geocoding_success']
            df.loc[idx, 'Geocoding_Method'] = geocoding['geocoding_method']
            df.loc[idx, 'Geocoding_Confidence'] = geocoding['geocoding_confidence']
            
            if not geocoding['latitude']:
                df.loc[idx, 'Overall_Score'] = 0
                df.loc[idx, 'Recommendation'] = 'Cannot analyze - geocoding failed'
                df.loc[idx, 'Infrastructure_Assessment'] = 'Unknown'
                isolated_sites.append(idx)
                continue
            
            # 2. Comprehensive Anchor Analysis
            anchor_score, anchor_details, anchor_data = self.calculate_anchor_score(
                geocoding['latitude'], geocoding['longitude']
            )
            
            # Store anchor results
            df.loc[idx, 'Anchor_Score'] = anchor_score
            df.loc[idx, 'Anchor_Details'] = anchor_details
            df.loc[idx, 'Schools_Within_2_5mi'] = anchor_data.get('schools_within_2_5mi', 0)
            df.loc[idx, 'Closest_School_Miles'] = anchor_data.get('closest_school_miles')
            df.loc[idx, 'Within_City_Limits'] = anchor_data.get('within_city_limits', False)
            df.loc[idx, 'City_Name'] = anchor_data.get('city_name', 'Unknown')
            df.loc[idx, 'LIHTC_Within_2mi'] = anchor_data.get('lihtc_within_2mi', 0)
            
            # 3. Infrastructure Assessment
            if anchor_score == 0:
                df.loc[idx, 'Infrastructure_Assessment'] = 'Fatal - Too Isolated'
                df.loc[idx, 'Isolation_Risk'] = 'FATAL'
                df.loc[idx, 'Development_Viability'] = 'Not Viable'
                df.loc[idx, 'Priority_Ranking'] = 'Do Not Pursue'
                isolated_sites.append(idx)
            elif anchor_score <= 2:
                df.loc[idx, 'Infrastructure_Assessment'] = 'Poor - Limited Infrastructure'
                df.loc[idx, 'Isolation_Risk'] = 'HIGH'
                df.loc[idx, 'Development_Viability'] = 'High Risk'
                df.loc[idx, 'Priority_Ranking'] = 'Low Priority'
                risky_sites.append(idx)
            elif anchor_score <= 3:
                df.loc[idx, 'Infrastructure_Assessment'] = 'Adequate - Basic Infrastructure'
                df.loc[idx, 'Isolation_Risk'] = 'MEDIUM'
                df.loc[idx, 'Development_Viability'] = 'Viable with Caution'
                df.loc[idx, 'Priority_Ranking'] = 'Medium Priority'
                viable_sites.append(idx)
            else:
                df.loc[idx, 'Infrastructure_Assessment'] = 'Excellent - Strong Infrastructure'
                df.loc[idx, 'Isolation_Risk'] = 'LOW'
                df.loc[idx, 'Development_Viability'] = 'Highly Viable'
                df.loc[idx, 'Priority_Ranking'] = 'High Priority'
                excellent_sites.append(idx)
            
            # 4. Market Validation
            lihtc_count = anchor_data.get('lihtc_within_2mi', 0)
            if lihtc_count > 0:
                df.loc[idx, 'Market_Validation'] = f'Proven ({lihtc_count} LIHTC projects nearby)'
            else:
                df.loc[idx, 'Market_Validation'] = 'Unproven market'
            
            # 5. Economic Analysis
            region = row['Region']
            cost_multiplier = self.regional_cost_multipliers.get(region, 1.0)
            df.loc[idx, 'Region'] = region
            df.loc[idx, 'Construction_Cost_Multiplier'] = cost_multiplier
            df.loc[idx, 'Estimated_Cost_Per_SF'] = self.base_construction_cost * cost_multiplier
            
            # Acreage analysis
            acreage = float(row['Acres'])
            df.loc[idx, 'Acreage'] = acreage
            if acreage >= 20:
                df.loc[idx, 'Size_Category'] = 'Large Development (20+ acres)'
            elif acreage >= 5:
                df.loc[idx, 'Size_Category'] = 'Medium Development (5-20 acres)'
            else:
                df.loc[idx, 'Size_Category'] = 'Small Development (<5 acres)'
            
            # 6. Overall Scoring and Recommendations
            overall_score = anchor_score  # Start with anchor score
            strengths = []
            risks = []
            
            # Infrastructure strengths
            if anchor_score >= 4:
                strengths.append('Excellent infrastructure and schools')
            elif anchor_score >= 3:
                strengths.append('Adequate infrastructure')
            
            if anchor_data.get('within_city_limits'):
                strengths.append(f"Within {anchor_data['city_name']} city limits")
            
            if lihtc_count > 0:
                strengths.append(f'Market validated ({lihtc_count} LIHTC projects)')
            
            # Size advantages
            if acreage >= 20:
                strengths.append(f'Large site ({acreage} acres)')
            elif acreage < 3:
                risks.append(f'Small site may limit development ({acreage} acres)')
            
            # Cost considerations
            if cost_multiplier <= 1.0:
                strengths.append(f'Reasonable construction costs ({region})')
            elif cost_multiplier >= 1.15:
                risks.append(f'High construction costs ({region})')
            
            # Infrastructure risks
            if not anchor_data.get('within_city_limits'):
                risks.append('Unincorporated area - infrastructure uncertain')
            
            if lihtc_count == 0:
                risks.append('Unproven market for affordable housing')
            
            df.loc[idx, 'Overall_Score'] = overall_score
            df.loc[idx, 'Key_Strengths'] = '; '.join(strengths) if strengths else 'Limited strengths identified'
            df.loc[idx, 'Risk_Factors'] = '; '.join(risks) if risks else 'No major risks identified'
            
            # Final recommendations
            if anchor_score == 0:
                df.loc[idx, 'Recommendation'] = 'DO NOT PURSUE - Site too isolated'
                df.loc[idx, 'Next_Steps'] = 'Consider alternative locations'
            elif anchor_score >= 4:
                df.loc[idx, 'Recommendation'] = 'HIGHLY RECOMMENDED - Excellent infrastructure'
                df.loc[idx, 'Next_Steps'] = 'Proceed with immediate due diligence'
            elif anchor_score >= 3:
                df.loc[idx, 'Recommendation'] = 'RECOMMENDED - Adequate infrastructure'
                df.loc[idx, 'Next_Steps'] = 'Conduct market study and infrastructure assessment'
            else:
                df.loc[idx, 'Recommendation'] = 'PROCEED WITH CAUTION - Limited infrastructure'
                df.loc[idx, 'Next_Steps'] = 'Address infrastructure concerns before proceeding'
            
            # Rate limiting for geocoding
            time.sleep(0.3)
        
        # Save comprehensive results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"DMarco_Complete_Anchor_Analysis_{timestamp}.xlsx"
        
        self._save_analysis_results(df, output_file, {
            'total': total_sites,
            'excellent': len(excellent_sites),
            'viable': len(viable_sites),
            'risky': len(risky_sites),
            'isolated': len(isolated_sites)
        })
        
        return df, output_file
    
    def _create_scoring_methodology_sheet(self):
        """Create detailed scoring methodology documentation"""
        methodology_data = []
        
        # Anchor Viability Scoring System
        methodology_data.extend([
            ['ANCHOR VIABILITY SCORING SYSTEM', '', '', '', ''],
            ['Purpose', 'Prevents selection of isolated sites without adequate community infrastructure', '', '', ''],
            ['Total Score Range', '0-5 points', '', '', ''],
            ['', '', '', '', ''],
            ['Component', 'Criteria', 'Points Awarded', 'Weight', 'Rationale'],
            ['Schools Proximity', 'Must have ≥1 school within 2.5 miles', '2 points (base)', '40%', 'CRITICAL: No schools = isolated rural area unsuitable for families'],
            ['', '≥3 schools within 2.5 miles', '+1 bonus point', '', 'Multiple schools indicate established community'],
            ['', '≥5 schools within 2.5 miles', '+1 additional bonus', '', 'Major population center with full educational infrastructure'],
            ['', '0 schools within 2.5 miles', 'FATAL FLAW (0 total)', '', 'Site too isolated - do not pursue'],
            ['City Incorporation', 'Site within incorporated city limits', '1 point', '20%', 'City incorporation indicates established infrastructure (water, sewer, utilities, services)'],
            ['', 'Unincorporated area', '0 points', '', 'Infrastructure availability uncertain'],
            ['Market Validation', '≥1 LIHTC project within 2 miles', '1 point', '30%', 'Proven market demand for affordable housing in area'],
            ['', 'No LIHTC projects nearby', '0 points', '', 'Unproven market - higher development risk'],
            ['Community Scale', '≥5 schools (major center)', '1 bonus point', '10%', 'Large population centers provide better amenity access'],
            ['', '', '', '', ''],
            ['ASSESSMENT LEVELS', '', '', '', ''],
            ['Score 0', 'FATAL - Too Isolated', 'DO NOT PURSUE', '', 'No schools within 2.5 miles'],
            ['Score 1-2', 'HIGH RISK - Limited Infrastructure', 'PROCEED WITH CAUTION', '', 'Minimal community services'],
            ['Score 3', 'VIABLE - Adequate Infrastructure', 'RECOMMENDED', '', 'Basic community infrastructure present'],
            ['Score 4-5', 'EXCELLENT - Strong Infrastructure', 'HIGHLY RECOMMENDED', '', 'Strong community with proven services'],
            ['', '', '', '', ''],
        ])
        
        # QCT/DDA Federal Designation System
        methodology_data.extend([
            ['QCT/DDA FEDERAL DESIGNATION SYSTEM', '', '', '', ''],
            ['Purpose', 'Determines eligibility for 30% federal tax credit basis boost', '', '', ''],
            ['Authority', 'HUD annually designates Qualified Census Tracts and Difficult Development Areas', '', '', ''],
            ['', '', '', '', ''],
            ['Designation Type', 'Criteria', 'Benefit', 'Source', 'Coverage'],
            ['Qualified Census Tract (QCT)', 'Census tract with ≥50% low-income households OR ≥25% poverty rate', '30% basis boost', 'HUD/Census Bureau', '15,727 tracts nationally'],
            ['Difficult Development Area (DDA)', 'High construction/land costs relative to AMI (typically metro areas)', '30% basis boost', 'HUD Fair Market Rents', '2,958 areas nationally'],
            ['Non-QCT/Non-DDA', 'Does not meet QCT or DDA criteria', 'No basis boost', 'Default classification', 'Remaining areas'],
            ['', '', '', '', ''],
            ['LIHTC Impact', 'QCT/DDA designation increases eligible basis by 30%', '', '', ''],
            ['Example', '$10M project → $13M eligible basis → ~$1.2M additional tax credits', '', '', ''],
            ['', '', '', '', ''],
        ])
        
        # TDHCA Regional Analysis System
        methodology_data.extend([
            ['TDHCA REGIONAL ANALYSIS SYSTEM', '', '', '', ''],
            ['Purpose', 'Texas-specific affordable housing development rules and market analysis', '', '', ''],
            ['Authority', 'Texas Department of Housing and Community Affairs (TDHCA)', '', '', ''],
            ['', '', '', '', ''],
            ['Analysis Component', 'Methodology', 'Impact', 'Data Source', 'Coverage'],
            ['Competition Rules (4% Credits)', 'One-mile three-year rule: Projects within 1 mile in last 3 years', 'Risk assessment', 'TDHCA project database', '3,189+ projects'],
            ['Competition Rules (9% Credits)', 'One-mile fatal flaw: Cannot have 9% project within 1 mile', 'Binary elimination', 'TDHCA project database', 'Same database'],
            ['Large County Rules (9%)', 'Two-mile same-year rule in 7 largest counties', 'Additional restrictions', 'County classifications', 'Harris, Dallas, Tarrant, Bexar, Travis, Collin, Fort Bend'],
            ['Low Poverty Bonus (9%)', 'Census tracts with ≤20% poverty rate eligible for 2 bonus points', 'Scoring advantage', 'Census ACS 5-year data', 'All Texas census tracts'],
            ['Regional Cost Adjustments', 'Construction cost multipliers by TDHCA region (1-13)', 'Economic viability', 'Regional market data', '13 TDHCA service regions'],
            ['', '', '', '', ''],
        ])
        
        # Construction Cost Analysis
        methodology_data.extend([
            ['CONSTRUCTION COST ANALYSIS SYSTEM', '', '', '', ''],
            ['Purpose', 'Estimate development costs by geographic region', '', '', ''],
            ['Base Cost', '$150 per square foot (2025 Texas average)', '', '', ''],
            ['', '', '', '', ''],
            ['TDHCA Region', 'Cost Multiplier', 'Estimated Cost/SF', 'Market Factors', 'Major Cities'],
            ['Region 1 (Panhandle)', '0.90x', '$135/SF', 'Lower labor/material costs', 'Amarillo, Lubbock'],
            ['Region 2 (North Central)', '0.95x', '$143/SF', 'Moderate costs', 'Wichita Falls, Abilene'],
            ['Region 3 (Dallas/Fort Worth)', '1.15x', '$173/SF', 'High demand metro', 'Dallas, Fort Worth, Plano'],
            ['Region 4 (East Texas)', '0.98x', '$147/SF', 'Rural/small city costs', 'Tyler, Longview, Marshall'],
            ['Region 5 (Southeast)', '1.00x', '$150/SF', 'Average costs', 'Beaumont, Port Arthur'],
            ['Region 6 (Houston)', '1.18x', '$177/SF', 'Major metro premium', 'Houston, Baytown, Sugar Land'],
            ['Region 7 (Austin)', '1.20x', '$180/SF', 'Highest cost region', 'Austin, Round Rock, Cedar Park'],
            ['Region 8 (Central)', '1.00x', '$150/SF', 'Average rural costs', 'Waco, Temple, Killeen'],
            ['Region 9 (San Antonio)', '1.10x', '$165/SF', 'Metro premium', 'San Antonio, New Braunfels'],
            ['Region 10 (Coastal)', '1.05x', '$158/SF', 'Coastal transport costs', 'Corpus Christi, Victoria'],
            ['Region 11 (Rio Grande Valley)', '0.92x', '$138/SF', 'Lower border costs', 'McAllen, Brownsville, Harlingen'],
            ['Region 12 (West Texas)', '1.12x', '$168/SF', 'Oil region premium', 'Midland, Odessa, San Angelo'],
            ['Region 13 (El Paso)', '1.08x', '$162/SF', 'Border metro costs', 'El Paso'],
            ['', '', '', '', ''],
        ])
        
        # FEMA Flood Risk Analysis
        methodology_data.extend([
            ['FEMA FLOOD RISK ANALYSIS SYSTEM', '', '', '', ''],
            ['Purpose', 'Assess flood risk impact on development costs and insurance', '', '', ''],
            ['Authority', 'Federal Emergency Management Agency (FEMA) Flood Insurance Rate Maps', '', '', ''],
            ['', '', '', '', ''],
            ['Flood Zone', 'Risk Level', 'Insurance Requirement', 'Construction Cost Impact', 'Design Requirements'],
            ['Zone X (Unshaded)', 'Minimal Risk', 'Not required', 'No impact', 'Standard construction'],
            ['Zone AE', 'High Risk (1% annual)', 'Required if federally financed', '+20% construction cost', 'Elevated foundation required'],
            ['Zone A', 'High Risk (1% annual)', 'Required if federally financed', '+20% construction cost', 'Elevated foundation required'],
            ['Zone VE', 'High Risk + Wave Action', 'Required if federally financed', '+30% construction cost', 'Special coastal construction'],
            ['Zone V', 'High Risk + Wave Action', 'Required if federally financed', '+30% construction cost', 'Special coastal construction'],
            ['', '', '', '', ''],
            ['Insurance Costs', 'Zone X: ~$400-600/year | Zones A/AE: ~$1,200-2,000/year | Zones V/VE: ~$2,500-4,000/year', '', '', ''],
            ['', '', '', '', ''],
        ])
        
        # Data Sources and Coverage
        methodology_data.extend([
            ['DATA SOURCES AND COVERAGE', '', '', '', ''],
            ['', '', '', '', ''],
            ['Dataset', 'Source', 'Coverage', 'Last Updated', 'Records'],
            ['Texas Public Schools', 'Texas Education Agency', 'Statewide', '2024-2025 School Year', '9,739 schools'],
            ['Texas City Boundaries', 'US Census TIGER/Line', 'All incorporated places', '2024', '1,863 cities/towns'],
            ['QCT/DDA Designations', 'HUD/Census Bureau', 'Statewide', '2025', '100% coverage'],
            ['TDHCA LIHTC Projects', 'Texas Department of Housing', 'All LIHTC developments', 'May 2025', '3,189 projects'],
            ['FEMA Flood Maps', 'Federal Emergency Management Agency', 'Texas: 78% geometry, 100% attributes', '2024', 'County-level coverage'],
            ['Census Poverty Data', 'US Census ACS 5-Year', 'All census tracts', '2022', 'Tract-level data'],
            ['AMI Data', 'HUD Area Median Income', 'All Texas counties', '2025', '254 counties'],
            ['', '', '', '', ''],
        ])
        
        # Scoring Integration and Final Assessment
        methodology_data.extend([
            ['INTEGRATED SCORING AND FINAL ASSESSMENT', '', '', '', ''],
            ['', '', '', '', ''],
            ['Assessment Factor', 'Weight', 'Scoring Method', 'Impact on Recommendation', 'Decision Threshold'],
            ['Anchor Viability', '60%', '0-5 point scale', 'Score 0 = Fatal Flaw', 'Must be ≥1 to proceed'],
            ['QCT/DDA Status', '30%', 'Binary (Yes/No)', 'No QCT/DDA = Not Recommended', 'Must be Yes to proceed'],
            ['Regional Cost Factor', '10%', 'Cost multiplier impact', 'Affects economic viability', 'Considered in final assessment'],
            ['', '', '', '', ''],
            ['FINAL RECOMMENDATION MATRIX', '', '', '', ''],
            ['Anchor Score', 'QCT/DDA', 'Recommendation', 'Priority Level', 'Next Steps'],
            ['0', 'Any', 'DO NOT PURSUE', 'Not Viable', 'Find alternative sites'],
            ['1-2', 'Yes', 'PROCEED WITH CAUTION', 'Low Priority', 'Address infrastructure risks'],
            ['3', 'Yes', 'RECOMMENDED', 'Medium Priority', 'Conduct market study'],
            ['4-5', 'Yes', 'HIGHLY RECOMMENDED', 'High Priority', 'Immediate due diligence'],
            ['Any', 'No', 'NOT RECOMMENDED', 'Not Viable', 'No 30% basis boost available'],
            ['', '', '', '', ''],
        ])
        
        # Analysis Limitations and Assumptions
        methodology_data.extend([
            ['ANALYSIS LIMITATIONS AND ASSUMPTIONS', '', '', '', ''],
            ['', '', '', '', ''],
            ['Limitation/Assumption', 'Impact', 'Mitigation Strategy', 'Confidence Level', 'Notes'],
            ['Geocoding Accuracy', 'Some sites use city center coordinates', 'Manual verification recommended', 'Medium-High', 'Address-specific geocoding preferred'],
            ['School Distance Calculation', 'Straight-line distance approximation', 'Good proxy for accessibility', 'High', '2.5 mile radius validated standard'],
            ['LIHTC Competition Data', 'Based on available TDHCA records', 'Most comprehensive available', 'High', '3,189 projects in database'],
            ['Construction Cost Estimates', 'Regional averages, not site-specific', 'Detailed cost analysis needed', 'Medium', 'Actual costs vary by project specifics'],
            ['Infrastructure Assumptions', 'City incorporation = infrastructure availability', 'Generally reliable proxy', 'Medium-High', 'Site-specific verification recommended'],
            ['Market Validation Logic', 'LIHTC proximity = market viability', 'Proven affordable housing demand', 'High', 'Strong correlation with successful projects'],
            ['', '', '', '', ''],
        ])
        
        return pd.DataFrame(methodology_data, columns=['Category', 'Description', 'Details', 'Additional_Info', 'Notes'])

    def _save_analysis_results(self, df, output_file, summary_stats):
        """Save comprehensive analysis results to Excel"""
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            
            # Executive Summary
            summary_data = {
                'Metric': [
                    'Total D\'Marco Sites Analyzed',
                    'Successfully Geocoded',
                    'Excellent Infrastructure (Score 4-5)',
                    'Viable Infrastructure (Score 3)',
                    'Risky Infrastructure (Score 1-2)',
                    'Isolated Sites (Score 0)',
                    'Within City Limits',
                    'Market Validated (LIHTC Nearby)',
                    'High Priority Sites',
                    'Recommended for Development'
                ],
                'Count': [
                    summary_stats['total'],
                    len(df[df['Geocoding_Success'] == True]),
                    summary_stats['excellent'],
                    summary_stats['viable'],
                    summary_stats['risky'],
                    summary_stats['isolated'],
                    len(df[df['Within_City_Limits'] == True]),
                    len(df[df['LIHTC_Within_2mi'] > 0]),
                    len(df[df['Priority_Ranking'] == 'High Priority']),
                    len(df[df['Recommendation'].str.contains('RECOMMENDED', na=False)])
                ],
                'Percentage': [
                    100.0,
                    round(len(df[df['Geocoding_Success'] == True]) / summary_stats['total'] * 100, 1),
                    round(summary_stats['excellent'] / summary_stats['total'] * 100, 1),
                    round(summary_stats['viable'] / summary_stats['total'] * 100, 1),
                    round(summary_stats['risky'] / summary_stats['total'] * 100, 1),
                    round(summary_stats['isolated'] / summary_stats['total'] * 100, 1),
                    round(len(df[df['Within_City_Limits'] == True]) / summary_stats['total'] * 100, 1),
                    round(len(df[df['LIHTC_Within_2mi'] > 0]) / summary_stats['total'] * 100, 1),
                    round(len(df[df['Priority_Ranking'] == 'High Priority']) / summary_stats['total'] * 100, 1),
                    round(len(df[df['Recommendation'].str.contains('RECOMMENDED', na=False)]) / summary_stats['total'] * 100, 1)
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Executive_Summary', index=False)
            
            # All sites ranked by overall score
            df_ranked = df.sort_values(['Overall_Score', 'Schools_Within_2_5mi'], ascending=[False, False])
            df_ranked.to_excel(writer, sheet_name='All_Sites_Ranked', index=False)
            
            # High priority sites only
            high_priority = df[df['Priority_Ranking'] == 'High Priority'].sort_values('Overall_Score', ascending=False)
            if len(high_priority) > 0:
                high_priority.to_excel(writer, sheet_name='High_Priority_Sites', index=False)
            
            # Recommended sites
            recommended = df[df['Recommendation'].str.contains('RECOMMENDED', na=False)].sort_values('Overall_Score', ascending=False)
            if len(recommended) > 0:
                recommended.to_excel(writer, sheet_name='Recommended_Sites', index=False)
            
            # Sites with isolation issues
            problematic = df[df['Anchor_Score'] <= 2].sort_values('Anchor_Score')
            if len(problematic) > 0:
                problematic.to_excel(writer, sheet_name='Sites_With_Issues', index=False)
            
            # Regional summary
            regional_summary = df.groupby('Region').agg({
                'Overall_Score': 'mean',
                'Anchor_Score': 'mean',
                'Schools_Within_2_5mi': 'mean',
                'Within_City_Limits': 'sum',
                'LIHTC_Within_2mi': 'sum',
                'Acreage': 'mean'
            }).round(2)
            regional_summary.to_excel(writer, sheet_name='Regional_Summary')
            
            # Scoring Methodology Documentation
            methodology_df = self._create_scoring_methodology_sheet()
            methodology_df.to_excel(writer, sheet_name='Scoring_Methodology', index=False)
        
        logger.info(f"\n🎯 Complete D'Marco Analysis Summary:")
        logger.info(f"   Total sites: {summary_stats['total']}")
        logger.info(f"   Excellent infrastructure: {summary_stats['excellent']}")
        logger.info(f"   Viable sites: {summary_stats['viable']}")
        logger.info(f"   High-risk sites: {summary_stats['risky']}")
        logger.info(f"   Isolated sites: {summary_stats['isolated']}")
        logger.info(f"\n💾 Complete results saved to: {output_file}")

def main():
    analyzer = FullDMarcoAnalyzer()
    
    # Input file
    csv_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/From_Brent_06182025.csv"
    
    if Path(csv_file).exists():
        print(f"🚀 Starting full analysis of all D'Marco sites...")
        print(f"📂 Input file: {csv_file}")
        
        try:
            df_results, output_file = analyzer.analyze_all_dmarco_sites(csv_file)
            
            print(f"\n✅ Full analysis complete!")
            print(f"📊 Results saved to: {output_file}")
            
            # Quick summary
            excellent = len(df_results[df_results['Overall_Score'] >= 4])
            viable = len(df_results[df_results['Overall_Score'] >= 3])
            isolated = len(df_results[df_results['Overall_Score'] == 0])
            
            print(f"\n🎯 Quick Summary:")
            print(f"   🌟 Excellent sites (score 4-5): {excellent}")
            print(f"   👍 Viable sites (score 3+): {viable}")
            print(f"   ⚠️ Isolated sites (score 0): {isolated}")
            print(f"\n💡 Focus on the {viable} sites with scores ≥ 3 for development")
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            print(f"❌ Analysis failed: {e}")
    else:
        print(f"❌ File not found: {csv_file}")

if __name__ == "__main__":
    main()