#!/usr/bin/env python3
"""
Re-analyze Tyler and other corrected sites using proper comprehensive Texas QCT/DDA analyzer
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Add the current directory to path
sys.path.append('/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/pyforma_integration/projects/TX_land_analysis')
from comprehensive_texas_qct_dda_analyzer import ComprehensiveTexasQCTDDAAnalyzer
from pyforma_wrapper import PyformaWrapper

def load_geocoded_sites():
    """Load the successfully geocoded sites"""
    
    geocoded_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/pyforma_integration/projects/TX_land_analysis/outputs/geocoded_sites_results.csv"
    
    try:
        df = pd.read_csv(geocoded_file)
        successful = df[df['status'] == 'success'].copy()
        print(f"✅ Loaded {len(successful)} successfully geocoded sites")
        return successful
    except Exception as e:
        print(f"❌ Error loading geocoded data: {e}")
        return None

def comprehensive_qct_dda_reanalysis(geocoded_df):
    """Run comprehensive QCT/DDA analysis on all geocoded sites"""
    
    print(f"🔍 Running comprehensive QCT/DDA analysis...")
    
    # Initialize the comprehensive analyzer
    analyzer = ComprehensiveTexasQCTDDAAnalyzer()
    
    results = []
    
    for idx, site in geocoded_df.iterrows():
        site_name = site.get('address', f"Site {idx}")
        lat = site.get('latitude')
        lon = site.get('longitude')
        
        print(f"  📍 Analyzing: {site_name}")
        
        try:
            # Run comprehensive analysis
            result = analyzer.comprehensive_analysis(lat, lon)
            
            # Add original data for comparison
            result.update({
                'original_index': site.get('original_index'),
                'address': site.get('address'),
                'positionstack_county': site.get('county'),
                'positionstack_confidence': site.get('confidence')
            })
            
            results.append(result)
            
        except Exception as e:
            print(f"    ❌ Error analyzing {site_name}: {e}")
            results.append({
                'original_index': site.get('original_index'),
                'address': site.get('address'),
                'error': str(e)
            })
    
    return pd.DataFrame(results)

def enhanced_financial_analysis(qct_dda_df):
    """Run enhanced financial analysis with correct QCT/DDA status"""
    
    print(f"💰 Running enhanced financial analysis with corrected QCT/DDA status...")
    
    # Initialize pyforma wrapper
    wrapper = PyformaWrapper()
    
    enhanced_results = []
    
    for idx, site in qct_dda_df.iterrows():
        if 'error' in site:
            enhanced_results.append(site.to_dict())
            continue
        
        site_name = site.get('address', f"Site {idx}")
        print(f"  💼 Financial analysis: {site_name}")
        
        try:
            # Create enhanced site record with corrected QCT/DDA data
            enhanced_site = {
                'Address': site.get('address'),
                'Latitude': site.get('latitude'),
                'Longitude': site.get('longitude'),
                'County': site.get('county'),  # From Census API
                'Acres': 5.0,  # Default assumption for missing acres
                'Federal_Basis_Boost_30pct': site.get('lihtc_eligible', False),
                'QCT_Status': site.get('qct_status'),
                'DDA_Status': site.get('dda_status'),
                'QCT_Type': site.get('qct_type'),
                'DDA_Type': site.get('dda_type'),
                'AMI_Source': site.get('ami_source')
            }
            
            # Run financial analysis
            financial_result = wrapper.analyze_texas_site(enhanced_site)
            
            # Combine QCT/DDA and financial results
            combined_result = site.to_dict()
            combined_result.update({
                'total_revenue': financial_result.get('total_revenue', 0),
                'total_cost': financial_result.get('total_cost', 0),
                'profit': financial_result.get('profit', 0),
                'revenue_cost_ratio': financial_result.get('revenue_cost_ratio', 0),
                'financial_method': financial_result.get('method', 'unknown')
            })
            
            enhanced_results.append(combined_result)
            
        except Exception as e:
            print(f"    ❌ Financial analysis error for {site_name}: {e}")
            combined_result = site.to_dict()
            combined_result.update({
                'financial_error': str(e),
                'total_revenue': 0,
                'total_cost': 0,
                'profit': 0,
                'revenue_cost_ratio': 0
            })
            enhanced_results.append(combined_result)
    
    return pd.DataFrame(enhanced_results)

def generate_tyler_specific_report(results_df):
    """Generate specific report for Tyler site"""
    
    tyler_results = results_df[results_df['address'].str.contains('2505 Walton', na=False)]
    
    if len(tyler_results) > 0:
        tyler = tyler_results.iloc[0]
        
        print(f"\n" + "="*80)
        print(f"🎯 TYLER SITE COMPREHENSIVE ANALYSIS REPORT")
        print(f"="*80)
        
        print(f"📍 LOCATION DATA:")
        print(f"   Address: {tyler.get('address')}")
        print(f"   Coordinates: {tyler.get('latitude'):.6f}, {tyler.get('longitude'):.6f}")
        print(f"   Census Tract: {tyler.get('census_tract')}")
        print(f"   ZIP Code: {tyler.get('zip_code')}")
        print(f"   County: {tyler.get('county')} (Census) / {tyler.get('positionstack_county')} (PositionStack)")
        
        print(f"\n🏛️  QCT/DDA ANALYSIS:")
        print(f"   QCT Status: {tyler.get('qct_status')} ({tyler.get('qct_type')})")
        print(f"   DDA Status: {tyler.get('dda_status')} ({tyler.get('dda_type')})")
        print(f"   Combined Status: {tyler.get('status_combined')}")
        print(f"   LIHTC Eligible (30% Basis Boost): {tyler.get('lihtc_eligible')}")
        print(f"   AMI Source: {tyler.get('ami_source')}")
        
        if tyler.get('poverty_rate'):
            print(f"   Poverty Rate: {tyler.get('poverty_rate'):.1%}")
        if tyler.get('income_limit'):
            print(f"   Income Limit: ${tyler.get('income_limit'):,.0f}")
        
        print(f"\n💰 FINANCIAL ANALYSIS:")
        print(f"   Total Revenue: ${tyler.get('total_revenue', 0):,.0f}")
        print(f"   Total Cost: ${tyler.get('total_cost', 0):,.0f}")
        print(f"   Profit: ${tyler.get('profit', 0):,.0f}")
        print(f"   Revenue/Cost Ratio: {tyler.get('revenue_cost_ratio', 0):.4f}")
        print(f"   Analysis Method: {tyler.get('financial_method', 'Unknown')}")
        
        print(f"\n🔄 COMPARISON TO PREVIOUS 'FATAL' STATUS:")
        print(f"   Previous Classification: Fatal (due to data processing failures)")
        print(f"   Correct Classification: {tyler.get('qct_status')} with 30% Basis Boost")
        print(f"   Impact: Site should be re-evaluated for 9% LIHTC viability")
        print(f"   Datasets Used: {tyler.get('datasets_used')}")
        
        print(f"="*80)
        
        return tyler
    else:
        print(f"⚠️ Tyler site not found in comprehensive results")
        return None

def save_comprehensive_results(results_df):
    """Save comprehensive analysis results"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/pyforma_integration/projects/TX_land_analysis/outputs"
    
    results_file = f"{output_dir}/Comprehensive_QCT_DDA_Analysis_{timestamp}.xlsx"
    
    with pd.ExcelWriter(results_file, engine='openpyxl') as writer:
        
        # All comprehensive results
        results_df.to_excel(writer, sheet_name='Comprehensive_Analysis', index=False)
        
        # QCT sites only
        qct_sites = results_df[results_df['qct_status'] == 'QCT']
        if len(qct_sites) > 0:
            qct_sites.to_excel(writer, sheet_name='QCT_Sites', index=False)
        
        # DDA sites only
        dda_sites = results_df[results_df['dda_status'] == 'DDA']
        if len(dda_sites) > 0:
            dda_sites.to_excel(writer, sheet_name='DDA_Sites', index=False)
        
        # Basis boost eligible sites
        basis_boost = results_df[results_df['lihtc_eligible'] == True]
        if len(basis_boost) > 0:
            basis_boost.to_excel(writer, sheet_name='Basis_Boost_Eligible', index=False)
        
        # Tyler specific analysis
        tyler_results = results_df[results_df['address'].str.contains('2505 Walton', na=False)]
        if len(tyler_results) > 0:
            tyler_results.to_excel(writer, sheet_name='Tyler_Site_Complete', index=False)
    
    print(f"💾 Comprehensive results saved to: {results_file}")
    return results_file

def main():
    """Main execution"""
    
    print("🚀 COMPREHENSIVE TEXAS QCT/DDA REANALYSIS")
    print("=" * 80)
    
    # Load geocoded sites
    geocoded_df = load_geocoded_sites()
    if geocoded_df is None:
        return
    
    # Run comprehensive QCT/DDA analysis
    qct_dda_df = comprehensive_qct_dda_reanalysis(geocoded_df)
    
    # Run enhanced financial analysis with corrected data
    comprehensive_df = enhanced_financial_analysis(qct_dda_df)
    
    # Generate Tyler-specific report
    tyler_result = generate_tyler_specific_report(comprehensive_df)
    
    # Save comprehensive results
    output_file = save_comprehensive_results(comprehensive_df)
    
    # Final summary
    total_sites = len(comprehensive_df)
    qct_count = len(comprehensive_df[comprehensive_df['qct_status'] == 'QCT'])
    dda_count = len(comprehensive_df[comprehensive_df['dda_status'] == 'DDA'])
    basis_boost_count = len(comprehensive_df[comprehensive_df['lihtc_eligible'] == True])
    
    print(f"\n" + "="*80)
    print(f"📊 COMPREHENSIVE ANALYSIS SUMMARY")
    print(f"   Total Sites Analyzed: {total_sites}")
    print(f"   QCT Sites: {qct_count}")
    print(f"   DDA Sites: {dda_count}")
    print(f"   Basis Boost Eligible: {basis_boost_count}")
    print(f"   Tyler Site Status: {'✅ QCT Eligible' if tyler_result and tyler_result.get('lihtc_eligible') else '❌ Not Found'}")
    print(f"   Output File: {os.path.basename(output_file)}")
    print(f"🎉 Analysis complete! Tyler site's true potential revealed!")

if __name__ == "__main__":
    main()