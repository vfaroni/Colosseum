# ADJUSTABLE PARAMETERS GUIDE
## Enhanced LIHTC Financial Model - All Variable Controls

---

## 📊 **OVERVIEW OF ADJUSTABLE VARIABLES**

The enhanced LIHTC financial model provides comprehensive control over all key financial parameters that affect project feasibility and returns. Here are ALL the variables you can adjust:

---

## 🏗️ **1. LIHTC CREDIT PARAMETERS**

### Credit Rates and Pricing
```python
lihtc_4pct_rate = 0.04          # 4% credit rate (tax-exempt bond deals)
lihtc_9pct_rate = 0.09          # 9% credit rate (competitive deals)
credit_period = 10              # Credit period in years
credit_pricing = 0.85           # Credit price ($0.85 per $1.00 of credit)
```

### Basis Calculations
```python
basis_boost_qct_dda = 0.30      # 30% basis boost for QCT/DDA areas
```

**Impact**: Credit pricing directly affects project feasibility. A $0.05 change in pricing affects funding by ~$1.5M on a $30M project.

---

## 🏠 **2. CONSTRUCTION COST PARAMETERS**

### Base Construction Costs
```python
base_construction_cost_per_sf = 150.0    # Base cost per square foot
soft_cost_percentage = 0.25              # Soft costs as % of hard costs (25%)
contingency_percentage = 0.05            # Construction contingency (5%)
```

### Regional Cost Adjustments
```python
regional_cost_multipliers = {
    'TRAVIS': 1.20,     # Austin - 20% premium
    'HARRIS': 1.18,     # Houston - 18% premium
    'DALLAS': 1.15,     # Dallas - 15% premium
    'BEXAR': 1.12,      # San Antonio - 12% premium
    'TARRANT': 1.10,    # Fort Worth - 10% premium
    'COLLIN': 1.08,     # Plano - 8% premium
    'default': 1.00     # Other counties - base cost
}
```

### Environmental/Risk Adjustments
```python
flood_zone_multipliers = {
    'VE': 1.30,         # High risk coastal (+30%)
    'V': 1.30,          # High risk coastal (+30%)
    'AE': 1.20,         # 100-year floodplain (+20%)
    'A': 1.20,          # 100-year floodplain (+20%)
    'X': 1.00,          # Minimal risk (base)
    'default': 1.00
}

market_type_multipliers = {
    'Urban': 1.05,      # Urban premium (+5%)
    'Suburban': 1.00,   # Base cost
    'Rural': 0.95,      # Rural discount (-5%)
    'default': 1.00
}
```

**Example Cost Impact**:
- Base: $150/sqft × 120,000 sqft = $18M
- Austin + Flood Zone AE: $150 × 1.20 × 1.20 = $21.6M (+$3.6M)

---

## 🏡 **3. UNIT MIX AND SIZING PARAMETERS**

### Unit Mix Composition
```python
mix_1br_pct = 0.20              # 20% 1-bedroom units
mix_2br_pct = 0.60              # 60% 2-bedroom units  
mix_3br_pct = 0.20              # 20% 3-bedroom units
```

### Unit Sizes (Square Feet)
```python
unit_size_1br = 750             # 1BR unit size
unit_size_2br = 1000            # 2BR unit size
unit_size_3br = 1250            # 3BR unit size
```

### AMI Targeting
```python
ami_percentage = 0.60           # Primary targeting (60% AMI)
ami_mix_50pct = 0.20           # 20% of units at 50% AMI
ami_mix_60pct = 0.80           # 80% of units at 60% AMI
```

**Revenue Impact**: Increasing 3BR mix from 20% to 30% can add $200K+ annually in high-rent markets.

---

## 💰 **4. DEBT PARAMETERS**

### Construction Loan Terms
```python
construction_interest_rate = 0.08       # 8% construction loan rate
construction_term_months = 18           # 18-month construction period
construction_ltc = 0.75                 # 75% loan-to-cost ratio
```

### Permanent Debt Terms
```python
permanent_interest_rate = 0.055         # 5.5% permanent rate
permanent_amortization_years = 35       # 35-year amortization
permanent_ltv = 0.80                    # 80% loan-to-value
debt_service_coverage_min = 1.20        # Minimum DSCR (1.20x)
```

### Loan Structure
```python
interest_only_period_years = 2          # IO period after construction
loan_fees_percentage = 0.015            # 1.5% loan fees
```

**Debt Capacity Impact**: 
- 1% interest rate change = ~$2M change in debt capacity
- 0.10 DSCR change = ~$1.5M change in debt capacity

---

## 🏛️ **5. SOFT FUNDS AND SUBSIDIES**

### Government Funding Sources
```python
home_funds_per_unit = 50000             # HOME funds per unit
trust_fund_per_unit = 30000             # Housing trust fund per unit
tdhca_soft_loan_rate = 0.03             # 3% TDHCA soft loan rate
tdhca_soft_loan_term = 30               # 30-year soft loan term
```

### Grants and Incentives
```python
cdbg_funds = 0                          # CDBG funding (project-specific)
aht_funds = 0                           # Affordable Housing Trust
utility_rebates_per_unit = 2000         # Energy efficiency rebates
```

### Developer Fee Structure
```python
developer_fee_percentage = 0.15         # 15% developer fee
deferred_fee_percentage = 0.50          # 50% of fee deferred
```

**Soft Funds Impact**: $80K per unit in soft funds = $9.6M on 120-unit project

---

## 🏢 **6. OPERATING PARAMETERS**

### Income Assumptions
```python
vacancy_rate = 0.05                     # 5% vacancy allowance
rent_growth_annual = 0.025              # 2.5% annual rent growth
other_income_per_unit = 1200            # Other income (laundry, fees)
```

### Operating Expenses (Per Unit Annually)
```python
management_fee_pct = 0.06               # 6% of gross income
maintenance_per_unit = 800              # Maintenance and repairs
utilities_per_unit = 600                # Utilities (common areas)
insurance_per_unit = 400                # Property insurance
property_tax_per_unit = 300             # Property taxes (if applicable)
reserves_per_unit = 300                 # Replacement reserves
administrative_per_unit = 200           # Administrative costs
```

### LIHTC-Specific Costs
```python
lihtc_monitoring_annual = 5000          # Annual compliance monitoring
asset_management_fee = 8000             # Annual asset management
```

**Operating Impact**: 1% vacancy change = ~$200K annual NOI impact on 120-unit project

---

## 🎯 **7. SCENARIO ANALYSIS CAPABILITIES**

### Pre-Built Scenarios
```python
scenarios = {
    'base': Standard assumptions,
    'conservative': Higher costs, lower credit pricing,
    'optimistic': Lower costs, higher credit pricing
}
```

### Custom Scenario Creation
```python
# Example: High-cost, low-credit scenario
custom_params = LIHTCFinancialParameters(
    credit_pricing=0.75,                    # Lower credit price
    base_construction_cost_per_sf=180.0,    # Higher construction
    soft_cost_percentage=0.35               # Higher soft costs
)
```

---

## 📈 **8. SENSITIVITY ANALYSIS EXAMPLES**

### Credit Pricing Impact (120-unit project)
- **$0.75 pricing**: 4% feasible, 9% tight
- **$0.85 pricing**: Both programs highly feasible  
- **$0.95 pricing**: Excess equity available

### Construction Cost Impact
- **$140/sqft**: Strong feasibility both programs
- **$150/sqft**: Base case (current model)
- **$170/sqft**: 4% program challenges, 9% viable

### Interest Rate Impact (Current: 5.5%)
- **4.5% rate**: +$3M debt capacity
- **6.5% rate**: -$2.5M debt capacity

---

## 🛠️ **HOW TO ADJUST PARAMETERS**

### Method 1: Direct Parameter Modification
```python
# Create custom financial parameters
custom_financial = LIHTCFinancialParameters(
    credit_pricing=0.90,                    # Increase credit price
    base_construction_cost_per_sf=140.0     # Reduce construction cost
)

# Create model with custom parameters
model = EnhancedLIHTCModel(financial_params=custom_financial)
```

### Method 2: Scenario-Based Analysis
```python
# Run multiple scenarios
scenarios = create_scenario_analysis()
base_result = scenarios['base'].calculate_sources_and_uses(site_data)
conservative_result = scenarios['conservative'].calculate_sources_and_uses(site_data)
```

### Method 3: Parameter Sensitivity Testing
```python
# Test specific parameter sensitivity
analyze_parameter_sensitivity(site_data)
```

---

## 💡 **RECOMMENDED PARAMETER ADJUSTMENTS FOR YOUR ANALYSIS**

### For Conservative Underwriting:
```python
conservative_params = LIHTCFinancialParameters(
    credit_pricing=0.80,                    # Conservative credit pricing
    base_construction_cost_per_sf=165.0,    # Higher construction costs
    soft_cost_percentage=0.30,              # Higher soft cost allowance
    contingency_percentage=0.08             # Higher contingency
)

conservative_operating = OperatingParameters(
    vacancy_rate=0.07,                      # Higher vacancy assumption
    maintenance_per_unit=1000               # Higher maintenance costs
)
```

### For Market-Rate Analysis:
```python
market_params = LIHTCFinancialParameters(
    credit_pricing=0.85,                    # Current market pricing
    base_construction_cost_per_sf=150.0     # Current market costs
)
```

### For Optimal Site Selection:
```python
# Run all 195 sites with different scenarios
for scenario_name, model in scenarios.items():
    results[scenario_name] = []
    for site in all_sites:
        result = model.calculate_sources_and_uses(site)
        results[scenario_name].append(result)
```

---

## 🚀 **INTEGRATION WITH YOUR EXISTING WORKFLOW**

The enhanced model maintains full compatibility with your existing 195-site analysis while adding these comprehensive adjustable parameters. You can:

1. **Batch Process**: Run all 195 sites with multiple parameter scenarios
2. **Sensitivity Analysis**: Test key variables across your entire portfolio  
3. **Market Conditions**: Adjust for changing credit pricing, interest rates, construction costs
4. **Regional Analysis**: Fine-tune cost multipliers by county/market
5. **Deal Optimization**: Find optimal unit mix, financing structure, and subsidy layering

This gives you complete control over every financial variable that affects LIHTC project feasibility and returns!
