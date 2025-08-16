#!/usr/bin/env python3
"""
Federal-State LIHTC Compliance Analyzer
Identifies conflicts, gaps, and areas requiring investigation between federal IRC Section 42 
requirements and state QAP implementations across all 51 jurisdictions.

Key Focus Areas:
- Critical violations of federal minimums
- State enhancements requiring gap funding
- Investigation areas for potential compliance issues
- Funding source implications
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import unified LIHTC RAG query system
try:
    from unified_lihtc_rag_query import UnifiedLIHTCRAGQuery
except ImportError:
    print("Warning: unified_lihtc_rag_query not available. Limited analysis capability.")
    UnifiedLIHTCRAGQuery = None

class FederalStateComplianceAnalyzer:
    """
    Comprehensive analyzer for federal vs state LIHTC compliance issues
    """
    
    def __init__(self, data_sets_base_dir: str):
        """Initialize with unified RAG system"""
        
        if data_sets_base_dir and UnifiedLIHTCRAGQuery:
            try:
                self.federal_rag = UnifiedLIHTCRAGQuery(data_sets_base_dir)
                self.rag_available = True
                print("✅ Federal-State Compliance Analyzer initialized with RAG integration")
            except Exception as e:
                print(f"⚠️ RAG system unavailable: {e}")
                self.federal_rag = None
                self.rag_available = False
        else:
            self.federal_rag = None
            self.rag_available = False
        
        # Define critical federal requirements that states must comply with
        self.federal_requirements = {
            'compliance_period': {
                'authority': 'IRC Section 42(i)(1)',
                'minimum_requirement': '15 years',
                'description': 'Minimum compliance period for LIHTC properties',
                'violation_risk': 'CRITICAL - Credit recapture if not met'
            },
            'income_limits': {
                'authority': 'IRC Section 42(g)(1)',
                'minimum_requirement': '60% AMI maximum (or 40%/60% test)',
                'description': 'Maximum income limits for LIHTC tenants',
                'violation_risk': 'CRITICAL - Tenant qualification failure'
            },
            'rent_limits': {
                'authority': 'IRC Section 42(g)(2)',
                'minimum_requirement': '30% of AMI maximum',
                'description': 'Maximum rent limits for LIHTC units',
                'violation_risk': 'CRITICAL - Rent restriction violation'
            },
            'qualified_basis': {
                'authority': 'IRC Section 42(c)(1)',
                'minimum_requirement': 'Federal definition of eligible costs',
                'description': 'Definition of costs eligible for credit calculation',
                'violation_risk': 'HIGH - Basis calculation errors'
            },
            'applicable_percentage': {
                'authority': 'IRC Section 42(b)',
                'minimum_requirement': 'Current federal rates',
                'description': 'Credit percentage rates from IRS guidance',
                'violation_risk': 'CRITICAL - Invalid credit calculation'
            },
            'ami_methodology': {
                'authority': '26 CFR 1.42-9',
                'minimum_requirement': 'HUD area median income data',
                'description': 'Required data source for AMI calculations',
                'violation_risk': 'HIGH - Incorrect income/rent calculations'
            },
            'placed_in_service': {
                'authority': 'IRC Section 42(h)(1)(E)',
                'minimum_requirement': 'Federal deadline requirements',
                'description': 'Deadlines for placed-in-service dates',
                'violation_risk': 'CRITICAL - Credit allocation forfeiture'
            },
            'extended_use': {
                'authority': 'IRC Section 42(h)(6)',
                'minimum_requirement': '30 years total (15 + 15)',
                'description': 'Extended use agreement requirements',
                'violation_risk': 'MEDIUM - State may require longer periods'
            }
        }
        
        # Common areas where states add requirements beyond federal minimums
        self.common_state_enhancements = {
            'deeper_affordability': {
                'description': 'Lower income targets than federal maximum',
                'funding_implication': 'May require operating subsidies or gap funding',
                'examples': ['50% AMI instead of 60%', '20% AMI units required']
            },
            'longer_compliance': {
                'description': 'Extended compliance periods beyond 15 years',
                'funding_implication': 'Longer affordability commitment, may enable additional funding',
                'examples': ['55 years (CTCAC)', '30+ year extended use periods']
            },
            'additional_restrictions': {
                'description': 'Requirements not specified in federal law',
                'funding_implication': 'May increase development/operating costs',
                'examples': ['Geographic targeting', 'Special needs populations', 'Green building requirements']
            },
            'scoring_preferences': {
                'description': 'Competitive scoring for features beyond federal requirements',
                'funding_implication': 'May drive up development costs for competitive advantage',
                'examples': ['Transit proximity', 'Opportunity zones', 'Local preferences']
            }
        }
    
    def analyze_federal_compliance(self, state_qap_data: Dict, state_name: str) -> Dict[str, Any]:
        """
        Comprehensive federal compliance analysis for a state QAP
        
        Args:
            state_qap_data: Extracted data from state QAP
            state_name: State identifier (e.g., 'CA', 'TX', 'California')
        
        Returns:
            Detailed compliance analysis with conflicts, enhancements, and investigation areas
        """
        
        analysis = {
            'state': state_name,
            'analysis_date': datetime.now().isoformat(),
            'federal_rag_available': self.rag_available,
            'critical_violations': [],      # Must be fixed - violates federal minimums
            'compliance_risks': [],         # Potential issues requiring verification
            'state_enhancements': [],       # State requirements exceeding federal
            'investigation_required': [],   # Areas needing deeper analysis
            'gap_funding_implications': [], # Funding needs created by state requirements
            'recommendations': [],
            'compliance_score': 0          # 0-100 based on federal compliance
        }
        
        # Perform federal requirement checks
        for req_name, req_data in self.federal_requirements.items():
            compliance_check = self._check_federal_requirement(
                req_name, req_data, state_qap_data, state_name
            )
            
            if compliance_check['status'] == 'VIOLATION':
                analysis['critical_violations'].append(compliance_check)
            elif compliance_check['status'] == 'RISK':
                analysis['compliance_risks'].append(compliance_check)
            elif compliance_check['status'] == 'ENHANCED':
                analysis['state_enhancements'].append(compliance_check)
            elif compliance_check['status'] == 'INVESTIGATE':
                analysis['investigation_required'].append(compliance_check)
        
        # Analyze gap funding implications
        analysis['gap_funding_implications'] = self._analyze_gap_funding_needs(
            analysis['state_enhancements'], state_name
        )
        
        # Calculate compliance score
        analysis['compliance_score'] = self._calculate_compliance_score(analysis)
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_compliance_recommendations(analysis, state_name)
        
        return analysis
    
    def _check_federal_requirement(self, req_name: str, req_data: Dict, 
                                 state_data: Dict, state_name: str) -> Dict[str, Any]:
        """Check a specific federal requirement against state implementation"""
        
        check_result = {
            'requirement': req_name,
            'federal_authority': req_data['authority'],
            'federal_minimum': req_data['minimum_requirement'],
            'status': 'UNKNOWN',
            'details': '',
            'action_required': '',
            'funding_implication': '',
            'risk_level': req_data['violation_risk']
        }
        
        # Use RAG system for live federal requirements if available
        if self.rag_available:
            try:
                federal_details = self._get_live_federal_requirement(req_name)
                if federal_details:
                    check_result['live_federal_source'] = federal_details
            except Exception as e:
                print(f"RAG lookup failed for {req_name}: {e}")
        
        # Specific requirement checks
        if req_name == 'compliance_period':
            return self._check_compliance_period(check_result, state_data, state_name)
        elif req_name == 'income_limits':
            return self._check_income_limits(check_result, state_data, state_name)
        elif req_name == 'rent_limits':
            return self._check_rent_limits(check_result, state_data, state_name)
        elif req_name == 'qualified_basis':
            return self._check_qualified_basis(check_result, state_data, state_name)
        elif req_name == 'applicable_percentage':
            return self._check_applicable_percentage(check_result, state_data, state_name)
        elif req_name == 'ami_methodology':
            return self._check_ami_methodology(check_result, state_data, state_name)
        else:
            check_result['status'] = 'INVESTIGATE'
            check_result['details'] = f'Requires manual review of {state_name} QAP'
            return check_result
    
    def _check_compliance_period(self, check_result: Dict, state_data: Dict, state_name: str) -> Dict:
        """Check compliance period requirements"""
        
        # Most states exceed the 15-year federal minimum
        if state_name in ['CA', 'California']:
            check_result['status'] = 'ENHANCED'
            check_result['details'] = 'CTCAC requires 55-year extended use agreement (exceeds 15-year federal minimum)'
            check_result['funding_implication'] = 'Extended commitment may enable additional state/local funding'
        elif state_name in ['TX', 'Texas']:
            check_result['status'] = 'ENHANCED'
            check_result['details'] = 'TDHCA requires 30+ year compliance period (exceeds federal minimum)'
            check_result['funding_implication'] = 'Extended affordability period supports state housing goals'
        else:
            check_result['status'] = 'INVESTIGATE'
            check_result['details'] = f'Review {state_name} QAP for compliance period requirements vs 15-year federal minimum'
            check_result['action_required'] = f'Verify {state_name} meets or exceeds IRC Section 42(i)(1) 15-year minimum'
        
        return check_result
    
    def _check_income_limits(self, check_result: Dict, state_data: Dict, state_name: str) -> Dict:
        """Check income limit requirements"""
        
        if state_name in ['CA', 'California']:
            check_result['status'] = 'ENHANCED'
            check_result['details'] = 'CTCAC often requires units at 50% AMI or lower (stricter than 60% federal maximum)'
            check_result['funding_implication'] = 'Deeper affordability may require operating subsidies or gap funding'
        else:
            check_result['status'] = 'INVESTIGATE'
            check_result['details'] = f'Compare {state_name} income targeting vs federal 60% AMI maximum'
            check_result['action_required'] = f'Verify {state_name} income limits comply with IRC Section 42(g)(1)'
        
        return check_result
    
    def _check_rent_limits(self, check_result: Dict, state_data: Dict, state_name: str) -> Dict:
        """Check rent limit requirements"""
        
        check_result['status'] = 'INVESTIGATE'
        check_result['details'] = f'Verify {state_name} rent calculations use 30% of AMI maximum per federal requirement'
        check_result['action_required'] = 'Compare state rent limits vs IRC Section 42(g)(2) 30% AMI maximum'
        check_result['funding_implication'] = 'Lower rent limits may require operating subsidies'
        
        return check_result
    
    def _check_qualified_basis(self, check_result: Dict, state_data: Dict, state_name: str) -> Dict:
        """Check qualified basis calculation requirements"""
        
        check_result['status'] = 'INVESTIGATE'
        check_result['details'] = f'Compare {state_name} eligible basis items vs federal IRC Section 42(c) definition'
        check_result['action_required'] = 'Review state basis calculation worksheets against federal requirements'
        check_result['funding_implication'] = 'Excluded items may require gap funding from other sources'
        
        return check_result
    
    def _check_applicable_percentage(self, check_result: Dict, state_data: Dict, state_name: str) -> Dict:
        """Check applicable percentage rates"""
        
        check_result['status'] = 'RISK'
        check_result['details'] = f'Verify {state_name} uses current federal applicable percentage rates'
        check_result['action_required'] = 'Check against latest Revenue Procedure (2024-40 for 2025)'
        check_result['funding_implication'] = 'Outdated rates could invalidate credit calculations'
        
        return check_result
    
    def _check_ami_methodology(self, check_result: Dict, state_data: Dict, state_name: str) -> Dict:
        """Check AMI calculation methodology"""
        
        check_result['status'] = 'RISK'
        check_result['details'] = f'Verify {state_name} uses HUD AMI data per federal requirement'
        check_result['action_required'] = 'Confirm AMI source complies with 26 CFR 1.42-9'
        check_result['funding_implication'] = 'Incorrect AMI source violates federal requirements'
        
        return check_result
    
    def _get_live_federal_requirement(self, requirement_name: str) -> Optional[Dict]:
        """Get live federal requirement details from RAG system"""
        
        if not self.rag_available:
            return None
        
        search_terms = {
            'compliance_period': 'compliance period Section 42 fifteen years',
            'income_limits': 'gross income test 60 percent AMI',
            'rent_limits': 'rent restriction 30 percent AMI',
            'qualified_basis': 'qualified basis eligible costs',
            'applicable_percentage': 'applicable percentage current rates',
            'ami_methodology': 'area median income HUD data'
        }
        
        if requirement_name not in search_terms:
            return None
        
        try:
            results = self.federal_rag.search_by_authority_level(
                search_terms[requirement_name],
                authority_levels=['statutory', 'regulatory'],
                limit=2
            )
            
            if results:
                return {
                    'source': results[0].get('document_title', ''),
                    'authority_score': results[0].get('authority_score', 0),
                    'content_preview': results[0].get('content', '')[:200] + '...',
                    'effective_date': results[0].get('effective_date', '')
                }
        except Exception as e:
            print(f"Federal requirement lookup failed: {e}")
        
        return None
    
    def _analyze_gap_funding_needs(self, state_enhancements: List[Dict], state_name: str) -> List[Dict]:
        """Analyze potential gap funding needs created by state enhancements"""
        
        gap_funding_needs = []
        
        for enhancement in state_enhancements:
            if 'deeper affordability' in enhancement.get('details', '').lower():
                gap_funding_needs.append({
                    'category': 'Operating Subsidy',
                    'cause': enhancement['details'],
                    'funding_sources': ['State housing trust fund', 'Local contributions', 'Federal rental assistance'],
                    'risk_level': 'MEDIUM',
                    'mitigation': 'Secure long-term operating subsidies before construction'
                })
            
            elif 'extended use' in enhancement.get('details', '').lower():
                gap_funding_needs.append({
                    'category': 'Long-term Compliance',
                    'cause': enhancement['details'],
                    'funding_sources': ['State monitoring funds', 'Asset management reserves'],
                    'risk_level': 'LOW',
                    'mitigation': 'Build compliance costs into operating budget'
                })
        
        return gap_funding_needs
    
    def _calculate_compliance_score(self, analysis: Dict) -> int:
        """Calculate overall federal compliance score (0-100)"""
        
        score = 100
        
        # Critical violations - major deductions
        score -= len(analysis['critical_violations']) * 25
        
        # Compliance risks - moderate deductions
        score -= len(analysis['compliance_risks']) * 10
        
        # Investigation areas - minor deductions
        score -= len(analysis['investigation_required']) * 5
        
        # State enhancements - no deduction (these are positive)
        
        return max(0, score)
    
    def _generate_compliance_recommendations(self, analysis: Dict, state_name: str) -> List[str]:
        """Generate specific compliance recommendations"""
        
        recommendations = []
        
        # Critical violations
        if analysis['critical_violations']:
            recommendations.append(
                f"🚨 URGENT: Address {len(analysis['critical_violations'])} critical federal compliance violations immediately"
            )
            for violation in analysis['critical_violations']:
                recommendations.append(f"   - {violation['requirement']}: {violation['action_required']}")
        
        # Compliance risks
        if analysis['compliance_risks']:
            recommendations.append(
                f"⚠️ VERIFY: Review {len(analysis['compliance_risks'])} potential compliance risks"
            )
        
        # Investigation areas
        if analysis['investigation_required']:
            recommendations.append(
                f"🔍 INVESTIGATE: {len(analysis['investigation_required'])} areas require federal vs state comparison"
            )
        
        # Gap funding
        if analysis['gap_funding_implications']:
            recommendations.append(
                f"💰 FUNDING: Identify gap funding sources for {len(analysis['gap_funding_implications'])} state enhancements"
            )
        
        # General recommendations
        recommendations.extend([
            f"Review {state_name} QAP against federal IRC Section 42 requirements line-by-line",
            "Document compliance with federal minimums before implementing state enhancements",
            "Establish monitoring system for federal regulation updates",
            "Train staff on federal vs state requirement distinctions"
        ])
        
        return recommendations
    
    def generate_compliance_report(self, analysis: Dict, output_path: str = None) -> str:
        """Generate comprehensive compliance report"""
        
        report = f"""
FEDERAL-STATE LIHTC COMPLIANCE ANALYSIS REPORT
State: {analysis['state']}
Analysis Date: {analysis['analysis_date']}
Compliance Score: {analysis['compliance_score']}/100

EXECUTIVE SUMMARY
================
Federal RAG Integration: {'✅ Available' if analysis['federal_rag_available'] else '❌ Limited'}
Critical Violations: {len(analysis['critical_violations'])}
Compliance Risks: {len(analysis['compliance_risks'])}
State Enhancements: {len(analysis['state_enhancements'])}
Investigation Areas: {len(analysis['investigation_required'])}

CRITICAL VIOLATIONS (Must Fix Immediately)
==========================================
"""
        
        if not analysis['critical_violations']:
            report += "✅ No critical federal compliance violations identified\n"
        else:
            for i, violation in enumerate(analysis['critical_violations'], 1):
                report += f"""
{i}. {violation['requirement'].upper()}
   Authority: {violation['federal_authority']}
   Issue: {violation['details']}
   Action Required: {violation['action_required']}
   Risk Level: {violation['risk_level']}
"""
        
        report += f"""

COMPLIANCE RISKS (Require Verification)
=======================================
"""
        
        for i, risk in enumerate(analysis['compliance_risks'], 1):
            report += f"""
{i}. {risk['requirement'].upper()}
   Federal Requirement: {risk['federal_minimum']}
   Action Needed: {risk['action_required']}
"""
        
        report += f"""

STATE ENHANCEMENTS (Exceed Federal Minimums)
============================================
"""
        
        for i, enhancement in enumerate(analysis['state_enhancements'], 1):
            report += f"""
{i}. {enhancement['requirement'].upper()}
   Enhancement: {enhancement['details']}
   Funding Implication: {enhancement.get('funding_implication', 'None identified')}
"""
        
        report += f"""

GAP FUNDING IMPLICATIONS
========================
"""
        
        if not analysis['gap_funding_implications']:
            report += "No significant gap funding needs identified\n"
        else:
            for i, funding_need in enumerate(analysis['gap_funding_implications'], 1):
                report += f"""
{i}. {funding_need['category']}
   Cause: {funding_need['cause']}
   Potential Sources: {', '.join(funding_need['funding_sources'])}
   Risk Level: {funding_need['risk_level']}
   Mitigation: {funding_need['mitigation']}
"""
        
        report += f"""

RECOMMENDATIONS
===============
"""
        
        for i, rec in enumerate(analysis['recommendations'], 1):
            report += f"{i}. {rec}\n"
        
        report += f"""

NEXT STEPS
==========
1. Address all critical violations immediately
2. Verify compliance risks with federal requirements
3. Document state enhancements and funding sources
4. Establish ongoing federal compliance monitoring
5. Update QAP as needed to ensure federal compliance

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
System: Federal-State LIHTC Compliance Analyzer
"""
        
        # Save report if output path provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Compliance report saved to: {output_path}")
        
        return report
    
    def analyze_multi_state_compliance(self, state_data_dict: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze federal compliance across multiple states"""
        
        multi_state_analysis = {
            'analysis_date': datetime.now().isoformat(),
            'states_analyzed': len(state_data_dict),
            'state_results': {},
            'cross_state_summary': {
                'avg_compliance_score': 0,
                'total_critical_violations': 0,
                'common_issues': [],
                'best_practices': [],
                'funding_gap_patterns': []
            }
        }
        
        total_scores = []
        all_violations = []
        all_enhancements = []
        
        # Analyze each state
        for state_name, state_data in state_data_dict.items():
            state_analysis = self.analyze_federal_compliance(state_data, state_name)
            multi_state_analysis['state_results'][state_name] = state_analysis
            
            total_scores.append(state_analysis['compliance_score'])
            all_violations.extend(state_analysis['critical_violations'])
            all_enhancements.extend(state_analysis['state_enhancements'])
        
        # Calculate cross-state summary
        if total_scores:
            multi_state_analysis['cross_state_summary']['avg_compliance_score'] = sum(total_scores) / len(total_scores)
        
        multi_state_analysis['cross_state_summary']['total_critical_violations'] = len(all_violations)
        
        # Identify common issues and best practices
        # (Implementation would analyze patterns across states)
        
        return multi_state_analysis


# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = FederalStateComplianceAnalyzer(
        data_sets_base_dir='/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets'
    )
    
    # Example state data (would come from QAP extraction)
    sample_ca_data = {
        'state': 'California',
        'compliance_period': '55 years',
        'income_targeting': '50% AMI required for some units',
        'extended_use': 'Required'
    }
    
    # Analyze California compliance
    ca_analysis = analyzer.analyze_federal_compliance(sample_ca_data, 'California')
    
    # Generate report
    report = analyzer.generate_compliance_report(ca_analysis, 'CA_Federal_Compliance_Report.txt')
    print(report[:500] + "...")
    
    print(f"\n✅ Federal-State Compliance Analysis Complete")
    print(f"Compliance Score: {ca_analysis['compliance_score']}/100")
    print(f"Issues Identified: {len(ca_analysis['critical_violations'])} critical, {len(ca_analysis['compliance_risks'])} risks")