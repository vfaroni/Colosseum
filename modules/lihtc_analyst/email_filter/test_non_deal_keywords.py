#!/usr/bin/env python3
"""Test non-deal keyword detection functionality"""

from email_deal_filter_oauth_improved import EmailDealFilterOAuth

def test_non_deal_keywords():
    filter_tool = EmailDealFilterOAuth()
    
    # Test subjects that should be detected as non-deal emails
    test_subjects = [
        "CalHFA homebuyer workshop - Join us for free education",
        "Upcoming seminar on real estate investing",
        "Monthly newsletter update - Market trends",
        "Webinar invitation: Property management tips",
        "19 unit Pasadena Playhouse - Investment opportunity",
        "Elmwood Avenue, LA deal - 45 units available",
        "Development site in Phoenix, AZ - 200 units potential",
        "Workshop on financing options for developers",
        "Training session for new agents",
        "Survey: Tell us about your investment needs",
        # NEW TEST CASES: "Just sold" emails that should be filtered out
        "Just Sold | First Waterfront Transaction Since 2019 | Villa Del Mar in Marina Del Rey",
        "Just sold - 42 Units in Downtown LA",
        "Recently sold | 150-unit apartment complex in Phoenix",
        "JUST SOLD: Luxury development in Sacramento, CA",
        "Transaction completed | 89 units | San Diego County",
        "Sale completed - Multifamily property in Fresno"
    ]
    
    print("Testing non-deal keyword detection:")
    print("=" * 60)
    
    for subject in test_subjects:
        analysis = filter_tool.extract_from_subject(subject)
        should_delete, reason = filter_tool.should_delete_email(analysis)
        
        print(f"\nSubject: {subject}")
        print(f"Is non-deal: {analysis.get('is_non_deal', False)}")
        print(f"Location: {analysis.get('location_state', 'Unknown')}")
        print(f"Units: {analysis.get('number_of_units', 'Unknown')}")
        print(f"Should delete: {should_delete}")
        print(f"Reason: {reason}")
        print("-" * 60)

if __name__ == "__main__":
    test_non_deal_keywords()