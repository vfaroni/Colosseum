#!/usr/bin/env python3
"""
Unit tests for CoStar Analysis Tool - Roman Engineering Standards Compliance
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import pandas as pd
import json

# Add the module path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules" / "lihtc_analyst" / "botn_engine"))

from costar_analysis_tool import CoStarAnalyzer

class TestCoStarAnalyzer(unittest.TestCase):
    """Test suite for CoStar Analysis Tool"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.analyzer = CoStarAnalyzer()
        
        # Create mock sites directory structure
        self.sites_dir = self.temp_dir / "Sites"
        self.sites_dir.mkdir()
        
        # Override paths for testing
        self.analyzer.base_path = self.temp_dir
        self.analyzer.sites_path = self.sites_dir
        
        # Create test files
        self.create_test_files()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def create_test_files(self):
        """Create mock CoStar export files for testing"""
        
        # Create test CoStar files with different structures
        test_files = [
            {
                'filename': 'CostarExport-8.xlsx',
                'columns': ['Property Name', 'Property Address', 'City', 'State', 'For Sale Price'],
                'rows': 25
            },
            {
                'filename': 'CostarExport-9.xlsx',
                'columns': ['Property Name', 'Property Address', 'City', 'State', 'For Sale Price', 'Land Area (AC)'],
                'rows': 30
            },
            {
                'filename': 'Combined_CostarExport_Final.xlsx',
                'columns': ['Property Name', 'Property Address', 'City', 'State', 'For Sale Price', 'Market Name'],
                'rows': 50
            }
        ]
        
        for file_info in test_files:
            data = []
            for i in range(file_info['rows']):
                row = {}
                for col in file_info['columns']:
                    if col == 'Property Name':
                        row[col] = f'Test Property {i}'
                    elif col == 'Property Address':
                        row[col] = f'{100 + i} Test Street'
                    elif col == 'For Sale Price':
                        row[col] = 1000000 + (i * 50000)
                    else:
                        row[col] = f'Test_{col}_{i}'
                data.append(row)
            
            df = pd.DataFrame(data)
            file_path = self.sites_dir / file_info['filename']
            df.to_excel(file_path, index=False)
    
    def test_analyzer_initialization(self):
        """Test that analyzer initializes correctly"""
        analyzer = CoStarAnalyzer()
        self.assertIsInstance(analyzer.base_path, Path)
        self.assertIsInstance(analyzer.sites_path, Path)
        self.assertEqual(analyzer.analysis_results, {})
    
    def test_analyze_single_file(self):
        """Test analysis of a single CoStar file"""
        test_file = self.sites_dir / "CostarExport-8.xlsx"
        result = self.analyzer.analyze_single_file(test_file)
        
        # Check basic analysis structure
        self.assertIn('file_path', result)
        self.assertIn('row_count', result)
        self.assertIn('column_count', result)
        self.assertIn('columns', result)
        
        # Check specific values
        self.assertEqual(result['row_count'], 25)
        self.assertEqual(result['column_count'], 5)
        self.assertIn('Property Name', result['columns'])
        self.assertIn('Property Address', result['columns'])
    
    def test_analyze_single_file_with_error(self):
        """Test analysis behavior with corrupted file"""
        corrupted_file = self.sites_dir / "corrupted.xlsx"
        
        # Create a corrupted file
        with open(corrupted_file, 'w') as f:
            f.write("This is not a valid Excel file")
        
        result = self.analyzer.analyze_single_file(corrupted_file)
        
        # Check error handling
        self.assertIn('error', result)
        self.assertIn('analysis_failed', result)
        self.assertTrue(result['analysis_failed'])
    
    def test_analyze_all_costar_files(self):
        """Test comprehensive analysis of all files"""
        results = self.analyzer.analyze_all_costar_files()
        
        # Should analyze the files we created
        self.assertGreater(len(results), 0)
        
        # Check that valid files were analyzed
        analyzed_files = [filename for filename, result in results.items() 
                         if 'analysis_failed' not in result]
        self.assertGreater(len(analyzed_files), 0)
        
        # Check analysis_results was populated
        self.assertEqual(self.analyzer.analysis_results, results)
    
    def test_property_identification(self):
        """Test property identification logic"""
        test_file = self.sites_dir / "CostarExport-8.xlsx"
        result = self.analyzer.analyze_single_file(test_file)
        
        # Should identify Property Name as unique identifier
        self.assertIsNotNone(result.get('unique_properties'))
        unique_props = result['unique_properties']
        self.assertEqual(unique_props['column'], 'Property Name')
        self.assertEqual(unique_props['unique_count'], 25)
        self.assertEqual(unique_props['total_count'], 25)
    
    def test_duplicate_detection(self):
        """Test duplicate detection logic"""
        # Create file with duplicates
        data = [
            {'Property Name': 'Duplicate Prop', 'Property Address': '123 Main St', 'City': 'Test'},
            {'Property Name': 'Duplicate Prop', 'Property Address': '456 Oak Ave', 'City': 'Test'},
            {'Property Name': 'Unique Prop', 'Property Address': '789 Pine Rd', 'City': 'Test'}
        ]
        
        df = pd.DataFrame(data)
        duplicate_file = self.sites_dir / "CostarExport-duplicates.xlsx"
        df.to_excel(duplicate_file, index=False)
        
        result = self.analyzer.analyze_single_file(duplicate_file)
        
        # Check duplicate detection
        duplicate_check = result.get('duplicate_check')
        self.assertIsNotNone(duplicate_check)
        self.assertTrue(duplicate_check['has_duplicates'])
        self.assertEqual(duplicate_check['duplicate_count'], 2)
    
    def test_save_analysis_report(self):
        """Test saving analysis report to JSON"""
        # Run analysis first
        self.analyzer.analyze_all_costar_files()
        
        # Save report
        self.analyzer.save_analysis_report()
        
        # Check that report file was created
        report_file = self.analyzer.base_path / "costar_analysis_report.json"
        self.assertTrue(report_file.exists())
        
        # Check report content
        with open(report_file, 'r') as f:
            report = json.load(f)
        
        self.assertIn('analysis_timestamp', report)
        self.assertIn('files_analyzed', report)
        self.assertIn('analysis_results', report)
        self.assertIn('consolidation_plan', report)
    
    def test_consolidation_strategy_generation(self):
        """Test consolidation strategy recommendation"""
        # This method doesn't return anything, just check it runs without error
        self.analyzer.analyze_all_costar_files()
        
        # Should run without error
        self.analyzer.recommend_consolidation_strategy()
    
    def test_file_size_calculation(self):
        """Test file size calculation accuracy"""
        test_file = self.sites_dir / "CostarExport-8.xlsx"
        result = self.analyzer.analyze_single_file(test_file)
        
        # Should have file size information
        self.assertIn('file_size_mb', result)
        self.assertIsInstance(result['file_size_mb'], float)
        self.assertGreater(result['file_size_mb'], 0)
    
    def test_column_analysis_accuracy(self):
        """Test column analysis accuracy"""
        test_file = self.sites_dir / "CostarExport-9.xlsx"  # Has 6 columns
        result = self.analyzer.analyze_single_file(test_file)
        
        # Check column information accuracy
        self.assertEqual(result['column_count'], 6)
        self.assertIn('Land Area (AC)', result['columns'])
        self.assertEqual(len(result['columns']), 6)
    
    def test_sample_data_extraction(self):
        """Test sample data extraction functionality"""
        test_file = self.sites_dir / "CostarExport-8.xlsx"
        result = self.analyzer.analyze_single_file(test_file)
        
        # Should have sample data
        self.assertIn('sample_data', result)
        sample_data = result['sample_data']
        
        # Should have samples for key columns
        self.assertIn('Property Name', sample_data)
        self.assertIn('Property Address', sample_data)
        
        # Sample data should not be empty
        self.assertGreater(len(sample_data['Property Name']), 0)

class TestCoStarAnalyzerIntegration(unittest.TestCase):
    """Integration tests for CoStar analyzer"""
    
    def test_end_to_end_analysis_workflow(self):
        """Test complete end-to-end analysis workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sites_path = temp_path / "Sites"
            sites_path.mkdir()
            
            # Create test files
            for i in [8, 9]:
                df = pd.DataFrame({
                    'Property Name': [f'Property_{i}_{j}' for j in range(5)],
                    'Property Address': [f'{j} Street_{i}' for j in range(5)],
                    'For Sale Price': [1000000 + (j * 100000) for j in range(5)]
                })
                
                file_path = sites_path / f"CostarExport-{i}.xlsx"
                df.to_excel(file_path, index=False)
            
            # Run analysis
            analyzer = CoStarAnalyzer()
            analyzer.base_path = temp_path
            analyzer.sites_path = sites_path
            
            results = analyzer.analyze_all_costar_files()
            
            # Verify results
            self.assertGreater(len(results), 0)
            
            # Check that report was created
            analyzer.save_analysis_report()
            report_file = temp_path / "costar_analysis_report.json"
            self.assertTrue(report_file.exists())

def run_tests():
    """Run all analysis tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCoStarAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestCoStarAnalyzerIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)