#!/usr/bin/env python3
"""
Calculate Highway Proximity for LIHTC Sites
Measure distance from each site to nearest highway by classification

Author: Claude Code
Date: July 2025
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import numpy as np
from pathlib import Path
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HighwayProximityCalculator:
    """Calculate highway proximity for LIHTC sites"""
    
    def __init__(self):
        # Load highway data
        self.highway_data_path = Path('/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas/TxDOT_Roadways')
        self.highways_gdf = None
        
        # Load classification system
        with open('txdot_highway_classifications.json', 'r') as f:
            self.classifications = json.load(f)
        
        # Load highways
        self._load_highway_data()
    
    def _load_highway_data(self):
        """Load TxDOT highway data"""
        logger.info("Loading TxDOT highway data...")
        
        try:
            # Load simplified highway network
            highway_file = self.highway_data_path / "texas_highways_simplified.gpkg"
            if highway_file.exists():
                self.highways_gdf = gpd.read_file(highway_file)
                logger.info(f"✅ Loaded {len(self.highways_gdf)} highway features")
            else:
                # Fallback to full dataset
                highway_file = self.highway_data_path / "texas_major_highways.gpkg"
                self.highways_gdf = gpd.read_file(highway_file)
                logger.info(f"✅ Loaded {len(self.highways_gdf)} highway segments")
            
            # Ensure CRS is WGS84
            if self.highways_gdf.crs != 'EPSG:4326':
                self.highways_gdf = self.highways_gdf.to_crs('EPSG:4326')
            
        except Exception as e:
            logger.error(f"Error loading highway data: {e}")
            raise
    
    def load_sites_data(self, excel_file):
        """Load the 195 LIHTC sites from Excel"""
        logger.info(f"Loading sites from: {excel_file}")
        
        try:
            # Read the All Sites sheet
            df = pd.read_excel(excel_file, sheet_name='All_195_Sites_Ranked')
            
            # Convert to GeoDataFrame
            geometry = [Point(row['Anchor_Longitude'], row['Anchor_Latitude']) 
                       for _, row in df.iterrows()]
            
            self.sites_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
            
            logger.info(f"✅ Loaded {len(self.sites_gdf)} sites")
            
            return self.sites_gdf
            
        except Exception as e:
            logger.error(f"Error loading sites: {e}")
            raise
    
    def calculate_nearest_highway(self, site_point, highway_type=None):
        """Calculate distance to nearest highway of specific type"""
        
        # Filter highways by type if specified
        if highway_type:
            highways = self.highways_gdf[self.highways_gdf['classification'] == highway_type].copy()
        else:
            highways = self.highways_gdf.copy()
        
        if len(highways) == 0:
            return None, float('inf')
        
        # Reset index to avoid issues
        highways = highways.reset_index(drop=True)
        
        # Project to Texas State Plane (meters) for accurate distance
        site_projected = gpd.GeoSeries([site_point], crs='EPSG:4326').to_crs('EPSG:3081')
        highways_projected = highways.to_crs('EPSG:3081')
        
        # Calculate distances
        distances = highways_projected.geometry.distance(site_projected.iloc[0])
        
        # Get nearest
        nearest_idx = distances.idxmin()
        nearest_highway = highways.loc[nearest_idx]
        nearest_distance_meters = distances.loc[nearest_idx]
        nearest_distance_miles = nearest_distance_meters * 0.000621371
        
        return nearest_highway, nearest_distance_miles
    
    def calculate_highway_scores(self):
        """Calculate highway proximity scores for all sites"""
        logger.info("\n🛣️  Calculating Highway Proximity Scores...")
        
        results = []
        
        for idx, site in self.sites_gdf.iterrows():
            if idx % 20 == 0:
                logger.info(f"   Processing site {idx+1}/{len(self.sites_gdf)}...")
            
            site_results = {
                'Site_Index': idx,
                'Property_Name': site.get('Property_Name', ''),
                'Address': site.get('Address', ''),
                'City': site.get('City', ''),
                'County': site.get('County', ''),
                'Latitude': site.geometry.y,
                'Longitude': site.geometry.x
            }
            
            # Calculate distance to each highway type
            for class_name, class_info in self.classifications.items():
                if class_info['scoring_weight'] > 0:
                    nearest, distance = self.calculate_nearest_highway(
                        site.geometry, 
                        class_name
                    )
                    
                    if nearest is not None:
                        site_results[f'{class_name}_Distance_Miles'] = round(distance, 2)
                        site_results[f'{class_name}_Name'] = nearest.get('display_name', 'Unknown')
                        
                        # Check if within search radius
                        within_radius = distance <= class_info['search_radius_miles']
                        site_results[f'{class_name}_Within_Radius'] = within_radius
                    else:
                        site_results[f'{class_name}_Distance_Miles'] = float('inf')
                        site_results[f'{class_name}_Name'] = 'None'
                        site_results[f'{class_name}_Within_Radius'] = False
            
            # Calculate overall highway score
            highway_score = self.calculate_highway_access_score(site_results)
            site_results['Highway_Access_Score'] = highway_score
            site_results['Highway_Access_Rating'] = self.get_highway_rating(highway_score)
            
            results.append(site_results)
        
        # Convert to DataFrame
        results_df = pd.DataFrame(results)
        
        # Add summary statistics
        logger.info("\n📊 Highway Proximity Summary:")
        logger.info(f"   Sites with Interstate < 5 miles: {sum(results_df['Interstate_Within_Radius'])}")
        logger.info(f"   Sites with US Highway < 4 miles: {sum(results_df['US_Highway_Within_Radius'])}")
        logger.info(f"   Sites with State Highway < 3 miles: {sum(results_df['State_Highway_Within_Radius'])}")
        
        return results_df
    
    def calculate_highway_access_score(self, site_data):
        """Calculate highway access score (0-1) based on proximity"""
        
        score = 0.0
        
        # Check each highway type in priority order
        if site_data.get('Interstate_Within_Radius', False):
            # Interstate within radius
            distance = site_data['Interstate_Distance_Miles']
            if distance <= 2:
                score = 1.0
            elif distance <= 5:
                score = 0.8 + (0.2 * (5 - distance) / 3)  # Linear scale 0.8-1.0
        
        elif site_data.get('US_Highway_Within_Radius', False):
            # US Highway within radius
            distance = site_data['US_Highway_Distance_Miles']
            if distance <= 2:
                score = 0.8
            elif distance <= 4:
                score = 0.6 + (0.2 * (4 - distance) / 2)  # Linear scale 0.6-0.8
        
        elif site_data.get('State_Highway_Within_Radius', False):
            # State Highway within radius
            distance = site_data['State_Highway_Distance_Miles']
            if distance <= 2:
                score = 0.6
            elif distance <= 3:
                score = 0.4 + (0.2 * (3 - distance) / 1)  # Linear scale 0.4-0.6
        
        else:
            # No major highway within search radius
            score = 0.0
        
        return round(score, 3)
    
    def get_highway_rating(self, score):
        """Get text rating for highway score"""
        if score >= 0.8:
            return "Excellent - Major highway nearby"
        elif score >= 0.6:
            return "Good - Highway accessible"
        elif score >= 0.4:
            return "Fair - Limited highway access"
        elif score > 0:
            return "Poor - Distant from highways"
        else:
            return "Isolated - No highway access"
    
    def save_results(self, results_df, output_file):
        """Save highway proximity results"""
        logger.info(f"\n💾 Saving results to: {output_file}")
        
        # Create summary statistics
        summary_stats = {
            'Total_Sites': len(results_df),
            'Excellent_Access': sum(results_df['Highway_Access_Score'] >= 0.8),
            'Good_Access': sum((results_df['Highway_Access_Score'] >= 0.6) & 
                              (results_df['Highway_Access_Score'] < 0.8)),
            'Fair_Access': sum((results_df['Highway_Access_Score'] >= 0.4) & 
                              (results_df['Highway_Access_Score'] < 0.6)),
            'Poor_Access': sum((results_df['Highway_Access_Score'] > 0) & 
                              (results_df['Highway_Access_Score'] < 0.4)),
            'Isolated': sum(results_df['Highway_Access_Score'] == 0),
            'Average_Score': results_df['Highway_Access_Score'].mean(),
            'Median_Score': results_df['Highway_Access_Score'].median()
        }
        
        # Save to Excel with multiple sheets
        with pd.ExcelWriter(output_file) as writer:
            # All results
            results_df.to_excel(writer, sheet_name='Highway_Proximity_Analysis', index=False)
            
            # Summary statistics
            summary_df = pd.DataFrame([summary_stats]).T
            summary_df.columns = ['Value']
            summary_df.to_excel(writer, sheet_name='Summary_Statistics')
            
            # Sites by rating
            for rating in results_df['Highway_Access_Rating'].unique():
                rating_df = results_df[results_df['Highway_Access_Rating'] == rating]
                sheet_name = rating.split(' - ')[0].replace(' ', '_')[:30]
                rating_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info("✅ Results saved successfully!")
        
        return summary_stats

def main():
    """Calculate highway proximity for all LIHTC sites"""
    
    calculator = HighwayProximityCalculator()
    
    # Load sites data
    excel_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/Complete_Anchor_Analysis_All_195_Sites_20250702_151312.xlsx"
    
    if not Path(excel_file).exists():
        logger.error(f"Sites file not found: {excel_file}")
        return
    
    sites_gdf = calculator.load_sites_data(excel_file)
    
    # Calculate highway proximity
    results_df = calculator.calculate_highway_scores()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"Highway_Proximity_Analysis_{timestamp}.xlsx"
    
    summary = calculator.save_results(results_df, output_file)
    
    # Print summary
    print("\n🛣️  HIGHWAY PROXIMITY ANALYSIS COMPLETE")
    print("=" * 50)
    print(f"Total Sites Analyzed: {summary['Total_Sites']}")
    print(f"\nHighway Access Distribution:")
    print(f"  Excellent (≥0.8): {summary['Excellent_Access']} sites")
    print(f"  Good (0.6-0.8):   {summary['Good_Access']} sites")
    print(f"  Fair (0.4-0.6):   {summary['Fair_Access']} sites")
    print(f"  Poor (>0-0.4):    {summary['Poor_Access']} sites")
    print(f"  Isolated (0):     {summary['Isolated']} sites")
    print(f"\nAverage Score: {summary['Average_Score']:.3f}")
    print(f"Median Score:  {summary['Median_Score']:.3f}")
    print(f"\n✅ Analysis saved to: {output_file}")

if __name__ == "__main__":
    main()