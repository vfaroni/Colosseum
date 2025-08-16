#!/usr/bin/env python3
"""
Cross-Reference Validation System
Validates and enforces regulatory hierarchy across complete regulatory universe

Implements:
- Federal > State > Municipal hierarchy enforcement
- Cross-reference validation between QAPs and external regulations
- Conflict detection and resolution
- Authority precedence validation

Built by Structured Consultants LLC
Roman Engineering Standards: Built to Last 2000+ Years
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AuthorityLevel(Enum):
    """Regulatory authority hierarchy"""
    FEDERAL_STATUTORY = 100    # IRC, USC
    FEDERAL_REGULATORY = 80    # CFR
    FEDERAL_GUIDANCE = 60      # Revenue Procedures, Notices
    FEDERAL_INTERPRETIVE = 40  # Private Letter Rulings, TAMs
    STATE_STATUTORY = 35       # State statutes
    STATE_REGULATORY = 30      # State QAPs, Administrative Codes
    MUNICIPAL_CODE = 20        # City/county ordinances
    LOCAL_GUIDANCE = 10        # Local housing authority rules

@dataclass
class RegulationReference:
    """A reference to another regulation"""
    source_id: str              # Where the reference appears
    target_regulation: str      # What regulation is referenced
    reference_text: str         # Exact text of the reference
    reference_type: str         # "cites", "implements", "supersedes", "conflicts"
    authority_level: AuthorityLevel
    confidence: float           # 0.0-1.0 confidence in reference accuracy
    context: str               # Surrounding context of reference

@dataclass
class RegulatoryConflict:
    """Detected conflict between regulations"""
    conflict_id: str
    regulation_1: str
    regulation_2: str
    conflict_type: str          # "contradiction", "ambiguity", "gap"
    description: str
    severity: str              # "critical", "moderate", "minor"
    resolution: str            # How to resolve the conflict
    authority_precedence: str  # Which regulation takes precedence

@dataclass
class ValidationResult:
    """Result of cross-reference validation"""
    regulation_id: str
    total_references: int
    valid_references: int
    broken_references: int
    conflicts: List[RegulatoryConflict]
    warnings: List[str]
    validation_status: str     # "passed", "failed", "warnings"

class CrossReferenceValidator:
    """Validates cross-references in regulatory content"""
    
    def __init__(self):
        self.reference_patterns = self._define_reference_patterns()
        self.authority_hierarchy = self._define_authority_hierarchy()
        self.known_regulations = set()
        
    def _define_reference_patterns(self) -> Dict[str, List[str]]:
        """Define regex patterns for different types of references"""
        
        return {
            "federal_irc": [
                r'IRC\s+Section\s+(\d+[a-z]*(?:\([^)]+\))*)',
                r'Internal\s+Revenue\s+Code\s+Section\s+(\d+[a-z]*(?:\([^)]+\))*)',
                r'section\s+(\d+)\s+of\s+the\s+Code',
                r'Section\s+(\d+[a-z]*(?:\([^)]+\))*)\s+of\s+the\s+Internal\s+Revenue\s+Code'
            ],
            "federal_cfr": [
                r'(\d+)\s+CFR\s+(?:Part\s+)?(\d+)(?:\.(\d+))?(?:-(\d+))?',
                r'(\d+)\s+C\.F\.R\.\s+§\s*(\d+\.\d+)',
                r'§\s*(\d+\.\d+-\d+)',
                r'Regulation\s+§\s*(\d+\.\d+-\d+)'
            ],
            "state_statute": [
                r'(Health\s+(?:and|&)\s+Safety\s+Code)\s+Section[s]?\s+([\d.]+)',
                r'(Revenue\s+(?:and|&)\s+Taxation\s+Code)\s+Section[s]?\s+([\d.]+)',
                r'(Government\s+Code)\s+(?:Chapter\s+)?(\d+)',
                r'Section\s+([\d.]+)[,\s]+(Florida\s+Statutes|F\.S\.)',
                r'(Texas\s+Government\s+Code)\s+(?:Chapter\s+)?(\d+)'
            ],
            "state_admin_code": [
                r'Rule\s+Chapter\s+(67-\d+)',
                r'(\d+)\s+TAC\s+(?:Chapter\s+)?(\d+)',
                r'Title\s+(\d+)\s+(?:CCR|Texas\s+Administrative\s+Code)',
                r'§\s*(\d+)\s+of\s+the\s+(?:QAP|Qualified\s+Allocation\s+Plan)'
            ],
            "qap_internal": [
                r'Section\s+([IVX]+)',
                r'Part\s+([IVX]+)',
                r'subsection\s+\(([a-z0-9]+)\)',
                r'paragraph\s+\(([a-z0-9]+)\)'
            ]
        }
    
    def _define_authority_hierarchy(self) -> Dict[AuthorityLevel, int]:
        """Define authority precedence scores"""
        
        return {
            AuthorityLevel.FEDERAL_STATUTORY: 100,
            AuthorityLevel.FEDERAL_REGULATORY: 80,
            AuthorityLevel.FEDERAL_GUIDANCE: 60,
            AuthorityLevel.FEDERAL_INTERPRETIVE: 40,
            AuthorityLevel.STATE_STATUTORY: 35,
            AuthorityLevel.STATE_REGULATORY: 30,
            AuthorityLevel.MUNICIPAL_CODE: 20,
            AuthorityLevel.LOCAL_GUIDANCE: 10
        }
    
    def extract_references(self, content: str, source_id: str, authority_level: AuthorityLevel) -> List[RegulationReference]:
        """Extract all regulation references from content"""
        
        references = []
        
        for ref_type, patterns in self.reference_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    # Extract context around the reference
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end].strip()
                    
                    reference = RegulationReference(
                        source_id=source_id,
                        target_regulation=self._format_regulation_id(match, ref_type),
                        reference_text=match.group(0),
                        reference_type=self._determine_reference_type(context),
                        authority_level=authority_level,
                        confidence=self._calculate_reference_confidence(match, context),
                        context=context
                    )
                    
                    references.append(reference)
        
        return references
    
    def _format_regulation_id(self, match, ref_type: str) -> str:
        """Format regulation ID from regex match"""
        
        if ref_type == "federal_irc":
            return f"IRC_SECTION_{match.group(1)}"
        elif ref_type == "federal_cfr":
            groups = [g for g in match.groups() if g]
            return f"26_CFR_{'_'.join(groups)}"
        elif ref_type == "state_statute":
            return f"STATE_STATUTE_{match.group(1)}_{match.group(2)}"
        elif ref_type == "state_admin_code":
            return f"STATE_ADMIN_{match.group(1) if match.group(1) else match.group(0)}"
        elif ref_type == "qap_internal":
            return f"QAP_SECTION_{match.group(1)}"
        else:
            return match.group(0)
    
    def _determine_reference_type(self, context: str) -> str:
        """Determine the type of reference from context"""
        
        context_lower = context.lower()
        
        if any(word in context_lower for word in ["pursuant to", "in accordance with", "as required by"]):
            return "implements"
        elif any(word in context_lower for word in ["see also", "refer to", "as defined in"]):
            return "cites"
        elif any(word in context_lower for word in ["supersedes", "replaces", "overrides"]):
            return "supersedes"
        elif any(word in context_lower for word in ["conflicts with", "inconsistent with"]):
            return "conflicts"
        else:
            return "cites"
    
    def _calculate_reference_confidence(self, match, context: str) -> float:
        """Calculate confidence score for reference accuracy"""
        
        confidence = 0.8  # Base confidence
        
        # Boost confidence for complete section numbers
        if re.search(r'\d+\([a-z]+\)', match.group(0)):
            confidence += 0.1
        
        # Boost confidence for formal language
        if any(word in context.lower() for word in ["section", "subsection", "paragraph", "code"]):
            confidence += 0.05
        
        # Reduce confidence for abbreviated references
        if len(match.group(0)) < 10:
            confidence -= 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def validate_references(self, regulation_id: str, content: str, authority_level: AuthorityLevel) -> ValidationResult:
        """Validate all references in a regulation"""
        
        logger.info(f"Validating references in {regulation_id}")
        
        # Extract all references
        references = self.extract_references(content, regulation_id, authority_level)
        
        # Validate each reference
        valid_count = 0
        broken_count = 0
        conflicts = []
        warnings = []
        
        for ref in references:
            if self._is_valid_reference(ref):
                valid_count += 1
            else:
                broken_count += 1
                warnings.append(f"Broken reference: {ref.reference_text} -> {ref.target_regulation}")
        
        # Check for authority conflicts
        authority_conflicts = self._detect_authority_conflicts(references)
        conflicts.extend(authority_conflicts)
        
        # Determine validation status
        if broken_count == 0 and len(conflicts) == 0:
            status = "passed"
        elif len(conflicts) > 0:
            status = "failed"
        else:
            status = "warnings"
        
        return ValidationResult(
            regulation_id=regulation_id,
            total_references=len(references),
            valid_references=valid_count,
            broken_references=broken_count,
            conflicts=conflicts,
            warnings=warnings,
            validation_status=status
        )
    
    def _is_valid_reference(self, reference: RegulationReference) -> bool:
        """Check if a reference points to a valid regulation"""
        
        # In production, this would check against a database of known regulations
        # For now, assume high-confidence references are valid
        return reference.confidence > 0.7
    
    def _detect_authority_conflicts(self, references: List[RegulationReference]) -> List[RegulatoryConflict]:
        """Detect conflicts in regulatory authority"""
        
        conflicts = []
        
        # Group references by target regulation
        ref_groups = {}
        for ref in references:
            target = ref.target_regulation
            if target not in ref_groups:
                ref_groups[target] = []
            ref_groups[target].append(ref)
        
        # Check for conflicting implementations
        for target, refs in ref_groups.items():
            if len(refs) > 1:
                # Check if references have conflicting types
                types = set(ref.reference_type for ref in refs)
                if "implements" in types and "conflicts" in types:
                    conflict = RegulatoryConflict(
                        conflict_id=f"CONFLICT_{target}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        regulation_1=refs[0].source_id,
                        regulation_2=refs[1].source_id,
                        conflict_type="contradiction",
                        description=f"Conflicting references to {target}",
                        severity="moderate",
                        resolution="Review regulatory hierarchy and precedence",
                        authority_precedence=self._determine_precedence(refs)
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def _determine_precedence(self, references: List[RegulationReference]) -> str:
        """Determine which regulation takes precedence"""
        
        # Sort by authority level (highest first)
        sorted_refs = sorted(references, key=lambda r: self.authority_hierarchy[r.authority_level], reverse=True)
        
        if sorted_refs:
            highest_authority = sorted_refs[0]
            return f"{highest_authority.source_id} (Authority Level: {highest_authority.authority_level.value})"
        
        return "Unable to determine precedence"
    
    def validate_regulatory_universe(self, regulations: Dict[str, any]) -> Dict[str, ValidationResult]:
        """Validate cross-references across entire regulatory universe"""
        
        logger.info(f"🔍 Validating regulatory universe with {len(regulations)} regulations")
        
        results = {}
        
        for reg_id, reg_data in regulations.items():
            # Determine authority level from regulation ID
            authority_level = self._determine_authority_level(reg_id)
            
            # Extract content
            content = ""
            if hasattr(reg_data, 'content'):
                content = reg_data.content
            elif isinstance(reg_data, dict) and 'content' in reg_data:
                content = reg_data['content']
            else:
                content = str(reg_data)
            
            # Validate references
            result = self.validate_references(reg_id, content, authority_level)
            results[reg_id] = result
        
        return results
    
    def _determine_authority_level(self, regulation_id: str) -> AuthorityLevel:
        """Determine authority level from regulation ID"""
        
        reg_id_upper = regulation_id.upper()
        
        if "IRC_SECTION" in reg_id_upper:
            return AuthorityLevel.FEDERAL_STATUTORY
        elif "CFR" in reg_id_upper:
            return AuthorityLevel.FEDERAL_REGULATORY
        elif "QAP" in reg_id_upper or "STATE_ADMIN" in reg_id_upper:
            return AuthorityLevel.STATE_REGULATORY
        elif "STATE_STATUTE" in reg_id_upper:
            return AuthorityLevel.STATE_STATUTORY
        elif "MUNICIPAL" in reg_id_upper:
            return AuthorityLevel.MUNICIPAL_CODE
        else:
            return AuthorityLevel.STATE_REGULATORY  # Default assumption
    
    def generate_validation_report(self, validation_results: Dict[str, ValidationResult]) -> str:
        """Generate comprehensive validation report"""
        
        total_regulations = len(validation_results)
        passed_count = sum(1 for r in validation_results.values() if r.validation_status == "passed")
        warning_count = sum(1 for r in validation_results.values() if r.validation_status == "warnings")
        failed_count = sum(1 for r in validation_results.values() if r.validation_status == "failed")
        
        total_references = sum(r.total_references for r in validation_results.values())
        total_valid = sum(r.valid_references for r in validation_results.values())
        total_broken = sum(r.broken_references for r in validation_results.values())
        total_conflicts = sum(len(r.conflicts) for r in validation_results.values())
        
        report = f"""
🏛️ CROSS-REFERENCE VALIDATION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
========================================

📊 VALIDATION SUMMARY:
  Total Regulations: {total_regulations:,}
  ✅ Passed: {passed_count:,} ({passed_count/total_regulations*100:.1f}%)
  ⚠️  Warnings: {warning_count:,} ({warning_count/total_regulations*100:.1f}%)
  ❌ Failed: {failed_count:,} ({failed_count/total_regulations*100:.1f}%)

📋 REFERENCE SUMMARY:
  Total References: {total_references:,}
  Valid References: {total_valid:,} ({total_valid/total_references*100:.1f}%)
  Broken References: {total_broken:,} ({total_broken/total_references*100:.1f}%)
  Authority Conflicts: {total_conflicts:,}

🎯 VALIDATION DETAILS:
"""
        
        # Add details for failed regulations
        for reg_id, result in validation_results.items():
            if result.validation_status == "failed":
                report += f"\n❌ {reg_id}:\n"
                report += f"   References: {result.total_references} total, {result.broken_references} broken\n"
                for conflict in result.conflicts:
                    report += f"   Conflict: {conflict.description} ({conflict.severity})\n"
        
        # Add warnings
        warning_regulations = [r for r in validation_results.values() if r.validation_status == "warnings"]
        if warning_regulations:
            report += f"\n⚠️  REGULATIONS WITH WARNINGS:\n"
            for result in warning_regulations[:5]:  # Show first 5
                report += f"   {result.regulation_id}: {len(result.warnings)} warnings\n"
        
        report += f"\n✅ VALIDATION COMPLETE"
        
        return report

def main():
    """Test cross-reference validation system"""
    
    print("🏛️ CROSS-REFERENCE VALIDATION SYSTEM")
    print("=" * 60)
    
    validator = CrossReferenceValidator()
    
    # Create sample regulations for testing
    sample_regulations = {
        "CA_QAP_2025": {
            "content": """
            Section 10302 implements IRC Section 42 and is subject to 26 CFR 1.42-1.
            This section refers to Health and Safety Code Section 50199.4 and 
            Revenue and Taxation Code Section 17058. See also Part II of this QAP.
            """
        },
        "IRC_SECTION_42": {
            "content": """
            (a) In general - For purposes of section 38, the amount of the low-income 
            housing credit determined under this section shall be calculated pursuant 
            to subsection (b). See also 26 CFR 1.42-1 for implementation details.
            """
        },
        "FL_QAP_2025": {
            "content": """
            This allocation plan implements Rule Chapter 67-21 and is consistent 
            with IRC Section 42(m). Applications must comply with Section 420.5099, 
            Florida Statutes and 26 CFR Part 1.
            """
        }
    }
    
    # Validate regulatory universe
    validation_results = validator.validate_regulatory_universe(sample_regulations)
    
    # Generate and display report
    report = validator.generate_validation_report(validation_results)
    print(report)

if __name__ == "__main__":
    main()