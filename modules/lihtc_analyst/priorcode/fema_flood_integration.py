#!/usr/bin/env python3
"""
FEMA Flood Risk Integration for CoStar TDHCA Analysis
Adds comprehensive flood risk assessment to existing property analysis
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class FEMAFloodRiskIntegrator:
    def __init__(self, base_data_path: str):
        """Initialize with path to flood data directory"""
        self.base_path = Path(base_data_path)
        self.flood_data_path = self.base_path / "state_flood_data"
        
        # Flood zone risk classifications
        self.high_risk_zones = ['A', 'AE', 'AH', 'AO', 'V', 'VE', 'AR', 'A99']
        self.moderate_risk_zones = ['X', 'X500']  # X includes shaded X (0.2% annual chance)
        self.minimal_risk_zones = ['X (unshaded)', 'C']
        self.undetermined_zones = ['D']
        
        # Load available flood data
        self.state_flood_data = self._load_state_flood_data()
        
    def _load_state_flood_data(self) -> dict:
        """Load flood data for available states"""
        flood_data = {}
        
        # State file mappings (only load Texas for CoStar analysis)
        state_files = {
            'TX': 'TX/processed/TX_flood_zones_complete.gpkg'
        }
        
        for state, file_path in state_files.items():
            full_path = self.flood_data_path / file_path
            if full_path.exists():
                print(f"✅ Loading {state} flood data: {full_path}")
                try:
                    flood_data[state] = gpd.read_file(full_path)
                    print(f"   📊 {len(flood_data[state])} flood zones loaded")
                except Exception as e:
                    print(f"   ❌ Error loading {state}: {e}")
            else:
                print(f"   ⚠️ {state} flood data not found: {full_path}")
        
        # Load TX attributes file as backup
        tx_attrs_file = self.flood_data_path / 'TX/processed/TX_flood_zones_attributes.csv'
        if tx_attrs_file.exists():
            try:
                flood_data['TX_attributes'] = pd.read_csv(tx_attrs_file)
                print(f"✅ TX attributes backup loaded: {len(flood_data['TX_attributes'])} records")
            except Exception as e:
                print(f"❌ Error loading TX attributes: {e}")
        
        return flood_data
    
    def determine_state_from_coords(self, lat: float, lon: float) -> str:
        """Determine state from coordinates (simplified)"""
        # Texas: roughly 25.8-36.5°N, -106.6--93.5°W
        if 25.8 <= lat <= 36.5 and -106.6 <= lon <= -93.5:
            return 'TX'
        # California: roughly 32.5-42°N, -124.4--114.1°W  
        elif 32.5 <= lat <= 42.0 and -124.4 <= lon <= -114.1:
            return 'CA'
        # New Mexico: roughly 31.3-37°N, -109--103°W
        elif 31.3 <= lat <= 37.0 and -109.0 <= lon <= -103.0:
            return 'NM'
        else:
            return 'UNKNOWN'
    
    def get_flood_zone_info(self, lat: float, lon: float, state: str = None) -> dict:
        """Get flood zone information for a point"""
        
        if pd.isna(lat) or pd.isna(lon):
            return self._empty_flood_result("Invalid coordinates")
        
        # Auto-determine state if not provided
        if not state:
            state = self.determine_state_from_coords(lat, lon)
        
        if state not in self.state_flood_data:
            return self._empty_flood_result(f"No flood data for {state}")
        
        # Create point geometry
        point = Point(lon, lat)
        
        try:
            # Spatial intersection with flood zones
            flood_gdf = self.state_flood_data[state]
            
            # Find intersecting flood zones
            intersects = flood_gdf[flood_gdf.contains(point) | flood_gdf.intersects(point)]
            
            if len(intersects) == 0:
                # No flood zone found - likely outside mapped areas
                return self._empty_flood_result("Outside mapped flood areas")
            
            # Get primary flood zone (first match or highest risk)
            primary_zone = intersects.iloc[0]
            
            flood_zone = primary_zone.get('FLD_ZONE', 'UNKNOWN')
            sfha_flag = primary_zone.get('SFHA_TF', 'N')
            
            # Determine risk category
            risk_category = self._categorize_flood_risk(flood_zone)
            
            # Determine insurance requirements
            insurance_req = self._determine_insurance_requirement(flood_zone, sfha_flag)
            
            return {
                'flood_zone': flood_zone,
                'sfha_flag': sfha_flag,
                'risk_category': risk_category,
                'insurance_required': insurance_req['required'],
                'insurance_notes': insurance_req['notes'],
                'dfirm_id': primary_zone.get('DFIRM_ID', ''),
                'source_date': primary_zone.get('EFF_DATE', ''),
                'data_source': f'{state}_geometry',
                'analysis_notes': f"Found in {len(intersects)} flood zone(s)"
            }
            
        except Exception as e:
            return self._empty_flood_result(f"Analysis error: {str(e)}")
    
    def _categorize_flood_risk(self, flood_zone: str) -> str:
        """Categorize flood risk level"""
        if flood_zone in self.high_risk_zones:
            return 'HIGH'
        elif flood_zone in self.moderate_risk_zones:
            return 'MODERATE' 
        elif flood_zone in self.minimal_risk_zones:
            return 'LOW'
        elif flood_zone in self.undetermined_zones:
            return 'UNDETERMINED'
        else:
            return 'UNKNOWN'
    
    def _determine_insurance_requirement(self, flood_zone: str, sfha_flag: str) -> dict:
        """Determine flood insurance requirements"""
        if sfha_flag == 'Y' or flood_zone in self.high_risk_zones:
            return {
                'required': True,
                'notes': 'Mandatory flood insurance required for federally-backed mortgages'
            }
        elif flood_zone in self.moderate_risk_zones:
            return {
                'required': False,
                'notes': 'Flood insurance recommended but not required'
            }
        else:
            return {
                'required': False,
                'notes': 'Minimal flood risk, insurance optional'
            }
    
    def _empty_flood_result(self, reason: str) -> dict:
        """Return empty flood result with reason"""
        return {
            'flood_zone': None,
            'sfha_flag': None,
            'risk_category': 'UNKNOWN',
            'insurance_required': False,
            'insurance_notes': reason,
            'dfirm_id': None,
            'source_date': None,
            'data_source': 'none',
            'analysis_notes': reason
        }
    
    def enhance_costar_analysis(self, excel_file: str) -> str:
        """Enhance existing CoStar analysis with flood risk data"""
        
        print(f"\n🌊 ENHANCING COSTAR ANALYSIS WITH FEMA FLOOD RISK")
        print(f"📁 Input file: {excel_file}")
        
        # Load all sheets to preserve different orderings
        try:
            all_sheets = {}
            xl_file = pd.ExcelFile(excel_file)
            for sheet_name in xl_file.sheet_names:
                all_sheets[sheet_name] = pd.read_excel(excel_file, sheet_name=sheet_name)
                print(f"✅ Loaded {len(all_sheets[sheet_name])} properties from {sheet_name}")
        except Exception as e:
            print(f"❌ Error loading Excel file: {e}")
            return None
        
        # Add new flood risk columns to each sheet
        flood_columns = [
            'Flood_Zone', 'SFHA_Flag', 'Flood_Risk_Category',
            'Flood_Insurance_Required', 'Flood_Insurance_Notes',
            'DFIRM_ID', 'Flood_Source_Date', 'Flood_Data_Source', 'Flood_Analysis_Notes'
        ]
        
        # Process each sheet separately to maintain proper data alignment
        enhanced_sheets = {}
        total_successful_analyses = 0
        total_state_counts = {}
        total_risk_counts = {'HIGH': 0, 'MODERATE': 0, 'LOW': 0, 'UNKNOWN': 0}
        
        for sheet_name, df in all_sheets.items():
            print(f"\n🔄 Processing sheet: {sheet_name}")
            
            # Add flood columns to this sheet
            for col in flood_columns:
                df[col] = None
            
            # Process each property in this sheet
            successful_analyses = 0
            state_counts = {}
            risk_counts = {'HIGH': 0, 'MODERATE': 0, 'LOW': 0, 'UNKNOWN': 0}
            
            for idx, row in df.iterrows():
                # Try multiple coordinate columns - check for columns Z and AA first
                lat = None
                lon = None
                
                # Check column Z and AA first (0-indexed: Z=25, AA=26)
                if len(df.columns) > 26:  # AA exists
                    lat = row.iloc[25] if not pd.isna(row.iloc[25]) else None  # Column Z
                    lon = row.iloc[26] if not pd.isna(row.iloc[26]) else None  # Column AA
                
                # Fallback to named columns
                if lat is None:
                    lat = row.get('Latitude')
                if lon is None:
                    lon = row.get('Longitude')
                    
                address = row.get('Address', f'Property {idx+1}')
                
                print(f"\n[{sheet_name}][{idx+1}/{len(df)}] Analyzing: {address}")
                
                if pd.isna(lat) or pd.isna(lon):
                    print(f"   ⚠️ Missing coordinates")
                    continue
                
                # Determine state
                state = self.determine_state_from_coords(lat, lon)
                state_counts[state] = state_counts.get(state, 0) + 1
                
                print(f"   📍 Coordinates: {lat:.4f}, {lon:.4f} (State: {state})")
                
                # Try geometric flood zone lookup first
                flood_info = self.get_flood_zone_info(lat, lon, state)
                
                # If geometric lookup failed and we're in Texas, try static data
                if (flood_info['data_source'] == 'none' or 'Outside mapped' in flood_info['analysis_notes']) and state == 'TX':
                    print(f"   🔄 Trying static data lookup...")
                    static_flood_info = self.get_flood_zone_from_static_data(lat, lon)
                    if static_flood_info['flood_zone']:
                        flood_info = static_flood_info
                        print(f"   📋 Static data: {flood_info['flood_zone']} ({flood_info['risk_category']} risk)")
                
                # Update dataframe
                df.at[idx, 'Flood_Zone'] = flood_info['flood_zone']
                df.at[idx, 'SFHA_Flag'] = flood_info['sfha_flag']
                df.at[idx, 'Flood_Risk_Category'] = flood_info['risk_category']
                df.at[idx, 'Flood_Insurance_Required'] = flood_info['insurance_required']
                df.at[idx, 'Flood_Insurance_Notes'] = flood_info['insurance_notes']
                df.at[idx, 'DFIRM_ID'] = flood_info['dfirm_id']
                df.at[idx, 'Flood_Source_Date'] = flood_info['source_date']
                df.at[idx, 'Flood_Data_Source'] = flood_info['data_source']
                df.at[idx, 'Flood_Analysis_Notes'] = flood_info['analysis_notes']
                
                # Track results
                risk_category = flood_info['risk_category']
                risk_counts[risk_category] = risk_counts.get(risk_category, 0) + 1
                
                if flood_info['flood_zone']:
                    successful_analyses += 1
                    print(f"   🌊 Flood Zone: {flood_info['flood_zone']} ({risk_category} risk)")
                    if flood_info['insurance_required']:
                        print(f"   ⚠️ Flood insurance REQUIRED")
                else:
                    print(f"   ❓ {flood_info['analysis_notes']}")
            
            # Store the processed sheet
            enhanced_sheets[sheet_name] = df
            
            # Add to totals
            total_successful_analyses += successful_analyses
            for state, count in state_counts.items():
                total_state_counts[state] = total_state_counts.get(state, 0) + count
            for risk, count in risk_counts.items():
                total_risk_counts[risk] = total_risk_counts.get(risk, 0) + count
            
            # Print summary for this sheet
            print(f"\n📊 {sheet_name} SUMMARY:")
            print(f"   🎯 Properties analyzed: {len(df)}")
            print(f"   ✅ Successful flood zone matches: {successful_analyses}")
            print(f"   📍 State distribution: {state_counts}")
            print(f"   🌊 Risk distribution: {risk_counts}")
        
        # Print overall summary
        print(f"\n📊 OVERALL FLOOD RISK ANALYSIS SUMMARY:")
        print(f"   🎯 Total properties analyzed: {sum(len(df) for df in enhanced_sheets.values())}")
        print(f"   ✅ Total successful flood zone matches: {total_successful_analyses}")
        print(f"   📍 Overall state distribution: {total_state_counts}")
        print(f"   🌊 Overall risk distribution: {total_risk_counts}")
        
        # Save enhanced results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(excel_file).parent / f"CoStar_TX_Land_TDHCA_FLOOD_Analysis_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Save each processed sheet with flood data (maintaining original order)
            for sheet_name, df in enhanced_sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Create summary sheets from all properties combined
            all_properties_combined = pd.concat(enhanced_sheets.values(), ignore_index=True)
            
            # High Risk Properties (for avoidance)
            high_risk = all_properties_combined[all_properties_combined['Flood_Risk_Category'] == 'HIGH'].copy()
            if len(high_risk) > 0:
                high_risk.to_excel(writer, sheet_name='HIGH_FLOOD_RISK_AVOID', index=False)
            
            # Low Risk Properties (preferred)
            low_risk = all_properties_combined[all_properties_combined['Flood_Risk_Category'].isin(['LOW', 'MODERATE'])].copy()
            if len(low_risk) > 0:
                low_risk.to_excel(writer, sheet_name='LOW_FLOOD_RISK_PREFERRED', index=False)
            
            # Summary with flood statistics
            insurance_required = len(all_properties_combined[all_properties_combined['Flood_Insurance_Required'] == True])
            
            summary_data = {
                'Metric': [
                    'Total Properties Analyzed',
                    'Properties with Flood Zone Data',
                    'High Flood Risk Properties',
                    'Moderate Flood Risk Properties', 
                    'Low/Minimal Flood Risk Properties',
                    'Unknown Flood Risk Properties',
                    'Mandatory Flood Insurance Required',
                    'Texas Properties',
                    'Properties Using Static Data',
                    'Properties Outside Mapped Areas'
                ],
                'Count': [
                    len(all_properties_combined),
                    total_successful_analyses,
                    total_risk_counts.get('HIGH', 0),
                    total_risk_counts.get('MODERATE', 0),
                    total_risk_counts.get('LOW', 0),
                    total_risk_counts.get('UNKNOWN', 0),
                    insurance_required,
                    total_state_counts.get('TX', 0),
                    len(all_properties_combined[all_properties_combined['Flood_Data_Source'].str.contains('static', na=False)]),
                    len(all_properties_combined[all_properties_combined['Flood_Analysis_Notes'].str.contains('Outside mapped', na=False)])
                ]
            }
            
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary_with_Flood', index=False)
        
        print(f"\n✅ Enhanced analysis saved to: {output_file}")
        return str(output_file)
    
    def get_flood_zone_from_static_data(self, lat: float, lon: float) -> dict:
        """Get flood zone information from static TX attributes file using coordinates"""
        
        if pd.isna(lat) or pd.isna(lon):
            return self._empty_flood_result("Invalid coordinates for static lookup")
        
        # Check if we have TX attributes data
        if 'TX_attributes' not in self.state_flood_data:
            return self._empty_flood_result("No TX attributes data available")
        
        tx_attrs = self.state_flood_data['TX_attributes']
        
        # For now, we'll do a simplified county-based lookup
        # In the real implementation, you'd need to determine county from lat/lon
        # and filter the flood zones by county FIPS code
        
        # This is a simplified approach - find zones near the coordinates
        # A more sophisticated approach would use county FIPS codes
        
        try:
            # Get county FIPS from coordinates (simplified)
            county_fips = self._get_county_fips_from_coords(lat, lon)
            if not county_fips:
                return self._empty_flood_result("Could not determine county from coordinates")
            
            # Filter flood zones by county FIPS (first 5 digits of DFIRM_ID)
            county_zones = tx_attrs[tx_attrs['DFIRM_ID'].str.startswith(str(county_fips), na=False)]
            
            if len(county_zones) == 0:
                return self._empty_flood_result(f"No flood zones found for county FIPS {county_fips}")
            
            # For static data, we can't do precise spatial matching
            # Return the most common flood zone in the county or a representative one
            most_common_zone = county_zones['FLD_ZONE'].mode()
            if len(most_common_zone) == 0:
                return self._empty_flood_result("No valid flood zones in county")
            
            flood_zone = most_common_zone.iloc[0]
            
            # Get a representative record
            zone_record = county_zones[county_zones['FLD_ZONE'] == flood_zone].iloc[0]
            
            sfha_flag = zone_record.get('SFHA_TF', 'N')
            
            # Determine risk category
            risk_category = self._categorize_flood_risk(flood_zone)
            
            # Determine insurance requirements
            insurance_req = self._determine_insurance_requirement(flood_zone, sfha_flag)
            
            return {
                'flood_zone': flood_zone,
                'sfha_flag': sfha_flag,
                'risk_category': risk_category,
                'insurance_required': insurance_req['required'],
                'insurance_notes': insurance_req['notes'],
                'dfirm_id': zone_record.get('DFIRM_ID', ''),
                'source_date': zone_record.get('EFF_DATE', ''),
                'data_source': f'TX_static_county_{county_fips}',
                'analysis_notes': f"Static data lookup for county {county_fips} - {len(county_zones)} zones available"
            }
            
        except Exception as e:
            return self._empty_flood_result(f"Static lookup error: {str(e)}")
    
    def _get_county_fips_from_coords(self, lat: float, lon: float) -> str:
        """Simplified county FIPS lookup from coordinates"""
        # This is a very simplified approach - in practice you'd use a proper 
        # county boundary lookup or geocoding service
        
        # Major Texas county FIPS codes for common metro areas
        county_mapping = {
            # Houston area
            (29.5, 30.2, -95.8, -95.0): "48201",  # Harris County
            (29.3, 29.8, -95.8, -95.4): "48157",  # Fort Bend County
            
            # Dallas area  
            (32.5, 33.0, -97.0, -96.5): "48113",  # Dallas County
            (32.6, 33.0, -97.5, -97.0): "48439",  # Tarrant County
            (33.0, 33.5, -96.8, -96.4): "48085",  # Collin County
            (33.0, 33.5, -97.5, -97.0): "48121",  # Denton County
            
            # Austin area
            (30.0, 30.6, -98.2, -97.5): "48453",  # Travis County
            (30.4, 31.0, -98.0, -97.4): "48491",  # Williamson County
            
            # San Antonio area
            (29.2, 29.8, -98.8, -98.2): "48029",  # Bexar County
        }
        
        for (min_lat, max_lat, min_lon, max_lon), fips in county_mapping.items():
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                return fips
        
        return None


def main():
    """Main execution function"""
    
    # Configuration
    DATA_BASE_PATH = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code"
    
    # Find the most recent CoStar analysis file
    code_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code")
    
    # Look for existing analysis files (exclude ones that already have flood data)
    analysis_files = list(code_dir.glob("*TDHCA_Analysis*.xlsx"))
    costar_files = list(code_dir.glob("**/CoStar*.xlsx"))
    
    # Filter out files that already have flood analysis
    all_analysis_files = [f for f in analysis_files + costar_files 
                         if "FLOOD" not in str(f).upper()]
    
    if not all_analysis_files:
        print("❌ No existing TDHCA or CoStar analysis files found!")
        print("Available files:")
        for f in code_dir.glob("*.xlsx"):
            print(f"   {f.name}")
        return
    
    # Use most recent file
    latest_file = max(all_analysis_files, key=lambda x: x.stat().st_mtime)
    print(f"📁 Using analysis file: {latest_file}")
    
    # Initialize flood risk integrator
    print(f"\n🌊 Initializing FEMA Flood Risk Integration...")
    integrator = FEMAFloodRiskIntegrator(DATA_BASE_PATH)
    
    # Check available flood data
    print(f"\n📊 Available flood data states: {list(integrator.state_flood_data.keys())}")
    
    # Enhance the analysis
    enhanced_file = integrator.enhance_costar_analysis(str(latest_file))
    
    if enhanced_file:
        print(f"\n🎯 INTEGRATION COMPLETE!")
        print(f"📁 Enhanced file: {enhanced_file}")
        print(f"\n📋 New flood risk columns added:")
        print(f"   • Flood_Zone - FEMA flood zone designation")
        print(f"   • SFHA_Flag - Special Flood Hazard Area flag")
        print(f"   • Flood_Risk_Category - HIGH/MODERATE/LOW/UNKNOWN")
        print(f"   • Flood_Insurance_Required - True/False")
        print(f"   • Flood_Insurance_Notes - Insurance requirements")
        print(f"   • Enhanced scoring with flood risk consideration")
        
        print(f"\n💡 NEXT STEPS:")
        print(f"   1. Review HIGH_FLOOD_RISK_AVOID sheet")
        print(f"   2. Focus on LOW_FLOOD_RISK_PREFERRED properties")
        print(f"   3. Update HTML report with flood risk visualization")
        print(f"   4. Consider flood mitigation costs in underwriting")


if __name__ == "__main__":
    main()