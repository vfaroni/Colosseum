#!/usr/bin/env python3
"""
Pipeline Manager - Single Document Processing Script
Roman Engineering Standard: Built for 2000+ year reliability

Command-line script for processing individual documents through the
complete pipeline workflow with comprehensive reporting.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

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
        description="Process a single document through the Pipeline Manager workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 process_document.py document.pdf
  python3 process_document.py document.pdf --excel-file pipeline.xlsx
  python3 process_document.py document.pdf --document-type offering_memorandum
  python3 process_document.py document.pdf --model gpt-4-turbo --verbose
  python3 process_document.py document.pdf --config config.json --output-report
        """
    )
    
    # Required arguments
    parser.add_argument(
        "document_path",
        help="Path to the document to process"
    )
    
    # Optional arguments
    parser.add_argument(
        "--excel-file",
        default="pipeline.xlsx",
        help="Excel pipeline file path (default: pipeline.xlsx)"
    )
    
    parser.add_argument(
        "--document-type",
        choices=["offering_memorandum", "financial_statement", "rent_roll", "property_report"],
        help="Document type for specialized processing"
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
    
    parser.add_argument(
        "--output-report",
        action="store_true",
        help="Generate detailed processing report"
    )
    
    parser.add_argument(
        "--output-json",
        help="Save extracted data to JSON file"
    )
    
    parser.add_argument(
        "--skip-excel",
        action="store_true",
        help="Skip Excel integration (extraction only)"
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
    
    return parser


def load_configuration(config_path: Optional[str]) -> dict:
    """Load configuration from file"""
    if not config_path:
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return {}


def validate_inputs(args: argparse.Namespace) -> bool:
    """Validate input arguments"""
    # Check document exists
    if not Path(args.document_path).exists():
        logger.error(f"Document not found: {args.document_path}")
        return False
    
    # Check document is readable
    try:
        with open(args.document_path, 'rb') as f:
            f.read(1024)  # Try to read first KB
    except Exception as e:
        logger.error(f"Cannot read document: {e}")
        return False
    
    # Check OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY environment variable not set")
        return False
    
    # Validate temperature range
    if not 0.0 <= args.temperature <= 2.0:
        logger.error("Temperature must be between 0.0 and 2.0")
        return False
    
    return True


def map_document_type(type_string: Optional[str]) -> Optional[DocumentType]:
    """Map string to DocumentType enum"""
    if not type_string:
        return None
    
    mapping = {
        "offering_memorandum": DocumentType.OFFERING_MEMORANDUM,
        "financial_statement": DocumentType.FINANCIAL_STATEMENT,
        "rent_roll": DocumentType.RENT_ROLL,
        "property_report": DocumentType.PROPERTY_REPORT
    }
    
    return mapping.get(type_string)


def create_processing_config(args: argparse.Namespace, base_config: dict) -> dict:
    """Create processing configuration from arguments"""
    config = base_config.copy()
    
    # Update Excel configuration
    if not args.skip_excel:
        config.setdefault("excel", {})
        config["excel"]["file_path"] = args.excel_file
        config["excel"]["backup_enabled"] = not args.dry_run
    
    # Update OpenAI configuration
    config.setdefault("openai", {})
    config["openai"]["model"] = args.model
    config["openai"]["temperature"] = args.temperature
    
    # Update processing options
    if args.dry_run:
        config["dry_run"] = True
    
    return config


def process_document(args: argparse.Namespace) -> bool:
    """Process the document through the pipeline"""
    logger.info(f"Starting document processing: {args.document_path}")
    
    # Load configuration
    base_config = load_configuration(args.config)
    processing_config = create_processing_config(args, base_config)
    
    # Initialize orchestrator
    try:
        orchestrator = ExtractionOrchestrator()
        logger.info("Pipeline orchestrator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {e}")
        return False
    
    # Determine document type
    document_type = map_document_type(args.document_type)
    if args.document_type and not document_type:
        logger.warning(f"Unknown document type: {args.document_type}")
    
    # Process document
    try:
        logger.info("Processing document through pipeline...")
        task = orchestrator.process_single_document(args.document_path, document_type)
        
        # Check processing results
        if task.status == ProcessingStatus.COMPLETED:
            logger.info("✅ Document processing completed successfully")
            
            # Display results summary
            display_processing_summary(task, args.verbose)
            
            # Save outputs
            save_outputs(task, args)
            
            return True
            
        elif task.status == ProcessingStatus.FAILED:
            logger.error(f"❌ Document processing failed: {task.error_message}")
            return False
            
        else:
            logger.warning(f"⚠️ Document processing incomplete: {task.status.value}")
            return False
            
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return False


def display_processing_summary(task, verbose: bool = False):
    """Display processing results summary"""
    print("\n" + "="*60)
    print("PROCESSING SUMMARY")
    print("="*60)
    
    # Basic information
    print(f"Document: {Path(task.file_path).name}")
    print(f"Status: {task.status.value.upper()}")
    print(f"Processing Time: {task.processing_time:.2f} seconds")
    
    # Extraction results
    if task.extraction_result:
        print(f"Extraction Success: {'✅ Yes' if task.extraction_result.success else '❌ No'}")
        print(f"Extraction Confidence: {task.extraction_result.confidence_score:.3f}")
        print(f"Document Type: {task.extraction_result.document_type.value}")
        
        if task.extraction_result.errors:
            print(f"Errors: {len(task.extraction_result.errors)}")
            if verbose:
                for error in task.extraction_result.errors:
                    print(f"  - {error}")
        
        if task.extraction_result.warnings:
            print(f"Warnings: {len(task.extraction_result.warnings)}")
            if verbose:
                for warning in task.extraction_result.warnings:
                    print(f"  - {warning}")
    
    # Validation results
    if task.validation_result:
        print(f"Validation Success: {'✅ Yes' if task.validation_result.is_valid else '❌ No'}")
        print(f"Validation Confidence: {task.validation_result.confidence_score:.3f}")
        print(f"Validation Issues: {len(task.validation_result.issues)}")
        
        if verbose and task.validation_result.issues:
            for issue in task.validation_result.issues:
                print(f"  - {issue.severity.value.upper()}: {issue.message}")
    
    # Excel integration
    if task.excel_row:
        print(f"Excel Row: {task.excel_row}")
    
    # Extracted data summary
    if task.extraction_result and task.extraction_result.data and verbose:
        print("\nEXTRACTED DATA SUMMARY:")
        print("-" * 30)
        
        data = task.extraction_result.data
        for section, section_data in data.items():
            if not section.startswith("_") and isinstance(section_data, dict):
                filled_fields = sum(1 for v in section_data.values() if v is not None and v != "")
                total_fields = len(section_data)
                print(f"{section}: {filled_fields}/{total_fields} fields")


def save_outputs(task, args: argparse.Namespace):
    """Save processing outputs"""
    # Save JSON output
    if args.output_json and task.extraction_result:
        try:
            output_data = {
                "processing_metadata": {
                    "document_path": task.file_path,
                    "processing_time": task.processing_time,
                    "extraction_timestamp": task.extraction_result.extraction_timestamp,
                    "status": task.status.value
                },
                "extraction_data": task.extraction_result.data,
                "validation_summary": {
                    "is_valid": task.validation_result.is_valid if task.validation_result else None,
                    "confidence_score": task.validation_result.confidence_score if task.validation_result else None,
                    "issues_count": len(task.validation_result.issues) if task.validation_result else 0
                }
            }
            
            with open(args.output_json, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            
            logger.info(f"Saved JSON output to: {args.output_json}")
        except Exception as e:
            logger.error(f"Failed to save JSON output: {e}")
    
    # Generate detailed report
    if args.output_report:
        report_path = Path(args.document_path).stem + "_processing_report.txt"
        try:
            generate_detailed_report(task, report_path)
            logger.info(f"Generated detailed report: {report_path}")
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")


def generate_detailed_report(task, report_path: str):
    """Generate detailed processing report"""
    with open(report_path, 'w') as f:
        f.write("PIPELINE MANAGER - DOCUMENT PROCESSING REPORT\n")
        f.write("=" * 60 + "\n\n")
        
        # Processing metadata
        f.write("PROCESSING METADATA:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Document: {task.file_path}\n")
        f.write(f"Task ID: {task.task_id}\n")
        f.write(f"Status: {task.status.value}\n")
        f.write(f"Created: {task.created_at}\n")
        f.write(f"Started: {task.started_at}\n")
        f.write(f"Completed: {task.completed_at}\n")
        f.write(f"Processing Time: {task.processing_time:.2f} seconds\n")
        f.write(f"Retry Count: {task.retry_count}\n\n")
        
        # Extraction results
        if task.extraction_result:
            f.write("EXTRACTION RESULTS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Success: {task.extraction_result.success}\n")
            f.write(f"Confidence Score: {task.extraction_result.confidence_score:.3f}\n")
            f.write(f"Document Type: {task.extraction_result.document_type.value}\n")
            f.write(f"Processing Time: {task.extraction_result.processing_time:.2f}s\n")
            
            if task.extraction_result.errors:
                f.write(f"Errors ({len(task.extraction_result.errors)}):\n")
                for error in task.extraction_result.errors:
                    f.write(f"  - {error}\n")
            
            if task.extraction_result.warnings:
                f.write(f"Warnings ({len(task.extraction_result.warnings)}):\n")
                for warning in task.extraction_result.warnings:
                    f.write(f"  - {warning}\n")
            
            f.write("\n")
        
        # Validation results
        if task.validation_result:
            f.write("VALIDATION RESULTS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Valid: {task.validation_result.is_valid}\n")
            f.write(f"Confidence Score: {task.validation_result.confidence_score:.3f}\n")
            f.write(f"Total Issues: {len(task.validation_result.issues)}\n")
            f.write(f"Critical Issues: {len(task.validation_result.critical_issues)}\n")
            f.write(f"Error Issues: {len(task.validation_result.error_issues)}\n")
            f.write(f"Warning Issues: {len(task.validation_result.warning_issues)}\n")
            
            if task.validation_result.issues:
                f.write("\nValidation Issues:\n")
                for issue in task.validation_result.issues:
                    f.write(f"  {issue.severity.value.upper()}: {issue.field_path} - {issue.message}\n")
            
            f.write("\n")
        
        # Extracted data
        if task.extraction_result and task.extraction_result.data:
            f.write("EXTRACTED DATA:\n")
            f.write("-" * 20 + "\n")
            f.write(json.dumps(task.extraction_result.data, indent=2, default=str))
            f.write("\n\n")


def main():
    """Main execution function"""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate inputs
    if not validate_inputs(args):
        sys.exit(1)
    
    # Display startup information
    logger.info("🏛️ Pipeline Manager - Document Processing Script")
    logger.info(f"Document: {args.document_path}")
    logger.info(f"Model: {args.model}")
    logger.info(f"Excel File: {args.excel_file if not args.skip_excel else 'Skipped'}")
    
    if args.dry_run:
        logger.info("🧪 DRY RUN MODE - No changes will be made")
    
    # Process document
    success = process_document(args)
    
    # Exit with appropriate code
    if success:
        logger.info("✅ Processing completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Processing failed")
        sys.exit(1)


if __name__ == "__main__":
    main()