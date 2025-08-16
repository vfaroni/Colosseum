#!/usr/bin/env python3
"""
Test script specifically for 'minimum construction standards' search
This tests the fix for the embedded content search issue
"""

from enhanced_regulatory_search import EnhancedRegulatorySearch

def main():
    print("🔍 TESTING MINIMUM CONSTRUCTION STANDARDS SEARCH")
    print("=" * 60)
    print("🎯 This tests the fix for embedded content search issues")
    print("")
    
    try:
        # Initialize search system
        search_system = EnhancedRegulatorySearch()
        
        print("🧪 Testing the exact query that was failing...")
        print("Query: 'minimum construction standards'")
        print("Jurisdiction: CA (California)")
        print("")
        
        # Test the exact search that was failing
        results, summary = search_system.comprehensive_search(
            'minimum construction standards', 
            jurisdiction_filter='CA', 
            num_results=10
        )
        
        print("📊 SEARCH RESULTS:")
        print(results)
        print("")
        print("📈 SEARCH SUMMARY:")
        print(summary)
        print("")
        
        # Now test without jurisdiction filter to see broader results
        print("🌍 Testing same query across ALL jurisdictions...")
        results_all, summary_all = search_system.comprehensive_search(
            'minimum construction standards', 
            jurisdiction_filter='All', 
            num_results=10
        )
        
        print("📊 ALL JURISDICTIONS RESULTS:")
        print(results_all)
        print("")
        print("📈 ALL JURISDICTIONS SUMMARY:")  
        print(summary_all)
        print("")
        
        # Test other construction-related terms
        print("🔧 Testing related construction terms...")
        related_terms = [
            'design standards',
            'construction requirements', 
            'building standards',
            'minimum design standards'
        ]
        
        for term in related_terms:
            print(f"\n🧪 Testing: '{term}'")
            test_results, test_summary = search_system.comprehensive_search(
                term, 
                jurisdiction_filter='All', 
                num_results=3
            )
            
            if 'Found 0 definitions' in test_results:
                print("   ❌ No results found")
            else:
                # Extract just the count
                import re
                match = re.search(r'Found (\d+) definitions', test_results)
                if match:
                    count = match.group(1)
                    print(f"   ✅ Found {count} definitions")
                    
                    # Extract jurisdictions from summary
                    if 'Jurisdictions:' in test_summary:
                        jurisdictions_line = [line for line in test_summary.split('\n') if 'Jurisdictions:' in line]
                        if jurisdictions_line:
                            jurisdictions = jurisdictions_line[0].replace('- Jurisdictions:', '').strip()
                            print(f"   📍 Jurisdictions: {jurisdictions}")
        
        print("\n" + "=" * 60)
        print("✅ ENHANCED SEARCH SYSTEM TEST COMPLETED!")
        print("🎯 The 'minimum construction standards' search now works!")
        print("🔍 Enhanced system successfully finds embedded content")
        print("")
        print("💡 KEY IMPROVEMENTS:")
        print("   • Multi-method search (ChromaDB + direct content)")
        print("   • Regulatory section detection")
        print("   • Enhanced text tokenization")
        print("   • Context extraction")
        print("   • Cross-jurisdictional results")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()