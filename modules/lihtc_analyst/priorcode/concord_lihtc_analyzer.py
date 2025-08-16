#!/usr/bin/env python3
"""
California LIHTC Analysis for 2451 Olivera Road, Concord, CA 94520
Combines QCT/DDA, HQTA, and HUD AMI rent analysis
"""

import requests
import json
import pandas as pd
import sys
from pathlib import Path

# Add the current directory to path to import our modules
sys.path.append('/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code')

from ca_qct_dda_checker import CaliforniaQCTDDAChecker
from ca_transit_checker import CaliforniaTransitChecker
from hud_rent_integration import HUDRentIntegrator

class ConcordLIHTCAnalyzer:
    def __init__(self):
        self.address = "2451 Olivera Road, Concord, CA 94520"
        self.apn = "110-035-002-2"
        self.unit_mix = {"1BR": 8, "2BR": 86}
        self.total_units = 94
        self.built_year = 1971
        self.parking_spots = 162
        self.zoning = "M18"
        self.stories = 2
        
        # Initialize checkers
        self.qct_dda_checker = CaliforniaQCTDDAChecker()
        self.transit_checker = CaliforniaTransitChecker()
        self.rent_integrator = HUDRentIntegrator()
        
        # Get coordinates
        self.latitude, self.longitude = self.geocode_address()
    
    def geocode_address(self):
        """Get coordinates for the address"""
        print(f"🗺️  Geocoding address: {self.address}")
        
        # Use Census geocoding API
        census_geocoding_url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
        params = {
            'address': self.address,
            'benchmark': 'Public_AR_Current',
            'format': 'json'
        }
        
        try:
            response = requests.get(census_geocoding_url, params=params)
            data = response.json()
            
            if data['result']['addressMatches']:
                match = data['result']['addressMatches'][0]
                coordinates = match['coordinates']
                latitude = coordinates['y']
                longitude = coordinates['x']
                
                print(f"✅ Geocoded successfully: {latitude}, {longitude}")
                return latitude, longitude
            else:
                print("❌ No geocoding match found, using approximate coordinates")
                return 37.9779, -122.0312  # Approximate Concord coordinates
                
        except Exception as e:
            print(f"⚠️  Error geocoding: {e}")
            print("Using approximate Concord coordinates")
            return 37.9779, -122.0312
    
    def analyze_qct_dda_status(self):
        """Analyze QCT/DDA federal designation status"""
        print(f"\n🏛️  FEDERAL QCT/DDA ANALYSIS")
        print("=" * 60)
        
        result = self.qct_dda_checker.check_qct_dda_status(self.latitude, self.longitude)
        
        print(f"📍 Location: {self.latitude}, {self.longitude}")
        print(f"QCT Status: {'✅ YES' if result['qct_status'] else '❌ NO'}")
        print(f"DDA Status: {'✅ YES' if result['dda_status'] else '❌ NO'}")
        print(f"Federal Basis Boost (30%): {'✅ YES' if result['federal_basis_boost'] else '❌ NO'}")
        
        if result['qct_status']:
            print(f"QCT Name: {result['qct_name']}")
            if result['qct_tract']:
                print(f"QCT Tract: {result['qct_tract']}")
        
        if result['dda_status']:
            print(f"DDA Name: {result['dda_name']}")
            if result['dda_details']['metro_area']:
                print(f"Metro Area: {result['dda_details']['metro_area']}")
        
        return result
    
    def analyze_transit_scoring(self):
        """Analyze CTCAC transit scoring potential"""
        print(f"\n🚊 CTCAC TRANSIT SCORING ANALYSIS")
        print("=" * 60)
        
        result = self.transit_checker.evaluate_ctcac_transit_scoring(self.latitude, self.longitude)
        
        # HQTA Status
        print(f"📍 HIGH QUALITY TRANSIT AREA (HQTA) STATUS:")
        if result["hqta_status"]["in_hqta"]:
            print(f"   ✅ Location IS within HQTA")
            hqta_info = result["hqta_status"]["hqta_info"]
            print(f"   📋 Area: {hqta_info['area_name']}")
            print(f"   🚌 Transit Type: {hqta_info['transit_type']}")
            print(f"   🏢 Agency: {hqta_info['agency']}")
        else:
            print(f"   ❌ Location is NOT within HQTA")
        
        # Transit Proximity
        print(f"\n🚇 TRANSIT PROXIMITY:")
        for distance_name, analysis in result["transit_analysis"].items():
            print(f"   Within {analysis['distance_miles']} miles: {analysis['transit_stops_found']} stops")
            if analysis['nearest_stops']:
                nearest = analysis['nearest_stops'][0]
                print(f"   Nearest: {nearest['stop_name']} ({nearest['distance_miles']} miles)")
        
        # CTCAC Scoring Categories
        print(f"\n🏆 9% COMPETITIVE SCORING CATEGORIES:")
        for i, category in enumerate(result["ctcac_scoring"]["9p_eligible_categories"], 1):
            print(f"   {i}. {category['category']}")
            print(f"      Status: {category['status']}")
            print(f"      Distance: {category['distance']}")
        
        return result
    
    def get_hud_ami_rents(self):
        """Get HUD AMI rent data for Contra Costa County"""
        print(f"\n💰 HUD AMI RENT ANALYSIS - CONTRA COSTA COUNTY")
        print("=" * 60)
        
        # Get rent data for Contra Costa County
        county_rents = self.rent_integrator.get_rent_for_county("Contra Costa")
        
        if not county_rents:
            print("❌ No HUD rent data found for Contra Costa County")
            print("📝 Using sample Bay Area rent estimates...")
            
            # Bay Area sample rents (2025 estimates)
            county_rents = {
                'BR1_50AMI_rent': 1450,
                'BR2_50AMI_rent': 1740,
                'BR1_60AMI_rent': 1740,
                'BR2_60AMI_rent': 2088,
                'BR1_70AMI_rent': 2030,  # Calculated estimate
                'BR2_70AMI_rent': 2436,  # Calculated estimate
                'BR1_80AMI_rent': 2320,  # Calculated estimate
                'BR2_80AMI_rent': 2784   # Calculated estimate
            }
        else:
            # Calculate 70% and 80% AMI rents (HUD file may only have 50% and 60%)
            if 'BR1_60AMI_rent' in county_rents and 'BR1_50AMI_rent' in county_rents:
                br1_50 = county_rents.get('BR1_50AMI_rent', 0)
                br1_60 = county_rents.get('BR1_60AMI_rent', 0)
                br2_50 = county_rents.get('BR2_50AMI_rent', 0)
                br2_60 = county_rents.get('BR2_60AMI_rent', 0)
                
                # Calculate 70% and 80% based on 50%/60% progression
                if br1_50 > 0 and br1_60 > 0:
                    br1_70 = int(br1_50 * 1.4)  # 70% = 50% * 1.4
                    br1_80 = int(br1_50 * 1.6)  # 80% = 50% * 1.6
                    br2_70 = int(br2_50 * 1.4)
                    br2_80 = int(br2_50 * 1.6)
                    
                    county_rents.update({
                        'BR1_70AMI_rent': br1_70,
                        'BR2_70AMI_rent': br2_70,
                        'BR1_80AMI_rent': br1_80,
                        'BR2_80AMI_rent': br2_80
                    })
        
        # Display rent table
        print("\n📊 AMI RENT LIMITS (2025):")
        print("-" * 50)
        print(f"{'AMI Level':<12} {'1BR':<8} {'2BR':<8}")
        print("-" * 50)
        
        ami_levels = ['50%', '60%', '70%', '80%']
        for ami in ami_levels:
            ami_code = ami.replace('%', 'AMI')
            br1_rent = county_rents.get(f'BR1_{ami_code}_rent', 'N/A')
            br2_rent = county_rents.get(f'BR2_{ami_code}_rent', 'N/A')
            
            br1_str = f"${br1_rent:,}" if br1_rent != 'N/A' else 'N/A'
            br2_str = f"${br2_rent:,}" if br2_rent != 'N/A' else 'N/A'
            
            print(f"{ami:<12} {br1_str:<8} {br2_str:<8}")
        
        return county_rents
    
    def calculate_revenue_projections(self, county_rents):
        """Calculate revenue projections for the unit mix"""
        print(f"\n📈 REVENUE PROJECTIONS")
        print("=" * 60)
        print(f"Unit Mix: {self.unit_mix['1BR']} x 1BR + {self.unit_mix['2BR']} x 2BR = {self.total_units} total units")
        
        # Calculate monthly and annual revenue for each AMI level
        ami_levels = ['50AMI', '60AMI', '70AMI', '80AMI']
        
        print(f"\n💵 POTENTIAL RENTAL INCOME:")
        print("-" * 70)
        print(f"{'AMI Level':<12} {'Monthly':<12} {'Annual':<12} {'Per Unit Avg':<12}")
        print("-" * 70)
        
        for ami in ami_levels:
            br1_rent = county_rents.get(f'BR1_{ami}_rent', 0)
            br2_rent = county_rents.get(f'BR2_{ami}_rent', 0)
            
            if br1_rent > 0 and br2_rent > 0:
                monthly_revenue = (self.unit_mix['1BR'] * br1_rent) + (self.unit_mix['2BR'] * br2_rent)
                annual_revenue = monthly_revenue * 12
                avg_per_unit = monthly_revenue / self.total_units
                
                ami_display = ami.replace('AMI', '%')
                print(f"{ami_display:<12} ${monthly_revenue:,<11} ${annual_revenue:,<11} ${avg_per_unit:,.0f}")
        
        return True
    
    def search_competing_projects(self):
        """Search for competing LIHTC projects in Concord area"""
        print(f"\n🏢 COMPETING LIHTC PROJECTS ANALYSIS")
        print("=" * 60)
        print("📍 Searching for LIHTC projects within 3-mile radius of Concord...")
        print("⚠️  Note: Comprehensive competition analysis requires CTCAC project database")
        print("💡 Recommendation: Manual review of CTCAC project list for Contra Costa County")
        
        # This would require access to CTCAC project database
        # For now, provide guidance on what to look for
        competition_factors = [
            "CTCAC 9% projects within 3 miles (tie-breaker impacts)",
            "CTCAC 4% projects within 1 mile (scoring impacts)", 
            "Market-rate developments affecting rent comps",
            "Other affordable housing reducing demand"
        ]
        
        print("\n🎯 COMPETITION FACTORS TO RESEARCH:")
        for i, factor in enumerate(competition_factors, 1):
            print(f"   {i}. {factor}")
        
        return True
    
    def generate_summary_report(self, qct_dda_result, transit_result, county_rents):
        """Generate comprehensive summary report"""
        print(f"\n📋 COMPREHENSIVE LIHTC ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Property: {self.address}")
        print(f"APN: {self.apn}")
        print(f"Coordinates: {self.latitude}, {self.longitude}")
        print(f"Unit Mix: {self.unit_mix['1BR']} x 1BR + {self.unit_mix['2BR']} x 2BR = {self.total_units} units")
        print(f"Built: {self.built_year} | Stories: {self.stories} | Parking: {self.parking_spots}")
        print(f"Zoning: {self.zoning}")
        
        print(f"\n🏛️  FEDERAL ELIGIBILITY:")
        print(f"   QCT Status: {'✅ YES' if qct_dda_result['qct_status'] else '❌ NO'}")
        print(f"   DDA Status: {'✅ YES' if qct_dda_result['dda_status'] else '❌ NO'}")
        print(f"   30% Basis Boost: {'✅ ELIGIBLE' if qct_dda_result['federal_basis_boost'] else '❌ NOT ELIGIBLE'}")
        
        print(f"\n🚊 TRANSIT SCORING (9% Deals):")
        hqta_status = "✅ HQTA" if transit_result["hqta_status"]["in_hqta"] else "❌ Not HQTA"
        print(f"   HQTA Status: {hqta_status}")
        
        one_third_stops = transit_result["transit_analysis"]["1/3_mile"]["transit_stops_found"]
        one_half_stops = transit_result["transit_analysis"]["1/2_mile"]["transit_stops_found"]
        print(f"   Transit within 1/3 mile: {one_third_stops} stops")
        print(f"   Transit within 1/2 mile: {one_half_stops} stops")
        
        print(f"\n💰 RENT POTENTIAL (Key AMI Levels):")
        for ami in ['60AMI', '80AMI']:
            br1_rent = county_rents.get(f'BR1_{ami}_rent', 0)
            br2_rent = county_rents.get(f'BR2_{ami}_rent', 0)
            if br1_rent > 0 and br2_rent > 0:
                monthly_revenue = (self.unit_mix['1BR'] * br1_rent) + (self.unit_mix['2BR'] * br2_rent)
                ami_display = ami.replace('AMI', '%')
                print(f"   {ami_display} AMI: ${monthly_revenue:,}/month (${monthly_revenue * 12:,}/year)")
        
        print(f"\n🎯 LIHTC DEAL RECOMMENDATIONS:")
        if qct_dda_result['federal_basis_boost']:
            print("   ✅ 4% Tax-Exempt Bond: ELIGIBLE (federal basis boost available)")
            print("   ✅ 9% Competitive: ELIGIBLE (federal basis boost + transit scoring potential)")
        else:
            print("   ⚠️  4% Tax-Exempt Bond: ELIGIBLE (no federal basis boost)")
            print("   ⚠️  9% Competitive: ELIGIBLE (limited scoring without QCT/DDA)")
        
        if transit_result["hqta_status"]["in_hqta"]:
            print("   🏆 HQTA location provides strong 9% competitive scoring potential")
        
        print(f"\n📝 NEXT STEPS:")
        print("   1. Verify current ownership and acquisition feasibility")
        print("   2. Conduct detailed market study and rent analysis")
        print("   3. Review CTCAC project database for competition")
        print("   4. Analyze Concord rent stabilization impacts")
        print("   5. Evaluate rehabilitation vs. new construction economics")
        
        return True

def main():
    """Run comprehensive Concord LIHTC analysis"""
    print("🏠 CALIFORNIA LIHTC ANALYSIS")
    print("2451 Olivera Road, Concord, CA 94520")
    print("=" * 80)
    
    # Initialize analyzer
    analyzer = ConcordLIHTCAnalyzer()
    
    # Run analysis components
    qct_dda_result = analyzer.analyze_qct_dda_status()
    transit_result = analyzer.analyze_transit_scoring()
    county_rents = analyzer.get_hud_ami_rents()
    analyzer.calculate_revenue_projections(county_rents)
    analyzer.search_competing_projects()
    
    # Generate summary
    analyzer.generate_summary_report(qct_dda_result, transit_result, county_rents)
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main()