#!/usr/bin/env python3
"""
Coordinate Validator - GPS coordinate validation and geocoding

Validates GPS coordinates and enhances with location information.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of coordinate validation"""
    is_valid: bool
    latitude: float
    longitude: float
    address: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    census_tract: Optional[str] = None
    error_message: Optional[str] = None


class CoordinateValidator:
    """
    Validates and enhances GPS coordinates with location information
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the coordinate validator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    def validate_and_enhance(
        self, 
        latitude: float, 
        longitude: float,
        state: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate coordinates and enhance with location information
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            state: Optional state abbreviation
            
        Returns:
            ValidationResult with validation status and enhanced data
        """
        # Basic coordinate validation
        if not self._is_valid_latitude(latitude):
            return ValidationResult(
                is_valid=False,
                latitude=latitude,
                longitude=longitude,
                error_message=f"Invalid latitude: {latitude}. Must be between -90 and 90."
            )
        
        if not self._is_valid_longitude(longitude):
            return ValidationResult(
                is_valid=False,
                latitude=latitude,
                longitude=longitude,
                error_message=f"Invalid longitude: {longitude}. Must be between -180 and 180."
            )
        
        # Basic US bounds check
        if not self._is_within_us_bounds(latitude, longitude):
            self.logger.warning(f"Coordinates {latitude}, {longitude} appear to be outside US bounds")
        
        # Enhanced coordinate precision validation
        precision_warnings = self._check_coordinate_precision(latitude, longitude)
        
        result = ValidationResult(
            is_valid=True,
            latitude=latitude,
            longitude=longitude,
            address=self._get_placeholder_address(latitude, longitude),
            state=state or self._guess_state_from_coordinates(latitude, longitude),
            county="Sample County",  # Placeholder
            census_tract="06037001.00"  # Placeholder
        )
        
        # Add precision warnings to result
        if precision_warnings:
            self.logger.warning(f"Coordinate precision concerns: {'; '.join(precision_warnings)}")
            if not hasattr(result, 'warnings'):
                result.warnings = precision_warnings
        
        self.logger.info(f"Validated coordinates: {latitude}, {longitude}")
        return result
    
    def _is_valid_latitude(self, latitude: float) -> bool:
        """Check if latitude is within valid range"""
        return -90.0 <= latitude <= 90.0
    
    def _is_valid_longitude(self, longitude: float) -> bool:
        """Check if longitude is within valid range"""
        return -180.0 <= longitude <= 180.0
    
    def _is_within_us_bounds(self, latitude: float, longitude: float) -> bool:
        """
        Check if coordinates are within approximate US bounds
        Includes Alaska, Hawaii, and territories
        """
        # Continental US bounds (approximate)
        if (24.0 <= latitude <= 49.0) and (-125.0 <= longitude <= -66.0):
            return True
        
        # Alaska bounds (approximate)
        if (54.0 <= latitude <= 71.0) and (-180.0 <= longitude <= -129.0):
            return True
        
        # Hawaii bounds (approximate)
        if (18.0 <= latitude <= 23.0) and (-161.0 <= longitude <= -154.0):
            return True
        
        # US Territories (approximate)
        if (17.0 <= latitude <= 19.0) and (-68.0 <= longitude <= -64.0):  # Puerto Rico/USVI
            return True
        
        return False
    
    def _get_placeholder_address(self, latitude: float, longitude: float) -> str:
        """Generate placeholder address for testing"""
        return f"Sample Address at {latitude:.6f}, {longitude:.6f}"
    
    def _check_coordinate_precision(self, latitude: float, longitude: float) -> list[str]:
        """
        Check coordinate precision and flag potential geocoding issues
        
        Returns:
            List of warning messages about coordinate precision
        """
        warnings = []
        
        # Check if coordinates appear to be rounded (potential city center)
        lat_decimals = len(str(latitude).split('.')[-1]) if '.' in str(latitude) else 0
        lon_decimals = len(str(longitude).split('.')[-1]) if '.' in str(longitude) else 0
        
        if lat_decimals < 4 or lon_decimals < 4:
            warnings.append(f"Low coordinate precision (lat: {lat_decimals} decimals, lon: {lon_decimals} decimals) - may indicate approximate location")
        
        # Check for common rounded values that suggest city center coordinates
        if abs(latitude - round(latitude, 1)) < 0.001:
            warnings.append("Latitude appears rounded to 1 decimal place - possible city center coordinate")
        
        if abs(longitude - round(longitude, 1)) < 0.001:
            warnings.append("Longitude appears rounded to 1 decimal place - possible city center coordinate")
        
        # Check for exact integer values (very suspicious for property locations)
        if latitude == int(latitude) or longitude == int(longitude):
            warnings.append("Coordinates contain integer values - highly suspicious for specific property location")
        
        return warnings
    
    def _guess_state_from_coordinates(self, latitude: float, longitude: float) -> str:
        """
        Very basic state guessing based on coordinates
        In full implementation, this would use proper geographic lookup
        """
        # California bounds (very approximate)
        if (32.0 <= latitude <= 42.0) and (-125.0 <= longitude <= -114.0):
            return "CA"
        
        # Texas bounds (very approximate)
        if (25.0 <= latitude <= 37.0) and (-107.0 <= longitude <= -93.0):
            return "TX"
        
        # New York bounds (very approximate)
        if (40.0 <= latitude <= 45.0) and (-80.0 <= longitude <= -71.0):
            return "NY"
        
        # Default fallback
        return "Unknown"