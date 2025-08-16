#!/usr/bin/env python3
"""
Create Final D'Marco Analysis Using Best Geocoding Results
Uses PositionStack coordinates where recommended for maximum accuracy
"""

import pandas as pd
from datetime import datetime
from tdhca_qct_focused_analyzer import TDHCAQCTFocusedAnalyzer
import logging

def create_final_dmarco_analysis():
    """Create the definitive D'Marco analysis using best geocoding"""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Load geocoding comparison results
    comparison_file = "Geocoding_Comparison_Report_20250618_234851.xlsx"
    df_comparison = pd.read_excel(comparison_file, sheet_name='Full_Comparison')
    
    logger.info(f"Loaded geocoding comparison for {len(df_comparison)} sites")
    
    # Initialize analyzer
    analyzer = TDHCAQCTFocusedAnalyzer()
    
    # Create final analysis with best coordinates
    final_results = []
    
    for _, row in df_comparison.iterrows():
        # Use best coordinates based on comparison
        if row['Best_Coordinates'] == 'PositionStack':
            lat = row['PS_Latitude']
            lng = row['PS_Longitude']
            geocoding_method = 'PositionStack'
            geocoding_confidence = row['PS_Confidence']
        else:
            lat = row['Nom_Latitude']
            lng = row['Nom_Longitude']  
            geocoding_method = 'Nominatim'
            geocoding_confidence = 1.0  # Nominatim doesn't provide confidence
        
        logger.info(f"Analyzing {row['MailingName']} using {geocoding_method} coordinates")
        
        # Create property data structure
        property_data = {
            'address': row['Address'],
            'city': row['City'],
            'county': row['County'],
            'lat': lat,
            'lng': lng,
            'flood_zone': 'X'  # Default, would need separate flood lookup
        }
        
        # Run full analysis with best coordinates
        site_analysis = analyzer.analyze_site(property_data, deal_type='4%')
        
        # Combine with original data
        final_result = {
            'MailingName': row['MailingName'],
            'Address': row['Address'], 
            'City': row['City'],
            'County': row['County'],
            'Region': row['Region'],
            'Acres': row['Acres'],
            
            # Best geocoding results
            'Latitude': lat,
            'Longitude': lng,
            'Geocoding_Method': geocoding_method,
            'Geocoding_Confidence': geocoding_confidence,
            
            # QCT/DDA Analysis  
            'QCT_Status': site_analysis['qct_dda_status']['in_qct'],
            'DDA_Status': site_analysis['qct_dda_status']['in_dda'],
            'QCT_DDA_Combined': site_analysis['qct_dda_status']['status'],
            'Basis_Boost_Eligible': site_analysis['basis_boost_eligible'],
            'Basis_Boost_Score': site_analysis['basis_boost_preference_score'],
            
            # Competition Analysis
            'One_Mile_Competition_Count': site_analysis['competition_analysis']['one_mile_count'],
            'One_Mile_Risk_4pct': site_analysis['competition_analysis']['one_mile_risk_level'],
            'One_Mile_Fatal_9pct': site_analysis['competition_analysis']['one_mile_fatal_flaw'],
            'Two_Mile_Competition': site_analysis['competition_analysis']['two_mile_same_year_count'],
            
            # Economic Factors
            'Flood_Cost_Impact': site_analysis['flood_cost_impact'],
            
            # Overall Assessment
            'Viable_For_Development': site_analysis['viable_for_development'],
            'Development_Recommendation': site_analysis['recommendation'],
            'Key_Advantages': '; '.join(site_analysis['development_advantages']),
            'Risk_Factors': '; '.join(site_analysis['development_risks']),
            
            # 4% vs 9% Analysis
            'Economic_Viability_4pct': 'Excellent' if site_analysis['basis_boost_eligible'] and site_analysis['competition_analysis']['one_mile_risk_level'] == 'Low' else
                                     'Good' if site_analysis['basis_boost_eligible'] and site_analysis['competition_analysis']['one_mile_risk_level'] == 'Medium' else
                                     'Fair' if site_analysis['basis_boost_eligible'] else 'Not Viable',
            
            'Economic_Viability_9pct': 'Not Viable - Fatal Flaw' if site_analysis['competition_analysis']['one_mile_fatal_flaw'] else
                                     'Viable' if site_analysis['basis_boost_eligible'] else 'Challenging'
        }
        
        final_results.append(final_result)
    
    # Convert to DataFrame
    df_final = pd.DataFrame(final_results)
    
    # Sort by viability
    viability_order = {'Excellent': 1, 'Good': 2, 'Fair': 3, 'Not Viable': 4}
    df_final['sort_order'] = df_final['Economic_Viability_4pct'].map(viability_order)
    df_final = df_final.sort_values(['Basis_Boost_Eligible', 'sort_order', 'One_Mile_Competition_Count'], ascending=[False, True, True])
    df_final = df_final.drop('sort_order', axis=1)
    
    # Save final results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"DMarco_Final_Analysis_PositionStack_{timestamp}.xlsx"
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Executive Summary
        qct_dda_count = len(df_final[df_final['Basis_Boost_Eligible'] == True])
        excellent_count = len(df_final[df_final['Economic_Viability_4pct'] == 'Excellent'])
        
        summary_data = {
            'Metric': [
                'Total D\'Marco Sites',
                'QCT/DDA Eligible (30% Boost)',
                'Non-QCT/DDA Sites',
                'Excellent 4% Opportunities',
                'Good 4% Opportunities',
                'Fair 4% Opportunities', 
                'Fatal Flaw 9% Sites',
                'PositionStack Geocoded',
                'Nominatim Geocoded'
            ],
            'Count': [
                len(df_final),
                qct_dda_count,
                len(df_final) - qct_dda_count,
                excellent_count,
                len(df_final[df_final['Economic_Viability_4pct'] == 'Good']),
                len(df_final[df_final['Economic_Viability_4pct'] == 'Fair']),
                len(df_final[df_final['One_Mile_Fatal_9pct'] == True]),
                len(df_final[df_final['Geocoding_Method'] == 'PositionStack']),
                len(df_final[df_final['Geocoding_Method'] == 'Nominatim'])
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Executive_Summary', index=False)
        
        # All sites with final analysis
        df_final.to_excel(writer, sheet_name='Final_Analysis_All_Sites', index=False)
        
        # QCT/DDA priority sites only
        qct_dda_sites = df_final[df_final['Basis_Boost_Eligible'] == True].copy()
        if len(qct_dda_sites) > 0:
            qct_dda_sites.to_excel(writer, sheet_name='QCT_DDA_Priority_Sites', index=False)
            
            # Best 4% opportunities
            excellent_sites = qct_dda_sites[qct_dda_sites['Economic_Viability_4pct'] == 'Excellent']
            if len(excellent_sites) > 0:
                excellent_sites.to_excel(writer, sheet_name='Top_4pct_Opportunities', index=False)
        
        # Regional breakdown
        regional_summary = df_final.groupby('Region').agg({
            'MailingName': 'count',
            'Basis_Boost_Eligible': 'sum',
            'Acres': ['mean', 'sum'],
            'Economic_Viability_4pct': lambda x: (x == 'Excellent').sum()
        }).round(2)
        regional_summary.columns = ['Total_Sites', 'QCT_DDA_Sites', 'Avg_Acres', 'Total_Acres', 'Excellent_4pct']
        regional_summary = regional_summary.sort_values('QCT_DDA_Sites', ascending=False)
        regional_summary.to_excel(writer, sheet_name='Regional_Summary')
        
        # Geocoding comparison results
        geocoding_summary = df_final.groupby('Geocoding_Method').agg({
            'MailingName': 'count',
            'Basis_Boost_Eligible': 'sum',
            'Economic_Viability_4pct': lambda x: (x == 'Excellent').sum()
        })
        geocoding_summary.columns = ['Total_Sites', 'QCT_DDA_Sites', 'Excellent_4pct']
        geocoding_summary.to_excel(writer, sheet_name='Geocoding_Method_Summary')
    
    logger.info(f"\n🎯 FINAL D'MARCO ANALYSIS COMPLETE:")
    logger.info(f"   Total sites: {len(df_final)}")
    logger.info(f"   QCT/DDA eligible: {qct_dda_count} ({qct_dda_count/len(df_final)*100:.1f}%)")
    logger.info(f"   Excellent 4% opportunities: {excellent_count}")
    logger.info(f"   PositionStack geocoded: {len(df_final[df_final['Geocoding_Method'] == 'PositionStack'])}")
    logger.info(f"\n💾 Final analysis saved to: {output_file}")
    
    return df_final, output_file

def print_final_summary(df_final):
    """Print final analysis summary"""
    qct_dda_sites = df_final[df_final['Basis_Boost_Eligible'] == True]
    
    print("="*80)
    print("D'MARCO FINAL ANALYSIS - USING BEST GEOCODING")
    print("="*80)
    
    print(f"\n🎯 FINAL RESULTS WITH IMPROVED GEOCODING:")
    print(f"   Total Sites: {len(df_final)}")
    print(f"   QCT/DDA Eligible: {len(qct_dda_sites)} ({len(qct_dda_sites)/len(df_final)*100:.1f}%)")
    print(f"   PositionStack Used: {len(df_final[df_final['Geocoding_Method'] == 'PositionStack'])}")
    print(f"   Nominatim Used: {len(df_final[df_final['Geocoding_Method'] == 'Nominatim'])}")
    
    if len(qct_dda_sites) > 0:
        print(f"\n🏆 TOP QCT/DDA OPPORTUNITIES:")
        excellent = qct_dda_sites[qct_dda_sites['Economic_Viability_4pct'] == 'Excellent']
        for _, site in excellent.head(10).iterrows():
            confidence = f" (PS: {site['Geocoding_Confidence']:.2f})" if site['Geocoding_Method'] == 'PositionStack' else ""
            print(f"   • {site['MailingName']} - {site['City']}, {site['County']} ({site['Acres']} ac, {site['QCT_DDA_Combined']}){confidence}")
        
        print(f"\n🗺️ REGIONAL LEADERS:")
        regional = qct_dda_sites.groupby('Region').size().sort_values(ascending=False)
        for region, count in regional.head(5).items():
            print(f"   {region}: {count} QCT/DDA sites")

if __name__ == "__main__":
    df_final, output_file = create_final_dmarco_analysis()
    print_final_summary(df_final)
    print(f"\n📁 Complete analysis with best geocoding: {output_file}")