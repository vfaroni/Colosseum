#!/usr/bin/env python3
"""
Simple QCT/DDA checker for California coordinates
Adapted from texas-land-qct-dda-screener-2.py
"""

import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path

class CaliforniaQCTDDAChecker:
    def __init__(self):
        # Paths to HUD QCT/DDA shapefiles
        self.base_hud_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data")
        self.qct_file = self.base_hud_path / "HUD_DDA_QCT_2025_Combined.gpkg"
        self.dda_file = self.base_hud_path / "HUD_DDA_QCT_2025_Combined.gpkg"
        
        # Load shapefiles
        self.qct_data = None
        self.dda_data = None
        self.load_hud_designation_data()
    
    def load_hud_designation_data(self):
        """Load QCT/DDA shapefiles"""
        try:
            # Load QCT data
            if self.qct_file.exists():
                print(f"Loading QCT data from: {self.qct_file}")
                self.qct_data = gpd.read_file(self.qct_file)
                if self.qct_data.crs != 'EPSG:4326':
                    self.qct_data = self.qct_data.to_crs('EPSG:4326')
                print(f"✅ Loaded QCT data: {len(self.qct_data)} features")
                
                # Filter for California if there's a state field
                if 'STATE' in self.qct_data.columns:
                    ca_qct = self.qct_data[self.qct_data['STATE'] == 'CA']
                    if len(ca_qct) > 0:
                        self.qct_data = ca_qct
                        print(f"✅ Filtered to California QCTs: {len(self.qct_data)} features")
                
            else:
                print(f"❌ QCT file not found: {self.qct_file}")
            
            # Load DDA data
            if self.dda_file.exists():
                print(f"Loading DDA data from: {self.dda_file}")
                self.dda_data = gpd.read_file(self.dda_file)
                if self.dda_data.crs != 'EPSG:4326':
                    self.dda_data = self.dda_data.to_crs('EPSG:4326')
                print(f"✅ Loaded DDA data: {len(self.dda_data)} features")
                
                # Filter for California if there's a state field
                if 'STATE' in self.dda_data.columns:
                    ca_dda = self.dda_data[self.dda_data['STATE'] == 'CA']
                    if len(ca_dda) > 0:
                        self.dda_data = ca_dda
                        print(f"✅ Filtered to California DDAs: {len(self.dda_data)} features")
                
            else:
                print(f"❌ DDA file not found: {self.dda_file}")
                
        except Exception as e:
            print(f"⚠️ Error loading HUD designation data: {e}")
    
    def check_qct_dda_status(self, latitude, longitude):
        """Check if coordinates are in QCT or DDA"""
        status = {
            "latitude": latitude,
            "longitude": longitude,
            "qct_status": False,
            "dda_status": False,
            "federal_basis_boost": False,
            "qct_name": None,
            "dda_name": None,
            "qct_tract": None,
            "dda_details": None
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
                    
                    # Try different column names for QCT identification
                    status["qct_name"] = (qct_row.get('NAME') or 
                                        qct_row.get('QCT_NAME') or 
                                        qct_row.get('NAMELSAD') or 
                                        'QCT Area')
                    status["qct_tract"] = (qct_row.get('GEOID') or 
                                         qct_row.get('TRACTCE') or 
                                         qct_row.get('FIPS'))
                    
                    print(f"✅ Location is in QCT: {status['qct_name']}")
                    if status["qct_tract"]:
                        print(f"   Tract ID: {status['qct_tract']}")
            
            # Check DDA status
            if self.dda_data is not None:
                dda_intersects = self.dda_data[self.dda_data.contains(point)]
                if not dda_intersects.empty:
                    status["dda_status"] = True
                    status["federal_basis_boost"] = True
                    dda_row = dda_intersects.iloc[0]
                    
                    # Try different column names for DDA identification
                    status["dda_name"] = (dda_row.get('DDA_NAME') or 
                                        dda_row.get('NAME') or 
                                        dda_row.get('AREA_NAME') or 
                                        'DDA Area')
                    status["dda_details"] = {
                        'metro_area': dda_row.get('METRO_NAME'),
                        'county': dda_row.get('COUNTY_NAME')
                    }
                    
                    print(f"✅ Location is in DDA: {status['dda_name']}")
                    if status["dda_details"]['metro_area']:
                        print(f"   Metro Area: {status['dda_details']['metro_area']}")
                    if status["dda_details"]['county']:
                        print(f"   County: {status['dda_details']['county']}")
        
        except Exception as e:
            print(f"⚠️ Error checking QCT/DDA status: {e}")
        
        return status

def check_single_location(lat, lon):
    """Check QCT/DDA status for a single coordinate pair"""
    print(f"\n🔍 Checking QCT/DDA status for coordinates: {lat}, {lon}")
    
    checker = CaliforniaQCTDDAChecker()
    result = checker.check_qct_dda_status(lat, lon)
    
    print(f"\n📍 RESULTS FOR {lat}, {lon}:")
    print(f"   QCT Status: {'✅ YES' if result['qct_status'] else '❌ NO'}")
    print(f"   DDA Status: {'✅ YES' if result['dda_status'] else '❌ NO'}")
    print(f"   Federal Basis Boost: {'✅ YES' if result['federal_basis_boost'] else '❌ NO'}")
    
    if result['qct_status']:
        print(f"   QCT Name: {result['qct_name']}")
        if result['qct_tract']:
            print(f"   QCT Tract: {result['qct_tract']}")
    
    if result['dda_status']:
        print(f"   DDA Name: {result['dda_name']}")
        if result['dda_details']['metro_area']:
            print(f"   Metro Area: {result['dda_details']['metro_area']}")
        if result['dda_details']['county']:
            print(f"   County: {result['dda_details']['county']}")
    
    return result

if __name__ == "__main__":
    # Test with the provided coordinates
    # 38°47'47.1"N 121°13'57.6"W = 38.796417, -121.232667
    lat = 38.796417
    lon = -121.232667
    
    result = check_single_location(lat, lon)