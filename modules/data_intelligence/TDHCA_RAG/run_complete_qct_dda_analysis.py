#!/usr/bin/env python3
"""
Run complete QCT/DDA analysis on all 375 CoStar sites
"""

import pandas as pd
from fixed_qct_dda_analyzer import FixedQCTDDAAnalyzer
from datetime import datetime
import time

def run_complete_analysis():
    """Run QCT/DDA analysis on all 375 sites"""
    print("🎯 RUNNING COMPLETE QCT/DDA ANALYSIS ON 375 COSTAR SITES")
    print("=" * 70)
    
    # Initialize analyzer
    analyzer = FixedQCTDDAAnalyzer()
    
    # Load CoStar sites
    input_file = "D'Marco_Sites/Analysis_Results/CoStar_375_Phase1_Screening_20250731_160305.xlsx"
    df = pd.read_excel(input_file)
    print(f"✅ Loaded {len(df)} CoStar sites")
    
    # Add analysis columns
    analysis_columns = [
        'Census_Tract', 'ZIP_Code', 'QCT_Status', 'DDA_Status',
        'Basis_Boost_Eligible', 'Industry_Classification', 'Analysis_Status'
    ]
    
    for col in analysis_columns:
        df[col] = ''
    
    # Track results
    qct_count = 0
    dda_count = 0
    dual_count = 0
    boost_eligible_count = 0
    successful_analyses = 0
    
    print("\\n🔍 ANALYZING SITES (this will take about 6-7 minutes with rate limiting)...")
    
    start_time = time.time()
    
    for idx, row in df.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']
        city = row.get('City', 'Unknown')
        
        # Analyze site
        result = analyzer.analyze_site(lat, lon, city)
        
        # Populate columns
        df.at[idx, 'Census_Tract'] = result['census_tract'] or ''
        df.at[idx, 'ZIP_Code'] = result['zip_code'] or ''
        df.at[idx, 'QCT_Status'] = result['qct_status']
        df.at[idx, 'DDA_Status'] = result['dda_status']
        df.at[idx, 'Basis_Boost_Eligible'] = 'YES' if result['basis_boost_eligible'] else 'NO'
        df.at[idx, 'Industry_Classification'] = result['industry_classification']
        df.at[idx, 'Analysis_Status'] = result['analysis_status']
        
        # Count results
        if 'QCT' in result['qct_status'] and result['qct_status'] != 'Not QCT':
            qct_count += 1
        if 'DDA' in result['dda_status'] and result['dda_status'] != 'Not DDA':
            dda_count += 1
        if result['industry_classification'] == 'QCT + DDA':
            dual_count += 1
        if result['basis_boost_eligible']:
            boost_eligible_count += 1
        if result['analysis_status'] == 'Success':
            successful_analyses += 1
        
        # Progress update every 25 sites
        if (idx + 1) % 25 == 0:
            elapsed = time.time() - start_time
            rate = (idx + 1) / elapsed * 60  # sites per minute
            remaining = (len(df) - idx - 1) / rate if rate > 0 else 0
            print(f"✅ {idx+1}/{len(df)} complete ({rate:.1f} sites/min, ~{remaining:.1f} min remaining)")
            print(f"   Current totals: QCT={qct_count}, DDA={dda_count}, Boost={boost_eligible_count}")
        
        # Rate limiting - be nice to Census API
        time.sleep(1.1)
    
    # Final summary
    elapsed_total = time.time() - start_time
    print(f"\\n📊 COMPLETE QCT/DDA ANALYSIS RESULTS:")
    print(f"⏱️ Total time: {elapsed_total/60:.1f} minutes")
    print(f"✅ Successful analyses: {successful_analyses}/{len(df)} ({successful_analyses/len(df)*100:.1f}%)")
    print(f"🎯 QCT Sites: {qct_count}")
    print(f"🎯 DDA Sites: {dda_count}")
    print(f"🎯 QCT + DDA Sites: {dual_count}")
    print(f"✅ Total Basis Boost Eligible: {boost_eligible_count}")
    print(f"📈 Eligibility Rate: {boost_eligible_count/len(df)*100:.1f}%")
    
    # Geographic breakdown
    print(f"\\n🗺️ QCT/DDA SITES BY CITY:")
    eligible_sites = df[df['Basis_Boost_Eligible'] == 'YES']
    if len(eligible_sites) > 0:
        city_counts = eligible_sites['City'].value_counts().head(10)
        for city, count in city_counts.items():
            city_total = len(df[df['City'] == city])
            print(f"  {city}: {count}/{city_total} sites ({count/city_total*100:.1f}%)")
    else:
        print("  No QCT/DDA eligible sites found")
    
    # Density breakdown
    if len(eligible_sites) > 0:
        print(f"\\n🏗️ QCT/DDA SITES BY DENSITY CATEGORY:")
        density_breakdown = eligible_sites['Unit_Count_Category'].value_counts()
        for category, count in density_breakdown.items():
            print(f"  {category}: {count} sites")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"D'Marco_Sites/Analysis_Results/CoStar_375_Complete_QCT_DDA_Analysis_{timestamp}.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\\n💾 Complete analysis saved: {output_file}")
    
    # Save QCT/DDA eligible sites only
    if len(eligible_sites) > 0:
        eligible_file = f"D'Marco_Sites/Analysis_Results/CoStar_375_QCT_DDA_ELIGIBLE_Sites_{timestamp}.xlsx"
        eligible_sites.to_excel(eligible_file, index=False)
        print(f"🎯 QCT/DDA eligible sites saved: {eligible_file}")
    
    return df, boost_eligible_count

if __name__ == "__main__":
    results, eligible_count = run_complete_analysis()
    print(f"\\n🎯 ANALYSIS COMPLETE: {eligible_count} sites eligible for 130% basis boost!")