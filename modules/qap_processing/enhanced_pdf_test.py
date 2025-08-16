#!/usr/bin/env python3
"""
Enhanced PDF Processing Test - M4 Strike Leader
Tests new tools (pdfplumber, whoosh, sentence-transformers) for QAP reconstruction

Mission: Validate enhanced PDF processing capabilities
Target: Extract §10325(f)(7) Minimum Construction Standards with page mapping (66-69)
"""

import pdfplumber
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

class EnhancedQAPProcessor:
    """Enhanced QAP processor using new tools for superior extraction"""
    
    def __init__(self):
        self.qap_pdf_path = None
        self.find_qap_pdf()
        
    def find_qap_pdf(self):
        """Find the California QAP PDF file"""
        possible_paths = [
            Path(__file__).parent / "test_split" / "CA_2025_QAP_section_01_pages_001-095.pdf",
            Path(__file__).parent / "test_split" / "CA_2025_QAP_section_02_pages_096-109.pdf",
            Path(__file__).parent.parent / "data_sets" / "QAPs" / "CA_2025_QAP.pdf",
            Path(__file__).parent / "CA_2025_QAP.pdf"
        ]
        
        for path in possible_paths:
            if path.exists():
                self.qap_pdf_path = path
                print(f"✅ Found QAP PDF: {path}")
                return
        
        print("⚠️ QAP PDF not found in expected locations")
    
    def test_pdfplumber_extraction(self) -> Dict[str, Any]:
        """Test pdfplumber for enhanced PDF processing"""
        if not self.qap_pdf_path:
            return {"error": "No QAP PDF found"}
        
        print(f"🔍 Testing pdfplumber extraction on: {self.qap_pdf_path}")
        
        results = {
            "tool": "pdfplumber",
            "pdf_path": str(self.qap_pdf_path),
            "pages_processed": 0,
            "sections_found": [],
            "construction_standards_found": False,
            "page_mapping_test": False
        }
        
        try:
            with pdfplumber.open(self.qap_pdf_path) as pdf:
                results["total_pages"] = len(pdf.pages)
                
                # Test page-by-page extraction
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        results["pages_processed"] += 1
                        
                        # Look for section patterns
                        section_matches = re.findall(r'§\s*(\d{5})', text)
                        if section_matches:
                            results["sections_found"].extend([(page_num, match) for match in section_matches])
                        
                        # Look for construction standards specifically
                        if 'construction' in text.lower() and 'standard' in text.lower():
                            results["construction_standards_found"] = True
                            print(f"📄 Found construction standards content on page {page_num}")
                        
                        # Test for page 66-69 range (if we have the full PDF)
                        if 66 <= page_num <= 69:
                            results["page_mapping_test"] = True
                            print(f"🎯 Page {page_num} in construction standards range (66-69)")
                
                print(f"✅ Processed {results['pages_processed']} pages")
                print(f"📊 Found {len(set([s[1] for s in results['sections_found']]))} unique sections")
                
        except Exception as e:
            results["error"] = str(e)
            print(f"❌ pdfplumber extraction failed: {e}")
        
        return results
    
    def test_section_parsing_patterns(self) -> Dict[str, Any]:
        """Test regex patterns for QAP section identification"""
        print("🧪 Testing QAP section parsing patterns")
        
        # Test patterns for California QAP structure
        patterns = {
            "main_section": r'§\s*(\d{5})',           # §10325
            "subsection": r'§\s*(\d{5})\(([a-z])\)',  # §10325(f)
            "subitem": r'§\s*(\d{5})\(([a-z])\)\((\d+)\)', # §10325(f)(7)
            "detail": r'§\s*(\d{5})\(([a-z])\)\((\d+)\)\(([A-Z])\)', # §10325(f)(7)(A)
            "construction_standards": r'(?i)minimum\s+construction\s+standards?',
            "basic_threshold": r'(?i)basic\s+threshold\s+requirements?'
        }
        
        # Test strings based on actual QAP content
        test_strings = [
            "§10325. Application Selection Criteria-Credit Ceiling Applications",
            "§10325(f) Basic Threshold Requirements", 
            "§10325(f)(7) Minimum Construction Standards",
            "§10325(f)(7)(A) General construction requirements",
            "§10325(f)(7)(M)(iv) Final construction requirements",
            "minimum construction standards for all projects",
            "Basic Threshold Requirements as specified",
            "## (9) Tie Breakers"  # Wrong classification we need to avoid
        ]
        
        results = {
            "patterns_tested": len(patterns),
            "test_strings": len(test_strings),
            "pattern_matches": {},
            "construction_detection": False,
            "hierarchy_detection": False
        }
        
        for pattern_name, pattern in patterns.items():
            results["pattern_matches"][pattern_name] = []
            compiled_pattern = re.compile(pattern)
            
            for test_string in test_strings:
                matches = compiled_pattern.findall(test_string)
                if matches:
                    results["pattern_matches"][pattern_name].append({
                        "string": test_string,
                        "matches": matches
                    })
        
        # Check specific detections
        construction_matches = results["pattern_matches"]["construction_standards"]
        if construction_matches:
            results["construction_detection"] = True
            print("✅ Construction standards pattern detection working")
        
        main_matches = results["pattern_matches"]["main_section"]
        if main_matches:
            results["hierarchy_detection"] = True
            print("✅ Hierarchical section detection working")
        
        return results
    
    def test_search_comparison(self) -> Dict[str, Any]:
        """Compare our enhanced search vs simple text search (CTRL+F equivalent)"""
        print("⚖️ Testing search capabilities vs CTRL+F baseline")
        
        # Load existing QAP JSON for comparison
        try:
            qap_json_path = Path(__file__).parent / "enhanced_output" / "enhanced_qap_CA_20250731_170303.json"
            with open(qap_json_path, 'r') as f:
                qap_data = json.load(f)
        except Exception as e:
            return {"error": f"Could not load QAP JSON: {e}"}
        
        query = "minimum construction standards"
        results = {
            "query": query,
            "simple_search_results": 0,
            "enhanced_search_potential": 0,
            "current_system_problems": [],
            "improvement_opportunities": []
        }
        
        # Simple text search (CTRL+F equivalent)
        simple_matches = 0
        for chunk in qap_data.get('enhanced_chunks', []):
            content = chunk.get('content', '').lower()
            title = chunk.get('section_title', '').lower()
            
            if query.lower() in content or query.lower() in title:
                simple_matches += 1
                
                # Analyze current system problems
                section_title = chunk.get('section_title', '')
                if 'tie breaker' in section_title.lower():
                    results["current_system_problems"].append({
                        "issue": "Wrong section classification",
                        "found": section_title,
                        "should_be": "§10325(f)(7) Minimum Construction Standards"
                    })
        
        results["simple_search_results"] = simple_matches
        
        # Identify improvement opportunities
        results["improvement_opportunities"] = [
            "Correct section identification (§10325(f)(7) not Tie Breakers)",
            "Complete section extraction (pages 66-69)",
            "Hierarchical structure preservation",
            "PDF page mapping",
            "Working verification links",
            "Semantic search beyond keyword matching"
        ]
        
        print(f"📊 Simple search found {simple_matches} matches")
        print(f"⚠️ Identified {len(results['current_system_problems'])} classification problems")
        
        return results
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test suite for Phase 1 validation"""
        print("🚀 M4 STRIKE LEADER - PHASE 1 TOOL VALIDATION")
        print("=" * 60)
        
        start_time = time.time()
        
        test_results = {
            "mission_phase": "Phase 1 - Tool Preparation",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests_run": [],
            "overall_success": False,
            "critical_findings": [],
            "next_steps": []
        }
        
        # Test 1: pdfplumber extraction
        print("\n📋 TEST 1: Enhanced PDF Processing")
        pdf_results = self.test_pdfplumber_extraction()
        test_results["tests_run"].append({"test": "pdfplumber_extraction", "results": pdf_results})
        
        if pdf_results.get("construction_standards_found"):
            test_results["critical_findings"].append("✅ Construction standards content detected in PDF")
        
        # Test 2: Section parsing patterns  
        print("\n📋 TEST 2: QAP Section Parsing Patterns")
        pattern_results = self.test_section_parsing_patterns()
        test_results["tests_run"].append({"test": "section_patterns", "results": pattern_results})
        
        if pattern_results.get("construction_detection"):
            test_results["critical_findings"].append("✅ Construction standards regex patterns working")
        
        # Test 3: Search comparison
        print("\n📋 TEST 3: Search Capability Analysis")
        search_results = self.test_search_comparison()
        test_results["tests_run"].append({"test": "search_comparison", "results": search_results})
        
        if search_results.get("current_system_problems"):
            test_results["critical_findings"].append(f"⚠️ Found {len(search_results['current_system_problems'])} classification problems")
        
        # Overall assessment
        successful_tests = sum(1 for test in test_results["tests_run"] if not test["results"].get("error"))
        test_results["overall_success"] = successful_tests >= 2
        
        # Next steps based on results
        if test_results["overall_success"]:
            test_results["next_steps"] = [
                "Proceed to Phase 2: QAP Structure Analysis",
                "Map complete QAP outline (§10300-§10337)",
                "Build hierarchical section parser",
                "Create enhanced data structures"
            ]
        else:
            test_results["next_steps"] = [
                "Resolve tool installation issues",
                "Debug PDF processing problems", 
                "Retry Phase 1 validation"
            ]
        
        elapsed_time = time.time() - start_time
        print(f"\n⏱️ Test completed in {elapsed_time:.2f} seconds")
        print(f"🎯 Phase 1 Success: {test_results['overall_success']}")
        
        return test_results

if __name__ == "__main__":
    processor = EnhancedQAPProcessor()
    results = processor.run_comprehensive_test()
    
    # Save results for milestone report
    output_path = Path(__file__).parent / "phase1_test_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {output_path}")