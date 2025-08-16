#!/usr/bin/env python3
"""
EPA Geodatabase Processor
Extracts environmental site locations from downloaded .gdb.zip files
Converts to unified CSV/Parquet format for analysis
WINGMAN Federal Environmental Data Mission - Final Processing
Date: 2025-08-09
"""

import zipfile
import geopandas as gpd
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

class EPAGeodatabaseProcessor:
    """Process EPA geodatabase files to extract site locations"""
    
    def __init__(self):
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.epa_data_path = self.base_path / "data_sets" / "federal" / "EPA_Data"
        self.output_path = self.base_path / "data_sets" / "federal" / "EPA_Sites"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        self.processed_sites = []
        self.processing_log = []
        self.start_time = datetime.now()
        
    def find_geodatabases(self):
        """Find all .gdb.zip files in EPA_Data directory"""
        gdb_files = []
        
        for gdb_file in self.epa_data_path.rglob("*.gdb.zip"):
            gdb_files.append({
                'path': gdb_file,
                'category': gdb_file.parent.parent.name if gdb_file.parent.parent != self.epa_data_path else 'Other',
                'region': gdb_file.parent.name,
                'filename': gdb_file.name,
                'size_mb': gdb_file.stat().st_size / (1024 * 1024)
            })
        
        print(f"Found {len(gdb_files)} geodatabase files to process")
        return sorted(gdb_files, key=lambda x: x['size_mb'])  # Process smaller files first
    
    def process_geodatabase(self, gdb_info):
        """Extract environmental sites from a geodatabase"""
        print(f"\nProcessing: {gdb_info['filename']}")
        print(f"  Category: {gdb_info['category']}, Region: {gdb_info['region']}")
        print(f"  Size: {gdb_info['size_mb']:.1f} MB")
        
        try:
            # Extract the geodatabase
            extract_dir = self.output_path / "temp_extract"
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(gdb_info['path'], 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the .gdb directory
            gdb_dirs = list(extract_dir.glob("*.gdb"))
            if not gdb_dirs:
                print("  ⚠️ No .gdb found in archive")
                self.processing_log.append({
                    'file': gdb_info['filename'],
                    'status': 'no_gdb_found'
                })
                return 0
            
            gdb_path = gdb_dirs[0]
            
            # List layers in the geodatabase
            try:
                layers = gpd.list_layers(gdb_path)
                print(f"  Found {len(layers)} layers")
            except:
                print("  ⚠️ Could not read geodatabase layers")
                self.processing_log.append({
                    'file': gdb_info['filename'],
                    'status': 'read_error'
                })
                return 0
            
            sites_extracted = 0
            
            # Process each layer
            for layer_info in layers:
                # Handle both tuple and single value returns
                if isinstance(layer_info, tuple):
                    layer_name = layer_info[0]
                    layer_type = layer_info[1] if len(layer_info) > 1 else 'Unknown'
                else:
                    layer_name = layer_info
                    layer_type = 'Unknown'
                if layer_type in ['Point', 'MultiPoint', 'Polygon', 'MultiPolygon']:
                    try:
                        # Read the layer
                        gdf = gpd.read_file(gdb_path, layer=layer_name)
                        
                        if len(gdf) == 0:
                            continue
                        
                        print(f"    Layer: {layer_name} ({len(gdf)} features)")
                        
                        # Convert to WGS84 if needed
                        if gdf.crs and gdf.crs != 'EPSG:4326':
                            gdf = gdf.to_crs('EPSG:4326')
                        
                        # Extract coordinates
                        if layer_type in ['Point', 'MultiPoint']:
                            gdf['longitude'] = gdf.geometry.x
                            gdf['latitude'] = gdf.geometry.y
                        else:
                            # For polygons, use centroid
                            centroids = gdf.geometry.centroid
                            gdf['longitude'] = centroids.x
                            gdf['latitude'] = centroids.y
                        
                        # Create standardized site records
                        for idx, row in gdf.iterrows():
                            site = {
                                'source_file': gdb_info['filename'],
                                'source_category': gdb_info['category'],
                                'source_region': gdb_info['region'],
                                'layer_name': layer_name,
                                'latitude': row.get('latitude'),
                                'longitude': row.get('longitude'),
                                'site_name': None,
                                'site_id': None,
                                'site_type': gdb_info['category']
                            }
                            
                            # Try to extract site identifiers
                            for field in ['SITE_NAME', 'SiteName', 'NAME', 'Name', 'FACILITY_NAME']:
                                if field in row and pd.notna(row[field]):
                                    site['site_name'] = str(row[field])
                                    break
                            
                            for field in ['SITE_ID', 'SiteID', 'ID', 'FacilityID', 'EPA_ID']:
                                if field in row and pd.notna(row[field]):
                                    site['site_id'] = str(row[field])
                                    break
                            
                            # Add other relevant fields
                            for field in ['STATUS', 'CONTAMINATION', 'CLEANUP_STATUS', 'NPL_STATUS']:
                                if field in row and pd.notna(row[field]):
                                    site[field.lower()] = str(row[field])
                            
                            if pd.notna(site['latitude']) and pd.notna(site['longitude']):
                                self.processed_sites.append(site)
                                sites_extracted += 1
                        
                    except Exception as e:
                        print(f"    ⚠️ Error processing layer {layer_name}: {str(e)[:100]}")
            
            # Clean up temp files
            import shutil
            shutil.rmtree(extract_dir, ignore_errors=True)
            
            print(f"  ✅ Extracted {sites_extracted} sites")
            
            self.processing_log.append({
                'file': gdb_info['filename'],
                'status': 'success',
                'sites_extracted': sites_extracted,
                'layers_processed': len(layers)
            })
            
            return sites_extracted
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:200]}")
            self.processing_log.append({
                'file': gdb_info['filename'],
                'status': 'error',
                'error': str(e)[:200]
            })
            return 0
    
    def process_zip_files(self):
        """Process regular ZIP files that might contain CSV data"""
        zip_files = []
        
        for zip_file in self.epa_data_path.rglob("*.zip"):
            if not zip_file.name.endswith('.gdb.zip'):
                zip_files.append(zip_file)
        
        print(f"\nFound {len(zip_files)} regular ZIP files to check")
        
        for zip_path in zip_files[:10]:  # Process first 10 as sample
            print(f"\nChecking: {zip_path.name}")
            
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Look for CSV files
                    csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
                    
                    if csv_files:
                        print(f"  Found {len(csv_files)} CSV files")
                        
                        for csv_file in csv_files[:2]:  # Sample first 2
                            try:
                                df = pd.read_csv(zip_ref.open(csv_file), nrows=100)
                                
                                # Look for coordinate columns
                                lat_cols = [c for c in df.columns if 'lat' in c.lower()]
                                lon_cols = [c for c in df.columns if 'lon' in c.lower() or 'lng' in c.lower()]
                                
                                if lat_cols and lon_cols:
                                    print(f"    ✓ {csv_file}: Has coordinates ({len(df)} rows sampled)")
                                    # Could process this file for sites
                                    
                            except:
                                pass
            except:
                pass
    
    def create_unified_database(self):
        """Create unified federal EPA sites database"""
        if not self.processed_sites:
            print("\n⚠️ No sites extracted from geodatabases")
            return
        
        # Create DataFrame
        df = pd.DataFrame(self.processed_sites)
        
        # Remove duplicates based on coordinates
        df = df.drop_duplicates(subset=['latitude', 'longitude'], keep='first')
        
        # Add processing metadata
        df['processed_date'] = datetime.now().isoformat()
        df['data_source'] = 'EPA Federal'
        
        print(f"\n📊 Unified Database Statistics:")
        print(f"  Total Sites: {len(df)}")
        print(f"  Categories: {df['source_category'].nunique()}")
        print(f"  Regions: {df['source_region'].nunique()}")
        
        # Category breakdown
        print("\n  Sites by Category:")
        for cat, count in df['source_category'].value_counts().head(10).items():
            print(f"    {cat}: {count}")
        
        # Save to CSV
        csv_file = self.output_path / "epa_federal_sites.csv"
        df.to_csv(csv_file, index=False)
        print(f"\n✅ Saved to: {csv_file.name}")
        
        # Save to Parquet for efficiency
        parquet_file = self.output_path / "epa_federal_sites.parquet"
        df.to_parquet(parquet_file, index=False, compression='snappy')
        print(f"✅ Saved to: {parquet_file.name}")
        
        return df
    
    def generate_processing_report(self):
        """Generate comprehensive processing report"""
        duration = (datetime.now() - self.start_time).total_seconds() / 60
        
        successful = [p for p in self.processing_log if p['status'] == 'success']
        failed = [p for p in self.processing_log if p['status'] != 'success']
        
        report = {
            'processing_date': self.start_time.isoformat(),
            'duration_minutes': round(duration, 1),
            'files_processed': len(self.processing_log),
            'files_successful': len(successful),
            'files_failed': len(failed),
            'total_sites_extracted': len(self.processed_sites),
            'unique_sites': len(set((s['latitude'], s['longitude']) for s in self.processed_sites if s['latitude'] and s['longitude'])),
            'processing_log': self.processing_log
        }
        
        report_file = self.output_path / "geodatabase_processing_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Processing report: {report_file.name}")
        
        return report
    
    def run_processing(self):
        """Main processing pipeline"""
        print("\n" + "="*80)
        print("EPA GEODATABASE PROCESSOR")
        print("Extracting environmental sites from federal data")
        print(f"Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Find geodatabases
        gdb_files = self.find_geodatabases()
        
        if not gdb_files:
            print("\n❌ No geodatabase files found")
            return 0
        
        # Process each geodatabase
        total_sites = 0
        for gdb_info in gdb_files:
            sites = self.process_geodatabase(gdb_info)
            total_sites += sites
            
            # Save progress periodically
            if len(self.processed_sites) > 1000:
                print(f"\n💾 Saving intermediate results ({len(self.processed_sites)} sites)...")
                self.create_unified_database()
        
        # Also check ZIP files
        self.process_zip_files()
        
        # Create final unified database
        if self.processed_sites:
            df = self.create_unified_database()
        
        # Generate report
        report = self.generate_processing_report()
        
        print("\n" + "="*80)
        print("PROCESSING COMPLETE")
        print("="*80)
        print(f"Duration: {report['duration_minutes']:.1f} minutes")
        print(f"Files Processed: {report['files_processed']}")
        print(f"Sites Extracted: {report['total_sites_extracted']}")
        print(f"Unique Locations: {report['unique_sites']}")
        print("="*80)
        
        return total_sites

def main():
    print("\n🔧 EPA GEODATABASE PROCESSOR")
    print("Extracting site locations from federal environmental data")
    print("-"*60)
    
    processor = EPAGeodatabaseProcessor()
    sites = processor.run_processing()
    
    print(f"\n✅ GEODATABASE PROCESSING COMPLETE")
    print(f"Extracted {sites} environmental sites from EPA data")
    print("\nOutput files:")
    print("  - epa_federal_sites.csv")
    print("  - epa_federal_sites.parquet")
    print("  - geodatabase_processing_report.json")

if __name__ == "__main__":
    main()