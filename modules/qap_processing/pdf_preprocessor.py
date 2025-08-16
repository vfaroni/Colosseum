#!/usr/bin/env python3
"""
PDF Preprocessor - Integrated PDF preparation for QAP chunking pipeline

CRITICAL QAP PROCESSING COMPONENT
- Prevents PDF processing failures by checking page limits before processing
- Automatically splits oversized PDFs into manageable sections
- Provides processing-ready PDF sections for chunking pipeline
- Part of solution for systematic QAP chunking failures identified in STRIKE_LEADER report
"""

import os
import sys
from pathlib import Path
import argparse
import logging
import json
from datetime import datetime

# Add modules to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from pdf_page_counter import check_pdf_processing_limit, batch_check_qap_pdfs
    from pdf_splitter import split_qap_pdf_if_needed, batch_split_qap_pdfs
except ImportError as e:
    logging.error(f"Import error: {e}")
    logging.error("Ensure pdf_page_counter.py and pdf_splitter.py are in the same directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QAPPDFPreprocessor:
    """
    Comprehensive PDF preprocessor for QAP chunking pipeline
    """
    
    def __init__(self, max_pages=100, output_base_dir=None):
        self.max_pages = max_pages
        self.output_base_dir = output_base_dir
        self.processing_log = []
        
    def preprocess_single_pdf(self, pdf_path, force_split=False):
        """
        Preprocess a single PDF for chunking
        
        Args:
            pdf_path (str): Path to PDF file
            force_split (bool): Force splitting even if under page limit
            
        Returns:
            dict: Preprocessing results with ready-to-process file paths
        """
        logger.info(f"Preprocessing PDF: {pdf_path}")
        
        # Step 1: Check page count
        check_result = check_pdf_processing_limit(pdf_path, self.max_pages)
        
        preprocessing_result = {
            'original_file': pdf_path,
            'timestamp': datetime.now().isoformat(),
            'page_count': check_result['pages'],
            'processing_status': check_result['status'],
            'ready_for_chunking': [],
            'split_performed': False,
            'error': None
        }
        
        if check_result['status'] == 'error':
            preprocessing_result['error'] = check_result['message']
            logger.error(f"❌ Cannot preprocess {pdf_path}: {check_result['message']}")
            return preprocessing_result
        
        # Step 2: Determine if splitting is needed
        needs_splitting = check_result['needs_splitting'] or force_split
        
        if not needs_splitting:
            # PDF is ready for direct processing
            preprocessing_result['ready_for_chunking'] = [pdf_path]
            logger.info(f"✅ {pdf_path} ready for direct chunking ({check_result['pages']} pages)")
            
        else:
            # PDF needs splitting
            logger.info(f"🔧 {pdf_path} requires splitting ({check_result['pages']} pages)")
            
            # Determine output directory
            output_dir = self.output_base_dir
            if output_dir is None:
                output_dir = Path(pdf_path).parent / "split_sections"
            
            # Split the PDF
            split_result = split_qap_pdf_if_needed(pdf_path, output_dir, self.max_pages)
            
            if split_result['split'] and split_result['sections']:
                preprocessing_result['split_performed'] = True
                preprocessing_result['ready_for_chunking'] = split_result['sections']
                logger.info(f"✅ Split into {len(split_result['sections'])} sections")
            else:
                preprocessing_result['error'] = f"Failed to split PDF: {split_result['reason']}"
                logger.error(f"❌ Failed to split {pdf_path}")
        
        # Log the preprocessing step
        self.processing_log.append(preprocessing_result)
        return preprocessing_result
    
    def preprocess_qap_directory(self, qap_directory):
        """
        Preprocess all QAP PDFs in a directory structure
        
        Args:
            qap_directory (str): Path to QAP data directory
            
        Returns:
            dict: Complete preprocessing results
        """
        logger.info(f"Preprocessing QAP directory: {qap_directory}")
        
        # Step 1: Identify all PDFs and their status
        check_results = batch_check_qap_pdfs(qap_directory)
        
        preprocessing_results = {
            'timestamp': datetime.now().isoformat(),
            'qap_directory': qap_directory,
            'max_pages': self.max_pages,
            'total_pdfs': len(check_results),
            'pdfs_ready': 0,
            'pdfs_split': 0,
            'pdfs_failed': 0,
            'individual_results': {},
            'chunking_ready_files': []
        }
        
        logger.info(f"Found {len(check_results)} PDFs to preprocess")
        
        # Step 2: Process each PDF
        for relative_path, check_result in check_results.items():
            full_path = Path(qap_directory) / relative_path
            
            # Skip PDFs with errors
            if check_result['status'] == 'error':
                preprocessing_results['pdfs_failed'] += 1
                preprocessing_results['individual_results'][relative_path] = {
                    'status': 'error',
                    'error': check_result['message']
                }
                continue
            
            # Preprocess the PDF
            result = self.preprocess_single_pdf(str(full_path))
            preprocessing_results['individual_results'][relative_path] = result
            
            # Update summary statistics
            if result['error']:
                preprocessing_results['pdfs_failed'] += 1
            elif result['split_performed']:
                preprocessing_results['pdfs_split'] += 1
                preprocessing_results['chunking_ready_files'].extend(result['ready_for_chunking'])
            else:
                preprocessing_results['pdfs_ready'] += 1
                preprocessing_results['chunking_ready_files'].extend(result['ready_for_chunking'])
        
        logger.info(f"Preprocessing complete: {preprocessing_results['pdfs_ready']} ready, {preprocessing_results['pdfs_split']} split, {preprocessing_results['pdfs_failed']} failed")
        
        return preprocessing_results
    
    def generate_chunking_pipeline_config(self, preprocessing_results, output_file=None):
        """
        Generate configuration for the chunking pipeline
        
        Args:
            preprocessing_results (dict): Results from preprocessing
            output_file (str): Optional output file for configuration
            
        Returns:
            dict: Chunking pipeline configuration
        """
        config = {
            'pipeline_config': {
                'generated': datetime.now().isoformat(),
                'max_pages_per_file': self.max_pages,
                'total_files_to_process': len(preprocessing_results['chunking_ready_files'])
            },
            'processing_queue': []
        }
        
        # Create processing queue with metadata
        for i, file_path in enumerate(preprocessing_results['chunking_ready_files'], 1):
            file_path_obj = Path(file_path)
            
            # Determine if this is a split section or original file
            is_split_section = 'split_sections' in file_path_obj.parts
            
            if is_split_section:
                # Extract original file info from split section path
                parent_dir = file_path_obj.parent.parent
                original_pattern = file_path_obj.stem.split('_section_')[0]
                section_info = file_path_obj.stem.split('_section_')[1] if '_section_' in file_path_obj.stem else 'unknown'
            else:
                parent_dir = file_path_obj.parent
                original_pattern = file_path_obj.stem
                section_info = None
            
            queue_item = {
                'sequence': i,
                'file_path': file_path,
                'file_name': file_path_obj.name,
                'original_document': original_pattern,
                'is_split_section': is_split_section,
                'section_info': section_info,
                'jurisdiction': self._extract_jurisdiction_from_path(file_path),
                'processing_priority': 'high' if 'CA_2025' in file_path else 'normal'
            }
            
            config['processing_queue'].append(queue_item)
        
        # Sort by jurisdiction and section order
        config['processing_queue'].sort(key=lambda x: (x['jurisdiction'], x['original_document'], x['section_info'] or ''))
        
        # Update sequence numbers
        for i, item in enumerate(config['processing_queue'], 1):
            item['sequence'] = i
        
        # Output configuration
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Chunking pipeline configuration saved to: {output_file}")
        
        return config
    
    def _extract_jurisdiction_from_path(self, file_path):
        """Extract jurisdiction code from file path"""
        path_parts = Path(file_path).parts
        
        # Look for 2-letter jurisdiction codes in path
        for part in path_parts:
            if len(part) == 2 and part.isupper():
                return part
        
        # Fallback: extract from filename
        filename = Path(file_path).name
        if filename.startswith('CA_'):
            return 'CA'
        elif filename.startswith('TX_'):
            return 'TX'
        # Add more patterns as needed
        
        return 'UNKNOWN'

def generate_comprehensive_report(preprocessing_results, config, output_file=None):
    """
    Generate comprehensive preprocessing and pipeline report
    """
    report_lines = []
    report_lines.append("# QAP PDF Preprocessing & Pipeline Configuration Report")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Executive Summary
    report_lines.append("## 🎯 Executive Summary")
    report_lines.append(f"- **Total PDFs processed**: {preprocessing_results['total_pdfs']}")
    report_lines.append(f"- **Ready for chunking**: {preprocessing_results['pdfs_ready']}")
    report_lines.append(f"- **Required splitting**: {preprocessing_results['pdfs_split']}")
    report_lines.append(f"- **Processing failures**: {preprocessing_results['pdfs_failed']}")
    report_lines.append(f"- **Files ready for chunking**: {len(preprocessing_results['chunking_ready_files'])}")
    report_lines.append("")
    
    # Processing Status
    if preprocessing_results['pdfs_split'] > 0:
        report_lines.append("## 🔧 Split Processing Results")
        report_lines.append("")
        
        for relative_path, result in preprocessing_results['individual_results'].items():
            if result.get('split_performed'):
                report_lines.append(f"### {relative_path}")
                report_lines.append(f"- Original pages: {result['page_count']}")
                report_lines.append(f"- Sections created: {len(result['ready_for_chunking'])}")
                report_lines.append("- Section files:")
                for section in result['ready_for_chunking']:
                    section_name = Path(section).name
                    report_lines.append(f"  - `{section_name}`")
                report_lines.append("")
    
    # Pipeline Configuration Summary
    report_lines.append("## 📋 Chunking Pipeline Configuration")
    report_lines.append(f"- **Queue size**: {len(config['processing_queue'])} files")
    report_lines.append(f"- **Max pages per file**: {config['pipeline_config']['max_pages_per_file']}")
    report_lines.append("")
    
    # High Priority Items
    high_priority_items = [item for item in config['processing_queue'] if item['processing_priority'] == 'high']
    if high_priority_items:
        report_lines.append("## 🚨 High Priority Processing Queue")
        report_lines.append("")
        for item in high_priority_items:
            report_lines.append(f"{item['sequence']}. **{item['file_name']}** ({item['jurisdiction']})")
            if item['is_split_section']:
                report_lines.append(f"   - Split section: {item['section_info']}")
        report_lines.append("")
    
    # Next Steps
    report_lines.append("## ⚔️ STRIKE_LEADER Recommendations")
    report_lines.append("")
    report_lines.append("### Immediate Actions")
    report_lines.append("1. **Begin chunking pipeline** using the generated configuration")
    report_lines.append("2. **Process high-priority items first** (CA 2025 QAP sections)")
    report_lines.append("3. **Monitor chunking quality** for split sections vs original files")
    report_lines.append("4. **Validate extracted content** against source sections")
    report_lines.append("")
    
    report_lines.append("### Quality Assurance")
    report_lines.append("- Test chunking on split sections to ensure no content loss")
    report_lines.append("- Verify that section boundaries don't break regulatory content")
    report_lines.append("- Compare chunked content quality between original and split files")
    report_lines.append("")
    
    report_content = "\n".join(report_lines)
    
    # Output report
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report_content)
        logger.info(f"Comprehensive report saved to: {output_file}")
    else:
        print(report_content)

def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive PDF preprocessor for QAP chunking pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preprocess single PDF
  python3 pdf_preprocessor.py --pdf path/to/qap.pdf
  
  # Preprocess entire QAP directory
  python3 pdf_preprocessor.py --qap-directory ../../data_sets/QAP/
  
  # Generate pipeline configuration
  python3 pdf_preprocessor.py --qap-directory ../../data_sets/QAP/ --config pipeline_config.json --report preprocessing_report.md
        """
    )
    
    parser.add_argument('--pdf', help='Preprocess a single PDF file')
    parser.add_argument('--qap-directory', help='Preprocess all PDFs in QAP directory')
    parser.add_argument('--max-pages', type=int, default=100, help='Maximum pages per section (default: 100)')
    parser.add_argument('--output-dir', help='Base directory for split sections')
    parser.add_argument('--config', help='Output file for chunking pipeline configuration (JSON)')
    parser.add_argument('--report', help='Output file for comprehensive report (Markdown)')
    
    args = parser.parse_args()
    
    # Initialize preprocessor
    preprocessor = QAPPDFPreprocessor(args.max_pages, args.output_dir)
    
    if args.pdf:
        # Preprocess single PDF
        result = preprocessor.preprocess_single_pdf(args.pdf)
        
        print(f"PDF: {args.pdf}")
        print(f"Pages: {result['page_count']}")
        print(f"Status: {result['processing_status']}")
        print(f"Split performed: {'Yes' if result['split_performed'] else 'No'}")
        print(f"Ready for chunking: {len(result['ready_for_chunking'])} files")
        
        if result['ready_for_chunking']:
            print("Files ready for chunking:")
            for i, file_path in enumerate(result['ready_for_chunking'], 1):
                print(f"  {i}. {Path(file_path).name}")
                
    elif args.qap_directory:
        # Preprocess QAP directory
        results = preprocessor.preprocess_qap_directory(args.qap_directory)
        
        # Generate pipeline configuration
        config = preprocessor.generate_chunking_pipeline_config(results, args.config)
        
        # Generate comprehensive report
        generate_comprehensive_report(results, config, args.report)
        
    else:
        # Default: check local QAP directory
        default_qap_path = "../../data_sets/QAP/"
        if os.path.exists(default_qap_path):
            logger.info(f"Using default QAP directory: {default_qap_path}")
            results = preprocessor.preprocess_qap_directory(default_qap_path)
            config = preprocessor.generate_chunking_pipeline_config(results, args.config)
            generate_comprehensive_report(results, config, args.report)
        else:
            logger.error("No PDF specified and default QAP directory not found")
            parser.print_help()

if __name__ == "__main__":
    main()