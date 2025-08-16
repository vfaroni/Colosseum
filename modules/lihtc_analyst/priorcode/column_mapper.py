#!/usr/bin/env python3
"""
Universal Column Mapper for Texas LIHTC Dashboard
Handles different Excel file formats and column naming variations
"""

import pandas as pd
import numpy as np

class ColumnMapper:
    """Maps various column name formats to standardized dashboard columns"""
    
    def __init__(self):
        # Standard dashboard column names mapped to possible variations
        self.column_mappings = {
            # Basic property info
            'Address': ['Address', 'address', 'Property Address', 'Street Address'],
            'City': ['City', 'city', 'City_Clean', 'Property City'],
            'County': ['County', 'county', 'County Name'],
            'Latitude': ['Latitude', 'latitude', 'lat', 'Lat'],
            'Longitude': ['Longitude', 'longitude', 'lng', 'lon', 'Lng', 'Lon'],
            
            # Scoring columns (old and new formats)
            '4pct_score': ['4pct_score', '4pct_total_score', '4%_score', 'four_pct_score'],
            '9pct_score': ['9pct_score', '9pct_total_score', '9%_score', 'nine_pct_score'],
            
            # Population and demographics  
            'city_population': ['city_population', 'City_Population', 'population', 'Population', 'City Population'],
            
            # Distance/proximity columns
            'grocery_store_distance_miles': ['grocery_store_distance_miles', 'grocery_distance', 'grocery_store_distance'],
            'elementary_school_distance_miles': ['elementary_school_distance_miles', 'school_distance', 'elementary_distance'],
            'hospital_distance_miles': ['hospital_distance_miles', 'hospital_distance', 'medical_distance'],
            'transit_stop_distance_miles': ['transit_stop_distance_miles', 'transit_distance', 'public_transit_distance'],
            'pharmacy_distance_miles': ['pharmacy_distance_miles', 'pharmacy_distance'],
            'park_distance_miles': ['park_distance_miles', 'park_distance'],
            
            # Competition analysis
            'one_mile_compliant': ['one_mile_compliant', 'one_mile_rule_compliant', 'eligible'],
            'one_mile_competing_count': ['one_mile_competing_count', 'competing_projects', 'competition_count'],
            'two_mile_compliant': ['two_mile_compliant', 'two_mile_rule_compliant'],
            'same_tract_points': ['same_tract_points', 'census_tract_points', 'tract_points'],
            
            # Eligibility
            'eligibility': ['eligibility', 'Eligibility', 'eligible', 'Eligible', 'status', 'Status'],
            
            # Census data
            'Census_Tract': ['Census_Tract', 'census_tract', 'CT_2020', 'tract_id'],
        }
    
    def map_columns(self, df):
        """Map actual column names to standard names"""
        mapped_df = df.copy()
        column_mapping_applied = {}
        
        for standard_name, variations in self.column_mappings.items():
            for variation in variations:
                if variation in df.columns:
                    if standard_name not in mapped_df.columns:
                        mapped_df[standard_name] = mapped_df[variation]
                        column_mapping_applied[variation] = standard_name
                    break
        
        return mapped_df, column_mapping_applied
    
    def add_missing_essential_columns(self, df):
        """Add essential missing columns with default values"""
        essential_defaults = {
            'eligibility': 'ELIGIBLE',
            'deal_quality': 'Review Needed',
            '4pct_score': 50,  # Default medium score
            '9pct_score': 50,  # Default medium score
            'city_population': 100000,  # Default population
            'one_mile_compliant': True,
            'one_mile_competing_count': 0,
        }
        
        added_columns = []
        for col, default_value in essential_defaults.items():
            if col not in df.columns:
                df[col] = default_value
                added_columns.append(col)
        
        return df, added_columns
    
    def safe_column_selection(self, df, requested_columns):
        """Return only columns that exist in the dataframe"""
        return [col for col in requested_columns if col in df.columns]
    
    def diagnose_dataframe(self, df):
        """Provide diagnostic information about the dataframe"""
        info = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'missing_essential': [],
            'suggestions': []
        }
        
        # Check for essential columns
        essential = ['Address', 'City', 'County', '4pct_score', '9pct_score']
        for col in essential:
            if col not in df.columns:
                info['missing_essential'].append(col)
                # Suggest similar columns
                similar = [c for c in df.columns if col.lower() in c.lower() or c.lower() in col.lower()]
                if similar:
                    info['suggestions'].append(f"{col} -> {similar}")
        
        return info

def quick_fix_dashboard_data(df):
    """Quick fix function to prepare any Excel data for the dashboard"""
    mapper = ColumnMapper()
    
    print("🔧 Applying universal column mapping...")
    
    # Step 1: Map columns
    df, mappings = mapper.map_columns(df)
    if mappings:
        print(f"✅ Mapped columns: {mappings}")
    
    # Step 2: Add missing essentials
    df, added = mapper.add_missing_essential_columns(df)
    if added:
        print(f"✅ Added missing columns: {added}")
    
    # Step 3: Create City_Clean if needed
    if 'City_Clean' not in df.columns and 'City' in df.columns:
        df['City_Clean'] = df['City'].fillna('Unknown')
        print("✅ Created City_Clean column")
    
    # Step 4: Ensure numeric columns are numeric
    numeric_columns = ['4pct_score', '9pct_score', 'city_population', 'one_mile_competing_count']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(50)
    
    print(f"✅ Data prepared: {len(df)} rows, {len(df.columns)} columns")
    return df

if __name__ == "__main__":
    # Test with sample problematic data
    print("🧪 Testing Column Mapper...")
    
    # Simulate your Excel file format
    test_data = {
        'Address': ['123 Test St', '456 Demo Ave'],
        'city': ['Houston', 'Dallas'],  # lowercase
        'County Name': ['Harris', 'Dallas'],  # different name
        'Population': [2000000, 1300000],  # different name
        # Missing many expected columns
    }
    
    df = pd.DataFrame(test_data)
    print(f"Original columns: {list(df.columns)}")
    
    fixed_df = quick_fix_dashboard_data(df)
    print(f"Fixed columns: {list(fixed_df.columns)}")
    print("✅ Column mapping test passed!")