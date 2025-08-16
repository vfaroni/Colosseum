# GEOCODING ACCURACY CONTRACT

**Effective Date**: July 22, 2025  
**Purpose**: Prevent coordinate accuracy errors in LIHTC site analysis

## MANDATORY GEOCODING REQUIREMENTS

This contract establishes binding requirements for ALL location-based analyses in the CALIHTCScorer system.

### ARTICLE 1: ABSOLUTE PROHIBITION ON APPROXIMATE COORDINATES

**1.1 NO APPROXIMATIONS ALLOWED**  
- ❌ NEVER use "general area" coordinates for a specific address
- ❌ NEVER use city center coordinates as a proxy for a street address
- ❌ NEVER proceed with analysis using "close enough" coordinates

**1.2 PRECISE COORDINATES ONLY**  
- ✅ ALWAYS obtain exact GPS coordinates for the specific street address
- ✅ ALWAYS verify coordinates match the intended property location
- ✅ ALWAYS use professional geocoding services (Google Maps API, Mapbox, etc.)

### ARTICLE 2: MANDATORY GEOCODING WORKFLOW

**2.1 REQUIRED STEPS** (NO EXCEPTIONS)

**CRITICAL REQUIREMENT**: Coordinate lookup MUST be completed BEFORE any analysis begins. No exceptions.

1. **Input Validation**
   - Verify complete address: Street number, street name, city, state, ZIP
   - Flag any ambiguous or incomplete addresses

2. **Geocoding Service** (MUST COMPLETE FIRST)
   - Use authorized geocoding API
   - Store raw geocoding response for audit trail
   - Verify geocoding confidence score > 0.8
   - Display exact coordinates to user for confirmation

3. **Coordinate Verification**
   - Cross-reference with multiple sources when possible
   - Validate coordinates fall within expected city/county boundaries
   - Check for geocoding warnings or partial matches

4. **Pre-Analysis Gate**
   - STOP: Do not proceed to any analysis until coordinates are confirmed
   - Display coordinates to user: "Will analyze site at: [lat, lon]"
   - Allow user to correct if needed

5. **Error Handling**
   - If exact match not found, STOP analysis
   - Request clarification from user
   - Document geocoding failures

### ARTICLE 3: VALIDATION REQUIREMENTS

**3.1 MANDATORY CHECKS**
```python
def validate_geocoding_accuracy(address, coordinates, geocoding_response):
    # REQUIRED: All checks must pass
    assert geocoding_response['match_type'] == 'exact'
    assert geocoding_response['confidence'] >= 0.8
    assert coordinates_within_city_bounds(coordinates, address['city'])
    assert no_ambiguous_matches(geocoding_response)
```

**3.2 RED FLAGS REQUIRING IMMEDIATE STOP**
- Multiple possible matches
- Partial address matches
- Low confidence scores
- Coordinates outside expected jurisdiction
- User indicates results don't match expectations

### ARTICLE 4: DOCUMENTATION REQUIREMENTS

**4.1 AUDIT TRAIL**
Every analysis MUST document:
- Original address input
- Geocoding service used
- Raw geocoding response
- Final coordinates selected
- Validation checks performed
- Any user corrections

**4.2 TRANSPARENCY**
Always display to user:
- Exact coordinates being analyzed
- Source of coordinates
- Confidence level
- Option to correct if wrong

### ARTICLE 5: CONSEQUENCES OF VIOLATION

**5.1 IMMEDIATE ACTIONS**
- Analysis results are VOID
- Must restart with proper geocoding
- Document the error for prevention

**5.2 SYSTEM IMPROVEMENTS**
- Add geocoding validation to pre-analysis checks
- Implement coordinate confidence warnings
- Create geocoding best practices guide

### ARTICLE 6: IMPLEMENTATION CHECKLIST

- [ ] Integrate professional geocoding API
- [ ] Add coordinate validation module
- [ ] Create geocoding confidence metrics
- [ ] Implement user confirmation step
- [ ] Add coordinate audit logging
- [ ] Build coordinate correction workflow
- [ ] Document geocoding standards

## AGREEMENT

This contract represents a commitment to absolute precision in location-based analysis. Opportunity areas, QCT boundaries, and amenity distances can vary dramatically within small geographic areas. 

**There is no acceptable margin of error when it comes to property coordinates.**

## ENFORCEMENT

This contract shall be referenced in:
- CLAUDE.md (AI instructions)
- Code review checklists
- Testing procedures
- User documentation

---

**Remember**: In LIHTC analysis, being off by even 0.001 degrees can mean the difference between a Highest Resource and Moderate Resource area, potentially changing project viability. Precision is not optional—it's mandatory.