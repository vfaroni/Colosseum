#!/usr/bin/env python3
"""
Simple Data Export for Enhanced CTCAC Extraction
Generate sample showing all LIHTC data fields with labels in Column A
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def create_simple_sample_export():
    """Create a simple sample export from recent extraction results"""
    
    print("📊 SIMPLE ENHANCED CTCAC DATA EXPORT")
    print("=" * 50)
    
    # Load the most recent extraction results
    results_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/results/wingman_extraction")
    results_files = list(results_dir.glob("wingman_extraction_results_*.json"))
    
    if not results_files:
        print("❌ No extraction results found")
        return
    
    # Get the latest results file
    latest_results_file = sorted(results_files)[-1]
    print(f"📁 Using results: {latest_results_file.name}")
    
    with open(latest_results_file, "r") as f:
        results_data = json.load(f)
    
    # Create data structure for export
    export_data = []
    
    # Process up to 3 files for sample
    for i, result in enumerate(results_data[:3]):
        file_sample = create_file_sample(result, i+1)
        export_data.append(file_sample)
    
    # Create consolidated view with data labels in Column A
    consolidated_data = create_consolidated_view(export_data)
    
    # Export to files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/results/wingman_extraction")
    
    # Export to Excel
    excel_file = output_dir / f"ctcac_data_sample_{timestamp}.xlsx"
    export_to_excel(consolidated_data, excel_file)
    
    # Export to CSV  
    csv_file = output_dir / f"ctcac_data_sample_{timestamp}.csv"
    export_to_csv(consolidated_data, csv_file)
    
    print(f"\n✅ Sample export complete!")
    print(f"📊 Excel file: {excel_file}")
    print(f"📄 CSV file: {csv_file}")
    print(f"\n🎯 REVIEW PATH: {excel_file}")
    
    return excel_file

def create_file_sample(result_dict, file_number):
    """Create sample data from a single extraction result"""
    
    sample = {
        "category": [],
        "field_name": [], 
        "description": [],
        "value": [],
        "data_type": []
    }
    
    # File metadata
    add_sample_field(sample, "Metadata", "filename", "Source filename", result_dict.get("filename", ""), "string")
    add_sample_field(sample, "Performance", "processing_time", "Processing time (seconds)", result_dict.get("total_processing_time_seconds", 0), "float")
    add_sample_field(sample, "Performance", "memory_usage", "Memory usage (MB)", result_dict.get("memory_usage_mb", 0), "float")
    add_sample_field(sample, "Quality", "sections_extracted", "Sections successfully extracted", result_dict.get("sections_successfully_extracted", 0), "integer")
    add_sample_field(sample, "Quality", "math_validation", "Mathematical validation passed", result_dict.get("mathematical_validation_passed", False), "boolean")
    add_sample_field(sample, "Quality", "overall_confidence", "Overall extraction confidence (%)", result_dict.get("overall_extraction_confidence", 0), "float")
    
    # Sources & Uses Data (from the actual structure we know exists)
    if "sources_uses_data" in result_dict and result_dict["sources_uses_data"]:
        su_data = result_dict["sources_uses_data"]
        if isinstance(su_data, dict):
            add_sample_field(sample, "Sources_Uses", "line_items_count", "Number of budget line items", len(su_data.get("line_items", [])), "integer")
            add_sample_field(sample, "Sources_Uses", "funding_sources_count", "Number of funding sources", len(su_data.get("funding_headers", [])), "integer")
            add_sample_field(sample, "Sources_Uses", "data_completeness", "Sources & Uses completeness (%)", su_data.get("data_completeness_percent", 0), "float")
            
            # Sample line items
            line_items = su_data.get("line_items", [])
            for i, item in enumerate(line_items[:5]):
                if item and str(item).strip():
                    add_sample_field(sample, "Sources_Uses", f"line_item_{i+1}", f"Budget line item {i+1}", str(item), "string")
            
            # Sample funding sources
            funding_headers = su_data.get("funding_headers", [])
            for i, header in enumerate(funding_headers[:5]):
                if header and str(header).strip():
                    add_sample_field(sample, "Sources_Uses", f"funding_source_{i+1}", f"Funding source {i+1}", str(header), "string")
    
    # Enhanced Application Data Fields (what we're targeting to extract)
    add_sample_field(sample, "Project_Info", "project_name", "Project name", "Extraction pending", "string")
    add_sample_field(sample, "Project_Info", "project_address", "Project address", "Extraction pending", "string")
    add_sample_field(sample, "Project_Info", "project_city", "Project city", "Extraction pending", "string")
    add_sample_field(sample, "Project_Info", "project_county", "Project county", "Extraction pending", "string")
    add_sample_field(sample, "Project_Info", "census_tract", "Census tract number", "Extraction pending", "string")
    
    add_sample_field(sample, "Unit_Mix", "total_units", "Total dwelling units", "Extraction pending", "integer")
    add_sample_field(sample, "Unit_Mix", "affordable_units", "Affordable housing units", "Extraction pending", "integer")
    add_sample_field(sample, "Unit_Mix", "market_rate_units", "Market rate units", "Extraction pending", "integer")
    add_sample_field(sample, "Unit_Mix", "studio_units", "Studio/efficiency units", "Extraction pending", "integer")
    add_sample_field(sample, "Unit_Mix", "one_br_units", "One bedroom units", "Extraction pending", "integer")
    add_sample_field(sample, "Unit_Mix", "two_br_units", "Two bedroom units", "Extraction pending", "integer")
    add_sample_field(sample, "Unit_Mix", "three_br_units", "Three bedroom units", "Extraction pending", "integer")
    
    add_sample_field(sample, "AMI_Targeting", "ami_levels_served", "AMI levels served", "Extraction pending", "string")
    add_sample_field(sample, "AMI_Targeting", "30_ami_units", "30% AMI units", "Extraction pending", "integer")
    add_sample_field(sample, "AMI_Targeting", "50_ami_units", "50% AMI units", "Extraction pending", "integer")
    add_sample_field(sample, "AMI_Targeting", "60_ami_units", "60% AMI units", "Extraction pending", "integer")
    add_sample_field(sample, "AMI_Targeting", "80_ami_units", "80% AMI units", "Extraction pending", "integer")
    
    add_sample_field(sample, "Rent_Analysis", "lihtc_rent_1br", "LIHTC rent - 1 bedroom", "Extraction pending", "float")
    add_sample_field(sample, "Rent_Analysis", "lihtc_rent_2br", "LIHTC rent - 2 bedroom", "Extraction pending", "float")
    add_sample_field(sample, "Rent_Analysis", "market_rent_1br", "Market rent - 1 bedroom", "Extraction pending", "float")
    add_sample_field(sample, "Rent_Analysis", "market_rent_2br", "Market rent - 2 bedroom", "Extraction pending", "float")
    
    add_sample_field(sample, "Operating_Expenses", "annual_operating_expenses", "Annual operating expenses", "Extraction pending", "float")
    add_sample_field(sample, "Operating_Expenses", "property_taxes", "Property taxes", "Extraction pending", "float")
    add_sample_field(sample, "Operating_Expenses", "insurance", "Insurance", "Extraction pending", "float")
    add_sample_field(sample, "Operating_Expenses", "management_fees", "Management fees", "Extraction pending", "float")
    add_sample_field(sample, "Operating_Expenses", "maintenance", "Maintenance", "Extraction pending", "float")
    add_sample_field(sample, "Operating_Expenses", "expense_per_unit", "Operating expense per unit", "Extraction pending", "float")
    
    add_sample_field(sample, "Developer_Info", "developer_name", "Developer/sponsor name", "Extraction pending", "string")
    add_sample_field(sample, "Developer_Info", "developer_contact", "Developer contact person", "Extraction pending", "string")
    add_sample_field(sample, "Developer_Info", "developer_phone", "Developer phone", "Extraction pending", "string")
    add_sample_field(sample, "Developer_Info", "developer_email", "Developer email", "Extraction pending", "string")
    add_sample_field(sample, "Developer_Info", "general_partner", "General partner", "Extraction pending", "string")
    add_sample_field(sample, "Developer_Info", "management_company", "Management company", "Extraction pending", "string")
    
    add_sample_field(sample, "Financial_Structure", "total_development_cost", "Total development cost", "Extraction pending", "float")
    add_sample_field(sample, "Financial_Structure", "tax_credit_request", "Tax credit request", "Extraction pending", "float")
    add_sample_field(sample, "Financial_Structure", "tax_credit_equity", "Tax credit equity", "Extraction pending", "float")
    add_sample_field(sample, "Financial_Structure", "bank_loan", "Bank loan", "Extraction pending", "float")
    add_sample_field(sample, "Financial_Structure", "city_loan", "City loan", "Extraction pending", "float")
    add_sample_field(sample, "Financial_Structure", "deferred_dev_fee", "Deferred developer fee", "Extraction pending", "float")
    
    add_sample_field(sample, "LIHTC_Metrics", "eligible_basis", "Eligible basis", "Extraction pending", "float")
    add_sample_field(sample, "LIHTC_Metrics", "applicable_percentage", "Applicable percentage", "Extraction pending", "float")
    add_sample_field(sample, "LIHTC_Metrics", "annual_credit_amount", "Annual credit amount", "Extraction pending", "float")
    
    add_sample_field(sample, "Construction", "project_type", "Project type", "Extraction pending", "string")
    add_sample_field(sample, "Construction", "construction_type", "Construction type", "Extraction pending", "string")
    add_sample_field(sample, "Construction", "building_stories", "Number of stories", "Extraction pending", "integer")
    add_sample_field(sample, "Construction", "building_area", "Gross building area", "Extraction pending", "float")
    add_sample_field(sample, "Construction", "parking_spaces", "Parking spaces", "Extraction pending", "integer")
    
    add_sample_field(sample, "Timeline", "construction_start", "Construction start date", "Extraction pending", "string")
    add_sample_field(sample, "Timeline", "construction_completion", "Construction completion", "Extraction pending", "string")
    add_sample_field(sample, "Timeline", "placed_in_service", "Placed in service date", "Extraction pending", "string")
    
    add_sample_field(sample, "Points_System", "total_points_achieved", "Total CTCAC points", "Extraction pending", "float")
    add_sample_field(sample, "Tie_Breaker", "cost_per_unit", "Cost per unit", "Extraction pending", "float")
    add_sample_field(sample, "CALHFA", "is_calhfa_deal", "Is CALHFA deal", "Extraction pending", "boolean")
    add_sample_field(sample, "Subsidy_Contract", "has_rental_assistance", "Has rental assistance", "Extraction pending", "boolean")
    add_sample_field(sample, "Proforma", "stabilized_noi", "Stabilized NOI", "Extraction pending", "float")
    
    return sample

def add_sample_field(sample_dict, category, field_name, description, value, data_type):
    """Add a field to the sample"""
    sample_dict["category"].append(category)
    sample_dict["field_name"].append(field_name) 
    sample_dict["description"].append(description)
    sample_dict["value"].append(value)
    sample_dict["data_type"].append(data_type)

def create_consolidated_view(export_data):
    """Create consolidated view with data labels in Column A"""
    
    if not export_data:
        return {}
    
    # Use the first file as the template
    template = export_data[0]
    
    consolidated = {
        "Data_Field_Label": template["field_name"],
        "Description": template["description"],
        "Category": template["category"],
        "Data_Type": template["data_type"]
    }
    
    # Add file columns
    for i, file_data in enumerate(export_data):
        consolidated[f"File_{i+1}_Value"] = file_data["value"]
    
    return consolidated

def export_to_excel(data_dict, filepath):
    """Export to Excel with multiple sheets"""
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Create main data sheet
        df_main = pd.DataFrame(data_dict)
        df_main.to_excel(writer, sheet_name="Enhanced_CTCAC_Data", index=False)
        
        # Create summary sheet
        summary = {
            "Metric": [
                "Export Type",
                "Export Date",
                "Total Data Fields",
                "Files Analyzed", 
                "Purpose",
                "Key Categories"
            ],
            "Value": [
                "Enhanced CTCAC Data Fields Sample",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                len(data_dict.get("Data_Field_Label", [])),
                len([col for col in data_dict.keys() if col.startswith("File_")]),
                "Review comprehensive LIHTC extraction capabilities",
                "12+ categories including AMI, rents, expenses, financing"
            ]
        }
        
        pd.DataFrame(summary).to_excel(writer, sheet_name="Summary", index=False)
        
        # Create category breakdown
        if "Category" in data_dict:
            category_summary = {}
            for i, category in enumerate(data_dict["Category"]):
                if category not in category_summary:
                    category_summary[category] = 0
                category_summary[category] += 1
            
            cat_df = pd.DataFrame({
                "Category": list(category_summary.keys()),
                "Field_Count": list(category_summary.values())
            })
            cat_df.to_excel(writer, sheet_name="Category_Summary", index=False)

def export_to_csv(data_dict, filepath):
    """Export to CSV"""
    df = pd.DataFrame(data_dict)
    df.to_csv(filepath, index=False)

if __name__ == "__main__":
    export_path = create_simple_sample_export()
    print(f"\n🎯 REVIEW THIS FILE: {export_path}")