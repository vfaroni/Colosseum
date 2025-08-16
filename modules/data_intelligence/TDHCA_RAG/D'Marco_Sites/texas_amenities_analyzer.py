#!/usr/bin/env python3
"""
🎯 Texas Comprehensive Amenities Analysis
WINGMAN Agent - Schools, Parks, Transportation, Major Road Access

AMENITIES ANALYZED:
1. Public Schools (distance to elementary, middle, high schools)
2. Parks & Recreation (if available in datasets)
3. Major Road Access (TxDOT highways, interstates)
4. Transportation Infrastructure
5. Healthcare Facilities (if available)
6. Libraries (if available)

LIHTC SCORING IMPACT:
- School proximity enhances family housing appeal
- Park access improves quality of life scores
- Highway access affects development costs and marketability
- Transit access supports car-free households
"""

import pandas as pd
import geopandas as gpd
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from shapely.geometry import Point
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

class TexasAmenitiesAnalyzer:
    """Comprehensive amenities analysis for Texas LIHTC sites"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        self.data_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas")
        
        # Amenity datasets available
        self.amenity_datasets = {
            'schools': self.data_dir / 'TX_Public_Schools/Schools_2024_to_2025.geojson',
            'major_highways': self.data_dir / 'TxDOT_Roadways/texas_major_highways.gpkg',
            'interstate_highways': self.data_dir / 'TxDOT_Roadways/texas_interstate_highways.gpkg',
            'us_highways': self.data_dir / 'TxDOT_Roadways/texas_us_highway_highways.gpkg',
            'state_highways': self.data_dir / 'TxDOT_Roadways/texas_state_highway_highways.gpkg'
        }
        
        # Distance thresholds for amenity scoring (miles)
        self.DISTANCE_THRESHOLDS = {
            'schools': {
                'excellent': 0.25,    # Within 1/4 mile
                'good': 0.5,          # Within 1/2 mile  
                'fair': 1.0,          # Within 1 mile
                'poor': 2.0           # Within 2 miles
            },
            'parks': {
                'excellent': 0.25,
                'good': 0.5,
                'fair': 1.0,
                'poor': 2.0
            },
            'major_roads': {
                'excellent': 0.5,     # Within 1/2 mile of major highway
                'good': 1.0,          # Within 1 mile
                'fair': 2.0,          # Within 2 miles
                'poor': 5.0           # Within 5 miles
            }
        }
        
        # Scoring weights for LIHTC applications
        self.AMENITY_SCORES = {
            'schools_elementary': {'weight': 20, 'max_distance': 1.0},
            'schools_middle': {'weight': 15, 'max_distance': 1.5},
            'schools_high': {'weight': 15, 'max_distance': 2.0},
            'parks_local': {'weight': 10, 'max_distance': 1.0},
            'parks_regional': {'weight': 15, 'max_distance': 2.0},
            'major_highway_access': {'weight': 25, 'max_distance': 2.0},
            'transit_access': {'weight': 10, 'max_distance': 0.5}
        }
        
        # School level classification
        self.SCHOOL_LEVELS = {
            'elementary': ['ELEMENTARY', 'PRIMARY', 'K-', 'PRE-K', 'KINDERGARTEN'],
            'middle': ['MIDDLE', 'INTERMEDIATE', 'JUNIOR'],
            'high': ['HIGH', 'SENIOR', '9-12', 'SECONDARY']
        }
    
    def load_dmarco_sites(self):
        """Load D'Marco sites data"""
        sites_file = self.base_dir / "Production_Analysis_20250730/dmarco_production_analysis_20250730_134731_COUNTY_CORRECTED.json"
        
        with open(sites_file, 'r') as f:
            sites_data = json.load(f)
        
        print(f"✅ Loaded {len(sites_data)} D'Marco sites for amenities analysis")
        return sites_data
    
    def load_amenity_datasets(self):
        """Load all available amenity datasets"""
        print("📊 LOADING TEXAS AMENITY DATASETS")
        
        loaded_datasets = {}
        
        for amenity_type, file_path in self.amenity_datasets.items():
            if file_path.exists():
                try:
                    if file_path.suffix == '.geojson':
                        gdf = gpd.read_file(file_path)
                    elif file_path.suffix == '.gpkg':
                        gdf = gpd.read_file(file_path)
                    else:
                        continue
                    
                    # Ensure CRS is WGS84 for distance calculations
                    if gdf.crs != 'EPSG:4326':
                        gdf = gdf.to_crs('EPSG:4326')
                    
                    loaded_datasets[amenity_type] = gdf
                    print(f"  ✅ {amenity_type}: {len(gdf)} features loaded")
                    
                except Exception as e:
                    print(f"  ❌ Error loading {amenity_type}: {e}")
            else:
                print(f"  ⚠️  {amenity_type}: File not found - {file_path}")
        
        return loaded_datasets
    
    def classify_school_level(self, school_name):
        """Classify school level based on name"""
        school_name_upper = school_name.upper() if school_name else ""
        
        for level, keywords in self.SCHOOL_LEVELS.items():
            for keyword in keywords:
                if keyword in school_name_upper:
                    return level
        
        return 'unknown'
    
    def find_nearest_amenities(self, site_lat, site_lng, amenity_gdf, amenity_type, max_distance=5.0):
        """Find nearest amenities within max distance"""
        site_point = Point(site_lng, site_lat)
        
        # Calculate distances to all amenities
        amenity_distances = []
        
        for idx, amenity in amenity_gdf.iterrows():
            try:
                # Get amenity coordinates
                if amenity.geometry.geom_type == 'Point':
                    amenity_coords = (amenity.geometry.y, amenity.geometry.x)
                else:
                    # For non-point geometries, use centroid
                    centroid = amenity.geometry.centroid
                    amenity_coords = (centroid.y, centroid.x)
                
                # Calculate distance in miles
                distance = geodesic((site_lat, site_lng), amenity_coords).miles
                
                if distance <= max_distance:
                    amenity_info = {
                        'distance_miles': round(distance, 2),
                        'amenity_type': amenity_type,
                        'name': amenity.get('NAME', amenity.get('SCHOOL_NAM', amenity.get('FULLNAME', 'Unknown'))),
                        'coordinates': amenity_coords
                    }
                    
                    # Add school-specific classification
                    if amenity_type == 'schools':
                        school_level = self.classify_school_level(amenity_info['name'])
                        amenity_info['school_level'] = school_level
                        amenity_info['district'] = amenity.get('DISTRICT', 'Unknown')
                    
                    # Add highway-specific information
                    elif 'highway' in amenity_type:
                        amenity_info['highway_type'] = amenity_type
                        amenity_info['route_name'] = amenity.get('ROUTE_NAME', amenity.get('ROADWAY', 'Unknown'))
                    
                    amenity_distances.append(amenity_info)
                    
            except Exception as e:
                continue
        
        # Sort by distance and return closest ones
        amenity_distances.sort(key=lambda x: x['distance_miles'])
        return amenity_distances[:10]  # Return up to 10 nearest
    
    def calculate_amenity_score(self, site_amenities):
        """Calculate overall amenity score for LIHTC application"""
        total_score = 0
        score_breakdown = {}
        
        # School accessibility scores
        elementary_schools = [a for a in site_amenities.get('schools', []) if a.get('school_level') == 'elementary']
        middle_schools = [a for a in site_amenities.get('schools', []) if a.get('school_level') == 'middle']
        high_schools = [a for a in site_amenities.get('schools', []) if a.get('school_level') == 'high']
        
        # Elementary school score
        if elementary_schools:
            closest_elementary = min(elementary_schools, key=lambda x: x['distance_miles'])
            if closest_elementary['distance_miles'] <= 0.5:
                elementary_score = 20
            elif closest_elementary['distance_miles'] <= 1.0:
                elementary_score = 15
            else:
                elementary_score = 10
        else:
            elementary_score = 0
        
        score_breakdown['elementary_schools'] = elementary_score
        total_score += elementary_score
        
        # Middle school score
        if middle_schools:
            closest_middle = min(middle_schools, key=lambda x: x['distance_miles'])
            if closest_middle['distance_miles'] <= 1.0:
                middle_score = 15
            elif closest_middle['distance_miles'] <= 2.0:
                middle_score = 10
            else:
                middle_score = 5
        else:
            middle_score = 0
        
        score_breakdown['middle_schools'] = middle_score
        total_score += middle_score
        
        # High school score
        if high_schools:
            closest_high = min(high_schools, key=lambda x: x['distance_miles'])
            if closest_high['distance_miles'] <= 2.0:
                high_score = 15
            elif closest_high['distance_miles'] <= 3.0:
                high_score = 10
            else:
                high_score = 5
        else:
            high_score = 0
        
        score_breakdown['high_schools'] = high_score
        total_score += high_score
        
        # Major highway access score
        highway_amenities = []
        for highway_type in ['interstate_highways', 'major_highways', 'us_highways']:
            if highway_type in site_amenities:
                highway_amenities.extend(site_amenities[highway_type])
        
        if highway_amenities:
            closest_highway = min(highway_amenities, key=lambda x: x['distance_miles'])
            if closest_highway['distance_miles'] <= 0.5:
                highway_score = 25
            elif closest_highway['distance_miles'] <= 1.0:
                highway_score = 20
            elif closest_highway['distance_miles'] <= 2.0:
                highway_score = 15
            else:
                highway_score = 10
        else:
            highway_score = 0
        
        score_breakdown['highway_access'] = highway_score
        total_score += highway_score
        
        # Overall assessment
        if total_score >= 70:
            overall_rating = 'EXCELLENT'
        elif total_score >= 50:
            overall_rating = 'GOOD'
        elif total_score >= 30:
            overall_rating = 'FAIR'
        else:
            overall_rating = 'POOR'
        
        return {
            'total_score': total_score,
            'overall_rating': overall_rating,
            'score_breakdown': score_breakdown,
            'max_possible_score': 75
        }
    
    def analyze_site_amenities(self, sites_data, amenity_datasets):
        """Analyze amenities for all D'Marco sites"""
        print("🎯 ANALYZING AMENITIES FOR ALL SITES")
        
        site_amenity_analyses = []
        
        for site in sites_data:
            site_index = site['site_index']
            site_lat = site['parcel_center_lat']
            site_lng = site['parcel_center_lng']
            county = site.get('census_county', 'Unknown')
            
            print(f"  Site {site_index} ({county}): ", end="")
            
            # Analyze each amenity type
            site_amenities = {}
            
            for amenity_type, amenity_gdf in amenity_datasets.items():
                max_dist = 5.0 if 'highway' in amenity_type else 2.0
                nearby_amenities = self.find_nearest_amenities(
                    site_lat, site_lng, amenity_gdf, amenity_type, max_dist
                )
                site_amenities[amenity_type] = nearby_amenities
            
            # Calculate amenity score
            amenity_score = self.calculate_amenity_score(site_amenities)
            
            # Create comprehensive analysis
            site_analysis = {
                'site_index': site_index,
                'county': county,
                'coordinates': [site_lat, site_lng],
                'amenities_found': site_amenities,
                'amenity_scoring': amenity_score,
                'nearest_amenities_summary': {}
            }
            
            # Create summary of nearest amenities
            for amenity_type, amenities in site_amenities.items():
                if amenities:
                    closest = min(amenities, key=lambda x: x['distance_miles'])
                    site_analysis['nearest_amenities_summary'][amenity_type] = {
                        'name': closest['name'],
                        'distance_miles': closest['distance_miles']
                    }
                else:
                    site_analysis['nearest_amenities_summary'][amenity_type] = None
            
            site_amenity_analyses.append(site_analysis)
            
            # Print summary
            score_text = f"{amenity_score['total_score']}/75 ({amenity_score['overall_rating']})"
            schools_count = len(site_amenities.get('schools', []))
            highways_count = sum(len(site_amenities.get(ht, [])) for ht in ['interstate_highways', 'major_highways', 'us_highways'])
            print(f"{score_text}, {schools_count} schools, {highways_count} highways")
        
        return site_amenity_analyses
    
    def create_amenities_analysis(self):
        """Create comprehensive amenities analysis"""
        print("🚀 CREATING TEXAS AMENITIES ANALYSIS")
        
        # Load data
        sites_data = self.load_dmarco_sites()
        amenity_datasets = self.load_amenity_datasets()
        
        if not amenity_datasets:
            print("❌ No amenity datasets loaded - cannot proceed")
            return None
        
        # Analyze amenities
        site_analyses = self.analyze_site_amenities(sites_data, amenity_datasets)
        
        # Create summary statistics
        scores = [analysis['amenity_scoring']['total_score'] for analysis in site_analyses]
        
        summary_stats = {
            'total_sites_analyzed': len(site_analyses),
            'average_amenity_score': round(np.mean(scores), 1),
            'score_distribution': {
                'excellent': len([s for s in scores if s >= 70]),
                'good': len([s for s in scores if 50 <= s < 70]),
                'fair': len([s for s in scores if 30 <= s < 50]),
                'poor': len([s for s in scores if s < 30])
            },
            'amenity_dataset_coverage': {name: len(gdf) for name, gdf in amenity_datasets.items()}
        }
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed analysis
        analysis_file = self.base_dir / f"Texas_Amenities_Analysis_{timestamp}.json"
        
        comprehensive_report = {
            'analysis_date': datetime.now().isoformat(),
            'analysis_type': 'TEXAS_COMPREHENSIVE_AMENITIES',
            'methodology': {
                'distance_thresholds': self.DISTANCE_THRESHOLDS,
                'scoring_system': self.AMENITY_SCORES,
                'school_classification': self.SCHOOL_LEVELS
            },
            'summary_statistics': summary_stats,
            'site_analyses': site_analyses,
            'dataset_info': {name: str(path) for name, path in self.amenity_datasets.items()}
        }
        
        with open(analysis_file, 'w') as f:
            json.dump(comprehensive_report, f, indent=2)
        
        # Create Excel export
        excel_file = self.base_dir / f"DMarco_Amenities_Analysis_{timestamp}.xlsx"
        
        # Prepare data for Excel
        excel_data = []
        for analysis in site_analyses:
            row = {
                'Site_Index': analysis['site_index'],
                'County': analysis['county'],
                'Amenity_Score': analysis['amenity_scoring']['total_score'],
                'Overall_Rating': analysis['amenity_scoring']['overall_rating'],
                'Elementary_Score': analysis['amenity_scoring']['score_breakdown']['elementary_schools'],
                'Middle_School_Score': analysis['amenity_scoring']['score_breakdown']['middle_schools'],
                'High_School_Score': analysis['amenity_scoring']['score_breakdown']['high_schools'],
                'Highway_Access_Score': analysis['amenity_scoring']['score_breakdown']['highway_access']
            }
            
            # Add nearest amenity distances
            summary = analysis['nearest_amenities_summary']
            row['Nearest_Elementary_Distance'] = None
            row['Nearest_High_School_Distance'] = None
            row['Nearest_Highway_Distance'] = None
            
            # Find school distances
            schools = analysis['amenities_found'].get('schools', [])
            elementary = [s for s in schools if s.get('school_level') == 'elementary']
            high_schools = [s for s in schools if s.get('school_level') == 'high']
            
            if elementary:
                row['Nearest_Elementary_Distance'] = min(s['distance_miles'] for s in elementary)
            if high_schools:
                row['Nearest_High_School_Distance'] = min(s['distance_miles'] for s in high_schools)
            
            # Find highway distances
            highway_distances = []
            for highway_type in ['interstate_highways', 'major_highways', 'us_highways']:
                highways = analysis['amenities_found'].get(highway_type, [])
                if highways:
                    highway_distances.extend([h['distance_miles'] for h in highways])
            
            if highway_distances:
                row['Nearest_Highway_Distance'] = min(highway_distances)
            
            excel_data.append(row)
        
        df = pd.DataFrame(excel_data)
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main amenities analysis
            df.to_excel(writer, sheet_name='Amenities_Analysis', index=False)
            
            # Summary by rating
            rating_summary = df.groupby('Overall_Rating').agg({
                'Site_Index': 'count',
                'Amenity_Score': 'mean'
            }).round(1)
            rating_summary.columns = ['Site_Count', 'Average_Score']
            rating_summary.to_excel(writer, sheet_name='Rating_Summary')
            
            # Top scoring sites
            top_sites = df.nlargest(10, 'Amenity_Score')
            top_sites.to_excel(writer, sheet_name='Top_Amenity_Sites', index=False)
        
        print(f"\n📊 AMENITIES ANALYSIS COMPLETE!")
        print(f"✅ Sites analyzed: {summary_stats['total_sites_analyzed']}")
        print(f"🎯 Average amenity score: {summary_stats['average_amenity_score']}/75")
        print(f"📈 Score distribution: {summary_stats['score_distribution']}")
        print(f"📚 Datasets used: {list(amenity_datasets.keys())}")
        
        print(f"\n💾 Files created:")  
        print(f"   • Detailed analysis: {analysis_file.name}")
        print(f"   • Excel summary: {excel_file.name}")
        
        return comprehensive_report

if __name__ == "__main__":
    analyzer = TexasAmenitiesAnalyzer()
    results = analyzer.create_amenities_analysis()