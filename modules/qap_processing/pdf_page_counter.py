#!/usr/bin/env python3
"""
PDF Page Counter - Detects documents over 100 pages before Claude API processing
Part of Colosseum QAP RAG system emergency patch

Built by Structured Consultants LLC
Roman Engineering Standards: Built to Last 2000+ Years
"""

import os
import sys
from pathlib import Path
import PyPDF2
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFPageCounter:
    """Utility to count PDF pages and check Claude API compatibility"""
    
    def __init__(self):
        self.max_pages = 100  # Claude API limit
        
    def count_pages(self, pdf_path):
        """Count pages in a PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                return page_count
        except Exception as e:
            logger.error(f"Error counting pages in {pdf_path}: {str(e)}")
            return None
    
    def check_claude_compatibility(self, pdf_path):
        """Check if PDF is compatible with Claude API (<=100 pages)"""
        page_count = self.count_pages(pdf_path)
        if page_count is None:
            return False, None, "Error reading PDF"
        
        is_compatible = page_count <= self.max_pages
        status = "COMPATIBLE" if is_compatible else "NEEDS_SPLITTING"
        message = f"{page_count} pages - {status}"
        
        return is_compatible, page_count, message
    
    def scan_directory(self, directory_path):
        """Scan directory for PDFs and check compatibility"""
        results = []
        pdf_files = list(Path(directory_path).glob("**/*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files in {directory_path}")
        
        for pdf_file in pdf_files:
            is_compatible, page_count, message = self.check_claude_compatibility(pdf_file)
            results.append({
                'file': str(pdf_file),
                'compatible': is_compatible,
                'pages': page_count,
                'status': message
            })
            
            # Log incompatible files
            if not is_compatible and page_count:
                logger.warning(f"NEEDS SPLITTING: {pdf_file.name} ({page_count} pages)")
        
        return results
    
    def generate_report(self, results):
        """Generate compatibility report"""
        compatible_count = sum(1 for r in results if r['compatible'])
        needs_splitting = sum(1 for r in results if not r['compatible'] and r['pages'])
        error_count = sum(1 for r in results if r['pages'] is None)
        
        report = f"""
PDF COMPATIBILITY REPORT
========================
Total PDFs scanned: {len(results)}
Compatible with Claude API: {compatible_count}
Need splitting (>100 pages): {needs_splitting}
Errors reading: {error_count}

FILES NEEDING SPLITTING:
"""
        
        for result in results:
            if not result['compatible'] and result['pages']:
                report += f"- {Path(result['file']).name}: {result['pages']} pages\n"
        
        return report

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python3 pdf_page_counter.py <pdf_file_or_directory>")
        print("Examples:")
        print("  python3 pdf_page_counter.py document.pdf")
        print("  python3 pdf_page_counter.py /path/to/qap/directory")
        sys.exit(1)
    
    path = sys.argv[1]
    counter = PDFPageCounter()
    
    if os.path.isfile(path) and path.endswith('.pdf'):
        # Single file mode
        is_compatible, page_count, message = counter.check_claude_compatibility(path)
        print(f"\nFile: {Path(path).name}")
        print(f"Pages: {page_count}")
        print(f"Status: {message}")
        
        if not is_compatible:
            print(f"\n⚠️  WARNING: This PDF exceeds Claude's 100-page limit")
            print(f"   Recommended: Use pdf_splitter.py to split into sections")
            sys.exit(1)
        else:
            print(f"✅ PDF is compatible with Claude API")
            
    elif os.path.isdir(path):
        # Directory mode
        results = counter.scan_directory(path)
        report = counter.generate_report(results)
        print(report)
        
        # Save report to file
        report_file = Path(path) / "pdf_compatibility_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {report_file}")
        
    else:
        print(f"Error: {path} is not a valid PDF file or directory")
        sys.exit(1)

if __name__ == "__main__":
    main()