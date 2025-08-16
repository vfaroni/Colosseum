#!/usr/bin/env python3
"""
LIHTC Application Scoring Analysis - Complete Pipeline

This script integrates all steps of the LIHTC scoring analysis process:
1. Extract scoring data from Excel application files
2. Analyze scoring patterns and compare to total possible scores
3. Generate comprehensive visualizations and reports

Usage:
    python lihtc_scoring_pipeline.py --input_dir /path/to/applications --output_dir /path/to/output
"""

import os
import argparse
import logging
import time
from pathlib import Path

# Import the individual components 
# (Make sure these Python files are in the same directory or properly importable)
from lihtc_score_extractor import LIHTCScoreExtractor
from lihtc_score_analyzer import LIHTCScoreAnalyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("lihtc_scoring_pipeline.log"),
        logging.StreamHandler()
    ]
)

def run_pipeline(input_dir, output_dir, skip_extraction=False, app_type=None, year=None):
    """
    Run the complete LIHTC scoring analysis pipeline.
    
    Args:
        input_dir: Directory containing LIHTC Excel application files
        output_dir: Directory to save the analysis results
        skip_extraction: Whether to skip the extraction step (if already done)
        app_type: Type of application to analyze ('4%', '9%', or None for both)
        year: Year to filter by
    """
    start_time = time.time()
    logging.info("Starting LIHTC Scoring Analysis Pipeline")
    
    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Extract scoring data from Excel files
    if not skip_extraction:
        logging.info("Step 1: Extracting scoring data from Excel files")
        extractor = LIHTCScoreExtractor(input_dir, output_dir)
        extraction_stats = extractor.process_all_files()
        
        logging.info("Extraction complete:")
        for key, value in extraction_stats.items():
            logging.info(f"  {key}: {value}")
    else:
        logging.info("Skipping extraction step as requested")
    
    # Step 2: Analyze scoring data
    logging.info("Step 2: Analyzing extracted scoring data")
    analyzer = LIHTCScoreAnalyzer(output_dir)
    
    # Step 3: Generate comprehensive report
    logging.info("Step 3: Generating comprehensive report")
    report_dir = os.path.join(output_dir, 'reports')
    os.makedirs(report_dir, exist_ok=True)
    
    if app_type:
        # Analyze specific application type
        type_dir = os.path.join(report_dir, app_type.replace('%', 'pct'))
        os.makedirs(type_dir, exist_ok=True)
        
        analyzer.analyze_score_distribution(app_type=app_type, year=year, output_dir=type_dir)
        analyzer.analyze_category_performance(app_type=app_type, year=year, output_dir=type_dir)
        
        year_str = f" for {year}" if year else ""
        logging.info(f"Generated analysis for {app_type} applications{year_str}")
    else:
        # Generate comprehensive report for all data
        analyzer.generate_comprehensive_report(report_dir)
        logging.info("Generated comprehensive report for all application types")
    
    # Log completion and timing
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Pipeline completed in {elapsed_time:.2f} seconds")
    logging.info(f"Results saved to: {output_dir}")

def main():
    """Parse command-line arguments and run the pipeline."""
    parser = argparse.ArgumentParser(
        description='Run the complete LIHTC scoring analysis pipeline'
    )
    parser.add_argument(
        '--input_dir', 
        required=True, 
        help='Directory containing LIHTC Excel application files'
    )
    parser.add_argument(
        '--output_dir', 
        required=True, 
        help='Directory to save the analysis results'
    )
    parser.add_argument(
        '--skip_extraction', 
        action='store_true', 
        help='Skip the extraction step (if already done)'
    )
    parser.add_argument(
        '--app_type', 
        choices=['4%', '9%'], 
        help='Type of application to analyze (if not specified, analyze both)'
    )
    parser.add_argument(
        '--year', 
        type=int, 
        help='Year to filter by'
    )
    
    args = parser.parse_args()
    
    # Validate input directory
    if not os.path.isdir(args.input_dir):
        logging.error(f"Input directory does not exist: {args.input_dir}")
        return 1
    
    # Run the pipeline
    try:
        run_pipeline(
            args.input_dir, 
            args.output_dir, 
            args.skip_extraction, 
            args.app_type, 
            args.year
        )
        return 0
    except Exception as e:
        logging.error(f"Error running pipeline: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit(main())