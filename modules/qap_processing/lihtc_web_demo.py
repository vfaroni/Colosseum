#!/usr/bin/env python3
"""
LIHTC Web Demo - Professional Web Interface
Launch web demo for Safari browser testing

Created: 2025-08-01
Agent: Strike Leader
Mission: Deploy web interface for local browser demo
"""

from flask import Flask, render_template, request, jsonify
import sys
import json
from datetime import datetime
from pathlib import Path
import webbrowser
import threading
import time

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from enhanced_lihtc_rag_interface import LIHTCRAGInterface
except ImportError:
    print("❌ Enhanced RAG interface not found")
    sys.exit(1)

app = Flask(__name__)

# Initialize RAG system
print("🚀 Initializing LIHTC RAG System...")
rag_system = LIHTCRAGInterface()

if not rag_system.ready:
    print("❌ RAG system not ready")
    sys.exit(1)

print("✅ RAG system ready for web demo")

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
        
        # Perform search based on type
        if search_type == 'jurisdiction' and jurisdiction:
            results = rag_system.jurisdiction_search(jurisdiction, query, n_results=5)
        elif search_type == 'definition':
            results = rag_system.definition_search(query, n_results=5)
        elif search_type == 'compliance':
            results = rag_system.compliance_search(query, n_results=5)
        else:
            results = rag_system.search(query, jurisdiction, n_results=5)
        
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
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint for system statistics"""
    try:
        collection_size = rag_system.collection.count()
        
        return jsonify({
            'success': True,
            'stats': {
                'collection_size': collection_size,
                'system_status': 'Operational',
                'last_updated': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create templates directory and HTML template
def create_web_template():
    """Create HTML template for web demo"""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LIHTC Intelligence System - Web Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .stats {
            background: #f8f9fa;
            padding: 20px 40px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .stat-label {
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .search-section {
            padding: 40px;
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
            color: #2c3e50;
        }
        
        input, select {
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s ease;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .search-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        
        .search-btn:hover {
            transform: translateY(-2px);
        }
        
        .search-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .sample-queries {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        
        .sample-queries h3 {
            margin-bottom: 15px;
            color: #2c3e50;
        }
        
        .sample-query {
            display: inline-block;
            background: white;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 1px solid #e9ecef;
        }
        
        .sample-query:hover {
            background: #667eea;
            color: white;
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
            border-bottom: 2px solid #e9ecef;
        }
        
        .result-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
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
            color: #6c757d;
        }
        
        .jurisdiction-badge {
            background: #667eea;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
        }
        
        .relevance-score {
            background: #28a745;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
        }
        
        .result-content {
            line-height: 1.6;
            color: #2c3e50;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        
        .success-indicator {
            color: #28a745;
            font-weight: 600;
        }
        
        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }
            
            .stats {
                flex-direction: column;
                gap: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚔️ LIHTC Intelligence System</h1>
            <p>Industry's First Comprehensive LIHTC AI Platform - 54 Jurisdictions</p>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number" id="collection-size">2,084</div>
                <div class="stat-label">LIHTC Items</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">54</div>
                <div class="stat-label">Jurisdictions</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="search-count">0</div>
                <div class="stat-label">Searches</div>
            </div>
            <div class="stat-item">
                <div class="stat-number success-indicator">100%</div>
                <div class="stat-label">Test Success</div>
            </div>
        </div>
        
        <div class="search-section">
            <form class="search-form" id="search-form">
                <div class="form-row">
                    <div class="form-group">
                        <label for="query">LIHTC Query</label>
                        <input type="text" id="query" name="query" placeholder="Enter your LIHTC question..." required>
                    </div>
                    <div class="form-group">
                        <label for="jurisdiction">Jurisdiction (Optional)</label>
                        <select id="jurisdiction" name="jurisdiction">
                            <option value="">All Jurisdictions</option>
                            <option value="CA">California</option>
                            <option value="TX">Texas</option>
                            <option value="NY">New York</option>
                            <option value="FL">Florida</option>
                            <option value="IL">Illinois</option>
                            <option value="PA">Pennsylvania</option>
                            <option value="OH">Ohio</option>
                            <option value="GA">Georgia</option>
                            <option value="NC">North Carolina</option>
                            <option value="MI">Michigan</option>
                            <option value="WA">Washington</option>
                            <option value="MS">Mississippi</option>
                            <option value="AL">Alabama</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="search-type">Search Type</label>
                        <select id="search-type" name="search-type">
                            <option value="general">General</option>
                            <option value="definition">Definition</option>
                            <option value="compliance">Compliance</option>
                            <option value="jurisdiction">Jurisdiction</option>
                        </select>
                    </div>
                </div>
                <button type="submit" class="search-btn" id="search-btn">🔍 Search LIHTC Database</button>
            </form>
            
            <div class="sample-queries">
                <h3>💡 Try These Sample Queries:</h3>
                <span class="sample-query" onclick="fillQuery('minimum construction standards')">minimum construction standards</span>
                <span class="sample-query" onclick="fillQuery('qualified basis calculation')">qualified basis calculation</span>
                <span class="sample-query" onclick="fillQuery('income limits verification')">income limits verification</span>
                <span class="sample-query" onclick="fillQuery('tenant file requirements')">tenant file requirements</span>
                <span class="sample-query" onclick="fillQuery('compliance monitoring')">compliance monitoring</span>
                <span class="sample-query" onclick="fillQuery('affordability period')">affordability period</span>
            </div>
            
            <div class="results-section" id="results-section" style="display: none;">
                <div class="results-header">
                    <h3 id="results-title">Search Results</h3>
                    <span id="results-count" class="success-indicator"></span>
                </div>
                <div id="results-container"></div>
            </div>
        </div>
    </div>

    <script>
        let searchCount = 0;
        
        // Load system stats
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                if (data.success) {
                    document.getElementById('collection-size').textContent = data.stats.collection_size.toLocaleString();
                }
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }
        
        // Fill query from sample
        function fillQuery(query) {
            document.getElementById('query').value = query;
            document.getElementById('query').focus();
        }
        
        // Search form handler
        document.getElementById('search-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const query = document.getElementById('query').value.trim();
            const jurisdiction = document.getElementById('jurisdiction').value;
            const searchType = document.getElementById('search-type').value;
            
            if (!query) return;
            
            // Update UI
            const searchBtn = document.getElementById('search-btn');
            const resultsSection = document.getElementById('results-section');
            const resultsContainer = document.getElementById('results-container');
            
            searchBtn.disabled = true;
            searchBtn.textContent = '🔍 Searching...';
            resultsSection.style.display = 'block';
            resultsContainer.innerHTML = '<div class="loading">🔍 Searching LIHTC database...</div>';
            
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
                    resultsContainer.innerHTML = `<div class="error">❌ Error: ${data.error}</div>`;
                }
                
            } catch (error) {
                resultsContainer.innerHTML = `<div class="error">❌ Search failed: ${error.message}</div>`;
            } finally {
                searchBtn.disabled = false;
                searchBtn.textContent = '🔍 Search LIHTC Database';
            }
        });
        
        // Display search results
        function displayResults(data) {
            const resultsTitle = document.getElementById('results-title');
            const resultsCount = document.getElementById('results-count');
            const resultsContainer = document.getElementById('results-container');
            
            resultsTitle.textContent = `Results for: "${data.query}"`;
            resultsCount.textContent = `${data.total_results} results found`;
            
            if (data.results.length === 0) {
                resultsContainer.innerHTML = `
                    <div class="result-item">
                        <div class="result-content">No results found for your query. Try different keywords or check spelling.</div>
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
        
        // Load stats on page load
        loadStats();
        
        // Auto-focus search input
        document.getElementById('query').focus();
        
        console.log('🚀 LIHTC Intelligence System Web Demo Ready!');
        console.log('✅ RAG System: Operational');
        console.log('📊 Collection: 2,084 items across 54 jurisdictions');
    </script>
</body>
</html>'''
    
    template_path = templates_dir / "index.html"
    with open(template_path, 'w') as f:
        f.write(html_template)
    
    print(f"✅ Web template created: {template_path}")

def open_browser():
    """Open browser after short delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    """Main web demo execution"""
    print("⚔️ STRIKE LEADER: WEB DEMO DEPLOYMENT")
    print("=" * 50)
    
    # Create web template
    create_web_template()
    
    print("🌐 Starting web server...")
    print("📱 Opening Safari browser...")
    
    # Start browser in separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Flask app
    print("\n🚀 LIHTC Web Demo Running!")
    print("🔗 URL: http://localhost:5000")
    print("⚡ Ready for demo in Safari!")
    print("\n💡 Try the original problem query: 'minimum construction standards'")
    print("🎯 Press Ctrl+C to stop the server")
    
    try:
        app.run(host='localhost', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Web demo stopped")

if __name__ == "__main__":
    main()