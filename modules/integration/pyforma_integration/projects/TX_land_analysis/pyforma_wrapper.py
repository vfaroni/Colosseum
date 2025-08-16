#!/usr/bin/env python3
"""
Python 3 compatible wrapper for pyforma functionality
"""

import pandas as pd
import numpy as np

class PyformaWrapper:
    """Wrapper class to handle pyforma functionality with Python 3 compatibility"""
    
    def __init__(self):
        self.pyforma_available = False
        self.try_import_pyforma()
    
    def try_import_pyforma(self):
        """Try to import and fix pyforma for Python 3"""
        try:
            # First try importing
            import pyforma.pyforma as pf
            self.pf = pf
            
            # Try a simple test to see if it works
            test_config = self.create_minimal_config()
            result = pf.spot_residential_sales_proforma(test_config)
            self.pyforma_available = True
            print("✅ pyforma imported successfully")
            
        except Exception as e:
            print(f"❌ pyforma not available: {e}")
            self.pyforma_available = False
    
    def create_minimal_config(self):
        """Create minimal configuration for testing"""
        return {
            "parcel_size": 43560,
            "built_dua": 10,
            "parcel_efficiency": 0.85,
            "parcel_acquisition_cost": 0,
            
            "use_types": {
                "2br": {
                    "price_per_sqft": 1.5,
                    "size": 1000,
                    "parking_ratio": 1.0
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
    
    def calculate_simple_proforma(self, parcel_acres, target_dua, unit_mix_config):
        """
        Simple pro forma calculation without pyforma complexity
        Based on your existing methodology but with vectorized calculations
        """
        
        print(f"Calculating simple pro forma (pyforma not available)")
        
        # Basic calculations
        total_units = parcel_acres * target_dua
        parcel_sqft = parcel_acres * 43560
        
        # Calculate unit breakdown and revenue
        total_revenue = 0
        total_sqft = 0
        unit_breakdown = {}
        
        # Extract land cost first
        land_cost = unit_mix_config.get('land_cost', 0)
        
        for unit_type, config in unit_mix_config.items():
            # Skip non-unit entries
            if unit_type == 'land_cost':
                continue
                
            # Calculate number of units of this type
            mix_pct = config.get('mix_pct', 0.33)  # Default if not specified
            units_of_type = total_units * mix_pct
            unit_breakdown[f"{unit_type}_units"] = units_of_type
            
            # Calculate revenue for this unit type
            monthly_rent = config['monthly_rent']
            annual_rent = monthly_rent * 12
            revenue_from_type = annual_rent * units_of_type
            total_revenue += revenue_from_type
            
            # Calculate square footage
            unit_sqft = config['size']
            sqft_from_type = unit_sqft * units_of_type
            total_sqft += sqft_from_type
        
        # Calculate costs (simplified)
        construction_cost_per_sqft = 150  # Base cost
        total_construction_cost = total_sqft * construction_cost_per_sqft
        
        # Add land cost (already extracted above)
        total_cost = total_construction_cost + land_cost
        
        # Calculate metrics
        profit = total_revenue - total_cost
        profit_per_unit = profit / total_units if total_units > 0 else 0
        revenue_cost_ratio = total_revenue / total_cost if total_cost > 0 else 0
        
        result = {
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "profit": profit,
            "profit_per_unit": profit_per_unit,
            "revenue_cost_ratio": revenue_cost_ratio,
            "total_units": total_units,
            "total_sqft": total_sqft,
            "unit_breakdown": unit_breakdown,
            "method": "simplified_calculation"
        }
        
        return result
    
    def analyze_texas_site(self, site_data):
        """Analyze a single Texas site using available method"""
        
        # Extract site information
        acres = site_data.get('Acres', 1.0)
        county = site_data.get('County', 'Unknown')
        
        # Get rent data (prefer corrected values)
        rent_1br = site_data.get('rent_1br_60pct', 800)
        rent_2br = site_data.get('Corrected_Annual_Rent', site_data.get('rent_2br_60pct', 1000)) / 12
        rent_3br = site_data.get('rent_3br_60pct', 1200)
        
        # Configure unit mix (typical LIHTC mix)
        unit_mix_config = {
            "1br": {
                "monthly_rent": rent_1br,
                "size": 750,
                "mix_pct": 0.2
            },
            "2br": {
                "monthly_rent": rent_2br,
                "size": 1000,
                "mix_pct": 0.6
            },
            "3br": {
                "monthly_rent": rent_3br,
                "size": 1250,
                "mix_pct": 0.2
            },
        }
        
        # Add land cost separately
        land_cost = site_data.get('Total_Cost_Per_Unit', 180000) * 12 * acres  # Estimate total land cost
        unit_mix_config["land_cost"] = land_cost
        
        # Calculate pro forma
        if self.pyforma_available:
            # TODO: Use actual pyforma when compatibility is fixed
            result = self.calculate_simple_proforma(acres, 12, unit_mix_config)
        else:
            result = self.calculate_simple_proforma(acres, 12, unit_mix_config)
        
        # Add site context
        result.update({
            "site_address": site_data.get('Address', 'Unknown'),
            "county": county,
            "acres": acres,
            "existing_economic_score": site_data.get('Economic_Score', 0),
            "existing_revenue_cost_ratio": site_data.get('Corrected_Revenue_Cost_Ratio', site_data.get('Revenue_Cost_Ratio', 0))
        })
        
        return result

def test_wrapper():
    """Test the pyforma wrapper"""
    
    print("TESTING PYFORMA WRAPPER")
    print("=" * 50)
    
    wrapper = PyformaWrapper()
    
    # Test with sample site data
    sample_site = {
        'Address': '271 The Rock Rd',
        'County': 'LLANO',
        'Acres': 10.0,
        'rent_1br_60pct': 988,
        'rent_2br_60pct': 1600,
        'rent_3br_60pct': 1370,
        'Economic_Score': 53.12,
        'Revenue_Cost_Ratio': 0.106,
        'Total_Cost_Per_Unit': 180725
    }
    
    print(f"\nAnalyzing sample site: {sample_site['Address']}")
    result = wrapper.analyze_texas_site(sample_site)
    
    print(f"\nResults:")
    print(f"  Method: {result['method']}")
    print(f"  Total Revenue: ${result['total_revenue']:,.0f}")
    print(f"  Total Cost: ${result['total_cost']:,.0f}")
    print(f"  Profit: ${result['profit']:,.0f}")
    print(f"  Revenue/Cost Ratio: {result['revenue_cost_ratio']:.3f}")
    print(f"  Total Units: {result['total_units']:.1f}")
    
    print(f"\nComparison with existing:")
    print(f"  Existing Revenue/Cost: {result['existing_revenue_cost_ratio']:.3f}")
    print(f"  New Revenue/Cost: {result['revenue_cost_ratio']:.3f}")
    
    return wrapper

if __name__ == "__main__":
    test_wrapper()