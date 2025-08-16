#!/usr/bin/env python3
"""
Test script for the enhanced TDHCA extractor
Tests on a single file for quick validation
"""

from pathlib import Path
import logging
from tdhca_enhanced_extractor_with_address_scoring import EnhancedTDHCAExtractor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_file():
    """Test extraction on a single TDHCA file"""
    
    # Set up paths
    base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites")
    
    # Find a test file - use the validated one from the handoff document
    test_file = base_path / 'Successful_2023_Applications' / 'Dallas_Fort_Worth' / 'TDHCA_23461_Estates_at_Ferguson.pdf'
    
    if not test_file.exists():
        logger.error(f"Test file not found: {test_file}")
        return
    
    logger.info(f"Testing on: {test_file.name}")
    
    # Initialize extractor
    extractor = EnhancedTDHCAExtractor(base_path)
    
    # Process single file
    project_data = extractor.process_application(test_file)
    
    if project_data:
        logger.info("Extraction successful!")
        
        # Display key extracted data
        print("\n=== EXTRACTED DATA ===")
        print(f"Project Name: {project_data.project_name}")
        print(f"Application #: {project_data.application_number}")
        
        print("\n--- ADDRESS INFORMATION ---")
        print(f"Street Address: {project_data.street_address}")
        print(f"City: {project_data.city}")
        print(f"County: {project_data.county}")
        print(f"State: {project_data.state}")
        print(f"ZIP: {project_data.zip_code}")
        print(f"Full Address: {project_data.full_address}")
        
        print("\n--- UNIT INFORMATION ---")
        print(f"Total Units: {project_data.total_units}")
        print(f"Unit Mix: {project_data.unit_mix}")
        print(f"AMI Matrix: {project_data.ami_matrix}")
        
        print("\n--- SCORING INFORMATION ---")
        print(f"Opportunity Index Score: {project_data.opportunity_index_score}")
        print(f"QCT/DDA Status: {project_data.qct_dda_status}")
        print(f"QCT/DDA Boost: {project_data.qct_dda_boost}")
        print(f"Total TDHCA Score: {project_data.total_tdhca_score}")
        print(f"Scoring Breakdown: {project_data.scoring_breakdown}")
        print(f"Award Factors: {project_data.award_factors}")
        
        print("\n--- FINANCIAL DATA ---")
        print(f"Land Cost: ${project_data.land_cost_total:,.0f}")
        print(f"Total Dev Cost: ${project_data.total_development_cost:,.0f}")
        print(f"Developer Fee: ${project_data.developer_fee:,.0f}")
        print(f"LIHTC Equity: ${project_data.lihtc_equity:,.0f}")
        
        print("\n--- DATA QUALITY ---")
        print(f"Confidence Scores: {project_data.confidence_scores}")
        print(f"Processing Notes: {project_data.processing_notes}")
        
        # Save test results
        extractor.save_results([project_data], "test_extraction_results")
        
    else:
        logger.error("Extraction failed!")

if __name__ == "__main__":
    test_single_file()