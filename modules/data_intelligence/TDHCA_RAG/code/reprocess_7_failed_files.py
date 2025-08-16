#!/usr/bin/env python3
"""
Reprocess the 7 Failed Files with Improved Extractor
All files are valid PDFs - should succeed with enhanced patterns
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from improved_tdhca_extractor import ImprovedTDHCAExtractor

def main():
    print("🔄 REPROCESSING 7 FAILED FILES")
    print("=" * 60)
    print("Using improved extractor with critical fixes:")
    print("✅ County extraction (ZIP-to-county mapping)")
    print("✅ Project name patterns (exclude generic text)")
    print("✅ Better address parsing")
    print("✅ Improved unit count extraction")
    print()
    
    # The 7 files that failed in batch processing
    failed_files = [
        {
            'name': 'TDHCA_23444_Tobias_Place.pdf',
            'path': '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D\'Marco_Sites/Successful_2023_Applications/Dallas_Fort_Worth/TDHCA_23444_Tobias_Place.pdf',
            'expected_project': 'Tobias Place'
        },
        {
            'name': 'TDHCA_23403_Cattleman_Square.pdf', 
            'path': '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D\'Marco_Sites/Successful_2023_Applications/San_Antonio/TDHCA_23403_Cattleman_Square.pdf',
            'expected_project': 'Cattleman Square'
        },
        {
            'name': '25447.pdf',
            'path': '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D\'Marco_Sites/Successful_Applications_Benchmarks/Dallas_FW_Priority_2/TDHCA_25447_Columbia_Renaissance_Square/25447.pdf',
            'expected_project': 'Columbia Renaissance Square'
        },
        {
            'name': '25409.pdf',
            'path': '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D\'Marco_Sites/Successful_Applications_Benchmarks/Houston_Priority_1/TDHCA_25409_Lancaster_Apartments/25409.pdf',
            'expected_project': 'Lancaster Apartments'
        },
        {
            'name': '25410.pdf',
            'path': '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D\'Marco_Sites/Successful_Applications_Benchmarks/Houston_Priority_1/TDHCA_25410_Regency_Park/25410.pdf',
            'expected_project': 'Regency Park'
        },
        {
            'name': '25411.pdf',
            'path': '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D\'Marco_Sites/Successful_Applications_Benchmarks/Houston_Priority_1/TDHCA_25411_Sugar_Creek/25411.pdf',
            'expected_project': 'Sugar Creek'
        },
        {
            'name': '25449.pdf',
            'path': '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D\'Marco_Sites/Successful_Applications_Benchmarks/Houston_Priority_1/TDHCA_25449_Enclave_on_Louetta/25449.pdf',
            'expected_project': 'Enclave on Louetta'
        }
    ]
    
    # Initialize improved extractor
    extractor = ImprovedTDHCAExtractor("")
    
    # Results storage
    results = []
    success_count = 0
    
    # Create timestamp for output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"🚀 Starting reprocessing of {len(failed_files)} files...")
    print()
    
    for i, file_info in enumerate(failed_files, 1):
        filename = file_info['name']
        filepath = file_info['path']
        expected = file_info['expected_project']
        
        print(f"{i}/7 Processing {filename}")
        print(f"    Expected: {expected}")
        
        try:
            # Process with improved extractor
            result = extractor.process_application_improved(Path(filepath))
            
            if result and result.project_name:
                success_count += 1
                print(f"    ✅ SUCCESS: '{result.project_name}'")
                print(f"    📍 Address: {result.street_address}, {result.city} {result.zip_code}")
                print(f"    🏛️ County: {result.county}")
                print(f"    🏢 Units: {result.total_units}")
                print(f"    📊 Confidence: {result.confidence_scores.get('overall', 0):.2f}")
                
                # Store result
                result_data = {
                    'filename': filename,
                    'status': 'SUCCESS',
                    'project_name': result.project_name,
                    'street_address': result.street_address,
                    'city': result.city,
                    'zip_code': result.zip_code,
                    'county': result.county,
                    'total_units': result.total_units,
                    'developer_name': result.developer_name,
                    'urban_rural': result.urban_rural,
                    'hud_qct_status': result.hud_qct_status,
                    'hud_dda_status': result.hud_dda_status,
                    'latitude': result.latitude,
                    'longitude': result.longitude,
                    'confidence_overall': result.confidence_scores.get('overall', 0),
                    'processing_notes': '; '.join(result.processing_notes),
                    'expected_name': expected,
                    'name_match': expected.lower() in result.project_name.lower()
                }
                results.append(result_data)
                
            else:
                print(f"    ❌ FAILED: No data extracted")
                results.append({
                    'filename': filename,
                    'status': 'FAILED',
                    'error': 'No data extracted',
                    'expected_name': expected
                })
                
        except Exception as e:
            print(f"    💥 ERROR: {str(e)[:60]}...")
            results.append({
                'filename': filename,
                'status': 'ERROR', 
                'error': str(e),
                'expected_name': expected
            })
        
        print()
    
    # Save results
    print("💾 SAVING RESULTS")
    print("=" * 30)
    
    # Save JSON results
    json_file = f"reprocessed_7_files_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"📄 JSON results saved: {json_file}")
    
    # Save Excel results
    df = pd.DataFrame(results)
    excel_file = f"reprocessed_7_files_{timestamp}.xlsx"
    df.to_excel(excel_file, index=False)
    print(f"📊 Excel results saved: {excel_file}")
    
    # Summary
    print()
    print("📈 FINAL SUMMARY")
    print("=" * 30)
    print(f"✅ Successfully processed: {success_count}/7 files ({success_count/7*100:.1f}%)")
    print(f"❌ Still failed: {7-success_count}/7 files")
    
    if success_count > 0:
        print()
        print("🎉 RECOVERED FILES:")
        for result in results:
            if result['status'] == 'SUCCESS':
                match_indicator = "✅" if result.get('name_match', False) else "⚠️"
                print(f"  {match_indicator} {result['filename']}: {result['project_name']}")
    
    if success_count < 7:
        print()
        print("🔍 STILL FAILING:")
        for result in results:
            if result['status'] != 'SUCCESS':
                print(f"  ❌ {result['filename']}: {result.get('error', 'Unknown error')}")
    
    print()
    print(f"🎯 IMPACT: Improved success rate from 84.2% to {(32+success_count)/38*100:.1f}%")
    print(f"📊 Total successful extractions: {32+success_count}/38")

if __name__ == "__main__":
    main()