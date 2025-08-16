#!/usr/bin/env python3
"""
PositionStack vs Nominatim Geocoding Comparison
Test all 65 D'Marco addresses with both services and compare accuracy
"""

import pandas as pd
import requests
import time
import json
from datetime import datetime
from pathlib import Path
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import logging
from tdhca_qct_focused_analyzer import TDHCAQCTFocusedAnalyzer

class GeocodingComparison:
    """Compare PositionStack vs Nominatim geocoding accuracy"""
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # PositionStack API key
        self.positionstack_api_key = "41b80ed51d92978904592126d2bb8f7e"  # Updated working key
        
        # Nominatim geocoder
        self.geolocator = Nominatim(user_agent="tdhca_analyzer_comparison")
        
        # QCT/DDA analyzer for testing accuracy
        self.analyzer = TDHCAQCTFocusedAnalyzer()
        
        # Stats tracking
        self.stats = {
            'nominatim': {'success': 0, 'partial': 0, 'fail': 0, 'total': 0},
            'positionstack': {'success': 0, 'partial': 0, 'fail': 0, 'total': 0}
        }
    
    def geocode_with_positionstack(self, address, city, county, max_retries=3):
        """Geocode using PositionStack API"""
        full_address = f"{address}, {city}, {county} County, Texas"
        
        for attempt in range(max_retries):
            try:
                url = "http://api.positionstack.com/v1/forward"
                params = {
                    'access_key': self.positionstack_api_key,
                    'query': full_address,
                    'limit': 1,
                    'country': 'US',
                    'region': 'Texas',
                    'output': 'json'
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('data') and len(data['data']) > 0:
                        result = data['data'][0]
                        
                        # Check confidence score
                        confidence = result.get('confidence', 0)
                        
                        return {
                            'latitude': result['latitude'],
                            'longitude': result['longitude'],
                            'formatted_address': result.get('label', full_address),
                            'confidence': confidence,
                            'accuracy': 'high' if confidence >= 0.8 else 'medium' if confidence >= 0.5 else 'low',
                            'success': True,
                            'method': 'positionstack',
                            'api_response': result
                        }
                    else:
                        self.logger.warning(f"PositionStack: No results for {full_address}")
                
                elif response.status_code == 429:
                    self.logger.warning("PositionStack rate limit hit, waiting...")
                    time.sleep(2)
                    continue
                    
                else:
                    self.logger.error(f"PositionStack API error {response.status_code}: {response.text}")
                
                time.sleep(0.2)  # Rate limiting
                
            except Exception as e:
                self.logger.error(f"PositionStack error for {full_address}: {e}")
                time.sleep(1)
        
        return {
            'latitude': None,
            'longitude': None,
            'formatted_address': 'PositionStack geocoding failed',
            'confidence': 0,
            'accuracy': 'fail',
            'success': False,
            'method': 'positionstack'
        }
    
    def geocode_with_nominatim(self, address, city, county, max_retries=3):
        """Geocode using Nominatim (OpenStreetMap)"""
        full_address = f"{address}, {city}, {county} County, Texas"
        
        for attempt in range(max_retries):
            try:
                location = self.geolocator.geocode(full_address, timeout=10)
                
                if location:
                    return {
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'formatted_address': location.address,
                        'confidence': 1.0,  # Nominatim doesn't provide confidence scores
                        'accuracy': 'high',
                        'success': True,
                        'method': 'nominatim'
                    }
                else:
                    # Try with just city, county if full address fails
                    simple_address = f"{city}, {county} County, Texas"
                    location = self.geolocator.geocode(simple_address, timeout=10)
                    
                    if location:
                        return {
                            'latitude': location.latitude,
                            'longitude': location.longitude,
                            'formatted_address': f"{location.address} (City Center - Address Not Found)",
                            'confidence': 0.5,  # Lower confidence for city center
                            'accuracy': 'medium',
                            'success': False,  # Partial success
                            'method': 'nominatim'
                        }
                
                time.sleep(1)  # Nominatim rate limiting
                
            except Exception as e:
                self.logger.error(f"Nominatim error for {full_address}: {e}")
                time.sleep(2)
        
        return {
            'latitude': None,
            'longitude': None,
            'formatted_address': 'Nominatim geocoding failed',
            'confidence': 0,
            'accuracy': 'fail',
            'success': False,
            'method': 'nominatim'
        }
    
    def compare_geocoding_accuracy(self, lat1, lng1, lat2, lng2):
        """Compare two geocoding results and calculate distance difference"""
        if pd.isna(lat1) or pd.isna(lng1) or pd.isna(lat2) or pd.isna(lng2):
            return None
        
        try:
            distance = geodesic((lat1, lng1), (lat2, lng2)).meters
            return distance
        except:
            return None
    
    def test_qct_dda_with_both_methods(self, nom_lat, nom_lng, ps_lat, ps_lng):
        """Test QCT/DDA status with both geocoding methods"""
        results = {
            'nominatim_qct_dda': 'Unknown',
            'positionstack_qct_dda': 'Unknown',
            'qct_dda_match': False
        }
        
        # Test Nominatim coordinates
        if pd.notna(nom_lat) and pd.notna(nom_lng):
            nom_qct_dda = self.analyzer.check_qct_dda_status(nom_lat, nom_lng)
            results['nominatim_qct_dda'] = nom_qct_dda['status']
        
        # Test PositionStack coordinates  
        if pd.notna(ps_lat) and pd.notna(ps_lng):
            ps_qct_dda = self.analyzer.check_qct_dda_status(ps_lat, ps_lng)
            results['positionstack_qct_dda'] = ps_qct_dda['status']
        
        # Check if they match
        results['qct_dda_match'] = results['nominatim_qct_dda'] == results['positionstack_qct_dda']
        
        return results
    
    def run_comparison(self, csv_file):
        """Run full comparison on all D'Marco sites"""
        self.logger.info(f"Starting geocoding comparison for: {csv_file}")
        
        # Load D'Marco sites
        df = pd.read_csv(csv_file)
        self.logger.info(f"Loaded {len(df)} sites for comparison")
        
        # Initialize comparison columns
        comparison_columns = [
            # Nominatim results
            'Nom_Latitude', 'Nom_Longitude', 'Nom_Address', 'Nom_Accuracy', 'Nom_Success',
            
            # PositionStack results
            'PS_Latitude', 'PS_Longitude', 'PS_Address', 'PS_Confidence', 'PS_Accuracy', 'PS_Success',
            
            # Comparison metrics
            'Distance_Difference_Meters', 'Geocoding_Winner', 
            
            # QCT/DDA comparison
            'Nom_QCT_DDA_Status', 'PS_QCT_DDA_Status', 'QCT_DDA_Match',
            
            # Final recommendation
            'Best_Coordinates', 'Recommendation'
        ]
        
        for col in comparison_columns:
            df[col] = None
        
        # Process each site
        for idx, row in df.iterrows():
            self.logger.info(f"Processing {idx + 1}/{len(df)}: {row['MailingName']} in {row['City']}")
            
            address = row['Address']
            city = row['City']
            county = row['County']
            
            # 1. Geocode with Nominatim
            self.logger.info("  Testing Nominatim...")
            nom_result = self.geocode_with_nominatim(address, city, county)
            
            df.loc[idx, 'Nom_Latitude'] = nom_result['latitude']
            df.loc[idx, 'Nom_Longitude'] = nom_result['longitude']
            df.loc[idx, 'Nom_Address'] = nom_result['formatted_address']
            df.loc[idx, 'Nom_Accuracy'] = nom_result['accuracy']
            df.loc[idx, 'Nom_Success'] = nom_result['success']
            
            # Update stats
            if nom_result['success']:
                self.stats['nominatim']['success'] += 1
            elif nom_result['latitude']:
                self.stats['nominatim']['partial'] += 1
            else:
                self.stats['nominatim']['fail'] += 1
            self.stats['nominatim']['total'] += 1
            
            # 2. Geocode with PositionStack
            self.logger.info("  Testing PositionStack...")
            ps_result = self.geocode_with_positionstack(address, city, county)
            
            df.loc[idx, 'PS_Latitude'] = ps_result['latitude']
            df.loc[idx, 'PS_Longitude'] = ps_result['longitude']
            df.loc[idx, 'PS_Address'] = ps_result['formatted_address']
            df.loc[idx, 'PS_Confidence'] = ps_result['confidence']
            df.loc[idx, 'PS_Accuracy'] = ps_result['accuracy']
            df.loc[idx, 'PS_Success'] = ps_result['success']
            
            # Update stats
            if ps_result['success']:
                self.stats['positionstack']['success'] += 1
            elif ps_result['latitude']:
                self.stats['positionstack']['partial'] += 1
            else:
                self.stats['positionstack']['fail'] += 1
            self.stats['positionstack']['total'] += 1
            
            # 3. Compare results
            if nom_result['latitude'] and ps_result['latitude']:
                distance_diff = self.compare_geocoding_accuracy(
                    nom_result['latitude'], nom_result['longitude'],
                    ps_result['latitude'], ps_result['longitude']
                )
                df.loc[idx, 'Distance_Difference_Meters'] = distance_diff
                
                # Determine winner based on accuracy and confidence
                if ps_result['confidence'] > 0.8 and nom_result['accuracy'] == 'medium':
                    winner = 'PositionStack'
                elif nom_result['success'] and not ps_result['success']:
                    winner = 'Nominatim'
                elif ps_result['success'] and not nom_result['success']:
                    winner = 'PositionStack'
                elif ps_result['confidence'] > 0.8:
                    winner = 'PositionStack'
                else:
                    winner = 'Tie'
                
                df.loc[idx, 'Geocoding_Winner'] = winner
            
            # 4. Test QCT/DDA status with both
            qct_dda_comparison = self.test_qct_dda_with_both_methods(
                nom_result['latitude'], nom_result['longitude'],
                ps_result['latitude'], ps_result['longitude']
            )
            
            df.loc[idx, 'Nom_QCT_DDA_Status'] = qct_dda_comparison['nominatim_qct_dda']
            df.loc[idx, 'PS_QCT_DDA_Status'] = qct_dda_comparison['positionstack_qct_dda']
            df.loc[idx, 'QCT_DDA_Match'] = qct_dda_comparison['qct_dda_match']
            
            # 5. Final recommendation
            if ps_result['success'] and ps_result['confidence'] > 0.8:
                df.loc[idx, 'Best_Coordinates'] = 'PositionStack'
                df.loc[idx, 'Recommendation'] = f"Use PositionStack (confidence: {ps_result['confidence']:.2f})"
            elif nom_result['success']:
                df.loc[idx, 'Best_Coordinates'] = 'Nominatim'
                df.loc[idx, 'Recommendation'] = "Use Nominatim (exact address match)"
            elif ps_result['latitude']:
                df.loc[idx, 'Best_Coordinates'] = 'PositionStack'
                df.loc[idx, 'Recommendation'] = f"Use PositionStack (best available, confidence: {ps_result['confidence']:.2f})"
            elif nom_result['latitude']:
                df.loc[idx, 'Best_Coordinates'] = 'Nominatim'
                df.loc[idx, 'Recommendation'] = "Use Nominatim (city center fallback)"
            else:
                df.loc[idx, 'Best_Coordinates'] = 'Neither'
                df.loc[idx, 'Recommendation'] = "Manual geocoding required"
            
            # Rate limiting pause
            time.sleep(0.3)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"Geocoding_Comparison_Report_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Summary statistics
            summary_data = {
                'Service': ['Nominatim', 'PositionStack'],
                'Exact_Success': [self.stats['nominatim']['success'], self.stats['positionstack']['success']],
                'Partial_Success': [self.stats['nominatim']['partial'], self.stats['positionstack']['partial']],
                'Failures': [self.stats['nominatim']['fail'], self.stats['positionstack']['fail']],
                'Success_Rate': [
                    f"{self.stats['nominatim']['success']/self.stats['nominatim']['total']*100:.1f}%",
                    f"{self.stats['positionstack']['success']/self.stats['positionstack']['total']*100:.1f}%"
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Full comparison
            df.to_excel(writer, sheet_name='Full_Comparison', index=False)
            
            # QCT/DDA differences
            qct_dda_diffs = df[df['QCT_DDA_Match'] == False].copy()
            if len(qct_dda_diffs) > 0:
                key_cols = ['MailingName', 'City', 'County', 'Nom_QCT_DDA_Status', 'PS_QCT_DDA_Status', 'Distance_Difference_Meters']
                qct_dda_diffs[key_cols].to_excel(writer, sheet_name='QCT_DDA_Differences', index=False)
            
            # Best coordinates for re-analysis
            best_coords = []
            for _, row in df.iterrows():
                if row['Best_Coordinates'] == 'PositionStack':
                    lat, lng = row['PS_Latitude'], row['PS_Longitude']
                elif row['Best_Coordinates'] == 'Nominatim':
                    lat, lng = row['Nom_Latitude'], row['Nom_Longitude']
                else:
                    lat, lng = None, None
                
                best_coords.append({
                    'MailingName': row['MailingName'],
                    'Address': row['Address'],
                    'City': row['City'],
                    'County': row['County'],
                    'Region': row['Region'],
                    'Acres': row['Acres'],
                    'Best_Method': row['Best_Coordinates'],
                    'Latitude': lat,
                    'Longitude': lng,
                    'Recommendation': row['Recommendation']
                })
            
            best_df = pd.DataFrame(best_coords)
            best_df.to_excel(writer, sheet_name='Best_Coordinates', index=False)
        
        self.logger.info(f"✅ Comparison complete! Results saved to: {output_file}")
        return df, output_file
    
    def print_comparison_summary(self):
        """Print comparison statistics"""
        print("="*80)
        print("GEOCODING COMPARISON SUMMARY")
        print("="*80)
        
        nom_total = self.stats['nominatim']['total']
        ps_total = self.stats['positionstack']['total']
        
        print(f"\\n📊 NOMINATIM RESULTS:")
        print(f"   Exact Success: {self.stats['nominatim']['success']}/{nom_total} ({self.stats['nominatim']['success']/nom_total*100:.1f}%)")
        print(f"   Partial Success: {self.stats['nominatim']['partial']}/{nom_total} ({self.stats['nominatim']['partial']/nom_total*100:.1f}%)")
        print(f"   Failures: {self.stats['nominatim']['fail']}/{nom_total} ({self.stats['nominatim']['fail']/nom_total*100:.1f}%)")
        
        print(f"\\n🎯 POSITIONSTACK RESULTS:")
        print(f"   Exact Success: {self.stats['positionstack']['success']}/{ps_total} ({self.stats['positionstack']['success']/ps_total*100:.1f}%)")
        print(f"   Partial Success: {self.stats['positionstack']['partial']}/{ps_total} ({self.stats['positionstack']['partial']/ps_total*100:.1f}%)")
        print(f"   Failures: {self.stats['positionstack']['fail']}/{ps_total} ({self.stats['positionstack']['fail']/ps_total*100:.1f}%)")

def main():
    comparison = GeocodingComparison()
    
    # Run comparison on D'Marco sites
    csv_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/From_Brent_06182025.csv"
    
    if Path(csv_file).exists():
        df_results, output_file = comparison.run_comparison(csv_file)
        
        # Print summary
        comparison.print_comparison_summary()
        
        print(f"\\n📁 DETAILED COMPARISON: {output_file}")
        print("\\nKey sheets:")
        print("  • Summary: Success rates comparison")
        print("  • Full_Comparison: Side-by-side results")
        print("  • QCT_DDA_Differences: Where methods disagree")
        print("  • Best_Coordinates: Recommended coordinates for each site")
        
    else:
        print(f"❌ File not found: {csv_file}")

if __name__ == "__main__":
    main()