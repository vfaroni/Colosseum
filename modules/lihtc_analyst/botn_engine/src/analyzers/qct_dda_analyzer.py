#!/usr/bin/env python3
"""
QCT/DDA Analyzer - Federal Qualification Analysis for LIHTC Sites

Analyzes QCT (Qualified Census Tract) and DDA (Difficult Development Area) 
status using HUD shapefiles to determine federal basis boost eligibility.

Based on proven patterns from CTCAC RAG system.
"""

import logging
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class QCTDDAResult:
    """Result of QCT/DDA analysis"""
    qct_qualified: bool = False
    dda_qualified: bool = False
    federal_basis_boost: bool = False
    qct_name: Optional[str] = None
    dda_name: Optional[str] = None
    qct_tract_id: Optional[str] = None
    dda_details: Optional[Dict[str, Any]] = None
    basis_boost_percentage: float = 0.0


class QCTDDAAnalyzer:
    """
    Analyzes federal QCT/DDA qualification for LIHTC sites
    
    Uses HUD shapefiles to determine if coordinates qualify for:
    - QCT (Qualified Census Tract): 30% basis boost
    - DDA (Difficult Development Area): 30% basis boost
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the QCT/DDA analyzer
        
        Args:
            config: Configuration dictionary with data paths
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Data path from Claude.md instruction
        self.data_path = Path("/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets")
        
        # HUD QCT/DDA data paths - using the correct file with actual data
        self.hud_data_path = self.data_path / "federal" / "HUD_QCT_DDA_Data"
        self.qct_file = self.hud_data_path / "HUD QCT DDA 2025 Merged.gpkg"
        self.dda_file = self.hud_data_path / "HUD QCT DDA 2025 Merged.gpkg"
        
        # Load shapefiles
        self.qct_data = None
        self.dda_data = None
        self._load_hud_designation_data()
    
    def analyze(self, site_info) -> Dict[str, Any]:
        """
        Perform QCT/DDA analysis for a site
        
        Args:
            site_info: SiteInfo object with coordinates
            
        Returns:
            Dictionary with QCT/DDA analysis results
        """
        try:
            result = self._check_qct_dda_status(
                site_info.latitude, 
                site_info.longitude
            )
            
            # Convert to the expected format for the main analyzer
            return {
                'qct_qualified': result.qct_qualified,
                'dda_qualified': result.dda_qualified,
                'federal_basis_boost': result.federal_basis_boost,
                'basis_boost_percentage': result.basis_boost_percentage,
                'qct_details': {
                    'name': result.qct_name,
                    'tract_id': result.qct_tract_id
                } if result.qct_qualified else None,
                'dda_details': result.dda_details if result.dda_qualified else None,
                'analysis_notes': self._generate_analysis_notes(result)
            }
            
        except Exception as e:
            self.logger.error(f"QCT/DDA analysis failed: {str(e)}")
            return {
                'qct_qualified': False,
                'dda_qualified': False,
                'federal_basis_boost': False,
                'basis_boost_percentage': 0.0,
                'error': str(e)
            }
    
    def _load_hud_designation_data(self):
        """Load QCT/DDA shapefiles from HUD data"""
        try:
            # Check if data files exist
            if not self.hud_data_path.exists():
                self.logger.warning(f"HUD data path not found: {self.hud_data_path}")
                return
            
            # Load combined QCT/DDA data and filter appropriately
            if self.qct_file.exists():
                self.logger.info(f"Loading HUD QCT/DDA data from: {self.qct_file}")
                full_data = gpd.read_file(self.qct_file)
                
                # Ensure proper CRS
                if full_data.crs != 'EPSG:4326':
                    full_data = full_data.to_crs('EPSG:4326')
                
                # Filter QCT data (records where DDA_CODE is null/empty or layer indicates QCT)
                qct_filter = (
                    (full_data['DDA_CODE'].isna()) | 
                    (full_data['DDA_CODE'] == '') |
                    (full_data['layer'].str.contains('QCT', na=False))
                )
                self.qct_data = full_data[qct_filter].copy()
                
                # Filter DDA data (records where DDA_CODE is not null/empty)
                dda_filter = (
                    (full_data['DDA_CODE'].notna()) & 
                    (full_data['DDA_CODE'] != '') &
                    (~full_data['DDA_CODE'].isin(['', None]))
                )
                self.dda_data = full_data[dda_filter].copy()
                
                self.logger.info(f"Loaded QCT data: {len(self.qct_data)} features")
                self.logger.info(f"Loaded DDA data: {len(self.dda_data)} features")
                
                # Additional info for California
                if len(self.qct_data) > 0:
                    ca_qct = self.qct_data[self.qct_data['STATE'] == 'CA'] if 'STATE' in self.qct_data.columns else self.qct_data
                    la_qct = ca_qct[ca_qct['COUNTY'].str.contains('Los Angeles', na=False)] if 'COUNTY' in ca_qct.columns else ca_qct
                    self.logger.info(f"California QCT features: {len(ca_qct)}")
                    self.logger.info(f"Los Angeles County QCT features: {len(la_qct)}")
                
            else:
                self.logger.warning(f"HUD data file not found: {self.qct_file}")
                
        except Exception as e:
            self.logger.error(f"Error loading HUD designation data: {e}")
    
    def _check_qct_dda_status(self, latitude: float, longitude: float) -> QCTDDAResult:
        """
        Check if coordinates are in QCT or DDA
        
        Args:
            latitude: Site latitude
            longitude: Site longitude
            
        Returns:
            QCTDDAResult with qualification status
        """
        result = QCTDDAResult()
        
        try:
            point = Point(longitude, latitude)
            
            # Check QCT status
            if self.qct_data is not None:
                qct_intersects = self.qct_data[self.qct_data.contains(point)]
                if not qct_intersects.empty:
                    result.qct_qualified = True
                    result.federal_basis_boost = True
                    result.basis_boost_percentage = 30.0
                    
                    qct_row = qct_intersects.iloc[0]
                    
                    # Extract QCT information with multiple possible column names
                    result.qct_name = (
                        qct_row.get('NAME') or 
                        qct_row.get('QCT_NAME') or 
                        qct_row.get('NAMELSAD') or 
                        'QCT Area'
                    )
                    result.qct_tract_id = (
                        qct_row.get('GEOID') or 
                        qct_row.get('TRACTCE') or 
                        qct_row.get('FIPS')
                    )
                    
                    self.logger.info(f"Location qualified as QCT: {result.qct_name}")
            
            # Check DDA status (sites can qualify for both QCT and DDA)
            if self.dda_data is not None:
                dda_intersects = self.dda_data[self.dda_data.contains(point)]
                if not dda_intersects.empty:
                    result.dda_qualified = True
                    result.federal_basis_boost = True
                    # Basis boost is maximum 30% even if both QCT and DDA qualified
                    if result.basis_boost_percentage < 30.0:
                        result.basis_boost_percentage = 30.0
                    
                    dda_row = dda_intersects.iloc[0]
                    
                    # Extract DDA information
                    result.dda_name = (
                        dda_row.get('DDA_NAME') or 
                        dda_row.get('NAME') or 
                        dda_row.get('AREA_NAME') or 
                        'DDA Area'
                    )
                    result.dda_details = {
                        'metro_area': dda_row.get('METRO_NAME'),
                        'county': dda_row.get('COUNTY_NAME'),
                        'state': dda_row.get('STATE')
                    }
                    
                    self.logger.info(f"Location qualified as DDA: {result.dda_name}")
        
        except Exception as e:
            self.logger.error(f"Error checking QCT/DDA status: {e}")
        
        return result
    
    def _generate_analysis_notes(self, result: QCTDDAResult) -> str:
        """Generate human-readable analysis notes"""
        if result.qct_qualified:
            return f"Site qualifies for 30% basis boost as QCT: {result.qct_name}"
        elif result.dda_qualified:
            return f"Site qualifies for 30% basis boost as DDA: {result.dda_name}"
        else:
            return "Site does not qualify for federal QCT or DDA basis boost"
    
    def get_data_status(self) -> Dict[str, Any]:
        """Get status of loaded data for diagnostics"""
        return {
            'qct_data_loaded': self.qct_data is not None,
            'dda_data_loaded': self.dda_data is not None,
            'qct_features': len(self.qct_data) if self.qct_data is not None else 0,
            'dda_features': len(self.dda_data) if self.dda_data is not None else 0,
            'data_path': str(self.hud_data_path),
            'qct_file_exists': self.qct_file.exists(),
            'dda_file_exists': self.dda_file.exists()
        }