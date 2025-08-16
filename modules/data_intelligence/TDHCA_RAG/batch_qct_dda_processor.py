#!/usr/bin/env python3
"""
Batch QCT/DDA Processor - Handles 375 sites with proper rate limiting and checkpointing
"""

import pandas as pd
from fixed_qct_dda_analyzer import FixedQCTDDAAnalyzer
from datetime import datetime
import time
import os

def batch_process_qct_dda():
    """Process 375 sites in batches with checkpointing"""
    print("🎯 BATCH QCT/DDA PROCESSOR - 375 COSTAR SITES")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = FixedQCTDDAAnalyzer()
    
    # Load input data
    input_file = "D'Marco_Sites/Analysis_Results/CoStar_375_Phase1_Screening_20250731_160305.xlsx"
    df = pd.read_excel(input_file)
    print(f"✅ Loaded {len(df)} sites for analysis")
    
    # Add analysis columns if not present
    analysis_columns = [
        'Census_Tract', 'ZIP_Code', 'QCT_Status', 'DDA_Status',
        'Basis_Boost_Eligible', 'Industry_Classification', 'Analysis_Status'
    ]
    
    for col in analysis_columns:
        if col not in df.columns:
            df[col] = ''
    
    # Check for existing checkpoint
    checkpoint_file = "D'Marco_Sites/Analysis_Results/QCT_DDA_Progress_Checkpoint.xlsx"
    start_idx = 0
    
    if os.path.exists(checkpoint_file):
        checkpoint_df = pd.read_excel(checkpoint_file)
        print(f"📄 Found checkpoint with {len(checkpoint_df)} completed sites")
        
        # Copy completed results
        for idx in range(len(checkpoint_df)):
            if checkpoint_df.at[idx, 'Analysis_Status'] == 'Success':
                for col in analysis_columns:
                    if col in checkpoint_df.columns:
                        df.at[idx, col] = checkpoint_df.at[idx, col]
        
        # Find where to restart
        completed_count = len(checkpoint_df[checkpoint_df['Analysis_Status'] == 'Success'])
        start_idx = completed_count
        print(f"🔄 Resuming from site {start_idx + 1}")
    
    # Process in batches of 25
    batch_size = 25
    total_sites = len(df)
    
    # Counters
    qct_count = len(df[df['QCT_Status'].str.contains('QCT', na=False) & (df['QCT_Status'] != 'Not QCT')])
    dda_count = len(df[df['DDA_Status'].str.contains('DDA', na=False) & (df['DDA_Status'] != 'Not DDA')])
    boost_count = len(df[df['Basis_Boost_Eligible'] == 'YES'])
    
    print(f"📊 Starting counters - QCT: {qct_count}, DDA: {dda_count}, Boost: {boost_count}")
    
    start_time = time.time()
    
    for batch_start in range(start_idx, total_sites, batch_size):
        batch_end = min(batch_start + batch_size, total_sites)
        print(f"\n🔄 PROCESSING BATCH {batch_start + 1}-{batch_end}...")
        
        batch_start_time = time.time()
        
        for idx in range(batch_start, batch_end):
            if df.at[idx, 'Analysis_Status'] == 'Success':
                continue  # Skip already completed
            
            row = df.iloc[idx]
            lat = row['Latitude']
            lon = row['Longitude']
            city = row.get('City', 'Unknown')
            
            # Analyze site
            result = analyzer.analyze_site(lat, lon, city)
            
            # Update dataframe
            df.at[idx, 'Census_Tract'] = result['census_tract'] or ''
            df.at[idx, 'ZIP_Code'] = result['zip_code'] or ''
            df.at[idx, 'QCT_Status'] = result['qct_status']
            df.at[idx, 'DDA_Status'] = result['dda_status']
            df.at[idx, 'Basis_Boost_Eligible'] = 'YES' if result['basis_boost_eligible'] else 'NO'
            df.at[idx, 'Industry_Classification'] = result['industry_classification']
            df.at[idx, 'Analysis_Status'] = result['analysis_status']
            
            # Update counters
            if 'QCT' in result['qct_status'] and result['qct_status'] != 'Not QCT':
                qct_count += 1
            if 'DDA' in result['dda_status'] and result['dda_status'] != 'Not DDA':
                dda_count += 1
            if result['basis_boost_eligible']:
                boost_count += 1
            
            print(f"  ✅ {idx+1:3d}/{total_sites}: {city[:20]:20s} - {result['industry_classification']}")
            
            # Rate limiting
            time.sleep(1.1)
        
        batch_time = time.time() - batch_start_time
        total_time = time.time() - start_time
        remaining_sites = total_sites - batch_end
        
        if batch_end < total_sites:
            rate = (batch_end - start_idx) / total_time * 60 if total_time > 0 else 0
            eta_minutes = remaining_sites / rate if rate > 0 else 0
            
            print(f"📊 Batch complete: {batch_time:.1f}s, Rate: {rate:.1f} sites/min, ETA: {eta_minutes:.1f} min")
            print(f"🎯 Current totals: QCT={qct_count}, DDA={dda_count}, Boost={boost_count}")
            
            # Save checkpoint
            df.to_excel(checkpoint_file, index=False)
            print(f"💾 Checkpoint saved")
    
    # Final results
    total_time = time.time() - start_time
    successful_analyses = len(df[df['Analysis_Status'] == 'Success'])
    
    print(f"\n📊 FINAL QCT/DDA ANALYSIS RESULTS:")
    print(f"⏱️ Total time: {total_time/60:.1f} minutes")
    print(f"✅ Successful analyses: {successful_analyses}/{total_sites} ({successful_analyses/total_sites*100:.1f}%)")
    print(f"🎯 QCT Sites: {qct_count}")
    print(f"🎯 DDA Sites: {dda_count}")
    print(f"✅ Total Basis Boost Eligible: {boost_count}")
    print(f"📈 Eligibility Rate: {boost_count/total_sites*100:.1f}%")
    
    # Geographic breakdown
    print(f"\n🗺️ QCT/DDA SITES BY TOP CITIES:")
    eligible_sites = df[df['Basis_Boost_Eligible'] == 'YES']
    if len(eligible_sites) > 0:
        city_counts = eligible_sites['City'].value_counts().head(10)
        for city, count in city_counts.items():
            city_total = len(df[df['City'] == city])
            print(f"  {city}: {count}/{city_total} sites ({count/city_total*100:.1f}%)")
    
    # Save final results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Complete analysis
    output_file = f"D'Marco_Sites/Analysis_Results/CoStar_375_COMPLETE_QCT_DDA_Analysis_{timestamp}.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\n💾 Complete analysis saved: {output_file}")
    
    # QCT/DDA eligible sites only
    if len(eligible_sites) > 0:
        eligible_file = f"D'Marco_Sites/Analysis_Results/CoStar_375_QCT_DDA_ELIGIBLE_Sites_{timestamp}.xlsx"
        eligible_sites.to_excel(eligible_file, index=False)
        print(f"🎯 QCT/DDA eligible sites saved: {eligible_file}")
        
        # Summary for M4 Beast
        print(f"\n📋 M4 BEAST HANDOFF SUMMARY:")
        print(f"🎯 {len(eligible_sites)} QCT/DDA eligible sites ready for comprehensive analysis")
        print(f"🏗️ Combined with {len(df[df['Unit_Count_Category'] == 'Excellent (400+)'])} excellent density sites")
        print(f"📊 Total investment pipeline: {len(df[df['Viable_250_Units'] == 'YES'])} viable sites")
    
    # Clean up checkpoint
    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)
        print(f"🧹 Checkpoint file cleaned up")
    
    return df, boost_count

if __name__ == "__main__":
    results, eligible_count = batch_process_qct_dda()
    print(f"\n🎯 MISSION COMPLETE: {eligible_count} sites eligible for 130% basis boost!")