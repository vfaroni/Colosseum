#!/usr/bin/env python3
"""Test script for Excel functionality in SiteDataReader"""

import sys
import logging
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from src.batch.csv_reader import SiteDataReader

def test_excel_reader():
    """Test the Excel functionality in SiteDataReader"""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    reader = SiteDataReader()
    
    # Test Excel file with column mapping
    excel_path = 'test_sites.xlsx'
    print(f'Testing Excel reader with column mapping on: {excel_path}')
    
    try:
        # Test validation
        result = reader.validate_file(excel_path)
        print(f'Validation result: {result}')
        
        if result['valid']:
            # Test loading with column mapping
            sites = reader.load_file(excel_path)
            print(f'Successfully loaded {len(sites)} sites from Excel')
            print('Site data with mapped columns:')
            for i, site in enumerate(sites, 1):
                print(f'  Site {i}: {site}')
                
            # Test that column mapping worked
            expected_columns = {'site_id', 'latitude', 'longitude'}
            for site in sites:
                if not expected_columns.issubset(site.keys()):
                    print(f'ERROR: Missing required columns in site: {site.keys()}')
                else:
                    print(f'✅ Excel column mapping successful for site {site["site_id"]}')
                    
        else:
            print('❌ Excel validation failed')
            for error in result['errors']:
                print(f'   Error: {error}')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_excel_reader()