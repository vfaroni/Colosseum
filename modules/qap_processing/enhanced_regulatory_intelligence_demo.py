#!/usr/bin/env python3
"""
Enhanced Regulatory Intelligence Demo - Complete Universe Search
Professional web interface showcasing Complete Regulatory Universe capabilities

Features:
- California's 316 legal references with authority hierarchy
- Hub-and-spoke regulatory model visualization  
- Cross-jurisdictional comparison (CA vs TX vs FL vs NY)
- Authority-weighted search results
- Business case demonstration (3-5X revenue opportunity)

Built by Structured Consultants LLC
Roman Engineering Standards: Built to Last 2000+ Years
"""

from flask import Flask, render_template, request, jsonify
import sys
import json
from datetime import datetime
from pathlib import Path
import webbrowser
import threading
import time
import os
from typing import Dict, List, Any, Optional

# Import existing systems
sys.path.append(str(Path(__file__).parent))

try:
    from enhanced_lihtc_rag_interface import LIHTCRAGInterface
    from complete_universe_search_engine import CompleteUniverseSearchEngine, SearchResult, SearchResultType
    print("✅ Successfully imported RAG and Search interfaces")
except ImportError as e:
    print(f"⚠️ Some imports failed, running in demo mode: {e}")

app = Flask(__name__)

class EnhancedRegulatoryDemo:
    """Enhanced demo showcasing complete regulatory universe capabilities"""
    
    def __init__(self):
        self.ca_demo_data = self._load_ca_regulatory_data()
        self.jurisdictions_data = self._load_jurisdictions_comparison()
        self.search_engine = None
        self.rag_system = None
        
        # Initialize search engine if available
        try:
            self.search_engine = CompleteUniverseSearchEngine()
            print("✅ Complete Universe Search Engine initialized")
        except:
            print("⚠️ Search engine running in demo mode")
            
        # Initialize RAG system if available
        try:
            chromadb_path = str(Path(__file__).parent / "lihtc_definitions_chromadb")
            if Path(chromadb_path).exists():
                self.rag_system = LIHTCRAGInterface(chromadb_path)
                print("✅ RAG system initialized")
        except:
            print("⚠️ RAG system running in demo mode")

    def _load_ca_regulatory_data(self) -> Dict[str, Any]:
        """Load California regulatory universe demo data"""
        try:
            demo_data_path = Path(__file__).parent / "ca_regulatory_universe_demo_data.json"
            with open(demo_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Using fallback CA demo data: {e}")
            return self._generate_fallback_ca_data()

    def _generate_fallback_ca_data(self) -> Dict[str, Any]:
        """Generate fallback demo data for California"""
        return {
            "metadata": {
                "system": "Colosseum Complete Regulatory Universe",
                "jurisdiction": "California",
                "demo_type": "Enhanced Regulatory Intelligence Demo"
            },
            "regulatory_universe": {
                "qap_sections": 17,
                "total_legal_refs": 316,
                "federal_refs": 57,
                "state_refs": 8,
                "internal_refs": 251,
                "hub_to_spoke_ratio": "2-3:1",
                "estimated_external_pages": 700,
                "business_value_multiplier": "3-4X"
            },
            "demo_insights": {
                "authority_hierarchy_demo": {
                    "total_federal_authority_refs": 57,
                    "total_state_authority_refs": 8,
                    "highest_authority_examples": [
                        "IRC Section 42(b)(1)", 
                        "IRC Section 42(h)(3)(C)",
                        "26 CFR 1.42", 
                        "Public Law No. 99-514"
                    ]
                },
                "hub_spoke_model_demo": {
                    "hub_references": 251,
                    "spoke_references": 65,
                    "external_universe_size": "600-800 pages (2-3X QAP size)"
                }
            },
            "business_case": {
                "current_market_value": "$5,000-$15,000/month per developer",
                "complete_universe_value": "$20,000-$50,000/month per developer",
                "revenue_multiplication": "3-4X increase"
            }
        }

    def _load_jurisdictions_comparison(self) -> Dict[str, Any]:
        """Load comparison data for multiple jurisdictions"""
        return {
            "CA": {
                "name": "California",
                "model_type": "Comprehensive Model",
                "qap_pages": 109,
                "external_pages": 700,
                "ratio": "2-3:1",
                "revenue_multiplier": "3-4X",
                "legal_refs": 316,
                "authority_breakdown": {"Federal": 57, "State": 8, "Internal": 251}
            },
            "TX": {
                "name": "Texas", 
                "model_type": "Complex-Hybrid Model",
                "qap_pages": 218,
                "external_pages": 1100,
                "ratio": "4-5:1",
                "revenue_multiplier": "4-5X",
                "legal_refs": 450,
                "authority_breakdown": {"Federal": 85, "State": 15, "Internal": 350}
            },
            "FL": {
                "name": "Florida",
                "model_type": "Hub-Heavy Model", 
                "qap_pages": 14,
                "external_pages": 565,
                "ratio": "40:1",
                "revenue_multiplier": "10X+",
                "legal_refs": 200,
                "authority_breakdown": {"Federal": 45, "State": 120, "Internal": 35}
            },
            "NY": {
                "name": "New York",
                "model_type": "Federal-Focus Model",
                "qap_pages": 48,
                "external_pages": 140,
                "ratio": "3:1", 
                "revenue_multiplier": "3X",
                "legal_refs": 180,
                "authority_breakdown": {"Federal": 95, "State": 25, "Internal": 60}
            }
        }

    def search_complete_universe(self, query: str, jurisdiction: str = "CA") -> List[Dict[str, Any]]:
        """Search across complete regulatory universe"""
        
        if self.search_engine:
            # Use real search engine
            try:
                results = self.search_engine.search_unified(
                    query=query,
                    target_jurisdictions=[jurisdiction],
                    max_results=10
                )
                return [self._format_search_result(r) for r in results]
            except:
                pass
        
        # Fallback demo results
        return self._generate_demo_search_results(query, jurisdiction)

    def _format_search_result(self, result: SearchResult) -> Dict[str, Any]:
        """Format search result for web display"""
        return {
            "id": result.result_id,
            "title": result.title,
            "content": result.content_snippet,
            "jurisdiction": result.jurisdiction,
            "authority_level": result.authority_level,
            "match_score": result.match_score,
            "section": result.section_id,
            "result_type": result.result_type.value
        }

    def _generate_demo_search_results(self, query: str, jurisdiction: str) -> List[Dict[str, Any]]:
        """Generate realistic demo search results"""
        
        demo_results = []
        
        if "income limit" in query.lower():
            demo_results = [
                {
                    "id": "IRC_42_g_1",
                    "title": "IRC Section 42(g)(1) - Income Limitations",
                    "content": "The income limitation applicable to any building for any taxable year is 60 percent of area median gross income...",
                    "jurisdiction": "Federal",
                    "authority_level": 100,
                    "match_score": 0.95,
                    "section": "IRC Section 42(g)(1)", 
                    "result_type": "exact_match"
                },
                {
                    "id": "CA_QAP_10325_c_1",
                    "title": "CA QAP §10325(c)(1) - Income Targeting",
                    "content": "Applications shall receive points for the percentage of Lower Income units in the development that will be restricted to tenants at or below specific income levels...",
                    "jurisdiction": "California",
                    "authority_level": 30,
                    "match_score": 0.87,
                    "section": "§10325(c)(1)",
                    "result_type": "semantic_match"
                }
            ]
            
        elif "qualified basis" in query.lower():
            demo_results = [
                {
                    "id": "IRC_42_d_1",
                    "title": "IRC Section 42(d)(1) - Qualified Basis",
                    "content": "The qualified basis of any building for any taxable year is an amount equal to the applicable fraction of the eligible basis of such building...",
                    "jurisdiction": "Federal", 
                    "authority_level": 100,
                    "match_score": 0.98,
                    "section": "IRC Section 42(d)(1)",
                    "result_type": "exact_match"
                }
            ]
            
        else:
            # General search results
            demo_results = [
                {
                    "id": "GENERAL_1",
                    "title": f"{jurisdiction} General Search Result",
                    "content": f"Demo search result for query: {query}",
                    "jurisdiction": jurisdiction,
                    "authority_level": 30,
                    "match_score": 0.75,
                    "section": "Demo Section",
                    "result_type": "partial_match"
                }
            ]
            
        return demo_results

    def get_authority_hierarchy_demo(self) -> Dict[str, Any]:
        """Get authority hierarchy demonstration data"""
        return {
            "hierarchy_levels": [
                {"level": 100, "name": "Federal IRC", "description": "Statutory law - overrides all state interpretations", "count": 43},
                {"level": 80, "name": "Federal CFR", "description": "Federal regulations - overrides state regulations", "count": 13}, 
                {"level": 60, "name": "Federal Guidance", "description": "Revenue procedures - minimum standards", "count": 1},
                {"level": 30, "name": "State QAP", "description": "State implementation of federal requirements", "count": 8},
                {"level": 30, "name": "Internal References", "description": "QAP cross-references", "count": 251}
            ],
            "examples": {
                "federal_override": "IRC Section 42(g)(1) income limits override any conflicting state requirements",
                "state_implementation": "CA QAP §10325 implements federal targeting requirements with state-specific scoring"
            }
        }

    def get_business_case_demo(self) -> Dict[str, Any]:
        """Get business case demonstration data"""
        return {
            "market_transformation": {
                "before": "QAP-only document processing service",
                "after": "Complete regulatory intelligence platform",
                "advantage": "Industry monopoly on complete regulatory universe"
            },
            "revenue_analysis": {
                "qap_only_value": "$5,000-$15,000/month per developer",
                "complete_universe_value": "$20,000-$50,000/month per developer",
                "multiplication_factor": "3-4X revenue increase",
                "market_expansion": "$50M → $500M+ total addressable market"
            },
            "competitive_moat": {
                "development_time": "18-24 months for competitors to replicate",
                "barrier_height": "Exponentially increases with each jurisdiction",
                "customer_lock_in": "Complete regulatory dependency prevents switching"
            }
        }

# Global demo instance
demo = EnhancedRegulatoryDemo()

@app.route('/')
def index():
    """Main demo dashboard"""
    return render_template('regulatory_intelligence_demo.html',
                         ca_data=demo.ca_demo_data,
                         jurisdictions=demo.jurisdictions_data)

@app.route('/api/search')
def api_search():
    """API endpoint for complete universe search"""
    query = request.args.get('query', '')
    jurisdiction = request.args.get('jurisdiction', 'CA')
    
    if not query:
        return jsonify({"error": "Query parameter required"}), 400
    
    results = demo.search_complete_universe(query, jurisdiction)
    
    return jsonify({
        "query": query,
        "jurisdiction": jurisdiction,
        "results": results,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/authority_hierarchy')
def api_authority_hierarchy():
    """API endpoint for authority hierarchy demo"""
    return jsonify(demo.get_authority_hierarchy_demo())

@app.route('/api/business_case')
def api_business_case():
    """API endpoint for business case demo"""
    return jsonify(demo.get_business_case_demo())

@app.route('/api/jurisdictions_comparison')
def api_jurisdictions_comparison():
    """API endpoint for cross-jurisdictional comparison"""
    return jsonify(demo.jurisdictions_data)

def launch_demo():
    """Launch enhanced regulatory intelligence demo"""
    print("🏛️ ENHANCED REGULATORY INTELLIGENCE DEMO")
    print("="*50)
    print("🚀 Complete Universe Search Engine")
    print("📊 Authority Hierarchy Intelligence") 
    print("🎯 Cross-Jurisdictional Comparison")
    print("💰 5X Revenue Opportunity Demo")
    print("="*50)
    
    # Start Flask app
    def run_flask():
        app.run(host='127.0.0.1', port=5001, debug=False)
    
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Open in browser
    demo_url = "http://127.0.0.1:5001"
    print(f"🌐 Opening demo in browser: {demo_url}")
    
    try:
        webbrowser.open(demo_url)
    except:
        print("❌ Could not open browser automatically")
        print(f"📱 Please open manually: {demo_url}")
    
    print("\n✅ Enhanced Regulatory Intelligence Demo is running!")
    print("💡 Demonstrates complete regulatory universe capabilities")
    print("🏆 Shows 18-24 month competitive advantage")
    print("\nPress Ctrl+C to stop the demo")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped")

if __name__ == "__main__":
    launch_demo()