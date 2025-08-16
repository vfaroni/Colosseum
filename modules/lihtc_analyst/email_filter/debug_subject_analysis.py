#!/usr/bin/env python3
"""Debug subject analysis for problematic emails"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_deal_filter_oauth_improved import EmailDealFilterOAuth

# Initialize filter
filter_tool = EmailDealFilterOAuth()

test_subjects = [
    "Price Reduced: 6 Units in Prime Van Nuys | Meticulously Renovated with 3 New Construction Units",
    "For Sale : Silver Lake 6-Unit Multifamily | 9.57% Proforma CAP",
    "Just Listed: Triplex in Prime Corona | 5.54% Actual Cap Rate | Pride of Ownership"
]

print("Testing subject analysis:")
print("=" * 80)

for subject in test_subjects:
    print(f"\nSubject: {subject}")
    
    analysis = filter_tool.extract_from_subject(subject)
    
    print(f"Analysis result:")
    print(f"  location_state: {analysis['location_state']}")
    print(f"  number_of_units: {analysis['number_of_units']}")
    print(f"  is_land_opportunity: {analysis['is_land_opportunity']}")
    print(f"  is_non_deal: {analysis['is_non_deal']}")
    
    # Apply the filtering logic like the batch script does
    should_delete = False
    reason = ""
    
    if analysis.get('is_non_deal', False):
        should_delete = True
        reason = "Non-deal email"
    elif analysis['location_state'] and analysis['number_of_units'] is not None:
        # Convert state abbreviations to full names for comparison
        state_name = analysis['location_state']
        if state_name == "CA":
            state_name = "California"
        elif state_name == "AZ":
            state_name = "Arizona"
        elif state_name == "NM":
            state_name = "New Mexico"
        
        if state_name not in filter_tool.target_states:
            should_delete = True
            reason = f"Wrong state: {state_name}"
        elif analysis['number_of_units'] < filter_tool.minimum_units:
            should_delete = True
            reason = f"Too few units: {analysis['number_of_units']}"
        else:
            reason = f"{state_name}, {analysis['number_of_units']} units"
    else:
        reason = "Could not determine - kept for review"
    
    print(f"Decision: {'DELETE' if should_delete else 'KEEP'}")
    print(f"Reason: {reason}")
    
    if not should_delete and analysis['number_of_units'] and analysis['number_of_units'] < 50:
        print(f"⚠️  WARNING: This should be deleted but is being kept!")