#!/usr/bin/env python3
"""
Enhanced Chunking Processor - Handles split PDFs for QAP RAG system
Integrates with pdf_page_counter.py and pdf_splitter.py for complete pipeline

Built by Structured Consultants LLC
Roman Engineering Standards: Built to Last 2000+ Years
"""

import os
import sys
from pathlib import Path
import json
import logging
from typing import List, Dict, Optional, Union

# Import our PDF processing utilities
from pdf_page_counter import PDFPageCounter
from pdf_splitter import PDFSplitter

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedChunkingProcessor:
    """Processes PDFs with automatic splitting and chunking for Claude API compatibility"""
    
    def __init__(self, max_pages_per_section=95, chunk_size=1000, chunk_overlap=200):
        self.page_counter = PDFPageCounter()
        self.pdf_splitter = PDFSplitter(max_pages_per_section)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def process_pdf_for_rag(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict:
        """Complete pipeline: check compatibility, split if needed, prepare for chunking"""
        pdf_path = Path(pdf_path)
        
        if output_dir is None:
            output_dir = pdf_path.parent / "processed"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Processing PDF for RAG: {pdf_path.name}")
        
        # Step 1: Check Claude API compatibility
        is_compatible, page_count, message = self.page_counter.check_claude_compatibility(pdf_path)
        
        result = {
            'original_file': str(pdf_path),
            'page_count': page_count,
            'claude_compatible': is_compatible,
            'processing_status': 'success',
            'sections': [],
            'metadata_file': None,
            'ready_for_chunking': False
        }
        
        if page_count is None:
            result['processing_status'] = 'error'
            result['error'] = 'Could not read PDF file'
            return result
        
        # Step 2: Handle PDF based on compatibility
        if is_compatible:
            logger.info(f"PDF is Claude compatible ({page_count} pages) - no splitting needed")
            result['sections'] = [str(pdf_path)]
            result['ready_for_chunking'] = True
            
        else:
            logger.info(f"PDF needs splitting ({page_count} pages) - processing...")
            
            # Create split output directory
            split_dir = output_dir / f"{pdf_path.stem}_split"
            
            # Split the PDF
            section_files = self.pdf_splitter.split_pdf(pdf_path, split_dir)
            
            if section_files:
                result['sections'] = section_files
                result['metadata_file'] = str(split_dir / "split_metadata.txt")
                result['ready_for_chunking'] = True
                logger.info(f"Successfully split into {len(section_files)} sections")
            else:
                result['processing_status'] = 'error'
                result['error'] = 'Failed to split PDF'
                return result
        
        # Step 3: Prepare chunking metadata
        result['chunking_plan'] = self._create_chunking_plan(result['sections'])
        
        return result
    
    def _create_chunking_plan(self, section_files: List[str]) -> Dict:
        """Create a plan for chunking the processed sections"""
        chunking_plan = {
            'total_sections': len(section_files),
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'sections': []
        }
        
        for i, section_file in enumerate(section_files, 1):
            section_path = Path(section_file)
            section_info = {
                'section_number': i,
                'file_path': str(section_path),
                'file_name': section_path.name,
                'estimated_chunks': 'TBD',  # Would need text extraction to estimate
                'status': 'ready_for_chunking'
            }
            chunking_plan['sections'].append(section_info)
        
        return chunking_plan
    
    def batch_process_directory(self, input_dir: str, output_dir: Optional[str] = None) -> Dict:
        """Process all PDFs in a directory"""
        input_dir = Path(input_dir)
        
        if output_dir is None:
            output_dir = input_dir / "batch_processed"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(exist_ok=True)
        
        pdf_files = list(input_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        batch_results = {
            'input_directory': str(input_dir),
            'output_directory': str(output_dir),
            'total_files': len(pdf_files),
            'successful': 0,
            'failed': 0,
            'results': []
        }
        
        for pdf_file in pdf_files:
            logger.info(f"Processing: {pdf_file.name}")
            
            # Create individual output directory for this PDF
            pdf_output_dir = output_dir / pdf_file.stem
            
            result = self.process_pdf_for_rag(pdf_file, pdf_output_dir)
            batch_results['results'].append(result)
            
            if result['processing_status'] == 'success':
                batch_results['successful'] += 1
                logger.info(f"✅ Successfully processed: {pdf_file.name}")
            else:
                batch_results['failed'] += 1
                logger.error(f"❌ Failed to process: {pdf_file.name}")
        
        # Save batch results
        results_file = output_dir / "batch_processing_results.json"
        with open(results_file, 'w') as f:
            json.dump(batch_results, f, indent=2)
        
        logger.info(f"Batch processing complete - Results saved to: {results_file}")
        return batch_results
    
    def generate_processing_report(self, results: Union[Dict, List[Dict]]) -> str:
        """Generate a human-readable processing report"""
        
        if isinstance(results, dict) and 'results' in results:
            # Batch results
            batch_results = results
            report = f"""QAP PDF PROCESSING REPORT
========================
Input Directory: {batch_results['input_directory']}
Output Directory: {batch_results['output_directory']}
Total Files: {batch_results['total_files']}
Successful: {batch_results['successful']}
Failed: {batch_results['failed']}

PROCESSING DETAILS:
"""
            
            for result in batch_results['results']:
                original_name = Path(result['original_file']).name
                status = "✅ SUCCESS" if result['processing_status'] == 'success' else "❌ FAILED"
                
                report += f"\n{original_name}:\n"
                report += f"  Status: {status}\n"
                report += f"  Pages: {result['page_count']}\n"
                report += f"  Claude Compatible: {result['claude_compatible']}\n"
                report += f"  Sections Created: {len(result['sections'])}\n"
                
                if result['processing_status'] == 'error':
                    report += f"  Error: {result.get('error', 'Unknown error')}\n"
        
        else:
            # Single file result
            result = results
            original_name = Path(result['original_file']).name
            status = "✅ SUCCESS" if result['processing_status'] == 'success' else "❌ FAILED"
            
            report = f"""QAP PDF PROCESSING REPORT
========================
File: {original_name}
Status: {status}
Pages: {result['page_count']}
Claude Compatible: {result['claude_compatible']}
Sections Created: {len(result['sections'])}

CHUNKING PLAN:
Total Sections: {result.get('chunking_plan', {}).get('total_sections', 'N/A')}
Chunk Size: {result.get('chunking_plan', {}).get('chunk_size', 'N/A')}
Chunk Overlap: {result.get('chunking_plan', {}).get('chunk_overlap', 'N/A')}
"""
            
            if result['processing_status'] == 'error':
                report += f"\nError: {result.get('error', 'Unknown error')}\n"
        
        return report

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python3 enhanced_chunking_processor.py <pdf_file_or_directory> [output_directory]")
        print("Examples:")
        print("  python3 enhanced_chunking_processor.py document.pdf")
        print("  python3 enhanced_chunking_processor.py /path/to/qap/directory")
        print("  python3 enhanced_chunking_processor.py document.pdf ./processed_output/")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    processor = EnhancedChunkingProcessor()
    
    if os.path.isfile(input_path) and input_path.endswith('.pdf'):
        # Single file mode
        print(f"\nProcessing PDF for RAG: {Path(input_path).name}")
        result = processor.process_pdf_for_rag(input_path, output_dir)
        
        # Generate and display report
        report = processor.generate_processing_report(result)
        print(f"\n{report}")
        
        if result['processing_status'] == 'success':
            print(f"\n🎯 READY FOR CHUNKING:")
            for section in result['sections']:
                print(f"   - {Path(section).name}")
        else:
            print(f"\n❌ Processing failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    elif os.path.isdir(input_path):
        # Directory mode
        print(f"\nBatch processing PDFs in: {input_path}")
        results = processor.batch_process_directory(input_path, output_dir)
        
        # Generate and display report
        report = processor.generate_processing_report(results)
        print(f"\n{report}")
        
        print(f"\n📊 Summary: {results['successful']}/{results['total_files']} files processed successfully")
        
    else:
        print(f"Error: {input_path} is not a valid PDF file or directory")
        sys.exit(1)

if __name__ == "__main__":
    main()