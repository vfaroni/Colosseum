#!/usr/bin/env python3
"""
Fix Python 2 compatibility issues in pyforma
"""

def monkey_patch_pyforma():
    """Add Python 2 compatibility to pyforma"""
    
    print("Applying Python 2 compatibility patches...")
    
    # Add iteritems method to dict class if it doesn't exist
    if not hasattr(dict, 'iteritems'):
        dict.iteritems = lambda self: iter(self.items())
        print("✅ Added iteritems compatibility")
    
    # Add iterkeys method if needed
    if not hasattr(dict, 'iterkeys'):
        dict.iterkeys = lambda self: iter(self.keys())
        print("✅ Added iterkeys compatibility")
        
    # Add itervalues method if needed  
    if not hasattr(dict, 'itervalues'):
        dict.itervalues = lambda self: iter(self.values())
        print("✅ Added itervalues compatibility")

def test_with_compatibility():
    """Test pyforma with compatibility patches"""
    
    # Apply patches first
    monkey_patch_pyforma()
    
    # Now import and test pyforma
    import pyforma.pyforma as pyforma
    
    print("\nTesting pyforma with compatibility patches...")
    
    config = {
        "parcel_size": 43560,
        "built_dua": 12,
        "parcel_efficiency": 0.85,
        "parcel_acquisition_cost": 0,
        
        "use_types": {
            "2br": {
                "price_per_sqft": 1.6,
                "size": 1000,
                "parking_ratio": 1.5
            },
            "retail": {
                "rent_per_sqft": 20,
                "parking_ratio": 3.0
            }
        },
        "use_mix": {
            "use_types": ["2br"],
            "mix": [1.0],
            "ground_floor": {
                "use": "retail",
                "size": 0
            }
        },
        
        "building_type": "garden_apartments",
        "building_types": {
            "garden_apartments": {
                "cost_per_sqft": 150,
                "allowable_densities": [5, 25]
            }
        },
        "building_efficiency": 0.85,
        "height_per_story": 10,
        
        "parking_type": "surface",
        "parking_types": {
            "surface": {
                "space_size": 300,
                "space_cost_sqft": 5
            }
        },
        "non_res_parking_denom": 1000,
        
        "cap_rate": 0.06,
        "cost_shifter": 1.0,
        
        "max_dua": 25,
        "max_far": 2.0,
        "max_height": 35
    }
    
    try:
        result = pyforma.spot_residential_sales_proforma(config)
        print("✅ pyforma works with compatibility patches!")
        
        # Show key results
        key_results = ['total_revenue', 'total_cost', 'profit', 'num_units_by_type']
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
        
        return True
        
    except Exception as e:
        print(f"❌ Still failing: {e}")
        return False

if __name__ == "__main__":
    print("FIXING PYTHON 2 COMPATIBILITY ISSUES")
    print("=" * 50)
    
    success = test_with_compatibility()
    
    if success:
        print("\n🎉 pyforma compatibility fixed! Ready for Texas sites.")
    else:
        print("\n❌ Still need to debug further.")