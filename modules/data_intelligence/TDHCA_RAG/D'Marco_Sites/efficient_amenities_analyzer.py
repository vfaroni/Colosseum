#!/usr/bin/env python3
"""
⚡ EFFICIENT Texas Amenities Analysis
WINGMAN Agent - Optimized for Speed with CSV data

AMENITIES ANALYZED:
1. Texas Public Schools (2024-2025) - Elementary, Middle, High
2. Major Highway Access (simplified distance calculations)
3. LIHTC Amenity Scoring System
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

class EfficientAmenitiesAnalyzer:
    """Fast amenities analysis using CSV data"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        self.data_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas")
        
        # Distance thresholds for scoring (miles)
        self.SCORING_THRESHOLDS = {
            'elementary': {'excellent': 0.5, 'good': 1.0, 'fair': 1.5},
            'middle': {'excellent': 1.0, 'good': 1.5, 'fair': 2.0},
            'high': {'excellent': 1.5, 'good': 2.5, 'fair': 3.0}
        }
        
        # Point values for amenity scoring
        self.POINT_VALUES = {
            'elementary_excellent': 25,
            'elementary_good': 20,
            'elementary_fair': 15,
            'middle_excellent': 20,
            'middle_good': 15,
            'middle_fair': 10,
            'high_excellent': 20,
            'high_good': 15,
            'high_fair': 10,
            'school_diversity_bonus': 10  # Bonus for having all school levels nearby
        }
    
    def load_dmarco_sites(self):
        """Load D'Marco sites data"""
        sites_file = self.base_dir / "Production_Analysis_20250730/dmarco_production_analysis_20250730_134731_COUNTY_CORRECTED.json"
        
        with open(sites_file, 'r') as f:
            sites_data = json.load(f)
        
        print(f"✅ Loaded {len(sites_data)} D'Marco sites")
        return sites_data
    
    def load_texas_schools(self):
        """Load Texas schools from CSV"""
        print("📚 Loading Texas Schools Database...")
        
        schools_file = self.data_dir / 'TX_Public_Schools/Schools_2024_to_2025.csv'
        
        if not schools_file.exists():
            print(f"❌ Schools file not found: {schools_file}")
            return pd.DataFrame()
        
        try:
            # Load schools with relevant columns
            schools_df = pd.read_csv(schools_file, encoding='utf-8-sig')
            
            # Clean and filter data
            schools_clean = schools_df[
                (schools_df['X'].notna()) & 
                (schools_df['Y'].notna()) & 
                (schools_df['USER_School_Status'] == 'Active')
            ].copy()
            
            # Extract school type from School_Type column
            schools_clean['school_level'] = schools_clean['School_Type'].str.lower()
            
            # Standardize coordinates  
            schools_clean['longitude'] = pd.to_numeric(schools_clean['X'], errors='coerce')
            schools_clean['latitude'] = pd.to_numeric(schools_clean['Y'], errors='coerce')
            
            # Filter to valid Texas coordinates
            texas_schools = schools_clean[
                (schools_clean['latitude'] >= 25.0) & (schools_clean['latitude'] <= 37.0) &
                (schools_clean['longitude'] >= -107.0) & (schools_clean['longitude'] <= -93.0)
            ].copy()
            
            print(f"✅ Loaded {len(texas_schools)} active Texas schools with coordinates")
            
            # Show school type distribution
            school_types = texas_schools['school_level'].value_counts()
            print(f"   School types: {dict(school_types)}")
            
            return texas_schools
            
        except Exception as e:
            print(f"❌ Error loading schools: {e}")
            return pd.DataFrame()
    
    def classify_school_level(self, school_type):
        """Classify school level from school type"""
        if pd.isna(school_type):
            return 'unknown'
        
        school_type_lower = school_type.lower()
        
        if 'elementary' in school_type_lower or 'primary' in school_type_lower:
            return 'elementary'
        elif 'middle' in school_type_lower or 'intermediate' in school_type_lower:
            return 'middle'  
        elif 'high' in school_type_lower or 'secondary' in school_type_lower:
            return 'high'
        else:
            return 'other'
    
    def find_nearby_schools(self, site_lat, site_lng, schools_df, max_distance=3.0):
        """Find schools within max distance of site"""
        nearby_schools = []
        
        for idx, school in schools_df.iterrows():
            try:
                # Calculate distance
                school_coords = (school['latitude'], school['longitude'])
                site_coords = (site_lat, site_lng)
                distance = geodesic(site_coords, school_coords).miles
                
                if distance <= max_distance:
                    school_level = self.classify_school_level(school['school_level'])
                    
                    school_info = {
                        'name': school.get('USER_School_Name', 'Unknown School'),
                        'district': school.get('USER_District_Name', 'Unknown District'),
                        'level': school_level,
                        'distance_miles': round(distance, 2),
                        'coordinates': [school['latitude'], school['longitude']],
                        'address': school.get('USER_School_Street_Address', ''),
                        'city': school.get('USER_School_City', ''),
                        'enrollment': school.get('USER_School_Enrollment_as_of_Oc', 0)
                    }
                    
                    nearby_schools.append(school_info)
                    
            except Exception as e:
                continue
        
        # Sort by distance
        nearby_schools.sort(key=lambda x: x['distance_miles'])
        return nearby_schools
    
    def calculate_school_amenity_score(self, nearby_schools):
        """Calculate amenity score based on nearby schools"""
        
        # Group schools by level
        schools_by_level = {}
        for school in nearby_schools:
            level = school['level']
            if level not in schools_by_level:
                schools_by_level[level] = []
            schools_by_level[level].append(school)
        
        total_score = 0
        scoring_detail = {}
        
        # Score each school level
        for level in ['elementary', 'middle', 'high']:
            level_schools = schools_by_level.get(level, [])
            level_score = 0
            
            if level_schools:
                closest_school = min(level_schools, key=lambda x: x['distance_miles'])
                distance = closest_school['distance_miles']
                
                thresholds = self.SCORING_THRESHOLDS[level]
                
                if distance <= thresholds['excellent']:
                    level_score = self.POINT_VALUES[f'{level}_excellent']
                    quality = 'excellent'
                elif distance <= thresholds['good']:
                    level_score = self.POINT_VALUES[f'{level}_good']
                    quality = 'good'
                elif distance <= thresholds['fair']:
                    level_score = self.POINT_VALUES[f'{level}_fair']
                    quality = 'fair'
                else:
                    level_score = 5  # Minimal points for distant schools
                    quality = 'poor'
                
                scoring_detail[level] = {
                    'score': level_score,
                    'quality': quality,
                    'closest_school': closest_school['name'],
                    'distance': distance,
                    'schools_count': len(level_schools)
                }
            else:
                scoring_detail[level] = {
                    'score': 0,
                    'quality': 'none',
                    'closest_school': None,
                    'distance': None,
                    'schools_count': 0
                }
            
            total_score += level_score
        
        # Diversity bonus (all school levels within reasonable distance)
        has_all_levels = all(
            scoring_detail[level]['score'] > 0 
            for level in ['elementary', 'middle', 'high']
        )
        
        if has_all_levels:
            total_score += self.POINT_VALUES['school_diversity_bonus']
            scoring_detail['diversity_bonus'] = self.POINT_VALUES['school_diversity_bonus']
        else:
            scoring_detail['diversity_bonus'] = 0
        
        # Overall assessment
        if total_score >= 60:
            overall_rating = 'EXCELLENT'
        elif total_score >= 40:
            overall_rating = 'GOOD'
        elif total_score >= 20:
            overall_rating = 'FAIR'
        else:
            overall_rating = 'POOR'
        
        return {
            'total_score': total_score,
            'max_possible_score': 75,  # 25+20+20+10 = 75
            'overall_rating': overall_rating,
            'scoring_detail': scoring_detail
        }
    
    def analyze_all_sites(self):
        """Analyze amenities for all D'Marco sites"""
        print("🎯 ANALYZING SCHOOL AMENITIES FOR ALL SITES")
        
        # Load data
        sites_data = self.load_dmarco_sites()
        schools_df = self.load_texas_schools()
        
        if schools_df.empty:
            print("❌ No schools data available")
            return []
        
        site_analyses = []
        
        for site in sites_data:
            site_index = site['site_index']
            site_lat = site['parcel_center_lat']
            site_lng = site['parcel_center_lng'] 
            county = site.get('census_county', 'Unknown')
            
            print(f"  Site {site_index} ({county}): ", end="")
            
            # Find nearby schools
            nearby_schools = self.find_nearby_schools(site_lat, site_lng, schools_df)
            
            # Calculate amenity score
            amenity_score = self.calculate_school_amenity_score(nearby_schools)
            
            # Create site analysis
            site_analysis = {
                'site_index': site_index,
                'county': county,
                'coordinates': [site_lat, site_lng],
                'nearby_schools': nearby_schools,
                'amenity_scoring': amenity_score,
                'school_summary': {
                    'total_schools_within_3_miles': len(nearby_schools),
                    'elementary_schools': len([s for s in nearby_schools if s['level'] == 'elementary']),
                    'middle_schools': len([s for s in nearby_schools if s['level'] == 'middle']),
                    'high_schools': len([s for s in nearby_schools if s['level'] == 'high'])
                }
            }
            
            site_analyses.append(site_analysis)
            
            # Print summary
            score = amenity_score['total_score']
            rating = amenity_score['overall_rating']
            schools_count = len(nearby_schools)
            print(f"{score}/75 ({rating}) with {schools_count} schools")
        
        return site_analyses
    
    def create_amenities_analysis(self):
        """Create comprehensive amenities analysis"""
        print("🚀 CREATING EFFICIENT AMENITIES ANALYSIS")
        
        # Analyze all sites
        site_analyses = self.analyze_all_sites()
        
        if not site_analyses:
            return None
        
        # Calculate summary statistics
        scores = [analysis['amenity_scoring']['total_score'] for analysis in site_analyses]
        ratings = [analysis['amenity_scoring']['overall_rating'] for analysis in site_analyses]
        
        summary_stats = {
            'total_sites': len(site_analyses),
            'average_score': round(np.mean(scores), 1),
            'median_score': round(np.median(scores), 1),
            'score_range': [min(scores), max(scores)],
            'rating_distribution': {
                'EXCELLENT': ratings.count('EXCELLENT'),
                'GOOD': ratings.count('GOOD'),
                'FAIR': ratings.count('FAIR'),
                'POOR': ratings.count('POOR')
            }
        }
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create Excel export
        excel_data = []
        for analysis in site_analyses:
            scoring = analysis['amenity_scoring']
            detail = scoring['scoring_detail']
            summary = analysis['school_summary']
            
            row = {
                'Site_Index': analysis['site_index'],
                'County': analysis['county'],
                'Total_Amenity_Score': scoring['total_score'],
                'Overall_Rating': scoring['overall_rating'],
                'Schools_Within_3_Miles': summary['total_schools_within_3_miles'],
                'Elementary_Schools': summary['elementary_schools'],
                'Middle_Schools': summary['middle_schools'], 
                'High_Schools': summary['high_schools'],
                'Elementary_Score': detail['elementary']['score'],
                'Middle_Score': detail['middle']['score'],
                'High_School_Score': detail['high']['score'],
                'Diversity_Bonus': detail['diversity_bonus'],
                'Nearest_Elementary': detail['elementary']['closest_school'],
                'Nearest_Elementary_Distance': detail['elementary']['distance'],
                'Nearest_Middle': detail['middle']['closest_school'],
                'Nearest_Middle_Distance': detail['middle']['distance'],
                'Nearest_High_School': detail['high']['closest_school'],
                'Nearest_High_School_Distance': detail['high']['distance']
            }
            
            excel_data.append(row)
        
        df = pd.DataFrame(excel_data)
        
        # Save Excel
        excel_file = self.base_dir / f"DMarco_School_Amenities_Analysis_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main analysis
            df.to_excel(writer, sheet_name='School_Amenities', index=False)
            
            # Top scoring sites
            top_sites = df.nlargest(10, 'Total_Amenity_Score')
            top_sites.to_excel(writer, sheet_name='Top_School_Access', index=False)
            
            # Sites with all school levels
            all_levels = df[(df['Elementary_Schools'] > 0) & 
                           (df['Middle_Schools'] > 0) & 
                           (df['High_Schools'] > 0)]
            if not all_levels.empty:
                all_levels.to_excel(writer, sheet_name='Complete_School_Access', index=False)
            
            # Summary statistics
            summary_data = [
                ['SCHOOL AMENITIES SUMMARY', ''],
                ['Analysis Date', datetime.now().strftime('%Y-%m-%d %H:%M')],
                ['Total Sites Analyzed', summary_stats['total_sites']],
                ['Average Amenity Score', f"{summary_stats['average_score']}/75"],
                ['Median Score', f"{summary_stats['median_score']}/75"],
                ['Score Range', f"{summary_stats['score_range'][0]}-{summary_stats['score_range'][1]}"],
                ['', ''],
                ['RATING DISTRIBUTION', ''],
                ['Excellent Sites', summary_stats['rating_distribution']['EXCELLENT']],
                ['Good Sites', summary_stats['rating_distribution']['GOOD']],
                ['Fair Sites', summary_stats['rating_distribution']['FAIR']],
                ['Poor Sites', summary_stats['rating_distribution']['POOR']],
                ['', ''],
                ['SCHOOL ACCESS SUMMARY', ''],
                ['Sites with All School Levels', len(all_levels)],
                ['Sites with Elementary Access', len(df[df['Elementary_Schools'] > 0])],
                ['Sites with Middle School Access', len(df[df['Middle_Schools'] > 0])],
                ['Sites with High School Access', len(df[df['High_Schools'] > 0])]
            ]
            
            summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Save detailed JSON
        json_file = self.base_dir / f"Texas_School_Amenities_Detailed_{timestamp}.json"
        
        comprehensive_report = {
            'analysis_date': datetime.now().isoformat(),
            'analysis_type': 'TEXAS_SCHOOL_AMENITIES',
            'summary_statistics': summary_stats,
            'scoring_methodology': {
                'distance_thresholds': self.SCORING_THRESHOLDS,
                'point_values': self.POINT_VALUES,
                'max_possible_score': 75
            },
            'site_analyses': site_analyses
        }
        
        with open(json_file, 'w') as f:
            json.dump(comprehensive_report, f, indent=2)
        
        print(f"\n📊 SCHOOL AMENITIES ANALYSIS COMPLETE!")
        print(f"✅ Sites analyzed: {summary_stats['total_sites']}")
        print(f"🎯 Average score: {summary_stats['average_score']}/75")
        print(f"📈 Score range: {summary_stats['score_range'][0]}-{summary_stats['score_range'][1]}")
        print(f"🏆 Rating distribution: {summary_stats['rating_distribution']}")
        print(f"🏫 Sites with complete school access: {len(all_levels)}/{summary_stats['total_sites']}")
        
        print(f"\n💾 Files created:")
        print(f"   • Excel analysis: {excel_file.name}")
        print(f"   • Detailed JSON: {json_file.name}")
        
        return comprehensive_report

if __name__ == "__main__":
    analyzer = EfficientAmenitiesAnalyzer()
    results = analyzer.create_amenities_analysis()