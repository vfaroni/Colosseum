#!/usr/bin/env python3
"""
TDHCA 24600 Direct Analysis for Richland Hills
Direct cost application from successful San Antonio 302-unit project
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path

class RichlandHills24600DirectAnalysis:
    """Direct cost analysis using 24600 as comparable for Richland Hills"""
    
    def __init__(self):
        # Direct costs from 24600 (same unit count)
        self.original_project = {
            "application": "24600",
            "location": "San Antonio, TX", 
            "units": 302,
            "total_cost": 77252400,
            "eligible_basis": 67524186,
            "cost_per_unit": 77252400 / 302
        }
        
        # Direct cost breakdown from PDF analysis
        self.cost_categories = {
            "acquisition": {
                "site_acquisition": 4500000,
                "broker_fees": 135000,
                "total": 4635000
            },
            "site_work": {
                "rough_grading": 789582,
                "fine_grading": 134931,
                "on_site_concrete": 631960,
                "on_site_electrical": 250123,
                "on_site_utilities": 887635,
                "bumper_stops_striping": 55769,
                "total": 2750000
            },
            "site_amenities": {
                "landscaping": 1511481,
                "pool_decking": 271819,
                "athletic_courts": 260509,
                "fencing": 859056,
                "total": 2902865
            },
            "building_costs": {
                "concrete": 4025932,
                "masonry": 2328725,
                "woods_plastics": 10644348,
                "mechanical_hvac": 4616280,
                "electrical": 4029565,
                "finishes": 3660782,
                "doors_windows": 2402877,
                "roof": 1285843,
                "other_building": 6813657,  # Sum of remaining items
                "total": 36808009
            },
            "construction_soft": {
                "contingency": 1677273,
                "general_requirements": 2547652,
                "contractor_overhead": 849217,
                "contractor_profit": 2547652,
                "total": 7621794
            },
            "soft_costs": {
                "architectural": 599225,  # Design + supervision
                "engineering": 131250,
                "legal": 207500,
                "impact_fees": 973884,
                "permits": 148876,
                "insurance": 256460,
                "ffe": 300000,
                "other_soft": 356095,  # Remaining soft costs
                "total": 2973290
            },
            "financing": {
                "construction_interest": 2914798,
                "bridge_interest": 1722704,
                "origination_fees": 596331,
                "tax_credit_fees": 156500,
                "bonds_issuance": 479447,
                "other_financing": 1585622,
                "total": 7455402
            },
            "developer_fee": 8807503,  # 15%
            "reserves": 3298532
        }
    
    def create_richland_hills_analysis(self):
        """Create direct analysis for Richland Hills using 24600 costs"""
        print("🏗️  RICHLAND HILLS DIRECT COST ANALYSIS")
        print("📊 Source: TDHCA 24600 (Successful San Antonio, 302 units)")
        print("=" * 65)
        
        analysis = {
            "project_summary": {
                "site": "Richland Hills Tract, San Antonio, TX",
                "units": 302,
                "source_project": "TDHCA 24600",
                "analysis_method": "Direct comparable (same unit count)",
                "analysis_date": datetime.now().isoformat()
            },
            "cost_analysis": {},
            "key_insights": {}
        }
        
        total_project_cost = 0
        
        for category, costs in self.cost_categories.items():
            if isinstance(costs, dict) and "total" in costs:
                category_total = costs["total"]
                per_unit = category_total / 302
                
                analysis["cost_analysis"][category] = {
                    "total_cost": category_total,
                    "cost_per_unit": per_unit,
                    "percentage_of_total": 0,  # Will calculate after total known
                    "line_items": {k: v for k, v in costs.items() if k != "total"}
                }
                
                total_project_cost += category_total
                
                print(f"\n📈 {category.upper().replace('_', ' ')}")
                print(f"   💰 Total: ${category_total:,.0f}")
                print(f"   🏠 Per Unit: ${per_unit:,.0f}")
                
                # Show key line items
                for item, cost in costs.items():
                    if item != "total" and cost > 100000:  # Show items over $100K
                        print(f"      • {item.replace('_', ' ').title()}: ${cost:,.0f}")
            
            elif isinstance(costs, (int, float)):
                # Handle single-value categories like developer_fee
                per_unit = costs / 302
                
                analysis["cost_analysis"][category] = {
                    "total_cost": costs,
                    "cost_per_unit": per_unit,
                    "percentage_of_total": 0
                }
                
                total_project_cost += costs
                
                print(f"\n📈 {category.upper().replace('_', ' ')}")
                print(f"   💰 Total: ${costs:,.0f}")
                print(f"   🏠 Per Unit: ${per_unit:,.0f}")
        
        # Calculate percentages
        for category in analysis["cost_analysis"]:
            category_cost = analysis["cost_analysis"][category]["total_cost"]
            analysis["cost_analysis"][category]["percentage_of_total"] = (category_cost / total_project_cost) * 100
        
        # Add project totals
        analysis["project_totals"] = {
            "total_development_cost": total_project_cost,
            "cost_per_unit": total_project_cost / 302,
            "eligible_basis": 67524186,
            "eligible_basis_per_unit": 67524186 / 302
        }
        
        print(f"\n🎯 RICHLAND HILLS PROJECT TOTALS:")
        print(f"   💰 Total Development Cost: ${total_project_cost:,.0f}")
        print(f"   🏠 Cost Per Unit: ${total_project_cost/302:,.0f}")
        print(f"   📊 Eligible Basis: ${67524186:,.0f}")
        print(f"   🏗️ Eligible Basis Per Unit: ${67524186/302:,.0f}")
        
        # Key insights for Richland Hills
        analysis["richland_hills_insights"] = {
            "construction_readiness": {
                "site_work_budget": self.cost_categories["site_work"]["total"],
                "site_work_per_unit": self.cost_categories["site_work"]["total"] / 302,
                "focus_areas": ["On-site utilities ($887K)", "Rough grading ($790K)", "Concrete work ($632K)"]
            },
            "building_cost_drivers": {
                "major_categories": [
                    f"Woods/Plastics: ${self.cost_categories['building_costs']['woods_plastics']:,.0f}",
                    f"Mechanical/HVAC: ${self.cost_categories['building_costs']['mechanical_hvac']:,.0f}",
                    f"Electrical: ${self.cost_categories['building_costs']['electrical']:,.0f}",
                    f"Finishes: ${self.cost_categories['building_costs']['finishes']:,.0f}"
                ],
                "total_building": self.cost_categories["building_costs"]["total"],
                "building_per_unit": self.cost_categories["building_costs"]["total"] / 302
            },
            "financing_structure": {
                "developer_fee": 8807503,
                "developer_fee_rate": "15.0%",
                "tax_credit_type": "4% with Tax-Exempt Bonds",
                "bond_financing_percent": 51.09,
                "total_financing_costs": self.cost_categories["financing"]["total"]
            },
            "market_positioning": {
                "comparable_quality": "Successful 2024 San Antonio project",
                "amenity_level": "Full amenities ($2.9M total)",
                "construction_type": "Multi-story with elevators",
                "target_market": "Family housing with premium finishes"
            }
        }
        
        return analysis
    
    def export_analysis(self, analysis):
        """Export analysis for BOTN integration"""
        output_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        
        # Export JSON
        json_file = output_dir / "Richland_Hills_24600_Direct_Analysis.json"
        with open(json_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Create BOTN-ready Excel
        excel_file = output_dir / "Richland_Hills_BOTN_Ready_Costs.xlsx"
        self.create_botn_excel(analysis, excel_file)
        
        print(f"\n✅ ANALYSIS EXPORTED:")
        print(f"   📁 Detailed JSON: {json_file}")
        print(f"   📊 BOTN Excel: {excel_file}")
        
        return json_file, excel_file
    
    def create_botn_excel(self, analysis, excel_file):
        """Create BOTN-ready Excel with cost categories"""
        
        # BOTN Summary Data
        botn_data = []
        
        for category, details in analysis["cost_analysis"].items():
            botn_data.append({
                "Cost Category": category.replace("_", " ").title(),
                "Total Cost": details["total_cost"],
                "Cost Per Unit": details["cost_per_unit"],
                "% of Total": details["percentage_of_total"]
            })
        
        # Add totals row
        totals = analysis["project_totals"]
        botn_data.append({
            "Cost Category": "TOTAL PROJECT",
            "Total Cost": totals["total_development_cost"],
            "Cost Per Unit": totals["cost_per_unit"],
            "% of Total": 100.0
        })
        
        # Create Excel
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main summary
            df_summary = pd.DataFrame(botn_data)
            df_summary.to_excel(writer, sheet_name="BOTN_Summary", index=False)
            
            # Detailed breakdown
            detailed_data = []
            for category, details in analysis["cost_analysis"].items():
                if "line_items" in details:
                    for item, cost in details["line_items"].items():
                        detailed_data.append({
                            "Category": category.replace("_", " ").title(),
                            "Line Item": item.replace("_", " ").title(),
                            "Cost": cost,
                            "Per Unit": cost / 302
                        })
            
            if detailed_data:
                df_detailed = pd.DataFrame(detailed_data)
                df_detailed.to_excel(writer, sheet_name="Detailed_Costs", index=False)

def main():
    print("🏗️  RICHLAND HILLS - TDHCA 24600 DIRECT COST ANALYSIS")
    print("📍 Comparing identical 302-unit projects in San Antonio")
    print("=" * 65)
    
    analyzer = RichlandHills24600DirectAnalysis()
    analysis = analyzer.create_richland_hills_analysis()
    
    json_file, excel_file = analyzer.export_analysis(analysis)
    
    print(f"\n🎯 KEY TAKEAWAYS FOR RICHLAND HILLS:")
    insights = analysis["richland_hills_insights"]
    
    print(f"   🏗️  Building Costs: ${insights['building_cost_drivers']['total_building']:,.0f} ({insights['building_cost_drivers']['building_per_unit']:,.0f}/unit)")
    print(f"   🚧 Site Work: ${insights['construction_readiness']['site_work_budget']:,.0f} ({insights['construction_readiness']['site_work_per_unit']:,.0f}/unit)")
    print(f"   💰 Developer Fee: ${insights['financing_structure']['developer_fee']:,.0f} (15%)")
    print(f"   🏦 Financing: 4% Tax Credits + {insights['financing_structure']['bond_financing_percent']}% Bond Financing")
    
    print(f"\n📊 INTEGRATION READY:")
    print(f"   • Direct costs from successful comparable project")
    print(f"   • BOTN calculator ready with detailed line items")
    print(f"   • Same unit count eliminates scaling uncertainty")
    print(f"   • Proven financing structure and development model")

if __name__ == "__main__":
    main()