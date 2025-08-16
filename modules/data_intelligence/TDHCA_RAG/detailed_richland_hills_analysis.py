#!/usr/bin/env python3
"""
Detailed QCT/DDA Analysis for Richland Hills Tract 
Location: Corner of Midhurst Ave & Richland Hills Dr, San Antonio, TX
Coordinates: 29.4187, -98.6788
"""

import sys
import os
import pandas as pd

# Add the path to import the comprehensive analyzer
sys.path.append('/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG')

from comprehensive_qct_dda_analyzer import ComprehensiveQCTDDAAnalyzer

def enhanced_analysis():
    """Enhanced analysis with detailed debugging"""
    
    print("DETAILED RICHLAND HILLS TRACT ANALYSIS")
    print("="*70)
    print("Property: Corner of Midhurst Ave & Richland Hills Dr, San Antonio, TX")
    print("Parcel ID: 15329-000-0260 | Land Area: 9.83 acres")
    print("="*70)
    
    # Initialize analyzer
    analyzer = ComprehensiveQCTDDAAnalyzer()
    
    # Coordinates for the correct Richland Hills Tract location
    lat, lon = 29.4187, -98.6788
    
    print(f"\n🔍 DETAILED GEOCODING ANALYSIS:")
    print(f"Coordinates: {lat}, {lon}")
    
    # Get census tract details
    tract_info = analyzer.get_census_tract(lat, lon)
    if tract_info:
        print(f"✅ Census Tract Found:")
        print(f"   State FIPS: {tract_info['state']}")
        print(f"   County FIPS: {tract_info['county']}")
        print(f"   Tract: {tract_info['tract']}")
        print(f"   GEOID: {tract_info['geoid']}")
        print(f"   Name: {tract_info['name']}")
        
        # Manual county lookup for Bexar County (FIPS 29)
        state_fips = int(tract_info['state'])  # Should be 48 for Texas
        county_fips = int(tract_info['county'])  # Should be 029 for Bexar County
        
        print(f"\n📍 LOCATION DETAILS:")
        print(f"   State: Texas (FIPS: {state_fips})")
        
        # Texas county mapping
        texas_counties = {
            1: "Anderson County", 3: "Andrews County", 5: "Angelina County",
            7: "Aransas County", 9: "Archer County", 11: "Armstrong County",
            13: "Atascosa County", 15: "Austin County", 17: "Bailey County",
            19: "Bandera County", 21: "Bastrop County", 23: "Baylor County",
            25: "Bee County", 27: "Bell County", 29: "Bexar County",
            31: "Blanco County", 33: "Borden County", 35: "Bosque County",
            37: "Bowie County", 39: "Brazoria County", 41: "Brazos County",
            43: "Brewster County", 45: "Briscoe County", 47: "Brooks County",
            49: "Brown County", 51: "Burleson County", 53: "Burnet County",
            55: "Caldwell County", 57: "Calhoun County", 59: "Callahan County",
            61: "Cameron County", 63: "Camp County", 65: "Carson County",
            67: "Cass County", 69: "Castro County", 71: "Chambers County",
            73: "Cherokee County", 75: "Childress County", 77: "Clay County",
            79: "Cochran County", 81: "Coke County", 83: "Coleman County",
            85: "Collin County", 87: "Collingsworth County", 89: "Colorado County",
            91: "Comal County", 93: "Comanche County", 95: "Concho County",
            97: "Cooke County", 99: "Coryell County", 101: "Cottle County",
            103: "Crane County", 105: "Crockett County", 107: "Crosby County",
            109: "Culberson County", 111: "Dallam County", 113: "Dallas County",
            115: "Dawson County", 117: "Deaf Smith County", 119: "Delta County",
            121: "Denton County", 123: "DeWitt County", 125: "Dickens County",
            127: "Dimmit County", 129: "Donley County", 131: "Duval County",
            133: "Eastland County", 135: "Ector County", 137: "Edwards County",
            139: "Ellis County", 141: "El Paso County", 143: "Erath County",
            145: "Falls County", 147: "Fannin County", 149: "Fayette County",
            151: "Fisher County", 153: "Floyd County", 155: "Foard County",
            157: "Fort Bend County", 159: "Franklin County", 161: "Freestone County",
            163: "Frio County", 165: "Gaines County", 167: "Galveston County",
            169: "Garza County", 171: "Gillespie County", 173: "Glasscock County",
            175: "Goliad County", 177: "Gonzales County", 179: "Gray County",
            181: "Grayson County", 183: "Gregg County", 185: "Grimes County",
            187: "Guadalupe County", 189: "Hale County", 191: "Hall County",
            193: "Hamilton County", 195: "Hansford County", 197: "Hardeman County",
            199: "Hardin County", 201: "Harris County", 203: "Harrison County",
            205: "Hartley County", 207: "Haskell County", 209: "Hays County",
            211: "Hemphill County", 213: "Henderson County", 215: "Hidalgo County",
            217: "Hill County", 219: "Hockley County", 221: "Hood County",
            223: "Hopkins County", 225: "Houston County", 227: "Howard County",
            229: "Hudspeth County", 231: "Hunt County", 233: "Hutchinson County",
            235: "Irion County", 237: "Jack County", 239: "Jackson County",
            241: "Jasper County", 243: "Jeff Davis County", 245: "Jefferson County",
            247: "Jim Hogg County", 249: "Jim Wells County", 251: "Johnson County",
            253: "Jones County", 255: "Karnes County", 257: "Kaufman County",
            259: "Kendall County", 261: "Kenedy County", 263: "Kent County",
            265: "Kerr County", 267: "Kimble County", 269: "King County",
            271: "Kinney County", 273: "Kleberg County", 275: "Knox County",
            277: "Lamar County", 279: "Lamb County", 281: "Lampasas County",
            283: "La Salle County", 285: "Lavaca County", 287: "Lee County",
            289: "Leon County", 291: "Liberty County", 293: "Limestone County",
            295: "Lipscomb County", 297: "Live Oak County", 299: "Llano County",
            301: "Loving County", 303: "Lubbock County", 305: "Lynn County",
            307: "McCulloch County", 309: "McLennan County", 311: "McMullen County",
            313: "Madison County", 315: "Marion County", 317: "Martin County",
            319: "Mason County", 321: "Matagorda County", 323: "Maverick County",
            325: "Medina County", 327: "Menard County", 329: "Midland County",
            331: "Milam County", 333: "Mills County", 335: "Mitchell County",
            337: "Montague County", 339: "Montgomery County", 341: "Moore County",
            343: "Morris County", 345: "Motley County", 347: "Nacogdoches County",
            349: "Navarro County", 351: "Newton County", 353: "Nolan County",
            355: "Nueces County", 357: "Ochiltree County", 359: "Oldham County",
            361: "Orange County", 363: "Palo Pinto County", 365: "Panola County",
            367: "Parker County", 369: "Parmer County", 371: "Pecos County",
            373: "Polk County", 375: "Potter County", 377: "Presidio County",
            379: "Rains County", 381: "Randall County", 383: "Reagan County",
            385: "Real County", 387: "Red River County", 389: "Reeves County",
            391: "Refugio County", 393: "Roberts County", 395: "Robertson County",
            397: "Rockwall County", 399: "Runnels County", 401: "Rusk County",
            403: "Sabine County", 405: "San Augustine County", 407: "San Jacinto County",
            409: "San Patricio County", 411: "San Saba County", 413: "Schleicher County",
            415: "Scurry County", 417: "Shackelford County", 419: "Shelby County",
            421: "Sherman County", 423: "Smith County", 425: "Somervell County",
            427: "Starr County", 429: "Stephens County", 431: "Sterling County",
            433: "Stonewall County", 435: "Sutton County", 437: "Swisher County",
            439: "Tarrant County", 441: "Taylor County", 443: "Terrell County",
            445: "Terry County", 447: "Throckmorton County", 449: "Titus County",
            451: "Tom Green County", 453: "Travis County", 455: "Trinity County",
            457: "Tyler County", 459: "Upshur County", 461: "Upton County",
            463: "Uvalde County", 465: "Val Verde County", 467: "Van Zandt County",
            469: "Victoria County", 471: "Walker County", 473: "Waller County",
            475: "Ward County", 477: "Washington County", 479: "Webb County",
            481: "Wharton County", 483: "Wheeler County", 485: "Wichita County",
            487: "Wilbarger County", 489: "Willacy County", 491: "Williamson County",
            493: "Wilson County", 495: "Winkler County", 497: "Wise County",
            499: "Wood County", 501: "Yoakum County", 503: "Young County",
            505: "Zapata County", 507: "Zavala County"
        }
        
        county_name = texas_counties.get(county_fips, f"County {county_fips}")
        print(f"   County: {county_name} (FIPS: {county_fips:03d})")
    else:
        print("❌ Could not determine census tract")
        return
    
    # Get ZIP code
    zip_code = analyzer.get_zip_code(lat, lon)
    print(f"   ZIP Code: {zip_code}")
    
    # Now run the full analysis
    print(f"\n🏗️ COMPREHENSIVE LIHTC ANALYSIS:")
    result = analyzer.lookup_qct_status(lat, lon)
    
    # Enhanced reporting
    print(f"\n📊 COMPLETE RESULTS:")
    print(f"Census Tract: {result['census_tract']['name']}")
    print(f"State: {result['state_name']}")
    print(f"County: {county_name}")  # Use our corrected county name
    print(f"ZIP Code: {result.get('zip_code', 'Unknown')}")
    
    # Check QCT data specifically for this tract
    tract_formatted = analyzer.convert_tract_format(tract_info['tract'])
    print(f"\n🔎 QCT DATABASE LOOKUP:")
    print(f"Looking for: State {state_fips}, County {county_fips}, Tract {tract_formatted}")
    
    matching_tract = analyzer.qct_data[
        (analyzer.qct_data['state'] == state_fips) & 
        (analyzer.qct_data['county'] == county_fips) & 
        (analyzer.qct_data['tract'] == tract_formatted)
    ]
    
    if len(matching_tract) > 0:
        record = matching_tract.iloc[0]
        is_qct = record['qct'] == 1
        metro_status = "Metro" if record.get('metro', 0) == 1 else "Non-Metro"
        
        print(f"✅ Tract found in database")
        print(f"   QCT Designation: {'YES' if is_qct else 'NO'}")
        print(f"   Metro Status: {metro_status}")
        print(f"   Poverty Rate (2022): {record.get('pov_rate_22', 0):.1%}")
        print(f"   CBSA: {record.get('cbsa', 'N/A')}")
    else:
        print(f"❌ Tract not found in QCT database")
    
    # Check DDA status for ZIP 78245
    if zip_code:
        print(f"\n🏔️ DDA DATABASE LOOKUP:")
        print(f"Looking for ZIP: {zip_code}")
        
        dda_info = analyzer.lookup_dda_status(zip_code)
        if dda_info:
            print(f"✅ ZIP found in DDA database")
            print(f"   DDA Designation: {'YES' if dda_info['dda_designated'] else 'NO'}")
            if dda_info['dda_designated']:
                print(f"   SAFMR: ${dda_info['safmr']:,.0f}")
                print(f"   LIHTC Max Rent: ${dda_info['lihtc_max_rent']:,.0f}")
                print(f"   Ranking Ratio: {dda_info['ranking_ratio']:.2f}")
        else:
            print(f"❌ ZIP not found in DDA database")
    
    # Final determination
    print(f"\n🎯 FINAL DETERMINATION:")
    qct_qualified = result.get('qct_status') == 'QCT'
    dda_qualified = result.get('dda_status') == 'DDA'
    basis_boost = qct_qualified or dda_qualified
    
    print(f"QCT Status: {'✅ QUALIFIED' if qct_qualified else '❌ NOT QUALIFIED'}")
    print(f"DDA Status: {'✅ QUALIFIED' if dda_qualified else '❌ NOT QUALIFIED'}")
    print(f"130% Basis Boost: {'✅ ELIGIBLE' if basis_boost else '❌ NOT ELIGIBLE'}")
    
    if not basis_boost:
        print(f"\n💡 DEVELOPMENT IMPLICATIONS:")
        print(f"   • Property must use standard LIHTC basis calculation")
        print(f"   • No 30% basis boost available")
        print(f"   • Consider alternative financial structures")
        print(f"   • Focus on other competitive advantages")
    
    return result

if __name__ == "__main__":
    result = enhanced_analysis()