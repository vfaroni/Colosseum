#!/usr/bin/env python3
"""
Unit tests for SiteAnalyzer core functionality
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import the modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.site_analyzer import SiteAnalyzer, SiteInfo, AnalysisResult

class TestSiteAnalyzer:
    """Test cases for SiteAnalyzer class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.analyzer = SiteAnalyzer()
        
        # Sample coordinates (Simi Valley site)
        self.test_lat = 34.282556
        self.test_lon = -118.708943
        self.test_state = 'CA'
    
    def test_init(self):
        """Test SiteAnalyzer initialization"""
        assert self.analyzer is not None
        assert hasattr(self.analyzer, 'config')
        assert hasattr(self.analyzer, 'logger')
    
    def test_site_info_creation(self):
        """Test SiteInfo data class"""
        site_info = SiteInfo(
            latitude=self.test_lat,
            longitude=self.test_lon,
            state=self.test_state
        )
        
        assert site_info.latitude == self.test_lat
        assert site_info.longitude == self.test_lon
        assert site_info.state == self.test_state
        assert site_info.address is None
    
    @patch('src.core.site_analyzer.CoordinateValidator')
    @patch('src.core.site_analyzer.QCTDDAAnalyzer')
    @patch('src.core.site_analyzer.QAPAnalyzer')
    @patch('src.core.site_analyzer.AmenityAnalyzer')
    @patch('src.core.site_analyzer.RentAnalyzer')
    def test_analyze_site_basic(self, mock_rent, mock_amenity, mock_qap, mock_qct, mock_coord):
        """Test basic site analysis workflow"""
        # Mock the analyzer responses
        mock_qct.return_value.analyze.return_value = {
            'qct_qualified': True,
            'dda_qualified': False,
            'basis_boost': 0.30
        }
        
        mock_qap.return_value.analyze.return_value = {
            'total_points': 23,
            'amenity_points': 15,
            'opportunity_area_points': 8
        }
        
        mock_amenity.return_value.analyze.return_value = {
            'transit': {'points': 7, 'distance': 0.24},
            'medical': {'points': 3, 'distance': 0.03}
        }
        
        mock_rent.return_value.analyze.return_value = {
            'max_rents': {'studio': 1500, '1br': 1600, '2br': 1900}
        }
        
        # Run analysis
        result = self.analyzer.analyze_site(
            latitude=self.test_lat,
            longitude=self.test_lon,
            state=self.test_state
        )
        
        # Verify result structure
        assert isinstance(result, AnalysisResult)
        assert result.site_info.latitude == self.test_lat
        assert result.site_info.longitude == self.test_lon
        assert result.federal_status['qct_qualified'] == True
        assert result.state_scoring['total_points'] == 23
    
    def test_coordinate_validation(self):
        """Test coordinate validation"""
        # Valid coordinates
        assert self.analyzer._validate_and_enhance_coordinates(
            self.test_lat, self.test_lon, self.test_state
        )
        
        # Invalid latitude
        with pytest.raises(Exception):
            self.analyzer._validate_and_enhance_coordinates(
                91.0, self.test_lon, self.test_state
            )
        
        # Invalid longitude  
        with pytest.raises(Exception):
            self.analyzer._validate_and_enhance_coordinates(
                self.test_lat, 181.0, self.test_state
            )
    
    def test_config_loading(self):
        """Test configuration loading"""
        # Test with default config
        config = self.analyzer._get_default_config()
        assert 'analysis_settings' in config
        assert 'logging' in config
        
        # Test config values
        assert config['analysis_settings']['max_search_radius_miles'] == 5.0
        assert config['logging']['level'] == 'INFO'
    
    def test_batch_analysis(self):
        """Test batch analysis functionality"""
        sites = [
            (34.282556, -118.708943),  # Simi Valley
            (34.0522, -118.2437),     # Los Angeles  
            (37.7749, -122.4194)      # San Francisco
        ]
        
        # Mock analyze_site to avoid actual API calls
        with patch.object(self.analyzer, 'analyze_site') as mock_analyze:
            mock_result = Mock(spec=AnalysisResult)
            mock_analyze.return_value = mock_result
            
            results = self.analyzer.analyze_batch(sites)
            
            assert len(results) == 3
            assert mock_analyze.call_count == 3
    
    def test_export_functionality(self):
        """Test analysis export"""
        # Create mock result
        mock_result = Mock(spec=AnalysisResult)
        
        # Mock report generator
        with patch.object(self.analyzer, 'report_generator') as mock_generator:
            self.analyzer.export_analysis(
                result=mock_result,
                output_path='test_output.json',
                format='json'
            )
            
            mock_generator.export_result.assert_called_once_with(
                mock_result, 'test_output.json', 'json'
            )
    
    def test_analysis_metadata(self):
        """Test analysis metadata generation"""
        data_sources = self.analyzer._get_data_sources_used()
        assert isinstance(data_sources, list)
        assert 'HUD QCT/DDA 2025' in data_sources
        assert 'OpenStreetMap' in data_sources
        
        analysis_id = self.analyzer._generate_analysis_id()
        assert analysis_id.startswith('LIHTC_')
        assert len(analysis_id) > 10


class TestSiteInfo:
    """Test cases for SiteInfo data class"""
    
    def test_site_info_basic(self):
        """Test basic SiteInfo functionality"""
        site = SiteInfo(
            latitude=34.282556,
            longitude=-118.708943,
            address="123 Test St, Simi Valley, CA",
            state="CA"
        )
        
        assert site.latitude == 34.282556
        assert site.longitude == -118.708943
        assert site.address == "123 Test St, Simi Valley, CA"
        assert site.state == "CA"
    
    def test_site_info_optional_fields(self):
        """Test SiteInfo with only required fields"""
        site = SiteInfo(latitude=34.0, longitude=-118.0)
        
        assert site.latitude == 34.0
        assert site.longitude == -118.0
        assert site.address is None
        assert site.state is None
        assert site.county is None
        assert site.census_tract is None


class TestAnalysisResult:
    """Test cases for AnalysisResult data class"""
    
    def test_analysis_result_structure(self):
        """Test AnalysisResult data structure"""
        site_info = SiteInfo(latitude=34.0, longitude=-118.0)
        
        result = AnalysisResult(
            site_info=site_info,
            federal_status={'qct_qualified': True},
            state_scoring={'total_points': 20},
            amenity_analysis={'transit': {'points': 7}},
            rent_analysis={'max_rents': {}},
            competitive_summary={'tier': 'Excellent'},
            recommendations={'proceed': True},
            analysis_metadata={'version': '1.0.0'}
        )
        
        assert result.site_info == site_info
        assert result.federal_status['qct_qualified'] == True
        assert result.state_scoring['total_points'] == 20
        assert result.amenity_analysis['transit']['points'] == 7


# Integration test with sample data
class TestIntegration:
    """Integration tests with sample data"""
    
    def test_simi_valley_analysis(self):
        """Test analysis of known good Simi Valley site"""
        # This test uses the actual Simi Valley coordinates we analyzed
        # Mock external dependencies to avoid API calls in tests
        
        analyzer = SiteAnalyzer()
        
        with patch.multiple(
            analyzer,
            _analyze_federal_status=Mock(return_value={'qct_qualified': True}),
            _analyze_state_scoring=Mock(return_value={'total_points': 23}),
            _analyze_amenities=Mock(return_value={'total_amenities': 5}),
            _analyze_rents=Mock(return_value={'max_rents': {}}),
        ):
            result = analyzer.analyze_site(
                latitude=34.282556,
                longitude=-118.708943,
                state='CA'
            )
            
            assert result.site_info.latitude == 34.282556
            assert result.site_info.longitude == -118.708943
            assert result.federal_status['qct_qualified'] == True
            assert result.state_scoring['total_points'] == 23


# Fixtures for common test data
@pytest.fixture
def sample_site_info():
    """Fixture providing sample site information"""
    return SiteInfo(
        latitude=34.282556,
        longitude=-118.708943,
        address="Tapo Street & Barnard, Simi Valley, CA",
        state="CA",
        county="Ventura",
        census_tract="06111008201"
    )

@pytest.fixture
def sample_config():
    """Fixture providing sample configuration"""
    return {
        "api_keys": {
            "positionstack": "test_key",
            "census": "test_key"
        },
        "analysis_settings": {
            "max_search_radius_miles": 5.0,
            "request_timeout_seconds": 30
        },
        "logging": {
            "level": "INFO"
        }
    }


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])