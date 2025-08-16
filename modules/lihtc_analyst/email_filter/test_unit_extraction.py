#!/usr/bin/env python3
"""Test unit extraction patterns"""

import re

test_subjects = [
    "Price Reduced: 6 Units in Prime Van Nuys | Meticulously Renovated with 3 New Construction Units",
    "For Sale : Silver Lake 6-Unit Multifamily | 9.57% Proforma CAP",
    "Just Listed: Triplex in Prime Corona | 5.54% Actual Cap Rate | Pride of Ownership",
    "New Exclusive Listing: 10200 De Soto Avenue - 86-Unit Value-Add Opportunity in Chatsworth, CA",
    "Bay Area Waterfront Investment Opportunity | 260-Unit Value-Add Community in Vallejo, California",
    "Just Listed: Duplex in Los Angeles",
    "Fourplex for Sale in San Diego"
]

# Test patterns
unit_patterns = [
    r'(\d+)\s*-?\s*[Uu]nits?\b',
    r'(\d+)\s*[Uu]nit\b',
    r'(\d+)\s*[Aa]partments?\b',
    r'(\d+)\s*[Dd]oors?\b',
    r'(\d+)\s*[Bb]eds?\b',
    r'(\d+)\s*[Rr]esidential\s*[Uu]nits?\b'
]

property_type_units = {
    'duplex': 2,
    'triplex': 3,
    'fourplex': 4,
    'quadplex': 4,
    '4-plex': 4,
    '4plex': 4
}

print("Testing unit extraction patterns:")
print("=" * 80)

for subject in test_subjects:
    print(f"\nSubject: {subject}")
    
    # Try regex patterns
    units_found = None
    for pattern in unit_patterns:
        matches = re.findall(pattern, subject)
        if matches:
            print(f"  Pattern '{pattern}' found: {matches}")
            if not units_found:
                units_found = int(matches[0])
    
    # Try property type matching
    subject_lower = subject.lower()
    for prop_type, units in property_type_units.items():
        if prop_type in subject_lower:
            print(f"  Property type '{prop_type}' found: {units} units")
            if not units_found:
                units_found = units
    
    print(f"  FINAL UNIT COUNT: {units_found}")
    
    if units_found and units_found < 50:
        print(f"  ⚠️  SHOULD BE DELETED (< 50 units)")
    elif units_found and units_found >= 50:
        print(f"  ✅ Should be kept (>= 50 units)")
    else:
        print(f"  ❓ Could not determine unit count")