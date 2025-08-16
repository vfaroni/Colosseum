#!/usr/bin/env python3
"""
CoStar Texas Land Pre-Filter
Filters 413 CoStar properties for LIHTC viability before expensive Google API calls

Filters:
1. QCT/DDA Status (Federal basis boost eligibility) - ELIMINATES non-viable sites
2. FEMA Flood Zone Analysis - DEPRIORITIZES major flood zones  
3. Sale Status Priority - PRIORITIZES active/available properties

Author: Enhanced for Texas LIHTC Analysis
Date: 2025-06-17
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
import numpy as np
from datetime import datetime

class CoStarTexasPreFilter:
    """Pre-filters CoStar data for LIHTC viability before Google API analysis"""
    
    def __init__(self):
        # Data paths
        self.base_hud_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD DDA QCT")
        self.qct_file = self.base_hud_path / "QUALIFIED_CENSUS_TRACTS_7341711606021821459.gpkg"
        self.dda_file = self.base_hud_path / "Difficult_Development_Areas_-4200740390724245794.gpkg"
        
        # FEMA flood data path
        self.fema_flood_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/state_flood_data")
        
        # CoStar data path
        self.costar_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Costar/TX/CS_Land_TX_1_10ac_06162025.xlsx"
        
        # Load HUD designation data
        self.qct_data = None
        self.dda_data = None
        self.fema_data = None
        
        self.load_federal_designation_data()
        self.load_fema_flood_data()
    
    def load_federal_designation_data(self):
        """Load QCT/DDA shapefiles"""
        try:
            # Load QCT data
            if self.qct_file.exists():
                print(f"Loading QCT data from: {self.qct_file}")
                self.qct_data = gpd.read_file(self.qct_file)
                if self.qct_data.crs != 'EPSG:4326':
                    self.qct_data = self.qct_data.to_crs('EPSG:4326')
                
                # Filter for Texas if there's a state field
                if 'STATE' in self.qct_data.columns:
                    tx_qct = self.qct_data[self.qct_data['STATE'] == 'TX']
                    if len(tx_qct) > 0:
                        self.qct_data = tx_qct
                        print(f"✅ Loaded Texas QCTs: {len(self.qct_data)} features")
                    else:
                        print(f"✅ Loaded QCT data: {len(self.qct_data)} features (checking all states)")
                else:
                    print(f"✅ Loaded QCT data: {len(self.qct_data)} features")
            else:
                print(f"❌ QCT file not found: {self.qct_file}")
            
            # Load DDA data
            if self.dda_file.exists():
                print(f"Loading DDA data from: {self.dda_file}")
                self.dda_data = gpd.read_file(self.dda_file)
                if self.dda_data.crs != 'EPSG:4326':
                    self.dda_data = self.dda_data.to_crs('EPSG:4326')
                
                # Filter for Texas if there's a state field
                if 'STATE' in self.dda_data.columns:
                    tx_dda = self.dda_data[self.dda_data['STATE'] == 'TX']
                    if len(tx_dda) > 0:
                        self.dda_data = tx_dda
                        print(f"✅ Loaded Texas DDAs: {len(self.dda_data)} features")
                    else:
                        print(f"✅ Loaded DDA data: {len(self.dda_data)} features (checking all states)")
                else:
                    print(f"✅ Loaded DDA data: {len(self.dda_data)} features")
            else:
                print(f"❌ DDA file not found: {self.dda_file}")
                
        except Exception as e:
            print(f"❌ Error loading HUD designation data: {e}")
    
    def load_fema_flood_data(self):
        """Load FEMA flood zone data for Texas"""
        try:
            # Look for Texas FEMA flood files
            potential_files = [
                self.fema_flood_path / "texas_flood_zones.shp",
                self.fema_flood_path / "tx_flood_zones.shp", 
                self.fema_flood_path / "FEMA_TX_flood.shp",
                self.fema_flood_path / "texas_fema_flood.gpkg"
            ]
            
            for flood_file in potential_files:
                if flood_file.exists():
                    print(f"Loading FEMA flood data from: {flood_file}")
                    self.fema_data = gpd.read_file(flood_file)
                    if self.fema_data.crs != 'EPSG:4326':
                        self.fema_data = self.fema_data.to_crs('EPSG:4326')
                    print(f"✅ Loaded FEMA flood data: {len(self.fema_data)} features")
                    break
            
            if self.fema_data is None:
                print("⚠️  No FEMA flood data found - will use CoStar flood fields only")
                
        except Exception as e:
            print(f"❌ Error loading FEMA flood data: {e}")
    
    def check_qct_dda_status(self, lat, lng):
        """Check if coordinates are in QCT or DDA"""
        try:
            point = Point(lng, lat)  # Note: Point(longitude, latitude)
            
            is_qct = False
            is_dda = False
            qct_tract = None
            dda_name = None
            
            # Check QCT status
            if self.qct_data is not None:
                qct_match = self.qct_data[self.qct_data.geometry.contains(point)]
                if len(qct_match) > 0:
                    is_qct = True
                    # Get tract identifier if available
                    if 'TRACT' in qct_match.columns:
                        qct_tract = qct_match.iloc[0]['TRACT']
                    elif 'GEOID' in qct_match.columns:
                        qct_tract = qct_match.iloc[0]['GEOID']
            
            # Check DDA status
            if self.dda_data is not None:
                dda_match = self.dda_data[self.dda_data.geometry.contains(point)]
                if len(dda_match) > 0:
                    is_dda = True
                    # Get DDA name if available
                    if 'NAME' in dda_match.columns:
                        dda_name = dda_match.iloc[0]['NAME']
                    elif 'DDA_NAME' in dda_match.columns:
                        dda_name = dda_match.iloc[0]['DDA_NAME']
            
            return {
                'QCT_Status': is_qct,
                'DDA_Status': is_dda,
                'Federal_Basis_Boost': is_qct or is_dda,
                'QCT_Tract': qct_tract,
                'DDA_Name': dda_name
            }
            
        except Exception as e:
            print(f"❌ Error checking QCT/DDA for {lat}, {lng}: {e}")
            return {
                'QCT_Status': False,
                'DDA_Status': False,
                'Federal_Basis_Boost': False,
                'QCT_Tract': None,
                'DDA_Name': None
            }
    
    def check_flood_risk(self, lat, lng, costar_flood_zone=None, costar_flood_risk=None):
        """Analyze flood risk from FEMA data and CoStar fields"""
        try:
            flood_analysis = {
                'FEMA_Flood_Zone': None,
                'FEMA_High_Risk': False,
                'CoStar_Flood_Zone': costar_flood_zone,
                'CoStar_Flood_Risk': costar_flood_risk,
                'Overall_Flood_Risk': 'Unknown',
                'Flood_Priority_Penalty': 0
            }
            
            # Check FEMA data if available
            if self.fema_data is not None:
                point = Point(lng, lat)
                fema_match = self.fema_data[self.fema_data.geometry.contains(point)]
                if len(fema_match) > 0:
                    fema_zone = fema_match.iloc[0].get('FLD_ZONE', 'Unknown')
                    flood_analysis['FEMA_Flood_Zone'] = fema_zone
                    
                    # High-risk FEMA zones
                    high_risk_zones = ['A', 'AE', 'AH', 'AO', 'AR', 'A99', 'V', 'VE']
                    if any(zone in str(fema_zone).upper() for zone in high_risk_zones):
                        flood_analysis['FEMA_High_Risk'] = True
            
            # Analyze CoStar flood data
            costar_high_risk = False
            if costar_flood_zone:
                high_risk_zones = ['A', 'AE', 'AH', 'AO', 'V', 'VE']
                costar_high_risk = any(zone in str(costar_flood_zone).upper() for zone in high_risk_zones)
            
            if costar_flood_risk:
                if 'high' in str(costar_flood_risk).lower() or 'moderate' in str(costar_flood_risk).lower():
                    costar_high_risk = True
            
            # Determine overall flood risk
            if flood_analysis['FEMA_High_Risk'] or costar_high_risk:
                flood_analysis['Overall_Flood_Risk'] = 'High'
                flood_analysis['Flood_Priority_Penalty'] = 10  # Lower priority
            elif costar_flood_zone and 'X' in str(costar_flood_zone).upper():
                flood_analysis['Overall_Flood_Risk'] = 'Low'
                flood_analysis['Flood_Priority_Penalty'] = 0
            else:
                flood_analysis['Overall_Flood_Risk'] = 'Moderate'
                flood_analysis['Flood_Priority_Penalty'] = 2
            
            return flood_analysis
            
        except Exception as e:
            print(f"❌ Error checking flood risk for {lat}, {lng}: {e}")
            return {
                'FEMA_Flood_Zone': None,
                'FEMA_High_Risk': False,
                'CoStar_Flood_Zone': costar_flood_zone,
                'CoStar_Flood_Risk': costar_flood_risk,
                'Overall_Flood_Risk': 'Unknown',
                'Flood_Priority_Penalty': 5
            }
    
    def calculate_priority_score(self, row):
        """Calculate overall priority score for property"""
        score = 100  # Start with perfect score
        
        # Federal basis boost requirement (CRITICAL)
        if not row.get('Federal_Basis_Boost', False):
            return 0  # ELIMINATE - not viable for LIHTC
        
        # Sale status priority
        sale_status = str(row.get('Sale Status', '')).lower()
        if 'active' in sale_status or 'available' in sale_status:
            score += 20  # Boost for available properties
        elif 'under contract' in sale_status or 'pending' in sale_status:
            score -= 30  # Penalize contracted properties
        elif 'sold' in sale_status:
            score -= 50  # Heavy penalty for sold properties
        
        # Flood risk penalty
        score -= row.get('Flood_Priority_Penalty', 0)
        
        # Price considerations (if reasonable for LIHTC)
        price = row.get('Sale Price', 0)
        if price > 0:
            if price > 10000000:  # $10M+ very expensive
                score -= 15
            elif price > 5000000:  # $5M+ expensive
                score -= 8
            elif price < 500000:   # Under $500K potentially good value
                score += 5
        
        # Acreage considerations
        acreage = row.get('Size (SF)', 0)
        if acreage > 0:
            acres = acreage / 43560  # Convert SF to acres
            if 1 <= acres <= 10:  # Ideal size for LIHTC
                score += 10
            elif acres > 20:  # Too large
                score -= 5
        
        return max(0, score)  # Ensure non-negative
    
    def process_costar_data(self):
        """Process all CoStar properties with pre-filtering"""
        print("=== CoStar Texas LIHTC Pre-Filter Analysis ===")
        print(f"Loading CoStar data from: {self.costar_file}")
        
        # Load CoStar data
        df = pd.read_excel(self.costar_file)
        print(f"✅ Loaded {len(df)} CoStar properties")
        
        # Initialize new columns
        new_columns = [
            'QCT_Status', 'DDA_Status', 'Federal_Basis_Boost', 'QCT_Tract', 'DDA_Name',
            'FEMA_Flood_Zone', 'FEMA_High_Risk', 'Overall_Flood_Risk', 'Flood_Priority_Penalty',
            'Priority_Score', 'LIHTC_Viable', 'Analysis_Notes'
        ]
        
        for col in new_columns:
            df[col] = None
        
        # Process each property
        viable_count = 0
        high_priority_count = 0
        
        print("\n🔍 Analyzing properties...")
        for idx, row in df.iterrows():
            if idx % 50 == 0:
                print(f"   Processing {idx+1}/{len(df)} properties...")
            
            lat = row['Latitude']
            lng = row['Longitude']
            
            if pd.isna(lat) or pd.isna(lng):
                df.loc[idx, 'Analysis_Notes'] = 'Missing coordinates'
                df.loc[idx, 'LIHTC_Viable'] = False
                df.loc[idx, 'Priority_Score'] = 0
                continue
            
            # Check QCT/DDA status
            qct_dda_result = self.check_qct_dda_status(lat, lng)
            for key, value in qct_dda_result.items():
                df.loc[idx, key] = value
            
            # Check flood risk
            flood_result = self.check_flood_risk(
                lat, lng, 
                row.get('Flood Zone'), 
                row.get('Flood Risk')
            )
            for key, value in flood_result.items():
                df.loc[idx, key] = value
            
            # Calculate priority score
            row_with_analysis = df.loc[idx]
            priority_score = self.calculate_priority_score(row_with_analysis)
            df.loc[idx, 'Priority_Score'] = priority_score
            
            # Determine viability
            if priority_score > 0:
                df.loc[idx, 'LIHTC_Viable'] = True
                viable_count += 1
                if priority_score >= 80:
                    high_priority_count += 1
            else:
                df.loc[idx, 'LIHTC_Viable'] = False
                df.loc[idx, 'Analysis_Notes'] = 'Not QCT/DDA - eliminated'
        
        print(f"\n📊 Pre-Filter Results:")
        print(f"   Total Properties: {len(df)}")
        print(f"   LIHTC Viable: {viable_count} ({viable_count/len(df)*100:.1f}%)")
        print(f"   High Priority (80+ score): {high_priority_count}")
        print(f"   Eliminated (No QCT/DDA): {len(df) - viable_count}")
        
        # Sort by priority score (highest first)
        df_sorted = df.sort_values('Priority_Score', ascending=False)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"CoStar_Texas_PreFiltered_{timestamp}.xlsx"
        
        # Create summary sheet
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main results
            df_sorted.to_excel(writer, sheet_name='All_Properties', index=False)
            
            # Viable properties only
            viable_df = df_sorted[df_sorted['LIHTC_Viable'] == True]
            viable_df.to_excel(writer, sheet_name='LIHTC_Viable', index=False)
            
            # High priority only
            high_priority_df = df_sorted[df_sorted['Priority_Score'] >= 80]
            high_priority_df.to_excel(writer, sheet_name='High_Priority', index=False)
            
            # Summary statistics
            summary_data = {
                'Metric': [
                    'Total Properties',
                    'LIHTC Viable',
                    'High Priority (80+)',
                    'Medium Priority (50-79)',
                    'Low Priority (1-49)',
                    'Eliminated (No QCT/DDA)',
                    'QCT Properties',
                    'DDA Properties',
                    'High Flood Risk',
                    'Active/Available'
                ],
                'Count': [
                    len(df),
                    len(viable_df),
                    len(df_sorted[df_sorted['Priority_Score'] >= 80]),
                    len(df_sorted[(df_sorted['Priority_Score'] >= 50) & (df_sorted['Priority_Score'] < 80)]),
                    len(df_sorted[(df_sorted['Priority_Score'] >= 1) & (df_sorted['Priority_Score'] < 50)]),
                    len(df_sorted[df_sorted['Priority_Score'] == 0]),
                    len(df_sorted[df_sorted['QCT_Status'] == True]),
                    len(df_sorted[df_sorted['DDA_Status'] == True]),
                    len(df_sorted[df_sorted['Overall_Flood_Risk'] == 'High']),
                    len(df_sorted[df_sorted['Sale Status'].str.contains('Active|Available', case=False, na=False)])
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"\n💾 Results saved to: {output_file}")
        print(f"\n🎯 Next Steps:")
        print(f"   1. Review High_Priority sheet ({high_priority_count} properties)")
        print(f"   2. Focus Google API analysis on viable properties only")
        print(f"   3. Prioritize active/available properties first")
        
        return df_sorted, output_file

def main():
    """Run the CoStar pre-filtering analysis"""
    try:
        prefilter = CoStarTexasPreFilter()
        results_df, output_file = prefilter.process_costar_data()
        
        print(f"\n✅ CoStar pre-filtering complete!")
        print(f"📁 Results file: {output_file}")
        
        return results_df, output_file
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    main()