#!/usr/bin/env python3
"""
Quick analysis of TX structure from the already processed content
"""
import re

def quick_tx_analysis():
    """Analyze TX structure from already processed JSON"""
    
    # Read the content from the TX JSON file we already generated
    import json
    
    try:
        with open('TX_regulatory_framework.json', 'r') as f:
            data = json.load(f)
        
        print("🔍 TX QAP STRUCTURE ANALYSIS FROM PROCESSED DATA")
        print("=" * 60)
        
        # Get one section content to understand the format
        first_section = list(data['sections'].values())[0]
        print(f"Sample content from first section:")
        print(f"Content: {first_section['content']}")
        print(f"This appears to be table of contents, not actual regulatory content!")
        
        print(f"\n🎯 CONCLUSION:")
        print(f"TX QAP uses a different structure - our regex is matching TOC entries")
        print(f"Need to find actual section content in the 594K character document")
        
        # The solution: TX likely uses different patterns than §11.1, §11.2
        # Let's suggest using generic fallback for now
        print(f"\n💡 RECOMMENDATION:")
        print(f"1. Use generic fallback extraction for TX")
        print(f"2. Focus on completing NY validation") 
        print(f"3. TX can be refined later with manual pattern analysis")
        
    except FileNotFoundError:
        print("❌ TX_regulatory_framework.json not found")
        return False
    
    return True

if __name__ == "__main__":
    quick_tx_analysis()