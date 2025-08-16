# CTCAC QAP OCR TEMPLATE - ENHANCED FOR RAG/VECTOR DATABASE
## Optimized for AI Retrieval Systems

### ADDITIONAL RAG-SPECIFIC FORMATTING

#### 1. SEMANTIC CHUNKING MARKERS
```
[CHUNK_START: topic="At-Risk Housing" section="10325(c)(4)" type="definition,requirements"]
Content here...
[CHUNK_END]

[CHUNK_START: topic="Developer Fees" section="10327(c)(2)" type="limits,calculations"]
Content here...
[CHUNK_END]
```

#### 2. METADATA-RICH HEADERS
```
================================================================================
SECTION 10325. APPLICATION SELECTION CRITERIA
[METADATA]
- Section ID: 10325
- Topics: scoring, selection, competitive allocation, 9% credits
- Related Sections: 10322, 10326, 10327
- Key Concepts: basis limits, tiebreakers, set-asides, point scoring
- Applicability: 9% competitive rounds only
- Last Updated: December 11, 2024
[END METADATA]
================================================================================
```

#### 3. STRUCTURED Q&A PAIRS (For Fine-tuning)
```
[QA_PAIR]
Q: What is the developer fee limit for at-risk projects?
A: For at-risk projects, the developer fee limit is 15% of eligible basis 
   minus the developer fee, per Section 10327(c)(2)(A)(3).
CONTEXT: Section 10327(c)(2)(A) - Developer Fee Limits
[END_QA_PAIR]
```

#### 4. ENTITY RECOGNITION TAGS
```
The <<ENTITY:ORG>>California Tax Credit Allocation Committee<</ENTITY:ORG>> 
(<<ENTITY:ABBR>>CTCAC<</ENTITY:ABBR>>) requires <<ENTITY:PERCENT>>9%<</ENTITY:PERCENT>> 
applications to be submitted by <<ENTITY:DATE>>March 3, 2025<</ENTITY:DATE>>.

<<ENTITY:MONEY>>$500,000<</ENTITY:MONEY>> minimum for rehabilitation
<<ENTITY:REGULATION>>IRC Section 42(h)(3)(C)<</ENTITY:REGULATION>>
```

#### 5. SEMANTIC RELATIONSHIP MAPPING
```
[RELATIONSHIP]
SOURCE: Section 10325(c)(4) - At-Risk Set-Aside
TARGET: Section 10327(c)(2)(A)(3) - At-Risk Developer Fees
TYPE: fee_calculation
DESCRIPTION: At-risk projects qualifying under 10325(c)(4) receive 15% developer fee allowance under 10327(c)(2)(A)(3)
[END_RELATIONSHIP]
```

#### 6. CONCEPT HIERARCHY
```
[HIERARCHY: Set-Asides]
└── Geographic Set-Asides (10325(c)(1-3))
    ├── Rural: 20% minimum
    ├── Non-Rural Northern: specific %
    └── Non-Rural Southern: specific %
└── Project Type Set-Asides (10325(c)(4-8))
    ├── At-Risk: [varies by round]
    ├── SRO: 5% maximum
    ├── Special Needs: 5% maximum
    ├── Large Family: 20% minimum
    └── Native American: [if applicable]
[END_HIERARCHY]
```

#### 7. CALCULATION TEMPLATES
```
[FORMULA_TEMPLATE: name="Developer_Fee_Calculation"]
INPUT_PARAMS:
  - eligible_basis: number
  - project_type: enum[new_construction, at_risk, acquisition, rehab]
  - credit_type: enum[9%, 4%]
FORMULA:
  if project_type == "at_risk":
    max_fee = eligible_basis * 0.15 / 1.15
  else:
    max_fee = eligible_basis * 0.15 / 1.15
OUTPUT: developer_fee_amount
REFERENCE: Section 10327(c)(2)(A)
[END_FORMULA_TEMPLATE]
```

#### 8. VECTOR-FRIENDLY SUMMARIES
```
[SUMMARY: Section 10325(c)(9) - Tiebreakers]
Primary tiebreaker factors for 9% competitive allocation:
1. Lowest requested unadjusted eligible basis per unit
2. Readiness points (building permits, financing commitments)
3. Cost efficiency relative to threshold basis limits
Used when point scores are equal. Applied sequentially.
[END_SUMMARY]
```

#### 9. TEMPORAL MARKERS
```
[TIMELINE: 9% Application Process]
- Round 1 Deadline: <<DATE:2025-03-03>>March 3, 2025<</DATE>>
- Round 2 Deadline: <<DATE:2025-07-01>>July 1, 2025<</DATE>>
- Allocation Meeting: Within 90 days of deadline
- Reservation Expiration: 180 days (extensions possible)
[END_TIMELINE]
```

#### 10. DECISION TREE NOTATION
```
[DECISION_TREE: Eligible Basis Determination]
START: Is project federally subsidized?
├─YES→ Is it at-risk conversion?
│  ├─YES→ Apply 130% basis boost if in QCT/DDA
│  └─NO→ Standard basis (no boost unless QCT/DDA)
└─NO→ Is project in QCT or DDA?
   ├─YES→ Apply 130% basis boost
   └─NO→ Standard basis (100%)
[END_DECISION_TREE]
```

### IMPLEMENTATION FOR RAG SYSTEM

#### File Structure for Optimal Retrieval:
```
CTCAC_QAP_2025/
├── full_text_ocr.txt           # Complete OCR document
├── sections/                   # Individual section files
│   ├── 10301_definitions.txt
│   ├── 10325_selection_criteria.txt
│   └── 10327_building_requirements.txt
├── chunks/                     # Semantic chunks (300-500 tokens)
│   ├── chunk_001_at_risk_definition.txt
│   └── chunk_002_at_risk_requirements.txt
├── metadata/
│   ├── entity_index.json       # All recognized entities
│   ├── relationships.json      # Cross-references
│   └── qa_pairs.json          # Q&A for fine-tuning
└── embeddings/
    └── vector_store.db        # Pre-computed embeddings
```

#### Chunk Size Recommendations:
- **Primary chunks**: 300-500 tokens (optimal for most embedding models)
- **Context overlap**: 50-100 tokens between chunks
- **Section preservation**: Never split definitions or formulas

#### Additional Metadata for Each Chunk:
```json
{
  "chunk_id": "qap_2025_chunk_042",
  "source_section": "10325(c)(4)",
  "topics": ["at-risk", "preservation", "set-aside"],
  "chunk_type": "requirements",
  "importance_score": 0.9,
  "frequently_referenced": true,
  "last_updated": "2024-12-11",
  "embedding_model": "text-embedding-3-small",
  "parent_doc": "CTCAC_QAP_2025",
  "regulatory_level": "state",
  "applies_to": ["9% credits"],
  "geographic_scope": "california"
}
```

### QUICK IMPLEMENTATION SCRIPT
```python
# Example processing for RAG optimization
def process_for_rag(ocr_text):
    chunks = []
    
    # 1. Split into semantic chunks
    sections = split_by_section(ocr_text)
    
    for section in sections:
        # 2. Create overlapping chunks
        section_chunks = create_chunks(
            section, 
            chunk_size=400,
            overlap=75
        )
        
        # 3. Add metadata
        for chunk in section_chunks:
            chunk['metadata'] = extract_metadata(chunk['text'])
            chunk['entities'] = extract_entities(chunk['text'])
            chunk['qa_pairs'] = generate_qa(chunk['text'])
            
        chunks.extend(section_chunks)
    
    # 4. Create embeddings
    embeddings = embed_chunks(chunks)
    
    # 5. Store in vector DB
    store_in_vectordb(chunks, embeddings)
    
    return chunks
```

This enhanced formatting will significantly improve:
- **Retrieval accuracy**: Better semantic matching
- **Context preservation**: Maintains regulatory relationships
- **Query understanding**: Pre-structured Q&A pairs
- **Citation accuracy**: Precise section references
- **Multi-hop reasoning**: Clear relationship mapping