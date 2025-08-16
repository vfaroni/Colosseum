#!/usr/bin/env python3
"""
CRITICAL VALIDATION: Fire Hazard & Flood Risk Analysis Accuracy Test

This script validates the accuracy of hazard identification systems
BEFORE applying any site filtering to prevent incorrect elimination.

Mission: VITOR-WINGMAN-HAZARD-001
Target: 630 sites in CostarExport_HighResource_BACKUP_20250730_090645.xlsx
"""

import pandas as pd
import sys
import os
from pathlib import Path

# Add the analyzer path
sys.path.append(str(Path(__file__).parent.parent / 'src' / 'analyzers'))

try:
    from fire_hazard_analyzer import FireHazardAnalyzer
except ImportError as e:
    print(f"❌ Error importing FireHazardAnalyzer: {e}")
    print("Please check the analyzer path and dependencies")
    sys.exit(1)

class HazardValidationTester:
    """Validates hazard analysis accuracy before production use"""
    
    def __init__(self):
        self.fire_analyzer = FireHazardAnalyzer(use_api=True)
        self.validation_results = []
        
    def run_known_site_validation(self):
        """Test hazard analysis on sites with known risk levels"""
        
        print("🚨 CRITICAL VALIDATION: Testing Known Fire/Flood Risk Sites")
        print("=" * 70)
        
        # Known high-risk fire areas (should be eliminated)
        high_fire_risk_sites = [
            {
                'name': 'Oakland Hills (1991 fire area)',
                'lat': 37.8716, 'lng': -122.2727,
                'expected_fire': 'High/Very High',
                'expected_elimination': True
            },
            {
                'name': 'Malibu Hills (fire-prone)',
                'lat': 34.0259, 'lng': -118.7798,
                'expected_fire': 'High/Very High',
                'expected_elimination': True
            },
            {
                'name': 'Santa Barbara foothills',
                'lat': 34.4208, 'lng': -119.6982,
                'expected_fire': 'High/Very High',
                'expected_elimination': True
            }
        ]
        
        # Known low-risk areas (should be kept)
        low_fire_risk_sites = [
            {
                'name': 'Downtown San Francisco',
                'lat': 37.7749, 'lng': -122.4194,
                'expected_fire': 'Low/Moderate',
                'expected_elimination': False
            },
            {
                'name': 'Central Valley (Fresno)',
                'lat': 36.7378, 'lng': -119.7871,
                'expected_fire': 'Low/Moderate',
                'expected_elimination': False
            },
            {
                'name': 'Downtown Los Angeles',
                'lat': 34.0522, 'lng': -118.2437,
                'expected_fire': 'Low/Moderate',
                'expected_elimination': False
            }
        ]
        
        print("🔥 FIRE HAZARD VALIDATION:")
        print("-" * 50)
        
        # Test high-risk sites
        print("\n🚨 Testing HIGH-RISK sites (should be ELIMINATED):")
        for site in high_fire_risk_sites:
            result = self._test_fire_site(site)
            self.validation_results.append(result)
            
        # Test low-risk sites
        print("\n✅ Testing LOW-RISK sites (should be KEPT):")
        for site in low_fire_risk_sites:
            result = self._test_fire_site(site)
            self.validation_results.append(result)
            
        return self._analyze_validation_results()
    
    def _test_fire_site(self, site):
        """Test individual site for fire hazard accuracy"""
        try:
            fire_result = self.fire_analyzer.analyze_fire_risk(
                site['lat'], site['lng']
            )
            
            hazard_class = fire_result.get('hazard_class', 'Unknown')
            meets_criteria = fire_result.get('meets_criteria')
            should_eliminate = not meets_criteria if meets_criteria is not None else None
            
            # Determine if results match expectations
            expected_elimination = site['expected_elimination']
            
            if should_eliminate is None:
                accuracy_status = "⚠️  REQUIRES_MANUAL_VERIFICATION"
                print(f"  ⚠️  {site['name']}: {hazard_class} - MANUAL VERIFICATION REQUIRED")
                if 'verification_sources' in fire_result:
                    print(f"     📋 Verify at: {fire_result['verification_sources'][0]}")
            elif should_eliminate == expected_elimination:
                accuracy_status = "✅ CORRECT"
                action = "ELIMINATE" if should_eliminate else "KEEP"
                print(f"  ✅ {site['name']}: {hazard_class} - {action} (correct)")
            else:
                accuracy_status = "❌ INCORRECT"
                expected_action = "ELIMINATE" if expected_elimination else "KEEP"
                actual_action = "ELIMINATE" if should_eliminate else "KEEP"
                print(f"  ❌ {site['name']}: {hazard_class} - Expected: {expected_action}, Got: {actual_action}")
            
            return {
                'site_name': site['name'],
                'coordinates': (site['lat'], site['lng']),
                'hazard_class': hazard_class,
                'should_eliminate': should_eliminate,
                'expected_elimination': expected_elimination,
                'accuracy_status': accuracy_status,
                'raw_result': fire_result
            }
            
        except Exception as e:
            print(f"  ❌ ERROR testing {site['name']}: {e}")
            return {
                'site_name': site['name'],
                'accuracy_status': "❌ ERROR",
                'error': str(e)
            }
    
    def _analyze_validation_results(self):
        """Analyze overall validation accuracy"""
        print("\n" + "=" * 70)
        print("📊 VALIDATION RESULTS SUMMARY:")
        print("=" * 70)
        
        correct_count = sum(1 for r in self.validation_results 
                          if r.get('accuracy_status') == '✅ CORRECT')
        incorrect_count = sum(1 for r in self.validation_results 
                            if r.get('accuracy_status') == '❌ INCORRECT')
        manual_verification_count = sum(1 for r in self.validation_results 
                                      if 'MANUAL_VERIFICATION' in r.get('accuracy_status', ''))
        error_count = sum(1 for r in self.validation_results 
                        if r.get('accuracy_status') == '❌ ERROR')
        
        total_tested = len(self.validation_results)
        
        print(f"✅ Correct classifications: {correct_count}/{total_tested}")
        print(f"❌ Incorrect classifications: {incorrect_count}/{total_tested}")
        print(f"⚠️  Manual verification needed: {manual_verification_count}/{total_tested}")
        print(f"💥 Errors encountered: {error_count}/{total_tested}")
        
        if total_tested > 0:
            accuracy_rate = (correct_count / (total_tested - manual_verification_count - error_count)) * 100 if (total_tested - manual_verification_count - error_count) > 0 else 0
            print(f"\n📈 Overall Accuracy Rate: {accuracy_rate:.1f}%")
        
        # Determine if system is ready for production
        print("\n🎯 PRODUCTION READINESS ASSESSMENT:")
        print("-" * 50)
        
        if incorrect_count > 0:
            print("🚨 CRITICAL: System has incorrect classifications!")
            print("❌ DO NOT PROCEED with automated site elimination")
            print("🔧 REQUIRED: Fix classification errors before proceeding")
            return False
        elif manual_verification_count > 2:
            print("⚠️  WARNING: Multiple sites require manual verification")
            print("📋 RECOMMENDED: Verify API data sources before proceeding")
            return None  # Proceed with caution
        elif error_count > 0:
            print("💥 ERROR: System errors detected")
            print("🔧 REQUIRED: Fix system errors before proceeding")
            return False
        else:
            print("✅ VALIDATION PASSED: System ready for production use")
            print("🎯 Safe to proceed with automated site filtering")
            return True
    
    def test_actual_dataset_sample(self, dataset_path, sample_size=5):
        """Test a sample of actual sites from the dataset"""
        print(f"\n🗂️  TESTING ACTUAL DATASET SAMPLE:")
        print("-" * 50)
        
        try:
            df = pd.read_excel(dataset_path)
            
            # Get sites with coordinates
            coords_available = df[df[['Latitude', 'Longitude']].notna().all(axis=1)]
            
            if len(coords_available) < sample_size:
                sample_size = len(coords_available)
                
            # Sample random sites
            sample_sites = coords_available.sample(n=sample_size, random_state=42)
            
            print(f"Testing {sample_size} random sites from dataset...")
            
            for idx, row in sample_sites.iterrows():
                lat, lng = row['Latitude'], row['Longitude']
                address = row.get('Property Address', 'Unknown Address')
                
                try:
                    fire_result = self.fire_analyzer.analyze_fire_risk(lat, lng)
                    hazard_class = fire_result.get('hazard_class', 'Unknown')
                    meets_criteria = fire_result.get('meets_criteria')
                    
                    if meets_criteria is None:
                        status = "⚠️  MANUAL VERIFICATION REQUIRED"
                    elif meets_criteria:
                        status = "✅ SAFE (keep site)"
                    else:
                        status = "🚨 HIGH RISK (eliminate site)"
                    
                    print(f"  {address[:50]:<50} | {hazard_class:<15} | {status}")
                    
                except Exception as e:
                    print(f"  {address[:50]:<50} | ERROR: {str(e)[:30]}")
                    
        except Exception as e:
            print(f"❌ Error testing dataset sample: {e}")


def main():
    """Run comprehensive validation before site filtering"""
    print("🏛️ COLOSSEUM HAZARD VALIDATION SYSTEM")
    print("Mission: VITOR-WINGMAN-HAZARD-001")
    print("=" * 70)
    
    tester = HazardValidationTester()
    
    # Run known site validation
    validation_passed = tester.run_known_site_validation()
    
    # Test sample from actual dataset
    dataset_path = "CostarExport_HighResource_BACKUP_20250730_090645.xlsx"
    if os.path.exists(dataset_path):
        tester.test_actual_dataset_sample(dataset_path, sample_size=10)
    else:
        print(f"\n⚠️  Dataset not found: {dataset_path}")
    
    print("\n" + "=" * 70)
    print("🎯 FINAL RECOMMENDATION:")
    print("=" * 70)
    
    if validation_passed is True:
        print("✅ PROCEED: Validation successful - safe to filter sites")
    elif validation_passed is None:
        print("⚠️  PROCEED WITH CAUTION: Some manual verification required")
    else:
        print("❌ STOP: Fix validation issues before proceeding")
        print("🚨 DO NOT eliminate any sites until validation passes")
    
    return validation_passed


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result is not False else 1)