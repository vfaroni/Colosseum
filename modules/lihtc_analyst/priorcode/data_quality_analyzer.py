#!/usr/bin/env python3
"""
Data Quality Analyzer for LIHTC RAG System
Comprehensive analysis of chunk quality across 17,430 documents
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re
from collections import Counter, defaultdict
import statistics

class DataQualityAnalyzer:
    """Analyze data quality issues across all QAP chunks"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.qap_dir = self.base_dir / "QAP" / "_processed"
        self.results = {
            'total_chunks': 0,
            'jurisdictions': 0,
            'quality_issues': defaultdict(list),
            'statistics': {},
            'recommendations': []
        }
        
    def load_all_chunks(self) -> List[Dict]:
        """Load all chunks from all jurisdictions"""
        all_chunks = []
        jurisdictions = 0
        
        for state_dir in self.qap_dir.iterdir():
            if state_dir.is_dir() and len(state_dir.name) <= 3:  # State codes
                chunks_file = state_dir / f"{state_dir.name}_all_chunks.json"
                if chunks_file.exists():
                    try:
                        with open(chunks_file, 'r') as f:
                            chunks = json.load(f)
                        all_chunks.extend(chunks)
                        jurisdictions += 1
                        print(f"✅ Loaded {len(chunks)} chunks from {state_dir.name}")
                    except Exception as e:
                        print(f"❌ Error loading {state_dir.name}: {e}")
        
        self.results['total_chunks'] = len(all_chunks)
        self.results['jurisdictions'] = jurisdictions
        print(f"\n📊 Total: {len(all_chunks)} chunks from {jurisdictions} jurisdictions")
        
        return all_chunks
    
    def analyze_content_quality(self, chunks: List[Dict]) -> None:
        """Analyze content quality issues"""
        print("\n🔍 Analyzing content quality...")
        
        issues = {
            'too_short': 0,
            'too_long': 0,
            'truncated_sentences': 0,
            'missing_content': 0,
            'encoding_issues': 0,
            'repeated_content': 0
        }
        
        content_lengths = []
        content_hash_counts = Counter()
        
        for i, chunk in enumerate(chunks):
            content = chunk.get('content', '')
            
            # Missing content
            if not content or content.strip() == '':
                issues['missing_content'] += 1
                self.results['quality_issues']['missing_content'].append({
                    'chunk_id': chunk.get('chunk_id', f'unknown_{i}'),
                    'state': chunk.get('state_code', 'unknown')
                })
                continue
            
            content_length = len(content)
            content_lengths.append(content_length)
            
            # Content too short (likely extraction error)
            if content_length < 50:
                issues['too_short'] += 1
                self.results['quality_issues']['too_short'].append({
                    'chunk_id': chunk.get('chunk_id', f'unknown_{i}'),
                    'length': content_length,
                    'content_preview': content[:100]
                })
            
            # Content too long (might need better chunking)
            if content_length > 5000:
                issues['too_long'] += 1
                self.results['quality_issues']['too_long'].append({
                    'chunk_id': chunk.get('chunk_id', f'unknown_{i}'),
                    'length': content_length,
                    'state': chunk.get('state_code', 'unknown')
                })
            
            # Truncated sentences (ends mid-sentence)
            if content_length > 100 and not re.search(r'[.!?]\s*$', content.strip()):
                if not content.strip().endswith(':') and not content.strip().endswith(';'):
                    issues['truncated_sentences'] += 1
                    self.results['quality_issues']['truncated_sentences'].append({
                        'chunk_id': chunk.get('chunk_id', f'unknown_{i}'),
                        'ending': content.strip()[-50:]
                    })
            
            # Encoding issues (common problematic characters)
            if re.search(r'[^\x00-\x7F\u2013\u2014\u2018\u2019\u201C\u201D\u2022\u00A0\u00B0\u00A9\u00AE]', content):
                issues['encoding_issues'] += 1
                self.results['quality_issues']['encoding_issues'].append({
                    'chunk_id': chunk.get('chunk_id', f'unknown_{i}'),
                    'state': chunk.get('state_code', 'unknown')
                })
            
            # Track content for duplication analysis
            content_hash = hash(content.strip().lower())
            content_hash_counts[content_hash] += 1
        
        # Find duplicated content
        for content_hash, count in content_hash_counts.items():
            if count > 1:
                issues['repeated_content'] += count - 1  # Don't count original
        
        # Calculate statistics
        if content_lengths:
            self.results['statistics']['content_length'] = {
                'min': min(content_lengths),
                'max': max(content_lengths),
                'mean': statistics.mean(content_lengths),
                'median': statistics.median(content_lengths),
                'std_dev': statistics.stdev(content_lengths) if len(content_lengths) > 1 else 0
            }
        
        self.results['quality_issues']['content_summary'] = issues
        
        print(f"   📏 Content lengths: {min(content_lengths) if content_lengths else 0}-{max(content_lengths) if content_lengths else 0} chars")
        print(f"   📈 Average length: {statistics.mean(content_lengths):.1f} chars")
        print(f"   🚨 Quality issues: {sum(issues.values())} total")
        for issue_type, count in issues.items():
            if count > 0:
                print(f"      - {issue_type}: {count}")
    
    def analyze_metadata_quality(self, chunks: List[Dict]) -> None:
        """Analyze metadata completeness and consistency"""
        print("\n🏷️  Analyzing metadata quality...")
        
        required_fields = ['chunk_id', 'state_code', 'content', 'content_type', 'program_type']
        field_completeness = {field: 0 for field in required_fields}
        
        content_type_distribution = Counter()
        program_type_distribution = Counter()
        year_distribution = Counter()
        
        inconsistencies = []
        
        for i, chunk in enumerate(chunks):
            # Check required field completeness
            for field in required_fields:
                if chunk.get(field):
                    field_completeness[field] += 1
            
            # Collect distributions
            content_type_distribution[chunk.get('content_type', 'unknown')] += 1
            program_type_distribution[chunk.get('program_type', 'unknown')] += 1
            year_distribution[chunk.get('document_year', 'unknown')] += 1
            
            # Check for inconsistencies
            chunk_id = chunk.get('chunk_id', '')
            state_code = chunk.get('state_code', '')
            
            if chunk_id and state_code:
                if not chunk_id.startswith(state_code):
                    inconsistencies.append({
                        'chunk_id': chunk_id,
                        'state_code': state_code,
                        'issue': 'chunk_id_state_mismatch'
                    })
        
        self.results['statistics']['metadata'] = {
            'field_completeness': {
                field: f"{count}/{len(chunks)} ({count/len(chunks)*100:.1f}%)"
                for field, count in field_completeness.items()
            },
            'content_types': dict(content_type_distribution.most_common()),
            'program_types': dict(program_type_distribution.most_common()),
            'years': dict(year_distribution.most_common()),
            'inconsistencies': len(inconsistencies)
        }
        
        print(f"   ✅ Field completeness:")
        for field, completion in self.results['statistics']['metadata']['field_completeness'].items():
            print(f"      - {field}: {completion}")
        
        print(f"   📊 Content type distribution:")
        for content_type, count in content_type_distribution.most_common(5):
            print(f"      - {content_type}: {count}")
        
        if inconsistencies:
            print(f"   ⚠️  Found {len(inconsistencies)} metadata inconsistencies")
            self.results['quality_issues']['metadata_inconsistencies'] = inconsistencies[:10]  # First 10
    
    def analyze_duplicate_content(self, chunks: List[Dict]) -> None:
        """Analyze content duplication patterns"""
        print("\n🔄 Analyzing content duplication...")
        
        # Group chunks by normalized content
        content_groups = defaultdict(list)
        
        for chunk in chunks:
            content = chunk.get('content', '').strip().lower()
            if len(content) > 50:  # Only analyze substantial content
                # Normalize content for comparison
                normalized = re.sub(r'\s+', ' ', content)
                normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
                
                content_groups[normalized].append({
                    'chunk_id': chunk.get('chunk_id'),
                    'state_code': chunk.get('state_code'),
                    'content_type': chunk.get('content_type'),
                    'length': len(chunk.get('content', ''))
                })
        
        # Find duplicates
        duplicates = []
        total_duplicate_chunks = 0
        
        for content, chunk_list in content_groups.items():
            if len(chunk_list) > 1:
                duplicates.append({
                    'content_preview': content[:100] + '...',
                    'duplicate_count': len(chunk_list),
                    'chunks': chunk_list
                })
                total_duplicate_chunks += len(chunk_list) - 1  # Don't count original
        
        # Sort by most duplicated
        duplicates.sort(key=lambda x: x['duplicate_count'], reverse=True)
        
        self.results['quality_issues']['duplicates'] = {
            'total_duplicate_groups': len(duplicates),
            'total_duplicate_chunks': total_duplicate_chunks,
            'top_duplicates': duplicates[:10]  # Top 10 most duplicated content
        }
        
        print(f"   🔍 Found {len(duplicates)} groups of duplicate content")
        print(f"   📝 Total duplicate chunks: {total_duplicate_chunks}")
        if duplicates:
            print(f"   🏆 Most duplicated: {duplicates[0]['duplicate_count']} copies")
    
    def generate_recommendations(self) -> None:
        """Generate actionable recommendations for data quality improvements"""
        recommendations = []
        
        issues = self.results['quality_issues']
        
        # Content issues
        if issues.get('content_summary', {}).get('too_short', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'content_processing',
                'issue': f"{issues['content_summary']['too_short']} chunks too short",
                'action': 'Implement minimum content length filter and merge adjacent short chunks',
                'impact': 'Removes low-quality extraction artifacts'
            })
        
        if issues.get('content_summary', {}).get('truncated_sentences', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'chunk_boundaries',
                'issue': f"{issues['content_summary']['truncated_sentences']} truncated sentences",
                'action': 'Improve sentence boundary detection and chunk merging',
                'impact': 'Ensures complete regulatory statements for better RAG accuracy'
            })
        
        if issues.get('duplicates', {}).get('total_duplicate_chunks', 0) > 100:
            recommendations.append({
                'priority': 'medium',
                'category': 'deduplication',
                'issue': f"{issues['duplicates']['total_duplicate_chunks']} duplicate chunks",
                'action': 'Implement semantic deduplication system',
                'impact': 'Reduces storage and improves search result relevance'
            })
        
        if issues.get('content_summary', {}).get('encoding_issues', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'text_processing',
                'issue': f"{issues['content_summary']['encoding_issues']} encoding issues",
                'action': 'Implement text normalization and encoding cleanup',
                'impact': 'Improves search accuracy and display quality'
            })
        
        # Metadata issues
        completeness = self.results['statistics'].get('metadata', {}).get('field_completeness', {})
        for field, completion_str in completeness.items():
            percentage = float(completion_str.split('(')[1].split('%')[0])
            if percentage < 95.0:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'metadata_validation',
                    'issue': f"{field} only {percentage:.1f}% complete",
                    'action': f'Add validation and auto-generation for {field}',
                    'impact': 'Improves filtering and search capabilities'
                })
        
        self.results['recommendations'] = recommendations
        
        print(f"\n💡 Generated {len(recommendations)} actionable recommendations")
        for rec in recommendations[:5]:  # Show top 5
            print(f"   🎯 {rec['priority'].upper()}: {rec['action']}")
    
    def run_analysis(self) -> Dict:
        """Run complete data quality analysis"""
        print("🔍 LIHTC Data Quality Analysis")
        print("=" * 60)
        
        # Load all chunks
        chunks = self.load_all_chunks()
        
        if not chunks:
            print("❌ No chunks found to analyze!")
            return self.results
        
        # Run analysis components
        self.analyze_content_quality(chunks)
        self.analyze_metadata_quality(chunks)
        self.analyze_duplicate_content(chunks)
        self.generate_recommendations()
        
        # Add timestamp
        self.results['analysis_timestamp'] = datetime.now().isoformat()
        
        return self.results
    
    def save_report(self, output_path: str = None) -> None:
        """Save detailed analysis report"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data_quality_report_{timestamp}.json"
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Saved detailed report to: {output_path}")

def main():
    """Run data quality analysis"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    analyzer = DataQualityAnalyzer(base_dir)
    
    results = analyzer.run_analysis()
    
    # Save report
    report_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/mac_studio_rag/data_quality_report.json"
    analyzer.save_report(report_path)
    
    # Print executive summary
    print("\n" + "=" * 60)
    print("📊 EXECUTIVE SUMMARY")
    print("=" * 60)
    print(f"Total Chunks Analyzed: {results['total_chunks']:,}")
    print(f"Jurisdictions Covered: {results['jurisdictions']}")
    
    if 'content_summary' in results['quality_issues']:
        issues = results['quality_issues']['content_summary']
        total_issues = sum(issues.values())
        print(f"Content Quality Issues: {total_issues:,} ({total_issues/results['total_chunks']*100:.1f}%)")
    
    if 'duplicates' in results['quality_issues']:
        duplicates = results['quality_issues']['duplicates']['total_duplicate_chunks']
        print(f"Duplicate Chunks: {duplicates:,} ({duplicates/results['total_chunks']*100:.1f}%)")
    
    print(f"Improvement Recommendations: {len(results['recommendations'])}")
    
    return results

if __name__ == "__main__":
    main()