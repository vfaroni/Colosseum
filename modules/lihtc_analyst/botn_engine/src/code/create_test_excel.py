#!/usr/bin/env python3
"""Create a test Excel file for testing enhanced SiteDataReader"""

import pandas as pd

# Create test data with column variations
data = {
    'property_id': ['EXCEL001', 'EXCEL002', 'EXCEL003'],
    'lat': [37.7749, 34.0522, 32.7157],
    'lng': [-122.4194, -118.2437, -117.1611],
    'property_address': ['San Francisco, CA', 'Los Angeles, CA', 'San Diego, CA'],
    'comments': ['Urban site', 'High density area', 'Coastal location']
}

df = pd.DataFrame(data)

# Save as Excel file
excel_path = 'test_sites.xlsx'
df.to_excel(excel_path, index=False)
print(f'Created test Excel file: {excel_path}')
print(f'Columns: {list(df.columns)}')
print(f'Rows: {len(df)}')