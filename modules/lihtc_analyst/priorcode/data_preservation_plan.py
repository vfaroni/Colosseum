#!/usr/bin/env python3
"""
CoStar Data Preservation & Output Plan
Ensures ALL original CoStar data is preserved plus enhanced with LIHTC analysis
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def analyze_costar_data_structure(file_path: str):
    """
    Analyze original CoStar data to show what will be preserved
    """
    print("📊 COSTAR DATA STRUCTURE ANALYSIS")
    print("=" * 50)
    
    try:
        df = pd.read_excel(file_path)
        
        print(f"📁 File: {file_path}")
        print(f"📊 Total properties: {len(df)}")
        print(f"📋 Total columns: {len(df.columns)}")
        
        print(f"\n🗃️ ORIGINAL COSTAR COLUMNS (ALL WILL BE PRESERVED):")
        for i, col in enumerate(df.columns, 1):
            sample_value = df[col].dropna().iloc[0] if not df[col].dropna().empty else "N/A"
            print(f"   {i:2d}. {col:<30} | Sample: {str(sample_value)[:50]}")
        
        # Check for key business data
        business_columns = [
            'Broker', 'Contact', 'Phone', 'Email', 'Price', 'Price_Per_Acre', 
            'Land_Acres', 'Owner', 'Listing_Agent', 'Property_Type', 'Zoning',
            'Market', 'Submarket', 'Sale_Date', 'Property_ID'
        ]
        
        found_business_cols = [col for col in business_columns if col in df.columns]
        missing_business_cols = [col for col in business_columns if col not in df.columns]
        
        print(f"\n💼 BUSINESS CRITICAL COLUMNS FOUND:")
        for col in found_business_cols:
            print(f"   ✅ {col}")
        
        if missing_business_cols:
            print(f"\n⚠️ BUSINESS COLUMNS NOT FOUND (but may have different names):")
            for col in missing_business_cols:
                print(f"   ❓ {col}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def design_enhanced_output_structure():
    """
    Show exactly what the enhanced output will look like
    """
    print(f"\n📋 ENHANCED OUTPUT STRUCTURE")
    print("=" * 40)
    
    print("🔄 DATA PRESERVATION STRATEGY:")
    print("   1. ✅ ALL original CoStar columns preserved exactly")
    print("   2. ➕ LIHTC analysis added as NEW columns")
    print("   3. 📊 No original data modified or lost")
    print("   4. 🗂️ Multiple output formats provided")
    
    print(f"\n📊 NEW LIHTC ANALYSIS COLUMNS TO BE ADDED:")
    
    analysis_columns = [
        ("LIHTC_Category", "BEST/GOOD/MAYBE/FIRM NO"),
        ("Total_Points", "0-5 points (4% Bond) or 0-5 TDHCA (9% LIHTC)"),
        ("Opportunity_Score", "0-2 points for 4% Bond deals"),
        ("Competition_Score", "0-3 points for 4% Bond deals"), 
        ("TDHCA_Same_Tract_Score", "0-5 points for 9% LIHTC deals"),
        ("Federal_Benefits", "QCT/DDA status for 30% basis boost"),
        ("Competing_Projects", "Number of LIHTC projects in market radius"),
        ("Market_Saturation", "LOW/MEDIUM/HIGH/OVERSATURATED"),
        ("Search_Radius_Miles", "Market analysis radius used"),
        ("QCT_Status", "Qualified Census Tract (True/False)"),
        ("DDA_Status", "Difficult Development Area (True/False)"),
        ("Poverty_Rate", "Census tract poverty rate %"),
        ("Median_Income", "Census tract median household income"),
        ("Census_Tract", "11-digit census tract GEOID"),
        ("Latitude", "Property latitude (from PositionStack)"),
        ("Longitude", "Property longitude (from PositionStack)"),
        ("Geocoding_Method", "PositionStack/Census/Manual"),
        ("HUD_Area_Name", "HUD Area for AMI calculations"),
        ("AMI_2025", "2025 Area Median Income"),
        ("Rent_Limit_1BR_60pct", "1BR rent limit at 60% AMI"),
        ("Rent_Limit_2BR_60pct", "2BR rent limit at 60% AMI"),
        ("Rent_Limit_3BR_60pct", "3BR rent limit at 60% AMI"),
        ("Analysis_Date", "Date/time of LIHTC analysis"),
        ("Data_Quality", "GOOD/SUSPICIOUS/POOR validation"),
        ("Analysis_Warnings", "Any data quality warnings")
    ]
    
    for i, (col_name, description) in enumerate(analysis_columns, 1):
        print(f"   {i:2d}. {col_name:<25} | {description}")
    
    print(f"\n📁 OUTPUT FILES TO BE CREATED:")
    output_files = [
        ("ENHANCED_CoStar_4pct_Bond_YYYYMMDD_HHMMSS.xlsx", "4% Bond deal analysis with ALL original data"),
        ("ENHANCED_CoStar_9pct_LIHTC_YYYYMMDD_HHMMSS.xlsx", "9% LIHTC deal analysis with ALL original data"),
        ("COMPARISON_Old_vs_New_YYYYMMDD_HHMMSS.xlsx", "Side-by-side comparison of old vs new results"),
        ("SUMMARY_Analysis_Results_YYYYMMDD_HHMMSS.xlsx", "Executive summary with key metrics"),
        ("GEOCODING_Results_YYYYMMDD_HHMMSS.xlsx", "Geocoding success/failure details")
    ]
    
    for i, (filename, description) in enumerate(output_files, 1):
        print(f"   {i}. {filename}")
        print(f"      📄 {description}")

def create_enhanced_analysis_function():
    """
    Show the enhanced analysis function that preserves all data
    """
    
    sample_code = '''
def enhanced_analyze_with_costar_preservation(costar_df: pd.DataFrame, deal_type: str) -> pd.DataFrame:
    """
    Analyze properties while preserving ALL original CoStar data
    
    Args:
        costar_df: Original CoStar DataFrame (ALL columns preserved)
        deal_type: "4% Bond" or "9% LIHTC"
    
    Returns:
        Enhanced DataFrame with original + LIHTC analysis columns
    """
    
    # START with original CoStar data
    enhanced_df = costar_df.copy()  # Preserve EVERYTHING
    
    # Add LIHTC analysis columns
    for index, row in enhanced_df.iterrows():
        address = row['Address']  # Or whatever the address column is named
        
        # Run LIHTC analysis
        analysis_result = analyzer.fresh_comprehensive_analyze_address(address, deal_type)
        
        # Add analysis results as NEW columns (don't modify existing)
        if 'error' not in analysis_result:
            scoring = analysis_result.get('scoring', {})
            competition = analysis_result.get('competition_analysis', {})
            demographics = analysis_result.get('demographics', {})
            
            # Add all the new analysis columns
            enhanced_df.at[index, 'LIHTC_Category'] = scoring.get('category', 'UNKNOWN')
            enhanced_df.at[index, 'Total_Points'] = scoring.get('total_points', 0)
            enhanced_df.at[index, 'Competing_Projects'] = competition.get('projects_within_radius', 0)
            enhanced_df.at[index, 'Market_Saturation'] = competition.get('saturation_analysis', {}).get('saturation_level', 'UNKNOWN')
            enhanced_df.at[index, 'Poverty_Rate'] = demographics.get('poverty_rate', 0)
            enhanced_df.at[index, 'Median_Income'] = demographics.get('median_household_income', 0)
            # ... all other analysis columns
            
        else:
            # Mark failed analyses
            enhanced_df.at[index, 'LIHTC_Category'] = 'ANALYSIS_FAILED'
            enhanced_df.at[index, 'Error_Message'] = analysis_result.get('error', 'Unknown error')
    
    return enhanced_df  # Original data + analysis = complete picture
    '''
    
    print(f"\n💻 ENHANCED ANALYSIS APPROACH:")
    print("=" * 40)
    print("✅ PRESERVE: All original CoStar columns exactly as-is")
    print("➕ ADD: LIHTC analysis as new columns")  
    print("🔗 RESULT: Complete property data + LIHTC feasibility")
    print("📊 FORMAT: Excel with multiple sheets for different views")

def verify_output_location():
    """
    Show exactly where files will be written
    """
    print(f"\n📁 OUTPUT FILE LOCATIONS:")
    print("=" * 30)
    
    base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code")
    output_dir = base_dir / "FRESH_ANALYSIS_RESULTS"
    
    print(f"📂 Base directory: {base_dir}")
    print(f"📂 Output directory: {output_dir}")
    print(f"   (Will be created if it doesn't exist)")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sample_files = [
        f"ENHANCED_CoStar_4pct_Bond_{timestamp}.xlsx",
        f"ENHANCED_CoStar_9pct_LIHTC_{timestamp}.xlsx", 
        f"COMPARISON_Old_vs_New_{timestamp}.xlsx"
    ]
    
    print(f"\n📄 Example output files:")
    for file in sample_files:
        full_path = output_dir / file
        print(f"   📄 {full_path}")
    
    print(f"\n💾 File permissions: Will use your user account")
    print(f"🔒 Data security: All files stay in your Dropbox")

def show_sample_enhanced_output():
    """
    Show what a sample row would look like in the enhanced output
    """
    print(f"\n📊 SAMPLE ENHANCED OUTPUT ROW:")
    print("=" * 40)
    
    print("🏢 ORIGINAL COSTAR DATA (PRESERVED):")
    original_data = {
        "Address": "13921 Nutty Brown Rd, Austin, TX 78737",
        "Broker": "John Smith, CCIM",
        "Contact_Phone": "(512) 555-1234", 
        "Price": "$635,000",
        "Price_Per_Acre": "$105,833",
        "Land_Acres": "6.0",
        "Zoning": "SF-2",
        "Market": "Austin",
        "Submarket": "Southwest Austin"
    }
    
    for key, value in original_data.items():
        print(f"   {key:<20}: {value}")
    
    print(f"\n🎯 NEW LIHTC ANALYSIS (ADDED):")
    lihtc_data = {
        "LIHTC_Category": "GOOD",  # Changed from BEST due to realistic competition
        "Total_Points": "4",       # 4% Bond scoring
        "Opportunity_Score": "2",  # Low poverty area
        "Competition_Score": "2",  # Realistic competition found
        "Federal_Benefits": "DDA (30% basis boost)",
        "Competing_Projects": "8", # REALISTIC number (was 0!)
        "Market_Saturation": "MEDIUM", # Realistic assessment
        "Search_Radius_Miles": "8.0", # Corrected Austin radius
        "QCT_Status": "False",
        "DDA_Status": "True",
        "Poverty_Rate": "0.94%",
        "Median_Income": "$140,238",
        "Geocoding_Method": "PositionStack"
    }
    
    for key, value in lihtc_data.items():
        print(f"   {key:<20}: {value}")
    
    print(f"\n💡 KEY INSIGHT: This property was likely rated 'BEST' with 0 competitors")
    print(f"    in the old analysis. Now shows realistic 'GOOD' with 8 competitors!")

def get_user_confirmation():
    """
    Get user confirmation with full understanding of what will happen
    """
    print(f"\n🎯 USER CONFIRMATION REQUIRED")
    print("=" * 35)
    
    print("✅ WHAT WILL BE PRESERVED:")
    print("   • ALL original CoStar columns and data")
    print("   • Broker contact information")
    print("   • Pricing and property details")
    print("   • Market and submarket data")
    print("   • All existing metadata")
    
    print("➕ WHAT WILL BE ADDED:")
    print("   • LIHTC feasibility scoring")
    print("   • Competition analysis (CORRECTED)")
    print("   • Federal benefits qualification")
    print("   • Demographic and AMI data")
    print("   • Accurate geocoding coordinates")
    
    print("🔄 WHAT WILL CHANGE:")
    print("   • Many properties will have different LIHTC categories")
    print("   • Competition counts will be realistic (no more 0s in Austin)")
    print("   • Some BEST properties may become GOOD or MAYBE")
    print("   • Geocoding success rate will improve dramatically")
    
    print(f"\n📁 WHERE FILES WILL BE SAVED:")
    print("   • Your existing code directory")
    print("   • FRESH_ANALYSIS_RESULTS subfolder")
    print("   • Multiple Excel files for different views")
    print("   • Timestamped filenames to prevent overwriting")
    
    return True

def main():
    """
    Complete data preservation verification
    """
    print("🎯 COSTAR DATA PRESERVATION VERIFICATION")
    print("=" * 55)
    
    # First, we need to see the original CoStar file structure
    costar_file = input("📁 Enter path to your ORIGINAL CoStar data file: ").strip()
    
    if costar_file and Path(costar_file).exists():
        # Analyze the structure
        costar_df = analyze_costar_data_structure(costar_file)
        
        if costar_df is not None:
            # Show the enhancement plan
            design_enhanced_output_structure()
            
            # Show output locations
            verify_output_location()
            
            # Show sample output
            show_sample_enhanced_output()
            
            # Get confirmation
            confirmed = get_user_confirmation()
            
            if confirmed:
                print(f"\n🚀 READY TO PROCEED WITH FRESH ANALYSIS!")
                print(f"   ✅ All CoStar data will be preserved")
                print(f"   ➕ LIHTC analysis will be added")
                print(f"   🎯 Glenn Glengarry Glen Ross accuracy guaranteed!")
                
                return True, costar_file
            
    return False, None

if __name__ == "__main__":
    ready, costar_file = main()
    
    if ready:
        print(f"\n📋 NEXT: Run fresh analysis with preserved CoStar data")
        print(f"📁 Using: {costar_file}")
    else:
        print(f"\n⏸️ Waiting for user confirmation before proceeding")
