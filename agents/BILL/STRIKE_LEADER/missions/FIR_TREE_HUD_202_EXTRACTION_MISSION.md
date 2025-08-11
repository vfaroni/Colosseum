# STRIKE LEADER MISSION: FIR TREE HUD 202 SENIOR PROPERTY EXTRACTION

**Mission ID**: FT-HUD-202-001  
**Priority**: CRITICAL - ACQUISITION DECISION  
**Commander**: M4 Strike Leader  
**Date**: 2025-08-09  
**Status**: ACTIVE  

## MISSION OBJECTIVE

Extract, validate, and analyze complete underwriting data from Fir Tree Park Apartments (60-unit HUD 202 senior property in Shelton, WA) for acquisition decision. Deploy GPT-OSS models with Docling to achieve 95%+ extraction accuracy in 72 hours.

## CRITICAL INTELLIGENCE

**Property**: Fir Tree Park Apartments  
**Location**: 614 North 4th Street, Shelton, WA 98584  
**Transaction**: Held for sale, closing June 30, 2025  
**Mission Critical**: Preserve affordable senior housing through strategic acquisition  

## EXTRACTION BATTLE PLAN

### CATEGORY 1: FINANCIAL OPERATIONS
**Priority**: IMMEDIATE  
**Model**: GPT-OSS 20B  
**Documents**: Excel files (xlwings), Audited Financials  

**Targets**:
- NOI: $65,538 (validate)
- HAP Revenue: $230,347
- Debt Service: $63,983
- Reserves: $100,288

### CATEGORY 2: REGULATORY COMPLIANCE  
**Priority**: CRITICAL  
**Model**: GPT-OSS 120B  
**Documents**: HAP Contract, OCAF Letter, MOR/NSPIRE  

**Targets**:
- HAP Contract: WA19M000067 (expires 2034)
- NSPIRE Score: 92
- MOR Score: 72
- HTF/HOME Loans: $950,000

### CATEGORY 3: RENT & OCCUPANCY
**Priority**: HIGH  
**Model**: GPT-OSS 20B  
**Documents**: OCAF Letter, Occupancy Report  

**Targets**:
- Contract Rent: $699/unit
- HAP Units: 55 of 60
- Occupancy Rate: Extract
- Utility Allowance: $0

### CATEGORY 4: PHYSICAL ASSET
**Priority**: MEDIUM  
**Model**: GPT-OSS 120B (chunked)  
**Documents**: Appraisal, CNA  

**Targets**:
- Property Value: Extract
- Capital Needs: 20-year projection
- Year Built: Extract
- Building Count: Extract

### CATEGORY 5: TRANSACTION DETAILS
**Priority**: HIGH  
**Model**: GPT-OSS 20B  
**Documents**: Audited Financials  

**Targets**:
- Owner: Riverside Charitable Corp
- Related Party Note: $428,067 @ 4.75%
- Sale Status: Closing 6/30/2025

## EXECUTION PHASES

### PHASE 1: RAPID EXTRACTION (4 hours)
```bash
# Deploy extractors in parallel
python3 fir_tree_extractor.py --category financial --model gpt-oss:20b
python3 fir_tree_extractor.py --category regulatory --model gpt-oss:120b
python3 fir_tree_extractor.py --category rent_occupancy --model gpt-oss:20b
```

### PHASE 2: VALIDATION (2 hours)
- Cross-reference Excel vs Audited Financials
- Verify HAP contract terms
- Validate compliance scores
- Check debt calculations

### PHASE 3: CONSOLIDATION (1 hour)
- Generate unified JSON output
- Calculate underwriting metrics
- Flag critical issues
- Prepare acquisition recommendation

## SUCCESS CRITERIA

✅ **Data Completeness**: 95%+ of required fields extracted  
✅ **Accuracy**: Cross-validation variance <5%  
✅ **Speed**: Complete extraction in <8 hours  
✅ **Quality**: Zero critical data conflicts  

## TOOLS & RESOURCES

**Models**:
- GPT-OSS 120B (complex documents)
- GPT-OSS 20B (standard extraction)
- Llama 3.3 70B (backup)

**Infrastructure**:
- IBM Docling (PDF parsing)
- xlwings (Excel extraction)
- Ollama (model management)

**Validation**:
- Claude (spot checks only)
- Cross-document verification
- Industry benchmarks

## RISK MITIGATION

**Risk 1**: Large PDF processing failure  
**Mitigation**: Chunk to 4000 tokens, use GPT-OSS 120B  

**Risk 2**: Financial data conflicts  
**Mitigation**: Prioritize audited statements, flag variances  

**Risk 3**: Missing critical data  
**Mitigation**: Define minimum viable dataset, escalate gaps  

## DELIVERABLES

**Primary**: Complete underwriting package (JSON)  
**Secondary**: Reusable HUD 202 extraction framework  
**Tertiary**: Validation rule library  

## COMMAND STRUCTURE

**Lead**: Strike Leader (orchestration)  
**Support**: Wingman (technical implementation)  
**QA**: Tower (validation oversight)  

## MISSION TIMELINE

**H+0**: Mission launch, parallel extraction  
**H+4**: Initial extraction complete  
**H+6**: Validation complete  
**H+8**: Final report delivered  

## AUTHORIZATION

This mission is authorized under the Colosseum Initiative to preserve affordable senior housing through strategic intelligence and superior execution.

**Roman Standard**: Built to Last 2000+ Years  
**Mission Motto**: *"Vincere Habitatio"* - To Conquer Housing  

---

**STATUS**: READY FOR EXECUTION  
**NEXT ACTION**: Deploy extraction framework

*End Mission Brief*