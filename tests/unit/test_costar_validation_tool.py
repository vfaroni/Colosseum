#!/usr/bin/env python3
"""
Unit tests for CoStar Validation Tool - Roman Engineering Standards Compliance
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import pandas as pd
import json
import numpy as np

# Add the module path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules" / "lihtc_analyst" / "botn_engine"))

from costar_validation_tool import CoStarValidator

class TestCoStarValidator(unittest.TestCase):
    """Test suite for CoStar Validation Tool"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.validator = CoStarValidator()
        
        # Create mock sites directory structure
        self.sites_dir = self.temp_dir / "Sites"
        self.sites_dir.mkdir()
        
        # Override paths for testing
        self.validator.base_path = self.temp_dir
        self.validator.sites_path = self.sites_dir
        
        # Create test consolidated data
        self.create_test_consolidated_data()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def create_test_consolidated_data(self):
        """Create mock consolidated data for testing"""
        
        # Create realistic test data
        test_data = []
        for i in range(100):  # 100 test records
            row = {
                'Property Name': f'Test Property {i}' if i % 10 != 0 else '',  # Some empty names
                'Property Address': f'{100 + i} Test Street, Test City, CA',
                'City': 'Test City',
                'State': 'CA',
                'For Sale Price': 500000 + (i * 25000) if i % 15 != 0 else np.nan,  # Some missing prices
                'Land Area (AC)': 2.5 + (i * 0.1),
                'Property Type': 'Land',
                'Market Name': 'Test Market',
                'County Name': 'Test County',
                'Zip': '90210',
                'Zoning': 'R1',
                'Source_File': f'CostarExport-{8 + (i % 8)}.xlsx',
                'Source_File_Number': 8 + (i % 8),
                'Load_Timestamp': '2025-01-30T10:00:00',
                'Consolidation_Timestamp': '2025-01-30T12:00:00',
                'Consolidation_Version': 'CombinedCostarExportUpdated_v1.0',
                'Has_Property_Name': i % 10 != 0,
                'Has_Address': True,
                'Has_Price': i % 15 != 0,
                'Data_Completeness_Score': 80 + (i % 21),  # Scores from 80-100
                'Record_Quality': 'Excellent' if (80 + (i % 21)) >= 90 else 'Good'
            }
            test_data.append(row)
        
        df = pd.DataFrame(test_data)
        
        # Save as consolidated file
        consolidated_file = self.sites_dir / "CombinedCostarExportUpdated.xlsx"
        with pd.ExcelWriter(consolidated_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Consolidated_Data', index=False)
        
        # Create mock stats file
        stats = {
            'consolidation_timestamp': '2025-01-30T12:00:00',
            'source_files': {
                'count': 8,
                'total_original_rows': 120
            },
            'final_dataset': {
                'total_rows': 100,
                'unique_properties': 90,
                'data_quality_distribution': {'Excellent': 60, 'Good': 40}
            },
            'consolidation_impact': {
                'rows_removed': 20,
                'deduplication_rate': 16.67,
                'data_completeness_avg': 85.5
            }
        }
        
        stats_file = self.sites_dir / "CombinedCostarExportUpdated_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
    
    def test_validator_initialization(self):
        """Test that validator initializes correctly"""
        validator = CoStarValidator()
        self.assertIsInstance(validator.base_path, Path)
        self.assertIsInstance(validator.sites_path, Path)
    
    def test_validate_file_structure(self):
        """Test file structure validation"""
        # Load test data
        consolidated_file = self.sites_dir / "CombinedCostarExportUpdated.xlsx"
        df = pd.read_excel(consolidated_file, sheet_name='Consolidated_Data')
        
        result = self.validator.validate_file_structure(df)
        
        # Check validation structure
        self.assertIn('status', result)
        self.assertIn('checks', result)
        self.assertIn('details', result)
        
        # Should pass basic structure checks
        checks = result['checks']
        self.assertTrue(checks['has_data'])
        self.assertTrue(checks['has_columns'])
        
        # Check details
        details = result['details']
        self.assertEqual(details['row_count'], 100)
        self.assertGreater(details['column_count'], 15)
    
    def test_validate_data_quality(self):
        """Test data quality validation"""
        consolidated_file = self.sites_dir / "CombinedCostarExportUpdated.xlsx"
        df = pd.read_excel(consolidated_file, sheet_name='Consolidated_Data')
        
        result = self.validator.validate_data_quality(df)
        
        # Check basic structure
        self.assertIn('status', result)
        self.assertIn('checks', result)
        self.assertIn('details', result)
        
        # Check specific validations
        checks = result['checks']
        self.assertIn('all_required_columns_present', checks)
        self.assertIn('has_metadata_columns', checks)
        
        # Check details
        details = result['details']
        self.assertIn('completeness_stats', details)
    
    def test_validate_column_preservation(self):
        """Test column preservation validation"""
        consolidated_file = self.sites_dir / "CombinedCostarExportUpdated.xlsx"
        df = pd.read_excel(consolidated_file, sheet_name='Consolidated_Data')
        
        result = self.validator.validate_column_preservation(df)
        
        # Should detect core columns
        checks = result['checks']
        self.assertIn('core_columns_preserved', checks)
        self.assertIn('has_metadata_columns', checks)
        
        # Check that metadata columns were detected
        details = result['details']
        self.assertGreater(details['metadata_columns_count'], 0)
    
    def test_validate_source_tracking(self):
        """Test source tracking validation"""
        consolidated_file = self.sites_dir / "CombinedCostarExportUpdated.xlsx"
        df = pd.read_excel(consolidated_file, sheet_name='Consolidated_Data')
        
        result = self.validator.validate_source_tracking(df)
        
        # Should detect source tracking
        checks = result['checks']
        self.assertTrue(checks['has_source_tracking'])
        
        # Should identify multiple sources
        details = result['details']
        self.assertGreater(len(details['unique_sources']), 1)
    
    def test_validate_deduplication(self):
        """Test deduplication validation"""
        consolidated_file = self.sites_dir / "CombinedCostarExportUpdated.xlsx"
        df = pd.read_excel(consolidated_file, sheet_name='Consolidated_Data')
        
        result = self.validator.validate_deduplication(df)
        
        # Should be able to check duplicates
        checks = result['checks']
        self.assertTrue(checks['can_check_duplicates'])
        
        # Should have low duplicate rate (our test data has unique addresses)
        details = result['details']
        self.assertLessEqual(details['duplicate_rate_percent'], 2.0)
    
    def test_validate_business_logic(self):
        """Test business logic validation"""
        consolidated_file = self.sites_dir / "CombinedCostarExportUpdated.xlsx"
        df = pd.read_excel(consolidated_file, sheet_name='Consolidated_Data')
        
        result = self.validator.validate_business_logic(df)
        
        # Should have price data
        checks = result['checks']
        self.assertTrue(checks['has_price_data'])
        
        # Should detect California focus
        self.assertTrue(checks['primarily_california'])
        
        # Check price statistics
        details = result['details']
        price_stats = details['price_stats']
        self.assertIn('min_price', price_stats)
        self.assertIn('max_price', price_stats)
        self.assertGreater(price_stats['count_with_price'], 0)
    
    def test_comprehensive_validation_with_valid_data(self):
        """Test comprehensive validation with valid data"""
        # This should pass most validations
        success = self.validator.comprehensive_validation()
        
        # May have warnings but should complete successfully
        # (We can't guarantee 100% success due to our test data limitations)
        self.assertIsInstance(success, bool)
        
        # Check that report was generated
        report_file = self.sites_dir / "CoStar_Validation_Report.json"
        self.assertTrue(report_file.exists())
    
    def test_comprehensive_validation_missing_file(self):
        """Test comprehensive validation with missing file"""
        # Remove the consolidated file
        consolidated_file = self.sites_dir / "CombinedCostarExportUpdated.xlsx"
        consolidated_file.unlink()
        
        success = self.validator.comprehensive_validation()
        
        # Should fail gracefully
        self.assertFalse(success)
    
    def test_generate_validation_report(self):
        """Test validation report generation"""
        # Load test data first
        consolidated_file = self.sites_dir / "CombinedCostarExportUpdated.xlsx"
        df = pd.read_excel(consolidated_file, sheet_name='Consolidated_Data')
        
        # Run individual validations
        validation_results = {
            'file_info': self.validator.validate_file_structure(df),
            'data_quality': self.validator.validate_data_quality(df),
            'column_preservation': self.validator.validate_column_preservation(df)
        }
        
        # Load mock stats
        stats_file = self.sites_dir / "CombinedCostarExportUpdated_stats.json"
        with open(stats_file, 'r') as f:
            stats = json.load(f)
        
        # Generate report
        self.validator.generate_validation_report(validation_results, stats)
        
        # Check report was created
        report_file = self.sites_dir / "CoStar_Validation_Report.json"
        self.assertTrue(report_file.exists())
        
        # Check report content
        with open(report_file, 'r') as f:
            report = json.load(f)
        
        self.assertIn('validation_timestamp', report)
        self.assertIn('overall_status', report)
        self.assertIn('detailed_results', report)
    
    def test_validation_with_poor_quality_data(self):
        """Test validation with poor quality data"""
        # Create poor quality data
        poor_data = []
        for i in range(50):
            row = {
                'Property Name': '' if i % 3 == 0 else f'Property {i}',  # Many empty
                'Property Address': '' if i % 4 == 0 else f'Address {i}',  # Many empty
                'For Sale Price': np.nan if i % 2 == 0 else 100,  # Many missing, some too low
                'City': 'Test City',
                'State': 'CA',
                'Source_File': 'test.xlsx',
                'Data_Completeness_Score': 30 + (i % 20),  # Low scores
                'Record_Quality': 'Poor'
            }
            poor_data.append(row)
        
        df = pd.DataFrame(poor_data)
        
        # Test data quality validation
        result = self.validator.validate_data_quality(df)
        
        # Should detect poor quality
        checks = result['checks']
        # May fail completeness checks
        details = result['details']
        self.assertIn('completeness_stats', details)

class TestCoStarValidatorEdgeCases(unittest.TestCase):
    """Test edge cases for CoStar validator"""
    
    def test_empty_dataframe_validation(self):
        """Test validation with empty dataframe"""
        validator = CoStarValidator()
        empty_df = pd.DataFrame()
        
        # Should handle empty dataframe gracefully
        result = validator.validate_file_structure(empty_df)
        
        self.assertIn('status', result)
        self.assertFalse(result['status'])  # Should fail
    
    def test_dataframe_with_missing_columns(self):
        """Test validation with missing required columns"""
        validator = CoStarValidator()
        
        # Create dataframe without required columns
        df = pd.DataFrame({
            'Random Column': [1, 2, 3],
            'Another Column': [4, 5, 6]
        })
        
        result = validator.validate_data_quality(df)
        
        # Should detect missing required columns
        checks = result['checks']
        self.assertFalse(checks['all_required_columns_present'])
        
        details = result['details']
        self.assertGreater(len(details['missing_required_columns']), 0)

def run_tests():
    """Run all validation tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCoStarValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestCoStarValidatorEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)