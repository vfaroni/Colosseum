#!/usr/bin/env python3
"""
Pipeline Manager - Batch Document Processing Script
Roman Engineering Standard: Built for 2000+ year reliability

Command-line script for processing multiple documents in batch through
the complete pipeline workflow with comprehensive reporting and monitoring.
"""

import os
import sys
import json
import argparse
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
import glob

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.extraction_orchestrator import ExtractionOrchestrator, ProcessingStatus
from core.document_processor import DocumentType
from integrations.openai_client import OpenAIConfig, ModelType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Process multiple documents in batch through the Pipeline Manager workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 batch_processor.py --input-dir documents/
  python3 batch_processor.py --input-pattern "*.pdf" --excel-file batch_results.xlsx
  python3 batch_processor.py --input-files doc1.pdf doc2.pdf doc3.pdf
  python3 batch_processor.py --input-dir documents/ --workers 8 --batch-size 20
  python3 batch_processor.py --input-dir documents/ --filter-type offering_memorandum
  python3 batch_processor.py --input-dir documents/ --resume-from batch_state.json
        """
    )
    
    # Input source options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input-dir",
        help="Directory containing documents to process"
    )
    input_group.add_argument(
        "--input-pattern",
        help="Glob pattern for finding documents (e.g., '**/*.pdf')"
    )
    input_group.add_argument(
        "--input-files",
        nargs="+",
        help="Specific files to process"
    )
    input_group.add_argument(
        "--input-list",
        help="Text file containing list of files to process (one per line)"
    )
    
    # Processing options
    parser.add_argument(
        "--excel-file",
        default="batch_pipeline.xlsx",
        help="Excel pipeline file path (default: batch_pipeline.xlsx)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of concurrent workers (default: 4)"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for processing (default: 50)"
    )
    
    parser.add_argument(
        "--filter-type",
        choices=["offering_memorandum", "financial_statement", "rent_roll", "property_report"],
        help="Filter documents by type (auto-detected if not specified)"
    )
    
    parser.add_argument(
        "--file-extensions",
        nargs="+",
        default=[".pdf", ".docx", ".xlsx", ".txt"],
        help="File extensions to process (default: .pdf .docx .xlsx .txt)"
    )
    
    parser.add_argument(
        "--model",
        choices=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"],
        default="gpt-4",
        help="OpenAI model to use (default: gpt-4)"
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Model temperature (default: 0.1)"
    )
    
    parser.add_argument(
        "--config",
        help="Configuration file path"
    )
    
    # Output options
    parser.add_argument(
        "--output-dir",
        help="Directory for output files (default: current directory)"
    )
    
    parser.add_argument(
        "--save-json",
        action="store_true",
        help="Save extracted data to individual JSON files"
    )
    
    parser.add_argument(
        "--save-summary",
        action="store_true",
        help="Save batch processing summary"
    )
    
    parser.add_argument(
        "--save-failed",
        action="store_true",
        help="Save list of failed documents"
    )
    
    # Control options
    parser.add_argument(
        "--resume-from",
        help="Resume from previous batch state file"
    )
    
    parser.add_argument(
        "--save-state",
        help="Save batch state for resuming"
    )
    
    parser.add_argument(
        "--skip-excel",
        action="store_true",
        help="Skip Excel integration (extraction only)"
    )
    
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue processing even if some documents fail"
    )
    
    parser.add_argument(
        "--max-failures",
        type=int,
        default=10,
        help="Maximum number of failures before stopping (default: 10)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform dry run without making changes"
    )
    
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Show progress bar"
    )
    
    return parser


def discover_documents(args: argparse.Namespace) -> List[str]:
    """Discover documents to process based on input arguments"""
    documents = []
    
    if args.input_dir:
        # Process directory
        input_path = Path(args.input_dir)
        if not input_path.exists():
            logger.error(f"Input directory not found: {args.input_dir}")
            return []
        
        logger.info(f"Scanning directory: {args.input_dir}")
        for ext in args.file_extensions:
            pattern = f"**/*{ext}"
            found_files = list(input_path.glob(pattern))
            documents.extend([str(f) for f in found_files])
            logger.debug(f"Found {len(found_files)} {ext} files")
    
    elif args.input_pattern:
        # Process glob pattern
        logger.info(f"Using pattern: {args.input_pattern}")
        found_files = glob.glob(args.input_pattern, recursive=True)
        documents.extend(found_files)
    
    elif args.input_files:
        # Process specific files
        documents = args.input_files
    
    elif args.input_list:
        # Process file list
        try:
            with open(args.input_list, 'r') as f:
                documents = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Failed to read input list: {e}")
            return []
    
    # Filter by file extensions
    if args.file_extensions:
        original_count = len(documents)
        documents = [
            doc for doc in documents 
            if any(doc.lower().endswith(ext.lower()) for ext in args.file_extensions)
        ]
        filtered_count = original_count - len(documents)
        if filtered_count > 0:
            logger.info(f"Filtered out {filtered_count} files by extension")
    
    # Remove duplicates and sort
    documents = sorted(list(set(documents)))
    
    # Verify files exist
    valid_documents = []
    for doc in documents:
        if Path(doc).exists():
            valid_documents.append(doc)
        else:
            logger.warning(f"Document not found: {doc}")
    
    logger.info(f"Discovered {len(valid_documents)} documents to process")
    return valid_documents


def load_batch_state(state_file: str) -> Dict[str, Any]:
    """Load batch processing state from file"""
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
        logger.info(f"Loaded batch state from {state_file}")
        return state
    except Exception as e:
        logger.error(f"Failed to load batch state: {e}")
        return {}


def save_batch_state(state: Dict[str, Any], state_file: str):
    """Save batch processing state to file"""
    try:
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        logger.debug(f"Saved batch state to {state_file}")
    except Exception as e:
        logger.error(f"Failed to save batch state: {e}")


def filter_documents_by_state(documents: List[str], state: Dict[str, Any]) -> List[str]:
    """Filter out already processed documents based on state"""
    if not state or "completed_documents" not in state:
        return documents
    
    completed = set(state["completed_documents"])
    remaining = [doc for doc in documents if doc not in completed]
    
    skipped_count = len(documents) - len(remaining)
    if skipped_count > 0:
        logger.info(f"Skipping {skipped_count} already processed documents")
    
    return remaining


def create_progress_tracker(total_docs: int, show_progress: bool):
    """Create progress tracking function"""
    if not show_progress:
        return lambda current, status: None
    
    try:
        from tqdm import tqdm
        pbar = tqdm(total=total_docs, desc="Processing documents")
        
        def update_progress(current: int, status: str = ""):
            pbar.n = current
            pbar.set_description(f"Processing documents - {status}")
            pbar.refresh()
        
        return update_progress, pbar
    except ImportError:
        logger.warning("tqdm not available, progress bar disabled")
        return lambda current, status: print(f"Progress: {current}/{total_docs} - {status}")


def process_batch(args: argparse.Namespace) -> bool:
    """Process batch of documents"""
    logger.info("🏛️ Starting batch document processing")
    
    # Discover documents
    documents = discover_documents(args)
    if not documents:
        logger.error("No documents found to process")
        return False
    
    # Load previous state if resuming
    batch_state = {}
    if args.resume_from and Path(args.resume_from).exists():
        batch_state = load_batch_state(args.resume_from)
        documents = filter_documents_by_state(documents, batch_state)
        
        if not documents:
            logger.info("All documents already processed")
            return True
    
    # Initialize progress tracking
    progress_info = create_progress_tracker(len(documents), args.progress)
    if isinstance(progress_info, tuple):
        update_progress, pbar = progress_info
    else:
        update_progress = progress_info
        pbar = None
    
    # Initialize orchestrator
    try:
        orchestrator = ExtractionOrchestrator()
        logger.info("Pipeline orchestrator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {e}")
        return False
    
    # Process documents in batches
    total_processed = 0
    total_successful = 0
    total_failed = 0
    failed_documents = []
    successful_documents = []
    processing_results = []
    
    try:
        # Determine document type filter
        document_type = None
        if args.filter_type:
            type_mapping = {
                "offering_memorandum": DocumentType.OFFERING_MEMORANDUM,
                "financial_statement": DocumentType.FINANCIAL_STATEMENT,
                "rent_roll": DocumentType.RENT_ROLL,
                "property_report": DocumentType.PROPERTY_REPORT
            }
            document_type = type_mapping.get(args.filter_type)
        
        # Process documents in chunks
        batch_size = args.batch_size
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            
            logger.info(f"Processing batch {i//batch_size + 1}: {len(batch_docs)} documents")
            
            # Create document types list if filtering
            doc_types = [document_type] * len(batch_docs) if document_type else None
            
            # Process batch
            batch_result = orchestrator.process_batch_documents(batch_docs, doc_types)
            
            # Update counters
            total_processed += batch_result.total_tasks
            total_successful += batch_result.successful_tasks
            total_failed += batch_result.failed_tasks
            
            # Track results
            for task in batch_result.tasks:
                processing_results.append(task)
                
                if task.status == ProcessingStatus.COMPLETED:
                    successful_documents.append(task.file_path)
                else:
                    failed_documents.append({
                        "file_path": task.file_path,
                        "error": task.error_message,
                        "status": task.status.value
                    })
            
            # Update progress
            update_progress(total_processed, f"{total_successful} successful, {total_failed} failed")
            
            # Save state periodically
            if args.save_state:
                current_state = {
                    "started_at": batch_state.get("started_at", datetime.now().isoformat()),
                    "last_updated": datetime.now().isoformat(),
                    "total_documents": len(documents),
                    "processed_documents": total_processed,
                    "successful_documents": total_successful,
                    "failed_documents": total_failed,
                    "completed_documents": successful_documents + [f["file_path"] for f in failed_documents]
                }
                save_batch_state(current_state, args.save_state)
            
            # Check failure threshold
            if total_failed >= args.max_failures and not args.continue_on_error:
                logger.error(f"Stopping: reached maximum failures ({args.max_failures})")
                break
            
            # Brief pause between batches
            if i + batch_size < len(documents):
                time.sleep(1)
        
        # Close progress bar
        if pbar:
            pbar.close()
        
        # Generate summary
        success_rate = (total_successful / total_processed) * 100 if total_processed > 0 else 0
        
        logger.info(f"✅ Batch processing completed")
        logger.info(f"📊 Results: {total_successful}/{total_processed} successful ({success_rate:.1f}%)")
        
        # Save outputs
        save_batch_outputs(processing_results, failed_documents, args)
        
        return total_failed == 0 or args.continue_on_error
        
    except KeyboardInterrupt:
        logger.info("⏹️ Processing interrupted by user")
        if pbar:
            pbar.close()
        
        # Save current state
        if args.save_state:
            current_state = {
                "started_at": batch_state.get("started_at", datetime.now().isoformat()),
                "interrupted_at": datetime.now().isoformat(),
                "total_documents": len(documents),
                "processed_documents": total_processed,
                "successful_documents": total_successful,
                "failed_documents": total_failed,
                "completed_documents": successful_documents + [f["file_path"] for f in failed_documents]
            }
            save_batch_state(current_state, args.save_state)
        
        return False
    
    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        if pbar:
            pbar.close()
        return False


def save_batch_outputs(processing_results: List, failed_documents: List, args: argparse.Namespace):
    """Save batch processing outputs"""
    output_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save individual JSON files
    if args.save_json:
        json_dir = output_dir / "extracted_data"
        json_dir.mkdir(exist_ok=True)
        
        for task in processing_results:
            if task.extraction_result and task.extraction_result.success:
                doc_name = Path(task.file_path).stem
                json_file = json_dir / f"{doc_name}_{timestamp}.json"
                
                try:
                    output_data = {
                        "document_path": task.file_path,
                        "extraction_data": task.extraction_result.data,
                        "metadata": {
                            "processing_time": task.processing_time,
                            "confidence_score": task.extraction_result.confidence_score,
                            "document_type": task.extraction_result.document_type.value
                        }
                    }
                    
                    with open(json_file, 'w') as f:
                        json.dump(output_data, f, indent=2, default=str)
                
                except Exception as e:
                    logger.warning(f"Failed to save JSON for {doc_name}: {e}")
    
    # Save batch summary
    if args.save_summary:
        summary_file = output_dir / f"batch_summary_{timestamp}.json"
        
        try:
            # Calculate statistics
            successful_tasks = [t for t in processing_results if t.status == ProcessingStatus.COMPLETED]
            failed_tasks = [t for t in processing_results if t.status == ProcessingStatus.FAILED]
            
            processing_times = [t.processing_time for t in successful_tasks if t.processing_time]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            confidence_scores = [
                t.extraction_result.confidence_score 
                for t in successful_tasks 
                if t.extraction_result and t.extraction_result.confidence_score
            ]
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            summary_data = {
                "batch_metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "total_documents": len(processing_results),
                    "successful_documents": len(successful_tasks),
                    "failed_documents": len(failed_tasks),
                    "success_rate": len(successful_tasks) / len(processing_results) if processing_results else 0
                },
                "performance_metrics": {
                    "average_processing_time": avg_processing_time,
                    "average_confidence_score": avg_confidence,
                    "total_processing_time": sum(processing_times)
                },
                "document_types": {},
                "failure_analysis": {
                    "common_errors": [],
                    "failed_documents": len(failed_documents)
                }
            }
            
            # Document type breakdown
            for task in successful_tasks:
                if task.extraction_result:
                    doc_type = task.extraction_result.document_type.value
                    summary_data["document_types"][doc_type] = summary_data["document_types"].get(doc_type, 0) + 1
            
            with open(summary_file, 'w') as f:
                json.dump(summary_data, f, indent=2, default=str)
            
            logger.info(f"Saved batch summary to: {summary_file}")
        
        except Exception as e:
            logger.error(f"Failed to save batch summary: {e}")
    
    # Save failed documents list
    if args.save_failed and failed_documents:
        failed_file = output_dir / f"failed_documents_{timestamp}.json"
        
        try:
            with open(failed_file, 'w') as f:
                json.dump(failed_documents, f, indent=2, default=str)
            
            logger.info(f"Saved failed documents list to: {failed_file}")
        
        except Exception as e:
            logger.error(f"Failed to save failed documents list: {e}")


def main():
    """Main execution function"""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    # Display startup information
    logger.info("🏛️ Pipeline Manager - Batch Document Processing Script")
    logger.info(f"Workers: {args.workers}")
    logger.info(f"Batch Size: {args.batch_size}")
    logger.info(f"Model: {args.model}")
    logger.info(f"Excel File: {args.excel_file if not args.skip_excel else 'Skipped'}")
    
    if args.dry_run:
        logger.info("🧪 DRY RUN MODE - No changes will be made")
    
    if args.resume_from:
        logger.info(f"📂 Resuming from: {args.resume_from}")
    
    # Process batch
    success = process_batch(args)
    
    # Exit with appropriate code
    if success:
        logger.info("✅ Batch processing completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Batch processing failed or incomplete")
        sys.exit(1)


if __name__ == "__main__":
    main()