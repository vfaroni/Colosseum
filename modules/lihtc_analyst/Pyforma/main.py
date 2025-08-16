#!/usr/bin/env python3
"""
Pyforma Example Script - Real Estate Pro Forma Analysis
Creates a sample 50-unit residential project and runs the analysis
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pyforma'))

from pyforma.pyforma import spot_residential_sales_proforma

def main():
    """Create and analyze a 50-unit residential project"""
    
    # Configuration for a 50-unit residential project
    config = {
        "use_types": {
            "1br": {
                "price_per_sqft": 650,   # $650 per sqft market price
                "size": 750,             # 750 sqft per unit
                "parking_ratio": 1.0     # 1 parking space per unit
            },
            "2br": {
                "price_per_sqft": 700,   # $700 per sqft market price
                "size": 950,             # 950 sqft per unit
                "parking_ratio": 1.5     # 1.5 parking spaces per unit
            },
            "3br": {
                "price_per_sqft": 750,   # $750 per sqft market price
                "size": 1200,            # 1200 sqft per unit
                "parking_ratio": 2.0     # 2 parking spaces per unit
            }
        },
        "parking_types": {
            "surface": {
                "space_size": 300,       # 300 sqft per parking space
                "space_cost_sqft": 30    # $30 per sqft construction cost
            },
            "deck": {
                "space_size": 250,       # 250 sqft per parking space
                "space_cost_sqft": 90    # $90 per sqft construction cost
            },
            "underground": {
                "space_size": 250,       # 250 sqft per parking space
                "space_cost_sqft": 110   # $110 per sqft construction cost
            }
        },
        "building_types": {
            "mid_rise_apartments": {
                "cost_per_sqft": 250,    # $250 per sqft construction cost
                "allowable_densities": [20, 80]  # 20-80 units per acre
            },
            "luxury_condos": {
                "cost_per_sqft": 350,    # $350 per sqft construction cost
                "allowable_densities": [15, 60]  # 15-60 units per acre
            }
        },
        "parcel_size": 43560,            # 1 acre = 43,560 sqft
        "cap_rate": 0.06,                # 6% capitalization rate
        "max_far": 2.0,                  # Maximum Floor Area Ratio
        "max_height": 60,                # Maximum building height (feet)
        "height_per_story": 12,          # 12 feet per story
        "parcel_efficiency": 0.8,        # 80% of parcel can be used for building
        "building_efficiency": 0.85,     # 85% efficiency (common area factor)
        "cost_shifter": 1.0,             # No cost adjustment
        "parcel_acquisition_cost": 2000000,  # $2M land acquisition cost
        "non_res_parking_denom": 1000,   # For non-residential parking calculations
        "use_mix": {
            "use_types": ["1br", "2br", "3br"],  # Unit types to include
            "mix": [0.4, 0.4, 0.2]       # 40% 1BR, 40% 2BR, 20% 3BR
        },
        "absorption_in_months": 18,      # 18 months to sell all units
        "parking_type": "deck",          # Use deck parking
        "building_type": "mid_rise_apartments",  # Building type
        "built_dua": 50                  # 50 dwelling units per acre (50 total units)
    }
    
    print("=== PYFORMA REAL ESTATE PRO FORMA ANALYSIS ===")
    print(f"Project: 50-Unit Residential Development")
    print(f"Parcel Size: 1 acre ({config['parcel_size']:,} sqft)")
    print(f"Unit Mix: 40% 1BR, 40% 2BR, 20% 3BR")
    print(f"Average Construction Cost: ${config['building_types']['mid_rise_apartments']['cost_per_sqft']}/sqft")
    print(f"Land Acquisition Cost: ${config['parcel_acquisition_cost']:,}")
    print()
    
    # Run the pro forma analysis
    try:
        results = spot_residential_sales_proforma(config)
        
        print("=== ANALYSIS RESULTS ===")
        print(f"Total Units: {sum(results['num_units_by_type'].values()):.0f}")
        print(f"Building Stories: {results['stories']:.0f}")
        print(f"Building Height: {results['height']:.0f} feet")
        print(f"Built FAR: {results['built_far']:.2f}")
        print(f"Usable Floor Area: {results['usable_floor_area']:,.0f} sqft")
        print(f"Total Floor Area: {results['total_floor_area']:,.0f} sqft")
        print(f"Parking Spaces: {results['parking_spaces']:.0f}")
        print(f"Parking Cost: ${results['parking_cost']:,.0f}")
        print()
        
        print("=== FINANCIAL SUMMARY ===")
        print(f"Total Revenue: ${results['revenue']:,.0f}")
        print(f"Total Construction Cost: ${results['cost']:,.0f}")
        print(f"Net Profit: ${results['profit']:,.0f}")
        
        if results['profit'] > 0:
            profit_margin = (results['profit'] / results['revenue']) * 100
            print(f"Profit Margin: {profit_margin:.1f}%")
            print("✓ PROJECT IS FINANCIALLY FEASIBLE")
        else:
            print("✗ PROJECT IS NOT FINANCIALLY FEASIBLE")
        
        print()
        
        # Check for zoning violations
        violations = []
        if results.get('failure_dua', False):
            violations.append("DUA (Density)")
        if results.get('failure_far', False):
            violations.append("FAR (Floor Area Ratio)")
        if results.get('failure_height', False):
            violations.append("Height Limit")
        if results.get('failure_btype', False):
            violations.append("Building Type")
        
        if violations:
            print("=== ZONING VIOLATIONS ===")
            for violation in violations:
                print(f"✗ {violation}")
        else:
            print("✓ No zoning violations detected")
        
        print()
        print("=== UNIT BREAKDOWN ===")
        for unit_type, count in results['num_units_by_type'].items():
            if count > 0:
                print(f"{unit_type}: {count:.0f} units")
        
    except Exception as e:
        print(f"Error running analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())