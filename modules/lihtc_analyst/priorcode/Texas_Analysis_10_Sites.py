#!/usr/bin/env python3
"""
HUD QCT/DDA Analysis Tool - Customized for William's Texas Data
Mac QGIS Compatible - Avoids problematic geometry operations
"""

import os
import sys
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import requests
from pathlib import Path
import tempfile
from typing import Dict, List, Tuple, Optional
import time
import re

class TexasHUDAnalyzer:
    def __init__(self, work_dir: str = "./texas_analysis_results"):
        """Initialize with William's specific file paths"""
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True)
        
        # William's specific file paths
        self.base_hud_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD DDA QCT")
        self.poverty_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Poverty Rate Census Tracts (ACS)/texas_low_poverty_tracts.gpkg")
        
        # Data containers
        self.qct_data = None
        self.dda_data = None
        self.poverty_data = None
        
        print(f"Texas HUD Analyzer initialized.")
        print(f"Working directory: {self.work_dir}")
        print(f"HUD data path: {self.base_hud_path}")
        print(f"Poverty data path: {self.poverty_path}")
    
    def backup_progress(self, step_name: str, data_summary: dict = None):
        """Save progress to avoid losing work"""
        backup_file = self.work_dir / f"backup_{step_name}_{int(time.time())}.json"
        
        progress = {
            "step": step_name,
            "timestamp": time.time(),
            "qct_loaded": self.qct_data is not None,
            "dda_loaded": self.dda_data is not None,
            "poverty_loaded": self.poverty_data is not None,
            "data_summary": data_summary or {}
        }
        
        if self.qct_data is not None:
            progress["qct_count"] = len(self.qct_data)
        if self.dda_data is not None:
            progress["dda_count"] = len(self.dda_data)
        if self.poverty_data is not None:
            progress["poverty_count"] = len(self.poverty_data)
        
        with open(backup_file, 'w') as f:
            json.dump(progress, f, indent=2)
        print(f"✓ Progress backed up: {backup_file}")
    
    def load_hud_data(self):
        """Load William's HUD QCT and DDA data"""
        try:
            print("Loading HUD data from your files...")
            
            # Look for QCT files in the HUD directory
            qct_files = []
            dda_files = []
            
            # Check for various file formats
            for pattern in ["*qct*", "*QCT*", "*tract*"]:
                qct_files.extend(list(self.base_hud_path.glob(f"{pattern}.geojson")))
                qct_files.extend(list(self.base_hud_path.glob(f"{pattern}.shp")))
                qct_files.extend(list(self.base_hud_path.glob(f"{pattern}.gpkg")))
            
            for pattern in ["*dda*", "*DDA*"]:
                dda_files.extend(list(self.base_hud_path.glob(f"{pattern}.geojson")))
                dda_files.extend(list(self.base_hud_path.glob(f"{pattern}.shp")))
                dda_files.extend(list(self.base_hud_path.glob(f"{pattern}.gpkg")))
            
            print(f"Found potential QCT files: {[f.name for f in qct_files]}")
            print(f"Found potential DDA files: {[f.name for f in dda_files]}")
            
            # Load QCT data
            if qct_files:
                qct_file = qct_files[0]  # Use first found file
                print(f"Loading QCT data from: {qct_file}")
                self.qct_data = gpd.read_file(qct_file)
                
                # Ensure proper CRS
                if self.qct_data.crs is None:
                    self.qct_data.set_crs('EPSG:4326', inplace=True)
                elif self.qct_data.crs != 'EPSG:4326':
                    self.qct_data = self.qct_data.to_crs('EPSG:4326')
                
                print(f"✓ Loaded QCT data: {len(self.qct_data)} features")
                print(f"  QCT columns: {list(self.qct_data.columns)}")
                
                # Display sample of data structure
                if len(self.qct_data) > 0:
                    sample = self.qct_data.iloc[0]
                    print(f"  Sample QCT record:")
                    for col in ['GEOID', 'STATE', 'COUNTY', 'TRACT', 'NAME']:
                        if col in sample:
                            print(f"    {col}: {sample[col]}")
            
            # Load DDA data
            if dda_files:
                dda_file = dda_files[0]  # Use first found file
                print(f"Loading DDA data from: {dda_file}")
                self.dda_data = gpd.read_file(dda_file)
                
                # Ensure proper CRS
                if self.dda_data.crs is None:
                    self.dda_data.set_crs('EPSG:4326', inplace=True)
                elif self.dda_data.crs != 'EPSG:4326':
                    self.dda_data = self.dda_data.to_crs('EPSG:4326')
                
                print(f"✓ Loaded DDA data: {len(self.dda_data)} features")
                print(f"  DDA columns: {list(self.dda_data.columns)}")
                
                # Display sample of data structure
                if len(self.dda_data) > 0:
                    sample = self.dda_data.iloc[0]
                    print(f"  Sample DDA record:")
                    for col in ['ZCTA5', 'DDA_CODE', 'DDA_TYPE', 'DDA_NAME']:
                        if col in sample:
                            print(f"    {col}: {sample[col]}")
            
            # Load poverty data
            if self.poverty_path.exists():
                print(f"Loading poverty data from: {self.poverty_path}")
                self.poverty_data = gpd.read_file(self.poverty_path)
                
                # Ensure proper CRS
                if self.poverty_data.crs is None:
                    self.poverty_data.set_crs('EPSG:4326', inplace=True)
                elif self.poverty_data.crs != 'EPSG:4326':
                    self.poverty_data = self.poverty_data.to_crs('EPSG:4326')
                
                print(f"✓ Loaded poverty data: {len(self.poverty_data)} features")
                print(f"  Poverty columns: {list(self.poverty_data.columns)}")
                
                # Display sample of poverty data structure
                if len(self.poverty_data) > 0:
                    sample = self.poverty_data.iloc[0]
                    print(f"  Sample poverty record:")
                    for col in self.poverty_data.columns:
                        if 'poverty' in col.lower() or 'rate' in col.lower() or 'GEOID' in col:
                            print(f"    {col}: {sample[col]}")
            
            # Backup progress
            summary = {
                "qct_loaded": self.qct_data is not None,
                "dda_loaded": self.dda_data is not None,
                "poverty_loaded": self.poverty_data is not None
            }
            self.backup_progress("data_loaded", summary)
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading HUD data: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def clean_address(self, address: str) -> List[str]:
        """Create multiple variations of an address for better matching"""
        address = address.strip()
        variations = [address]  # Original address first
        
        # Common address cleaning
        cleaned = address.replace(',', ' ').replace('  ', ' ')
        if cleaned != address:
            variations.append(cleaned)
        
        # Add "TX" if not present and no other state mentioned
        if ', TX' not in address.upper() and address.upper().count(' TX ') == 0:
            if not any(state in address.upper() for state in [' CA ', ' AZ ', ' NM ', ' HI ', ' FL ', ' NY ']):
                variations.append(f"{address}, TX")
        
        # Remove apartment/unit numbers for better geocoding
        no_apt = re.sub(r'(apt\.?|unit|#)\s*\w+', '', address, flags=re.IGNORECASE).strip()
        if no_apt != address and no_apt:
            variations.append(no_apt)
            if ', TX' not in no_apt.upper():
                variations.append(f"{no_apt}, TX")
        
        # Enhanced street type variations for failed geocoding
        street_replacements = [
            ('Drive', ''),           # Remove "Drive" entirely (for Cypress Slough)
            ('Drive', 'Dr'),
            ('Street', 'St'),
            ('Avenue', 'Ave'),
            ('Boulevard', 'Blvd'),
            ('Road', 'Rd'),
            ('Lane', 'Ln'),
            ('Court', 'Ct'),
            ('Circle', 'Cir'),
            ('Place', 'Pl')
        ]
        
        for full_word, abbrev in street_replacements:
            # Try replacing full word with abbreviation
            if full_word in address:
                new_addr = address.replace(full_word, abbrev).strip()
                if new_addr not in variations:
                    variations.append(new_addr)
                    if ', TX' not in new_addr.upper():
                        variations.append(f"{new_addr}, TX")
        
        # Remove extra formatting like "USA"
        no_usa = re.sub(r',?\s*USA\s*$', '', address, flags=re.IGNORECASE).strip()
        if no_usa != address:
            variations.append(no_usa)
        
        # Remove double commas and extra spaces
        for i, addr in enumerate(variations):
            cleaned = re.sub(r',\s*,', ',', addr)  # Remove double commas
            cleaned = re.sub(r'\s+', ' ', cleaned)  # Remove extra spaces
            cleaned = cleaned.strip()
            if cleaned != addr:
                variations.append(cleaned)
        
        return list(set(variations))  # Remove duplicates
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float, str, str, float]]:
        """Enhanced geocoding with multiple attempts and address variations"""
        address_variations = self.clean_address(address)
        
        for i, addr_variant in enumerate(address_variations):
            try:
                print(f"    Attempt {i+1}: {addr_variant}")
                
                # Census Geocoding API
                url = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
                params = {
                    'address': addr_variant,
                    'benchmark': 'Public_AR_Current',
                    'vintage': 'Current_Current',
                    'format': 'json'
                }
                
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('result', {}).get('addressMatches'):
                    match = data['result']['addressMatches'][0]
                    coords = match['coordinates']
                    match_score = match.get('tigerLine', {}).get('tigerLineId', 0)
                    matched_address = match.get('matchedAddress', addr_variant)
                    
                    # Extract census tract GEOID
                    census_tract = None
                    if 'geographies' in match:
                        tracts = match['geographies'].get('Census Tracts', [])
                        if tracts:
                            census_tract = tracts[0].get('GEOID')
                    
                    print(f"    ✅ Matched: {matched_address}")
                    return (coords['x'], coords['y'], census_tract, matched_address, match_score)
                
                # Small delay between attempts
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    ❌ Attempt {i+1} failed: {e}")
                continue
        
        print(f"    ❌ All geocoding attempts failed for: {address}")
        return None
    
    def format_census_tract(self, geoid: str) -> str:
        """Format census tract GEOID into readable format"""
        if not geoid or len(geoid) < 11:
            return geoid
        
        try:
            # GEOID format: SSCCCTTTTTT (State, County, Tract)
            state = geoid[:2]
            county = geoid[2:5]
            tract = geoid[5:]
            
            # Format tract with decimal if needed
            if len(tract) == 6:
                tract_formatted = f"{tract[:4]}.{tract[4:]}"
            else:
                tract_formatted = tract
            
            return f"State {state}, County {county}, Tract {tract_formatted} (GEOID: {geoid})"
        except:
            return geoid
    
    def analyze_address(self, address: str) -> Dict:
        """Main analysis function using point-in-polygon approach"""
        try:
            print(f"\n🔍 Analyzing address: {address}")
            
            # Step 1: Enhanced geocoding with multiple attempts
            geocode_result = self.geocode_address(address)
            if not geocode_result:
                return {"error": "Could not geocode address", "address": address}
            
            lon, lat, census_tract, matched_address, match_score = geocode_result
            point = Point(lon, lat)
            
            result = {
                "address": address,
                "matched_address": matched_address,
                "geocoding_confidence": match_score,
                "longitude": lon,
                "latitude": lat,
                "census_tract": census_tract,
                "census_tract_formatted": self.format_census_tract(census_tract) if census_tract else None,
                "qct_status": False,
                "dda_status": False,
                "metro_status": None,
                "dda_details": {},
                "poverty_rate": None,
                "low_poverty_tract": False,
                "analysis_summary": ""
            }
            
            print(f"  📍 Coordinates: ({lat:.6f}, {lon:.6f})")
            print(f"  🏛️ Census Tract: {result['census_tract_formatted']}")
            if matched_address != address:
                print(f"  📝 Matched as: {matched_address}")
            
            # Step 2: Check QCT status using point-in-polygon
            if self.qct_data is not None:
                print("  🔍 Checking QCT status...")
                qct_intersects = self.qct_data[self.qct_data.contains(point)]
                
                if not qct_intersects.empty:
                    result["qct_status"] = True
                    qct_row = qct_intersects.iloc[0]
                    print(f"  ✅ QCT Status: QUALIFIED")
                    print(f"    QCT GEOID: {qct_row.get('GEOID', 'N/A')}")
                    print(f"    QCT Name: {qct_row.get('NAME', 'N/A')}")
                else:
                    print(f"  ❌ QCT Status: NOT QUALIFIED")
            
            # Step 3: Check DDA status
            if self.dda_data is not None:
                print("  🔍 Checking DDA status...")
                dda_intersects = self.dda_data[self.dda_data.contains(point)]
                
                if not dda_intersects.empty:
                    result["dda_status"] = True
                    dda_row = dda_intersects.iloc[0]
                    
                    # Extract DDA details based on your data structure
                    result["dda_details"] = {
                        "zcta5": dda_row.get('ZCTA5', 'N/A'),
                        "dda_code": dda_row.get('DDA_CODE', 'N/A'),
                        "dda_type": dda_row.get('DDA_TYPE', 'N/A'),
                        "dda_name": dda_row.get('DDA_NAME', 'N/A')
                    }
                    
                    print(f"  ✅ DDA Status: QUALIFIED")
                    print(f"    DDA ZIP: {result['dda_details']['zcta5']}")
                    print(f"    DDA Code: {result['dda_details']['dda_code']}")
                    print(f"    DDA Type: {result['dda_details']['dda_type']}")
                    print(f"    DDA Name: {result['dda_details']['dda_name']}")
                else:
                    print(f"  ❌ DDA Status: NOT QUALIFIED")
            
            # Step 4: Check poverty rate
            if self.poverty_data is not None and census_tract:
                print("  🔍 Checking poverty rate...")
                
                # Try multiple approaches to match census tract
                poverty_match = None
                
                # First try exact GEOID match
                if 'GEOID' in self.poverty_data.columns:
                    poverty_match = self.poverty_data[
                        self.poverty_data['GEOID'].astype(str) == str(census_tract)
                    ]
                
                # If no match, try point-in-polygon with poverty data
                if poverty_match is None or poverty_match.empty:
                    poverty_match = self.poverty_data[self.poverty_data.contains(point)]
                
                if not poverty_match.empty:
                    poverty_row = poverty_match.iloc[0]
                    
                    # Look for poverty rate column - using William's specific column name
                    poverty_rate = None
                    
                    # First try the exact column name from William's data
                    if 'poverty_pct' in poverty_row.index:
                        poverty_rate = poverty_row['poverty_pct']
                    # Fallback to other possible column names
                    else:
                        for col in poverty_row.index:
                            if 'poverty' in col.lower() and ('rate' in col.lower() or 'pct' in col.lower()):
                                poverty_rate = poverty_row[col]
                                break
                            elif col.lower() in ['poverty_rate', 'pov_rate', 'rate', 'poverty_pct']:
                                poverty_rate = poverty_row[col]
                                break
                    
                    if poverty_rate is not None:
                        try:
                            poverty_rate = float(poverty_rate)
                            result["poverty_rate"] = round(poverty_rate, 2)
                            result["low_poverty_tract"] = poverty_rate <= 20.0
                            
                            print(f"  📊 Poverty Rate: {poverty_rate:.2f}%")
                            if result["low_poverty_tract"]:
                                print(f"  ✅ Low Poverty Status: QUALIFIED (≤20%)")
                            else:
                                print(f"  ❌ High Poverty Area: NOT QUALIFIED (>20%)")
                        except (ValueError, TypeError):
                            print(f"  ⚠️ Could not parse poverty rate: {poverty_rate}")
                    else:
                        print(f"  ⚠️ Poverty rate column not found in data")
                else:
                    print(f"  ⚠️ No poverty data found for this location")
            else:
                print(f"  ⚠️ Poverty data not available or no census tract")
            
            # Step 5: Create analysis summary and compact status
            summary_parts = []
            if result["qct_status"]:
                summary_parts.append("QCT Qualified")
            if result["dda_status"]:
                summary_parts.append("DDA Qualified")
            if result["low_poverty_tract"]:
                summary_parts.append("Low Poverty Tract")
            
            if summary_parts:
                result["analysis_summary"] = " + ".join(summary_parts)
            else:
                result["analysis_summary"] = "No special designations"
            
            # Create compact status line with checkmarks/X marks and poverty details
            qct_icon = "✅" if result["qct_status"] else "❌"
            dda_icon = "✅" if result["dda_status"] else "❌"
            
            # Enhanced poverty status with percentage
            if result.get("poverty_rate") is not None:
                if result["low_poverty_tract"]:
                    poverty_icon = f"✅ ({result['poverty_rate']:.1f}%)"
                else:
                    poverty_icon = f"❌ ({result['poverty_rate']:.1f}%)"
            else:
                poverty_icon = "❓ (No data)"
            
            result["compact_status"] = f"QCT: {qct_icon} | DDA: {dda_icon} | Low Poverty: {poverty_icon}"
            
            print(f"  🎯 Final Status: {result['analysis_summary']}")
            print(f"  📊 Quick Status: {result['compact_status']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e), "address": address}
    
    def suggest_address_fixes(self, failed_addresses: List[str]) -> Dict[str, List[str]]:
        """Suggest fixes for addresses that failed geocoding"""
        suggestions = {}
        
        for address in failed_addresses:
            address_suggestions = []
            addr_upper = address.upper()
            
            # Specific fixes for William's known problem addresses
            if 'CYPRESS SLOUGH DRIVE' in addr_upper:
                # Remove "Drive" as William found it works without it
                no_drive = address.replace(' Drive', '').replace(' DRIVE', '')
                address_suggestions.append(no_drive)
                address_suggestions.append(f"{no_drive}, TX")
            
            if 'UNISON RD' in addr_upper:
                # Try variations for the Unison Road address
                address_suggestions.append(address.replace('Unison Rd', 'Unison Road'))
                address_suggestions.append(address.replace('12520', '12520-12522'))  # Sometimes ranges help
                # Try without street number in case it's a newer development
                base_addr = re.sub(r'^\d+\s+', '', address)
                if base_addr != address:
                    address_suggestions.append(base_addr)
            
            if 'ELLA BLVD' in addr_upper:
                # Try variations for Ella Boulevard
                address_suggestions.append(address.replace('Blvd', 'Boulevard'))
                address_suggestions.append(address.replace('Ella Blvd', 'Ella Blvd.'))
            
            # Common issues and suggestions
            if 'STREET' in addr_upper and 'ST' not in addr_upper:
                address_suggestions.append(address.replace('Street', 'St').replace('STREET', 'ST'))
            
            if 'AVENUE' in addr_upper and 'AVE' not in addr_upper:
                address_suggestions.append(address.replace('Avenue', 'Ave').replace('AVENUE', 'AVE'))
            
            if 'BOULEVARD' in addr_upper and 'BLVD' not in addr_upper:
                address_suggestions.append(address.replace('Boulevard', 'Blvd').replace('BOULEVARD', 'BLVD'))
            
            if 'DRIVE' in addr_upper and 'DR' not in addr_upper:
                address_suggestions.append(address.replace('Drive', 'Dr').replace('DRIVE', 'DR'))
                # Also try removing "Drive" entirely
                address_suggestions.append(address.replace(' Drive', '').replace(' DRIVE', ''))
            
            # Add TX if no state
            if ', TX' not in addr_upper and ' TX ' not in addr_upper:
                address_suggestions.append(f"{address}, TX")
            
            # Remove unit/apt info
            clean_addr = re.sub(r'(apt\.?|unit|suite|#)\s*\w+', '', address, flags=re.IGNORECASE).strip()
            if clean_addr != address and clean_addr not in address_suggestions:
                address_suggestions.append(clean_addr)
                if ', TX' not in clean_addr.upper():
                    address_suggestions.append(f"{clean_addr}, TX")
            
            # Try with ZIP code patterns for Houston area
            if not re.search(r'\d{5}', address) and 'houston' in address.lower():
                houston_zips = ['77002', '77003', '77004', '77005']  # Common Houston ZIPs
                for zip_code in houston_zips:
                    address_suggestions.append(f"{address} {zip_code}")
            
            suggestions[address] = address_suggestions
        
        return suggestions
    
    def batch_analyze_with_retry(self, addresses: List[str]) -> pd.DataFrame:
        """Enhanced batch analysis with automatic retry for failed addresses"""
        print(f"\n🚀 Starting enhanced batch analysis of {len(addresses)} addresses...")
        results = []
        failed_addresses = []
        
        # First pass
        for i, address in enumerate(addresses):
            print(f"\n--- Processing {i+1}/{len(addresses)} ---")
            
            result = self.analyze_address(address)
            results.append(result)
            
            if 'error' in result:
                failed_addresses.append(address)
            
            # Save progress every 5 addresses
            if (i + 1) % 5 == 0:
                temp_df = pd.DataFrame(results)
                temp_file = self.work_dir / f"temp_results_{i+1}.csv"
                temp_df.to_csv(temp_file, index=False)
                print(f"🔄 Progress saved: {temp_file}")
            
            # Be nice to the Census API
            time.sleep(1)
        
        # Enhanced retry for failed addresses with more aggressive attempts
        if failed_addresses:
            print(f"\n🔄 Retrying {len(failed_addresses)} failed addresses with enhanced fixes...")
            
            for orig_address in failed_addresses:
                print(f"\n--- Enhanced Retry: {orig_address} ---")
                
                # Create more aggressive address variations
                retry_variations = []
                addr_upper = orig_address.upper()
                
                # Specific enhanced fixes for William's problem addresses
                if 'CYPRESS SLOUGH DRIVE' in addr_upper:
                    retry_variations.extend([
                        orig_address.replace(' Drive', ''),
                        orig_address.replace(' Drive', ', Houston, TX'),
                        orig_address.replace('Cypress Slough Drive', 'Cypress Slough'),
                        orig_address.replace('22214 Cypress Slough Drive', 'Cypress Slough Dr'),
                        '22214 Cypress Slough, Houston, TX 77073',
                        'Cypress Slough Dr, Houston, TX 77073'
                    ])
                
                if 'UNISON' in addr_upper:
                    retry_variations.extend([
                        orig_address.replace('Unison Rd', 'Unison Road'),
                        orig_address.replace('12520', '12500'),  # Try nearby numbers
                        orig_address.replace('12520', '12522'),
                        'Unison Road, Houston, TX 77044',
                        'Unison Dr, Houston, TX 77044',
                        '12520 Unison Street, Houston, TX 77044'
                    ])
                
                if 'ELLA BLVD' in addr_upper:
                    retry_variations.extend([
                        orig_address.replace('Blvd', 'Boulevard'),
                        orig_address.replace('Ella Blvd', 'Ella Boulevard'),
                        orig_address.replace('13450', '13400'),  # Try nearby numbers
                        orig_address.replace('13450', '13500'),
                        'Ella Boulevard, Houston, TX 77067',
                        '13450 Ella Blvd., Houston, TX 77067'
                    ])
                
                # General aggressive variations
                retry_variations.extend([
                    # Remove specific numbers and try just street
                    re.sub(r'^\d+\s+', '', orig_address),
                    # Try with common Houston ZIP codes
                    f"{orig_address}, 77002",
                    f"{orig_address}, 77003",
                    # Remove punctuation
                    orig_address.replace(',', '').replace('.', ''),
                    # Add explicit Texas
                    f"{orig_address}, Texas"
                ])
                
                # Remove duplicates and empty strings
                retry_variations = [addr.strip() for addr in retry_variations if addr.strip()]
                retry_variations = list(dict.fromkeys(retry_variations))  # Remove duplicates preserve order
                
                print(f"  Trying {len(retry_variations)} enhanced variations...")
                
                success = False
                for j, suggested in enumerate(retry_variations):
                    print(f"  Enhanced attempt {j+1}: {suggested}")
                    retry_result = self.analyze_address(suggested)
                    
                    if 'error' not in retry_result:
                        # Update the original result with the successful retry
                        for k, result in enumerate(results):
                            if result.get('address') == orig_address and 'error' in result:
                                # Keep original address but update with successful data
                                retry_result['address'] = orig_address
                                retry_result['suggested_fix'] = suggested
                                results[k] = retry_result
                                success = True
                                print(f"  ✅ SUCCESS with: {suggested}")
                                break
                        break
                    
                    time.sleep(0.5)
                
                if not success:
                    print(f"  ❌ All {len(retry_variations)} enhanced attempts failed for: {orig_address}")
                    print(f"  💡 Manual suggestion: Try searching Google Maps for the exact address")
        
        # Save final results
        final_df = pd.DataFrame(results)
        final_file = self.work_dir / f"final_results_{int(time.time())}.csv"
        final_df.to_csv(final_file, index=False)
        
        print(f"\n✅ Enhanced batch analysis complete!")
        print(f"📁 Results saved to: {final_file}")
        
        return final_df
    
    def create_summary_report(self, results_df: pd.DataFrame, format_type: str = 'both') -> str:
        """Generate detailed summary report in TXT and/or RTF format"""
        if results_df.empty:
            return "No results to report"
        
        total = len(results_df)
        successful = len(results_df[results_df['longitude'].notna()])
        qct_qualified = len(results_df[results_df['qct_status'] == True])
        dda_qualified = len(results_df[results_df['dda_status'] == True])
        low_poverty = len(results_df[results_df['low_poverty_tract'] == True])
        
        # Combination benefits
        qct_and_low_poverty = len(results_df[
            (results_df['qct_status'] == True) & 
            (results_df['low_poverty_tract'] == True)
        ])
        dda_and_low_poverty = len(results_df[
            (results_df['dda_status'] == True) & 
            (results_df['low_poverty_tract'] == True)
        ])
        triple_qualified = len(results_df[
            (results_df['qct_status'] == True) & 
            (results_df['dda_status'] == True) & 
            (results_df['low_poverty_tract'] == True)
        ])
        
        # Create text version
        text_report = f"""
Texas HUD QCT/DDA Analysis Summary Report
========================================

📊 PROCESSING SUMMARY:
Total Addresses: {total}
Successfully Geocoded: {successful} ({successful/total*100:.1f}%)
Failed Geocoding: {total - successful}

🏛️ QCT (QUALIFIED CENSUS TRACT) STATUS:
✅ QCT Qualified: {qct_qualified} ({qct_qualified/total*100:.1f}%)
❌ Non-QCT: {total - qct_qualified} ({(total-qct_qualified)/total*100:.1f}%)

🏗️ DDA (DIFFICULT DEVELOPMENT AREA) STATUS:
✅ DDA Qualified: {dda_qualified} ({dda_qualified/total*100:.1f}%)
❌ Non-DDA: {total - dda_qualified} ({(total-dda_qualified)/total*100:.1f}%)

💰 LOW POVERTY TRACT STATUS (≤20%):
✅ Low Poverty: {low_poverty} ({low_poverty/total*100:.1f}%)
❌ Higher Poverty: {total - low_poverty} ({(total-low_poverty)/total*100:.1f}%)

🎯 COMBINATION BENEFITS:
QCT + Low Poverty: {qct_and_low_poverty} addresses
DDA + Low Poverty: {dda_and_low_poverty} addresses
Triple Qualified (QCT + DDA + Low Poverty): {triple_qualified} addresses

📈 LIHTC IMPLICATIONS:
- QCT Qualified properties can claim 30% basis boost
- DDA Qualified properties can claim 30% basis boost  
- Low Poverty areas may qualify for additional state incentives
- Triple qualified sites have maximum flexibility for tax credit structures

📋 DETAILED RESULTS BY ADDRESS:
"""
        
        # Add detailed results for each address
        for _, row in results_df.iterrows():
            if pd.isna(row.get('longitude')):
                text_report += f"\n❌ {row['address']}: GEOCODING FAILED"
            else:
                text_report += f"\n✅ {row['address']}"
                text_report += f"\n   {row.get('compact_status', 'Status unavailable')}"
                text_report += f"\n   Census Tract: {row.get('census_tract_formatted', row.get('census_tract', 'N/A'))}"
                text_report += f"\n   Full Status: {row['analysis_summary']}"
                if not pd.isna(row.get('poverty_rate')):
                    poverty_status = "Low Poverty Tract" if row.get('low_poverty_tract') else "High Poverty Area"
                    text_report += f"\n   Poverty Status: {poverty_status} ({row['poverty_rate']:.2f}%)"
                if row.get('matched_address') and row['matched_address'] != row['address']:
                    text_report += f"\n   (Matched as: {row['matched_address']})"
                text_report += "\n"
        
        text_report += f"\nGenerated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # Save text report
        if format_type in ['txt', 'both']:
            text_file = self.work_dir / f"analysis_report_{int(time.time())}.txt"
            with open(text_file, 'w') as f:
                f.write(text_report)
            print(f"📋 Text report saved to: {text_file}")
        
        # Create RTF version with better formatting
        if format_type in ['rtf', 'both']:
            rtf_content = self.create_rtf_report(results_df, total, successful, qct_qualified, 
                                               dda_qualified, low_poverty, qct_and_low_poverty, 
                                               dda_and_low_poverty, triple_qualified)
            rtf_file = self.work_dir / f"analysis_report_{int(time.time())}.rtf"
            with open(rtf_file, 'w') as f:
                f.write(rtf_content)
            print(f"📋 RTF report saved to: {rtf_file}")
        
        return text_report
    
    def create_rtf_report(self, results_df, total, successful, qct_qualified, dda_qualified, 
                         low_poverty, qct_and_low_poverty, dda_and_low_poverty, triple_qualified) -> str:
        """Create a formatted RTF report"""
        rtf_content = r"""{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;} {\f1 Arial;} {\f2 Courier New;}}
{\colortbl;\red0\green0\blue0;\red255\green0\blue0;\red0\green128\blue0;\red0\green0\blue255;\red128\green0\blue128;}

\f1\fs24\b Texas HUD QCT/DDA Analysis Summary Report\b0\fs20
\line
\line

\b\fs22 PROCESSING SUMMARY:\b0\fs20
\line
""" + f"""Total Addresses: \\b {total}\\b0
\\line
Successfully Geocoded: \\cf3\\b {successful}\\b0\\cf1 ({successful/total*100:.1f}%)
\\line
Failed Geocoding: \\cf2\\b {total - successful}\\b0\\cf1
\\line
\\line

\\b\\fs22 QCT (QUALIFIED CENSUS TRACT) STATUS:\\b0\\fs20
\\line
\\cf3 QCT Qualified: \\b {qct_qualified}\\b0\\cf1 ({qct_qualified/total*100:.1f}%)
\\line
\\cf2 Non-QCT: \\b {total - qct_qualified}\\b0\\cf1 ({(total-qct_qualified)/total*100:.1f}%)
\\line
\\line

\\b\\fs22 DDA (DIFFICULT DEVELOPMENT AREA) STATUS:\\b0\\fs20
\\line
\\cf3 DDA Qualified: \\b {dda_qualified}\\b0\\cf1 ({dda_qualified/total*100:.1f}%)
\\line
\\cf2 Non-DDA: \\b {total - dda_qualified}\\b0\\cf1 ({(total-dda_qualified)/total*100:.1f}%)
\\line
\\line

\\b\\fs22 LOW POVERTY TRACT STATUS (≤20%):\\b0\\fs20
\\line
\\cf3 Low Poverty: \\b {low_poverty}\\b0\\cf1 ({low_poverty/total*100:.1f}%)
\\line
\\cf2 Higher Poverty: \\b {total - low_poverty}\\b0\\cf1 ({(total-low_poverty)/total*100:.1f}%)
\\line
\\line

\\b\\fs22 COMBINATION BENEFITS:\\b0\\fs20
\\line
\\cf5 QCT + Low Poverty:\\cf1 \\b {qct_and_low_poverty}\\b0 addresses
\\line
\\cf5 DDA + Low Poverty:\\cf1 \\b {dda_and_low_poverty}\\b0 addresses
\\line
\\cf5 Triple Qualified (QCT + DDA + Low Poverty):\\cf1 \\b {triple_qualified}\\b0 addresses
\\line
\\line

\\b\\fs22 LIHTC IMPLICATIONS:\\b0\\fs20
\\line
• QCT Qualified properties can claim 30% basis boost
\\line
• DDA Qualified properties can claim 30% basis boost
\\line
• Low Poverty areas may qualify for additional state incentives
\\line
• Triple qualified sites have maximum flexibility for tax credit structures
\\line
\\line

\\b\\fs22 DETAILED RESULTS BY ADDRESS:\\b0\\fs20
\\line
"""
        
        # Add detailed results for each address
        for _, row in results_df.iterrows():
            if pd.isna(row.get('longitude')):
                rtf_content += f"\\line\\cf2\\b {row['address']}: GEOCODING FAILED\\b0\\cf1"
            else:
                rtf_content += f"\\line\\cf3\\b {row['address']}\\b0\\cf1"
                rtf_content += f"\\line    \\cf4\\b {row.get('compact_status', 'Status unavailable')}\\b0\\cf1"
                rtf_content += f"\\line    Census Tract: \\f2 {row.get('census_tract_formatted', row.get('census_tract', 'N/A'))}\\f1"
                rtf_content += f"\\line    Full Status: \\cf4\\b {row['analysis_summary']}\\b0\\cf1"
                if not pd.isna(row.get('poverty_rate')):
                    poverty_status = "Low Poverty Tract" if row.get('low_poverty_tract') else "High Poverty Area"
                    rtf_content += f"\\line    Poverty Status: \\b {poverty_status} ({row['poverty_rate']:.2f}%)\\b0"
                if row.get('matched_address') and row['matched_address'] != row['address']:
                    rtf_content += f"\\line    (Matched as: {row['matched_address']})"
                rtf_content += "\\line"
        
        rtf_content += f"\\line\\line Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        rtf_content += "\n}"
        
        return rtf_content


# Example usage and testing
if __name__ == "__main__":
    # Initialize the analyzer
    analyzer = TexasHUDAnalyzer()
    
    # Load William's data
    if analyzer.load_hud_data():
        print("\n✅ Data loaded successfully!")
        
        # Test with a single address
        test_addresses = [
            "1600 Pennsylvania Ave NW, Washington, DC",
            "100 Main St, Dallas, TX",
            "500 Commerce St, Fort Worth, TX",
            "1234 Elm Street, Houston"  # Missing TX - will test address cleaning
        ]
        
        print("\n🧪 Testing with sample addresses...")
        for address in test_addresses:
            result = analyzer.analyze_address(address)
            if 'error' not in result:
                print(f"✅ {address}: {result['analysis_summary']}")
                if result.get('matched_address') and result['matched_address'] != address:
                    print(f"   (Geocoded as: {result['matched_address']})")
            else:
                print(f"❌ {address}: {result['error']}")
        
        # William's actual project addresses for testing
        print("\n🏗️ Testing with William's project addresses...")
        project_addresses = [
            "22214 Cypress Slough Drive, Houston, TX 77073",
            "6053 Bellfort St Houston, TX 77033",
            "2904 Greens Rd, Houston, TX 77032",
            "12520 Unison Rd, Houston, TX 77044",
            "13450 Ella Blvd, Houston, TX 77067",
            "3206 Spring Stuebner Rd, Spring, TX 77389",
            "814 Autumnwood Dr Houston",  # Missing state/ZIP - good test case
            "4810 S Acres Dr, Houston, TX, 77048, USA",
            "822 W Greens Rd, Houston, TX 77060",
            "2110 Aldine Western Rd, Houston, TX 77038",
            "4810 S Acres Dr, Houston, TX 77048"
        ]
        
        # Run batch analysis with enhanced retry
        print(f"Starting batch analysis of {len(project_addresses)} project addresses...")
        results_df = analyzer.batch_analyze_with_retry(project_addresses)
        
        # Generate comprehensive report
        print("\n📊 Generating comprehensive reports...")
        report = analyzer.create_summary_report(results_df, format_type='both')
        
        # Print quick summary to console
        print("\n🎯 QUICK SUMMARY:")
        total = len(results_df)
        successful = len(results_df[results_df['longitude'].notna()])
        qct_qualified = len(results_df[results_df['qct_status'] == True])
        dda_qualified = len(results_df[results_df['dda_status'] == True])
        low_poverty = len(results_df[results_df['low_poverty_tract'] == True])
        triple_qualified = len(results_df[
            (results_df['qct_status'] == True) & 
            (results_df['dda_status'] == True) & 
            (results_df['low_poverty_tract'] == True)
        ])
        
        print(f"📍 Successfully geocoded: {successful}/{total}")
        print(f"🏛️ QCT Qualified: {qct_qualified}")
        print(f"🏗️ DDA Qualified: {dda_qualified}")
        print(f"💰 Low Poverty: {low_poverty}")
        print(f"🎯 Triple Qualified: {triple_qualified}")
        
        print("\n✅ Analysis complete! Check the generated files:")
        print("   - CSV file: Contains all detailed results")
        print("   - TXT file: Text summary report")
        print("   - RTF file: Rich formatted report (open in Word/Pages)")
        
        # For custom batch processing, uncomment and modify:
        # custom_addresses = ["Your", "Custom", "Address", "List"]
        # results_df = analyzer.batch_analyze_with_retry(custom_addresses)
        # report = analyzer.create_summary_report(results_df, format_type='both')
    else:
        print("❌ Failed to load data. Please check file paths.")