#!/usr/bin/env python3
"""
Compare datasets to understand what happened to Northern California properties
"""

import pandas as pd
import numpy as np

def compare_datasets():
    """Compare the original combined dataset with the backup we've been using"""
    
    print("🔍 COMPARING DATASETS TO FIND NORTHERN CALIFORNIA PROPERTIES")
    print("=" * 70)
    
    # Load both datasets
    original_file = "CostarExport_AllLand_Combined_20250727_184937.xlsx"
    backup_file = "CostarExport_HighResource_BACKUP_20250730_090645.xlsx"
    
    try:
        print(f"📊 Loading original dataset: {original_file}")
        df_original = pd.read_excel(original_file)
        print(f"   Original dataset: {len(df_original)} sites")
        
        print(f"📊 Loading backup dataset: {backup_file}")
        df_backup = pd.read_excel(backup_file)
        print(f"   Backup dataset: {len(df_backup)} sites")
        
        # Check geographic distribution
        print(f"\n🗺️ GEOGRAPHIC ANALYSIS:")
        
        # Original dataset geographic distribution
        original_with_coords = df_original[df_original[['Latitude', 'Longitude']].notna().all(axis=1)]
        print(f"\n📍 Original dataset coordinates:")
        print(f"   Sites with coordinates: {len(original_with_coords)}")
        
        if len(original_with_coords) > 0:
            print(f"   Latitude range: {original_with_coords['Latitude'].min():.4f} to {original_with_coords['Latitude'].max():.4f}")
            print(f"   Longitude range: {original_with_coords['Longitude'].min():.4f} to {original_with_coords['Longitude'].max():.4f}")
            
            # Northern California is roughly above latitude 37.0
            northern_ca = original_with_coords[original_with_coords['Latitude'] > 37.0]
            southern_ca = original_with_coords[original_with_coords['Latitude'] <= 37.0]
            
            print(f"   Northern CA (lat > 37.0): {len(northern_ca)} sites")
            print(f"   Southern CA (lat <= 37.0): {len(southern_ca)} sites")
            
            if len(northern_ca) > 0:
                print(f"\n🌉 NORTHERN CA SAMPLE SITES (from original):")
                for i, (_, site) in enumerate(northern_ca.head(5).iterrows()):
                    addr = site.get('Property Address', 'Unknown')[:50]
                    lat = site.get('Latitude', 'N/A')
                    print(f"   {i+1}. {addr} (Lat: {lat})")
        
        # Backup dataset geographic distribution
        backup_with_coords = df_backup[df_backup[['Latitude', 'Longitude']].notna().all(axis=1)]
        print(f"\n📍 Backup dataset coordinates:")
        print(f"   Sites with coordinates: {len(backup_with_coords)}")
        
        if len(backup_with_coords) > 0:
            print(f"   Latitude range: {backup_with_coords['Latitude'].min():.4f} to {backup_with_coords['Latitude'].max():.4f}")
            print(f"   Longitude range: {backup_with_coords['Longitude'].min():.4f} to {backup_with_coords['Longitude'].max():.4f}")
            
            northern_ca_backup = backup_with_coords[backup_with_coords['Latitude'] > 37.0]
            southern_ca_backup = backup_with_coords[backup_with_coords['Latitude'] <= 37.0]
            
            print(f"   Northern CA (lat > 37.0): {len(northern_ca_backup)} sites")
            print(f"   Southern CA (lat <= 37.0): {len(southern_ca_backup)} sites")
        
        # Check if there are differences in column names
        print(f"\n📋 COLUMN COMPARISON:")
        original_cols = set(df_original.columns)
        backup_cols = set(df_backup.columns)
        
        print(f"   Original columns: {len(original_cols)}")
        print(f"   Backup columns: {len(backup_cols)}")
        
        missing_in_backup = original_cols - backup_cols
        missing_in_original = backup_cols - original_cols
        
        if missing_in_backup:
            print(f"   Columns in original but not backup: {list(missing_in_backup)}")
        if missing_in_original:
            print(f"   Columns in backup but not original: {list(missing_in_original)}")
        
        # Check state distribution if there's a state column
        state_columns = [col for col in df_original.columns if 'state' in col.lower()]
        if state_columns:
            print(f"\n🏛️ STATE DISTRIBUTION (using {state_columns[0]}):")
            state_col = state_columns[0]
            
            print(f"   Original dataset states:")
            orig_states = df_original[state_col].value_counts(dropna=False)
            for state, count in orig_states.head(10).items():
                print(f"      {state}: {count}")
            
            print(f"   Backup dataset states:")
            backup_states = df_backup[state_col].value_counts(dropna=False) if state_col in df_backup.columns else "Column not found"
            if isinstance(backup_states, pd.Series):
                for state, count in backup_states.head(10).items():
                    print(f"      {state}: {count}")
            else:
                print(f"      {backup_states}")
        
        # Look for Northern California cities/counties
        print(f"\n🌉 LOOKING FOR NORTHERN CA INDICATORS:")
        
        # Check for Bay Area cities/counties
        northern_indicators = [
            'san francisco', 'oakland', 'san jose', 'berkeley', 'palo alto', 
            'sacramento', 'fresno', 'stockton', 'modesto', 'santa rosa',
            'alameda', 'contra costa', 'marin', 'napa', 'sonoma', 'solano'
        ]
        
        address_columns = [col for col in df_original.columns if 'address' in col.lower() or 'city' in col.lower() or 'county' in col.lower()]
        
        for col in address_columns:
            print(f"\n   Checking column: {col}")
            col_values = df_original[col].astype(str).str.lower()
            
            for indicator in northern_indicators:
                matches = col_values.str.contains(indicator, na=False).sum()
                if matches > 0:
                    print(f"      Found '{indicator}': {matches} sites")
    
    except Exception as e:
        print(f"❌ Error comparing datasets: {e}")

if __name__ == "__main__":
    compare_datasets()