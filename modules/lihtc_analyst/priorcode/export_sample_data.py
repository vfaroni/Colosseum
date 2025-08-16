#!/usr/bin/env python3
"""
Export Sample Data for Enhanced CTCAC Extraction
Generate comprehensive sample showing all 35+ LIHTC data fields
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from wingman_ctcac_extractor_v2 import WingmanCTCACExtractor

def export_comprehensive_sample():
    """Export comprehensive sample of all enhanced LIHTC data fields"""
    
    print("📊 ENHANCED CTCAC DATA SAMPLE EXPORT")
    print("=" * 60)
    
    # Initialize extractor
    extractor = WingmanCTCACExtractor(performance_mode="optimized")
    
    # Get sample files
    raw_data_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data")
    excel_files = list(raw_data_path.glob("*.xlsx"))[:5]  # Get 5 files
    
    if not excel_files:
        print("❌ No Excel files found")
        return
    
    print(f"📁 Processing {len(excel_files)} files for sample export...")
    
    # Extract data from sample files
    results = extractor.extract_batch(excel_files)
    
    # Create comprehensive data export
    export_data = []
    
    for i, result in enumerate(results):
        file_data = create_comprehensive_data_structure(result, i+1)
        export_data.append(file_data)
    
    # Export to multiple formats
    output_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/results/wingman_extraction")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Export to Excel with data labels in Column A
    export_to_excel(export_data, output_dir / f"enhanced_ctcac_sample_{timestamp}.xlsx")
    
    # 2. Export to JSON for detailed review
    export_to_json(export_data, output_dir / f"enhanced_ctcac_sample_{timestamp}.json")
    
    # 3. Export to CSV for easy viewing
    export_to_csv(export_data, output_dir / f"enhanced_ctcac_sample_{timestamp}.csv")
    
    print(f"\n✅ Sample export complete!")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Files exported:")
    print(f"   📈 Excel: enhanced_ctcac_sample_{timestamp}.xlsx")
    print(f"   📋 JSON: enhanced_ctcac_sample_{timestamp}.json") 
    print(f"   📄 CSV: enhanced_ctcac_sample_{timestamp}.csv")
    
    return output_dir / f"enhanced_ctcac_sample_{timestamp}.xlsx"

def create_comprehensive_data_structure(result, file_number):
    """Create comprehensive data structure showing all fields"""
    
    data = {
        "Data Field": [],
        "Description": [],
        f"File_{file_number}_Value": [],
        "Data_Type": [],
        "Category": []
    }
    
    # File metadata
    add_field(data, "filename", "Source filename", result.filename, "string", "Metadata")
    add_field(data, "processing_time_seconds", "Total processing time", result.total_processing_time_seconds, "float", "Performance")
    add_field(data, "memory_usage_mb", "Memory usage", result.memory_usage_mb, "float", "Performance")
    add_field(data, "sections_extracted", f"Sections successfully extracted", result.sections_successfully_extracted, "integer", "Quality")
    add_field(data, "mathematical_validation", "Mathematical validation passed", result.mathematical_validation_passed, "boolean", "Quality")
    
    # Sources & Uses Budget Data
    if result.sources_uses_data:
        su = result.sources_uses_data
        add_field(data, "total_line_items", "Number of budget line items", len(su.line_items), "integer", "Sources_Uses")
        add_field(data, "funding_sources_count", "Number of funding sources", len(su.funding_headers), "integer", "Sources_Uses")
        add_field(data, "data_completeness_percent", "Sources & Uses data completeness", su.data_completeness_percent, "float", "Sources_Uses")
        
        # Sample line items (first 5)
        for i, item in enumerate(su.line_items[:5]):
            if item and item.strip():
                add_field(data, f"line_item_{i+1}", f"Budget line item {i+1}", item, "string", "Sources_Uses")
        
        # Sample costs (first 5)
        for i, cost in enumerate(su.total_costs[:5]):
            if cost > 0:
                add_field(data, f"line_cost_{i+1}", f"Budget cost {i+1}", cost, "float", "Sources_Uses")
        
        # Funding sources
        for i, header in enumerate(su.funding_headers[:5]):
            if header and header.strip():
                add_field(data, f"funding_source_{i+1}", f"Funding source {i+1}", header, "string", "Sources_Uses")
    
    # Basis Breakdown Data
    if result.basis_breakdown_data:
        bb = result.basis_breakdown_data
        add_field(data, "total_eligible_basis", "Total eligible basis (CRITICAL LIHTC)", bb.total_eligible_basis, "float", "Basis_Breakdown")
        add_field(data, "basis_categories_count", "Number of basis categories", len(bb.basis_headers), "integer", "Basis_Breakdown")
        add_field(data, "basis_mathematical_check", "Basis calculations valid", bb.basis_mathematical_check, "boolean", "Basis_Breakdown")
        
        # Basis categories
        for i, header in enumerate(bb.basis_headers[:5]):
            if header and header.strip():
                add_field(data, f"basis_category_{i+1}", f"Basis category {i+1}", header, "string", "Basis_Breakdown")
    
    # Enhanced Application Data
    if result.application_data:
        app = result.application_data
        
        # Project Identification
        add_field(data, "project_name", "Project name", app.project_name, "string", "Project_Info")
        add_field(data, "project_address", "Project address", app.project_address, "string", "Project_Info")
        add_field(data, "project_city", "Project city", app.project_city, "string", "Project_Info")
        add_field(data, "project_county", "Project county", app.project_county, "string", "Project_Info")
        add_field(data, "project_zip", "Project ZIP code", app.project_zip, "string", "Project_Info")
        add_field(data, "census_tract", "Census tract number", app.census_tract, "string", "Project_Info")
        
        # Unit Information
        add_field(data, "total_units", "Total dwelling units", app.total_units, "integer", "Unit_Mix")
        add_field(data, "affordable_units", "Affordable housing units", app.affordable_units, "integer", "Unit_Mix")
        add_field(data, "market_rate_units", "Market rate units", app.market_rate_units, "integer", "Unit_Mix")
        
        # Unit mix by bedroom count
        for unit_type, count in app.unit_mix_details.items():
            add_field(data, f"units_{unit_type.lower()}", f"Number of {unit_type} units", count, "integer", "Unit_Mix")
        
        # AMI Targeting (CRITICAL for LIHTC)
        add_field(data, "ami_levels_served", "AMI levels served", ", ".join(app.ami_levels_served), "string", "AMI_Targeting")
        
        # AMI unit breakdown
        for ami_level, unit_breakdown in app.unit_mix_by_ami.items():
            for unit_type, count in unit_breakdown.items():
                add_field(data, f"ami_{ami_level}_{unit_type}", f"{ami_level} AMI {unit_type} units", count, "integer", "AMI_Targeting")
        
        # Rent Information (CRITICAL for financial analysis)
        for unit_type, rent in app.lihtc_rents_by_unit_type.items():
            add_field(data, f"lihtc_rent_{unit_type.lower()}", f"LIHTC rent {unit_type}", rent, "float", "Rent_Analysis")
        
        for unit_type, rent in app.market_rents_by_unit_type.items():
            add_field(data, f"market_rent_{unit_type.lower()}", f"Market rent {unit_type}", rent, "float", "Rent_Analysis")
        
        # Operating Expenses (CRITICAL for NOI)
        add_field(data, "annual_operating_expenses", "Annual operating expenses", app.annual_operating_expenses, "float", "Operating_Expenses")
        add_field(data, "operating_expense_per_unit", "Operating expense per unit", app.operating_expense_per_unit, "float", "Operating_Expenses")
        
        # Operating expense breakdown
        for expense_type, amount in app.operating_expense_breakdown.items():
            add_field(data, f"expense_{expense_type.lower()}", f"{expense_type.replace('_', ' ')} expense", amount, "float", "Operating_Expenses")
        
        # Developer Information
        add_field(data, "developer_name", "Developer/sponsor name", app.developer_name, "string", "Developer_Info")
        add_field(data, "developer_contact_person", "Developer contact person", app.developer_contact_person, "string", "Developer_Info")
        add_field(data, "developer_phone", "Developer phone number", app.developer_phone, "string", "Developer_Info")
        add_field(data, "developer_email", "Developer email address", app.developer_email, "string", "Developer_Info")
        add_field(data, "general_partner", "General partner name", app.general_partner, "string", "Developer_Info")
        add_field(data, "management_company", "Management company", app.management_company, "string", "Developer_Info")
        
        # Financial Structure (CRITICAL for deal analysis)
        add_field(data, "total_development_cost", "Total development cost", app.total_development_cost, "float", "Financial_Structure")
        add_field(data, "tax_credit_request", "Tax credit request amount", app.tax_credit_request, "float", "Financial_Structure")
        
        # Financing sources
        for source, amount in app.financing_sources.items():
            add_field(data, f"financing_{source.lower()}", f"{source.replace('_', ' ')} amount", amount, "float", "Financial_Structure")
        
        # LIHTC Financial Metrics
        add_field(data, "eligible_basis", "Eligible basis amount", app.eligible_basis, "float", "LIHTC_Metrics")
        add_field(data, "applicable_percentage", "Applicable percentage", app.applicable_percentage, "float", "LIHTC_Metrics")
        add_field(data, "annual_credit_amount", "Annual credit amount", app.annual_credit_amount, "float", "LIHTC_Metrics")
        
        # Construction Details
        add_field(data, "project_type", "Project type", app.project_type, "string", "Construction")
        add_field(data, "construction_type", "Construction type", app.construction_type, "string", "Construction")
        add_field(data, "building_stories", "Number of building stories", app.building_stories, "integer", "Construction")
        add_field(data, "gross_building_area", "Gross building area (sq ft)", app.gross_building_area, "float", "Construction")
        add_field(data, "parking_spaces", "Number of parking spaces", app.parking_spaces, "integer", "Construction")
        
        # Timeline
        add_field(data, "construction_start_date", "Construction start date", app.construction_start_date, "string", "Timeline")
        add_field(data, "construction_completion_date", "Construction completion date", app.construction_completion_date, "string", "Timeline")
        add_field(data, "placed_in_service_date", "Placed in service date", app.placed_in_service_date, "string", "Timeline")
        
        # Special Programs
        add_field(data, "special_needs_population", "Special needs populations", ", ".join(app.special_needs_population), "string", "Special_Programs")
        add_field(data, "green_building_certification", "Green building certification", app.green_building_certification, "string", "Special_Programs")
        
        # Extraction Quality
        add_field(data, "application_extraction_confidence", "Application extraction confidence", app.extraction_confidence, "float", "Quality")
        add_field(data, "application_fields_extracted", "Application fields extracted", app.fields_extracted, "integer", "Quality")
    
    # Points System Data
    if result.points_system_data:
        ps = result.points_system_data
        add_field(data, "total_points_achieved", "Total CTCAC points achieved", ps.total_points_achieved, "float", "Points_System")
        add_field(data, "maximum_possible_points", "Maximum possible points", ps.maximum_possible_points, "float", "Points_System")
        
        # Scoring categories
        for category, points in ps.scoring_categories.items():
            add_field(data, f"points_{category.lower()}", f"{category} points", points, "float", "Points_System")
    
    # Tie-Breaker Data
    if result.tie_breaker_data:
        tb = result.tie_breaker_data
        add_field(data, "cost_per_unit", "Cost per unit (tie-breaker)", tb.cost_per_unit, "float", "Tie_Breaker")
        add_field(data, "tie_breaker_score", "Tie-breaker score", tb.tie_breaker_score, "float", "Tie_Breaker")
        add_field(data, "developer_experience_score", "Developer experience score", tb.developer_experience_score, "float", "Tie_Breaker")
        add_field(data, "leverage_ratio", "Leverage ratio", tb.leverage_ratio, "float", "Tie_Breaker")
    
    # CALHFA Data
    if result.calhfa_addendum_data:
        cf = result.calhfa_addendum_data
        add_field(data, "is_calhfa_deal", "Is CALHFA deal", cf.is_calhfa_deal, "boolean", "CALHFA")
        add_field(data, "calhfa_loan_amount", "CALHFA loan amount", cf.calhfa_loan_amount, "float", "CALHFA")
        add_field(data, "calhfa_loan_terms", "CALHFA loan terms", cf.calhfa_loan_terms, "string", "CALHFA")
    
    # Subsidy Contract Data
    if result.subsidy_contract_data:
        sc = result.subsidy_contract_data
        add_field(data, "has_rental_assistance", "Has rental assistance", sc.has_rental_assistance, "boolean", "Subsidy_Contract")
        add_field(data, "subsidy_amount_monthly", "Monthly subsidy amount", sc.subsidy_amount_monthly, "float", "Subsidy_Contract")
        add_field(data, "subsidy_contract_term", "Subsidy contract term (years)", sc.subsidy_contract_term, "integer", "Subsidy_Contract")
        add_field(data, "subsidy_source", "Subsidy source", sc.subsidy_source, "string", "Subsidy_Contract")
    
    # Proforma Data
    if result.proforma_data:
        pf = result.proforma_data
        add_field(data, "stabilized_noi", "Stabilized NOI", pf.stabilized_noi, "float", "Proforma")
        add_field(data, "debt_service_coverage_ratio", "Debt service coverage ratio", pf.debt_service_coverage_ratio, "float", "Proforma")
        add_field(data, "income_categories_count", "Number of income categories", len(pf.income_categories), "integer", "Proforma")
        add_field(data, "expense_categories_count", "Number of expense categories", len(pf.expense_categories), "integer", "Proforma")
    
    return data

def add_field(data_dict, field_name, description, value, data_type, category):
    """Add a field to the data structure"""
    data_dict["Data Field"].append(field_name)
    data_dict["Description"].append(description)
    data_dict[list(data_dict.keys())[2]].append(value)  # File value column
    data_dict["Data_Type"].append(data_type)
    data_dict["Category"].append(category)

def export_to_excel(export_data, filepath):
    """Export to Excel with data labels in Column A"""
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Create summary sheet
        summary_data = {
            "Export Information": [
                "Export Type",
                "Export Date", 
                "Files Processed",
                "Total Data Fields",
                "Categories Covered",
                "Purpose"
            ],
            "Value": [
                "Enhanced CTCAC Data Sample",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                len(export_data),
                len(export_data[0]["Data Field"]) if export_data else 0,
                "12+ LIHTC categories",
                "Review comprehensive extraction capabilities"
            ]
        }
        
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)
        
        # Create main data sheet with labels in Column A
        if export_data:
            df = pd.DataFrame(export_data[0])
            
            # Add additional files as columns
            for i, file_data in enumerate(export_data[1:], 1):
                df[f"File_{i+1}_Value"] = file_data[f"File_{i+1}_Value"]
            
            df.to_excel(writer, sheet_name="Enhanced_CTCAC_Data", index=False)
        
        # Create category breakdown sheet
        if export_data:
            categories = {}
            for i, category in enumerate(export_data[0]["Category"]):
                if category not in categories:
                    categories[category] = []
                categories[category].append({
                    "Data Field": export_data[0]["Data Field"][i],
                    "Description": export_data[0]["Description"][i],
                    "Data Type": export_data[0]["Data_Type"][i]
                })
            
            for category, fields in categories.items():
                if fields:
                    pd.DataFrame(fields).to_excel(writer, sheet_name=f"Category_{category}", index=False)

def export_to_json(export_data, filepath):
    """Export to JSON for detailed review"""
    
    with open(filepath, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)

def export_to_csv(export_data, filepath):
    """Export to CSV for easy viewing"""
    
    if export_data:
        df = pd.DataFrame(export_data[0])
        
        # Add additional files as columns
        for i, file_data in enumerate(export_data[1:], 1):
            df[f"File_{i+1}_Value"] = file_data[f"File_{i+1}_Value"]
        
        df.to_csv(filepath, index=False)

if __name__ == "__main__":
    export_path = export_comprehensive_sample()
    print(f"\n🎯 REVIEW PATH: {export_path}")