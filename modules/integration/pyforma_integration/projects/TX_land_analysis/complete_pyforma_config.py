#!/usr/bin/env python3
"""
Build complete pyforma configuration with all required fields
"""

import pyforma.pyforma as pyforma
import pandas as pd

def create_complete_config():
    """Create a complete pyforma configuration with all required fields"""
    
    print("Creating complete pyforma configuration...")
    
    # Based on source code analysis, here are ALL required fields:
    complete_config = {
        # BASIC PARCEL INFO
        "parcel_size": 43560,  # Square feet (1 acre)
        "built_dua": 12,       # Dwelling units per acre
        "parcel_efficiency": 0.85,  # Percentage of parcel that can be built on
        "parcel_acquisition_cost": 0,  # Cost already included in land price
        
        # UNIT TYPES AND MIX
        "use_types": {
            "2br": {
                "price_per_sqft": 1.6,    # Monthly rent per sqft
                "size": 1000,             # Square feet per unit
                "parking_ratio": 1.5      # Parking spaces per unit
            },
            "retail": {
                "rent_per_sqft": 20,      # Annual rent per sqft for ground floor
                "parking_ratio": 3.0      # Parking spaces per 1000 sqft
            }
        },
        "use_mix": {
            "use_types": ["2br"],         # Array of unit type names
            "mix": [1.0],                 # Array of proportions (must sum to 1.0)
            "ground_floor": {             # Required to avoid variable initialization bug
                "use": "retail",
                "size": 0                 # 0 size means no ground floor
            }
        },
        
        # BUILDING CONFIGURATION
        "building_type": "garden_apartments",
        "building_types": {
            "garden_apartments": {
                "cost_per_sqft": 150,     # Construction cost per square foot
                "allowable_densities": [5, 25]  # Min/max density range
            }
        },
        "building_efficiency": 0.85,      # Ratio of usable to total building area
        "height_per_story": 10,           # Feet per story
        
        # PARKING CONFIGURATION  
        "parking_type": "surface",
        "parking_types": {
            "surface": {
                "space_size": 300,        # Square feet per parking space
                "space_cost_sqft": 5      # Cost per sqft for parking
            }
        },
        "non_res_parking_denom": 1000,   # For commercial parking calculations
        
        # FINANCIAL PARAMETERS
        "cap_rate": 0.06,                 # Capitalization rate (6%)
        "cost_shifter": 1.0,              # Cost adjustment multiplier
        
        # ZONING CONSTRAINTS
        "max_dua": 25,                    # Maximum dwelling units per acre
        "max_far": 2.0,                   # Maximum floor area ratio
        "max_height": 35                  # Maximum building height in feet
    }
    
    print("✅ Complete configuration created")
    return complete_config

def test_complete_config():
    """Test the complete configuration"""
    
    config = create_complete_config()
    
    try:
        print("\nTesting complete configuration...")
        result = pyforma.spot_residential_sales_proforma(config)
        print("✅ Complete configuration works!")
        
        # Show key results
        key_results = [
            'total_revenue', 'total_cost', 'profit', 'profit_per_sqft',
            'num_units_by_type', 'usable_floor_area', 'built_far',
            'building_height', 'parking_spaces'
        ]
        
        print(f"\nKey Results:")
        for key in key_results:
            if key in result:
                value = result[key]
                if isinstance(value, (int, float)):
                    if 'revenue' in key or 'cost' in key or 'profit' in key:
                        print(f"  {key}: ${value:,.0f}")
                    else:
                        print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")
        
        return result, True
        
    except Exception as e:
        print(f"❌ Complete configuration failed: {e}")
        return None, False

def test_affordable_housing_config():
    """Test configuration with affordable housing"""
    
    print(f"\nTesting with affordable housing...")
    
    config = create_complete_config()
    
    # Add affordable housing configuration
    config["affordable_housing"] = {
        "AMI": 60000,                     # Area Median Income
        "depth_of_affordability": 0.60,  # 60% of AMI
        "pct_affordable_units": 1.0,     # 100% affordable (LIHTC)
        "price_multiplier_by_type": {
            "2br": 1.0                    # No price adjustment
        }
    }
    
    try:
        result = pyforma.spot_residential_sales_proforma(config)
        print("✅ Affordable housing configuration works!")
        
        # Show affordable housing impact
        if 'affordable_housing_applied' in result:
            print(f"  Affordable housing applied: {result['affordable_housing_applied']}")
        
        return result, True
        
    except Exception as e:
        print(f"❌ Affordable housing configuration failed: {e}")
        return None, False

def test_multiple_unit_types():
    """Test with multiple unit types like our Texas sites"""
    
    print(f"\nTesting multiple unit types...")
    
    config = create_complete_config()
    
    # Update for multiple unit types
    config["use_types"] = {
        "1br": {
            "price_per_sqft": 1.32,  # $988/month ÷ 750 sqft
            "size": 750,
            "parking_ratio": 1.0
        },
        "2br": {
            "price_per_sqft": 1.60,  # $1600/month ÷ 1000 sqft
            "size": 1000,
            "parking_ratio": 1.5
        },
        "3br": {
            "price_per_sqft": 1.10,  # $1370/month ÷ 1250 sqft
            "size": 1250,
            "parking_ratio": 2.0
        }
    }
    
    config["use_mix"] = {
        "use_types": ["1br", "2br", "3br"],
        "mix": [0.2, 0.6, 0.2]  # 20% 1BR, 60% 2BR, 20% 3BR
    }
    
    # Add affordable housing for all unit types
    config["affordable_housing"] = {
        "AMI": 60000,
        "depth_of_affordability": 0.60,
        "pct_affordable_units": 1.0,
        "price_multiplier_by_type": {
            "1br": 1.0,
            "2br": 1.0,
            "3br": 1.0
        }
    }
    
    try:
        result = pyforma.spot_residential_sales_proforma(config)
        print("✅ Multiple unit types work!")
        
        # Show unit breakdown
        units = result.get('num_units_by_type', {})
        total_units = units.get('residential_units', 0)
        print(f"  Total units: {total_units:.1f}")
        print(f"  1BR units: {units.get('1br_num_units', 0):.1f}")
        print(f"  2BR units: {units.get('2br_num_units', 0):.1f}")
        print(f"  3BR units: {units.get('3br_num_units', 0):.1f}")
        
        return result, True
        
    except Exception as e:
        print(f"❌ Multiple unit types failed: {e}")
        return None, False

if __name__ == "__main__":
    print("BUILDING COMPLETE PYFORMA CONFIGURATION")
    print("=" * 60)
    
    # Test progression
    tests = [
        ("Basic Configuration", test_complete_config),
        ("Affordable Housing", test_affordable_housing_config), 
        ("Multiple Unit Types", test_multiple_unit_types)
    ]
    
    success_count = 0
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result, success = test_func()
        if success:
            success_count += 1
    
    print(f"\n" + "="*60)
    print(f"RESULTS: {success_count}/{len(tests)} tests passed")
    
    if success_count == len(tests):
        print("🎉 pyforma configuration complete! Ready for Texas sites analysis.")
    else:
        print("❌ Still debugging configuration issues.")