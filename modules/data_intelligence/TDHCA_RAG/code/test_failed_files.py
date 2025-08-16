#!/usr/bin/env python3
"""
Test the 7 failed files to determine:
1. Are they actually corrupted (can't read PDF)?
2. Can we extract data with improved patterns?
3. What specific errors are we hitting?
"""

import PyPDF2
from pathlib import Path
from improved_tdhca_extractor import ImprovedTDHCAExtractor
from datetime import datetime

def test_pdf_readability(pdf_path):
    """Test if PDF can be opened and read"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            
            # Try to read first page
            first_page = reader.pages[0]
            text_sample = first_page.extract_text()[:200]
            
            return {
                'readable': True,
                'pages': num_pages,
                'sample_text': text_sample,
                'error': None
            }
    except Exception as e:
        return {
            'readable': False,
            'pages': 0,
            'sample_text': '',
            'error': str(e)
        }

def test_improved_extraction(pdf_path, extractor):
    """Test if improved extractor can handle the file"""
    try:
        result = extractor.process_application_improved(pdf_path)
        if result:
            return {
                'success': True,
                'project_name': result.project_name,
                'county': result.county,
                'address': f"{result.street_address}, {result.city} {result.zip_code}",
                'units': result.total_units,
                'confidence': result.confidence_scores.get('overall', 0),
                'error': None
            }
        else:
            return {
                'success': False,
                'error': 'No result returned'
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    # Failed files from our analysis
    failed_files = [
        "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_2023_Applications/Dallas_Fort_Worth/TDHCA_23444_Tobias_Place.pdf",
        "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_2023_Applications/San_Antonio/TDHCA_23403_Cattleman_Square.pdf",
        "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_Applications_Benchmarks/Dallas_FW_Priority_2/TDHCA_25447_Columbia_Renaissance_Square/25447.pdf",
        "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_Applications_Benchmarks/Houston_Priority_1/TDHCA_25409_Lancaster_Apartments/25409.pdf",
        "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_Applications_Benchmarks/Houston_Priority_1/TDHCA_25410_Regency_Park/25410.pdf",
        "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_Applications_Benchmarks/Houston_Priority_1/TDHCA_25411_Sugar_Creek/25411.pdf",
        "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_Applications_Benchmarks/Houston_Priority_1/TDHCA_25449_Enclave_on_Louetta/25449.pdf"
    ]
    
    # Create extractor
    extractor = ImprovedTDHCAExtractor("")
    
    # Create output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"failed_files_analysis_{timestamp}.txt"
    
    print(f"🔍 ANALYZING 7 FAILED FILES")
    print("=" * 60)
    print("Testing PDF readability and improved extraction")
    print()
    
    results = []
    
    with open(output_file, 'w') as f:
        f.write(f"Failed Files Analysis - {datetime.now()}\n")
        f.write("=" * 80 + "\n\n")
        
        for i, file_path in enumerate(failed_files, 1):
            file_name = Path(file_path).name
            print(f"{i}. Testing {file_name}")
            f.write(f"{i}. FILE: {file_name}\n")
            f.write("-" * 50 + "\n")
            
            # Test PDF readability first
            pdf_test = test_pdf_readability(file_path)
            f.write(f"PDF Readability: {'✅ READABLE' if pdf_test['readable'] else '❌ CORRUPTED'}\n")
            
            if pdf_test['readable']:
                f.write(f"Pages: {pdf_test['pages']}\n")
                f.write(f"Sample Text: {pdf_test['sample_text'][:100]}...\n")
                print(f"   ✅ PDF readable ({pdf_test['pages']} pages)")
                
                # Test improved extraction
                extraction_test = test_improved_extraction(Path(file_path), extractor)
                f.write(f"Improved Extraction: {'✅ SUCCESS' if extraction_test['success'] else '❌ FAILED'}\n")
                
                if extraction_test['success']:
                    f.write(f"Project Name: '{extraction_test['project_name']}'\n")
                    f.write(f"County: '{extraction_test['county']}'\n") 
                    f.write(f"Address: '{extraction_test['address']}'\n")
                    f.write(f"Units: {extraction_test['units']}\n")
                    f.write(f"Confidence: {extraction_test['confidence']:.2f}\n")
                    print(f"   ✅ Extraction successful: {extraction_test['project_name']}")
                    
                    results.append({
                        'file': file_name,
                        'status': 'FIXED',
                        'project_name': extraction_test['project_name']
                    })
                else:
                    f.write(f"Extraction Error: {extraction_test['error']}\n")
                    print(f"   ❌ Extraction failed: {extraction_test['error'][:50]}...")
                    
                    results.append({
                        'file': file_name,
                        'status': 'EXTRACTION_FAILED',
                        'error': extraction_test['error']
                    })
            else:
                f.write(f"PDF Error: {pdf_test['error']}\n")
                print(f"   ❌ PDF corrupted: {pdf_test['error'][:50]}...")
                
                results.append({
                    'file': file_name,
                    'status': 'CORRUPTED',
                    'error': pdf_test['error']
                })
            
            f.write("\n")
            print()
        
        # Summary
        f.write("SUMMARY\n")
        f.write("=" * 30 + "\n")
        
        corrupted = [r for r in results if r['status'] == 'CORRUPTED']
        fixed = [r for r in results if r['status'] == 'FIXED']
        still_failed = [r for r in results if r['status'] == 'EXTRACTION_FAILED']
        
        f.write(f"✅ Fixed with improved patterns: {len(fixed)}\n")
        f.write(f"❌ Still failing extraction: {len(still_failed)}\n")
        f.write(f"💀 Actually corrupted: {len(corrupted)}\n")
        
        if fixed:
            f.write("\nFIXED FILES:\n")
            for r in fixed:
                f.write(f"- {r['file']}: {r['project_name']}\n")
        
        if corrupted:
            f.write("\nCORRUPTED FILES:\n")
            for r in corrupted:
                f.write(f"- {r['file']}: {r['error'][:50]}...\n")
    
    print(f"📄 Analysis saved to: {output_file}")
    print()
    print("SUMMARY:")
    print(f"✅ Fixed: {len(fixed)}")
    print(f"❌ Still failing: {len(still_failed)}")
    print(f"💀 Corrupted: {len(corrupted)}")

if __name__ == "__main__":
    main()