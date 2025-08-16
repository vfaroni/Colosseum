
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
    