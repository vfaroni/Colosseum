#!/usr/bin/env python3
"""Test script for enhanced SiteDataReader"""

import sys
import logging
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from src.batch.csv_reader import SiteDataReader

def test_enhanced_reader():
    """Test the enhanced SiteDataReader functionality"""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    reader = SiteDataReader()
    
    # Test CSV file with column mapping
    csv_path = 'test_sites.csv'
    print(f'Testing enhanced CSV reader with column mapping on: {csv_path}')
    
    try:
        # Test validation
        result = reader.validate_file(csv_path)
        print(f'Validation result: {result}')
        
        if result['valid']:
            # Test loading with column mapping
            sites = reader.load_file(csv_path)
            print(f'Successfully loaded {len(sites)} sites')
            print('Site data with mapped columns:')
            for i, site in enumerate(sites, 1):
                print(f'  Site {i}: {site}')
                
            # Test that column mapping worked
            expected_columns = {'site_id', 'latitude', 'longitude'}
            for site in sites:
                if not expected_columns.issubset(site.keys()):
                    print(f'ERROR: Missing required columns in site: {site.keys()}')
                else:
                    print(f'✅ Column mapping successful for site {site["site_id"]}')
                    
        else:
            print('❌ Validation failed, not proceeding with load')
            for error in result['errors']:
                print(f'   Error: {error}')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_enhanced_reader()