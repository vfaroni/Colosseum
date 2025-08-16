#!/usr/bin/env python3
"""
Texas QCT/DDA Strategic Analysis - Live Execution
Let's run this together to analyze your top QCT/DDA opportunities
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import json

# Add your code directory to path
sys.path.append('/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code')

def main():
    """Live execution of strategic analysis with detailed feedback"""
    
    print("🚀 TEXAS QCT/DDA STRATEGIC ANALYSIS - LIVE EXECUTION")
    print("="*60)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Set up paths
    code_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code")
    data_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets")
    
    print(f"📁 Code directory: {code_dir}")
    print(f"📁 Data directory: {data_dir}")
    
    # Check required files
    print(f"\n🔍 CHECKING REQUIRED FILES...")
    
    qct_dda_file = code_dir / "texas_qct_FEDERAL_ONLY_20250531_183850.xlsx"
    if qct_dda_file.exists():
        print(f"✅ QCT/DDA file found: {qct_dda_file.name}")
    else:
        print(f"❌ QCT/DDA file missing: {qct_dda_file}")
        return False
    
    enhanced_analyzer_file = code_dir / "enhanced_texas_analyzer_st.py"
    if enhanced_analyzer_file.exists():
        print(f"✅ Enhanced analyzer found: {enhanced_analyzer_file.name}")
    else:
        print(f"❌ Enhanced analyzer missing: {enhanced_analyzer_file}")
        return False
    
    hud_ami_file = data_dir / "HUD AMI FMR" / "HUD2025_AMI_Rent_Data_Static.xlsx"
    if hud_ami_file.exists():
        print(f"✅ HUD AMI data found: {hud_ami_file.name}")
    else:
        print(f"❌ HUD AMI data missing: {hud_ami_file}")
        print(f"   Looking for: {hud_ami_file}")
    
    tdhca_file = data_dir / "State Specific" / "TX" / "Project_List" / "TX_TDHCA_Project_List_05252025.xlsx"
    if tdhca_file.exists():
        print(f"✅ TDHCA data found: {tdhca_file.name}")
    else:
        print(f"❌ TDHCA data missing: {tdhca_file}")
        print(f"   Looking for: {tdhca_file}")
    
    # Load and examine QCT/DDA data first
    print(f"\n📊 LOADING QCT/DDA PROPERTIES...")
    try:
        properties_df = pd.read_excel(qct_dda_file)
        total_properties = len(properties_df)
        print(f"✅ Loaded {total_properties} QCT/DDA properties")
        
        # Show quick stats
        qct_count = properties_df['QCT'].sum()
        dda_count = properties_df['DDA'].sum()
        both_count = (properties_df['QCT'] & properties_df['DDA']).sum()
        
        print(f"   • QCT only: {qct_count - both_count}")
        print(f"   • DDA only: {dda_count - both_count}")
        print(f"   • Both QCT + DDA: {both_count}")
        
        # Show city distribution
        top_cities = properties_df['City'].value_counts().head(5)
        print(f"   • Top cities: {dict(top_cities)}")
        
        # Show price range
        prices = properties_df['Price Per AC Land'].dropna()
        if len(prices) > 0:
            print(f"   • Price range: ${prices.min():,.0f} - ${prices.max():,.0f} per acre")
            print(f"   • Median price: ${prices.median():,.0f} per acre")
        
    except Exception as e:
        print(f"❌ Error loading QCT/DDA file: {e}")
        return False
    
    # Apply strategic filtering
    print(f"\n🎯 APPLYING STRATEGIC FILTERING...")
    
    # Land size filter (2-8 acres optimal for LIHTC)
    original_count = len(properties_df)
    filtered_df = properties_df[
        (properties_df['Land Area (AC)'] >= 2.0) & 
        (properties_df['Land Area (AC)'] <= 8.0)
    ].copy()
    print(f"   After land size filter (2-8 acres): {len(filtered_df)} properties ({len(filtered_df)/original_count*100:.1f}%)")
    
    # Price filter (under $2M per acre)
    filtered_df = filtered_df[filtered_df['Price Per AC Land'] <= 2_000_000]
    print(f"   After price filter (<$2M/acre): {len(filtered_df)} properties ({len(filtered_df)/original_count*100:.1f}%)")
    
    if len(filtered_df) == 0:
        print(f"❌ No properties passed filtering criteria")
        return False
    
    # Calculate strategic scores
    print(f"\n🏆 CALCULATING STRATEGIC SCORES...")
    
    major_metros = [
        'Houston', 'Dallas', 'Austin', 'San Antonio', 'Fort Worth',
        'Arlington', 'Plano', 'Garland', 'Irving', 'McKinney',
        'Frisco', 'Richardson', 'Allen', 'Rowlett', 'Carrollton'
    ]
    
    def calculate_strategic_score(row):
        score = 0
        
        # QCT/DDA bonus (both gets highest bonus)
        if row['QCT'] and row['DDA']:
            score += 10  # Best case - both benefits
        elif row['QCT'] or row['DDA']:
            score += 5   # Good - one federal benefit
        
        # Major metro bonus (stronger rental markets)
        if row['City'] in major_metros:
            score += 15
        
        # Land size bonus (4-6 acres is sweet spot for 150-250 units)
        land_acres = row['Land Area (AC)']
        if 4 <= land_acres <= 6:
            score += 10  # Perfect size
        elif 3 <= land_acres <= 7:
            score += 5   # Good size
        
        # Price per acre bonus (lower is better for development)
        price_per_acre = row['Price Per AC Land']
        if price_per_acre < 100_000:
            score += 15  # Excellent value
        elif price_per_acre < 250_000:
            score += 10  # Good value
        elif price_per_acre < 500_000:
            score += 5   # Acceptable value
        
        return score
    
    filtered_df['Strategic_Score'] = filtered_df.apply(calculate_strategic_score, axis=1)
    
    # Take top 25 opportunities
    top_properties = filtered_df.nlargest(25, 'Strategic_Score')
    
    print(f"✅ Selected top {len(top_properties)} strategic opportunities")
    print(f"   Score range: {top_properties['Strategic_Score'].min()}-{top_properties['Strategic_Score'].max()}")
    
    # Show top 10 summary
    print(f"\n🏆 TOP 10 STRATEGIC OPPORTUNITIES:")
    print(f"{'Rank':<4} {'Address':<35} {'City':<15} {'Acres':<6} {'$/Acre':<12} {'Benefits':<10} {'Score':<5}")
    print("-" * 95)
    
    for i, (_, row) in enumerate(top_properties.head(10).iterrows(), 1):
        address_short = row['Address'][:32] + "..." if len(row['Address']) > 35 else row['Address']
        city_short = row['City'][:12] + "..." if len(row['City']) > 15 else row['City']
        
        benefits = []
        if row['QCT']:
            benefits.append("QCT")
        if row['DDA']:
            benefits.append("DDA")
        benefits_str = "+".join(benefits)
        
        print(f"{i:<4} {address_short:<35} {city_short:<15} {row['Land Area (AC)']:<6.1f} ${row['Price Per AC Land']:<11,.0f} {benefits_str:<10} {row['Strategic_Score']:<5}")
    
    # Now try to import and run the enhanced analyzer
    print(f"\n🔧 INITIALIZING ENHANCED TEXAS ANALYZER...")
    
    try:
        from enhanced_texas_analyzer_st import EnhancedTexasAnalyzer
        print(f"✅ Successfully imported EnhancedTexasAnalyzer")
        
        # Your Census API key
        census_api_key = "06ece0121263282cd9ffd753215b007b8f9a3dfc"
        
        # Initialize the analyzer
        analyzer = EnhancedTexasAnalyzer(
            census_api_key=census_api_key,
            hud_ami_file_path=str(hud_ami_file) if hud_ami_file.exists() else None,
            tdhca_project_file_path=str(tdhca_file) if tdhca_file.exists() else None,
            work_dir=str(code_dir / "qct_dda_analysis")
        )
        print(f"✅ Enhanced Texas Analyzer initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing analyzer: {e}")
        print(f"   This might be due to missing dependencies or file paths")
        print(f"   You can still use the filtered strategic opportunities data")
        return False
    
    # Create addresses for analysis
    print(f"\n📍 PREPARING ADDRESSES FOR ANALYSIS...")
    
    top_properties['Full_Address'] = (
        top_properties['Address'].astype(str) + ', ' + 
        top_properties['City'].astype(str) + ', TX ' + 
        top_properties['Zip'].astype(str)
    )
    
    addresses = top_properties['Full_Address'].tolist()
    
    print(f"✅ Prepared {len(addresses)} addresses for comprehensive analysis")
    
    # Show first few addresses
    print(f"\nFirst 3 addresses to analyze:")
    for i, addr in enumerate(addresses[:3], 1):
        print(f"   {i}. {addr}")
    
    # Ask user if they want to proceed with full analysis
    print(f"\n🤔 READY TO RUN COMPREHENSIVE ANALYSIS")
    print(f"   This will take approximately 30-60 minutes for {len(addresses)} properties")
    print(f"   Each property will be analyzed for:")
    print(f"   • Demographics and poverty rates")
    print(f"   • Competition analysis")
    print(f"   • HUD AMI data and rent limits")
    print(f"   • 4% Bond deal scoring (0-5 points)")
    print(f"   • Federal benefits verification")
    
    return {
        'ready_for_analysis': True,
        'top_properties': top_properties,
        'addresses': addresses,
        'analyzer': analyzer,
        'total_strategic_properties': len(top_properties)
    }

if __name__ == "__main__":
    result = main()
    
    if result and result.get('ready_for_analysis'):
        print(f"\n🚀 EVERYTHING IS READY!")
        print(f"   Run the comprehensive analysis? This will analyze all {result['total_strategic_properties']} properties.")
        print(f"   You can type 'yes' to continue or 'no' to review the strategic filtering first.")
    else:
        print(f"\n❌ Setup incomplete. Please check the error messages above.")
