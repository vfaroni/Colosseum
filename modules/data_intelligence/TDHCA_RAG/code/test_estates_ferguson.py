#!/usr/bin/env python3
"""
Test enhanced extractor on the validated Estates at Ferguson application
This is the 20.5MB file that was successfully tested in the proof-of-concept
"""

from pathlib import Path
import logging
import json
from tdhca_enhanced_extractor_with_address_scoring import EnhancedTDHCAExtractor, EnhancedProjectData

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_estates_ferguson():
    """Test on the validated Estates at Ferguson application"""
    
    # Set up paths
    base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites")
    
    # The validated test file from the handoff document
    test_file = base_path / 'Successful_2023_Applications' / 'Dallas_Fort_Worth' / 'TDHCA_23461_Estates_at_Ferguson.pdf'
    
    if not test_file.exists():
        logger.error(f"Test file not found: {test_file}")
        return
    
    logger.info(f"Testing on validated file: {test_file.name}")
    logger.info(f"File size: {test_file.stat().st_size / 1024 / 1024:.1f} MB")
    
    # Initialize extractor with limited pages for faster processing
    extractor = EnhancedTDHCAExtractor(base_path)
    
    # Override the extract_pdf_text method to limit pages
    original_method = extractor.extract_pdf_text
    def limited_extract(pdf_path, max_pages=150):
        return original_method(pdf_path, max_pages=max_pages)
    extractor.extract_pdf_text = limited_extract
    
    logger.info("Processing application (limited to first 150 pages for speed)...")
    
    # Process the application
    project_data = extractor.process_application(test_file)
    
    if project_data:
        print("\n" + "="*60)
        print("EXTRACTION RESULTS - ESTATES AT FERGUSON")
        print("="*60)
        
        # Expected values from handoff document
        print("\n📋 EXPECTED VALUES (from proof-of-concept):")
        print("- Units: 99x 1BR (716 sq ft) + 65x 2BR (1005 sq ft) = 164 total")
        print("- AMI: 16 units at 50% + 148 units at 60%")
        print("- Land Cost: $3,960,000")
        print("- Property Type: Senior housing")
        
        print("\n✅ EXTRACTED VALUES:")
        
        # Basic Information
        print(f"\n🏢 PROJECT INFORMATION:")
        print(f"Project Name: {project_data.project_name}")
        print(f"Application #: {project_data.application_number}")
        print(f"Property Type: {project_data.property_type}")
        print(f"Target Population: {project_data.targeted_population}")
        
        # Address Information
        print(f"\n📍 ADDRESS INFORMATION:")
        print(f"Street Address: {project_data.street_address}")
        print(f"City: {project_data.city}")
        print(f"County: {project_data.county}")
        print(f"State: {project_data.state}")
        print(f"ZIP Code: {project_data.zip_code}")
        print(f"Full Address: {project_data.full_address}")
        print(f"Census Tract: {project_data.census_tract}")
        
        # Unit Information
        print(f"\n🏠 UNIT INFORMATION:")
        print(f"Total Units: {project_data.total_units}")
        print(f"Unit Mix: {json.dumps(project_data.unit_mix, indent=2)}")
        print(f"Unit Square Footage: {json.dumps(project_data.unit_square_footage, indent=2)}")
        
        # AMI Matrix
        print(f"\n💰 AMI SET-ASIDES:")
        for ami_level, units in project_data.ami_matrix.items():
            if units:
                print(f"{ami_level}: {json.dumps(units)}")
        
        # Financial Data
        print(f"\n💵 FINANCIAL DATA:")
        print(f"Land Cost Total: ${project_data.land_cost_total:,.0f}")
        print(f"Land Acres: {project_data.land_acres}")
        print(f"Land Cost per Acre: ${project_data.land_cost_per_acre:,.0f}")
        print(f"Total Development Cost: ${project_data.total_development_cost:,.0f}")
        print(f"Developer Fee: ${project_data.developer_fee:,.0f}")
        print(f"LIHTC Equity: ${project_data.lihtc_equity:,.0f}")
        
        # Scoring Information
        print(f"\n🏆 TDHCA SCORING INFORMATION:")
        print(f"Opportunity Index Score: {project_data.opportunity_index_score}")
        print(f"QCT/DDA Status: {project_data.qct_dda_status}")
        print(f"QCT/DDA Boost Eligible: {project_data.qct_dda_boost}")
        print(f"Total TDHCA Score: {project_data.total_tdhca_score}")
        
        if project_data.scoring_breakdown:
            print(f"Scoring Breakdown: {json.dumps(project_data.scoring_breakdown, indent=2)}")
        
        if project_data.proximity_scores:
            print(f"\nProximity Scores:")
            for item, distance in project_data.proximity_scores.items():
                print(f"  {item}: {distance} miles")
        
        if project_data.award_factors:
            print(f"\nAward Factors:")
            for factor in project_data.award_factors:
                print(f"  - {factor}")
        
        # Data Quality
        print(f"\n📊 DATA QUALITY:")
        print(f"Confidence Scores:")
        for category, score in project_data.confidence_scores.items():
            print(f"  {category}: {score:.2f}")
        
        if project_data.processing_notes:
            print(f"\nProcessing Notes:")
            for note in project_data.processing_notes:
                print(f"  ⚠️  {note}")
        
        # Save detailed results
        output_dir = base_path / 'enhanced_extraction_results'
        output_dir.mkdir(exist_ok=True)
        
        # Save as JSON
        output_file = output_dir / 'estates_ferguson_test_results.json'
        with open(output_file, 'w') as f:
            # Convert to dict for JSON serialization
            result_dict = {
                'application_number': project_data.application_number,
                'project_name': project_data.project_name,
                'address_info': {
                    'street_address': project_data.street_address,
                    'city': project_data.city,
                    'county': project_data.county,
                    'state': project_data.state,
                    'zip_code': project_data.zip_code,
                    'full_address': project_data.full_address,
                    'census_tract': project_data.census_tract
                },
                'unit_info': {
                    'total_units': project_data.total_units,
                    'unit_mix': project_data.unit_mix,
                    'unit_square_footage': project_data.unit_square_footage,
                    'ami_matrix': project_data.ami_matrix
                },
                'financial_data': {
                    'land_cost_total': project_data.land_cost_total,
                    'total_development_cost': project_data.total_development_cost,
                    'developer_fee': project_data.developer_fee,
                    'lihtc_equity': project_data.lihtc_equity
                },
                'scoring_info': {
                    'opportunity_index_score': project_data.opportunity_index_score,
                    'qct_dda_status': project_data.qct_dda_status,
                    'total_tdhca_score': project_data.total_tdhca_score,
                    'scoring_breakdown': project_data.scoring_breakdown,
                    'award_factors': project_data.award_factors
                },
                'confidence_scores': project_data.confidence_scores,
                'processing_notes': project_data.processing_notes
            }
            json.dump(result_dict, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {output_file}")
        
    else:
        logger.error("❌ Extraction failed!")

if __name__ == "__main__":
    test_estates_ferguson()