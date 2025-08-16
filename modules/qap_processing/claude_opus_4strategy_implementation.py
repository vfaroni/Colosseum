#!/usr/bin/env python3
"""
Claude Opus 4-Strategy QAP Chunking Implementation
Emergency reconstruction of QAP RAG system using research-backed methodology

Based on: Claude_Opus_DR_07122025.md research analyzing 117 QAPs across 56 jurisdictions
Addresses: Critical chunking failure across all 54 jurisdictions identified August 1, 2025

Built by Structured Consultants LLC
Roman Engineering Standards: Built to Last 2000+ Years
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import time
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChunkingStrategy(Enum):
    """4-Strategy framework from Claude Opus research"""
    COMPLEX_OUTLINE = "complex_outline"      # 40% of jurisdictions
    MEDIUM_COMPLEXITY = "medium_complexity"   # 35% of jurisdictions  
    SIMPLE_NARRATIVE = "simple_narrative"     # 20% of jurisdictions
    TABLE_MATRIX = "table_matrix"            # 5% of jurisdictions

@dataclass
class StrategyConfig:
    """Configuration for each chunking strategy"""
    name: str
    token_range: Tuple[int, int]
    nesting_levels: int
    characteristics: List[str]
    requirements: List[str]
    target_jurisdictions: List[str]

@dataclass
class JurisdictionMapping:
    """Mapping of jurisdiction to appropriate strategy"""
    jurisdiction: str
    state_code: str
    strategy: ChunkingStrategy
    complexity_score: float
    rationale: str

class ClaudeOpus4StrategyFramework:
    """Implementation of Claude Opus 4-strategy research for QAP chunking"""
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent.parent
        self.qap_data_path = self.base_path / "data_sets" / "QAP"
        self.output_path = self.base_path / "modules" / "qap_processing" / "4strategy_output"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize strategy configurations
        self.strategies = self._initialize_strategies()
        
        # Load jurisdiction mappings
        self.jurisdiction_mappings = self._load_jurisdiction_mappings()
        
        # Quality standards from D'Marco lessons
        self.quality_threshold = 0.95  # ≥95% completeness requirement
        
    def _initialize_strategies(self) -> Dict[ChunkingStrategy, StrategyConfig]:
        """Initialize the 4-strategy configurations from research"""
        
        return {
            ChunkingStrategy.COMPLEX_OUTLINE: StrategyConfig(
                name="Complex Outline-Based Strategy",
                token_range=(800, 1500),
                nesting_levels=7,
                characteristics=[
                    "5-7 hierarchical nesting levels",
                    "Detailed section/subsection organization", 
                    "Comprehensive cross-references",
                    "Formal regulatory structure"
                ],
                requirements=[
                    "Preserve hierarchical context",
                    "Maintain cross-reference integrity",
                    "Section-aware chunking boundaries",
                    "Regulatory citation preservation"
                ],
                target_jurisdictions=["CA", "TX", "NC", "IL", "VA", "PA", "OH", "GA"]
            ),
            
            ChunkingStrategy.MEDIUM_COMPLEXITY: StrategyConfig(
                name="Medium Complexity Strategy", 
                token_range=(600, 1200),
                nesting_levels=4,
                characteristics=[
                    "3-4 hierarchical nesting levels",
                    "Moderate structural complexity",
                    "Balanced narrative-outline hybrid",
                    "Standard regulatory format"
                ],
                requirements=[
                    "Flexible boundary detection",
                    "Context preservation across sections",
                    "Moderate overlap for continuity",
                    "Section relationship maintenance"
                ],
                target_jurisdictions=["FL", "NY", "MI", "WA", "MN", "WI", "CO", "AZ"]
            ),
            
            ChunkingStrategy.SIMPLE_NARRATIVE: StrategyConfig(
                name="Simple Narrative-Based Strategy",
                token_range=(400, 1200), 
                nesting_levels=2,
                characteristics=[
                    "Topic-based organization",
                    "Minimal hierarchical structure", 
                    "Flowing narrative style",
                    "Conversational regulatory tone"
                ],
                requirements=[
                    "Topic-boundary awareness",
                    "Natural language flow preservation",
                    "Semantic coherence prioritization",
                    "Narrative continuity maintenance"
                ],
                target_jurisdictions=["MA", "OR", "NV", "UT", "NM", "MT", "ID", "WY"]
            ),
            
            ChunkingStrategy.TABLE_MATRIX: StrategyConfig(
                name="Table/Matrix-Heavy Strategy",
                token_range=(300, 800),
                nesting_levels=2,
                characteristics=[
                    "Data-driven organizational structure",
                    "Matrix-based information presentation",
                    "Tabular format dependencies", 
                    "Structured data emphasis"
                ],
                requirements=[
                    "Table structure preservation",
                    "Matrix relationship maintenance",
                    "Data integrity validation",
                    "Structured format retention"
                ],
                target_jurisdictions=["DE", "GU", "VI", "PR", "HI"]
            )
        }
    
    def _load_jurisdiction_mappings(self) -> List[JurisdictionMapping]:
        """Load the complete 54-jurisdiction to strategy mappings"""
        
        mappings = []
        
        # Complex Outline-Based (40% - 22 jurisdictions)
        complex_jurisdictions = [
            ("CA", "California"), ("TX", "Texas"), ("NC", "North Carolina"), 
            ("IL", "Illinois"), ("VA", "Virginia"), ("PA", "Pennsylvania"),
            ("OH", "Ohio"), ("GA", "Georgia"), ("TN", "Tennessee"),
            ("IN", "Indiana"), ("MO", "Missouri"), ("MD", "Maryland"),
            ("SC", "South Carolina"), ("AL", "Alabama"), ("KY", "Kentucky"),
            ("LA", "Louisiana"), ("MS", "Mississippi"), ("AR", "Arkansas"),
            ("OK", "Oklahoma"), ("KS", "Kansas"), ("NE", "Nebraska"), ("IA", "Iowa")
        ]
        
        for state_code, state_name in complex_jurisdictions:
            mappings.append(JurisdictionMapping(
                jurisdiction=state_name,
                state_code=state_code,
                strategy=ChunkingStrategy.COMPLEX_OUTLINE,
                complexity_score=0.85,
                rationale="Large state with comprehensive regulatory framework requiring detailed hierarchical processing"
            ))
        
        # Medium Complexity (35% - 19 jurisdictions)  
        medium_jurisdictions = [
            ("FL", "Florida"), ("NY", "New York"), ("MI", "Michigan"),
            ("WA", "Washington"), ("MN", "Minnesota"), ("WI", "Wisconsin"),
            ("CO", "Colorado"), ("AZ", "Arizona"), ("CT", "Connecticut"),
            ("ME", "Maine"), ("NH", "New Hampshire"), ("VT", "Vermont"),
            ("RI", "Rhode Island"), ("NJ", "New Jersey"), ("WV", "West Virginia"),
            ("ND", "North Dakota"), ("SD", "South Dakota"), ("AK", "Alaska"), ("DC", "District of Columbia")
        ]
        
        for state_code, state_name in medium_jurisdictions:
            mappings.append(JurisdictionMapping(
                jurisdiction=state_name,
                state_code=state_code,
                strategy=ChunkingStrategy.MEDIUM_COMPLEXITY,
                complexity_score=0.65,
                rationale="Moderate regulatory complexity requiring balanced narrative-outline approach"
            ))
        
        # Simple Narrative (20% - 11 jurisdictions)
        simple_jurisdictions = [
            ("MA", "Massachusetts"), ("OR", "Oregon"), ("NV", "Nevada"),
            ("UT", "Utah"), ("NM", "New Mexico"), ("MT", "Montana"),
            ("ID", "Idaho"), ("WY", "Wyoming"), ("VT", "Vermont"),
            ("NH", "New Hampshire"), ("ME", "Maine")
        ]
        
        for state_code, state_name in simple_jurisdictions:
            mappings.append(JurisdictionMapping(
                jurisdiction=state_name,
                state_code=state_code,
                strategy=ChunkingStrategy.SIMPLE_NARRATIVE,
                complexity_score=0.45,
                rationale="Streamlined regulatory approach with topic-based organization"
            ))
        
        # Table/Matrix Heavy (5% - 3 jurisdictions)
        table_jurisdictions = [
            ("DE", "Delaware"), ("GU", "Guam"), ("VI", "Virgin Islands"),
            ("PR", "Puerto Rico"), ("HI", "Hawaii")
        ]
        
        for state_code, state_name in table_jurisdictions:
            mappings.append(JurisdictionMapping(
                jurisdiction=state_name,
                state_code=state_code,
                strategy=ChunkingStrategy.TABLE_MATRIX,
                complexity_score=0.25,
                rationale="Data-driven format requiring specialized table/matrix processing"
            ))
        
        return mappings
    
    def get_strategy_for_jurisdiction(self, jurisdiction: str) -> Optional[JurisdictionMapping]:
        """Get the appropriate strategy for a jurisdiction"""
        for mapping in self.jurisdiction_mappings:
            if (mapping.jurisdiction.lower() == jurisdiction.lower() or 
                mapping.state_code.lower() == jurisdiction.lower()):
                return mapping
        return None
    
    def analyze_qap_structure(self, qap_file_path: str) -> Dict[str, Any]:
        """Analyze QAP structure to validate strategy assignment"""
        qap_path = Path(qap_file_path)
        
        if not qap_path.exists():
            return {"error": f"QAP file not found: {qap_file_path}"}
        
        analysis = {
            "file_path": str(qap_path),
            "file_size_mb": round(qap_path.stat().st_size / (1024 * 1024), 2),
            "strategy_recommendation": None,
            "confidence_score": 0.0,
            "structural_indicators": {},
            "content_categories": []
        }
        
        try:
            # This would integrate with docling for actual PDF analysis
            # For now, provide framework for analysis
            logger.info(f"Analyzing QAP structure: {qap_path.name}")
            
            # Placeholder for actual document analysis
            analysis["structural_indicators"] = {
                "estimated_sections": 0,
                "nesting_depth": 0,
                "table_count": 0,
                "cross_references": 0,
                "regulatory_complexity": "unknown"
            }
            
            analysis["content_categories"] = [
                "construction_standards",
                "scoring_criteria", 
                "application_requirements",
                "compliance_monitoring",
                "financial_requirements"
            ]
            
        except Exception as e:
            analysis["error"] = str(e)
            logger.error(f"Error analyzing QAP structure: {e}")
        
        return analysis
    
    def create_chunking_plan(self, jurisdiction: str) -> Dict[str, Any]:
        """Create comprehensive chunking plan for a jurisdiction"""
        
        mapping = self.get_strategy_for_jurisdiction(jurisdiction)
        if not mapping:
            return {"error": f"No strategy mapping found for jurisdiction: {jurisdiction}"}
        
        strategy_config = self.strategies[mapping.strategy]
        
        plan = {
            "jurisdiction": jurisdiction,
            "state_code": mapping.state_code,
            "strategy": {
                "type": mapping.strategy.value,
                "name": strategy_config.name,
                "rationale": mapping.rationale,
                "confidence": mapping.complexity_score
            },
            "chunking_parameters": {
                "token_range": strategy_config.token_range,
                "max_nesting_levels": strategy_config.nesting_levels,
                "overlap_strategy": self._get_overlap_strategy(mapping.strategy),
                "boundary_detection": self._get_boundary_strategy(mapping.strategy)
            },
            "quality_requirements": {
                "completeness_threshold": self.quality_threshold,
                "required_sections": self._get_required_sections(),
                "validation_criteria": self._get_validation_criteria(mapping.strategy)
            },
            "processing_requirements": strategy_config.requirements,
            "expected_outcomes": self._get_expected_outcomes(mapping.strategy)
        }
        
        return plan
    
    def _get_overlap_strategy(self, strategy: ChunkingStrategy) -> str:
        """Get overlap strategy based on chunking approach"""
        overlap_map = {
            ChunkingStrategy.COMPLEX_OUTLINE: "hierarchical_overlap",
            ChunkingStrategy.MEDIUM_COMPLEXITY: "moderate_overlap", 
            ChunkingStrategy.SIMPLE_NARRATIVE: "semantic_overlap",
            ChunkingStrategy.TABLE_MATRIX: "structural_overlap"
        }
        return overlap_map.get(strategy, "standard_overlap")
    
    def _get_boundary_strategy(self, strategy: ChunkingStrategy) -> str:
        """Get boundary detection strategy"""
        boundary_map = {
            ChunkingStrategy.COMPLEX_OUTLINE: "section_header_boundaries",
            ChunkingStrategy.MEDIUM_COMPLEXITY: "mixed_boundaries",
            ChunkingStrategy.SIMPLE_NARRATIVE: "topic_boundaries", 
            ChunkingStrategy.TABLE_MATRIX: "table_boundaries"
        }
        return boundary_map.get(strategy, "standard_boundaries")
    
    def _get_required_sections(self) -> List[str]:
        """Get required sections for quality validation"""
        return [
            "construction_standards",
            "minimum_construction_requirements", 
            "scoring_criteria",
            "application_procedures",
            "compliance_monitoring",
            "financial_requirements",
            "geographic_preferences",
            "special_populations",
            "deadlines_and_procedures",
            "contact_information"
        ]
    
    def _get_validation_criteria(self, strategy: ChunkingStrategy) -> List[str]:
        """Get validation criteria specific to strategy"""
        base_criteria = [
            "content_completeness_≥95%",
            "section_integrity_maintained",
            "regulatory_accuracy_verified",
            "cross_references_preserved"
        ]
        
        strategy_specific = {
            ChunkingStrategy.COMPLEX_OUTLINE: [
                "hierarchical_structure_preserved",
                "nested_section_relationships_intact",
                "formal_citations_accurate"
            ],
            ChunkingStrategy.MEDIUM_COMPLEXITY: [
                "section_flow_maintained", 
                "context_boundaries_clear",
                "narrative_coherence_preserved"
            ],
            ChunkingStrategy.SIMPLE_NARRATIVE: [
                "topic_boundaries_natural",
                "narrative_flow_unbroken",
                "semantic_coherence_high"
            ],
            ChunkingStrategy.TABLE_MATRIX: [
                "table_structure_intact",
                "data_relationships_preserved",
                "matrix_formatting_maintained"
            ]
        }
        
        return base_criteria + strategy_specific.get(strategy, [])
    
    def _get_expected_outcomes(self, strategy: ChunkingStrategy) -> Dict[str, Any]:
        """Get expected processing outcomes"""
        config = self.strategies[strategy]
        
        return {
            "estimated_chunks": "varies_by_document_size",
            "average_chunk_size": f"{config.token_range[0]}-{config.token_range[1]} tokens",
            "processing_complexity": config.nesting_levels,
            "quality_score_target": ">95%",
            "search_effectiveness": "high",
            "regulatory_completeness": "comprehensive"
        }
    
    def generate_implementation_report(self) -> str:
        """Generate comprehensive implementation report"""
        
        report = f"""CLAUDE OPUS 4-STRATEGY IMPLEMENTATION REPORT
=============================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EMERGENCY QAP RAG RECONSTRUCTION FRAMEWORK
Based on: Claude_Opus_DR_07122025.md research (117 QAPs, 56 jurisdictions)
Addresses: Critical chunking failure identified August 1, 2025

STRATEGY DISTRIBUTION ANALYSIS:
"""
        
        for strategy, config in self.strategies.items():
            strategy_count = len([m for m in self.jurisdiction_mappings if m.strategy == strategy])
            percentage = (strategy_count / len(self.jurisdiction_mappings)) * 100
            
            report += f"""
{config.name}:
  - Target Jurisdictions: {strategy_count} ({percentage:.1f}%)
  - Token Range: {config.token_range[0]}-{config.token_range[1]}
  - Nesting Levels: {config.nesting_levels}
  - Key Requirements: {', '.join(config.requirements[:2])}
"""
        
        report += f"""

JURISDICTION ASSIGNMENTS:
========================
Total Jurisdictions: {len(self.jurisdiction_mappings)}
Quality Threshold: ≥{self.quality_threshold*100}% completeness

"""
        
        # Group by strategy for summary
        strategy_groups = {}
        for mapping in self.jurisdiction_mappings:
            if mapping.strategy not in strategy_groups:
                strategy_groups[mapping.strategy] = []
            strategy_groups[mapping.strategy].append(mapping)
        
        for strategy, mappings in strategy_groups.items():
            config = self.strategies[strategy]
            report += f"{config.name} ({len(mappings)} jurisdictions):\n"
            state_codes = [m.state_code for m in mappings]
            report += f"  States: {', '.join(sorted(state_codes))}\n\n"
        
        report += """
IMPLEMENTATION PRIORITIES:
=========================
1. CRITICAL SECTIONS RECOVERY:
   - Minimum construction standards (comprehensive sections, not fragments)
   - Scoring criteria (complete point allocations)  
   - Application procedures (complete requirements)
   - Compliance monitoring (complete oversight)

2. QUALITY VALIDATION:
   - ≥95% content completeness per jurisdiction
   - Expert validation against professional market studies
   - "Minimum construction standards" test passing
   - Cross-reference integrity maintained

3. SYSTEM RELIABILITY:
   - Docling pipeline optimization (96% PDF coverage achieved)
   - Multi-agent quality gates (STRIKE_LEADER → WINGMAN → TOWER)
   - Real-time completeness monitoring
   - Professional deployment readiness

ROMAN ENGINEERING STANDARD: "Qualitas Perpetua" - Quality Endures

Built by Structured Consultants LLC
System Status: RECONSTRUCTION IN PROGRESS
"""
        
        return report
    
    def export_jurisdiction_mappings(self, output_file: Optional[str] = None) -> str:
        """Export jurisdiction mappings to JSON for integration"""
        
        if not output_file:
            output_file = self.output_path / "jurisdiction_strategy_mappings.json"
        
        mappings_data = []
        for mapping in self.jurisdiction_mappings:
            mappings_data.append({
                "jurisdiction": mapping.jurisdiction,
                "state_code": mapping.state_code,
                "strategy": mapping.strategy.value,
                "complexity_score": mapping.complexity_score,
                "rationale": mapping.rationale,
                "chunking_config": {
                    "token_range": self.strategies[mapping.strategy].token_range,
                    "nesting_levels": self.strategies[mapping.strategy].nesting_levels,
                    "requirements": self.strategies[mapping.strategy].requirements
                }
            })
        
        with open(output_file, 'w') as f:
            json.dump({
                "metadata": {
                    "generated": datetime.now().isoformat(),
                    "total_jurisdictions": len(mappings_data),
                    "quality_threshold": self.quality_threshold,
                    "research_basis": "Claude_Opus_DR_07122025.md"
                },
                "jurisdiction_mappings": mappings_data
            }, f, indent=2)
        
        logger.info(f"Jurisdiction mappings exported to: {output_file}")
        return str(output_file)

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python3 claude_opus_4strategy_implementation.py <command> [options]")
        print("Commands:")
        print("  report                    - Generate implementation report")
        print("  plan <jurisdiction>       - Create chunking plan for jurisdiction")
        print("  analyze <qap_file>        - Analyze QAP structure")
        print("  export                    - Export jurisdiction mappings")
        print("  list                      - List all jurisdiction assignments")
        sys.exit(1)
    
    framework = ClaudeOpus4StrategyFramework()
    command = sys.argv[1].lower()
    
    if command == "report":
        print("\nGenerating Claude Opus 4-Strategy Implementation Report...")
        report = framework.generate_implementation_report()
        print(report)
        
        # Save report
        report_file = framework.output_path / f"4strategy_implementation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {report_file}")
        
    elif command == "plan" and len(sys.argv) > 2:
        jurisdiction = sys.argv[2]
        print(f"\nCreating chunking plan for: {jurisdiction}")
        plan = framework.create_chunking_plan(jurisdiction)
        
        if "error" in plan:
            print(f"Error: {plan['error']}")
        else:
            print(json.dumps(plan, indent=2))
            
    elif command == "analyze" and len(sys.argv) > 2:
        qap_file = sys.argv[2]
        print(f"\nAnalyzing QAP structure: {qap_file}")
        analysis = framework.analyze_qap_structure(qap_file)
        print(json.dumps(analysis, indent=2))
        
    elif command == "export":
        print("\nExporting jurisdiction mappings...")
        output_file = framework.export_jurisdiction_mappings()
        print(f"Mappings exported to: {output_file}")
        
    elif command == "list":
        print("\nJurisdiction Strategy Assignments:")
        print("=" * 50)
        for mapping in sorted(framework.jurisdiction_mappings, key=lambda x: x.state_code):
            strategy_name = framework.strategies[mapping.strategy].name
            print(f"{mapping.state_code:3s} | {mapping.jurisdiction:20s} | {strategy_name}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()