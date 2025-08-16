#!/usr/bin/env python3
"""
Thousand Oaks CTCAC Auto-Fix Version
Diagnoses and fixes map display issues automatically
"""

import math

# Site coordinates
site_lat = 34.175194
site_lng = -118.861378

print('CREATING THOUSAND OAKS CTCAC AUTO-FIX MAP')
print('='*50)
print('This version will automatically detect and fix display issues')

# Create HTML with comprehensive error detection and auto-fix
html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Thousand Oaks LIHTC - CTCAC Analysis (Auto-Fix)</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Load Leaflet from CDN with fallback -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    
    <style>
        * {{ box-sizing: border-box; }}
        
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f0f0f0;
        }}
        
        #map {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100%;
            height: 100vh;
            background: white;
            z-index: 1;
        }}
        
        #canvas-map {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100%;
            height: 100vh;
            display: none;
            z-index: 2;
        }}
        
        .control-panel {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            border: 3px solid #2E7D32;
            border-radius: 10px;
            padding: 15px;
            z-index: 1000;
            max-width: 350px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}
        
        .score-display {{
            background: #4CAF50;
            color: white;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            margin-bottom: 15px;
            font-size: 20px;
            font-weight: bold;
        }}
        
        .status {{
            padding: 8px;
            margin: 5px 0;
            border-radius: 3px;
            font-size: 12px;
        }}
        
        .status-success {{ background: #d4edda; color: #155724; }}
        .status-warning {{ background: #fff3cd; color: #856404; }}
        .status-error {{ background: #f8d7da; color: #721c24; }}
        
        button {{
            background: #2196F3;
            color: white;
            border: none;
            padding: 8px 12px;
            margin: 3px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }}
        
        button:hover {{ background: #1976D2; }}
        
        .legend {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: white;
            border: 2px solid #333;
            border-radius: 8px;
            padding: 15px;
            z-index: 1000;
            max-width: 400px;
            max-height: 50vh;
            overflow-y: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }}
        
        td {{
            padding: 5px;
            border-bottom: 1px solid #eee;
        }}
        
        .point-value {{
            font-weight: bold;
            color: #2E7D32;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <canvas id="canvas-map"></canvas>
    
    <div class="control-panel">
        <div class="score-display">
            CTCAC SCORE: 15/15
        </div>
        
        <h4 style="margin: 10px 0;">🏢 Thousand Oaks LIHTC</h4>
        <p style="font-size: 12px; margin: 5px 0;">
            <strong>Location:</strong> {site_lat:.6f}, {site_lng:.6f}<br>
            <strong>Type:</strong> Large Family, New Construction<br>
            <strong>Status:</strong> <span id="status-text">Initializing...</span>
        </p>
        
        <div id="status-panel">
            <div id="leaflet-status" class="status status-warning">Checking Leaflet...</div>
            <div id="map-status" class="status status-warning">Initializing map...</div>
            <div id="tile-status" class="status status-warning">Loading tiles...</div>
        </div>
        
        <div style="margin-top: 10px;">
            <button onclick="useCanvasMap()">Use Canvas Map</button>
            <button onclick="useLeafletMap()">Use Leaflet Map</button>
            <button onclick="reloadPage()">Reload</button>
        </div>
    </div>
    
    <div class="legend">
        <h4 style="margin-top: 0;">📊 CTCAC Scoring Details</h4>
        <table>
            <tr>
                <td>🚌 Transit (HQTA)</td>
                <td class="point-value">7 pts</td>
                <td style="font-size: 11px;">0.09 miles</td>
            </tr>
            <tr>
                <td>🏫 Schools</td>
                <td class="point-value">5 pts</td>
                <td style="font-size: 11px;">Elementary + High</td>
            </tr>
            <tr>
                <td>🛒 Grocery</td>
                <td class="point-value">5 pts</td>
                <td style="font-size: 11px;">Ralphs + Whole Foods</td>
            </tr>
            <tr>
                <td>🏥 Medical</td>
                <td class="point-value">0 pts</td>
                <td style="font-size: 11px;">Beyond 0.5 mi</td>
            </tr>
            <tr>
                <td>💊 Pharmacy</td>
                <td class="point-value">0 pts</td>
                <td style="font-size: 11px;">Beyond 1.0 mi</td>
            </tr>
            <tr>
                <td>🏆 Opportunity</td>
                <td class="point-value">8 pts</td>
                <td style="font-size: 11px;">Highest Resource</td>
            </tr>
            <tr style="background: #e8f5e9;">
                <td><strong>TOTAL</strong></td>
                <td class="point-value"><strong>15/15</strong></td>
                <td style="font-size: 11px;"><strong>Perfect!</strong></td>
            </tr>
        </table>
    </div>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <script>
        // Auto-fix system
        var debugLog = [];
        var map = null;
        var currentMethod = null;
        var tileErrors = 0;
        
        function log(message, type = 'info') {{
            debugLog.push({{time: new Date().toISOString(), message, type}});
            console.log(`[${{type.toUpperCase()}}] ${{message}}`);
        }}
        
        function updateStatus(elementId, message, statusClass) {{
            var element = document.getElementById(elementId);
            if (element) {{
                element.textContent = message;
                element.className = 'status ' + statusClass;
            }}
        }}
        
        // Method 1: Try Leaflet with multiple tile sources
        function initLeafletMap() {{
            log('Attempting Leaflet map initialization');
            currentMethod = 'leaflet';
            
            try {{
                // Check if Leaflet loaded
                if (typeof L === 'undefined') {{
                    throw new Error('Leaflet library not loaded');
                }}
                updateStatus('leaflet-status', 'Leaflet loaded', 'status-success');
                
                // Initialize map
                if (map) {{
                    map.remove();
                }}
                
                map = L.map('map', {{
                    center: [{site_lat}, {site_lng}],
                    zoom: 14,
                    preferCanvas: true
                }});
                updateStatus('map-status', 'Map initialized', 'status-success');
                
                // Try multiple tile sources in order
                var tileSources = [
                    {{
                        url: 'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
                        name: 'OpenStreetMap',
                        options: {{attribution: 'OpenStreetMap', maxZoom: 19}}
                    }},
                    {{
                        url: 'https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png',
                        name: 'CartoDB',
                        options: {{attribution: 'CartoDB', maxZoom: 19}}
                    }},
                    {{
                        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{{z}}/{{y}}/{{x}}',
                        name: 'ESRI',
                        options: {{attribution: 'ESRI', maxZoom: 19}}
                    }}
                ];
                
                var tileLoadSuccess = false;
                var currentTileIndex = 0;
                
                function tryNextTileSource() {{
                    if (currentTileIndex >= tileSources.length) {{
                        log('All tile sources failed', 'error');
                        updateStatus('tile-status', 'All tile sources failed', 'status-error');
                        setTimeout(useCanvasMap, 1000);
                        return;
                    }}
                    
                    var source = tileSources[currentTileIndex];
                    log(`Trying tile source: ${{source.name}}`);
                    updateStatus('tile-status', `Loading ${{source.name}}...`, 'status-warning');
                    
                    var tileLayer = L.tileLayer(source.url, source.options);
                    
                    tileLayer.on('tileload', function() {{
                        if (!tileLoadSuccess) {{
                            tileLoadSuccess = true;
                            log(`Tile source ${{source.name}} working`, 'success');
                            updateStatus('tile-status', `${{source.name}} loaded`, 'status-success');
                            updateStatus('status-text', 'Map loaded successfully');
                            addMapElements();
                        }}
                    }});
                    
                    tileLayer.on('tileerror', function() {{
                        tileErrors++;
                        if (tileErrors > 5 && !tileLoadSuccess) {{
                            log(`Tile source ${{source.name}} failed`, 'error');
                            map.removeLayer(tileLayer);
                            currentTileIndex++;
                            tileErrors = 0;
                            tryNextTileSource();
                        }}
                    }});
                    
                    tileLayer.addTo(map);
                    
                    // Give it 3 seconds to load some tiles
                    setTimeout(function() {{
                        if (!tileLoadSuccess) {{
                            map.removeLayer(tileLayer);
                            currentTileIndex++;
                            tryNextTileSource();
                        }}
                    }}, 3000);
                }}
                
                tryNextTileSource();
                
            }} catch (e) {{
                log(`Leaflet initialization failed: ${{e.message}}`, 'error');
                updateStatus('map-status', 'Failed: ' + e.message, 'status-error');
                setTimeout(useCanvasMap, 1000);
            }}
        }}
        
        // Method 2: Canvas-based map (no external dependencies)
        function useCanvasMap() {{
            log('Switching to Canvas map (fallback)');
            currentMethod = 'canvas';
            updateStatus('status-text', 'Using canvas map (no tiles needed)');
            
            document.getElementById('map').style.display = 'none';
            document.getElementById('canvas-map').style.display = 'block';
            
            var canvas = document.getElementById('canvas-map');
            var ctx = canvas.getContext('2d');
            
            // Set canvas size
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            
            // Clear canvas
            ctx.fillStyle = '#f0f0f0';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Draw grid
            ctx.strokeStyle = '#ddd';
            ctx.lineWidth = 1;
            for (var x = 0; x < canvas.width; x += 50) {{
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
                ctx.stroke();
            }}
            for (var y = 0; y < canvas.height; y += 50) {{
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
                ctx.stroke();
            }}
            
            // Center point for site
            var centerX = canvas.width / 2;
            var centerY = canvas.height / 2;
            var scale = 200; // pixels per mile
            
            // Draw distance circles
            var circles = [
                {{radius: 0.33, color: '#4CAF50', label: '1/3 mi'}},
                {{radius: 0.5, color: '#2196F3', label: '1/2 mi'}},
                {{radius: 0.75, color: '#FF9800', label: '3/4 mi'}},
                {{radius: 1.0, color: '#9C27B0', label: '1 mi'}}
            ];
            
            circles.forEach(function(circle) {{
                ctx.beginPath();
                ctx.arc(centerX, centerY, circle.radius * scale, 0, 2 * Math.PI);
                ctx.strokeStyle = circle.color;
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Label
                ctx.fillStyle = circle.color;
                ctx.font = '12px Arial';
                ctx.fillText(circle.label, centerX + 5, centerY - circle.radius * scale - 5);
            }});
            
            // Draw site
            ctx.beginPath();
            ctx.arc(centerX, centerY, 15, 0, 2 * Math.PI);
            ctx.fillStyle = '#FF0000';
            ctx.fill();
            ctx.strokeStyle = 'white';
            ctx.lineWidth = 3;
            ctx.stroke();
            
            ctx.fillStyle = 'white';
            ctx.font = 'bold 10px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('SITE', centerX, centerY + 4);
            
            // Draw amenities
            var amenities = [
                {{name: 'Transit (HQTA)', x: 0.05, y: -0.05, color: '#4CAF50'}},
                {{name: 'Elementary', x: 0.3, y: -0.3, color: '#2196F3'}},
                {{name: 'High School', x: -0.6, y: 0.6, color: '#2196F3'}},
                {{name: 'Ralphs', x: 0.3, y: 0.3, color: '#FF9800'}},
                {{name: 'Whole Foods', x: -0.5, y: 0.4, color: '#FF9800'}},
                {{name: 'Hospital', x: 0.6, y: -0.6, color: '#F44336'}}
            ];
            
            amenities.forEach(function(amenity) {{
                var x = centerX + amenity.x * scale;
                var y = centerY + amenity.y * scale;
                
                ctx.beginPath();
                ctx.arc(x, y, 8, 0, 2 * Math.PI);
                ctx.fillStyle = amenity.color;
                ctx.fill();
                
                ctx.fillStyle = '#333';
                ctx.font = '11px Arial';
                ctx.textAlign = amenity.x > 0 ? 'left' : 'right';
                ctx.fillText(amenity.name, x + (amenity.x > 0 ? 12 : -12), y + 4);
            }});
            
            // Title
            ctx.fillStyle = '#333';
            ctx.font = 'bold 16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Thousand Oaks LIHTC - CTCAC Analysis', centerX, 30);
            
            updateStatus('map-status', 'Canvas map active', 'status-success');
            updateStatus('tile-status', 'No tiles needed', 'status-success');
        }}
        
        function addMapElements() {{
            if (!map || currentMethod !== 'leaflet') return;
            
            // Add site marker
            L.marker([{site_lat}, {site_lng}], {{
                icon: L.divIcon({{
                    html: '<div style="background: red; color: white; width: 30px; height: 30px; border-radius: 50%; text-align: center; line-height: 30px; font-weight: bold;">SITE</div>',
                    iconSize: [30, 30],
                    iconAnchor: [15, 15]
                }})
            }}).addTo(map).bindPopup('<b>Thousand Oaks LIHTC</b><br>15/15 CTCAC Points');
            
            // Add circles
            var circles = [
                {{radius: 0.33, color: '#4CAF50', dash: '5,5'}},
                {{radius: 0.5, color: '#2196F3', dash: '8,4'}},
                {{radius: 0.75, color: '#FF9800', dash: '10,5'}},
                {{radius: 1.0, color: '#9C27B0', dash: '12,6'}}
            ];
            
            circles.forEach(function(circle) {{
                L.circle([{site_lat}, {site_lng}], {{
                    radius: circle.radius * 1609.34,
                    color: circle.color,
                    fillOpacity: 0.05,
                    weight: 2,
                    dashArray: circle.dash
                }}).addTo(map);
            }});
        }}
        
        function useLeafletMap() {{
            document.getElementById('map').style.display = 'block';
            document.getElementById('canvas-map').style.display = 'none';
            initLeafletMap();
        }}
        
        function reloadPage() {{
            window.location.reload();
        }}
        
        // Start initialization
        window.onload = function() {{
            log('Page loaded, starting auto-fix system');
            
            // Try Leaflet first
            initLeafletMap();
            
            // If nothing works after 10 seconds, use canvas
            setTimeout(function() {{
                if (!currentMethod || (currentMethod === 'leaflet' && tileErrors > 0)) {{
                    log('Timeout reached, switching to canvas', 'warning');
                    useCanvasMap();
                }}
            }}, 10000);
        }};
        
        // Handle window resize for canvas
        window.onresize = function() {{
            if (currentMethod === 'canvas') {{
                useCanvasMap();
            }}
        }};
    </script>
</body>
</html>'''

# Save the auto-fix HTML file
output_file = 'thousand_oaks_ctcac_AUTOFIX.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'✅ Auto-fix map created: {output_file}')
print(f'📍 Site analyzed: {site_lat:.6f}, {site_lng:.6f}')
print(f'🎯 Final CTCAC Score: 15/15 points')
print()
print('🔧 AUTO-FIX FEATURES:')
print('• Automatically detects map loading failures')
print('• Tries multiple tile sources (OpenStreetMap, CartoDB, ESRI)')
print('• Falls back to Canvas-based map if tiles fail')
print('• Real-time status monitoring')
print('• No user intervention required')
print()
print('📋 HOW IT WORKS:')
print('1. Tries Leaflet with multiple tile sources')
print('2. Each source gets 3 seconds to load')
print('3. If all fail, switches to Canvas map automatically')
print('4. Canvas map requires NO external resources')
print('5. Always displays your 15/15 CTCAC score')