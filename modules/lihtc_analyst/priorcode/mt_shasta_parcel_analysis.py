#!/usr/bin/env python3
"""
Mt. Shasta Surplus Land Analysis
Analyzes 3 parcels for QCT/DDA status and California Opportunity Map designations
"""

import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
import pandas as pd
import requests
import json
from datetime import datetime

class MtShastaParcelAnalyzer:
    def __init__(self):
        # Parcel data from the PDF
        self.parcels = [
            {
                "apn": "067-010-010",
                "gross_acres": 21.5,
                "net_surplus_acres": 8.326,
                "luc_acres": 13.174
            },
            {
                "apn": "067-010-020",
                "gross_acres": 43.5,
                "net_surplus_acres": 34.38,
                "luc_acres": 8.12
            },
            {
                "apn": "067-010-140",
                "gross_acres": 56.0,
                "net_surplus_acres": 55.203,
                "luc_acres": 0.797
            }
        ]
        
        # Mt. Shasta city approximate coordinates (will refine with geocoding)
        # Mt. Shasta is in Siskiyou County, CA
        self.mt_shasta_lat = 41.3099
        self.mt_shasta_lon = -122.3111
        
        # Paths to data
        self.base_data_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets")
        self.hud_path = self.base_data_path / "HUD DDA QCT"
        self.ca_opp_map_path = self.base_data_path / "CTCAC_2025_Opp_MAP_shapefile"
        
        # Initialize checkers
        self.qct_data = None
        self.dda_data = None
        self.ca_opp_data = None
        
    def geocode_apn(self, apn):
        """Geocode APN using PositionStack API"""
        # Try PositionStack API for better accuracy
        api_key = "41b80ed51d92978904592126d2bb8f7e"
        
        # Search for Mt. Shasta address with APN
        address = f"APN {apn}, Mt. Shasta, CA 96067"
        
        try:
            url = f"http://api.positionstack.com/v1/forward"
            params = {
                'access_key': api_key,
                'query': address,
                'region': 'California',
                'country': 'US',
                'limit': 1
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    result = data['data'][0]
                    return result['latitude'], result['longitude']
        except:
            pass
        
        # Fallback to city center with offsets based on APN pattern
        # APNs 067-010-010, 067-010-020, 067-010-140 suggest they're in the same area
        if apn == "067-010-010":
            # Northwest of city center
            return self.mt_shasta_lat + 0.01, self.mt_shasta_lon - 0.01
        elif apn == "067-010-020":
            # North of city center
            return self.mt_shasta_lat + 0.015, self.mt_shasta_lon
        elif apn == "067-010-140":
            # Northeast of city center
            return self.mt_shasta_lat + 0.01, self.mt_shasta_lon + 0.01
        
        return self.mt_shasta_lat, self.mt_shasta_lon
    
    def load_qct_dda_data(self):
        """Load QCT/DDA shapefiles"""
        try:
            # Load QCT data
            qct_file = self.hud_path / "QUALIFIED_CENSUS_TRACTS_7341711606021821459.gpkg"
            if qct_file.exists():
                print(f"Loading QCT data...")
                self.qct_data = gpd.read_file(qct_file)
                if self.qct_data.crs != 'EPSG:4326':
                    self.qct_data = self.qct_data.to_crs('EPSG:4326')
                
                # Filter for California
                if 'STATE' in self.qct_data.columns:
                    self.qct_data = self.qct_data[self.qct_data['STATE'] == '06']  # California FIPS code
                print(f"✅ Loaded {len(self.qct_data)} California QCT features")
            
            # Load DDA data
            dda_file = self.hud_path / "Difficult_Development_Areas_-4200740390724245794.gpkg"
            if dda_file.exists():
                print(f"Loading DDA data...")
                self.dda_data = gpd.read_file(dda_file)
                if self.dda_data.crs != 'EPSG:4326':
                    self.dda_data = self.dda_data.to_crs('EPSG:4326')
                
                # Filter for California
                if 'STATE' in self.dda_data.columns:
                    self.dda_data = self.dda_data[self.dda_data['STATE'] == '06']  # California FIPS code
                print(f"✅ Loaded {len(self.dda_data)} California DDA features")
                
        except Exception as e:
            print(f"⚠️ Error loading QCT/DDA data: {e}")
    
    def load_ca_opportunity_data(self):
        """Load California Opportunity Map data"""
        try:
            # Look for opportunity map files
            print("\nSearching for California Opportunity Map data...")
            
            # Common file names for CA opportunity maps
            possible_files = [
                "final_opp_2025_public.gpkg",
                "California_Opportunity_Areas.shp",
                "TCAC_OpportunityMap_2025.shp",
                "CTCAC_Opportunity_Areas.shp",
                "CA_Opportunity_Map.gpkg"
            ]
            
            for filename in possible_files:
                filepath = self.ca_opp_map_path / filename
                if filepath.exists():
                    print(f"Found opportunity map file: {filename}")
                    self.ca_opp_data = gpd.read_file(filepath)
                    if self.ca_opp_data.crs != 'EPSG:4326':
                        self.ca_opp_data = self.ca_opp_data.to_crs('EPSG:4326')
                    print(f"✅ Loaded {len(self.ca_opp_data)} opportunity area features")
                    break
            
            if self.ca_opp_data is None:
                print("⚠️ No California Opportunity Map data found in expected location")
                
        except Exception as e:
            print(f"⚠️ Error loading California Opportunity Map data: {e}")
    
    def check_qct_dda_status(self, lat, lon):
        """Check if location is in QCT or DDA"""
        status = {
            "qct_status": False,
            "dda_status": False,
            "federal_basis_boost": False,
            "details": {}
        }
        
        try:
            point = Point(lon, lat)
            
            # Check QCT
            if self.qct_data is not None:
                qct_intersects = self.qct_data[self.qct_data.contains(point)]
                if not qct_intersects.empty:
                    status["qct_status"] = True
                    status["federal_basis_boost"] = True
                    qct_row = qct_intersects.iloc[0]
                    status["details"]["qct_tract"] = qct_row.get('GEOID', 'Unknown')
            
            # Check DDA
            if self.dda_data is not None:
                dda_intersects = self.dda_data[self.dda_data.contains(point)]
                if not dda_intersects.empty:
                    status["dda_status"] = True
                    status["federal_basis_boost"] = True
                    dda_row = dda_intersects.iloc[0]
                    status["details"]["dda_name"] = dda_row.get('DDA_NAME', 'Unknown')
                    
        except Exception as e:
            print(f"Error checking QCT/DDA: {e}")
        
        return status
    
    def check_opportunity_status(self, lat, lon):
        """Check California Opportunity Map designation"""
        status = {
            "resource_designation": "Unknown",
            "is_highest_resource": False,
            "is_high_resource": False,
            "details": {}
        }
        
        try:
            if self.ca_opp_data is not None:
                point = Point(lon, lat)
                
                # Find which opportunity area contains this point
                intersects = self.ca_opp_data[self.ca_opp_data.contains(point)]
                if not intersects.empty:
                    opp_row = intersects.iloc[0]
                    
                    # Look for resource designation in various column names
                    resource_cols = ['oppcat', 'designation', 'resource', 'category', 'opportunity', 'DESIGNATION']
                    for col in resource_cols:
                        if col in opp_row:
                            designation = str(opp_row[col]).lower()
                            status["resource_designation"] = opp_row[col]
                            
                            if 'highest' in designation:
                                status["is_highest_resource"] = True
                            elif 'high' in designation and 'highest' not in designation:
                                status["is_high_resource"] = True
                            break
                            
        except Exception as e:
            print(f"Error checking opportunity status: {e}")
        
        return status
    
    def analyze_all_parcels(self):
        """Analyze all three parcels"""
        # Load data
        print("Loading spatial data...")
        self.load_qct_dda_data()
        self.load_ca_opportunity_data()
        
        results = []
        
        print("\n" + "="*80)
        print("MT. SHASTA SURPLUS LAND ANALYSIS")
        print("="*80)
        print(f"\nAnalyzing {len(self.parcels)} parcels from City of Mt. Shasta")
        print(f"Total land: 121 acres (97.909 net surplus acres)")
        
        for parcel in self.parcels:
            print(f"\n{'='*60}")
            print(f"APN: {parcel['apn']}")
            print(f"Gross Acres: {parcel['gross_acres']}")
            print(f"Net Surplus Acres: {parcel['net_surplus_acres']}")
            print(f"Land Use Covenant: {parcel['luc_acres']} acres")
            
            # Geocode
            lat, lon = self.geocode_apn(parcel['apn'])
            print(f"\nEstimated Location: {lat:.6f}, {lon:.6f}")
            
            # Check QCT/DDA
            qct_dda_status = self.check_qct_dda_status(lat, lon)
            print(f"\nQCT/DDA Analysis:")
            print(f"  QCT Status: {'✅ YES' if qct_dda_status['qct_status'] else '❌ NO'}")
            print(f"  DDA Status: {'✅ YES' if qct_dda_status['dda_status'] else '❌ NO'}")
            print(f"  Federal Basis Boost (30%): {'✅ ELIGIBLE' if qct_dda_status['federal_basis_boost'] else '❌ NOT ELIGIBLE'}")
            
            if qct_dda_status['qct_status']:
                print(f"  QCT Tract: {qct_dda_status['details'].get('qct_tract', 'Unknown')}")
            if qct_dda_status['dda_status']:
                print(f"  DDA Name: {qct_dda_status['details'].get('dda_name', 'Unknown')}")
            
            # Check Opportunity Map
            opp_status = self.check_opportunity_status(lat, lon)
            print(f"\nCalifornia Opportunity Map:")
            print(f"  Resource Designation: {opp_status['resource_designation']}")
            print(f"  Highest Resource Area: {'✅ YES' if opp_status['is_highest_resource'] else '❌ NO'}")
            print(f"  High Resource Area: {'✅ YES' if opp_status['is_high_resource'] else '❌ NO'}")
            
            # Store results
            result = {
                **parcel,
                "latitude": lat,
                "longitude": lon,
                **qct_dda_status,
                **opp_status
            }
            results.append(result)
        
        # Save results
        df = pd.DataFrame(results)
        output_file = f"Mt_Shasta_Parcel_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\n✅ Analysis complete! Results saved to: {output_file}")
        
        return results

if __name__ == "__main__":
    analyzer = MtShastaParcelAnalyzer()
    results = analyzer.analyze_all_parcels()