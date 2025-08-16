#!/usr/bin/env python3
"""
Test pyforma with a single site from our 195 sites data
"""

import pandas as pd
import numpy as np
import pyforma.pyforma as pyforma

def load_single_site():
    """Load data for a single site to test with"""
    
    excel_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/FINAL_195_Sites_Complete_With_Poverty_20250621_213537.xlsx"
    
    try:
        df = pd.read_excel(excel_file, sheet_name='All_195_Sites_Final')
        
        # Pick a site with good data - find one with acres, county, and economic data
        good_sites = df.dropna(subset=['Acres', 'County', 'Economic_Score', 'Annual_Rent_Per_Unit', 'Total_Cost_Per_Unit'])
        
        if len(good_sites) == 0:
            print("❌ No sites with complete data found")
            return None
        
        # Take the first good site
        site = good_sites.iloc[0]
        
        print(f"Selected test site:")
        print(f"  Address: {site['Address']}")
        print(f"  City: {site['City']}, {site['County']} County")
        print(f"  Acres: {site['Acres']}")
        print(f"  Existing Annual Rent/Unit: ${site['Annual_Rent_Per_Unit']:,.0f}")
        print(f"  Existing Total Cost/Unit: ${site['Total_Cost_Per_Unit']:,.0f}")
        print(f"  Existing Economic Score: {site['Economic_Score']:.2f}")
        
        return site
        
    except Exception as e:
        print(f"❌ Error loading single site: {e}")
        return None

def build_pyforma_config(site):
    """Build pyforma configuration for the selected site"""
    
    print(f"\nBuilding pyforma configuration...")
    
    # Convert acres to square feet
    parcel_sqft = site['Acres'] * 43560
    
    # Use existing rent data for unit mix - we have 1BR, 2BR, 3BR rents
    rent_1br = site.get('rent_1br_60pct', 800)  # Default if missing
    rent_2br = site.get('rent_2br_60pct', 1000)
    rent_3br = site.get('rent_3br_60pct', 1200)
    
    # Convert monthly rent to price per sqft (assuming typical unit sizes)
    # Typical sizes: 1BR=750sf, 2BR=1000sf, 3BR=1250sf
    price_1br_sqft = rent_1br / 750
    price_2br_sqft = rent_2br / 1000
    price_3br_sqft = rent_3br / 1250
    
    config = {
        "use_types": {
            "1br": {
                "price_per_sqft": price_1br_sqft,
                "size": 750,
                "parking_ratio": 1.0
            },
            "2br": {
                "price_per_sqft": price_2br_sqft, 
                "size": 1000,
                "parking_ratio": 1.5
            },
            "3br": {
                "price_per_sqft": price_3br_sqft,
                "size": 1250,
                "parking_ratio": 2.0
            }
        },
        "use_mix": [0.2, 0.6, 0.2],  # 20% 1BR, 60% 2BR, 20% 3BR (typical LIHTC mix)
        "parcel_size": parcel_sqft,
        "building_type": "garden_apartments",  # Typical for LIHTC
        "built_dua": 12,  # Start with 12 dwelling units per acre
        "affordable_housing": {
            "AMI": site.get('median_ami_2025', 60000),  # Area Median Income
            "depth_of_affordability": 0.60,  # 60% AMI for LIHTC
            "pct_affordable_units": 1.0  # 100% affordable for LIHTC
        }
    }
    
    print(f"  Parcel size: {parcel_sqft:,.0f} sqft ({site['Acres']:.1f} acres)")
    print(f"  Unit mix pricing:")
    print(f"    1BR: ${rent_1br}/month (${price_1br_sqft:.2f}/sqft)")
    print(f"    2BR: ${rent_2br}/month (${price_2br_sqft:.2f}/sqft)")
    print(f"    3BR: ${rent_3br}/month (${price_3br_sqft:.2f}/sqft)")
    print(f"  Target density: {config['built_dua']} units/acre")
    print(f"  AMI: ${config['affordable_housing']['AMI']:,.0f}")
    
    return config

def run_pyforma_analysis(config):
    """Run pyforma analysis with the configuration"""
    
    print(f"\nRunning pyforma analysis...")
    
    try:
        # Run the analysis
        result = pyforma.spot_residential_sales_proforma(config)
        
        print(f"✅ pyforma analysis completed successfully!")
        print(f"Result type: {type(result)}")
        print(f"Number of result keys: {len(result.keys())}")
        
        # Show key results
        key_metrics = [
            'built_far', 'num_units_by_type', 'usable_floor_area', 
            'floor_area_including_common_space', 'total_revenue', 
            'total_cost', 'profit', 'profit_per_sqft'
        ]
        
        print(f"\nKey results:")
        for metric in key_metrics:
            if metric in result:
                value = result[metric]
                if isinstance(value, (int, float)):
                    if 'revenue' in metric or 'cost' in metric or 'profit' in metric:
                        print(f"  {metric}: ${value:,.0f}")
                    else:
                        print(f"  {metric}: {value}")
                else:
                    print(f"  {metric}: {value}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error running pyforma analysis: {e}")
        return None

def compare_with_existing(site, pyforma_result):
    """Compare pyforma results with existing calculations"""
    
    if pyforma_result is None:
        return
    
    print(f"\n" + "=" * 60)
    print(f"COMPARISON: pyforma vs Existing Analysis")
    print(f"=" * 60)
    
    # Extract pyforma results
    pf_units = sum(pyforma_result.get('num_units_by_type', [0]))
    pf_revenue = pyforma_result.get('total_revenue', 0)
    pf_cost = pyforma_result.get('total_cost', 0)
    pf_profit = pyforma_result.get('profit', 0)
    
    # Calculate per-unit metrics from pyforma
    if pf_units > 0:
        pf_revenue_per_unit = pf_revenue / pf_units
        pf_cost_per_unit = pf_cost / pf_units
        pf_profit_per_unit = pf_profit / pf_units
    else:
        pf_revenue_per_unit = pf_cost_per_unit = pf_profit_per_unit = 0
    
    # Existing calculations
    existing_revenue_per_unit = site.get('Annual_Rent_Per_Unit', 0)
    existing_cost_per_unit = site.get('Total_Cost_Per_Unit', 0)
    existing_profit_per_unit = existing_revenue_per_unit - existing_cost_per_unit
    existing_ratio = site.get('Revenue_Cost_Ratio', 0)
    
    print(f"REVENUE PER UNIT:")
    print(f"  pyforma:  ${pf_revenue_per_unit:,.0f}")
    print(f"  Existing: ${existing_revenue_per_unit:,.0f}")
    if existing_revenue_per_unit > 0:
        diff_pct = ((pf_revenue_per_unit - existing_revenue_per_unit) / existing_revenue_per_unit) * 100
        print(f"  Difference: {diff_pct:+.1f}%")
    
    print(f"\nCOST PER UNIT:")
    print(f"  pyforma:  ${pf_cost_per_unit:,.0f}")
    print(f"  Existing: ${existing_cost_per_unit:,.0f}")
    if existing_cost_per_unit > 0:
        diff_pct = ((pf_cost_per_unit - existing_cost_per_unit) / existing_cost_per_unit) * 100
        print(f"  Difference: {diff_pct:+.1f}%")
    
    print(f"\nPROFIT PER UNIT:")
    print(f"  pyforma:  ${pf_profit_per_unit:,.0f}")
    print(f"  Existing: ${existing_profit_per_unit:,.0f}")
    
    print(f"\nREVENUE/COST RATIO:")
    if pf_cost_per_unit > 0:
        pf_ratio = pf_revenue_per_unit / pf_cost_per_unit
        print(f"  pyforma:  {pf_ratio:.3f}")
    print(f"  Existing: {existing_ratio:.3f}")
    
    print(f"\nUNIT COUNT:")
    print(f"  pyforma units: {pf_units}")
    print(f"  Target density: {12} units/acre on {site['Acres']:.1f} acres = {12 * site['Acres']:.0f} units")

if __name__ == "__main__":
    print("PYFORMA SINGLE SITE TEST")
    print("=" * 60)
    
    # Load a test site
    site = load_single_site()
    if site is None:
        exit(1)
    
    # Build pyforma configuration
    config = build_pyforma_config(site)
    
    # Run analysis
    result = run_pyforma_analysis(config)
    
    # Compare results
    compare_with_existing(site, result)
    
    print(f"\n🎉 Single site test complete!")
    print(f"Next step: Scale to all 195 sites using vectorized analysis.")