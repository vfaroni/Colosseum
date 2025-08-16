#!/usr/bin/env python3
"""
Quick CA/TX Regulatory Universe Analysis
Uses cached data for rapid strategic intelligence
"""

from complete_regulatory_universe_mapper import CompleteRegulatoryUniverseMapper
import json

def quick_ca_tx_analysis():
    """Quick analysis using existing framework"""
    
    print("🚀 QUICK CA/TX REGULATORY UNIVERSE ANALYSIS")
    print("=" * 60)
    
    mapper = CompleteRegulatoryUniverseMapper()
    
    # CA Analysis
    print("\n🏛️ CALIFORNIA ANALYSIS")
    print("-" * 40)
    try:
        ca_universe = mapper.map_complete_regulatory_universe("CA")
        print(f"✅ CA: {len(ca_universe.external_regulations)} external regs, {ca_universe.total_estimated_pages:,} pages")
        
        print(f"\n📊 CA REGULATORY UNIVERSE BREAKDOWN:")
        print(f"QAP Content: {sum(len(s.content) for s in ca_universe.qap_sections.values()):,} chars")
        print(f"External Regulations: {len(ca_universe.external_regulations)}")
        print(f"Hub-to-Spoke Ratio: {ca_universe.total_estimated_pages // (sum(len(s.content) for s in ca_universe.qap_sections.values()) // 2000 + 1)}:1")
        
    except Exception as e:
        print(f"❌ CA analysis error: {e}")
    
    # TX Analysis  
    print("\n🏛️ TEXAS ANALYSIS")
    print("-" * 40)
    try:
        tx_universe = mapper.map_complete_regulatory_universe("TX")
        print(f"✅ TX: {len(tx_universe.external_regulations)} external regs, {tx_universe.total_estimated_pages:,} pages")
        
        print(f"\n📊 TX REGULATORY UNIVERSE BREAKDOWN:")
        print(f"QAP Content: {sum(len(s.content) for s in tx_universe.qap_sections.values()):,} chars")
        print(f"External Regulations: {len(tx_universe.external_regulations)}")
        print(f"Hub-to-Spoke Ratio: {tx_universe.total_estimated_pages // (sum(len(s.content) for s in tx_universe.qap_sections.values()) // 2000 + 1)}:1")
        
    except Exception as e:
        print(f"❌ TX analysis error: {e}")
    
    print(f"\n🎯 STRATEGIC INTELLIGENCE COMPLETE")

if __name__ == "__main__":
    quick_ca_tx_analysis()