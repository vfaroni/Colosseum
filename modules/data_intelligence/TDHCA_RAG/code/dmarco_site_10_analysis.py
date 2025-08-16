#!/usr/bin/env python3

import pandas as pd
import json

def analyze_dmarco_site_10():
    """Analyze data quality issues specifically affecting D'Marco site 10"""
    
    # Load environmental database
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG"
    env_database = f"{base_dir}/D'Marco_Sites/Comprehensive_Environmental_Database.csv"
    
    print("🎯 ANALYZING D'MARCO SITE 10 ENVIRONMENTAL RISKS")
    print("=" * 55)
    
    env_df = pd.read_csv(env_database, low_memory=False)
    
    # Find all sites within 1 mile of D'Marco site 10
    site_10_risks = env_df[env_df['dmarco_site_10_within_1_mile'] == True].copy()
    
    print(f"📊 Sites within 1 mile of D'Marco Site 10: {len(site_10_risks)}")
    
    # Check for data quality issues in these sites
    problematic_sites = []
    
    for idx, site in site_10_risks.iterrows():
        issues = []
        
        # Check address quality
        address = str(site['address'])
        if pd.isna(site['address']) or address == 'nan' or 'nan' in address.lower():
            issues.append('nan_address')
        
        # Check geocoding confidence
        if site['geocoding_confidence'] < 0.8:
            issues.append('low_confidence')
            
        if issues:
            problematic_sites.append({
                'site_name': site['site_name'],
                'address': address,
                'dataset': site['dataset'],
                'distance_miles': site['dmarco_site_10_distance_miles'],
                'risk_level': site['dmarco_site_10_risk_level'],
                'geocoding_confidence': site['geocoding_confidence'],
                'issues': issues,
                'coordinates': f"{site['latitude']}, {site['longitude']}"
            })
    
    print(f"\n🚨 PROBLEMATIC SITES AFFECTING D'MARCO SITE 10:")
    print(f"   Total problematic sites: {len(problematic_sites)}")
    
    for i, site in enumerate(problematic_sites, 1):
        print(f"\n   {i}. {site['site_name']}")
        print(f"      Address: {site['address']}")
        print(f"      Dataset: {site['dataset']}")
        print(f"      Distance: {site['distance_miles']:.3f} miles")
        print(f"      Risk Level: {site['risk_level']}")
        print(f"      Geocoding Confidence: {site['geocoding_confidence']}")
        print(f"      Coordinates: {site['coordinates']}")
        print(f"      Issues: {', '.join(site['issues'])}")
    
    # Show all valid sites for comparison
    valid_sites = site_10_risks[~site_10_risks.index.isin([idx for idx, site in site_10_risks.iterrows() 
                                                          if pd.isna(site['address']) or 'nan' in str(site['address']).lower()])]
    
    print(f"\n✅ VALID SITES AFFECTING D'MARCO SITE 10:")
    print(f"   Total valid sites: {len(valid_sites)}")
    
    for idx, site in valid_sites.iterrows():
        print(f"   • {site['site_name']}")
        print(f"     Address: {site['address']}")
        print(f"     Distance: {site['dmarco_site_10_distance_miles']:.3f} miles")
        print(f"     Risk Level: {site['dmarco_site_10_risk_level']}")
    
    # Calculate impact
    total_sites = len(site_10_risks)
    bad_sites = len(problematic_sites)
    
    print(f"\n📈 IMPACT SUMMARY:")
    print(f"   • Total sites within 1 mile: {total_sites}")
    print(f"   • Problematic sites: {bad_sites}")
    print(f"   • Valid sites: {total_sites - bad_sites}")
    print(f"   • Percentage problematic: {(bad_sites/total_sites)*100:.1f}%")
    
    if problematic_sites:
        print(f"\n🔧 RECOMMENDATION:")
        print(f"   • Exclude {bad_sites} problematic site(s) from risk analysis")
        print(f"   • Re-calculate D'Marco Site 10 risk level with {total_sites - bad_sites} valid sites only")
        print(f"   • Update environmental maps to exclude sites with 'nan' addresses")

if __name__ == "__main__":
    analyze_dmarco_site_10()