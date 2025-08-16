#!/usr/bin/env python3
"""
Analyze TDHCA Application Template Structure
Map sections and identify high-value data extraction targets
"""

import pandas as pd
import numpy as np

def analyze_tdhca_template():
    """Analyze the TDHCA application template structure"""
    
    print("🔍 ANALYZING TDHCA APPLICATION TEMPLATE")
    print("=" * 60)
    
    # Read the template
    df = pd.read_excel('/Users/williamrice/Downloads/25-MFUniformApp-2025-2.xlsx', 
                       sheet_name='REA DATA MASTER', header=None)
    
    print(f"📊 Template dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
    print()
    
    # Find section headers and major structure
    print("🔍 SEARCHING FOR SECTION HEADERS:")
    print("-" * 40)
    
    section_keywords = [
        'rent schedule', 'utility', 'operating expense', 'development cost', 
        'sources of funds', 'applicant information', 'site information',
        'development narrative', 'team members', 'specifications', 'building'
    ]
    
    sections_found = []
    
    for i in range(0, min(150, df.shape[0])):
        for j in range(0, min(30, df.shape[1])):
            cell = str(df.iloc[i, j])
            if cell and cell != 'nan' and cell != '0' and len(cell) > 5:
                cell_lower = cell.lower()
                for keyword in section_keywords:
                    if keyword in cell_lower:
                        sections_found.append({
                            'row': i,
                            'col': j, 
                            'text': cell[:80],
                            'keyword': keyword
                        })
                        print(f"  Row {i:3d}, Col {j:2d}: {cell[:60]}")
                        break
    
    print()
    print("📋 SECTION ANALYSIS:")
    print("-" * 30)
    
    # Look for financial data patterns
    print("\n💰 FINANCIAL DATA PATTERNS:")
    financial_keywords = ['cost', 'fee', 'total', 'amount', '$', 'expense']
    
    for i in range(0, min(200, df.shape[0])):
        for j in range(0, min(50, df.shape[1])):
            cell = str(df.iloc[i, j])
            if cell and cell != 'nan' and len(cell) > 8:
                cell_lower = cell.lower()
                if any(keyword in cell_lower for keyword in financial_keywords):
                    # Check if it looks like a label (not just data)
                    if ':' in cell or 'total' in cell_lower or 'cost' in cell_lower:
                        print(f"  Row {i:3d}, Col {j:2d}: {cell[:60]}")
    
    print()
    print("🏠 UNIT MIX PATTERNS:")
    unit_keywords = ['bedroom', 'unit', 'sq ft', 'square', 'rent']
    
    for i in range(0, min(100, df.shape[0])):
        for j in range(0, min(30, df.shape[1])):
            cell = str(df.iloc[i, j])
            if cell and cell != 'nan' and len(cell) > 5:
                cell_lower = cell.lower()
                if any(keyword in cell_lower for keyword in unit_keywords):
                    if 'bedroom' in cell_lower or 'unit' in cell_lower:
                        print(f"  Row {i:3d}, Col {j:2d}: {cell[:60]}")
    
    return sections_found

def map_high_value_targets():
    """Map the highest value data extraction targets"""
    
    print("\n🎯 HIGH-VALUE EXTRACTION TARGETS")
    print("=" * 50)
    
    targets = {
        'Financial Data (HIGHEST VALUE)': [
            'Total Development Cost',
            'Construction Cost per Unit',
            'Land Cost per Unit', 
            'Developer Fee Amount',
            'General Contractor Fee',
            'Soft Costs Total'
        ],
        'Unit Mix (HIGH VALUE)': [
            'Studio/Efficiency Units',
            '1-Bedroom Units',
            '2-Bedroom Units', 
            '3-Bedroom Units',
            '4-Bedroom Units',
            'Average Unit Square Footage'
        ],
        'AMI Targeting (MEDIUM VALUE)': [
            '30% AMI Units',
            '50% AMI Units',
            '60% AMI Units',
            '80% AMI Units'
        ],
        'Development Team (MEDIUM VALUE)': [
            'Developer/General Partner',
            'General Contractor',
            'Architect',
            'Management Company'
        ]
    }
    
    for category, fields in targets.items():
        print(f"\n📊 {category}:")
        for field in fields:
            print(f"  • {field}")
    
    print("\n💡 EXTRACTION STRATEGY:")
    print("=" * 30)
    print("1. Focus on Development Cost Schedule section (3 pages)")
    print("2. Extract Unit Mix from Rent Schedule section (2 pages)")
    print("3. Parse Development Team Members section (4-5 pages)")
    print("4. Skip narrative sections entirely")
    print("5. Target structured tables/forms, not free text")

if __name__ == "__main__":
    sections = analyze_tdhca_template()
    map_high_value_targets()