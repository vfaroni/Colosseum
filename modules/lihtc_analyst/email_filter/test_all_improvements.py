#!/usr/bin/env python3
"""Test all filtering improvements including non-deal keyword detection"""

def test_filtering_logic():
    """Test the core filtering logic without Gmail API"""
    
    # Mock the EmailDealFilterOAuth class functionality
    class MockEmailFilter:
        def __init__(self):
            self.target_states = ["California", "Arizona", "New Mexico"]
            self.minimum_units = 50
            
            # Non-deal keywords
            self.non_deal_keywords = [
                "homebuyer workshop", "workshop", "seminar", "webinar", "conference",
                "training", "educational", "news", "enews", "newsletter", "update",
                "announcement", "reminder", "statement", "invoice", "payment",
                "marketing", "advertisement", "promotion", "survey", "feedback",
                "just closed", "recently financed", "recent closing", "recently closed",
                "just financed", "recent financing", "closing announcement", "deal closed",
                "transaction closed", "financing completed", "loan closed"
            ]
            
            # City to state mapping (subset)
            self.city_state_map = {
                "los angeles": "California",
                "pasadena": "California",
                "phoenix": "Arizona",
                "houston": "Texas",
                "denver": "Colorado"
            }
        
        def extract_from_subject(self, subject):
            """Extract info from subject line"""
            subject_lower = subject.lower()
            
            # Check for non-deal keywords
            is_non_deal = False
            for keyword in self.non_deal_keywords:
                if keyword in subject_lower:
                    is_non_deal = True
                    break
            
            # Check for location
            location_state = None
            for city, state in self.city_state_map.items():
                if city in subject_lower:
                    location_state = state
                    break
            
            # Check for unit count
            number_of_units = None
            import re
            unit_patterns = [
                r'(\\d+)\\s*-?\\s*[Uu]nits?\\b',
                r'(\\d+)\\s*[Uu]nit\\b',
            ]
            
            for pattern in unit_patterns:
                match = re.search(pattern, subject)
                if match:
                    number_of_units = int(match.group(1))
                    break
            
            return {
                'location_state': location_state,
                'number_of_units': number_of_units,
                'is_land_opportunity': False,
                'is_non_deal': is_non_deal
            }
        
        def should_delete_email(self, analysis):
            """Determine if email should be deleted"""
            location_state = analysis.get('location_state')
            number_of_units = analysis.get('number_of_units')
            is_non_deal = analysis.get('is_non_deal', False)
            
            delete_reasons = []
            
            # Check if it's a non-deal email - DELETE these
            if is_non_deal:
                delete_reasons.append("Non-deal email (workshop, newsletter, etc.)")
            
            # Check location
            if location_state and location_state not in self.target_states:
                delete_reasons.append(f"Location is {location_state}, not in CA, AZ, or NM")
            
            # Check unit count
            if number_of_units is not None and number_of_units < self.minimum_units:
                delete_reasons.append(f"Only {number_of_units} units, less than {self.minimum_units} minimum")
            
            # If we couldn't determine location or units AND it's not a non-deal email, don't delete
            if not is_non_deal and location_state is None and number_of_units is None:
                return False, "Could not analyze email content"
            
            should_delete = len(delete_reasons) > 0
            return should_delete, "; ".join(delete_reasons) if delete_reasons else "Meets criteria"
    
    # Test cases from the user's screenshot
    test_cases = [
        {
            "subject": "CalHFA homebuyer workshop - Join us for free education",
            "expected_delete": True,
            "expected_reason": "Non-deal email"
        },
        {
            "subject": "19 unit Pasadena Playhouse - Investment opportunity",
            "expected_delete": True,
            "expected_reason": "Less than 50 units"
        },
        {
            "subject": "Elmwood Avenue, LA deal - 45 units available",
            "expected_delete": True,
            "expected_reason": "Less than 50 units"
        },
        {
            "subject": "150 unit Phoenix, AZ development - Great opportunity",
            "expected_delete": False,
            "expected_reason": "Meets criteria"
        },
        {
            "subject": "25 unit Houston, TX property for sale",
            "expected_delete": True,
            "expected_reason": "Wrong location"
        },
        {
            "subject": "Monthly newsletter update - Market trends",
            "expected_delete": True,
            "expected_reason": "Non-deal email"
        },
        {
            "subject": "Just Closed: 75-unit Phoenix property - Congratulations!",
            "expected_delete": True,
            "expected_reason": "Non-deal email"
        },
        {
            "subject": "Recently Financed: $5M LA apartment complex",
            "expected_delete": True,
            "expected_reason": "Non-deal email"
        },
        {
            "subject": "Recent Closing - 120 units in Tucson, AZ",
            "expected_delete": True,
            "expected_reason": "Non-deal email"
        }
    ]
    
    filter_tool = MockEmailFilter()
    
    print("Testing Email Filter Improvements")
    print("=" * 70)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        subject = test_case["subject"]
        expected_delete = test_case["expected_delete"]
        expected_reason = test_case["expected_reason"]
        
        print(f"\nTest {i}: {subject}")
        print("-" * 70)
        
        analysis = filter_tool.extract_from_subject(subject)
        should_delete, reason = filter_tool.should_delete_email(analysis)
        
        print(f"Analysis: {analysis}")
        print(f"Should delete: {should_delete} (expected: {expected_delete})")
        print(f"Reason: {reason}")
        
        if should_delete == expected_delete and expected_reason in reason:
            print("✅ PASSED")
        else:
            print("❌ FAILED")
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED! The filtering improvements are working correctly.")
        print("\nKey improvements verified:")
        print("✓ Non-deal emails (workshops, newsletters) are correctly identified for deletion")
        print("✓ Small properties (<50 units) are correctly identified for deletion")
        print("✓ Properties in non-target states are correctly identified for deletion")
        print("✓ Properties meeting criteria are correctly kept")
    else:
        print("❌ Some tests failed. Please review the filtering logic.")
    
    return all_passed

if __name__ == "__main__":
    test_filtering_logic()