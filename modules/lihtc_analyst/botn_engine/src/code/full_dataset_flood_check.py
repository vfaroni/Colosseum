#!/usr/bin/env python3
"""
Full Dataset Flood Check
Check ALL 630 sites (not just those with coordinates) for flood designations
"""

import pandas as pd
from datetime import datetime

def check_full_dataset_flood_status():
    """Check flood status across the complete 630-site dataset"""
    
    print("🌊 FULL DATASET FLOOD STATUS CHECK")
    print("Analyzing ALL 630 sites for flood designations")
    print("=" * 55)
    
    # Load complete dataset
    dataset_path = "CostarExport_HighResource_BACKUP_20250730_090645.xlsx"
    df = pd.read_excel(dataset_path)
    
    print(f"📊 Complete dataset: {len(df)} sites")
    
    # Analyze flood status across ALL sites
    flood_indicators = ['A', 'AE', 'AH', 'AO', 'AR', 'A99', 'V', 'VE', 'B', 'C', 'X', 'D', 'SFHA']
    
    sites_with_coords = 0
    sites_without_coords = 0
    safe_with_coords = 0
    safe_without_coords = 0
    eliminated_with_coords = 0
    eliminated_without_coords = 0
    
    safe_sites = []
    eliminated_sites = []
    
    print("\n⚡ Analyzing flood status for all sites...")
    
    for idx, (_, row) in enumerate(df.iterrows()):
        site_address = row.get('Property Address', 'Unknown')
        has_coordinates = pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude'))
        
        # Count coordinate status
        if has_coordinates:
            sites_with_coords += 1
        else:
            sites_without_coords += 1
        
        # Check flood designations
        sfha_status = str(row.get('In SFHA', '')).upper()
        flood_risk_area = str(row.get('Flood Risk Area', ''))
        fema_flood_zone = str(row.get('Fema Flood Zone', ''))
        
        # Determine flood elimination status
        has_sfha = sfha_status == 'YES'
        has_flood_zone = any(indicator in fema_flood_zone.upper() for indicator in flood_indicators)
        has_flood_area = 'Risk' in flood_risk_area
        
        should_eliminate = has_sfha or has_flood_zone or has_flood_area
        
        if should_eliminate:
            # Site eliminated due to flood designation
            if has_coordinates:
                eliminated_with_coords += 1
            else:
                eliminated_without_coords += 1
            
            elimination_reasons = []
            if has_sfha:
                elimination_reasons.append(f"SFHA: {sfha_status}")
            if has_flood_zone:
                elimination_reasons.append(f"Zone: {fema_flood_zone}")
            if has_flood_area:
                elimination_reasons.append(f"Area: {flood_risk_area}")
            
            row_dict = row.to_dict()
            row_dict['Has_Coordinates'] = 'Yes' if has_coordinates else 'No'
            row_dict['Elimination_Reason'] = "; ".join(elimination_reasons)
            row_dict['Status'] = 'ELIMINATED_FLOOD'
            eliminated_sites.append(row_dict)
        else:
            # Site safe from flood designation
            if has_coordinates:
                safe_with_coords += 1
            else:
                safe_without_coords += 1
            
            row_dict = row.to_dict()
            row_dict['Has_Coordinates'] = 'Yes' if has_coordinates else 'No'
            row_dict['Status'] = 'SAFE_NO_FLOOD'
            safe_sites.append(row_dict)
    
    # Results summary
    print("\n" + "=" * 55)
    print("🎯 COMPLETE DATASET FLOOD ANALYSIS")
    print("=" * 55)
    
    total_sites = len(df)
    total_safe = len(safe_sites)
    total_eliminated = len(eliminated_sites)
    
    print(f"📊 OVERALL RESULTS:")
    print(f"   Total sites: {total_sites}")
    print(f"   ✅ Safe (no flood designation): {total_safe} ({total_safe/total_sites*100:.1f}%)")
    print(f"   🌊 Eliminated (flood designation): {total_eliminated} ({total_eliminated/total_sites*100:.1f}%)")
    
    print(f"\n📍 COORDINATE BREAKDOWN:")
    print(f"   Sites with coordinates: {sites_with_coords}")
    print(f"   Sites without coordinates: {sites_without_coords}")
    
    print(f"\n✅ SAFE SITES BREAKDOWN:")
    print(f"   Safe with coordinates: {safe_with_coords}")
    print(f"   Safe without coordinates: {safe_without_coords}")
    print(f"   Total safe: {total_safe}")
    
    print(f"\n🌊 ELIMINATED SITES BREAKDOWN:")
    print(f"   Eliminated with coordinates: {eliminated_with_coords}")
    print(f"   Eliminated without coordinates: {eliminated_without_coords}")
    print(f"   Total eliminated: {total_eliminated}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if safe_sites:
        safe_df = pd.DataFrame(safe_sites)
        safe_file = f"COLOSSEUM_ALL_SAFE_SITES_{timestamp}.xlsx"
        safe_df.to_excel(safe_file, index=False)
        print(f"\n✅ All safe sites: {safe_file} ({len(safe_df)} sites)")
        
        # Show breakdown of safe sites
        safe_with_coords_df = safe_df[safe_df['Has_Coordinates'] == 'Yes']
        safe_without_coords_df = safe_df[safe_df['Has_Coordinates'] == 'No']
        
        if len(safe_with_coords_df) > 0:
            coords_file = f"COLOSSEUM_SAFE_WITH_COORDINATES_{timestamp}.xlsx"
            safe_with_coords_df.to_excel(coords_file, index=False)
            print(f"   ✅ Safe with coordinates: {coords_file} ({len(safe_with_coords_df)} sites)")
    
    if eliminated_sites:
        eliminated_df = pd.DataFrame(eliminated_sites)
        eliminated_file = f"COLOSSEUM_ALL_ELIMINATED_{timestamp}.xlsx"
        eliminated_df.to_excel(eliminated_file, index=False)
        print(f"\n🌊 All eliminated sites: {eliminated_file} ({len(eliminated_df)} sites)")
    
    # Show samples
    if safe_sites:
        print(f"\n✅ SAMPLE SAFE SITES (no flood designation):")
        for i, site in enumerate(safe_sites[:5]):
            addr = site['Property Address'][:45]
            coords = site['Has_Coordinates']
            print(f"   {i+1}. {addr} (Coords: {coords})")
    
    print(f"\n🏛️ Complete dataset flood analysis finished!")
    
    return safe_df if safe_sites else None, eliminated_df if eliminated_sites else None

if __name__ == "__main__":
    check_full_dataset_flood_status()