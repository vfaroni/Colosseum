#!/usr/bin/env python3
"""
Fixed QCT/DDA checker for California coordinates
Using the new data location and proper layer filtering
"""

import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path

class CaliforniaQCTDDAChecker:
    def __init__(self):
        # Path to merged HUD QCT/DDA file
        self.hud_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data/HUD QCT DDA 2025 Merged.gpkg")
        
        # Load data
        self.qct_data = None
        self.dda_data = None
        self.load_hud_designation_data()
    
    def load_hud_designation_data(self):
        """Load QCT/DDA data from merged file"""
        try:
            if self.hud_file.exists():
                print(f"Loading HUD data from: {self.hud_file}")
                
                # Load full dataset
                full_data = gpd.read_file(self.hud_file)
                
                # Ensure CRS is WGS84
                if full_data.crs != 'EPSG:4326':
                    full_data = full_data.to_crs('EPSG:4326')
                
                # Separate QCT and DDA data by layer
                self.qct_data = full_data[full_data['layer'] == 'HUD QCT 2025'].copy()
                self.dda_data = full_data[full_data['layer'] == 'HUD DDA 2025'].copy()
                
                print(f"✅ Loaded QCT data: {len(self.qct_data)} features")
                print(f"✅ Loaded DDA data: {len(self.dda_data)} features")
                
            else:
                print(f"❌ HUD file not found: {self.hud_file}")
                
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
                    
                    # Get QCT details
                    status["qct_name"] = qct_row.get('NAME', 'QCT Area')
                    status["qct_tract"] = qct_row.get('GEOID', qct_row.get('TRACT'))
                    
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
                    
                    # Get DDA details
                    status["dda_name"] = dda_row.get('DDA_NAME', 'DDA Area')
                    status["dda_details"] = {
                        'dda_code': dda_row.get('DDA_CODE'),
                        'dda_type': dda_row.get('DDA_TYPE'),
                        'zcta': dda_row.get('ZCTA5')
                    }
                    
                    print(f"✅ Location is in DDA: {status['dda_name']}")
                    if status["dda_details"]['dda_type']:
                        print(f"   DDA Type: {status['dda_details']['dda_type']}")
                    if status["dda_details"]['dda_code']:
                        print(f"   DDA Code: {status['dda_details']['dda_code']}")
        
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
    print(f"   Federal Basis Boost (30%): {'✅ YES' if result['federal_basis_boost'] else '❌ NO'}")
    
    if result['qct_status']:
        print(f"   QCT Name: {result['qct_name']}")
        if result['qct_tract']:
            print(f"   QCT Tract: {result['qct_tract']}")
    
    if result['dda_status']:
        print(f"   DDA Name: {result['dda_name']}")
        if result['dda_details']:
            for key, value in result['dda_details'].items():
                if value:
                    print(f"   {key.replace('_', ' ').title()}: {value}")
    
    return result

if __name__ == "__main__":
    # Test with Rocklin coordinates
    lat = 38.795282
    lon = -121.233117
    
    result = check_single_location(lat, lon)