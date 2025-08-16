#!/usr/bin/env python3
"""
Final Corrected Flood Elimination Processor
Updated criteria per user feedback:

ELIMINATE:
- Properties with SFHA = "Yes" 
- Special Flood Hazard Areas: Zone A, V, AV99, AE, AO, AH, VE, AR
- Flood Risk Area = "High Risk Areas" (NEW ADDITION)

KEEP:
- Properties with SFHA = "No" or blank/null
- Zone X and Zone D (acceptable)
- Flood Risk Area = "Moderate to Low Risk Areas" or "Undetermined Risk Areas"
"""

import pandas as pd
from datetime import datetime

def final_corrected_flood_elimination():
    """Apply final corrected flood elimination including Flood Risk Area column"""
    
    print("🌊 FINAL CORRECTED FLOOD ELIMINATION PROCESSOR")
    print("Updated with Flood Risk Area elimination criteria")
    print("=" * 65)
    
    # Load original dataset
    dataset_path = "CostarExport_HighResource_BACKUP_20250730_090645.xlsx"
    df = pd.read_excel(dataset_path)
    
    print(f"📊 Original dataset: {len(df)} sites")
    
    # Focus on sites with coordinates
    sites_with_coords = df[df[['Latitude', 'Longitude']].notna().all(axis=1)].copy()
    print(f"📍 Sites with coordinates: {len(sites_with_coords)} sites")
    
    # Define elimination criteria
    high_risk_zones = ['A', 'V', 'AV99', 'AE', 'AO', 'AH', 'VE', 'AR']
    
    print(f"\n🚨 ELIMINATION CRITERIA:")
    print(f"   - SFHA = 'Yes' (Special Flood Hazard Area)")
    print(f"   - High-risk zones: {', '.join(high_risk_zones)}")
    print(f"   - Flood Risk Area = 'High Risk Areas' (NEW)")
    print(f"\n✅ ACCEPTABLE CRITERIA:")
    print(f"   - SFHA = 'No' or blank/null")
    print(f"   - Acceptable zones: X, D (and descriptive text)")
    print(f"   - Flood Risk Area = 'Moderate to Low Risk Areas' or 'Undetermined Risk Areas'")
    
    # Process sites
    eliminated_sites = []
    safe_sites = []
    
    print(f"\n⚡ Processing sites with updated criteria...")
    
    for idx, (_, row) in enumerate(sites_with_coords.iterrows()):
        site_address = row.get('Property Address', 'Unknown')
        
        # Get flood data
        sfha_status = row.get('In SFHA')
        flood_risk_area = row.get('Flood Risk Area', '')
        fema_flood_zone = row.get('Fema Flood Zone', '')
        
        # Convert to strings for analysis
        sfha_str = str(sfha_status).strip() if pd.notna(sfha_status) else ""
        flood_zone_str = str(fema_flood_zone).strip() if pd.notna(fema_flood_zone) else ""
        flood_risk_str = str(flood_risk_area).strip() if pd.notna(flood_risk_area) else ""
        
        # Determine elimination status
        should_eliminate = False
        elimination_reasons = []
        
        # Check SFHA status (eliminate if "Yes")
        if sfha_str.upper() == 'YES':
            should_eliminate = True
            elimination_reasons.append(f"SFHA: {sfha_str}")
        
        # Check for high-risk flood zones
        zone_found = None
        for zone in high_risk_zones:
            if (f" {zone} " in f" {flood_zone_str} " or 
                flood_zone_str.startswith(f"{zone} ") or 
                flood_zone_str.endswith(f" {zone}") or
                flood_zone_str == zone):
                zone_found = zone
                should_eliminate = True
                elimination_reasons.append(f"High-risk zone: {zone}")
                break
        
        # Check Flood Risk Area (NEW ADDITION)
        if flood_risk_str == 'High Risk Areas':
            should_eliminate = True
            elimination_reasons.append(f"Flood Risk Area: {flood_risk_str}")
        
        # Create result record
        row_dict = row.to_dict()
        row_dict['SFHA_Status_Clean'] = sfha_str
        row_dict['Flood_Zone_Clean'] = flood_zone_str
        row_dict['Flood_Risk_Area_Clean'] = flood_risk_str
        row_dict['Zone_Found'] = zone_found
        
        if should_eliminate:
            row_dict['Status'] = 'ELIMINATED_FLOOD'
            row_dict['Elimination_Reason'] = "; ".join(elimination_reasons)
            eliminated_sites.append(row_dict)
        else:
            row_dict['Status'] = 'SAFE_FLOOD'
            row_dict['Elimination_Reason'] = None
            safe_sites.append(row_dict)
    
    # Results summary
    print("\n" + "=" * 65)
    print("🎯 FINAL CORRECTED FLOOD ELIMINATION RESULTS")
    print("=" * 65)
    
    total_processed = len(sites_with_coords)
    eliminated_count = len(eliminated_sites)
    safe_count = len(safe_sites)
    
    print(f"📊 RESULTS:")
    print(f"   ✅ Safe sites: {safe_count} ({safe_count/total_processed*100:.1f}%)")
    print(f"   🚨 Eliminated sites: {eliminated_count} ({eliminated_count/total_processed*100:.1f}%)")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Safe sites (final corrected portfolio)
    if safe_sites:
        safe_df = pd.DataFrame(safe_sites)
        safe_file = f"COLOSSEUM_FINAL_SAFE_SITES_{timestamp}.xlsx"
        safe_df.to_excel(safe_file, index=False)
        print(f"\n✅ Final safe sites: {safe_file} ({len(safe_df)} sites)")
    
    # Eliminated sites
    if eliminated_sites:
        eliminated_df = pd.DataFrame(eliminated_sites)
        eliminated_file = f"COLOSSEUM_FINAL_ELIMINATED_{timestamp}.xlsx"
        eliminated_df.to_excel(eliminated_file, index=False)
        print(f"🚨 Final eliminated sites: {eliminated_file} ({len(eliminated_df)} sites)")
    
    # Analysis breakdown
    print(f"\n📊 ELIMINATION BREAKDOWN:")
    sfha_eliminations = sum(1 for site in eliminated_sites if 'SFHA:' in site.get('Elimination_Reason', ''))
    zone_eliminations = sum(1 for site in eliminated_sites if 'High-risk zone:' in site.get('Elimination_Reason', ''))
    risk_area_eliminations = sum(1 for site in eliminated_sites if 'Flood Risk Area:' in site.get('Elimination_Reason', ''))
    
    print(f"   SFHA = 'Yes' eliminations: {sfha_eliminations}")
    print(f"   High-risk zone eliminations: {zone_eliminations}")
    print(f"   High Risk Area eliminations: {risk_area_eliminations}")
    
    # Show breakdown of remaining flood risk areas
    if safe_sites:
        risk_area_breakdown = {}
        for site in safe_sites:
            risk_area = site['Flood_Risk_Area_Clean'] or 'blank'
            risk_area_breakdown[risk_area] = risk_area_breakdown.get(risk_area, 0) + 1
        
        print(f"\n📊 REMAINING FLOOD RISK AREA BREAKDOWN:")
        for risk_area, count in risk_area_breakdown.items():
            print(f"   '{risk_area}': {count} sites")
    
    # Show sample results
    if safe_sites:
        print(f"\n✅ SAMPLE SAFE SITES:")
        for i, site in enumerate(safe_sites[:5]):
            addr = site['Property Address'][:45]
            sfha = site['SFHA_Status_Clean'] or 'blank'
            risk_area = site['Flood_Risk_Area_Clean'] or 'blank'
            print(f"   {i+1}. {addr}")
            print(f"      SFHA: {sfha}, Risk Area: {risk_area}")
    
    if eliminated_sites:
        print(f"\n🚨 ELIMINATED SITES:")
        for i, site in enumerate(eliminated_sites):
            addr = site['Property Address'][:45]
            reason = site['Elimination_Reason']
            print(f"   {i+1}. {addr}")
            print(f"      Reason: {reason}")
    
    print(f"\n🏛️ Final corrected flood elimination complete!")
    print(f"Now properly excludes 'High Risk Areas' from Flood Risk Area column")
    
    return safe_df if safe_sites else None, eliminated_df if eliminated_sites else None

if __name__ == "__main__":
    final_corrected_flood_elimination()