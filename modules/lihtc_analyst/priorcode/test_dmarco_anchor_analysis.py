#!/usr/bin/env python3
"""
Quick Test: D'Marco Anchor Analysis
Tests the anchor scoring system on a few D'Marco sites to validate the approach.
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
from geopy.geocoders import Nominatim
from shapely.geometry import Point
import time

def test_anchor_scoring():
    """Test anchor scoring on a sample of D'Marco sites"""
    
    # Load datasets
    base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas")
    
    print("Loading infrastructure datasets...")
    
    # Load schools
    schools_file = base_dir / "TX_Public_Schools" / "Schools_2024_to_2025.geojson"
    schools_gdf = gpd.read_file(schools_file)
    print(f"✅ Loaded {len(schools_gdf)} Texas schools")
    
    # Load cities
    cities_file = base_dir / "City_Boundaries" / "TX_cities_2024.geojson"
    cities_gdf = gpd.read_file(cities_file)
    print(f"✅ Loaded {len(cities_gdf)} Texas cities")
    
    # Load TDHCA projects (fix column names)
    tdhca_file = base_dir / "State Specific" / "TX" / "Project_List" / "TX_TDHCA_Project_List_05252025.xlsx"
    tdhca_df = pd.read_excel(tdhca_file)
    
    # Fix coordinate column names
    tdhca_df = tdhca_df.rename(columns={
        'Latitude11': 'Latitude',
        'Longitude11': 'Longitude'
    })
    tdhca_df = tdhca_df.dropna(subset=['Latitude', 'Longitude'])
    print(f"✅ Loaded {len(tdhca_df)} TDHCA projects with coordinates")
    
    # Load D'Marco sites (just first 5 for testing)
    dmarco_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/From_Brent_06182025.csv"
    df = pd.read_csv(dmarco_file).head(5)
    
    print(f"\n🧪 Testing anchor analysis on {len(df)} D'Marco sites...\n")
    
    # Geocoding
    geolocator = Nominatim(user_agent="test_anchor_analyzer")
    
    results = []
    
    for idx, row in df.iterrows():
        site_name = f"{row['MailingName']} - {row['City']}, {row['County']} County"
        print(f"📍 Analyzing: {site_name}")
        
        # Geocode
        try:
            full_address = f"{row['City']}, {row['County']} County, Texas"
            location = geolocator.geocode(full_address, timeout=10)
            
            if not location:
                print(f"   ❌ Geocoding failed")
                continue
                
            lat, lng = location.latitude, location.longitude
            print(f"   📌 Coordinates: {lat:.4f}, {lng:.4f}")
            
        except Exception as e:
            print(f"   ❌ Geocoding error: {e}")
            continue
        
        # Anchor Analysis
        site_point = Point(lng, lat)
        
        # 1. Schools within 2.5 miles
        schools_nearby = 0
        school_distances = []
        
        for _, school in schools_gdf.iterrows():
            try:
                if school.geometry and not school.geometry.is_empty:
                    distance_deg = site_point.distance(school.geometry)
                    distance_miles = distance_deg * 69  # Rough conversion
                    if distance_miles <= 2.5:
                        schools_nearby += 1
                        school_distances.append(distance_miles)
            except:
                continue
        
        print(f"   🏫 Schools within 2.5 miles: {schools_nearby}")
        
        # 2. City boundaries check
        within_city = False
        city_name = "Unincorporated"
        try:
            site_gdf = gpd.GeoDataFrame([1], geometry=[site_point], crs='EPSG:4326')
            cities_intersect = gpd.sjoin(site_gdf, cities_gdf, how='inner', predicate='within')
            
            if len(cities_intersect) > 0:
                within_city = True
                city_name = cities_intersect.iloc[0]['NAME']
        except:
            pass
        
        print(f"   🏛️ Within city limits: {within_city} ({city_name})")
        
        # 3. Nearby LIHTC projects
        lihtc_nearby = 0
        for _, project in tdhca_df.iterrows():
            try:
                proj_lat = float(project['Latitude'])
                proj_lng = float(project['Longitude'])
                
                # Simple distance calculation
                lat_diff = abs(lat - proj_lat)
                lng_diff = abs(lng - proj_lng)
                distance_approx = ((lat_diff**2 + lng_diff**2)**0.5) * 69
                
                if distance_approx <= 2.0:
                    lihtc_nearby += 1
                    
            except:
                continue
        
        print(f"   💼 LIHTC projects within 2 miles: {lihtc_nearby}")
        
        # 4. Calculate anchor score
        anchor_score = 0
        details = []
        
        if schools_nearby == 0:
            anchor_score = 0
            details.append("❌ FATAL: No schools within 2.5 miles")
        else:
            anchor_score += 2
            details.append(f"✅ {schools_nearby} schools nearby")
            
            if schools_nearby >= 3:
                anchor_score += 1
                details.append("🌟 Multiple schools (established community)")
        
        if within_city:
            anchor_score += 1
            details.append(f"🏛️ Within {city_name}")
        
        if lihtc_nearby > 0:
            anchor_score += 1
            details.append(f"💼 {lihtc_nearby} LIHTC projects (market validation)")
        
        print(f"   🎯 Anchor Score: {anchor_score}/5")
        print(f"   📝 Details: {'; '.join(details)}")
        
        # Assessment
        if anchor_score == 0:
            assessment = "❌ DO NOT PURSUE - Too isolated"
        elif anchor_score <= 2:
            assessment = "⚠️ HIGH RISK - Limited infrastructure"
        elif anchor_score <= 3:
            assessment = "👍 VIABLE - Adequate infrastructure"
        else:
            assessment = "🌟 EXCELLENT - Strong infrastructure"
        
        print(f"   🔍 Assessment: {assessment}")
        print()
        
        results.append({
            'Site': site_name,
            'Coordinates': f"{lat:.4f}, {lng:.4f}",
            'Schools_2_5mi': schools_nearby,
            'Within_City': within_city,
            'City_Name': city_name,
            'LIHTC_2mi': lihtc_nearby,
            'Anchor_Score': anchor_score,
            'Assessment': assessment
        })
        
        time.sleep(1)  # Rate limiting
    
    # Summary
    print("📊 ANCHOR ANALYSIS SUMMARY")
    print("=" * 50)
    
    results_df = pd.DataFrame(results)
    if len(results_df) > 0:
        
        excellent = len(results_df[results_df['Anchor_Score'] >= 4])
        viable = len(results_df[results_df['Anchor_Score'] >= 3])
        risky = len(results_df[(results_df['Anchor_Score'] >= 1) & (results_df['Anchor_Score'] < 3)])
        fatal = len(results_df[results_df['Anchor_Score'] == 0])
        
        print(f"🌟 Excellent infrastructure: {excellent}")
        print(f"👍 Viable infrastructure: {viable}")
        print(f"⚠️ Risky/limited infrastructure: {risky}")
        print(f"❌ Fatal isolation: {fatal}")
        print(f"\n💡 Recommendation: Focus on {viable} sites with scores ≥ 3")
        
        # Save results
        results_df.to_csv("DMarco_Anchor_Test_Results.csv", index=False)
        print(f"\n💾 Results saved to: DMarco_Anchor_Test_Results.csv")
        
        return results_df
    
    else:
        print("❌ No sites successfully analyzed")
        return None

if __name__ == "__main__":
    test_anchor_scoring()