#!/usr/bin/env python3
"""
PDF Splitter - Breaks large PDFs into Claude API compatible sections (<100 pages)
Part of Colosseum QAP RAG system emergency patch

Built by Structured Consultants LLC
Roman Engineering Standards: Built to Last 2000+ Years
"""

import os
import sys
from pathlib import Path
import PyPDF2
import logging
import math

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFSplitter:
    """Utility to split large PDFs into Claude API compatible sections"""
    
    def __init__(self, max_pages_per_section=95):
        self.max_pages_per_section = max_pages_per_section  # Slightly under 100 for safety
        
    def split_pdf(self, input_path, output_dir=None, custom_prefix=None):
        """Split a PDF into multiple sections"""
        input_path = Path(input_path)
        
        if output_dir is None:
            output_dir = input_path.parent / f"{input_path.stem}_split"
        else:
            output_dir = Path(output_dir)
        
        # Create output directory
        output_dir.mkdir(exist_ok=True)
        
        try:
            with open(input_path, 'rb') as input_file:
                pdf_reader = PyPDF2.PdfReader(input_file)
                total_pages = len(pdf_reader.pages)
                
                logger.info(f"Splitting {input_path.name}: {total_pages} pages")
                
                # Calculate number of sections needed
                num_sections = math.ceil(total_pages / self.max_pages_per_section)
                
                if num_sections == 1:
                    logger.info(f"PDF has {total_pages} pages, no splitting needed")
                    return [str(input_path)]
                
                output_files = []
                
                for section in range(num_sections):
                    start_page = section * self.max_pages_per_section
                    end_page = min(start_page + self.max_pages_per_section, total_pages)
                    
                    # Create output filename
                    if custom_prefix:
                        output_filename = f"{custom_prefix}_section_{section + 1:02d}_pages_{start_page + 1:03d}-{end_page:03d}.pdf"
                    else:
                        output_filename = f"{input_path.stem}_section_{section + 1:02d}_pages_{start_page + 1:03d}-{end_page:03d}.pdf"
                    
                    output_path = output_dir / output_filename
                    
                    # Create new PDF with pages for this section
                    pdf_writer = PyPDF2.PdfWriter()
                    
                    for page_num in range(start_page, end_page):
                        pdf_writer.add_page(pdf_reader.pages[page_num])
                    
                    # Write section to file
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
                    
                    output_files.append(str(output_path))
                    logger.info(f"Created section {section + 1}/{num_sections}: {output_filename} (pages {start_page + 1}-{end_page})")
                
                # Create metadata file
                self._create_metadata_file(output_dir, input_path, output_files, total_pages)
                
                logger.info(f"Successfully split {input_path.name} into {num_sections} sections")
                return output_files
                
        except Exception as e:
            logger.error(f"Error splitting PDF {input_path}: {str(e)}")
            return None
    
    def _create_metadata_file(self, output_dir, original_file, section_files, total_pages):
        """Create metadata file for tracking split information"""
        metadata = {
            'original_file': str(original_file),
            'total_pages': total_pages,
            'sections_created': len(section_files),
            'max_pages_per_section': self.max_pages_per_section,
            'section_files': [Path(f).name for f in section_files]
        }
        
        metadata_content = f"""PDF SPLIT METADATA
==================
Original File: {metadata['original_file']}
Total Pages: {metadata['total_pages']}
Sections Created: {metadata['sections_created']}
Max Pages per Section: {metadata['max_pages_per_section']}

SECTION FILES:
"""
        
        for i, section_file in enumerate(metadata['section_files'], 1):
            start_page = (i - 1) * self.max_pages_per_section + 1
            end_page = min(i * self.max_pages_per_section, total_pages)
            metadata_content += f"{i:2d}. {section_file} (pages {start_page}-{end_page})\n"
        
        metadata_file = output_dir / "split_metadata.txt"
        with open(metadata_file, 'w') as f:
            f.write(metadata_content)
        
        logger.info(f"Metadata saved to: {metadata_file}")
    
    def batch_split(self, input_dir, file_pattern="*.pdf"):
        """Split multiple PDFs in a directory"""
        input_dir = Path(input_dir)
        pdf_files = list(input_dir.glob(file_pattern))
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        results = []
        for pdf_file in pdf_files:
            logger.info(f"Processing: {pdf_file.name}")
            output_files = self.split_pdf(pdf_file)
            
            if output_files:
                results.append({
                    'original': str(pdf_file),
                    'sections': output_files,
                    'success': True
                })
            else:
                results.append({
                    'original': str(pdf_file),
                    'sections': [],
                    'success': False
                })
        
        return results

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python3 pdf_splitter.py <pdf_file_or_directory> [output_directory] [custom_prefix]")
        print("Examples:")
        print("  python3 pdf_splitter.py document.pdf")
        print("  python3 pdf_splitter.py document.pdf ./split_output/")
        print("  python3 pdf_splitter.py document.pdf ./split_output/ CA_2025_QAP")
        print("  python3 pdf_splitter.py /path/to/qap/directory/")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    custom_prefix = sys.argv[3] if len(sys.argv) > 3 else None
    
    splitter = PDFSplitter()
    
    if os.path.isfile(input_path) and input_path.endswith('.pdf'):
        # Single file mode
        print(f"\nSplitting PDF: {Path(input_path).name}")
        output_files = splitter.split_pdf(input_path, output_dir, custom_prefix)
        
        if output_files:
            print(f"\n✅ Successfully created {len(output_files)} sections:")
            for output_file in output_files:
                print(f"   - {Path(output_file).name}")
        else:
            print("\n❌ Error splitting PDF")
            sys.exit(1)
            
    elif os.path.isdir(input_path):
        # Directory mode
        print(f"\nBatch splitting PDFs in: {input_path}")
        results = splitter.batch_split(input_path)
        
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        print(f"\n📊 Batch Results:")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        
        if successful > 0:
            print(f"\n✅ Successfully split files:")
            for result in results:
                if result['success']:
                    original_name = Path(result['original']).name
                    print(f"   - {original_name} → {len(result['sections'])} sections")
        
        if failed > 0:
            print(f"\n❌ Failed to split:")
            for result in results:
                if not result['success']:
                    print(f"   - {Path(result['original']).name}")
    else:
        print(f"Error: {input_path} is not a valid PDF file or directory")
        sys.exit(1)

if __name__ == "__main__":
    main()