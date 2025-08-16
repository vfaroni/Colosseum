#!/usr/bin/env python3
"""Test the fixed non-deal keyword detection"""

from email_deal_filter_oauth_improved import EmailDealFilterOAuth

def test_problematic_emails():
    """Test emails that were incorrectly deleted"""
    
    filter_tool = EmailDealFilterOAuth()
    
    # Test cases that should be KEPT (not deleted)
    should_keep = [
        "REMINDER CALL FOR OFFERS | TUESDAY, JULY 15, 2025 | Valle at Fairway | 68 Units | Value-Add Asset | La Mesa, CA",
        "REMINDER - CALL FOR OFFERS: July 18th, 2025 | MV on 3rd | 60 Units located in Midtown Phoenix",
        "Reminder Call for Offers | 350 Units in Affluent Hacienda Heights, CA of the San Gabriel Valley | Due: July 16th",
        "Re: Just Listed: 133 Senior LIHTC Units in San Diego County"
    ]
    
    # Test cases that should still be DELETED
    should_delete = [
        "eNews: Join CalHFA at a FREE Homebuyer Workshop in Temecula",
        "Just Closed | Avana Desert View | 412 Units | Scottsdale, Arizona",
        "Recently Financed: Multifamily Apartments | San Diego, CA",
        "Your statement is now available"
    ]
    
    print("Testing FIXED keyword detection:")
    print("=" * 60)
    
    print("\n🟢 THESE SHOULD BE KEPT (NOT DELETED):")
    for subject in should_keep:
        analysis = filter_tool.extract_from_subject(subject)
        should_delete_email, reason = filter_tool.should_delete_email(analysis)
        
        print(f"\nSubject: {subject}")
        print(f"Non-deal detected: {analysis.get('is_non_deal', False)}")
        print(f"Should delete: {should_delete_email}")
        print(f"Reason: {reason}")
        
        if should_delete_email:
            print("❌ STILL BEING DELETED - NEEDS FIX")
        else:
            print("✅ CORRECTLY KEPT")
    
    print("\n🔴 THESE SHOULD STILL BE DELETED:")
    for subject in should_delete:
        analysis = filter_tool.extract_from_subject(subject)
        should_delete_email, reason = filter_tool.should_delete_email(analysis)
        
        print(f"\nSubject: {subject}")
        print(f"Non-deal detected: {analysis.get('is_non_deal', False)}")
        print(f"Should delete: {should_delete_email}")
        print(f"Reason: {reason}")
        
        if should_delete_email:
            print("✅ CORRECTLY DELETED")
        else:
            print("❌ INCORRECTLY KEPT - NEEDS FIX")

if __name__ == "__main__":
    test_problematic_emails()