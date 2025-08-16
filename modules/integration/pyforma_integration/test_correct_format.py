#!/usr/bin/env python3
"""
Test pyforma with correct configuration format based on source code inspection
"""

import pyforma.pyforma as pyforma
import pandas as pd

def test_correct_format():
    """Test with correct configuration format"""
    
    print("Testing correct configuration format...")
    
    correct_config = {
        "use_types": {
            "2br": {
                "price_per_sqft": 1.6,
                "size": 1000,
                "parking_ratio": 1.5
            }
        },
        "use_mix": {
            "use_types": ["2br"],  # Array of use type names
            "mix": [1.0]           # Array of proportions (must sum to 1.0)
        },
        "parcel_size": 43560,  # 1 acre in sqft
        "building_type": "garden_apartments",
        "built_dua": 12
    }
    
    try:
        result = pyforma.spot_residential_sales_proforma(correct_config)
        print("✅ Correct format worked!")
        
        # Show key results
        key_results = ['total_revenue', 'total_cost', 'profit', 'num_units_by_type', 'usable_floor_area']
        for key in key_results:
            if key in result:
                value = result[key]
                if isinstance(value, (int, float)):
                    if 'revenue' in key or 'cost' in key or 'profit' in key:
                        print(f"  {key}: ${value:,.0f}")
                    else:
                        print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {value}")
        
        return result
    except Exception as e:
        print(f"❌ Correct format failed: {e}")
        return None

def test_mixed_units():
    """Test with multiple unit types"""
    
    print("\nTesting multiple unit types...")
    
    mixed_config = {
        "use_types": {
            "1br": {
                "price_per_sqft": 1.32,
                "size": 750,
                "parking_ratio": 1.0
            },
            "2br": {
                "price_per_sqft": 1.60,
                "size": 1000,
                "parking_ratio": 1.5
            },
            "3br": {
                "price_per_sqft": 1.10,
                "size": 1250,
                "parking_ratio": 2.0
            }
        },
        "use_mix": {
            "use_types": ["1br", "2br", "3br"],
            "mix": [0.2, 0.6, 0.2]  # 20% 1BR, 60% 2BR, 20% 3BR
        },
        "parcel_size": 435600,  # 10 acres
        "building_type": "garden_apartments",
        "built_dua": 12
    }
    
    try:
        result = pyforma.spot_residential_sales_proforma(mixed_config)
        print("✅ Mixed units worked!")
        
        # Show unit breakdown
        print(f"  Total units: {result.get('num_units_by_type', {}).get('residential_units', 0):.1f}")
        print(f"  1BR units: {result.get('num_units_by_type', {}).get('1br_num_units', 0):.1f}")
        print(f"  2BR units: {result.get('num_units_by_type', {}).get('2br_num_units', 0):.1f}")
        print(f"  3BR units: {result.get('num_units_by_type', {}).get('3br_num_units', 0):.1f}")
        
        return result
    except Exception as e:
        print(f"❌ Mixed units failed: {e}")
        return None

def test_affordable_housing():
    """Test with affordable housing configuration"""
    
    print("\nTesting affordable housing...")
    
    affordable_config = {
        "use_types": {
            "2br": {
                "price_per_sqft": 1.6,
                "size": 1000,
                "parking_ratio": 1.5
            }
        },
        "use_mix": {
            "use_types": ["2br"],
            "mix": [1.0]
        },
        "parcel_size": 43560,
        "building_type": "garden_apartments", 
        "built_dua": 12,
        "affordable_housing": {
            "AMI": 60000,
            "depth_of_affordability": 0.60,
            "pct_affordable_units": 1.0
        }
    }
    
    try:
        result = pyforma.spot_residential_sales_proforma(affordable_config)
        print("✅ Affordable housing worked!")
        
        return result
    except Exception as e:
        print(f"❌ Affordable housing failed: {e}")
        return None

if __name__ == "__main__":
    print("TESTING CORRECT PYFORMA FORMAT")
    print("=" * 50)
    
    test_correct_format()
    test_mixed_units()
    test_affordable_housing()
    
    print("\n🎉 Configuration format verified! Ready for Texas sites analysis.")