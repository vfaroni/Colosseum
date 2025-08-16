#!/usr/bin/env python3
"""
Ultra-Conservative Hazard Processor
Executes flood elimination per user requirement: "delete the sites that have any flood designation"
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))
from multi_source_fire_analyzer import MultiSourceFireAnalyzer
from multi_source_flood_analyzer import MultiSourceFloodAnalyzer

def execute_ultra_conservative_processing():
    """Execute ultra-conservative processing on full dataset"""
    
    print("🏛️ ULTRA-CONSERVATIVE HAZARD PROCESSOR")
    print("Executing flood elimination per user requirement")
    print("=" * 60)
    
    dataset_path = "CostarExport_HighResource_BACKUP_20250730_090645.xlsx"
    
    # Load dataset
    df = pd.read_excel(dataset_path)
    sites_with_coords = df[df[['Latitude', 'Longitude']].notna().all(axis=1)].copy()
    
    print(f"📊 Dataset: {len(df)} total sites")
    print(f"📍 Processable: {len(sites_with_coords)} sites with coordinates")
    
    # Initialize analyzers
    fire_analyzer = MultiSourceFireAnalyzer()
    flood_analyzer = MultiSourceFloodAnalyzer()
    
    # Results tracking
    results = []
    eliminated_flood = 0
    eliminated_fire = 0
    safe_sites = 0
    manual_verification = 0
    
    print(f"\n⚡ Processing {len(sites_with_coords)} sites...")
    
    for idx, (_, row) in enumerate(sites_with_coords.iterrows()):
        if (idx + 1) % 25 == 0 or idx == 0:
            print(f"📊 Progress: {idx+1}/{len(sites_with_coords)}")
        
        site_address = row.get('Property Address', 'Unknown')
        lat, lng = row['Latitude'], row['Longitude']
        
        try:
            # Fire analysis
            fire_result = fire_analyzer.analyze_fire_risk_comprehensive(lat, lng, site_address)
            
            # Flood analysis with existing data
            existing_flood = {
                'In SFHA': row.get('In SFHA'),
                'Flood Risk Area': row.get('Flood Risk Area'),
                'Fema Flood Zone': row.get('Fema Flood Zone')
            }
            flood_result = flood_analyzer.analyze_flood_risk_comprehensive(
                lat, lng, existing_flood, site_address
            )
            
            # Ultra-conservative decision logic
            fire_eliminate = fire_result.get('meets_criteria') is False
            flood_eliminate = flood_result.get('meets_flood_criteria') is False
            
            fire_manual = fire_result.get('manual_verification_required', False)
            flood_manual = flood_result.get('requires_verification', False)
            
            # Status determination
            if flood_eliminate:
                status = "ELIMINATED_FLOOD"
                eliminated_flood += 1
            elif fire_eliminate:
                status = "ELIMINATED_FIRE"
                eliminated_fire += 1
            elif fire_manual or flood_manual:
                status = "MANUAL_VERIFICATION"
                manual_verification += 1
            else:
                status = "SAFE"
                safe_sites += 1
            
            # Create result record
            result = {
                'Property Address': site_address,
                'Latitude': lat,
                'Longitude': lng,
                'Status': status,
                'Fire_Hazard': fire_result.get('hazard_class', 'Unknown'),
                'Fire_Source': fire_result.get('data_source', 'Unknown'),
                'Flood_Risk': flood_result.get('flood_risk_level', 'Unknown'),
                'Flood_Zone': flood_result.get('fema_flood_zone', 'Unknown'),
                'SFHA_Status': flood_result.get('sfha_status', 'Unknown'),
                'Elimination_Reason': flood_result.get('elimination_reason') or 
                                    (f"Fire hazard: {fire_result.get('hazard_class')}" if fire_eliminate else None)
            }
            
            # Copy original data
            for col in df.columns:
                if col not in result:
                    result[col] = row.get(col)
            
            results.append(result)
            
        except Exception as e:
            print(f"❌ Error processing {site_address}: {e}")
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Generate results
    print("\n" + "=" * 60)
    print("🎯 ULTRA-CONSERVATIVE PROCESSING RESULTS")
    print("=" * 60)
    
    total = len(results)
    print(f"✅ Safe sites: {safe_sites} ({safe_sites/total*100:.1f}%)")
    print(f"🌊 Eliminated (flood): {eliminated_flood} ({eliminated_flood/total*100:.1f}%)")
    print(f"🔥 Eliminated (fire): {eliminated_fire} ({eliminated_fire/total*100:.1f}%)")
    print(f"⚠️  Manual verification: {manual_verification} ({manual_verification/total*100:.1f}%)")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Complete results
    complete_file = f"COLOSSEUM_COMPLETE_RESULTS_{timestamp}.xlsx"
    results_df.to_excel(complete_file, index=False)
    print(f"\n📄 Complete results: {complete_file}")
    
    # Safe sites only (final portfolio)
    safe_df = results_df[results_df['Status'] == 'SAFE']
    safe_file = f"COLOSSEUM_SAFE_PORTFOLIO_{timestamp}.xlsx"
    safe_df.to_excel(safe_file, index=False)
    print(f"✅ Safe portfolio: {safe_file} ({len(safe_df)} sites)")
    
    # Eliminated sites
    eliminated_df = results_df[results_df['Status'].str.contains('ELIMINATED')]
    eliminated_file = f"COLOSSEUM_ELIMINATED_SITES_{timestamp}.xlsx"
    eliminated_df.to_excel(eliminated_file, index=False)
    print(f"🚨 Eliminated sites: {eliminated_file} ({len(eliminated_df)} sites)")
    
    # Show sample results
    if len(safe_df) > 0:
        print(f"\n✅ SAMPLE SAFE SITES ({len(safe_df)} total):")
        for _, site in safe_df.head(5).iterrows():
            addr = site['Property Address'][:50]
            fire = site['Fire_Hazard']
            flood = site['Flood_Risk']
            print(f"   • {addr} - Fire: {fire}, Flood: {flood}")
    
    if len(eliminated_df) > 0:
        print(f"\n🚨 SAMPLE ELIMINATED SITES ({len(eliminated_df)} total):")
        for _, site in eliminated_df.head(5).iterrows():
            addr = site['Property Address'][:50]
            reason = site['Elimination_Reason'][:60] if site['Elimination_Reason'] else 'Unknown'
            print(f"   • {addr} - {reason}")
    
    print(f"\n🏛️ Ultra-conservative processing complete!")
    print(f"Sites with ANY flood designation have been eliminated per user requirement")
    
    return results_df

if __name__ == "__main__":
    execute_ultra_conservative_processing()