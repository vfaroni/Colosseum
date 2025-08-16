#!/usr/bin/env python3
"""
CTCAC San Jacinto Custom Mapper
Uses custom parks and pharmacy data for San Jacinto Vista II site
"""

import pandas as pd
from pathlib import Path
from ctcac_parcel_boundary_mapper import CTCACParcelBoundaryMapper

class CTCACSanJacintoCustomMapper(CTCACParcelBoundaryMapper):
    """Custom mapper with San Jacinto-specific parks and pharmacy data"""
    
    def __init__(self, data_path=None):
        """Initialize with custom data paths"""
        super().__init__(data_path)
        self.custom_data_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code")
        
    def load_parks_data(self):
        """Load custom San Jacinto parks data"""
        parks_file = self.custom_data_path / "san_jacinto_parks.csv"
        
        if not parks_file.exists():
            print(f"Custom parks file not found: {parks_file}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(parks_file)
            
            # Standardize for CTCAC format
            parks = pd.DataFrame()
            parks['name'] = df['name']
            parks['amenity_type'] = 'park_community_center'  # CTCAC standard type
            parks['amenity_category'] = 'public_park'
            parks['latitude'] = df['latitude']
            parks['longitude'] = df['longitude']
            parks['address'] = df['address']
            
            print(f"Loaded {len(parks)} custom San Jacinto parks")
            return parks.dropna()
            
        except Exception as e:
            print(f"Error loading custom parks: {e}")
            return pd.DataFrame()
    
    def load_pharmacies_data(self):
        """Load custom San Jacinto pharmacy data"""
        pharmacies_file = self.custom_data_path / "san_jacinto_pharmacies.csv"
        
        if not pharmacies_file.exists():
            print(f"Custom pharmacies file not found: {pharmacies_file}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(pharmacies_file)
            
            # Standardize for CTCAC format
            pharmacies = pd.DataFrame()
            pharmacies['name'] = df['name']
            pharmacies['amenity_type'] = 'pharmacy'
            pharmacies['amenity_category'] = 'pharmacy'
            pharmacies['latitude'] = df['latitude']
            pharmacies['longitude'] = df['longitude']
            pharmacies['address'] = df['address']
            
            print(f"Loaded {len(pharmacies)} custom San Jacinto pharmacies")
            return pharmacies.dropna()
            
        except Exception as e:
            print(f"Error loading custom pharmacies: {e}")
            return pd.DataFrame()
    


def analyze_san_jacinto_with_custom_data(parcel_corners, address, **kwargs):
    """
    Analyze San Jacinto Vista II site with custom parks and pharmacy data
    
    Args:
        parcel_corners: Dict with 'nw', 'ne', 'sw', 'se' corners as (lat, lng) tuples
        address: Address string for the site
        **kwargs: Additional arguments for the analysis
    
    Returns:
        Tuple of (map_object, results_dict)
    """
    mapper = CTCACSanJacintoCustomMapper()
    
    return mapper.create_parcel_enhanced_map(
        parcel_corners=parcel_corners,
        project_address=address,
        **kwargs
    )