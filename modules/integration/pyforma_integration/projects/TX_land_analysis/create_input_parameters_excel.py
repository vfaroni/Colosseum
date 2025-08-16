#!/usr/bin/env python3
"""
Create comprehensive Excel input parameters file for LIHTC analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def create_parameters_excel():
    """Create comprehensive Excel file with all input parameters"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/pyforma_integration/projects/TX_land_analysis/outputs"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f"{output_dir}/LIHTC_Input_Parameters_{timestamp}.xlsx"
    
    print(f"Creating comprehensive input parameters Excel file...")
    print(f"Output: {output_file}")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        # ===============================
        # SHEET 1: LIHTC CREDIT PARAMETERS
        # ===============================
        
        lihtc_params = pd.DataFrame({
            'Parameter': [
                'lihtc_4pct_rate',
                'lihtc_9pct_rate', 
                'credit_period_years',
                'credit_pricing_4pct',
                'credit_pricing_9pct',
                'basis_boost_qct_dda_pct',
                'qualified_basis_pct'
            ],
            'Value': [
                0.04,
                0.09,
                10,
                0.85,
                0.85,
                0.30,
                1.00
            ],
            'Description': [
                '4% LIHTC credit rate (tax-exempt bond deals)',
                '9% LIHTC credit rate (competitive deals)',
                'Credit period in years',
                'Credit pricing for 4% deals ($X per $1.00 credit)',
                'Credit pricing for 9% deals ($X per $1.00 credit)', 
                'Basis boost percentage for QCT/DDA areas',
                'Percentage of development cost that qualifies for credits'
            ],
            'Category': [
                'Credit Rate',
                'Credit Rate',
                'Credit Structure',
                'Credit Pricing',
                'Credit Pricing',
                'Basis Calculation',
                'Basis Calculation'
            ],
            'Notes': [
                'Set by IRS, rarely changes',
                'Set by IRS, rarely changes',
                'Standard 10-year credit period',
                'Market-driven, adjust based on current pricing',
                'Market-driven, adjust based on current pricing',
                'Federal designation bonus',
                'Typically 100% for LIHTC projects'
            ]
        })
        
        lihtc_params.to_excel(writer, sheet_name='LIHTC_Credits', index=False)
        
        # ===============================
        # SHEET 2: CONSTRUCTION COSTS
        # ===============================
        
        construction_params = pd.DataFrame({
            'Parameter': [
                'base_construction_cost_per_sf',
                'soft_cost_percentage',
                'contingency_percentage',
                'architect_engineering_pct',
                'permits_fees_pct',
                'construction_loan_interest_pct',
                'construction_period_months'
            ],
            'Value': [
                150.0,
                0.25,
                0.05,
                0.08,
                0.03,
                0.08,
                18
            ],
            'Description': [
                'Base hard construction cost per square foot',
                'Soft costs as percentage of hard costs',
                'Construction contingency percentage',
                'Architect and engineering fees as % of hard costs',
                'Permits and fees as % of hard costs',
                'Construction loan interest rate',
                'Construction period in months'
            ],
            'Category': [
                'Hard Costs',
                'Soft Costs', 
                'Hard Costs',
                'Soft Costs',
                'Soft Costs',
                'Construction Financing',
                'Construction Timeline'
            ],
            'Notes': [
                'Adjust by region - see Regional_Multipliers sheet',
                'Includes A&E, permits, fees, legal, etc.',
                'Buffer for cost overruns',
                'Typical range 6-10%',
                'Varies significantly by jurisdiction',
                'Current market rate for construction loans',
                'Garden apartments typically 12-18 months'
            ]
        })
        
        construction_params.to_excel(writer, sheet_name='Construction_Costs', index=False)
        
        # ===============================
        # SHEET 3: REGIONAL MULTIPLIERS
        # ===============================
        
        regional_data = pd.DataFrame({
            'County': [
                'TRAVIS',
                'HARRIS', 
                'DALLAS',
                'BEXAR',
                'TARRANT',
                'COLLIN',
                'WILLIAMSON',
                'HAYS',
                'FORT BEND',
                'MONTGOMERY',
                'GALVESTON',
                'BRAZORIA',
                'DENTON',
                'DEFAULT'
            ],
            'Cost_Multiplier': [
                1.20,
                1.18,
                1.15,
                1.12,
                1.10,
                1.08,
                1.15,
                1.12,
                1.16,
                1.10,
                1.14,
                1.12,
                1.08,
                1.00
            ],
            'Major_City': [
                'Austin',
                'Houston',
                'Dallas',
                'San Antonio',
                'Fort Worth',
                'Plano',
                'Cedar Park',
                'Kyle',
                'Sugar Land',
                'Conroe',
                'Galveston',
                'Pearland',
                'Denton',
                'Other Counties'
            ],
            'Market_Type': [
                'Major Metro',
                'Major Metro',
                'Major Metro',
                'Major Metro',
                'Major Metro',
                'Suburban',
                'Suburban',
                'Suburban',
                'Suburban',
                'Suburban',
                'Secondary',
                'Suburban',
                'Suburban',
                'Rural/Other'
            ],
            'Notes': [
                'High cost due to rapid growth',
                'Energy corridor premium',
                'Major metro premium',
                'Moderate metro premium',
                'Major metro premium',
                'North Dallas suburban',
                'Austin suburban',
                'Austin suburban',
                'Houston suburban premium',
                'Houston suburban',
                'Coastal location premium',
                'Houston suburban',
                'North Dallas suburban',
                'Base cost for other areas'
            ]
        })
        
        regional_data.to_excel(writer, sheet_name='Regional_Multipliers', index=False)
        
        # ===============================
        # SHEET 4: FLOOD ZONE ADJUSTMENTS
        # ===============================
        
        flood_data = pd.DataFrame({
            'FEMA_Flood_Zone': [
                'VE',
                'V',
                'AE', 
                'A',
                'AH',
                'AO',
                'X (Protected)',
                'X (Unprotected)',
                'D',
                'Unknown'
            ],
            'Cost_Multiplier': [
                1.30,
                1.30,
                1.20,
                1.20,
                1.15,
                1.10,
                1.00,
                1.05,
                1.10,
                1.05
            ],
            'Risk_Level': [
                'Very High',
                'Very High',
                'High',
                'High',
                'Moderate-High',
                'Moderate',
                'Low',
                'Moderate',
                'Undetermined',
                'Unknown'
            ],
            'Description': [
                'High-risk coastal area with velocity hazard and base flood elevation',
                'High-risk coastal area with velocity hazard',
                '1% annual chance flood area with base flood elevation',
                '1% annual chance flood area',
                'Areas with 1% annual chance shallow flooding (1-3 feet)',
                'Areas with 1% annual chance sheet flow flooding',
                'Areas of minimal flood risk (protected by levee)',
                'Areas of minimal flood risk',
                'Areas with possible but undetermined flood hazards',
                'Area not studied or data not available'
            ],
            'Insurance_Impact': [
                'Required flood insurance, highest premium',
                'Required flood insurance, highest premium',
                'Required flood insurance, high premium',
                'Required flood insurance, high premium',
                'Required flood insurance, moderate premium',
                'Required flood insurance, moderate premium',
                'Flood insurance optional, low cost',
                'Flood insurance optional, moderate cost',
                'Flood insurance recommended',
                'Flood insurance recommended'
            ]
        })
        
        flood_data.to_excel(writer, sheet_name='Flood_Zone_Adjustments', index=False)
        
        # ===============================
        # SHEET 5: UNIT MIX PARAMETERS
        # ===============================
        
        unit_mix_data = pd.DataFrame({
            'Unit_Type': [
                '1BR',
                '2BR',
                '3BR'
            ],
            'Default_Mix_Pct': [
                0.20,
                0.60,
                0.20
            ],
            'Unit_Size_SF': [
                750,
                1000,
                1250
            ],
            'Parking_Ratio': [
                1.0,
                1.5,
                2.0
            ],
            'Min_Mix_Pct': [
                0.10,
                0.40,
                0.10
            ],
            'Max_Mix_Pct': [
                0.40,
                0.80,
                0.40
            ],
            'Typical_AMI_Target': [
                '50-60%',
                '60%',
                '60%'
            ],
            'Notes': [
                'Smaller units, good for seniors/singles',
                'Most common LIHTC unit type',
                'Family units, required for many programs'
            ]
        })
        
        unit_mix_data.to_excel(writer, sheet_name='Unit_Mix_Parameters', index=False)
        
        # ===============================
        # SHEET 6: AMI PARAMETERS
        # ===============================
        
        ami_data = pd.DataFrame({
            'AMI_Level': [
                '30%',
                '40%',
                '50%',
                '60%',
                '70%',
                '80%'
            ],
            'Typical_Mix_Pct': [
                0.10,
                0.10,
                0.20,
                0.60,
                0.00,
                0.00
            ],
            'Min_Mix_Pct': [
                0.00,
                0.00,
                0.00,
                0.20,
                0.00,
                0.00
            ],
            'Max_Mix_Pct': [
                0.20,
                0.20,
                0.40,
                1.00,
                0.20,
                0.20
            ],
            'LIHTC_Requirement': [
                'Qualifies',
                'Qualifies',
                'Qualifies',
                'Qualifies',
                'Does not qualify for 9%',
                'Does not qualify for 9%'
            ],
            'Notes': [
                'Very low income, challenging rents',
                'Very low income, challenging rents',
                'Common for deeper affordability',
                'Standard LIHTC targeting',
                'Market rate or bond deal only',
                'Market rate or bond deal only'
            ]
        })
        
        ami_data.to_excel(writer, sheet_name='AMI_Parameters', index=False)
        
        # ===============================
        # SHEET 7: DEBT PARAMETERS
        # ===============================
        
        debt_params = pd.DataFrame({
            'Parameter': [
                'permanent_interest_rate',
                'permanent_amortization_years',
                'permanent_ltv_max',
                'debt_service_coverage_min',
                'loan_fees_percentage',
                'interest_only_period_years',
                'construction_ltc_max',
                'bridge_loan_rate',
                'prepayment_penalty_years'
            ],
            'Value': [
                0.055,
                35,
                0.80,
                1.20,
                0.015,
                2,
                0.75,
                0.08,
                10
            ],
            'Description': [
                'Permanent loan interest rate',
                'Permanent loan amortization period in years',
                'Maximum loan-to-value ratio',
                'Minimum debt service coverage ratio',
                'Loan fees as percentage of loan amount',
                'Interest-only period after construction',
                'Maximum construction loan-to-cost ratio',
                'Bridge/construction loan interest rate',
                'Prepayment penalty period in years'
            ],
            'Category': [
                'Permanent Debt',
                'Permanent Debt',
                'Permanent Debt',
                'Underwriting',
                'Loan Costs',
                'Permanent Debt',
                'Construction Debt',
                'Construction Debt',
                'Permanent Debt'
            ],
            'Notes': [
                'Adjust based on current market rates',
                'LIHTC deals often get longer amortization',
                'Conservative LTV for LIHTC properties',
                'Lender requirement for cash flow coverage',
                'Includes origination, legal, and other fees',
                'Stabilization period before P&I payments',
                'Construction-to-perm structure',
                'Short-term rate during construction',
                'Lock-in period for permanent financing'
            ]
        })
        
        debt_params.to_excel(writer, sheet_name='Debt_Parameters', index=False)
        
        # ===============================
        # SHEET 8: SOFT FUNDING SOURCES
        # ===============================
        
        soft_funding = pd.DataFrame({
            'Funding_Source': [
                'HOME Investment Partnerships',
                'Housing Trust Fund',
                'CDBG',
                'TDHCA Soft Loan',
                'Local Housing Trust Fund',
                'Utility Rebates',
                'FHLB AHP Grant',
                'Foundation Grants',
                'Deferred Developer Fee'
            ],
            'Typical_Amount_Per_Unit': [
                50000,
                30000,
                25000,
                40000,
                20000,
                2000,
                15000,
                10000,
                25000
            ],
            'Interest_Rate': [
                0.00,
                0.00,
                0.00,
                0.03,
                0.02,
                0.00,
                0.00,
                0.00,
                0.06
            ],
            'Term_Years': [
                30,
                30,
                0,
                30,
                30,
                0,
                0,
                0,
                15
            ],
            'Funding_Type': [
                'Grant/Loan',
                'Grant',
                'Grant',
                'Soft Loan',
                'Soft Loan',
                'Grant',
                'Grant',
                'Grant',
                'Deferred Fee'
            ],
            'Availability': [
                'Competitive',
                'Competitive',
                'Limited',
                'Available',
                'Varies by City',
                'Available',
                'Competitive',
                'Limited',
                'Available'
            ],
            'Notes': [
                'Federal program, competitive application',
                'State/federal program',
                'Community Development Block Grant',
                'Texas Department of Housing soft loan',
                'City/county specific programs',
                'Energy efficiency incentives',
                'Federal Home Loan Bank program',
                'Private foundation funding',
                'Developer contribution to project'
            ]
        })
        
        soft_funding.to_excel(writer, sheet_name='Soft_Funding_Sources', index=False)
        
        # ===============================
        # SHEET 9: OPERATING PARAMETERS
        # ===============================
        
        operating_params = pd.DataFrame({
            'Parameter': [
                'vacancy_rate',
                'rent_growth_annual',
                'other_income_per_unit_annual',
                'management_fee_pct',
                'maintenance_per_unit_annual',
                'utilities_per_unit_annual',
                'insurance_per_unit_annual',
                'property_tax_per_unit_annual',
                'replacement_reserves_per_unit',
                'administrative_per_unit_annual',
                'lihtc_monitoring_annual',
                'asset_management_annual'
            ],
            'Value': [
                0.05,
                0.025,
                1200,
                0.06,
                800,
                600,
                400,
                300,
                300,
                200,
                5000,
                8000
            ],
            'Description': [
                'Vacancy and credit loss percentage',
                'Annual rent growth rate',
                'Other income per unit (laundry, fees, etc.)',
                'Management fee as percentage of gross income',
                'Annual maintenance and repairs per unit',
                'Utilities (common areas) per unit annually',
                'Property insurance per unit annually',
                'Property taxes per unit annually',
                'Replacement reserves per unit annually',
                'Administrative costs per unit annually',
                'Annual LIHTC compliance monitoring fee',
                'Annual asset management fee'
            ],
            'Category': [
                'Income',
                'Income',
                'Income',
                'Operating Expense',
                'Operating Expense',
                'Operating Expense',
                'Operating Expense',
                'Operating Expense',
                'Operating Expense',
                'Operating Expense',
                'LIHTC Specific',
                'LIHTC Specific'
            ],
            'Range_Low': [
                0.03,
                0.015,
                600,
                0.04,
                600,
                400,
                300,
                0,
                250,
                150,
                3000,
                5000
            ],
            'Range_High': [
                0.08,
                0.035,
                2000,
                0.08,
                1200,
                1000,
                600,
                800,
                400,
                300,
                8000,
                12000
            ],
            'Notes': [
                'Lower for stabilized LIHTC properties',
                'Varies by market and inflation',
                'Varies by amenities and management',
                'Economies of scale for larger properties',
                'Higher for older properties',
                'Varies by climate and property type',
                'Higher in coastal/disaster-prone areas',
                'May be exempt for LIHTC properties',
                'Required by lenders and investors',
                'Varies by management structure',
                'Required for LIHTC compliance',
                'Third-party asset management'
            ]
        })
        
        operating_params.to_excel(writer, sheet_name='Operating_Parameters', index=False)
        
        # ===============================
        # SHEET 10: SCENARIO TEMPLATES
        # ===============================
        
        scenarios = pd.DataFrame({
            'Scenario_Name': [
                'Base_Case',
                'Conservative',
                'Optimistic',
                'High_Cost_Market',
                'Low_Cost_Market',
                'High_Credit_Pricing',
                'Low_Credit_Pricing',
                'High_Interest_Rate',
                'Low_Interest_Rate'
            ],
            'Credit_Pricing': [
                0.85,
                0.80,
                0.90,
                0.85,
                0.85,
                0.95,
                0.75,
                0.85,
                0.85
            ],
            'Construction_Cost_SF': [
                150,
                165,
                140,
                180,
                120,
                150,
                150,
                150,
                150
            ],
            'Interest_Rate': [
                0.055,
                0.065,
                0.045,
                0.055,
                0.055,
                0.055,
                0.055,
                0.075,
                0.045
            ],
            'Soft_Cost_Pct': [
                0.25,
                0.30,
                0.20,
                0.30,
                0.22,
                0.25,
                0.25,
                0.25,
                0.25
            ],
            'Vacancy_Rate': [
                0.05,
                0.07,
                0.03,
                0.05,
                0.05,
                0.05,
                0.05,
                0.06,
                0.04
            ],
            'Use_Case': [
                'Standard underwriting assumptions',
                'Risk-averse underwriting',
                'Aggressive/best-case assumptions',
                'Austin, Houston, Dallas markets',
                'Rural/secondary markets',
                'Strong credit market conditions',
                'Weak credit market conditions',
                'Rising interest rate environment',
                'Low interest rate environment'
            ]
        })
        
        scenarios.to_excel(writer, sheet_name='Scenario_Templates', index=False)
        
        # ===============================
        # SHEET 11: INSTRUCTIONS
        # ===============================
        
        instructions = pd.DataFrame({
            'Step': [
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8
            ],
            'Action': [
                'Review all parameter sheets',
                'Select appropriate scenario template',
                'Adjust parameters for current market conditions',
                'Modify regional multipliers as needed',
                'Update credit pricing based on current market',
                'Adjust interest rates to current levels',
                'Customize soft funding based on available sources',
                'Save customized version for analysis'
            ],
            'Description': [
                'Familiarize yourself with all available parameters and their current values',
                'Choose from Base_Case, Conservative, or Optimistic scenarios as starting point',
                'Update construction costs, interest rates, and credit pricing for current market',
                'Add or modify county cost multipliers based on local market knowledge',
                'Check with LIHTC syndicators for current credit pricing',
                'Update based on current treasury rates and credit spreads',
                'Identify available soft funding sources for specific projects/regions',
                'Create project-specific or market-specific parameter sets'
            ],
            'Notes': [
                'Each sheet contains different categories of parameters',
                'Scenario templates provide tested parameter combinations',
                'Market conditions change frequently - update regularly',
                'Local market knowledge is crucial for accurate cost multipliers',
                'Credit pricing can vary significantly by deal structure and sponsor',
                'Interest rates affect debt capacity significantly',
                'Soft funding availability varies by location and program cycles',
                'Maintain multiple versions for different markets/deal types'
            ]
        })
        
        instructions.to_excel(writer, sheet_name='Instructions', index=False)
        
    print(f"✅ Created comprehensive input parameters file: {output_file}")
    print(f"\nFile contains {11} sheets:")
    print(f"  1. LIHTC_Credits - Credit rates and pricing")
    print(f"  2. Construction_Costs - Hard and soft costs")
    print(f"  3. Regional_Multipliers - County-specific cost adjustments")
    print(f"  4. Flood_Zone_Adjustments - FEMA flood zone cost impacts")
    print(f"  5. Unit_Mix_Parameters - Unit sizes and mix ratios")
    print(f"  6. AMI_Parameters - Income targeting levels")
    print(f"  7. Debt_Parameters - Loan terms and underwriting")
    print(f"  8. Soft_Funding_Sources - Subsidy sources and amounts")
    print(f"  9. Operating_Parameters - Income and expense assumptions")
    print(f"  10. Scenario_Templates - Pre-built parameter combinations")
    print(f"  11. Instructions - How to use and customize parameters")
    
    return output_file

if __name__ == "__main__":
    print("CREATING LIHTC INPUT PARAMETERS EXCEL FILE")
    print("=" * 50)
    
    output_file = create_parameters_excel()
    
    print(f"\n🎉 Input parameters file created successfully!")
    print(f"📁 Location: {output_file}")
    print(f"🚀 Ready for use in pyforma analysis pipeline!")