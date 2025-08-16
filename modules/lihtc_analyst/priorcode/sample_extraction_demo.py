#!/usr/bin/env python3
"""
Sample CTCAC Extraction Demo
Extract data from 5 sample applications to demonstrate quality of results
"""

import xlwings as xw
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re

# Import the M4 Beast extractor components
from m4_beast_xlwings_extractor import CTCACProjectData, M4BeastXLWingsExtractor

def create_sample_extractor():
    """Create a focused extractor for sample demonstration"""
    return M4BeastXLWingsExtractor(max_workers=1, enable_benchmarking=True)

def extract_sample_applications(sample_size: int = 5) -> Dict[str, Any]:
    """Extract data from sample CTCAC applications"""
    
    # Setup paths
    raw_data_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data")
    output_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/results/sample_extraction")
    
    # Get sample files (mix of different years and types)
    excel_files = list(raw_data_path.glob("*.xlsx"))
    
    if len(excel_files) < sample_size:
        return {"error": f"Only {len(excel_files)} files found, need {sample_size}"}
    
    # Select diverse sample
    sample_files = []
    
    # Try to get mix of years and types
    for pattern in ["2025_4pct", "2024_4pct", "2023_4pct", "2024_9pct", "2023_9pct"]:
        matching = [f for f in excel_files if pattern in f.name]
        if matching:
            sample_files.append(matching[0])
        if len(sample_files) >= sample_size:
            break
    
    # Fill remaining with any files
    while len(sample_files) < sample_size and len(sample_files) < len(excel_files):
        for f in excel_files:
            if f not in sample_files:
                sample_files.append(f)
                break
    
    sample_files = sample_files[:sample_size]
    
    print(f"🎯 SAMPLE EXTRACTION: {len(sample_files)} CTCAC Applications")
    print("=" * 60)
    
    # Create extractor
    extractor = create_sample_extractor()
    
    # Process each file individually for detailed analysis
    results = []
    total_start_time = time.time()
    
    for i, file_path in enumerate(sample_files, 1):
        print(f"\n📊 Processing Application {i}/{len(sample_files)}: {file_path.name}")
        print("-" * 50)
        
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"📁 File size: {file_size_mb:.1f} MB")
        
        start_time = time.time()
        
        try:
            project_data, metrics = extractor.extract_single_file(file_path)
            processing_time = time.time() - start_time
            
            # Analyze extraction quality
            quality_analysis = analyze_extraction_quality(project_data)
            
            result = {
                "file_info": {
                    "filename": file_path.name,
                    "file_size_mb": file_size_mb,
                    "processing_time_seconds": processing_time
                },
                "extraction_metrics": {
                    "success": metrics.success,
                    "cells_processed": metrics.cells_processed,
                    "fields_extracted": metrics.data_fields_extracted,
                    "extraction_time": metrics.extraction_time_seconds,
                    "memory_usage_mb": metrics.memory_usage_mb
                },
                "project_data": asdict(project_data),
                "quality_analysis": quality_analysis
            }
            
            results.append(result)
            
            # Display key extracted data
            print(f"✅ Extraction successful:")
            print(f"   📊 Processing time: {processing_time:.1f}s")
            print(f"   🔢 Cells processed: {metrics.cells_processed:,}")
            print(f"   📋 Fields extracted: {metrics.data_fields_extracted}")
            print(f"   🏠 Project: {project_data.project_name[:50]}...")
            print(f"   📍 Location: {project_data.project_city}, {project_data.project_county}")
            print(f"   🏢 Units: {project_data.total_units} total, {project_data.affordable_units} affordable")
            print(f"   💰 Total Cost: ${project_data.total_development_cost:,.0f}")
            print(f"   🏗️  Developer: {project_data.developer_name[:30]}...")
            print(f"   🎯 Quality Score: {quality_analysis['overall_quality_score']:.1f}/100")
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            result = {
                "file_info": {
                    "filename": file_path.name,
                    "file_size_mb": file_size_mb,
                    "processing_time_seconds": time.time() - start_time
                },
                "extraction_metrics": {"success": False, "error": str(e)},
                "project_data": {},
                "quality_analysis": {"overall_quality_score": 0}
            }
            results.append(result)
    
    total_time = time.time() - total_start_time
    
    # Generate summary
    summary = generate_extraction_summary(results, total_time)
    
    # Save results
    save_sample_results(results, summary, output_path)
    
    return {
        "success": True,
        "sample_results": results,
        "summary": summary,
        "output_path": str(output_path)
    }

def analyze_extraction_quality(project_data: CTCACProjectData) -> Dict[str, Any]:
    """Analyze the quality of extracted data"""
    
    quality_metrics = {
        "data_completeness": {},
        "data_validity": {},
        "business_logic": {},
        "overall_quality_score": 0
    }
    
    # Core fields completeness
    core_fields = {
        "project_name": project_data.project_name,
        "project_address": project_data.project_address,
        "project_city": project_data.project_city,
        "project_county": project_data.project_county,
        "total_units": project_data.total_units,
        "affordable_units": project_data.affordable_units,
        "total_development_cost": project_data.total_development_cost,
        "developer_name": project_data.developer_name
    }
    
    # Financing fields completeness
    financing_fields = {
        "construction_loan_amount": project_data.construction_loan_amount,
        "construction_loan_lender": project_data.construction_loan_lender,
        "permanent_loan_amount": project_data.permanent_loan_amount,
        "permanent_loan_lender": project_data.permanent_loan_lender,
        "developer_fee": project_data.developer_fee
    }
    
    # Contact fields completeness
    contact_fields = {
        "developer_contact": project_data.developer_contact,
        "developer_phone": project_data.developer_phone,
        "developer_email": project_data.developer_email,
        "management_company": project_data.management_company
    }
    
    # Calculate completeness scores
    def calculate_completeness(fields_dict):
        total_fields = len(fields_dict)
        completed_fields = sum(1 for v in fields_dict.values() if v and str(v).strip())
        return (completed_fields / total_fields * 100) if total_fields > 0 else 0
    
    quality_metrics["data_completeness"] = {
        "core_fields": calculate_completeness(core_fields),
        "financing_fields": calculate_completeness(financing_fields),
        "contact_fields": calculate_completeness(contact_fields),
        "overall_completeness": calculate_completeness({**core_fields, **financing_fields, **contact_fields})
    }
    
    # Data validity checks
    validity_checks = []
    
    # Numeric validations
    if project_data.total_units > 0:
        validity_checks.append("total_units_positive")
    if project_data.total_development_cost > 0:
        validity_checks.append("development_cost_positive")
    if project_data.affordable_units <= project_data.total_units:
        validity_checks.append("affordable_units_logical")
    
    # Text field validations
    if len(project_data.project_name) > 5:
        validity_checks.append("project_name_reasonable")
    if len(project_data.developer_name) > 3:
        validity_checks.append("developer_name_reasonable")
    
    # Email format validation
    if project_data.developer_email and "@" in project_data.developer_email:
        validity_checks.append("email_format_valid")
    
    quality_metrics["data_validity"] = {
        "checks_passed": validity_checks,
        "validity_score": len(validity_checks) / 6 * 100  # 6 total checks
    }
    
    # Business logic validations
    business_logic_score = 0
    business_checks = []
    
    # Financial reasonableness
    if project_data.total_development_cost > 0 and project_data.total_units > 0:
        cost_per_unit = project_data.total_development_cost / project_data.total_units
        if 100000 <= cost_per_unit <= 1000000:  # $100K - $1M per unit is reasonable
            business_checks.append("cost_per_unit_reasonable")
            business_logic_score += 20
    
    # Developer fee reasonableness
    if project_data.developer_fee > 0 and project_data.total_development_cost > 0:
        fee_percent = project_data.developer_fee / project_data.total_development_cost * 100
        if 5 <= fee_percent <= 25:  # 5-25% developer fee is typical
            business_checks.append("developer_fee_reasonable")
            business_logic_score += 20
    
    # Geographic consistency
    if project_data.project_city and project_data.project_county:
        business_checks.append("geographic_data_present")
        business_logic_score += 15
    
    # Construction vs permanent loan logic
    if (project_data.construction_loan_amount > 0 and 
        project_data.permanent_loan_amount > 0 and
        project_data.permanent_loan_amount >= project_data.construction_loan_amount * 0.8):
        business_checks.append("loan_structure_logical")
        business_logic_score += 25
    
    # Contact information completeness
    contact_score = sum([
        1 for field in [project_data.developer_contact, project_data.developer_phone, 
                       project_data.developer_email] if field and str(field).strip()
    ])
    if contact_score >= 2:
        business_checks.append("adequate_contact_info")
        business_logic_score += 20
    
    quality_metrics["business_logic"] = {
        "checks_passed": business_checks,
        "business_logic_score": business_logic_score
    }
    
    # Overall quality score (weighted average)
    overall_score = (
        quality_metrics["data_completeness"]["overall_completeness"] * 0.4 +
        quality_metrics["data_validity"]["validity_score"] * 0.3 +
        business_logic_score * 0.3
    )
    
    quality_metrics["overall_quality_score"] = overall_score
    
    return quality_metrics

def generate_extraction_summary(results: List[Dict], total_time: float) -> Dict[str, Any]:
    """Generate summary statistics for the sample extraction"""
    
    successful_extractions = [r for r in results if r["extraction_metrics"]["success"]]
    
    if not successful_extractions:
        return {"error": "No successful extractions"}
    
    # Performance metrics
    avg_processing_time = sum(r["extraction_metrics"]["extraction_time"] for r in successful_extractions) / len(successful_extractions)
    total_cells = sum(r["extraction_metrics"]["cells_processed"] for r in successful_extractions)
    total_fields = sum(r["extraction_metrics"]["fields_extracted"] for r in successful_extractions)
    
    # Quality metrics
    quality_scores = [r["quality_analysis"]["overall_quality_score"] for r in successful_extractions]
    avg_quality = sum(quality_scores) / len(quality_scores)
    
    # Data analysis
    project_names = [r["project_data"]["project_name"] for r in successful_extractions if r["project_data"]["project_name"]]
    cities = [r["project_data"]["project_city"] for r in successful_extractions if r["project_data"]["project_city"]]
    total_units = [r["project_data"]["total_units"] for r in successful_extractions if r["project_data"]["total_units"] > 0]
    total_costs = [r["project_data"]["total_development_cost"] for r in successful_extractions if r["project_data"]["total_development_cost"] > 0]
    
    return {
        "extraction_performance": {
            "files_processed": len(results),
            "successful_extractions": len(successful_extractions),
            "success_rate": len(successful_extractions) / len(results) * 100,
            "total_processing_time": total_time,
            "avg_processing_time": avg_processing_time,
            "total_cells_processed": total_cells,
            "total_fields_extracted": total_fields,
            "cells_per_second": total_cells / total_time if total_time > 0 else 0
        },
        "data_quality": {
            "avg_quality_score": avg_quality,
            "quality_distribution": {
                "excellent": sum(1 for q in quality_scores if q >= 80),
                "good": sum(1 for q in quality_scores if 60 <= q < 80),
                "fair": sum(1 for q in quality_scores if 40 <= q < 60),
                "poor": sum(1 for q in quality_scores if q < 40)
            }
        },
        "extracted_data_analysis": {
            "projects_with_names": len(project_names),
            "cities_identified": len(cities),
            "unique_cities": len(set(cities)) if cities else 0,
            "projects_with_unit_counts": len(total_units),
            "avg_total_units": sum(total_units) / len(total_units) if total_units else 0,
            "projects_with_costs": len(total_costs),
            "avg_development_cost": sum(total_costs) / len(total_costs) if total_costs else 0,
            "cost_range": {
                "min": min(total_costs) if total_costs else 0,
                "max": max(total_costs) if total_costs else 0
            }
        }
    }

def save_sample_results(results: List[Dict], summary: Dict, output_path: Path):
    """Save sample extraction results"""
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save detailed results
    with open(output_path / "sample_extraction_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save summary
    with open(output_path / "sample_extraction_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    
    # Generate human-readable report
    generate_readable_report(results, summary, output_path)

def generate_readable_report(results: List[Dict], summary: Dict, output_path: Path):
    """Generate human-readable extraction report"""
    
    report_lines = []
    report_lines.append("🎯 CTCAC SAMPLE EXTRACTION REPORT")
    report_lines.append("=" * 60)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Summary section
    perf = summary["extraction_performance"]
    quality = summary["data_quality"]
    data = summary["extracted_data_analysis"]
    
    report_lines.append("📊 EXTRACTION PERFORMANCE")
    report_lines.append("-" * 30)
    report_lines.append(f"Files Processed: {perf['files_processed']}")
    report_lines.append(f"Success Rate: {perf['success_rate']:.1f}%")
    report_lines.append(f"Avg Processing Time: {perf['avg_processing_time']:.1f} seconds")
    report_lines.append(f"Total Cells Processed: {perf['total_cells_processed']:,}")
    report_lines.append(f"Processing Speed: {perf['cells_per_second']:.0f} cells/second")
    report_lines.append("")
    
    report_lines.append("🎯 DATA QUALITY")
    report_lines.append("-" * 30)
    report_lines.append(f"Average Quality Score: {quality['avg_quality_score']:.1f}/100")
    report_lines.append(f"Quality Distribution:")
    for level, count in quality['quality_distribution'].items():
        report_lines.append(f"  {level.title()}: {count} files")
    report_lines.append("")
    
    report_lines.append("📋 EXTRACTED DATA ANALYSIS")
    report_lines.append("-" * 30)
    report_lines.append(f"Projects with Names: {data['projects_with_names']}")
    report_lines.append(f"Cities Identified: {data['cities_identified']} ({data['unique_cities']} unique)")
    report_lines.append(f"Projects with Unit Counts: {data['projects_with_unit_counts']}")
    if data['avg_total_units'] > 0:
        report_lines.append(f"Average Units per Project: {data['avg_total_units']:.1f}")
    report_lines.append(f"Projects with Development Costs: {data['projects_with_costs']}")
    if data['avg_development_cost'] > 0:
        report_lines.append(f"Average Development Cost: ${data['avg_development_cost']:,.0f}")
        report_lines.append(f"Cost Range: ${data['cost_range']['min']:,.0f} - ${data['cost_range']['max']:,.0f}")
    report_lines.append("")
    
    # Individual file details
    report_lines.append("📁 INDIVIDUAL FILE RESULTS")
    report_lines.append("-" * 30)
    
    for i, result in enumerate(results, 1):
        file_info = result["file_info"]
        metrics = result["extraction_metrics"]
        project = result["project_data"]
        quality_analysis = result["quality_analysis"]
        
        report_lines.append(f"\n{i}. {file_info['filename']}")
        report_lines.append(f"   Size: {file_info['file_size_mb']:.1f} MB")
        report_lines.append(f"   Processing: {file_info['processing_time_seconds']:.1f}s")
        
        if metrics["success"]:
            report_lines.append(f"   Fields Extracted: {metrics['fields_extracted']}")
            report_lines.append(f"   Quality Score: {quality_analysis['overall_quality_score']:.1f}/100")
            
            # Key data points
            if project.get("project_name"):
                report_lines.append(f"   Project: {project['project_name'][:40]}...")
            if project.get("project_city"):
                report_lines.append(f"   Location: {project['project_city']}")
            if project.get("total_units"):
                report_lines.append(f"   Units: {project['total_units']}")
            if project.get("developer_name"):
                report_lines.append(f"   Developer: {project['developer_name'][:30]}...")
            if project.get("total_development_cost"):
                report_lines.append(f"   Cost: ${project['total_development_cost']:,.0f}")
        else:
            report_lines.append(f"   ❌ Failed: {metrics.get('error', 'Unknown error')}")
    
    # Save report
    with open(output_path / "sample_extraction_report.txt", "w") as f:
        f.write("\n".join(report_lines))

def main():
    """Run sample extraction demo"""
    
    print("🎯 CTCAC SAMPLE EXTRACTION DEMO")
    print("Demonstrating data extraction quality from 5 sample applications")
    print("=" * 60)
    
    try:
        results = extract_sample_applications(sample_size=5)
        
        if results["success"]:
            summary = results["summary"]
            perf = summary["extraction_performance"]
            quality = summary["data_quality"]
            
            print(f"\n🎉 SAMPLE EXTRACTION COMPLETE!")
            print(f"✅ Success Rate: {perf['success_rate']:.1f}%")
            print(f"⚡ Processing Speed: {perf['cells_per_second']:.0f} cells/second")
            print(f"🎯 Average Quality: {quality['avg_quality_score']:.1f}/100")
            print(f"📊 Results saved to: {results['output_path']}")
            
        else:
            print(f"❌ Extraction failed: {results}")
    
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    main()