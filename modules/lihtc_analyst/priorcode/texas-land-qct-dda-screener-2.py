#!/usr/bin/env python3
"""
QCT/DDA Pre-screening Script for Texas Land Properties
Uses Positionstack API for fast geocoding
Checks if properties are in Qualified Census Tracts or Difficult Development Areas
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import requests
import time
from pathlib import Path
import json
from datetime import datetime
import os

class QCTDDAScreener:
    def __init__(self, positionstack_api_key=None):
        # Get API key from parameter or environment variable
        self.positionstack_api_key = positionstack_api_key or os.environ.get('POSITIONSTACK_API_KEY')
        if not self.positionstack_api_key:
            raise ValueError("Positionstack API key required! Set it as parameter or POSITIONSTACK_API_KEY environment variable")
        
        # Paths to QCT/DDA shapefiles
        self.base_hud_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD DDA QCT")
        self.qct_file = self.base_hud_path / "QUALIFIED_CENSUS_TRACTS_7341711606021821459.gpkg"
        self.dda_file = self.base_hud_path / "Difficult_Development_Areas_-4200740390724245794.gpkg"
        
        # Load shapefiles
        self.qct_data = None
        self.dda_data = None
        self.load_hud_designation_data()
        
        # Cache for geocoding results
        self.cache_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/qct_dda_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Track API usage
        self.api_calls = 0
        
    def load_hud_designation_data(self):
        """Load QCT/DDA shapefiles"""
        try:
            # Load QCT data
            if self.qct_file.exists():
                self.qct_data = gpd.read_file(self.qct_file)
                if self.qct_data.crs != 'EPSG:4326':
                    self.qct_data = self.qct_data.to_crs('EPSG:4326')
                print(f"✅ Loaded QCT data: {len(self.qct_data)} features")
            else:
                print(f"❌ QCT file not found: {self.qct_file}")
            
            # Load DDA data
            if self.dda_file.exists():
                self.dda_data = gpd.read_file(self.dda_file)
                if self.dda_data.crs != 'EPSG:4326':
                    self.dda_data = self.dda_data.to_crs('EPSG:4326')
                print(f"✅ Loaded DDA data: {len(self.dda_data)} features")
            else:
                print(f"❌ DDA file not found: {self.dda_file}")
                
        except Exception as e:
            print(f"⚠️ Error loading HUD designation data: {e}")
    
    def geocode_with_positionstack(self, address, city, state, zip_code):
        """Geocode address using Positionstack API"""
        
        # Create full address
        full_address = f"{address}, {city}, {state} {zip_code}".strip()
        
        # Check cache first
        cache_key = f"geocode_ps_{hash(full_address)}"
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                    print(f"  📋 Using cached geocode result")
                    return cached
            except:
                pass
        
        # Call Positionstack API
        try:
            url = "http://api.positionstack.com/v1/forward"
            params = {
                'access_key': self.positionstack_api_key,
                'query': full_address,
                'country': 'US',
                'region': 'Texas',
                'limit': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.api_calls += 1
            
            if data.get('data') and len(data['data']) > 0:
                location = data['data'][0]
                result = {
                    "success": True,
                    "latitude": location['latitude'],
                    "longitude": location['longitude'],
                    "confidence": location.get('confidence', 0),
                    "matched_address": location.get('label', full_address),
                    "county": location.get('county', ''),
                    "api_response": location  # Store full response for debugging
                }
                
                # Cache the result
                with open(cache_file, 'w') as f:
                    json.dump(result, f)
                
                return result
            else:
                print(f"  ⚠️ No results from Positionstack for: {full_address}")
                return {"success": False, "error": "No results found"}
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"  ❌ Rate limit reached. Waiting 60 seconds...")
                time.sleep(60)
                return self.geocode_with_positionstack(address, city, state, zip_code)  # Retry
            else:
                print(f"  ❌ Positionstack API error: {e}")
                return {"success": False, "error": f"API error: {e}"}
        except Exception as e:
            print(f"  ❌ Geocoding error: {e}")
            return {"success": False, "error": str(e)}
    
    def check_qct_dda_status(self, latitude, longitude):
        """Check if coordinates are in QCT or DDA"""
        status = {
            "qct_status": False,
            "dda_status": False,
            "federal_basis_boost": False,
            "qct_name": None,
            "dda_name": None
        }
        
        try:
            point = Point(longitude, latitude)
            
            # Check QCT status
            if self.qct_data is not None:
                qct_intersects = self.qct_data[self.qct_data.contains(point)]
                if not qct_intersects.empty:
                    status["qct_status"] = True
                    status["federal_basis_boost"] = True
                    qct_row = qct_intersects.iloc[0]
                    status["qct_name"] = qct_row.get('NAME', 'QCT Area')
            
            # Check DDA status
            if self.dda_data is not None:
                dda_intersects = self.dda_data[self.dda_data.contains(point)]
                if not dda_intersects.empty:
                    status["dda_status"] = True
                    status["federal_basis_boost"] = True
                    dda_row = dda_intersects.iloc[0]
                    status["dda_name"] = dda_row.get('DDA_NAME', 'DDA Area')
        
        except Exception as e:
            print(f"  ⚠️ Error checking QCT/DDA status: {e}")
        
        return status
    
    def process_properties(self, input_file, output_file, batch_size=10):
        """Process all properties in the Excel file"""
        
        start_time = datetime.now()
        print(f"\n🚀 Starting QCT/DDA pre-screening with Positionstack API...")
        print(f"Input file: {input_file}")
        print(f"Batch processing: {batch_size} properties at a time")
        
        # Read Excel file
        df = pd.read_excel(input_file)
        total_properties = len(df)
        print(f"Total properties to process: {total_properties}")
        
        # Add new columns for results
        df['Latitude'] = None
        df['Longitude'] = None
        df['Geocoding_Success'] = False
        df['Geocoding_Confidence'] = None
        df['QCT_Status'] = False
        df['DDA_Status'] = False
        df['Federal_Basis_Boost'] = False
        df['QCT_Name'] = None
        df['DDA_Name'] = None
        df['Processing_Error'] = None
        
        # Process each property
        successful_geocodes = 0
        qct_properties = 0
        dda_properties = 0
        federal_boost_properties = 0
        
        for idx, row in df.iterrows():
            print(f"\n--- Processing {idx + 1}/{total_properties} ---")
            print(f"Address: {row['Address']}, {row['City']}, {row['State']} {row['Zip']}")
            
            try:
                # Geocode address with Positionstack
                geocode_result = self.geocode_with_positionstack(
                    row['Address'], 
                    row['City'], 
                    row['State'], 
                    row['Zip']
                )
                
                if geocode_result['success']:
                    successful_geocodes += 1
                    lat = geocode_result['latitude']
                    lon = geocode_result['longitude']
                    confidence = geocode_result.get('confidence', 0)
                    
                    df.at[idx, 'Latitude'] = lat
                    df.at[idx, 'Longitude'] = lon
                    df.at[idx, 'Geocoding_Success'] = True
                    df.at[idx, 'Geocoding_Confidence'] = confidence
                    
                    print(f"  ✅ Geocoded: {lat:.6f}, {lon:.6f} (confidence: {confidence:.2f})")
                    
                    # Check QCT/DDA status
                    qct_dda_status = self.check_qct_dda_status(lat, lon)
                    
                    df.at[idx, 'QCT_Status'] = qct_dda_status['qct_status']
                    df.at[idx, 'DDA_Status'] = qct_dda_status['dda_status']
                    df.at[idx, 'Federal_Basis_Boost'] = qct_dda_status['federal_basis_boost']
                    df.at[idx, 'QCT_Name'] = qct_dda_status['qct_name']
                    df.at[idx, 'DDA_Name'] = qct_dda_status['dda_name']
                    
                    if qct_dda_status['qct_status']:
                        qct_properties += 1
                        print(f"  ✅ QCT: Yes - {qct_dda_status['qct_name']}")
                    else:
                        print(f"  ❌ QCT: No")
                    
                    if qct_dda_status['dda_status']:
                        dda_properties += 1
                        print(f"  ✅ DDA: Yes - {qct_dda_status['dda_name']}")
                    else:
                        print(f"  ❌ DDA: No")
                    
                    if qct_dda_status['federal_basis_boost']:
                        federal_boost_properties += 1
                        print(f"  🎯 Federal Basis Boost: YES (30% boost eligible)")
                    
                else:
                    print(f"  ❌ Geocoding failed: {geocode_result.get('error', 'Unknown error')}")
                    df.at[idx, 'Processing_Error'] = geocode_result.get('error', 'Geocoding failed')
                
                # Small delay to be respectful of API limits
                if (idx + 1) % batch_size == 0:
                    print(f"\n⏸️  Batch complete. API calls so far: {self.api_calls}")
                    time.sleep(1)  # 1 second pause between batches
                
                # Progress save every 50 properties
                if (idx + 1) % 50 == 0:
                    temp_file = output_file.replace('.xlsx', f'_progress_{idx+1}.xlsx')
                    df.to_excel(temp_file, index=False)
                    print(f"📁 Progress saved: {temp_file}")
                    
            except Exception as e:
                print(f"❌ Error processing property: {e}")
                df.at[idx, 'Processing_Error'] = str(e)
        
        # Save final results
        df.to_excel(output_file, index=False)
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"🎯 PROCESSING COMPLETE!")
        print(f"{'='*60}")
        print(f"Total properties processed: {total_properties}")
        print(f"Successfully geocoded: {successful_geocodes} ({successful_geocodes/total_properties*100:.1f}%)")
        print(f"Properties in QCT: {qct_properties} ({qct_properties/total_properties*100:.1f}%)")
        print(f"Properties in DDA: {dda_properties} ({dda_properties/total_properties*100:.1f}%)")
        print(f"Properties with Federal Basis Boost: {federal_boost_properties} ({federal_boost_properties/total_properties*100:.1f}%)")
        print(f"\nTotal API calls made: {self.api_calls}")
        print(f"Total processing time: {processing_time:.1f} seconds ({processing_time/60:.1f} minutes)")
        print(f"Average time per property: {processing_time/total_properties:.1f} seconds")
        print(f"\n📁 Results saved to: {output_file}")
        
        # Create filtered file with only QCT/DDA properties
        filtered_df = df[df['Federal_Basis_Boost'] == True].copy()
        if len(filtered_df) > 0:
            # Sort by multiple criteria for best opportunities
            filtered_df = filtered_df.sort_values(
                by=['QCT_Status', 'DDA_Status', 'Land Area (AC)', 'Price Per AC Land'],
                ascending=[False, False, False, True]
            )
            
            filtered_file = output_file.replace('.xlsx', '_QCT_DDA_ONLY.xlsx')
            filtered_df.to_excel(filtered_file, index=False)
            print(f"\n📁 Filtered file (QCT/DDA only): {filtered_file}")
            print(f"   Contains {len(filtered_df)} properties eligible for 30% basis boost")
            print(f"   Sorted by: QCT status, DDA status, Land Area (descending), Price/Acre (ascending)")
            
            # Show top opportunities
            print(f"\n🏆 TOP 5 QCT/DDA OPPORTUNITIES:")
            for i, row in filtered_df.head(5).iterrows():
                print(f"\n   {filtered_df.index.get_loc(i) + 1}. {row['Address']}, {row['City']}")
                print(f"      Land: {row['Land Area (AC)']:.2f} acres | Price/AC: ${row['Price Per AC Land']:,.0f}")
                status = []
                if row['QCT_Status']:
                    status.append("QCT")
                if row['DDA_Status']:
                    status.append("DDA")
                print(f"      Status: {' + '.join(status)}")
        
        return df


# Main execution
if __name__ == "__main__":
    # Set your Positionstack API key as environment variable for security
    # Or pass it directly (but don't commit it to code!)
    
    # Option 1: Set environment variable before running
    # export POSITIONSTACK_API_KEY="your_api_key_here"
    
    # Option 2: Pass directly (remove before committing)
    # api_key = "your_api_key_here"
    
    # File paths - FULL PATHS
    input_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Costar/TX/CS_Land_TX-1-10ac_05312025.xlsx"
    
    # Output to your code directory
    output_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code"
    output_file = f"{output_dir}/CS_Land_TX-1-10ac_05312025_QCT_DDA_SCREENED.xlsx"
    
    # Initialize screener
    # Use environment variable (recommended)
    screener = QCTDDAScreener()
    
    # Or pass API key directly (not recommended for production)
    # screener = QCTDDAScreener(positionstack_api_key=api_key)
    
    # Process properties
    results = screener.process_properties(input_file, output_file)
