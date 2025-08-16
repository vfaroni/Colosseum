#!/usr/bin/env python3
"""
Analyze TDHCA extraction completeness to benchmark current system performance
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

def analyze_tdhca_completeness():
    """Analyze the completeness of TDHCA extraction results"""
    
    # Load the Excel file
    file_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/code/TDHCA_Complete_Analysis_20250724_234946.xlsx"
    
    try:
        df = pd.read_excel(file_path)
        
        print("📊 TDHCA Extraction Completeness Analysis")
        print("=" * 60)
        
        # Basic stats
        print(f"\n📈 Dataset Overview:")
        print(f"Total Records: {len(df)}")
        print(f"Total Columns: {len(df.columns)}")
        
        # Analyze missing data by column
        print("\n🔍 Missing Data Analysis:")
        missing_stats = []
        
        for col in df.columns:
            total = len(df)
            missing = df[col].isna().sum()
            missing_pct = (missing / total) * 100
            
            missing_stats.append({
                'column': col,
                'missing_count': missing,
                'missing_pct': missing_pct,
                'complete_pct': 100 - missing_pct
            })
        
        # Sort by completeness
        missing_stats.sort(key=lambda x: x['missing_pct'])
        
        # Show best fields (most complete)
        print("\n✅ Best Extracted Fields (>90% complete):")
        for stat in missing_stats:
            if stat['complete_pct'] > 90:
                print(f"  - {stat['column']}: {stat['complete_pct']:.1f}% complete")
        
        # Show problematic fields
        print("\n❌ Problematic Fields (<50% complete):")
        for stat in missing_stats:
            if stat['complete_pct'] < 50:
                print(f"  - {stat['column']}: {stat['complete_pct']:.1f}% complete ({stat['missing_count']} missing)")
        
        # Calculate overall completeness
        total_cells = len(df) * len(df.columns)
        total_missing = df.isna().sum().sum()
        overall_completeness = ((total_cells - total_missing) / total_cells) * 100
        
        print(f"\n📊 Overall Data Completeness: {overall_completeness:.1f}%")
        
        # Analyze by data category
        print("\n📂 Completeness by Category:")
        
        # Define field categories
        categories = {
            'Basic Info': ['application_number', 'project_name', 'development_type', 'property_type'],
            'Location': ['street_address', 'city', 'county', 'state', 'zip_code', 'census_tract'],
            'Units': ['total_units', 'lihtc_units', 'market_units'],
            'Financial': ['total_development_cost', 'lihtc_equity', 'developer_fee'],
            'Team': ['developer_name', 'developer_contact', 'developer_email'],
            'Scoring': ['total_score', 'ami_30_percent', 'ami_50_percent', 'ami_60_percent']
        }
        
        category_stats = {}
        for category, fields in categories.items():
            available_fields = [f for f in fields if f in df.columns]
            if available_fields:
                category_missing = df[available_fields].isna().sum().sum()
                category_total = len(df) * len(available_fields)
                category_complete = ((category_total - category_missing) / category_total) * 100
                category_stats[category] = category_complete
                print(f"  - {category}: {category_complete:.1f}% complete")
        
        # Recommendations for improvement
        print("\n💡 Key Insights for Hybrid Model Improvement:")
        
        # Identify patterns in missing data
        if 'application_number' in df.columns:
            # Group by application to see if certain applications have more missing data
            app_completeness = df.groupby('application_number').apply(
                lambda x: (x.notna().sum().sum() / (len(x.columns) * len(x))) * 100
            ).sort_values()
            
            print(f"\n📱 Applications with lowest completeness:")
            for app, completeness in app_completeness.head(5).items():
                print(f"  - {app}: {completeness:.1f}% complete")
        
        # Save detailed analysis
        analysis_results = {
            'overall_completeness': overall_completeness,
            'total_records': len(df),
            'field_stats': missing_stats,
            'category_stats': category_stats,
            'recommendations': [
                'Focus Docling on tables for financial data extraction',
                'Use Granite for regulatory compliance fields',
                'Apply Claude Opus for complex address parsing',
                'Implement OCR preprocessing for scanned sections'
            ]
        }
        
        # Save analysis
        output_path = Path(__file__).parent / 'tdhca_completeness_analysis.json'
        with open(output_path, 'w') as f:
            json.dump(analysis_results, f, indent=2)
        
        print(f"\n💾 Detailed analysis saved to: {output_path}")
        
        # Return for benchmarking
        return analysis_results
        
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")
        return None

if __name__ == "__main__":
    results = analyze_tdhca_completeness()