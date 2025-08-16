#!/usr/bin/env python3
"""
Integration tests for QAP RAG Emergency Reconstruction Framework
Tests all major components for TOWER compliance

Built by Structured Consultants LLC
Roman Engineering Standards: Built to Last 2000+ Years
"""

import unittest
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from claude_opus_4strategy_implementation import ClaudeOpus4StrategyFramework, ChunkingStrategy
from quality_assurance_framework import QualityAssuranceFramework, ContentCategory
from docling_4strategy_integration import DoclingStrategyIntegration

class TestQAPFrameworkIntegration(unittest.TestCase):
    """Integration tests for QAP reconstruction framework"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.strategy_framework = ClaudeOpus4StrategyFramework()
        self.quality_framework = QualityAssuranceFramework()
        self.integration = DoclingStrategyIntegration()
    
    def test_strategy_framework_initialization(self):
        """Test Claude Opus 4-strategy framework initialization"""
        # Test framework has all 4 strategies
        self.assertEqual(len(self.strategy_framework.strategies), 4)
        
        # Test all strategy types are present
        expected_strategies = {
            ChunkingStrategy.COMPLEX_OUTLINE,
            ChunkingStrategy.MEDIUM_COMPLEXITY, 
            ChunkingStrategy.SIMPLE_NARRATIVE,
            ChunkingStrategy.TABLE_MATRIX
        }
        self.assertEqual(set(self.strategy_framework.strategies.keys()), expected_strategies)
        
        # Test jurisdiction mappings exist
        self.assertGreater(len(self.strategy_framework.jurisdiction_mappings), 50)
    
    def test_california_strategy_assignment(self):
        """Test California gets Complex Outline strategy (critical test case)"""
        ca_mapping = self.strategy_framework.get_strategy_for_jurisdiction("CA")
        
        self.assertIsNotNone(ca_mapping)
        self.assertEqual(ca_mapping.state_code, "CA")
        self.assertEqual(ca_mapping.strategy, ChunkingStrategy.COMPLEX_OUTLINE)
        self.assertGreaterEqual(ca_mapping.complexity_score, 0.8)  # High complexity
    
    def test_chunking_plan_generation(self):
        """Test chunking plan generation for California"""
        plan = self.strategy_framework.create_chunking_plan("CA")
        
        self.assertNotIn("error", plan)
        self.assertEqual(plan["jurisdiction"], "CA")
        self.assertEqual(plan["strategy"]["type"], "complex_outline")
        self.assertIn("token_range", plan["chunking_parameters"])
        self.assertIn("completeness_threshold", plan["quality_requirements"])
        self.assertEqual(plan["quality_requirements"]["completeness_threshold"], 0.95)
    
    def test_quality_framework_initialization(self):
        """Test quality assurance framework initialization"""
        # Test D'Marco standards applied
        self.assertEqual(self.quality_framework.completeness_threshold, 0.95)
        self.assertEqual(self.quality_framework.expert_validation_threshold, 0.90)
        
        # Test validation criteria exist
        self.assertIn(ContentCategory.CONSTRUCTION_STANDARDS, self.quality_framework.validation_criteria)
        self.assertIn(ContentCategory.SCORING_CRITERIA, self.quality_framework.validation_criteria)
    
    def test_construction_standards_validator(self):
        """Test construction standards content validation"""
        # Good content example
        good_content = """
        Minimum construction standards require all projects to meet or exceed local building codes,
        demonstrate ADA compliance and fair housing accessibility requirements, implement green building
        standards including energy efficiency specifications, and provide comprehensive construction cost
        documentation including hard costs and soft costs limitations.
        """
        
        validator = self.quality_framework.validators[ContentCategory.CONSTRUCTION_STANDARDS]
        criteria = self.quality_framework.validation_criteria[ContentCategory.CONSTRUCTION_STANDARDS]
        
        result = validator.validate_content(good_content, criteria)
        
        self.assertIn("validation_passed", result)
        self.assertIn("score", result)
        self.assertIn("keyword_coverage", result)
        self.assertGreater(result["keyword_coverage"], 0.5)  # Should find multiple keywords
    
    def test_integration_pdf_loading(self):
        """Test integration system loads PDF database"""
        # Test readable PDFs loaded
        self.assertGreater(len(self.integration.readable_pdfs), 50)
        
        # Test California PDFs available
        self.assertIn("CA", self.integration.readable_pdfs)
        ca_pdfs = self.integration.readable_pdfs["CA"]
        self.assertGreater(len(ca_pdfs), 0)
    
    def test_minimum_construction_test_framework(self):
        """Test minimum construction standards test framework"""
        # Test data with good and bad content
        test_data = {
            "CA": {
                "construction_standards": "Comprehensive minimum construction standards including building code requirements, accessibility compliance (ADA), fair housing standards...",
                "scoring_criteria": "Complete scoring criteria..."
            },
            "TX": {
                "construction_standards": "Hard construction costs",  # Bad - fragment
                "scoring_criteria": "Some scoring..."
            }
        }
        
        results = self.quality_framework.run_minimum_construction_standards_test(test_data)
        
        self.assertIn("test_name", results)
        self.assertIn("success_rate", results)
        self.assertIn("detailed_results", results)
        self.assertEqual(len(results["detailed_results"]), 2)
    
    def test_strategy_distribution(self):
        """Test 4-strategy distribution matches research (approximately)"""
        strategy_counts = {}
        for mapping in self.strategy_framework.jurisdiction_mappings:
            strategy = mapping.strategy
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        total = len(self.strategy_framework.jurisdiction_mappings)
        
        # Test Complex Outline is largest group (should be ~40%)
        complex_pct = strategy_counts.get(ChunkingStrategy.COMPLEX_OUTLINE, 0) / total
        self.assertGreater(complex_pct, 0.30)  # At least 30%
        
        # Test Table/Matrix is smallest group (should be ~5%)
        table_pct = strategy_counts.get(ChunkingStrategy.TABLE_MATRIX, 0) / total
        self.assertLess(table_pct, 0.15)  # Less than 15%
    
    def test_report_generation(self):
        """Test framework can generate reports"""
        # Test strategy report
        strategy_report = self.strategy_framework.generate_implementation_report()
        self.assertIn("CLAUDE OPUS 4-STRATEGY IMPLEMENTATION REPORT", strategy_report)
        self.assertIn("57", strategy_report)  # Should mention total jurisdictions
        
        # Test quality dashboard (empty state)
        quality_dashboard = self.quality_framework.generate_quality_dashboard()
        self.assertIn("quality metrics", quality_dashboard.lower())
    
    def test_export_functionality(self):
        """Test frameworks can export data"""
        # Test strategy export
        strategy_file = self.strategy_framework.export_jurisdiction_mappings()
        self.assertTrue(Path(strategy_file).exists())
        
        # Test quality export (even if no data)
        quality_file = self.quality_framework.export_quality_report()
        self.assertTrue(Path(quality_file).exists())
    
    def test_ca_2025_qap_ready(self):
        """Test framework is ready for CA 2025 QAP processing"""
        # Test CA strategy is appropriate for complex QAP
        ca_mapping = self.strategy_framework.get_strategy_for_jurisdiction("CA")
        self.assertEqual(ca_mapping.strategy, ChunkingStrategy.COMPLEX_OUTLINE)
        
        # Test CA chunking plan has appropriate parameters
        ca_plan = self.strategy_framework.create_chunking_plan("CA")
        token_range = ca_plan["chunking_parameters"]["token_range"]
        self.assertEqual(list(token_range), [800, 1500])  # Complex outline range
        self.assertEqual(ca_plan["chunking_parameters"]["max_nesting_levels"], 7)
        
        # Test quality requirements are comprehensive
        required_sections = ca_plan["quality_requirements"]["required_sections"]
        self.assertIn("construction_standards", required_sections)
        self.assertIn("minimum_construction_requirements", required_sections)
        self.assertIn("scoring_criteria", required_sections)

class TestRomanEngineeringCompliance(unittest.TestCase):
    """Test compliance with Roman Engineering Standards"""
    
    def test_qualitas_perpetua_standard(self):
        """Test 'Quality Endures' principle implementation"""
        framework = ClaudeOpus4StrategyFramework()
        
        # Test systematic excellence - all jurisdictions mapped
        self.assertEqual(len(framework.jurisdiction_mappings), 57)  # All US jurisdictions
        
        # Test redundant verification - multiple validation levels
        quality_framework = QualityAssuranceFramework()
        self.assertEqual(quality_framework.completeness_threshold, 0.95)  # High standards
        
        # Test professional validation - expert validation required
        self.assertEqual(quality_framework.expert_validation_threshold, 0.90)
    
    def test_system_reliability_2000_years(self):
        """Test system built for 2000+ year reliability"""
        # Test error handling and graceful degradation
        framework = ClaudeOpus4StrategyFramework()
        
        # Test invalid jurisdiction handling
        invalid_mapping = framework.get_strategy_for_jurisdiction("INVALID")
        self.assertIsNone(invalid_mapping)
        
        # Test invalid plan generation
        invalid_plan = framework.create_chunking_plan("INVALID")
        self.assertIn("error", invalid_plan)
    
    def test_documentation_completeness(self):
        """Test comprehensive documentation exists"""
        # Test all framework files have docstrings
        import claude_opus_4strategy_implementation
        import quality_assurance_framework
        import docling_4strategy_integration
        
        self.assertIsNotNone(claude_opus_4strategy_implementation.__doc__)
        self.assertIsNotNone(quality_assurance_framework.__doc__)
        self.assertIsNotNone(docling_4strategy_integration.__doc__)

def run_tower_compliance_tests():
    """Run all tests for TOWER compliance"""
    print("🏛️ TOWER COMPLIANCE TESTING - QAP RAG Reconstruction Framework")
    print("=" * 70)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add framework tests
    suite.addTest(unittest.makeSuite(TestQAPFrameworkIntegration))
    suite.addTest(unittest.makeSuite(TestRomanEngineeringCompliance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    if result.wasSuccessful():
        print("\n✅ TOWER COMPLIANCE: ALL TESTS PASSED")
        print("🏛️ Roman Engineering Standards: SATISFIED")
        print("🚀 Framework ready for CA 2025 QAP deployment")
        return True
    else:
        print(f"\n❌ TOWER COMPLIANCE: {len(result.failures + result.errors)} TESTS FAILED")
        print("🚨 Framework requires fixes before deployment")
        return False

if __name__ == "__main__":
    success = run_tower_compliance_tests()
    sys.exit(0 if success else 1)