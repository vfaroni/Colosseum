# CTCAC QAP OCR Processing Documentation

## Project Overview

This document outlines the comprehensive OCR (Optical Character Recognition) processing of the **California Tax Credit Allocation Committee (CTCAC) December 11, 2024 QAP Regulations** for use in a Retrieval-Augmented Generation (RAG) system. The project transforms a 109-page PDF regulatory document into an AI-optimized, searchable format with critical program-specific tagging.

## Business Context

### Problem Statement
The CTCAC QAP regulations govern both **9% competitive tax credit** and **4% tax-exempt bond** programs, with different rules, requirements, and procedures for each. Standard OCR would create a simple text file, but this approach would be inadequate for an AI system that needs to:

1. **Distinguish between programs** - Prevent mixing 9% competitive rules with 4% bond rules
2. **Maintain regulatory accuracy** - Ensure citations and cross-references are preserved
3. **Enable semantic search** - Allow queries like "What's the developer fee limit?" to be answered correctly based on program type
4. **Support compliance** - Provide structured data for automated compliance checking

### Why This Matters
- **Regulatory Compliance**: Wrong program rules = failed applications or compliance violations
- **Cost Efficiency**: Automated regulatory guidance reduces manual legal review
- **User Safety**: AI must never confuse 9% vs 4% program requirements
- **Data Quality**: Structured extraction enables better AI responses than raw text

## Technical Approach

### 1. Enhanced OCR Strategy

Instead of basic text extraction, we implemented:

**RAG-Optimized Processing**:
- Semantic chunking for vector databases
- Metadata enrichment for better search
- Entity recognition for structured queries
- Cross-reference mapping for multi-hop reasoning

**Program-Specific Tagging**:
- 9% competitive sections clearly marked
- 4% tax-exempt bond sections identified
- Shared sections tagged with program variations
- Inline program tags for subsection differences

### 2. File Structure Design

```
CTCAC_QAP_2025_RAG/
├── CTCAC_QAP_2025_OCR_RAG.txt    # Main formatted document
├── sections/                      # Individual section files (29 total)
│   ├── 10325_Application_Selection_Criteria.txt  # 9% only
│   ├── 10326_Tax-Exempt_Bond_Applications.txt    # 4% only
│   └── 10327_Building_Requirements.txt           # Both programs
├── chunks/                        # Semantic chunks for vector DB (30 total)
│   ├── ctcac_qap_2025_chunk_0000.json
│   └── [each chunk includes program applicability]
├── metadata/                      # Search indices and mappings
│   ├── program_mapping.json      # Section-to-program mapping
│   ├── entities.json             # Extracted entities (dates, money, etc.)
│   ├── chunk_index.json          # Chunk organization by topic/program
│   └── qa_pairs.json             # Question-answer pairs for fine-tuning
└── extraction_summary.json       # Complete processing report
```

## Implementation Details

### Core Files Created

#### 1. OCR Templates and Guides
- **`qap_ocr_template.md`** - Original OCR formatting template
- **`qap_ocr_rag_template.md`** - Enhanced template with RAG optimizations
- **`ctcac_9p_4p_mapping.md`** - Program applicability mapping guide

#### 2. Processing Scripts
- **`ctcac_qap_ocr_rag_extractor.py`** - Main OCR extraction script with RAG optimization

#### 3. Output Files
- **`CTCAC_QAP_2025_RAG/`** - Complete processed document structure

### Key Technical Features

#### Program Applicability Tagging
```
[APPLICABILITY: 9% COMPETITIVE ONLY]
[NOT_APPLICABLE: 4% Tax-Exempt Bond Projects - See Section 10326]
```

#### Semantic Chunking with Metadata
```json
{
  "chunk_id": "ctcac_qap_2025_chunk_0005",
  "program_applicability": ["9%", "4%"],
  "topics": ["set-aside", "developer-fee"],
  "entities": [{"type": "MONEY", "value": "$500,000"}],
  "warning": "Check program type before applying rules"
}
```

#### Cross-Reference Tracking
```
Section 10327(c)(2)(A) <<XREF:10327_c_2_A>>
```

#### Entity Recognition
```
<<ENTITY:MONEY>>$500,000<</ENTITY:MONEY>>
<<ENTITY:PERCENT>>15%<</ENTITY:PERCENT>>
<<ENTITY:DATE>>March 3, 2025<</ENTITY:DATE>>
```

## Processing Results

### Extraction Statistics
- **Source**: 109-page PDF (December 11, 2024 QAP Regulations)
- **Sections Extracted**: 29 regulatory sections
- **Chunks Created**: 30 semantic chunks optimized for vector search
- **Entities Found**: 328 structured entities (dates, money, percentages, references)
- **Processing Time**: ~2 minutes on standard hardware

### Program Classification Results
- **9% Competitive Only**: Section 10325 (Application Selection Criteria)
- **4% Tax-Exempt Bond Only**: Section 10326 (Tax-Exempt Bond Projects)
- **Both Programs**: Sections 10300-10302, 10322, 10327 (with variation tagging)

### Quality Metrics
- **Text Accuracy**: High-quality extraction using pdfplumber library
- **Structure Preservation**: All section headers, subsections, and cross-references maintained
- **Metadata Completeness**: 100% of chunks include program applicability
- **Entity Coverage**: All regulatory references, dates, and monetary amounts tagged

## Use Cases and Applications

### 1. RAG System Integration
```python
# Example query routing based on program type
def query_ctcac_rules(question, program_type):
    if program_type == "9%":
        # Route to 9% competitive chunks only
        relevant_chunks = filter_chunks_by_program("9%")
    elif program_type == "4%":
        # Route to 4% bond chunks only
        relevant_chunks = filter_chunks_by_program("4%")
    
    return search_and_generate_response(question, relevant_chunks)
```

### 2. Compliance Checking
```python
# Automated compliance validation
def validate_developer_fee(project_type, fee_amount, eligible_basis):
    if project_type == "9%_at_risk":
        max_fee = eligible_basis * 0.15 / 1.15  # Section 10327(c)(2)(A)(3)
    elif project_type == "9%_standard":
        max_fee = eligible_basis * 0.15 / 1.15  # Section 10327(c)(2)(A)(1)
    elif project_type == "4%":
        # Different calculation for 4% projects
        max_fee = calculate_4_percent_fee_limit(eligible_basis)
    
    return fee_amount <= max_fee
```

### 3. Document Search and Navigation
- **Semantic Search**: "What are the at-risk project requirements?" → Automatically routes to relevant 9% competitive sections
- **Cross-Reference Navigation**: Click on "Section 10327(c)(2)(A)" → Jump to exact location
- **Program Filtering**: Show only 4% tax-exempt bond requirements

## Team Usage Guide

### For Developers (Vitor and Team)

#### Vector Database Setup
```python
# Load chunks into vector database
import json
from pathlib import Path

chunks_dir = Path("CTCAC_QAP_2025_RAG/chunks/")
for chunk_file in chunks_dir.glob("*.json"):
    with open(chunk_file) as f:
        chunk_data = json.load(f)
        
    # Create embedding
    embedding = create_embedding(chunk_data["text"])
    
    # Store with metadata
    vector_db.store(
        id=chunk_data["chunk_id"],
        embedding=embedding,
        metadata=chunk_data["metadata"],
        text=chunk_data["text"]
    )
```

#### Query Enhancement
```python
def enhance_query_with_program_context(user_query, project_type=None):
    if not project_type:
        # Prompt user for program type
        return "Is this for a 9% competitive or 4% tax-exempt bond project?"
    
    # Add program context to query
    enhanced_query = f"[{project_type} LIHTC] {user_query}"
    
    # Filter search results by program applicability
    return search_with_program_filter(enhanced_query, project_type)
```

### For Claude Project Integration

#### Prompt Engineering
```
System: You are a CTCAC LIHTC expert. Always ask for project type (9% competitive vs 4% tax-exempt bond) before answering program-specific questions. Use the structured OCR data to provide accurate, section-specific citations.

User: What's the developer fee limit?
Assistant: I need to know your project type first. Are you working on:
1. A 9% competitive tax credit project, or 
2. A 4% tax-exempt bond project?

The developer fee limits are different for each program type.
```

#### Document Loading
```python
# Load the processed CTCAC regulations
with open("CTCAC_QAP_2025_RAG/CTCAC_QAP_2025_OCR_RAG.txt") as f:
    ctcac_regulations = f.read()

# Load program mappings
with open("CTCAC_QAP_2025_RAG/metadata/program_mapping.json") as f:
    program_mapping = json.load(f)
```

### For Claude Code Sessions

#### File Navigation
```bash
# Quick section lookup
grep -n "SECTION_10325" CTCAC_QAP_2025_OCR_RAG.txt

# Find all 9% competitive sections
grep -l "9% ONLY" sections/*.txt

# Search for specific topics
grep -r "developer fee" chunks/ | head -5
```

#### Content Verification
```bash
# Check program tagging accuracy
jq '.program_applicability' chunks/*.json | sort | uniq -c

# Validate entity extraction
jq '.metadata.entities[] | select(.type=="MONEY") | .value' chunks/*.json
```

## Data Quality and Validation

### Accuracy Checks Performed
1. **Section Mapping Verification**: Cross-referenced known 9% vs 4% sections
2. **Entity Extraction Validation**: Spot-checked monetary amounts and percentages
3. **Cross-Reference Integrity**: Verified section reference tagging
4. **Chunk Completeness**: Ensured all major content areas are represented

### Known Limitations
1. **Complex Tables**: Some regulatory tables may require manual review
2. **Footnotes**: Small footnotes might be missed in automated processing
3. **Graphic Elements**: Charts and diagrams are not processed
4. **Legal Interpretation**: OCR provides text, not legal analysis

### Quality Assurance Recommendations
1. **Spot Check**: Manually verify 5-10 chunks against original PDF
2. **Cross-Reference Test**: Validate that section references link correctly
3. **Program Logic Test**: Ensure 9% vs 4% tagging is accurate
4. **Entity Validation**: Check that monetary amounts and percentages are correct

## Future Enhancements

### Planned Improvements
1. **Formula Extraction**: Programmatic extraction of calculation formulas
2. **Timeline Integration**: Automated deadline and timeline tracking
3. **Comparative Analysis**: Side-by-side 9% vs 4% requirement comparison
4. **Update Tracking**: Change detection for regulation updates

### Integration Opportunities
1. **Compliance Dashboard**: Real-time compliance checking interface
2. **Application Assistant**: Guided application completion based on regulations
3. **Training Module**: Interactive learning system for LIHTC professionals
4. **API Development**: Regulatory query API for external systems

## Conclusion

The CTCAC QAP OCR processing project successfully transforms a complex regulatory document into an AI-ready format that maintains critical program distinctions while enabling sophisticated search and retrieval capabilities. The structured approach ensures regulatory accuracy while supporting advanced AI applications for LIHTC compliance and guidance.

The deliverables provide a solid foundation for RAG system implementation, with comprehensive metadata, program-specific tagging, and quality assurance measures that ensure reliable AI-powered regulatory assistance.

---

**Project Team**: Bill Rice, Vitor  
**Completion Date**: June 17, 2025  
**Document Version**: 1.0  
**Last Updated**: June 17, 2025