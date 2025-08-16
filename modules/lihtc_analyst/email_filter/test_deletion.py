#!/usr/bin/env python3

from email_deal_filter_oauth_improved import EmailDealFilterOAuth
import sys

def test_deletion():
    """Test actual email deletion with proper error handling"""
    
    print("Testing email deletion permissions...")
    
    filter_instance = EmailDealFilterOAuth()
    service = filter_instance.authenticate_gmail()
    
    if not service:
        print("❌ Failed to authenticate")
        return False
    
    # Get folder ID
    folder_id = filter_instance.get_folder_id(service, "Deal Announcements")
    if not folder_id:
        print("❌ Could not find Deal Announcements folder")
        return False
    
    print(f"✅ Found Deal Announcements folder: {folder_id}")
    
    # Get a few emails to test with
    query = 'in:"INBOX/Deal Announcements"'
    results = service.users().messages().list(userId='me', q=query, maxResults=3).execute()
    messages = results.get('messages', [])
    
    if not messages:
        print("❌ No emails found to test with")
        return False
    
    print(f"✅ Found {len(messages)} emails to test with")
    
    # Try to get message details and test deletion on first email
    for i, message in enumerate(messages):
        try:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            print(f"Email {i+1}: {subject[:60]}...")
            
            # Test actual deletion permission
            print(f"  Testing deletion of email {i+1}...")
            
            # Try to delete this email
            try:
                service.users().messages().delete(userId='me', id=message['id']).execute()
                print(f"  ✅ Successfully deleted email {i+1}")
                break  # Only delete one for testing
            except Exception as delete_error:
                print(f"  ❌ Delete failed: {delete_error}")
                if "403" in str(delete_error):
                    print("  This is a permission error - OAuth scope might be insufficient")
                return False
                
        except Exception as e:
            print(f"  ❌ Error getting message {i+1}: {e}")
            continue
    
    return True

if __name__ == "__main__":
    success = test_deletion()
    if success:
        print("\n✅ Email deletion test completed successfully!")
        print("OAuth permissions are working correctly.")
    else:
        print("\n❌ Email deletion test failed!")
        print("OAuth permissions need to be fixed.")
        sys.exit(1)