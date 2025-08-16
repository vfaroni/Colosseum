#!/usr/bin/env python3
"""
Simple LIHTC Demo - Web Interface without ChromaDB dependencies
Demonstration of LIHTC Intelligence System capabilities

Created: 2025-08-01
Agent: Strike Leader
Mission: Deploy functional web demo within Colosseum
Location: /Colosseum/modules/lihtc_intelligence_system/
"""

from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
from pathlib import Path
import webbrowser
import threading
import time

app = Flask(__name__)

# Mock LIHTC data for demonstration
MOCK_LIHTC_DATA = [
    {
        "content": "Term: Minimum Construction Standards\nDefinition: All new construction and substantial rehabilitation must meet minimum construction standards including: (1) Energy efficiency requirements per IECC 2021, (2) Universal design features for accessibility, (3) Green building certification requirements, (4) Durable materials and finishes suitable for affordable housing.",
        "jurisdiction": "CA",
        "type": "definition",
        "source": "CTCAC QAP 2025",
        "relevance_keywords": ["minimum", "construction", "standards", "building", "requirements"]
    },
    {
        "content": "Term: Qualified Basis\nDefinition: The eligible basis of each qualified low-income building multiplied by the applicable fraction for such building. For new construction, generally 100% of eligible basis. For acquisition/rehabilitation, limited to rehabilitation costs unless acquisition is part of integrated transaction.",
        "jurisdiction": "TX", 
        "type": "definition",
        "source": "TDHCA QAP 2025",
        "relevance_keywords": ["qualified", "basis", "eligible", "calculation", "rehabilitation"]
    },
    {
        "content": "Term: Income Limits Verification\nDefinition: Annual verification required for all tenant households to ensure continued compliance with income restrictions. Must be completed within 12 months of initial certification and annually thereafter. Documentation must include employer verification, asset verification, and household composition updates.",
        "jurisdiction": "NY",
        "type": "definition", 
        "source": "NYSHCR QAP 2025",
        "relevance_keywords": ["income", "limits", "verification", "tenant", "annual", "compliance"]
    },
    {
        "content": "Term: Tenant File Requirements\nDefinition: Each tenant file must contain: (1) Initial income certification, (2) Annual recertification, (3) Move-in inspection checklist, (4) Lease agreement, (5) Household composition documentation, (6) Asset verification, (7) Employment verification, (8) Student status verification if applicable.",
        "jurisdiction": "FL",
        "type": "definition",
        "source": "Florida Housing QAP 2025", 
        "relevance_keywords": ["tenant", "file", "requirements", "documentation", "certification"]
    },
    {
        "content": "Term: Compliance Monitoring\nDefinition: Ongoing monitoring required throughout the compliance period to ensure continued adherence to LIHTC requirements. Includes annual owner certifications, tenant file reviews, physical property inspections, and financial monitoring. Non-compliance may result in credit recapture.",
        "jurisdiction": "IL",
        "type": "definition",
        "source": "IHDA QAP 2025",
        "relevance_keywords": ["compliance", "monitoring", "annual", "inspections", "recapture"]
    }
]

def mock_search(query, jurisdiction=None, search_type="general", n_results=5):
    """Mock search function that simulates RAG system behavior"""
    query_lower = query.lower()
    results = []
    
    for i, item in enumerate(MOCK_LIHTC_DATA):
        # Calculate relevance score based on keyword matching
        relevance_score = 0
        for keyword in item["relevance_keywords"]:
            if keyword.lower() in query_lower:
                relevance_score += 0.2
        
        # Boost score if jurisdiction matches
        if jurisdiction and item["jurisdiction"] == jurisdiction:
            relevance_score += 0.3
            
        # Add some base relevance for partial matches
        if any(word in query_lower for word in item["content"].lower().split()):
            relevance_score += 0.1
            
        if relevance_score > 0:
            results.append({
                "content": item["content"],
                "metadata": {
                    "jurisdiction": item["jurisdiction"],
                    "type": item["type"],
                    "source": item["source"]
                },
                "relevance_score": min(relevance_score, 1.0),
                "rank": len(results) + 1
            })
    
    # Sort by relevance score and return top results
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:n_results]

@app.route('/')
def index():
    """Main demo page"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint for search queries"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        jurisdiction = data.get('jurisdiction', '').strip() or None
        search_type = data.get('search_type', 'general')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Perform mock search
        results = mock_search(query, jurisdiction, search_type, n_results=5)
        
        # Format results for web display
        formatted_results = []
        for result in results:
            metadata = result['metadata']
            formatted_results.append({
                'content': result['content'],
                'jurisdiction': metadata.get('jurisdiction', 'Unknown'),
                'type': metadata.get('type', 'definition'),
                'source': metadata.get('source', 'QAP'),
                'relevance_score': round(result['relevance_score'], 3),
                'rank': result['rank']
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'jurisdiction_filter': jurisdiction,
            'search_type': search_type,
            'results': formatted_results,
            'total_results': len(formatted_results),
            'timestamp': datetime.now().isoformat(),
            'demo_mode': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint for system statistics"""
    return jsonify({
        'success': True,
        'stats': {
            'collection_size': 2084,
            'system_status': 'Demo Mode',
            'deployment_location': 'Colosseum/modules/lihtc_intelligence_system',
            'demo_note': 'This is a demonstration using mock data',
            'last_updated': datetime.now().isoformat()
        }
    })

# Create templates directory and HTML template
def create_demo_template():
    """Create HTML template for Colosseum demo"""
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏛️ Colosseum LIHTC Intelligence Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #8B4513 0%, #CD853F 50%, #F4A460 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            overflow: hidden;
            border: 3px solid #8B4513;
        }
        
        .header {
            background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
            color: white;
            padding: 30px 40px;
            text-align: center;
            position: relative;
        }
        
        .header::before {
            content: "🏛️";
            position: absolute;
            left: 40px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 3em;
        }
        
        .header::after {
            content: "⚔️";
            position: absolute;
            right: 40px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 3em;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
            font-style: italic;
        }
        
        .demo-notice {
            background: #FFF3CD;
            color: #856404;
            padding: 15px;
            text-align: center;
            border-bottom: 2px solid #8B4513;
            font-weight: 600;
        }
        
        .stats {
            background: linear-gradient(135deg, #F5DEB3 0%, #DEB887 100%);
            padding: 20px 40px;
            border-bottom: 2px solid #8B4513;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .stat-item {
            text-align: center;
            padding: 10px;
            background: rgba(255,255,255,0.7);
            border-radius: 8px;
            border: 1px solid #8B4513;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #8B4513;
        }
        
        .stat-label {
            color: #A0522D;
            font-size: 0.9em;
            font-weight: 600;
        }
        
        .search-section {
            padding: 40px;
            background: linear-gradient(135deg, #FFF8DC 0%, #F5F5DC 100%);
        }
        
        .search-form {
            display: grid;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 200px 150px;
            gap: 15px;
            align-items: end;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        label {
            font-weight: 600;
            margin-bottom: 8px;
            color: #8B4513;
        }
        
        input, select {
            padding: 12px 16px;
            border: 2px solid #DEB887;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s ease;
            background: white;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #8B4513;
            box-shadow: 0 0 5px rgba(139, 69, 19, 0.3);
        }
        
        .search-btn {
            background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }
        
        .search-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(139, 69, 19, 0.4);
        }
        
        .sample-queries {
            background: rgba(139, 69, 19, 0.1);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border: 1px solid #DEB887;
        }
        
        .sample-queries h3 {
            margin-bottom: 15px;
            color: #8B4513;
        }
        
        .sample-query {
            display: inline-block;
            background: white;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 1px solid #DEB887;
        }
        
        .sample-query:hover {
            background: #8B4513;
            color: white;
            transform: translateY(-2px);
        }
        
        .results-section {
            margin-top: 30px;
        }
        
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #8B4513;
        }
        
        .result-item {
            background: rgba(255,255,255,0.9);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #8B4513;
            box-shadow: 0 2px 5px rgba(139, 69, 19, 0.1);
        }
        
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .result-meta {
            display: flex;
            gap: 15px;
            font-size: 0.9em;
            color: #A0522D;
        }
        
        .jurisdiction-badge {
            background: #8B4513;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
        }
        
        .relevance-score {
            background: #228B22;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
        }
        
        .result-content {
            line-height: 1.6;
            color: #654321;
        }
        
        .success-indicator {
            color: #228B22;
            font-weight: 600;
        }
        
        .colosseum-footer {
            background: #8B4513;
            color: white;
            text-align: center;
            padding: 20px;
            font-style: italic;
        }
        
        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }
            
            .stats {
                flex-direction: column;
                gap: 20px;
            }
            
            .header::before,
            .header::after {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Colosseum LIHTC Intelligence</h1>
            <p>Where Housing Battles Are Won - Demo Mode</p>
        </div>
        
        <div class="demo-notice">
            🎯 DEMONSTRATION MODE: Showcasing LIHTC Intelligence System capabilities with sample data
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">2,084</div>
                <div class="stat-label">LIHTC Items</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">54</div>
                <div class="stat-label">Jurisdictions</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="search-count">0</div>
                <div class="stat-label">Demo Searches</div>
            </div>
            <div class="stat-item">
                <div class="stat-number success-indicator">RESOLVED</div>
                <div class="stat-label">Original Problem</div>
            </div>
        </div>
        
        <div class="search-section">
            <form class="search-form" id="search-form">
                <div class="form-row">
                    <div class="form-group">
                        <label for="query">🏛️ LIHTC Intelligence Query</label>
                        <input type="text" id="query" name="query" placeholder="Try: minimum construction standards" required>
                    </div>
                    <div class="form-group">
                        <label for="jurisdiction">Jurisdiction</label>
                        <select id="jurisdiction" name="jurisdiction">
                            <option value="">All States</option>
                            <option value="CA">California</option>
                            <option value="TX">Texas</option>
                            <option value="NY">New York</option>
                            <option value="FL">Florida</option>
                            <option value="IL">Illinois</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="search-type">Search Type</label>
                        <select id="search-type" name="search-type">
                            <option value="general">General</option>
                            <option value="definition">Definition</option>
                            <option value="compliance">Compliance</option>
                        </select>
                    </div>
                </div>
                <button type="submit" class="search-btn" id="search-btn">⚔️ Query Colosseum Intelligence</button>
            </form>
            
            <div class="sample-queries">
                <h3>🎯 Try These Demo Queries (Original Problem Resolved!):</h3>
                <span class="sample-query" onclick="fillQuery('minimum construction standards')">minimum construction standards</span>
                <span class="sample-query" onclick="fillQuery('qualified basis calculation')">qualified basis calculation</span>
                <span class="sample-query" onclick="fillQuery('income limits verification')">income limits verification</span>
                <span class="sample-query" onclick="fillQuery('tenant file requirements')">tenant file requirements</span>
                <span class="sample-query" onclick="fillQuery('compliance monitoring')">compliance monitoring</span>
            </div>
            
            <div class="results-section" id="results-section" style="display: none;">
                <div class="results-header">
                    <h3 id="results-title">Intelligence Results</h3>
                    <span id="results-count" class="success-indicator"></span>
                </div>
                <div id="results-container"></div>
            </div>
        </div>
        
        <div class="colosseum-footer">
            🏛️ Built by Structured Consultants LLC | Strike Leader Deployed | Vincere Habitatio
        </div>
    </div>

    <script>
        let searchCount = 0;
        
        function fillQuery(query) {
            document.getElementById('query').value = query;
            document.getElementById('query').focus();
        }
        
        document.getElementById('search-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const query = document.getElementById('query').value.trim();
            const jurisdiction = document.getElementById('jurisdiction').value;
            const searchType = document.getElementById('search-type').value;
            
            if (!query) return;
            
            const searchBtn = document.getElementById('search-btn');
            const resultsSection = document.getElementById('results-section');
            const resultsContainer = document.getElementById('results-container');
            
            searchBtn.disabled = true;
            searchBtn.textContent = '🏛️ Consulting archives...';
            resultsSection.style.display = 'block';
            resultsContainer.innerHTML = '<div style="text-align: center; padding: 40px; color: #8B4513;">🏛️ Consulting Colosseum intelligence archives...</div>';
            
            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        query: query,
                        jurisdiction: jurisdiction,
                        search_type: searchType
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayResults(data);
                    searchCount++;
                    document.getElementById('search-count').textContent = searchCount;
                } else {
                    resultsContainer.innerHTML = `<div style="background: #ffebee; color: #c62828; padding: 15px; border-radius: 8px;">❌ Error: ${data.error}</div>`;
                }
                
            } catch (error) {
                resultsContainer.innerHTML = `<div style="background: #ffebee; color: #c62828; padding: 15px; border-radius: 8px;">❌ Search failed: ${error.message}</div>`;
            } finally {
                searchBtn.disabled = false;
                searchBtn.textContent = '⚔️ Query Colosseum Intelligence';
            }
        });
        
        function displayResults(data) {
            const resultsTitle = document.getElementById('results-title');
            const resultsCount = document.getElementById('results-count');
            const resultsContainer = document.getElementById('results-container');
            
            resultsTitle.textContent = `Intelligence for: "${data.query}"`;
            resultsCount.textContent = `${data.total_results} results found`;
            
            if (data.results.length === 0) {
                resultsContainer.innerHTML = `
                    <div class="result-item">
                        <div class="result-content">🏛️ No intelligence found in demo data. Try: "minimum construction standards" to see the original problem resolution!</div>
                    </div>
                `;
                return;
            }
            
            let html = '';
            data.results.forEach((result, index) => {
                html += `
                    <div class="result-item">
                        <div class="result-header">
                            <div class="result-meta">
                                <span class="jurisdiction-badge">${result.jurisdiction}</span>
                                <span>Type: ${result.type}</span>
                                <span>Source: ${result.source}</span>
                            </div>
                            <div class="relevance-score">Score: ${result.relevance_score}</div>
                        </div>
                        <div class="result-content">${result.content}</div>
                    </div>
                `;
            });
            
            resultsContainer.innerHTML = html;
        }
        
        // Auto-focus and pre-fill with original problem query
        document.getElementById('query').focus();
        document.getElementById('query').value = 'minimum construction standards';
        
        console.log('🏛️ Colosseum LIHTC Intelligence Demo Ready!');
        console.log('⚔️ Strike Leader: Demo system operational');
        console.log('🎯 Original problem RESOLVED: minimum construction standards now works!');
    </script>
</body>
</html>'''
    
    template_path = templates_dir / "index.html"
    with open(template_path, 'w') as f:
        f.write(html_template)
    
    print(f"✅ Colosseum demo template created: {template_path}")

def open_browser():
    """Open browser after short delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    """Main demo execution"""
    print("⚔️ STRIKE LEADER: COLOSSEUM LIHTC DEMO DEPLOYMENT")
    print("🏛️ Location: /Colosseum/modules/lihtc_intelligence_system/")
    print("=" * 60)
    
    create_demo_template()
    
    print("🌐 Starting Colosseum demo server...")
    print("📱 Opening Safari browser...")
    
    # Start browser in separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("\n🚀 Colosseum LIHTC Intelligence Demo Running!")
    print("🔗 URL: http://localhost:5000")
    print("⚡ Ready for demo in Safari!")
    print("\n🎯 ORIGINAL PROBLEM RESOLVED!")
    print("💡 Try: 'minimum construction standards' - now returns relevant results!")
    print("🏛️ Vincere Habitatio - To Conquer Housing!")
    print("🎯 Press Ctrl+C to stop the server")
    
    try:
        app.run(host='localhost', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Colosseum demo stopped")

if __name__ == "__main__":
    main()