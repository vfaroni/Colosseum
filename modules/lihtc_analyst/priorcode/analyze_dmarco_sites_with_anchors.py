#!/usr/bin/env python3
"""
Enhanced D'Marco Site Analyzer with Anchor Viability Scoring
Addresses isolation issues by requiring proximity to essential services and infrastructure.

Key Features:
- School proximity requirements (eliminates rural isolation)
- City boundaries check (infrastructure validation)
- LIHTC proximity as market validation indicator
- Comprehensive anchor scoring system

Author: Claude Code
Date: July 2025
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path
from datetime import datetime
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from shapely.geometry import Point
import requests
import time
import logging
from tdhca_qct_focused_analyzer import TDHCAQCTFocusedAnalyzer

class EnhancedDMarcoAnalyzer:
    """Enhanced analyzer with anchor viability scoring to prevent isolated site selection"""
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize the base analyzer
        self.base_analyzer = TDHCAQCTFocusedAnalyzer()
        
        # Geocoding
        self.geolocator = Nominatim(user_agent="enhanced_dmarco_analyzer")
        
        # Load Texas infrastructure datasets
        self._load_infrastructure_data()
        
        # Construction cost multipliers by region
        self.regional_cost_multipliers = {
            'Region 1': 0.90,   'Region 2': 0.95,   'Region 3': 1.15,
            'Region 4': 0.98,   'Region 5': 1.00,   'Region 6': 1.18,
            'Region 7': 1.20,   'Region 8': 1.00,   'Region 9': 1.10,
            'Region 10': 1.05,  'Region 11': 0.92,  'Region 12': 1.12,
            'Region 13': 1.08
        }
        
        self.base_construction_cost = 150  # $/SF
        
    def _load_infrastructure_data(self):
        """Load Texas infrastructure datasets for anchor analysis"""
        base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas")
        
        try:
            # Load Texas schools
            schools_file = base_dir / "TX_Public_Schools" / "Schools_2024_to_2025.geojson"
            if schools_file.exists():
                self.schools_gdf = gpd.read_file(schools_file)
                self.logger.info(f"Loaded {len(self.schools_gdf)} Texas schools")
            else:
                self.logger.warning(f"Schools file not found: {schools_file}")
                self.schools_gdf = None
            
            # Load Texas city boundaries
            cities_file = base_dir / "City_Boundaries" / "TX_cities_2024.geojson"
            if cities_file.exists():
                self.cities_gdf = gpd.read_file(cities_file)
                self.logger.info(f"Loaded {len(self.cities_gdf)} Texas cities/places")
            else:
                self.logger.warning(f"Cities file not found: {cities_file}")
                self.cities_gdf = None
                
            # Load TDHCA LIHTC projects
            tdhca_file = base_dir / "State Specific" / "TX" / "Project_List" / "TX_TDHCA_Project_List_05252025.xlsx"
            if tdhca_file.exists():
                self.tdhca_projects = pd.read_excel(tdhca_file)
                # Clean coordinates
                self.tdhca_projects = self.tdhca_projects.dropna(subset=['Latitude', 'Longitude'])
                self.logger.info(f"Loaded {len(self.tdhca_projects)} TDHCA projects")
            else:
                self.logger.warning(f"TDHCA projects file not found: {tdhca_file}")
                self.tdhca_projects = None
                
        except Exception as e:
            self.logger.error(f"Error loading infrastructure data: {e}")
            self.schools_gdf = None
            self.cities_gdf = None
            self.tdhca_projects = None
    
    def calculate_anchor_viability_score(self, lat, lng):
        """
        Calculate anchor viability score to identify isolated sites.
        Returns score 0-5 where 0 = isolated, 5 = excellent infrastructure.
        """
        if not lat or not lng:
            return 0, "No coordinates available"
        
        site_point = Point(lng, lat)
        score = 0
        details = []
        fatal_flaw = False
        
        # CRITICAL: Schools within 2.5 miles (MUST HAVE)
        schools_nearby = 0
        if self.schools_gdf is not None:
            # Calculate distances to all schools
            school_distances = []
            for _, school in self.schools_gdf.iterrows():
                try:
                    school_point = school.geometry
                    if school_point and not school_point.is_empty:
                        # Convert to miles (approximate)
                        distance_deg = site_point.distance(school_point)
                        distance_miles = distance_deg * 69  # Rough conversion
                        school_distances.append(distance_miles)
                except:
                    continue
            
            schools_nearby = sum(1 for d in school_distances if d <= 2.5)
            
        if schools_nearby == 0:
            fatal_flaw = True
            details.append("❌ FATAL: No schools within 2.5 miles (isolated site)")
            return 0, "; ".join(details)
        else:
            score += 2  # Base points for school access
            details.append(f"✅ {schools_nearby} school(s) within 2.5 miles")
            
            if schools_nearby >= 3:
                score += 1  # Bonus for multiple schools (established community)
                details.append("🏫 Multiple schools indicate established community")
        
        # BONUS: Within incorporated city limits
        within_city = False
        city_name = "Unincorporated"
        if self.cities_gdf is not None:
            try:
                site_gdf = gpd.GeoDataFrame([1], geometry=[site_point], crs='EPSG:4326')
                cities_intersect = gpd.sjoin(site_gdf, self.cities_gdf, how='inner', predicate='within')
                
                if len(cities_intersect) > 0:
                    within_city = True
                    city_name = cities_intersect.iloc[0]['NAME']
                    score += 1
                    details.append(f"🏛️ Within {city_name} city limits")
                else:
                    details.append("⚠️ Unincorporated area - infrastructure uncertain")
            except Exception as e:
                self.logger.debug(f"City boundary check failed: {e}")
        
        # BONUS: Nearby LIHTC projects indicate market viability
        lihtc_nearby = 0
        if self.tdhca_projects is not None:
            for _, project in self.tdhca_projects.iterrows():
                try:
                    project_lat = float(project['Latitude'])
                    project_lng = float(project['Longitude'])
                    distance = geodesic((lat, lng), (project_lat, project_lng)).miles
                    
                    if distance <= 2.0:
                        lihtc_nearby += 1
                except:
                    continue
        
        if lihtc_nearby > 0:
            score += 1
            details.append(f"💼 {lihtc_nearby} LIHTC project(s) within 2 miles (market validation)")
        else:
            details.append("⚠️ No nearby LIHTC projects - market unproven")
        
        # Additional scoring based on school density (community establishment)
        if schools_nearby >= 5:
            score += 1
            details.append("🌟 High school density indicates major population center")
        
        # Cap score at 5
        score = min(score, 5)
        
        return score, "; ".join(details)
    
    def geocode_address(self, address, city, county, max_retries=3):
        """Enhanced geocoding with better address handling"""
        # Try multiple address formats
        address_variations = [
            f"{address}, {city}, {county} County, Texas",
            f"{address}, {city}, TX",
            f"{city}, {county} County, Texas",  # City center fallback
            f"{city}, TX"
        ]
        
        for variation in address_variations:
            for attempt in range(max_retries):
                try:
                    location = self.geolocator.geocode(variation, timeout=10)
                    if location:
                        success = (address in variation)  # True if specific address found
                        return {
                            'latitude': location.latitude,
                            'longitude': location.longitude,
                            'geocoded_address': location.address,
                            'geocoding_success': success,
                            'geocoding_method': variation
                        }
                    time.sleep(1)
                except Exception as e:
                    self.logger.debug(f"Geocoding failed for {variation}: {e}")
                    time.sleep(2)
        
        return {
            'latitude': None, 'longitude': None,
            'geocoded_address': 'Geocoding Failed',
            'geocoding_success': False, 'geocoding_method': 'Failed'
        }
    
    def analyze_enhanced_dmarco_sites(self, csv_file):
        """Main analysis with anchor viability scoring"""
        self.logger.info(f"Enhanced analysis of D'Marco sites from: {csv_file}")
        
        df = pd.read_csv(csv_file)
        self.logger.info(f"Loaded {len(df)} D'Marco sites")
        
        # Enhanced analysis columns
        analysis_columns = [
            # Geocoding
            'Latitude', 'Longitude', 'Geocoded_Address', 'Geocoding_Success', 'Geocoding_Method',
            
            # Anchor Viability Analysis
            'Anchor_Viability_Score', 'Anchor_Details', 'Site_Isolation_Risk',
            'Schools_Within_2_5_Miles', 'Within_City_Limits', 'City_Name',
            'LIHTC_Projects_Within_2_Miles', 'Market_Validation',
            
            # QCT/DDA Status
            'QCT_Status', 'DDA_Status', 'QCT_DDA_Combined', 'Basis_Boost_Eligible',
            
            # Competition Analysis
            'One_Mile_Competition_Count', 'One_Mile_Risk_4pct', 'One_Mile_Fatal_9pct',
            'Two_Mile_Competition_Count', 'Large_County_Rules_Apply',
            
            # Economic factors
            'Regional_Construction_Cost_Multiplier', 'Estimated_Construction_Cost_SF',
            
            # Overall Assessment
            'Final_Viability_Score', 'Development_Recommendation', 
            'Key_Advantages', 'Risk_Factors', 'Next_Steps'
        ]
        
        for col in analysis_columns:
            df[col] = None
        
        viable_sites = []
        qct_dda_sites = []
        
        # Process each site
        for idx, row in df.iterrows():
            site_name = f"{row['MailingName']} - {row['City']}, {row['County']} County"
            self.logger.info(f"Processing {idx + 1}/{len(df)}: {site_name}")
            
            # 1. Enhanced Geocoding
            geocoding = self.geocode_address(row['Address'], row['City'], row['County'])
            for key, value in geocoding.items():
                df.loc[idx, key.replace('_', '_').title().replace(' ', '_')] = value
            
            if not geocoding['latitude']:
                df.loc[idx, 'Development_Recommendation'] = 'Cannot analyze - geocoding failed'
                df.loc[idx, 'Final_Viability_Score'] = 0
                continue
            
            # 2. Anchor Viability Assessment (CRITICAL FILTER)
            anchor_score, anchor_details = self.calculate_anchor_viability_score(
                geocoding['latitude'], geocoding['longitude']
            )
            
            df.loc[idx, 'Anchor_Viability_Score'] = anchor_score
            df.loc[idx, 'Anchor_Details'] = anchor_details
            
            # Determine isolation risk
            if anchor_score == 0:
                df.loc[idx, 'Site_Isolation_Risk'] = 'FATAL - Too Isolated'
                df.loc[idx, 'Development_Recommendation'] = 'DO NOT PURSUE - Isolated location with no nearby schools'
                df.loc[idx, 'Final_Viability_Score'] = 0
                continue
            elif anchor_score <= 2:
                df.loc[idx, 'Site_Isolation_Risk'] = 'HIGH - Limited Infrastructure'
            elif anchor_score <= 3:
                df.loc[idx, 'Site_Isolation_Risk'] = 'MEDIUM - Adequate Infrastructure'
            else:
                df.loc[idx, 'Site_Isolation_Risk'] = 'LOW - Good Infrastructure'
            
            # 3. QCT/DDA Analysis (for non-isolated sites)
            qct_dda = self.base_analyzer.check_qct_dda_status(
                geocoding['latitude'], geocoding['longitude']
            )
            
            df.loc[idx, 'QCT_Status'] = qct_dda['in_qct']
            df.loc[idx, 'DDA_Status'] = qct_dda['in_dda']
            df.loc[idx, 'QCT_DDA_Combined'] = qct_dda['status']
            df.loc[idx, 'Basis_Boost_Eligible'] = qct_dda['basis_boost_eligible']
            
            if not qct_dda['basis_boost_eligible']:
                df.loc[idx, 'Development_Recommendation'] = 'Not recommended - No 30% basis boost'
                df.loc[idx, 'Final_Viability_Score'] = anchor_score * 0.3  # Heavily penalized
                continue
            
            qct_dda_sites.append(idx)
            
            # 4. Competition Analysis
            competition_4pct = self.base_analyzer.analyze_competition_by_type(
                geocoding['latitude'], geocoding['longitude'], row['County'], '4%'
            )
            competition_9pct = self.base_analyzer.analyze_competition_by_type(
                geocoding['latitude'], geocoding['longitude'], row['County'], '9%'
            )
            
            df.loc[idx, 'One_Mile_Competition_Count'] = competition_4pct['one_mile_recent_count']
            df.loc[idx, 'One_Mile_Risk_4pct'] = competition_4pct['one_mile_risk_level']
            df.loc[idx, 'One_Mile_Fatal_9pct'] = competition_9pct['one_mile_fatal_flaw']
            df.loc[idx, 'Two_Mile_Competition_Count'] = competition_4pct['market_saturation_2mi']
            
            # 5. Economic Analysis
            region = row['Region']
            cost_multiplier = self.regional_cost_multipliers.get(region, 1.0)
            df.loc[idx, 'Regional_Construction_Cost_Multiplier'] = cost_multiplier
            df.loc[idx, 'Estimated_Construction_Cost_SF'] = self.base_construction_cost * cost_multiplier
            
            # 6. Final Viability Scoring (0-10 scale)
            final_score = 0
            advantages = []
            risks = []
            
            # Anchor infrastructure (40% weight)
            final_score += anchor_score * 0.8  # Max 4 points
            advantages.append(f"Infrastructure score: {anchor_score}/5")
            
            # QCT/DDA bonus (20% weight)
            final_score += 2  # Max 2 points for QCT/DDA eligibility
            advantages.append(f"30% basis boost ({qct_dda['status']})")
            
            # Competition impact (30% weight)
            if competition_4pct['one_mile_risk_level'] == 'Low':
                final_score += 3
                advantages.append('No recent LIHTC competition')
            elif competition_4pct['one_mile_risk_level'] == 'Medium':
                final_score += 2
                risks.append('Some recent LIHTC competition')
            else:
                final_score += 1
                risks.append('High LIHTC competition')
            
            # Cost considerations (10% weight)
            if cost_multiplier <= 1.0:
                final_score += 1
                advantages.append(f'Reasonable construction costs ({region})')
            elif cost_multiplier > 1.15:
                risks.append(f'High construction costs ({region})')
            
            # 9% program viability check
            if competition_9pct['one_mile_fatal_flaw']:
                risks.append('9% program not viable - fatal competition')
            else:
                advantages.append('9% program potentially viable')
            
            # Acreage considerations
            acreage = float(row['Acres'])
            if acreage > 50:
                advantages.append(f'Large development opportunity ({acreage} acres)')
            elif acreage < 3:
                risks.append(f'Small site may limit unit count ({acreage} acres)')
            
            df.loc[idx, 'Final_Viability_Score'] = round(final_score, 1)
            df.loc[idx, 'Key_Advantages'] = '; '.join(advantages)
            df.loc[idx, 'Risk_Factors'] = '; '.join(risks) if risks else 'None identified'
            
            # Final recommendation based on combined scoring
            if final_score >= 8:
                df.loc[idx, 'Development_Recommendation'] = 'EXCELLENT OPPORTUNITY'
                df.loc[idx, 'Next_Steps'] = 'Immediate due diligence recommended'
                viable_sites.append(idx)
            elif final_score >= 6:
                df.loc[idx, 'Development_Recommendation'] = 'STRONG CANDIDATE'
                df.loc[idx, 'Next_Steps'] = 'Full market study recommended'
                viable_sites.append(idx)
            elif final_score >= 4:
                df.loc[idx, 'Development_Recommendation'] = 'PROCEED WITH CAUTION'
                df.loc[idx, 'Next_Steps'] = 'Address risk factors before proceeding'
            else:
                df.loc[idx, 'Development_Recommendation'] = 'NOT RECOMMENDED'
                df.loc[idx, 'Next_Steps'] = 'Consider alternative sites'
        
        # Save comprehensive results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"DMarco_Enhanced_Analysis_With_Anchors_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Executive Summary
            summary_data = {
                'Metric': [
                    'Total D\'Marco Sites Analyzed',
                    'Successfully Geocoded',
                    'Non-Isolated Sites (Anchor Score > 0)',
                    'QCT/DDA Eligible Sites',
                    'Excellent Opportunities (Score ≥ 8)',
                    'Strong Candidates (Score ≥ 6)',
                    'Sites with Fatal Isolation',
                    'Sites with Fatal 9% Competition'
                ],
                'Count': [
                    len(df),
                    len(df[df['Geocoding_Success'] == True]),
                    len(df[df['Anchor_Viability_Score'] > 0]),
                    len(qct_dda_sites),
                    len(df[df['Final_Viability_Score'] >= 8]),
                    len(df[df['Final_Viability_Score'] >= 6]),
                    len(df[df['Site_Isolation_Risk'] == 'FATAL - Too Isolated']),
                    len(df[df['One_Mile_Fatal_9pct'] == True])
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Executive_Summary', index=False)
            
            # All sites with full analysis
            df_sorted = df.sort_values('Final_Viability_Score', ascending=False)
            df_sorted.to_excel(writer, sheet_name='All_Sites_Ranked', index=False)
            
            # Top opportunities only
            top_sites = df[df['Final_Viability_Score'] >= 6].sort_values('Final_Viability_Score', ascending=False)
            if len(top_sites) > 0:
                top_sites.to_excel(writer, sheet_name='Top_Opportunities', index=False)
            
            # QCT/DDA sites analysis
            if qct_dda_sites:
                qct_dda_df = df.iloc[qct_dda_sites].sort_values('Final_Viability_Score', ascending=False)
                qct_dda_df.to_excel(writer, sheet_name='QCT_DDA_Sites', index=False)
            
            # Sites with isolation issues
            isolated_sites = df[df['Site_Isolation_Risk'].str.contains('FATAL|HIGH', na=False)]
            if len(isolated_sites) > 0:
                isolated_sites.to_excel(writer, sheet_name='Isolation_Issues', index=False)
        
        # Logging summary
        self.logger.info(f"\n🎯 Enhanced D'Marco Analysis Complete:")
        self.logger.info(f"   Total sites analyzed: {len(df)}")
        self.logger.info(f"   Non-isolated sites: {len(df[df['Anchor_Viability_Score'] > 0])}")
        self.logger.info(f"   QCT/DDA eligible: {len(qct_dda_sites)}")
        self.logger.info(f"   Excellent opportunities: {len(df[df['Final_Viability_Score'] >= 8])}")
        self.logger.info(f"   Strong candidates: {len(df[df['Final_Viability_Score'] >= 6])}")
        self.logger.info(f"\n💾 Results saved to: {output_file}")
        
        return df, output_file

def main():
    analyzer = EnhancedDMarcoAnalyzer()
    
    # Input file path
    csv_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/From_Brent_06182025.csv"
    
    if Path(csv_file).exists():
        df_results, output_file = analyzer.analyze_enhanced_dmarco_sites(csv_file)
        
        print(f"\n✅ Enhanced analysis complete!")
        print(f"📊 Results saved to: {output_file}")
        
        # Key findings
        excellent = len(df_results[df_results['Final_Viability_Score'] >= 8])
        strong = len(df_results[df_results['Final_Viability_Score'] >= 6])
        isolated = len(df_results[df_results['Site_Isolation_Risk'] == 'FATAL - Too Isolated'])
        
        print(f"\n🎯 Key Findings:")
        print(f"   🌟 Excellent opportunities: {excellent}")
        print(f"   💪 Strong candidates: {strong}")
        print(f"   ⚠️ Isolated sites (avoid): {isolated}")
        print(f"\n💡 Focus on the {strong} sites with scores ≥ 6.0 for development")
        
    else:
        print(f"❌ File not found: {csv_file}")

if __name__ == "__main__":
    main()