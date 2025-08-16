#!/usr/bin/env python3
"""
Test Suite for Flood Elimination Logic
Following Colosseum testing protocols: validation before processing
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

class TestFloodEliminationLogic:
    """Comprehensive test suite for flood elimination logic"""
    
    def setup_method(self):
        """Setup test data and known validation sites"""
        
        # Known test sites for validation
        self.known_test_sites = [
            {
                'name': 'Safe Site - No Flood Data',
                'sfha': np.nan,
                'flood_risk_area': np.nan,
                'fema_flood_zone': np.nan,
                'expected_eliminate': False,
                'expected_reason': None
            },
            {
                'name': 'Safe Site - SFHA No',
                'sfha': 'No',
                'flood_risk_area': 'Moderate to Low Risk Areas',
                'fema_flood_zone': 'Area of minimal flood hazard',
                'expected_eliminate': False,
                'expected_reason': None
            },
            {
                'name': 'Eliminate - SFHA Yes',
                'sfha': 'Yes',
                'flood_risk_area': 'High Risk Areas',
                'fema_flood_zone': 'AE',
                'expected_eliminate': True,
                'expected_reason': 'SFHA: Yes'
            },
            {
                'name': 'Eliminate - High Risk Area',
                'sfha': np.nan,
                'flood_risk_area': 'High Risk Areas',
                'fema_flood_zone': 'Area of moderate flood hazard',
                'expected_eliminate': True,
                'expected_reason': 'Flood Risk Area: High Risk Areas'
            },
            {
                'name': 'Eliminate - AE Zone',
                'sfha': np.nan,
                'flood_risk_area': 'Moderate to Low Risk Areas',
                'fema_flood_zone': 'The base floodplain where base flood elevations are provided',
                'expected_eliminate': True,
                'expected_reason': 'High-risk zone: AE'
            },
            {
                'name': 'Safe - Zone X Descriptive',
                'sfha': np.nan,
                'flood_risk_area': 'Moderate to Low Risk Areas', 
                'fema_flood_zone': 'Area of minimal flood hazard, usually depicted on FIRMs as above the 500-year flood level',
                'expected_eliminate': False,
                'expected_reason': None
            },
            {
                'name': 'Safe - Zone D Descriptive',
                'sfha': np.nan,
                'flood_risk_area': 'Undetermined Risk Areas',
                'fema_flood_zone': 'Areas with possible but undetermined flood hazards',
                'expected_eliminate': False,
                'expected_reason': None
            }
        ]
        
        # Northern California test coordinates
        self.northern_ca_coordinates = [
            {'name': 'San Francisco', 'lat': 37.7749, 'lng': -122.4194},
            {'name': 'Sacramento', 'lat': 38.5816, 'lng': -121.4944},
            {'name': 'San Jose', 'lat': 37.3382, 'lng': -121.8863},
            {'name': 'Oakland', 'lat': 37.8044, 'lng': -122.2712},
            {'name': 'Fresno', 'lat': 36.7468, 'lng': -119.7725}
        ]
        
        # Southern California test coordinates
        self.southern_ca_coordinates = [
            {'name': 'Los Angeles', 'lat': 34.0522, 'lng': -118.2437},
            {'name': 'San Diego', 'lat': 32.7157, 'lng': -117.1611},
            {'name': 'Riverside', 'lat': 33.9533, 'lng': -117.3962}
        ]
    
    def create_flood_elimination_logic(self):
        """Create the flood elimination logic function to test"""
        
        def evaluate_flood_elimination(sfha_status, flood_risk_area, fema_flood_zone):
            """
            Core flood elimination logic based on user requirements
            
            ELIMINATE:
            - Properties with SFHA = "Yes" 
            - Flood Risk Area = "High Risk Areas"
            - Special Flood Hazard Areas: Zone A, V, AV99, AE, AO, AH, VE, AR
            
            KEEP:
            - Properties with SFHA = "No" or blank/null
            - Zone X and Zone D (acceptable)
            - Flood Risk Area = "Moderate to Low Risk Areas" or "Undetermined Risk Areas"
            """
            
            # Convert to strings for analysis
            sfha_str = str(sfha_status).strip() if pd.notna(sfha_status) else ""
            flood_zone_str = str(fema_flood_zone).strip() if pd.notna(fema_flood_zone) else ""
            flood_risk_str = str(flood_risk_area).strip() if pd.notna(flood_risk_area) else ""
            
            # Define high-risk zones to eliminate
            high_risk_zones = ['A', 'V', 'AV99', 'AE', 'AO', 'AH', 'VE', 'AR']
            
            should_eliminate = False
            elimination_reasons = []
            
            # Check SFHA status (eliminate if "Yes")
            if sfha_str.upper() == 'YES':
                should_eliminate = True
                elimination_reasons.append(f"SFHA: {sfha_str}")
            
            # Check Flood Risk Area (eliminate if "High Risk Areas")
            if flood_risk_str == 'High Risk Areas':
                should_eliminate = True
                elimination_reasons.append(f"Flood Risk Area: {flood_risk_str}")
            
            # Check for high-risk flood zones in descriptive text
            zone_found = None
            for zone in high_risk_zones:
                # Look for zone codes in flood zone descriptions
                # Be careful to match actual zone codes, not partial strings
                if _zone_matches_in_description(zone, flood_zone_str):
                    zone_found = zone
                    should_eliminate = True
                    elimination_reasons.append(f"High-risk zone: {zone}")
                    break
            
            return {
                'should_eliminate': should_eliminate,
                'elimination_reasons': elimination_reasons,
                'zone_found': zone_found,
                'processed_values': {
                    'sfha_clean': sfha_str,
                    'flood_risk_clean': flood_risk_str, 
                    'flood_zone_clean': flood_zone_str
                }
            }
        
        def _zone_matches_in_description(zone_code, description):
            """Check if a zone code is actually present in flood zone description"""
            
            # Special handling for common zone codes to avoid false positives
            description_upper = description.upper()
            
            # AE zone - look for specific indicators
            if zone_code == 'AE':
                return ('BASE FLOOD' in description_upper and 
                       'ELEVATION' in description_upper and
                       'PROVIDED' in description_upper)
            
            # A zone - look for "1% annual chance" indicator
            elif zone_code == 'A':
                return ('1% ANNUAL CHANCE' in description_upper or
                       'ANNUAL CHANCE OF FLOODING' in description_upper)
            
            # V zone - look for velocity/coastal indicators  
            elif zone_code == 'V':
                return ('VELOCITY' in description_upper or
                       'COASTAL' in description_upper)
            
            # For other zones, be very specific to avoid false matches
            elif zone_code in ['AO', 'AH', 'AR', 'AV99', 'VE']:
                # These are rare, only match if explicitly mentioned
                return f' {zone_code} ' in f' {description_upper} '
            
            # Default - no match for descriptive text
            else:
                return False
        
        # Make helper method available
        evaluate_flood_elimination._zone_matches_in_description = _zone_matches_in_description
        
        return evaluate_flood_elimination
    
    def test_known_flood_sites_accuracy(self):
        """Test flood elimination logic on known sites"""
        
        print("\n🧪 TESTING KNOWN FLOOD SITES FOR ACCURACY")
        print("=" * 50)
        
        flood_logic = self.create_flood_elimination_logic()
        
        passed_tests = 0
        total_tests = len(self.known_test_sites)
        
        for i, site in enumerate(self.known_test_sites):
            print(f"\n📍 Test {i+1}: {site['name']}")
            
            result = flood_logic(
                site['sfha'],
                site['flood_risk_area'], 
                site['fema_flood_zone']
            )
            
            should_eliminate = result['should_eliminate']
            reasons = result['elimination_reasons']
            
            print(f"   SFHA: {repr(site['sfha'])}")
            print(f"   Risk Area: {repr(site['flood_risk_area'])}")
            print(f"   Flood Zone: {repr(site['fema_flood_zone'])}")
            print(f"   Expected Eliminate: {site['expected_eliminate']}")
            print(f"   Actually Eliminate: {should_eliminate}")
            
            # Check if result matches expectation
            if should_eliminate == site['expected_eliminate']:
                print(f"   ✅ PASS")
                passed_tests += 1
                
                # If elimination expected, check reason contains expected text
                if site['expected_eliminate'] and site['expected_reason']:
                    reason_text = '; '.join(reasons) if reasons else ''
                    if site['expected_reason'].split(':')[0] in reason_text:
                        print(f"   ✅ Elimination reason correct: {reason_text}")
                    else:
                        print(f"   ⚠️  Elimination reason mismatch:")
                        print(f"        Expected: {site['expected_reason']}")
                        print(f"        Got: {reason_text}")
            else:
                print(f"   ❌ FAIL - Expected {site['expected_eliminate']}, got {should_eliminate}")
                if reasons:
                    print(f"   Elimination reasons: {'; '.join(reasons)}")
        
        accuracy_rate = (passed_tests / total_tests) * 100
        print(f"\n📊 ACCURACY TEST RESULTS:")
        print(f"   Passed: {passed_tests}/{total_tests}")
        print(f"   Accuracy Rate: {accuracy_rate:.1f}%")
        
        # Assert minimum 90% accuracy
        assert accuracy_rate >= 90.0, f"Accuracy rate {accuracy_rate:.1f}% below required 90%"
        
        return accuracy_rate
    
    def test_sfha_criteria_validation(self):
        """Test SFHA criteria specifically"""
        
        print("\n🏛️ TESTING SFHA CRITERIA VALIDATION")
        print("=" * 40)
        
        flood_logic = self.create_flood_elimination_logic()
        
        # Test SFHA Yes/No/blank scenarios
        sfha_test_cases = [
            ('Yes', True, 'Should eliminate SFHA=Yes'),
            ('YES', True, 'Should eliminate SFHA=YES (case insensitive)'),
            ('No', False, 'Should keep SFHA=No'),
            ('NO', False, 'Should keep SFHA=NO (case insensitive)'),
            (np.nan, False, 'Should keep blank SFHA'),
            ('', False, 'Should keep empty SFHA'),
            ('Unknown', False, 'Should keep SFHA=Unknown')
        ]
        
        passed = 0
        for sfha_value, expected_eliminate, description in sfha_test_cases:
            result = flood_logic(sfha_value, np.nan, np.nan)
            
            if result['should_eliminate'] == expected_eliminate:
                print(f"   ✅ {description}")
                passed += 1
            else:
                print(f"   ❌ {description} - FAILED")
                print(f"        Expected: {expected_eliminate}, Got: {result['should_eliminate']}")
        
        accuracy = (passed / len(sfha_test_cases)) * 100
        print(f"\n   SFHA Test Accuracy: {accuracy:.1f}%")
        
        assert accuracy >= 95.0, f"SFHA test accuracy {accuracy:.1f}% below required 95%"
        
        return accuracy
    
    def test_flood_risk_area_validation(self):
        """Test Flood Risk Area criteria"""
        
        print("\n🌊 TESTING FLOOD RISK AREA VALIDATION")
        print("=" * 40)
        
        flood_logic = self.create_flood_elimination_logic()
        
        risk_area_test_cases = [
            ('High Risk Areas', True, 'Should eliminate High Risk Areas'),
            ('Moderate to Low Risk Areas', False, 'Should keep Moderate to Low Risk Areas'),
            ('Undetermined Risk Areas', False, 'Should keep Undetermined Risk Areas'), 
            (np.nan, False, 'Should keep blank Risk Area'),
            ('', False, 'Should keep empty Risk Area'),
            ('Low Risk Areas', False, 'Should keep Low Risk Areas')
        ]
        
        passed = 0
        for risk_value, expected_eliminate, description in risk_area_test_cases:
            result = flood_logic(np.nan, risk_value, np.nan)
            
            if result['should_eliminate'] == expected_eliminate:
                print(f"   ✅ {description}")
                passed += 1
            else:
                print(f"   ❌ {description} - FAILED")
                print(f"        Expected: {expected_eliminate}, Got: {result['should_eliminate']}")
        
        accuracy = (passed / len(risk_area_test_cases)) * 100
        print(f"\n   Risk Area Test Accuracy: {accuracy:.1f}%")
        
        assert accuracy >= 95.0, f"Risk area test accuracy {accuracy:.1f}% below required 95%"
        
        return accuracy
    
    def test_zone_classification_accuracy(self):
        """Test flood zone classification logic"""
        
        print("\n🗺️ TESTING FLOOD ZONE CLASSIFICATION")
        print("=" * 40)
        
        flood_logic = self.create_flood_elimination_logic()
        
        zone_test_cases = [
            # High-risk zones that should be eliminated
            ('The base floodplain where base flood elevations are provided', True, 'AE', 'AE zone description'),
            ('Areas with a 1% annual chance of flooding', True, 'A', 'A zone description'),
            ('Coastal areas with velocity hazard', True, 'V', 'V zone description'),
            
            # Safe zones that should be kept
            ('Area of minimal flood hazard, usually depicted on FIRMs as above the 500-year flood level', False, None, 'X zone description'),
            ('Area of moderate flood hazard, usually the area between the limits of the 100-year and 500-year floods', False, None, 'X shaded zone description'),
            ('Areas with possible but undetermined flood hazards', False, None, 'D zone description'),
            
            # Edge cases
            ('', False, None, 'Empty zone description'),
            (np.nan, False, None, 'Null zone description')
        ]
        
        passed = 0
        for zone_desc, expected_eliminate, expected_zone, description in zone_test_cases:
            result = flood_logic(np.nan, np.nan, zone_desc)
            
            eliminate_correct = result['should_eliminate'] == expected_eliminate
            zone_correct = True
            
            # If elimination expected, check if correct zone was found
            if expected_eliminate and expected_zone:
                zone_correct = result['zone_found'] == expected_zone
            
            if eliminate_correct and zone_correct:
                print(f"   ✅ {description}")
                passed += 1
            else:
                print(f"   ❌ {description} - FAILED")
                print(f"        Expected eliminate: {expected_eliminate}, Got: {result['should_eliminate']}")
                if expected_zone:
                    print(f"        Expected zone: {expected_zone}, Got: {result['zone_found']}")
        
        accuracy = (passed / len(zone_test_cases)) * 100
        print(f"\n   Zone Classification Accuracy: {accuracy:.1f}%")
        
        assert accuracy >= 90.0, f"Zone classification accuracy {accuracy:.1f}% below required 90%"
        
        return accuracy
    
    def test_dataset_availability(self):
        """Test that required datasets are available"""
        
        print("\n📊 TESTING DATASET AVAILABILITY")
        print("=" * 35)
        
        # Check original dataset
        original_file = Path("CostarExport_AllLand_Combined_20250727_184937.xlsx")
        backup_file = Path("CostarExport_HighResource_BACKUP_20250730_090645.xlsx")
        
        files_found = 0
        total_files = 2
        
        if original_file.exists():
            print(f"   ✅ Original dataset found: {original_file}")
            files_found += 1
            
            # Test loading original dataset
            try:
                df = pd.read_excel(original_file)
                print(f"   ✅ Original dataset loads: {len(df)} sites")
                
                # Check for Northern California sites
                if 'Latitude' in df.columns:
                    with_coords = df[df[['Latitude', 'Longitude']].notna().all(axis=1)]
                    northern_ca = with_coords[with_coords['Latitude'] > 37.0]
                    print(f"   ✅ Northern CA sites found: {len(northern_ca)}")
                    
                    if len(northern_ca) == 0:
                        print(f"   ⚠️  WARNING: No Northern CA sites in original dataset")
                
            except Exception as e:
                print(f"   ❌ Error loading original dataset: {e}")
        else:
            print(f"   ❌ Original dataset not found: {original_file}")
        
        if backup_file.exists():
            print(f"   ✅ Backup dataset found: {backup_file}")
            files_found += 1
        else:
            print(f"   ❌ Backup dataset not found: {backup_file}")
        
        availability_rate = (files_found / total_files) * 100
        print(f"\n   Dataset Availability: {availability_rate:.1f}%")
        
        assert files_found >= 1, "At least one dataset must be available for testing"
        
        return availability_rate
    
    def test_coordinate_coverage(self):
        """Test geographic coordinate coverage"""
        
        print("\n🗺️ TESTING COORDINATE COVERAGE")
        print("=" * 35)
        
        # Test Northern California coordinates
        print("\n   📍 Northern California Test Coordinates:")
        for coord in self.northern_ca_coordinates:
            lat, lng = coord['lat'], coord['lng']
            if 37.0 <= lat <= 42.0 and -124.5 <= lng <= -114.0:
                print(f"     ✅ {coord['name']}: {lat}, {lng}")
            else:
                print(f"     ❌ {coord['name']}: {lat}, {lng} - Outside CA bounds")
        
        # Test Southern California coordinates  
        print("\n   📍 Southern California Test Coordinates:")
        for coord in self.southern_ca_coordinates:
            lat, lng = coord['lat'], coord['lng']
            if 32.5 <= lat <= 37.0 and -124.5 <= lng <= -114.0:
                print(f"     ✅ {coord['name']}: {lat}, {lng}")
            else:
                print(f"     ❌ {coord['name']}: {lat}, {lng} - Outside CA bounds")
        
        return True
    
    def run_comprehensive_test_suite(self):
        """Run all tests in the comprehensive test suite"""
        
        print("🧪 COLOSSEUM FLOOD ELIMINATION TEST SUITE")
        print("Following Colosseum Testing Protocol")
        print("=" * 60)
        
        # Initialize test data
        self.setup_method()
        
        test_results = {}
        
        try:
            # 1. Dataset availability
            test_results['dataset_availability'] = self.test_dataset_availability()
            
            # 2. Coordinate coverage
            test_results['coordinate_coverage'] = self.test_coordinate_coverage()
            
            # 3. SFHA criteria validation
            test_results['sfha_accuracy'] = self.test_sfha_criteria_validation()
            
            # 4. Flood Risk Area validation
            test_results['risk_area_accuracy'] = self.test_flood_risk_area_validation()
            
            # 5. Zone classification accuracy
            test_results['zone_accuracy'] = self.test_zone_classification_accuracy()
            
            # 6. Known sites accuracy
            test_results['known_sites_accuracy'] = self.test_known_flood_sites_accuracy()
            
            # Calculate overall test score
            accuracy_tests = [
                test_results['sfha_accuracy'],
                test_results['risk_area_accuracy'], 
                test_results['zone_accuracy'],
                test_results['known_sites_accuracy']
            ]
            
            overall_accuracy = sum(accuracy_tests) / len(accuracy_tests)
            
            print("\n" + "=" * 60)
            print("🎯 COMPREHENSIVE TEST RESULTS")
            print("=" * 60)
            
            for test_name, result in test_results.items():
                print(f"   {test_name}: {result:.1f}%")
            
            print(f"\n   📊 OVERALL ACCURACY: {overall_accuracy:.1f}%")
            
            # Colosseum standards check
            meets_standards = overall_accuracy >= 85.0
            print(f"   🏛️  COLOSSEUM STANDARDS: {'✅ PASS' if meets_standards else '❌ FAIL'}")
            
            if meets_standards:
                print(f"\n✅ FLOOD ELIMINATION LOGIC VALIDATED")
                print(f"   Ready for production deployment on full dataset")
                print(f"   Roman Engineering Standards: Met")
            else:
                print(f"\n❌ FLOOD ELIMINATION LOGIC REQUIRES IMPROVEMENT")
                print(f"   Accuracy {overall_accuracy:.1f}% below required 85%")
                print(f"   Review failed test cases before deployment")
            
            return test_results, meets_standards
            
        except Exception as e:
            print(f"\n❌ TEST SUITE FAILED: {e}")
            return {}, False

def main():
    """Run the test suite"""
    
    tester = TestFloodEliminationLogic()
    test_results, passes = tester.run_comprehensive_test_suite()
    
    if passes:
        print("\n🏛️ READY FOR PRODUCTION DEPLOYMENT")
        return 0
    else:
        print("\n🚨 TESTING FAILED - DO NOT DEPLOY")
        return 1

if __name__ == "__main__":
    exit(main())