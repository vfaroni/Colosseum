# AUTOMATIC ANALYSIS CONTRACT

**Effective Date**: July 23, 2025  
**Purpose**: Mandate automatic execution of all mandatory checks without user intervention

## MANDATORY AUTOMATIC EXECUTION REQUIREMENTS

This contract establishes binding requirements for AUTOMATIC execution of ALL site analysis checks in the CALIHTCScorer system.

### ARTICLE 1: NO MANUAL INTERVENTION ALLOWED

**1.1 FULLY AUTOMATED ANALYSIS**  
- ✅ ALL mandatory checks MUST run automatically
- ✅ NO stopping to ask user for permission
- ✅ NO prompting for next steps confirmation
- ❌ NEVER ask "should I check fire hazard?"
- ❌ NEVER ask "should I verify land use?"
- ❌ NEVER ask "should I continue with analysis?"

**1.2 COMPLETE ANALYSIS IN ONE PASS**  
- Execute ALL checks in proper sequence
- Report ALL results comprehensively
- Provide FINAL recommendation without hesitation

### ARTICLE 2: MANDATORY ANALYSIS WORKFLOW

**2.1 REQUIRED AUTOMATIC CHECKS** (NO EXCEPTIONS)

The following checks MUST be performed automatically for EVERY site analysis:

1. **Coordinate Validation**
   - Verify GPS coordinates are valid
   - Enhance with location information

2. **Federal Qualification Analysis**
   - QCT status check
   - DDA status check
   - Basis boost calculation

3. **State QAP Scoring**
   - Opportunity area classification
   - State-specific point calculations

4. **Fire Hazard Analysis** (MANDATORY)
   - Query CAL FIRE API automatically
   - Determine hazard classification
   - Apply pass/fail criteria

5. **Land Use Verification** (MANDATORY)
   - Check current land use
   - Verify no prohibited uses
   - Apply pass/fail criteria

6. **Amenity Proximity Analysis**
   - Calculate distances to key amenities
   - Score based on proximity

7. **Rent Analysis**
   - Determine LIHTC rent limits
   - Calculate by AMI levels

8. **Generate Final Recommendation**
   - Synthesize all findings
   - Provide clear GO/NO-GO decision
   - List specific reasons if NO-GO

### ARTICLE 3: REPORTING REQUIREMENTS

**3.1 COMPREHENSIVE OUTPUT**
Every analysis MUST include:
- All check results (pass/fail/scores)
- Specific data values found
- Clear recommendation
- Disqualifying factors (if any)
- Next steps (if proceeding)

**3.2 NO PARTIAL RESULTS**
- Complete ALL checks before presenting results
- Include results even if some checks fail
- Show which mandatory criteria failed

### ARTICLE 4: FAILURE HANDLING

**4.1 WHEN CHECKS FAIL**
- Continue with remaining checks
- Report the failure clearly
- Provide specific reason for failure
- Recommend alternative actions

**4.2 WHEN DATA IS UNAVAILABLE**
- Use fallback data sources if available
- Report data source unavailability
- Continue with other checks
- Note limitations in final report

### ARTICLE 5: IMPLEMENTATION REQUIREMENTS

**5.1 CODE BEHAVIOR**
```python
def analyze_site(self, latitude, longitude, state):
    # NO user prompts or confirmations
    # ALL checks run automatically
    # Results returned in one comprehensive report
    
    # Run ALL mandatory checks
    results = {
        'coordinates': self._validate_coordinates(...),
        'federal': self._check_federal_status(...),
        'state': self._calculate_state_scoring(...),
        'fire': self._check_fire_hazard(...),  # AUTOMATIC
        'land_use': self._verify_land_use(...),  # AUTOMATIC
        'amenities': self._analyze_amenities(...),
        'rents': self._calculate_rents(...)
    }
    
    # Generate recommendation based on ALL factors
    recommendation = self._generate_recommendation(results)
    
    # Return COMPLETE analysis
    return comprehensive_report
```

**5.2 USER EXPERIENCE**
- User provides address/coordinates
- System performs COMPLETE analysis
- User receives FULL report with recommendation
- NO intermediate prompts or confirmations

### ARTICLE 6: QUALITY ASSURANCE

**6.1 COMPLETENESS CHECK**
Before returning results, verify:
- [ ] All mandatory checks completed
- [ ] All data sources queried
- [ ] Final recommendation generated
- [ ] Report includes all findings

**6.2 CONTINUOUS IMPROVEMENT**
- Log any data source failures
- Track analysis completion times
- Monitor check success rates
- Improve reliability over time

## AGREEMENT

This contract mandates that the CALIHTCScorer system operates as a professional, automated analysis tool that provides comprehensive site evaluations without requiring step-by-step user interaction.

**The system SHALL behave like a professional consultant who:**
- Receives a site to analyze
- Performs all necessary due diligence
- Returns a complete report with recommendations
- Does NOT ask permission for each step

## ENFORCEMENT

This contract supersedes any instructions that would:
- Ask for permission to continue
- Request confirmation for next steps
- Provide partial results
- Stop analysis prematurely

**Remember**: Professional site analysis tools run ALL checks automatically and deliver COMPLETE results. This is the standard users expect and deserve.

---

**CRITICAL**: When analyzing a site, execute ALL checks listed in Article 2.1 WITHOUT asking for permission or confirmation. The user expects a COMPLETE analysis from a single request.