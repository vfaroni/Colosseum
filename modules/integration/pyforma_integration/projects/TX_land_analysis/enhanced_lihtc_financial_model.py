#!/usr/bin/env python3
"""
Enhanced LIHTC Financial Model with Comprehensive Adjustable Parameters
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class LIHTCFinancialParameters:
    """
    Comprehensive LIHTC financial parameters that can be adjusted for analysis
    """
    
    # ======================
    # LIHTC CREDIT PARAMETERS
    # ======================
    lihtc_4pct_rate: float = 0.04          # 4% credit rate (bond deals)
    lihtc_9pct_rate: float = 0.09          # 9% credit rate (competitive)
    credit_period: int = 10                # Credit period in years
    credit_pricing: float = 0.85           # Credit price ($ per $1 of credit)
    basis_boost_qct_dda: float = 0.30      # 30% basis boost for QCT/DDA
    
    # ======================
    # CONSTRUCTION COSTS
    # ======================
    base_construction_cost_per_sf: float = 150.0   # Base cost per square foot
    regional_cost_multipliers: Dict[str, float] = None  # By county/region
    soft_cost_percentage: float = 0.25     # Soft costs as % of hard costs
    contingency_percentage: float = 0.05   # Construction contingency
    
    # Construction cost adjustments
    flood_zone_multipliers: Dict[str, float] = None  # FEMA flood zone costs
    market_type_multipliers: Dict[str, float] = None  # Urban/suburban/rural
    
    def __post_init__(self):
        if self.regional_cost_multipliers is None:
            self.regional_cost_multipliers = {
                'TRAVIS': 1.20,    # Austin
                'HARRIS': 1.18,    # Houston  
                'DALLAS': 1.15,    # Dallas
                'BEXAR': 1.12,     # San Antonio
                'TARRANT': 1.10,   # Fort Worth
                'COLLIN': 1.08,    # Plano
                'default': 1.00    # Other counties
            }
        
        if self.flood_zone_multipliers is None:
            self.flood_zone_multipliers = {
                'VE': 1.30,    # High risk coastal
                'V': 1.30,     # High risk coastal
                'AE': 1.20,    # 100-year floodplain
                'A': 1.20,     # 100-year floodplain
                'X': 1.00,     # Minimal risk
                'default': 1.00
            }
        
        if self.market_type_multipliers is None:
            self.market_type_multipliers = {
                'Urban': 1.05,
                'Suburban': 1.00,
                'Rural': 0.95,
                'default': 1.00
            }

@dataclass 
class UnitMixParameters:
    """
    Unit mix and sizing parameters
    """
    
    # ======================
    # UNIT MIX COMPOSITION
    # ======================
    mix_1br_pct: float = 0.20              # 20% 1-bedroom units
    mix_2br_pct: float = 0.60              # 60% 2-bedroom units  
    mix_3br_pct: float = 0.20              # 20% 3-bedroom units
    
    # ======================
    # UNIT SIZES (SQUARE FEET)
    # ======================
    unit_size_1br: int = 750               # 1BR unit size
    unit_size_2br: int = 1000              # 2BR unit size
    unit_size_3br: int = 1250              # 3BR unit size
    
    # ======================
    # AMI TARGETING
    # ======================
    ami_percentage: float = 0.60           # 60% AMI targeting
    ami_mix_50pct: float = 0.20           # 20% at 50% AMI
    ami_mix_60pct: float = 0.80           # 80% at 60% AMI
    
    def validate_mix(self):
        """Ensure unit mix percentages sum to 100%"""
        total = self.mix_1br_pct + self.mix_2br_pct + self.mix_3br_pct
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Unit mix must sum to 100%, got {total*100:.1f}%")

@dataclass
class DebtParameters:
    """
    Construction and permanent debt parameters
    """
    
    # ======================
    # CONSTRUCTION LOAN
    # ======================
    construction_interest_rate: float = 0.08       # 8% construction loan rate
    construction_term_months: int = 18              # 18-month construction period
    construction_ltc: float = 0.75                  # 75% loan-to-cost
    
    # ======================
    # PERMANENT DEBT
    # ======================
    permanent_interest_rate: float = 0.055         # 5.5% permanent rate
    permanent_amortization_years: int = 35          # 35-year amortization
    permanent_ltv: float = 0.80                     # 80% loan-to-value
    debt_service_coverage_min: float = 1.20        # Minimum DSCR
    
    # ======================
    # DEBT STRUCTURE
    # ======================
    interest_only_period_years: int = 2            # IO period after construction
    loan_fees_percentage: float = 0.015            # 1.5% loan fees

@dataclass
class SoftFundsParameters:
    """
    Soft funding sources and parameters
    """
    
    # ======================
    # GOVERNMENT FUNDING
    # ======================
    home_funds_per_unit: float = 50000             # HOME funds per unit
    trust_fund_per_unit: float = 30000             # Housing trust fund
    tdhca_soft_loan_rate: float = 0.03             # 3% TDHCA soft loan rate
    tdhca_soft_loan_term: int = 30                 # 30-year term
    
    # ======================
    # GRANTS AND SUBSIDIES
    # ======================
    cdbg_funds: float = 0                          # CDBG funding
    aht_funds: float = 0                           # Affordable Housing Trust
    utility_rebates_per_unit: float = 2000         # Energy efficiency rebates
    
    # ======================
    # DEFERRED DEVELOPER FEE
    # ======================
    developer_fee_percentage: float = 0.15         # 15% developer fee
    deferred_fee_percentage: float = 0.50          # 50% of fee deferred

@dataclass
class OperatingParameters:
    """
    Operating income and expense parameters
    """
    
    # ======================
    # INCOME PARAMETERS
    # ======================
    vacancy_rate: float = 0.05                     # 5% vacancy allowance
    rent_growth_annual: float = 0.025              # 2.5% annual rent growth
    other_income_per_unit: float = 1200            # Other income (laundry, etc.)
    
    # ======================
    # OPERATING EXPENSES (per unit annually)
    # ======================
    management_fee_pct: float = 0.06               # 6% of gross income
    maintenance_per_unit: float = 800              # Maintenance/repairs
    utilities_per_unit: float = 600                # Utilities
    insurance_per_unit: float = 400                # Property insurance
    property_tax_per_unit: float = 300             # Property taxes (if applicable)
    reserves_per_unit: float = 300                 # Replacement reserves
    administrative_per_unit: float = 200           # Administrative costs
    
    # ======================
    # COMPLIANCE COSTS
    # ======================
    lihtc_monitoring_annual: float = 5000          # Annual compliance monitoring
    asset_management_fee: float = 8000             # Annual asset management

class EnhancedLIHTCModel:
    """
    Enhanced LIHTC financial model with comprehensive adjustable parameters
    """
    
    def __init__(self, 
                 financial_params: LIHTCFinancialParameters = None,
                 unit_mix_params: UnitMixParameters = None,
                 debt_params: DebtParameters = None,
                 soft_funds_params: SoftFundsParameters = None,
                 operating_params: OperatingParameters = None):
        
        self.financial = financial_params or LIHTCFinancialParameters()
        self.unit_mix = unit_mix_params or UnitMixParameters()
        self.debt = debt_params or DebtParameters()
        self.soft_funds = soft_funds_params or SoftFundsParameters()
        self.operating = operating_params or OperatingParameters()
        
        # Validate parameters
        self.unit_mix.validate_mix()
    
    def calculate_project_costs(self, site_data: Dict) -> Dict:
        """Calculate total project costs with all adjustable parameters"""
        
        acres = site_data.get('acres', 1.0)
        target_dua = site_data.get('target_dua', 12)
        county = site_data.get('county', 'default').upper()
        flood_zone = site_data.get('flood_zone', 'X')
        market_type = site_data.get('market_type', 'Suburban')
        
        # Calculate units
        total_units = acres * target_dua
        units_1br = total_units * self.unit_mix.mix_1br_pct
        units_2br = total_units * self.unit_mix.mix_2br_pct
        units_3br = total_units * self.unit_mix.mix_3br_pct
        
        # Calculate total square footage
        total_sqft = (units_1br * self.unit_mix.unit_size_1br + 
                     units_2br * self.unit_mix.unit_size_2br + 
                     units_3br * self.unit_mix.unit_size_3br)
        
        # Base construction cost
        base_cost = total_sqft * self.financial.base_construction_cost_per_sf
        
        # Apply multipliers
        regional_multiplier = self.financial.regional_cost_multipliers.get(county, 
                            self.financial.regional_cost_multipliers['default'])
        flood_multiplier = self.financial.flood_zone_multipliers.get(flood_zone,
                         self.financial.flood_zone_multipliers['default'])
        market_multiplier = self.financial.market_type_multipliers.get(market_type,
                          self.financial.market_type_multipliers['default'])
        
        # Adjusted construction cost
        hard_costs = base_cost * regional_multiplier * flood_multiplier * market_multiplier
        
        # Add contingency
        hard_costs_with_contingency = hard_costs * (1 + self.financial.contingency_percentage)
        
        # Soft costs
        soft_costs = hard_costs_with_contingency * self.financial.soft_cost_percentage
        
        # Land cost (from existing analysis)
        land_cost = site_data.get('land_cost', 0)
        
        # Total development cost
        total_development_cost = hard_costs_with_contingency + soft_costs + land_cost
        
        return {
            'total_units': total_units,
            'units_1br': units_1br,
            'units_2br': units_2br, 
            'units_3br': units_3br,
            'total_sqft': total_sqft,
            'base_construction_cost': base_cost,
            'hard_costs': hard_costs_with_contingency,
            'soft_costs': soft_costs,
            'land_cost': land_cost,
            'total_development_cost': total_development_cost,
            'cost_per_unit': total_development_cost / total_units,
            'cost_per_sqft': total_development_cost / total_sqft,
            'regional_multiplier': regional_multiplier,
            'flood_multiplier': flood_multiplier,
            'market_multiplier': market_multiplier
        }
    
    def calculate_lihtc_credits(self, development_cost: float, qct_dda_eligible: bool = True) -> Dict:
        """Calculate LIHTC credit amounts and proceeds"""
        
        # Eligible basis (simplified - assumes 100% LIHTC eligible)
        eligible_basis = development_cost
        
        # Apply basis boost if QCT/DDA eligible
        if qct_dda_eligible:
            eligible_basis *= (1 + self.financial.basis_boost_qct_dda)
        
        # Calculate annual credits
        annual_4pct_credits = eligible_basis * self.financial.lihtc_4pct_rate
        annual_9pct_credits = eligible_basis * self.financial.lihtc_9pct_rate
        
        # 10-year credit totals
        total_4pct_credits = annual_4pct_credits * self.financial.credit_period
        total_9pct_credits = annual_9pct_credits * self.financial.credit_period
        
        # Credit proceeds (what investor pays)
        credit_4pct_proceeds = total_4pct_credits * self.financial.credit_pricing
        credit_9pct_proceeds = total_9pct_credits * self.financial.credit_pricing
        
        return {
            'eligible_basis': eligible_basis,
            'basis_boost_applied': qct_dda_eligible,
            'annual_4pct_credits': annual_4pct_credits,
            'annual_9pct_credits': annual_9pct_credits,
            'total_4pct_credits': total_4pct_credits,
            'total_9pct_credits': total_9pct_credits,
            'credit_4pct_proceeds': credit_4pct_proceeds,
            'credit_9pct_proceeds': credit_9pct_proceeds
        }
    
    def calculate_debt_capacity(self, noi: float) -> Dict:
        """Calculate debt capacity based on NOI and DSCR requirements"""
        
        # Monthly debt service capacity
        monthly_ds_capacity = (noi / 12) / self.debt.debt_service_coverage_min
        
        # Calculate loan amount based on payment capacity
        monthly_rate = self.debt.permanent_interest_rate / 12
        num_payments = self.debt.permanent_amortization_years * 12
        
        # Payment calculation: PMT = PV * [r(1+r)^n] / [(1+r)^n - 1]
        if monthly_rate > 0:
            payment_factor = (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                           ((1 + monthly_rate) ** num_payments - 1)
            max_loan_amount = monthly_ds_capacity / payment_factor
        else:
            max_loan_amount = monthly_ds_capacity * num_payments
        
        # Apply LTV limitation
        ltv_limited_amount = max_loan_amount / self.debt.permanent_ltv
        
        # Loan fees
        loan_fees = max_loan_amount * self.debt.loan_fees_percentage
        
        return {
            'monthly_ds_capacity': monthly_ds_capacity,
            'annual_ds_capacity': monthly_ds_capacity * 12,
            'max_loan_amount': max_loan_amount,
            'ltv_limited_amount': ltv_limited_amount,
            'loan_fees': loan_fees,
            'net_loan_proceeds': max_loan_amount - loan_fees,
            'dscr': self.debt.debt_service_coverage_min
        }
    
    def calculate_operating_income(self, site_data: Dict, cost_data: Dict) -> Dict:
        """Calculate operating income with adjustable parameters"""
        
        total_units = cost_data['total_units']
        units_1br = cost_data['units_1br']
        units_2br = cost_data['units_2br'] 
        units_3br = cost_data['units_3br']
        
        # Get AMI rent data
        rent_1br = site_data.get('rent_1br_60pct', 800) * 12  # Annual
        rent_2br = site_data.get('rent_2br_60pct', 1000) * 12
        rent_3br = site_data.get('rent_3br_60pct', 1200) * 12
        
        # Calculate gross rental income
        gross_rental_income = (units_1br * rent_1br + 
                              units_2br * rent_2br + 
                              units_3br * rent_3br)
        
        # Other income
        other_income = total_units * self.operating.other_income_per_unit
        
        # Gross income
        gross_income = gross_rental_income + other_income
        
        # Vacancy adjustment
        effective_gross_income = gross_income * (1 - self.operating.vacancy_rate)
        
        # Operating expenses
        management_expense = effective_gross_income * self.operating.management_fee_pct
        maintenance_expense = total_units * self.operating.maintenance_per_unit
        utilities_expense = total_units * self.operating.utilities_per_unit
        insurance_expense = total_units * self.operating.insurance_per_unit
        property_tax_expense = total_units * self.operating.property_tax_per_unit
        reserves_expense = total_units * self.operating.reserves_per_unit
        administrative_expense = total_units * self.operating.administrative_per_unit
        compliance_expense = self.operating.lihtc_monitoring_annual + self.operating.asset_management_fee
        
        total_operating_expenses = (management_expense + maintenance_expense + 
                                  utilities_expense + insurance_expense + 
                                  property_tax_expense + reserves_expense + 
                                  administrative_expense + compliance_expense)
        
        # Net Operating Income
        noi = effective_gross_income - total_operating_expenses
        
        return {
            'gross_rental_income': gross_rental_income,
            'other_income': other_income,
            'gross_income': gross_income,
            'vacancy_amount': gross_income * self.operating.vacancy_rate,
            'effective_gross_income': effective_gross_income,
            'management_expense': management_expense,
            'maintenance_expense': maintenance_expense,
            'utilities_expense': utilities_expense,
            'insurance_expense': insurance_expense,
            'property_tax_expense': property_tax_expense,
            'reserves_expense': reserves_expense,
            'administrative_expense': administrative_expense,
            'compliance_expense': compliance_expense,
            'total_operating_expenses': total_operating_expenses,
            'noi': noi,
            'expense_ratio': total_operating_expenses / effective_gross_income,
            'noi_per_unit': noi / total_units
        }
    
    def calculate_sources_and_uses(self, site_data: Dict) -> Dict:
        """Complete sources and uses analysis"""
        
        # Calculate costs
        cost_data = self.calculate_project_costs(site_data)
        
        # Calculate income
        income_data = self.calculate_operating_income(site_data, cost_data)
        
        # Calculate LIHTC credits
        qct_dda_eligible = site_data.get('qct_dda_eligible', True)
        credit_data = self.calculate_lihtc_credits(cost_data['total_development_cost'], qct_dda_eligible)
        
        # Calculate debt capacity
        debt_data = self.calculate_debt_capacity(income_data['noi'])
        
        # Soft funding
        soft_home_funds = cost_data['total_units'] * self.soft_funds.home_funds_per_unit
        soft_trust_funds = cost_data['total_units'] * self.soft_funds.trust_fund_per_unit
        utility_rebates = cost_data['total_units'] * self.soft_funds.utility_rebates_per_unit
        
        # Developer fee
        developer_fee = cost_data['total_development_cost'] * self.soft_funds.developer_fee_percentage
        deferred_fee = developer_fee * self.soft_funds.deferred_fee_percentage
        cash_fee = developer_fee - deferred_fee
        
        # Sources calculation
        sources = {
            'lihtc_4pct_proceeds': credit_data['credit_4pct_proceeds'],
            'lihtc_9pct_proceeds': credit_data['credit_9pct_proceeds'],
            'permanent_loan': debt_data['net_loan_proceeds'],
            'home_funds': soft_home_funds,
            'trust_funds': soft_trust_funds,
            'utility_rebates': utility_rebates,
            'deferred_developer_fee': deferred_fee,
            'cdbg_funds': self.soft_funds.cdbg_funds,
            'aht_funds': self.soft_funds.aht_funds
        }
        
        # Calculate total sources for 4% and 9% scenarios
        total_sources_4pct = (sources['lihtc_4pct_proceeds'] + sources['permanent_loan'] + 
                             sources['home_funds'] + sources['trust_funds'] + 
                             sources['utility_rebates'] + sources['deferred_developer_fee'] +
                             sources['cdbg_funds'] + sources['aht_funds'])
        
        total_sources_9pct = (sources['lihtc_9pct_proceeds'] + sources['permanent_loan'] + 
                             sources['home_funds'] + sources['trust_funds'] + 
                             sources['utility_rebates'] + sources['deferred_developer_fee'] +
                             sources['cdbg_funds'] + sources['aht_funds'])
        
        # Uses
        uses = {
            'hard_costs': cost_data['hard_costs'],
            'soft_costs': cost_data['soft_costs'],
            'land_cost': cost_data['land_cost'],
            'cash_developer_fee': cash_fee,
            'loan_fees': debt_data['loan_fees'],
            'construction_interest': cost_data['hard_costs'] * 
                                   (self.debt.construction_interest_rate * 
                                    self.debt.construction_term_months / 12)
        }
        
        total_uses = sum(uses.values())
        
        # Funding gap analysis
        gap_4pct = total_uses - total_sources_4pct
        gap_9pct = total_uses - total_sources_9pct
        
        return {
            'cost_data': cost_data,
            'income_data': income_data,
            'credit_data': credit_data,
            'debt_data': debt_data,
            'sources': sources,
            'uses': uses,
            'total_sources_4pct': total_sources_4pct,
            'total_sources_9pct': total_sources_9pct,
            'total_uses': total_uses,
            'funding_gap_4pct': gap_4pct,
            'funding_gap_9pct': gap_9pct,
            'feasible_4pct': gap_4pct <= 0,
            'feasible_9pct': gap_9pct <= 0,
            'developer_fee_total': developer_fee,
            'developer_fee_cash': cash_fee,
            'developer_fee_deferred': deferred_fee
        }

def create_scenario_analysis():
    """Create multiple scenarios with different parameter sets"""
    
    # Base case
    base_params = LIHTCFinancialParameters()
    
    # Conservative case (higher costs, lower credit pricing)
    conservative_params = LIHTCFinancialParameters(
        credit_pricing=0.80,  # Lower credit price
        base_construction_cost_per_sf=165.0,  # Higher construction cost
        soft_cost_percentage=0.30  # Higher soft costs
    )
    
    # Optimistic case (lower costs, higher credit pricing)  
    optimistic_params = LIHTCFinancialParameters(
        credit_pricing=0.90,  # Higher credit price
        base_construction_cost_per_sf=140.0,  # Lower construction cost
        soft_cost_percentage=0.20  # Lower soft costs
    )
    
    scenarios = {
        'base': EnhancedLIHTCModel(financial_params=base_params),
        'conservative': EnhancedLIHTCModel(financial_params=conservative_params),
        'optimistic': EnhancedLIHTCModel(financial_params=optimistic_params)
    }
    
    return scenarios

def analyze_parameter_sensitivity(site_data: Dict):
    """Analyze sensitivity to key parameters"""
    
    base_model = EnhancedLIHTCModel()
    base_result = base_model.calculate_sources_and_uses(site_data)
    
    print("PARAMETER SENSITIVITY ANALYSIS")
    print("=" * 50)
    
    # Test different credit pricing levels
    credit_prices = [0.75, 0.80, 0.85, 0.90, 0.95]
    print(f"\nCredit Pricing Sensitivity (Base: {base_model.financial.credit_pricing}):")
    
    for price in credit_prices:
        test_params = LIHTCFinancialParameters(credit_pricing=price)
        test_model = EnhancedLIHTCModel(financial_params=test_params)
        result = test_model.calculate_sources_and_uses(site_data)
        
        gap_4pct = result['funding_gap_4pct']
        gap_9pct = result['funding_gap_9pct']
        
        print(f"  ${price:.2f}: 4% Gap ${gap_4pct:,.0f} | 9% Gap ${gap_9pct:,.0f}")

if __name__ == "__main__":
    # Example usage
    sample_site = {
        'acres': 10.0,
        'target_dua': 12,
        'county': 'TRAVIS',
        'flood_zone': 'X',
        'market_type': 'Suburban',
        'qct_dda_eligible': True,
        'land_cost': 500000,
        'rent_1br_60pct': 988,
        'rent_2br_60pct': 1600,
        'rent_3br_60pct': 1370
    }
    
    # Run analysis
    model = EnhancedLIHTCModel()
    result = model.calculate_sources_and_uses(sample_site)
    
    print("ENHANCED LIHTC FINANCIAL MODEL RESULTS")
    print("=" * 50)
    print(f"Total Development Cost: ${result['cost_data']['total_development_cost']:,.0f}")
    print(f"Cost per Unit: ${result['cost_data']['cost_per_unit']:,.0f}")
    print(f"NOI: ${result['income_data']['noi']:,.0f}")
    print(f"4% Credit Proceeds: ${result['credit_data']['credit_4pct_proceeds']:,.0f}")
    print(f"9% Credit Proceeds: ${result['credit_data']['credit_9pct_proceeds']:,.0f}")
    print(f"Debt Capacity: ${result['debt_data']['net_loan_proceeds']:,.0f}")
    print(f"4% Funding Gap: ${result['funding_gap_4pct']:,.0f}")
    print(f"9% Funding Gap: ${result['funding_gap_9pct']:,.0f}")
    print(f"4% Feasible: {result['feasible_4pct']}")
    print(f"9% Feasible: {result['feasible_9pct']}")
    
    # Sensitivity analysis
    analyze_parameter_sensitivity(sample_site)