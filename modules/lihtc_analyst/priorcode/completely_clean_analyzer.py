#!/usr/bin/env python3
"""
HUD QCT/DDA Analysis Tool - Completely Clean Version
Mac QGIS Compatible - No problematic USA removal code
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
                qct_file = qct_files[0]
                print(f"Loading QCT data from: {qct_file}")
                self.qct_data = gpd.read_file(qct_file)
                
                # Ensure proper CRS
                if self.qct_data.crs is None:
                    self.qct_data.set_crs('EPSG:4326', inplace=True)
                elif self.qct_data.crs != 'EPSG:4326':
                    self.qct_data = self.qct_data.to_crs('EPSG:4326')
                
                print(f"✓ Loaded QCT data: {len(self.qct_data)} features")
                print(f"  QCT columns: {list(self.qct_data.columns)}")
                
                if len(self.qct_data) > 0:
                    sample = self.qct_data.iloc[0]
                    print(f"  Sample QCT record:")
                    for col in ['GEOID', 'STATE', 'COUNTY', 'TRACT', 'NAME']:
                        if col in sample:
                            print(f"    {col}: {sample[col]}")
            
            # Load DDA data
            if dda_files:
                dda_file = dda_files[0]
                print(f"Loading DDA data from: {dda_file}")
                self.dda_data = gpd.read_file(dda_file)
                
                # Ensure proper CRS
                if self.dda_data.crs is None:
                    self.dda_data.set_crs('EPSG:4326', inplace=True)
                elif self.dda_data.crs != 'EPSG:4326':
                    self.dda_data = self.dda_data.to_crs('EPSG:4326')
                
                print(f"✓ Loaded DDA data: {len(self.dda_data)} features")
                print(f"  DDA columns: {list(self.dda_data.columns)}")
                
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
        """Create multiple variations of an address for better matching - NO PROBLEMATIC CODE"""
        address = address.strip()
        variations = [address]
        
        # Check if address already has state
        has_state = ', TX' in address.upper() or ' TX ' in address.upper()
        
        # Add TX if missing
        if not has_state:
            variations.append(f"{address}, TX")
        
        # Remove apartment/unit numbers
        no_apt = re.sub(r'(apt\.?|unit|#)\s*\w+', '', address, flags=re.IGNORECASE).strip()
        if no_apt != address and no_apt:
            variations.append(no_apt)
            if not has_state:
                variations.append(f"{no_apt}, TX")
        
        # Street type replacements
        street_types = [
            ('Drive', ''),
            ('Drive', 'Dr'),
            ('Street', 'St'),
            ('Avenue', 'Ave'),
            ('Boulevard', 'Blvd'),
            ('Road', 'Rd')
        ]
        
        for full_word, abbrev in street_types:
            if full_word in address:
                new_addr = address.replace(full_word, abbrev).strip()
                if new_addr not in variations:
                    variations.append(new_addr)
                    if not has_state:
                        variations.append(f"{new_addr}, TX")
        
        # Remove duplicates and empty strings
        clean_variations = []
        seen = set()
        for var in variations:
            var = var.strip()
            if var and var not in seen:
                seen.add(var)
                clean_variations.append(var)
        
        return clean_variations
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float, str, str, float]]:
        """Enhanced geocoding with multiple attempts"""
        address_variations = self.clean_address(address)
        
        for i, addr_variant in enumerate(address_variations):
            try:
                print(f"    Attempt {i+1}: {addr_variant}")
                
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
                    
                    census_tract = None
                    if 'geographies' in match:
                        tracts = match['geographies'].get('Census Tracts', [])
                        if tracts:
                            census_tract = tracts[0].get('GEOID')
                    
                    print(f"    ✅ Matched: {matched_address}")
                    return (coords['x'], coords['y'], census_tract, matched_address, match_score)
                
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
            state = geoid[:2]
            county = geoid[2:5]
            tract = geoid[5:]
            
            if len(tract) == 6:
                tract_formatted = f"{tract[:4]}.{tract[4:]}"
            else:
                tract_formatted = tract
            
            return f"State {state}, County {county}, Tract {tract_formatted} (GEOID: {geoid})"
        except:
            return geoid
    
    def calculate_lihtc_ranking(self, result: Dict) -> Dict:
        """Calculate LIHTC project ranking"""
        if 'error' in result:
            return {
                "category": "FIRM NO", 
                "score": 0,
                "description": "Geocoding failed",
                "reasoning": "Cannot determine qualifications"
            }
        
        qct_qualified = result.get("qct_status", False)
        dda_qualified = result.get("dda_status", False) 
        low_poverty = result.get("low_poverty_tract", False)
        poverty_rate = result.get("poverty_rate")
        
        if qct_qualified and dda_qualified and low_poverty:
            return {
                "category": "BEST",
                "score": 10,
                "description": "Triple Qualified - Maximum Benefits",
                "reasoning": "QCT + DDA (30% basis boost) + Low Poverty"
            }
        elif qct_qualified and dda_qualified:
            return {
                "category": "BEST", 
                "score": 9,
                "description": "Dual Qualified - Excellent Benefits", 
                "reasoning": "QCT + DDA = 30% basis boost available"
            }
        elif (qct_qualified or dda_qualified) and low_poverty:
            basis_type = "QCT" if qct_qualified else "DDA"
            return {
                "category": "GOOD",
                "score": 8,
                "description": f"{basis_type} + Low Poverty",
                "reasoning": f"{basis_type} qualification + Low Poverty benefits"
            }
        elif qct_qualified or dda_qualified:
            basis_type = "QCT" if qct_qualified else "DDA" 
            return {
                "category": "GOOD",
                "score": 7,
                "description": f"{basis_type} Qualified Only",
                "reasoning": f"{basis_type} qualification = 30% basis boost"
            }
        elif low_poverty:
            return {
                "category": "MAYBE",
                "score": 5,
                "description": "Low Poverty Only",
                "reasoning": "Low Poverty area - state incentives possible"
            }
        else:
            return {
                "category": "FIRM NO",
                "score": 1,
                "description": "No Qualifications",
                "reasoning": "No QCT, DDA, or Low Poverty qualifications"
            }
    
    def analyze_address(self, address: str) -> Dict:
        """Main analysis function"""
        try:
            print(f"\n🔍 Analyzing address: {address}")
            
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
                "dda_details": {},
                "poverty_rate": None,
                "low_poverty_tract": False,
                "analysis_summary": ""
            }
            
            print(f"  📍 Coordinates: ({lat:.6f}, {lon:.6f})")
            print(f"  🏛️ Census Tract: {result['census_tract_formatted']}")
            if matched_address != address:
                print(f"  📝 Matched as: {matched_address}")
            
            # Check QCT status
            if self.qct_data is not None:
                print("  🔍 Checking QCT status...")
                qct_intersects = self.qct_data[self.qct_data.contains(point)]
                
                if not qct_intersects.empty:
                    result["qct_status"] = True
                    qct_row = qct_intersects.iloc[0]
                    print(f"  ✅ QCT Status: QUALIFIED")
                    print(f"    QCT GEOID: {qct_row.get('GEOID', 'N/A')}")
                else:
                    print(f"  ❌ QCT Status: NOT QUALIFIED")
            
            # Check DDA status
            if self.dda_data is not None:
                print("  🔍 Checking DDA status...")
                dda_intersects = self.dda_data[self.dda_data.contains(point)]
                
                if not dda_intersects.empty:
                    result["dda_status"] = True
                    dda_row = dda_intersects.iloc[0]
                    
                    result["dda_details"] = {
                        "zcta5": dda_row.get('ZCTA5', 'N/A'),
                        "dda_code": dda_row.get('DDA_CODE', 'N/A'),
                        "dda_type": dda_row.get('DDA_TYPE', 'N/A'),
                        "dda_name": dda_row.get('DDA_NAME', 'N/A')
                    }
                    
                    print(f"  ✅ DDA Status: QUALIFIED")
                    print(f"    DDA ZIP: {result['dda_details']['zcta5']}")
                else:
                    print(f"  ❌ DDA Status: NOT QUALIFIED")
            
            # Check poverty rate - enhanced lookup
            if self.poverty_data is not None and census_tract:
                print("  🔍 Checking poverty rate...")
                
                poverty_match = None
                
                # Try multiple matching approaches
                if 'GEOID' in self.poverty_data.columns:
                    # First try exact GEOID match
                    poverty_match = self.poverty_data[
                        self.poverty_data['GEOID'].astype(str) == str(census_tract)
                    ]
                    
                    # If no exact match, try without leading zeros or other variations
                    if poverty_match.empty:
                        # Try matching the last 6 digits (tract portion)
                        tract_part = str(census_tract)[-6:] if len(str(census_tract)) >= 6 else str(census_tract)
                        poverty_match = self.poverty_data[
                            self.poverty_data['GEOID'].astype(str).str.endswith(tract_part)
                        ]
                
                # If still no match, try point-in-polygon
                if poverty_match is None or poverty_match.empty:
                    print("    Trying point-in-polygon for poverty data...")
                    poverty_match = self.poverty_data[self.poverty_data.contains(point)]
                
                if not poverty_match.empty:
                    poverty_row = poverty_match.iloc[0]
                    print(f"    Found poverty data for GEOID: {poverty_row.get('GEOID', 'N/A')}")
                    
                    # Look for poverty rate column
                    poverty_rate = None
                    if 'poverty_pct' in poverty_row.index:
                        poverty_rate = poverty_row['poverty_pct']
                    elif 'POVERTY_PCT' in poverty_row.index:
                        poverty_rate = poverty_row['POVERTY_PCT']
                    else:
                        # Search for any column with poverty in the name
                        for col in poverty_row.index:
                            if 'poverty' in col.lower() and ('pct' in col.lower() or 'rate' in col.lower()):
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
                        print(f"  ⚠️ Poverty rate column not found in poverty data")
                        print(f"    Available columns: {list(poverty_row.index)}")
                else:
                    print(f"  ⚠️ No poverty data found for census tract {census_tract}")
            else:
                print(f"  ⚠️ No poverty data available or no census tract")
            
            # Create summary
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
            
            # Create compact status with icons
            qct_icon = "✅" if result["qct_status"] else "❌"
            dda_icon = "✅" if result["dda_status"] else "❌"
            
            if result.get("poverty_rate") is not None:
                if result["low_poverty_tract"]:
                    poverty_icon = f"✅ ({result['poverty_rate']:.1f}%)"
                else:
                    poverty_icon = f"❌ ({result['poverty_rate']:.1f}%)"
            else:
                poverty_icon = "❓ (No data)"
            
            result["compact_status"] = f"QCT: {qct_icon} | DDA: {dda_icon} | Low Poverty: {poverty_icon}"
            
            # Create Google Maps link
            import urllib.parse
            encoded_address = urllib.parse.quote_plus(address)
            result["google_maps_link"] = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
            
            # Calculate ranking
            result["lihtc_ranking"] = self.calculate_lihtc_ranking(result)
            
            print(f"  🎯 Final Status: {result['analysis_summary']}")
            print(f"  📊 Quick Status: {result['compact_status']}")
            print(f"  🏆 LIHTC Ranking: {result['lihtc_ranking']['category']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return {"error": str(e), "address": address}
    
    def batch_analyze(self, addresses: List[str]) -> pd.DataFrame:
        """Analyze multiple addresses"""
        print(f"\n🚀 Starting batch analysis of {len(addresses)} addresses...")
        results = []
        
        for i, address in enumerate(addresses):
            print(f"\n--- Processing {i+1}/{len(addresses)} ---")
            
            result = self.analyze_address(address)
            results.append(result)
            
            if (i + 1) % 5 == 0:
                temp_df = pd.DataFrame(results)
                temp_file = self.work_dir / f"temp_results_{i+1}.csv"
                temp_df.to_csv(temp_file, index=False)
                print(f"🔄 Progress saved")
            
            time.sleep(1)
        
        # Sort by ranking
        final_df = pd.DataFrame(results)
        
        def get_sort_key(row):
            if 'error' in row or pd.isna(row.get('longitude')):
                return (0, row.get('address', ''))
            ranking = row.get('lihtc_ranking', {})
            return (ranking.get('score', 0), row.get('address', ''))
        
        results_list = final_df.to_dict('records')
        results_list.sort(key=get_sort_key, reverse=True)
        final_df = pd.DataFrame(results_list)
        
        final_file = self.work_dir / f"final_results_{int(time.time())}.csv"
        final_df.to_csv(final_file, index=False)
        
        print(f"\n✅ Analysis complete! Results saved to: {final_file}")
        return final_df
    
    def create_report(self, results_df: pd.DataFrame) -> str:
        """Generate clean, human-readable reports in both TXT and RTF formats"""
        total = len(results_df)
        successful = len(results_df[results_df['longitude'].notna()])
        qct_qualified = len(results_df[results_df['qct_status'] == True])
        dda_qualified = len(results_df[results_df['dda_status'] == True])
        low_poverty = len(results_df[results_df['low_poverty_tract'] == True])
        
        # Count rankings manually to avoid pandas issues
        best_count = 0
        good_count = 0
        maybe_count = 0
        firm_no_count = 0
        
        for _, row in results_df.iterrows():
            ranking = row.get('lihtc_ranking')
            if isinstance(ranking, dict):
                category = ranking.get('category')
                if category == 'BEST':
                    best_count += 1
                elif category == 'GOOD':
                    good_count += 1
                elif category == 'MAYBE':
                    maybe_count += 1
                elif category == 'FIRM NO':
                    firm_no_count += 1
        
        # Create clean, human-readable text report
        report = f"""Texas HUD QCT/DDA Analysis Summary Report
========================================

EXECUTIVE SUMMARY:
• Total Properties Analyzed: {total}
• Successfully Geocoded: {successful} ({successful/total*100:.0f}%)
• QCT Qualified: {qct_qualified} (30% basis boost eligible)
• DDA Qualified: {dda_qualified} (30% basis boost eligible)
• Low Poverty Areas: {low_poverty} (state incentive eligible)

LIHTC PROJECT RANKINGS:
🥇 BEST Projects: {best_count} (Immediate development priority)
🥈 GOOD Projects: {good_count} (Strong candidates)
🥉 MAYBE Projects: {maybe_count} (Consider with other factors)
❌ FIRM NO: {firm_no_count} (Avoid for LIHTC)

DETAILED PROPERTY ANALYSIS (Ranked by LIHTC Viability):
"""
        
        # Add clean property details
        rank_number = 1
        for _, row in results_df.iterrows():
            if pd.isna(row.get('longitude')):
                report += f"\n❌ FAILED: {row['address']}"
                report += f"\n   Status: Could not locate address"
                report += f"\n   Action: Verify address or find alternative location"
                report += f"\n   Google Maps: {row.get('google_maps_link', 'N/A')}\n"
            else:
                ranking = row.get('lihtc_ranking', {})
                if isinstance(ranking, dict):
                    category = ranking.get('category', 'UNKNOWN')
                    description = ranking.get('description', 'N/A')
                    reasoning = ranking.get('reasoning', 'N/A')
                else:
                    category = 'UNKNOWN'
                    description = 'N/A'
                    reasoning = 'N/A'
                
                emoji = {"BEST": "🥇", "GOOD": "🥈", "MAYBE": "🥉", "FIRM NO": "❌"}.get(category, "❓")
                
                # Clean status display
                qct_status = "✅ Qualified" if row.get('qct_status') else "❌ Not Qualified"
                dda_status = "✅ Qualified" if row.get('dda_status') else "❌ Not Qualified"
                
                poverty_rate = row.get('poverty_rate')
                if poverty_rate is not None:
                    if row.get('low_poverty_tract'):
                        poverty_status = f"✅ Low Poverty ({poverty_rate:.1f}%)"
                    else:
                        poverty_status = f"❌ High Poverty ({poverty_rate:.1f}%)"
                else:
                    poverty_status = "❓ No Data Available"
                
                report += f"\n{rank_number}. {emoji} {row['address']}"
                report += f"\n   LIHTC Rating: {category} - {description}"
                report += f"\n   QCT Status: {qct_status}"
                report += f"\n   DDA Status: {dda_status}"
                report += f"\n   Poverty Status: {poverty_status}"
                report += f"\n   Investment Logic: {reasoning}"
                if row.get('matched_address') and row['matched_address'] != row['address']:
                    report += f"\n   Geocoded As: {row['matched_address']}"
                report += f"\n   Google Maps: {row.get('google_maps_link', 'N/A')}"
                report += f"\n   Census Tract: {row.get('census_tract_formatted', 'N/A')}\n"
                
                if category in ['BEST', 'GOOD']:
                    rank_number += 1
        
        # Save text report
        report_file = self.work_dir / f"clean_analysis_report_{int(time.time())}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"📋 Clean text report saved to: {report_file}")
        
        # Create RTF version
        self.create_rtf_report(results_df, total, successful, qct_qualified, dda_qualified, 
                              low_poverty, best_count, good_count, maybe_count, firm_no_count)
        
        return report
    
    def create_rtf_report(self, results_df, total, successful, qct_qualified, dda_qualified, 
                         low_poverty, best_count, good_count, maybe_count, firm_no_count):
        """Create a clean RTF report for professional presentation"""
        
        rtf_content = r"""{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;} {\f1 Arial;} {\f2 Courier New;}}
{\colortbl;\red0\green0\blue0;\red255\green0\blue0;\red0\green128\blue0;\red0\green0\blue255;\red128\green0\blue128;\red255\green165\blue0;}

\f1\fs28\b Texas HUD QCT/DDA Analysis Summary Report\b0\fs22
\line
\line

\b\fs24 EXECUTIVE SUMMARY:\b0\fs20
\line
""" + f"""• Total Properties Analyzed: \\b {total}\\b0
\\line
• Successfully Geocoded: \\cf3\\b {successful}\\b0\\cf1 ({successful/total*100:.0f} percent)
\\line
• QCT Qualified: \\cf3\\b {qct_qualified}\\b0\\cf1 (30 percent basis boost eligible)
\\line
• DDA Qualified: \\cf3\\b {dda_qualified}\\b0\\cf1 (30 percent basis boost eligible)
\\line
• Low Poverty Areas: \\cf3\\b {low_poverty}\\b0\\cf1 (state incentive eligible)
\\line
\\line

\\b\\fs24 LIHTC PROJECT RANKINGS:\\b0\\fs20
\\line
\\cf3 BEST Projects: \\b {best_count}\\b0\\cf1 (Immediate development priority)
\\line
\\cf6 GOOD Projects: \\b {good_count}\\b0\\cf1 (Strong candidates)
\\line
\\cf4 MAYBE Projects: \\b {maybe_count}\\b0\\cf1 (Consider with other factors)
\\line
\\cf2 FIRM NO: \\b {firm_no_count}\\b0\\cf1 (Avoid for LIHTC)
\\line
\\line

\\b\\fs24 DETAILED PROPERTY ANALYSIS (Ranked by LIHTC Viability):\\b0\\fs20
\\line
"""
        
        # Add clean property details in RTF
        rank_number = 1
        for _, row in results_df.iterrows():
            if pd.isna(row.get('longitude')):
                rtf_content += f"\\line\\cf2\\b FAILED: {row['address']}\\b0\\cf1"
                rtf_content += f"\\line Status: Could not locate address"
                rtf_content += f"\\line Action: Verify address or find alternative location"
            else:
                ranking = row.get('lihtc_ranking', {})
                if isinstance(ranking, dict):
                    category = ranking.get('category', 'UNKNOWN')
                    description = ranking.get('description', 'N/A')
                    reasoning = ranking.get('reasoning', 'N/A')
                else:
                    category = 'UNKNOWN'
                    description = 'N/A'
                    reasoning = 'N/A'
                
                # Color coding by ranking
                ranking_color = {"BEST": "\\cf3", "GOOD": "\\cf6", "MAYBE": "\\cf4", "FIRM NO": "\\cf2"}.get(category, "\\cf1")
                
                # Clean status display for RTF
                qct_status = "Qualified" if row.get('qct_status') else "Not Qualified"
                dda_status = "Qualified" if row.get('dda_status') else "Not Qualified"
                
                poverty_rate = row.get('poverty_rate')
                if poverty_rate is not None:
                    if row.get('low_poverty_tract'):
                        poverty_status = f"Low Poverty ({poverty_rate:.1f} percent)"
                    else:
                        poverty_status = f"High Poverty ({poverty_rate:.1f} percent)"
                else:
                    poverty_status = "No Data Available"
                
                rtf_content += f"\\line{ranking_color}\\b {rank_number}. {row['address']}\\b0\\cf1"
                rtf_content += f"\\line LIHTC Rating: \\b {category} - {description}\\b0"
                rtf_content += f"\\line QCT Status: {qct_status}"
                rtf_content += f"\\line DDA Status: {dda_status}"
                rtf_content += f"\\line Poverty Status: {poverty_status}"
                rtf_content += f"\\line Investment Logic: {reasoning}"
                if row.get('matched_address') and row['matched_address'] != row['address']:
                    rtf_content += f"\\line Geocoded As: {row['matched_address']}"
                rtf_content += f"\\line Google Maps: {row.get('google_maps_link', 'N/A')}"
                rtf_content += "\\line"
                
                if category in ['BEST', 'GOOD']:
                    rank_number += 1
        
        rtf_content += f"\\line\\line Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        rtf_content += "\n}"
        
        # Save RTF report
        rtf_file = self.work_dir / f"clean_analysis_report_{int(time.time())}.rtf"
        with open(rtf_file, 'w') as f:
            f.write(rtf_content)
        print(f"📋 Clean RTF report saved to: {rtf_file}")
        
        return rtf_content


# Example usage
if __name__ == "__main__":
    analyzer = TexasHUDAnalyzer()
    
    if analyzer.load_hud_data():
        print("\n✅ Data loaded successfully!")
        
        # Your project addresses
        project_addresses = [
            "22214 Cypress Slough Drive, Houston, TX 77073",
            "6053 Bellfort St Houston, TX 77033",
            "2904 Greens Rd, Houston, TX 77032",
            "12520 Unison Rd, Houston, TX 77044",
            "13450 Ella Blvd, Houston, TX 77067",
            "3206 Spring Stuebner Rd, Spring, TX 77389",
            "814 Autumnwood Dr, Houston, TX",
            "4810 S Acres Dr, Houston, TX, 77048",
            "822 W Greens Rd, Houston, TX 77060",
            "2110 Aldine Western Rd, Houston, TX 77038",
            "4810 S Acres Dr, Houston, TX 77048"
        ]
        
        # Run analysis
        results_df = analyzer.batch_analyze(project_addresses)
        
        # Create report
        report = analyzer.create_report(results_df)
        
        # Show summary
        print("\n🎯 QUICK SUMMARY:")
        total = len(results_df)
        successful = len(results_df[results_df['longitude'].notna()])
        
        # Count rankings manually to avoid pandas issues
        best_count = 0
        good_count = 0
        for _, row in results_df.iterrows():
            ranking = row.get('lihtc_ranking')
            if isinstance(ranking, dict):
                category = ranking.get('category')
                if category == 'BEST':
                    best_count += 1
                elif category == 'GOOD':
                    good_count += 1
        
        print(f"📍 Successfully geocoded: {successful}/{total}")
        print(f"🥇 BEST Projects: {best_count}")
        print(f"🥈 GOOD Projects: {good_count}")
        
        print("\n✅ Analysis complete!")
    else:
        print("❌ Failed to load data.")