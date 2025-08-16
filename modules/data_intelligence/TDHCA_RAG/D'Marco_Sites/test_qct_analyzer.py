#!/usr/bin/env python3
"""
Test QCT/DDA Analyzer - Validation Script
Test with known Houston QCT coordinates to verify functionality
"""

import sys
import os
sys.path.append('.')

from comprehensive_qct_dda_analyzer import ComprehensiveQCTDDAAnalyzer

def test_houston_qct():
    """Test with known Houston QCT coordinate"""
    
    print("🧪 TESTING QCT/DDA ANALYZER WITH KNOWN HOUSTON QCT")
    print("="*70)
    
    # Initialize analyzer
    try:
        analyzer = ComprehensiveQCTDDAAnalyzer()
        print("✅ Analyzer initialized successfully")
    except Exception as e:
        print(f"❌ Analyzer initialization failed: {e}")
        return
    
    # Test with Houston Third Ward (known QCT area)
    # Third Ward, Houston - historically QCT eligible
    test_coordinates = [
        (29.7372, -95.3647),  # Third Ward, Houston (known QCT)
        (29.7604, -95.3698),  # Downtown Houston area
        (29.8663, -95.3473),  # North Houston (from D'Marco sites)
    ]
    
    for i, (lat, lng) in enumerate(test_coordinates, 1):
        print(f"\n🎯 TEST {i}: Coordinates {lat}, {lng}")
        print("-" * 50)
        
        try:
            result = analyzer.lookup_qct_status(lat, lng)
            
            if 'error' in result:
                print(f"❌ Analysis failed: {result['error']}")
            else:
                # Extract key results
                qct_status = result.get('qct_status', 'unknown')
                dda_status = result.get('dda_status', 'unknown') 
                basis_boost = result.get('basis_boost_eligible', False)
                metro_status = result.get('metro_status', 'unknown')
                classification = result.get('industry_classification', 'unknown')
                
                print(f"📍 Location: {result.get('state_name', 'unknown')}, {result.get('county_name', 'unknown')}")
                print(f"🏙️  Metro Status: {metro_status}")
                print(f"🎯 QCT Status: {qct_status}")
                print(f"🏔️  DDA Status: {dda_status}")
                print(f"💰 Basis Boost Eligible: {'YES' if basis_boost else 'NO'}")
                print(f"🏢 Classification: {classification}")
                
                # Check if this is working properly
                if qct_status != 'unknown' and metro_status != 'Unknown':
                    print("✅ Analysis successful - API working")
                else:
                    print("⚠️ Analysis returned unknown values - possible API issue")
        
        except Exception as e:
            print(f"❌ Exception during analysis: {e}")

if __name__ == "__main__":
    test_houston_qct()