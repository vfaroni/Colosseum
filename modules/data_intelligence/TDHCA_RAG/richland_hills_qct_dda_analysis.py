#!/usr/bin/env python3
"""
QCT/DDA Analysis for Richland Hills Tract 
Location: Corner of Midhurst Ave & Richland Hills Dr, San Antonio, TX
Coordinates: 29.4187, -98.6788
"""

import sys
import os

# Add the path to import the comprehensive analyzer
sys.path.append('/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG')

from comprehensive_qct_dda_analyzer import ComprehensiveQCTDDAAnalyzer

def main():
    """Analyze the correct Richland Hills Tract location"""
    
    print("RICHLAND HILLS TRACT QCT/DDA ANALYSIS")
    print("="*60)
    print("Property Location: Corner of Midhurst Ave & Richland Hills Dr")
    print("San Antonio, TX 78245")
    print("Parcel ID: 15329-000-0260")
    print("Land Area: 9.83 acres")
    print("Owner: KEM TEXAS LTD")
    print("="*60)
    
    # Initialize analyzer
    analyzer = ComprehensiveQCTDDAAnalyzer()
    
    # Coordinates for the correct Richland Hills Tract location
    lat, lon = 29.4187, -98.6788
    
    print(f"\nAnalyzing coordinates: {lat}, {lon}")
    print("(Center of parcel at corner of Midhurst Ave & Richland Hills Dr)")
    
    # Perform complete QCT/DDA analysis
    result = analyzer.lookup_qct_status(lat, lon)
    
    # Print detailed results
    analyzer.print_detailed_analysis(result)
    
    # Additional summary for development purposes
    print("\nDEVELOPMENT SUMMARY:")
    print("="*40)
    
    basis_boost = result.get('basis_boost_eligible', False)
    classification = result.get('industry_classification', 'Unknown')
    
    if basis_boost:
        print("🎯 EXCELLENT NEWS: This property QUALIFIES for 130% basis boost!")
        print(f"📋 Qualification Type: {classification}")
        print("💰 Financial Impact: 30% increase in eligible basis")
        print("📈 Development Advantage: Significantly improved project economics")
    else:
        print("❌ This property does NOT qualify for 130% basis boost")
        print(f"📋 Classification: {classification}")
        print("💡 Consider: Standard LIHTC development approach")
    
    # QCT/DDA status breakdown
    qct_status = result.get('qct_status', 'Unknown')
    dda_status = result.get('dda_status', 'Unknown')
    
    print(f"\nSTATUS BREAKDOWN:")
    print(f"QCT Status: {qct_status}")
    print(f"DDA Status: {dda_status}")
    print(f"Metro Classification: {result.get('metro_status', 'Unknown')}")
    print(f"AMI Source: {result.get('ami_source', 'Unknown')}")
    
    return result

if __name__ == "__main__":
    result = main()