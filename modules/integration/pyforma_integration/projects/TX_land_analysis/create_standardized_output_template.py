#!/usr/bin/env python3
"""
Create standardized output template for LIHTC analysis results
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def create_standardized_output_template():
    """Create standardized output template for future analysis results"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/pyforma_integration/projects/TX_land_analysis/outputs"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    template_file = f"{output_dir}/LIHTC_Standardized_Output_Template_{timestamp}.xlsx"
    
    print(f"Creating standardized output template...")
    print(f"Template: {template_file}")
    
    with pd.ExcelWriter(template_file, engine='openpyxl') as writer:
        
        # ===============================
        # SHEET 1: EXECUTIVE SUMMARY
        # ===============================
        
        exec_summary = pd.DataFrame({
            'Metric': [
                'Total Sites Analyzed',
                'Analysis Date',
                'Scenario Used',
                'Sites Feasible for 4% Credits',
                'Sites Feasible for 9% Credits', 
                'Average Development Cost per Unit',
                'Average NOI per Unit',
                'Average Credit Proceeds (4%)',
                'Average Credit Proceeds (9%)',
                'Top Performing County',
                'Recommended Investment Focus'
            ],
            'Value': [
                '[COUNT]',
                '[DATE]',
                '[SCENARIO_NAME]',
                '[COUNT_4PCT]',
                '[COUNT_9PCT]',
                '[AVG_COST_PER_UNIT]',
                '[AVG_NOI_PER_UNIT]',
                '[AVG_4PCT_PROCEEDS]',
                '[AVG_9PCT_PROCEEDS]',
                '[TOP_COUNTY]',
                '[RECOMMENDATION]'
            ],
            'Notes': [
                'Total number of land sites processed',
                'Date analysis was completed',
                'Parameter scenario used (Base/Conservative/Optimistic)',
                'Number of sites with positive feasibility for 4% credits',
                'Number of sites with positive feasibility for 9% credits',
                'Average total development cost per unit across all sites',
                'Average net operating income per unit',
                'Average LIHTC credit proceeds for 4% deals',
                'Average LIHTC credit proceeds for 9% deals',
                'County with highest average feasibility scores',
                'Investment strategy recommendation based on analysis'
            ]
        })
        
        exec_summary.to_excel(writer, sheet_name='Executive_Summary', index=False)
        
        # ===============================
        # SHEET 2: SITE ANALYSIS RESULTS
        # ===============================
        
        # Create template with example data structure
        site_results_template = pd.DataFrame({
            'Site_ID': ['SITE_001', 'SITE_002', 'SITE_003'],
            'Address': ['[SITE_ADDRESS]', '[SITE_ADDRESS]', '[SITE_ADDRESS]'],
            'City': ['[CITY]', '[CITY]', '[CITY]'],
            'County': ['[COUNTY]', '[COUNTY]', '[COUNTY]'],
            'Acres': ['[ACRES]', '[ACRES]', '[ACRES]'],
            'Target_Units': ['[TOTAL_UNITS]', '[TOTAL_UNITS]', '[TOTAL_UNITS]'],
            'Units_1BR': ['[UNITS_1BR]', '[UNITS_1BR]', '[UNITS_1BR]'],
            'Units_2BR': ['[UNITS_2BR]', '[UNITS_2BR]', '[UNITS_2BR]'],
            'Units_3BR': ['[UNITS_3BR]', '[UNITS_3BR]', '[UNITS_3BR]'],
            'Total_Development_Cost': ['[TOTAL_DEV_COST]', '[TOTAL_DEV_COST]', '[TOTAL_DEV_COST]'],
            'Cost_Per_Unit': ['[COST_PER_UNIT]', '[COST_PER_UNIT]', '[COST_PER_UNIT]'],
            'Hard_Costs': ['[HARD_COSTS]', '[HARD_COSTS]', '[HARD_COSTS]'],
            'Soft_Costs': ['[SOFT_COSTS]', '[SOFT_COSTS]', '[SOFT_COSTS]'],
            'Land_Cost': ['[LAND_COST]', '[LAND_COST]', '[LAND_COST]'],
            'Annual_NOI': ['[NOI]', '[NOI]', '[NOI]'],
            'NOI_Per_Unit': ['[NOI_PER_UNIT]', '[NOI_PER_UNIT]', '[NOI_PER_UNIT]'],
            'Eligible_Basis': ['[ELIGIBLE_BASIS]', '[ELIGIBLE_BASIS]', '[ELIGIBLE_BASIS]'],
            'QCT_DDA_Eligible': ['[QCT_DDA_STATUS]', '[QCT_DDA_STATUS]', '[QCT_DDA_STATUS]'],
            'Annual_4PCT_Credits': ['[4PCT_ANNUAL]', '[4PCT_ANNUAL]', '[4PCT_ANNUAL]'],
            'Annual_9PCT_Credits': ['[9PCT_ANNUAL]', '[9PCT_ANNUAL]', '[9PCT_ANNUAL]'],
            'Credit_4PCT_Proceeds': ['[4PCT_PROCEEDS]', '[4PCT_PROCEEDS]', '[4PCT_PROCEEDS]'],
            'Credit_9PCT_Proceeds': ['[9PCT_PROCEEDS]', '[9PCT_PROCEEDS]', '[9PCT_PROCEEDS]'],
            'Max_Debt_Amount': ['[MAX_DEBT]', '[MAX_DEBT]', '[MAX_DEBT]'],
            'DSCR': ['[DSCR]', '[DSCR]', '[DSCR]'],
            'Funding_Gap_4PCT': ['[GAP_4PCT]', '[GAP_4PCT]', '[GAP_4PCT]'],
            'Funding_Gap_9PCT': ['[GAP_9PCT]', '[GAP_9PCT]', '[GAP_9PCT]'],
            'Feasible_4PCT': ['[FEASIBLE_4PCT]', '[FEASIBLE_4PCT]', '[FEASIBLE_4PCT]'],
            'Feasible_9PCT': ['[FEASIBLE_9PCT]', '[FEASIBLE_9PCT]', '[FEASIBLE_9PCT]'],
            'Recommendation': ['[RECOMMENDATION]', '[RECOMMENDATION]', '[RECOMMENDATION]'],
            'Risk_Factors': ['[RISK_FACTORS]', '[RISK_FACTORS]', '[RISK_FACTORS]']
        })
        
        site_results_template.to_excel(writer, sheet_name='Site_Analysis_Results', index=False)
        
        # ===============================
        # SHEET 3: SOURCES AND USES
        # ===============================
        
        sources_uses_template = pd.DataFrame({
            'Site_ID': ['SITE_001', 'SITE_002', 'SITE_003'],
            'Address': ['[SITE_ADDRESS]', '[SITE_ADDRESS]', '[SITE_ADDRESS]'],
            
            # SOURCES
            'LIHTC_4PCT_Proceeds': ['[4PCT_PROCEEDS]', '[4PCT_PROCEEDS]', '[4PCT_PROCEEDS]'],
            'LIHTC_9PCT_Proceeds': ['[9PCT_PROCEEDS]', '[9PCT_PROCEEDS]', '[9PCT_PROCEEDS]'],
            'Permanent_Loan': ['[PERM_LOAN]', '[PERM_LOAN]', '[PERM_LOAN]'],
            'HOME_Funds': ['[HOME_FUNDS]', '[HOME_FUNDS]', '[HOME_FUNDS]'],
            'Trust_Fund': ['[TRUST_FUND]', '[TRUST_FUND]', '[TRUST_FUND]'],
            'TDHCA_Soft_Loan': ['[TDHCA_LOAN]', '[TDHCA_LOAN]', '[TDHCA_LOAN]'],
            'Other_Soft_Funds': ['[OTHER_SOFT]', '[OTHER_SOFT]', '[OTHER_SOFT]'],
            'Deferred_Developer_Fee': ['[DEFERRED_FEE]', '[DEFERRED_FEE]', '[DEFERRED_FEE]'],
            'Total_Sources_4PCT': ['[TOTAL_SOURCES_4PCT]', '[TOTAL_SOURCES_4PCT]', '[TOTAL_SOURCES_4PCT]'],
            'Total_Sources_9PCT': ['[TOTAL_SOURCES_9PCT]', '[TOTAL_SOURCES_9PCT]', '[TOTAL_SOURCES_9PCT]'],
            
            # USES
            'Hard_Costs': ['[HARD_COSTS]', '[HARD_COSTS]', '[HARD_COSTS]'],
            'Soft_Costs': ['[SOFT_COSTS]', '[SOFT_COSTS]', '[SOFT_COSTS]'],
            'Land_Acquisition': ['[LAND_COST]', '[LAND_COST]', '[LAND_COST]'],
            'Construction_Interest': ['[CONST_INTEREST]', '[CONST_INTEREST]', '[CONST_INTEREST]'],
            'Loan_Fees': ['[LOAN_FEES]', '[LOAN_FEES]', '[LOAN_FEES]'],
            'Developer_Fee_Cash': ['[DEV_FEE_CASH]', '[DEV_FEE_CASH]', '[DEV_FEE_CASH]'],
            'Reserves_Escrows': ['[RESERVES]', '[RESERVES]', '[RESERVES]'],
            'Total_Uses': ['[TOTAL_USES]', '[TOTAL_USES]', '[TOTAL_USES]'],
            
            'Sources_Uses_Gap_4PCT': ['[GAP_4PCT]', '[GAP_4PCT]', '[GAP_4PCT]'],
            'Sources_Uses_Gap_9PCT': ['[GAP_9PCT]', '[GAP_9PCT]', '[GAP_9PCT]']
        })
        
        sources_uses_template.to_excel(writer, sheet_name='Sources_and_Uses', index=False)
        
        # ===============================
        # SHEET 4: OPERATING PROJECTIONS
        # ===============================
        
        operating_template = pd.DataFrame({
            'Site_ID': ['SITE_001', 'SITE_002', 'SITE_003'],
            'Address': ['[SITE_ADDRESS]', '[SITE_ADDRESS]', '[SITE_ADDRESS]'],
            
            # INCOME
            'Gross_Rental_Income': ['[GROSS_RENTAL]', '[GROSS_RENTAL]', '[GROSS_RENTAL]'],
            'Other_Income': ['[OTHER_INCOME]', '[OTHER_INCOME]', '[OTHER_INCOME]'],
            'Vacancy_Loss': ['[VACANCY_LOSS]', '[VACANCY_LOSS]', '[VACANCY_LOSS]'],
            'Effective_Gross_Income': ['[EGI]', '[EGI]', '[EGI]'],
            
            # EXPENSES
            'Management_Fee': ['[MGMT_FEE]', '[MGMT_FEE]', '[MGMT_FEE]'],
            'Maintenance_Repairs': ['[MAINTENANCE]', '[MAINTENANCE]', '[MAINTENANCE]'],
            'Utilities': ['[UTILITIES]', '[UTILITIES]', '[UTILITIES]'],
            'Insurance': ['[INSURANCE]', '[INSURANCE]', '[INSURANCE]'],
            'Property_Taxes': ['[PROP_TAXES]', '[PROP_TAXES]', '[PROP_TAXES]'],
            'Administrative': ['[ADMIN]', '[ADMIN]', '[ADMIN]'],
            'Replacement_Reserves': ['[RESERVES]', '[RESERVES]', '[RESERVES]'],
            'LIHTC_Compliance': ['[COMPLIANCE]', '[COMPLIANCE]', '[COMPLIANCE]'],
            'Total_Operating_Expenses': ['[TOTAL_OPEX]', '[TOTAL_OPEX]', '[TOTAL_OPEX]'],
            
            'Net_Operating_Income': ['[NOI]', '[NOI]', '[NOI]'],
            'Expense_Ratio': ['[EXPENSE_RATIO]', '[EXPENSE_RATIO]', '[EXPENSE_RATIO]'],
            'NOI_Per_Unit': ['[NOI_PER_UNIT]', '[NOI_PER_UNIT]', '[NOI_PER_UNIT]']
        })
        
        operating_template.to_excel(writer, sheet_name='Operating_Projections', index=False)
        
        # ===============================
        # SHEET 5: FEASIBILITY RANKINGS
        # ===============================
        
        rankings_template = pd.DataFrame({
            'Rank_4PCT': [1, 2, 3],
            'Rank_9PCT': [1, 2, 3],
            'Site_ID': ['SITE_001', 'SITE_002', 'SITE_003'],
            'Address': ['[SITE_ADDRESS]', '[SITE_ADDRESS]', '[SITE_ADDRESS]'],
            'County': ['[COUNTY]', '[COUNTY]', '[COUNTY]'],
            'Feasibility_Score_4PCT': ['[SCORE_4PCT]', '[SCORE_4PCT]', '[SCORE_4PCT]'],
            'Feasibility_Score_9PCT': ['[SCORE_9PCT]', '[SCORE_9PCT]', '[SCORE_9PCT]'],
            'Funding_Gap_4PCT': ['[GAP_4PCT]', '[GAP_4PCT]', '[GAP_4PCT]'],
            'Funding_Gap_9PCT': ['[GAP_9PCT]', '[GAP_9PCT]', '[GAP_9PCT]'],
            'ROI_4PCT': ['[ROI_4PCT]', '[ROI_4PCT]', '[ROI_4PCT]'],
            'ROI_9PCT': ['[ROI_9PCT]', '[ROI_9PCT]', '[ROI_9PCT]'],
            'Risk_Level': ['[RISK_LEVEL]', '[RISK_LEVEL]', '[RISK_LEVEL]'],
            'Investment_Category': ['[CATEGORY]', '[CATEGORY]', '[CATEGORY]'],
            'Primary_Recommendation': ['[RECOMMENDATION]', '[RECOMMENDATION]', '[RECOMMENDATION]'],
            'Notes': ['[NOTES]', '[NOTES]', '[NOTES]']
        })
        
        rankings_template.to_excel(writer, sheet_name='Feasibility_Rankings', index=False)
        
        # ===============================
        # SHEET 6: PARAMETER SENSITIVITY
        # ===============================
        
        sensitivity_template = pd.DataFrame({
            'Parameter': [
                'Credit_Pricing',
                'Construction_Cost_Per_SF',
                'Interest_Rate',
                'Soft_Cost_Percentage',
                'Vacancy_Rate',
                'AMI_Rent_Level',
                'Regional_Cost_Multiplier',
                'Debt_Service_Coverage'
            ],
            'Base_Value': [
                '[BASE_CREDIT_PRICING]',
                '[BASE_CONSTRUCTION_COST]',
                '[BASE_INTEREST_RATE]',
                '[BASE_SOFT_COST_PCT]',
                '[BASE_VACANCY_RATE]',
                '[BASE_AMI_RENT]',
                '[BASE_REGIONAL_MULT]',
                '[BASE_DSCR]'
            ],
            'Sensitivity_Range_Low': [
                '[CREDIT_PRICING_LOW]',
                '[CONSTRUCTION_LOW]',
                '[INTEREST_LOW]',
                '[SOFT_COST_LOW]',
                '[VACANCY_LOW]',
                '[AMI_RENT_LOW]',
                '[REGIONAL_LOW]',
                '[DSCR_LOW]'
            ],
            'Sensitivity_Range_High': [
                '[CREDIT_PRICING_HIGH]',
                '[CONSTRUCTION_HIGH]',
                '[INTEREST_HIGH]',
                '[SOFT_COST_HIGH]',
                '[VACANCY_HIGH]',
                '[AMI_RENT_HIGH]',
                '[REGIONAL_HIGH]',
                '[DSCR_HIGH]'
            ],
            'Impact_on_Feasibility_Low': [
                '[IMPACT_LOW]',
                '[IMPACT_LOW]',
                '[IMPACT_LOW]',
                '[IMPACT_LOW]',
                '[IMPACT_LOW]',
                '[IMPACT_LOW]',
                '[IMPACT_LOW]',
                '[IMPACT_LOW]'
            ],
            'Impact_on_Feasibility_High': [
                '[IMPACT_HIGH]',
                '[IMPACT_HIGH]',
                '[IMPACT_HIGH]',
                '[IMPACT_HIGH]',
                '[IMPACT_HIGH]',
                '[IMPACT_HIGH]',
                '[IMPACT_HIGH]',
                '[IMPACT_HIGH]'
            ],
            'Key_Insights': [
                '[INSIGHT]',
                '[INSIGHT]',
                '[INSIGHT]',
                '[INSIGHT]',
                '[INSIGHT]',
                '[INSIGHT]',
                '[INSIGHT]',
                '[INSIGHT]'
            ]
        })
        
        sensitivity_template.to_excel(writer, sheet_name='Parameter_Sensitivity', index=False)
        
        # ===============================
        # SHEET 7: MARKET ANALYSIS
        # ===============================
        
        market_template = pd.DataFrame({
            'County': ['[COUNTY_1]', '[COUNTY_2]', '[COUNTY_3]'],
            'Number_of_Sites': ['[SITE_COUNT]', '[SITE_COUNT]', '[SITE_COUNT]'],
            'Avg_Development_Cost_Per_Unit': ['[AVG_COST]', '[AVG_COST]', '[AVG_COST]'],
            'Avg_NOI_Per_Unit': ['[AVG_NOI]', '[AVG_NOI]', '[AVG_NOI]'],
            'Feasible_Sites_4PCT': ['[FEASIBLE_4PCT]', '[FEASIBLE_4PCT]', '[FEASIBLE_4PCT]'],
            'Feasible_Sites_9PCT': ['[FEASIBLE_9PCT]', '[FEASIBLE_9PCT]', '[FEASIBLE_9PCT]'],
            'Avg_Credit_Proceeds_4PCT': ['[CREDIT_4PCT]', '[CREDIT_4PCT]', '[CREDIT_4PCT]'],
            'Avg_Credit_Proceeds_9PCT': ['[CREDIT_9PCT]', '[CREDIT_9PCT]', '[CREDIT_9PCT]'],
            'Market_Risk_Level': ['[RISK_LEVEL]', '[RISK_LEVEL]', '[RISK_LEVEL]'],
            'Construction_Cost_Multiplier': ['[COST_MULT]', '[COST_MULT]', '[COST_MULT]'],
            'Recommended_Strategy': ['[STRATEGY]', '[STRATEGY]', '[STRATEGY]'],
            'Market_Notes': ['[NOTES]', '[NOTES]', '[NOTES]']
        })
        
        market_template.to_excel(writer, sheet_name='Market_Analysis', index=False)
        
        # ===============================
        # SHEET 8: DATA DICTIONARY
        # ===============================
        
        data_dictionary = pd.DataFrame({
            'Field_Name': [
                'Site_ID',
                'Total_Development_Cost', 
                'Cost_Per_Unit',
                'Annual_NOI',
                'Eligible_Basis',
                'QCT_DDA_Eligible',
                'Credit_4PCT_Proceeds',
                'Credit_9PCT_Proceeds',
                'Max_Debt_Amount',
                'DSCR',
                'Funding_Gap_4PCT',
                'Funding_Gap_9PCT',
                'Feasible_4PCT',
                'Feasible_9PCT',
                'Feasibility_Score',
                'Investment_Category',
                'ROI',
                'Risk_Level'
            ],
            'Data_Type': [
                'Text',
                'Currency',
                'Currency',
                'Currency',
                'Currency',
                'Boolean',
                'Currency',
                'Currency',
                'Currency',
                'Decimal',
                'Currency',
                'Currency',
                'Boolean',
                'Boolean',
                'Decimal',
                'Text',
                'Percentage',
                'Text'
            ],
            'Description': [
                'Unique identifier for each land site',
                'Total cost to develop the project including all hard costs, soft costs, and land',
                'Total development cost divided by number of units',
                'Annual net operating income after all operating expenses',
                'Portion of development cost eligible for LIHTC credits',
                'Whether site qualifies for QCT/DDA 30% basis boost',
                'Proceeds from sale of 4% LIHTC credits to investor',
                'Proceeds from sale of 9% LIHTC credits to investor', 
                'Maximum permanent loan amount based on NOI and DSCR requirements',
                'Debt service coverage ratio (NOI / Annual Debt Service)',
                'Funding shortfall/excess for 4% credit scenario',
                'Funding shortfall/excess for 9% credit scenario',
                'Whether 4% credit scenario is financially feasible',
                'Whether 9% credit scenario is financially feasible',
                'Composite score measuring overall project feasibility',
                'Investment recommendation category (Exceptional/Good/Poor)',
                'Return on investment calculation',
                'Overall project risk assessment (Low/Medium/High)'
            ],
            'Calculation_Method': [
                'Generated sequentially',
                'Hard Costs + Soft Costs + Land Cost + Fees',
                'Total Development Cost / Total Units',
                'Effective Gross Income - Operating Expenses',
                'Development Cost * Qualified Basis Percentage',
                'Based on HUD QCT/DDA designation',
                'Annual 4% Credits * 10 years * Credit Pricing',
                'Annual 9% Credits * 10 years * Credit Pricing',
                'NOI / Interest Rate / DSCR',
                'NOI / Annual Debt Service',
                'Total Uses - Total Sources (4% scenario)',
                'Total Uses - Total Sources (9% scenario)',
                'Funding Gap <= 0',
                'Funding Gap <= 0',
                'Weighted combination of gap, ROI, and risk factors',
                'Based on feasibility score thresholds',
                'Net Present Value calculation',
                'Based on market, flood, and financial risk factors'
            ],
            'Notes': [
                'Format: SITE_XXX',
                'Includes all project costs',
                'Key metric for comparative analysis',
                'Stabilized year 1 operating performance',
                'Typically 100% for LIHTC projects',
                'Provides 30% boost to eligible basis',
                'Current market credit pricing applied',
                'Current market credit pricing applied',
                'Conservative debt sizing',
                'Lender requirement typically 1.15-1.25',
                'Negative = surplus, Positive = gap',
                'Negative = surplus, Positive = gap',
                'Primary feasibility indicator',
                'Primary feasibility indicator',
                'Scale 0-100, higher = better',
                'Investment recommendation tiers',
                'Various return metrics calculated',
                'Qualitative risk assessment'
            ]
        })
        
        data_dictionary.to_excel(writer, sheet_name='Data_Dictionary', index=False)
        
    print(f"✅ Created standardized output template: {template_file}")
    print(f"\nTemplate contains {8} sheets:")
    print(f"  1. Executive_Summary - High-level analysis results")
    print(f"  2. Site_Analysis_Results - Detailed results for each site")
    print(f"  3. Sources_and_Uses - Project financing breakdown")
    print(f"  4. Operating_Projections - Income and expense projections")
    print(f"  5. Feasibility_Rankings - Sites ranked by feasibility")
    print(f"  6. Parameter_Sensitivity - Impact of parameter changes")
    print(f"  7. Market_Analysis - County/market-level analysis")
    print(f"  8. Data_Dictionary - Field definitions and calculations")
    
    return template_file

def create_output_mapping_guide():
    """Create guide showing how to map analysis results to standardized output"""
    
    mapping_guide = """
    # OUTPUT MAPPING GUIDE
    ## How to Map Analysis Results to Standardized Output Template
    
    ### Sheet 1: Executive Summary
    - Total Sites Analyzed: len(results_df)
    - Sites Feasible 4%: sum(results_df['feasible_4pct'])
    - Sites Feasible 9%: sum(results_df['feasible_9pct'])
    - Average Cost per Unit: results_df['cost_per_unit'].mean()
    
    ### Sheet 2: Site Analysis Results
    - Map enhanced_lihtc_financial_model results directly
    - Include all cost components and feasibility metrics
    - Add risk assessment and recommendations
    
    ### Sheet 3: Sources and Uses
    - Extract from sources_and_uses calculation
    - Show both 4% and 9% scenarios
    - Include all funding sources and cost categories
    
    ### Sheet 4: Operating Projections
    - Use operating income calculations
    - Include all income and expense line items
    - Calculate key ratios and per-unit metrics
    
    ### Sheet 5: Feasibility Rankings
    - Rank by feasibility score or funding gap
    - Separate rankings for 4% and 9% scenarios
    - Include investment recommendations
    
    ### Sheet 6: Parameter Sensitivity
    - Run sensitivity analysis on key parameters
    - Show impact ranges for each variable
    - Provide insights on parameter importance
    
    ### Sheet 7: Market Analysis
    - Group results by county
    - Calculate market-level averages
    - Provide market strategy recommendations
    
    ### Sheet 8: Data Dictionary
    - Use provided template
    - Update calculations as model evolves
    - Maintain field definitions for consistency
    """
    
    guide_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/pyforma_integration/projects/TX_land_analysis/OUTPUT_MAPPING_GUIDE.md"
    
    with open(guide_file, 'w') as f:
        f.write(mapping_guide)
    
    print(f"✅ Created output mapping guide: OUTPUT_MAPPING_GUIDE.md")
    
    return guide_file

if __name__ == "__main__":
    print("CREATING STANDARDIZED OUTPUT TEMPLATE")
    print("=" * 50)
    
    template_file = create_standardized_output_template()
    guide_file = create_output_mapping_guide()
    
    print(f"\n🎉 Standardized output system created!")
    print(f"📄 Template: {template_file}")
    print(f"📋 Mapping Guide: {guide_file}")
    print(f"🚀 Ready for consistent analysis reporting!")