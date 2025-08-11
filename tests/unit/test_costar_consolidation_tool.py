#!/usr/bin/env python3
"""
Unit tests for CoStar Consolidation Tool - Roman Engineering Standards Compliance
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import pandas as pd
import numpy as np

# Add the module path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules" / "lihtc_analyst" / "botn_engine"))

from costar_consolidation_tool import CoStarConsolidator

class TestCoStarConsolidator(unittest.TestCase):
    """Test suite for CoStar Consolidation Tool"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.consolidator = CoStarConsolidator()
        
        # Create mock sites directory structure
        self.sites_dir = self.temp_dir / "Sites"
        self.sites_dir.mkdir()
        
        # Override paths for testing
        self.consolidator.base_path = self.temp_dir
        self.consolidator.sites_path = self.sites_dir
        
        # Create test data files
        self.create_test_costar_files()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def create_test_costar_files(self):
        """Create mock CoStar export files for testing"""
        
        # Base columns that should be in all files
        base_columns = [
            'Property Address', 'Property Name', 'City', 'State', 'Zip',
            'For Sale Price', 'Market Name', 'County Name'
        ]
        
        # Additional columns for some files
        extended_columns = base_columns + [
            'Land Area (AC)', 'Land Area (SF)', 'Property Type',
            'Sale Company Name', 'Zoning', 'Parcel Number 1(Min)'
        ]
        
        # Create test files with different structures (like real CoStar exports)
        test_files = [
            {
                'filename': 'CostarExport-8.xlsx',
                'columns': extended_columns,
                'rows': 50,
                'has_duplicates': True
            },
            {
                'filename': 'CostarExport-9.xlsx',
                'columns': extended_columns,
                'rows': 75,
                'has_duplicates': False
            },
            {
                'filename': 'CostarExport-10.xlsx',
                'columns': base_columns,  # Fewer columns like real file
                'rows': 60,
                'has_duplicates': True
            }
        ]
        
        for file_info in test_files:
            df_data = []
            
            for i in range(file_info['rows']):
                row = {}
                
                # Generate test data for each column
                for col in file_info['columns']:
                    if col == 'Property Name':
                        # Include some duplicates if specified
                        if file_info['has_duplicates'] and i < 5:
                            row[col] = f'Duplicate Property {i % 3}'
                        else:
                            row[col] = f'Test Property {file_info["filename"][-6:-5]}_{i}'
                    elif col == 'Property Address':
                        row[col] = f'{100 + i} Test Street, Test City, CA'
                    elif col == 'City':
                        row[col] = 'Test City'
                    elif col == 'State':
                        row[col] = 'CA'
                    elif col == 'For Sale Price':
                        row[col] = 1000000 + (i * 50000)
                    elif 'Land Area' in col:
                        row[col] = 2.5 + (i * 0.1)
                    else:
                        row[col] = f'Test_{col}_{i}'
                
                df_data.append(row)
            
            # Create DataFrame and save to Excel
            df = pd.DataFrame(df_data)
            file_path = self.sites_dir / file_info['filename']
            df.to_excel(file_path, index=False)
    
    def test_consolidator_initialization(self):
        """Test that consolidator initializes correctly"""
        consolidator = CoStarConsolidator()
        self.assertIsInstance(consolidator.base_path, Path)
        self.assertIsInstance(consolidator.sites_path, Path)
        self.assertIsNone(consolidator.consolidated_data)
        self.assertEqual(consolidator.consolidation_stats, {})
    
    def test_smart_consolidate_dataframes(self):
        """Test smart consolidation of multiple DataFrames"""
        # Create test DataFrames with different structures
        df1 = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6],
            'Source_File': ['test1.xlsx'] * 3,
            'Source_File_Number': [1] * 3
        })
        
        df2 = pd.DataFrame({
            'A': [7, 8],
            'C': [9, 10],  # Different column
            'Source_File': ['test2.xlsx'] * 2,
            'Source_File_Number': [2] * 2
        })
        
        result = self.consolidator.smart_consolidate_dataframes([df1, df2])
        
        # Check that all rows are preserved
        self.assertEqual(len(result), 5)
        
        # Check that all columns are preserved (outer join)
        expected_columns = {'A', 'B', 'C', 'Source_File', 'Source_File_Number'}
        self.assertEqual(set(result.columns), expected_columns)
        
        # Check that data from both sources is present
        source_files = set(result['Source_File'])
        self.assertEqual(source_files, {'test1.xlsx', 'test2.xlsx'})
    
    def test_smart_deduplication(self):
        """Test smart deduplication with priority logic"""
        # Create DataFrame with duplicates
        df = pd.DataFrame({
            'Property Name': ['Prop A', 'Prop A', 'Prop B', 'Prop C'],
            'Property Address': ['123 Main St', '123 Main St', '456 Oak Ave', '789 Pine Rd'],
            'Source_File_Number': [8, 15, 10, 12],  # Higher number should be kept
            'Data': ['old_data', 'new_data', 'data_b', 'data_c']
        })
        
        result = self.consolidator.smart_deduplication(df)
        
        # Should have 3 rows (one duplicate removed)
        self.assertEqual(len(result), 3)
        
        # The duplicate with higher source file number should be kept
        prop_a_rows = result[result['Property Name'] == 'Prop A']
        self.assertEqual(len(prop_a_rows), 1)
        self.assertEqual(prop_a_rows.iloc[0]['Source_File_Number'], 15)
        self.assertEqual(prop_a_rows.iloc[0]['Data'], 'new_data')
    
    def test_add_consolidation_metadata(self):
        """Test adding consolidation metadata"""
        df = pd.DataFrame({
            'Property Name': ['Test Prop 1', '', 'Test Prop 3'],
            'Property Address': ['123 Main St', '456 Oak Ave', ''],
            'For Sale Price': [1000000, 0, 2000000],
            'City': ['Test City', 'Test City', 'Test City'],
            'State': ['CA', 'CA', 'CA']
        })
        
        result = self.consolidator.add_consolidation_metadata(df)
        
        # Check that metadata columns were added
        metadata_columns = [
            'Consolidation_Timestamp', 'Consolidation_Version',
            'Has_Property_Name', 'Has_Address', 'Has_Price',
            'Data_Completeness_Score', 'Record_Quality'
        ]
        
        for col in metadata_columns:
            self.assertIn(col, result.columns)
        
        # Check data quality calculations
        self.assertFalse(result.iloc[1]['Has_Property_Name'])  # Empty name
        self.assertFalse(result.iloc[2]['Has_Address'])        # Empty address
        self.assertFalse(result.iloc[1]['Has_Price'])          # Zero price
        
        # Check completeness scores
        scores = result['Data_Completeness_Score'].tolist()
        self.assertTrue(all(0 <= score <= 100 for score in scores))
        
        # Check quality classifications
        qualities = result['Record_Quality'].tolist()
        valid_qualities = {'Excellent', 'Good', 'Fair', 'Poor'}
        self.assertTrue(all(quality in valid_qualities for quality in qualities))
    
    def test_consolidate_costar_exports(self):
        """Test full consolidation process"""
        # Run consolidation on test files
        result = self.consolidator.consolidate_costar_exports(export_range=(8, 11))
        
        # Check that consolidation was successful
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)
        
        # Check that data from multiple files was consolidated
        source_files = result['Source_File'].unique()
        self.assertGreaterEqual(len(source_files), 2)
        
        # Check that metadata was added
        metadata_columns = ['Source_File', 'Consolidation_Timestamp', 'Data_Completeness_Score']
        for col in metadata_columns:
            self.assertIn(col, result.columns)
        
        # Check deduplication worked (should be fewer rows than sum of inputs)
        total_input_rows = 50 + 75 + 60  # From test files
        self.assertLess(len(result), total_input_rows)
        
        # Check that consolidation stats were generated
        self.assertNotEqual(self.consolidator.consolidation_stats, {})
        self.assertIn('consolidation_timestamp', self.consolidator.consolidation_stats)
    
    def test_consolidation_with_no_files(self):
        """Test consolidation behavior with no files"""
        # Clear the sites directory
        for file in self.sites_dir.glob("*.xlsx"):
            file.unlink()
        
        result = self.consolidator.consolidate_costar_exports()
        self.assertIsNone(result)
    
    def test_consolidation_with_corrupted_file(self):
        """Test consolidation behavior with corrupted file"""
        # Create a corrupted file
        corrupted_file = self.sites_dir / "CostarExport-99.xlsx"
        with open(corrupted_file, 'w') as f:
            f.write("This is not a valid Excel file")
        
        # Should handle the error gracefully
        result = self.consolidator.consolidate_costar_exports(export_range=(8, 100))
        
        # Should still return results from valid files
        if result is not None:
            self.assertIsInstance(result, pd.DataFrame)
    
    def test_data_completeness_scoring(self):
        """Test data completeness scoring logic"""
        # Test with various data completeness scenarios
        test_data = [
            {
                'Property Name': 'Complete Property',
                'Property Address': '123 Main St',
                'City': 'Test City',
                'State': 'CA',
                'For Sale Price': 1000000,
                'expected_score': 100.0
            },
            {
                'Property Name': '',
                'Property Address': '456 Oak Ave', 
                'City': 'Test City',
                'State': 'CA',
                'For Sale Price': 2000000,
                'expected_score': 80.0  # 4/5 fields complete
            },
            {
                'Property Name': 'Incomplete Property',
                'Property Address': '',
                'City': '',
                'State': 'CA',
                'For Sale Price': np.nan,
                'expected_score': 40.0  # 2/5 fields complete
            }
        ]
        
        df = pd.DataFrame(test_data)
        result = self.consolidator.add_consolidation_metadata(df)
        
        for i, expected in enumerate([100.0, 80.0, 40.0]):
            actual_score = result.iloc[i]['Data_Completeness_Score']
            self.assertAlmostEqual(actual_score, expected, places=1)

class TestCoStarConsolidatorIntegration(unittest.TestCase):
    """Integration tests for CoStar consolidation"""
    
    def test_end_to_end_consolidation_workflow(self):
        """Test complete end-to-end consolidation workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sites_path = temp_path / "Sites"
            sites_path.mkdir()
            
            # Create minimal test files
            for i in [8, 9]:
                df = pd.DataFrame({
                    'Property Name': [f'Property_{i}_{j}' for j in range(10)],
                    'Property Address': [f'{j} Street_{i}' for j in range(10)],
                    'For Sale Price': [1000000 + (j * 100000) for j in range(10)],
                    'City': ['Test City'] * 10,
                    'State': ['CA'] * 10
                })
                
                file_path = sites_path / f"CostarExport-{i}.xlsx"
                df.to_excel(file_path, index=False)
            
            # Run consolidation
            consolidator = CoStarConsolidator()
            consolidator.base_path = temp_path
            consolidator.sites_path = sites_path
            
            result = consolidator.consolidate_costar_exports(export_range=(8, 10))
            
            # Verify results
            self.assertIsNotNone(result)
            self.assertEqual(len(result), 20)  # 10 rows from each file
            self.assertIn('Source_File', result.columns)
            self.assertIn('Data_Completeness_Score', result.columns)
            
            # Test save functionality
            output_file = consolidator.save_consolidated_data("test_output.xlsx")
            self.assertIsNotNone(output_file)
            self.assertTrue(output_file.exists())
            
            # Verify saved file can be loaded
            loaded_df = pd.read_excel(output_file, sheet_name='Consolidated_Data')
            self.assertEqual(len(loaded_df), len(result))

def run_tests():
    """Run all consolidation tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCoStarConsolidator))
    suite.addTests(loader.loadTestsFromTestCase(TestCoStarConsolidatorIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)