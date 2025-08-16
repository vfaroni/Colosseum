#!/usr/bin/env python3
"""
Batch Hazard Processor for VITOR-WINGMAN-HAZARD-001
Processes all 630 sites with validation-first approach
"""

import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import time
from datetime import datetime
import logging

# Import our analyzers
sys.path.append(str(Path(__file__).parent))
from enhanced_fire_hazard_analyzer import EnhancedFireHazardAnalyzer
from enhanced_flood_analyzer import EnhancedFloodAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_sites_with_validation(dataset_path: str, max_sites: int = 10):
    """
    Process sites with comprehensive validation
    
    Args:
        dataset_path: Path to Excel dataset
        max_sites: Maximum sites to process (for testing)
    """
    print("🏛️ COLOSSEUM BATCH HAZARD PROCESSOR")
    print("Mission: VITOR-WINGMAN-HAZARD-001")
    print("=" * 60)
    
    # Load dataset
    print("📂 Loading dataset...")
    df = pd.read_excel(dataset_path)
    print(f"✅ Loaded {len(df)} total sites")
    
    # Filter to sites with coordinates
    sites_with_coords = df[df[['Latitude', 'Longitude']].notna().all(axis=1)].copy()
    print(f"📍 Found {len(sites_with_coords)} sites with coordinates")
    
    if max_sites:
        sites_with_coords = sites_with_coords.head(max_sites)
        print(f"🧪 Testing mode: Processing first {max_sites} sites")
    
    # Initialize analyzers
    fire_analyzer = EnhancedFireHazardAnalyzer()
    flood_analyzer = EnhancedFloodAnalyzer()
    
    # Process sites
    results = []
    eliminated_sites = []
    verification_sites = []
    
    print(f"\n⚡ Processing {len(sites_with_coords)} sites...")
    
    for idx, (_, row) in enumerate(sites_with_coords.iterrows()):
        print(f"📊 Progress: {idx+1}/{len(sites_with_coords)}")
        
        site_address = row.get('Property Address', 'Unknown')
        lat, lng = row['Latitude'], row['Longitude']
        
        try:
            # Fire analysis
            fire_result = fire_analyzer.analyze_fire_risk_enhanced(lat, lng, site_address)
            
            # Flood analysis
            existing_flood = {
                'In SFHA': row.get('In SFHA'),
                'Flood Risk Area': row.get('Flood Risk Area'),
                'Fema Flood Zone': row.get('Fema Flood Zone')
            }
            flood_result = flood_analyzer.analyze_flood_risk_comprehensive(
                lat, lng, existing_flood, site_address
            )
            
            # Combine results
            site_result = {
                'site_address': site_address,
                'coordinates': f"{lat:.6f}, {lng:.6f}",
                'county': row.get('County Name', 'Unknown'),
                'fire_hazard_class': fire_result.get('hazard_class', 'Unknown'),
                'fire_meets_criteria': fire_result.get('meets_criteria'),
                'flood_risk_level': flood_result.get('flood_risk_level', 'Unknown'),
                'flood_meets_criteria': flood_result.get('meets_flood_criteria'),
                'sfha_status': flood_result.get('sfha_status', 'Unknown'),
            }
            
            # Elimination decision
            should_eliminate = (
                fire_result.get('meets_criteria') is False or
                flood_result.get('meets_flood_criteria') is False
            )
            
            needs_verification = (
                fire_result.get('manual_verification_required', False) or
                flood_result.get('requires_verification', False) or
                fire_result.get('meets_criteria') is None or
                flood_result.get('meets_flood_criteria') is None
            )
            
            if should_eliminate:
                site_result['recommendation'] = 'ELIMINATE'
                eliminated_sites.append(site_result)
                print(f"  🚨 ELIMINATE: {site_address[:40]} - High risk")
            elif needs_verification:
                site_result['recommendation'] = 'VERIFY'
                verification_sites.append(site_result)
                print(f"  ⚠️  VERIFY: {site_address[:40]} - Manual check needed")
            else:
                site_result['recommendation'] = 'KEEP'
                print(f"  ✅ KEEP: {site_address[:40]} - Safe")
            
            results.append(site_result)
            
        except Exception as e:
            print(f"  ❌ ERROR: {site_address[:40]} - {e}")
            results.append({
                'site_address': site_address,
                'error': str(e),
                'recommendation': 'ERROR'
            })
    
    # Generate summary
    print("\n" + "=" * 60)
    print("🎯 PROCESSING COMPLETE")
    print("=" * 60)
    
    safe_sites = len([r for r in results if r.get('recommendation') == 'KEEP'])
    print(f"✅ Safe sites: {safe_sites}")
    print(f"🚨 Eliminated sites: {len(eliminated_sites)}")
    print(f"⚠️  Manual verification: {len(verification_sites)}")
    print(f"📊 Elimination rate: {len(eliminated_sites)/len(results)*100:.1f}%")
    
    # Save results
    output_dir = Path("hazard_analysis_outputs")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save safe sites
    if safe_sites > 0:
        safe_df = pd.DataFrame([r for r in results if r.get('recommendation') == 'KEEP'])
        safe_file = output_dir / f'SAFE_SITES_{timestamp}.xlsx'
        safe_df.to_excel(safe_file, index=False)
        print(f"💾 Safe sites saved: {safe_file}")
    
    # Save eliminated sites
    if eliminated_sites:
        elim_df = pd.DataFrame(eliminated_sites)
        elim_file = output_dir / f'ELIMINATED_SITES_{timestamp}.xlsx'
        elim_df.to_excel(elim_file, index=False)
        print(f"💾 Eliminated sites saved: {elim_file}")
    
    # Save verification sites
    if verification_sites:
        verify_df = pd.DataFrame(verification_sites)
        verify_file = output_dir / f'VERIFICATION_SITES_{timestamp}.xlsx'
        verify_df.to_excel(verify_file, index=False)
        print(f"💾 Verification sites saved: {verify_file}")
    
    print("\n🏛️ Victoria Per Data - 'Victory Through Data' 🏛️")
    
    return results

def main():
    """Main execution function"""
    dataset_path = "CostarExport_HighResource_BACKUP_20250730_090645.xlsx"
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found: {dataset_path}")
        return
    
    # Process with testing limit first
    results = process_sites_with_validation(dataset_path, max_sites=20)
    return results

if __name__ == "__main__":
    main()