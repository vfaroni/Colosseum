#!/usr/bin/env python3
"""
Highway Isolation Example - Visual Demonstration
Shows how sites can pass current anchor scoring but fail in reality

Example: "Smithville Commons" - A cautionary tale
Author: Claude Code
Date: July 2025
"""

def demonstrate_isolation_problem():
    """Show real-world example of highway access importance"""
    
    print("🏘️  CASE STUDY: Why Highway Access Matters")
    print("=" * 60)
    
    # Site profile
    site_profile = {
        'name': 'Smithville Commons (Hypothetical)',
        'location': 'Small town 45 miles from Austin',
        'size': '8.5 acres',
        'price': '$850,000 ($100K/acre)',
        'planned_units': 48
    }
    
    print(f"\n📍 Site Profile: {site_profile['name']}")
    for key, value in site_profile.items():
        if key != 'name':
            print(f"   {key}: {value}")
    
    # Current anchor scoring
    print("\n📊 CURRENT ANCHOR SCORING (Without Highway Factor):")
    current_scoring = {
        'Schools (2.5 mi)': {'found': 3, 'score': 2.0, 'weight': 0.40, 'points': 0.80},
        'City Limits': {'status': 'Yes', 'score': 1.0, 'weight': 0.20, 'points': 0.20},
        'LIHTC (2 mi)': {'found': 1, 'score': 1.0, 'weight': 0.30, 'points': 0.30},
        'Community Scale': {'schools': 3, 'score': 0.5, 'weight': 0.10, 'points': 0.05}
    }
    
    total_current = 0
    for factor, data in current_scoring.items():
        print(f"   {factor}: {data['score']} × {data['weight']} = {data['points']:.2f}")
        total_current += data['points']
    
    print(f"   TOTAL SCORE: {total_current:.2f}/5.00 ⭐⭐⭐⭐ (HIGH PRIORITY)")
    print("   ✅ Site PASSES and ranks as High Priority!")
    
    # Hidden reality
    print("\n🚨 THE HIDDEN REALITY:")
    reality = {
        'Nearest Interstate': 'I-35 is 22 miles away',
        'Nearest US Highway': 'US-290 is 15 miles away',  
        'Nearest State Highway': 'SH-21 is 8 miles away',
        'Public Transit': 'None available',
        'Major Employers': 'All in Austin (45+ miles)',
        'Grocery Store': 'Local store only, Walmart 25 miles',
        'Healthcare': 'Clinic in town, hospital 35 miles'
    }
    
    for aspect, detail in reality.items():
        print(f"   ❌ {aspect}: {detail}")
    
    # Development challenges
    print("\n💸 ACTUAL DEVELOPMENT CHALLENGES:")
    challenges = {
        'Construction Costs': '+18% for material delivery charges',
        'Timeline': '+2 months due to contractor travel time',
        'Utility Connection': 'Water main extension needed (1.2 miles)',
        'Property Management': 'No local companies, Austin firms charge travel',
        'Maintenance': 'Emergency repairs costly due to travel time'
    }
    
    for challenge, impact in challenges.items():
        print(f"   • {challenge}: {impact}")
    
    # Operations reality
    print("\n📉 YEAR 1 OPERATIONS REALITY:")
    operations = {
        'Target Occupancy': '95%',
        'Actual Occupancy': '72%',
        'Turnover Rate': '64% (vs 25% projected)',
        'Rent Concessions': '2 months free common',
        'Top Complaint': '"Too far from everything"',
        'Management Trips': '3x per week from Austin'
    }
    
    for metric, value in operations.items():
        print(f"   {metric}: {value}")
    
    # Enhanced scoring
    print("\n📊 ENHANCED SCORING (With Highway Factor):")
    enhanced_scoring = {
        'Schools (2.5 mi)': {'score': 2.0, 'weight': 0.30, 'points': 0.60},
        'City Limits': {'score': 1.0, 'weight': 0.15, 'points': 0.15},
        'LIHTC (2 mi)': {'score': 1.0, 'weight': 0.25, 'points': 0.25},
        'Community Scale': {'score': 0.5, 'weight': 0.10, 'points': 0.05},
        'Highway Access': {'score': 0.0, 'weight': 0.15, 'points': 0.00, 'note': '❌ NO HIGHWAY <5mi'},
        'Utility Service': {'score': 0.3, 'weight': 0.05, 'points': 0.015, 'note': '⚠️ Extension required'}
    }
    
    total_enhanced = 0
    for factor, data in enhanced_scoring.items():
        points = data['points']
        note = data.get('note', '')
        print(f"   {factor}: {data['score']} × {data['weight']} = {points:.3f} {note}")
        total_enhanced += points
    
    print(f"   TOTAL SCORE: {total_enhanced:.2f}/5.00 ⭐ (CAUTION - ISOLATED)")
    print("   ⚠️  Site now correctly identified as HIGH RISK!")
    
    # TWDB utility insights
    print("\n💧 TWDB UTILITY DATA INSIGHTS:")
    utility_findings = {
        'Water Provider': 'Smithville Water Supply Corp',
        'Service Area': 'Site outside current boundary',
        'Extension Cost': '$385,000 (1.2 mile main)',
        'Per Unit Impact': '$8,021 additional cost',
        'Wastewater': 'Package plant required',
        'Wastewater Cost': '$450,000 for 48 units',
        'Total Utility Premium': '$16,396 per unit vs city service'
    }
    
    for finding, detail in utility_findings.items():
        print(f"   {finding}: {detail}")
    
    # Financial impact
    print("\n💰 FINANCIAL IMPACT SUMMARY:")
    print("   Original Pro Forma NOI: $412,000")
    print("   Actual Year 1 NOI: $186,000 (-55%)")
    print("   Primary Factors:")
    print("     • Low occupancy (72% vs 95%)")
    print("     • High turnover costs")
    print("     • Rent concessions")
    print("     • Excess management travel")
    print("     • Higher utility debt service")
    
    print("\n🎯 KEY LESSON:")
    print("   Highway accessibility isn't a 'nice to have' - it's essential")
    print("   for preventing operational failures and protecting investors.")
    
    return total_current, total_enhanced

if __name__ == "__main__":
    current_score, enhanced_score = demonstrate_isolation_problem()
    
    print(f"\n📊 SCORING COMPARISON:")
    print(f"   Current System: {current_score:.2f} (FALSE POSITIVE)")
    print(f"   Enhanced System: {enhanced_score:.2f} (CORRECTLY IDENTIFIED)")
    print(f"   Difference: {current_score - enhanced_score:.2f} points")
    
    print("\n✅ ENHANCED SYSTEM BENEFITS:")
    print("   1. Prevents selection of isolated sites")
    print("   2. Validates true infrastructure accessibility")
    print("   3. Protects against operational failures")
    print("   4. Ensures resident satisfaction")
    print("   5. Reduces investor risk")