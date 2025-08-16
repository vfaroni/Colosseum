#!/usr/bin/env python3
"""
Test WINGMAN Validation Suite
Comprehensive validation analysis of extraction results
"""

import json
from pathlib import Path
from ctcac_validation_suite import CTCACValidationSuite
from ctcac_data_structures import CTCACExtractionResult

def test_wingman_validation():
    """Test validation suite on latest WINGMAN results"""
    
    print("🔍 WINGMAN VALIDATION SUITE TEST")
    print("=" * 50)
    
    # Load latest extraction results
    results_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/results/wingman_extraction")
    results_files = list(results_dir.glob("wingman_extraction_results_*.json"))
    
    if not results_files:
        print("❌ No WINGMAN results found for validation")
        return
    
    # Get latest results file
    latest_results_file = sorted(results_files)[-1]
    print(f"📁 Loading results: {latest_results_file.name}")
    
    with open(latest_results_file, "r") as f:
        results_data = json.load(f)
    
    # Convert to CTCACExtractionResult objects
    extraction_results = []
    for result_dict in results_data:
        # Create CTCACExtractionResult from dict data
        result = CTCACExtractionResult()
        
        # Basic metadata
        result.filename = result_dict.get("filename", "")
        result.total_processing_time_seconds = result_dict.get("total_processing_time_seconds", 0)
        result.overall_extraction_confidence = result_dict.get("overall_extraction_confidence", 0)
        result.memory_usage_mb = result_dict.get("memory_usage_mb", 0)
        result.sections_successfully_extracted = result_dict.get("sections_successfully_extracted", 0)
        result.sections_attempted = result_dict.get("sections_attempted", 0)
        result.mathematical_validation_passed = result_dict.get("mathematical_validation_passed", False)
        result.cells_processed = result_dict.get("cells_processed", 0)
        result.extraction_errors = result_dict.get("extraction_errors", [])
        result.extraction_warnings = result_dict.get("extraction_warnings", [])
        
        # Calculate cells per second
        if result.total_processing_time_seconds > 0:
            result.cells_per_second = result.cells_processed / result.total_processing_time_seconds
        
        extraction_results.append(result)
    
    print(f"✅ Loaded {len(extraction_results)} extraction results")
    
    # Initialize validation suite
    validator = CTCACValidationSuite(tolerance=1.0)
    
    # Generate comprehensive validation report
    validation_report = validator.generate_validation_report(extraction_results)
    
    # Display detailed analysis
    print(f"\n📊 DETAILED VALIDATION ANALYSIS")
    print("=" * 50)
    
    for i, result in enumerate(extraction_results):
        print(f"\n📄 File {i+1}: {result.filename}")
        print(f"   ⏱️  Processing time: {result.total_processing_time_seconds:.2f}s")
        print(f"   🎯 Confidence: {result.overall_extraction_confidence:.1f}%")
        print(f"   📊 Sections extracted: {result.sections_successfully_extracted}/{result.sections_attempted}")
        print(f"   🔢 Cells processed: {result.cells_processed}")
        print(f"   💾 Memory used: {result.memory_usage_mb:.1f} MB")
        print(f"   ✅ Math validation: {'PASSED' if result.mathematical_validation_passed else 'FAILED'}")
        
        if result.extraction_errors:
            print(f"   ❌ Errors: {len(result.extraction_errors)}")
            for error in result.extraction_errors[:2]:  # Show first 2 errors
                print(f"      • {error}")
    
    # Export detailed validation report
    timestamp = latest_results_file.stem.split('_')[-1]
    validation_report_file = results_dir / f"wingman_validation_report_{timestamp}.json"
    
    with open(validation_report_file, "w") as f:
        json.dump(validation_report, f, indent=2, default=str)
    
    print(f"\n💾 Detailed validation report saved to: {validation_report_file}")
    
    # Mission assessment
    mission_success = validation_report["mission_targets"]["overall_mission_success"]
    
    if mission_success:
        print(f"\n🎊 MISSION WINGMAN-01 SUCCESS!")
        print(f"✅ Phase 1A complete - ready for Phase 1B")
        print(f"🚀 Integration with QAP RAG approved")
    else:
        print(f"\n🔧 MISSION WINGMAN-01 needs optimization")
        print(f"📊 Current status: Phase 1A requires improvement")
        
        # Specific recommendations
        if validation_report["validation_summary"]["average_validation_score"] < 70:
            print(f"⚠️  Recommendation: Improve data extraction accuracy")
        if validation_report["performance_summary"]["average_processing_time"] > 5.0:
            print(f"⚠️  Recommendation: Optimize processing speed")
        if validation_report["validation_summary"]["mathematical_accuracy_rate"] < 99:
            print(f"⚠️  Recommendation: Fix mathematical validation logic")

if __name__ == "__main__":
    test_wingman_validation()