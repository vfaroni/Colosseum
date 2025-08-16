#!/usr/bin/env python3
"""
Main Site Analyzer - Core LIHTC Site Scoring Engine

This module provides the primary interface for analyzing LIHTC development sites.
Takes GPS coordinates and returns comprehensive scoring analysis.
"""

import json
import logging
from typing import Dict, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Import project modules (will be created)
from .coordinate_validator import CoordinateValidator
from ..analyzers.qct_dda_analyzer import QCTDDAAnalyzer
from ..analyzers.qap_analyzer import QAPAnalyzer
from ..analyzers.amenity_analyzer import AmenityAnalyzer
from ..analyzers.rent_analyzer import RentAnalyzer
from ..analyzers.fire_hazard_analyzer import FireHazardAnalyzer
from ..analyzers.land_use_analyzer import LandUseAnalyzer
from ..utils.report_generator import ReportGenerator

@dataclass
class SiteInfo:
    """Data class for site information"""
    latitude: float
    longitude: float
    address: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    census_tract: Optional[str] = None
    # CoStar-specific fields for land use analysis
    secondary_type: Optional[str] = None
    zoning: Optional[str] = None
    property_type: Optional[str] = None

@dataclass
class AnalysisResult:
    """Data class for analysis results"""
    site_info: SiteInfo
    federal_status: Dict[str, Any]
    state_scoring: Dict[str, Any]
    amenity_analysis: Dict[str, Any]
    rent_analysis: Dict[str, Any]
    fire_hazard_analysis: Dict[str, Any]
    land_use_analysis: Dict[str, Any]
    competitive_summary: Dict[str, Any]
    recommendations: Dict[str, Any]
    analysis_metadata: Dict[str, Any]

class SiteAnalyzer:
    """
    Main LIHTC Site Analyzer
    
    Coordinates all analysis components to provide comprehensive
    LIHTC site scoring and qualification verification.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Site Analyzer
        
        Args:
            config_path: Path to configuration file
        """
        # Set up basic logging first
        self.logger = self._setup_basic_logging()
        
        # Then load config
        self.config = self._load_config(config_path)
        
        # Update logging with config settings
        self.logger = self._setup_logging()
        
        # Initialize analyzers
        self.coordinate_validator = CoordinateValidator()
        self.qct_dda_analyzer = QCTDDAAnalyzer(self.config)
        self.qap_analyzer = QAPAnalyzer(self.config)
        self.amenity_analyzer = AmenityAnalyzer(self.config)
        self.rent_analyzer = RentAnalyzer(self.config)
        self.fire_hazard_analyzer = FireHazardAnalyzer(use_api=True)
        self.land_use_analyzer = LandUseAnalyzer(self.config)
        self.report_generator = ReportGenerator(self.config)
        
        self.logger.info("SiteAnalyzer initialized successfully")
    
    def analyze_site(
        self, 
        latitude: float, 
        longitude: float,
        state: Optional[str] = None,
        project_type: str = 'family',
        include_detailed_amenities: bool = True
    ) -> AnalysisResult:
        """
        Perform comprehensive LIHTC site analysis
        
        Args:
            latitude: Site latitude
            longitude: Site longitude  
            state: State abbreviation (auto-detected if None)
            project_type: 'family', 'senior', or 'special_needs'
            include_detailed_amenities: Include full amenity analysis
            
        Returns:
            AnalysisResult object with comprehensive analysis
        """
        start_time = datetime.now()
        self.logger.info(f"Starting analysis for coordinates: {latitude}, {longitude}")
        
        try:
            # 1. Validate coordinates
            site_info = self._validate_and_enhance_coordinates(
                latitude, longitude, state
            )
            
            # 2. Federal qualification analysis
            federal_status = self._analyze_federal_status(site_info)
            
            # 3. State-specific QAP analysis
            state_scoring = self._analyze_state_scoring(
                site_info, project_type, federal_status
            )
            
            # 4. Amenity proximity analysis
            amenity_analysis = self._analyze_amenities(
                site_info, project_type, include_detailed_amenities
            )
            
            # 5. LIHTC rent analysis
            rent_analysis = self._analyze_rents(site_info, federal_status)
            
            # 6. Fire hazard analysis (mandatory check)
            fire_hazard_analysis = self._analyze_fire_hazard(site_info)
            
            # 7. Land use analysis (mandatory check)
            land_use_analysis = self._analyze_land_use(site_info)
            
            # 8. Competitive summary and recommendations
            competitive_summary = self._generate_competitive_summary(
                federal_status, state_scoring, amenity_analysis, 
                fire_hazard_analysis, land_use_analysis
            )
            
            recommendations = self._generate_recommendations(
                site_info, federal_status, state_scoring, amenity_analysis,
                fire_hazard_analysis, land_use_analysis
            )
            
            # 9. Analysis metadata
            analysis_metadata = {
                'analysis_date': datetime.now().isoformat(),
                'analysis_duration_seconds': (datetime.now() - start_time).total_seconds(),
                'software_version': '1.0.0',
                'data_sources_used': self._get_data_sources_used(),
                'analysis_id': self._generate_analysis_id()
            }
            
            result = AnalysisResult(
                site_info=site_info,
                federal_status=federal_status,
                state_scoring=state_scoring,
                amenity_analysis=amenity_analysis,
                rent_analysis=rent_analysis,
                fire_hazard_analysis=fire_hazard_analysis,
                land_use_analysis=land_use_analysis,
                competitive_summary=competitive_summary,
                recommendations=recommendations,
                analysis_metadata=analysis_metadata
            )
            
            self.logger.info(f"Analysis completed successfully in {analysis_metadata['analysis_duration_seconds']:.2f} seconds")
            return result
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            raise
    
    def analyze_batch(
        self, 
        sites: list[Tuple[float, float]], 
        **kwargs
    ) -> list[AnalysisResult]:
        """
        Analyze multiple sites in batch
        
        Args:
            sites: List of (latitude, longitude) tuples
            **kwargs: Arguments passed to analyze_site
            
        Returns:
            List of AnalysisResult objects
        """
        self.logger.info(f"Starting batch analysis for {len(sites)} sites")
        results = []
        
        for i, (lat, lon) in enumerate(sites):
            try:
                result = self.analyze_site(lat, lon, **kwargs)
                results.append(result)
                self.logger.debug(f"Completed site {i+1}/{len(sites)}")
            except Exception as e:
                self.logger.error(f"Failed to analyze site {i+1}: {str(e)}")
                # Could append error result instead of skipping
                continue
        
        self.logger.info(f"Batch analysis completed: {len(results)}/{len(sites)} successful")
        return results
    
    def export_analysis(
        self, 
        result: AnalysisResult, 
        output_path: str,
        format: str = 'json'
    ) -> None:
        """
        Export analysis results to file
        
        Args:
            result: AnalysisResult to export
            output_path: Output file path
            format: Export format ('json', 'excel', 'pdf')
        """
        self.report_generator.export_result(result, output_path, format)
        self.logger.info(f"Analysis exported to {output_path}")
    
    def _validate_and_enhance_coordinates(
        self, 
        latitude: float, 
        longitude: float, 
        state: Optional[str]
    ) -> SiteInfo:
        """Validate coordinates and enhance with location information"""
        # Use coordinate validator to check precision and accuracy
        validation_result = self.coordinate_validator.validate_and_enhance(
            latitude, longitude, state
        )
        
        if not validation_result.is_valid:
            raise ValueError(f"Invalid coordinates: {validation_result.error_message}")
        
        # Log any coordinate precision warnings
        if hasattr(validation_result, 'warnings') and validation_result.warnings:
            self.logger.warning("COORDINATE PRECISION CONCERNS:")
            for warning in validation_result.warnings:
                self.logger.warning(f"  - {warning}")
            self.logger.warning("Consider using more precise geocoding for accurate results")
        
        return SiteInfo(
            latitude=latitude,
            longitude=longitude,
            address=validation_result.address,
            state=validation_result.state,
            county=validation_result.county,
            census_tract=validation_result.census_tract
        )
    
    def _analyze_federal_status(self, site_info: SiteInfo) -> Dict[str, Any]:
        """Analyze federal QCT/DDA qualification"""
        return self.qct_dda_analyzer.analyze(site_info)
    
    def _analyze_state_scoring(
        self, 
        site_info: SiteInfo, 
        project_type: str,
        federal_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze state-specific QAP scoring"""
        result = self.qap_analyzer.analyze(site_info, project_type, federal_status)
        
        # Extract opportunity area information if available
        if 'opportunity_area' in result:
            opp_area = result['opportunity_area']
            result['resource_category'] = opp_area.get('resource_category', 'Unknown')
            result['resource_score'] = opp_area.get('resource_score', 0)
            result['opportunity_area_points'] = result.get('scoring_breakdown', {}).get('opportunity_area_points', 0)
            result['in_opportunity_area'] = opp_area.get('qualified', False)
            
            # Add detailed opportunity area demographics
            result['opportunity_area_details'] = {
                'tract_id': opp_area.get('tract_id', 'Unknown'),
                'county': opp_area.get('county', 'Unknown'),
                'region': opp_area.get('region', 'Unknown'),
                'poverty_rate': round(opp_area.get('poverty_rate', 0) * 100, 1) if opp_area.get('poverty_rate') else 0,
                'bachelor_plus_rate': round(opp_area.get('bachelor_plus_rate', 0) * 100, 1) if opp_area.get('bachelor_plus_rate') else 0,
                'employment_rate': round(opp_area.get('employment_rate', 0) * 100, 1) if opp_area.get('employment_rate') else 0,
                'math_proficiency': round(opp_area.get('math_proficiency', 0) * 100, 1) if opp_area.get('math_proficiency') else 0,
                'reading_proficiency': round(opp_area.get('reading_proficiency', 0) * 100, 1) if opp_area.get('reading_proficiency') else 0,
                'graduation_rate': round(opp_area.get('graduation_rate', 0) * 100, 1) if opp_area.get('graduation_rate') else 0
            }
        else:
            # No opportunity area data available
            result['resource_category'] = 'Not in Opportunity Area'
            result['resource_score'] = 0
            result['opportunity_area_points'] = 0
            result['in_opportunity_area'] = False
            result['opportunity_area_details'] = {}
        
        self.logger.info(f"Resource category determined: {result.get('resource_category', 'Unknown')}")
        return result
    
    def _analyze_amenities(
        self, 
        site_info: SiteInfo, 
        project_type: str,
        include_detailed: bool
    ) -> Dict[str, Any]:
        """Analyze amenity proximity and scoring"""
        return self.amenity_analyzer.analyze(site_info, project_type, include_detailed)
    
    def _analyze_rents(
        self, 
        site_info: SiteInfo, 
        federal_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze LIHTC rent limits and projections"""
        return self.rent_analyzer.analyze(site_info, federal_status)
    
    def _analyze_fire_hazard(self, site_info: SiteInfo) -> Dict[str, Any]:
        """Analyze fire hazard risk at site"""
        self.logger.info("Analyzing fire hazard risk...")
        
        try:
            result = self.fire_hazard_analyzer.analyze_fire_risk(
                site_info.latitude, 
                site_info.longitude
            )
            
            # Add validation result
            meets_criteria, explanation = self.fire_hazard_analyzer.validate_site_fire_safety(
                site_info.latitude,
                site_info.longitude
            )
            
            result['meets_mandatory_criteria'] = meets_criteria
            result['explanation'] = explanation
            
            self.logger.info(f"Fire hazard analysis complete: {result['hazard_class']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Fire hazard analysis failed: {str(e)}")
            return {
                'hazard_class': 'Unknown',
                'meets_mandatory_criteria': None,
                'error': str(e),
                'explanation': 'Fire hazard analysis failed'
            }
    
    def _analyze_land_use(self, site_info: SiteInfo) -> Dict[str, Any]:
        """Analyze current land use at site"""
        self.logger.info("Analyzing land use...")
        
        try:
            result = self.land_use_analyzer.analyze(site_info)
            
            # Add validation result
            meets_criteria, explanation = self.land_use_analyzer.validate_site_land_use(site_info)
            
            result['meets_mandatory_criteria'] = meets_criteria
            result['explanation'] = explanation
            
            # Add detailed information for reporting
            result['current_use'] = site_info.secondary_type or 'Unknown'
            result['zoning'] = site_info.zoning or 'Unknown'
            result['prohibited_uses_present'] = len(result.get('prohibited_uses', [])) > 0
            
            self.logger.info(f"Land use analysis complete: {'Suitable' if result['is_suitable'] else 'Not Suitable'}")
            return result
            
        except Exception as e:
            self.logger.error(f"Land use analysis failed: {str(e)}")
            return {
                'current_use': site_info.secondary_type or 'Unknown',
                'zoning': site_info.zoning or 'Unknown',
                'prohibited_uses_present': None,
                'meets_mandatory_criteria': None,
                'error': str(e),
                'explanation': f'Land use analysis failed: {str(e)}',
                'data_source': 'LandUseAnalyzer (error)'
            }
    
    def _generate_competitive_summary(
        self,
        federal_status: Dict[str, Any],
        state_scoring: Dict[str, Any], 
        amenity_analysis: Dict[str, Any],
        fire_hazard_analysis: Dict[str, Any],
        land_use_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate competitive positioning summary"""
        # Check mandatory criteria first
        fire_meets = fire_hazard_analysis.get('meets_mandatory_criteria', None)
        land_meets = land_use_analysis.get('meets_mandatory_criteria', None)
        
        # If any mandatory criteria fail or are unknown, site is not competitive
        if fire_meets is False or land_meets is False or fire_meets is None or land_meets is None:
            disqualifying_factors = []
            if fire_meets is False:
                disqualifying_factors.append('High fire hazard risk')
            elif fire_meets is None:
                disqualifying_factors.append('Fire hazard status unknown - manual verification required')
            
            if land_meets is False:
                disqualifying_factors.append('Prohibited land use')
            elif land_meets is None:
                disqualifying_factors.append('Land use verification pending')
            
            return {
                'total_points': state_scoring.get('total_points', 0),
                'percentile_rank': 0,
                'competitive_tier': 'Not Eligible - Fails or Unknown Mandatory Criteria',
                'mandatory_criteria_met': False,
                'disqualifying_factors': disqualifying_factors
            }
        
        # Normal competitive assessment
        return {
            'total_points': state_scoring.get('total_points', 0),
            'percentile_rank': 85,  # Placeholder
            'competitive_tier': 'Excellent',
            'mandatory_criteria_met': True
        }
    
    def _generate_recommendations(
        self,
        site_info: SiteInfo,
        federal_status: Dict[str, Any],
        state_scoring: Dict[str, Any],
        amenity_analysis: Dict[str, Any],
        fire_hazard_analysis: Dict[str, Any],
        land_use_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate actionable recommendations"""
        
        # Check mandatory criteria
        fire_meets = fire_hazard_analysis.get('meets_mandatory_criteria', None)
        land_meets = land_use_analysis.get('meets_mandatory_criteria', None)
        
        # Determine recommendation based on all factors
        if fire_meets is False:
            return {
                'overall_recommendation': 'DO NOT PROCEED - Fire Hazard Risk',
                'priority_level': 'Disqualified',
                'key_strengths': [],
                'areas_for_improvement': [],
                'next_steps': ['Find alternative site outside high fire hazard zones'],
                'disqualifying_factors': [fire_hazard_analysis.get('explanation', 'High fire risk')]
            }
        
        if fire_meets is None:
            return {
                'overall_recommendation': 'MANUAL VERIFICATION REQUIRED - Fire Hazard Unknown',
                'priority_level': 'On Hold',
                'key_strengths': [],
                'areas_for_improvement': [],
                'next_steps': [
                    'Verify fire hazard status with official CAL FIRE maps',
                    'Check local fire department hazard classifications',
                    'Consult with fire safety professionals',
                    'Do not proceed until fire hazard status is confirmed'
                ],
                'disqualifying_factors': [fire_hazard_analysis.get('explanation', 'Fire hazard status unknown')]
            }
        
        if land_meets is False:
            return {
                'overall_recommendation': 'DO NOT PROCEED - Prohibited Land Use',
                'priority_level': 'Disqualified',
                'key_strengths': [],
                'areas_for_improvement': [],
                'next_steps': ['Find alternative site with appropriate land use'],
                'disqualifying_factors': [land_use_analysis.get('explanation', 'Prohibited land use')]
            }
        
        # Build recommendations for qualifying sites
        key_strengths = []
        if federal_status.get('qct_qualified'):
            key_strengths.append('QCT Qualified - 30% basis boost')
        if federal_status.get('dda_qualified'):
            key_strengths.append('DDA Qualified - 30% basis boost')
        if state_scoring.get('total_points', 0) >= 20:
            key_strengths.append(f'Strong CTCAC score: {state_scoring.get("total_points")}/30')
        
        return {
            'overall_recommendation': 'Proceed with development',
            'priority_level': 'High',
            'key_strengths': key_strengths,
            'areas_for_improvement': [],
            'next_steps': [
                'Complete detailed financial feasibility analysis',
                'Engage with local community for support',
                'Prepare LIHTC application materials'
            ],
            'mandatory_criteria_met': True
        }
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {config_path}. Using defaults.")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'analysis_settings': {
                'max_search_radius_miles': 5.0,
                'request_timeout_seconds': 30
            },
            'logging': {
                'level': 'INFO'
            }
        }
    
    def _setup_basic_logging(self) -> logging.Logger:
        """Setup basic logging before config is loaded"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(__name__)
        level = self.config.get('logging', {}).get('level', 'INFO')
        logger.setLevel(getattr(logging, level))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _get_data_sources_used(self) -> list[str]:
        """Get list of data sources used in analysis"""
        return [
            'HUD QCT/DDA 2025',
            'CAL FIRE Fire Hazard Severity Zones',
            'California CTCAC Opportunity Maps',
            'OpenStreetMap',
            'Census Bureau',
            'State QAP Documents'
        ]
    
    def _generate_analysis_id(self) -> str:
        """Generate unique analysis ID"""
        return f"LIHTC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Example usage and testing
if __name__ == "__main__":
    # This will be moved to examples/ or tests/
    analyzer = SiteAnalyzer()
    
    # Example analysis
    result = analyzer.analyze_site(
        latitude=34.282556,
        longitude=-118.708943,
        state='CA'
    )
    
    print(f"Analysis completed for {result.site_info.latitude}, {result.site_info.longitude}")
    print(f"Total points: {result.competitive_summary['total_points']}")