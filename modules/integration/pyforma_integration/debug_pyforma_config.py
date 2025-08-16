#!/usr/bin/env python3
"""
Debug pyforma configuration to understand expected format
"""

import pyforma.pyforma as pyforma
import pandas as pd

def test_simple_config():
    """Test with the simplest possible configuration"""
    
    print("Testing simple configuration...")
    
    simple_config = {
        "use_types": {
            "2br": {
                "price_per_sqft": 1.5,
                "size": 1000,
                "parking_ratio": 1.0
            }
        },
        "use_mix": [1.0],  # 100% 2BR units
        "parcel_size": 10000,
        "building_type": "garden_apartments",
        "built_dua": 10
    }
    
    try:
        result = pyforma.spot_residential_sales_proforma(simple_config)
        print("✅ Simple config worked!")
        print(f"Result keys: {list(result.keys())[:10]}")
        return True
    except Exception as e:
        print(f"❌ Simple config failed: {e}")
        return False

def test_github_example():
    """Test with example from GitHub README"""
    
    print("\nTesting GitHub README example...")
    
    github_config = {
        "use_types": {
            "1br": {
                "price_per_sqft": 650,
                "size": 750,
                "parking_ratio": 1.0
            }
        },
        "use_mix": [1.0],
        "parcel_size": 10000,
        "building_type": "garden_apartments",
        "built_dua": 10
    }
    
    try:
        result = pyforma.spot_residential_sales_proforma(github_config)
        print("✅ GitHub example worked!")
        print(f"Result keys: {list(result.keys())[:10]}")
        return True
    except Exception as e:
        print(f"❌ GitHub example failed: {e}")
        return False

def test_affordable_housing():
    """Test with affordable housing configuration"""
    
    print("\nTesting affordable housing configuration...")
    
    affordable_config = {
        "use_types": {
            "2br": {
                "price_per_sqft": 1.6,
                "size": 1000,
                "parking_ratio": 1.5
            }
        },
        "use_mix": [1.0],
        "parcel_size": 43560,  # 1 acre
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
        print("✅ Affordable housing config worked!")
        
        # Show detailed results
        key_results = ['total_revenue', 'total_cost', 'profit', 'num_units_by_type']
        for key in key_results:
            if key in result:
                print(f"  {key}: {result[key]}")
        
        return True
    except Exception as e:
        print(f"❌ Affordable housing config failed: {e}")
        return False

def test_vectorized():
    """Test vectorized calculation"""
    
    print("\nTesting vectorized calculation...")
    
    try:
        # Create series for vectorized analysis
        dua_series = pd.Series([8, 10, 12, 15], name="built_dua")
        
        vectorized_config = {
            "use_types": {
                "2br": {
                    "price_per_sqft": 1.6,
                    "size": 1000,
                    "parking_ratio": 1.5
                }
            },
            "use_mix": [1.0],
            "parcel_size": 43560,
            "building_type": "garden_apartments",
            "built_dua": dua_series  # Vectorized parameter
        }
        
        result = pyforma.spot_residential_sales_proforma(vectorized_config)
        print("✅ Vectorized calculation worked!")
        print(f"Result type: {type(result)}")
        
        return True
    except Exception as e:
        print(f"❌ Vectorized calculation failed: {e}")
        return False

def test_cartesian_product():
    """Test cartesian product functionality"""
    
    print("\nTesting cartesian product...")
    
    try:
        dua_series = pd.Series([10, 12, 15], name="dua")
        parcel_series = pd.Series([20000, 30000, 40000], name="parcel_size")
        
        df = pyforma.cartesian_product([dua_series, parcel_series])
        print("✅ Cartesian product worked!")
        print(f"Result shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("Sample rows:")
        print(df.head(3))
        
        return True
    except Exception as e:
        print(f"❌ Cartesian product failed: {e}")
        return False

if __name__ == "__main__":
    print("PYFORMA CONFIGURATION DEBUG")
    print("=" * 50)
    
    success_count = 0
    tests = [
        test_simple_config,
        test_github_example, 
        test_affordable_housing,
        test_vectorized,
        test_cartesian_product
    ]
    
    for test in tests:
        if test():
            success_count += 1
        print()
    
    print(f"Results: {success_count}/{len(tests)} tests passed")
    
    if success_count >= 3:
        print("🎉 pyforma is working! Ready to proceed with Texas sites.")
    else:
        print("❌ Multiple test failures. Check pyforma installation.")