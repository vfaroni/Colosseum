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
from typing import Dict, Any, Optional, List
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
        Initialize the simplified Land Use analyzer
        
        Args:
            config: Configuration dictionary (unused in simple version)
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Simplified LandUseAnalyzer initialized (CoStar Secondary Type only)")
    
    def analyze(self, site_info) -> Dict[str, Any]:
        """
        Perform simple land use analysis using CoStar Secondary Type
        
        Args:
            site_info: SiteInfo object with site details
            
        Returns:
            Dictionary with land use analysis results
        """
        try:
            # Get CoStar Secondary Type
            secondary_type = getattr(site_info, 'secondary_type', None)
            
            # Create result
            result = LandUseResult()
            result.costar_secondary_type = secondary_type
            
            # Simple classification based on CoStar Secondary Type
            if pd.isna(secondary_type) or secondary_type is None:
                result.is_suitable = True  # Default to suitable if unknown
                result.confidence_level = "LOW"
                result.analysis_notes = "No CoStar Secondary Type available - assumed suitable"
                result.elimination_reason = "Unknown secondary type - assumed suitable"
                
            elif secondary_type in self.PROHIBITED_SECONDARY_TYPES:
                result.is_suitable = False
                result.prohibited_uses.append(f"{secondary_type}: {self.PROHIBITED_SECONDARY_TYPES[secondary_type]}")
                result.confidence_level = "HIGH"
                result.analysis_notes = f"CoStar Secondary Type '{secondary_type}' indicates prohibited use"
                result.elimination_reason = f"Eliminated - CoStar classified as {secondary_type}"
                
            elif secondary_type in self.SUITABLE_SECONDARY_TYPES:
                result.is_suitable = True
                result.confidence_level = "HIGH"
                result.analysis_notes = f"CoStar Secondary Type '{secondary_type}' suitable for LIHTC"
                result.elimination_reason = f"Suitable - CoStar classified as {secondary_type}"
                
            else:
                # Unknown secondary type - assume suitable but flag for review
                result.is_suitable = True
                result.confidence_level = "MEDIUM"
                result.analysis_notes = f"Unknown CoStar Secondary Type '{secondary_type}' - assumed suitable"
                result.elimination_reason = f"Unknown secondary type '{secondary_type}' - assumed suitable"
            
            # Convert to expected format for main analyzer
            return {
                'is_suitable': result.is_suitable,
                'prohibited_uses': result.prohibited_uses,
                'confidence_level': result.confidence_level,
                'suspected_land_use': result.costar_secondary_type or "Unknown",
                'elimination_reason': result.elimination_reason,
                'manual_review_required': result.confidence_level in ["LOW", "MEDIUM"],
                'costar_info': {
                    'secondary_type': result.costar_secondary_type
                },
                'data_sources': ['CoStar Secondary Type'] if result.costar_secondary_type else [],
                'analysis_notes': result.analysis_notes
            }
            
        except Exception as e:
            self.logger.error(f"Simple land use analysis failed: {str(e)}")
            return {
                'is_suitable': True,  # Default to suitable on error
                'prohibited_uses': [],
                'confidence_level': 'LOW',
                'error': str(e),
                'analysis_notes': f"Analysis failed: {str(e)} - Assumed suitable"
            }
    
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
                return (True, f"Analysis failed: {result['error']} - Assumed suitable")
            
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
            return (True, f"Land use validation error: {str(e)} - Assumed suitable")
    
    def get_prohibited_use_summary(self) -> Dict[str, Any]:
        """Get summary of all prohibited use categories"""
        return {
            'prohibited_types': list(self.PROHIBITED_SECONDARY_TYPES.keys()),
            'suitable_types': list(self.SUITABLE_SECONDARY_TYPES.keys()),
            'method': 'CoStar Secondary Type classification',
            'accuracy': 'HIGH - based on CoStar professional analysis'
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the simplified analyzer
    analyzer = LandUseAnalyzer()
    
    # Mock site info for testing
    class MockSiteInfo:
        def __init__(self, secondary_type=None):
            self.secondary_type = secondary_type
    
    # Test cases
    test_sites = [
        MockSiteInfo(secondary_type="Residential"),
        MockSiteInfo(secondary_type="Commercial"), 
        MockSiteInfo(secondary_type="Industrial"),
        MockSiteInfo(secondary_type="Agricultural"),
        MockSiteInfo(secondary_type="Land"),
        MockSiteInfo(secondary_type=None),
    ]
    
    print("🏛️ SIMPLIFIED LAND USE ANALYZER TEST")
    print("=" * 45)
    
    for i, site in enumerate(test_sites, 1):
        result = analyzer.analyze(site)
        print(f"\nTest Site {i}:")
        print(f"  Secondary Type: {site.secondary_type}")
        print(f"  Suitable: {result['is_suitable']}")
        print(f"  Confidence: {result['confidence_level']}")
        print(f"  Prohibited Uses: {result['prohibited_uses']}")
        print(f"  Elimination Reason: {result['elimination_reason']}")
    
    print(f"\nProhibited Use Summary:")
    print("=" * 25)
    summary = analyzer.get_prohibited_use_summary()
    print(f"Prohibited Types: {', '.join(summary['prohibited_types'])}")
    print(f"Suitable Types: {', '.join(summary['suitable_types'])}")
    print(f"Method: {summary['method']}")
    print(f"Accuracy: {summary['accuracy']}")