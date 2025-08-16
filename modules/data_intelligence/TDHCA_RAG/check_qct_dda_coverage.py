#!/usr/bin/env python3
"""
Check data coverage for QCT/DDA sites specifically
"""

import pandas as pd
import numpy as np

# Load the comprehensive sheet
df = pd.read_excel("D'Marco_Sites/Analysis_Results/COMPREHENSIVE_MASTER_WITH_COSTS_20250801_174753.xlsx", sheet_name='Comprehensive_Analysis')

print(f'Total sites in comprehensive sheet: {len(df)}')

# Check what values exist in Basis_Boost_Eligible
print('\nBasis_Boost_Eligible values:')
print(df['Basis_Boost_Eligible'].value_counts())

# Check QCT/DDA coverage
qct_dda_sites = df[df['Basis_Boost_Eligible'] != 'MISSING']
print(f'\nSites with QCT/DDA data (non-MISSING): {len(qct_dda_sites)}')

if len(qct_dda_sites) > 0:
    print(f'\nData coverage for {len(qct_dda_sites)} QCT/DDA analyzed sites:')
    
    # Key data fields to check
    key_fields = [
        'ACS_Poverty_Rate', 'AMI_60_2BR', 'Schools_Within_3_Miles', 
        'QCT_Status', 'DDA_Status', 'Basis_Boost_Eligible',
        'Competing_Projects_Within_10_Miles', 'Construction_Cost_Multiplier'
    ]
    
    for field in key_fields:
        if field in df.columns:
            not_missing = (qct_dda_sites[field] != 'MISSING').sum()
            coverage_pct = (not_missing / len(qct_dda_sites)) * 100
            print(f'  {field}: {not_missing}/{len(qct_dda_sites)} ({coverage_pct:.1f}% coverage)')
    
    # Check for sites with complete core data
    core_complete = (
        (qct_dda_sites['ACS_Poverty_Rate'] != 'MISSING') &
        (qct_dda_sites['AMI_60_2BR'] != 'MISSING') &
        (qct_dda_sites['Construction_Cost_Multiplier'] != 'MISSING')
    ).sum()
    
    print(f'\nSites with complete core data (poverty + AMI + costs): {core_complete}/{len(qct_dda_sites)}')

# Also check Census API coverage
census_sites = df[df['Census_Data_Source'] != 'MISSING']
print(f'\nSites with Census API poverty data: {len(census_sites)}')

# Check AMI coverage
ami_sites = df[df['AMI_60_2BR'] != 'MISSING']
print(f'Sites with HUD AMI rent data: {len(ami_sites)}')

# Check school coverage
school_sites = df[df['Schools_Within_3_Miles'] != 'MISSING']
print(f'Sites with school analysis data: {len(school_sites)}')