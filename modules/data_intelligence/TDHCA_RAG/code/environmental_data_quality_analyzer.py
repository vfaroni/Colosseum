#!/usr/bin/env python3

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

class EnvironmentalDataQualityAnalyzer:
    """
    Analyze data quality issues in the comprehensive environmental database
    Focus on sites with 'nan' addresses and other data quality problems
    """
    
    def __init__(self):
        self.base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG"
        self.output_dir = f"{self.base_dir}/D'Marco_Sites/"
        
        # Load comprehensive environmental database
        self.env_database = f"{self.output_dir}Comprehensive_Environmental_Database.csv"
    
    def load_environmental_data(self):
        """Load the comprehensive environmental database"""
        print("📊 Loading comprehensive environmental database for quality analysis...")
        
        env_df = pd.read_csv(self.env_database, low_memory=False)
        print(f"   ✅ Loaded {len(env_df)} environmental sites")
        
        return env_df
    
    def analyze_address_quality(self, env_df):
        """Analyze address data quality issues"""
        print("🏠 Analyzing address data quality...")
        
        # Check for various address issues
        address_issues = {}
        
        # Sites with 'nan' addresses
        address_issues['nan_addresses'] = env_df[env_df['address'].isna() | (env_df['address'] == 'nan')].copy()
        
        # Sites with empty/null addresses
        address_issues['empty_addresses'] = env_df[env_df['address'].isin(['', ' ', None])].copy()
        
        # Sites with very short addresses (likely incomplete)
        address_issues['short_addresses'] = env_df[env_df['address'].str.len() < 5].copy()
        
        # Sites with generic/placeholder addresses
        generic_patterns = ['N/A', 'TBD', 'UNKNOWN', 'NOT PROVIDED', '0', 'NONE']
        address_issues['generic_addresses'] = env_df[env_df['address'].str.upper().isin(generic_patterns)].copy()
        
        # Combine all address issues
        all_bad_addresses = pd.concat([
            address_issues['nan_addresses'],
            address_issues['empty_addresses'], 
            address_issues['short_addresses'],
            address_issues['generic_addresses']
        ]).drop_duplicates()
        
        print(f"   📊 Address Quality Analysis:")
        print(f"      • NaN addresses: {len(address_issues['nan_addresses'])}")
        print(f"      • Empty addresses: {len(address_issues['empty_addresses'])}")
        print(f"      • Short addresses (< 5 chars): {len(address_issues['short_addresses'])}")
        print(f"      • Generic addresses: {len(address_issues['generic_addresses'])}")
        print(f"      • Total problematic addresses: {len(all_bad_addresses)}")
        
        return address_issues, all_bad_addresses
    
    def analyze_geocoding_quality(self, env_df):
        """Analyze geocoding confidence and coordinate quality"""
        print("🌍 Analyzing geocoding quality...")
        
        geocoding_issues = {}
        
        # Sites with low geocoding confidence
        geocoding_issues['low_confidence'] = env_df[env_df['geocoding_confidence'] < 0.8].copy()
        
        # Sites with invalid coordinates (0,0 or extreme values)
        geocoding_issues['invalid_coords'] = env_df[
            ((env_df['latitude'] == 0) & (env_df['longitude'] == 0)) |
            (env_df['latitude'].abs() > 90) |
            (env_df['longitude'].abs() > 180) |
            env_df['latitude'].isna() |
            env_df['longitude'].isna()
        ].copy()
        
        # Sites with coordinates that seem to be geographic centers (common with bad geocoding)
        # Look for coordinates with many decimal places that end in common patterns
        geocoding_issues['suspicious_coords'] = env_df[
            env_df['geocoding_confidence'] < 1.0
        ].copy()
        
        print(f"   📊 Geocoding Quality Analysis:")
        print(f"      • Low confidence (< 0.8): {len(geocoding_issues['low_confidence'])}")
        print(f"      • Invalid coordinates: {len(geocoding_issues['invalid_coords'])}")
        print(f"      • Suspicious coordinates (< 1.0 confidence): {len(geocoding_issues['suspicious_coords'])}")
        
        return geocoding_issues
    
    def analyze_dataset_specific_issues(self, env_df):
        """Analyze data quality issues by dataset"""
        print("📂 Analyzing dataset-specific quality issues...")
        
        dataset_quality = {}
        
        for dataset in ['lpst', 'operating_dry_cleaners', 'enforcement']:
            dataset_sites = env_df[env_df['dataset'] == dataset].copy()
            
            # Address issues for this dataset
            nan_addresses = len(dataset_sites[dataset_sites['address'].isna() | (dataset_sites['address'] == 'nan')])
            low_confidence = len(dataset_sites[dataset_sites['geocoding_confidence'] < 0.8])
            
            dataset_quality[dataset] = {
                'total_sites': len(dataset_sites),
                'nan_addresses': nan_addresses,
                'nan_percentage': (nan_addresses / len(dataset_sites)) * 100 if len(dataset_sites) > 0 else 0,
                'low_confidence_geocoding': low_confidence,
                'low_confidence_percentage': (low_confidence / len(dataset_sites)) * 100 if len(dataset_sites) > 0 else 0
            }
            
            print(f"   📊 {dataset.upper()} Dataset:")
            print(f"      • Total sites: {dataset_quality[dataset]['total_sites']}")
            print(f"      • NaN addresses: {nan_addresses} ({dataset_quality[dataset]['nan_percentage']:.1f}%)")
            print(f"      • Low confidence geocoding: {low_confidence} ({dataset_quality[dataset]['low_confidence_percentage']:.1f}%)")
        
        return dataset_quality
    
    def find_sites_affecting_dmarco_analysis(self, env_df, bad_addresses_df):
        """Find problematic sites that are currently flagged as risks for D'Marco sites"""
        print("🚨 Finding problematic sites affecting D'Marco risk analysis...")
        
        affected_analysis = {}
        
        # Check each D'Marco site for bad data affecting their risk assessment
        for i in range(1, 12):
            site_id = f"dmarco_site_{str(i).zfill(2)}"
            within_1_mile_col = f"{site_id}_within_1_mile"
            
            if within_1_mile_col in env_df.columns:
                # Find bad sites within 1 mile of this D'Marco site
                bad_sites_affecting = bad_addresses_df[
                    bad_addresses_df[within_1_mile_col] == True
                ].copy()
                
                if len(bad_sites_affecting) > 0:
                    affected_analysis[site_id] = {
                        'total_bad_sites_within_1_mile': len(bad_sites_affecting),
                        'bad_sites_details': []
                    }
                    
                    for idx, bad_site in bad_sites_affecting.iterrows():
                        affected_analysis[site_id]['bad_sites_details'].append({
                            'site_name': bad_site['site_name'],
                            'address': bad_site['address'],
                            'dataset': bad_site['dataset'],
                            'geocoding_confidence': bad_site['geocoding_confidence'],
                            'distance_miles': bad_site[f"{site_id}_distance_miles"],
                            'risk_level': bad_site[f"{site_id}_risk_level"]
                        })
                    
                    print(f"   🎯 {site_id.upper()}: {len(bad_sites_affecting)} problematic sites within 1 mile")
        
        return affected_analysis
    
    def create_detailed_quality_report(self):
        """Create comprehensive data quality analysis report"""
        print("📋 CREATING COMPREHENSIVE ENVIRONMENTAL DATA QUALITY REPORT")
        print("=" * 70)
        
        # Load data
        env_df = self.load_environmental_data()
        
        # Analyze address quality
        address_issues, all_bad_addresses = self.analyze_address_quality(env_df)
        
        # Analyze geocoding quality
        geocoding_issues = self.analyze_geocoding_quality(env_df)
        
        # Analyze dataset-specific issues
        dataset_quality = self.analyze_dataset_specific_issues(env_df)
        
        # Find sites affecting D'Marco analysis
        affected_analysis = self.find_sites_affecting_dmarco_analysis(env_df, all_bad_addresses)
        
        # Calculate overall statistics
        total_sites = len(env_df)
        total_bad_addresses = len(all_bad_addresses)
        bad_address_percentage = (total_bad_addresses / total_sites) * 100
        
        # Create comprehensive report
        quality_report = {
            'report_metadata': {
                'report_title': 'Environmental Database Data Quality Analysis',
                'analysis_date': datetime.now().isoformat(),
                'report_type': 'Data Quality Assessment',
                'prepared_by': 'Structured Consultants LLC',
                'total_environmental_sites': total_sites
            },
            'executive_summary': {
                'total_sites_analyzed': total_sites,
                'sites_with_address_issues': total_bad_addresses,
                'bad_address_percentage': round(bad_address_percentage, 2),
                'dmarco_sites_affected': len(affected_analysis),
                'critical_finding': f"{total_bad_addresses} sites ({bad_address_percentage:.1f}%) have problematic address data that may invalidate environmental risk analysis"
            },
            'address_quality_analysis': {
                'nan_addresses': len(address_issues['nan_addresses']),
                'empty_addresses': len(address_issues['empty_addresses']),
                'short_addresses': len(address_issues['short_addresses']),
                'generic_addresses': len(address_issues['generic_addresses']),
                'total_problematic': total_bad_addresses
            },
            'geocoding_quality_analysis': {
                'low_confidence_sites': len(geocoding_issues['low_confidence']),
                'invalid_coordinates': len(geocoding_issues['invalid_coords']),
                'suspicious_coordinates': len(geocoding_issues['suspicious_coords'])
            },
            'dataset_quality_breakdown': dataset_quality,
            'dmarco_impact_analysis': affected_analysis,
            'recommendations': {
                'immediate_actions': [
                    f"Exclude {total_bad_addresses} sites with problematic addresses from risk analysis",
                    "Implement data validation to filter out 'nan' and invalid addresses",
                    "Re-run D'Marco environmental risk analysis with clean data only",
                    "Update mapping system to exclude low-quality geocoded sites"
                ],
                'data_improvement': [
                    "Research actual addresses for sites with 'nan' addresses where possible",
                    "Improve geocoding confidence thresholds (require > 0.8)",
                    "Validate coordinates against known geographic boundaries",
                    "Implement automated data quality checks in processing pipeline"
                ]
            }
        }
        
        # Save detailed report
        report_file = f"{self.output_dir}Environmental_Data_Quality_Analysis.json"
        with open(report_file, 'w') as f:
            json.dump(quality_report, f, indent=2, default=str)
        
        # Save list of problematic sites for exclusion
        bad_sites_file = f"{self.output_dir}Problematic_Environmental_Sites_for_Exclusion.csv"
        all_bad_addresses.to_csv(bad_sites_file, index=False)
        
        print(f"\n✅ DATA QUALITY ANALYSIS COMPLETE!")
        print(f"   📋 Report saved: {report_file}")
        print(f"   📊 Problematic sites list: {bad_sites_file}")
        
        # Print key findings to console
        print(f"\n🚨 KEY FINDINGS:")
        print(f"   📊 Total environmental sites: {total_sites:,}")
        print(f"   ❌ Sites with address issues: {total_bad_addresses:,} ({bad_address_percentage:.1f}%)")
        print(f"   🎯 D'Marco sites affected: {len(affected_analysis)} of 11")
        print(f"   🏠 Sites with 'nan' addresses: {len(address_issues['nan_addresses'])}")
        print(f"   🌍 Sites with low geocoding confidence: {len(geocoding_issues['low_confidence'])}")
        
        print(f"\n💡 IMPACT ON D'MARCO ANALYSIS:")
        for site_id, impact in affected_analysis.items():
            print(f"   • {site_id.upper()}: {impact['total_bad_sites_within_1_mile']} problematic sites within 1 mile")
        
        return quality_report

def main():
    """Analyze environmental data quality issues"""
    analyzer = EnvironmentalDataQualityAnalyzer()
    report = analyzer.create_detailed_quality_report()
    
    print("\n🎉 DATA QUALITY ANALYSIS COMPLETE!")
    print("📋 Comprehensive report shows extent of 'nan' address and geocoding issues")
    print("🚨 Recommendations provided for data cleanup and re-analysis")

if __name__ == "__main__":
    main()