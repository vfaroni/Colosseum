# QCT/DDA Mapping Guidance for 5-Site Analysis - CRITICAL UPDATE

## 🚨 URGENT: Use Updated Comprehensive Analyzer

**Critical Change**: The QCT/DDA analysis system has been completely corrected with industry-standard methodology. You MUST use the new `comprehensive_qct_dda_analyzer.py` for accurate results.

## Background: What Was Wrong

The previous analysis was missing critical data and using incorrect industry logic:

1. **Missing Non-Metro DDA Data**: Only had Metro DDAs, missing county-level Non-Metro DDAs
2. **Incomplete QCT Coverage**: Missing Non-Metro QCT designations
3. **Wrong Industry Logic**: Not properly handling dual QCT+DDA designations
4. **Incorrect AMI Sources**: Not distinguishing Metro vs Non-Metro AMI sources

## Critical Example: United Church Village (Nogales, AZ)

**BEFORE (Incorrect)**: "QCT-only"
**AFTER (Industry Accurate)**: "Non-Metro QCT + DDA"

This demonstrates why ALL 5 sites need re-analysis with the corrected system.

## How to Use the Updated Analyzer

### 1. Import the Correct Module
```python
from comprehensive_qct_dda_analyzer import ComprehensiveQCTDDAAnalyzer

# Initialize with complete US datasets
analyzer = ComprehensiveQCTDDAAnalyzer()
```

### 2. Analyze Each Property
```python
# For each of your 5 properties
lat, lon = 33.4484, -112.0740  # Your property coordinates
result = analyzer.lookup_qct_status(lat, lon)

# Key results to extract:
classification = result['industry_classification']  # e.g., "Non-Metro QCT + DDA"
basis_boost = result['basis_boost_eligible']        # True/False for 130% boost
ami_source = result['ami_source']                   # "Regional MSA AMI" or "County AMI"
metro_status = result['metro_status']               # "Metro" or "Non-Metro"
```

### 3. Industry-Standard Classifications

The corrected system returns these industry-accurate classifications:

- **"Metro QCT"** - Metro area QCT designation
- **"Metro DDA"** - Metro area DDA designation  
- **"Metro QCT + DDA"** - Metro area with both designations
- **"Non-Metro QCT"** - Non-Metro area QCT designation
- **"Non-Metro DDA"** - Non-Metro area DDA designation
- **"Non-Metro QCT + DDA"** - Non-Metro area with both designations
- **"No QCT/DDA"** - No qualifying designations

### 4. Complete Data Coverage

The updated system includes all 4 HUD datasets:

- **Metro DDAs**: 2,612 ZIP areas across 640 metro areas
- **Metro QCTs**: 7,519 census tracts
- **Non-Metro DDAs**: 105 counties across 33 states
- **Non-Metro QCTs**: 983 census tracts

## Arizona-Specific Corrections

### Non-Metro DDA Counties (6 total):
- Apache County
- Gila County  
- Graham County
- La Paz County
- Navajo County
- **Santa Cruz County** (was missing in previous analysis)

### Expected Results for Your 5 Sites:

Based on the comprehensive solution document, you should expect:

1. **Mt. Graham (Safford)**: "No QCT/DDA" - Graham County Non-Metro
2. **Safford Villa (Safford)**: "No QCT/DDA" - Graham County Non-Metro
3. **Willcox Villa (Willcox)**: "No QCT/DDA" - Cochise County Metro
4. **Cochise Apts (Benson)**: "No QCT/DDA" - Cochise County Metro
5. **United Church Village (Nogales)**: **"Non-Metro QCT + DDA"** - Santa Cruz County Non-Metro

## Mapping Requirements

### 1. Update All Property Markers
Each property marker should display:
```
Property Name
Industry Classification: [Metro/Non-Metro QCT/DDA/QCT + DDA/No QCT/DDA]
AMI Source: [Regional MSA AMI / County AMI]
Basis Boost Eligible: [Yes - 130% / No]
```

### 2. Legend Updates
Update your map legend to show:
- **QCT Areas**: Census tract boundaries (where available)
- **Metro DDA Areas**: ZIP code boundaries (for metro areas)
- **Non-Metro DDA Counties**: County boundaries (for rural areas)
- **Metro vs Non-Metro**: Clear visual distinction

### 3. Color Coding Recommendations
- **Green**: QCT or DDA qualified areas
- **Blue**: Dual QCT + DDA areas (premium qualification)
- **Gray**: No QCT/DDA designation
- **Border Colors**: Metro (solid) vs Non-Metro (dashed)

## Technical Implementation

### 1. Batch Analysis
```python
properties = [
    {"name": "Mt. Graham", "lat": 32.7016, "lon": -109.8710},
    {"name": "Safford Villa", "lat": 32.8340, "lon": -109.7073},
    {"name": "Willcox Villa", "lat": 32.2532, "lon": -109.8320},
    {"name": "Cochise Apts", "lat": 31.9590, "lon": -110.2943},
    {"name": "United Church Village", "lat": 31.3713, "lon": -110.9240}
]

results = []
for prop in properties:
    result = analyzer.lookup_qct_status(prop['lat'], prop['lon'])
    results.append({
        'name': prop['name'],
        'classification': result['industry_classification'],
        'basis_boost': result['basis_boost_eligible'],
        'ami_source': result['ami_source'],
        'metro_status': result['metro_status']
    })

# Generate updated map with corrected classifications
```

### 2. Data Validation
Verify each result by checking:
- **United Church Village**: MUST show "Non-Metro QCT + DDA"
- **Santa Cruz County properties**: Should be Non-Metro DDA
- **Graham County properties**: Should be Non-Metro (no DDA per HUD data)
- **Cochise County properties**: Should be Metro (no QCT/DDA per analysis)

## Business Impact

### Portfolio Summary (Corrected):
- **Qualification Rate**: 20% of properties (1/5), 30% of units (48/160)
- **Only United Church Village qualifies** for 130% basis boost
- **Critical**: Previous analysis may have missed this qualification entirely

### Client Communication:
- **Accurate Classifications**: Use industry-standard terminology
- **AMI Source Clarity**: Specify Regional MSA vs County AMI for underwriting
- **Compliance Assurance**: Based on complete HUD 2025 official datasets

## Quality Assurance Checklist

Before finalizing your 5-site map:

- [ ] All 5 properties analyzed with `comprehensive_qct_dda_analyzer.py`
- [ ] United Church Village shows "Non-Metro QCT + DDA"
- [ ] Industry classifications use proper terminology
- [ ] AMI sources correctly assigned (Metro vs Non-Metro)
- [ ] Map legend reflects all 4 HUD dataset types
- [ ] Color coding distinguishes Metro vs Non-Metro areas
- [ ] Property markers show complete qualification details

## Files to Reference

- **Analyzer**: `comprehensive_qct_dda_analyzer.py` (use this version only)
- **Data Sources**: All files in `/Data_Sets/federal/HUD_QCT_DDA_Data/`
- **Solution Document**: `QCT_DDA_ANALYSIS_COMPREHENSIVE_SOLUTION.md`
- **Updated CLAUDE.md**: Contains complete system documentation

---

**CRITICAL**: Do not use any previous QCT/DDA analysis results. The corrected system provides industry-accurate classifications that align with HUD official data and LIHTC industry standards.