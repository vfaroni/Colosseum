#!/usr/bin/env python3
"""
Demonstration Script: Unified LIHTC RAG System Results Showcase
Shows real content snippets and business value for LIHTC professionals
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from unified_lihtc_rag_query import UnifiedLIHTCRAGQuery, QueryResult

class LIHTCRAGDemo:
    """Demonstration of LIHTC RAG system capabilities with real content"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.query_system = UnifiedLIHTCRAGQuery(base_dir)
        
    def demonstrate_key_capabilities(self):
        """Demonstrate key LIHTC research capabilities with actual content"""
        
        print("="*80)
        print("🏢 UNIFIED LIHTC RAG SYSTEM - LIVE DEMONSTRATION")
        print("="*80)
        print("Real-world LIHTC research queries with actual federal source content")
        print("Demonstrating authority hierarchies, conflict resolution, and business value")
        print()
        
        # Demo 1: Authority-Based Federal Search
        print("1. 📋 FEDERAL COMPLIANCE MONITORING REQUIREMENTS")
        print("   Query: 'What are the federal compliance monitoring requirements under Section 42?'")
        print("   Use Case: Property managers verifying federal compliance obligations")
        print("-" * 60)
        
        results = self.query_system.search_by_authority_level(
            "What are the federal compliance monitoring requirements under Section 42?",
            authority_levels=['statutory', 'regulatory'],
            limit=3
        )
        
        self.show_results_with_content(results, "Federal Compliance Monitoring")
        
        # Demo 2: Effective Date Search
        print("\n2. 📅 CURRENT INFLATION ADJUSTMENTS")
        print("   Query: 'What are the 2025 inflation adjustments for per capita credit?'")
        print("   Use Case: Allocation agencies determining current credit ceiling amounts")
        print("-" * 60)
        
        results = self.query_system.search_by_effective_date(
            "What are the 2025 inflation adjustments for per capita credit?",
            date_range=('2024', '2025'),
            limit=3
        )
        
        self.show_results_with_content(results, "2025 Inflation Adjustments")
        
        # Demo 3: Authority Hierarchy Demonstration
        print("\n3. ⚖️ AUTHORITY HIERARCHY DEMONSTRATION")
        print("   Query: 'placed in service requirements and deadlines'")
        print("   Use Case: Developers understanding construction timeline requirements")
        print("-" * 60)
        
        results = self.query_system.search_by_authority_level(
            "placed in service requirements and deadlines",
            authority_levels=['statutory', 'regulatory', 'guidance'],
            limit=3
        )
        
        self.show_authority_hierarchy(results)
        
        # Demo 4: Cross-Jurisdictional Analysis
        print("\n4. 🗺️ CROSS-JURISDICTIONAL ANALYSIS")
        print("   Query: 'compliance period duration federal requirements'")
        print("   Use Case: Legal counsel comparing federal vs state compliance periods")
        print("-" * 60)
        
        comparison = self.query_system.cross_jurisdictional_comparison(
            "compliance period duration federal requirements",
            comparison_type='federal_vs_states'
        )
        
        self.show_cross_jurisdictional_analysis(comparison)
        
        # Demo 5: Business Value Summary
        print("\n5. 💼 BUSINESS VALUE SUMMARY")
        print("-" * 60)
        self.show_business_value_summary()
        
        print("\n" + "="*80)
        print("✅ DEMONSTRATION COMPLETE")
        print("="*80)
    
    def show_results_with_content(self, results, query_type):
        """Show results with actual content snippets"""
        
        if not results:
            print("   ❌ No results found")
            return
        
        print(f"   ✅ Found {len(results)} results")
        print()
        
        for i, result in enumerate(results[:3], 1):
            print(f"   📄 Result {i}:")
            print(f"      🏛️ Authority: {result.authority_level.upper()} (Score: {result.authority_score})")
            print(f"      📚 Source: {result.source_type}")
            print(f"      📅 Effective: {result.effective_date}")
            print(f"      🎯 Relevance: {result.relevance_score:.3f}")
            
            # Show meaningful content snippet
            content_snippet = self.extract_meaningful_content(result.content, query_type)
            print(f"      📝 Content Preview:")
            print(f"         {content_snippet}")
            
            if result.conflicts:
                print(f"      ⚠️ Conflicts: {', '.join(result.conflicts)}")
            
            print()
    
    def extract_meaningful_content(self, content, query_type):
        """Extract meaningful content based on query type"""
        
        # Clean up HTML and excessive whitespace
        content = content.replace('&amp;', '&').replace('&sect;', '§')
        content = ' '.join(content.split())
        
        # Try to find specific content based on query type
        if query_type == "Federal Compliance Monitoring":
            # Look for compliance-related content
            keywords = ['compliance', 'monitoring', 'requirements', 'must', 'shall']
            for keyword in keywords:
                if keyword in content.lower():
                    # Find sentence containing the keyword
                    sentences = content.split('. ')
                    for sentence in sentences:
                        if keyword in sentence.lower() and len(sentence) > 20:
                            return sentence[:200] + "..."
        
        elif query_type == "2025 Inflation Adjustments":
            # Look for 2025 and dollar amounts
            if '2025' in content:
                # Find content around 2025
                pos = content.find('2025')
                start = max(0, pos - 100)
                end = min(len(content), pos + 200)
                return content[start:end] + "..."
        
        # Default: return first meaningful chunk
        if len(content) > 300:
            return content[:300] + "..."
        return content
    
    def show_authority_hierarchy(self, results):
        """Demonstrate authority hierarchy with actual examples"""
        
        if not results:
            print("   ❌ No results found")
            return
        
        print("   📊 Authority Hierarchy in Action:")
        print()
        
        # Group by authority level
        authority_groups = {}
        for result in results:
            level = result.authority_level
            if level not in authority_groups:
                authority_groups[level] = []
            authority_groups[level].append(result)
        
        # Show hierarchy
        hierarchy_order = ['statutory', 'regulatory', 'guidance', 'interpretive']
        
        for level in hierarchy_order:
            if level in authority_groups:
                count = len(authority_groups[level])
                score = authority_groups[level][0].authority_score
                print(f"   🏛️ {level.upper()} (Score: {score}) - {count} sources")
                
                # Show example
                example = authority_groups[level][0]
                print(f"      📚 Example: {example.source_type}")
                print(f"      📅 Effective: {example.effective_date}")
                print()
        
        print("   ✅ Higher authority sources automatically ranked first")
        print("   ⚖️ Conflict resolution: Statutory > Regulatory > Guidance")
    
    def show_cross_jurisdictional_analysis(self, comparison):
        """Show cross-jurisdictional analysis results"""
        
        federal_count = len(comparison.get('federal_requirements', []))
        state_count = comparison.get('analysis', {}).get('implementing_states_count', 0)
        
        print(f"   📊 Analysis Results:")
        print(f"      🏛️ Federal Sources: {federal_count}")
        print(f"      🗺️ State Implementations: {state_count}")
        
        if federal_count > 0:
            print(f"      ✅ Federal requirements found in multiple authority levels")
            
            # Show federal sources
            for i, req in enumerate(comparison.get('federal_requirements', [])[:2], 1):
                print(f"         {i}. {req.get('source_type', 'Unknown')} - {req.get('authority_level', 'Unknown')}")
        
        if state_count > 0:
            print(f"      🗺️ State-level implementation tracking available")
        else:
            print(f"      ⚠️ State implementation mapping requires QAP integration")
    
    def show_business_value_summary(self):
        """Show business value for different LIHTC professionals"""
        
        print("   🎯 Value for LIHTC Professionals:")
        print()
        
        use_cases = [
            {
                'role': 'Property Managers',
                'value': 'Automated compliance monitoring requirement lookups',
                'time_savings': 'Reduces research time from hours to minutes',
                'accuracy': 'Direct access to authoritative federal sources'
            },
            {
                'role': 'Developers',
                'value': 'Basis calculation rules and construction deadlines',
                'time_savings': 'Eliminates manual regulation searches',
                'accuracy': 'Authority hierarchy ensures correct interpretations'
            },
            {
                'role': 'Allocation Agencies',
                'value': 'Current credit ceiling and inflation adjustments',
                'time_savings': 'Automated effective date filtering',
                'accuracy': 'Real-time access to latest IRS guidance'
            },
            {
                'role': 'Legal Counsel',
                'value': 'Conflict resolution and authority ranking',
                'time_savings': 'Systematic federal-state comparison',
                'accuracy': 'Hierarchical source prioritization'
            }
        ]
        
        for use_case in use_cases:
            print(f"   👥 {use_case['role']}:")
            print(f"      💡 Value: {use_case['value']}")
            print(f"      ⏱️ Time Savings: {use_case['time_savings']}")
            print(f"      🎯 Accuracy: {use_case['accuracy']}")
            print()
        
        print("   🏆 Key System Advantages:")
        print("      • Multi-source federal integration (IRC, CFR, Revenue Procedures)")
        print("      • Authority-based result ranking (Statutory > Regulatory > Guidance)")
        print("      • Effective date filtering for current regulations")
        print("      • Cross-jurisdictional analysis capabilities")
        print("      • Automated conflict detection and resolution")
        print("      • Professional-grade citations and references")

def main():
    """Main demonstration function"""
    
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    
    print("🚀 Initializing LIHTC RAG System Demo...")
    
    try:
        demo = LIHTCRAGDemo(base_dir)
        demo.demonstrate_key_capabilities()
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()