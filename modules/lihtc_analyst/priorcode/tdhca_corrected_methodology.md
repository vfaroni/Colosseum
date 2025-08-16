# CORRECTED: TDHCA 4% and 9% LIHTC Analysis Methodology

## Critical Corrections to Current Approach

### Problem with Current System
1. **QCT/DDA treated as scoring factor** → Should be **BINARY REQUIREMENT**
2. **Mixed 4% and 9% rules** → Need **SEPARATE ANALYSIS PATHS**
3. **40%/60% weighting wrong** → Should be **SEQUENTIAL FILTERS**
4. **Unknown TDHCA scoring** → Need **ACTUAL TDHCA POINT SYSTEM**

## Corrected Analysis Flow

### Step 1: Federal Eligibility Filter (BINARY - REQUIRED)
```
IF (QCT_Status = TRUE) OR (DDA_Status = TRUE):
    Federal_Basis_Boost = 30%
    Proceed to Step 2
ELSE:
    Property Status = INELIGIBLE
    STOP ANALYSIS
```

**Result**: Currently all 165 properties pass this filter

### Step 2: Deal Type Determination
```
User selects analysis type:
- 4% Tax-Exempt Bond Analysis
- 9% Competitive Tax Credit Analysis
- Both (separate results)
```

### Step 3A: 4% Tax-Exempt Bond Rules

**Competition Rules for 4% Deals**:
```
FATAL FLAW CHECK:
- One Mile Three Year Rule: No LIHTC project within 1 mile in last 3 years
- (Confirm: Are there additional 4% specific rules?)

SCORING FACTORS:
- Market need demonstration
- Local government support
- Site control requirements
- (Need to research actual 4% scoring criteria)
```

### Step 3B: 9% Competitive Tax Credit Rules

**Competition Rules for 9% Deals**:
```
FATAL FLAW CHECKS:
- One Mile Three Year Rule: No LIHTC project within 1 mile in last 3 years
- Two Mile Same Year Rule: (Large counties only - Harris, Dallas, Tarrant, Bexar, Travis)
  IF 9% project within 2 miles in same application year: FATAL FLAW

TDHCA SCORING POINTS:
- Same Census Tract: Points based on years since last project
- Opportunity Index: (Need to research - is this real?)
- Other TDHCA scoring factors: (Need official QAP)
```

### Step 4: Economic Viability Analysis
**Only run on properties that pass fatal flaw checks**

### Step 5: Combined Ranking
```
FOR properties without fatal flaws:
Final Score = TDHCA_Points + Economic_Viability_Bonus
```

## Key Questions We Need to Answer

### 1. TDHCA 9% Scoring System
**Question**: What are the actual TDHCA 9% competitive scoring criteria?
- Same Census Tract points (0-5 points based on years?)
- Opportunity Index (real or estimated?)
- Other location-based scoring factors?

### 2. TDHCA 4% Requirements  
**Question**: Do 4% tax-exempt bond deals have scoring criteria or just compliance?
- Different competition rules?
- Different proximity requirements?
- Market study requirements?

### 3. Flood Zone Impact
**Question**: Does TDHCA penalize flood zones in official scoring?
- AE/VE zones = point deductions?
- Or purely economic impact (insurance costs)?

### 4. Large County Rules
**Question**: Confirm large county list and specific rules
- Current list: Harris, Dallas, Tarrant, Bexar, Travis
- Two Mile Same Year rule applies to which deal types?

## Immediate Action Items

### 1. Research TDHCA QAP Documents
Need to find official Texas QAP for:
- 9% competitive scoring matrix
- 4% tax-exempt bond requirements  
- Flood zone treatment
- Exact competition rules by deal type

### 2. Verify Competition Rules
Current understanding to verify:
- **4% Deals**: One Mile Three Year Rule only?
- **9% Deals**: One Mile Three Year + Two Mile Same Year (large counties)

### 3. Create Separate Analysis Paths
```python
def analyze_4pct_deals(properties):
    # Apply 4% specific filters and scoring
    pass

def analyze_9pct_deals(properties):  
    # Apply 9% specific filters and scoring
    pass
```

### 4. Fix Scoring Weights
Instead of arbitrary 40%/60%:
```
Step 1: Binary eligibility (QCT/DDA)
Step 2: Fatal flaw elimination  
Step 3: TDHCA scoring points (official system)
Step 4: Economic viability as tiebreaker/secondary factor
```

## Sample Corrected Output Structure

### 4% Tax-Exempt Bond Analysis
```
Total Properties: 165
QCT/DDA Eligible: 165 (100%)
Pass 4% Competition Rules: XX properties
Economic Analysis: Top XX by revenue potential
Final Recommendations: Top 25 ranked by [TDHCA criteria + economics]
```

### 9% Competitive Analysis  
```
Total Properties: 165
QCT/DDA Eligible: 165 (100%)  
Pass 9% Competition Rules: XX properties
TDHCA Scoring Analysis: Points by same census tract, etc.
Economic Analysis: Revenue potential for scoring properties
Final Recommendations: Top 25 by total TDHCA points + economic bonus
```

## Next Steps

1. **Research Phase**: Get actual TDHCA QAP requirements
2. **Methodology Update**: Separate 4% and 9% analysis paths
3. **Scoring Correction**: Implement real TDHCA point system
4. **Economic Integration**: Use economics as enhancement, not primary factor
5. **Validation**: Test against known successful LIHTC projects

**Bottom Line**: We need to flip from "economic-first" to "TDHCA compliance-first" with economics as the optimization layer.