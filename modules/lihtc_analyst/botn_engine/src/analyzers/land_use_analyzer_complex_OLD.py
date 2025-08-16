#!/usr/bin/env python3
"""
Land Use Analyzer - Phase 6 of BOTN Filtering System

Simple and efficient land use filtering using CoStar Secondary Type classifications.
Eliminates sites that CoStar has already identified as:
- Agricultural: Farms, ranches, agricultural land
- Industrial: Manufacturing, warehouses, industrial zones

Uses CoStar's own professional property classifications for fast, accurate filtering.
"""

import logging
import pandas as pd
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass 
class LandUseResult:
    """Result of simplified land use analysis"""
    is_suitable: bool = True
    prohibited_uses: List[str] = None
    confidence_level: str = "HIGH"  # Always HIGH with CoStar data
    costar_secondary_type: Optional[str] = None
    analysis_notes: str = ""
    elimination_reason: str = ""
    
    def __post_init__(self):
        if self.prohibited_uses is None:
            self.prohibited_uses = []


class LandUseAnalyzer:
    """
    Simple land use analyzer using CoStar Secondary Type classifications
    
    Eliminates sites that CoStar has already identified as prohibited uses:
    - Agricultural: Unsuitable for LIHTC residential development
    - Industrial: Incompatible with affordable housing zoning
    """
    
    # Prohibited secondary types from CoStar (simple and reliable)
    PROHIBITED_SECONDARY_TYPES = {
        'Agricultural': 'Agricultural land unsuitable for LIHTC residential development',
        'Industrial': 'Industrial zoning/use incompatible with affordable housing'
    }
    
    # Suitable secondary types from CoStar
    SUITABLE_SECONDARY_TYPES = {
        'Residential': 'Suitable for residential LIHTC development',
        'Commercial': 'Suitable for mixed-use or adaptive reuse LIHTC development',
        'Land': 'Vacant/undeveloped land suitable for new construction'
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Land Use analyzer
        
        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # API configuration
        self.google_api_key = self.config.get('google_api_key')
        self.enable_google_places = self.google_api_key is not None
        
        # California official zoning API
        self.california_zoning_api = None
        if CALIFORNIA_ZONING_AVAILABLE:
            try:
                self.california_zoning_api = CaliforniaZoningAPI()
                self.logger.info("California official zoning API enabled")
            except Exception as e:
                self.logger.warning(f"Failed to initialize California zoning API: {e}")
        
        # Rate limiting for APIs
        self.last_api_call = 0
        self.api_delay = 0.1  # 100ms between calls
        
        self.logger.info("LandUseAnalyzer initialized successfully")
    
    def analyze(self, site_info) -> Dict[str, Any]:
        """
        Perform land use analysis for a site
        
        Args:
            site_info: SiteInfo object with site details
            
        Returns:
            Dictionary with land use analysis results
        """
        try:
            result = self._analyze_land_use_suitability(site_info)
            
            # Convert to expected format for main analyzer
            return {
                'is_suitable': result.is_suitable,
                'prohibited_uses': result.prohibited_uses,
                'confidence_level': result.confidence_level,
                'suspected_land_use': self._determine_suspected_land_use(result),
                'elimination_reason': self._get_elimination_reason(result),
                'manual_review_required': len(result.prohibited_uses) > 0 and result.is_suitable,
                'costar_info': {
                    'secondary_type': result.costar_secondary_type
                },
                'data_sources': result.data_sources,
                'analysis_notes': result.analysis_notes,
                'detailed_result': result  # For debugging/advanced use
            }
            
        except Exception as e:
            self.logger.error(f"Land use analysis failed: {str(e)}")
            return {
                'is_suitable': None,  # Unknown, requires manual review
                'prohibited_uses': [],
                'confidence_level': 'LOW',
                'error': str(e),
                'analysis_notes': f"Analysis failed: {str(e)} - Manual review required"
            }
    
    def _analyze_land_use_suitability(self, site_info) -> LandUseResult:
        """
        Core land use suitability analysis
        
        Args:
            site_info: Site information object
            
        Returns:
            LandUseResult with detailed analysis
        """
        result = LandUseResult()
        
        # 1. Try California official zoning API first (if coordinates available)
        if (self.california_zoning_api and 
            hasattr(site_info, 'latitude') and hasattr(site_info, 'longitude') and
            site_info.latitude and site_info.longitude):
            self._analyze_california_official_zoning(site_info, result)
        
        # 2. Analyze CoStar data (primary source if no official zoning)
        if result.confidence_level == "LOW":
            self._analyze_costar_data(site_info, result)
        
        # 3. If still inconclusive, try additional sources
        if result.confidence_level == "LOW":
            # Try Google Places API if available
            if self.enable_google_places:
                self._analyze_google_places(site_info, result)
            
            # Try zoning analysis (fallback to local zoning codes)
            self._analyze_zoning_data(site_info, result)
        
        # 3. Final determination
        self._make_final_determination(result)
        
        return result
    
    def _analyze_california_official_zoning(self, site_info, result: LandUseResult):
        """Analyze using California's official statewide zoning database"""
        try:
            zoning_info = self.california_zoning_api.get_zoning_by_coordinates(
                site_info.latitude, site_info.longitude
            )
            
            if zoning_info:
                result.data_sources.append('California Official Zoning Database')
                result.zoning_classification = zoning_info.code
                
                # Use the official determination
                if zoning_info.is_prohibited_use:
                    result.is_suitable = False
                    result.prohibited_uses.append(f"{zoning_info.prohibited_category}: Official zoning '{zoning_info.code}'")
                    result.confidence_level = "HIGH"  # Official data = high confidence
                    result.analysis_notes += f"Official CA zoning: {zoning_info.description}. {zoning_info.analysis_notes}"
                else:
                    result.is_suitable = True
                    result.confidence_level = "HIGH"  # Official data = high confidence
                    result.analysis_notes += f"Official CA zoning suitable: {zoning_info.description}. "
                
                self.logger.debug(f"Official zoning: {zoning_info.code} - {zoning_info.description}")
                
            else:
                result.analysis_notes += "No official California zoning data found for coordinates. "
                # Keep confidence at LOW to try other sources
                
        except Exception as e:
            self.logger.error(f"Error analyzing official California zoning: {e}")
            result.analysis_notes += f"Official zoning lookup error: {str(e)}. "
            # Keep confidence at LOW to try other sources
    
    def _analyze_costar_data(self, site_info, result: LandUseResult):
        """Analyze CoStar Secondary Type for prohibited uses"""
        try:
            # Extract CoStar data from site_info
            costar_secondary_type = getattr(site_info, 'secondary_type', None)
            result.costar_secondary_type = costar_secondary_type
            result.data_sources.append('CoStar Secondary Type')
            
            # Handle None, NaN, or non-string values
            if not costar_secondary_type or not isinstance(costar_secondary_type, str):
                result.confidence_level = "LOW"
                result.analysis_notes += "No valid CoStar Secondary Type available. "
                return
            
            # Check against prohibited uses
            secondary_type_lower = costar_secondary_type.lower()
            
            for category, details in self.PROHIBITED_USES.items():
                # Check CoStar types
                for prohibited_type in details['costar_types']:
                    if prohibited_type.lower() in secondary_type_lower:
                        result.is_suitable = False
                        result.prohibited_uses.append(f"{category}: {costar_secondary_type}")
                        result.confidence_level = "HIGH"
                        result.analysis_notes += f"CoStar Secondary Type '{costar_secondary_type}' indicates {category} use. "
                        return
                
                # Check keywords
                for keyword in details['keywords']:
                    if keyword in secondary_type_lower:
                        result.is_suitable = False
                        result.prohibited_uses.append(f"{category}: {costar_secondary_type}")
                        result.confidence_level = "MEDIUM"
                        result.analysis_notes += f"CoStar Secondary Type contains '{keyword}' keyword. "
                        return
            
            # Check if it's an acceptable use
            for category, acceptable_terms in self.ACCEPTABLE_USES.items():
                for term in acceptable_terms:
                    if term.lower() in secondary_type_lower:
                        result.is_suitable = True
                        result.confidence_level = "HIGH"
                        result.analysis_notes += f"CoStar Secondary Type '{costar_secondary_type}' indicates suitable {category} use. "
                        return
            
            # Unknown CoStar category
            result.confidence_level = "MEDIUM"
            result.analysis_notes += f"CoStar Secondary Type '{costar_secondary_type}' not in known categories - assumed suitable. "
            
        except Exception as e:
            self.logger.error(f"Error analyzing CoStar data: {e}")
            result.confidence_level = "LOW"
            result.analysis_notes += f"CoStar analysis error: {str(e)}. "
    
    def _analyze_google_places(self, site_info, result: LandUseResult):
        """Analyze Google Places API for nearby businesses"""
        if not self.enable_google_places:
            return
            
        try:
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_api_call < self.api_delay:
                time.sleep(self.api_delay)
            
            latitude = getattr(site_info, 'latitude', None)
            longitude = getattr(site_info, 'longitude', None)
            
            if not latitude or not longitude:
                result.analysis_notes += "No coordinates for Google Places lookup. "
                return
            
            # Search for nearby places
            places_data = self._query_google_places(latitude, longitude)
            
            if places_data:
                result.data_sources.append('Google Places API')
                result.google_place_types = places_data.get('types', [])
                
                # Check for prohibited business types
                for place_type in result.google_place_types:
                    for category, details in self.PROHIBITED_USES.items():
                        if place_type in details['google_types']:
                            result.is_suitable = False
                            result.prohibited_uses.append(f"{category}: Google Places type '{place_type}'")
                            result.confidence_level = "MEDIUM"
                            result.analysis_notes += f"Google Places indicates {category} business nearby. "
                            return
            
            self.last_api_call = time.time()
            
        except Exception as e:
            self.logger.error(f"Error analyzing Google Places: {e}")
            result.analysis_notes += f"Google Places analysis error: {str(e)}. "
    
    def _query_google_places(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Query Google Places API for location information"""
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            
            params = {
                'location': f"{latitude},{longitude}",
                'radius': 100,  # 100 meter radius
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'OK' and data.get('results'):
                # Return first result (closest)
                return data['results'][0]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Google Places API error: {e}")
            return None
    
    def _analyze_zoning_data(self, site_info, result: LandUseResult):
        """Analyze zoning classification for prohibited uses"""
        try:
            # Extract zoning from site_info
            zoning = getattr(site_info, 'zoning', None)
            result.zoning_classification = zoning
            
            # Handle None, NaN, or non-string values
            if zoning and isinstance(zoning, str):
                result.data_sources.append('Zoning Classification')
                zoning_upper = zoning.upper()
                
                # Check against prohibited zoning codes
                for category, details in self.PROHIBITED_USES.items():
                    for zone_code in details['zoning_codes']:
                        # Use exact match or word boundary matching to avoid false positives
                        if (zoning_upper == zone_code or  # Exact match
                            zoning_upper.startswith(zone_code + '-') or  # Hyphen separator (e.g., M1-L)
                            zoning_upper.startswith(zone_code + '/') or  # Slash separator (e.g., M1/R)
                            zoning_upper.endswith('-' + zone_code) or    # Suffix with hyphen
                            zoning_upper.endswith('/' + zone_code)):     # Suffix with slash
                            result.is_suitable = False
                            result.prohibited_uses.append(f"{category}: Zoning '{zoning}'")
                            result.confidence_level = "MEDIUM"
                            result.analysis_notes += f"Zoning '{zoning}' indicates {category} use. "
                            return
                
                result.analysis_notes += f"Zoning '{zoning}' appears suitable for residential development. "
            else:
                result.analysis_notes += "No zoning information available. "
                
        except Exception as e:
            self.logger.error(f"Error analyzing zoning data: {e}")
            result.analysis_notes += f"Zoning analysis error: {str(e)}. "
    
    def _make_final_determination(self, result: LandUseResult):
        """Make final suitability determination based on all data sources"""
        # CONSERVATIVE APPROACH: Only eliminate sites with HIGH confidence prohibited uses
        # MEDIUM/LOW confidence sites are kept for manual review
        if result.prohibited_uses and result.confidence_level == "HIGH":
            result.is_suitable = False
            result.analysis_notes += "HIGH confidence prohibited use - site eliminated. "
            return
        elif result.prohibited_uses and result.confidence_level in ["MEDIUM", "LOW"]:
            # Keep the site but flag it for manual review
            result.is_suitable = True
            result.analysis_notes += f"FLAGGED for manual review - {result.confidence_level} confidence prohibited use detected but not eliminated. "
            return
        
        # Adjust confidence based on data sources used
        if len(result.data_sources) >= 2:
            if result.confidence_level == "MEDIUM":
                result.confidence_level = "HIGH"
        elif len(result.data_sources) == 0:
            result.confidence_level = "LOW"
            result.analysis_notes += "No data sources available for analysis - manual review required. "
        
        # Default to suitable unless proven otherwise
        if result.is_suitable is None:
            result.is_suitable = True
            result.analysis_notes += "No prohibited uses detected - assumed suitable. "
    
    def get_prohibited_use_summary(self) -> Dict[str, List[str]]:
        """Get summary of all prohibited use categories"""
        summary = {}
        for category, details in self.PROHIBITED_USES.items():
            summary[category] = {
                'keywords': details['keywords'],
                'costar_types': details['costar_types'],
                'reason': f"Eliminates {category} sites that are unsuitable for LIHTC development"
            }
        return summary
    
    def validate_site_land_use(self, site_info) -> tuple[bool, str]:
        """
        Quick validation method for pipeline integration
        
        Args:
            site_info: Site information object
            
        Returns:
            Tuple of (is_suitable, explanation)
        """
        try:
            result = self.analyze(site_info)
            
            if result.get('error'):
                return (None, f"Analysis failed: {result['error']} - Manual review required")
            
            is_suitable = result['is_suitable']
            prohibited = result['prohibited_uses']
            confidence = result['confidence_level']
            
            if is_suitable:
                explanation = f"Land use suitable for LIHTC development (confidence: {confidence})"
                if result['analysis_notes']:
                    explanation += f" - {result['analysis_notes']}"
            else:
                explanation = f"Prohibited land uses detected: {', '.join(prohibited)}"
                
            return (is_suitable, explanation)
            
        except Exception as e:
            return (None, f"Land use validation error: {str(e)} - Manual review required")
    
    def _determine_suspected_land_use(self, result: LandUseResult) -> str:
        """Determine the suspected land use category based on analysis"""
        # If we have CoStar Secondary Type, use it
        if result.costar_secondary_type and isinstance(result.costar_secondary_type, str):
            return result.costar_secondary_type
        
        # If we detected prohibited uses, return the category
        if result.prohibited_uses:
            # Extract the category from the first prohibited use
            first_prohibited = result.prohibited_uses[0]
            if ":" in first_prohibited:
                category = first_prohibited.split(":")[0]
                return f"Suspected {category.title()}"
        
        # If we have zoning, make an educated guess
        if result.zoning_classification and isinstance(result.zoning_classification, str):
            zoning = result.zoning_classification.upper()
            if any(z in zoning for z in ['R', 'RES']):
                return "Likely Residential"
            elif any(z in zoning for z in ['C', 'COM']):
                return "Likely Commercial"
            elif any(z in zoning for z in ['M', 'I', 'IND']):
                return "Likely Industrial"
            elif any(z in zoning for z in ['A', 'AG']):
                return "Likely Agricultural"
        
        return "Unknown"
    
    def _get_elimination_reason(self, result: LandUseResult) -> str:
        """Get the reason for elimination or retention"""
        if not result.is_suitable and result.confidence_level == "HIGH":
            return "Eliminated - HIGH confidence prohibited use"
        elif result.prohibited_uses and result.is_suitable:
            return f"Kept for manual review - {result.confidence_level} confidence prohibited use"
        elif result.is_suitable:
            return "Suitable for LIHTC development"
        else:
            return "Unknown elimination reason"


# Example usage and testing
if __name__ == "__main__":
    # Enable logging to see what's happening
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
    
    # Test the analyzer
    analyzer = LandUseAnalyzer()
    
    # Mock site info for testing
    class MockSiteInfo:
        def __init__(self, secondary_type=None, zoning=None, latitude=None, longitude=None):
            self.secondary_type = secondary_type
            self.zoning = zoning
            self.latitude = latitude
            self.longitude = longitude
    
    # Test cases with California coordinates for official zoning API testing
    test_sites = [
        MockSiteInfo(secondary_type="Residential", zoning="R1", latitude=34.0522, longitude=-118.2437),  # LA Commercial
        MockSiteInfo(secondary_type="Commercial", zoning="C1", latitude=37.7749, longitude=-122.4194),  # SF Commercial
        MockSiteInfo(secondary_type="Industrial", zoning="M1", latitude=34.0928, longitude=-117.4353),  # SB Area
        MockSiteInfo(secondary_type="Agricultural", zoning="A1", latitude=39.5296, longitude=-121.3716),  # Yuba Agricultural
        MockSiteInfo(secondary_type="Land", zoning="R2", latitude=32.7157, longitude=-117.1611),  # SD Commercial
    ]
    
    print("Land Use Analyzer Test Results:")
    print("=" * 50)
    
    for i, site in enumerate(test_sites, 1):
        result = analyzer.analyze(site)
        print(f"\nTest Site {i}:")
        print(f"  Secondary Type: {site.secondary_type}")
        print(f"  Zoning: {site.zoning}")
        print(f"  Suitable: {result['is_suitable']}")
        print(f"  Confidence: {result['confidence_level']}")
        print(f"  Prohibited Uses: {result['prohibited_uses']}")
        print(f"  Notes: {result['analysis_notes']}")
    
    print(f"\nProhibited Use Categories:")
    print("=" * 30)
    summary = analyzer.get_prohibited_use_summary()
    for category, details in summary.items():
        print(f"{category.upper()}:")
        print(f"  Keywords: {', '.join(details['keywords'])}")
        print(f"  Reason: {details['reason']}")