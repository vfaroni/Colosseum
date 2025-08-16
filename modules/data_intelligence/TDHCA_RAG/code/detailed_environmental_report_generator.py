#!/usr/bin/env python3

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

class DetailedEnvironmentalReportGenerator:
    """
    Generate comprehensive environmental status reports for D'Marco sites
    """
    
    def __init__(self):
        self.base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG"
        self.output_dir = f"{self.base_dir}/D'Marco_Sites/"
        
        # Load comprehensive environmental database
        self.env_database = f"{self.output_dir}Comprehensive_Environmental_Database.csv"
        self.risk_analysis = f"{self.output_dir}DMarco_Environmental_Risk_Analysis.json"
    
    def load_data(self):
        """Load environmental data and risk analysis"""
        print("📊 Loading comprehensive environmental data for detailed reporting...")
        
        env_df = pd.read_csv(self.env_database, low_memory=False)
        with open(self.risk_analysis, 'r') as f:
            risk_data = json.load(f)
        
        # Load D'Marco site data
        sites_file = "/Users/williamrice/priority_sites_data.json"
        with open(sites_file, 'r') as f:
            dmarco_sites = json.load(f)
        
        print(f"   ✅ Loaded {len(env_df)} environmental sites")
        print(f"   ✅ Loaded risk analysis for {len(risk_data)} D'Marco sites")
        print(f"   ✅ Loaded {len(dmarco_sites)} D'Marco site details")
        
        return env_df, risk_data, dmarco_sites
    
    def analyze_dataset_statistics(self, env_df):
        """Analyze statistics for each environmental dataset"""
        print("📈 Analyzing dataset statistics...")
        
        dataset_stats = {}
        
        for dataset in ['lpst', 'operating_dry_cleaners', 'enforcement']:
            dataset_sites = env_df[env_df['dataset'] == dataset]
            
            # Calculate distance statistics for each D'Marco site
            dmarco_stats = {}
            for i in range(1, 12):
                site_id = f"dmarco_site_{str(i).zfill(2)}"
                distance_col = f"{site_id}_distance_miles"
                
                if distance_col in dataset_sites.columns:
                    distances = dataset_sites[distance_col].dropna()
                    within_1_mile = dataset_sites[f"{site_id}_within_1_mile"].sum() if f"{site_id}_within_1_mile" in dataset_sites.columns else 0
                    
                    dmarco_stats[site_id] = {
                        'closest_distance_miles': distances.min() if len(distances) > 0 else None,
                        'sites_within_1_mile': int(within_1_mile),
                        'average_distance_miles': distances.mean() if len(distances) > 0 else None
                    }
            
            dataset_stats[dataset] = {
                'total_sites': len(dataset_sites),
                'sites_with_coordinates': len(dataset_sites.dropna(subset=['latitude', 'longitude'])),
                'average_geocoding_confidence': dataset_sites['geocoding_confidence'].mean(),
                'dmarco_proximity_stats': dmarco_stats
            }
        
        return dataset_stats
    
    def create_site_specific_analysis(self, site_id, risk_data, env_df, dmarco_sites):
        """Create detailed analysis for a specific D'Marco site"""
        site_index = int(site_id.split('_')[-1]) - 1
        site_info = dmarco_sites[site_index]
        site_risk = risk_data[site_id]
        
        # Get environmental sites within 1 mile
        environmental_threats = []
        
        for dataset in ['lpst', 'operating_dry_cleaners', 'enforcement']:
            dataset_sites = env_df[
                (env_df['dataset'] == dataset) & 
                (env_df[f'{site_id}_within_1_mile'] == True)
            ]
            
            for idx, threat in dataset_sites.iterrows():
                environmental_threats.append({
                    'dataset': dataset,
                    'site_name': threat['site_name'],
                    'risk_type': threat['risk_type'],
                    'address': threat['address'],
                    'city': threat['city'],
                    'distance_miles': threat[f'{site_id}_distance_miles'],
                    'risk_level': threat[f'{site_id}_risk_level'],
                    'status': threat['status'],
                    'coordinates': f"{threat['latitude']:.5f}, {threat['longitude']:.5f}"
                })
        
        # Sort by distance (closest first)
        environmental_threats.sort(key=lambda x: x['distance_miles'])
        
        # Determine due diligence requirements
        if site_risk['overall_risk_level'] in ['CRITICAL', 'HIGH']:
            due_diligence = {
                'phase_i_esa': 'Required - Enhanced scope with vapor assessment',
                'subsurface_investigation': 'Recommended - Soil borings and groundwater monitoring',
                'estimated_cost': '$8,000 - $15,000',
                'timeline': '4-6 weeks',
                'additional_requirements': 'Indoor air quality assessment may be needed'
            }
        elif site_risk['overall_risk_level'] == 'MEDIUM':
            due_diligence = {
                'phase_i_esa': 'Required - Standard scope',
                'subsurface_investigation': 'May be required based on Phase I findings',
                'estimated_cost': '$3,000 - $5,000',
                'timeline': '2-3 weeks',
                'additional_requirements': 'Standard environmental screening protocols'
            }
        else:
            due_diligence = {
                'phase_i_esa': 'Recommended - Standard due diligence',
                'subsurface_investigation': 'Unlikely to be required',
                'estimated_cost': '$1,500 - $3,000',
                'timeline': '1-2 weeks',
                'additional_requirements': 'Basic environmental compliance review'
            }
        
        return {
            'site_info': {
                'site_id': site_id,
                'address': site_info.get('Address', 'Unknown'),
                'size_acres': site_info.get('Size (Acres)', 0),
                'county': site_info.get('County', 'Unknown'),
                'region': site_info.get('Region', 'Unknown')
            },
            'risk_assessment': {
                'overall_risk_level': site_risk['overall_risk_level'],
                'total_environmental_sites': site_risk['total_environmental_sites'],
                'environmental_concern_types': site_risk['environmental_concerns'],
                'risks_by_type': site_risk['risks_by_type']
            },
            'environmental_threats': environmental_threats,
            'due_diligence_requirements': due_diligence
        }
    
    def generate_executive_summary(self, risk_data, dataset_stats):
        """Generate executive summary of environmental findings"""
        
        # Count sites by risk level
        risk_counts = {}
        for site_id, analysis in risk_data.items():
            risk_level = analysis['overall_risk_level']
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        # Calculate total environmental sites within 1 mile of all D'Marco sites
        total_threats = sum(analysis['total_environmental_sites'] for analysis in risk_data.values())
        
        # Identify highest risk sites
        critical_sites = [site_id for site_id, analysis in risk_data.items() if analysis['overall_risk_level'] == 'CRITICAL']
        high_risk_sites = [site_id for site_id, analysis in risk_data.items() if analysis['overall_risk_level'] == 'HIGH']
        
        return {
            'analysis_overview': {
                'total_dmarco_sites_analyzed': len(risk_data),
                'sites_with_environmental_concerns': len([s for s in risk_data.values() if s['overall_risk_level'] != 'NO RISK']),
                'total_environmental_threats_identified': total_threats,
                'environmental_datasets_analyzed': 3
            },
            'risk_level_distribution': risk_counts,
            'critical_findings': {
                'critical_risk_sites': critical_sites,
                'high_risk_sites': high_risk_sites,
                'sites_requiring_enhanced_due_diligence': critical_sites + high_risk_sites
            },
            'dataset_coverage': {
                'lpst_sites': dataset_stats['lpst']['total_sites'],
                'operating_dry_cleaners': dataset_stats['operating_dry_cleaners']['total_sites'],
                'enforcement_actions': dataset_stats['enforcement']['total_sites'],
                'total_environmental_sites': sum(ds['total_sites'] for ds in dataset_stats.values())
            }
        }
    
    def create_detailed_report(self):
        """Create comprehensive detailed environmental status report"""
        print("📋 GENERATING COMPREHENSIVE ENVIRONMENTAL STATUS REPORT")
        print("=" * 65)
        
        # Load data
        env_df, risk_data, dmarco_sites = self.load_data()
        
        # Analyze dataset statistics
        dataset_stats = self.analyze_dataset_statistics(env_df)
        
        # Generate executive summary
        executive_summary = self.generate_executive_summary(risk_data, dataset_stats)
        
        # Create site-specific analyses
        site_analyses = {}
        for i in range(1, 12):
            site_id = f"dmarco_site_{str(i).zfill(2)}"
            print(f"   📊 Analyzing {site_id}...")
            site_analyses[site_id] = self.create_site_specific_analysis(site_id, risk_data, env_df, dmarco_sites)
        
        # Compile comprehensive report
        comprehensive_report = {
            'report_metadata': {
                'report_title': "D'Marco Sites Comprehensive Environmental Status Report",
                'analysis_date': datetime.now().isoformat(),
                'report_type': 'Multi-Dataset Environmental Risk Assessment',
                'prepared_by': 'Structured Consultants LLC',
                'datasets_analyzed': ['LPST', 'Operating Dry Cleaners', 'Environmental Violations'],
                'total_environmental_sites': len(env_df)
            },
            'executive_summary': executive_summary,
            'dataset_statistics': dataset_stats,
            'site_specific_analyses': site_analyses,
            'methodology': {
                'geocoding_service': 'OpenStreetMap Nominatim + WKT Coordinate Parsing',
                'distance_calculation': 'Geodesic distance using geopy library',
                'risk_thresholds': {
                    'IMMEDIATE': '≤ 500 feet (0.095 miles)',
                    'CRITICAL': '≤ 1/4 mile (0.25 miles)',
                    'HIGH': '≤ 1/2 mile (0.5 miles)',
                    'MEDIUM': '≤ 1 mile (1.0 miles)',
                    'LOW': '> 1 mile'
                },
                'data_sources': 'Texas Commission on Environmental Quality (TCEQ) - July 2, 2025'
            }
        }
        
        # Save comprehensive report
        report_file = f"{self.output_dir}DMarco_Comprehensive_Environmental_Status_Report.json"
        with open(report_file, 'w') as f:
            json.dump(comprehensive_report, f, indent=2, default=str)
        
        print(f"\n✅ COMPREHENSIVE ENVIRONMENTAL STATUS REPORT COMPLETE!")
        print(f"   📋 Report saved: {report_file}")
        print(f"   📊 Sites analyzed: {len(site_analyses)}")
        print(f"   🌍 Environmental sites: {len(env_df):,}")
        
        # Print executive summary to console
        print(f"\n📈 EXECUTIVE SUMMARY:")
        print(f"   🚨 CRITICAL Risk Sites: {len(executive_summary['critical_findings']['critical_risk_sites'])}")
        print(f"   ⚠️ HIGH Risk Sites: {len(executive_summary['critical_findings']['high_risk_sites'])}")
        print(f"   📊 Total Environmental Threats: {executive_summary['analysis_overview']['total_environmental_threats_identified']}")
        print(f"   🏭 Sites Requiring Enhanced Due Diligence: {len(executive_summary['critical_findings']['sites_requiring_enhanced_due_diligence'])}")
        
        return comprehensive_report

def main():
    """Generate detailed environmental status report"""
    generator = DetailedEnvironmentalReportGenerator()
    report = generator.create_detailed_report()
    
    print("\n🎉 COMPREHENSIVE ENVIRONMENTAL ANALYSIS COMPLETE!")
    print("📋 Detailed status report with site-specific findings ready")
    print("🗺️ Interactive maps with multi-dataset visualization complete")

if __name__ == "__main__":
    main()