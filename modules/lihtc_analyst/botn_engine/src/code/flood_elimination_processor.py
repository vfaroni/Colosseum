#!/usr/bin/env python3
"""
Flood Elimination Processor
Executes user requirement: "delete the sites that have any flood designation"
"""

import pandas as pd
from datetime import datetime

def eliminate_flood_sites():
    """Execute flood site elimination per user requirement"""
    
    print("🌊 FLOOD SITE ELIMINATION PROCESSOR")
    print("User requirement: Delete sites with ANY flood designation")
    print("=" * 50)
    
    # Load dataset
    dataset_path = "CostarExport_HighResource_BACKUP_20250730_090645.xlsx"
    df = pd.read_excel(dataset_path)
    
    print(f"📊 Original dataset: {len(df)} sites")
    
    # Filter to sites with coordinates
    sites_with_coords = df[df[['Latitude', 'Longitude']].notna().all(axis=1)].copy()
    print(f"📍 Sites with coordinates: {len(sites_with_coords)} sites")
    
    # Ultra-conservative flood elimination criteria
    flood_indicators = ['A', 'AE', 'AH', 'AO', 'AR', 'A99', 'V', 'VE', 'B', 'C', 'X', 'D', 'SFHA']
    
    eliminated_sites = []
    safe_sites = []
    
    print("\n⚡ Processing flood eliminations...")
    
    for idx, (_, row) in enumerate(sites_with_coords.iterrows()):
        site_address = row.get('Property Address', 'Unknown')
        
        # Check existing flood data
        sfha_status = str(row.get('In SFHA', '')).upper()
        flood_risk_area = str(row.get('Flood Risk Area', ''))
        fema_flood_zone = str(row.get('Fema Flood Zone', ''))
        
        # Determine if site has ANY flood designation
        has_sfha = sfha_status == 'YES'
        has_flood_zone = any(indicator in fema_flood_zone.upper() for indicator in flood_indicators)
        has_flood_area = 'Risk' in flood_risk_area
        
        should_eliminate = has_sfha or has_flood_zone or has_flood_area
        
        if should_eliminate:
            elimination_reasons = []
            if has_sfha:
                elimination_reasons.append(f"SFHA: {sfha_status}")
            if has_flood_zone:
                elimination_reasons.append(f"Flood Zone: {fema_flood_zone}")
            if has_flood_area:
                elimination_reasons.append(f"Flood Area: {flood_risk_area}")
            
            row_dict = row.to_dict()
            row_dict['Elimination_Reason'] = "; ".join(elimination_reasons)
            row_dict['Status'] = 'ELIMINATED_FLOOD'
            eliminated_sites.append(row_dict)
        else:
            row_dict = row.to_dict()
            row_dict['Status'] = 'SAFE_NO_FLOOD'
            safe_sites.append(row_dict)
    
    # Results
    print("\n" + "=" * 50)
    print("🎯 FLOOD ELIMINATION RESULTS")
    print("=" * 50)
    
    total_processed = len(sites_with_coords)
    eliminated_count = len(eliminated_sites)
    safe_count = len(safe_sites)
    
    print(f"🌊 Sites eliminated (flood designation): {eliminated_count} ({eliminated_count/total_processed*100:.1f}%)")
    print(f"✅ Sites safe (no flood designation): {safe_count} ({safe_count/total_processed*100:.1f}%)")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Safe sites (final portfolio)
    if safe_sites:
        safe_df = pd.DataFrame(safe_sites)
        safe_file = f"COLOSSEUM_NO_FLOOD_SITES_{timestamp}.xlsx"
        safe_df.to_excel(safe_file, index=False)
        print(f"\n✅ Safe sites (no flood): {safe_file} ({len(safe_df)} sites)")
    
    # Eliminated sites
    if eliminated_sites:
        eliminated_df = pd.DataFrame(eliminated_sites)
        eliminated_file = f"COLOSSEUM_ELIMINATED_FLOOD_{timestamp}.xlsx"
        eliminated_df.to_excel(eliminated_file, index=False)
        print(f"🌊 Eliminated sites: {eliminated_file} ({len(eliminated_df)} sites)")
    
    # Show samples
    if safe_sites:
        print(f"\n✅ SAMPLE SAFE SITES (no flood designation):")
        for i, site in enumerate(safe_sites[:5]):
            addr = site['Property Address'][:50]
            print(f"   {i+1}. {addr}")
    
    if eliminated_sites:
        print(f"\n🌊 SAMPLE ELIMINATED SITES (had flood designation):")
        for i, site in enumerate(eliminated_sites[:5]):
            addr = site['Property Address'][:50]
            reason = site['Elimination_Reason'][:50]
            print(f"   {i+1}. {addr} - {reason}")
    
    print(f"\n🏛️ Flood elimination complete!")
    print(f"All sites with ANY flood designation have been eliminated per user requirement")
    
    return safe_df if safe_sites else None, eliminated_df if eliminated_sites else None

if __name__ == "__main__":
    eliminate_flood_sites()