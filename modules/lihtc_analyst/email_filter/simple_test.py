#!/usr/bin/env python3
"""Simple test for non-deal keyword detection"""

# Test the non-deal keyword detection
non_deal_keywords = [
    "homebuyer workshop", "workshop", "seminar", "webinar", "conference",
    "training", "educational", "news", "enews", "newsletter", "update",
    "announcement", "reminder", "statement", "invoice", "payment",
    "marketing", "advertisement", "promotion", "survey", "feedback"
]

test_subjects = [
    "CalHFA homebuyer workshop - Join us for free education",
    "19 unit Pasadena Playhouse - Investment opportunity",
    "Elmwood Avenue, LA deal - 45 units available",
    "Monthly newsletter update - Market trends",
    "Workshop on financing options for developers"
]

print("Testing non-deal keyword detection:")
print("=" * 60)

for subject in test_subjects:
    subject_lower = subject.lower()
    is_non_deal = False
    
    for keyword in non_deal_keywords:
        if keyword in subject_lower:
            is_non_deal = True
            print(f"✓ NON-DEAL: {subject}")
            print(f"  Matched keyword: '{keyword}'")
            break
    
    if not is_non_deal:
        print(f"✗ DEAL: {subject}")
    
    print("-" * 60)