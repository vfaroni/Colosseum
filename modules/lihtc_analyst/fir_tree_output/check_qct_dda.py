#!/usr/bin/env python3
"""
Quick QCT/DDA check for Fir Tree Park, Shelton WA
"""
import sys
import os

# Add path to our analyzers
sys.path.append('../botn_engine/src/analyzers')

from qct_dda_analyzer import QCTDDAAnalyzer

def check_fir_tree_qct_dda():
    """Check QCT/DDA status for Fir Tree Park"""
    
    # Fir Tree Park coordinates (from docs)
    lat = 47.2179  # Latitude for Shelton, WA area
    lon = -123.1043  # Longitude for Shelton, WA area
    address = "1602 E Birch St, Shelton, WA 98584"
    
    print("🏛️ FEDERAL BASIS BOOST ANALYSIS")
    print("=" * 50)
    print(f"📍 Property: Fir Tree Park")
    print(f"📫 Address: {address}")
    print(f"🗺️  Coordinates: {lat}, {lon}")
    print()
    
    # Try to analyze QCT/DDA status
    try:
        analyzer = QCTDDAAnalyzer()
        result = analyzer.analyze(lat, lon)
        
        if result:
            print("✅ FEDERAL BASIS BOOST ANALYSIS COMPLETE")
            print(f"🎯 QCT Qualified: {'✅ YES' if result.qct_qualified else '❌ NO'}")
            print(f"🏔️  DDA Qualified: {'✅ YES' if result.dda_qualified else '❌ NO'}")
            print(f"💰 Federal Basis Boost: {'✅ YES' if result.federal_basis_boost else '❌ NO'}")
            
            if result.federal_basis_boost:
                print(f"📈 Basis Boost: +{result.basis_boost_percentage}%")
                if result.qct_qualified:
                    print(f"📊 QCT Details: {result.qct_name} (Tract: {result.qct_tract_id})")
                if result.dda_qualified:
                    print(f"🏔️  DDA Details: {result.dda_name}")
            else:
                print("❌ NO BASIS BOOST: Property not in QCT or DDA")
        else:
            print("❌ ANALYSIS FAILED: Unable to determine QCT/DDA status")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print()
        print("📋 MANUAL LOOKUP REQUIRED:")
        print("• Check HUD QCT/DDA maps at: https://hudgis-hud.opendata.arcgis.com/")
        print("• Washington State may be Non-Metro QCT area")
        print("• Rural areas often qualify for different basis boost rules")

if __name__ == "__main__":
    check_fir_tree_qct_dda()