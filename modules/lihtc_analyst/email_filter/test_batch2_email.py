#!/usr/bin/env python3
"""Test the specific email from Batch 2 that was incorrectly kept"""

from email_deal_filter_oauth_improved import EmailDealFilterOAuth

def test_batch2_problematic_email():
    filter_tool = EmailDealFilterOAuth()
    
    # The specific email from Batch 2 that was incorrectly kept
    problematic_email = "Just Sold | First Waterfront Transaction Since 2019 | Villa Del Mar in Marina Del Rey"
    
    print("Testing the specific problematic email from Batch 2:")
    print("=" * 80)
    print(f"Email: {problematic_email}")
    print("=" * 80)
    
    analysis = filter_tool.extract_from_subject(problematic_email)
    should_delete, reason = filter_tool.should_delete_email(analysis)
    
    print(f"Is non-deal: {analysis.get('is_non_deal', False)}")
    print(f"Location: {analysis.get('location_state', 'Unknown')}")
    print(f"Units: {analysis.get('number_of_units', 'Unknown')}")
    print(f"Should delete: {should_delete}")
    print(f"Reason: {reason}")
    
    print("\n" + "=" * 80)
    if should_delete and analysis.get('is_non_deal', False):
        print("✅ SUCCESS: Email is now correctly flagged for deletion!")
        print("✅ This email would now be filtered out properly.")
    else:
        print("❌ FAILURE: Email is still not being flagged correctly.")
        print("❌ The fix did not work as expected.")
    print("=" * 80)

if __name__ == "__main__":
    test_batch2_problematic_email()