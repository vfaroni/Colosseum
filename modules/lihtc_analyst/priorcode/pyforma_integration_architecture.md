# PYFORMA Integration Architecture for LIHTC Analysis System

## Overview
This document outlines the integration of pyforma (Oakland Analytics) with our existing LIHTC analysis pipeline to create a comprehensive real estate pro forma system.

## Current System Architecture

### Your Existing Data Sources
1. **CoStar Land Data**: 165 LIHTC-eligible sites with county assignments
2. **TDHCA Competition Data**: 3,189 existing LIHTC projects for competition analysis
3. **HUD AMI Data**: 254 Texas counties with 2025 rent limits
4. **Census Poverty Data**: For 9% low poverty bonus calculations
5. **FEMA Flood Data**: Construction cost impacts

### New Data Sources to Add
1. **REDIQ**: Operating expense benchmarks by market type
2. **CoStar Rent Comps**: Market rent data (up to 500 records per query)
3. **pyforma**: High-performance pro forma engine (18M calculations/second)

## How The Integration Works

### Data Flow Process
**STEP 1: Data Collection**
- Load your existing 195 sites from Excel
- Pull REDIQ expense data for each market type
- Query CoStar for rent comps by county/city
- Access HUD AMI data (already integrated)

**STEP 2: pyforma Configuration**
- Configure unit mix (1BR, 2BR, 3BR) with market rents
- Set AMI requirements (60% AMI for LIHTC)
- Input operating expenses from REDIQ
- Set construction costs with flood zone adjustments

**STEP 3: Vectorized Analysis**
- Process all 195 sites simultaneously (instead of one-by-one)
- Generate complete pro formas in seconds
- Calculate revenue, costs, and returns for each site

**STEP 4: Enhanced Reporting**
- Rank sites by financial performance
- Include detailed pro forma sheets
- Show sensitivity to market rent changes
- Export to Excel with enhanced analysis

## Data Flow Integration Points

### 1. Enhanced Site Analysis Pipeline
```python
# Current: texas_economic_viability_analyzer_final.py
# Enhanced: pyforma_enhanced_texas_analyzer.py

def analyze_site_with_pyforma(site_data):
    # Existing analysis
    qct_dda_status = check_qct_dda_eligibility(site_data)
    competition_risk = analyze_tdhca_competition(site_data)
    poverty_bonus = calculate_poverty_bonus(site_data)
    
    # NEW: pyforma integration
    rent_comps = get_costar_rent_comps(site_data.county, site_data.city)
    expense_comps = get_rediq_expense_data(site_data.county, site_data.market_type)
    
    # pyforma configuration
    cfg = {
        "use_types": build_unit_mix_config(site_data, rent_comps),
        "parcel_size": site_data.acres * 43560,  # Convert to sqft
        "building_type": determine_building_type(site_data),
        "affordable_housing": {
            "AMI": get_hud_ami_for_county(site_data.county),
            "depth_of_affordability": 0.60,  # 60% AMI
            "pct_affordable_units": 1.0 if site_data.program == "LIHTC" else 0.20
        },
        "operating_expenses": expense_comps.total_per_unit,
        "construction_costs": get_construction_costs(site_data.county, site_data.flood_zone)
    }
    
    # Run pyforma analysis
    proforma_results = pyforma.spot_residential_sales_proforma(cfg)
    
    # Combine with existing analysis
    return combine_analysis_results(
        existing_analysis, 
        proforma_results,
        competition_risk,
        poverty_bonus
    )
```

### 2. Vectorized Analysis for All Sites
```python
# NEW: pyforma_bulk_analyzer.py
def analyze_all_sites_vectorized():
    # Load all 195 sites
    sites_df = pd.read_excel("FINAL_195_Sites_Complete_With_Poverty.xlsx")
    
    # Prepare pyforma config for vectorized analysis
    cfg = {
        "use_types": build_vectorized_unit_mix(sites_df),
        "parcel_size": sites_df['acres'] * 43560,
        "built_dua": sites_df['target_density'],
        "affordable_housing": {
            "AMI": sites_df['hud_ami_2br_60pct'],
            "depth_of_affordability": 0.60,
            "pct_affordable_units": 1.0
        }
    }
    
    # Run 195 pro formas in seconds instead of minutes
    results = pyforma.spot_residential_sales_proforma(cfg)
    
    # Merge with existing analysis
    return merge_with_existing_analysis(sites_df, results)
```

## File Structure Recommendations

### Recommended Directory Structure
**Main Integration Folder**: `pyforma_integration/`
- `pyforma_wrapper.py` - Custom wrapper for LIHTC use
- `lihtc_config_builder.py` - LIHTC-specific configurations  
- `market_data_integrator.py` - REDIQ + CoStar integration
- `vectorized_analyzer.py` - Bulk analysis functions
- `enhanced_reporting.py` - Enhanced reporting with pyforma

**Enhanced Analyzers**: `enhanced_analyzers/`
- `pyforma_enhanced_texas_analyzer.py` - Enhanced version of your current analyzer
- `pyforma_bulk_analyzer.py` - Process all 195 sites at once
- `pyforma_market_validator.py` - Validate against market data

**Market Data**: `market_data/`
- `rediq_integration.py` - REDIQ expense data integration
- `costar_rent_processor.py` - CoStar rent comp processing
- `market_data_cache.py` - Cache expensive API calls

**Reports**: `reports/`
- `pyforma_enhanced_reports.py` - Enhanced Excel/HTML reports
- `comparative_analysis.py` - Before/after comparisons

## Technical Implementation Plan

### Phase 1: Installation and Setup
1. **Install pyforma from GitHub**
   ```bash
   cd /Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code
   pip3 install git+https://github.com/oaklandanalytics/pyforma.git
   ```

2. **Create integration directory**
   ```bash
   mkdir pyforma_integration
   mkdir enhanced_analyzers
   mkdir market_data
   ```

3. **Test basic functionality**
   ```python
   import pyforma
   # Basic test with single site
   ```

### Phase 2: Market Data Integration
1. **REDIQ Integration**
   - API setup or data import process
   - Expense benchmarking by market type
   - Operating expense modeling

2. **CoStar Rent Integration**
   - CSV import and processing
   - Rent comp analysis (up to 500 records)
   - Market positioning analysis

### Phase 3: Enhanced Analysis Pipeline
1. **Wrapper Development**
   - Custom pyforma wrapper for LIHTC
   - Configuration builders
   - Result processors

2. **Vectorized Analysis**
   - Bulk processing of all 195 sites
   - Performance optimization
   - Memory management

### Phase 4: Reporting Enhancement
1. **Enhanced Excel Reports**
   - Detailed pro forma sheets
   - Sensitivity analysis
   - Comparative analysis

2. **Interactive Dashboards**
   - Streamlit integration
   - Real-time updates
   - Market data visualization

## Expected Benefits

### Performance Improvements
- **18M pro formas per second** vs current individual calculations
- **Vectorized processing** of all 195 sites simultaneously
- **900x faster** than scalar loops

### Analysis Depth
- **Comprehensive pro formas** with construction costs, operating expenses, revenues
- **Sensitivity analysis** with market rent variations
- **AMI integration** with existing HUD data

### Market Intelligence
- **REDIQ expense benchmarking** for realistic operating assumptions
- **CoStar rent comps** for market positioning
- **Enhanced reporting** with professional pro forma outputs

### Workflow Efficiency
- **Automated pro forma generation** for all sites
- **Standardized analysis** across all properties
- **Reduced manual Excel modeling**

## Integration Timeline

### Week 1: Setup and Testing
- Install pyforma and dependencies
- Create directory structure
- Test basic functionality

### Week 2: Market Data Integration
- Integrate REDIQ expense data
- Process CoStar rent comps
- Build data pipelines

### Week 3: Enhanced Analysis
- Develop pyforma wrapper
- Create vectorized analyzer
- Test with existing 195 sites

### Week 4: Reporting and Validation
- Enhanced reporting system
- Validation against existing analysis
- Performance optimization

## Success Metrics

1. **Performance**: Process all 195 sites in under 1 minute
2. **Accuracy**: Match existing revenue/cost calculations within 5%
3. **Enhancement**: Provide detailed pro forma outputs for all sites
4. **Market Intelligence**: Integrate REDIQ and CoStar data successfully
5. **Workflow**: Reduce manual analysis time by 80%

This integration will transform our LIHTC analysis from site-by-site calculations to a comprehensive, vectorized pro forma system with real market intelligence.