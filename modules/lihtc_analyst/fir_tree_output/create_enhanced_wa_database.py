#!/usr/bin/env python3
"""
Create enhanced WA LIHTC database with coordinate columns and improved structure
Start with a framework and add coordinates for key projects first
"""

import pandas as pd
from datetime import datetime

def create_enhanced_database():
    """Create the enhanced database structure with coordinate columns"""
    
    print("🏛️ CREATING ENHANCED WA LIHTC DATABASE")
    print("=" * 50)
    
    input_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/Data_Sets/washington/lihtc_projects/Big TC List for website_2-6-25.xlsx"
    output_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/Data_Sets/washington/lihtc_projects/WA_LIHTC_Enhanced_with_Coordinates_2025.xlsx"
    
    try:
        # Load original database
        print("📊 Loading original database...")
        df = pd.read_excel(input_path)
        
        print(f"✅ Loaded {len(df)} projects")
        print(f"📍 Original columns: {len(df.columns)}")
        
        # Add coordinate and analysis columns
        df['Latitude'] = None
        df['Longitude'] = None
        df['Geocoding_Source'] = None
        df['Geocoding_Date'] = None
        df['Distance_to_Seattle_Miles'] = None
        df['Distance_to_Spokane_Miles'] = None
        df['Rural_Classification'] = None
        
        print(f"🔧 Enhanced columns: {len(df.columns)} (+7 new columns)")
        
        # Add known coordinates for key projects (starting with Shelton)
        print(f"\n📍 Adding known coordinates for key projects...")
        
        # Shelton projects (we already geocoded these)
        shelton_coords = {
            'Creekside Apartments': (47.209760862643, -123.105589991796, 'Manual Entry'),
            'Harmony House': (47.220662552818, -123.113351913034, 'Manual Entry'),  
            'Kneeland Park': (47.208122681021, -123.102238336428, 'Manual Entry')
        }
        
        for project_name, (lat, lon, source) in shelton_coords.items():
            mask = df['Property Name'] == project_name
            if mask.any():
                df.loc[mask, 'Latitude'] = lat
                df.loc[mask, 'Longitude'] = lon
                df.loc[mask, 'Geocoding_Source'] = source
                df.loc[mask, 'Geocoding_Date'] = datetime.now().strftime('%Y-%m-%d')
                print(f"   ✅ {project_name}: {lat}, {lon}")
        
        # Add Fir Tree Park for reference (not in LIHTC database but useful for analysis)
        fir_tree_row = {
            'WSHFC Unique ID #': 'FIR-TREE-REF',
            'Property Name': 'Fir Tree Park Apartments (Reference)',
            'Property Address': '614 North 4th Street',
            'Property City': 'Shelton',
            'Property Zip Code': '98584',
            'Property County': 'Mason',
            'TOTAL Units': 60,
            'Elderly Setaside': 60,  # All senior housing
            '1BR': 60,  # All 1-bedroom
            'First Credit Year': 'N/A (Pre-LIHTC)',
            'Latitude': 47.2172038,
            'Longitude': -123.1027976,
            'Geocoding_Source': 'Manual Entry - Reference Property',
            'Geocoding_Date': datetime.now().strftime('%Y-%m-%d'),
            'Rural_Classification': 'Rural'
        }
        
        # Add Fir Tree as reference row
        fir_tree_df = pd.DataFrame([fir_tree_row])
        df = pd.concat([df, fir_tree_df], ignore_index=True)
        
        print(f"   ✅ Added Fir Tree Park as reference property")
        
        # Generate summary
        geocoded_count = df['Latitude'].notna().sum()
        
        print(f"\n📊 ENHANCED DATABASE SUMMARY:")
        print(f"   Total Projects: {len(df)} (+1 reference)")
        print(f"   Geocoded Projects: {geocoded_count}")
        print(f"   Total Columns: {len(df.columns)}")
        print(f"   New Columns: Latitude, Longitude, Geocoding_Source, Geocoding_Date,")
        print(f"                Distance_to_Seattle_Miles, Distance_to_Spokane_Miles, Rural_Classification")
        
        # Save enhanced database
        df.to_excel(output_path, index=False)
        
        print(f"\n💾 ENHANCED DATABASE CREATED:")
        print(f"   📁 File: WA_LIHTC_Enhanced_with_Coordinates_2025.xlsx") 
        print(f"   📍 Location: Data_Sets/washington/lihtc_projects/")
        print(f"   🚀 Ready for batch geocoding when needed")
        
        # Show structure of enhanced database
        print(f"\n📋 DATABASE STRUCTURE PREVIEW:")
        key_columns = ['Property Name', 'Property City', 'TOTAL Units', 'Elderly Setaside', 
                      'First Credit Year', 'Latitude', 'Longitude']
        
        sample = df[df['Latitude'].notna()][key_columns].head()
        print(sample.to_string(index=False))
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    create_enhanced_database()