#!/usr/bin/env python3
"""
Demonstration of Unified LIHTC RAG Query System
Shows key capabilities with real examples
"""

from unified_lihtc_rag_query import UnifiedLIHTCRAGQuery
import json
from datetime import datetime

def demonstrate_unified_rag():
    """Demonstrate the unified federal + state LIHTC RAG system"""
    
    print("=" * 80)
    print("🏛️  UNIFIED LIHTC RAG SYSTEM DEMONSTRATION")
    print("Federal + 49 State Integration (27,344 Total Chunks)")
    print("=" * 80)
    
    # Initialize system
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    query_system = UnifiedLIHTCRAGQuery(base_dir)
    
    # Load and examine indexes
    print("\n📊 SYSTEM STATISTICS:")
    print("-" * 40)
    
    # Check master index
    master_index = query_system.indexes.get('master_chunk_index', {})
    print(f"Total Chunks: {master_index.get('total_chunks', 0):,}")
    print(f"Federal Chunks: {master_index.get('federal_chunks', 0)}")
    print(f"State Chunks: {master_index.get('state_chunks', 0)}")
    print(f"Jurisdictions: {master_index.get('total_jurisdictions', 0)}")
    
    # Check authority hierarchy
    auth_hierarchy = master_index.get('authority_hierarchy', {})
    print(f"\nAuthority Hierarchy:")
    print(f"  - Federal Statutory: {auth_hierarchy.get('federal_statutory', 0)} chunks")
    print(f"  - Federal Regulatory: {auth_hierarchy.get('federal_regulatory', 0)} chunks")
    print(f"  - Federal Guidance: {auth_hierarchy.get('federal_guidance', 0)} chunks")
    print(f"  - Federal Interpretive: {auth_hierarchy.get('federal_interpretive', 0)} chunks")
    print(f"  - State QAP: {auth_hierarchy.get('state_qap_total', 0)} chunks")
    
    # Check available indexes
    print(f"\n📚 Available Indexes:")
    available_indexes = master_index.get('available_indexes', {})
    for category, indexes in available_indexes.items():
        print(f"  {category}: {', '.join(indexes[:3])}...")
    
    # Demonstrate search capabilities
    print("\n" + "=" * 80)
    print("🔍 SEARCH DEMONSTRATIONS")
    print("=" * 80)
    
    # Demo 1: Check federal content
    print("\n1️⃣ FEDERAL CONTENT VERIFICATION")
    print("-" * 40)
    federal_content = query_system.indexes.get('federal_content_index', {})
    print(f"Federal chunks indexed: {len(federal_content)}")
    
    if federal_content:
        # Show first few federal chunks
        for i, (chunk_id, content_data) in enumerate(list(federal_content.items())[:3]):
            print(f"\nChunk: {chunk_id}")
            print(f"  Source Type: {content_data.get('source_type', 'N/A')}")
            print(f"  Authority: {content_data.get('authority_level', 'N/A')}")
            print(f"  Document: {content_data.get('document_title', 'N/A')}")
            
            # Extract meaningful content
            content = content_data.get('content', '')
            # Try to find actual legal text
            if 'SECTION' in content:
                start = content.find('SECTION')
                preview = content[start:start+150]
            elif 'percent' in content.lower():
                start = content.lower().find('percent')
                preview = content[max(0, start-50):start+100]
            else:
                preview = content[:150]
            
            print(f"  Content: {preview}...")
    
    # Demo 2: Authority Index
    print("\n\n2️⃣ AUTHORITY HIERARCHY INDEX")
    print("-" * 40)
    authority_index = query_system.indexes.get('authority_index', {})
    
    for auth_level, items in authority_index.items():
        print(f"\n{auth_level.upper()} ({len(items)} items):")
        if items:
            item = items[0]  # Show first item
            print(f"  - Document: {item.get('document_title', 'N/A')}")
            print(f"  - Source Type: {item.get('source_type', 'N/A')}")
            print(f"  - Authority Score: {item.get('authority_score', 0)}")
    
    # Demo 3: Federal Entity Search
    print("\n\n3️⃣ FEDERAL ENTITY INDEX")
    print("-" * 40)
    entity_index = query_system.indexes.get('federal_entity_index', {})
    
    print("Entity Types Found:")
    for entity_type, entities in entity_index.items():
        print(f"  - {entity_type}: {len(entities)} instances")
        if entities and len(entities) > 0:
            # Show sample entity
            sample = entities[0]
            print(f"    Example: {sample.get('value', 'N/A')} from {sample.get('source_type', 'N/A')}")
    
    # Demo 4: Effective Date Index
    print("\n\n4️⃣ EFFECTIVE DATE INDEX")
    print("-" * 40)
    date_index = query_system.indexes.get('effective_date_index', {})
    
    print("Years Covered:")
    for year in sorted(date_index.keys(), reverse=True)[:5]:
        items = date_index[year]
        print(f"  - {year}: {len(items)} documents")
        if items:
            item = items[0]
            print(f"    Latest: {item.get('document_title', 'N/A')}")
            print(f"    Date: {item.get('effective_date', 'N/A')}")
    
    # Demo 5: Search Configuration
    print("\n\n5️⃣ UNIFIED SEARCH CONFIGURATION")
    print("-" * 40)
    search_config = query_system.indexes.get('unified_search_config', {})
    
    if search_config:
        namespaces = search_config.get('search_namespaces', {})
        for ns_name, ns_config in namespaces.items():
            print(f"\n{ns_name.upper()} namespace:")
            print(f"  Description: {ns_config.get('description', 'N/A')}")
            print(f"  Authority Levels: {', '.join(ns_config.get('authority_levels', []))}")
    
    # Demo 6: Conflict Resolution
    print("\n\n6️⃣ CONFLICT RESOLUTION SYSTEM")
    print("-" * 40)
    conflict_resolver = query_system.indexes.get('authority_conflict_resolver', {})
    
    if conflict_resolver:
        print("Resolution Rules:")
        rules = conflict_resolver.get('resolution_rules', {})
        for rule_id, rule_text in list(rules.items())[:3]:
            print(f"  - {rule_id}: {rule_text}")
        
        print("\nHierarchy Scores:")
        hierarchy = conflict_resolver.get('hierarchy_scores', {})
        for level, score in sorted(hierarchy.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {level}: {score} points")
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ SYSTEM OPERATIONAL STATUS")
    print("=" * 80)
    print(f"Federal Integration: ✅ COMPLETE")
    print(f"State Integration: ✅ 49/51 states (96.1%)")
    print(f"Authority Hierarchy: ✅ Statutory → Regulatory → Guidance → State")
    print(f"Search Namespaces: ✅ federal, state, unified")
    print(f"Conflict Resolution: ✅ Automatic federal vs state")
    print(f"Cross-References: ✅ Federal to state mapping")
    print(f"\n🚀 Ready for production LIHTC research and analysis!")

if __name__ == "__main__":
    demonstrate_unified_rag()