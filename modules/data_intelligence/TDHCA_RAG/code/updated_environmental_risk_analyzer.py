#!/usr/bin/env python3

import pandas as pd
import json
import numpy as np
from pathlib import Path
from datetime import datetime

class UpdatedEnvironmentalRiskAnalyzer:
    """
    Updated environmental risk analyzer using proper distance-based risk categories
    Based on industry-standard environmental due diligence practices
    """
    
    def __init__(self):
        self.base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG"
        self.output_dir = f"{self.base_dir}/D'Marco_Sites/"
        
        # Load comprehensive environmental database
        self.env_database = f"{self.output_dir}Comprehensive_Environmental_Database.csv"
        
        # Updated risk thresholds based on industry standards
        self.risk_thresholds = {
            'CRITICAL': {
                'max_distance_miles': 0.0,  # On-site
                'description': 'On-site contamination',
                'due_diligence': 'Immediate Phase II ESA and remediation assessment required',
                'cost_range': '$15,000 - $50,000+',
                'timeline': '6-12 weeks',
                'regulatory_impact': 'Immediate regulatory liability'
            },
            'HIGH': {
                'max_distance_miles': 500 * 0.000189394,  # 500 feet in miles (0.0947 miles)
                'description': 'Within 500 feet - Vapor intrusion potential',
                'due_diligence': 'Phase II ESA typically required, environmental insurance needed',
                'cost_range': '$12,000 - $25,000',
                'timeline': '4-8 weeks',
                'regulatory_impact': 'Groundwater migration and vapor intrusion concerns'
            },
            'MODERATE-HIGH': {
                'max_distance_miles': 0.1,  # 500 feet to 0.1 mile
                'description': '500 feet to 0.1 mile - Potential groundwater impacts',
                'due_diligence': 'Enhanced due diligence recommended, case-by-case evaluation',
                'cost_range': '$8,000 - $15,000',
                'timeline': '3-6 weeks',
                'regulatory_impact': 'Vapor concerns for chlorinated solvents'
            },
            'MODERATE': {
                'max_distance_miles': 0.25,  # 0.1 to 0.25 mile
                'description': '0.1 to 0.25 mile - Limited direct impact potential',
                'due_diligence': 'Standard Phase I protocols apply',
                'cost_range': '$5,000 - $8,000',
                'timeline': '2-4 weeks',
                'regulatory_impact': 'Regulatory database triggers'
            },
            'LOW-MODERATE': {
                'max_distance_miles': 0.5,  # 0.25 to 0.5 mile
                'description': '0.25 to 0.5 mile - Minimal direct site impact',
                'due_diligence': 'Standard environmental review',
                'cost_range': '$3,000 - $5,000',
                'timeline': '1-3 weeks',
                'regulatory_impact': 'Database documentation required'
            },
            'LOW': {
                'max_distance_miles': 1.0,  # 0.5 to 1.0 mile
                'description': '0.5 to 1.0 mile - Negligible site impact potential',
                'due_diligence': 'Standard documentation, database recording',
                'cost_range': '$1,500 - $3,000',
                'timeline': '1-2 weeks',
                'regulatory_impact': 'Standard regulatory compliance'
            }
        }
        
        # Contaminant-specific risk modifiers
        self.contaminant_modifiers = {
            'Petroleum Contamination': {
                'modifier': 1.0,
                'notes': 'Standard petroleum hydrocarbon assessment'
            },
            'Active Solvent Operations': {
                'modifier': 1.2,  # Higher risk due to chlorinated solvents
                'notes': 'Enhanced vapor intrusion concerns for dry cleaning solvents'
            },
            'Environmental Violations': {
                'modifier': 1.1,  # Slightly elevated due to unknown contaminants
                'notes': 'Unknown contaminant types require enhanced evaluation'
            }
        }
    
    def determine_risk_level(self, distance_miles, contaminant_type='Unknown'):
        """Determine risk level based on distance and contaminant type"""
        
        # Apply contaminant modifier
        modifier = self.contaminant_modifiers.get(contaminant_type, {}).get('modifier', 1.0)
        effective_distance = distance_miles / modifier  # Closer effective distance for higher-risk contaminants
        
        if effective_distance <= 0.001:  # Essentially on-site
            return 'CRITICAL'
        elif effective_distance <= self.risk_thresholds['HIGH']['max_distance_miles']:
            return 'HIGH'
        elif effective_distance <= self.risk_thresholds['MODERATE-HIGH']['max_distance_miles']:
            return 'MODERATE-HIGH'
        elif effective_distance <= self.risk_thresholds['MODERATE']['max_distance_miles']:
            return 'MODERATE'
        elif effective_distance <= self.risk_thresholds['LOW-MODERATE']['max_distance_miles']:
            return 'LOW-MODERATE'
        elif effective_distance <= self.risk_thresholds['LOW']['max_distance_miles']:
            return 'LOW'
        else:
            return 'NEGLIGIBLE'
    
    def load_and_filter_data(self):
        """Load environmental data and filter out problematic sites"""
        print("📊 Loading environmental data with quality filtering...")
        
        env_df = pd.read_csv(self.env_database, low_memory=False)
        print(f"   ✅ Loaded {len(env_df)} total environmental sites")
        
        # Filter out sites with data quality issues
        original_count = len(env_df)
        
        # Remove sites with 'nan' addresses
        env_df = env_df[~(env_df['address'].isna() | env_df['address'].str.contains('nan', case=False, na=False))]
        
        # Remove sites with low geocoding confidence
        env_df = env_df[env_df['geocoding_confidence'] >= 0.8]
        
        filtered_count = len(env_df)
        excluded_count = original_count - filtered_count
        
        print(f"   ✅ Quality filtering complete:")
        print(f"      • Sites excluded: {excluded_count}")
        print(f"      • Valid sites remaining: {filtered_count}")
        
        return env_df
    
    def recalculate_dmarco_risks(self, env_df):
        """Recalculate D'Marco site risks using updated thresholds and clean data"""
        print("🎯 Recalculating D'Marco site risks with updated methodology...")
        
        updated_risk_analysis = {}
        
        for i in range(1, 12):
            site_id = f"dmarco_site_{str(i).zfill(2)}"
            print(f"   📊 Analyzing {site_id}...")
            
            # Find all environmental sites and their distances
            site_risks = []
            risk_counts_by_level = {}
            risk_counts_by_type = {}
            
            for idx, env_site in env_df.iterrows():
                distance_col = f"{site_id}_distance_miles"
                if distance_col in env_df.columns and not pd.isna(env_site[distance_col]):
                    distance = env_site[distance_col]
                    contaminant_type = env_site['risk_type']
                    
                    # Calculate updated risk level
                    risk_level = self.determine_risk_level(distance, contaminant_type)
                    
                    if risk_level != 'NEGLIGIBLE':  # Only include sites with meaningful risk
                        site_risks.append({
                            'dataset': env_site['dataset'],
                            'site_name': env_site['site_name'],
                            'address': env_site['address'],
                            'risk_type': contaminant_type,
                            'distance_miles': distance,
                            'risk_level': risk_level,
                            'geocoding_confidence': env_site['geocoding_confidence']
                        })
                        
                        # Count by risk level
                        risk_counts_by_level[risk_level] = risk_counts_by_level.get(risk_level, 0) + 1
                        
                        # Count by risk type
                        risk_counts_by_type[contaminant_type] = risk_counts_by_type.get(contaminant_type, 0) + 1
            
            # Determine overall site risk level (highest individual risk)
            if not site_risks:
                overall_risk = 'NO RISK'
            else:
                risk_hierarchy = ['CRITICAL', 'HIGH', 'MODERATE-HIGH', 'MODERATE', 'LOW-MODERATE', 'LOW']
                overall_risk = 'LOW'
                for level in risk_hierarchy:
                    if level in risk_counts_by_level:
                        overall_risk = level
                        break
            
            # Organize risks by type for reporting
            risks_by_type = {}
            for risk in site_risks:
                risk_type = risk['risk_type']
                if risk_type not in risks_by_type:
                    risks_by_type[risk_type] = []
                risks_by_type[risk_type].append(risk)
            
            # Sort risks by distance (closest first)
            site_risks.sort(key=lambda x: x['distance_miles'])
            
            updated_risk_analysis[site_id] = {
                'overall_risk_level': overall_risk,
                'total_environmental_sites': len(site_risks),
                'environmental_concerns': len(set(risk['risk_type'] for risk in site_risks)),
                'risks_by_level': risk_counts_by_level,
                'risks_by_type': risks_by_type,
                'all_risks': site_risks,
                'due_diligence_requirements': self.risk_thresholds.get(overall_risk, {})
            }
            
            print(f"      ✅ {site_id}: {overall_risk} ({len(site_risks)} sites)")
        
        return updated_risk_analysis
    
    def create_updated_analysis_report(self):
        """Create updated environmental risk analysis with proper thresholds"""
        print("📋 CREATING UPDATED ENVIRONMENTAL RISK ANALYSIS")
        print("=" * 55)
        
        # Load filtered data
        env_df = self.load_and_filter_data()
        
        # Recalculate risks
        updated_risks = self.recalculate_dmarco_risks(env_df)
        
        # Create comparison with old analysis
        old_analysis_file = f"{self.output_dir}DMarco_Environmental_Risk_Analysis.json"
        if Path(old_analysis_file).exists():
            with open(old_analysis_file, 'r') as f:
                old_analysis = json.load(f)
        else:
            old_analysis = {}
        
        # Generate comparison report
        comparison_data = {}
        for site_id in updated_risks.keys():
            old_risk = old_analysis.get(site_id, {}).get('overall_risk_level', 'Unknown')
            new_risk = updated_risks[site_id]['overall_risk_level']
            old_count = old_analysis.get(site_id, {}).get('total_environmental_sites', 0)
            new_count = updated_risks[site_id]['total_environmental_sites']
            
            comparison_data[site_id] = {
                'old_risk_level': old_risk,
                'new_risk_level': new_risk,
                'risk_changed': old_risk != new_risk,
                'old_site_count': old_count,
                'new_site_count': new_count,
                'sites_excluded': old_count - new_count
            }
        
        # Create comprehensive report
        updated_report = {
            'report_metadata': {
                'report_title': 'Updated D\'Marco Environmental Risk Analysis',
                'analysis_date': datetime.now().isoformat(),
                'report_type': 'Updated Risk Assessment with Industry-Standard Thresholds',
                'prepared_by': 'Structured Consultants LLC',
                'methodology_update': 'Applied proper environmental distance-based risk categories'
            },
            'methodology_updates': {
                'risk_threshold_changes': self.risk_thresholds,
                'contaminant_modifiers': self.contaminant_modifiers,
                'data_quality_improvements': [
                    'Excluded sites with \'nan\' addresses',
                    'Excluded sites with geocoding confidence < 0.8',
                    'Applied contaminant-specific risk modifiers'
                ]
            },
            'updated_site_analysis': updated_risks,
            'comparison_with_old_analysis': comparison_data,
            'executive_summary': {
                'total_sites_analyzed': 11,
                'methodology_improvements': [
                    'Industry-standard distance-based risk categories',
                    'Contaminant-specific risk modifiers',
                    'Enhanced data quality filtering'
                ]
            }
        }
        
        # Save updated analysis
        updated_file = f"{self.output_dir}Updated_DMarco_Environmental_Risk_Analysis.json"
        with open(updated_file, 'w') as f:
            json.dump(updated_report, f, indent=2, default=str)
        
        print(f"\n✅ UPDATED RISK ANALYSIS COMPLETE!")
        print(f"   📋 Report saved: {updated_file}")
        
        # Print comparison summary
        print(f"\n📊 RISK LEVEL CHANGES:")
        for site_id, comparison in comparison_data.items():
            if comparison['risk_changed']:
                print(f"   • {site_id.upper()}: {comparison['old_risk_level']} → {comparison['new_risk_level']}")
                if comparison['sites_excluded'] > 0:
                    print(f"     ({comparison['sites_excluded']} problematic sites excluded)")
        
        # Print new risk distribution
        risk_distribution = {}
        for site_data in updated_risks.values():
            risk_level = site_data['overall_risk_level']
            risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
        
        print(f"\n📈 UPDATED RISK DISTRIBUTION:")
        for risk_level, count in sorted(risk_distribution.items()):
            print(f"   • {risk_level}: {count} sites")
        
        return updated_report

def main():
    """Create updated environmental risk analysis"""
    analyzer = UpdatedEnvironmentalRiskAnalyzer()
    report = analyzer.create_updated_analysis_report()
    
    print("\n🎉 ENVIRONMENTAL RISK METHODOLOGY UPDATED!")
    print("📋 Industry-standard distance thresholds now applied")
    print("🧹 Data quality filtering implemented")

if __name__ == "__main__":
    main()