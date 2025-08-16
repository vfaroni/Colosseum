#!/usr/bin/env python3
"""
PDF Diagnostics - Analyze and fix problematic PDFs in QAP database
Handles encrypted, corrupted, and malformed PDF files

Built by Structured Consultants LLC
Roman Engineering Standards: Built to Last 2000+ Years
"""

import os
import sys
from pathlib import Path
import PyPDF2
import logging
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFDiagnostics:
    """Comprehensive PDF diagnostics and repair utility"""
    
    def __init__(self):
        self.error_categories = {
            'encrypted': [],
            'corrupted': [],
            'malformed': [],
            'permission_denied': [],
            'unknown': []
        }
    
    def diagnose_pdf(self, pdf_path: str) -> Dict:
        """Comprehensive PDF diagnosis"""
        pdf_path = Path(pdf_path)
        
        result = {
            'file_path': str(pdf_path),
            'file_name': pdf_path.name,
            'file_size_mb': 0,
            'exists': False,
            'readable': False,
            'pages': None,
            'encrypted': False,
            'error_type': None,
            'error_message': None,
            'repair_suggestions': []
        }
        
        # Check if file exists
        if not pdf_path.exists():
            result['error_type'] = 'file_not_found'
            result['error_message'] = 'File does not exist'
            result['repair_suggestions'] = ['Re-download from source', 'Check file path']
            return result
        
        result['exists'] = True
        result['file_size_mb'] = round(pdf_path.stat().st_size / (1024 * 1024), 2)
        
        # Attempt to read PDF
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if encrypted
                if pdf_reader.is_encrypted:
                    result['encrypted'] = True
                    result['error_type'] = 'encrypted'
                    result['error_message'] = 'PDF is password protected'
                    result['repair_suggestions'] = [
                        'Try empty password',
                        'Contact source for password',
                        'Use PDF decryption tool',
                        'Re-download unencrypted version'
                    ]
                    
                    # Try to decrypt with empty password
                    try:
                        pdf_reader.decrypt('')
                        result['pages'] = len(pdf_reader.pages)
                        result['readable'] = True
                        result['repair_suggestions'] = ['PDF decrypted with empty password - processable']
                    except:
                        pass
                
                else:
                    # Not encrypted, try to count pages
                    result['pages'] = len(pdf_reader.pages)
                    result['readable'] = True
                    
                    # Additional checks
                    if result['pages'] == 0:
                        result['error_type'] = 'empty'
                        result['error_message'] = 'PDF has no pages'
                        result['repair_suggestions'] = ['Re-download from source', 'Check if file is corrupted']
                
        except Exception as e:
            error_str = str(e).lower()
            result['error_message'] = str(e)
            
            # Categorize error types
            if 'pycryptodome' in error_str or 'aes' in error_str:
                result['error_type'] = 'encryption_library'
                result['repair_suggestions'] = [
                    'PyCryptodome installed - should work now',
                    'Retry PDF processing'
                ]
            elif 'eof marker not found' in error_str:
                result['error_type'] = 'corrupted'
                result['repair_suggestions'] = [
                    'PDF file is corrupted',
                    'Re-download from original source',
                    'Try PDF repair tool',
                    'Contact data provider'
                ]
            elif 'permission denied' in error_str:
                result['error_type'] = 'permission_denied'
                result['repair_suggestions'] = [
                    'Check file permissions',
                    'Run with appropriate privileges'
                ]
            else:
                result['error_type'] = 'unknown'
                result['repair_suggestions'] = [
                    'Unknown PDF error',
                    'Try alternative PDF reader',
                    'Re-download from source'
                ]
        
        return result
    
    def batch_diagnose(self, pdf_paths: List[str]) -> Dict:
        """Diagnose multiple PDFs and categorize issues"""
        
        results = {
            'total_files': len(pdf_paths),
            'categories': {
                'readable': [],
                'encrypted': [],
                'corrupted': [],
                'missing': [],
                'unknown_error': []
            },
            'detailed_results': []
        }
        
        for pdf_path in pdf_paths:
            logger.info(f"Diagnosing: {Path(pdf_path).name}")
            diagnosis = self.diagnose_pdf(pdf_path)
            results['detailed_results'].append(diagnosis)
            
            # Categorize
            if not diagnosis['exists']:
                results['categories']['missing'].append(diagnosis)
            elif diagnosis['readable']:
                results['categories']['readable'].append(diagnosis)
            elif diagnosis['error_type'] == 'encrypted':
                results['categories']['encrypted'].append(diagnosis)
            elif diagnosis['error_type'] == 'corrupted':
                results['categories']['corrupted'].append(diagnosis)
            else:
                results['categories']['unknown_error'].append(diagnosis)
        
        return results
    
    def generate_repair_report(self, batch_results: Dict) -> str:
        """Generate detailed repair recommendations"""
        
        report = f"""PDF DIAGNOSTICS AND REPAIR REPORT
=================================
Total Files Analyzed: {batch_results['total_files']}

SUMMARY:
- Readable: {len(batch_results['categories']['readable'])}
- Encrypted: {len(batch_results['categories']['encrypted'])}
- Corrupted: {len(batch_results['categories']['corrupted'])}
- Missing: {len(batch_results['categories']['missing'])}
- Unknown Errors: {len(batch_results['categories']['unknown_error'])}

"""
        
        # Encrypted PDFs
        if batch_results['categories']['encrypted']:
            report += "\n🔒 ENCRYPTED PDFs:\n"
            for pdf in batch_results['categories']['encrypted']:
                report += f"- {pdf['file_name']} ({pdf['file_size_mb']} MB)\n"
                report += f"  Error: {pdf['error_message']}\n"
                report += f"  Suggestions: {', '.join(pdf['repair_suggestions'])}\n\n"
        
        # Corrupted PDFs
        if batch_results['categories']['corrupted']:
            report += "\n💀 CORRUPTED PDFs (Need Re-download):\n"
            for pdf in batch_results['categories']['corrupted']:
                report += f"- {pdf['file_name']} ({pdf['file_size_mb']} MB)\n"
                report += f"  Error: {pdf['error_message']}\n"
                report += f"  Location: {Path(pdf['file_path']).parent}\n\n"
        
        # Missing PDFs
        if batch_results['categories']['missing']:
            report += "\n❌ MISSING PDFs:\n"
            for pdf in batch_results['categories']['missing']:
                report += f"- {pdf['file_name']}\n"
                report += f"  Path: {pdf['file_path']}\n\n"
        
        # Unknown errors
        if batch_results['categories']['unknown_error']:
            report += "\n❓ UNKNOWN ERRORS:\n"
            for pdf in batch_results['categories']['unknown_error']:
                report += f"- {pdf['file_name']} ({pdf['file_size_mb']} MB)\n"
                report += f"  Error: {pdf['error_message']}\n"
                report += f"  Suggestions: {', '.join(pdf['repair_suggestions'])}\n\n"
        
        # Successfully readable
        if batch_results['categories']['readable']:
            report += f"\n✅ READABLE PDFs ({len(batch_results['categories']['readable'])}):\n"
            for pdf in batch_results['categories']['readable']:
                report += f"- {pdf['file_name']}: {pdf['pages']} pages ({pdf['file_size_mb']} MB)\n"
        
        return report

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python3 pdf_diagnostics.py <pdf_file_or_directory>")
        print("Examples:")
        print("  python3 pdf_diagnostics.py problem_document.pdf")
        print("  python3 pdf_diagnostics.py ../../data_sets/QAP/")
        sys.exit(1)
    
    path = sys.argv[1]
    diagnostics = PDFDiagnostics()
    
    if os.path.isfile(path) and path.endswith('.pdf'):
        # Single file mode
        print(f"\nDiagnosing PDF: {Path(path).name}")
        result = diagnostics.diagnose_pdf(path)
        
        print(f"\nFile: {result['file_name']}")
        print(f"Size: {result['file_size_mb']} MB")
        print(f"Pages: {result['pages']}")
        print(f"Readable: {result['readable']}")
        print(f"Encrypted: {result['encrypted']}")
        
        if result['error_type']:
            print(f"Error Type: {result['error_type']}")
            print(f"Error: {result['error_message']}")
            print(f"Repair Suggestions:")
            for suggestion in result['repair_suggestions']:
                print(f"  - {suggestion}")
        else:
            print("✅ PDF is healthy and readable")
            
    elif os.path.isdir(path):
        # Directory mode - find all PDFs
        pdf_files = list(Path(path).glob("**/*.pdf"))
        print(f"\nFound {len(pdf_files)} PDF files to diagnose")
        
        results = diagnostics.batch_diagnose([str(f) for f in pdf_files])
        report = diagnostics.generate_repair_report(results)
        
        print(report)
        
        # Save report to file
        report_file = Path(path) / "pdf_diagnostics_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\nDiagnostics report saved to: {report_file}")
        
    else:
        print(f"Error: {path} is not a valid PDF file or directory")
        sys.exit(1)

if __name__ == "__main__":
    main()