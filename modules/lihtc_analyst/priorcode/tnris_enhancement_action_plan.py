#!/usr/bin/env python3
"""
TNRIS Dataset Enhancement Action Plan
Implementation roadmap for expanding Texas LIHTC anchor analysis with official state datasets

Findings from TNRIS exploration:
- Transportation data available via TxDOT REST services
- Water/utility data available via TWDB
- Emergency services and healthcare NOT in TNRIS catalog
- Focus on high-impact, available datasets first

Author: Claude Code
Date: July 2025
"""

import requests
import pandas as pd
import geopandas as gpd
from pathlib import Path
import logging

class TNRISEnhancementPlan:
    """Action plan for TNRIS dataset integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define available dataset endpoints
        self.available_datasets = {
            'txdot_roadways': {
                'url': 'https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/Roadways/FeatureServer/0',
                'description': 'Complete Texas roadway network with classifications',
                'impact': 'Highway proximity, arterial access, traffic volume',
                'priority': 'HIGH'
            },
            'txdot_traffic': {
                'url': 'https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/TrafficData/FeatureServer/0',
                'description': 'Annual Average Daily Traffic (AADT) counts',
                'impact': 'Traffic volume validation, congestion assessment',
                'priority': 'MEDIUM'
            },
            'twdb_utilities': {
                'url': 'https://api.tnris.org/api/v1/collections',
                'description': 'Water/sewer service areas, MUDs, special districts',
                'impact': 'Utility service confirmation, cost estimation',
                'priority': 'HIGH'
            }
        }
        
        # Current system capabilities
        self.current_anchor_factors = {
            'schools_2_5_miles': 0.40,  # 40% weight
            'city_incorporation': 0.20,  # 20% weight  
            'lihtc_market_validation': 0.30,  # 30% weight
            'community_scale': 0.10   # 10% weight
        }
        
        # Enhanced system design
        self.enhanced_anchor_factors = {
            'schools_2_5_miles': 0.30,  # Reduced to 30%
            'city_incorporation': 0.15,  # Reduced to 15%
            'lihtc_market_validation': 0.25,  # Reduced to 25%
            'community_scale': 0.10,  # Keep at 10%
            'highway_access': 0.15,  # NEW: Major highway within 5 miles
            'utility_service': 0.05   # NEW: Confirmed water/sewer service
        }
    
    def phase_1_transportation_enhancement(self):
        """Phase 1: Implement TxDOT transportation data integration"""
        
        enhancement_plan = {
            'objective': 'Add highway accessibility and traffic validation to anchor scoring',
            'datasets_required': ['txdot_roadways', 'txdot_traffic'],
            'implementation_steps': [
                '1. Connect to TxDOT ArcGIS REST services',
                '2. Download Texas roadway network with classifications',
                '3. Filter for US/State highways and major arterials',
                '4. Calculate highway proximity for all 195 sites',
                '5. Add traffic volume data where available',
                '6. Create highway_access scoring (0-1 points)',
                '7. Update anchor scoring algorithm to 5-factor system'
            ],
            'new_scoring_criteria': {
                'highway_access': {
                    'US/Interstate within 2 miles': 1.0,
                    'State highway within 3 miles': 0.8,
                    'Major arterial within 5 miles': 0.6,
                    'Local roads only': 0.0
                }
            },
            'expected_impact': 'Identify sites with superior resident commuting access',
            'technical_complexity': 'MEDIUM - REST API integration required',
            'timeline': '1-2 weeks development + testing'
        }
        
        return enhancement_plan
    
    def phase_2_utility_validation(self):
        """Phase 2: Implement TWDB utility service validation"""
        
        validation_plan = {
            'objective': 'Confirm water/sewer service availability for unincorporated sites',
            'datasets_required': ['twdb_utilities', 'mud_boundaries', 'service_areas'],
            'implementation_steps': [
                '1. Access TWDB utility service area boundaries',
                '2. Download MUD and special district boundaries',  
                '3. Spatial join sites with service areas',
                '4. Identify sites requiring utility extensions',
                '5. Flag potential high-cost utility scenarios',
                '6. Create utility_service scoring (0-0.5 points)',
                '7. Update risk assessments for unincorporated sites'
            ],
            'new_scoring_criteria': {
                'utility_service': {
                    'Within city limits (assumed service)': 0.5,
                    'Within MUD/water district': 0.5,
                    'Extension required (<1 mile)': 0.3,
                    'Extension required (>1 mile)': 0.0
                }
            },
            'expected_impact': 'Eliminate utility surprises in development costs',
            'technical_complexity': 'MEDIUM - GIS spatial analysis required',
            'timeline': '1-2 weeks development + validation'
        }
        
        return validation_plan
    
    def phase_3_alternative_sources(self):
        """Phase 3: Explore alternative data sources for missing infrastructure"""
        
        alternative_plan = {
            'objective': 'Find healthcare and emergency services data outside TNRIS',
            'missing_datasets': ['hospitals', 'urgent_care', 'fire_stations', 'police_stations'],
            'alternative_sources': {
                'healthcare': [
                    'Texas Hospital Association registry',
                    'CMS Provider of Services database',
                    'HRSA Find a Health Center',
                    'Commercial datasets (SafeGraph, Yelp API)'
                ],
                'emergency_services': [
                    'County GIS portals (fire/police stations)',
                    'Regional planning council datasets',
                    'Municipal open data portals',
                    'Commercial datasets (SafeGraph)'
                ]
            },
            'implementation_approach': [
                '1. Survey major Texas counties for available GIS data',
                '2. Test commercial API access (SafeGraph, Yelp)',
                '3. Evaluate data quality and coverage',
                '4. Implement fallback scoring for missing data',
                '5. Document data source reliability by region'
            ],
            'expected_coverage': '60-80% of sites (concentrated in major metros)',
            'technical_complexity': 'HIGH - Multiple data sources, quality varies',
            'timeline': '3-4 weeks research + implementation'
        }
        
        return alternative_plan
    
    def implementation_roadmap(self):
        """Complete implementation roadmap with timelines and priorities"""
        
        roadmap = {
            'current_system': {
                'status': '✅ PRODUCTION READY',
                'sites_analyzed': 195,
                'success_rate': '77% viable (151 sites)',
                'scoring_factors': 3,
                'limitations': [
                    'Highway access assumed based on city incorporation',
                    'Utility service assumed for incorporated areas',
                    'No traffic volume or congestion data',
                    'Missing emergency services proximity'
                ]
            },
            
            'enhancement_phases': {
                'Phase 1 (Weeks 1-2)': {
                    'focus': 'Transportation Enhancement',
                    'datasets': 'TxDOT Roadways + Traffic',
                    'impact': 'Highway accessibility scoring',
                    'deliverable': '5-factor anchor scoring system'
                },
                'Phase 2 (Weeks 3-4)': {
                    'focus': 'Utility Validation', 
                    'datasets': 'TWDB Service Areas + MUDs',
                    'impact': 'Utility cost risk assessment',
                    'deliverable': 'Infrastructure cost validation'
                },
                'Phase 3 (Weeks 5-8)': {
                    'focus': 'Alternative Data Sources',
                    'datasets': 'County/Commercial APIs',
                    'impact': 'Healthcare/emergency services',
                    'deliverable': 'Comprehensive infrastructure analysis'
                }
            },
            
            'success_metrics': {
                'Phase 1': 'Highway proximity data for 100% of sites',
                'Phase 2': 'Utility service validation for 80%+ unincorporated sites',
                'Phase 3': 'Healthcare/emergency data for 60%+ major metro sites'
            },
            
            'final_system_capabilities': [
                '✅ Schools proximity (existing)',
                '✅ City incorporation (existing)', 
                '✅ LIHTC market validation (existing)',
                '✅ Community scale assessment (existing)',
                '🆕 Highway accessibility scoring',
                '🆕 Utility service validation',
                '🆕 Traffic volume analysis',
                '🆕 Emergency services proximity (partial)',
                '🆕 Healthcare facility proximity (partial)'
            ]
        }
        
        return roadmap
    
    def cost_benefit_analysis(self):
        """Analyze costs vs benefits of TNRIS enhancement"""
        
        analysis = {
            'development_costs': {
                'Phase 1 (Transportation)': '$3,000 - $5,000 dev time',
                'Phase 2 (Utilities)': '$3,000 - $5,000 dev time', 
                'Phase 3 (Alternative sources)': '$5,000 - $8,000 dev time',
                'Total estimated cost': '$11,000 - $18,000'
            },
            
            'ongoing_costs': {
                'TxDOT API access': '$0 (public)',
                'TWDB data access': '$0 (public)',
                'Commercial APIs': '$500-2,000/month (if used)',
                'Storage/compute': '$100-300/month'
            },
            
            'benefits': {
                'risk_reduction': [
                    'Eliminate highway access assumptions',
                    'Validate utility service availability', 
                    'Reduce infrastructure cost surprises',
                    'Improve resident satisfaction predictions'
                ],
                'competitive_advantage': [
                    'Industry-leading infrastructure analysis',
                    'Official state data integration',
                    'Professional-grade due diligence',
                    'Enhanced financing applications'
                ],
                'roi_potential': [
                    'Avoid 1-2 bad site selections: $500K+ savings',
                    'Identify superior sites: Higher NOI potential',
                    'Faster due diligence: Reduced carrying costs',
                    'Better financing terms: Lower rates/fees'
                ]
            },
            
            'recommendation': 'PROCEED with Phase 1 & 2 (high ROI, low risk)',
            'phase_3_decision': 'Evaluate after Phase 1/2 results'
        }
        
        return analysis

def main():
    """Generate comprehensive TNRIS enhancement documentation"""
    
    planner = TNRISEnhancementPlan()
    
    print("🚀 TNRIS Enhancement Action Plan")
    print("=" * 50)
    
    # Phase plans
    print("\n📋 PHASE 1: Transportation Enhancement")
    phase1 = planner.phase_1_transportation_enhancement()
    for key, value in phase1.items():
        if isinstance(value, list):
            print(f"{key}:")
            for item in value:
                print(f"  {item}")
        else:
            print(f"{key}: {value}")
    
    print("\n📋 PHASE 2: Utility Validation") 
    phase2 = planner.phase_2_utility_validation()
    print(f"Objective: {phase2['objective']}")
    print(f"Timeline: {phase2['timeline']}")
    print(f"Impact: {phase2['expected_impact']}")
    
    print("\n📋 PHASE 3: Alternative Sources")
    phase3 = planner.phase_3_alternative_sources()
    print(f"Objective: {phase3['objective']}")
    print(f"Expected Coverage: {phase3['expected_coverage']}")
    print(f"Complexity: {phase3['technical_complexity']}")
    
    # Implementation roadmap
    print("\n🗓️ IMPLEMENTATION ROADMAP")
    roadmap = planner.implementation_roadmap()
    for phase, details in roadmap['enhancement_phases'].items():
        print(f"\n{phase}:")
        print(f"  Focus: {details['focus']}")
        print(f"  Impact: {details['impact']}")
        print(f"  Deliverable: {details['deliverable']}")
    
    # Cost-benefit analysis
    print("\n💰 COST-BENEFIT ANALYSIS")
    analysis = planner.cost_benefit_analysis()
    print(f"Total Development Cost: {analysis['development_costs']['Total estimated cost']}")
    print(f"Recommendation: {analysis['recommendation']}")
    
    print("\n✅ NEXT STEPS:")
    print("1. Begin Phase 1 with TxDOT roadway data integration")
    print("2. Develop highway proximity scoring algorithm")  
    print("3. Test enhanced 5-factor anchor scoring")
    print("4. Validate results against current system")
    print("5. Document improvements and proceed to Phase 2")

if __name__ == "__main__":
    main()