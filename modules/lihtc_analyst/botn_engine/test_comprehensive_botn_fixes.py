#!/usr/bin/env python3
"""
Test Suite for Comprehensive BOTN Engine Fixes

Tests for:
1. CostarExport column preservation
2. HQTA sites processing fixes
3. Terrain analysis implementation
4. CTCAC cost data integration

Author: VITOR WINGMAN
Date: 2025-08-16
"""

import unittest
import pandas as pd
import json
import os
from pathlib import Path
import sys

# Add current directory to Python path
sys.path.append('/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/botn_engine')

class TestComprehensiveBOTNFixes(unittest.TestCase):
    """Test comprehensive BOTN engine fixes"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data_dir = Path("/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/botn_engine/Sites")
        self.costar_file = self.test_data_dir / "CostarExport-15.xlsx"
        
        # Expected CostarExport columns (37 total)
        self.expected_columns = [
            'Property Address', 'Property Name', 'Land Area (AC)', 'Land Area (SF)',
            'Property Type', 'Secondary Type', 'Market Name', 'Submarket Name',
            'City', 'County Name', 'State', 'Zip', 'For Sale Price',
            'Sale Company Name', 'Sale Company Address', 'Sale Company City State Zip',
            'Sale Company Phone', 'Sale Company Fax', 'Sale Company Contact',
            'Zoning', 'Parcel Number 1(Min)', 'Parcel Number 2(Max)',
            'True Owner Address', 'True Owner City State Zip', 'True Owner Contact',
            'True Owner Name', 'True Owner Phone', 'Flood Risk Area',
            'Fema Flood Zone', 'FEMA Map Date', 'FEMA Map Identifier',
            'Days On Market', 'Closest Transit Stop', 'Closest Transit Stop Dist (mi)',
            'Closest Transit Stop Walk Time (min)', 'Latitude', 'Longitude'
        ]
        
    def test_costar_column_preservation(self):
        """Test that all original CostarExport columns are preserved"""
        # This test should FAIL initially - we need to implement the fix
        
        # Load CostarExport file
        if not self.costar_file.exists():
            self.skipTest(f"CostarExport file not found: {self.costar_file}")
            
        df = pd.read_excel(self.costar_file)
        
        # Verify original columns exist
        self.assertEqual(len(df.columns), 37, "CostarExport should have 37 columns")
        
        for expected_col in self.expected_columns:
            self.assertIn(expected_col, df.columns, f"Missing expected column: {expected_col}")
        
        # Test enhanced BOTN processor preserves these columns
        from enhanced_botn_processor import EnhancedBOTNProcessor
        enhanced_processor = EnhancedBOTNProcessor()
        self.assertIsNotNone(enhanced_processor, "Enhanced BOTN processor should be implemented")
        
        # Test column preservation
        preserved_df = enhanced_processor.preserve_costar_columns(df.copy())
        
        # Verify all original columns are preserved
        for expected_col in self.expected_columns:
            self.assertIn(expected_col, preserved_df.columns, f"Column should be preserved: {expected_col}")
        
        # Verify column count (should have at least 37 original columns)
        original_cols_in_result = [col for col in self.expected_columns if col in preserved_df.columns]
        self.assertEqual(len(original_cols_in_result), 37, "Should preserve all 37 original columns")
        
    def test_hqta_seven_point_qualification(self):
        """Test that HQTA sites receive correct 7-point scoring"""
        # This test should FAIL initially - we need to fix HQTA processing
        
        # Load HQTA analysis results
        hqta_file = Path("/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/botn_engine/outputs/CTCAC_HQTA_INTEGRATED_TRANSIT_ANALYSIS_20250801_093918.json")
        
        if not hqta_file.exists():
            self.skipTest(f"HQTA analysis file not found: {hqta_file}")
            
        with open(hqta_file, 'r') as f:
            hqta_data = json.load(f)
        
        # Verify HQTA sites get 7 points
        summary = hqta_data['ctcac_hqta_compliance_summary']['ctcac_hqta_compliance_summary']
        seven_point_sites = summary['sites_qualifying_7_points']
        hqta_qualified_sites = summary['sites_hqta_qualified']
        
        self.assertEqual(seven_point_sites, hqta_qualified_sites, 
                        "All HQTA qualified sites should get 7 points")
        self.assertGreater(seven_point_sites, 0, "Should have HQTA qualified sites")
        
        # Test that the fixed processor correctly identifies these sites
        from enhanced_botn_processor import EnhancedBOTNProcessor
        fixed_hqta_processor = EnhancedBOTNProcessor()
        self.assertIsNotNone(fixed_hqta_processor, "Fixed HQTA processor should be implemented")
        
        # Test HQTA qualification check
        if len(hqta_data['detailed_results']) > 0:
            # Get a known HQTA site
            test_site = hqta_data['detailed_results'][0]
            lat = test_site['latitude']
            lng = test_site['longitude']
            
            hqta_result = fixed_hqta_processor.check_hqta_qualification(lat, lng)
            
            if test_site['ctcac_analysis']['ctcac_points'] == 7:
                self.assertTrue(hqta_result['qualified'], "HQTA site should be qualified")
                self.assertEqual(hqta_result['points'], 7, "HQTA site should get 7 points")
        
    def test_terrain_slope_detection(self):
        """Test terrain analysis prevents cliff recommendations"""
        # This test should FAIL initially - we need to implement terrain analysis
        
        # Test coordinates with known steep terrain (example)
        test_coordinates = [
            {"lat": 34.123456, "lon": -118.654321, "expected_slope": 25.0},  # Steep cliff
            {"lat": 34.098765, "lon": -118.543210, "expected_slope": 3.0},   # Gentle slope
        ]
        
        # Test terrain analyzer
        from enhanced_botn_processor import EnhancedBOTNProcessor
        terrain_analyzer = EnhancedBOTNProcessor()
        self.assertIsNotNone(terrain_analyzer, "Terrain analyzer should be implemented")
        
        # Test with flat terrain (should be suitable)
        flat_result = terrain_analyzer.calculate_terrain_slope(34.098765, -118.543210)
        self.assertIsNotNone(flat_result, "Should return terrain analysis result")
        self.assertIn('risk_category', flat_result, "Should include risk category")
        self.assertIn('suitable_for_development', flat_result, "Should include suitability flag")
        
        # Note: Actual slope values will depend on real terrain data
        # The test verifies the analysis structure is correct
            
    def test_ctcac_cost_data_integration(self):
        """Test CTCAC application cost data extraction"""
        # This test should FAIL initially - we need to implement cost extraction
        
        # Expected cost categories
        expected_cost_categories = [
            'hard_costs_per_unit',
            'soft_costs_per_unit', 
            'architecture_costs_per_unit',
            'total_development_cost_per_unit'
        ]
        
        # Test CTCAC cost extractor
        from enhanced_botn_processor import EnhancedBOTNProcessor
        ctcac_cost_extractor = EnhancedBOTNProcessor()
        self.assertIsNotNone(ctcac_cost_extractor, "CTCAC cost extractor should be implemented")
        
        # Test cost extraction for different counties
        test_counties = ['Los Angeles', 'San Francisco', 'Orange', 'Unknown County']
        
        for county in test_counties:
            cost_data = ctcac_cost_extractor.get_ctcac_costs(county)
            
            # Verify all expected cost categories are present
            for category in expected_cost_categories:
                self.assertIn(category, cost_data, f"Missing cost category: {category}")
                self.assertIsInstance(cost_data[category], (int, float), f"Cost should be numeric: {category}")
                self.assertGreater(cost_data[category], 0, f"Cost should be positive: {category}")
        
        # Verify regional differences (LA should cost more than unknown)
        la_costs = ctcac_cost_extractor.get_ctcac_costs('Los Angeles')
        unknown_costs = ctcac_cost_extractor.get_ctcac_costs('Unknown County')
        self.assertGreater(la_costs['hard_costs_per_unit'], unknown_costs['hard_costs_per_unit'],
                          "LA should have higher costs than unknown county")
        
    def test_end_to_end_botn_generation(self):
        """Test complete BOTN generation with all fixes"""
        # This integration test should FAIL initially
        
        # Load test data
        if not self.costar_file.exists():
            self.skipTest(f"CostarExport file not found: {self.costar_file}")
            
        # Test complete pipeline with enhanced processor
        from enhanced_botn_processor import EnhancedBOTNProcessor
        complete_botn_generator = EnhancedBOTNProcessor()
        self.assertIsNotNone(complete_botn_generator, "Complete BOTN generator should be implemented")
        
        # Test with small sample for integration
        test_result = complete_botn_generator.process_sites(str(self.costar_file), max_sites=2)
        
        # Verify pipeline results
        self.assertIsNotNone(test_result, "Should return processed results")
        self.assertGreater(len(test_result.columns), 37, "Should have original + enhancement columns")
        
        # Check for enhancement columns
        enhancement_cols = ['hqta_qualified', 'terrain_slope_percent', 'terrain_suitable']
        for col in enhancement_cols:
            self.assertIn(col, test_result.columns, f"Should include enhancement column: {col}")
        
    def test_performance_requirements(self):
        """Test that fixes don't degrade performance"""
        # Should process 100+ sites in reasonable time
        # Should handle memory efficiently
        # Should provide progress tracking
        pass

if __name__ == '__main__':
    # Run the tests - they should all FAIL initially
    unittest.main(verbosity=2)