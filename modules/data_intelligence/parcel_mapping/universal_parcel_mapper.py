#!/usr/bin/env python3

"""
Universal LAT/LONG to APN Conversion System
Supporting Texas and California parcel boundary analysis

Built for testing with D'Marco sites and California LIHTC analysis
Dual-track approach for maximum compatibility and coverage
"""

import requests
import json
import time
import logging
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import geopandas as gpd
from geopy.distance import geodesic
from datetime import datetime
import pyproj

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ParcelData:
    """Standardized parcel data structure for all states"""
    apn: str
    state: str
    county: str
    boundary_coordinates: List[Tuple[float, float]]
    property_area_acres: float
    owner_name: Optional[str] = None
    owner_address: Optional[str] = None
    zoning_code: Optional[str] = None
    land_use_code: Optional[str] = None
    assessed_value: Optional[float] = None
    market_value: Optional[float] = None
    tax_year: Optional[int] = None
    centroid_lat: Optional[float] = None
    centroid_lng: Optional[float] = None
    data_source: Optional[str] = None
    acquisition_date: Optional[str] = None

class BaseParcelAPI(ABC):
    """Abstract base class for state-specific parcel APIs"""
    
    def __init__(self, state_code: str):
        self.state_code = state_code
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Colosseum-LIHTC-Analysis/1.0 (Structured Consultants LLC)'
        })
    
    @abstractmethod
    def lookup_parcel_from_coordinates(self, lat: float, lng: float) -> Optional[ParcelData]:
        """Convert LAT/LONG to parcel data with boundary coordinates"""
        pass
    
    @abstractmethod
    def get_parcel_boundaries(self, apn: str) -> List[Tuple[float, float]]:
        """Get boundary coordinates for a specific APN"""
        pass

class TexasParcelAPI(BaseParcelAPI):
    """Texas-specific parcel lookup using multiple county APIs and Regrid"""
    
    def __init__(self):
        super().__init__('TX')
        self.county_apis = {
            'Harris': 'https://www.gis.hctx.net/arcgis/rest/services/HCAD/Parcels/MapServer/0',
            'Dallas': 'https://gis.dallascounty.org/server/rest/services/Parcels/MapServer/0',
            'Travis': 'https://taxmaps.traviscountytx.gov/arcgis/rest/services/Parcels/MapServer/0',
            'Bexar': 'https://maps.bexar.org/arcgis/rest/services/Parcels/MapServer/0',
            'Tarrant': 'https://gisweb.tarrantcounty.com/arcgis/rest/services/Parcels/MapServer/0'
        }
        self.regrid_api_key = None  # Will be set from config
        
    def lookup_parcel_from_coordinates(self, lat: float, lng: float) -> Optional[ParcelData]:
        """
        Texas LAT/LONG to APN conversion
        Priority: 1) Regrid API, 2) County-specific APIs
        """
        logger.info(f"Looking up Texas parcel for coordinates: {lat}, {lng}")
        
        # Try Regrid first (if API key available)
        if self.regrid_api_key:
            parcel_data = self._regrid_lookup(lat, lng)
            if parcel_data:
                return parcel_data
        
        # Try county-specific APIs
        county = self._determine_county_from_coordinates(lat, lng)
        if county and county in self.county_apis:
            return self._county_api_lookup(lat, lng, county)
        
        # Try all county APIs as fallback
        for county_name, api_url in self.county_apis.items():
            parcel_data = self._county_api_lookup(lat, lng, county_name)
            if parcel_data:
                return parcel_data
                
        logger.warning(f"No Texas parcel found for coordinates: {lat}, {lng}")
        return None
    
    def _regrid_lookup(self, lat: float, lng: float) -> Optional[ParcelData]:
        """Use Regrid API for Texas parcel lookup"""
        try:
            url = "https://app.regrid.com/api/v1/search.json"
            params = {
                'token': self.regrid_api_key,
                'latitude': lat,
                'longitude': lng,
                'limit': 1
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('results') and len(data['results']) > 0:
                parcel = data['results'][0]
                
                # Extract boundary coordinates from geometry
                boundary_coords = []
                if parcel.get('geometry') and parcel['geometry'].get('coordinates'):
                    coords = parcel['geometry']['coordinates'][0]  # Assuming polygon
                    boundary_coords = [(coord[1], coord[0]) for coord in coords]  # Convert to (lat, lng)
                
                return ParcelData(
                    apn=parcel.get('fields', {}).get('parcelnumb', 'Unknown'),
                    state='TX',
                    county=parcel.get('fields', {}).get('county', 'Unknown'),
                    boundary_coordinates=boundary_coords,
                    property_area_acres=parcel.get('fields', {}).get('shapearea', 0) / 43560,  # Convert sq ft to acres
                    owner_name=parcel.get('fields', {}).get('ownername'),
                    zoning_code=parcel.get('fields', {}).get('zoning'),
                    assessed_value=parcel.get('fields', {}).get('assessval'),
                    centroid_lat=lat,
                    centroid_lng=lng,
                    data_source='Regrid API',
                    acquisition_date=datetime.now().strftime('%Y-%m-%d')
                )
                
        except Exception as e:
            logger.error(f"Regrid API error: {str(e)}")
            
        return None
    
    def _county_api_lookup(self, lat: float, lng: float, county: str) -> Optional[ParcelData]:
        """Use county-specific ArcGIS REST API for parcel lookup"""
        try:
            api_url = self.county_apis.get(county)
            if not api_url:
                return None
                
            # ArcGIS spatial query
            query_url = f"{api_url}/query"
            params = {
                'f': 'json',
                'geometry': f"{lng},{lat}",
                'geometryType': 'esriGeometryPoint',
                'inSR': '4326',  # WGS84
                'spatialRel': 'esriSpatialRelIntersects',
                'outFields': '*',
                'returnGeometry': 'true',
                'outSR': '4326'
            }
            
            response = self.session.get(query_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if data.get('features') and len(data['features']) > 0:
                feature = data['features'][0]
                attributes = feature.get('attributes', {})
                geometry = feature.get('geometry', {})
                
                # Extract boundary coordinates
                boundary_coords = []
                if geometry.get('rings'):
                    coords = geometry['rings'][0]  # Exterior ring
                    boundary_coords = [(coord[1], coord[0]) for coord in coords]  # Convert to (lat, lng)
                
                # Get APN field (varies by county)
                apn_fields = ['APN', 'PARCEL_ID', 'PIN', 'ACCOUNT', 'PARCEL_NUM']
                apn = 'Unknown'
                for field in apn_fields:
                    if field in attributes and attributes[field]:
                        apn = str(attributes[field])
                        break
                
                return ParcelData(
                    apn=apn,
                    state='TX',
                    county=county,
                    boundary_coordinates=boundary_coords,
                    property_area_acres=self._calculate_area_from_coords(boundary_coords),
                    owner_name=attributes.get('OWNER_NAME') or attributes.get('OWNER'),
                    centroid_lat=lat,
                    centroid_lng=lng,
                    data_source=f'{county} County API',
                    acquisition_date=datetime.now().strftime('%Y-%m-%d')
                )
                
        except Exception as e:
            logger.error(f"County API error for {county}: {str(e)}")
            
        return None
    
    def _determine_county_from_coordinates(self, lat: float, lng: float) -> Optional[str]:
        """Determine Texas county from coordinates using simple bounds checking"""
        # Major Texas county approximate bounds
        county_bounds = {
            'Harris': {'lat_min': 29.4, 'lat_max': 30.1, 'lng_min': -95.8, 'lng_max': -95.0},
            'Dallas': {'lat_min': 32.6, 'lat_max': 33.0, 'lng_min': -97.1, 'lng_max': -96.4},
            'Travis': {'lat_min': 30.0, 'lat_max': 30.6, 'lng_min': -98.0, 'lng_max': -97.5},
            'Bexar': {'lat_min': 29.1, 'lat_max': 29.8, 'lng_min': -98.9, 'lng_max': -98.2},
            'Tarrant': {'lat_min': 32.5, 'lat_max': 33.0, 'lng_min': -97.6, 'lng_max': -96.9}
        }
        
        for county, bounds in county_bounds.items():
            if (bounds['lat_min'] <= lat <= bounds['lat_max'] and 
                bounds['lng_min'] <= lng <= bounds['lng_max']):
                return county
        
        return None
    
    def get_parcel_boundaries(self, apn: str) -> List[Tuple[float, float]]:
        """Get boundary coordinates for specific Texas APN"""
        # Implementation would query by APN across county APIs
        # For now, return empty list
        return []
    
    def _calculate_area_from_coords(self, boundary_coords: List[Tuple[float, float]]) -> float:
        """Calculate area in acres from boundary coordinates"""
        if len(boundary_coords) < 3:
            return 0.0
        
        try:
            # Simple polygon area calculation (not geodesically correct, but approximate)
            # For production, would use proper geodesic calculations
            import math
            
            area_sq_meters = 0.0
            n = len(boundary_coords)
            
            for i in range(n):
                j = (i + 1) % n
                lat1, lng1 = boundary_coords[i]
                lat2, lng2 = boundary_coords[j]
                
                # Convert to meters (approximate)
                x1 = lng1 * 111320 * math.cos(math.radians(lat1))
                y1 = lat1 * 110540
                x2 = lng2 * 111320 * math.cos(math.radians(lat2))
                y2 = lat2 * 110540
                
                area_sq_meters += (x1 * y2 - x2 * y1)
            
            area_sq_meters = abs(area_sq_meters) / 2.0
            return area_sq_meters / 4047  # Convert to acres
            
        except Exception as e:
            logger.error(f"Area calculation error: {str(e)}")
            return 0.0

class CaliforniaParcelAPI(BaseParcelAPI):
    """California-specific parcel lookup using county APIs and ParcelQuest"""
    
    def __init__(self):
        super().__init__('CA')
        self.county_apis = {
            'Los Angeles': 'https://dpw.gis.lacounty.gov/dpw/rest/services/parcels/MapServer/0',
            'Orange': 'https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/Parcels/FeatureServer/0',
            'San Diego': 'https://webgis.sangis.org/server/rest/services/Assessor/Parcels/MapServer/0',
            'Riverside': 'https://gis.rivcoit.org/arcgis/rest/services/Parcels/MapServer/0',
            'San Bernardino': 'https://gis.sbcounty.gov/arcgis/rest/services/Parcels/MapServer/0'
        }
        self.parcelquest_api_key = None  # Will be set from config
    
    def lookup_parcel_from_coordinates(self, lat: float, lng: float) -> Optional[ParcelData]:
        """
        California LAT/LONG to APN conversion
        Priority: 1) ParcelQuest API, 2) County-specific APIs
        """
        logger.info(f"Looking up California parcel for coordinates: {lat}, {lng}")
        
        # Try ParcelQuest first (if API key available)
        if self.parcelquest_api_key:
            parcel_data = self._parcelquest_lookup(lat, lng)
            if parcel_data:
                return parcel_data
        
        # Try county-specific APIs
        county = self._determine_county_from_coordinates(lat, lng)
        if county and county in self.county_apis:
            return self._county_api_lookup(lat, lng, county)
        
        # Try all county APIs as fallback
        for county_name, api_url in self.county_apis.items():
            parcel_data = self._county_api_lookup(lat, lng, county_name)
            if parcel_data:
                return parcel_data
                
        logger.warning(f"No California parcel found for coordinates: {lat}, {lng}")
        return None
    
    def _parcelquest_lookup(self, lat: float, lng: float) -> Optional[ParcelData]:
        """Use ParcelQuest API for California parcel lookup"""
        # ParcelQuest implementation would go here
        # For now, return None to fall back to county APIs
        return None
    
    def _county_api_lookup(self, lat: float, lng: float, county: str) -> Optional[ParcelData]:
        """Use county-specific ArcGIS REST API for California parcel lookup"""
        try:
            api_url = self.county_apis.get(county)
            if not api_url:
                return None
                
            # ArcGIS spatial query (similar to Texas implementation)
            query_url = f"{api_url}/query"
            params = {
                'f': 'json',
                'geometry': f"{lng},{lat}",
                'geometryType': 'esriGeometryPoint',
                'inSR': '4326',  # WGS84
                'spatialRel': 'esriSpatialRelIntersects',
                'outFields': '*',
                'returnGeometry': 'true',
                'outSR': '4326'
            }
            
            response = self.session.get(query_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if data.get('features') and len(data['features']) > 0:
                feature = data['features'][0]
                attributes = feature.get('attributes', {})
                geometry = feature.get('geometry', {})
                
                # Extract boundary coordinates
                boundary_coords = []
                if geometry.get('rings'):
                    coords = geometry['rings'][0]  # Exterior ring
                    boundary_coords = [(coord[1], coord[0]) for coord in coords]  # Convert to (lat, lng)
                
                # Get APN field (varies by county)
                apn_fields = ['APN', 'PARCEL_ID', 'PIN', 'ASSESSOR_PARCEL_NUMBER']
                apn = 'Unknown'
                for field in apn_fields:
                    if field in attributes and attributes[field]:
                        apn = str(attributes[field])
                        break
                
                return ParcelData(
                    apn=apn,
                    state='CA',
                    county=county,
                    boundary_coordinates=boundary_coords,
                    property_area_acres=self._calculate_area_from_coords(boundary_coords),
                    owner_name=attributes.get('OWNER_NAME') or attributes.get('OWNER'),
                    zoning_code=attributes.get('ZONING'),
                    land_use_code=attributes.get('LAND_USE'),
                    assessed_value=attributes.get('ASSESSED_VALUE'),
                    centroid_lat=lat,
                    centroid_lng=lng,
                    data_source=f'{county} County API',
                    acquisition_date=datetime.now().strftime('%Y-%m-%d')
                )
                
        except Exception as e:
            logger.error(f"California county API error for {county}: {str(e)}")
            
        return None
    
    def _determine_county_from_coordinates(self, lat: float, lng: float) -> Optional[str]:
        """Determine California county from coordinates using simple bounds checking"""
        # Major California county approximate bounds
        county_bounds = {
            'Los Angeles': {'lat_min': 33.7, 'lat_max': 34.8, 'lng_min': -118.9, 'lng_max': -117.6},
            'Orange': {'lat_min': 33.4, 'lat_max': 33.9, 'lng_min': -118.1, 'lng_max': -117.4},
            'San Diego': {'lat_min': 32.5, 'lat_max': 33.5, 'lng_min': -117.6, 'lng_max': -116.1},
            'Riverside': {'lat_min': 33.4, 'lat_max': 34.1, 'lng_min': -117.7, 'lng_max': -114.4},
            'San Bernardino': {'lat_min': 34.0, 'lat_max': 35.8, 'lng_min': -118.0, 'lng_max': -114.1}
        }
        
        for county, bounds in county_bounds.items():
            if (bounds['lat_min'] <= lat <= bounds['lat_max'] and 
                bounds['lng_min'] <= lng <= bounds['lng_max']):
                return county
        
        return None
    
    def get_parcel_boundaries(self, apn: str) -> List[Tuple[float, float]]:
        """Get boundary coordinates for specific California APN"""
        # Implementation would query by APN across county APIs
        return []
    
    def _calculate_area_from_coords(self, boundary_coords: List[Tuple[float, float]]) -> float:
        """Calculate area in acres from boundary coordinates (same as Texas implementation)"""
        if len(boundary_coords) < 3:
            return 0.0
        
        try:
            import math
            
            area_sq_meters = 0.0
            n = len(boundary_coords)
            
            for i in range(n):
                j = (i + 1) % n
                lat1, lng1 = boundary_coords[i]
                lat2, lng2 = boundary_coords[j]
                
                # Convert to meters (approximate)
                x1 = lng1 * 111320 * math.cos(math.radians(lat1))
                y1 = lat1 * 110540
                x2 = lng2 * 111320 * math.cos(math.radians(lat2))
                y2 = lat2 * 110540
                
                area_sq_meters += (x1 * y2 - x2 * y1)
            
            area_sq_meters = abs(area_sq_meters) / 2.0
            return area_sq_meters / 4047  # Convert to acres
            
        except Exception as e:
            logger.error(f"Area calculation error: {str(e)}")
            return 0.0

class UniversalParcelMapper:
    """
    Universal LAT/LONG to APN conversion system
    Supporting Texas and California with extensible architecture
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.apis = {
            'TX': TexasParcelAPI(),
            'CA': CaliforniaParcelAPI()
        }
        
        # Load configuration if provided
        if config_file:
            self._load_config(config_file)
    
    def get_parcel_from_coordinates(self, lat: float, lng: float, state: str) -> Optional[ParcelData]:
        """
        Universal LAT/LONG to APN conversion
        
        Args:
            lat: Latitude in decimal degrees
            lng: Longitude in decimal degrees  
            state: State code ('TX', 'CA', etc.)
            
        Returns:
            ParcelData object or None if not found
        """
        if state not in self.apis:
            logger.error(f"State '{state}' not supported. Available: {list(self.apis.keys())}")
            return None
        
        api = self.apis[state]
        return api.lookup_parcel_from_coordinates(lat, lng)
    
    def analyze_multiple_sites(self, coordinates_list: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Analyze multiple sites for parcel data
        
        Args:
            coordinates_list: List of dicts with 'lat', 'lng', 'state', and optional 'site_id'
            
        Returns:
            DataFrame with parcel analysis results
        """
        results = []
        
        for i, coord_data in enumerate(coordinates_list):
            lat = coord_data['lat']
            lng = coord_data['lng']
            state = coord_data['state']
            site_id = coord_data.get('site_id', f'Site_{i+1}')
            
            logger.info(f"Processing {site_id}: {lat}, {lng} ({state})")
            
            parcel_data = self.get_parcel_from_coordinates(lat, lng, state)
            
            if parcel_data:
                result = {
                    'site_id': site_id,
                    'input_lat': lat,
                    'input_lng': lng,
                    'state': state,
                    'apn': parcel_data.apn,
                    'county': parcel_data.county,
                    'property_area_acres': parcel_data.property_area_acres,
                    'owner_name': parcel_data.owner_name,
                    'zoning_code': parcel_data.zoning_code,
                    'assessed_value': parcel_data.assessed_value,
                    'boundary_points_count': len(parcel_data.boundary_coordinates),
                    'data_source': parcel_data.data_source,
                    'acquisition_date': parcel_data.acquisition_date,
                    'status': 'SUCCESS'
                }
            else:
                result = {
                    'site_id': site_id,
                    'input_lat': lat,
                    'input_lng': lng,
                    'state': state,
                    'apn': None,
                    'county': None,
                    'property_area_acres': None,
                    'owner_name': None,
                    'zoning_code': None,
                    'assessed_value': None,
                    'boundary_points_count': 0,
                    'data_source': None,
                    'acquisition_date': datetime.now().strftime('%Y-%m-%d'),
                    'status': 'NOT_FOUND'
                }
            
            results.append(result)
            
            # Rate limiting
            time.sleep(1)
        
        return pd.DataFrame(results)
    
    def export_parcel_boundaries_kml(self, parcel_data: ParcelData, output_file: str):
        """Export parcel boundaries to KML for Google Earth visualization"""
        if not parcel_data.boundary_coordinates:
            logger.warning("No boundary coordinates available for KML export")
            return
        
        kml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Parcel Analysis: {parcel_data.apn}</name>
    <description>Generated by Colosseum Universal Parcel Mapper</description>
    
    <Style id="parcelBoundary">
      <LineStyle>
        <color>ff0000ff</color>
        <width>3</width>
      </LineStyle>
      <PolyStyle>
        <color>330000ff</color>
        <fill>1</fill>
        <outline>1</outline>
      </PolyStyle>
    </Style>
    
    <Placemark>
      <name>APN: {parcel_data.apn}</name>
      <description><![CDATA[
        <b>Assessor Parcel Number:</b> {parcel_data.apn}<br/>
        <b>State:</b> {parcel_data.state}<br/>
        <b>County:</b> {parcel_data.county}<br/>
        <b>Area:</b> {parcel_data.property_area_acres:.2f} acres<br/>
        <b>Owner:</b> {parcel_data.owner_name or 'Unknown'}<br/>
        <b>Zoning:</b> {parcel_data.zoning_code or 'Unknown'}<br/>
        <b>Assessed Value:</b> ${parcel_data.assessed_value:,.2f if parcel_data.assessed_value else 'Unknown'}<br/>
        <b>Data Source:</b> {parcel_data.data_source}<br/>
        <b>Analysis Date:</b> {parcel_data.acquisition_date}
      ]]></description>
      <styleUrl>#parcelBoundary</styleUrl>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
'''
        
        for lat, lng in parcel_data.boundary_coordinates:
            kml_content += f"              {lng},{lat},0\n"
        
        kml_content += '''            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>'''
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(kml_content)
        
        logger.info(f"KML exported to: {output_file}")
    
    def _load_config(self, config_file: str):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Set API keys if available
            if 'regrid_api_key' in config:
                self.apis['TX'].regrid_api_key = config['regrid_api_key']
            
            if 'parcelquest_api_key' in config:
                self.apis['CA'].parcelquest_api_key = config['parcelquest_api_key']
                
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")

# Test function for D'Marco sites
def test_with_dmarco_coordinates():
    """Test the system with sample D'Marco Texas coordinates"""
    
    # Sample D'Marco coordinates (you would replace with actual data)
    test_coordinates = [
        {'lat': 32.7767, 'lng': -96.7970, 'state': 'TX', 'site_id': 'DMarco_Dallas_Test'},
        {'lat': 29.7604, 'lng': -95.3698, 'state': 'TX', 'site_id': 'DMarco_Houston_Test'},
        {'lat': 30.2672, 'lng': -97.7431, 'state': 'TX', 'site_id': 'DMarco_Austin_Test'}
    ]
    
    mapper = UniversalParcelMapper()
    results_df = mapper.analyze_multiple_sites(test_coordinates)
    
    print("=== D'Marco Sites Parcel Analysis Results ===")
    print(results_df.to_string(index=False))
    
    # Export results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping/dmarco_parcel_analysis_{timestamp}.xlsx'
    results_df.to_excel(output_file, index=False)
    
    print(f"\nResults exported to: {output_file}")
    
    return results_df

if __name__ == "__main__":
    # Run test with D'Marco coordinates
    test_results = test_with_dmarco_coordinates()