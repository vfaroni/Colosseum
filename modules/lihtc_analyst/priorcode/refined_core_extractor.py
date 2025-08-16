#!/usr/bin/env python3
"""
Refined Core Extractor - Perfect unit mix + financial extraction
Uses exact cell ranges we identified from manual inspection
"""

import xlwings as xw
from pathlib import Path
import time

def test_refined_extraction():
    """Test refined extraction with exact cell ranges"""
    
    print("🎯 REFINED CORE EXTRACTION - 2025 4%")
    print("Using exact cell ranges from manual inspection")
    print("=" * 60)
    
    # Test file
    test_file = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data/2025_4pct_R1_25-464.xlsx")
    
    app = None
    wb = None
    
    try:
        # Open Excel
        app = xw.App(visible=False, add_book=False)
        app.display_alerts = False
        app.screen_updating = False
        
        wb = app.books.open(str(test_file), read_only=True, update_links=False)
        
        # 1. UNIT MIX - Using exact ranges we found
        print(f"\n🏠 UNIT MIX EXTRACTION (Rows 717-718):")
        unit_data = extract_precise_unit_mix(wb)
        
        # 2. SOURCES & USES - Already working
        print(f"\n💰 SOURCES & USES VALIDATION:")
        financial_data = validate_sources_uses(wb)
        
        # 3. PROJECT TOTALS - From known locations
        print(f"\n📊 PROJECT TOTALS:")
        totals_data = extract_project_totals(wb)
        
        # 4. CREATE FINAL SUMMARY TABLE
        print(f"\n📋 FINAL EXTRACTION RESULTS:")
        create_summary_table(unit_data, financial_data, totals_data)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        if wb: wb.close()
        if app: app.quit()
        print(f"\n🔄 Excel cleaned up")

def extract_precise_unit_mix(workbook):
    """Extract unit mix using exact cell positions we identified"""
    
    app_sheet = None
    for sheet in workbook.sheets:
        if sheet.name == 'Application':
            app_sheet = sheet
            break
    
    if not app_sheet:
        print("   ❌ Application sheet not found")
        return []
    
    unit_data = []
    
    try:
        # Row 717: 1 Bedroom, 41 units, 540 sq ft, $770 rent, $55 utility
        row717 = app_sheet.range("A717:U717").value
        if row717 and len(row717) > 15:
            # Extract from known positions (adjusted based on our manual inspection)
            unit1 = {
                'unit_type': str(row717[1]) if row717[1] else 'Unknown',  # Col B
                'unit_count': int(row717[6]) if row717[6] else 0,          # Col G  
                'avg_sqft': int(row717[10]) if row717[10] else 0,          # Col K
                'gross_rent': int(row717[14]) if row717[14] else 0,        # Col O
                'utility_allowance': int(row717[18]) if row717[18] else 55, # Col S (utility column)
                'ami_level': '60% AMI',  # $770 rent suggests income-restricted
                'row_source': 717
            }
            
            if unit1['unit_count'] > 0:
                unit_data.append(unit1)
                print(f"   ✅ {unit1['unit_type']}: {unit1['unit_count']} units @ ${unit1['gross_rent']} (60% AMI)")
        
        # Row 718: 1 Bedroom, 42 units, 540 sq ft, $1596 rent, $55 utility  
        row718 = app_sheet.range("A718:U718").value
        if row718 and len(row718) > 15:
            unit2 = {
                'unit_type': str(row718[1]) if row718[1] else 'Unknown',
                'unit_count': int(row718[6]) if row718[6] else 0,
                'avg_sqft': int(row718[10]) if row718[10] else 0, 
                'gross_rent': int(row718[14]) if row718[14] else 0,
                'utility_allowance': int(row718[18]) if row718[18] else 55,
                'ami_level': 'Market Rate',  # $1596 rent indicates market rate
                'row_source': 718
            }
            
            if unit2['unit_count'] > 0:
                unit_data.append(unit2)
                print(f"   ✅ {unit2['unit_type']}: {unit2['unit_count']} units @ ${unit2['gross_rent']} (Market)")
        
        # Verify total units matches known total (83)
        total_extracted = sum(unit['unit_count'] for unit in unit_data)
        print(f"   📊 Total units extracted: {total_extracted}")
        
        return unit_data
        
    except Exception as e:
        print(f"   ❌ Unit extraction error: {e}")
        return []

def validate_sources_uses(workbook):
    """Validate Sources & Uses extraction (already working)"""
    
    su_sheet = None
    for sheet in workbook.sheets:
        if 'Sources and Uses Budget' in sheet.name:
            su_sheet = sheet
            break
    
    if not su_sheet:
        print("   ❌ Sources & Uses sheet not found")
        return None
    
    try:
        # Sample key cost lines
        line_items = su_sheet.range("A4:A20").value
        total_costs = su_sheet.range("B4:B20").value
        
        # Filter valid costs
        valid_costs = [cost for cost in total_costs if cost and isinstance(cost, (int, float)) and cost > 0]
        sample_total = sum(valid_costs)
        
        print(f"   ✅ Sample costs (first 16 lines): ${sample_total:,.0f}")
        print(f"   📋 Valid cost entries: {len(valid_costs)}")
        
        return {
            'sample_total': sample_total,
            'valid_entries': len(valid_costs)
        }
        
    except Exception as e:
        print(f"   ❌ Sources & Uses validation error: {e}")
        return None

def extract_project_totals(workbook):
    """Extract project totals from known locations"""
    
    app_sheet = None
    for sheet in workbook.sheets:
        if sheet.name == 'Application':
            app_sheet = sheet
            break
    
    if not app_sheet:
        return {}
    
    try:
        # Row 752: Total # Units: 83 (check wider range)
        row752 = app_sheet.range("A752:H752").value
        total_units = 0
        
        if row752:
            for i, cell in enumerate(row752):
                if isinstance(cell, (int, float)) and 50 <= cell <= 200:
                    total_units = int(cell)
                    print(f"   📍 Found total at position {i}: {total_units}")
                    break
        
        print(f"   ✅ Total units (Row 752): {total_units}")
        
        return {
            'total_units': total_units,
            'extraction_source': 'Row 752'
        }
        
    except Exception as e:
        print(f"   ❌ Project totals error: {e}")
        return {}

def create_summary_table(unit_data, financial_data, totals_data):
    """Create final summary table for user review"""
    
    print(f"\n🏠 FINAL UNIT MIX TABLE:")
    print("Unit Type         | Unit Count | AMI Level    | Gross Rent | Utility Allow | Net Rent")
    print("-" * 80)
    
    total_units = 0
    total_affordable = 0
    
    for unit in unit_data:
        net_rent = unit['gross_rent'] - unit['utility_allowance']
        print(f"{unit['unit_type']:17s} | {unit['unit_count']:10d} | {unit['ami_level']:12s} | ${unit['gross_rent']:9d} | ${unit['utility_allowance']:12d} | ${net_rent:8d}")
        
        total_units += unit['unit_count']
        if unit['ami_level'] != 'Market Rate':
            total_affordable += unit['unit_count']
    
    print("-" * 80)
    print(f"{'TOTALS':17s} | {total_units:10d} | {'Mixed':12s} | {'Varies':>10s} | {'$55':>12s} | {'Varies':>8s}")
    
    # Validation
    expected_total = totals_data.get('total_units', 0)
    validation = "✅" if total_units == expected_total else "⚠️"
    
    print(f"\n📊 VALIDATION:")
    print(f"   {validation} Extracted units: {total_units} vs Expected: {expected_total}")
    print(f"   🏠 Affordable units: {total_affordable} ({total_affordable/total_units*100:.1f}%)")
    print(f"   💰 Financial data: {'✅' if financial_data else '❌'}")
    
    return {
        'unit_data': unit_data,
        'total_units': total_units,
        'affordable_units': total_affordable,
        'validation_passed': total_units == expected_total
    }

if __name__ == "__main__":
    test_refined_extraction()