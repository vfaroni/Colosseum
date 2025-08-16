#!/usr/bin/env python3
"""
Combine CostarExport Files 8-15 for Column Preservation Testing

This script combines CostarExport-8.xlsx through CostarExport-15.xlsx
and verifies column consistency across all files.

Author: VITOR WINGMAN
Date: 2025-08-16
"""

import pandas as pd
import os
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def combine_costar_exports():
    """Combine CostarExport files 8-15 and verify column consistency"""
    
    print("🏛️ COSTAR EXPORT COMBINER - FILES 8-15")
    print("=" * 50)
    
    base_dir = Path("/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/botn_engine/Sites")
    
    # Files to combine (8-15)
    file_numbers = range(8, 16)  # 8 through 15
    files_to_combine = []
    
    for num in file_numbers:
        file_path = base_dir / f"CostarExport-{num}.xlsx"
        if file_path.exists():
            files_to_combine.append((num, file_path))
            print(f"✅ Found: CostarExport-{num}.xlsx")
        else:
            print(f"❌ Missing: CostarExport-{num}.xlsx")
    
    if not files_to_combine:
        print("❌ No CostarExport files found!")
        return None
    
    print(f"\n📊 Processing {len(files_to_combine)} files...")
    
    # Load and analyze each file
    all_dataframes = []
    column_analysis = {}
    
    for file_num, file_path in files_to_combine:
        try:
            print(f"\n📁 Loading CostarExport-{file_num}.xlsx...")
            df = pd.read_excel(file_path)
            
            print(f"   📊 Shape: {df.shape}")
            print(f"   📋 Columns: {len(df.columns)}")
            
            # Store column info
            column_analysis[file_num] = {
                'columns': list(df.columns),
                'count': len(df.columns),
                'rows': len(df),
                'file_path': str(file_path)
            }
            
            # Add source file column
            df['Source_File'] = f'CostarExport-{file_num}'
            df['Source_File_Number'] = file_num
            
            all_dataframes.append(df)
            
        except Exception as e:
            print(f"❌ Error loading CostarExport-{file_num}.xlsx: {e}")
            continue
    
    if not all_dataframes:
        print("❌ No files successfully loaded!")
        return None
    
    # Analyze column consistency
    print(f"\n🔍 COLUMN CONSISTENCY ANALYSIS")
    print("=" * 50)
    
    # Get reference columns from first file
    reference_columns = column_analysis[files_to_combine[0][0]]['columns']
    reference_count = len(reference_columns)
    
    print(f"📋 Reference: CostarExport-{files_to_combine[0][0]} ({reference_count} columns)")
    
    consistent_columns = True
    for file_num, info in column_analysis.items():
        if file_num == files_to_combine[0][0]:
            continue
            
        current_columns = info['columns']
        current_count = info['count']
        
        if current_count != reference_count:
            print(f"⚠️  CostarExport-{file_num}: {current_count} columns (differs from reference)")
            consistent_columns = False
        else:
            print(f"✅ CostarExport-{file_num}: {current_count} columns (matches)")
        
        # Check for missing or extra columns
        missing_cols = set(reference_columns) - set(current_columns)
        extra_cols = set(current_columns) - set(reference_columns)
        
        if missing_cols:
            print(f"   ❌ Missing columns: {list(missing_cols)[:5]}{'...' if len(missing_cols) > 5 else ''}")
            consistent_columns = False
            
        if extra_cols:
            print(f"   ➕ Extra columns: {list(extra_cols)[:5]}{'...' if len(extra_cols) > 5 else ''}")
    
    print(f"\n📋 COLUMN CONSISTENCY: {'✅ CONSISTENT' if consistent_columns else '⚠️ INCONSISTENT'}")
    
    # Display all unique columns across files
    all_columns = set()
    for info in column_analysis.values():
        all_columns.update(info['columns'])
    
    print(f"\n📊 TOTAL UNIQUE COLUMNS FOUND: {len(all_columns)}")
    print("Columns:")
    for i, col in enumerate(sorted(all_columns), 1):
        print(f"   {i:2d}. {col}")
    
    # Combine dataframes
    print(f"\n🔄 COMBINING DATAFRAMES...")
    
    try:
        # Use concat to combine all dataframes
        combined_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
        
        total_rows = len(combined_df)
        total_cols = len(combined_df.columns)
        
        print(f"✅ Combined successfully!")
        print(f"   📊 Final shape: {combined_df.shape}")
        print(f"   📋 Total columns: {total_cols}")
        print(f"   📄 Total rows: {total_rows}")
        
        # Save combined file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = base_dir / f"CostarExport_Combined_8-15_{timestamp}.xlsx"
        
        print(f"\n💾 Saving combined file...")
        combined_df.to_excel(output_file, index=False)
        print(f"✅ Saved: {output_file.name}")
        
        # Create summary report
        summary = {
            'combination_timestamp': timestamp,
            'files_processed': len(files_to_combine),
            'total_rows': total_rows,
            'total_columns': total_cols,
            'column_consistency': consistent_columns,
            'files_info': column_analysis,
            'output_file': str(output_file)
        }
        
        summary_file = base_dir / f"CostarExport_Combination_Summary_{timestamp}.json"
        import json
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📝 Summary saved: {summary_file.name}")
        
        # Show file breakdown
        print(f"\n📊 FILE BREAKDOWN:")
        file_counts = combined_df['Source_File'].value_counts().sort_index()
        for file_name, count in file_counts.items():
            print(f"   {file_name}: {count:,} rows")
        
        return output_file, combined_df
        
    except Exception as e:
        print(f"❌ Error combining dataframes: {e}")
        return None, None

def verify_column_preservation(combined_file):
    """Verify the expected 37 columns are preserved"""
    
    print(f"\n🔍 COLUMN PRESERVATION VERIFICATION")
    print("=" * 50)
    
    # Expected columns (from previous analysis)
    expected_columns = [
        'Property Address', 'Property Name', 'Land Area (AC)', 'Land Area (SF)',
        'Property Type', 'Secondary Type', 'Market Name', 'Submarket Name',
        'City', 'County Name', 'State', 'Zip', 'For Sale Price',
        'Sale Company Name', 'Sale Company Address', 'Sale Company City State Zip',
        'Sale Company Phone', 'Sale Company Fax', 'Sale Company Contact',
        'Zoning', 'Parcel Number 1(Min)', 'Parcel Number 2(Max)',
        'True Owner Address', 'True Owner City State Zip', 'True Owner Contact',
        'True Owner Name', 'True Owner Phone', 'Flood Risk Area',
        'Fema Flood Zone', 'FEMA Map Date', 'FEMA Map Identifier',
        'Days On Market', 'Closest Transit Stop', 'Closest Transit Stop Dist (mi)',
        'Closest Transit Stop Walk Time (min)', 'Latitude', 'Longitude'
    ]
    
    if combined_file is None:
        print("❌ No combined file to verify")
        return
    
    # Load combined file
    df = pd.read_excel(combined_file)
    
    print(f"📁 File: {combined_file.name}")
    print(f"📊 Total columns in combined file: {len(df.columns)}")
    
    # Check each expected column
    missing_columns = []
    present_columns = []
    
    for col in expected_columns:
        if col in df.columns:
            present_columns.append(col)
            print(f"✅ {col}")
        else:
            missing_columns.append(col)
            print(f"❌ MISSING: {col}")
    
    print(f"\n📊 PRESERVATION SUMMARY:")
    print(f"   ✅ Present: {len(present_columns)}/{len(expected_columns)} ({100*len(present_columns)/len(expected_columns):.1f}%)")
    
    if missing_columns:
        print(f"   ❌ Missing: {len(missing_columns)} columns")
        print(f"   Missing columns: {missing_columns}")
    else:
        print(f"   🎉 ALL EXPECTED COLUMNS PRESENT!")
    
    # Show additional columns (not in expected list)
    additional_columns = [col for col in df.columns if col not in expected_columns]
    if additional_columns:
        print(f"   ➕ Additional: {len(additional_columns)} columns")
        print(f"   Additional columns: {additional_columns[:10]}{'...' if len(additional_columns) > 10 else ''}")
    
    return len(missing_columns) == 0

if __name__ == "__main__":
    # Combine files
    combined_file, combined_df = combine_costar_exports()
    
    if combined_file:
        # Verify column preservation
        all_present = verify_column_preservation(combined_file)
        
        print(f"\n" + "=" * 50)
        print(f"🎯 COMBINATION COMPLETE")
        print(f"   📁 Combined file: {combined_file.name}")
        print(f"   📊 Column preservation: {'✅ SUCCESS' if all_present else '❌ ISSUES FOUND'}")
        print(f"   🔄 Ready for enhanced BOTN processing")
    else:
        print(f"\n❌ COMBINATION FAILED")