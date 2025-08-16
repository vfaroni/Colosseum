#!/usr/bin/env python3
"""
Get Parcel Sizes for D'Marco Region 3 Sites
Uses multiple data sources to determine acreage:
1. County assessor APIs where available
2. Google Maps API for property data
3. Census/TIGER data for basic property boundaries
4. Manual lookup guidance for complex properties

Author: LIHTC Analysis System
Date: 2025-06-25
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
import requests
import time
import json

class Region3ParcelAnalyzer:
    """Get parcel sizes for Region 3 properties"""
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # APIs
        self.google_api_key = "AIzaSyBlOVHaaTw9nbgBlIuF90xlXHbgfzvUWAM"  # From CLAUDE.md
        
        # County assessor endpoints (Texas counties)
        self.county_apis = {
            'COLLIN': {
                'name': 'Collin County',
                'api_base': 'https://arcgis.collincountytx.gov/arcgis/rest/services',
                'parcels_service': '/ParcelFabric/ParcelFabric/MapServer/0/query'
            },
            'HARRIS': {
                'name': 'Harris County', 
                'api_base': 'https://gis-txhcad.opendata.arcgis.com/datasets',
                'parcels_service': None  # Different structure
            },
            'DENTON': {
                'name': 'Denton County',
                'api_base': 'https://gis.dentoncounty.gov/arcgis/rest/services',
                'parcels_service': '/Parcels/MapServer/0/query'
            }
        }
        
    def load_region3_sites(self):
        """Load the corrected Region 3 analysis"""
        code_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code")
        
        # Find the most recent corrected file
        corrected_files = list(code_path.glob("DMarco_Region3_Aubrey_Corrected_*.xlsx"))
        if not corrected_files:
            # Fall back to original analysis
            corrected_files = list(code_path.glob("DMarco_Region3_Complete_Analysis_*.xlsx"))
        
        if not corrected_files:
            self.logger.error("No Region 3 analysis files found!")
            return None
            
        latest_file = max(corrected_files, key=lambda x: x.stat().st_mtime)
        self.logger.info(f"Loading sites from: {latest_file}")
        
        # Load the main sheet
        all_sheets = pd.read_excel(latest_file, sheet_name=None)
        
        if 'All_Sites_Corrected' in all_sheets:
            df = all_sheets['All_Sites_Corrected']
        elif 'All_Region3_Sites' in all_sheets:
            df = all_sheets['All_Region3_Sites']
        else:
            # Find the main data sheet
            for sheet_name, sheet_df in all_sheets.items():
                if len(sheet_df) > 20:
                    df = sheet_df
                    break
        
        return df
    
    def query_collin_county_parcels(self, lat, lng, address=None):
        """Query Collin County parcel data"""
        try:
            # Collin County ArcGIS REST service
            base_url = "https://arcgis.collincountytx.gov/arcgis/rest/services/ParcelFabric/ParcelFabric/MapServer/0/query"
            
            params = {
                'where': '1=1',
                'geometry': f'{lng},{lat}',
                'geometryType': 'esriGeometryPoint',
                'spatialRel': 'esriSpatialRelIntersects',
                'outFields': 'PARCEL_ID,ACREAGE,OWNER_NAME,SITUS_ADDRESS,LEGAL_DESC',
                'returnGeometry': 'false',
                'f': 'json'
            }
            
            response = requests.get(base_url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if 'features' in data and data['features']:
                    feature = data['features'][0]['attributes']
                    return {
                        'source': 'Collin County Assessor',
                        'parcel_id': feature.get('PARCEL_ID', ''),
                        'acreage': feature.get('ACREAGE', None),
                        'owner': feature.get('OWNER_NAME', ''),
                        'address': feature.get('SITUS_ADDRESS', ''),
                        'legal_desc': feature.get('LEGAL_DESC', '')
                    }
        except Exception as e:
            self.logger.warning(f"Collin County query failed: {e}")
        
        return None
    
    def query_denton_county_parcels(self, lat, lng, address=None):
        """Query Denton County parcel data"""
        try:
            base_url = "https://gis.dentoncounty.gov/arcgis/rest/services/Parcels/MapServer/0/query"
            
            params = {
                'where': '1=1',
                'geometry': f'{lng},{lat}',
                'geometryType': 'esriGeometryPoint',
                'spatialRel': 'esriSpatialRelIntersects',
                'outFields': 'PARCEL_NUM,ACRES,OWNER_NAME,SITUS_ADDR,LEGAL_DESC',
                'returnGeometry': 'false',
                'f': 'json'
            }
            
            response = requests.get(base_url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if 'features' in data and data['features']:
                    feature = data['features'][0]['attributes']
                    return {
                        'source': 'Denton County Assessor',
                        'parcel_id': feature.get('PARCEL_NUM', ''),
                        'acreage': feature.get('ACRES', None),
                        'owner': feature.get('OWNER_NAME', ''),
                        'address': feature.get('SITUS_ADDR', ''),
                        'legal_desc': feature.get('LEGAL_DESC', '')
                    }
        except Exception as e:
            self.logger.warning(f"Denton County query failed: {e}")
        
        return None
    
    def query_harris_county_parcels(self, lat, lng, address=None):
        """Query Harris County parcel data (different API structure)"""
        try:
            # Harris County uses different ArcGIS service
            # This is a simplified approach - Harris County has complex parcel data
            base_url = "https://services.arcgis.com/su8ic9KbA7PYVhpd/arcgis/rest/services/Real_Property_Accounts/FeatureServer/0/query"
            
            params = {
                'where': '1=1',
                'geometry': f'{lng},{lat}',
                'geometryType': 'esriGeometryPoint',
                'spatialRel': 'esriSpatialRelIntersects',
                'outFields': 'HCAD_NUM,LAND_ACRES,OWNER_NAME,PROP_ADDR',
                'returnGeometry': 'false',
                'f': 'json'
            }
            
            response = requests.get(base_url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if 'features' in data and data['features']:
                    feature = data['features'][0]['attributes']
                    return {
                        'source': 'Harris County Assessor',
                        'parcel_id': feature.get('HCAD_NUM', ''),
                        'acreage': feature.get('LAND_ACRES', None),
                        'owner': feature.get('OWNER_NAME', ''),
                        'address': feature.get('PROP_ADDR', ''),
                        'legal_desc': ''
                    }
        except Exception as e:
            self.logger.warning(f"Harris County query failed: {e}")
        
        return None
    
    def get_google_maps_data(self, lat, lng, address=None):
        """Get property info from Google Maps API"""
        try:
            # Google Places API for nearby property data
            base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            
            params = {
                'location': f'{lat},{lng}',
                'radius': 50,  # 50 meter radius
                'key': self.google_api_key
            }
            
            response = requests.get(base_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and data['results']:
                    place = data['results'][0]
                    return {
                        'source': 'Google Maps',
                        'place_id': place.get('place_id', ''),
                        'name': place.get('name', ''),
                        'address': place.get('vicinity', ''),
                        'types': place.get('types', [])
                    }
        except Exception as e:
            self.logger.warning(f"Google Maps query failed: {e}")
        
        return None
    
    def estimate_parcel_size_by_location(self, city, address=None):
        """Estimate typical parcel sizes by city/area type"""
        
        # Typical parcel sizes in Texas suburban/rural areas
        size_estimates = {
            'FRISCO': {'min': 0.15, 'typical': 0.25, 'max': 2.0, 'type': 'Suburban'},
            'PROSPER': {'min': 0.25, 'typical': 0.5, 'max': 5.0, 'type': 'Suburban-Rural'},
            'CELINA': {'min': 0.5, 'typical': 1.0, 'max': 10.0, 'type': 'Rural-Suburban'},
            'ANNA': {'min': 0.5, 'typical': 2.0, 'max': 20.0, 'type': 'Rural'},
            'MELISSA': {'min': 0.25, 'typical': 1.0, 'max': 5.0, 'type': 'Suburban-Rural'},
            'AUBREY': {'min': 1.0, 'typical': 5.0, 'max': 50.0, 'type': 'Rural'},
            'HOUSTON': {'min': 0.1, 'typical': 0.15, 'max': 0.5, 'type': 'Urban'},
            'ALLEN': {'min': 0.15, 'typical': 0.25, 'max': 1.0, 'type': 'Suburban'},
            'WESTMINSTER': {'min': 0.25, 'typical': 1.0, 'max': 5.0, 'type': 'Suburban'}
        }
        
        city_upper = city.upper() if city else 'UNKNOWN'
        return size_estimates.get(city_upper, {'min': 0.5, 'typical': 2.0, 'max': 20.0, 'type': 'Unknown'})
    
    def analyze_all_parcels(self):
        """Analyze parcel sizes for all Region 3 sites"""
        
        # Load sites
        df = self.load_region3_sites()
        if df is None:
            return None
        
        self.logger.info(f"Analyzing parcel sizes for {len(df)} Region 3 sites")
        
        # Initialize parcel data columns
        parcel_cols = [
            'Parcel_Source', 'Parcel_ID', 'Acreage_Actual', 'Acreage_Estimated_Min',
            'Acreage_Estimated_Typical', 'Acreage_Estimated_Max', 'Property_Owner',
            'Legal_Description', 'Parcel_Query_Status'
        ]
        
        for col in parcel_cols:
            df[col] = None
        
        # Process each site
        for idx, row in df.iterrows():
            site_name = row.get('Property_Name', f'Site_{idx+1}')
            lat = row.get('Latitude')
            lng = row.get('Longitude') 
            city = row.get('City', '')
            county = row.get('County', '').upper()
            address = row.get('Address', '')
            
            self.logger.info(f"Processing {site_name} in {city}, {county} County")
            
            parcel_data = None
            
            # Try county assessor APIs based on county
            if lat and lng:
                if county == 'COLLIN':
                    parcel_data = self.query_collin_county_parcels(lat, lng, address)
                elif county == 'DENTON':
                    parcel_data = self.query_denton_county_parcels(lat, lng, address)
                elif county == 'HARRIS':
                    parcel_data = self.query_harris_county_parcels(lat, lng, address)
                
                time.sleep(0.5)  # Rate limiting
            
            # Get size estimates based on location
            size_estimate = self.estimate_parcel_size_by_location(city, address)
            
            # Update dataframe
            if parcel_data:
                df.at[idx, 'Parcel_Source'] = parcel_data['source']
                df.at[idx, 'Parcel_ID'] = parcel_data.get('parcel_id', '')
                df.at[idx, 'Acreage_Actual'] = parcel_data.get('acreage')
                df.at[idx, 'Property_Owner'] = parcel_data.get('owner', '')
                df.at[idx, 'Legal_Description'] = parcel_data.get('legal_desc', '')
                df.at[idx, 'Parcel_Query_Status'] = 'Found'
            else:
                df.at[idx, 'Parcel_Query_Status'] = 'Not Found - Manual Lookup Required'
            
            # Always add estimates
            df.at[idx, 'Acreage_Estimated_Min'] = size_estimate['min']
            df.at[idx, 'Acreage_Estimated_Typical'] = size_estimate['typical']
            df.at[idx, 'Acreage_Estimated_Max'] = size_estimate['max']
            df.at[idx, 'Property_Type_Estimate'] = size_estimate['type']
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"DMarco_Region3_Parcel_Analysis_{timestamp}.xlsx"
        
        code_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code")
        
        with pd.ExcelWriter(code_path / output_file, engine='openpyxl') as writer:
            # All sites with parcel data
            df.to_excel(writer, sheet_name='All_Sites_With_Parcels', index=False)
            
            # Summary by city
            city_summary = df.groupby('City').agg({
                'Property_Name': 'count',
                'Acreage_Actual': ['count', 'mean'],
                'Acreage_Estimated_Typical': 'mean',
                'Parcel_Query_Status': lambda x: (x == 'Found').sum()
            }).round(2)
            city_summary.columns = ['Total_Sites', 'Actual_Acreage_Count', 'Avg_Actual_Acreage', 
                                   'Avg_Estimated_Acreage', 'Successful_Queries']
            city_summary.to_excel(writer, sheet_name='Summary_By_City')
            
            # Sites needing manual lookup
            manual_lookup = df[df['Parcel_Query_Status'] != 'Found'][
                ['Property_Name', 'Address', 'City', 'County', 'Latitude', 'Longitude',
                 'Acreage_Estimated_Min', 'Acreage_Estimated_Typical', 'Acreage_Estimated_Max']
            ]
            manual_lookup.to_excel(writer, sheet_name='Manual_Lookup_Required', index=False)
            
            # Parcel size analysis
            size_analysis = pd.DataFrame([
                {'City': city, 'Property_Type': df[df['City'] == city]['Property_Type_Estimate'].iloc[0] if len(df[df['City'] == city]) > 0 else '',
                 'Estimated_Range': f"{df[df['City'] == city]['Acreage_Estimated_Min'].iloc[0]:.1f} - {df[df['City'] == city]['Acreage_Estimated_Max'].iloc[0]:.1f} acres" if len(df[df['City'] == city]) > 0 else '',
                 'Typical_Size': f"{df[df['City'] == city]['Acreage_Estimated_Typical'].iloc[0]:.1f} acres" if len(df[df['City'] == city]) > 0 else ''}
                for city in df['City'].unique() if pd.notna(city)
            ])
            size_analysis.to_excel(writer, sheet_name='Size_Analysis_By_City', index=False)
        
        self.logger.info(f"Parcel analysis saved to: {output_file}")
        
        return df, output_file
    
    def print_summary(self, df):
        """Print summary of parcel analysis"""
        
        print(f"\n=== D'Marco Region 3 Parcel Size Analysis ===")
        print(f"Total Sites: {len(df)}")
        
        # Success rate
        found_count = (df['Parcel_Query_Status'] == 'Found').sum()
        print(f"Actual Parcel Data Found: {found_count}/{len(df)} ({found_count/len(df)*100:.1f}%)")
        
        # By city
        print(f"\nParcel Size Estimates by City:")
        for city in df['City'].unique():
            if pd.notna(city):
                city_data = df[df['City'] == city]
                typical_size = city_data['Acreage_Estimated_Typical'].iloc[0]
                prop_type = city_data['Property_Type_Estimate'].iloc[0]
                actual_count = city_data['Acreage_Actual'].notna().sum()
                print(f"  {city}: {typical_size:.1f} acres typical ({prop_type}) - {len(city_data)} sites, {actual_count} actual")
        
        # Manual lookup needed
        manual_needed = df[df['Parcel_Query_Status'] != 'Found']
        if len(manual_needed) > 0:
            print(f"\nSites Requiring Manual Lookup: {len(manual_needed)}")
            for _, site in manual_needed.iterrows():
                print(f"  {site['Property_Name']} ({site['City']}) - Est: {site['Acreage_Estimated_Typical']:.1f} acres")


def main():
    """Main execution"""
    analyzer = Region3ParcelAnalyzer()
    
    # Run the analysis
    df, output_file = analyzer.analyze_all_parcels()
    
    if df is not None:
        analyzer.print_summary(df)
        print(f"\nResults saved to: {output_file}")
        
        print(f"\nNext Steps for Manual Lookup:")
        print(f"1. Use county assessor websites for remaining sites")
        print(f"2. Check Google Earth for property boundaries")
        print(f"3. Contact local real estate agents for detailed parcel info")
    else:
        print("Analysis failed!")


if __name__ == "__main__":
    main()