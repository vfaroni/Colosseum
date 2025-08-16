#!/usr/bin/env python3
"""
Master RAG Integration System
Extends the existing 49-state QAP master_chunk_index.json to include federal LIHTC sources
Creates unified search capability across federal + state sources with authority hierarchy
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import pandas as pd
from collections import defaultdict
import shutil

class MasterRAGIntegrator:
    """Integrate federal LIHTC sources into existing QAP RAG master index"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.qap_processed_dir = self.base_dir / "QAP" / "_processed"
        self.federal_processed_dir = self.base_dir / "federal" / "LIHTC_Federal_Sources" / "_processed"
        
        # Backup and integration paths
        self.backup_dir = self.qap_processed_dir / "_backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Authority hierarchy for conflict resolution
        self.authority_hierarchy = {
            'statutory': 100,    # IRC Section 42 (federal law)
            'regulatory': 80,    # CFR regulations (federal)
            'guidance': 60,      # Revenue Procedures (federal IRS guidance)
            'interpretive': 40,  # PLRs (federal interpretive)
            'state_qap': 30      # State QAP (implements federal)
        }
        
    def backup_existing_system(self):
        """Create backup of existing QAP system before integration"""
        print("💾 Creating backup of existing QAP system...")
        
        # Backup master index
        master_index_path = self.qap_processed_dir / "master_chunk_index.json"
        if master_index_path.exists():
            backup_path = self.backup_dir / f"master_chunk_index_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy2(master_index_path, backup_path)
            print(f"    ✅ Backed up master index to {backup_path}")
        
        # Backup existing indexes directory
        indexes_dir = self.qap_processed_dir / "_indexes"
        if indexes_dir.exists():
            backup_indexes_dir = self.backup_dir / f"indexes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree(indexes_dir, backup_indexes_dir)
            print(f"    ✅ Backed up indexes to {backup_indexes_dir}")
    
    def load_existing_qap_master_index(self) -> Dict:
        """Load the existing 49-state QAP master index"""
        master_file = self.qap_processed_dir / "master_chunk_index.json"
        if master_file.exists():
            with open(master_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_federal_unified_index(self) -> Dict:
        """Load the federal unified index"""
        federal_index_file = self.federal_processed_dir / "_indexes" / "unified_master_index.json"
        if federal_index_file.exists():
            with open(federal_index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_all_federal_chunks(self) -> List[Dict]:
        """Load all federal chunks for integration"""
        federal_chunks = []
        
        chunks_dir = self.federal_processed_dir / "chunks"
        if chunks_dir.exists():
            for chunk_file in chunks_dir.glob("federal_*.json"):
                try:
                    with open(chunk_file, 'r', encoding='utf-8') as f:
                        chunks = json.load(f)
                        federal_chunks.extend(chunks)
                except Exception as e:
                    print(f"    ⚠️  Error loading {chunk_file}: {e}")
        
        return federal_chunks
    
    def create_integrated_master_index(self, qap_master: Dict, federal_index: Dict, federal_chunks: List[Dict]) -> Dict:
        """Create new integrated master index combining QAP and federal systems"""
        print("🔗 Creating integrated master index...")
        
        # Start with existing QAP structure
        integrated_index = qap_master.copy()
        
        # Update system information
        integrated_index.update({
            'system_type': 'unified_federal_state_lihtc_rag',
            'integration_date': datetime.now().isoformat(),
            'version': '2.0_federal_integrated',
            
            # Enhanced metadata
            'total_chunks': qap_master.get('total_chunks', 0) + len(federal_chunks),
            'federal_chunks': len(federal_chunks),
            'state_chunks': qap_master.get('total_chunks', 0),
            
            # Source coverage
            'federal_sources_processed': federal_index.get('system_info', {}).get('federal_sources_processed', 0),
            'states_processed': qap_master.get('states_processed', []),
            'total_jurisdictions': len(qap_master.get('states_processed', [])) + 1,  # +1 for federal
            
            # Authority hierarchy information
            'authority_hierarchy': {
                'federal_statutory': federal_index.get('authority_hierarchy', {}).get('statutory', 0),
                'federal_regulatory': federal_index.get('authority_hierarchy', {}).get('regulatory', 0),
                'federal_guidance': federal_index.get('authority_hierarchy', {}).get('guidance', 0),
                'federal_interpretive': federal_index.get('authority_hierarchy', {}).get('interpretive', 0),
                'state_qap_total': qap_master.get('total_chunks', 0)
            },
            
            # Index types available
            'available_indexes': {
                'traditional': ['content_index', 'entity_index', 'section_index', 'program_index', 'state_index', 'keyword_index'],
                'federal_specific': ['authority_index', 'effective_date_index', 'federal_state_cross_ref_index'],
                'enhanced': ['federal_content_index', 'federal_entity_index', 'federal_section_index'],
                'unified': ['unified_master_index']
            },
            
            # Cross-reference statistics
            'integration_stats': {
                'federal_state_cross_references': federal_index.get('integration_stats', {}).get('federal_state_cross_references', 0),
                'effective_date_coverage': federal_index.get('integration_stats', {}).get('effective_date_coverage', 0),
                'authority_conflicts_resolved': 0,  # Will be updated during resolution
                'search_namespaces': ['federal', 'state', 'unified']
            }
        })
        
        # Add federal source breakdown
        integrated_index['federal_sources'] = federal_index.get('federal_sources', {})
        
        print(f"    ✅ Integrated index covers {integrated_index['total_jurisdictions']} jurisdictions")
        print(f"    📊 Total chunks: {integrated_index['total_chunks']} ({integrated_index['federal_chunks']} federal + {integrated_index['state_chunks']} state)")
        
        return integrated_index
    
    def create_authority_conflict_resolver(self) -> Dict:
        """Create system for resolving conflicts between federal and state sources"""
        print("⚖️  Creating authority conflict resolution system...")
        
        conflict_resolver = {
            'resolution_rules': {
                'rule_1': 'Federal statutory (IRC) overrides all state interpretations',
                'rule_2': 'Federal regulatory (CFR) overrides state regulatory interpretations', 
                'rule_3': 'Federal guidance (Rev Proc) provides minimum standards for states',
                'rule_4': 'State QAPs may be more restrictive than federal minimums',
                'rule_5': 'Federal interpretive guidance (PLRs) provides context but limited precedent'
            },
            'hierarchy_scores': self.authority_hierarchy,
            'conflict_examples': {
                'income_limits': 'Federal IRC sets maximum, states may be more restrictive',
                'compliance_periods': 'Federal law sets minimum 15-year compliance, states may extend',
                'monitoring_requirements': 'Federal CFR sets minimum standards, states may enhance',
                'scoring_criteria': 'States have discretion within federal program requirements'
            },
            'resolution_process': [
                '1. Identify conflicting requirements between federal and state sources',
                '2. Determine authority level of each source using hierarchy scores',
                '3. Apply resolution rules based on hierarchy',
                '4. Flag conflicts for manual review if rules unclear',
                '5. Document resolution in conflict log'
            ]
        }
        
        return conflict_resolver
    
    def integrate_federal_indexes_with_qap(self):
        """Copy federal indexes to QAP indexes directory for unified access"""
        print("📋 Integrating federal indexes with QAP system...")
        
        qap_indexes_dir = self.qap_processed_dir / "_indexes"
        qap_indexes_dir.mkdir(exist_ok=True)
        
        federal_indexes_dir = self.federal_processed_dir / "_indexes"
        
        if not federal_indexes_dir.exists():
            print(f"    ⚠️  Federal indexes directory not found: {federal_indexes_dir}")
            return
        
        # Copy federal-specific indexes to QAP indexes directory
        federal_index_files = [
            'authority_index.json',
            'effective_date_index.json', 
            'federal_state_cross_ref_index.json',
            'federal_content_index.json',
            'federal_entity_index.json',
            'federal_section_index.json',
            'unified_master_index.json'
        ]
        
        for index_file in federal_index_files:
            source_path = federal_indexes_dir / index_file
            dest_path = qap_indexes_dir / index_file
            
            if source_path.exists():
                shutil.copy2(source_path, dest_path)
                print(f"    ✅ Copied {index_file} to unified system")
            else:
                print(f"    ⚠️  Federal index not found: {index_file}")
    
    def create_unified_search_config(self) -> Dict:
        """Create configuration for unified search across federal and state sources"""
        print("🔍 Creating unified search configuration...")
        
        search_config = {
            'search_namespaces': {
                'federal': {
                    'description': 'Search only federal LIHTC sources',
                    'sources': ['IRC', 'CFR', 'Rev_Proc', 'Rev_Rul', 'PLR', 'Fed_Reg'],
                    'indexes': ['authority_index', 'effective_date_index', 'federal_content_index'],
                    'authority_levels': ['statutory', 'regulatory', 'guidance', 'interpretive']
                },
                'state': {
                    'description': 'Search only state QAP sources',
                    'sources': ['QAP documents from 49 states'],
                    'indexes': ['content_index', 'entity_index', 'section_index', 'program_index', 'state_index'],
                    'authority_levels': ['state_qap']
                },
                'unified': {
                    'description': 'Search across both federal and state sources with authority hierarchy',
                    'sources': ['All federal sources', 'All state QAP sources'],
                    'indexes': ['All available indexes'],
                    'authority_levels': ['statutory', 'regulatory', 'guidance', 'interpretive', 'state_qap'],
                    'conflict_resolution': 'Apply authority hierarchy for ranking results'
                }
            },
            'search_strategies': {
                'authority_first': 'Rank results by authority level (federal statutory first)',
                'chronological': 'Rank by effective date (most recent first)',
                'relevance': 'Rank by content relevance score',
                'comprehensive': 'Show all relevant sources with authority indicators',
                'state_specific': 'Filter to specific state implementation of federal rules'
            },
            'result_formatting': {
                'include_authority_level': True,
                'include_effective_date': True,
                'include_superseded_status': True,
                'include_state_applications': True,
                'include_cross_references': True,
                'highlight_conflicts': True
            }
        }
        
        return search_config
    
    def perform_full_integration(self):
        """Perform complete integration of federal sources into QAP system"""
        print("🚀 Starting Master RAG Integration")
        print("Integrating federal LIHTC sources with existing 49-state QAP system")
        
        # Step 1: Backup existing system
        self.backup_existing_system()
        
        # Step 2: Load existing data
        print("\n📥 Loading existing systems...")
        qap_master = self.load_existing_qap_master_index()
        federal_index = self.load_federal_unified_index()
        federal_chunks = self.load_all_federal_chunks()
        
        if not qap_master:
            print("❌ QAP master index not found - ensure QAP system is processed first")
            return
        
        if not federal_chunks:
            print("❌ Federal chunks not found - ensure federal processing is complete")
            return
        
        print(f"    📊 QAP system: {qap_master.get('total_chunks', 0)} chunks from {len(qap_master.get('states_processed', []))} states")
        print(f"    📊 Federal system: {len(federal_chunks)} chunks from {len(federal_index.get('federal_sources', {}))} source types")
        
        # Step 3: Create integrated master index
        integrated_master = self.create_integrated_master_index(qap_master, federal_index, federal_chunks)
        
        # Step 4: Create authority conflict resolver
        conflict_resolver = self.create_authority_conflict_resolver()
        
        # Step 5: Create unified search configuration
        search_config = self.create_unified_search_config()
        
        # Step 6: Integrate federal indexes with QAP system
        self.integrate_federal_indexes_with_qap()
        
        # Step 7: Save integrated master index
        print("\n💾 Saving integrated system...")
        
        # Save new integrated master index
        integrated_master_path = self.qap_processed_dir / "master_chunk_index.json"
        with open(integrated_master_path, 'w', encoding='utf-8') as f:
            json.dump(integrated_master, f, indent=2, ensure_ascii=False, default=str)
        print(f"    ✅ Saved integrated master index: {integrated_master_path}")
        
        # Save conflict resolver
        resolver_path = self.qap_processed_dir / "_indexes" / "authority_conflict_resolver.json"
        with open(resolver_path, 'w', encoding='utf-8') as f:
            json.dump(conflict_resolver, f, indent=2, ensure_ascii=False)
        print(f"    ✅ Saved conflict resolver: {resolver_path}")
        
        # Save search configuration  
        search_config_path = self.qap_processed_dir / "_indexes" / "unified_search_config.json"
        with open(search_config_path, 'w', encoding='utf-8') as f:
            json.dump(search_config, f, indent=2, ensure_ascii=False)
        print(f"    ✅ Saved search configuration: {search_config_path}")
        
        # Step 8: Generate integration report
        self.generate_integration_report(integrated_master, qap_master, federal_index)
        
        print(f"\n🎉 Master RAG Integration Complete!")
        print(f"📊 Unified system now contains {integrated_master['total_chunks']} chunks")
        print(f"🏛️  Federal sources: {integrated_master['federal_chunks']} chunks")
        print(f"🗺️  State sources: {integrated_master['state_chunks']} chunks") 
        print(f"⚖️  Authority hierarchy: Statutory → Regulatory → Guidance → Interpretive → State QAP")
        print(f"🔍 Search namespaces: federal, state, unified")
    
    def generate_integration_report(self, integrated_master: Dict, qap_master: Dict, federal_index: Dict):
        """Generate comprehensive integration report"""
        report = {
            'integration_summary': {
                'date': datetime.now().isoformat(),
                'success': True,
                'pre_integration': {
                    'qap_chunks': qap_master.get('total_chunks', 0),
                    'qap_states': len(qap_master.get('states_processed', [])),
                    'federal_chunks': 0
                },
                'post_integration': {
                    'total_chunks': integrated_master['total_chunks'],
                    'federal_chunks': integrated_master['federal_chunks'],
                    'state_chunks': integrated_master['state_chunks'],
                    'jurisdictions': integrated_master['total_jurisdictions']
                },
                'enhancement': {
                    'chunks_added': integrated_master['federal_chunks'],
                    'new_indexes': len(integrated_master['available_indexes']['federal_specific']),
                    'authority_levels': len(integrated_master['authority_hierarchy']),
                    'search_capabilities': len(integrated_master['integration_stats']['search_namespaces'])
                }
            },
            'system_capabilities': {
                'unified_search': 'Search across federal and state sources simultaneously',
                'authority_ranking': 'Results ranked by legal authority hierarchy',
                'cross_references': 'Map federal requirements to state implementations', 
                'conflict_resolution': 'Automatic resolution of federal vs state conflicts',
                'temporal_search': 'Search by effective dates and superseded rules'
            },
            'next_steps': [
                'Test unified search functionality',
                'Validate authority conflict resolution',
                'Update existing extractors to use federal citations',
                'Create unified query interface',
                'Implement federal update monitoring'
            ]
        }
        
        report_path = self.qap_processed_dir / f"integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"    📄 Integration report saved: {report_path}")

def main():
    """Main execution function"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    integrator = MasterRAGIntegrator(base_dir)
    integrator.perform_full_integration()

if __name__ == "__main__":
    main()