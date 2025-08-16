#!/usr/bin/env python3
"""
Enhanced Chunk Processor for LIHTC RAG System
Addresses major data quality issues identified in analysis:
- 30.3% content quality issues (5,245 problems)
- 4.3% duplicate chunks (749 duplicates)
- 2,959 truncated sentences (17.1%)
- 1,622 encoding issues (9.4%)
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
from collections import Counter, defaultdict
import hashlib
from dataclasses import dataclass, asdict
import unicodedata

@dataclass
class EnhancedChunk:
    """Enhanced chunk with improved processing"""
    chunk_id: str
    state_code: str
    document_title: str
    document_year: int
    page_number: int
    section_title: str = ""
    content: str = ""
    content_type: str = "text"
    program_type: str = "both"
    chunk_size: int = 0
    entities: List[str] = None
    cross_references: List[str] = None
    metadata: Dict = None
    
    # Quality indicators
    quality_score: float = 0.0
    has_complete_sentences: bool = True
    encoding_clean: bool = True
    is_duplicate: bool = False
    duplicate_group_id: Optional[str] = None
    confidence_score: float = 1.0
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = []
        if self.cross_references is None:
            self.cross_references = []
        if self.metadata is None:
            self.metadata = {}
        self.chunk_size = len(self.content)

class EnhancedChunkProcessor:
    """Enhanced processing with quality improvements"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.qap_dir = self.base_dir / "QAP" / "_processed"
        self.output_dir = self.qap_dir / "_enhanced"
        self.output_dir.mkdir(exist_ok=True)
        
        # Processing statistics
        self.stats = {
            'chunks_processed': 0,
            'chunks_improved': 0,
            'duplicates_removed': 0,
            'sentences_fixed': 0,
            'encoding_fixed': 0,
            'quality_improvements': defaultdict(int)
        }
        
        # Content normalization patterns
        self.encoding_fixes = {
            '\u2013': '-',      # en dash
            '\u2014': '--',     # em dash
            '\u2018': "'",      # left single quote
            '\u2019': "'",      # right single quote
            '\u201C': '"',      # left double quote
            '\u201D': '"',      # right double quote
            '\u2022': '•',      # bullet point
            '\u00A0': ' ',      # non-breaking space
            '\u00B0': '°',      # degree symbol
        }
        
    def normalize_text(self, text: str) -> Tuple[str, bool]:
        """Normalize text encoding and fix common issues"""
        if not text:
            return "", True
        
        original_text = text
        
        # Fix common encoding issues
        for old_char, new_char in self.encoding_fixes.items():
            text = text.replace(old_char, new_char)
        
        # Normalize unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Remove problematic characters but preserve essential ones
        text = re.sub(r'[^\x00-\x7F\u00A0-\u00FF]', '', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        encoding_clean = (text == original_text)
        return text, encoding_clean
    
    def fix_sentence_boundaries(self, text: str) -> Tuple[str, bool]:
        """Fix truncated sentences and improve boundaries"""
        if not text or len(text) < 50:
            return text, True
        
        original_text = text
        
        # Check if ends with incomplete sentence
        text_stripped = text.strip()
        
        # If doesn't end with proper punctuation and doesn't end with colon/semicolon
        if not re.search(r'[.!?:;]\s*$', text_stripped):
            # If it looks like it was cut off mid-word or mid-sentence
            if re.search(r'\w$', text_stripped):
                # Try to complete the sentence by adding period if it looks complete
                words = text_stripped.split()
                if len(words) > 5:  # Only if substantial content
                    # Check if last few words form a complete thought
                    last_part = ' '.join(words[-3:]).lower()
                    if any(keyword in last_part for keyword in ['shall', 'must', 'will', 'required', 'percent', 'points', 'dollars']):
                        text = text_stripped + '.'
        
        # Fix common sentence boundary issues
        # Handle cases where sentences run together
        text = re.sub(r'([.!?])\s*([A-Z][a-z])', r'\1 \2', text)
        
        # Ensure proper spacing after punctuation
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
        sentences_fixed = (text != original_text)
        return text, sentences_fixed
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate hash for duplicate detection"""
        # Normalize content for comparison
        normalized = re.sub(r'\s+', ' ', content.lower())
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def classify_content_type_enhanced(self, text: str, section_title: str = "") -> str:
        """Enhanced content type classification"""
        text_lower = text.lower()
        section_lower = section_title.lower()
        
        # Check section title first for better accuracy
        if any(word in section_lower for word in ['appendix', 'exhibit', 'attachment', 'schedule']):
            return 'appendix'
        
        # Table detection (improved)
        if ('|' in text and text.count('|') > 5) or \
           ('\t' in text and text.count('\t') > 3) or \
           re.search(r'\d+\s+\d+\s+\d+', text) or \
           re.search(r'^\s*\w+\s*\|\s*\w+', text, re.MULTILINE):
            return 'table'
        
        # List detection (improved)
        list_patterns = [
            r'^\s*[•\-\*]\s+',  # Bullet points
            r'^\s*\d+\.\s+',    # Numbered lists
            r'^\s*\([a-z]\)\s+', # Lettered lists
            r'^\s*[a-z]\.\s+',   # Letter lists
        ]
        
        list_matches = sum(1 for pattern in list_patterns 
                          if re.search(pattern, text, re.MULTILINE))
        
        if list_matches >= 2:
            return 'list'
        
        # Regulation detection (enhanced)
        regulation_keywords = [
            'section', 'subsection', 'paragraph', 'shall', 'must', 'required',
            'prohibited', 'compliance', 'violation', 'penalty'
        ]
        
        regulation_score = sum(1 for keyword in regulation_keywords 
                             if keyword in text_lower)
        
        if regulation_score >= 3 or re.search(r'§\s*\d+', text):
            return 'regulation'
        
        # Appendix detection
        if any(word in text_lower for word in ['appendix', 'exhibit', 'attachment', 'schedule']):
            return 'appendix'
        
        return 'text'
    
    def calculate_quality_score(self, chunk: EnhancedChunk) -> float:
        """Calculate quality score for chunk"""
        score = 100.0
        
        # Content length penalties
        if chunk.chunk_size < 50:
            score -= 30  # Too short
        elif chunk.chunk_size > 5000:
            score -= 10  # Too long
        
        # Sentence completeness
        if not chunk.has_complete_sentences:
            score -= 20
        
        # Encoding issues
        if not chunk.encoding_clean:
            score -= 15
        
        # Duplicate penalty
        if chunk.is_duplicate:
            score -= 25
        
        # Content type confidence
        content = chunk.content.lower()
        if chunk.content_type == 'regulation' and 'shall' not in content and 'must' not in content:
            score -= 10  # Misclassified regulation
        
        # Cross-reference bonus
        if chunk.cross_references:
            score += 5
        
        # Entity extraction bonus
        if chunk.entities:
            score += 5
        
        return max(0.0, min(100.0, score))
    
    def process_chunks_from_file(self, state_code: str, chunks_file: Path) -> List[EnhancedChunk]:
        """Process chunks from a single jurisdiction file"""
        print(f"  📄 Processing {state_code}...")
        
        with open(chunks_file, 'r') as f:
            raw_chunks = json.load(f)
        
        enhanced_chunks = []
        content_hashes = {}
        duplicate_groups = defaultdict(list)
        
        # First pass: normalize and enhance
        for i, raw_chunk in enumerate(raw_chunks):
            # Create enhanced chunk
            chunk = EnhancedChunk(
                chunk_id=raw_chunk.get('chunk_id', f'{state_code}_enhanced_{i:04d}'),
                state_code=raw_chunk.get('state_code', state_code),
                document_title=raw_chunk.get('document_title', ''),
                document_year=raw_chunk.get('document_year', 2024),
                page_number=raw_chunk.get('page_number', 0),
                section_title=raw_chunk.get('section_title', ''),
                content=raw_chunk.get('content', ''),
                content_type=raw_chunk.get('content_type', 'text'),
                program_type=raw_chunk.get('program_type', 'both'),
                entities=raw_chunk.get('entities', []),
                cross_references=raw_chunk.get('cross_references', []),
                metadata=raw_chunk.get('metadata', {})
            )
            
            # Skip empty content
            if not chunk.content or len(chunk.content.strip()) < 10:
                continue
            
            # Normalize text
            normalized_content, encoding_clean = self.normalize_text(chunk.content)
            chunk.content = normalized_content
            chunk.encoding_clean = encoding_clean
            
            if not encoding_clean:
                self.stats['encoding_fixed'] += 1
            
            # Fix sentence boundaries
            fixed_content, sentences_fixed = self.fix_sentence_boundaries(chunk.content)
            chunk.content = fixed_content
            chunk.has_complete_sentences = not sentences_fixed
            
            if sentences_fixed:
                self.stats['sentences_fixed'] += 1
            
            # Enhanced content type classification
            chunk.content_type = self.classify_content_type_enhanced(
                chunk.content, chunk.section_title
            )
            
            # Calculate content hash for duplicate detection
            content_hash = self.calculate_content_hash(chunk.content)
            
            if content_hash in content_hashes:
                # Mark as duplicate
                chunk.is_duplicate = True
                chunk.duplicate_group_id = content_hash
                duplicate_groups[content_hash].append(chunk)
                content_hashes[content_hash].is_duplicate = True
                content_hashes[content_hash].duplicate_group_id = content_hash
            else:
                content_hashes[content_hash] = chunk
            
            # Calculate quality score
            chunk.quality_score = self.calculate_quality_score(chunk)
            
            enhanced_chunks.append(chunk)
            self.stats['chunks_processed'] += 1
        
        # Second pass: handle duplicates
        for content_hash, chunk_list in duplicate_groups.items():
            if len(chunk_list) > 1:
                # Keep the highest quality version
                best_chunk = max(chunk_list, key=lambda c: c.quality_score)
                best_chunk.is_duplicate = False
                best_chunk.duplicate_group_id = None
                
                # Mark others for removal
                for chunk in chunk_list:
                    if chunk.chunk_id != best_chunk.chunk_id:
                        enhanced_chunks.remove(chunk)
                        self.stats['duplicates_removed'] += 1
        
        # Count improvements
        improvements = sum(1 for chunk in enhanced_chunks 
                          if not chunk.encoding_clean or not chunk.has_complete_sentences)
        self.stats['chunks_improved'] += improvements
        
        print(f"     ✅ Enhanced {len(enhanced_chunks)} chunks (removed {len(raw_chunks) - len(enhanced_chunks)} low-quality)")
        
        return enhanced_chunks
    
    def save_enhanced_chunks(self, state_code: str, chunks: List[EnhancedChunk]) -> None:
        """Save enhanced chunks to file"""
        output_file = self.output_dir / f"{state_code}_enhanced_chunks.json"
        
        # Convert to dict for JSON serialization
        chunk_dicts = [asdict(chunk) for chunk in chunks]
        
        with open(output_file, 'w') as f:
            json.dump(chunk_dicts, f, indent=2, default=str)
        
        # Also create summary
        summary = {
            'state_code': state_code,
            'total_chunks': len(chunks),
            'processing_date': datetime.now().isoformat(),
            'quality_distribution': {
                'high_quality': len([c for c in chunks if c.quality_score >= 80]),
                'medium_quality': len([c for c in chunks if 60 <= c.quality_score < 80]),
                'low_quality': len([c for c in chunks if c.quality_score < 60])
            },
            'content_types': dict(Counter(c.content_type for c in chunks)),
            'program_types': dict(Counter(c.program_type for c in chunks)),
            'encoding_issues_fixed': len([c for c in chunks if not c.encoding_clean]),
            'sentence_issues_fixed': len([c for c in chunks if not c.has_complete_sentences])
        }
        
        summary_file = self.output_dir / f"{state_code}_enhancement_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def process_all_jurisdictions(self) -> None:
        """Process all jurisdiction files"""
        print("🔧 Enhanced Chunk Processing")
        print("=" * 60)
        
        jurisdictions_processed = 0
        
        for state_dir in self.qap_dir.iterdir():
            if state_dir.is_dir() and len(state_dir.name) <= 3:  # State codes
                state_code = state_dir.name
                chunks_file = state_dir / f"{state_code}_all_chunks.json"
                
                if chunks_file.exists():
                    try:
                        enhanced_chunks = self.process_chunks_from_file(state_code, chunks_file)
                        self.save_enhanced_chunks(state_code, enhanced_chunks)
                        jurisdictions_processed += 1
                    except Exception as e:
                        print(f"  ❌ Error processing {state_code}: {e}")
        
        # Create master enhanced index
        self.create_master_enhanced_index(jurisdictions_processed)
        
        # Print final statistics
        self.print_final_statistics(jurisdictions_processed)
    
    def create_master_enhanced_index(self, jurisdictions_count: int) -> None:
        """Create master index for enhanced chunks"""
        master_index = {
            'total_jurisdictions': jurisdictions_count,
            'total_enhanced_chunks': 0,
            'processing_date': datetime.now().isoformat(),
            'quality_improvements': dict(self.stats),
            'jurisdictions': {}
        }
        
        # Load summaries from each jurisdiction
        for summary_file in self.output_dir.glob("*_enhancement_summary.json"):
            with open(summary_file, 'r') as f:
                summary = json.load(f)
            
            state_code = summary['state_code']
            master_index['jurisdictions'][state_code] = summary
            master_index['total_enhanced_chunks'] += summary['total_chunks']
        
        # Save master index
        master_file = self.output_dir / "master_enhanced_index.json"
        with open(master_file, 'w') as f:
            json.dump(master_index, f, indent=2)
        
        print(f"\n📄 Created master enhanced index: {master_file}")
    
    def print_final_statistics(self, jurisdictions_count: int) -> None:
        """Print final processing statistics"""
        print("\n" + "=" * 60)
        print("📊 ENHANCEMENT SUMMARY")
        print("=" * 60)
        print(f"Jurisdictions Processed: {jurisdictions_count}")
        print(f"Total Chunks Processed: {self.stats['chunks_processed']:,}")
        print(f"Chunks Improved: {self.stats['chunks_improved']:,}")
        print(f"Duplicates Removed: {self.stats['duplicates_removed']:,}")
        print(f"Sentences Fixed: {self.stats['sentences_fixed']:,}")
        print(f"Encoding Issues Fixed: {self.stats['encoding_fixed']:,}")
        
        improvement_rate = (self.stats['chunks_improved'] / max(1, self.stats['chunks_processed'])) * 100
        print(f"Overall Improvement Rate: {improvement_rate:.1f}%")

def main():
    """Run enhanced chunk processing"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    processor = EnhancedChunkProcessor(base_dir)
    processor.process_all_jurisdictions()

if __name__ == "__main__":
    main()