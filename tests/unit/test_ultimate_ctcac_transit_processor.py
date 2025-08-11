#!/usr/bin/env python3
"""
Unit Tests for Ultimate CTCAC Transit Processor

Tests the core functionality of the ultimate transit processor
that integrates comprehensive datasets for CTCAC scoring.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import geopandas as gpd
from pathlib import Path
import tempfile
import sys
import os

# Add the botn_engine directory to the path
botn_engine_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'modules', 'lihtc_analyst', 'botn_engine')
sys.path.insert(0, botn_engine_path)

from ultimate_ctcac_transit_processor import UltimateCTCACTransitProcessor


class TestUltimateCTCACTransitProcessor(unittest.TestCase):
    """Test suite for Ultimate CTCAC Transit Processor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = UltimateCTCACTransitProcessor()
    
    def test_initialization(self):
        """Test processor initialization"""
        self.assertIsNotNone(self.processor)
        self.assertEqual(self.processor.distance_threshold_miles, 1/3)
        self.assertEqual(self.processor.frequency_threshold_minutes, 30)
        self.assertEqual(self.processor.tiebreaker_threshold_minutes, 15)
        self.assertEqual(self.processor.tiebreaker_distance_miles, 0.5)
    
    def test_haversine_distance_calculation(self):
        """Test haversine distance calculation accuracy"""
        # Test known distance: LA to Long Beach (~25 miles)
        lat1, lon1 = 34.0522, -118.2437  # Los Angeles
        lat2, lon2 = 33.7701, -118.1937  # Long Beach
        
        distance_meters = self.processor.haversine_distance_meters(lat1, lon1, lat2, lon2)
        distance_miles = distance_meters / 1609.34
        
        # Should be approximately 20 miles (allowing 10% tolerance)
        self.assertGreater(distance_miles, 18)
        self.assertLess(distance_miles, 25)
    
    def test_haversine_distance_close_points(self):
        """Test haversine distance for close points"""
        # Test points about 1/3 mile apart
        lat1, lon1 = 34.0522, -118.2437
        lat2, lon2 = 34.0570, -118.2437  # ~536 meters north
        
        distance_meters = self.processor.haversine_distance_meters(lat1, lon1, lat2, lon2)
        
        # Should be approximately 536 meters (1/3 mile)
        self.assertGreater(distance_meters, 400)
        self.assertLess(distance_meters, 700)
    
    @patch('geopandas.read_file')
    def test_load_datasets_missing_files(self, mock_read_file):
        """Test load_all_datasets with missing files"""
        mock_read_file.side_effect = FileNotFoundError("File not found")
        
        result = self.processor.load_all_datasets()
        self.assertFalse(result)
    
    def test_hqta_qualification_no_data(self):
        """Test HQTA qualification when no data is loaded"""
        result = self.processor.analyze_hqta_qualification(34.0522, -118.2437, "test_site")
        
        self.assertFalse(result['within_hqta'])
        self.assertEqual(result['ctcac_points_earned'], 0)
        self.assertEqual(result['analysis_method'], 'HQTA_DISABLED')
    
    def test_find_nearby_stops_no_data(self):
        """Test find_nearby_stops when no comprehensive stops loaded"""
        stops = self.processor.find_nearby_stops_ultimate(34.0522, -118.2437)
        self.assertEqual(len(stops), 0)
    
    def test_analyze_ultimate_frequency_no_stops(self):
        """Test frequency analysis with no stops"""
        result = self.processor.analyze_ultimate_frequency([])
        
        self.assertEqual(result['total_stops'], 0)
        self.assertEqual(result['high_frequency_stops'], 0)
        self.assertEqual(result['estimated_peak_frequency'], 999)
    
    def test_analyze_ultimate_frequency_with_stops(self):
        """Test frequency analysis with mock stops"""
        mock_stops = [
            {
                'stop_id': 'test_1',
                'distance_meters': 100,
                'n_routes': 2,
                'calculated_frequency_minutes': 20,
                'frequency_method': 'TEST_METHOD_1',
                'hqts_enhancement': None,
                'is_high_frequency': True  # STRIKE_LEADER FIX: Added required field
            },
            {
                'stop_id': 'test_2', 
                'distance_meters': 200,
                'n_routes': 1,
                'calculated_frequency_minutes': 35,
                'frequency_method': 'TEST_METHOD_2',
                'hqts_enhancement': {'actual_peak_trips_per_hour': 4},
                'is_high_frequency': False  # STRIKE_LEADER FIX: Added required field
            }
        ]
        
        result = self.processor.analyze_ultimate_frequency(mock_stops)
        
        self.assertEqual(result['total_stops'], 2)
        self.assertEqual(result['total_routes'], 3)
        self.assertEqual(result['estimated_peak_frequency'], 20)  # Best frequency
        self.assertEqual(result['high_frequency_stops'], 1)  # Only first stop ≤30 min
        self.assertEqual(result['high_frequency_validated_stops'], 1)  # STRIKE_LEADER FIX: Added expected field
        self.assertEqual(result['hqts_enhanced_stops'], 1)  # Only second stop has HQTS
    
    def test_calculate_ctcac_points_no_qualification(self):
        """Test CTCAC points calculation with no qualifying stops"""
        mock_frequency_analysis = {
            'high_frequency_stops': 0,
            'high_frequency_validated_stops': 0,  # STRIKE_LEADER FIX: Added required field
            'total_stops': 0,  # STRIKE_LEADER FIX: Added required field
            'estimated_peak_frequency': 999
        }
        
        with patch.object(self.processor, 'find_nearby_stops_ultimate', return_value=[]):
            result = self.processor.calculate_ultimate_ctcac_points(
                mock_frequency_analysis, 34.0522, -118.2437
            )
        
        self.assertEqual(result['base_points'], 0)
        self.assertEqual(result['tiebreaker_points'], 0)
        self.assertEqual(result['total_points'], 0)
    
    def test_calculate_ctcac_points_with_qualification(self):
        """Test CTCAC points calculation with qualifying stops"""
        mock_frequency_analysis = {
            'high_frequency_stops': 2,
            'high_frequency_validated_stops': 1,  # STRIKE_LEADER FIX: Added required field
            'total_stops': 3,  # STRIKE_LEADER FIX: Added required field
            'estimated_peak_frequency': 25
        }
        
        # Mock tie-breaker stops with good frequency
        mock_tiebreaker_stops = [
            {'calculated_frequency_minutes': 12},
            {'calculated_frequency_minutes': 18}
        ]
        
        with patch.object(self.processor, 'find_nearby_stops_ultimate', return_value=mock_tiebreaker_stops):
            result = self.processor.calculate_ultimate_ctcac_points(
                mock_frequency_analysis, 34.0522, -118.2437
            )
        
        # STRIKE_LEADER FIX: Updated expected points for corrected scoring
        self.assertEqual(result['base_points'], 6)  # High-frequency validated stops = 6 points
        self.assertEqual(result['tiebreaker_points'], 1)  # 12 min ≤ 15 min threshold
        self.assertEqual(result['total_points'], 7)
        self.assertEqual(result['tiebreaker_frequency_minutes'], 12)
    
    def test_analyze_site_ultimate_basic(self):
        """Test basic site analysis functionality"""
        site_data = {
            'site_id': 'TEST_001',
            'latitude': 34.0522,
            'longitude': -118.2437
        }
        
        # Mock HQTA analysis to return not qualified
        with patch.object(self.processor, 'analyze_hqta_qualification') as mock_hqta:
            mock_hqta.return_value = {
                'within_hqta': False,
                'ctcac_points_earned': 0,
                'analysis_method': 'HQTA_POLYGON_PROVEN',
                'details': 'Site not within any HQTA boundary'
            }
            
            # Mock no nearby stops
            with patch.object(self.processor, 'find_nearby_stops_ultimate', return_value=[]):
                result = self.processor.analyze_site_ultimate(site_data)
        
        self.assertEqual(result['site_id'], 'TEST_001')
        self.assertFalse(result['transit_qualified'])
        self.assertEqual(result['qualification_method'], 'NO_NEARBY_STOPS')
        self.assertEqual(result['ctcac_points_earned'], 0)
    
    def test_site_coordinates_validation(self):
        """Test that site coordinates are properly validated"""
        # Test with string coordinates (should be converted to float)
        site_data = {
            'site_id': 'TEST_002',
            'latitude': '34.0522',
            'longitude': '-118.2437'
        }
        
        with patch.object(self.processor, 'analyze_hqta_qualification') as mock_hqta:
            mock_hqta.return_value = {'within_hqta': False, 'ctcac_points_earned': 0}
            with patch.object(self.processor, 'find_nearby_stops_ultimate', return_value=[]):
                result = self.processor.analyze_site_ultimate(site_data)
        
        # Should successfully convert string coordinates to float
        self.assertEqual(result['latitude'], 34.0522)
        self.assertEqual(result['longitude'], -118.2437)


class TestProcessorIntegration(unittest.TestCase):
    """Integration tests for processor components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = UltimateCTCACTransitProcessor()
    
    def test_full_workflow_mock_data(self):
        """Test complete workflow with mocked data"""
        # Create a simple test portfolio
        test_portfolio = pd.DataFrame({
            'Site_ID': ['SITE_001', 'SITE_002'],
            'Latitude': [34.0522, 34.0570],
            'Longitude': [-118.2437, -118.2437]
        })
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            test_portfolio.to_csv(tmp_file.name, index=False)
            tmp_file_path = tmp_file.name
        
        try:
            # Mock the load_all_datasets to return True
            with patch.object(self.processor, 'load_all_datasets', return_value=True):
                # Mock analyze_site_ultimate to return consistent results
                mock_site_result = {
                    'site_id': 'SITE_001',
                    'latitude': 34.0522,
                    'longitude': -118.2437,
                    'transit_qualified': True,
                    'qualification_method': 'ULTIMATE_FREQUENCY_QUALIFIED',
                    'ctcac_points_earned': 4,
                    'hqts_enhanced_stops': 2,
                    'analysis_timestamp': '2025-08-01T12:00:00'
                }
                
                with patch.object(self.processor, 'analyze_site_ultimate', return_value=mock_site_result):
                    result = self.processor.process_portfolio_ultimate(tmp_file_path)
                
                # Verify summary structure
                self.assertIn('summary', result)
                self.assertIn('detailed_results', result)
                self.assertEqual(result['summary']['total_sites_analyzed'], 2)
                self.assertEqual(len(result['detailed_results']), 2)
        
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)


if __name__ == '__main__':
    unittest.main()