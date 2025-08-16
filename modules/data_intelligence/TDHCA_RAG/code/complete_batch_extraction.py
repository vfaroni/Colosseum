#!/usr/bin/env python3
"""
Complete TDHCA Batch Extraction - All 38 Applications
Production system for comprehensive data extraction with checkpoints
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import logging
from targeted_tdhca_extractor import TargetedTDHCAExtractor, TargetedProjectData

def setup_logging():
    """Setup logging for batch processing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('complete_batch_extraction.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_checkpoint() -> Dict:
    """Load processing checkpoint"""
    checkpoint_file = Path("complete_batch_checkpoint.json")
    if checkpoint_file.exists():
        with open(checkpoint_file, 'r') as f:
            return json.load(f)
    return {"completed_files": [], "results": []}

def save_checkpoint(checkpoint_data: Dict):
    """Save processing checkpoint"""
    with open("complete_batch_checkpoint.json", 'w') as f:
        json.dump(checkpoint_data, f, indent=2, default=str)

def process_single_file(extractor: TargetedTDHCAExtractor, pdf_file: Path, logger) -> Dict:
    """Process a single PDF file"""
    logger.info(f"Processing {pdf_file.name}")
    
    try:
        start_time = datetime.now()
        result = extractor.process_targeted_application(pdf_file)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Convert to dict for storage
        result_dict = {
            'filename': result.filename,
            'project_name': result.project_name,
            'street_address': result.street_address,
            'city': result.city,
            'county': result.county,
            'zip_code': result.zip_code,
            'total_units': result.total_units,
            'unit_mix': result.unit_mix,
            'unit_square_footage': result.unit_square_footage,
            'unit_rents': result.unit_rents,
            'total_development_cost': result.total_development_cost,
            'development_cost_per_unit': result.development_cost_per_unit,
            'site_acquisition_cost': result.site_acquisition_cost,
            'building_acquisition_cost': result.building_acquisition_cost,
            'total_hard_costs': result.total_hard_costs,
            'total_soft_costs': result.total_soft_costs,
            'developer_fee': result.developer_fee,
            'general_contractor_fee': result.general_contractor_fee,
            'architectural_fees': result.architectural_fees,
            'engineering_fees': result.engineering_fees,
            'legal_fees': result.legal_fees,
            'housing_tax_credit_equity': result.housing_tax_credit_equity,
            'construction_loan': result.construction_loan,
            'permanent_loan': result.permanent_loan,
            'government_grants': result.government_grants,
            'developer_cash_equity': result.developer_cash_equity,
            'developer_name': result.developer_name,
            'general_contractor': result.general_contractor,
            'architect': result.architect,
            'management_company': result.management_company,
            'ami_breakdown': result.ami_breakdown,
            'extraction_confidence': result.extraction_confidence,
            'processing_time_seconds': processing_time,
            'processing_notes': result.processing_notes
        }
        
        logger.info(f"✅ {result.project_name or 'Unknown Project'} - Confidence: {result.extraction_confidence:.2f}")
        return result_dict
        
    except Exception as e:
        logger.error(f"❌ Error processing {pdf_file.name}: {str(e)}")
        return {
            'filename': pdf_file.name,
            'error': str(e),
            'processing_time_seconds': 0,
            'extraction_confidence': 0.0,
            'processing_notes': [f"Error: {str(e)}"]
        }

def create_comprehensive_excel_report(results: List[Dict], timestamp: str):
    """Create detailed Excel report with multiple analysis sheets"""
    
    excel_file = f"TDHCA_Complete_Analysis_{timestamp}.xlsx"
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # 1. Complete Raw Data
        df_all = pd.DataFrame(results)
        df_all.to_excel(writer, sheet_name='Complete_Raw_Data', index=False)
        
        # 2. Successful extractions only
        successful_results = [r for r in results if 'error' not in r]
        if successful_results:
            df_success = pd.DataFrame(successful_results)
            df_success.to_excel(writer, sheet_name='Successful_Extractions', index=False)
        
        # 3. Financial Summary - Key metrics only
        financial_summary = []
        for r in successful_results:
            financial_summary.append({
                'Project_Name': r.get('project_name', ''),
                'City': r.get('city', ''),
                'County': r.get('county', ''),
                'ZIP_Code': r.get('zip_code', ''),
                'Total_Units': r.get('total_units', 0),
                'Total_Development_Cost': r.get('total_development_cost', 0),
                'Cost_Per_Unit': r.get('development_cost_per_unit', 0),
                'Site_Acquisition_Cost': r.get('site_acquisition_cost', 0),
                'Total_Hard_Costs': r.get('total_hard_costs', 0),
                'Total_Soft_Costs': r.get('total_soft_costs', 0),
                'Developer_Fee': r.get('developer_fee', 0),
                'Developer_Name': r.get('developer_name', '')[:50],  # Truncate long names
                'General_Contractor': r.get('general_contractor', '')[:50],
                'Confidence_Rating': f"{r.get('extraction_confidence', 0):.3f}",
                'Unit_Mix': str(r.get('unit_mix', {})),
                'Processing_Time': f"{r.get('processing_time_seconds', 0):.1f}s"
            })
        
        if financial_summary:
            df_financial = pd.DataFrame(financial_summary)
            df_financial.to_excel(writer, sheet_name='Financial_Summary', index=False)
        
        # 4. Confidence Analysis
        confidence_ranges = [
            ('High (>0.50)', [r for r in successful_results if r.get('extraction_confidence', 0) > 0.5]),
            ('Medium (0.25-0.50)', [r for r in successful_results if 0.25 <= r.get('extraction_confidence', 0) <= 0.5]),
            ('Low (<0.25)', [r for r in successful_results if r.get('extraction_confidence', 0) < 0.25])
        ]
        
        confidence_analysis = []
        for range_name, range_results in confidence_ranges:
            if range_results:
                projects_with_costs = [r for r in range_results if r.get('total_development_cost', 0) > 0]
                projects_with_fees = [r for r in range_results if r.get('developer_fee', 0) > 0]
                
                avg_dev_cost = sum(r.get('total_development_cost', 0) for r in projects_with_costs) / len(projects_with_costs) if projects_with_costs else 0
                avg_dev_fee = sum(r.get('developer_fee', 0) for r in projects_with_fees) / len(projects_with_fees) if projects_with_fees else 0
                
                confidence_analysis.append({
                    'Confidence_Range': range_name,
                    'Number_of_Projects': len(range_results),
                    'Projects_with_Dev_Cost': len(projects_with_costs),
                    'Projects_with_Dev_Fee': len(projects_with_fees),
                    'Avg_Development_Cost': f"${avg_dev_cost:,.0f}" if avg_dev_cost > 0 else 'N/A',
                    'Avg_Developer_Fee': f"${avg_dev_fee:,.0f}" if avg_dev_fee > 0 else 'N/A',
                    'Projects_with_Unit_Mix': len([r for r in range_results if r.get('unit_mix')]),
                    'Projects_with_Team_Data': len([r for r in range_results if r.get('developer_name')])
                })
        
        if confidence_analysis:
            df_confidence = pd.DataFrame(confidence_analysis)
            df_confidence.to_excel(writer, sheet_name='Confidence_Analysis', index=False)
        
        # 5. Executive Summary
        if successful_results:
            costs_available = [r for r in successful_results if r.get('total_development_cost', 0) > 0]
            fees_available = [r for r in successful_results if r.get('developer_fee', 0) > 0]
            
            summary_data = {
                'Metric': [
                    'Total Applications Processed',
                    'Successful Extractions',
                    'Success Rate (%)',
                    'Files with Errors',
                    'Average Processing Time (seconds)',
                    'Average Confidence Score',
                    'High Confidence Extractions (>0.5)',
                    'Medium Confidence Extractions (0.25-0.5)',
                    'Low Confidence Extractions (<0.25)',
                    'Projects with Development Costs',
                    'Projects with Developer Fees',
                    'Projects with Unit Mix Data',
                    'Projects with Team Information',
                    'Total Combined Development Cost',
                    'Average Development Cost',
                    'Median Development Cost',
                    'Average Developer Fee',
                    'Total Processing Time (minutes)'
                ],
                'Value': [
                    len(results),
                    len(successful_results),
                    f"{len(successful_results)/len(results)*100:.1f}",
                    len([r for r in results if 'error' in r]),
                    f"{sum(r.get('processing_time_seconds', 0) for r in successful_results)/len(successful_results):.1f}" if successful_results else 0,
                    f"{sum(r.get('extraction_confidence', 0) for r in successful_results)/len(successful_results):.3f}" if successful_results else 0,
                    len([r for r in successful_results if r.get('extraction_confidence', 0) > 0.5]),
                    len([r for r in successful_results if 0.25 <= r.get('extraction_confidence', 0) <= 0.5]),
                    len([r for r in successful_results if r.get('extraction_confidence', 0) < 0.25]),
                    len(costs_available),
                    len(fees_available),
                    len([r for r in successful_results if r.get('unit_mix')]),
                    len([r for r in successful_results if r.get('developer_name')]),
                    f"${sum(r.get('total_development_cost', 0) for r in costs_available):,.0f}",
                    f"${sum(r.get('total_development_cost', 0) for r in costs_available)/len(costs_available):,.0f}" if costs_available else 'N/A',
                    f"${sorted([r.get('total_development_cost', 0) for r in costs_available])[len(costs_available)//2]:,.0f}" if len(costs_available) > 0 else 'N/A',
                    f"${sum(r.get('developer_fee', 0) for r in fees_available)/len(fees_available):,.0f}" if fees_available else 'N/A',
                    f"{sum(r.get('processing_time_seconds', 0) for r in successful_results)/60:.1f}" if successful_results else 0
                ]
            }
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Executive_Summary', index=False)
    
    return excel_file

def main():
    """Main execution function"""
    logger = setup_logging()
    
    print("🏆 COMPLETE TDHCA BATCH EXTRACTION")
    print("=" * 60)
    print("Processing ALL 38 successful TDHCA 4% applications")
    print("Target: High-value financial data with confidence ratings")
    print()
    
    # Load checkpoint
    checkpoint = load_checkpoint()
    completed_files = set(checkpoint.get("completed_files", []))
    results = checkpoint.get("results", [])
    
    # Initialize extractor
    extractor = TargetedTDHCAExtractor("")
    
    # Find all PDF files
    base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites")
    all_pdf_files = list(base_path.glob("**/*.pdf"))
    
    # Filter out already completed files
    remaining_files = [f for f in all_pdf_files if f.name not in completed_files]
    
    logger.info(f"📁 Found {len(all_pdf_files)} total PDF files")
    logger.info(f"✅ Already completed: {len(completed_files)} files")
    logger.info(f"⏳ Remaining to process: {len(remaining_files)} files")
    
    if not remaining_files:
        logger.info("🎉 All files already processed! Creating final report...")
    else:
        # Process remaining files
        for i, pdf_file in enumerate(remaining_files, 1):
            logger.info(f"\n📊 Processing {i}/{len(remaining_files)}: {pdf_file.name}")
            
            result = process_single_file(extractor, pdf_file, logger)
            results.append(result)
            completed_files.add(pdf_file.name)
            
            # Save checkpoint after each file
            checkpoint_data = {
                "completed_files": list(completed_files),
                "results": results,
                "last_updated": datetime.now().isoformat()
            }
            save_checkpoint(checkpoint_data)
            
            # Brief pause to prevent system overload
            if i % 5 == 0:
                logger.info(f"💾 Checkpoint saved. Processed {i}/{len(remaining_files)} files")
    
    # Create comprehensive Excel report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file = create_comprehensive_excel_report(results, timestamp)
    
    # Final summary
    successful_results = [r for r in results if 'error' not in r]
    
    print("\n🎯 EXTRACTION COMPLETE!")
    print("=" * 50)
    print(f"✅ Total Files Processed: {len(results)}")
    print(f"📈 Successful Extractions: {len(successful_results)}")
    print(f"📊 Success Rate: {len(successful_results)/len(results)*100:.1f}%")
    print(f"⭐ High Confidence (>0.5): {len([r for r in successful_results if r.get('extraction_confidence', 0) > 0.5])}")
    print(f"💰 Projects with Financial Data: {len([r for r in successful_results if r.get('total_development_cost', 0) > 0])}")
    print(f"🏠 Projects with Unit Mix: {len([r for r in successful_results if r.get('unit_mix')])}")
    print()
    print(f"📊 COMPREHENSIVE EXCEL REPORT: {excel_file}")
    print("   • Complete_Raw_Data: All extraction results")
    print("   • Financial_Summary: Key financial metrics with confidence ratings")
    print("   • Confidence_Analysis: Quality breakdown by confidence level")
    print("   • Executive_Summary: High-level statistics and totals")
    
    # Show top financial extractions
    costs_available = [r for r in successful_results if r.get('total_development_cost', 0) > 0]
    if costs_available:
        print(f"\n💰 TOP FINANCIAL EXTRACTIONS:")
        sorted_costs = sorted(costs_available, key=lambda x: x.get('total_development_cost', 0), reverse=True)
        for r in sorted_costs[:5]:
            print(f"   📋 {r.get('project_name', 'Unknown')[:30]}: ${r.get('total_development_cost', 0):,.0f} (Confidence: {r.get('extraction_confidence', 0):.2f})")
    
    return excel_file

if __name__ == "__main__":
    excel_report = main()