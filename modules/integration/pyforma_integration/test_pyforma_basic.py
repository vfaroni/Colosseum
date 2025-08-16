#!/usr/bin/env python3
"""
Basic test script to verify pyforma installation and functionality
"""

import sys
import pandas as pd
import numpy as np

def test_pyforma_installation():
    """Test that pyforma can be imported and basic functionality works"""
    print("Testing pyforma installation...")
    
    try:
        import pyforma
        print("✅ pyforma imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pyforma: {e}")
        return False
    
    # Test basic configuration
    print("\nTesting basic pro forma configuration...")
    
    config = {
        "use_types": {
            "1br": {
                "price_per_sqft": 650,  # Monthly rent per sqft
                "size": 750,            # Square feet
                "parking_ratio": 1.0    # Parking spaces per unit
            },
            "2br": {
                "price_per_sqft": 600,
                "size": 1000,
                "parking_ratio": 1.5
            }
        },
        "parcel_size": 10000,  # Square feet
        "building_type": "garden_apartments",
        "built_dua": 10  # Dwelling units per acre
    }
    
    try:
        # Test single calculation
        print("Testing single site calculation...")
        result = pyforma.spot_residential_sales_proforma(config)
        print("✅ Single calculation successful")
        print(f"   Result type: {type(result)}")
        print(f"   Keys: {list(result.keys())[:5]}...")  # Show first 5 keys
        
        # Test vectorized calculation
        print("\nTesting vectorized calculation...")
        dua_series = pd.Series([8, 10, 12, 15], name="built_dua")
        config_vector = config.copy()
        config_vector["built_dua"] = dua_series
        
        result_vector = pyforma.spot_residential_sales_proforma(config_vector)
        print("✅ Vectorized calculation successful")
        print(f"   Vector result type: {type(result_vector)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running pyforma calculations: {e}")
        return False

def test_cartesian_product():
    """Test pyforma's cartesian product functionality"""
    print("\nTesting cartesian product functionality...")
    
    try:
        import pyforma
        
        # Create test series
        dua_series = pd.Series([10, 15, 20], name="dua")
        far_series = pd.Series([0.5, 1.0, 1.5], name="far")
        
        # Test cartesian product
        df = pyforma.cartesian_product([dua_series, far_series])
        print("✅ Cartesian product successful")
        print(f"   Result shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Expected combinations: {len(dua_series) * len(far_series)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing cartesian product: {e}")
        return False

if __name__ == "__main__":
    print("pyforma Installation Test")
    print("=" * 50)
    
    success = True
    success &= test_pyforma_installation()
    success &= test_cartesian_product()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! pyforma is ready for LIHTC analysis.")
    else:
        print("❌ Some tests failed. Check installation and dependencies.")
        sys.exit(1)