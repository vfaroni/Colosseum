#!/usr/bin/env python3
"""
TDHCA 24600 Detailed Cost Extraction to Excel
Extracts all line items from PDF analysis with scaling notes
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

class TDHCA24600DetailedExtractor:
    """Extract all cost line items from 24600 PDF to Excel format"""
    
    def __init__(self):
        # Project details from PDF
        self.project_info = {
            "Application": "24600",
            "Location": "San Antonio, TX",
            "Developer": "Scott Johnson (972) 774-4450",
            "Total_Units": 321,  # Actual units in 24600 project
            "Target_Units": 302,  # Richland Hills target
            "Total_Development_Cost": 77252400,
            "Eligible_Basis": 67524186,
            "Submission_Date": "2/15/2024"
        }
    
    def extract_all_costs(self):
        """Extract every cost line item from the 24600 PDF"""
        
        # ACQUISITION COSTS
        acquisition_costs = [
            {"Category": "ACQUISITION", "Line_Item": "Site acquisition cost", "Amount": 4500000, "Scaling_Type": "Variable", "Notes": "Land cost - will vary by site"},
            {"Category": "ACQUISITION", "Line_Item": "Broker Fees", "Amount": 135000, "Scaling_Type": "Variable", "Notes": "Typically % of land cost"},
            {"Category": "ACQUISITION", "Line_Item": "Subtotal Acquisition", "Amount": 4635000, "Scaling_Type": "Variable", "Notes": "Sum of above"}
        ]
        
        # SITE WORK COSTS (from Site Work Cost Breakdown form)
        site_work_costs = [
            {"Category": "SITE WORK", "Line_Item": "Rough grading", "Amount": 789582, "Scaling_Type": "Variable", "Notes": "Scales with site size/units"},
            {"Category": "SITE WORK", "Line_Item": "Fine grading", "Amount": 134931, "Scaling_Type": "Variable", "Notes": "Scales with site size/units"},
            {"Category": "SITE WORK", "Line_Item": "On-site concrete", "Amount": 631960, "Scaling_Type": "Variable", "Notes": "Scales with units - drives, walks, etc"},
            {"Category": "SITE WORK", "Line_Item": "On-site electrical", "Amount": 250123, "Scaling_Type": "Variable", "Notes": "Scales with units"},
            {"Category": "SITE WORK", "Line_Item": "On-site utilities", "Amount": 887635, "Scaling_Type": "Variable", "Notes": "Scales with units"},
            {"Category": "SITE WORK", "Line_Item": "Bumper stops, striping & signs", "Amount": 55769, "Scaling_Type": "Variable", "Notes": "Scales with parking spaces/units"},
            {"Category": "SITE WORK", "Line_Item": "Subtotal Site Work", "Amount": 2750000, "Scaling_Type": "Variable", "Notes": "Sum of above"}
        ]
        
        # SITE AMENITIES
        site_amenities_costs = [
            {"Category": "SITE AMENITIES", "Line_Item": "Landscaping", "Amount": 1511481, "Scaling_Type": "Variable", "Notes": "Scales with site size"},
            {"Category": "SITE AMENITIES", "Line_Item": "Pool and decking", "Amount": 271819, "Scaling_Type": "Semi-Fixed", "Notes": "Pool size may not scale linearly"},
            {"Category": "SITE AMENITIES", "Line_Item": "Athletic court(s), playground(s)", "Amount": 260509, "Scaling_Type": "Semi-Fixed", "Notes": "May have minimum viable size"},
            {"Category": "SITE AMENITIES", "Line_Item": "Fencing", "Amount": 859056, "Scaling_Type": "Variable", "Notes": "Scales with perimeter/site size"},
            {"Category": "SITE AMENITIES", "Line_Item": "Subtotal Site Amenities", "Amount": 2902865, "Scaling_Type": "Variable", "Notes": "Sum of above"}
        ]
        
        # BUILDING COSTS (major category)
        building_costs = [
            {"Category": "BUILDING COSTS", "Line_Item": "Concrete", "Amount": 4025932, "Scaling_Type": "Variable", "Notes": "Scales with units"},
            {"Category": "BUILDING COSTS", "Line_Item": "Masonry", "Amount": 2328725, "Scaling_Type": "Variable", "Notes": "Scales with units"},
            {"Category": "BUILDING COSTS", "Line_Item": "Metals", "Amount": 241020, "Scaling_Type": "Variable", "Notes": "Scales with units"},
            {"Category": "BUILDING COSTS", "Line_Item": "Woods and Plastics", "Amount": 10644348, "Scaling_Type": "Variable", "Notes": "Largest building cost - scales with units"},
            {"Category": "BUILDING COSTS", "Line_Item": "Roof Covering", "Amount": 1285843, "Scaling_Type": "Variable", "Notes": "Scales with units"},
            {"Category": "BUILDING COSTS", "Line_Item": "Doors and Windows", "Amount": 2402877, "Scaling_Type": "Variable", "Notes": "Scales with units"},
            {"Category": "BUILDING COSTS", "Line_Item": "Finishes", "Amount": 3660782, "Scaling_Type": "Variable", "Notes": "Scales with units"},
            {"Category": "BUILDING COSTS", "Line_Item": "Specialties", "Amount": 483664, "Scaling_Type": "Variable", "Notes": "Scales with units"},
            {"Category": "BUILDING COSTS", "Line_Item": "Equipment", "Amount": 860485, "Scaling_Type": "Variable", "Notes": "Scales with units"},
            {"Category": "BUILDING COSTS", "Line_Item": "Furnishings", "Amount": 951225, "Scaling_Type": "Variable", "Notes": "Scales with units"},
            {"Category": "BUILDING COSTS", "Line_Item": "Special Construction", "Amount": 541103, "Scaling_Type": "Variable", "Notes": "Scales with units"},
            {"Category": "BUILDING COSTS", "Line_Item": "Conveying Systems (Elevators)", "Amount": 736160, "Scaling_Type": "Semi-Fixed", "Notes": "Elevator count may not scale linearly"},
            {"Category": "BUILDING COSTS", "Line_Item": "Mechanical (HVAC; Plumbing)", "Amount": 4616280, "Scaling_Type": "Variable", "Notes": "Large cost - scales with units"},
            {"Category": "BUILDING COSTS", "Line_Item": "Electrical", "Amount": 4029565, "Scaling_Type": "Variable", "Notes": "Large cost - scales with units"},
            {"Category": "BUILDING COSTS", "Line_Item": "Subtotal Building Costs", "Amount": 36808009, "Scaling_Type": "Variable", "Notes": "Sum of above"}
        ]
        
        # CONSTRUCTION COSTS
        construction_costs = [
            {"Category": "CONSTRUCTION", "Line_Item": "Contingency", "Amount": 1677273, "Scaling_Type": "Variable", "Notes": "3.95% of hard costs"},
            {"Category": "CONSTRUCTION", "Line_Item": "Total Hard Costs", "Amount": 44138147, "Scaling_Type": "Variable", "Notes": "Building + Site + Contingency"},
            {"Category": "CONSTRUCTION", "Line_Item": "General requirements (<6%)", "Amount": 2547652, "Scaling_Type": "Variable", "Notes": "5.77% of hard costs"},
            {"Category": "CONSTRUCTION", "Line_Item": "Contractor overhead (<2%)", "Amount": 849217, "Scaling_Type": "Variable", "Notes": "1.92% of hard costs"},
            {"Category": "CONSTRUCTION", "Line_Item": "Contractor profit (<6%)", "Amount": 2547652, "Scaling_Type": "Variable", "Notes": "5.77% of hard costs"},
            {"Category": "CONSTRUCTION", "Line_Item": "Total Contractor Fees", "Amount": 5944521, "Scaling_Type": "Variable", "Notes": "Sum of GR + Overhead + Profit"},
            {"Category": "CONSTRUCTION", "Line_Item": "Total Construction Contract", "Amount": 50082668, "Scaling_Type": "Variable", "Notes": "Hard costs + contractor fees"}
        ]
        
        # SOFT COSTS
        soft_costs = [
            {"Category": "SOFT COSTS", "Line_Item": "Architectural - Design fees", "Amount": 521325, "Scaling_Type": "Semi-Fixed", "Notes": "Partially fixed + per unit component"},
            {"Category": "SOFT COSTS", "Line_Item": "Architectural - Supervision fees", "Amount": 77900, "Scaling_Type": "Variable", "Notes": "Scales with construction cost"},
            {"Category": "SOFT COSTS", "Line_Item": "Engineering fees", "Amount": 131250, "Scaling_Type": "Semi-Fixed", "Notes": "Base fee + unit scaling"},
            {"Category": "SOFT COSTS", "Line_Item": "Real estate attorney/other legal fees", "Amount": 207500, "Scaling_Type": "Fixed", "Notes": "Mostly fixed legal work"},
            {"Category": "SOFT COSTS", "Line_Item": "Accounting fees", "Amount": 20000, "Scaling_Type": "Fixed", "Notes": "Fixed professional fee"},
            {"Category": "SOFT COSTS", "Line_Item": "Impact Fees", "Amount": 973884, "Scaling_Type": "Variable", "Notes": "Scales with units - major cost"},
            {"Category": "SOFT COSTS", "Line_Item": "Building permits & related costs", "Amount": 148876, "Scaling_Type": "Variable", "Notes": "Scales with construction cost"},
            {"Category": "SOFT COSTS", "Line_Item": "Appraisal", "Amount": 15000, "Scaling_Type": "Fixed", "Notes": "Fixed third-party cost"},
            {"Category": "SOFT COSTS", "Line_Item": "Market analysis", "Amount": 8000, "Scaling_Type": "Fixed", "Notes": "Fixed third-party cost"},
            {"Category": "SOFT COSTS", "Line_Item": "Environmental assessment", "Amount": 5500, "Scaling_Type": "Fixed", "Notes": "Fixed third-party cost"},
            {"Category": "SOFT COSTS", "Line_Item": "Soils report", "Amount": 22400, "Scaling_Type": "Fixed", "Notes": "Fixed third-party cost"},
            {"Category": "SOFT COSTS", "Line_Item": "Survey", "Amount": 35200, "Scaling_Type": "Fixed", "Notes": "Fixed third-party cost"},
            {"Category": "SOFT COSTS", "Line_Item": "Hazard & liability insurance", "Amount": 256460, "Scaling_Type": "Variable", "Notes": "Scales with construction cost"},
            {"Category": "SOFT COSTS", "Line_Item": "FFE", "Amount": 300000, "Scaling_Type": "Variable", "Notes": "Furniture/fixtures scale with units"},
            {"Category": "SOFT COSTS", "Line_Item": "Reimbursables", "Amount": 250000, "Scaling_Type": "Variable", "Notes": "Scales with project size"},
            {"Category": "SOFT COSTS", "Line_Item": "Subtotal Soft Cost", "Amount": 2973295, "Scaling_Type": "Mixed", "Notes": "Sum of above"}
        ]
        
        # FINANCING COSTS
        financing_costs = [
            {"Category": "FINANCING", "Line_Item": "Construction Loan Interest", "Amount": 2914798, "Scaling_Type": "Variable", "Notes": "Scales with construction loan amount"},
            {"Category": "FINANCING", "Line_Item": "Construction Loan origination fees", "Amount": 482948, "Scaling_Type": "Variable", "Notes": "% of construction loan"},
            {"Category": "FINANCING", "Line_Item": "Construction Title & recording fees", "Amount": 224804, "Scaling_Type": "Semi-Fixed", "Notes": "Mostly fixed with some scaling"},
            {"Category": "FINANCING", "Line_Item": "Construction Closing costs & legal fees", "Amount": 47500, "Scaling_Type": "Fixed", "Notes": "Fixed legal costs"},
            {"Category": "FINANCING", "Line_Item": "Construction Inspection fees", "Amount": 185749, "Scaling_Type": "Variable", "Notes": "Scales with construction cost"},
            {"Category": "FINANCING", "Line_Item": "Plan and Cost Review", "Amount": 40000, "Scaling_Type": "Fixed", "Notes": "Fixed review cost"},
            {"Category": "FINANCING", "Line_Item": "Materials Testing", "Amount": 25000, "Scaling_Type": "Semi-Fixed", "Notes": "Base cost + some scaling"},
            {"Category": "FINANCING", "Line_Item": "Bridge Loan Interest", "Amount": 1722704, "Scaling_Type": "Variable", "Notes": "Scales with bridge loan amount"},
            {"Category": "FINANCING", "Line_Item": "Bridge Loan origination fees", "Amount": 113383, "Scaling_Type": "Variable", "Notes": "% of bridge loan"},
            {"Category": "FINANCING", "Line_Item": "Bridge Closing costs & legal fees", "Amount": 20000, "Scaling_Type": "Fixed", "Notes": "Fixed legal costs"},
            {"Category": "FINANCING", "Line_Item": "Tax credit fees", "Amount": 156500, "Scaling_Type": "Fixed", "Notes": "Fixed syndication cost"},
            {"Category": "FINANCING", "Line_Item": "Performance bonds", "Amount": 479447, "Scaling_Type": "Variable", "Notes": "% of construction cost"},
            {"Category": "FINANCING", "Line_Item": "Mortgage insurance premiums", "Amount": 278624, "Scaling_Type": "Variable", "Notes": "% of permanent loan"},
            {"Category": "FINANCING", "Line_Item": "Cost of underwriting & issuance", "Amount": 713945, "Scaling_Type": "Semi-Fixed", "Notes": "Base cost + scaling component"},
            {"Category": "FINANCING", "Line_Item": "Equity Title", "Amount": 50000, "Scaling_Type": "Fixed", "Notes": "Fixed title cost"},
            {"Category": "FINANCING", "Line_Item": "Subtotal Financing Cost", "Amount": 7455402, "Scaling_Type": "Mixed", "Notes": "Sum of above"}
        ]
        
        # DEVELOPER FEES
        developer_fees = [
            {"Category": "DEVELOPER FEES", "Line_Item": "Profit or fee", "Amount": 8807503, "Scaling_Type": "Variable", "Notes": "15.00% of total development cost"},
            {"Category": "DEVELOPER FEES", "Line_Item": "Subtotal Developer Fees", "Amount": 8807503, "Scaling_Type": "Variable", "Notes": "15.00% rate"}
        ]
        
        # RESERVES
        reserves = [
            {"Category": "RESERVES", "Line_Item": "Operating - new funds", "Amount": 1782537, "Scaling_Type": "Variable", "Notes": "Scales with units/NOI"},
            {"Category": "RESERVES", "Line_Item": "Escrows - new funds", "Amount": 1515995, "Scaling_Type": "Variable", "Notes": "HUD Working Capital and Social Services"},
            {"Category": "RESERVES", "Line_Item": "Subtotal Reserves", "Amount": 3298532, "Scaling_Type": "Variable", "Notes": "Sum of above"}
        ]
        
        # Combine all costs
        all_costs = []
        all_costs.extend(acquisition_costs)
        all_costs.extend(site_work_costs)
        all_costs.extend(site_amenities_costs)
        all_costs.extend(building_costs)
        all_costs.extend(construction_costs)
        all_costs.extend(soft_costs)
        all_costs.extend(financing_costs)
        all_costs.extend(developer_fees)
        all_costs.extend(reserves)
        
        return all_costs
    
    def calculate_scaled_costs(self, all_costs):
        """Calculate scaled costs for 302 units vs 321 units"""
        source_units = self.project_info["Total_Units"]
        target_units = self.project_info["Target_Units"]
        scaling_factor = target_units / source_units  # 302/321 = 0.9408
        
        scaled_costs = []
        
        for cost in all_costs:
            scaled_cost = cost.copy()
            
            if cost["Scaling_Type"] == "Variable":
                # Scale with units
                scaled_amount = cost["Amount"] * scaling_factor
                scaled_cost["Scaled_Amount"] = scaled_amount
                scaled_cost["Scaling_Applied"] = f"Scaled by {scaling_factor:.4f}"
            elif cost["Scaling_Type"] == "Fixed":
                # No scaling
                scaled_cost["Scaled_Amount"] = cost["Amount"]
                scaled_cost["Scaling_Applied"] = "No scaling - fixed cost"
            elif cost["Scaling_Type"] == "Semi-Fixed":
                # 50% fixed, 50% variable
                fixed_portion = cost["Amount"] * 0.5
                variable_portion = cost["Amount"] * 0.5 * scaling_factor
                scaled_amount = fixed_portion + variable_portion
                scaled_cost["Scaled_Amount"] = scaled_amount
                scaled_cost["Scaling_Applied"] = f"50% fixed + 50% scaled by {scaling_factor:.4f}"
            else:  # Mixed
                # Default to variable scaling
                scaled_amount = cost["Amount"] * scaling_factor
                scaled_cost["Scaled_Amount"] = scaled_amount
                scaled_cost["Scaling_Applied"] = f"Mixed - scaled by {scaling_factor:.4f}"
            
            # Calculate per unit costs
            scaled_cost["Original_Per_Unit"] = cost["Amount"] / source_units
            scaled_cost["Scaled_Per_Unit"] = scaled_cost["Scaled_Amount"] / target_units
            
            scaled_costs.append(scaled_cost)
        
        return scaled_costs
    
    def export_to_excel(self, scaled_costs):
        """Export detailed cost analysis to Excel"""
        
        # Create DataFrame
        df = pd.DataFrame(scaled_costs)
        
        # Reorder columns for better presentation
        column_order = [
            "Category", "Line_Item", "Amount", "Scaled_Amount", 
            "Original_Per_Unit", "Scaled_Per_Unit", "Scaling_Type", 
            "Scaling_Applied", "Notes"
        ]
        df = df[column_order]
        
        # Format currency columns
        currency_cols = ["Amount", "Scaled_Amount", "Original_Per_Unit", "Scaled_Per_Unit"]
        for col in currency_cols:
            df[col] = df[col].round(0).astype(int)
        
        # Output file
        output_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/TDHCA_24600_Detailed_Cost_Extraction.xlsx")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main detailed breakdown
            df.to_excel(writer, sheet_name="Detailed_Cost_Breakdown", index=False)
            
            # Summary by category
            summary = df.groupby("Category").agg({
                "Amount": "sum",
                "Scaled_Amount": "sum"
            }).reset_index()
            summary["Difference"] = summary["Scaled_Amount"] - summary["Amount"]
            summary["Percent_Change"] = (summary["Difference"] / summary["Amount"] * 100).round(2)
            summary.to_excel(writer, sheet_name="Category_Summary", index=False)
            
            # Scaling type analysis
            scaling_analysis = df.groupby("Scaling_Type").agg({
                "Amount": "sum",
                "Scaled_Amount": "sum"
            }).reset_index()
            scaling_analysis["Difference"] = scaling_analysis["Scaled_Amount"] - scaling_analysis["Amount"]
            scaling_analysis.to_excel(writer, sheet_name="Scaling_Analysis", index=False)
            
            # Project info sheet
            project_df = pd.DataFrame([self.project_info])
            project_df.to_excel(writer, sheet_name="Project_Info", index=False)
        
        return output_file
    
    def create_summary_report(self, scaled_costs, output_file):
        """Create summary report"""
        total_original = sum(cost["Amount"] for cost in scaled_costs)
        total_scaled = sum(cost["Scaled_Amount"] for cost in scaled_costs)
        total_savings = total_original - total_scaled
        
        print(f"\n💰 TDHCA 24600 COST EXTRACTION COMPLETE")
        print(f"=" * 55)
        print(f"📊 Original Project (321 units): ${total_original:,.0f}")
        print(f"🎯 Scaled Project (302 units): ${total_scaled:,.0f}")
        print(f"💵 Total Savings: ${total_savings:,.0f}")
        print(f"📉 Percentage Reduction: {(total_savings/total_original)*100:.1f}%")
        print(f"")
        print(f"📁 Detailed Excel Export: {output_file}")
        print(f"📋 Ready for BOTN integration")
        
        return {
            "total_original": total_original,
            "total_scaled": total_scaled,
            "total_savings": total_savings,
            "percentage_reduction": (total_savings/total_original)*100
        }

def main():
    print("📊 TDHCA 24600 DETAILED COST EXTRACTION")
    print("=" * 50)
    print("🎯 Extracting all line items for Richland Hills scaling")
    print("📉 321 units → 302 units with proper scaling factors")
    print()
    
    extractor = TDHCA24600DetailedExtractor()
    
    # Extract all costs
    all_costs = extractor.extract_all_costs()
    print(f"✅ Extracted {len(all_costs)} cost line items")
    
    # Calculate scaled costs
    scaled_costs = extractor.calculate_scaled_costs(all_costs)
    print(f"⚖️ Applied scaling factors for 302-unit project")
    
    # Export to Excel
    output_file = extractor.export_to_excel(scaled_costs)
    print(f"📊 Excel export complete")
    
    # Summary report
    summary = extractor.create_summary_report(scaled_costs, output_file)

if __name__ == "__main__":
    main()