#!/usr/bin/env python3
"""
Federal-Enhanced Texas LIHTC Economic Viability Analyzer
Integrates federal authority citations from Federal LIHTC RAG system

Enhanced with:
- Federal QCT/DDA basis boost authority (IRC Section 42(d)(5)(B))
- Federal applicable percentage updates (Revenue Procedure 2024-40)
- Federal compliance monitoring requirements
- Federal AMI calculation methodology validation
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import unified LIHTC RAG query system
try:
    from unified_lihtc_rag_query import UnifiedLIHTCRAGQuery
except ImportError:
    print("Warning: unified_lihtc_rag_query not available. Federal citations will be limited.")
    UnifiedLIHTCRAGQuery = None

class FederalEnhancedTexasAnalyzer:
    """Texas analyzer with federal authority integration"""
    
    def __init__(self, data_sets_base_dir: str = None):
        # Construction cost modifiers by metro area
        self.metro_modifiers = {
            'Austin-Round Rock-Georgetown': 1.20,
            'Houston-The Woodlands-Sugar Land': 1.18,
            'Dallas-Plano-Irving': 1.17,
            'Fort Worth-Arlington-Grapevine': 1.15,
            'San Antonio-New Braunfels': 1.10,
            'El Paso': 1.05,
            'Corpus Christi': 1.08,
            'McAllen-Edinburg-Mission': 1.03,
            'Killeen-Temple': 1.05,
            'Beaumont-Port Arthur': 1.06,
            'Lubbock': 1.04,
            'Amarillo': 1.04,
            'Waco': 1.05,
            'Laredo': 1.03,
            'College Station-Bryan': 1.05
        }
        
        # County to metro mapping
        self.county_metro_map = {
            'Travis County': 'Austin-Round Rock-Georgetown',
            'Williamson County': 'Austin-Round Rock-Georgetown', 
            'Hays County': 'Austin-Round Rock-Georgetown',
            'Harris County': 'Houston-The Woodlands-Sugar Land',
            'Fort Bend County': 'Houston-The Woodlands-Sugar Land',
            'Montgomery County': 'Houston-The Woodlands-Sugar Land',
            'Dallas County': 'Dallas-Plano-Irving',
            'Collin County': 'Dallas-Plano-Irving',
            'Tarrant County': 'Fort Worth-Arlington-Grapevine',
            'Bexar County': 'San Antonio-New Braunfels',
            'El Paso County': 'El Paso',
            'Nueces County': 'Corpus Christi',
            'Hidalgo County': 'McAllen-Edinburg-Mission',
            'Bell County': 'Killeen-Temple',
            'Jefferson County': 'Beaumont-Port Arthur',
            'Lubbock County': 'Lubbock',
            'Potter County': 'Amarillo',
            'McLennan County': 'Waco',
            'Webb County': 'Laredo',
            'Brazos County': 'College Station-Bryan'
        }
        
        # FEMA flood zone construction cost impacts
        self.flood_modifiers = {
            'VE': 0.30, 'V': 0.30,
            'AE': 0.20, 'A': 0.20,
            'AO': 0.12, 'AH': 0.12,
            'X': 0.05,
            'AREA NOT INCLUDED': 0.0,
            'N/A': 0.0
        }
        
        # Federal RAG system integration
        if data_sets_base_dir and UnifiedLIHTCRAGQuery:
            try:
                self.federal_rag = UnifiedLIHTCRAGQuery(data_sets_base_dir)
                self.federal_available = True
                print("✅ Federal LIHTC RAG system loaded - Enhanced citations available")
            except Exception as e:
                print(f"⚠️ Federal RAG system unavailable: {e}")
                self.federal_rag = None
                self.federal_available = False
        else:
            self.federal_rag = None
            self.federal_available = False
        
        # Federal authority mappings for Texas analysis
        self.federal_authorities = {
            'qct_dda_basis_boost': {
                'authority': 'IRC Section 42(d)(5)(B)',
                'level': 'statutory',
                'description': 'Federal 130% basis boost for QCT/DDA areas',
                'current_rate': '30% additional basis'
            },
            'applicable_percentage_4p': {
                'authority': 'IRC Section 42(b)(2)(A)',
                'level': 'statutory',
                'description': 'Federal 4% credit applicable percentage'
            },
            'applicable_percentage_9p': {
                'authority': 'IRC Section 42(b)(2)(B)', 
                'level': 'statutory',
                'description': 'Federal 9% credit applicable percentage'
            },
            'ami_calculation': {
                'authority': '26 CFR 1.42-9',
                'level': 'regulatory',
                'description': 'Federal area median income methodology'
            },
            'placed_in_service_deadline': {
                'authority': 'IRC Section 42(h)(1)(E)',
                'level': 'statutory',
                'description': 'Federal placed-in-service deadline requirements'
            },
            'credit_ceiling': {
                'authority': 'Revenue Procedure 2024-40',
                'level': 'guidance',
                'description': '2025 federal credit ceiling and per capita amounts'
            }
        }
        
        # Density by location type
        self.density_map = {'urban': 30, 'suburban': 20, 'rural': 15}
        self.base_construction_cost = 150
        
    def get_federal_authority_context(self, concept: str, county: str = None) -> Dict[str, Any]:
        """Get federal authority context for Texas LIHTC analysis"""
        context = {
            'federal_authority': None,
            'authority_level': None,
            'compliance_requirements': [],
            'texas_implementation': None,
            'conflict_analysis': None
        }
        
        # Get base authority mapping
        if concept in self.federal_authorities:
            base_auth = self.federal_authorities[concept]
            context.update({
                'federal_authority': base_auth['authority'],
                'authority_level': base_auth['level'],
                'description': base_auth['description']
            })
        
        # Enhance with live federal RAG lookups
        if self.federal_available and self.federal_rag:
            try:
                search_terms = {
                    'qct_dda_basis_boost': 'qualified census tract difficult development area basis boost',
                    'applicable_percentage_4p': '4% credit applicable percentage',
                    'applicable_percentage_9p': '9% credit applicable percentage', 
                    'ami_calculation': 'area median income calculation HUD data',
                    'credit_ceiling': '2025 credit ceiling per capita Texas'
                }
                
                if concept in search_terms:
                    federal_results = self.federal_rag.search_by_authority_level(
                        search_terms[concept],
                        authority_levels=['statutory', 'regulatory', 'guidance'],
                        limit=2
                    )
                    
                    if federal_results:
                        top_result = federal_results[0]
                        context.update({
                            'live_federal_source': top_result.get('document_title', ''),
                            'authority_score': top_result.get('authority_score', 0),
                            'effective_date': top_result.get('effective_date', ''),
                            'content_preview': top_result.get('content', '')[:200] + '...'
                        })
                        
                        # Add Texas-specific implementation notes
                        if concept == 'qct_dda_basis_boost':
                            context['texas_implementation'] = 'Texas QCT/DDA areas determined by HUD. Automatic 30% basis increase.'
                            context['compliance_requirements'] = [
                                'Must be located in HUD-designated QCT or DDA',
                                'Basis boost applies to eligible basis calculation',
                                'TDHCA requires QCT/DDA verification in application'
                            ]
                        elif concept == 'credit_ceiling':
                            context['texas_implementation'] = 'Texas 2025 allocation: $25,877,830 (9% credits)'
                            context['compliance_requirements'] = [
                                'Total Texas allocation limited by federal ceiling',
                                'Per capita amount: $3.00 (2025)',
                                'Small state minimum: $3,455,000 (not applicable to Texas)'
                            ]
                
            except Exception as e:
                print(f"Federal RAG lookup failed for {concept}: {e}")
        
        return context
    
    def analyze_federal_compliance_requirements(self, property_data: Dict) -> Dict[str, Any]:
        """Analyze federal compliance requirements for Texas property"""
        compliance = {
            'qct_dda_status': None,
            'federal_basis_boost': 0,
            'applicable_percentages': {},
            'ami_compliance': {},
            'compliance_recommendations': []
        }
        
        # QCT/DDA Analysis with federal authority
        qct_dda_eligible = property_data.get('QCT_DDA_Eligible', False)
        if qct_dda_eligible:
            compliance['qct_dda_status'] = 'Eligible for federal 30% basis boost'
            compliance['federal_basis_boost'] = 0.30
            compliance['federal_authority'] = self.get_federal_authority_context('qct_dda_basis_boost')
            compliance['compliance_recommendations'].append(
                'Property qualifies for IRC Section 42(d)(5)(B) 130% basis boost'
            )
        else:
            compliance['qct_dda_status'] = 'Not eligible for federal basis boost'
            compliance['federal_basis_boost'] = 0
        
        # Current applicable percentages (from federal guidance)
        compliance['applicable_percentages'] = {
            '4_percent_rate': 4.00,  # Current federal rate
            '9_percent_rate': 9.00,  # Current federal rate
            'federal_authority_4p': self.get_federal_authority_context('applicable_percentage_4p'),
            'federal_authority_9p': self.get_federal_authority_context('applicable_percentage_9p')
        }
        
        # AMI compliance verification
        county = property_data.get('County', '').replace(' County', '') + ' County'
        if county:
            compliance['ami_compliance'] = {
                'county': county,
                'hud_data_required': True,
                'federal_methodology': self.get_federal_authority_context('ami_calculation', county),
                'texas_implementation': 'TDHCA uses HUD AMI data for rent calculations'
            }
            compliance['compliance_recommendations'].append(
                'Verify AMI calculations use current HUD data per 26 CFR 1.42-9'
            )
        
        # Federal credit ceiling implications
        compliance['credit_ceiling_analysis'] = self.get_federal_authority_context('credit_ceiling')
        compliance['compliance_recommendations'].append(
            'Texas 2025 allocation subject to federal per capita ceiling per Revenue Procedure 2024-40'
        )
        
        return compliance
    
    def calculate_enhanced_economic_score(self, property_data: Dict) -> Dict[str, Any]:
        """Calculate economic score with federal authority context"""
        
        # Standard economic calculations
        county = property_data.get('County', 'Unknown County')
        location_type = self.get_location_type(county)
        
        # Construction cost calculation
        metro = self.county_metro_map.get(county, None)
        metro_modifier = self.metro_modifiers.get(metro, 0.95) if metro else 0.95
        
        # FEMA flood impact
        flood_zone = property_data.get('FEMA_Flood_Zone', 'X')
        flood_modifier = self.flood_modifiers.get(flood_zone, 0.0)
        
        # Total construction cost per SF
        construction_cost_sf = self.base_construction_cost * metro_modifier * (1 + flood_modifier)
        
        # Revenue calculation (2BR 60% AMI)
        rent_2br = property_data.get('rent_2br_60pct', 1200)  # Default if missing
        units = self.density_map[location_type]
        annual_revenue = rent_2br * 12 * units * 0.95  # 95% occupancy
        
        # Development cost
        lot_size_acres = property_data.get('Lot Size (Acres)', 2.0)
        development_cost = lot_size_acres * 43560 * construction_cost_sf  # Convert acres to SF
        
        # Revenue/cost ratio
        revenue_cost_ratio = annual_revenue / development_cost if development_cost > 0 else 0
        
        # Economic score (0-100)
        economic_score = min(100, revenue_cost_ratio * 1000)
        
        # Add federal compliance analysis
        federal_compliance = self.analyze_federal_compliance_requirements(property_data)
        
        # Adjust score for federal basis boost
        if federal_compliance['federal_basis_boost'] > 0:
            # QCT/DDA properties get economic benefit from 30% basis boost
            basis_boost_benefit = federal_compliance['federal_basis_boost'] * 10  # Convert to score points
            economic_score += basis_boost_benefit
            economic_score = min(100, economic_score)  # Cap at 100
        
        return {
            'economic_score': round(economic_score, 1),
            'revenue_cost_ratio': round(revenue_cost_ratio, 4),
            'construction_cost_sf': round(construction_cost_sf, 0),
            'annual_revenue': round(annual_revenue, 0),
            'development_cost': round(development_cost, 0),
            'location_type': location_type,
            'metro_modifier': metro_modifier,
            'flood_modifier': flood_modifier,
            'federal_compliance': federal_compliance,
            'federal_enhancement': True
        }
    
    def get_location_type(self, county):
        """Determine location type from county"""
        if county in self.county_metro_map:
            metro = self.county_metro_map[county]
            if metro in ['Austin-Round Rock-Georgetown', 'Houston-The Woodlands-Sugar Land', 
                        'Dallas-Plano-Irving', 'Fort Worth-Arlington-Grapevine', 'San Antonio-New Braunfels']:
                return 'urban'
            else:
                return 'suburban'
        return 'rural'
    
    def analyze_portfolio_federal_compliance(self, portfolio_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze entire portfolio for federal compliance implications"""
        
        compliance_summary = {
            'total_properties': len(portfolio_data),
            'qct_dda_eligible': 0,
            'federal_basis_boost_value': 0,
            'credit_allocation_impact': {},
            'compliance_recommendations': [],
            'federal_authority_summary': {}
        }
        
        # Count QCT/DDA properties
        qct_dda_count = portfolio_data.get('QCT_DDA_Eligible', pd.Series([False] * len(portfolio_data))).sum()
        compliance_summary['qct_dda_eligible'] = int(qct_dda_count)
        
        # Calculate total basis boost value
        if qct_dda_count > 0:
            avg_development_cost = portfolio_data.get('development_cost', pd.Series([0] * len(portfolio_data))).mean()
            total_basis_boost_value = qct_dda_count * avg_development_cost * 0.30
            compliance_summary['federal_basis_boost_value'] = round(total_basis_boost_value, 0)
        
        # Federal authority summary
        if self.federal_available:
            try:
                # Get current credit ceiling information
                credit_ceiling_info = self.get_federal_authority_context('credit_ceiling')
                compliance_summary['credit_allocation_impact'] = {
                    'texas_2025_ceiling': '$25,877,830',
                    'per_capita_amount': '$3.00',
                    'federal_authority': credit_ceiling_info.get('federal_authority'),
                    'effective_date': credit_ceiling_info.get('effective_date')
                }
                
                # Get QCT/DDA authority
                qct_authority = self.get_federal_authority_context('qct_dda_basis_boost')
                compliance_summary['federal_authority_summary']['qct_dda_boost'] = {
                    'authority': qct_authority.get('federal_authority'),
                    'eligible_properties': int(qct_dda_count),
                    'total_boost_value': compliance_summary['federal_basis_boost_value']
                }
                
            except Exception as e:
                print(f"Portfolio federal analysis error: {e}")
        
        # Generate recommendations
        if qct_dda_count > 0:
            compliance_summary['compliance_recommendations'].extend([
                f'{qct_dda_count} properties eligible for federal 30% basis boost under IRC 42(d)(5)(B)',
                'Verify QCT/DDA designations with current HUD data',
                'Calculate basis boost impact on credit equity pricing'
            ])
        
        compliance_summary['compliance_recommendations'].extend([
            'Ensure AMI calculations use HUD methodology per 26 CFR 1.42-9',
            'Verify applicable percentages reflect latest Revenue Procedure guidance',
            'Monitor federal credit ceiling impact on Texas allocation capacity'
        ])
        
        return compliance_summary
    
    def load_data(self):
        """Load enhanced land data with counties"""
        print("Loading county-enhanced land analysis data with federal integration...")
        
        # Find the latest county-enhanced file
        county_files = list(Path('.').glob('CoStar_Land_Analysis_With_Counties_*.xlsx'))
        if not county_files:
            raise FileNotFoundError("County-enhanced land analysis file not found. Run add_county_to_land_data.py first.")
            
        latest_file = sorted(county_files)[-1]
        print(f"Loading from: {latest_file}")
        
        self.land_data = pd.read_excel(latest_file, sheet_name='Land_Analysis_With_Counties')
        print(f"Loaded {len(self.land_data)} properties with county data")
        print(f"Federal RAG integration: {'✅ Available' if self.federal_available else '❌ Not Available'}")
        
        # Check for AMI data columns
        has_ami = 'rent_2br_60pct' in self.land_data.columns
        print(f"Direct AMI data available: {has_ami}")
        
        return self.land_data
    
    def run_enhanced_analysis(self) -> pd.DataFrame:
        """Run complete analysis with federal authority integration"""
        
        # Load data
        data = self.load_data()
        
        print("\n" + "="*80)
        print("🏛️ FEDERAL-ENHANCED TEXAS LIHTC ECONOMIC ANALYSIS")
        print("="*80)
        
        # Calculate enhanced economic scores for each property
        enhanced_results = []
        
        for idx, row in data.iterrows():
            property_analysis = self.calculate_enhanced_economic_score(row.to_dict())
            enhanced_results.append(property_analysis)
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(enhanced_results)
        
        # Merge with original data
        enhanced_data = pd.concat([data.reset_index(drop=True), results_df], axis=1)
        
        # Portfolio-level federal compliance analysis
        portfolio_compliance = self.analyze_portfolio_federal_compliance(enhanced_data)
        
        # Generate summary
        print(f"\n📊 FEDERAL COMPLIANCE SUMMARY:")
        print(f"Properties Analyzed: {portfolio_compliance['total_properties']}")
        print(f"QCT/DDA Eligible: {portfolio_compliance['qct_dda_eligible']}")
        print(f"Federal Basis Boost Value: ${portfolio_compliance['federal_basis_boost_value']:,.0f}")
        
        if self.federal_available:
            print(f"✅ Federal RAG Integration: Active")
            print(f"🏛️ Federal Authorities Cited: {len(self.federal_authorities)}")
        else:
            print(f"⚠️ Federal RAG Integration: Limited")
        
        print(f"\n📋 COMPLIANCE RECOMMENDATIONS:")
        for rec in portfolio_compliance['compliance_recommendations'][:5]:
            print(f"  • {rec}")
        
        # Save enhanced results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"Federal_Enhanced_Texas_Analysis_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            enhanced_data.to_excel(writer, sheet_name='Federal_Enhanced_Analysis', index=False)
            
            # Add compliance summary sheet
            compliance_df = pd.DataFrame([portfolio_compliance])
            compliance_df.to_excel(writer, sheet_name='Federal_Compliance_Summary', index=False)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        return enhanced_data


# Example usage
if __name__ == "__main__":
    # Initialize with federal RAG integration
    analyzer = FederalEnhancedTexasAnalyzer(
        data_sets_base_dir='/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets'
    )
    
    # Run enhanced analysis
    results = analyzer.run_enhanced_analysis()
    print("\nFederal-Enhanced Texas LIHTC Analysis completed!")