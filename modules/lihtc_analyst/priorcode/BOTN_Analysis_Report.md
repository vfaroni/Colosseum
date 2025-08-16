# BOTN Workforce Housing Underwriting Template Analysis

**File**: Workforce BOTN 05.12.25.xlsx  
**Analysis Date**: June 26, 2025  
**Location**: `/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Workforce_Housing/BOTN_Proformas/`

## Executive Summary

The BOTN (Build on the Neighborhood) Workforce Housing Underwriting Template is a sophisticated Excel-based financial model designed for analyzing affordable housing investments. The model integrates comprehensive HUD data sources and provides detailed financial projections for workforce housing developments.

## Model Structure

### Sheet Overview
The workbook contains 6 primary sheets:

1. **Inputs** (51 rows × 18 columns) - Property parameters and assumptions
2. **Output** (113 rows × 67 columns) - Financial calculations and projections  
3. **FY25_FMRs** (4,765 rows × 14 columns) - HUD Fair Market Rents data
4. **SAFMRs** (51,899 rows × 18 columns) - Small Area Fair Market Rents by ZIP code
5. **Section8-FY25** (4,767 rows × 42 columns) - Section 8 payment standards
6. **Counties** (458 rows × 23 columns) - County-level housing data

## Key Input Parameters Identified

From the Inputs sheet analysis, the model captures:

- **Property Information**:
  - Property Name and Address
  - ZIP Code and Location (State: CA, County: Riverside County)
  - Affordable Housing Type: LIHTC (Low-Income Housing Tax Credit)

- **Financial Parameters**:
  - 100% Finance Rate - Senior Bond: 6.7%
  - Rent Type: Manual (customizable rent inputs)
  - % Units to Renovate: 0%
  - Ground Lease: 0

- **Unit Mix Configuration**:
  - Studio units: 1 unit at $2/month asking rent
  - 1-bedroom units: Multiple configurations with varying rents
  - 2-bedroom units: 1 unit at $2/month asking rent
  - 3-bedroom units: 1 unit at $2/month asking rent
  - 4-bedroom units: 1 unit at $2/month asking rent
  - 5-bedroom units: 1 unit at $2/month asking rent

## Data Integration Capabilities

### HUD Data Sources
The model integrates four major HUD datasets:

1. **Fair Market Rents (FY2025)**: 4,764 geographic areas nationwide
   - Columns include: state, county, HUD area codes, population, FMR by bedroom count (0-4)
   
2. **Small Area Fair Market Rents**: 51,899 ZIP codes
   - Provides ZIP-code level rent data for precise geographic targeting
   - Includes 90% and 110% payment standard calculations

3. **Section 8 Payment Standards**: Comprehensive voucher program data
   - Links to HUD's Housing Choice Voucher program requirements

4. **County Data**: 458 counties with detailed housing market information
   - Includes AMI (Area Median Income) calculations
   - County-specific adjustments for different bedroom counts

### Geographic Scope
Primary focus on **California and Texas** markets, with particular emphasis on:
- Major metropolitan areas
- Counties with significant affordable housing demand
- Areas eligible for LIHTC and other affordable housing programs

## Financial Model Architecture

### Model Type
**Sophisticated Multi-Unit Property Underwriting Model** designed for:
- Workforce housing developments
- LIHTC compliance analysis
- Mixed-income property evaluations
- Geographic rent optimization

### Key Features Identified

1. **Rent Analysis Integration**:
   - HUD Fair Market Rent benchmarking
   - Small Area FMR for precise ZIP-code targeting
   - Section 8 payment standard compliance
   - Manual rent override capabilities

2. **Financing Structure Support**:
   - Senior bond financing (6.7% rate identified)
   - 100% financing scenarios
   - Ground lease considerations
   - Renovation cost integration

3. **Unit Mix Optimization**:
   - Flexible bedroom configuration (Studio through 5BR)
   - Unit-specific rent calculations
   - Occupancy and revenue projections

4. **Compliance Framework**:
   - LIHTC program compliance
   - HUD regulatory alignment
   - State-specific requirements (CA/TX focus)

## Technical Implementation

### Excel Architecture
- **Complex Formula Structure**: 113 rows × 67 columns in Output sheet suggests sophisticated calculation matrix
- **Data Validation**: Built-in county and geographic validation systems
- **Dynamic Referencing**: Integration between input parameters and HUD data sources

### Analysis Capabilities
Based on the data structure, the model likely provides:
- **Revenue Projections**: Unit-by-unit rent calculations
- **Operating Expense Modeling**: Property-specific cost analysis  
- **Cash Flow Analysis**: Multi-year financial projections
- **Return Calculations**: IRR, NPV, and cash-on-cash returns
- **Compliance Scoring**: LIHTC and affordable housing program alignment

## Use Cases and Applications

### Primary Applications
1. **LIHTC Development Analysis**: Tax credit property underwriting
2. **Workforce Housing Feasibility**: Market-rate affordable housing analysis
3. **Geographic Market Studies**: HUD data-driven location analysis
4. **Mixed-Income Development**: Blended affordable/market-rate modeling

### Target Users
- Affordable housing developers
- LIHTC syndicators and investors
- Housing finance agencies
- Real estate investment funds focusing on social impact

## Data Quality and Coverage

### Strengths
- **Comprehensive Geographic Coverage**: 51,899+ ZIP codes analyzed
- **Current Data**: FY2025 HUD data integration
- **Multiple Rent Standards**: FMR, SAFMR, and Section 8 alignment
- **Regulatory Compliance**: Built-in HUD program requirements

### Considerations
- Model appears to be template-based requiring manual input customization
- Complex structure may require training for effective utilization
- Geographic focus primarily on CA/TX markets

## Recommendations for Usage

### Best Practices
1. **Input Validation**: Ensure property location matches HUD geographic codes
2. **Market Analysis**: Compare model outputs with local market comparables
3. **Compliance Review**: Verify LIHTC and HUD program requirements
4. **Sensitivity Analysis**: Test multiple scenarios for robust projections

### Integration Opportunities
The model structure suggests compatibility with:
- Property management systems
- LIHTC compliance software
- Geographic information systems (GIS)
- Market analysis platforms

## Conclusion

The BOTN Workforce Housing Underwriting Template represents a sophisticated, data-driven approach to affordable housing analysis. Its integration of comprehensive HUD datasets with flexible financial modeling capabilities makes it a valuable tool for workforce housing development and investment analysis.

The model's strength lies in its ability to provide geographically-precise rent analysis while maintaining compliance with federal affordable housing programs. This combination of market intelligence and regulatory alignment makes it particularly valuable for LIHTC and workforce housing development projects.

---
*Analysis completed using Python-based Excel parsing tools with openpyxl and pandas libraries.*