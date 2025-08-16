#!/usr/bin/env python3
"""
Find and analyze the Development Cost Schedule section
"""

import pandas as pd
import numpy as np

def find_development_cost_section():
    """Find the Development Cost Schedule section"""
    
    df = pd.read_excel('/Users/williamrice/Downloads/25-MFUniformApp-2025-2.xlsx', 
                       sheet_name='REA DATA MASTER', header=None)
    
    print("🔍 SEARCHING FOR DEVELOPMENT COST SCHEDULE")
    print("=" * 60)
    
    # Search for development cost section
    found_sections = []
    
    for j in range(0, df.shape[1]):  # All columns
        for i in range(0, min(100, df.shape[0])):  # First 100 rows
            cell = str(df.iloc[i, j])
            if (cell and cell != 'nan' and len(cell) > 10 and 
                'development' in cell.lower() and 'cost' in cell.lower()):
                
                found_sections.append((i, j, cell))
                print(f"FOUND at Row {i}, Col {j}: {cell}")
                
                # Show context around this location
                print("Context:")
                for row_offset in range(-3, 10):
                    for col_offset in range(0, 6):
                        try:
                            context_row = i + row_offset
                            context_col = j + col_offset
                            if context_row >= 0 and context_col >= 0:
                                context_cell = str(df.iloc[context_row, context_col])
                                if (context_cell and context_cell != 'nan' and 
                                    context_cell != '0' and len(context_cell.strip()) > 0):
                                    print(f"  [{context_row:3d},{context_col:3d}]: {context_cell[:50]}")
                        except IndexError:
                            pass
                print("-" * 40)
    
    if not found_sections:
        print("❌ Development Cost Schedule not found in expected location")
        print("Let me search for 'cost' and 'schedule' separately...")
        
        # Broader search
        cost_mentions = []
        for j in range(0, min(100, df.shape[1])):
            for i in range(0, min(150, df.shape[0])):
                cell = str(df.iloc[i, j])
                if (cell and cell != 'nan' and len(cell) > 8 and 
                    ('cost' in cell.lower() or 'schedule' in cell.lower())):
                    cost_mentions.append((i, j, cell))
        
        print(f"\n📊 Found {len(cost_mentions)} cost/schedule mentions:")
        for i, j, cell in cost_mentions[:20]:  # Show first 20
            print(f"  Row {i:3d}, Col {j:3d}: {cell[:60]}")
    
    return found_sections

def explore_column_ranges():
    """Explore different column ranges to understand layout"""
    
    df = pd.read_excel('/Users/williamrice/Downloads/25-MFUniformApp-2025-2.xlsx', 
                       sheet_name='REA DATA MASTER', header=None)
    
    print("\n🗺️ EXPLORING COLUMN RANGES")
    print("=" * 40)
    
    # Check different column ranges for section headers
    ranges = [
        (0, 30, "Left Section"),
        (30, 60, "Middle-Left Section"),
        (60, 90, "Middle Section"),
        (90, 120, "Middle-Right Section"),
        (120, 150, "Right Section")
    ]
    
    for start_col, end_col, section_name in ranges:
        print(f"\n📋 {section_name} (Columns {start_col}-{end_col}):")
        headers_found = []
        
        for j in range(start_col, min(end_col, df.shape[1])):
            for i in range(0, min(30, df.shape[0])):
                cell = str(df.iloc[i, j])
                if (cell and cell != 'nan' and len(cell) > 15 and 
                    any(keyword in cell.lower() for keyword in 
                        ['schedule', 'cost', 'development', 'sources', 'team', 'site'])):
                    headers_found.append((i, j, cell))
        
        for i, j, cell in headers_found[:5]:  # Show top 5
            print(f"  Row {i:2d}, Col {j:3d}: {cell[:60]}")

if __name__ == "__main__":
    sections = find_development_cost_section()
    explore_column_ranges()