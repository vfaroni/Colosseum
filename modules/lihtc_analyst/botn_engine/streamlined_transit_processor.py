#!/usr/bin/env python3
"""
Streamlined Transit Processor - Fast Production Version

Focused on getting results quickly from the 90,924 transit stops database
for our 263 filtered sites.
"""

import json
import pandas as pd
import math
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in miles using Haversine formula"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return 3959 * c  # Earth radius in miles

def calculate_ctcac_score(nearby_stops: List[Dict]) -> Dict[str, Any]:
    """Calculate CTCAC-compliant transit score"""
    # Count stops by distance
    quarter_mile = len([s for s in nearby_stops if s['distance_miles'] <= 0.25])
    half_mile = len([s for s in nearby_stops if s['distance_miles'] <= 0.5])
    
    if not nearby_stops:
        return {
            'total_points': 0, 
            'details': 'No transit stops found',
            'stops_quarter_mile': 0,
            'stops_half_mile': 0
        }
    
    # CTCAC scoring (simplified)
    if quarter_mile >= 5:
        points = 7
        detail = f"7 points: {quarter_mile} stops within 0.25 miles"
    elif quarter_mile >= 3:
        points = 5
        detail = f"5 points: {quarter_mile} stops within 0.25 miles"
    elif quarter_mile >= 1:
        points = 3
        detail = f"3 points: {quarter_mile} stops within 0.25 miles"
    else:
        points = 0
        detail = "0 points: No stops within 0.25 miles"
    
    return {
        'total_points': points,
        'details': detail,
        'stops_quarter_mile': quarter_mile,
        'stops_half_mile': half_mile
    }

def main():
    """Main processing function"""
    logger.info("🚀 WINGMAN Streamlined Transit Analysis")
    logger.info("🚌 Processing 90,924 CA transit stops for 263 sites")
    
    # Define paths
    base_dir = Path(__file__).parent
    portfolio_file = base_dir / "Sites/BOTN_TRANSIT_ANALYSIS_INPUT_BACKUP_20250731_211324.xlsx"
    transit_file = base_dir.parent / "priorcode/!VFupload/CALIHTCScorer/data/transit/california_transit_stops_master.geojson"
    output_dir = base_dir / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Load portfolio
        logger.info(f"📂 Loading portfolio: {portfolio_file.name}")
        df = pd.read_excel(portfolio_file)
        logger.info(f"📊 Loaded {len(df)} sites")
        
        # Load transit data
        logger.info(f"🚌 Loading transit data: {transit_file.name} ({transit_file.stat().st_size / (1024*1024):.1f} MB)")
        with open(transit_file, 'r') as f:
            transit_data = json.load(f)
        
        transit_stops = transit_data['features']
        logger.info(f"✅ Loaded {len(transit_stops)} transit stops")
        
        # Process each site
        results = []
        successful_analyses = 0
        
        for idx, row in df.iterrows():
            site_id = f"site_{idx:04d}"
            lat, lon = float(row['Latitude']), float(row['Longitude'])
            
            # Find nearby transit stops (within 3 miles)
            nearby_stops = []
            for stop_idx, stop in enumerate(transit_stops):
                if stop['geometry']['type'] != 'Point':
                    continue
                
                stop_coords = stop['geometry']['coordinates']
                stop_lon, stop_lat = stop_coords[0], stop_coords[1]
                
                distance = haversine_distance(lat, lon, stop_lat, stop_lon)
                
                if distance <= 3.0:  # 3 mile radius
                    nearby_stops.append({
                        'stop_id': stop_idx,
                        'distance_miles': round(distance, 3),
                        'stop_name': stop['properties'].get('stop_name', 'Unknown'),
                        'stop_lat': stop_lat,
                        'stop_lon': stop_lon
                    })
            
            # Sort by distance
            nearby_stops.sort(key=lambda x: x['distance_miles'])
            
            # Calculate score
            score_data = calculate_ctcac_score(nearby_stops)
            
            # Compile result
            result = {
                'site_id': site_id,
                'latitude': lat,
                'longitude': lon,
                'transit_stops_found': len(nearby_stops),
                'closest_stop_distance': nearby_stops[0]['distance_miles'] if nearby_stops else None,
                'ctcac_score': score_data['total_points'],
                'score_details': score_data['details'],
                'stops_quarter_mile': score_data['stops_quarter_mile'],
                'stops_half_mile': score_data['stops_half_mile'],
                'top_5_stops': nearby_stops[:5]
            }
            
            results.append(result)
            if len(nearby_stops) > 0:
                successful_analyses += 1
            
            # Progress update
            if (idx + 1) % 50 == 0 or idx == len(df) - 1:
                logger.info(f"📈 Progress: {idx+1}/{len(df)} sites processed")
        
        # Generate summary
        scores = [r['ctcac_score'] for r in results]
        summary = {
            'total_sites': len(results),
            'sites_with_transit': successful_analyses,
            'average_score': round(sum(scores) / len(scores), 2),
            'max_score': max(scores),
            'high_scoring_sites': len([s for s in scores if s >= 5]),
            'zero_score_sites': len([s for s in scores if s == 0])
        }
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Detailed JSON
        json_file = output_dir / f"STREAMLINED_TRANSIT_ANALYSIS_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump({
                'summary': summary,
                'results': results,
                'metadata': {
                    'analysis_timestamp': timestamp,
                    'transit_database_size': len(transit_stops),
                    'processing_mode': 'Streamlined JSON'
                }
            }, f, indent=2)
        
        # Excel summary
        excel_file = output_dir / f"STREAMLINED_TRANSIT_SUMMARY_{timestamp}.xlsx"
        df_results = pd.DataFrame([{
            'Site_ID': r['site_id'],
            'Latitude': r['latitude'],
            'Longitude': r['longitude'],
            'Transit_Stops_Found': r['transit_stops_found'],
            'Closest_Stop_Miles': r['closest_stop_distance'],
            'CTCAC_Score': r['ctcac_score'],
            'Score_Details': r['score_details'],
            'Stops_Quarter_Mile': r['stops_quarter_mile'],
            'Stops_Half_Mile': r['stops_half_mile']
        } for r in results])
        
        df_results.to_excel(excel_file, index=False)
        
        # Final summary
        logger.info("\n" + "="*60)
        logger.info("🎉 STREAMLINED TRANSIT ANALYSIS COMPLETE!")
        logger.info("="*60)
        logger.info(f"📊 Sites Processed: {summary['total_sites']}")
        logger.info(f"🚌 Sites with Transit: {summary['sites_with_transit']}")
        logger.info(f"📈 Average Score: {summary['average_score']}")
        logger.info(f"🎯 High-Scoring Sites: {summary['high_scoring_sites']}")
        logger.info(f"📄 Results: {json_file.name}")
        logger.info(f"📊 Summary: {excel_file.name}")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🏛️ ROMAN STANDARD: Transit Analysis Mission Complete!")
    else:
        print("\n❌ Mission Failed")
        exit(1)