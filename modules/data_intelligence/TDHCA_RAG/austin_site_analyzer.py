#!/usr/bin/env python3
"""
Austin Site Risk Analyzer
Identify which of our 117 sites are in Austin MSA rent cliff areas
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def analyze_austin_sites():
    """Analyze our 117 sites for Austin MSA rent cliff risk"""
    
    base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
    
    # Load our latest site analysis
    phase2_file = base_dir / "D'Marco_Sites/Analysis_Results/PHASE2_FINAL_Environmental_Screened_20250731_234408.xlsx"
    
    print("🎯 AUSTIN SITE RENT CLIFF ANALYSIS")
    print("🚨 Identifying sites in Austin MSA outer areas")
    print("=" * 60)
    
    try:
        # Load our 117 sites
        sites_df = pd.read_excel(phase2_file, sheet_name='Phase2_Complete_Analysis')
        print(f"✅ Loaded {len(sites_df)} sites for Austin analysis")
        
        # Filter for Austin MSA sites
        austin_indicators = ['austin', 'travis', 'williamson', 'hays', 'caldwell']
        
        austin_sites = []
        for idx, site in sites_df.iterrows():
            site_text = str(site.get('Address', '')) + ' ' + str(site.get('City', '')) + ' ' + str(site.get('County', ''))
            
            if any(indicator in site_text.lower() for indicator in austin_indicators):
                # Estimate distance from downtown Austin (rough geographic analysis)
                lat = site.get('Latitude', 0)
                lon = site.get('Longitude', 0)
                
                # Austin downtown approximate coordinates: 30.2672, -97.7431
                downtown_austin_lat = 30.2672
                downtown_austin_lon = -97.7431
                
                # Simple distance approximation
                lat_diff = abs(lat - downtown_austin_lat)
                lon_diff = abs(lon - downtown_austin_lon)
                rough_distance = ((lat_diff ** 2) + (lon_diff ** 2)) ** 0.5 * 69  # Miles approximation
                
                # Classify submarket based on location
                if rough_distance < 10:
                    submarket = 'Central Austin'
                    rent_risk = 'HIGH_RENTS'
                    viability = 'TOO_EXPENSIVE'
                elif rough_distance < 20:
                    submarket = 'Inner Austin MSA'
                    rent_risk = 'VIABLE'
                    viability = 'GOOD'
                elif rough_distance < 35:
                    submarket = 'Outer Austin MSA'
                    rent_risk = 'RENT_CLIFF_RISK'
                    viability = 'HIGH_RISK'
                else:
                    submarket = 'Far Austin MSA'
                    rent_risk = 'RENT_CLIFF_CERTAIN'
                    viability = 'ELIMINATE'
                
                austin_site = {
                    'site_index': idx,
                    'address': site.get('Address', 'Unknown'),
                    'city': site.get('City', 'Unknown'),
                    'county': site.get('County', 'Unknown'),
                    'latitude': lat,
                    'longitude': lon,
                    'distance_from_downtown': round(rough_distance, 1),
                    'estimated_submarket': submarket,
                    'rent_risk_level': rent_risk,
                    'lihtc_viability': viability,
                    'qct_dda_status': site.get('FINAL_METRO_QCT', 'Unknown'),
                    'competition_score': site.get('Competition_Score', 0),
                    'final_phase2_score': site.get('Final_Phase2_Score', 0)
                }
                austin_sites.append(austin_site)
        
        print(f"🏙️ Found {len(austin_sites)} sites in Austin MSA")
        
        if austin_sites:
            austin_df = pd.DataFrame(austin_sites)
            
            # Analyze risk distribution
            risk_distribution = austin_df['rent_risk_level'].value_counts()
            viability_distribution = austin_df['lihtc_viability'].value_counts()
            
            print(f"\n📊 AUSTIN MSA SITE DISTRIBUTION:")
            for risk, count in risk_distribution.items():
                print(f"   {risk}: {count} sites")
            
            print(f"\n⚠️ VIABILITY ASSESSMENT:")  
            for viability, count in viability_distribution.items():
                print(f"   {viability}: {count} sites")
            
            # Identify high-risk sites
            high_risk_sites = austin_df[austin_df['rent_risk_level'].isin(['RENT_CLIFF_RISK', 'RENT_CLIFF_CERTAIN'])]
            
            if len(high_risk_sites) > 0:
                print(f"\n🚨 HIGH RENT CLIFF RISK SITES ({len(high_risk_sites)}):")
                for _, site in high_risk_sites.iterrows():
                    print(f"   {site['address']} - {site['distance_from_downtown']} mi from downtown - {site['rent_risk_level']}")
            
            # Save analysis
            results_dir = base_dir / "D'Marco_Sites/Analysis_Results"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            excel_file = results_dir / f"Austin_Site_Rent_Risk_Analysis_{timestamp}.xlsx"
            austin_df.to_excel(excel_file, index=False)
            
            # Summary
            analysis_summary = {
                'analysis_date': timestamp,
                'total_austin_sites': len(austin_sites),
                'risk_distribution': risk_distribution.to_dict(),
                'viability_distribution': viability_distribution.to_dict(),
                'high_risk_sites': len(high_risk_sites),
                'recommendations': {
                    'eliminate': len(austin_df[austin_df['lihtc_viability'] == 'ELIMINATE']),
                    'high_risk_review': len(austin_df[austin_df['lihtc_viability'] == 'HIGH_RISK']),
                    'viable_sites': len(austin_df[austin_df['lihtc_viability'] == 'GOOD'])
                }
            }
            
            json_file = results_dir / f"Austin_Rent_Risk_Summary_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(analysis_summary, f, indent=2)
            
            print(f"\n💾 Austin analysis saved:")
            print(f"   📊 Excel: {excel_file.name}")
            print(f"   📋 Summary: {json_file.name}")
            
            return austin_df, analysis_summary
            
        else:
            print("ℹ️ No sites found in Austin MSA")
            return None, None
            
    except Exception as e:
        print(f"❌ Failed to analyze Austin sites: {e}")
        return None, None

if __name__ == "__main__":
    austin_df, summary = analyze_austin_sites()
    
    if summary:
        print(f"\n🎯 AUSTIN MSA RENT CLIFF SUMMARY:")
        print(f"   Total Austin Sites: {summary['total_austin_sites']}")
        print(f"   High Risk Sites: {summary['high_risk_sites']}")
        print(f"   Sites to Eliminate: {summary['recommendations']['eliminate']}")
        print(f"   Sites Needing Review: {summary['recommendations']['high_risk_review']}")
        print(f"   Viable Sites: {summary['recommendations']['viable_sites']}")
        
        print(f"\n✅ Austin rent cliff analysis complete - integrate with master analysis")