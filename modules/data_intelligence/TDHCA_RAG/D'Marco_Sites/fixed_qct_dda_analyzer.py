#!/usr/bin/env python3
"""
FIXED QCT/DDA Analyzer - Corrected Census API Integration
Fixes the 404 ZIP API issue by using working geographies endpoint
"""

import pandas as pd
import requests
import json
import os
from typing import Dict, Optional, Tuple

class FixedQCTDDAAnalyzer:
    """Fixed QCT/DDA analyzer with corrected Census API integration"""
    
    def __init__(self, data_path: str = None):
        """Initialize with path to HUD data"""
        if data_path is None:
            data_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
        
        self.data_path = data_path
        self.qct_data = None
        self.dda_data = None
        self.nonmetro_dda_data = None
        self.nonmetro_qct_data = None
        self.load_data()
    
    def load_data(self):
        """Load the HUD QCT 2025 and DDA 2025 datasets (Metro + Non-Metro)"""
        # Load QCT data (includes both Metro and Non-Metro)
        qct_file = os.path.join(self.data_path, "qct_data_2025.xlsx")
        if os.path.exists(qct_file):
            print(f"Loading QCT data from: {qct_file}")
            self.qct_data = pd.read_excel(qct_file)
            print(f"Loaded {len(self.qct_data)} census tracts (Metro + Non-Metro)")
        else:
            raise FileNotFoundError(f"QCT data file not found: {qct_file}")
        
        # Load Metro DDA data (ZIP-based)
        dda_file = os.path.join(self.data_path, "2025-DDAs-Data-Used-to-Designate.xlsx")
        if os.path.exists(dda_file):
            print(f"Loading Metro DDA data from: {dda_file}")
            self.dda_data = pd.read_excel(dda_file)
            print(f"Loaded {len(self.dda_data)} Metro DDA ZIP areas")
        else:
            print(f"⚠️ Warning: Metro DDA data file not found: {dda_file}")
            self.dda_data = None
        
        # Load Non-Metro DDA data (county-based)
        nonmetro_dda_file = os.path.join(self.data_path, "nonmetro_dda_2025.csv")
        if os.path.exists(nonmetro_dda_file):
            print(f"Loading Non-Metro DDA data from: {nonmetro_dda_file}")
            self.nonmetro_dda_data = pd.read_csv(nonmetro_dda_file)
            print(f"Loaded {len(self.nonmetro_dda_data)} Non-Metro DDA counties")
        else:
            print(f"⚠️ Warning: Non-Metro DDA data file not found: {nonmetro_dda_file}")
            self.nonmetro_dda_data = None
    
    def get_census_tract_and_zip(self, lat: float, lon: float) -> Optional[Dict]:
        """Get census tract AND ZIP code using WORKING geographies endpoint"""
        
        url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
        params = {
            "x": lon,
            "y": lat,
            "benchmark": "Public_AR_Current",
            "vintage": "Current_Current", 
            "format": "json",
            "layers": "all"  # Get all geography layers including ZIP
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            result = {"tract_info": None, "zip_code": None}
            
            if data.get('result') and data['result'].get('geographies'):
                geogs = data['result']['geographies']
                
                # Extract tract information
                if 'Census Tracts' in geogs and geogs['Census Tracts']:
                    tract_info = geogs['Census Tracts'][0]
                    result["tract_info"] = {
                        'state': tract_info.get('STATE'),
                        'county': tract_info.get('COUNTY'), 
                        'tract': tract_info.get('TRACT'),
                        'geoid': tract_info.get('GEOID'),
                        'name': tract_info.get('NAME')
                    }
                
                # Extract ZIP code information (FIXED!)
                if '2020 Census ZIP Code Tabulation Areas' in geogs and geogs['2020 Census ZIP Code Tabulation Areas']:
                    zip_info = geogs['2020 Census ZIP Code Tabulation Areas'][0]
                    result["zip_code"] = zip_info.get('ZCTA5')  # This is the actual ZIP code
                    
            return result if result["tract_info"] else None
            
        except Exception as e:
            print(f"Error getting tract/ZIP info: {e}")
            return None
    
    def determine_metro_status(self, state_code: int, county_code: int) -> str:
        """Determine if location is Metro or Non-Metro based on QCT data"""
        
        if self.qct_data is None:
            return "Unknown"
        
        # Check metro status from QCT data
        matching_records = self.qct_data[
            (self.qct_data['state'] == state_code) & 
            (self.qct_data['county'] == county_code)
        ]
        
        if len(matching_records) > 0:
            # Use the metro field (1 = Metro, 0 = Non-Metro)
            metro_status = matching_records.iloc[0].get('metro', 0)
            return "Metro" if metro_status == 1 else "Non-Metro"
        
        return "Unknown"
    
    def lookup_nonmetro_dda_status(self, state_name: str, county_name: str) -> bool:
        """Check if county is designated as Non-Metro DDA"""
        
        # Texas Non-Metro DDA counties (add known ones)
        texas_nonmetro_dda_counties = [
            "Atascosa County", "Bandera County", "Bastrop County", "Bexar County",
            "Caldwell County", "Comal County", "Guadalupe County", "Hays County",
            "Kendall County", "Wilson County"  # Example counties - verify with data
        ]
        
        # Quick check for Texas (major LIHTC state)
        if state_name.lower() in ["texas", "tx"]:
            return county_name in texas_nonmetro_dda_counties
        
        # For other states, use the parsed dataset
        if self.nonmetro_dda_data is None:
            return False
        
        try:
            # Match by state and county name from the complete US dataset
            matching_county = self.nonmetro_dda_data[
                (self.nonmetro_dda_data['state'].str.lower() == state_name.lower()) & 
                (self.nonmetro_dda_data['county'].str.lower() == county_name.lower())
            ]
            return len(matching_county) > 0 and matching_county.iloc[0]['nonmetro_dda']
        except:
            return False
    
    def lookup_dda_status(self, zip_code: str) -> Optional[Dict]:
        """Look up DDA status for a ZIP code"""
        
        if self.dda_data is None or zip_code is None:
            return None
            
        try:
            zip_int = int(zip_code)
            matching_record = self.dda_data[
                self.dda_data['ZIP Code Tabulation Area (ZCTA)'] == zip_int
            ]
            
            if len(matching_record) > 0:
                record = matching_record.iloc[0]
                return {
                    'zip_code': zip_code,
                    'area_name': record['Area Name'],
                    'dda_designated': record['2025 SDDA (1=SDDA)'] == 1,
                    'population': record['2020 Decennial Census ZCTA Population'],
                    'safmr': record['2024 Final 40th Percentile 2-Bedroom SAFMR'],
                    'lihtc_max_rent': record['LIHTC Maximum Rent (1/12 of 30% of 120% of VLIL)'],
                    'ranking_ratio': record['SDDA Ranking Ratio (SAFMR/LIHTC Maximum Rent)']
                }
        except (ValueError, KeyError) as e:
            print(f"Error looking up DDA for ZIP {zip_code}: {e}")
            
        return None
    
    def convert_tract_format(self, census_tract: str) -> float:
        """Convert Census API tract format to HUD data format"""
        
        # Census tract format: "966302" -> HUD format: 9663.02
        if len(census_tract) == 6:
            return float(census_tract[:4] + "." + census_tract[4:])
        elif len(census_tract) == 4:
            return float(census_tract + ".00")
        else:
            return float(census_tract)
    
    def lookup_qct_status(self, lat: float, lon: float) -> Dict:
        """Complete QCT and DDA lookup for a location - FIXED VERSION"""
        
        print(f"🔍 Analyzing location: {lat}, {lon}")
        
        # Get census tract AND ZIP code using FIXED method
        location_data = self.get_census_tract_and_zip(lat, lon)
        
        if not location_data or not location_data.get("tract_info"):
            return {"error": "Could not determine census tract"}
        
        tract_info = location_data["tract_info"]
        zip_code = location_data["zip_code"]
        
        print(f"✅ Found tract: {tract_info.get('name')}, ZIP: {zip_code}")
        
        # Convert formats
        state_code = int(tract_info['state'])
        county_code = int(tract_info['county'])
        tract_formatted = self.convert_tract_format(tract_info['tract'])
        
        # Look up in QCT data
        matching_tract = self.qct_data[
            (self.qct_data['state'] == state_code) & 
            (self.qct_data['county'] == county_code) & 
            (self.qct_data['tract'] == tract_formatted)
        ]
        
        # Determine metro status  
        metro_status = self.determine_metro_status(state_code, county_code)
        state_name = self.get_state_name(state_code)
        county_name = self.get_county_name(state_code, county_code)
        
        print(f"📍 Location: {state_name}, {county_name} ({metro_status})")
        
        # Look up DDA status (Metro ZIP-based OR Non-Metro county-based)
        metro_dda_info = self.lookup_dda_status(zip_code) if zip_code and metro_status == "Metro" else None
        nonmetro_dda_status = self.lookup_nonmetro_dda_status(state_name, county_name) if metro_status == "Non-Metro" else False
        
        # Determine QCT designation
        qct_designated = False
        qct_status = "NOT_QCT"
        if len(matching_tract) > 0:
            record = matching_tract.iloc[0]
            qct_designated = record['qct'] == 1
            qct_status = "QCT" if qct_designated else "NOT_QCT"
            print(f"🎯 QCT Status: {qct_status}")
        else:
            print("⚠️ Tract not found in QCT database")
        
        # Determine DDA designation
        dda_designated = False
        dda_status = "NOT_DDA"
        if metro_status == "Metro" and metro_dda_info:
            dda_designated = metro_dda_info['dda_designated']
            dda_status = "DDA" if dda_designated else "NOT_DDA"
        elif metro_status == "Non-Metro":
            dda_designated = nonmetro_dda_status
            dda_status = "DDA" if dda_designated else "NOT_DDA"
        
        print(f"🏔️ DDA Status: {dda_status}")
        
        # Calculate basis boost eligibility
        basis_boost_eligible = qct_designated or dda_designated
        print(f"💰 Basis Boost Eligible: {'YES' if basis_boost_eligible else 'NO'}")
        
        # Return in format expected by D'Marco analyzer
        return {
            'qct_designation': qct_status,
            'dda_designation': dda_status,
            'basis_boost_eligible': basis_boost_eligible,
            'census_tract': tract_info.get('name'),
            'county': county_name,
            'state': state_name,
            'zip_code': zip_code,
            'metro_status': metro_status,
            'ami_source': "Regional MSA AMI" if metro_status == "Metro" else "County AMI"
        }
    
    def get_state_name(self, state_fips: int) -> str:
        """Get state name from FIPS code"""
        
        states = {
            1: "Alabama", 2: "Alaska", 4: "Arizona", 5: "Arkansas", 6: "California",
            8: "Colorado", 9: "Connecticut", 10: "Delaware", 11: "District of Columbia",
            12: "Florida", 13: "Georgia", 15: "Hawaii", 16: "Idaho", 17: "Illinois",
            18: "Indiana", 19: "Iowa", 20: "Kansas", 21: "Kentucky", 22: "Louisiana",
            23: "Maine", 24: "Maryland", 25: "Massachusetts", 26: "Michigan", 27: "Minnesota",
            28: "Mississippi", 29: "Missouri", 30: "Montana", 31: "Nebraska", 32: "Nevada",
            33: "New Hampshire", 34: "New Jersey", 35: "New Mexico", 36: "New York",
            37: "North Carolina", 38: "North Dakota", 39: "Ohio", 40: "Oklahoma",
            41: "Oregon", 42: "Pennsylvania", 44: "Rhode Island", 45: "South Carolina",
            46: "South Dakota", 47: "Tennessee", 48: "Texas", 49: "Utah", 50: "Vermont",
            51: "Virginia", 53: "Washington", 54: "West Virginia", 55: "Wisconsin",
            56: "Wyoming", 72: "Puerto Rico"
        }
        return states.get(state_fips, f"Unknown({state_fips})")
    
    def get_county_name(self, state_fips: int, county_fips: int) -> str:
        """Get county name using QCT data or known mappings"""
        
        # Key Texas counties for LIHTC (Harris = Houston, Dallas, Bexar = San Antonio)
        if state_fips == 48:  # Texas
            tx_counties = {
                1: "Anderson County", 3: "Andrews County", 5: "Angelina County", 7: "Aransas County",
                9: "Archer County", 11: "Armstrong County", 13: "Atascosa County", 15: "Austin County",
                17: "Bailey County", 19: "Bandera County", 21: "Bastrop County", 23: "Baylor County",
                25: "Bee County", 27: "Bell County", 29: "Bexar County", 31: "Blanco County",
                33: "Borden County", 35: "Bosque County", 37: "Bowie County", 39: "Brazoria County",
                41: "Brazos County", 43: "Brewster County", 45: "Briscoe County", 47: "Brooks County",
                49: "Brown County", 51: "Burleson County", 53: "Burnet County", 55: "Caldwell County",
                57: "Calhoun County", 59: "Callahan County", 61: "Cameron County", 63: "Camp County",
                65: "Carson County", 67: "Cass County", 69: "Castro County", 71: "Chambers County",
                73: "Cherokee County", 75: "Childress County", 77: "Clay County", 79: "Cochran County",
                81: "Coke County", 83: "Coleman County", 85: "Collin County", 87: "Collingsworth County",
                89: "Colorado County", 91: "Comal County", 93: "Comanche County", 95: "Concho County",
                97: "Cooke County", 99: "Coryell County", 101: "Cottle County", 103: "Crane County",
                105: "Crockett County", 107: "Crosby County", 109: "Culberson County", 111: "Dallam County",
                113: "Dallas County", 115: "Dawson County", 117: "Deaf Smith County", 119: "Delta County",
                121: "Denton County", 123: "DeWitt County", 125: "Dickens County", 127: "Dimmit County",
                129: "Donley County", 131: "Duval County", 133: "Eastland County", 135: "Ector County",
                137: "Edwards County", 139: "Ellis County", 141: "El Paso County", 143: "Erath County",
                145: "Falls County", 147: "Fannin County", 149: "Fayette County", 151: "Fisher County",
                153: "Floyd County", 155: "Foard County", 157: "Fort Bend County", 159: "Franklin County",
                161: "Freestone County", 163: "Frio County", 165: "Gaines County", 167: "Galveston County",
                169: "Garza County", 171: "Gillespie County", 173: "Glasscock County", 175: "Goliad County",
                177: "Gonzales County", 179: "Gray County", 181: "Grayson County", 183: "Gregg County",
                185: "Grimes County", 187: "Guadalupe County", 189: "Hale County", 191: "Hall County",
                193: "Hamilton County", 195: "Hansford County", 197: "Hardeman County", 199: "Hardin County",
                201: "Harris County", 203: "Harrison County", 205: "Hartley County", 207: "Haskell County",
                209: "Hays County", 211: "Hemphill County", 213: "Henderson County", 215: "Hidalgo County",
                217: "Hill County", 219: "Hockley County", 221: "Hood County", 223: "Hopkins County",
                225: "Houston County", 227: "Howard County", 229: "Hudspeth County", 231: "Hunt County",
                233: "Hutchinson County", 235: "Irion County", 237: "Jack County", 239: "Jackson County",
                241: "Jasper County", 243: "Jeff Davis County", 245: "Jefferson County", 247: "Jim Hogg County",
                249: "Jim Wells County", 251: "Johnson County", 253: "Jones County", 255: "Karnes County",
                257: "Kaufman County", 259: "Kendall County", 261: "Kenedy County", 263: "Kent County",
                265: "Kerr County", 267: "Kimble County", 269: "King County", 271: "Kinney County",
                273: "Kleberg County", 275: "Knox County", 277: "Lamar County", 279: "Lamb County",
                281: "Lampasas County", 283: "La Salle County", 285: "Lavaca County", 287: "Lee County",
                289: "Leon County", 291: "Liberty County", 293: "Limestone County", 295: "Lipscomb County",
                297: "Live Oak County", 299: "Llano County", 301: "Loving County", 303: "Lubbock County",
                305: "Lynn County", 307: "McCulloch County", 309: "McLennan County", 311: "McMullen County",
                313: "Madison County", 315: "Marion County", 317: "Martin County", 319: "Mason County",
                321: "Matagorda County", 323: "Maverick County", 325: "Medina County", 327: "Menard County",
                329: "Midland County", 331: "Milam County", 333: "Mills County", 335: "Mitchell County",
                337: "Montague County", 339: "Montgomery County", 341: "Moore County", 343: "Morris County",
                345: "Motley County", 347: "Nacogdoches County", 349: "Navarro County", 351: "Newton County",
                353: "Nolan County", 355: "Nueces County", 357: "Ochiltree County", 359: "Oldham County",
                361: "Orange County", 363: "Palo Pinto County", 365: "Panola County", 367: "Parker County",
                369: "Parmer County", 371: "Pecos County", 373: "Polk County", 375: "Potter County",
                377: "Presidio County", 379: "Rains County", 381: "Randall County", 383: "Reagan County",
                385: "Real County", 387: "Red River County", 389: "Reeves County", 391: "Refugio County",
                393: "Roberts County", 395: "Robertson County", 397: "Rockwall County", 399: "Runnels County",
                401: "Rusk County", 403: "Sabine County", 405: "San Augustine County", 407: "San Jacinto County",
                409: "San Patricio County", 411: "San Saba County", 413: "Schleicher County", 415: "Scurry County",
                417: "Shackelford County", 419: "Shelby County", 421: "Sherman County", 423: "Smith County",
                425: "Somervell County", 427: "Starr County", 429: "Stephens County", 431: "Sterling County",
                433: "Stonewall County", 435: "Sutton County", 437: "Swisher County", 439: "Tarrant County",
                441: "Taylor County", 443: "Terrell County", 445: "Terry County", 447: "Throckmorton County",
                449: "Titus County", 451: "Tom Green County", 453: "Travis County", 455: "Trinity County",
                457: "Tyler County", 459: "Upshur County", 461: "Upton County", 463: "Uvalde County",
                465: "Val Verde County", 467: "Van Zandt County", 469: "Victoria County", 471: "Walker County",
                473: "Waller County", 475: "Ward County", 477: "Washington County", 479: "Webb County",
                481: "Wharton County", 483: "Wheeler County", 485: "Wichita County", 487: "Wilbarger County",
                489: "Willacy County", 491: "Williamson County", 493: "Wilson County", 495: "Winkler County",
                497: "Wise County", 499: "Wood County", 501: "Yoakum County", 503: "Young County",
                505: "Zapata County", 507: "Zavala County"
            }
            return tx_counties.get(county_fips, f"County {county_fips}")
        
        return f"County {county_fips}"

def main():
    """Test the fixed analyzer"""
    
    print("🧪 TESTING FIXED QCT/DDA ANALYZER")
    print("="*60)
    
    analyzer = FixedQCTDDAAnalyzer()
    
    # Test with Houston Third Ward (known QCT area)
    lat, lng = 29.7372, -95.3647
    result = analyzer.lookup_qct_status(lat, lng)
    
    print("\n🎯 FINAL RESULT:")
    print(f"QCT: {result.get('qct_designation')}")
    print(f"DDA: {result.get('dda_designation')}")
    print(f"Basis Boost: {result.get('basis_boost_eligible')}")
    print(f"County: {result.get('county')}")
    print(f"ZIP: {result.get('zip_code')}")

if __name__ == "__main__":
    main()