#!/usr/bin/env python3
"""
Complete Universe Search Engine
Unified search across QAP + external regulatory universe with cross-jurisdictional comparison

Features:
- Unified search across QAPs, state admin codes, federal regulations
- Cross-jurisdictional regulatory comparison
- Authority-weighted search results
- Semantic regulatory intelligence
- Real-time compliance analysis

Built by Structured Consultants LLC
Roman Engineering Standards: Built to Last 2000+ Years
"""

import re
import json
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from datetime import datetime
import hashlib
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SearchResultType(Enum):
    """Types of search results"""
    EXACT_MATCH = "exact_match"
    PARTIAL_MATCH = "partial_match"
    SEMANTIC_MATCH = "semantic_match"
    CROSS_REFERENCE = "cross_reference"

@dataclass
class SearchResult:
    """Individual search result"""
    result_id: str
    regulation_id: str
    jurisdiction: str
    authority_level: int           # 100=Federal IRC, 80=CFR, 30=State QAP, etc.
    result_type: SearchResultType
    title: str
    content_snippet: str          # Relevant content excerpt
    match_score: float            # 0.0-1.0 relevance score
    match_count: int              # Number of query matches
    section_id: str               # Specific section where match found
    cross_references: List[str]   # Related regulations
    compliance_notes: List[str]   # Compliance implications

@dataclass
class JurisdictionComparison:
    """Comparison of requirements across jurisdictions"""
    requirement_category: str
    jurisdictions: Dict[str, str]  # jurisdiction -> requirement text
    federal_baseline: str          # Federal minimum requirement
    variations: List[str]          # Key differences between states
    strictest_requirement: str     # Which jurisdiction is most restrictive
    compliance_complexity: str     # "simple", "moderate", "complex"

@dataclass
class SearchAnalysis:
    """Analysis of search results"""
    query: str
    total_results: int
    jurisdictions_covered: int
    authority_distribution: Dict[str, int]  # authority level -> count
    common_themes: List[str]
    regulatory_gaps: List[str]
    compliance_conflicts: List[str]

class CompleteUniverseSearchEngine:
    """Unified search engine for complete regulatory universe"""
    
    def __init__(self):
        self.regulatory_database = {}
        self.search_index = {}
        self.authority_weights = self._define_authority_weights()
        self.semantic_patterns = self._define_semantic_patterns()
        
    def _define_authority_weights(self) -> Dict[int, float]:
        """Define authority level weights for search ranking"""
        
        return {
            100: 1.0,    # Federal IRC - highest authority
            80: 0.9,     # Federal CFR
            60: 0.7,     # Federal guidance
            40: 0.5,     # Federal interpretive
            35: 0.6,     # State statutes
            30: 0.8,     # State QAPs (high relevance for LIHTC)
            20: 0.4,     # Municipal codes
            10: 0.3      # Local guidance
        }
    
    def _define_semantic_patterns(self) -> Dict[str, List[str]]:
        """Define semantic search patterns for LIHTC concepts"""
        
        return {
            "income_limits": [
                "area median income", "ami", "income restrictions", "income limits",
                "50 percent", "60 percent", "low income", "very low income"
            ],
            "rent_restrictions": [
                "rent limits", "affordable rent", "gross rent", "utility allowance",
                "maximum rent", "30 percent of income"
            ],
            "qualified_basis": [
                "eligible basis", "qualified basis", "130 percent", "basis boost",
                "difficult development areas", "qualified census tract"
            ],
            "compliance_monitoring": [
                "annual certification", "tenant certification", "compliance monitoring",
                "15 year compliance", "extended use period"
            ],
            "allocation_criteria": [
                "selection criteria", "scoring", "tie breaker", "set aside",
                "geographic distribution", "nonprofit set aside"
            ],
            "recapture": [
                "recapture", "noncompliance", "credit reduction", "acceleration",
                "disposition", "foreclosure"
            ]
        }
    
    def index_regulation(self, regulation_id: str, content: any, metadata: Dict[str, any] = None):
        """Add regulation to search index"""
        
        # Extract text content
        if hasattr(content, 'content'):
            text_content = content.content
        elif isinstance(content, dict) and 'content' in content:
            text_content = content['content']
        else:
            text_content = str(content)
        
        # Store in database
        self.regulatory_database[regulation_id] = {
            "content": text_content,
            "metadata": metadata or {},
            "indexed_at": datetime.now().isoformat()
        }
        
        # Create search index
        self._create_search_index(regulation_id, text_content, metadata)
        
        logger.info(f"Indexed {regulation_id}: {len(text_content):,} characters")
    
    def _create_search_index(self, regulation_id: str, content: str, metadata: Dict[str, any]):
        """Create searchable index for regulation"""
        
        # Tokenize content
        words = re.findall(r'\b\w+\b', content.lower())
        word_counts = Counter(words)
        
        # Create index entry
        self.search_index[regulation_id] = {
            "word_counts": word_counts,
            "total_words": len(words),
            "unique_words": len(word_counts),
            "sections": self._extract_sections(content),
            "jurisdiction": metadata.get("jurisdiction", "Unknown"),
            "authority_level": metadata.get("authority_level", 30),
            "regulation_type": metadata.get("regulation_type", "Unknown")
        }
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from regulation content"""
        
        sections = {}
        
        # Try different section patterns
        patterns = [
            r'(?:§|Section)\s*(\d+(?:\.\d+)*)\s*[.-]\s*([^§\n]+?)(?=(?:§|Section)\s*\d|$)',
            r'^\s*\(([a-z0-9]+)\)\s+([^(]+?)(?=^\s*\([a-z0-9]+\)|$)',
            r'Part\s+([IVX]+)\s*[.-]\s*([^P\n]+?)(?=Part\s+[IVX]+|$)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                section_id = match.group(1)
                section_content = match.group(2).strip()[:500]  # Limit length
                sections[section_id] = section_content
        
        return sections
    
    def search(self, query: str, jurisdictions: List[str] = None, authority_levels: List[int] = None, max_results: int = 50) -> List[SearchResult]:
        """Search across complete regulatory universe"""
        
        logger.info(f"🔍 Searching for: '{query}'")
        
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        
        results = []
        
        for regulation_id, index_data in self.search_index.items():
            # Filter by jurisdiction
            if jurisdictions and index_data["jurisdiction"] not in jurisdictions:
                continue
            
            # Filter by authority level
            if authority_levels and index_data["authority_level"] not in authority_levels:
                continue
            
            # Calculate match score
            match_score = self._calculate_match_score(query_words, query_lower, regulation_id, index_data)
            
            if match_score > 0.1:  # Minimum threshold
                # Find best matching section
                best_section, snippet = self._find_best_section_match(query_lower, regulation_id)
                
                # Count exact matches
                content = self.regulatory_database[regulation_id]["content"]
                match_count = len(re.findall(re.escape(query), content, re.IGNORECASE))
                
                # Determine result type
                if query.lower() in content.lower():
                    if match_count > 5:
                        result_type = SearchResultType.EXACT_MATCH
                    else:
                        result_type = SearchResultType.PARTIAL_MATCH
                else:
                    result_type = SearchResultType.SEMANTIC_MATCH
                
                # Get cross-references
                cross_refs = self._extract_cross_references(content)
                
                # Generate compliance notes
                compliance_notes = self._generate_compliance_notes(query, content, index_data["jurisdiction"])
                
                result = SearchResult(
                    result_id=f"{regulation_id}_{hashlib.md5(query.encode()).hexdigest()[:8]}",
                    regulation_id=regulation_id,
                    jurisdiction=index_data["jurisdiction"],
                    authority_level=index_data["authority_level"],
                    result_type=result_type,
                    title=f"{regulation_id} - {index_data['regulation_type']}",
                    content_snippet=snippet,
                    match_score=match_score,
                    match_count=match_count,
                    section_id=best_section,
                    cross_references=cross_refs[:3],  # Limit to top 3
                    compliance_notes=compliance_notes
                )
                
                results.append(result)
        
        # Sort by relevance (match score * authority weight)
        results.sort(key=lambda r: r.match_score * self.authority_weights.get(r.authority_level, 0.5), reverse=True)
        
        return results[:max_results]
    
    def _calculate_match_score(self, query_words: Set[str], query_full: str, regulation_id: str, index_data: Dict) -> float:
        """Calculate relevance score for search result"""
        
        word_counts = index_data["word_counts"]
        total_words = index_data["total_words"]
        
        # Base score from word matches
        word_matches = sum(word_counts.get(word, 0) for word in query_words)
        word_score = word_matches / max(total_words, 1)
        
        # Boost for exact phrase matches
        content = self.regulatory_database[regulation_id]["content"].lower()
        phrase_matches = len(re.findall(re.escape(query_full), content))
        phrase_score = phrase_matches * 0.1
        
        # Boost for semantic matches
        semantic_score = self._calculate_semantic_score(query_full, content)
        
        # Authority level weighting
        authority_weight = self.authority_weights.get(index_data["authority_level"], 0.5)
        
        # Combine scores
        total_score = (word_score + phrase_score + semantic_score) * authority_weight
        
        return min(1.0, total_score)
    
    def _calculate_semantic_score(self, query: str, content: str) -> float:
        """Calculate semantic relevance score"""
        
        score = 0.0
        
        for category, patterns in self.semantic_patterns.items():
            category_matches = sum(1 for pattern in patterns if pattern in query.lower())
            content_matches = sum(1 for pattern in patterns if pattern in content.lower())
            
            if category_matches > 0 and content_matches > 0:
                score += 0.1 * min(category_matches, content_matches)
        
        return score
    
    def _find_best_section_match(self, query: str, regulation_id: str) -> Tuple[str, str]:
        """Find the section with the best match for the query"""
        
        sections = self.search_index[regulation_id]["sections"]
        content = self.regulatory_database[regulation_id]["content"]
        
        best_section = ""
        best_snippet = ""
        best_score = 0
        
        for section_id, section_content in sections.items():
            section_lower = section_content.lower()
            matches = len(re.findall(re.escape(query), section_lower))
            
            if matches > best_score:
                best_score = matches
                best_section = section_id
                best_snippet = section_content[:300] + "..." if len(section_content) > 300 else section_content
        
        # If no section match, use content snippet around first match
        if not best_snippet:
            match = re.search(re.escape(query), content, re.IGNORECASE)
            if match:
                start = max(0, match.start() - 150)
                end = min(len(content), match.end() + 150)
                best_snippet = content[start:end]
                best_section = "general"
        
        return best_section, best_snippet
    
    def _extract_cross_references(self, content: str) -> List[str]:
        """Extract cross-references from content"""
        
        references = []
        
        # Common reference patterns
        patterns = [
            r'IRC\s+Section\s+\d+[a-z]*',
            r'\d+\s+CFR\s+[\d.]+',
            r'Section\s+\d+[a-z]*',
            r'Part\s+[IVX]+',
            r'Rule\s+\d+-\d+'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            references.extend(matches)
        
        return list(set(references))
    
    def _generate_compliance_notes(self, query: str, content: str, jurisdiction: str) -> List[str]:
        """Generate compliance notes based on search context"""
        
        notes = []
        
        # Check for compliance keywords
        if any(word in query.lower() for word in ["income", "rent", "ami"]):
            if "certification" in content.lower():
                notes.append("Annual tenant income certification required")
            if "monitoring" in content.lower():
                notes.append("Subject to ongoing compliance monitoring")
        
        if "allocation" in query.lower():
            notes.append(f"Allocation governed by {jurisdiction} QAP procedures")
        
        if "recapture" in query.lower():
            notes.append("Noncompliance may trigger credit recapture")
        
        return notes
    
    def compare_across_jurisdictions(self, query: str, jurisdictions: List[str]) -> JurisdictionComparison:
        """Compare regulatory requirements across jurisdictions"""
        
        logger.info(f"🔄 Comparing '{query}' across {len(jurisdictions)} jurisdictions")
        
        jurisdiction_results = {}
        federal_baseline = ""
        
        for jurisdiction in jurisdictions:
            results = self.search(query, jurisdictions=[jurisdiction], max_results=5)
            
            if results:
                # Get best result for this jurisdiction
                best_result = results[0]
                jurisdiction_results[jurisdiction] = best_result.content_snippet
                
                # Capture federal baseline
                if best_result.authority_level >= 80:  # Federal authority
                    federal_baseline = best_result.content_snippet
        
        # Analyze variations
        variations = self._analyze_variations(jurisdiction_results)
        strictest = self._identify_strictest_requirement(jurisdiction_results)
        complexity = self._assess_compliance_complexity(jurisdiction_results)
        
        return JurisdictionComparison(
            requirement_category=query,
            jurisdictions=jurisdiction_results,
            federal_baseline=federal_baseline,
            variations=variations,
            strictest_requirement=strictest,
            compliance_complexity=complexity
        )
    
    def _analyze_variations(self, jurisdiction_results: Dict[str, str]) -> List[str]:
        """Analyze key variations between jurisdictions"""
        
        variations = []
        
        # Look for numeric differences
        for jurisdiction, content in jurisdiction_results.items():
            numbers = re.findall(r'\d+(?:\.\d+)?%?', content)
            if numbers:
                variations.append(f"{jurisdiction}: {', '.join(numbers[:3])}")
        
        return variations
    
    def _identify_strictest_requirement(self, jurisdiction_results: Dict[str, str]) -> str:
        """Identify the most restrictive requirement"""
        
        # Simple heuristic: jurisdiction with most compliance-related words
        strictest_jurisdiction = ""
        max_compliance_words = 0
        
        compliance_keywords = ["must", "shall", "required", "mandatory", "compliance", "monitoring"]
        
        for jurisdiction, content in jurisdiction_results.items():
            compliance_count = sum(1 for keyword in compliance_keywords if keyword in content.lower())
            if compliance_count > max_compliance_words:
                max_compliance_words = compliance_count
                strictest_jurisdiction = jurisdiction
        
        return strictest_jurisdiction
    
    def _assess_compliance_complexity(self, jurisdiction_results: Dict[str, str]) -> str:
        """Assess overall compliance complexity"""
        
        total_words = sum(len(content.split()) for content in jurisdiction_results.values())
        avg_words_per_jurisdiction = total_words / len(jurisdiction_results) if jurisdiction_results else 0
        
        if avg_words_per_jurisdiction > 100:
            return "complex"
        elif avg_words_per_jurisdiction > 50:
            return "moderate"
        else:
            return "simple"
    
    def analyze_search_results(self, results: List[SearchResult], query: str) -> SearchAnalysis:
        """Analyze search results for insights"""
        
        jurisdictions = set(r.jurisdiction for r in results)
        authority_dist = defaultdict(int)
        
        for result in results:
            authority_dist[f"Level_{result.authority_level}"] += 1
        
        # Extract common themes
        all_snippets = " ".join(r.content_snippet for r in results)
        common_words = [word for word, count in Counter(all_snippets.lower().split()).most_common(10)]
        
        return SearchAnalysis(
            query=query,
            total_results=len(results),
            jurisdictions_covered=len(jurisdictions),
            authority_distribution=dict(authority_dist),
            common_themes=common_words,
            regulatory_gaps=["Identified gaps require further analysis"],
            compliance_conflicts=["No major conflicts detected"]
        )
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the regulatory database"""
        
        total_regulations = len(self.regulatory_database)
        total_characters = sum(len(reg["content"]) for reg in self.regulatory_database.values())
        
        jurisdiction_counts = defaultdict(int)
        authority_counts = defaultdict(int)
        
        for reg_id, index_data in self.search_index.items():
            jurisdiction_counts[index_data["jurisdiction"]] += 1
            authority_counts[f"Level_{index_data['authority_level']}"] += 1
        
        return {
            "total_regulations": total_regulations,
            "total_characters": total_characters,
            "average_regulation_size": total_characters // total_regulations if total_regulations > 0 else 0,
            "jurisdictions": dict(jurisdiction_counts),
            "authority_levels": dict(authority_counts),
            "search_index_size": len(self.search_index)
        }

def main():
    """Test complete universe search engine"""
    
    print("🏛️ COMPLETE UNIVERSE SEARCH ENGINE")
    print("=" * 60)
    
    search_engine = CompleteUniverseSearchEngine()
    
    # Index sample regulations
    sample_regulations = {
        "CA_QAP_2025": {
            "content": "The California QAP requires income limits at 50% and 60% of area median income. Projects must maintain affordability for 55 years. Scoring criteria include location, amenities, and developer experience. Compliance monitoring is conducted annually.",
            "metadata": {
                "jurisdiction": "CA",
                "authority_level": 30,
                "regulation_type": "State QAP"
            }
        },
        "IRC_SECTION_42": {
            "content": "IRC Section 42 establishes the Low-Income Housing Tax Credit program. Qualified low-income buildings must meet income and rent restrictions. The credit period is 10 years with a 15-year compliance period. Recapture applies for noncompliance.",
            "metadata": {
                "jurisdiction": "Federal",
                "authority_level": 100,
                "regulation_type": "Federal Statute"
            }
        },
        "FL_QAP_2025": {
            "content": "Florida allocates credits based on geographic distribution and developer experience. Set-asides include nonprofit and rural developments. Compliance monitoring includes annual certifications and physical inspections.",
            "metadata": {
                "jurisdiction": "FL",
                "authority_level": 30,
                "regulation_type": "State QAP"
            }
        },
        "26_CFR_1_42_5": {
            "content": "Federal regulations define qualified low-income buildings and compliance requirements. Annual income certifications are required for all low-income tenants. Rent restrictions apply to gross rent including utilities.",
            "metadata": {
                "jurisdiction": "Federal",
                "authority_level": 80,
                "regulation_type": "Federal Regulation"
            }
        }
    }
    
    # Index all regulations
    for reg_id, reg_data in sample_regulations.items():
        search_engine.index_regulation(reg_id, reg_data["content"], reg_data["metadata"])
    
    # Test searches
    test_queries = [
        "income limits",
        "compliance monitoring",
        "recapture",
        "nonprofit set aside"
    ]
    
    for query in test_queries:
        print(f"\n🔍 SEARCH: '{query}'")
        print("-" * 40)
        
        results = search_engine.search(query, max_results=3)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.regulation_id} ({result.jurisdiction})")
            print(f"   Authority Level: {result.authority_level} | Score: {result.match_score:.3f}")
            print(f"   {result.content_snippet[:100]}...")
            if result.compliance_notes:
                print(f"   📋 {result.compliance_notes[0]}")
        
        if not results:
            print("   No results found")
    
    # Test cross-jurisdictional comparison
    print(f"\n🔄 CROSS-JURISDICTIONAL COMPARISON:")
    print("-" * 40)
    
    comparison = search_engine.compare_across_jurisdictions("income limits", ["CA", "FL"])
    print(f"Category: {comparison.requirement_category}")
    print(f"Jurisdictions covered: {len(comparison.jurisdictions)}")
    print(f"Compliance complexity: {comparison.compliance_complexity}")
    print(f"Variations: {comparison.variations}")
    
    # Show database statistics
    stats = search_engine.get_database_stats()
    print(f"\n📊 DATABASE STATISTICS:")
    print("-" * 40)
    print(f"Total regulations: {stats['total_regulations']:,}")
    print(f"Total content: {stats['total_characters']:,} characters")
    print(f"Average size: {stats['average_regulation_size']:,} chars/regulation")
    print(f"Jurisdictions: {list(stats['jurisdictions'].keys())}")
    print(f"Authority levels: {list(stats['authority_levels'].keys())}")
    
    print(f"\n✅ Search Engine Test Complete")

if __name__ == "__main__":
    main()