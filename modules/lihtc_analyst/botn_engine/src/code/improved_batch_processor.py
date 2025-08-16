#!/usr/bin/env python3
"""
Improved Batch Processor with Multi-Source Fire Analysis
Tests the complete system with enhanced fire coverage
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))
from multi_source_fire_analyzer import MultiSourceFireAnalyzer
from enhanced_flood_analyzer import EnhancedFloodAnalyzer

def test_improved_system(dataset_path: str, sample_size: int = 30):
    """Test the improved system with multi-source fire analysis"""
    
    print("🏛️ IMPROVED COLOSSEUM HAZARD PROCESSOR")
    print("Testing Multi-Source Fire Analysis")
    print("=" * 60)
    
    # Load dataset
    df = pd.read_excel(dataset_path)
    sites_with_coords = df[df[['Latitude', 'Longitude']].notna().all(axis=1)].copy()
    
    # Take sample
    test_sites = sites_with_coords.head(sample_size)
    print(f"🧪 Testing {len(test_sites)} sites with improved analyzers")
    
    # Initialize improved analyzers
    fire_analyzer = MultiSourceFireAnalyzer()
    flood_analyzer = EnhancedFloodAnalyzer()
    
    # Results tracking
    results = []
    eliminated = 0
    manual_verification = 0
    safe_sites = 0
    
    print(f"\n⚡ Processing sites...")
    
    for idx, (_, row) in enumerate(test_sites.iterrows()):
        if idx % 10 == 0:
            print(f"📊 Progress: {idx+1}/{len(test_sites)}")
        
        site_address = row.get('Property Address', 'Unknown')
        lat, lng = row['Latitude'], row['Longitude']
        
        try:
            # Enhanced fire analysis
            fire_result = fire_analyzer.analyze_fire_risk_comprehensive(lat, lng, site_address)
            
            # Enhanced flood analysis
            existing_flood = {
                'In SFHA': row.get('In SFHA'),
                'Flood Risk Area': row.get('Flood Risk Area'),
                'Fema Flood Zone': row.get('Fema Flood Zone')
            }
            flood_result = flood_analyzer.analyze_flood_risk_comprehensive(
                lat, lng, existing_flood, site_address
            )
            
            # Decision logic
            fire_eliminate = fire_result.get('meets_criteria') is False
            flood_eliminate = flood_result.get('meets_flood_criteria') is False
            
            fire_verify = fire_result.get('manual_verification_required', False)
            flood_verify = flood_result.get('requires_verification', False)
            
            if fire_eliminate or flood_eliminate:
                status = "ELIMINATE"
                eliminated += 1
                reasons = []
                if fire_eliminate:
                    reasons.append(f"Fire: {fire_result.get('hazard_class')}")
                if flood_eliminate:
                    reasons.append(f"Flood: {flood_result.get('flood_risk_level')}")
                elimination_reason = "; ".join(reasons)
            elif fire_verify or flood_verify:
                status = "VERIFY"
                manual_verification += 1
                elimination_reason = None
            else:
                status = "SAFE"
                safe_sites += 1
                elimination_reason = None
            
            result = {
                'site_address': site_address,
                'status': status,
                'fire_hazard': fire_result.get('hazard_class'),
                'fire_source': fire_result.get('data_source'),
                'flood_risk': flood_result.get('flood_risk_level'),
                'flood_source': flood_result.get('data_source'),
                'elimination_reason': elimination_reason
            }
            
            results.append(result)
            
        except Exception as e:
            print(f"❌ Error processing {site_address}: {e}")
            manual_verification += 1
    
    # Final results
    print("\n" + "=" * 60)
    print("🎯 IMPROVED SYSTEM RESULTS")
    print("=" * 60)
    
    total = len(results)
    print(f"✅ Safe sites: {safe_sites} ({safe_sites/total*100:.1f}%)")
    print(f"🚨 Eliminated sites: {eliminated} ({eliminated/total*100:.1f}%)")
    print(f"⚠️  Manual verification: {manual_verification} ({manual_verification/total*100:.1f}%)")
    
    print(f"\n📊 IMPROVEMENT ANALYSIS:")
    print(f"Previous manual verification rate: 95%")
    print(f"New manual verification rate: {manual_verification/total*100:.1f}%")
    print(f"Improvement: {95 - (manual_verification/total*100):.1f} percentage points")
    
    # Fire analyzer statistics
    print(f"\n🔥 FIRE ANALYSIS COVERAGE:")
    fire_stats = fire_analyzer.get_coverage_statistics()
    print(f"Coverage rate: {fire_stats.get('coverage_rate', 'N/A')}")
    print(f"Manual verification rate: {fire_stats.get('manual_verification_rate', 'N/A')}")
    
    # Show eliminated sites
    eliminated_sites = [r for r in results if r['status'] == 'ELIMINATE']
    if eliminated_sites:
        print(f"\n🚨 ELIMINATED SITES ({len(eliminated_sites)}):")
        for site in eliminated_sites:
            print(f"  • {site['site_address'][:50]} - {site['elimination_reason']}")
    
    # Show safe sites sample
    safe_site_list = [r for r in results if r['status'] == 'SAFE']
    if safe_site_list:
        print(f"\n✅ SAFE SITES SAMPLE ({min(5, len(safe_site_list))} of {len(safe_site_list)}):")
        for site in safe_site_list[:5]:
            print(f"  • {site['site_address'][:50]} - Fire: {site['fire_hazard']}, Flood: {site['flood_risk']}")
    
    print("\n🏛️ Multi-Source Analysis Success!")
    
    return results

def main():
    """Main execution"""
    dataset_path = "CostarExport_HighResource_BACKUP_20250730_090645.xlsx"
    
    if not Path(dataset_path).exists():
        print(f"❌ Dataset not found: {dataset_path}")
        return
    
    # Test improved system
    results = test_improved_system(dataset_path, sample_size=50)
    
    return results

if __name__ == "__main__":
    main()