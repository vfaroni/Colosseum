#!/usr/bin/env python3
"""
Re-score the Tyler site and other corrected sites with proper coordinates and QCT/DDA data
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Add the parent directory to path so we can import our wrapper
sys.path.append('/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/pyforma_integration/projects/TX_land_analysis')
from pyforma_wrapper import PyformaWrapper

def load_corrected_geocoding_data():
    """Load the geocoded sites with corrected coordinates and QCT/DDA status"""
    
    geocoded_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/pyforma_integration/projects/TX_land_analysis/outputs/geocoded_sites_results.csv"
    
    try:
        df = pd.read_csv(geocoded_file)
        print(f"✅ Loaded {len(df)} geocoded sites")
        
        # Filter to successfully geocoded sites
        successful = df[df['status'] == 'success'].copy()
        print(f"✅ {len(successful)} sites successfully geocoded")
        
        return successful
    except Exception as e:
        print(f"❌ Error loading geocoded data: {e}")
        return None

def load_original_195_sites():
    """Load the original 195 sites dataset"""
    
    try:
        # Load from the original Excel file mentioned in analyze_all_195_sites.py
        excel_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/FINAL_195_Sites_Complete_With_Poverty_20250621_213537.xlsx"
        
        # Try reading different sheet names that might exist
        try:
            df = pd.read_excel(excel_file, sheet_name='All_195_Sites_Final')
        except:
            try:
                df = pd.read_excel(excel_file, sheet_name=0)  # First sheet
            except:
                # List available sheets
                xl = pd.ExcelFile(excel_file)
                print(f"Available sheets: {xl.sheet_names}")
                df = pd.read_excel(excel_file, sheet_name=xl.sheet_names[0])
        
        print(f"✅ Loaded original dataset: {len(df)} sites")
        return df
    except Exception as e:
        print(f"❌ Error loading original data: {e}")
        return None

def merge_corrected_data(original_df, geocoded_df):
    """Merge corrected geocoding data back into original dataset"""
    
    print(f"📊 Merging corrected data...")
    
    # Create a copy of original data
    updated_df = original_df.copy()
    
    # Create mapping from original_index to corrected data
    corrections = {}
    for _, row in geocoded_df.iterrows():
        orig_idx = row['original_index']
        corrections[orig_idx] = {
            'latitude': row.get('latitude'),
            'longitude': row.get('longitude'),
            'corrected_county': row.get('county'),
            'qct_status': row.get('qct_status'),
            'dda_status': row.get('dda_status'),
            'basis_boost_eligible': row.get('basis_boost_eligible', False)
        }
    
    # Apply corrections to original data
    corrected_sites = []
    for orig_idx, corrections_data in corrections.items():
        if orig_idx < len(updated_df):
            # Update the row with corrected data
            updated_df.loc[orig_idx, 'Corrected_Latitude'] = corrections_data['latitude']
            updated_df.loc[orig_idx, 'Corrected_Longitude'] = corrections_data['longitude']
            updated_df.loc[orig_idx, 'Corrected_County'] = corrections_data['corrected_county']
            updated_df.loc[orig_idx, 'Corrected_QCT_Status'] = corrections_data['qct_status']
            updated_df.loc[orig_idx, 'Corrected_DDA_Status'] = corrections_data['dda_status']
            updated_df.loc[orig_idx, 'Corrected_Basis_Boost'] = corrections_data['basis_boost_eligible']
            updated_df.loc[orig_idx, 'Data_Correction_Applied'] = True
            
            corrected_sites.append(orig_idx)
    
    print(f"✅ Applied corrections to {len(corrected_sites)} sites")
    
    return updated_df, corrected_sites

def rescore_corrected_sites(updated_df, corrected_indices):
    """Re-run pyforma analysis on corrected sites"""
    
    print(f"🔄 Re-scoring {len(corrected_indices)} corrected sites...")
    
    # Initialize wrapper
    wrapper = PyformaWrapper()
    
    results = []
    
    for i, orig_idx in enumerate(corrected_indices):
        site = updated_df.loc[orig_idx]
        
        print(f"  📊 Re-scoring site {i+1}/{len(corrected_indices)}: {site.get('Address', 'Unknown')}")
        
        try:
            # Create enhanced site data with corrections
            enhanced_site = site.copy()
            
            # If we have corrected coordinates, use them
            if not pd.isna(site.get('Corrected_Latitude')):
                enhanced_site['Latitude'] = site['Corrected_Latitude']
                enhanced_site['Longitude'] = site['Corrected_Longitude']
                
            # If we have corrected county, use it
            if not pd.isna(site.get('Corrected_County')):
                enhanced_site['County'] = site['Corrected_County']
            
            # Add QCT/DDA status
            enhanced_site['Federal_Basis_Boost_30pct'] = site.get('Corrected_Basis_Boost', False)
            enhanced_site['QCT_Status'] = site.get('Corrected_QCT_Status', 'Not QCT')
            enhanced_site['DDA_Status'] = site.get('Corrected_DDA_Status', 'Not DDA')
            
            # Re-analyze with corrected data
            result = wrapper.analyze_texas_site(enhanced_site)
            
            # Add tracking information
            result.update({
                'original_index': orig_idx,
                'correction_applied': True,
                'original_county': site.get('County', 'NONE'),
                'corrected_county': site.get('Corrected_County'),
                'original_ranking_9pct': site.get('Final_9pct_Ranking_With_Poverty', site.get('Ranking_9pct', 'Unknown')),
                'qct_dda_status': f"{site.get('Corrected_QCT_Status', 'Unknown')} / {site.get('Corrected_DDA_Status', 'Unknown')}",
                'basis_boost_eligible': site.get('Corrected_Basis_Boost', False)
            })
            
            results.append(result)
            
        except Exception as e:
            print(f"    ❌ Error re-scoring site {orig_idx}: {e}")
            results.append({
                'original_index': orig_idx,
                'site_address': site.get('Address', 'Unknown'),
                'error': str(e),
                'correction_applied': True
            })
    
    return pd.DataFrame(results)

def generate_tyler_comparison(results_df):
    """Generate specific comparison for Tyler site"""
    
    tyler_results = results_df[results_df['site_address'].str.contains('2505 Walton', na=False)]
    
    if len(tyler_results) > 0:
        tyler = tyler_results.iloc[0]
        
        print(f"\n" + "="*60)
        print(f"🎯 TYLER SITE COMPARISON REPORT")
        print(f"="*60)
        print(f"Address: {tyler.get('site_address', 'Unknown')}")
        print(f"Original County: {tyler.get('original_county', 'NONE')}")
        print(f"Corrected County: {tyler.get('corrected_county', 'Unknown')}")
        print(f"QCT/DDA Status: {tyler.get('qct_dda_status', 'Unknown')}")
        print(f"Basis Boost Eligible: {tyler.get('basis_boost_eligible', 'Unknown')}")
        print(f"")
        print(f"FINANCIAL ANALYSIS:")
        print(f"  Revenue/Cost Ratio: {tyler.get('revenue_cost_ratio', 0):.4f}")
        print(f"  Total Revenue: ${tyler.get('total_revenue', 0):,.0f}")
        print(f"  Total Cost: ${tyler.get('total_cost', 0):,.0f}")
        print(f"  Profit: ${tyler.get('profit', 0):,.0f}")
        print(f"")
        print(f"RANKING CHANGE:")
        print(f"  Original 9% Ranking: {tyler.get('original_ranking_9pct', 'Unknown')}")
        print(f"  New Pyforma Category: {tyler.get('pyforma_category', 'Unknown')}")
        print(f"="*60)
        
        return tyler
    else:
        print(f"⚠️ Tyler site not found in results")
        return None

def save_corrected_results(results_df, updated_df):
    """Save the corrected and re-scored results"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/pyforma_integration/projects/TX_land_analysis/outputs"
    
    # Corrected analysis results
    results_file = f"{output_dir}/Corrected_Sites_Analysis_{timestamp}.xlsx"
    
    with pd.ExcelWriter(results_file, engine='openpyxl') as writer:
        # Re-scored sites
        results_df.to_excel(writer, sheet_name='Corrected_Analysis', index=False)
        
        # Tyler specific results
        tyler_results = results_df[results_df['site_address'].str.contains('2505 Walton', na=False)]
        if len(tyler_results) > 0:
            tyler_results.to_excel(writer, sheet_name='Tyler_Site_Analysis', index=False)
        
        # All corrected sites from original dataset
        corrected_original = updated_df[updated_df.get('Data_Correction_Applied', False) == True]
        if len(corrected_original) > 0:
            corrected_original.to_excel(writer, sheet_name='Updated_Original_Data', index=False)
    
    print(f"💾 Results saved to: {results_file}")
    return results_file

def main():
    """Main execution"""
    
    print("🚀 RE-SCORING CORRECTED TEXAS SITES")
    print("=" * 60)
    
    # Load corrected geocoding data
    geocoded_df = load_corrected_geocoding_data()
    if geocoded_df is None:
        return
    
    # Load original dataset
    original_df = load_original_195_sites()
    if original_df is None:
        return
    
    # Merge corrections
    updated_df, corrected_indices = merge_corrected_data(original_df, geocoded_df)
    
    # Re-score corrected sites
    results_df = rescore_corrected_sites(updated_df, corrected_indices)
    
    # Generate Tyler comparison
    tyler_result = generate_tyler_comparison(results_df)
    
    # Save results
    output_file = save_corrected_results(results_df, updated_df)
    
    # Summary
    print(f"\n" + "="*60)
    print(f"📊 CORRECTION SUMMARY")
    print(f"  Sites corrected: {len(corrected_indices)}")
    print(f"  Sites re-scored: {len(results_df)}")
    print(f"  Tyler site status: {'✅ Found and analyzed' if tyler_result is not None else '❌ Not found'}")
    print(f"  Output file: {os.path.basename(output_file)}")
    print(f"🚀 Ready for investment analysis!")

if __name__ == "__main__":
    main()