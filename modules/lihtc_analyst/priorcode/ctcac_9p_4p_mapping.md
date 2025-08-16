# CTCAC 9% vs 4% SECTION MAPPING
## Critical for RAG Accuracy

### WHY THIS MATTERS
- **Different Rules**: Developer fees, basis limits, and requirements differ
- **User Queries**: "What's the developer fee limit?" has different answers for 9% vs 4%
- **Fatal Errors**: Applying 9% competitive scoring to a 4% deal would be wrong
- **Set-Asides**: Only apply to 9% competitive rounds, not 4% bonds

### KNOWN SECTION MAPPINGS

#### 9% COMPETITIVE ONLY SECTIONS
- **Section 10325**: Application Selection Criteria
  - Competitive scoring system
  - Set-asides (Geographic, At-Risk, SRO, etc.)
  - Tiebreakers
  - Point scoring categories
  - Competitive round deadlines

#### 4% TAX-EXEMPT BOND ONLY SECTIONS  
- **Section 10326**: Tax-Exempt Bond Projects
  - Minimum scoring requirements (not competitive)
  - Bond cap allocation procedures
  - Tax-Exempt bond specific requirements
  - Different timeline/process

#### BOTH 9% AND 4% SECTIONS (With Variations)
- **Section 10327**: Building Requirements
  - 10327(c)(2)(A): Developer Fee Limits
    - 9% Projects: 15% of eligible basis formula
    - 4% Projects: Different limits/calculations
  - Minimum construction standards
  - Accessibility requirements
  - Sustainable building methods

- **Section 10322**: Application Requirements
  - Different deadlines
  - Different documentation requirements
  - Some shared baseline requirements

- **Sections 10300-10302**: Definitions
  - Apply to both but some definitions specify program differences

### ENHANCED TAGGING FOR OCR

```
[SECTION_HEADER]
================================================================================
SECTION 10325. APPLICATION SELECTION CRITERIA
[APPLICABILITY: 9% COMPETITIVE ONLY]
[NOT_APPLICABLE: 4% Tax-Exempt Bond Projects - See Section 10326]
[METADATA]
- Program Type: 9% Competitive Tax Credits
- Purpose: Competitive scoring and ranking
- Key Features: Set-asides, Point scoring, Tiebreakers
[END_METADATA]
================================================================================

[SECTION_HEADER]  
================================================================================
SECTION 10327. BUILDING REQUIREMENTS
[APPLICABILITY: BOTH 9% AND 4% WITH VARIATIONS]
[METADATA]
- Program Type: Both 9% and 4% Credits
- Variations By Subsection:
  - 10327(c)(2)(A): Developer Fees - Different limits by program
  - 10327(g): Documentation - Some differences in timing
[END_METADATA]
================================================================================
```

### INLINE PROGRAM TAGS

```
(c)(2)(A) Developer Fee Limits <<PROGRAM:BOTH>>
    (1) <<PROGRAM:9%>> For 9% competitive tax credit projects, the 
        developer fee shall not exceed fifteen percent (15%) of 
        eligible basis minus developer fee...
        
    (2) <<PROGRAM:4%>> For tax-exempt bond projects under Section 
        10326, the developer fee shall be limited to...
        
    (3) <<PROGRAM:9%_ONLY>> Notwithstanding paragraph (1), for 
        at-risk projects competing in the 9% program...
```

### CHUNK-LEVEL METADATA

```json
{
  "chunk_id": "qap_2025_chunk_042",
  "program_applicability": ["9%"],  // or ["4%"] or ["9%", "4%"]
  "section": "10325(c)(4)",
  "warning_if_wrong_program": "This section only applies to 9% competitive credits",
  "alternative_section": "For 4% projects, see Section 10326"
}
```

### DECISION ROUTING

```
[PROGRAM_ROUTER: Developer Fee Limits]
IF user_project_type == "9% Competitive":
    → Route to Section 10327(c)(2)(A)(1) - 15% standard
    → Check 10327(c)(2)(A)(3) for at-risk exception
ELIF user_project_type == "4% Tax-Exempt Bond":
    → Route to Section 10327(c)(2)(A)(2) - Different calculation
    → Check Section 10326 for additional bond requirements
[END_PROGRAM_ROUTER]
```

### RECOMMENDATION: OCR APPROACH

1. **First Pass**: During OCR, tag every section header with program applicability
2. **Second Pass**: Within sections, identify subsections that differ by program
3. **Create Parallel Indices**:
   - 9%_only_sections_index.json
   - 4%_only_sections_index.json  
   - both_programs_sections_index.json
   - variation_points_index.json

4. **Query Enhancement**: 
   ```python
   def enhance_query(user_query, project_type=None):
       if not project_type:
           # Ask user: "Is this for a 9% competitive or 4% bond project?"
           return prompt_for_project_type()
       
       # Prepend to embedding search
       enhanced_query = f"[{project_type}] {user_query}"
       
       # Filter chunks by program_applicability
       return search_with_program_filter(enhanced_query, project_type)
   ```

### CRITICAL SECTIONS TO CAREFULLY TAG

1. **Set-Asides** (9% only) - Section 10325(c)
2. **Competitive Scoring** (9% only) - Section 10325
3. **Minimum Score Requirements** (Different for each) - 10325 vs 10326
4. **Developer Fee Calculations** - Section 10327(c)(2)(A)
5. **Credit Percentages** - Different basis boosts
6. **Application Deadlines** - Completely different schedules
7. **Tiebreakers** (9% only) - Section 10325(c)(9)

This upfront tagging will prevent costly errors and ensure accurate RAG responses!