#!/usr/bin/env python3
"""
Quality Assurance Framework for QAP RAG System
Implements D'Marco lessons learned with ≥95% completeness standards

Built by Structured Consultants LLC
Roman Engineering Standards: "Qualitas Perpetua" - Quality Endures
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import time
from datetime import datetime
from abc import ABC, abstractmethod

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QualityStatus(Enum):
    """Quality validation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_EXPERT_REVIEW = "needs_expert_review"

class ContentCategory(Enum):
    """Critical content categories from D'Marco lessons"""
    CONSTRUCTION_STANDARDS = "construction_standards"
    MINIMUM_CONSTRUCTION_REQUIREMENTS = "minimum_construction_requirements"
    SCORING_CRITERIA = "scoring_criteria"
    APPLICATION_PROCEDURES = "application_procedures"
    COMPLIANCE_MONITORING = "compliance_monitoring"
    FINANCIAL_REQUIREMENTS = "financial_requirements"
    GEOGRAPHIC_PREFERENCES = "geographic_preferences"
    SPECIAL_POPULATIONS = "special_populations"
    DEADLINES_PROCEDURES = "deadlines_procedures"
    CONTACT_INFORMATION = "contact_information"

@dataclass
class QualityMetrics:
    """Quality metrics for content assessment"""
    jurisdiction: str
    total_sections_expected: int
    sections_found: int
    completeness_score: float
    content_quality_score: float
    expert_validation_score: Optional[float] = None
    critical_sections_missing: List[str] = field(default_factory=list)
    fragmentation_issues: List[str] = field(default_factory=list)
    validation_timestamp: Optional[datetime] = None

@dataclass
class ValidationCriteria:
    """Validation criteria for quality assessment"""
    category: ContentCategory
    required_keywords: List[str]
    minimum_content_length: int
    expected_section_count: int
    critical_importance: bool
    expert_validation_required: bool

class ContentValidator(ABC):
    """Abstract base class for content validators"""
    
    @abstractmethod
    def validate_content(self, content: str, criteria: ValidationCriteria) -> Dict[str, Any]:
        pass

class ConstructionStandardsValidator(ContentValidator):
    """Specialized validator for construction standards content"""
    
    def __init__(self):
        self.required_keywords = [
            "minimum construction", "construction standards", "building code",
            "accessibility requirements", "ADA compliance", "fair housing",
            "construction costs", "hard costs", "green building", "energy efficiency"
        ]
    
    def validate_content(self, content: str, criteria: ValidationCriteria) -> Dict[str, Any]:
        """Validate construction standards content completeness"""
        
        content_lower = content.lower()
        
        # Check for required keywords
        keywords_found = []
        for keyword in self.required_keywords:
            if keyword.lower() in content_lower:
                keywords_found.append(keyword)
        
        keyword_coverage = len(keywords_found) / len(self.required_keywords)
        
        # Check content length (should be substantial for construction standards)
        length_adequate = len(content) >= criteria.minimum_content_length
        
        # Look for section structure indicators
        section_indicators = [
            "section", "subsection", "paragraph", "clause",
            "requirements", "standards", "specifications"
        ]
        
        structure_score = sum(1 for indicator in section_indicators 
                             if indicator in content_lower) / len(section_indicators)
        
        # Calculate overall score
        overall_score = (keyword_coverage * 0.4 + 
                        (1.0 if length_adequate else 0.0) * 0.3 + 
                        structure_score * 0.3)
        
        return {
            "category": criteria.category.value,
            "score": overall_score,
            "keyword_coverage": keyword_coverage,
            "keywords_found": keywords_found,
            "content_length": len(content),
            "length_adequate": length_adequate,
            "structure_score": structure_score,
            "validation_passed": overall_score >= 0.95,  # ≥95% requirement
            "issues": self._identify_issues(content, overall_score)
        }
    
    def _identify_issues(self, content: str, score: float) -> List[str]:
        """Identify specific content issues"""
        issues = []
        
        if score < 0.95:
            if len(content) < 1000:  # Minimum expected for construction standards
                issues.append("Content too brief for comprehensive construction standards")
            
            critical_terms = ["minimum construction standards", "building code requirements"]
            missing_critical = [term for term in critical_terms 
                               if term.lower() not in content.lower()]
            if missing_critical:
                issues.append(f"Missing critical terms: {', '.join(missing_critical)}")
                
            if "over a page long" not in content.lower() and len(content) < 2000:
                issues.append("Construction standards section appears incomplete (expected comprehensive section)")
        
        return issues

class QualityAssuranceFramework:
    """Comprehensive quality assurance framework for QAP RAG system"""
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent.parent
        self.output_path = self.base_path / "modules" / "qap_processing" / "quality_output"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Quality standards from D'Marco lessons
        self.completeness_threshold = 0.95  # ≥95% requirement
        self.expert_validation_threshold = 0.90  # ≥90% expert agreement
        
        # Initialize validators
        self.validators = {
            ContentCategory.CONSTRUCTION_STANDARDS: ConstructionStandardsValidator(),
            # Add more specialized validators as needed
        }
        
        # Initialize validation criteria
        self.validation_criteria = self._initialize_validation_criteria()
        
        # Quality tracking
        self.quality_metrics: Dict[str, QualityMetrics] = {}
        
    def _initialize_validation_criteria(self) -> Dict[ContentCategory, ValidationCriteria]:
        """Initialize validation criteria for each content category"""
        
        return {
            ContentCategory.CONSTRUCTION_STANDARDS: ValidationCriteria(
                category=ContentCategory.CONSTRUCTION_STANDARDS,
                required_keywords=[
                    "minimum construction standards", "building code", "construction requirements",
                    "accessibility", "ADA compliance", "fair housing", "green building"
                ],
                minimum_content_length=1500,  # Expected for comprehensive standards
                expected_section_count=3,
                critical_importance=True,
                expert_validation_required=True
            ),
            
            ContentCategory.SCORING_CRITERIA: ValidationCriteria(
                category=ContentCategory.SCORING_CRITERIA,
                required_keywords=[
                    "scoring", "points", "criteria", "ranking", "selection",
                    "competitive", "tie-breaker", "priority"
                ],
                minimum_content_length=1000,
                expected_section_count=5,
                critical_importance=True,
                expert_validation_required=True
            ),
            
            ContentCategory.APPLICATION_PROCEDURES: ValidationCriteria(
                category=ContentCategory.APPLICATION_PROCEDURES,
                required_keywords=[
                    "application", "procedure", "deadline", "submission",
                    "requirements", "documentation", "process"
                ],
                minimum_content_length=800,
                expected_section_count=3,
                critical_importance=True,
                expert_validation_required=True
            ),
            
            ContentCategory.COMPLIANCE_MONITORING: ValidationCriteria(
                category=ContentCategory.COMPLIANCE_MONITORING,
                required_keywords=[
                    "compliance", "monitoring", "oversight", "audit",
                    "reporting", "non-compliance", "penalties"
                ],
                minimum_content_length=600,
                expected_section_count=2,
                critical_importance=True,
                expert_validation_required=True
            ),
            
            ContentCategory.FINANCIAL_REQUIREMENTS: ValidationCriteria(
                category=ContentCategory.FINANCIAL_REQUIREMENTS,
                required_keywords=[
                    "financial", "feasibility", "cost", "budget",
                    "funding", "leverage", "debt"
                ],
                minimum_content_length=800,
                expected_section_count=3,
                critical_importance=True,
                expert_validation_required=False
            )
        }
    
    def assess_jurisdiction_quality(self, jurisdiction: str, content_data: Dict[str, str]) -> QualityMetrics:
        """Comprehensive quality assessment for a jurisdiction"""
        
        logger.info(f"Assessing quality for jurisdiction: {jurisdiction}")
        
        # Initialize metrics
        total_expected = len(self.validation_criteria)
        sections_found = 0
        total_content_score = 0.0
        missing_sections = []
        fragmentation_issues = []
        
        # Validate each content category
        for category, criteria in self.validation_criteria.items():
            category_content = content_data.get(category.value, "")
            
            if not category_content or len(category_content.strip()) < 50:
                missing_sections.append(category.value)
                continue
            
            # Run validation
            if category in self.validators:
                validation_result = self.validators[category].validate_content(category_content, criteria)
                
                if validation_result["validation_passed"]:
                    sections_found += 1
                    total_content_score += validation_result["score"]
                else:
                    fragmentation_issues.extend(validation_result.get("issues", []))
            else:
                # Basic validation for categories without specialized validators
                basic_score = self._basic_content_validation(category_content, criteria)
                if basic_score >= 0.95:
                    sections_found += 1
                    total_content_score += basic_score
                else:
                    fragmentation_issues.append(f"{category.value}: Basic validation failed")
        
        # Calculate overall scores
        completeness_score = sections_found / total_expected if total_expected > 0 else 0.0
        content_quality_score = total_content_score / sections_found if sections_found > 0 else 0.0
        
        # Create metrics object
        metrics = QualityMetrics(
            jurisdiction=jurisdiction,
            total_sections_expected=total_expected,
            sections_found=sections_found,
            completeness_score=completeness_score,
            content_quality_score=content_quality_score,
            critical_sections_missing=missing_sections,
            fragmentation_issues=fragmentation_issues,
            validation_timestamp=datetime.now()
        )
        
        # Store metrics
        self.quality_metrics[jurisdiction] = metrics
        
        logger.info(f"Quality assessment complete for {jurisdiction}: "
                   f"Completeness {completeness_score:.1%}, Quality {content_quality_score:.1%}")
        
        return metrics
    
    def _basic_content_validation(self, content: str, criteria: ValidationCriteria) -> float:
        """Basic content validation for categories without specialized validators"""
        
        content_lower = content.lower()
        
        # Check keyword coverage
        keywords_found = sum(1 for keyword in criteria.required_keywords 
                           if keyword.lower() in content_lower)
        keyword_score = keywords_found / len(criteria.required_keywords)
        
        # Check content length
        length_score = min(len(content) / criteria.minimum_content_length, 1.0)
        
        # Simple structure check
        structure_indicators = ["section", "paragraph", "requirement", "criteria"]
        structure_count = sum(1 for indicator in structure_indicators 
                            if indicator in content_lower)
        structure_score = min(structure_count / 2, 1.0)  # Normalize to 0-1
        
        # Weighted score
        overall_score = (keyword_score * 0.5 + length_score * 0.3 + structure_score * 0.2)
        
        return overall_score
    
    def run_minimum_construction_standards_test(self, jurisdiction_content: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        """Run the critical 'minimum construction standards' test across jurisdictions"""
        
        logger.info("Running 'minimum construction standards' test across all jurisdictions")
        
        test_results = {
            "test_name": "minimum_construction_standards_validation",
            "test_description": "Validates that comprehensive construction standards are properly extracted",
            "jurisdictions_tested": 0,
            "jurisdictions_passed": 0,
            "jurisdictions_failed": 0,
            "critical_failures": [],
            "detailed_results": {}
        }
        
        for jurisdiction, content_data in jurisdiction_content.items():
            test_results["jurisdictions_tested"] += 1
            
            # Look for construction standards content
            construction_content = ""
            for category, content in content_data.items():
                if "construction" in category.lower() or "standards" in category.lower():
                    construction_content += content + "\n"
            
            # Test criteria
            test_passed = True
            issues = []
            
            # Must contain the phrase "minimum construction standards"
            if "minimum construction standards" not in construction_content.lower():
                test_passed = False
                issues.append("Missing 'minimum construction standards' phrase")
            
            # Must be substantial content (not just a fragment)
            if len(construction_content) < 1000:
                test_passed = False
                issues.append("Construction standards content too brief (<1000 characters)")
            
            # Must not be fragmented financial terms
            financial_fragments = ["hard construction costs", "limitation on determination"]
            if any(fragment in construction_content.lower() for fragment in financial_fragments) and len(construction_content) < 2000:
                test_passed = False
                issues.append("Content appears to be fragmented financial terms, not comprehensive standards")
            
            # Record results
            if test_passed:
                test_results["jurisdictions_passed"] += 1
            else:
                test_results["jurisdictions_failed"] += 1
                test_results["critical_failures"].append({
                    "jurisdiction": jurisdiction,
                    "issues": issues
                })
            
            test_results["detailed_results"][jurisdiction] = {
                "passed": test_passed,
                "content_length": len(construction_content),
                "issues": issues,
                "content_preview": construction_content[:200] + "..." if construction_content else "No content found"
            }
        
        # Calculate success rate
        success_rate = test_results["jurisdictions_passed"] / test_results["jurisdictions_tested"] if test_results["jurisdictions_tested"] > 0 else 0.0
        test_results["success_rate"] = success_rate
        test_results["test_passed"] = success_rate >= 0.95  # ≥95% jurisdictions must pass
        
        logger.info(f"Minimum construction standards test complete: {success_rate:.1%} success rate")
        
        return test_results
    
    def generate_quality_dashboard(self) -> str:
        """Generate real-time quality dashboard"""
        
        if not self.quality_metrics:
            return "No quality metrics available. Run assessments first."
        
        total_jurisdictions = len(self.quality_metrics)
        passing_jurisdictions = sum(1 for m in self.quality_metrics.values() 
                                   if m.completeness_score >= self.completeness_threshold)
        
        avg_completeness = sum(m.completeness_score for m in self.quality_metrics.values()) / total_jurisdictions
        avg_quality = sum(m.content_quality_score for m in self.quality_metrics.values()) / total_jurisdictions
        
        dashboard = f"""
QAP RAG SYSTEM QUALITY DASHBOARD
================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL SYSTEM STATUS:
Jurisdictions Assessed: {total_jurisdictions}
Passing Quality Gate: {passing_jurisdictions} ({passing_jurisdictions/total_jurisdictions:.1%})
Average Completeness: {avg_completeness:.1%}
Average Content Quality: {avg_quality:.1%}

QUALITY GATE STATUS: {"✅ PASSING" if passing_jurisdictions/total_jurisdictions >= 0.95 else "❌ FAILING"}

DETAILED METRICS:
"""
        
        # Sort by completeness score (worst first)
        sorted_metrics = sorted(self.quality_metrics.values(), key=lambda x: x.completeness_score)
        
        for metrics in sorted_metrics:
            status = "✅ PASS" if metrics.completeness_score >= self.completeness_threshold else "❌ FAIL"
            dashboard += f"""
{metrics.jurisdiction:20s} | {status} | Completeness: {metrics.completeness_score:.1%} | Quality: {metrics.content_quality_score:.1%}
"""
            
            if metrics.critical_sections_missing:
                dashboard += f"  Missing: {', '.join(metrics.critical_sections_missing)}\n"
            if metrics.fragmentation_issues:
                dashboard += f"  Issues: {len(metrics.fragmentation_issues)} fragmentation problems\n"
        
        dashboard += f"""

QUALITY STANDARDS:
- Completeness Threshold: ≥{self.completeness_threshold:.0%}
- Expert Validation Required: ≥{self.expert_validation_threshold:.0%} agreement
- D'Marco Lessons Applied: Universal screening protocol active

ROMAN STANDARD: "Qualitas Perpetua" - Quality Endures
"""
        
        return dashboard
    
    def export_quality_report(self, output_file: Optional[str] = None) -> str:
        """Export comprehensive quality report"""
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.output_path / f"quality_assessment_report_{timestamp}.json"
        
        report_data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "total_jurisdictions": len(self.quality_metrics),
                "completeness_threshold": self.completeness_threshold,
                "expert_validation_threshold": self.expert_validation_threshold,
                "dmarco_lessons_applied": True
            },
            "summary": {
                "jurisdictions_assessed": len(self.quality_metrics),
                "passing_quality_gate": sum(1 for m in self.quality_metrics.values() 
                                          if m.completeness_score >= self.completeness_threshold),
                "average_completeness": sum(m.completeness_score for m in self.quality_metrics.values()) / len(self.quality_metrics) if self.quality_metrics else 0,
                "average_content_quality": sum(m.content_quality_score for m in self.quality_metrics.values()) / len(self.quality_metrics) if self.quality_metrics else 0
            },
            "detailed_metrics": {
                jurisdiction: {
                    "completeness_score": metrics.completeness_score,
                    "content_quality_score": metrics.content_quality_score,
                    "sections_found": metrics.sections_found,
                    "sections_expected": metrics.total_sections_expected,
                    "critical_sections_missing": metrics.critical_sections_missing,
                    "fragmentation_issues": metrics.fragmentation_issues,
                    "validation_timestamp": metrics.validation_timestamp.isoformat() if metrics.validation_timestamp else None
                }
                for jurisdiction, metrics in self.quality_metrics.items()
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Quality report exported to: {output_file}")
        return str(output_file)

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python3 quality_assurance_framework.py <command> [options]")
        print("Commands:")
        print("  dashboard                 - Generate quality dashboard")
        print("  test <data_file>          - Run minimum construction standards test")
        print("  assess <jurisdiction> <content_file> - Assess jurisdiction quality")
        print("  export                    - Export quality report")
        sys.exit(1)
    
    framework = QualityAssuranceFramework()
    command = sys.argv[1].lower()
    
    if command == "dashboard":
        print("\nGenerating Quality Dashboard...")
        dashboard = framework.generate_quality_dashboard()
        print(dashboard)
        
    elif command == "test" and len(sys.argv) > 2:
        data_file = sys.argv[2]
        print(f"\nRunning minimum construction standards test with: {data_file}")
        
        # Load test data (would come from actual QAP extraction system)
        test_data = {
            "CA": {
                "construction_standards": "Hard construction costs and limitation on determination...",  # Simulated bad data
                "scoring_criteria": "Some scoring content..."
            }
        }
        
        results = framework.run_minimum_construction_standards_test(test_data)
        print(json.dumps(results, indent=2))
        
    elif command == "export":
        print("\nExporting quality report...")
        output_file = framework.export_quality_report()
        print(f"Report exported to: {output_file}")
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()