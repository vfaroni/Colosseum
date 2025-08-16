#!/usr/bin/env python3
"""
ENHANCED Real Regulatory Intelligence Demo - Improved Search & Formatting
Shows actual regulatory connections from California's QAP with better search relevance

Features:
- Direct QAP content search with keyword highlighting
- Improved relevance scoring and ranking
- Better text formatting and presentation
- Structured Consultants LLC branding

Built by Structured Consultants LLC
Roman Engineering Standards: Built to Last 2000+ Years
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import sys
import json
import ollama
import requests
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List, Any, Optional

app = Flask(__name__)

class EnhancedRegulatoryIntelligence:
    """Enhanced regulatory intelligence system with improved search"""
    
    def __init__(self):
        self.ca_regulatory_data = self._load_ca_regulatory_data()
        self.legal_references = self._load_legal_references()
        self.ca_qap_content = self._load_qap_content()
        self.llm_model = "llama3.1:70b"
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Check LLM availability
        self._check_llm_availability()

    def _load_ca_regulatory_data(self) -> Dict[str, Any]:
        """Load actual California regulatory universe data"""
        try:
            data_path = Path(__file__).parent / "ca_regulatory_universe_demo_data.json"
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load CA regulatory data: {e}")
            return {}

    def _load_legal_references(self) -> List[Dict[str, Any]]:
        """Load the actual 92 legal references extracted from CA QAP"""
        if self.ca_regulatory_data:
            return self.ca_regulatory_data.get("legal_references", [])
        return []
    
    def _load_qap_content(self) -> Dict[str, Any]:
        """Load enhanced QAP structure v3.0 with construction standards"""
        try:
            qap_path = Path(__file__).parent / "enhanced_qap_structure_v3.json"
            with open(qap_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load enhanced QAP structure v3.0: {e}")
            # Fallback to old structure if v3.0 not available
            try:
                qap_path = Path(__file__).parent / "enhanced_output" / "enhanced_qap_CA_20250731_170303.json"
                with open(qap_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e2:
                print(f"⚠️ Could not load fallback QAP content: {e2}")
                return {}

    def _check_llm_availability(self):
        """Check which LLM models are available"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [m['name'] for m in models]
                
                if "llama3.1:70b" in available_models:
                    self.llm_model = "llama3.1:70b"
                    print("✅ Using Llama 3.1 70B for regulatory analysis")
                elif "llama3.1:34b" in available_models:
                    self.llm_model = "llama3.1:34b"
                    print("✅ Using Llama 3.1 34B for regulatory analysis")
                else:
                    print("⚠️ No Llama models found - demo will use fallback responses")
                    self.llm_model = None
            else:
                self.llm_model = None
        except Exception as e:
            print(f"⚠️ Could not connect to Ollama: {e}")
            self.llm_model = None

    def search_regulatory_universe(self, query: str, jurisdiction: str = "CA") -> List[Dict[str, Any]]:
        """Enhanced search through QAP content and regulatory references"""
        
        print(f"🔍 Enhanced search for: '{query}' in {jurisdiction}")
        
        # Step 1: Search QAP content directly for most relevant results
        qap_results = self._search_qap_content_enhanced(query)
        
        # Step 2: Search legal references with improved scoring
        ref_results = self._search_legal_references_enhanced(query)
        
        # Step 3: Combine and rank results
        all_results = []
        
        # Add QAP content results (highest priority)
        for qap_result in qap_results[:5]:
            enhanced_ref = self._create_qap_result(qap_result, query)
            all_results.append(enhanced_ref)
        
        # Add legal reference results
        for ref_result in ref_results[:5]:
            enhanced_ref = self._enhance_reference_with_content(ref_result, query)
            all_results.append(enhanced_ref)
        
        return all_results[:10]

    def _search_qap_content_enhanced(self, query: str) -> List[Dict[str, Any]]:
        """Search QAP content for relevant sections using v3.0 structure"""
        
        # Check for v3.0 structure first
        if self.ca_qap_content and 'sections' in self.ca_qap_content:
            return self._search_v3_structure(query)
        # Fallback to old structure
        elif self.ca_qap_content and 'enhanced_chunks' in self.ca_qap_content:
            return self._search_old_structure(query)
        else:
            return []
    
    def _search_v3_structure(self, query: str) -> List[Dict[str, Any]]:
        """Search enhanced QAP structure v3.0"""
        query_lower = query.lower()
        query_terms = [term.strip() for term in query_lower.split() if len(term.strip()) > 2]
        
        matching_sections = []
        
        for section_id, section in self.ca_qap_content['sections'].items():
            content = section.get('complete_content', '').lower()
            title = section.get('title', '').lower()
            citation = section.get('full_citation', '').lower()
            
            relevance_score = 0
            
            # Exact phrase match gets highest score
            if query_lower in content or query_lower in title or query_lower in citation:
                relevance_score += 1000
            
            # Individual term matches
            for term in query_terms:
                if term in content:
                    relevance_score += content.count(term) * 50
                if term in title:
                    relevance_score += title.count(term) * 100
                if term in citation:
                    relevance_score += citation.count(term) * 150
            
            if relevance_score > 0:
                matching_sections.append({
                    'section': section,
                    'section_id': section_id,
                    'relevance_score': relevance_score
                })
        
        # Sort by relevance score
        matching_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        return matching_sections
    
    def _search_old_structure(self, query: str) -> List[Dict[str, Any]]:
        """Search old enhanced chunks structure (fallback)"""
        query_lower = query.lower()
        query_terms = [term.strip() for term in query_lower.split() if len(term.strip()) > 2]
        
        matching_sections = []
        
        for chunk in self.ca_qap_content['enhanced_chunks']:
            content = chunk.get('content', '').lower()
            title = chunk.get('section_title', '').lower()
            
            relevance_score = 0
            
            # Exact phrase match gets highest score
            if query_lower in content or query_lower in title:
                relevance_score += 1000
            
            # Individual term matches
            for term in query_terms:
                if term in content:
                    relevance_score += 100
                if term in title:
                    relevance_score += 200
            
            if relevance_score > 0:
                chunk_copy = chunk.copy()
                chunk_copy['qap_relevance_score'] = relevance_score
                chunk_copy['matching_terms'] = [t for t in query_terms if t in content or t in title]
                matching_sections.append(chunk_copy)
        
        # Sort by relevance
        matching_sections.sort(key=lambda x: x.get('qap_relevance_score', 0), reverse=True)
        return matching_sections

    def _search_legal_references_enhanced(self, query: str) -> List[Dict[str, Any]]:
        """Enhanced search through legal references"""
        
        query_lower = query.lower()
        query_terms = [term.strip() for term in query_lower.split() if len(term.strip()) > 2]
        
        matching_refs = []
        
        for ref in self.legal_references:
            relevance_score = 0
            ref_text = (ref.get('citation_text', '') + ' ' + 
                       ref.get('business_impact', '') + ' ' + 
                       ref.get('category', '') + ' ' +
                       ref.get('section_found', '')).lower()
            
            # Exact phrase match
            if query_lower in ref_text:
                relevance_score += 500
            
            # Individual term matches
            for term in query_terms:
                if term in ref_text:
                    relevance_score += 50
            
            if relevance_score > 0:
                ref_copy = ref.copy()
                ref_copy['ref_relevance_score'] = relevance_score
                ref_copy['matching_terms'] = [t for t in query_terms if t in ref_text]
                matching_refs.append(ref_copy)
        
        matching_refs.sort(key=lambda x: x.get('ref_relevance_score', 0), reverse=True)
        return matching_refs

    def _create_qap_result(self, qap_result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Create search result from QAP content (supports both v3.0 and old structures)"""
        
        # Handle v3.0 structure
        if 'section' in qap_result:
            section = qap_result['section']
            section_id = qap_result.get('section_id', '')
            
            section_title = section.get('title', '')
            content = section.get('complete_content', '')
            citation = section.get('full_citation', section_title)
            verification_id = section.get('verification_id', '')
            
            return {
                "reference_id": verification_id or f"QAP_{section_id}",
                "citation_text": citation,
                "authority_level": 30,
                "jurisdiction": "California QAP",
                "category": "QAP Section",
                "section_found": citation,
                "business_impact": "Direct QAP requirement - affects project eligibility and scoring",
                "qap_section_content": content,
                "content_preview": self._create_highlighted_preview(content, query),
                "section_title": section_title,
                "verification_available": bool(verification_id),
                "relevance_score": qap_result.get('relevance_score', 0) / 1000,
                "result_type": "qap_direct",
                "matching_terms": [],
                "federal_refs_in_section": [],
                "state_refs_in_section": [],
                "page_references": f"Pages {section.get('page_start', '')}-{section.get('page_end', '')}" if section.get('page_start') else "",
                "pdf_link": f"/pdf/{section.get('pdf_source', 'CA_2025_QAP_section_01_pages_001-095.pdf')}#page={section.get('page_start', 66)}",
                "pdf_filename": section.get('pdf_source', '')
            }
        
        # Handle old structure (fallback)
        else:
            section_title = qap_result.get('section_title', '')
            content = qap_result.get('content', '')
            
            # Extract section number for citation
            section_match = re.search(r'§?(\d{5})', section_title)
            section_num = section_match.group(1) if section_match else "QAP"
            
            return {
                "reference_id": f"QAP_SECTION_{section_num}",
                "citation_text": f"California QAP {section_title}",
                "authority_level": 30,
                "jurisdiction": "California QAP",
                "category": "QAP Section",
                "section_found": section_title,
                "business_impact": "Direct QAP requirement - affects project eligibility and scoring",
                "qap_section_content": content,
                "content_preview": self._create_highlighted_preview(content, query),
                "section_title": section_title,
                "verification_available": True,
                "relevance_score": qap_result.get('qap_relevance_score', 0) / 1000,
                "result_type": "qap_direct",
                "matching_terms": qap_result.get('matching_terms', []),
                "federal_refs_in_section": qap_result.get('federal_refs', []),
                "state_refs_in_section": qap_result.get('state_refs', [])
            }

    def _enhance_reference_with_content(self, reference: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Enhance legal reference with content and highlighting"""
        
        enhanced = reference.copy()
        section_found = reference.get('section_found', '')
        
        # Find matching QAP section content
        qap_content = self._find_qap_section_content(section_found)
        
        if qap_content:
            enhanced.update({
                "qap_section_content": qap_content.get("content", ""),
                "section_title": qap_content.get("section_title", ""),
                "content_preview": self._create_highlighted_preview(qap_content.get("content", ""), query),
                "federal_refs_in_section": qap_content.get("federal_refs", []),
                "state_refs_in_section": qap_content.get("state_refs", []),
                "verification_available": True
            })
        else:
            enhanced.update({
                "content_preview": self._create_mock_highlighted_content(reference, query),
                "verification_available": False
            })
        
        # Add highlighting and relevance
        enhanced["relevance_score"] = reference.get('ref_relevance_score', 0) / 500
        enhanced["matching_terms"] = reference.get('matching_terms', [])
        enhanced["result_type"] = "legal_reference"
        
        return enhanced

    def _create_highlighted_preview(self, content: str, query: str) -> str:
        """Create preview with keyword highlighting"""
        
        if not content:
            return "Content not available"
        
        # Clean up content
        cleaned = re.sub(r'\s+', ' ', content.strip())
        
        # Find the best excerpt containing query terms
        query_terms = [term.strip() for term in query.lower().split() if len(term.strip()) > 2]
        
        best_excerpt = ""
        best_score = 0
        
        # Try different excerpt positions
        words = cleaned.split()
        for i in range(0, max(1, len(words) - 50), 10):
            excerpt_words = words[i:i + 50]
            excerpt = " ".join(excerpt_words)
            excerpt_lower = excerpt.lower()
            
            score = sum(1 for term in query_terms if term in excerpt_lower)
            if score > best_score:
                best_score = score
                best_excerpt = excerpt
        
        if not best_excerpt:
            best_excerpt = " ".join(words[:50])
        
        # Add highlighting
        highlighted = self._highlight_terms(best_excerpt, query_terms)
        
        if len(" ".join(words)) > 50:
            highlighted += "..."
        
        return highlighted

    def _highlight_terms(self, text: str, terms: List[str]) -> str:
        """Add HTML highlighting to search terms"""
        
        highlighted = text
        for term in terms:
            # Case-insensitive replacement with highlighting
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            highlighted = pattern.sub(f'<mark style="background-color: yellow; font-weight: bold;">{term}</mark>', highlighted)
        
        return highlighted

    def _create_mock_highlighted_content(self, reference: Dict[str, Any], query: str) -> str:
        """Create mock content with highlighting when actual content unavailable"""
        
        citation = reference.get('citation_text', '')
        authority = reference.get('authority_level', 0)
        query_terms = [term.strip() for term in query.lower().split() if len(term.strip()) > 2]
        
        if authority >= 100:  # Federal IRC
            content = f"Federal statutory authority: {citation} establishes requirements for qualified basis calculation, income restrictions, and compliance monitoring for LIHTC properties..."
        elif authority >= 80:  # Federal CFR
            content = f"Federal regulatory implementation: {citation} provides detailed procedures for income certification, rent calculations, and compliance reporting requirements..."
        else:  # State/QAP
            content = f"State implementation: {citation} specifies California-specific requirements for project selection, monitoring, and state tax credit coordination..."
        
        return self._highlight_terms(content, query_terms)

    def _find_qap_section_content(self, section_ref: str) -> Optional[Dict[str, Any]]:
        """Find actual QAP section content by section reference"""
        
        if not self.ca_qap_content or 'enhanced_chunks' not in self.ca_qap_content:
            return None
        
        # Extract section number from reference
        section_match = re.search(r'§?(\d{5})', section_ref)
        if not section_match:
            return None
        
        section_num = section_match.group(1)
        
        # Find matching chunk in QAP content
        for chunk in self.ca_qap_content['enhanced_chunks']:
            chunk_title = chunk.get('section_title', '')
            if section_num in chunk_title or f"§{section_num}" in chunk_title:
                return chunk
        
        return None

    def get_hub_spoke_analysis(self, jurisdiction: str = "CA") -> Dict[str, Any]:
        """Get real hub-and-spoke analysis for jurisdiction"""
        
        if not self.legal_references:
            return {"error": "No regulatory data available"}
        
        # Analyze actual reference distribution
        federal_refs = [r for r in self.legal_references if r.get('jurisdiction') == 'Federal']
        state_refs = [r for r in self.legal_references if r.get('jurisdiction') == 'California']
        internal_refs = [r for r in self.legal_references if r.get('jurisdiction') == 'QAP Internal']
        
        # Calculate real hub-to-spoke ratio
        spoke_refs = len(federal_refs) + len(state_refs)
        hub_refs = len(internal_refs)
        ratio = spoke_refs / hub_refs if hub_refs > 0 else 0
        
        return {
            "jurisdiction": jurisdiction,
            "total_references": len(self.legal_references),
            "hub_references": hub_refs,
            "spoke_references": spoke_refs,
            "ratio": f"{ratio:.1f}:1",
            "federal_authority": len(federal_refs),
            "state_authority": len(state_refs),
            "actual_qap_sections": len(self.ca_qap_content.get('enhanced_chunks', [])) if self.ca_qap_content else 0,
        }

    def get_authority_hierarchy_demo(self) -> Dict[str, Any]:
        """Show real authority hierarchy with actual references"""
        
        hierarchy_analysis = {}
        
        # Group references by authority level
        for ref in self.legal_references:
            level = ref.get('authority_level', 30)
            if level not in hierarchy_analysis:
                hierarchy_analysis[level] = []
            hierarchy_analysis[level].append(ref)
        
        # Create hierarchy display
        hierarchy_levels = []
        authority_names = {
            100: "Federal IRC/Public Law",
            80: "Federal CFR", 
            60: "Federal Guidance",
            30: "State QAP/Statutes"
        }
        
        for level in sorted(hierarchy_analysis.keys(), reverse=True):
            refs = hierarchy_analysis[level]
            hierarchy_levels.append({
                "level": level,
                "name": authority_names.get(level, f"Authority Level {level}"),
                "count": len(refs),
                "description": self._get_authority_description(level),
                "examples": [r.get('citation_text', '') for r in refs[:3]]
            })
        
        return {
            "hierarchy_levels": hierarchy_levels,
            "total_references": len(self.legal_references),
            "federal_precedence": "Federal regulations (100-80) override state (30-20)",
            "authority_explanation": "Higher numbers = higher authority = override lower authority"
        }

    def _get_authority_description(self, level: int) -> str:
        """Get description for authority level"""
        descriptions = {
            100: "Statutory law - overrides all state interpretations and regulations",
            80: "Federal regulations - override state regulations but must comply with statutes",
            60: "Federal guidance - minimum standards that states must meet or exceed",
            30: "State implementation - must comply with all federal requirements",
            20: "Local implementation - must comply with state and federal requirements"
        }
        return descriptions.get(level, "Regulatory authority")


# Global intelligence system
intelligence = EnhancedRegulatoryIntelligence()

@app.route('/')
def index():
    """Main demo page"""
    return render_template('enhanced_regulatory_demo.html')

@app.route('/api/search')
def api_search():
    """Enhanced regulatory universe search API"""
    query = request.args.get('query', '')
    jurisdiction = request.args.get('jurisdiction', 'CA')
    
    if not query:
        return jsonify({"error": "Query parameter required"}), 400
    
    print(f"🔍 Processing enhanced search: '{query}' in {jurisdiction}")
    
    results = intelligence.search_regulatory_universe(query, jurisdiction)
    
    # Add verification statistics  
    content_available = sum(1 for r in results if r.get('verification_available', False))
    qap_direct = sum(1 for r in results if r.get('result_type') == 'qap_direct')
    
    return jsonify({
        "query": query,
        "jurisdiction": jurisdiction,
        "results_count": len(results),
        "results": results,
        "verification_stats": {
            "results_with_content": content_available,
            "qap_direct_results": qap_direct,
            "results_total": len(results),
            "content_coverage": f"{min(100, (content_available/len(results)*100) if results else 0):.1f}%"
        },
        "timestamp": datetime.now().isoformat(),
        "llm_model": intelligence.llm_model or "fallback"
    })

@app.route('/api/hub_spoke_analysis')
def api_hub_spoke():
    """Real hub-and-spoke analysis API"""
    jurisdiction = request.args.get('jurisdiction', 'CA')
    analysis = intelligence.get_hub_spoke_analysis(jurisdiction)
    return jsonify(analysis)

@app.route('/api/authority_hierarchy')
def api_authority_hierarchy():
    """Real authority hierarchy API"""
    return jsonify(intelligence.get_authority_hierarchy_demo())

@app.route('/api/regulatory_stats')
def api_regulatory_stats():
    """Get real regulatory statistics"""
    return jsonify({
        "total_references": len(intelligence.legal_references),
        "qap_sections_with_content": len(intelligence.ca_qap_content.get('enhanced_chunks', [])) if intelligence.ca_qap_content else 0,
        "data_source": "California 2025 QAP - Real extracted references with full text",
        "extraction_date": intelligence.ca_regulatory_data.get("metadata", {}).get("extraction_date", ""),
        "llm_model": intelligence.llm_model or "fallback mode",
        "universe_stats": intelligence.ca_regulatory_data.get("regulatory_universe", {}),
        "content_verification": {
            "qap_pages_processed": intelligence.ca_qap_content.get('docling_metadata', {}).get('pages_processed', 0),
            "text_length": intelligence.ca_qap_content.get('docling_metadata', {}).get('text_length', 0),
            "extraction_method": intelligence.ca_qap_content.get('docling_metadata', {}).get('extraction_method', "unknown")
        }
    })

@app.route('/api/verify_content/<reference_id>')
def api_verify_content(reference_id):
    """Verify actual regulatory content by reference ID (supports v3.0 structure)"""
    
    # First check QAP v3.0 verification system
    if intelligence.ca_qap_content and 'verification_system' in intelligence.ca_qap_content:
        verification_info = intelligence.ca_qap_content['verification_system'].get(reference_id)
        if verification_info:
            # Find the corresponding section
            section_id = verification_info.get('reference_id')
            section = intelligence.ca_qap_content['sections'].get(section_id, {})
            
            return jsonify({
                "reference_id": reference_id,
                "citation": verification_info.get('modal_title', ''),
                "section_found": verification_info.get('modal_title', ''),
                "verification_available": True,
                "section_title": section.get('title', ''),
                "content_preview": section.get('complete_content', '')[:500] + "..." if len(section.get('complete_content', '')) > 500 else section.get('complete_content', ''),
                "full_content": section.get('complete_content', ''),
                "page_references": verification_info.get('page_references', ''),
                "hierarchy_path": " → ".join(section.get('hierarchy_path', [])),
                "content_length": len(section.get('complete_content', '')),
                "verification_timestamp": datetime.now().isoformat(),
                "structure_version": "v3.0",
                "pdf_link": f"/pdf/CA_2025_QAP_section_01_pages_001-095.pdf#page={section.get('page_start', 66)}",
                "pdf_filename": section.get('pdf_source', '')
            })
    
    # Fallback to old system
    ref = next((r for r in intelligence.legal_references if r.get('reference_id') == reference_id), None)
    if not ref:
        return jsonify({"error": "Reference not found"}), 404
    
    # Get actual content
    enhanced_ref = intelligence._enhance_reference_with_content(ref, "")
    
    return jsonify({
        "reference_id": reference_id,
        "citation": ref.get('citation_text', ''),
        "section_found": ref.get('section_found', ''),
        "verification_available": enhanced_ref.get('verification_available', False),
        "section_title": enhanced_ref.get('section_title', ''),
        "content_preview": enhanced_ref.get('content_preview', ''),
        "full_content": enhanced_ref.get('qap_section_content', ''),
        "federal_refs_in_section": enhanced_ref.get('federal_refs_in_section', []),
        "state_refs_in_section": enhanced_ref.get('state_refs_in_section', []),
        "content_length": len(enhanced_ref.get('qap_section_content', '')),
        "verification_timestamp": datetime.now().isoformat(),
        "structure_version": "legacy"
    })

@app.route('/pdf/<filename>')
def serve_pdf(filename):
    """Serve PDF files from test_split directory"""
    pdf_directory = Path(__file__).parent / "test_split"
    try:
        return send_from_directory(pdf_directory, filename)
    except FileNotFoundError:
        return jsonify({"error": "PDF not found"}), 404

def launch_enhanced_demo():
    """Launch the enhanced regulatory intelligence demo"""
    
    print("🏛️ ENHANCED REGULATORY INTELLIGENCE DEMO")
    print("="*55)
    print("🎯 IMPROVED: Direct QAP content search with highlighting")
    print("🔍 IMPROVED: Better relevance scoring and ranking")  
    print("💼 BUILT BY: Structured Consultants LLC")
    print("⚖️ Actual authority hierarchy (Federal > State)")
    print("🗺️ True hub-and-spoke model with real data")
    print("="*55)
    
    if intelligence.llm_model:
        print(f"✅ LLM: {intelligence.llm_model}")
    else:
        print("⚠️ LLM: Fallback mode (Ollama not available)")
    
    print(f"📊 Loaded {len(intelligence.legal_references)} real regulatory references")
    print(f"📄 Loaded {len(intelligence.ca_qap_content.get('enhanced_chunks', []))} QAP sections with full text")
    print()
    
    # Launch Flask app
    import threading
    import time
    import webbrowser
    
    def run_flask():
        app.run(host='127.0.0.1', port=5003, debug=False)
    
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Wait and open browser
    time.sleep(2)
    demo_url = "http://127.0.0.1:5003"
    print(f"🌐 Enhanced Demo URL: {demo_url}")
    
    try:
        webbrowser.open(demo_url)
        print("🚀 Enhanced Regulatory Intelligence Demo is running!")
    except:
        print("📱 Please open the URL manually in your browser")
    
    print("\n💡 Try searching for:")
    print("   • 'minimum construction standards' - See actual QAP requirements")
    print("   • 'income limits' - Find IRC Section 42 connections")
    print("   • 'qualified basis' - Federal vs state requirements")
    print("   • 'compliance monitoring' - Authority hierarchy")
    print("\nPress Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Enhanced demo stopped")

if __name__ == "__main__":
    launch_enhanced_demo()