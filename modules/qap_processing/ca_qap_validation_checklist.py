#!/usr/bin/env python3
"""
CA QAP Validation Checklist
Comprehensive validation for California 2025 QAP chunking quality

This validates that ALL critical regulatory sections are properly extracted
and chunked according to the Complex Outline strategy.

Built by Structured Consultants LLC
"""

import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CAQAPSection:
    """Critical section in CA QAP that must be extracted"""
    section_name: str
    keywords: List[str]
    min_content_length: int
    page_range_estimate: str  # For manual verification
    critical_for_lihtc: bool

class CaliforniaQAPValidator:
    """Validates CA QAP extraction completeness and quality"""
    
    def __init__(self):
        self.critical_sections = self._define_ca_qap_sections()
        self.validation_results = {}
        
    def _define_ca_qap_sections(self) -> Dict[str, CAQAPSection]:
        """Define all critical sections that must be extracted from CA QAP"""
        
        return {
            "scoring_criteria": CAQAPSection(
                section_name="Complete Scoring Criteria",
                keywords=["points", "scoring", "maximum points", "point categories", 
                         "scoring factors", "tiebreaker", "self-score"],
                min_content_length=5000,  # Should be comprehensive
                page_range_estimate="~20-40 pages typically",
                critical_for_lihtc=True
            ),
            
            "geographic_apportionments": CAQAPSection(
                section_name="Geographic Apportionments & Set-Asides",
                keywords=["geographic apportionment", "set-aside", "regional allocation",
                         "geographic region", "rural", "at-risk", "nonprofit"],
                min_content_length=3000,
                page_range_estimate="~5-10 pages",
                critical_for_lihtc=True
            ),
            
            "threshold_requirements": CAQAPSection(
                section_name="Threshold Requirements",
                keywords=["threshold", "minimum requirements", "site control",
                         "zoning", "environmental review", "financial feasibility"],
                min_content_length=4000,
                page_range_estimate="~10-15 pages",
                critical_for_lihtc=True
            ),
            
            "application_procedures": CAQAPSection(
                section_name="Application Procedures & Deadlines",
                keywords=["application", "deadline", "submission", "round",
                         "application materials", "required documentation"],
                min_content_length=2500,
                page_range_estimate="~5-8 pages",
                critical_for_lihtc=True
            ),
            
            "compliance_monitoring": CAQAPSection(
                section_name="Compliance & Monitoring",
                keywords=["compliance", "monitoring", "placed-in-service",
                         "annual reporting", "inspection", "noncompliance"],
                min_content_length=2000,
                page_range_estimate="~3-5 pages",
                critical_for_lihtc=True
            ),
            
            "construction_standards": CAQAPSection(
                section_name="Minimum Construction Standards",
                keywords=["minimum construction standards", "building requirements",
                         "accessibility", "sustainable building", "energy efficiency"],
                min_content_length=1500,
                page_range_estimate="~2-4 pages",
                critical_for_lihtc=False  # Important for QA but not critical
            ),
            
            "financial_underwriting": CAQAPSection(
                section_name="Financial Underwriting Standards",
                keywords=["underwriting", "debt service coverage", "operating expenses",
                         "replacement reserves", "developer fee", "eligible basis"],
                min_content_length=3000,
                page_range_estimate="~5-8 pages",
                critical_for_lihtc=True
            ),
            
            "tiebreaker_criteria": CAQAPSection(
                section_name="Tiebreaker Criteria",
                keywords=["tiebreaker", "tie-breaking", "first tiebreaker",
                         "second tiebreaker", "final tiebreaker"],
                min_content_length=1000,
                page_range_estimate="~1-2 pages",
                critical_for_lihtc=True
            ),
            
            "negative_points": CAQAPSection(
                section_name="Negative Points",
                keywords=["negative points", "point reduction", "penalty points",
                         "deduction", "prior performance"],
                min_content_length=800,
                page_range_estimate="~1-2 pages",
                critical_for_lihtc=True
            )
        }
    
    def validate_extraction(self, extracted_content: Dict[str, str]) -> Dict[str, Any]:
        """Validate that all critical CA QAP sections are properly extracted"""
        
        validation_report = {
            "timestamp": datetime.now().isoformat(),
            "total_sections_expected": len([s for s in self.critical_sections.values() 
                                           if s.critical_for_lihtc]),
            "sections_found": 0,
            "sections_missing": [],
            "sections_incomplete": [],
            "overall_completeness": 0.0,
            "critical_failures": [],
            "detailed_results": {}
        }
        
        # Check each critical section
        for section_id, section_def in self.critical_sections.items():
            if not section_def.critical_for_lihtc:
                continue
                
            # Find content that matches this section
            section_content = self._find_section_content(section_id, extracted_content)
            
            if not section_content:
                validation_report["sections_missing"].append(section_def.section_name)
                validation_report["critical_failures"].append(
                    f"MISSING: {section_def.section_name} - Critical LIHTC section not found"
                )
            else:
                # Validate content quality
                validation = self._validate_section_content(section_content, section_def)
                
                if validation["is_complete"]:
                    validation_report["sections_found"] += 1
                else:
                    validation_report["sections_incomplete"].append({
                        "section": section_def.section_name,
                        "issues": validation["issues"]
                    })
                
                validation_report["detailed_results"][section_id] = validation
        
        # Calculate overall completeness
        validation_report["overall_completeness"] = (
            validation_report["sections_found"] / 
            validation_report["total_sections_expected"]
        )
        
        # Determine if CA QAP extraction passes
        validation_report["extraction_passed"] = (
            validation_report["overall_completeness"] >= 0.95 and
            len(validation_report["critical_failures"]) == 0
        )
        
        return validation_report
    
    def _find_section_content(self, section_id: str, 
                             extracted_content: Dict[str, str]) -> str:
        """Find content that matches a section definition"""
        
        section_def = self.critical_sections[section_id]
        
        # Look for content chunks that contain section keywords
        matching_content = []
        
        for chunk_id, content in extracted_content.items():
            content_lower = content.lower()
            
            # Count keyword matches
            keyword_matches = sum(1 for keyword in section_def.keywords 
                                if keyword.lower() in content_lower)
            
            # If significant keyword overlap, include this chunk
            if keyword_matches >= len(section_def.keywords) * 0.3:  # 30% threshold
                matching_content.append(content)
        
        return "\n\n".join(matching_content)
    
    def _validate_section_content(self, content: str, 
                                 section_def: CAQAPSection) -> Dict[str, Any]:
        """Validate that section content meets quality standards"""
        
        content_lower = content.lower()
        
        # Check keyword coverage
        keywords_found = [kw for kw in section_def.keywords 
                         if kw.lower() in content_lower]
        keyword_coverage = len(keywords_found) / len(section_def.keywords)
        
        # Check content length
        content_adequate = len(content) >= section_def.min_content_length
        
        # Identify issues
        issues = []
        if keyword_coverage < 0.5:
            issues.append(f"Low keyword coverage: {keyword_coverage:.1%}")
        if not content_adequate:
            issues.append(f"Content too short: {len(content)} chars "
                         f"(expected {section_def.min_content_length}+)")
        
        # Check for fragmentation indicators
        fragment_indicators = ["see section", "refer to", "as described in", 
                              "detailed in section"]
        fragmentation_score = sum(1 for indicator in fragment_indicators 
                                if indicator in content_lower)
        
        if fragmentation_score > 2:
            issues.append("Content appears fragmented with multiple references")
        
        return {
            "section_name": section_def.section_name,
            "content_length": len(content),
            "keyword_coverage": keyword_coverage,
            "keywords_found": keywords_found,
            "is_complete": len(issues) == 0,
            "issues": issues,
            "content_preview": content[:500] + "..." if len(content) > 500 else content
        }
    
    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate human-readable validation report"""
        
        report = f"""
CA 2025 QAP EXTRACTION VALIDATION REPORT
========================================
Generated: {validation_results['timestamp']}

OVERALL RESULTS:
Extraction Status: {"✅ PASSED" if validation_results['extraction_passed'] else "❌ FAILED"}
Overall Completeness: {validation_results['overall_completeness']:.1%}
Critical Sections Found: {validation_results['sections_found']}/{validation_results['total_sections_expected']}

"""
        
        if validation_results['sections_missing']:
            report += "MISSING CRITICAL SECTIONS:\n"
            for section in validation_results['sections_missing']:
                report += f"  ❌ {section}\n"
            report += "\n"
        
        if validation_results['sections_incomplete']:
            report += "INCOMPLETE SECTIONS:\n"
            for incomplete in validation_results['sections_incomplete']:
                report += f"  ⚠️  {incomplete['section']}\n"
                for issue in incomplete['issues']:
                    report += f"     - {issue}\n"
            report += "\n"
        
        if validation_results['critical_failures']:
            report += "CRITICAL FAILURES:\n"
            for failure in validation_results['critical_failures']:
                report += f"  🚨 {failure}\n"
            report += "\n"
        
        report += "DETAILED SECTION ANALYSIS:\n"
        for section_id, results in validation_results['detailed_results'].items():
            status = "✅" if results['is_complete'] else "❌"
            report += f"\n{status} {results['section_name']}\n"
            report += f"   Content Length: {results['content_length']} chars\n"
            report += f"   Keyword Coverage: {results['keyword_coverage']:.1%}\n"
            if results['issues']:
                report += f"   Issues: {', '.join(results['issues'])}\n"
        
        report += """
VALIDATION CRITERIA:
- All critical LIHTC sections must be present
- Each section must meet minimum content length requirements  
- Keyword coverage must exceed 50% for section identification
- Content must not be excessively fragmented
- Overall completeness must be ≥95%

RECOMMENDATION:
"""
        
        if validation_results['extraction_passed']:
            report += "✅ CA QAP extraction meets quality standards for production use."
        else:
            report += "❌ CA QAP extraction requires improvement before production deployment."
        
        return report


def main():
    """Test the validator with sample data"""
    
    validator = CaliforniaQAPValidator()
    
    # This would be replaced with actual docling output
    sample_extraction = {
        "chunk_1": "The scoring criteria section contains maximum points...",
        "chunk_2": "Geographic apportionments for rural set-aside...",
        # etc.
    }
    
    results = validator.validate_extraction(sample_extraction)
    report = validator.generate_validation_report(results)
    
    print(report)
    
    # Save report
    with open("ca_qap_validation_report.json", "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()