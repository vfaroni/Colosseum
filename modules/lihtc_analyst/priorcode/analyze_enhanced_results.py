#!/usr/bin/env python3
"""
Analyze Enhanced Anchor Scoring Results
Quick diagnostic to understand the scoring distribution

Author: Claude Code
Date: July 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_results():
    """Analyze the enhanced scoring results"""
    
    # Find the most recent enhanced analysis file
    enhanced_files = list(Path('.').glob('Enhanced_Anchor_Analysis_*.xlsx'))
    if not enhanced_files:
        print("❌ No enhanced analysis files found")
        return
    
    latest_file = max(enhanced_files)
    print(f"📊 Analyzing: {latest_file}")
    
    # Load the data
    df = pd.read_excel(latest_file, sheet_name='Enhanced_Analysis_All_Sites')
    
    print(f"\n📈 ENHANCED SCORING ANALYSIS")
    print("=" * 50)
    print(f"Total Sites: {len(df)}")
    
    # Score distribution
    print(f"\n🎯 Enhanced Score Distribution:")
    print(f"  Min:    {df['Enhanced_Anchor_Score'].min():.3f}")
    print(f"  Max:    {df['Enhanced_Anchor_Score'].max():.3f}")
    print(f"  Mean:   {df['Enhanced_Anchor_Score'].mean():.3f}")
    print(f"  Median: {df['Enhanced_Anchor_Score'].median():.3f}")
    
    # Classification breakdown
    print(f"\n📊 Enhanced Classification Breakdown:")
    for classification in df['Enhanced_Classification'].value_counts().index:
        count = df['Enhanced_Classification'].value_counts()[classification]
        pct = count / len(df) * 100
        print(f"  {classification}: {count} sites ({pct:.1f}%)")
    
    # Component analysis
    print(f"\n🔧 Component Analysis (Average Contribution):")
    components = [
        ('Schools', 'Schools_Component'),
        ('City', 'City_Component'), 
        ('LIHTC', 'LIHTC_Component'),
        ('Scale', 'Scale_Component'),
        ('Highway', 'Highway_Component'),
        ('Utility', 'Utility_Component')
    ]
    
    for name, col in components:
        if col in df.columns:
            avg = df[col].mean()
            print(f"  {name:12s}: {avg:.3f} points (avg)")
    
    # Highway impact analysis
    print(f"\n🛣️  Highway Access Impact:")
    highway_excellent = df[df['Highway_Access_Score'] >= 0.8]
    highway_poor = df[df['Highway_Access_Score'] <= 0.2]
    
    print(f"  Sites with excellent highway access (≥0.8): {len(highway_excellent)}")
    print(f"  Sites with poor highway access (≤0.2): {len(highway_poor)}")
    
    if len(highway_excellent) > 0:
        print(f"  Avg enhanced score (excellent highway): {highway_excellent['Enhanced_Anchor_Score'].mean():.3f}")
    if len(highway_poor) > 0:
        print(f"  Avg enhanced score (poor highway): {highway_poor['Enhanced_Anchor_Score'].mean():.3f}")
    
    # Original vs Enhanced comparison
    if 'Anchor_Score' in df.columns:
        print(f"\n🔄 Original vs Enhanced Comparison:")
        original_avg = df['Anchor_Score'].mean()
        enhanced_avg = df['Enhanced_Anchor_Score'].mean()
        
        print(f"  Original average score: {original_avg:.3f}")
        print(f"  Enhanced average score: {enhanced_avg:.3f}")
        print(f"  Average change: {enhanced_avg - original_avg:+.3f}")
        
        # Sites that improved/declined
        improved = df[df['Enhanced_Anchor_Score'] > df['Anchor_Score']]
        declined = df[df['Enhanced_Anchor_Score'] < df['Anchor_Score']]
        
        print(f"  Sites improved: {len(improved)} ({len(improved)/len(df)*100:.1f}%)")
        print(f"  Sites declined: {len(declined)} ({len(declined)/len(df)*100:.1f}%)")
    
    # Top performers
    print(f"\n🏆 Top 10 Enhanced Scores:")
    top_10 = df.nlargest(10, 'Enhanced_Anchor_Score')[
        ['Property_Name', 'City', 'Enhanced_Anchor_Score', 'Enhanced_Classification', 'Highway_Access_Score']
    ]
    
    for idx, row in top_10.iterrows():
        print(f"  {row['Enhanced_Anchor_Score']:.3f} - {row['Property_Name']} ({row['City']}) - {row['Enhanced_Classification']}")
    
    # Bottom performers
    print(f"\n⚠️  Bottom 10 Enhanced Scores:")
    bottom_10 = df.nsmallest(10, 'Enhanced_Anchor_Score')[
        ['Property_Name', 'City', 'Enhanced_Anchor_Score', 'Enhanced_Classification', 'Highway_Access_Score']
    ]
    
    for idx, row in bottom_10.iterrows():
        print(f"  {row['Enhanced_Anchor_Score']:.3f} - {row['Property_Name']} ({row['City']}) - {row['Enhanced_Classification']}")

if __name__ == "__main__":
    analyze_results()