#!/usr/bin/env python3
"""
REAL Regulatory Intelligence Demo - Open LLM Integration
Shows actual regulatory connections from California's 316 legal references

Features:
- Real search through actual regulatory data
- Llama 70B/34B analysis of regulatory connections  
- Actual hub-and-spoke visualization with real data
- Authority hierarchy analysis with federal vs state precedence
- Interactive display of QAP sections referencing federal codes

Built by Structured Consultants LLC
Roman Engineering Standards: Built to Last 2000+ Years
"""

from flask import Flask, render_template, request, jsonify
import sys
import json
import ollama
import requests
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List, Any, Optional

app = Flask(__name__)

class RealRegulatoryIntelligence:
    """Real regulatory intelligence system with open LLM integration"""
    
    def __init__(self):
        self.ca_regulatory_data = self._load_ca_regulatory_data()
        self.legal_references = self._load_legal_references()
        self.ca_qap_content = self._load_qap_content()
        self.llm_model = "llama3.1:70b"  # Default to 70B, fallback to 34B if needed
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
        """Load actual QAP content with full text"""
        try:
            qap_path = Path(__file__).parent / "enhanced_output" / "enhanced_qap_CA_20250731_170303.json"
            with open(qap_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load QAP content: {e}")
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
                elif "llama3.1" in available_models:
                    self.llm_model = "llama3.1"
                    print("✅ Using Llama 3.1 for regulatory analysis")
                else:
                    print("⚠️ No Llama models found - demo will use fallback responses")
                    self.llm_model = None
            else:
                print("⚠️ Ollama not responding - demo will use fallback responses")
                self.llm_model = None
        except Exception as e:
            print(f"⚠️ Could not connect to Ollama: {e}")
            self.llm_model = None

    def search_regulatory_universe(self, query: str, jurisdiction: str = "CA") -> List[Dict[str, Any]]:
        """Search through actual regulatory references with LLM analysis"""
        
        print(f"🔍 Searching {len(self.legal_references)} real regulatory references for: '{query}'")
        
        # Find matching references in our actual data
        matching_refs = []
        query_lower = query.lower()
        
        for ref in self.legal_references:
            # Check if query matches in citation text or business impact
            citation_match = query_lower in ref.get('citation_text', '').lower()
            impact_match = query_lower in ref.get('business_impact', '').lower()
            category_match = query_lower in ref.get('category', '').lower()
            
            if citation_match or impact_match or category_match:
                matching_refs.append(ref)
        
        # If no direct matches, do semantic search based on query intent
        if not matching_refs:
            matching_refs = self._semantic_search(query_lower)
        
        # Enhance results with LLM analysis and actual text content
        enhanced_results = []
        for ref in matching_refs[:10]:  # Limit to top 10 results
            enhanced_ref = self._enhance_reference_with_llm(ref, query)
            # Add actual QAP section content
            enhanced_ref = self._add_actual_content(enhanced_ref)
            enhanced_results.append(enhanced_ref)
        
        return enhanced_results

    def _semantic_search(self, query: str) -> List[Dict[str, Any]]:
        """Find semantically related references"""
        semantic_matches = []
        
        # Define semantic mappings for common LIHTC queries
        semantic_mappings = {
            'income': ['income', 'AMI', 'qualification', 'tenant', 'revenue'],
            'basis': ['qualified', 'basis', 'cost', 'calculation', 'eligible'],
            'compliance': ['compliance', 'monitoring', 'requirements', 'certification'],
            'allocation': ['allocation', 'credit', 'scoring', 'selection', 'criteria'],
            'construction': ['construction', 'building', 'development', 'standards'],
            'federal': ['IRC', 'CFR', 'federal', 'treasury', 'internal revenue'],
            'state': ['california', 'health', 'safety', 'revenue', 'taxation']
        }
        
        # Find the most relevant semantic category
        relevant_terms = []
        for category, terms in semantic_mappings.items():
            if any(term in query for term in terms):
                relevant_terms.extend(terms)
        
        # Search references for semantic matches
        for ref in self.legal_references:
            ref_text = (ref.get('citation_text', '') + ' ' + 
                       ref.get('business_impact', '') + ' ' + 
                       ref.get('category', '')).lower()
            
            if any(term in ref_text for term in relevant_terms):
                semantic_matches.append(ref)
        
        return semantic_matches[:10]

    def _enhance_reference_with_llm(self, reference: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Enhance reference with LLM analysis of regulatory significance"""
        
        if not self.llm_model:
            # Fallback without LLM
            return self._enhance_reference_fallback(reference, query)
        
        try:
            # Create LLM prompt for regulatory analysis
            prompt = f"""
Analyze this LIHTC regulatory reference for the query "{query}":

Citation: {reference.get('citation_text', '')}
Authority Level: {reference.get('authority_level', 0)} (100=Federal IRC, 80=CFR, 30=State)
Jurisdiction: {reference.get('jurisdiction', '')}
Found in QAP Section: {reference.get('section_found', '')}
Business Impact: {reference.get('business_impact', '')}

Provide analysis in JSON format:
{{
    "relevance_score": 0.0-1.0,
    "regulatory_significance": "brief explanation of why this matters for LIHTC",
    "authority_explanation": "why this authority level matters",
    "practical_impact": "what this means for developers",
    "connections": "how this connects to other regulations"
}}
"""

            payload = {
                "model": self.llm_model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            analysis_text = result.get('response', '{}')
            
            # Parse LLM analysis
            try:
                llm_analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                # Extract JSON from response if wrapped
                json_match = re.search(r'\{[^}]+\}', analysis_text)
                if json_match:
                    llm_analysis = json.loads(json_match.group())
                else:
                    llm_analysis = {"relevance_score": 0.5, "regulatory_significance": "Analysis unavailable"}
            
            # Enhance original reference with LLM insights
            enhanced = reference.copy()
            enhanced.update({
                "llm_analysis": llm_analysis,
                "relevance_score": llm_analysis.get("relevance_score", 0.5),
                "regulatory_significance": llm_analysis.get("regulatory_significance", ""),
                "authority_explanation": llm_analysis.get("authority_explanation", ""),
                "practical_impact": llm_analysis.get("practical_impact", ""),
                "search_query": query
            })
            
            return enhanced
            
        except Exception as e:
            print(f"⚠️ LLM analysis failed for {reference.get('reference_id', 'unknown')}: {e}")
            return self._enhance_reference_fallback(reference, query)

    def _enhance_reference_fallback(self, reference: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Fallback enhancement without LLM"""
        
        # Simple relevance scoring based on text matching
        query_terms = query.lower().split()
        ref_text = (reference.get('citation_text', '') + ' ' + 
                   reference.get('business_impact', '')).lower()
        
        matches = sum(1 for term in query_terms if term in ref_text)
        relevance_score = min(matches / len(query_terms), 1.0) if query_terms else 0.5
        
        # Basic regulatory significance based on authority level
        authority_level = reference.get('authority_level', 30)
        if authority_level >= 100:
            significance = "Federal statutory authority - overrides all state interpretations"
        elif authority_level >= 80:
            significance = "Federal regulatory authority - overrides state regulations"
        else:
            significance = "State implementation of federal requirements"
        
        enhanced = reference.copy()
        enhanced.update({
            "relevance_score": relevance_score,
            "regulatory_significance": significance,
            "authority_explanation": f"Authority level {authority_level}",
            "practical_impact": reference.get('business_impact', ''),
            "search_query": query
        })
        
        return enhanced
    
    def _add_actual_content(self, reference: Dict[str, Any]) -> Dict[str, Any]:
        """Add actual regulatory text content to reference"""
        
        enhanced = reference.copy()
        section_found = reference.get('section_found', '')
        
        # Find matching QAP section content
        qap_content = self._find_qap_section_content(section_found)
        
        if qap_content:
            enhanced.update({
                "qap_section_content": qap_content.get("content", ""),
                "section_title": qap_content.get("section_title", ""),
                "content_preview": self._create_content_preview(qap_content.get("content", "")),
                "federal_refs_in_section": qap_content.get("federal_refs", []),
                "state_refs_in_section": qap_content.get("state_refs", []),
                "verification_available": True
            })
        else:
            # Add simulated content for demonstration
            enhanced.update({
                "content_preview": self._create_mock_content(reference),
                "verification_available": False
            })
        
        return enhanced
    
    def _find_qap_section_content(self, section_ref: str) -> Optional[Dict[str, Any]]:
        """Find actual QAP section content by section reference"""
        
        if not self.ca_qap_content or 'enhanced_chunks' not in self.ca_qap_content:
            return None
        
        # Extract section number from reference (e.g., "§10302 - Definitions" -> "10302")
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
    
    def _create_content_preview(self, content: str) -> str:
        """Create preview of actual content"""
        if not content:
            return "Content not available"
        
        # Clean up content and create preview
        cleaned = re.sub(r'\s+', ' ', content.strip())
        if len(cleaned) > 300:
            return cleaned[:300] + "..."
        return cleaned
    
    def _create_mock_content(self, reference: Dict[str, Any]) -> str:
        """Create mock content for demonstration when actual content unavailable"""
        
        citation = reference.get('citation_text', '')
        authority = reference.get('authority_level', 0)
        
        if authority >= 100:  # Federal IRC
            return f"Federal statutory authority: {citation} establishes requirements for qualified basis calculation, income restrictions, and compliance monitoring for LIHTC properties..."
        elif authority >= 80:  # Federal CFR
            return f"Federal regulatory implementation: {citation} provides detailed procedures for income certification, rent calculations, and compliance reporting requirements..."
        else:  # State/QAP
            return f"State implementation: {citation} specifies California-specific requirements for project selection, monitoring, and state tax credit coordination..."

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
            "breakdown": {
                "federal": [{"citation": r.get('citation_text', ''), 
                           "authority": r.get('authority_level', 0),
                           "section": r.get('section_found', '')} for r in federal_refs[:5]],
                "state": [{"citation": r.get('citation_text', ''), 
                         "authority": r.get('authority_level', 0),
                         "section": r.get('section_found', '')} for r in state_refs[:5]],
                "internal": [{"citation": r.get('citation_text', ''), 
                            "section": r.get('section_found', '')} for r in internal_refs[:5]]
            }
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
intelligence = RealRegulatoryIntelligence()

@app.route('/')
def index():
    """Main demo page"""
    return render_template('real_regulatory_demo.html')

@app.route('/api/search')
def api_search():
    """Real regulatory universe search API"""
    query = request.args.get('query', '')
    jurisdiction = request.args.get('jurisdiction', 'CA')
    
    if not query:
        return jsonify({"error": "Query parameter required"}), 400
    
    print(f"🔍 Processing search: '{query}' in {jurisdiction}")
    
    results = intelligence.search_regulatory_universe(query, jurisdiction)
    
    # Add verification statistics
    content_available = sum(1 for r in results if r.get('verification_available', False))
    
    return jsonify({
        "query": query,
        "jurisdiction": jurisdiction,
        "results_count": len(results),
        "results": results,
        "verification_stats": {
            "results_with_content": content_available,
            "results_total": len(results),
            "content_coverage": f"{(content_available/len(results)*100):.1f}%" if results else "0%"
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

@app.route('/api/verify_content/<reference_id>')
def api_verify_content(reference_id):
    """Verify actual regulatory content by reference ID"""
    
    # Find the reference
    ref = next((r for r in intelligence.legal_references if r.get('reference_id') == reference_id), None)
    if not ref:
        return jsonify({"error": "Reference not found"}), 404
    
    # Get actual content
    enhanced_ref = intelligence._add_actual_content(ref)
    
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
        "verification_timestamp": datetime.now().isoformat()
    })

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

def launch_real_demo():
    """Launch the real regulatory intelligence demo"""
    
    print("🏛️ REAL REGULATORY INTELLIGENCE DEMO")
    print("="*50)
    print("🔍 Real search through 92 California legal references")
    print("🧠 Llama LLM analysis of regulatory connections")
    print("⚖️ Actual authority hierarchy (Federal > State)")
    print("🗺️ True hub-and-spoke model with real data")
    print("="*50)
    
    if intelligence.llm_model:
        print(f"✅ LLM: {intelligence.llm_model}")
    else:
        print("⚠️ LLM: Fallback mode (Ollama not available)")
    
    print(f"📊 Loaded {len(intelligence.legal_references)} real regulatory references")
    print()
    
    # Launch Flask app
    import threading
    import time
    import webbrowser
    
    def run_flask():
        app.run(host='127.0.0.1', port=5002, debug=False)
    
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Wait and open browser
    time.sleep(2)
    demo_url = "http://127.0.0.1:5002"
    print(f"🌐 Demo URL: {demo_url}")
    
    try:
        webbrowser.open(demo_url)
        print("🚀 Real Regulatory Intelligence Demo is running!")
    except:
        print("📱 Please open the URL manually in your browser")
    
    print("\n💡 Try searching for:")
    print("   • 'income limits' - See IRC Section 42 connections")
    print("   • 'qualified basis' - Federal vs state requirements")
    print("   • 'compliance monitoring' - Authority hierarchy")
    print("   • 'selection criteria' - QAP scoring connections")
    print("\nPress Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped")

if __name__ == "__main__":
    launch_real_demo()