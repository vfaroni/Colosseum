#!/usr/bin/env python3
"""Test script to demonstrate improvements in email filtering"""

from email_deal_filter_oauth_improved import EmailDealFilterOAuth

def test_subject_analysis():
    """Test the improved subject line analysis"""
    filter_tool = EmailDealFilterOAuth()
    
    test_subjects = [
        # Should be KEPT (CA/AZ/NM with 50+ units or land opportunities)
        "150-Unit Multifamily Portfolio in Phoenix, AZ",
        "Rocklin, CA 7.19 AC 33 DU/Ac Development Site",
        "New Mexico Land Opportunity - 10 Acres Entitled for 200 Units",
        "100-Unit Apartment Complex in Los Angeles, CA",
        "Tucson, AZ - 75 Unit Value-Add Opportunity",
        
        # Should be DELETED (wrong state or too few units)
        "6-Unit Multifamily in Arlington Heights, IL",
        "10-Unit Apartment Building in Houston, TX",
        "Worcester, MA - 45 Unit Property For Sale",
        "Des Moines, IA Retail Center Available",
        "PE Lofts - 200 Units in Richmond, VA",
        
        # Edge cases
        "Development Site: 5 Acres in CA with 45 DU/Ac Density",
        "Mixed-Use Property - 30 Residential Units + Retail in NM",
    ]
    
    print("=== SUBJECT LINE ANALYSIS TEST ===\n")
    
    for subject in test_subjects:
        analysis = filter_tool.extract_from_subject(subject)
        should_delete, reason = filter_tool.should_delete_email(analysis)
        
        print(f"Subject: {subject}")
        print(f"  State: {analysis['location_state']}")
        print(f"  Units: {analysis['number_of_units']}")
        print(f"  Land Opportunity: {analysis['is_land_opportunity']}")
        print(f"  Should Delete: {should_delete}")
        print(f"  Reason: {reason}")
        print()

def test_state_matching():
    """Test improved state matching with word boundaries"""
    filter_tool = EmailDealFilterOAuth()
    
    test_cases = [
        ("PE Lofts in Richmond, VA", "Virginia"),  # Should correctly identify VA
        ("Property in CA near the beach", "California"),  # Should identify CA
        ("SCAM property listing", None),  # Should NOT match "SC" in "SCAM"
        ("Email from MACY's about property", None),  # Should NOT match "MA" in "MACY's"
    ]
    
    print("\n=== STATE MATCHING TEST ===\n")
    
    for text, expected_state in test_cases:
        analysis = filter_tool.extract_from_subject(text)
        print(f"Text: {text}")
        print(f"  Expected State: {expected_state}")
        print(f"  Detected State: {analysis['location_state']}")
        print(f"  Match: {'✓' if analysis['location_state'] == expected_state else '✗'}")
        print()

def test_land_detection():
    """Test land opportunity detection"""
    filter_tool = EmailDealFilterOAuth()
    
    test_cases = [
        ("Development Site with 100 DU/Ac in Phoenix", True),
        ("100-Unit Existing Apartment Complex", False),
        ("Entitled Land - Zoned for 200 Units", True),
        ("45 Units Built in 2020", False),
        ("Raw Land Opportunity - 5 Acres", True),
    ]
    
    print("\n=== LAND OPPORTUNITY DETECTION TEST ===\n")
    
    for subject, expected_is_land in test_cases:
        analysis = filter_tool.extract_from_subject(subject)
        print(f"Subject: {subject}")
        print(f"  Expected Land Opportunity: {expected_is_land}")
        print(f"  Detected Land Opportunity: {analysis['is_land_opportunity']}")
        print(f"  Match: {'✓' if analysis['is_land_opportunity'] == expected_is_land else '✗'}")
        print()

if __name__ == "__main__":
    print("Testing Email Deal Filter Improvements\n")
    print("=" * 50)
    
    test_subject_analysis()
    test_state_matching()
    test_land_detection()
    
    print("\n=== KEY IMPROVEMENTS ===")
    print("1. Subject line analysis now extracts location and unit counts")
    print("2. State abbreviations are matched with word boundaries (no false positives)")
    print("3. Land opportunities are identified and not filtered by unit count")
    print("4. HTML emails are parsed better with BeautifulSoup")
    print("5. Analysis prioritizes subject line data to reduce API calls")