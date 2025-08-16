#!/usr/bin/env python3
"""
Corrected Flood Elimination Processor
Uses proper SFHA criteria as specified by user:

ELIMINATE:
- Properties with SFHA = "Yes" 
- Special Flood Hazard Areas: Zone A, V, AV99, AE, AO, AH, VE, AR

KEEP:
- Properties with SFHA = "No"
- Properties with blank/null SFHA
- Zone X and Zone D (these are acceptable)
"""

import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

def corrected_flood_elimination():
    """Apply corrected flood elimination based on proper SFHA criteria"""
    
    print("🌊 CORRECTED FLOOD ELIMINATION PROCESSOR")
    print("Using proper SFHA criteria per user specification")
    print("=" * 60)
    
    # Load original dataset (clean copy)
    dataset_path = "CostarExport_HighResource_BACKUP_20250730_090645.xlsx"
    df = pd.read_excel(dataset_path)
    
    print(f"📊 Original dataset: {len(df)} sites")
    
    # Focus on sites with coordinates for analysis
    sites_with_coords = df[df[['Latitude', 'Longitude']].notna().all(axis=1)].copy()
    print(f"📍 Sites with coordinates: {len(sites_with_coords)} sites")
    
    # Define elimination criteria
    high_risk_zones = ['A', 'V', 'AV99', 'AE', 'AO', 'AH', 'VE', 'AR']
    acceptable_zones = ['X', 'D']  # These can be kept
    
    print(f"\n🚨 ELIMINATION CRITERIA:")
    print(f"   - SFHA = 'Yes' (Special Flood Hazard Area)")
    print(f"   - High-risk zones: {', '.join(high_risk_zones)}")
    print(f"\n✅ ACCEPTABLE CRITERIA:")
    print(f"   - SFHA = 'No' or blank/null")
    print(f"   - Acceptable zones: {', '.join(acceptable_zones)} (and descriptive text)")
    
    # Process sites
    eliminated_sites = []
    safe_sites = []
    
    print(f"\n⚡ Processing sites with corrected criteria...")
    
    for idx, (_, row) in enumerate(sites_with_coords.iterrows()):
        site_address = row.get('Property Address', 'Unknown')
        
        # Get flood data
        sfha_status = row.get('In SFHA')
        flood_risk_area = row.get('Flood Risk Area', '')
        fema_flood_zone = row.get('Fema Flood Zone', '')
        
        # Convert to strings for analysis
        sfha_str = str(sfha_status).strip() if pd.notna(sfha_status) else ""
        flood_zone_str = str(fema_flood_zone).strip() if pd.notna(fema_flood_zone) else ""
        
        # Determine elimination status
        should_eliminate = False
        elimination_reasons = []
        
        # Check SFHA status (eliminate if "Yes")
        if sfha_str.upper() == 'YES':
            should_eliminate = True
            elimination_reasons.append(f"SFHA: {sfha_str}")
        
        # Check for high-risk flood zones in the flood zone text
        zone_found = None
        for zone in high_risk_zones:
            # Look for exact zone matches (be careful not to match partial strings)
            if (f" {zone} " in f" {flood_zone_str} " or 
                flood_zone_str.startswith(f"{zone} ") or 
                flood_zone_str.endswith(f" {zone}") or
                flood_zone_str == zone):
                zone_found = zone
                should_eliminate = True
                elimination_reasons.append(f"High-risk zone: {zone}")
                break
        
        # Create result record
        row_dict = row.to_dict()
        row_dict['SFHA_Status_Clean'] = sfha_str
        row_dict['Flood_Zone_Clean'] = flood_zone_str
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
    print("\n" + "=" * 60)
    print("🎯 CORRECTED FLOOD ELIMINATION RESULTS")
    print("=" * 60)
    
    total_processed = len(sites_with_coords)
    eliminated_count = len(eliminated_sites)
    safe_count = len(safe_sites)
    
    print(f"📊 RESULTS:")
    print(f"   ✅ Safe sites (no SFHA/high-risk zones): {safe_count} ({safe_count/total_processed*100:.1f}%)")
    print(f"   🚨 Eliminated sites (SFHA/high-risk): {eliminated_count} ({eliminated_count/total_processed*100:.1f}%)")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Safe sites (corrected portfolio)
    if safe_sites:
        safe_df = pd.DataFrame(safe_sites)
        safe_file = f"COLOSSEUM_CORRECTED_SAFE_SITES_{timestamp}.xlsx"
        safe_df.to_excel(safe_file, index=False)
        print(f"\n✅ Corrected safe sites: {safe_file} ({len(safe_df)} sites)")
    
    # Eliminated sites
    if eliminated_sites:
        eliminated_df = pd.DataFrame(eliminated_sites)
        eliminated_file = f"COLOSSEUM_CORRECTED_ELIMINATED_{timestamp}.xlsx"
        eliminated_df.to_excel(eliminated_file, index=False)
        print(f"🚨 Eliminated sites: {eliminated_file} ({len(eliminated_df)} sites)")
    
    # Analysis breakdown
    print(f"\n📊 ELIMINATION BREAKDOWN:")
    sfha_eliminations = sum(1 for site in eliminated_sites if 'SFHA:' in site.get('Elimination_Reason', ''))
    zone_eliminations = sum(1 for site in eliminated_sites if 'High-risk zone:' in site.get('Elimination_Reason', ''))
    
    print(f"   SFHA = 'Yes' eliminations: {sfha_eliminations}")
    print(f"   High-risk zone eliminations: {zone_eliminations}")
    
    # Show sample results
    if safe_sites:
        print(f"\n✅ SAMPLE SAFE SITES:")
        for i, site in enumerate(safe_sites[:5]):
            addr = site['Property Address'][:45]
            sfha = site['SFHA_Status_Clean'] or 'blank'
            zone = site['Flood_Zone_Clean'][:50] if site['Flood_Zone_Clean'] else 'blank'
            print(f"   {i+1}. {addr}")
            print(f"      SFHA: {sfha}, Zone: {zone}")
    
    if eliminated_sites:
        print(f"\n🚨 SAMPLE ELIMINATED SITES:")
        for i, site in enumerate(eliminated_sites[:3]):
            addr = site['Property Address'][:45]
            reason = site['Elimination_Reason'][:60]
            print(f"   {i+1}. {addr}")
            print(f"      Reason: {reason}")
    
    print(f"\n🏛️ Corrected flood elimination complete!")
    print(f"Applied proper SFHA criteria - only eliminated true flood hazard areas")
    
    return safe_df if safe_sites else None, eliminated_df if eliminated_sites else None

def analyze_flood_zone_patterns():
    """Analyze the patterns in flood zone data to understand what we're working with"""
    
    print(f"\n🔍 ANALYZING FLOOD ZONE PATTERNS IN DATASET")
    print("=" * 50)
    
    dataset_path = "CostarExport_HighResource_BACKUP_20250730_090645.xlsx"
    df = pd.read_excel(dataset_path)
    sites_with_coords = df[df[['Latitude', 'Longitude']].notna().all(axis=1)].copy()
    
    # Analyze SFHA patterns
    sfha_counts = sites_with_coords['In SFHA'].value_counts(dropna=False)
    print(f"📊 SFHA Status Distribution:")
    for status, count in sfha_counts.items():
        print(f"   '{status}': {count} sites")
    
    # Analyze flood zone patterns
    print(f"\n📊 Flood Zone Patterns (first 10):")
    zone_counts = sites_with_coords['Fema Flood Zone'].value_counts(dropna=False)
    for zone, count in list(zone_counts.items())[:10]:
        zone_display = str(zone)[:60] + "..." if len(str(zone)) > 60 else str(zone)
        print(f"   {count} sites: '{zone_display}'")
    
    print(f"\n📊 Flood Risk Area Patterns:")
    risk_counts = sites_with_coords['Flood Risk Area'].value_counts(dropna=False)
    for risk, count in risk_counts.items():
        print(f"   '{risk}': {count} sites")

if __name__ == "__main__":
    # First analyze patterns
    analyze_flood_zone_patterns()
    
    # Then apply corrected elimination
    corrected_flood_elimination()