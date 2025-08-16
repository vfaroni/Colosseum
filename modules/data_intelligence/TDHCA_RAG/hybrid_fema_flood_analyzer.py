#!/usr/bin/env python3
"""
Hybrid FEMA Flood Zone Analyzer
- Primary: Use CoStar flood data when available
- Secondary: FEMA API verification/cross-check 
- Fallback: FEMA API for non-CoStar sites
"""

import pandas as pd
import requests
import time
import re
from datetime import datetime
from pathlib import Path

class HybridFEMAFloodAnalyzer:
    """Hybrid approach: CoStar data + FEMA API verification"""
    
    def __init__(self):
        # FEMA flood zone risk classification
        self.FLOOD_ZONE_RISK = {
            'A': 'HIGH_RISK',           # 1% annual chance
            'AE': 'HIGH_RISK',          # 1% annual chance with BFE
            'AH': 'HIGH_RISK',          # 1% annual chance shallow
            'AO': 'HIGH_RISK',          # 1% annual chance sheet flow
            'AR': 'HIGH_RISK',          # 1% annual chance restored
            'V': 'VERY_HIGH_RISK',      # 1% annual chance coastal
            'VE': 'VERY_HIGH_RISK',     # 1% annual chance coastal with BFE
            'X': 'LOW_RISK',            # Outside flood zones
            'B': 'LOW_RISK',            # Same as X (older designation)
            'C': 'LOW_RISK',            # Same as X (older designation)
            'X500': 'MODERATE_RISK',    # 0.2% annual chance
            'D': 'UNDETERMINED'         # Undetermined
        }
        
        # Risk scoring for LIHTC analysis
        self.RISK_SCORES = {
            'LOW_RISK': 20,             # Best for LIHTC (no flood insurance)
            'MODERATE_RISK': 15,        # Moderate
            'HIGH_RISK': 5,             # Poor (high flood insurance costs)
            'VERY_HIGH_RISK': 0,        # Eliminate (very high costs)
            'UNDETERMINED': 10          # Conservative middle
        }
        
        # Annual flood insurance costs (estimated per unit)
        self.INSURANCE_COSTS = {
            'LOW_RISK': 0,              # No flood insurance required
            'MODERATE_RISK': 500,       # Basic flood insurance
            'HIGH_RISK': 2000,          # Standard flood insurance
            'VERY_HIGH_RISK': 4000,     # High-risk flood insurance
            'UNDETERMINED': 1000        # Conservative estimate
        }
    
    def parse_costar_flood_zone(self, flood_zone_str):
        """Parse CoStar flood zone string (handles 'B and X', 'AE', etc.)"""
        if pd.isna(flood_zone_str) or flood_zone_str == 'nan':
            return []
        
        zone_str = str(flood_zone_str).upper()
        
        # Handle multiple zones like "B and X"
        if ' AND ' in zone_str:
            zones = [z.strip() for z in zone_str.split(' AND ')]
        elif ',' in zone_str:
            zones = [z.strip() for z in zone_str.split(',')]
        else:
            zones = [zone_str.strip()]
        
        # Clean up zones and validate
        valid_zones = []
        for zone in zones:
            zone = re.sub(r'[^A-Z0-9]', '', zone)  # Remove non-alphanumeric
            if zone in self.FLOOD_ZONE_RISK:
                valid_zones.append(zone)
        
        return valid_zones
    
    def get_worst_risk_level(self, zones):
        """Get the worst (highest) risk level from multiple zones"""
        if not zones:
            return 'UNDETERMINED'
        
        risk_levels = [self.FLOOD_ZONE_RISK.get(zone, 'UNDETERMINED') for zone in zones]
        
        # Return worst risk (priority order)
        if 'VERY_HIGH_RISK' in risk_levels:
            return 'VERY_HIGH_RISK'
        elif 'HIGH_RISK' in risk_levels:
            return 'HIGH_RISK'
        elif 'MODERATE_RISK' in risk_levels:
            return 'MODERATE_RISK'
        elif 'LOW_RISK' in risk_levels:
            return 'LOW_RISK'
        else:
            return 'UNDETERMINED'
    
    def get_fema_api_zone(self, lat, lng):
        """Get FEMA flood zone using FEMA API (for verification or missing data)"""
        try:
            base_url = "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer"
            identify_url = f"{base_url}/identify"
            
            params = {
                'geometry': f'{lng},{lat}',
                'geometryType': 'esriGeometryPoint',
                'sr': '4326',
                'layers': 'all:28',
                'tolerance': '0',
                'mapExtent': f'{lng-0.01},{lat-0.01},{lng+0.01},{lat+0.01}',
                'imageDisplay': '400,400,96',
                'returnGeometry': 'false',
                'f': 'json'
            }
            
            response = requests.get(identify_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    result = data['results'][0]
                    attributes = result.get('attributes', {})
                    flood_zone = attributes.get('FLD_ZONE', attributes.get('ZONE', 'X'))
                    return flood_zone
            
            return 'X'  # Default to low risk if API fails
            
        except Exception as e:
            print(f"   ⚠️ FEMA API error: {e}")
            return 'X'  # Default to low risk
    
    def analyze_site_flood_risk(self, site_data, verify_with_api=False):
        """Analyze flood risk for a single site"""
        city = site_data.get('City', 'Unknown')
        costar_risk = site_data.get('Flood Risk', '')
        costar_zone = site_data.get('Flood Zone', '')
        lat = site_data.get('Latitude')
        lng = site_data.get('Longitude')
        
        result = {
            'city': city,
            'costar_flood_risk': costar_risk,
            'costar_flood_zone': costar_zone,
            'parsed_zones': [],
            'primary_zone': None,
            'risk_level': 'UNDETERMINED',
            'risk_score': 10,
            'annual_insurance_cost': 1000,
            'data_source': 'UNKNOWN',
            'fema_api_zone': None,
            'zones_match': None
        }
        
        # Parse CoStar flood zones
        if costar_zone and costar_zone != 'nan':
            parsed_zones = self.parse_costar_flood_zone(costar_zone)
            result['parsed_zones'] = parsed_zones
            
            if parsed_zones:
                # Use worst risk level from multiple zones
                risk_level = self.get_worst_risk_level(parsed_zones)
                primary_zone = parsed_zones[0]  # Primary zone for display
                
                result.update({
                    'primary_zone': primary_zone,
                    'risk_level': risk_level,
                    'risk_score': self.RISK_SCORES[risk_level],
                    'annual_insurance_cost': self.INSURANCE_COSTS[risk_level],
                    'data_source': 'COSTAR_FLOOD_DATA'
                })
        
        # FEMA API verification or fallback
        if verify_with_api and pd.notna(lat) and pd.notna(lng):
            fema_zone = self.get_fema_api_zone(lat, lng)
            result['fema_api_zone'] = fema_zone
            
            # Check if CoStar and FEMA data match
            if result['parsed_zones']:
                result['zones_match'] = fema_zone in result['parsed_zones']
                if not result['zones_match']:
                    print(f"   ⚠️ MISMATCH: CoStar={result['parsed_zones']} vs FEMA={fema_zone}")
            else:
                # Use FEMA data as fallback
                fema_risk = self.FLOOD_ZONE_RISK.get(fema_zone, 'UNDETERMINED')
                result.update({
                    'primary_zone': fema_zone,
                    'risk_level': fema_risk,
                    'risk_score': self.RISK_SCORES[fema_risk],
                    'annual_insurance_cost': self.INSURANCE_COSTS[fema_risk],
                    'data_source': 'FEMA_API_FALLBACK'
                })
            
            time.sleep(1.0)  # Rate limit FEMA API
        
        return result
    
    def analyze_all_sites(self, df, verify_sample=True):
        """Analyze flood risk for all sites"""
        print("🌊 HYBRID FEMA FLOOD ANALYSIS")
        print("📊 Strategy: CoStar primary + FEMA API verification/fallback")
        print("=" * 70)
        
        results = []
        api_calls = 0
        max_api_calls = 20 if verify_sample else 0  # Limit API calls for testing
        
        for idx, site in df.iterrows():
            print(f"\n🏠 Site {idx}: {site.get('City', 'Unknown')}")
            
            # Decide whether to use FEMA API
            use_api = False
            if verify_sample and api_calls < max_api_calls:
                costar_zone = site.get('Flood Zone', '')
                if pd.isna(costar_zone) or costar_zone == 'nan':
                    use_api = True  # Missing CoStar data
                    print("   📡 Using FEMA API (missing CoStar data)")
                elif api_calls < 5:  # Verify first 5 sites
                    use_api = True
                    print("   📡 Using FEMA API (verification sample)")
            
            if use_api:
                api_calls += 1
            
            # Analyze flood risk
            result = self.analyze_site_flood_risk(site, verify_with_api=use_api)
            results.append(result)
            
            # Display result
            zone = result['primary_zone'] or 'Unknown'
            risk = result['risk_level']
            source = result['data_source']
            cost = result['annual_insurance_cost']
            
            print(f"   🏷️ Zone: {zone} | Risk: {risk} | Cost: ${cost:,}/unit/year")
            print(f"   📋 Source: {source}")
            
            if result['zones_match'] is not None:
                match_status = "✅ MATCH" if result['zones_match'] else "❌ MISMATCH"
                print(f"   🔍 Verification: {match_status}")
        
        print(f"\n📊 ANALYSIS COMPLETE:")
        print(f"   🏠 Total sites: {len(results)}")
        print(f"   📡 FEMA API calls: {api_calls}")
        
        # Risk distribution
        risk_dist = {}
        for result in results:
            risk = result['risk_level']
            risk_dist[risk] = risk_dist.get(risk, 0) + 1
        
        print(f"   📈 Risk distribution:")
        for risk, count in risk_dist.items():
            print(f"      {risk}: {count} sites")
        
        return results

def test_hybrid_flood_analysis():
    """Test hybrid flood analysis with first 10 sites"""
    
    base_file = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/Analysis_Results/MASTER_155_BoostEligible_Sites_20250731_223500.xlsx"
    df = pd.read_excel(base_file)
    test_df = df.head(10)
    
    analyzer = HybridFEMAFloodAnalyzer()
    results = analyzer.analyze_all_sites(test_df, verify_sample=True)
    
    return results

if __name__ == "__main__":
    results = test_hybrid_flood_analysis()