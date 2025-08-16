#!/usr/bin/env python3
"""
BOTN API Server - Web interface for BOTN file creation
Provides HTTP endpoints for the standalone HTML interface

Author: Claude Code Assistant  
Date: 2025-08-04
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from botn_file_creator import BOTNFileCreator

app = Flask(__name__)
CORS(app)  # Enable CORS for standalone HTML access

# Initialize BOTN creator
botn_creator = BOTNFileCreator()

@app.route('/api/create-botn', methods=['POST'])
def create_botn_api():
    """
    API endpoint to create BOTN file
    
    Expected JSON payload:
    {
        "deal_name": "Sunset Gardens - El Cajon, CA",
        "extracted_data": { ... property data ... }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        deal_name = data.get('deal_name')
        extracted_data = data.get('extracted_data', {})
        
        if not deal_name:
            return jsonify({
                "success": False,
                "error": "deal_name is required"
            }), 400
        
        print(f"\n🔥 API Request: Creating BOTN for {deal_name}")
        
        # Create the BOTN file
        result = botn_creator.create_botn_file(deal_name, extracted_data)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": result["message"],
                "file_path": result["file_path"],
                "filename": result["filename"],
                "folder": result["folder"]
            })
        else:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500
            
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/api/deals', methods=['GET'])
def get_deals():
    """Get list of available deals from cache directory"""
    try:
        cache_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/workforce_analyst/deal_cache"
        
        deals = []
        if os.path.exists(cache_dir):
            for filename in os.listdir(cache_dir):
                if filename.endswith('.json'):
                    # Remove .json extension and convert filename to deal name
                    deal_name = filename[:-5].replace('-', ' - ').replace('_', ' ')
                    deals.append(deal_name)
        
        return jsonify({
            "success": True,
            "deals": sorted(deals)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/deal-data/<path:deal_name>', methods=['GET'])
def get_deal_data(deal_name):
    """Get cached data for a specific deal"""
    try:
        cache_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/workforce_analyst/deal_cache"
        
        # Convert deal name to filename
        filename = deal_name.replace(' - ', '-').replace(' ', '-') + '.json'
        file_path = os.path.join(cache_dir, filename)
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            return jsonify({
                "success": True,
                "data": data.get("data", {}),
                "deal_name": data.get("deal_name", deal_name)
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Deal data not found: {deal_name}"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    """API status endpoint"""
    return jsonify({
        "success": True,
        "message": "BOTN API server is running",
        "endpoints": [
            "POST /api/create-botn - Create BOTN file",
            "GET /api/deals - List available deals", 
            "GET /api/deal-data/<deal_name> - Get deal data",
            "GET /api/status - API status"
        ]
    })

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return """
    <h1>🏢 BOTN File Creator API</h1>
    <p>Real Estate Deal Underwriting Assistant - Backend API</p>
    <h3>Available Endpoints:</h3>
    <ul>
        <li><code>POST /api/create-botn</code> - Create BOTN file</li>
        <li><code>GET /api/deals</code> - List available deals</li>
        <li><code>GET /api/deal-data/&lt;deal_name&gt;</code> - Get deal data</li>
        <li><code>GET /api/status</code> - API status</li>
    </ul>
    <p>Use with the standalone HTML interface for complete BOTN file creation.</p>
    """

if __name__ == '__main__':
    print("🚀 Starting BOTN API server...")
    print("📁 Verifying paths...")
    
    # Verify creator setup
    botn_creator.verify_paths()
    
    print("✅ BOTN API server ready!")
    print("🌐 Access at: http://localhost:5002")
    print("📋 API Status: http://localhost:5002/api/status")
    
    app.run(host='0.0.0.0', port=5002, debug=True)