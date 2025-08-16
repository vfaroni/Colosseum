#!/usr/bin/env python3
"""Debug Excel reading issue"""

import pandas as pd

# Test reading Excel file directly
excel_path = 'test_sites.xlsx'
print(f'Testing direct pandas Excel reading on: {excel_path}')

try:
    df = pd.read_excel(excel_path)
    print(f'Type: {type(df)}')
    print(f'Columns: {df.columns}')
    print(f'Shape: {df.shape}')
    print(f'Data:\n{df}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()