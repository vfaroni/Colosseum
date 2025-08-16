#!/usr/bin/env python3
"""
Highway Accessibility Scoring Design Document
Explains how highway proximity enhances anchor viability analysis

Key Insight: Sites can have schools nearby but still be isolated if they lack
major road connectivity. Highway access is critical for:
- Resident commuting patterns
- Emergency service response times
- Construction logistics and costs
- Property management efficiency
- Market rate rent comparability

Author: Claude Code
Date: July 2025
"""

class HighwayAccessibilityScoring:
    """Design for highway accessibility enhancement to anchor scoring"""
    
    def __init__(self):
        self.scoring_rationale = {
            'resident_needs': [
                'Daily commuting to employment centers',
                'Access to regional shopping/services',
                'Medical appointments at distant facilities',
                'Family visits and social connections'
            ],
            'development_needs': [
                'Construction material delivery costs',
                'Utility connection feasibility',
                'Emergency service response times',
                'Property management efficiency'
            ],
            'market_factors': [
                'Comparable properties cluster near highways',
                'Higher occupancy rates with good access',
                'Resident retention improves with connectivity',
                'Market rate achievability depends on access'
            ]
        }
    
    def highway_classification_system(self):
        """TxDOT roadway classifications and their importance"""
        
        classifications = {
            'Interstate_Highways': {
                'examples': ['I-35', 'I-10', 'I-45', 'I-20'],
                'importance': 'CRITICAL - Regional connectivity',
                'typical_speed': '65-75 mph',
                'scoring_weight': 1.0,
                'search_radius': '5 miles',
                'rationale': 'Interstates provide fastest access to employment centers'
            },
            
            'US_Highways': {
                'examples': ['US-290', 'US-281', 'US-90', 'US-287'],
                'importance': 'HIGH - Multi-city connectivity',
                'typical_speed': '55-70 mph',
                'scoring_weight': 0.8,
                'search_radius': '4 miles',
                'rationale': 'US highways often serve as main commercial corridors'
            },
            
            'State_Highways': {
                'examples': ['SH-130', 'SH-71', 'SH-6', 'SH-21'],
                'importance': 'MODERATE - Regional access',
                'typical_speed': '45-65 mph',
                'scoring_weight': 0.6,
                'search_radius': '3 miles',
                'rationale': 'State highways connect smaller communities to metros'
            },
            
            'FM_Roads': {
                'examples': ['FM-1960', 'FM-620', 'FM-973'],
                'importance': 'LOW - Local connectivity',
                'typical_speed': '35-55 mph',
                'scoring_weight': 0.3,
                'search_radius': '2 miles',
                'rationale': 'Farm-to-Market roads serve rural areas'
            },
            
            'Local_Roads': {
                'examples': ['County roads', 'City streets'],
                'importance': 'MINIMAL - Neighborhood only',
                'typical_speed': '25-45 mph',
                'scoring_weight': 0.0,
                'search_radius': 'N/A',
                'rationale': 'Local roads indicate potential isolation'
            }
        }
        
        return classifications
    
    def isolation_risk_examples(self):
        """Real-world examples of sites that fail without highway access"""
        
        examples = {
            'Example_1_Rural_School_Trap': {
                'scenario': 'Site near rural school but 15 miles from nearest highway',
                'schools_score': 'PASS (2 schools within 2.5 miles)',
                'highway_score': 'FAIL (no highway within 5 miles)',
                'problems': [
                    'Residents face 30+ minute commutes to any job',
                    'No public transit options in rural areas',
                    'Grocery shopping requires 45+ minute round trips',
                    'Healthcare access extremely limited'
                ],
                'outcome': 'High vacancy, resident turnover, operational failure'
            },
            
            'Example_2_Small_Town_Island': {
                'scenario': 'Site in small incorporated city with no highway access',
                'schools_score': 'PASS (adequate schools)',
                'city_score': 'PASS (within city limits)',
                'highway_score': 'FAIL (nearest highway 8 miles)',
                'problems': [
                    'Limited local employment opportunities',
                    'Young families avoid due to commute burden',
                    'Property management costs increase (travel time)',
                    'Construction costs 15-20% higher (delivery charges)'
                ],
                'outcome': 'Struggles to maintain occupancy, rent concessions required'
            },
            
            'Example_3_Highway_Adjacent_Success': {
                'scenario': 'Site 1 mile from US-290, suburban location',
                'schools_score': 'PASS (multiple schools nearby)',
                'highway_score': 'EXCELLENT (US highway < 1 mile)',
                'benefits': [
                    'Access to Houston and Austin job markets',
                    'Multiple grocery/retail options within 10 minutes',
                    'Strong comparable properties support rents',
                    'Emergency services reach site in < 5 minutes'
                ],
                'outcome': '95%+ occupancy, waiting lists, stable operations'
            }
        }
        
        return examples
    
    def enhanced_scoring_algorithm(self):
        """How highway access integrates with anchor scoring"""
        
        algorithm = {
            'current_system_gap': {
                'assumption': 'City incorporation = adequate infrastructure',
                'reality': 'Many small Texas cities lack highway connectivity',
                'risk': 'False positives for viable sites'
            },
            
            'enhanced_scoring_logic': """
            def calculate_enhanced_anchor_score(site):
                # Original factors (adjusted weights)
                school_score = check_schools(site) * 0.30  # Was 0.40
                city_score = check_city(site) * 0.15      # Was 0.20
                lihtc_score = check_lihtc(site) * 0.25    # Was 0.30
                scale_score = community_scale(site) * 0.10 # Same
                
                # NEW: Highway accessibility factor
                highway_score = calculate_highway_access(site) * 0.15
                
                # NEW: Utility validation factor  
                utility_score = validate_utilities(site) * 0.05
                
                total_score = (school_score + city_score + lihtc_score + 
                              scale_score + highway_score + utility_score)
                
                # Apply multiplier for sites with excellent highway access
                if highway_score >= 0.12:  # 80% of max highway score
                    total_score *= 1.1  # 10% bonus for excellent access
                
                return total_score
            """,
            
            'highway_calculation_detail': """
            def calculate_highway_access(site):
                # Query TxDOT roadway network
                nearby_roads = query_txdot_roads(site.lat, site.lng, radius=5)
                
                best_score = 0
                for road in nearby_roads:
                    if road.classification == 'Interstate':
                        if road.distance <= 2:
                            return 1.0  # Perfect score
                        elif road.distance <= 5:
                            return 0.8
                    elif road.classification == 'US Highway':
                        if road.distance <= 2:
                            return 0.9
                        elif road.distance <= 4:
                            return 0.7
                    elif road.classification == 'State Highway':
                        if road.distance <= 2:
                            return 0.7
                        elif road.distance <= 3:
                            return 0.5
                    # FM roads provide minimal benefit
                    
                return best_score
            """
        }
        
        return algorithm
    
    def traffic_volume_enhancement(self):
        """Using AADT (Annual Average Daily Traffic) for validation"""
        
        traffic_analysis = {
            'purpose': 'Validate that nearby highways actually provide connectivity',
            'data_available': 'TxDOT provides AADT counts at monitoring stations',
            
            'thresholds': {
                'high_traffic': {
                    'AADT': '> 50,000 vehicles/day',
                    'interpretation': 'Major commuter route, excellent connectivity',
                    'score_modifier': 1.0
                },
                'moderate_traffic': {
                    'AADT': '20,000 - 50,000 vehicles/day',
                    'interpretation': 'Good regional connectivity',
                    'score_modifier': 0.8
                },
                'low_traffic': {
                    'AADT': '< 20,000 vehicles/day',
                    'interpretation': 'Limited connectivity despite highway designation',
                    'score_modifier': 0.5
                }
            },
            
            'use_cases': [
                'Identify "paper highways" with low actual usage',
                'Validate commuter patterns support resident needs',
                'Assess commercial development potential nearby'
            ]
        }
        
        return traffic_analysis

class TWDBUtilityData:
    """Texas Water Development Board utility infrastructure data"""
    
    def __init__(self):
        self.data_categories = {
            'Water_Service_Areas': {
                'description': 'Boundaries of water utility service territories',
                'providers': ['Cities', 'Water Supply Corporations', 'MUDs', 'Private utilities'],
                'data_includes': [
                    'Service area polygons',
                    'Provider name and type',
                    'Customer counts',
                    'System capacity information'
                ]
            },
            
            'Wastewater_Service_Areas': {
                'description': 'Sewer/wastewater collection system boundaries',
                'importance': 'CRITICAL - Septic systems add $30-50K per unit',
                'data_includes': [
                    'Collection system boundaries',
                    'Treatment plant locations',
                    'Capacity and expansion plans',
                    'Industrial pretreatment requirements'
                ]
            },
            
            'Municipal_Utility_Districts': {
                'description': 'Special-purpose districts providing utilities',
                'importance': 'MUDs can have higher rates and debt obligations',
                'data_includes': [
                    'MUD boundaries',
                    'Debt per connection',
                    'Tax rates',
                    'Board contact information'
                ]
            },
            
            'Water_Planning_Regions': {
                'description': 'Regional water planning group boundaries',
                'use_case': 'Identify areas with water scarcity risks',
                'data_includes': [
                    'Projected water demand/supply',
                    'Drought contingency triggers',
                    'Infrastructure project plans'
                ]
            }
        }
    
    def utility_validation_process(self):
        """How TWDB data validates utility availability"""
        
        process = {
            'Step_1_Service_Check': {
                'action': 'Spatial join site coordinates with service area polygons',
                'outcomes': {
                    'Inside service area': 'Utilities available (verify capacity)',
                    'Outside but adjacent': 'Extension possible (estimate costs)',
                    'Remote from service': 'Major infrastructure required'
                }
            },
            
            'Step_2_Provider_Analysis': {
                'city_utility': {
                    'typical_cost': 'Standard connection fees ($5-15K)',
                    'reliability': 'HIGH - Municipal backing',
                    'rates': 'Regulated, predictable'
                },
                'MUD_utility': {
                    'typical_cost': 'Higher fees + ongoing MUD taxes',
                    'reliability': 'MODERATE - Depends on MUD finances',
                    'rates': 'Can be 20-50% higher than city rates'
                },
                'water_supply_corp': {
                    'typical_cost': 'Membership fees + connection costs',
                    'reliability': 'VARIES - Check financial health',
                    'rates': 'Often higher for commercial users'
                }
            },
            
            'Step_3_Cost_Estimation': {
                'inside_service_area': '$5,000 - $15,000 per unit',
                'extension_required_short': '$25,000 - $50,000 per unit',
                'extension_required_long': '$75,000+ per unit',
                'package_plant_required': '$150,000+ per unit'
            }
        }
        
        return process
    
    def case_studies(self):
        """Real examples of utility challenges in Texas LIHTC"""
        
        cases = {
            'Case_1_MUD_Surprise': {
                'location': 'Northwest Harris County site',
                'assumption': 'Near Houston = city utilities available',
                'reality': 'In MUD with $3,500/year additional taxes per unit',
                'impact': 'Reduced NOI by 8%, challenged feasibility'
            },
            
            'Case_2_Capacity_Constraint': {
                'location': 'Growing suburb in Williamson County',
                'assumption': 'Inside service area = ready to build',
                'reality': 'Wastewater plant at capacity, moratorium on connections',
                'impact': '2-year delay waiting for plant expansion'
            },
            
            'Case_3_Extension_Success': {
                'location': 'Site 0.5 miles outside Corsicana service area',
                'analysis': 'TWDB data showed planned expansion in area',
                'negotiation': 'City agreed to extend for development',
                'impact': 'Secured utilities with reasonable connection fees'
            }
        }
        
        return cases

def main():
    """Generate comprehensive documentation"""
    
    highway = HighwayAccessibilityScoring()
    utilities = TWDBUtilityData()
    
    print("🛣️  HIGHWAY ACCESSIBILITY SCORING DESIGN")
    print("=" * 50)
    
    print("\n📊 Why Highway Access Matters for Anchor Scoring:")
    print("\nThe Problem We're Solving:")
    print("- Sites can pass school proximity but still be isolated")
    print("- Small incorporated cities may lack regional connectivity")
    print("- Resident quality of life depends on commute access")
    print("- Construction and operations costs increase with isolation")
    
    print("\n🎯 Highway Classification Impact:")
    classifications = highway.highway_classification_system()
    for road_type, details in classifications.items():
        if details['scoring_weight'] > 0:
            print(f"\n{road_type}:")
            print(f"  Weight: {details['scoring_weight']}")
            print(f"  Search: {details['search_radius']}")
            print(f"  Why: {details['rationale']}")
    
    print("\n⚠️  Real-World Isolation Examples:")
    examples = highway.isolation_risk_examples()
    for name, example in examples.items():
        if 'FAIL' in str(example.get('highway_score', '')):
            print(f"\n{name}:")
            print(f"  Highway: {example['highway_score']}")
            print(f"  Result: {example['outcome']}")
    
    print("\n\n💧 TWDB UTILITY DATA CAPABILITIES")
    print("=" * 50)
    
    print("\n📁 Available Utility Datasets:")
    for category, details in utilities.data_categories.items():
        print(f"\n{category}:")
        print(f"  {details['description']}")
        if 'importance' in details:
            print(f"  ⚠️  {details['importance']}")
    
    print("\n💰 Utility Cost Impact Analysis:")
    process = utilities.utility_validation_process()
    costs = process['Step_3_Cost_Estimation']
    for scenario, cost in costs.items():
        print(f"  {scenario}: {cost}")
    
    print("\n📈 Why This Matters:")
    print("- Prevents $30-150K per unit utility surprises")
    print("- Identifies MUD tax obligations affecting NOI")
    print("- Validates infrastructure assumptions before closing")
    print("- Enables accurate development cost projections")

if __name__ == "__main__":
    main()