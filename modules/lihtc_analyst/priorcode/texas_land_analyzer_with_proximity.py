"""
Enhanced Texas Land Analyzer with Strict Proximity Analysis
Combines existing QCT/DDA/Flood analysis with strict amenity filtering
"""

import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from texas_proximity_analyzer_strict import TexasProximityAnalyzerStrict

class TexasLandAnalyzerWithProximity:
    """
    Integrates proximity analysis into existing Texas land analysis pipeline
    """
    
    def __init__(self, google_maps_api_key: str):
        """
        Initialize the analyzer
        
        Args:
            google_maps_api_key: Google Maps API key with Places API enabled
        """
        self.proximity_analyzer = TexasProximityAnalyzerStrict(
            google_maps_api_key=google_maps_api_key,
            schools_file="/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/TX_Public_Schools/Schools_2024_to_2025.csv",
            cache_dir="./proximity_cache"
        )
        
    def enhance_strategic_scoring(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add proximity scores to the existing strategic scoring system
        
        Args:
            df: DataFrame with existing analysis including Strategic_Score
            
        Returns:
            DataFrame with enhanced scoring including proximity
        """
        # Create a copy to avoid modifying original
        enhanced_df = df.copy()
        
        # Add proximity score weight to strategic score
        # Proximity can add up to 25 points to the strategic score
        proximity_weight = 0.25
        
        if 'score_total_proximity_score' in enhanced_df.columns:
            # Convert proximity score (0-100) to strategic points (0-25)
            enhanced_df['Proximity_Strategic_Points'] = (
                enhanced_df['score_total_proximity_score'] * proximity_weight
            ).round(1)
            
            # Create enhanced strategic score
            enhanced_df['Enhanced_Strategic_Score'] = (
                enhanced_df['Strategic_Score'] + enhanced_df['Proximity_Strategic_Points']
            ).round(1)
            
            # Add specific bonuses for key amenities
            bonus_points = 0
            
            # Transit-oriented development bonus (5 points if transit within 0.25 miles)
            transit_bonus = enhanced_df['transit_stop_nearest_miles'] <= 0.25
            enhanced_df['Transit_Bonus'] = transit_bonus * 5
            
            # School proximity bonus (3 points if elementary school within 1 mile)
            school_bonus = enhanced_df['elementary_school_nearest_miles'] <= 1.0
            enhanced_df['School_Bonus'] = school_bonus * 3
            
            # Essential services bonus (2 points if grocery and pharmacy within 1 mile)
            services_bonus = (
                (enhanced_df['grocery_store_nearest_miles'] <= 1.0) & 
                (enhanced_df['pharmacy_nearest_miles'] <= 1.0)
            )
            enhanced_df['Services_Bonus'] = services_bonus * 2
            
            # Add all bonuses to final score
            enhanced_df['Final_Strategic_Score'] = (
                enhanced_df['Enhanced_Strategic_Score'] + 
                enhanced_df['Transit_Bonus'] +
                enhanced_df['School_Bonus'] +
                enhanced_df['Services_Bonus']
            ).round(1)
            
            # Re-rank based on new scores
            enhanced_df['Enhanced_Rank'] = enhanced_df['Final_Strategic_Score'].rank(
                ascending=False, 
                method='min'
            ).astype(int)
            
        return enhanced_df
    
    def analyze_land_sites_with_proximity(self, input_file: str, output_dir: str = None):
        """
        Perform complete analysis including existing metrics and proximity
        
        Args:
            input_file: Path to input Excel file with land data
            output_dir: Directory for output files (default: current directory)
        """
        # Set output directory
        if output_dir is None:
            output_dir = Path.cwd()
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
        
        print(f"Loading data from: {input_file}")
        df = pd.read_excel(input_file)
        print(f"Loaded {len(df)} properties")
        
        # Check if proximity analysis has already been done
        if 'score_total_proximity_score' not in df.columns:
            print("\nPerforming proximity analysis with STRICT filtering...")
            print("Using Texas public schools dataset and strict amenity validation...")
            print("This may take some time depending on the number of properties...")
            
            # Run proximity analysis
            proximity_results = self.proximity_analyzer.analyze_multiple_sites(
                df,
                lat_col='Latitude',
                lng_col='Longitude',
                address_col='Address'
            )
            
            # Merge proximity results with original data
            df = df.merge(
                proximity_results,
                left_index=True,
                right_on='original_index',
                how='left'
            )
            
            # Clean up duplicate columns
            if 'address_y' in df.columns:
                df = df.drop(columns=['address_y'])
                df = df.rename(columns={'address_x': 'Address'})
            if 'latitude_y' in df.columns:
                df = df.drop(columns=['latitude_y', 'longitude_y'])
                df = df.rename(columns={'latitude_x': 'Latitude', 'longitude_x': 'Longitude'})
        else:
            print("Proximity analysis already present in data")
        
        # Enhance strategic scoring with proximity
        print("\nEnhancing strategic scores with proximity data...")
        df = self.enhance_strategic_scoring(df)
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save complete analysis
        output_file = output_dir / f'Texas_Land_Complete_Proximity_Analysis_{timestamp}.xlsx'
        print(f"\nGenerating comprehensive report...")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # All properties with enhanced scoring
            df.to_excel(writer, sheet_name='Complete Analysis', index=False)
            
            # Top 50 sites by enhanced score
            top_sites = df.nlargest(50, 'Final_Strategic_Score')
            top_sites.to_excel(writer, sheet_name='Top 50 Sites', index=False)
            
            # QCT/DDA sites with excellent proximity
            qct_dda_proximity = df[
                ((df['QCT_Status'] == True) | (df['DDA_Status'] == True)) &
                (df['score_total_proximity_score'] >= 70)
            ].sort_values('Final_Strategic_Score', ascending=False)
            qct_dda_proximity.to_excel(writer, sheet_name='QCT-DDA High Proximity', index=False)
            
            # Transit-oriented development opportunities
            tod_sites = df[
                df['transit_stop_nearest_miles'] <= 0.5
            ].sort_values('Final_Strategic_Score', ascending=False)
            tod_sites.to_excel(writer, sheet_name='Transit Oriented', index=False)
            
            # Family-friendly sites (near schools and parks)
            family_sites = df[
                (df['elementary_school_nearest_miles'] <= 1.0) &
                (df['park_nearest_miles'] <= 0.5)
            ].sort_values('Final_Strategic_Score', ascending=False)
            family_sites.to_excel(writer, sheet_name='Family Friendly', index=False)
            
            # Low flood risk with high proximity
            safe_proximity = df[
                (df['SFHA_Flag'] == 0) &
                (df['score_total_proximity_score'] >= 60)
            ].sort_values('Final_Strategic_Score', ascending=False)
            safe_proximity.to_excel(writer, sheet_name='Low Flood High Proximity', index=False)
        
        print(f"Analysis complete! Results saved to: {output_file}")
        
        # Print summary statistics
        print("\n" + "="*60)
        print("ANALYSIS SUMMARY")
        print("="*60)
        print(f"Total Properties Analyzed: {len(df)}")
        print(f"\nStrategic Scoring Summary:")
        print(f"  Original Average Strategic Score: {df['Strategic_Score'].mean():.1f}")
        print(f"  Enhanced Average Strategic Score: {df['Final_Strategic_Score'].mean():.1f}")
        print(f"  Average Proximity Score: {df['score_total_proximity_score'].mean():.1f}")
        
        print(f"\nTop 5 Properties by Enhanced Score:")
        top_5 = df.nlargest(5, 'Final_Strategic_Score')[
            ['Address', 'City', 'Final_Strategic_Score', 'score_proximity_rating']
        ]
        for idx, row in top_5.iterrows():
            print(f"  {row['Address']}, {row['City']}")
            print(f"    Score: {row['Final_Strategic_Score']}, Proximity: {row['score_proximity_rating']}")
        
        print(f"\nProximity Rating Distribution:")
        rating_dist = df['score_proximity_rating'].value_counts()
        for rating, count in rating_dist.items():
            pct = (count / len(df)) * 100
            print(f"  {rating}: {count} ({pct:.1f}%)")
        
        print(f"\nKey Findings:")
        tod_count = len(df[df['transit_stop_nearest_miles'] <= 0.5])
        print(f"  Properties near transit (≤0.5 mi): {tod_count} ({(tod_count/len(df)*100):.1f}%)")
        
        school_count = len(df[df['elementary_school_nearest_miles'] <= 1.0])
        print(f"  Properties near elementary schools (≤1 mi): {school_count} ({(school_count/len(df)*100):.1f}%)")
        
        grocery_count = len(df[df['grocery_store_nearest_miles'] <= 0.5])
        print(f"  Properties near grocery stores (≤0.5 mi): {grocery_count} ({(grocery_count/len(df)*100):.1f}%)")
        
        return df


def main():
    """
    Example usage of the enhanced analyzer
    """
    # Configuration
    # TEMPORARY API KEY - MUST BE CHANGED IN PRODUCTION
    API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'AIzaSyBlOVHaaTw9nbgBlIuF90xlXHbgfzvUWAM')
    
    if API_KEY == 'YOUR_API_KEY_HERE':
        print("ERROR: Please set your Google Maps API key!")
        print("Set environment variable: export GOOGLE_MAPS_API_KEY='your_key'")
        return
    
    # Input file
    input_file = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Costar/TX/CoStar_TX_Land_TDHCA_FLOOD_Analysis_20250606_113809.xlsx'
    
    # Initialize analyzer
    analyzer = TexasLandAnalyzerWithProximity(API_KEY)
    
    # Run analysis
    analyzer.analyze_land_sites_with_proximity(
        input_file=input_file,
        output_dir='./enhanced_analysis_results'
    )


if __name__ == "__main__":
    main()