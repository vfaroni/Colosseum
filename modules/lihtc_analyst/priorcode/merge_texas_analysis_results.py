"""
Merge Texas Land Analysis results with original CoStar data
Combines all original fields with new analysis results
"""

import pandas as pd
import os
from datetime import datetime
from pathlib import Path

def merge_analysis_with_original(original_file: str, analysis_file: str, output_file: str = None):
    """
    Merge analysis results with original CoStar data
    
    Args:
        original_file: Path to original CoStar Excel file
        analysis_file: Path to analysis results Excel file (with TEST at end)
        output_file: Optional output filename, auto-generated if not provided
    """
    
    print("="*80)
    print("MERGING TEXAS LAND ANALYSIS RESULTS WITH ORIGINAL DATA")
    print("="*80)
    
    # Load both files
    print("\nLoading original CoStar data...")
    df_original = pd.read_excel(original_file)
    print(f"Original data: {len(df_original)} properties")
    print(f"Original columns: {len(df_original.columns)}")
    
    print("\nLoading analysis results...")
    df_analysis = pd.read_excel(analysis_file, sheet_name='Full Analysis')
    print(f"Analysis results: {len(df_analysis)} properties")
    print(f"Analysis columns: {len(df_analysis.columns)}")
    
    # Create mapping based on original index
    print("\nMerging data based on original index...")
    
    # The analysis results should have 'original_index' column
    if 'original_index' in df_analysis.columns:
        # Sort analysis by original index
        df_analysis = df_analysis.sort_values('original_index')
        
        # Reset original dataframe index to ensure alignment
        df_original = df_original.reset_index(drop=True)
        
        # Merge using the index
        df_merged = df_original.copy()
        
        # Add all analysis columns except duplicates
        analysis_cols_to_add = []
        for col in df_analysis.columns:
            if col not in ['original_index', 'Address', 'City', 'County', 
                          'Census_Tract', 'Latitude', 'Longitude']:
                analysis_cols_to_add.append(col)
        
        print(f"\nAdding {len(analysis_cols_to_add)} new analysis columns...")
        
        # Map analysis results back to original rows
        for idx, analysis_row in df_analysis.iterrows():
            orig_idx = int(analysis_row['original_index'])
            if orig_idx < len(df_merged):
                for col in analysis_cols_to_add:
                    df_merged.loc[orig_idx, col] = analysis_row[col]
    
    else:
        # Fallback: merge on address/coordinates
        print("\nNo original_index found, merging by coordinates...")
        df_merged = pd.merge(
            df_original,
            df_analysis,
            left_on=['Latitude', 'Longitude'],
            right_on=['Latitude', 'Longitude'],
            how='left',
            suffixes=('', '_analysis')
        )
    
    # Generate output filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'Texas_Land_Analysis_COMPLETE_{timestamp}.xlsx'
    
    print(f"\nGenerating comprehensive output file...")
    
    # Create Excel writer
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Full merged data
        df_merged.to_excel(writer, sheet_name='Complete Analysis', index=False)
        
        # Summary sheets
        print("Creating summary sheets...")
        
        # 1. Overview Summary
        overview_data = {
            'Metric': [
                'Total Properties',
                'Properties Analyzed',
                'Properties Not Analyzed',
                'Eligible Properties (Pass One Mile Rule)',
                'Ineligible Properties',
                'Properties with Complete Proximity Data',
                'Properties Missing Some Proximity Data'
            ],
            'Count': [
                len(df_merged),
                df_merged['eligibility'].notna().sum() if 'eligibility' in df_merged else 0,
                df_merged['eligibility'].isna().sum() if 'eligibility' in df_merged else len(df_merged),
                (df_merged['eligibility'] == 'ELIGIBLE').sum() if 'eligibility' in df_merged else 0,
                (df_merged['eligibility'] != 'ELIGIBLE').sum() if 'eligibility' in df_merged else 0,
                sum(
                    df_merged['grocery_store_distance_miles'].notna() & 
                    df_merged['elementary_school_distance_miles'].notna() &
                    df_merged['pharmacy_distance_miles'].notna()
                ) if all(col in df_merged for col in ['grocery_store_distance_miles', 
                        'elementary_school_distance_miles', 'pharmacy_distance_miles']) else 0,
                sum(
                    df_merged['grocery_store_distance_miles'].isna() | 
                    df_merged['elementary_school_distance_miles'].isna() |
                    df_merged['pharmacy_distance_miles'].isna()
                ) if any(col in df_merged for col in ['grocery_store_distance_miles', 
                        'elementary_school_distance_miles', 'pharmacy_distance_miles']) else 0
            ]
        }
        pd.DataFrame(overview_data).to_excel(writer, sheet_name='Overview', index=False)
        
        # 2. Eligible Properties Only
        if 'eligibility' in df_merged:
            eligible_df = df_merged[df_merged['eligibility'] == 'ELIGIBLE'].copy()
            if len(eligible_df) > 0:
                eligible_df.to_excel(writer, sheet_name='Eligible Properties', index=False)
        
        # 3. Properties with LIHTC Competition
        if 'one_mile_competing_count' in df_merged:
            competition_df = df_merged[df_merged['one_mile_competing_count'] > 0].copy()
            if len(competition_df) > 0:
                competition_df.to_excel(writer, sheet_name='Properties with Competition', index=False)
        
        # 4. Top Opportunities (Eligible + Good Proximity)
        if all(col in df_merged for col in ['eligibility', 'grocery_store_distance_miles', 
                                            'elementary_school_distance_miles']):
            opportunities_df = df_merged[
                (df_merged['eligibility'] == 'ELIGIBLE') &
                (df_merged['grocery_store_distance_miles'] <= 2) &
                (df_merged['elementary_school_distance_miles'] <= 1) &
                (df_merged['pharmacy_distance_miles'] <= 1)
            ].copy()
            
            if len(opportunities_df) > 0:
                # Sort by best overall proximity
                opportunities_df['total_proximity_score'] = (
                    opportunities_df['grocery_store_distance_miles'] +
                    opportunities_df['elementary_school_distance_miles'] +
                    opportunities_df['pharmacy_distance_miles']
                )
                opportunities_df = opportunities_df.sort_values('total_proximity_score')
                opportunities_df.to_excel(writer, sheet_name='Top Opportunities', index=False)
        
        # 5. Properties Needing Review
        review_conditions = []
        if 'eligibility' in df_merged:
            review_conditions.append(df_merged['eligibility'] != 'ELIGIBLE')
        if 'grocery_store_distance_miles' in df_merged:
            review_conditions.append(df_merged['grocery_store_distance_miles'] > 5)
            review_conditions.append(df_merged['grocery_store_distance_miles'].isna())
        if 'city_population' in df_merged:
            review_conditions.append(df_merged['city_population'].isna())
        
        if review_conditions:
            review_df = df_merged[pd.concat(review_conditions, axis=1).any(axis=1)].copy()
            if len(review_df) > 0:
                review_df.to_excel(writer, sheet_name='Needs Review', index=False)
        
        # 6. Distance Statistics by County
        if all(col in df_merged for col in ['County', 'grocery_store_distance_miles']):
            county_stats = df_merged.groupby('County').agg({
                'Address': 'count',
                'eligibility': lambda x: (x == 'ELIGIBLE').sum() if 'eligibility' in df_merged else 0,
                'grocery_store_distance_miles': ['mean', 'min', 'max'],
                'pharmacy_distance_miles': ['mean', 'min', 'max'],
                'elementary_school_distance_miles': ['mean', 'min', 'max'],
                'transit_stop_distance_miles': ['mean', 'min', 'max']
            }).round(2)
            
            # Flatten column names
            county_stats.columns = ['_'.join(col).strip() if col[1] else col[0] 
                                   for col in county_stats.columns.values]
            county_stats.to_excel(writer, sheet_name='County Statistics')
    
    print(f"\n✅ Merge complete! Output saved to: {output_file}")
    print(f"\nFile contains:")
    print(f"  - Complete Analysis: All original CoStar fields + analysis results")
    print(f"  - Overview: Summary statistics")
    print(f"  - Eligible Properties: Only properties passing One Mile Rule")
    print(f"  - Top Opportunities: Best sites based on proximity")
    print(f"  - Needs Review: Properties with issues or missing data")
    print(f"  - County Statistics: Average distances by county")
    
    return df_merged


def find_latest_files():
    """Find the latest original and analysis files"""
    # Common directories to search
    search_dirs = [
        Path.cwd(),
        Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Costar/TX/"),
        Path("./")
    ]
    
    original_pattern = "*CoStar_TX_Land_TDHCA_FLOOD_Analysis*.xlsx"
    analysis_pattern = "*TEST.xlsx"
    
    original_files = []
    analysis_files = []
    
    for dir_path in search_dirs:
        if dir_path.exists():
            original_files.extend(dir_path.glob(original_pattern))
            analysis_files.extend(dir_path.glob(analysis_pattern))
    
    return original_files, analysis_files


def main():
    """Main function with interactive file selection"""
    
    print("Texas Land Analysis - Merge Results with Original Data")
    print("="*50)
    
    # Try to find files automatically
    original_files, analysis_files = find_latest_files()
    
    # Original file
    if original_files:
        print("\nFound original CoStar files:")
        for i, f in enumerate(original_files[:5]):
            print(f"{i+1}. {f.name}")
        
        if len(original_files) == 1:
            original_file = str(original_files[0])
            print(f"\nUsing: {original_file}")
        else:
            choice = input("\nSelect original file number (or enter path): ")
            if choice.isdigit() and 1 <= int(choice) <= len(original_files):
                original_file = str(original_files[int(choice)-1])
            else:
                original_file = choice
    else:
        original_file = input("\nEnter path to original CoStar Excel file: ")
    
    # Analysis file
    if analysis_files:
        print("\nFound analysis result files:")
        for i, f in enumerate(analysis_files[:5]):
            print(f"{i+1}. {f.name}")
        
        if len(analysis_files) == 1:
            analysis_file = str(analysis_files[0])
            print(f"\nUsing: {analysis_file}")
        else:
            choice = input("\nSelect analysis file number (or enter path): ")
            if choice.isdigit() and 1 <= int(choice) <= len(analysis_files):
                analysis_file = str(analysis_files[int(choice)-1])
            else:
                analysis_file = choice
    else:
        analysis_file = input("\nEnter path to analysis results Excel file (with TEST): ")
    
    # Check files exist
    if not Path(original_file).exists():
        print(f"\n❌ Error: Original file not found: {original_file}")
        return
    
    if not Path(analysis_file).exists():
        print(f"\n❌ Error: Analysis file not found: {analysis_file}")
        return
    
    # Run merge
    merge_analysis_with_original(original_file, analysis_file)


if __name__ == "__main__":
    main()