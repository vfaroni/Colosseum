#!/usr/bin/env python3
"""
TDHCA 24600 Cost Extraction and Analysis for Richland Hills
Extracts development costs from successful San Antonio project for 302-unit scaling
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path

class TDHCA24600CostExtractor:
    """Extract and scale development costs from TDHCA 24600 for Richland Hills analysis"""
    
    def __init__(self):
        # Project details from the PDF analysis
        self.project_details = {
            "application_number": "24600",
            "project_name": "Unknown (Successful San Antonio Project)",
            "location": "San Antonio, TX",
            "total_development_cost": 77252400,
            "eligible_basis": 67524186,
            "units": 302,  # Scaling target for Richland Hills
            "project_type": "4% Tax Credit with Tax-Exempt Bonds",
            "bond_financing_percent": 51.09,
            "developer": "Scott Johnson (972) 774-4450",
            "submission_date": "2/15/2024"
        }
        
        # Key cost categories extracted from PDF
        self.cost_breakdown = self.extract_detailed_costs()
        
    def extract_detailed_costs(self):
        """Extract detailed cost breakdown from 24600 analysis"""
        return {
            # ACQUISITION COSTS
            "acquisition": {
                "site_acquisition": 4500000,
                "broker_fees": 135000,
                "subtotal": 4635000
            },
            
            # SITE WORK (Critical for land development)
            "site_work": {
                "rough_grading": 789582,
                "fine_grading": 134931,
                "on_site_concrete": 631960,
                "on_site_electrical": 250123,
                "on_site_utilities": 887635,
                "bumper_stops_striping": 55769,
                "subtotal": 2750000
            },
            
            # SITE AMENITIES 
            "site_amenities": {
                "landscaping": 1511481,
                "pool_and_decking": 271819,
                "athletic_courts_playgrounds": 260509,
                "fencing": 859056,
                "subtotal": 2902865
            },
            
            # BUILDING COSTS (Major category)
            "building_costs": {
                "concrete": 4025932,
                "masonry": 2328725,
                "metals": 241020,
                "woods_and_plastics": 10644348,
                "roof_covering": 1285843,
                "doors_and_windows": 2402877,
                "finishes": 3660782,
                "specialties": 483664,
                "equipment": 860485,
                "furnishings": 951225,
                "special_construction": 541103,
                "elevators": 736160,
                "mechanical_hvac_plumbing": 4616280,
                "electrical": 4029565,
                "subtotal": 36808009
            },
            
            # CONSTRUCTION COSTS
            "construction": {
                "contingency_rate": 3.95,
                "contingency_amount": 1677273,
                "total_hard_costs": 44138147,
                "general_requirements": 2547652,
                "contractor_overhead": 849217,
                "contractor_profit": 2547652,
                "total_contractor_fees": 5944521,
                "total_construction_contract": 50082668
            },
            
            # SOFT COSTS
            "soft_costs": {
                "architectural_design": 521325,
                "architectural_supervision": 77900,
                "engineering_fees": 131250,
                "legal_fees": 207500,
                "accounting": 20000,
                "impact_fees": 973884,
                "building_permits": 148876,
                "appraisal": 15000,
                "market_analysis": 8000,
                "environmental_assessment": 5500,
                "soils_report": 22400,
                "survey": 35200,
                "insurance": 256460,
                "ffe": 300000,
                "reimbursables": 250000,
                "subtotal": 2973295
            },
            
            # FINANCING COSTS
            "financing": {
                "construction_interest": 2914798,
                "construction_origination": 482948,
                "bridge_interest": 1722704,
                "bridge_origination": 113383,
                "tax_credit_fees": 156500,
                "performance_bonds": 479447,
                "cost_of_issuance": 713945,
                "equity_title": 50000,
                "subtotal": 7455402
            },
            
            # DEVELOPER FEES
            "developer_fees": {
                "profit_fee": 8807503,
                "rate_percent": 15.00,
                "subtotal": 8807503
            },
            
            # RESERVES
            "reserves": {
                "operating_reserve": 1782537,
                "escrows": 1515995,
                "subtotal": 3298532
            }
        }
    
    def calculate_per_unit_costs(self):
        """Calculate per-unit costs for scaling analysis"""
        total_units = self.project_details["units"]
        per_unit_costs = {}
        
        # Calculate per-unit for each major category
        for category, costs in self.cost_breakdown.items():
            per_unit_costs[category] = {}
            if isinstance(costs, dict):
                for item, cost in costs.items():
                    if isinstance(cost, (int, float)) and item != "rate_percent":
                        per_unit_costs[category][item] = cost / total_units
            else:
                per_unit_costs[category] = costs / total_units
        
        return per_unit_costs
    
    def scale_costs_for_richland_hills(self, target_units=302):
        """Scale costs for Richland Hills 302-unit project"""
        per_unit = self.calculate_per_unit_costs()
        scaled_costs = {}
        
        print(f"🏗️  SCALING 24600 COSTS FOR RICHLAND HILLS ({target_units} UNITS)")
        print("=" * 70)
        
        total_scaled_cost = 0
        
        for category, costs in per_unit.items():
            scaled_costs[category] = {}
            category_total = 0
            
            print(f"\n📊 {category.upper().replace('_', ' ')}")
            
            if isinstance(costs, dict):
                for item, per_unit_cost in costs.items():
                    if isinstance(per_unit_cost, (int, float)):
                        scaled_cost = per_unit_cost * target_units
                        scaled_costs[category][item] = scaled_cost
                        category_total += scaled_cost
                        print(f"   • {item.replace('_', ' ').title()}: ${scaled_cost:,.0f} (${per_unit_cost:,.0f}/unit)")
            
            scaled_costs[category]["category_total"] = category_total
            total_scaled_cost += category_total
            print(f"   📈 Category Total: ${category_total:,.0f}")
        
        scaled_costs["project_totals"] = {
            "total_development_cost": total_scaled_cost,
            "cost_per_unit": total_scaled_cost / target_units,
            "cost_per_sf": total_scaled_cost / (target_units * 1000),  # Assuming 1000 sf/unit average
            "target_units": target_units,
            "source_project": self.project_details["application_number"]
        }
        
        print(f"\n🎯 RICHLAND HILLS PROJECT TOTALS:")
        print(f"   • Total Development Cost: ${total_scaled_cost:,.0f}")
        print(f"   • Cost Per Unit: ${total_scaled_cost/target_units:,.0f}")
        print(f"   • Cost Per SF: ${total_scaled_cost/(target_units*1000):,.0f}")
        
        return scaled_costs
    
    def create_richland_hills_cost_analysis(self):
        """Create comprehensive cost analysis for Richland Hills"""
        scaled_costs = self.scale_costs_for_richland_hills()
        
        analysis = {
            "project_info": {
                "target_site": "Richland Hills Tract, San Antonio, TX",
                "target_units": 302,
                "source_project": "TDHCA 24600 (Successful San Antonio)",
                "analysis_date": datetime.now().isoformat(),
                "scaling_methodology": "Per-unit cost scaling from successful comparable"
            },
            
            "source_project_summary": self.project_details,
            "detailed_cost_breakdown": scaled_costs,
            
            "key_insights": {
                "land_acquisition": {
                    "source_cost": self.cost_breakdown["acquisition"]["site_acquisition"],
                    "scaled_cost": scaled_costs["acquisition"]["site_acquisition"],
                    "per_unit": scaled_costs["acquisition"]["site_acquisition"] / 302,
                    "notes": "Actual land cost will vary - use for benchmarking"
                },
                
                "construction_costs": {
                    "source_total": self.cost_breakdown["construction"]["total_construction_contract"],
                    "scaled_total": scaled_costs["construction"]["total_construction_contract"],
                    "per_unit": scaled_costs["construction"]["total_construction_contract"] / 302,
                    "per_sf": scaled_costs["construction"]["total_construction_contract"] / (302 * 1000)
                },
                
                "developer_fee_potential": {
                    "source_fee": self.cost_breakdown["developer_fees"]["profit_fee"],
                    "scaled_fee": scaled_costs["developer_fees"]["profit_fee"],
                    "fee_rate": 15.0,
                    "notes": "15% developer fee based on successful project"
                },
                
                "financing_structure": {
                    "bond_financing_percent": self.project_details["bond_financing_percent"],
                    "tax_credit_type": "4% with Tax-Exempt Bonds",
                    "notes": "51.09% bond financing typical for this structure"
                }
            },
            
            "richland_hills_recommendations": {
                "site_work_focus": "On-site utilities ($2,938/unit) and grading ($3,063/unit) are major costs",
                "building_cost_drivers": "Mechanical/HVAC/Plumbing ($15,284/unit) and Woods/Plastics ($35,244/unit)",
                "soft_cost_priorities": "Impact fees ($3,225/unit) and architectural design ($1,726/unit)",
                "financing_strategy": "4% tax credits with tax-exempt bonds - 51% bond financing achievable",
                "total_project_scale": f"${scaled_costs['project_totals']['total_development_cost']:,.0f} for 302 units"
            }
        }
        
        return analysis
    
    def export_analysis(self, analysis):
        """Export analysis to JSON and create Excel summary"""
        output_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        
        # Export detailed JSON
        json_file = output_dir / "Richland_Hills_24600_Cost_Analysis.json"
        with open(json_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n✅ ANALYSIS EXPORTED:")
        print(f"   📁 JSON: {json_file}")
        
        # Create Excel summary
        self.create_excel_summary(analysis, output_dir)
        
        return json_file
    
    def create_excel_summary(self, analysis, output_dir):
        """Create Excel summary for easy review"""
        excel_file = output_dir / "Richland_Hills_24600_Cost_Summary.xlsx"
        
        # Create summary data for Excel
        summary_data = []
        
        # Add major cost categories
        for category, costs in analysis["detailed_cost_breakdown"].items():
            if category != "project_totals" and isinstance(costs, dict):
                category_total = costs.get("category_total", 0)
                per_unit = category_total / 302 if category_total > 0 else 0
                
                summary_data.append({
                    "Category": category.replace("_", " ").title(),
                    "Total Cost": category_total,
                    "Per Unit Cost": per_unit,
                    "Percentage": (category_total / analysis["detailed_cost_breakdown"]["project_totals"]["total_development_cost"]) * 100
                })
        
        # Create DataFrame and save
        df = pd.DataFrame(summary_data)
        df.to_excel(excel_file, index=False, sheet_name="Cost Summary")
        
        print(f"   📊 Excel: {excel_file}")

def main():
    print("🏢 TDHCA 24600 COST EXTRACTION FOR RICHLAND HILLS")
    print("=" * 60)
    print("Extracting costs from successful San Antonio project")
    print("Target: 302-unit Richland Hills Tract analysis")
    print()
    
    extractor = TDHCA24600CostExtractor()
    
    # Create comprehensive analysis
    analysis = extractor.create_richland_hills_cost_analysis()
    
    # Export results
    json_file = extractor.export_analysis(analysis)
    
    print(f"\n🎯 KEY RICHLAND HILLS INSIGHTS:")
    insights = analysis["richland_hills_recommendations"]
    for key, value in insights.items():
        print(f"   • {key.replace('_', ' ').title()}: {value}")
    
    print(f"\n🏁 COST EXTRACTION COMPLETE")
    print(f"📊 Total Scaled Cost: ${analysis['detailed_cost_breakdown']['project_totals']['total_development_cost']:,.0f}")
    print(f"💰 Cost Per Unit: ${analysis['detailed_cost_breakdown']['project_totals']['cost_per_unit']:,.0f}")
    print(f"📁 Analysis saved for integration with Richland Hills BOTN calculator")

if __name__ == "__main__":
    main()