#!/usr/bin/env python3
"""
Show Interactive Questions - Display all the questions the interactive generator will ask
"""

def show_questions():
    """Show all the interactive questions"""
    
    print("\n" + "="*70)
    print("🏠 BOTN INPUT CONFIGURATION QUESTIONS")
    print("="*70)
    print("The interactive BOTN generator will ask you these questions:")
    print()
    
    print("1. Housing Type (H2) - Choose from:")
    print("   a) At Risk and Non-Targeted")
    print("   b) Large Family")
    print("   c) Senior") 
    print("   d) Single Room/ Special Needs")
    print("   → This will be applied to ALL sites")
    print()
    
    print("2. Credit Pricing (I2)")
    print("   → Examples: '80 cents', '0.85', '75%'")
    print("   → Will be converted to decimal (80 cents = 0.8)")
    print()
    
    print("3. Credit Type (J2) - Choose from:")
    print("   a) 4%")
    print("   b) 9%")
    print("   → Must match template dropdown exactly")
    print()
    
    print("4. Construction Loan Term (K2)")
    print("   → Examples: '36 months', '24'")
    print("   → Will be converted to number (36)")
    print()
    
    print("5. Market Cap Rate (L2)")
    print("   → Examples: '5%', '0.05'")
    print("   → Will be converted to decimal (5% = 0.05)")
    print()
    
    print("6. Financing Interest Rate (M2)")
    print("   → Examples: '6%', '0.06'")
    print("   → Will be converted to decimal (6% = 0.06)")
    print()
    
    print("7. Elevator (N2) - Choose from:")
    print("   a) Elevator")
    print("   b) Non-Elevator")
    print("   → Must match template dropdown exactly")
    print()
    
    print("8. Purchase Price Assumption (G2)")
    print("   → For sites with missing prices")
    print("   → Examples: '$2000000', '2M', '1.5M'")
    print("   → Will use site's actual price when available")
    print()
    
    print("9. Number of Units (O2)")
    print("   → Examples: '100 units', '75'")
    print("   → Will be converted to number (100)")
    print()
    
    print("10. Average Unit Size (P2)")
    print("    → Examples: '900SF', '850'")
    print("    → Will be converted to number (900)")
    print()
    
    print("11. Hard Cost per SF (Q2)")
    print("    → Examples: '250/SF', '300'")
    print("    → Will be converted to number (250)")
    print()
    
    print("="*70)
    print("📋 SUMMARY:")
    print("These inputs will be applied to ALL sites in your portfolio.")
    print("Site-specific data (Name, Address, County, etc.) will be")
    print("automatically populated from your site data.")
    print("="*70)

if __name__ == "__main__":
    show_questions()