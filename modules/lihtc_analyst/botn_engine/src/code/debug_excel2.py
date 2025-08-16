#!/usr/bin/env python3
"""Debug Excel reading issue - check sheet names"""

import pandas as pd

# Test reading Excel file with different parameters
excel_path = 'test_sites.xlsx'
print(f'Testing Excel reading variations on: {excel_path}')

try:
    # Method 1: Default read
    print("\n1. Default read_excel:")
    result1 = pd.read_excel(excel_path)
    print(f'Type: {type(result1)}')
    if isinstance(result1, pd.DataFrame):
        print(f'Shape: {result1.shape}')
        print(f'Columns: {list(result1.columns)}')
    else:
        print(f'Result: {result1}')
    
    # Method 2: Specify sheet_name=None (returns dict of all sheets)
    print("\n2. read_excel with sheet_name=None:")
    result2 = pd.read_excel(excel_path, sheet_name=None)
    print(f'Type: {type(result2)}')
    print(f'Content: {result2}')
    
    # Method 3: Specify sheet_name=0 (first sheet)
    print("\n3. read_excel with sheet_name=0:")
    result3 = pd.read_excel(excel_path, sheet_name=0)
    print(f'Type: {type(result3)}')
    if isinstance(result3, pd.DataFrame):
        print(f'Shape: {result3.shape}')
        print(f'Columns: {list(result3.columns)}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()