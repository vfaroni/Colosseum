#!/usr/bin/env python3
"""Test edge cases to ensure we don't have false positives"""

from email_deal_filter_oauth_improved import EmailDealFilterOAuth

def test_edge_cases():
    filter_tool = EmailDealFilterOAuth()
    
    # Test subjects that should NOT be flagged as non-deal emails
    # These are legitimate "for sale" emails that should be kept
    legitimate_sale_subjects = [
        "FOR SALE: 150 Units in Sacramento, CA",
        "Now available for sale - 89 unit complex in Phoenix",
        "Sale opportunity: 200-unit development in Fresno",
        "Exclusive sale listing - Downtown LA property",
        "Private sale - Multifamily investment in Arizona",
        "Off-market sale - 75 units in San Diego"
    ]
    
    # Test subjects that SHOULD be flagged as non-deal emails  
    completed_sale_subjects = [
        "Just sold - 150 Units in Sacramento, CA",
        "Recently sold: 89 unit complex in Phoenix", 
        "Sale completed - 200-unit development in Fresno",
        "Transaction completed - Downtown LA property",
        "Just closed - Multifamily investment in Arizona",
        "Deal closed - 75 units in San Diego"
    ]
    
    print("Testing LEGITIMATE SALE emails (should NOT be flagged as non-deal):")
    print("=" * 80)
    
    for subject in legitimate_sale_subjects:
        analysis = filter_tool.extract_from_subject(subject)
        should_delete, reason = filter_tool.should_delete_email(analysis)
        
        print(f"\nSubject: {subject}")
        print(f"Is non-deal: {analysis.get('is_non_deal', False)}")
        print(f"Should delete: {should_delete}")
        print(f"Reason: {reason}")
        
        if analysis.get('is_non_deal', False):
            print("❌ FALSE POSITIVE: Legitimate sale email flagged as non-deal!")
        else:
            print("✅ CORRECT: Legitimate sale email not flagged")
        print("-" * 80)
    
    print("\n\nTesting COMPLETED SALE emails (SHOULD be flagged as non-deal):")
    print("=" * 80)
    
    for subject in completed_sale_subjects:
        analysis = filter_tool.extract_from_subject(subject)
        should_delete, reason = filter_tool.should_delete_email(analysis)
        
        print(f"\nSubject: {subject}")
        print(f"Is non-deal: {analysis.get('is_non_deal', False)}")
        print(f"Should delete: {should_delete}")
        print(f"Reason: {reason}")
        
        if not analysis.get('is_non_deal', False):
            print("❌ FALSE NEGATIVE: Completed sale email NOT flagged as non-deal!")
        else:
            print("✅ CORRECT: Completed sale email properly flagged")
        print("-" * 80)

if __name__ == "__main__":
    test_edge_cases()