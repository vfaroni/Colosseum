"""
LIHTC Site Scorer - Comprehensive LIHTC Development Site Analysis

A Python package for analyzing and scoring Low-Income Housing Tax Credit (LIHTC) 
development sites across the United States.

Main Components:
- Site analysis and scoring
- Federal QCT/DDA qualification verification  
- State-specific QAP compliance checking
- Amenity proximity analysis
- LIHTC rent calculations
- Competitive positioning analysis

Example Usage:
    from src.core.site_analyzer import SiteAnalyzer
    
    analyzer = SiteAnalyzer()
    result = analyzer.analyze_site(
        latitude=34.282556,
        longitude=-118.708943,
        state='CA'
    )
"""

__version__ = "1.0.0"
__author__ = "LIHTC Development Team"
__email__ = "development@company.com"

# Import main classes for convenience
from .core.site_analyzer import SiteAnalyzer, AnalysisResult, SiteInfo

__all__ = [
    'SiteAnalyzer',
    'AnalysisResult', 
    'SiteInfo'
]