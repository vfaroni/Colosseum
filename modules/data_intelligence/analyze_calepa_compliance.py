#!/usr/bin/env python3
"""
Analyze CalEPA Compliance Datasets
Evaluations, Violations, and Enforcements
WINGMAN Analysis - Mission CA-ENV-2025-002
Date: 2025-08-09
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json

def analyze_calepa_compliance():
    """Analyze the three CalEPA compliance datasets"""
    
    base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
    data_path = base_path / "data_sets" / "california" / "CA_Environmental_Data" / "CalEPA_Compliance"
    
    print("="*80)
    print("CALEPA COMPLIANCE DATA ANALYSIS")
    print("="*80)
    
    results = {}
    
    # 1. Analyze Evaluations.csv
    print("\n1. EVALUATIONS DATASET")
    print("-"*40)
    eval_file = data_path / "Evaluations.csv"
    if eval_file.exists():
        # Read sample to understand structure
        df_eval = pd.read_csv(eval_file, nrows=10000, low_memory=False)
        print(f"File size: {eval_file.stat().st_size / (1024*1024):.1f} MB")
        print(f"Columns: {', '.join(df_eval.columns)}")
        print(f"Sample records analyzed: {len(df_eval)}")
        
        # Check for violations found
        if 'ViolationsFound' in df_eval.columns:
            violations_summary = df_eval['ViolationsFound'].value_counts()
            print(f"\nViolations Found:")
            for key, val in violations_summary.items():
                print(f"  {key}: {val}")
        
        # Check evaluation types
        if 'EvalType' in df_eval.columns:
            eval_types = df_eval['EvalType'].value_counts().head(5)
            print(f"\nTop Evaluation Types:")
            for eval_type, count in eval_types.items():
                print(f"  {eval_type}: {count}")
        
        results['evaluations'] = {
            'file_size_mb': eval_file.stat().st_size / (1024*1024),
            'columns': list(df_eval.columns),
            'sample_size': len(df_eval)
        }
    
    # 2. Analyze Violations.csv
    print("\n2. VIOLATIONS DATASET")
    print("-"*40)
    viol_file = data_path / "Violations.csv"
    if viol_file.exists():
        # This is huge (918MB), read smaller sample
        df_viol = pd.read_csv(viol_file, nrows=5000, low_memory=False)
        print(f"File size: {viol_file.stat().st_size / (1024*1024):.1f} MB")
        print(f"Columns: {', '.join(df_viol.columns)}")
        print(f"Sample records analyzed: {len(df_viol)}")
        
        # Check for county information
        county_cols = [col for col in df_viol.columns if 'county' in col.lower()]
        if county_cols:
            print(f"County columns found: {county_cols}")
        
        results['violations'] = {
            'file_size_mb': viol_file.stat().st_size / (1024*1024),
            'columns': list(df_viol.columns),
            'sample_size': len(df_viol)
        }
    
    # 3. Analyze EA.csv (Enforcements)
    print("\n3. ENFORCEMENTS DATASET")
    print("-"*40)
    ea_file = data_path / "EA.csv"
    if ea_file.exists():
        df_ea = pd.read_csv(ea_file, nrows=10000, low_memory=False)
        print(f"File size: {ea_file.stat().st_size / (1024*1024):.1f} MB")
        print(f"Columns: {', '.join(df_ea.columns)}")
        print(f"Sample records analyzed: {len(df_ea)}")
        
        # Check enforcement types if available
        action_cols = [col for col in df_ea.columns if 'action' in col.lower() or 'enforce' in col.lower()]
        if action_cols:
            print(f"Enforcement columns found: {action_cols}")
        
        results['enforcements'] = {
            'file_size_mb': ea_file.stat().st_size / (1024*1024),
            'columns': list(df_ea.columns),
            'sample_size': len(df_ea)
        }
    
    # Get actual record counts
    print("\n" + "="*80)
    print("GETTING ACTUAL RECORD COUNTS (this may take a moment)...")
    print("-"*80)
    
    # Count actual records using wc -l (faster than pandas for large files)
    import subprocess
    
    for filename, label in [("Evaluations.csv", "Evaluations"), 
                            ("Violations.csv", "Violations"), 
                            ("EA.csv", "Enforcements")]:
        filepath = data_path / filename
        if filepath.exists():
            result = subprocess.run(['wc', '-l', str(filepath)], capture_output=True, text=True)
            line_count = int(result.stdout.split()[0]) - 1  # Subtract header
            print(f"{label}: {line_count:,} records")
            results[label.lower()]['total_records'] = line_count
    
    # Save analysis results
    analysis_file = data_path / "calepa_compliance_analysis.json"
    with open(analysis_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*80)
    print("ANALYSIS SUMMARY")
    print("="*80)
    
    total_size = sum(r['file_size_mb'] for r in results.values())
    total_records = sum(r.get('total_records', 0) for r in results.values())
    
    print(f"Total Data Volume: {total_size:.1f} MB")
    print(f"Total Records (estimated): {total_records:,}")
    print(f"Datasets: {len(results)}")
    
    print("\nThis appears to be comprehensive CalEPA compliance data including:")
    print("- Site evaluations and inspections")
    print("- Environmental violations records")  
    print("- Enforcement actions taken")
    print("\nSimilar to Texas TCEQ data structure for compliance tracking")
    
    return results

if __name__ == "__main__":
    results = analyze_calepa_compliance()