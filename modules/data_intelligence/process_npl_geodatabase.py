#!/usr/bin/env python3
"""
Process EPA NPL Geodatabase
Extracts Superfund site data from ESRI geodatabase
WINGMAN Federal Environmental Data Mission
Date: 2025-08-10
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import json
from datetime import datetime
import fiona

class NPLProcessor:
    """Process National Priorities List geodatabase"""
    
    def __init__(self):
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.gdb_path = self.base_path / "data_sets/federal/EPA_Superfund/NPL/NationalPrioritiesList.gdb"
        self.output_path = self.base_path / "data_sets/federal/EPA_Superfund"
        
    def explore_geodatabase(self):
        """Explore geodatabase contents"""
        print("\n" + "="*80)
        print("EXPLORING NPL GEODATABASE")
        print("="*80)
        
        try:
            # List all layers in the geodatabase
            layers = fiona.listlayers(str(self.gdb_path))
            
            print(f"\nFound {len(layers)} layers in geodatabase:")
            for i, layer in enumerate(layers, 1):
                print(f"  {i}. {layer}")
                
                # Get info about each layer
                with fiona.open(str(self.gdb_path), layer=layer) as src:
                    print(f"     - Records: {len(src)}")
                    print(f"     - CRS: {src.crs}")
                    
                    # Show first record's properties
                    if len(src) > 0:
                        first = next(iter(src))
                        props = list(first['properties'].keys())
                        print(f"     - Fields ({len(props)}): {', '.join(props[:5])}...")
            
            return layers
            
        except Exception as e:
            print(f"Error exploring geodatabase: {e}")
            print("This may require GDAL/OGR installation")
            return None
    
    def extract_npl_sites(self):
        """Extract NPL site data from geodatabase"""
        print("\n" + "="*80)
        print("EXTRACTING NPL SUPERFUND SITES")
        print("="*80)
        
        try:
            # Try to read the main NPL layer
            # Common layer names in NPL geodatabase
            possible_layers = [
                'NPL_Sites', 'NPL_Points', 'NPL', 'Sites', 
                'National_Priorities_List', 'Superfund_Sites'
            ]
            
            gdf = None
            layer_name = None
            
            # Try each possible layer name
            for layer in possible_layers:
                try:
                    print(f"Trying layer: {layer}")
                    gdf = gpd.read_file(str(self.gdb_path), layer=layer)
                    layer_name = layer
                    print(f"✅ Successfully read layer: {layer}")
                    break
                except:
                    continue
            
            # If no specific layer worked, try reading the whole GDB
            if gdf is None:
                print("Trying to read entire geodatabase...")
                gdf = gpd.read_file(str(self.gdb_path))
                layer_name = "default"
            
            if gdf is not None and len(gdf) > 0:
                print(f"\n✅ Extracted {len(gdf)} NPL sites")
                print(f"Columns: {', '.join(gdf.columns[:10])}")
                
                # Convert to regular dataframe for processing
                df = pd.DataFrame(gdf.drop(columns='geometry'))
                
                # Extract coordinates if geometry exists
                if 'geometry' in gdf.columns:
                    df['LONGITUDE'] = gdf.geometry.x
                    df['LATITUDE'] = gdf.geometry.y
                
                # Save as CSV
                csv_file = self.output_path / "npl_sites_extracted.csv"
                df.to_csv(csv_file, index=False)
                print(f"\n✅ Saved {len(df)} NPL sites to CSV")
                
                # Create summary
                self.create_summary(df)
                
                return df
            else:
                print("❌ Could not extract NPL data from geodatabase")
                return None
                
        except Exception as e:
            print(f"Error extracting NPL sites: {e}")
            print("\nThis requires geopandas and GDAL. Installing:")
            print("pip install geopandas")
            print("brew install gdal")
            return None
    
    def create_summary(self, df):
        """Create summary of NPL data"""
        
        # Identify key columns
        site_name_col = None
        state_col = None
        status_col = None
        
        # Common column name variations
        for col in df.columns:
            col_lower = col.lower()
            if 'name' in col_lower and site_name_col is None:
                site_name_col = col
            if 'state' in col_lower and state_col is None:
                state_col = col
            if 'status' in col_lower and status_col is None:
                status_col = col
        
        summary = {
            'extraction_date': datetime.now().isoformat(),
            'total_sites': len(df),
            'columns': list(df.columns),
            'has_coordinates': 'LATITUDE' in df.columns and 'LONGITUDE' in df.columns
        }
        
        if state_col:
            summary['states'] = df[state_col].nunique()
            summary['sites_by_state'] = df[state_col].value_counts().head(10).to_dict()
        
        if status_col:
            summary['sites_by_status'] = df[status_col].value_counts().to_dict()
        
        # Save summary
        with open(self.output_path / "npl_extraction_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\n" + "="*60)
        print("NPL DATA SUMMARY")
        print("="*60)
        print(f"Total Sites: {summary['total_sites']}")
        if 'states' in summary:
            print(f"States Covered: {summary['states']}")
        if 'sites_by_status' in summary:
            print("\nSites by Status:")
            for status, count in summary['sites_by_status'].items():
                print(f"  - {status}: {count}")
        print("="*60)
    
    def run(self):
        """Execute NPL processing"""
        print("\nNPL GEODATABASE PROCESSOR")
        print("Processing EPA Superfund National Priorities List")
        
        # First explore the geodatabase
        layers = self.explore_geodatabase()
        
        if layers:
            # Extract NPL sites
            df = self.extract_npl_sites()
            
            if df is not None:
                return df
        
        # If geodatabase processing fails, try alternative
        print("\n⚠️ Geodatabase processing requires GDAL/geopandas")
        print("Alternative: Use the sample data or manual export")
        
        return None

def main():
    processor = NPLProcessor()
    df = processor.run()
    
    if df is not None:
        print(f"\n✅ SUCCESS: Processed {len(df)} NPL sites")
    else:
        print("\n⚠️ Could not process geodatabase")
        print("Install requirements: pip install geopandas fiona")

if __name__ == "__main__":
    main()