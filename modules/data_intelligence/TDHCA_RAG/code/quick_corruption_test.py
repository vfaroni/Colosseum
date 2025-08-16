#!/usr/bin/env python3
"""
Quick test: Can we open the 7 failed PDFs?
"""

import PyPDF2
from pathlib import Path

def test_pdf_basic(pdf_path):
    """Quick test if PDF can be opened"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            return f"✅ READABLE ({num_pages} pages)"
    except Exception as e:
        return f"❌ CORRUPTED: {str(e)[:50]}"

def main():
    # Failed files
    failed_files = [
        ("TDHCA_23444_Tobias_Place.pdf", "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_2023_Applications/Dallas_Fort_Worth/TDHCA_23444_Tobias_Place.pdf"),
        ("TDHCA_23403_Cattleman_Square.pdf", "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_2023_Applications/San_Antonio/TDHCA_23403_Cattleman_Square.pdf"),
        ("25447.pdf", "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_Applications_Benchmarks/Dallas_FW_Priority_2/TDHCA_25447_Columbia_Renaissance_Square/25447.pdf"),
        ("25409.pdf", "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_Applications_Benchmarks/Houston_Priority_1/TDHCA_25409_Lancaster_Apartments/25409.pdf"),
        ("25410.pdf", "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_Applications_Benchmarks/Houston_Priority_1/TDHCA_25410_Regency_Park/25410.pdf"),
        ("25411.pdf", "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_Applications_Benchmarks/Houston_Priority_1/TDHCA_25411_Sugar_Creek/25411.pdf"),
        ("25449.pdf", "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_Applications_Benchmarks/Houston_Priority_1/TDHCA_25449_Enclave_on_Louetta/25449.pdf")
    ]
    
    print("🔍 QUICK CORRUPTION TEST - 7 Failed Files")
    print("=" * 60)
    
    corrupted_count = 0
    readable_count = 0
    
    for i, (filename, filepath) in enumerate(failed_files, 1):
        status = test_pdf_basic(filepath)
        print(f"{i}. {filename}")
        print(f"   {status}")
        
        if "CORRUPTED" in status:
            corrupted_count += 1
        else:
            readable_count += 1
    
    print()
    print("SUMMARY:")
    print(f"✅ Readable PDFs: {readable_count}")
    print(f"❌ Corrupted PDFs: {corrupted_count}")
    print()
    if readable_count > 0:
        print("✨ Good news: Some 'failed' files are actually readable!")
        print("   → These can likely be fixed with improved extraction patterns")
    if corrupted_count > 0:
        print("💀 Bad news: Some files are truly corrupted")
        print("   → These may need to be redownloaded from TDHCA")

if __name__ == "__main__":
    main()