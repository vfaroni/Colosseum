"""
Merge specific Texas Land Analysis files
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

def safe_merge_files():
    """Merge the specific analysis and CoStar files"""
    
    # Specific file paths
    analysis_file = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/Texas_Land_Integrated_Analysis_20250615_173225_TEST.xlsx'
    original_file = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Costar/TX/CoStar_TX_Land_TDHCA_FLOOD_Analysis_20250606_113809.xlsx'
    
    print("="*80)
    print("MERGING TEXAS LAND ANALYSIS FILES")
    print("="*80)
    
    try:
        # Load original CoStar data
        print(f"\nLoading original CoStar data...")
        print(f"File: {Path(original_file).name}")
        df_original = pd.read_excel(original_file)
        print(f"✓ Loaded {len(df_original)} properties with {len(df_original.columns)} columns")
        
        # Load analysis results
        print(f"\nLoading analysis results...")
        print(f"File: {Path(analysis_file).name}")
        
        # Try to read the Full Analysis sheet first
        try:
            df_analysis = pd.read_excel(analysis_file, sheet_name='Full Analysis')
            print(f"✓ Loaded 'Full Analysis' sheet: {len(df_analysis)} properties")
        except:
            # If no Full Analysis sheet, read first sheet
            df_analysis = pd.read_excel(analysis_file)
            print(f"✓ Loaded first sheet: {len(df_analysis)} properties")
        
        # Display column info for debugging
        print(f"\nAnalysis columns ({len(df_analysis.columns)}):")
        analysis_cols = list(df_analysis.columns)
        for i, col in enumerate(analysis_cols[:10]):
            print(f"  - {col}")
        if len(analysis_cols) > 10:
            print(f"  ... and {len(analysis_cols) - 10} more columns")
        
        # Check for key columns
        print("\nChecking for key columns in analysis data:")
        key_cols = ['original_index', 'Latitude', 'Longitude', 'Address', 'eligibility']
        for col in key_cols:
            if col in df_analysis.columns:
                print(f"  ✓ {col} found")
            else:
                print(f"  ✗ {col} NOT found")
        
        # Prepare for merge
        print("\nPreparing merge...")
        df_merged = df_original.copy()
        
        # Determine merge strategy
        if 'original_index' in df_analysis.columns:
            print("Using original_index for merge...")
            
            # Get columns to add (exclude duplicates)
            duplicate_cols = ['Address', 'City', 'County', 'Census_Tract', 'Latitude', 'Longitude', 
                            'original_index', 'CT_2020', 'Census Tract', 'CT 2020']
            
            new_cols = []
            for col in df_analysis.columns:
                if col not in duplicate_cols and col not in df_merged.columns:
                    new_cols.append(col)
            
            print(f"Adding {len(new_cols)} new columns from analysis")
            
            # Initialize new columns
            for col in new_cols:
                df_merged[col] = np.nan
            
            # Map data by original index
            merged_count = 0
            for idx, row in df_analysis.iterrows():
                try:
                    orig_idx = int(row['original_index'])
                    if 0 <= orig_idx < len(df_merged):
                        for col in new_cols:
                            if pd.notna(row[col]):
                                df_merged.loc[orig_idx, col] = row[col]
                        merged_count += 1
                except Exception as e:
                    continue
            
            print(f"✓ Successfully merged data for {merged_count} properties")
        
        else:
            print("No original_index found, using coordinate-based merge...")
            
            # Round coordinates for matching
            df_original['Lat_round'] = df_original['Latitude'].round(6)
            df_original['Lng_round'] = df_original['Longitude'].round(6)
            df_analysis['Lat_round'] = df_analysis['Latitude'].round(6)
            df_analysis['Lng_round'] = df_analysis['Longitude'].round(6)
            
            # Merge on rounded coordinates
            df_merged = pd.merge(
                df_original,
                df_analysis,
                left_on=['Lat_round', 'Lng_round'],
                right_on=['Lat_round', 'Lng_round'],
                how='left',
                suffixes=('', '_analysis')
            )
            
            # Clean up temporary columns
            df_merged = df_merged.drop(columns=['Lat_round', 'Lng_round'])
        
        # Generate output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'Texas_Analysis_COMPLETE_MERGED_{timestamp}.xlsx'
        
        print(f"\nCreating output file: {output_file}")
        
        # Save to Excel with multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 1. Complete merged data
            df_merged.to_excel(writer, sheet_name='Complete Data', index=False)
            
            # 2. Summary statistics
            summary_data = []
            
            # Basic counts
            summary_data.append(['Total Properties', len(df_merged)])
            
            if 'eligibility' in df_merged.columns:
                eligible_count = (df_merged['eligibility'] == 'ELIGIBLE').sum()
                summary_data.append(['Eligible Properties', eligible_count])
                summary_data.append(['Ineligible Properties', len(df_merged) - eligible_count])
            
            # Proximity statistics
            proximity_cols = {
                'grocery_store_distance_miles': 'Grocery Store',
                'pharmacy_distance_miles': 'Pharmacy',
                'hospital_distance_miles': 'Hospital',
                'elementary_school_distance_miles': 'Elementary School',
                'transit_stop_distance_miles': 'Transit Stop'
            }
            
            for col, name in proximity_cols.items():
                if col in df_merged.columns:
                    found = df_merged[col].notna().sum()
                    avg_dist = df_merged[col].mean()
                    summary_data.append([f'{name} Found', found])
                    if pd.notna(avg_dist):
                        summary_data.append([f'{name} Avg Distance (miles)', round(avg_dist, 2)])
            
            summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # 3. Eligible properties only
            if 'eligibility' in df_merged.columns:
                eligible_df = df_merged[df_merged['eligibility'] == 'ELIGIBLE'].copy()
                if len(eligible_df) > 0:
                    eligible_df.to_excel(writer, sheet_name='Eligible Properties', index=False)
                    print(f"  - Added {len(eligible_df)} eligible properties")
            
            # 4. Properties with issues
            if 'eligibility' in df_merged.columns:
                issues_df = df_merged[
                    (df_merged['eligibility'] != 'ELIGIBLE') |
                    (df_merged['grocery_store_distance_miles'].isna() if 'grocery_store_distance_miles' in df_merged.columns else False)
                ].copy()
                if len(issues_df) > 0:
                    issues_df.to_excel(writer, sheet_name='Properties with Issues', index=False)
                    print(f"  - Added {len(issues_df)} properties with issues")
        
        print(f"\n✅ SUCCESS! Merged file saved as: {output_file}")
        print(f"\nThe merged file contains:")
        print(f"  - {len(df_merged)} total properties")
        print(f"  - {len(df_merged.columns)} total columns")
        print(f"  - All original CoStar data")
        print(f"  - All proximity analysis results")
        print(f"  - Competition analysis results")
        
        return output_file
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    safe_merge_files()