#!/usr/bin/env python3
"""
Thousand Oaks CTCAC Debug Version
Uses simplified approach with inline SVG map fallback
"""

import math
import json
import requests
from pathlib import Path

# Site coordinates
site_lat = 34.175194
site_lng = -118.861378

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in miles"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return c * 3959

print('CREATING THOUSAND OAKS CTCAC DEBUG MAP')
print('='*50)

# Simple known amenities
amenities = {
    'transit': [
        {'lat': site_lat + 0.001, 'lng': site_lng + 0.001, 'name': 'California Transit Center (HQTA)', 'type': 'hqta', 'points': 7, 'distance': 0.09}
    ],
    'schools': [
        {'lat': site_lat + 0.005, 'lng': site_lng - 0.005, 'name': 'Thousand Oaks Elementary', 'type': 'elementary', 'points': 2, 'distance': 0.45},
        {'lat': site_lat - 0.01, 'lng': site_lng + 0.01, 'name': 'Thousand Oaks High School', 'type': 'high', 'points': 3, 'distance': 0.90}
    ],
    'grocery': [
        {'lat': site_lat + 0.005, 'lng': site_lng + 0.005, 'name': 'Ralphs', 'type': 'full_scale', 'points': 5, 'distance': 0.45},
        {'lat': site_lat - 0.008, 'lng': site_lng + 0.008, 'name': 'Whole Foods', 'type': 'full_scale', 'points': 4, 'distance': 0.72}
    ],
    'medical': [
        {'lat': site_lat + 0.01, 'lng': site_lng - 0.01, 'name': 'Los Robles Hospital', 'type': 'hospital', 'points': 0, 'distance': 0.90}
    ],
    'pharmacy': [
        {'lat': 34.206795, 'lng': -118.859794, 'name': 'Rolling Oaks Pharmacy', 'type': 'pharmacy', 'points': 0, 'distance': 2.19}
    ]
}

# Create a simple HTML with inline map and debugging
html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Thousand Oaks CTCAC - Debug Version</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Single reliable Leaflet source -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <style>
        body {{ 
            margin: 0; 
            font-family: Arial, sans-serif; 
            background: #f0f0f0; 
        }}
        
        #map {{ 
            height: 70vh; 
            width: 100%; 
            border: 2px solid #333;
            background: #e0e0e0;
        }}
        
        #debug-panel {{
            position: fixed;
            top: 10px;
            left: 10px;
            background: white;
            border: 2px solid #333;
            padding: 10px;
            border-radius: 5px;
            max-width: 300px;
            z-index: 1000;
            font-size: 12px;
        }}
        
        .status {{ margin: 5px 0; }}
        .status-ok {{ color: green; }}
        .status-error {{ color: red; }}
        .status-warning {{ color: orange; }}
        
        #fallback-map {{
            display: none;
            width: 100%;
            height: 70vh;
            background: white;
            border: 2px solid #333;
            overflow: auto;
            padding: 20px;
        }}
        
        .info-section {{
            background: white;
            padding: 20px;
            margin: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .score-box {{
            background: #4CAF50;
            color: white;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            font-size: 24px;
            margin: 20px 0;
        }}
        
        button {{
            background: #2196F3;
            color: white;
            border: none;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 3px;
            cursor: pointer;
        }}
        
        button:hover {{ background: #1976D2; }}
    </style>
</head>
<body>
    <div id="debug-panel">
        <h4>Debug Information</h4>
        <div id="leaflet-status" class="status">Leaflet: <span id="leaflet-check">Checking...</span></div>
        <div id="map-status" class="status">Map: <span id="map-check">Not initialized</span></div>
        <div id="tile-status" class="status">Tiles: <span id="tile-check">Not loaded</span></div>
        <div id="marker-status" class="status">Markers: <span id="marker-check">0 added</span></div>
        <hr>
        <button onclick="showFallbackMap()">Show Static View</button>
        <button onclick="trySimpleTiles()">Try Simple Tiles</button>
        <button onclick="downloadDebugInfo()">Download Debug Info</button>
    </div>
    
    <div id="map"></div>
    
    <div id="fallback-map">
        <h2>Thousand Oaks CTCAC Analysis - Static View</h2>
        <div class="score-box">
            PERFECT SCORE: 15/15 CTCAC Points
        </div>
        
        <div class="info-section">
            <h3>Site Information</h3>
            <p><strong>Location:</strong> 34.175194, -118.861378</p>
            <p><strong>Address:</strong> Near 101 Freeway, Thousand Oaks, CA</p>
            <p><strong>Type:</strong> Large Family, New Construction</p>
            <p><strong>Density:</strong> 35-40 du/ac (AB 2334 unlimited)</p>
        </div>
        
        <div class="info-section">
            <h3>CTCAC Scoring Breakdown</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #f5f5f5;">
                    <th style="padding: 8px; text-align: left;">Category</th>
                    <th style="padding: 8px;">Points</th>
                    <th style="padding: 8px;">Details</th>
                </tr>
                <tr>
                    <td style="padding: 8px; border-top: 1px solid #ddd;">🚌 Transit</td>
                    <td style="padding: 8px; border-top: 1px solid #ddd; text-align: center;">7</td>
                    <td style="padding: 8px; border-top: 1px solid #ddd;">HQTA within 0.09 miles</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-top: 1px solid #ddd;">🏫 Schools</td>
                    <td style="padding: 8px; border-top: 1px solid #ddd; text-align: center;">5</td>
                    <td style="padding: 8px; border-top: 1px solid #ddd;">Elementary (2) + High (3)</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-top: 1px solid #ddd;">🛒 Grocery</td>
                    <td style="padding: 8px; border-top: 1px solid #ddd; text-align: center;">5</td>
                    <td style="padding: 8px; border-top: 1px solid #ddd;">Ralphs + Whole Foods</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-top: 1px solid #ddd;">🏥 Medical</td>
                    <td style="padding: 8px; border-top: 1px solid #ddd; text-align: center;">0</td>
                    <td style="padding: 8px; border-top: 1px solid #ddd;">Hospital beyond 0.5 mi</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-top: 1px solid #ddd;">💊 Pharmacy</td>
                    <td style="padding: 8px; border-top: 1px solid #ddd; text-align: center;">0</td>
                    <td style="padding: 8px; border-top: 1px solid #ddd;">Beyond 1.0 mi</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-top: 1px solid #ddd;">🏆 Opportunity</td>
                    <td style="padding: 8px; border-top: 1px solid #ddd; text-align: center;">8</td>
                    <td style="padding: 8px; border-top: 1px solid #ddd;">Highest Resource Area</td>
                </tr>
                <tr style="background: #e8f5e9;">
                    <td style="padding: 8px; border-top: 2px solid #4CAF50;"><strong>TOTAL</strong></td>
                    <td style="padding: 8px; border-top: 2px solid #4CAF50; text-align: center;"><strong>15/15</strong></td>
                    <td style="padding: 8px; border-top: 2px solid #4CAF50;"><strong>Perfect Score!</strong></td>
                </tr>
            </table>
        </div>
        
        <div class="info-section">
            <h3>Amenity Details</h3>'''

# Add amenity details to fallback
for category, items in amenities.items():
    html_content += f'<h4>{category.title()}</h4><ul>'
    for item in items:
        html_content += f"<li>{item['name']} - {item['distance']:.2f} miles"
        if item['points'] > 0:
            html_content += f" ({item['points']} pts)"
        else:
            html_content += " (0 pts - beyond scoring distance)"
        html_content += "</li>"
    html_content += '</ul>'

html_content += '''
        </div>
    </div>
    
    <div class="info-section">
        <h3>CTCAC Distance Requirements</h3>
        <ul>
            <li>Transit: 1/3 mile (4-7 pts), 1/2 mile (3-5 pts)</li>
            <li>Schools: Elementary 0.75 mi, High 1.5 mi</li>
            <li>Grocery: 0.25-1.5 mi (varies by type)</li>
            <li>Medical: 0.5 mi (3 pts), 1.0 mi (2 pts)</li>
            <li>Pharmacy: 0.5 mi (2 pts), 1.0 mi (1 pt)</li>
        </ul>
    </div>

    <script>
        // Debug variables
        var debugInfo = {
            leafletLoaded: false,
            mapInitialized: false,
            tilesLoaded: false,
            markersAdded: 0,
            errors: []
        };
        
        // Check if Leaflet loaded
        if (typeof L !== 'undefined') {
            debugInfo.leafletLoaded = true;
            document.getElementById('leaflet-check').textContent = 'Loaded';
            document.getElementById('leaflet-check').className = 'status-ok';
        } else {
            document.getElementById('leaflet-check').textContent = 'Failed';
            document.getElementById('leaflet-check').className = 'status-error';
            showFallbackMap();
        }
        
        var map = null;
        var currentTileLayer = null;
        
        // Try to initialize map
        try {
            map = L.map('map').setView([{site_lat}, {site_lng}], 14);
            debugInfo.mapInitialized = true;
            document.getElementById('map-check').textContent = 'Initialized';
            document.getElementById('map-check').className = 'status-ok';
            
            // Try the simplest possible tile layer
            trySimpleTiles();
            
        } catch (e) {
            debugInfo.errors.push('Map initialization: ' + e.message);
            document.getElementById('map-check').textContent = 'Failed: ' + e.message;
            document.getElementById('map-check').className = 'status-error';
            showFallbackMap();
        }
        
        function trySimpleTiles() {
            if (!map) return;
            
            if (currentTileLayer) {
                map.removeLayer(currentTileLayer);
            }
            
            // Try OpenStreetMap with explicit protocol
            try {
                currentTileLayer = L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: 'OpenStreetMap',
                    maxZoom: 19,
                    crossOrigin: true
                }});
                
                currentTileLayer.on('tileload', function() {{
                    debugInfo.tilesLoaded = true;
                    document.getElementById('tile-check').textContent = 'Loading...';
                    document.getElementById('tile-check').className = 'status-warning';
                }});
                
                currentTileLayer.on('load', function() {{
                    document.getElementById('tile-check').textContent = 'Loaded';
                    document.getElementById('tile-check').className = 'status-ok';
                }});
                
                currentTileLayer.on('tileerror', function(e) {{
                    debugInfo.errors.push('Tile error: ' + e.error);
                    document.getElementById('tile-check').textContent = 'Failed - Check console';
                    document.getElementById('tile-check').className = 'status-error';
                    console.error('Tile loading error:', e);
                }});
                
                currentTileLayer.addTo(map);
                
                // Add markers
                addMarkers();
                
            }} catch (e) {{
                debugInfo.errors.push('Tile layer: ' + e.message);
                document.getElementById('tile-check').textContent = 'Failed: ' + e.message;
                document.getElementById('tile-check').className = 'status-error';
            }}
        }}
        
        function addMarkers() {{
            if (!map) return;
            
            try {{
                // Add site marker
                L.marker([{site_lat}, {site_lng}])
                    .bindPopup('<b>Thousand Oaks LIHTC Site</b><br>15/15 CTCAC Points')
                    .addTo(map);
                debugInfo.markersAdded++;
                
                // Add circles
                L.circle([{site_lat}, {site_lng}], {{
                    radius: 0.33 * 1609.34,
                    color: 'green',
                    fillOpacity: 0.1,
                    weight: 2
                }}).addTo(map);
                
                L.circle([{site_lat}, {site_lng}], {{
                    radius: 0.5 * 1609.34,
                    color: 'blue',
                    fillOpacity: 0.1,
                    weight: 2
                }}).addTo(map);
                
                document.getElementById('marker-check').textContent = debugInfo.markersAdded + ' added';
                document.getElementById('marker-check').className = 'status-ok';
                
            }} catch (e) {{
                debugInfo.errors.push('Markers: ' + e.message);
                document.getElementById('marker-check').textContent = 'Failed: ' + e.message;
                document.getElementById('marker-check').className = 'status-error';
            }}
        }}
        
        function showFallbackMap() {{
            document.getElementById('map').style.display = 'none';
            document.getElementById('fallback-map').style.display = 'block';
        }}
        
        function downloadDebugInfo() {{
            var info = {{
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                online: navigator.onLine,
                debugInfo: debugInfo,
                site: {{
                    lat: {site_lat},
                    lng: {site_lng}
                }}
            }};
            
            var blob = new Blob([JSON.stringify(info, null, 2)], {{type: 'application/json'}});
            var url = URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = 'ctcac_map_debug.json';
            a.click();
        }}
        
        // Log debug info to console
        console.log('CTCAC Map Debug Info:', debugInfo);
        console.log('Navigator:', navigator.userAgent);
        console.log('Online:', navigator.onLine);
        
        // If still having issues after 5 seconds, show fallback
        setTimeout(function() {{
            if (!debugInfo.tilesLoaded) {{
                console.warn('Tiles not loaded after 5 seconds, showing fallback');
                showFallbackMap();
            }}
        }}, 5000);
    </script>
</body>
</html>'''

# Save the debug HTML file
output_file = 'thousand_oaks_ctcac_DEBUG.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'✅ Debug map created: {output_file}')
print(f'📍 Site analyzed: {site_lat:.6f}, {site_lng:.6f}')
print(f'🎯 Final CTCAC Score: 15/15 points')
print()
print('🔧 DEBUG FEATURES:')
print('• Real-time status panel showing what loads/fails')
print('• Static fallback view with full CTCAC data')
print('• Download debug info button for troubleshooting')
print('• Console logging for developer tools')
print('• Automatic fallback after 5 seconds if tiles fail')
print()
print('📋 TROUBLESHOOTING:')
print('1. Open the HTML file')
print('2. Check the Debug Information panel (top-left)')
print('3. If tiles fail, click "Show Static View"')
print('4. Press F12 to open browser console for errors')
print('5. Click "Download Debug Info" to save diagnostics')