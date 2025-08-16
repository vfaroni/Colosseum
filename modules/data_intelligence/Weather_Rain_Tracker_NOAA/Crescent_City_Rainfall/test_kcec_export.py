#!/usr/bin/env python3
"""
Test script for KCEC Excel Export
Automatically exports existing complete dataset to Excel format for testing
"""

from kcec_excel_export import KCECExcelExporter

def test_export():
    """Test the Excel export functionality"""
    print("Testing KCEC Excel Export...")
    
    exporter = KCECExcelExporter()
    
    # Export existing complete dataset
    print("Exporting existing complete dataset to Excel format...")
    output_file = exporter.create_excel_format_export()
    
    if output_file:
        print(f"\nSUCCESS: Excel export created at {output_file}")
        return output_file
    else:
        print("ERROR: Failed to create Excel export")
        return None

if __name__ == "__main__":
    test_export()