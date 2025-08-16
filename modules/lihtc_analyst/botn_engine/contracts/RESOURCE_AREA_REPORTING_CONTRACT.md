# RESOURCE AREA REPORTING CONTRACT

**Effective Date**: July 23, 2025  
**Purpose**: Mandate clear and accurate reporting of California CTCAC Opportunity Area resource classifications

## MANDATORY RESOURCE AREA DISCLOSURE REQUIREMENTS

This contract establishes binding requirements for CLEAR and ACCURATE reporting of resource area classifications in ALL site analyses.

### ARTICLE 1: MANDATORY RESOURCE AREA REPORTING

**1.1 REQUIRED DISCLOSURE**  
Every site analysis MUST clearly report the California CTCAC Opportunity Area resource classification with the following information:

- ✅ **ALWAYS show exact resource category** (Highest, High, Moderate, Low, or Not in Opportunity Area)
- ✅ **ALWAYS show CTCAC points awarded** (8, 6, 4, 0, or 0 respectively)
- ✅ **ALWAYS show data source used** (final_opp_2025_public.gpkg)
- ✅ **ALWAYS show confidence level** of the determination

**1.2 PROHIBITED RESPONSES**
- ❌ NEVER report "Unknown" without attempting lookup
- ❌ NEVER report "Not determined" without explanation
- ❌ NEVER omit resource area information
- ❌ NEVER report generic "opportunity area" without specific classification

### ARTICLE 2: REQUIRED OUTPUT FORMAT

**2.1 STANDARD REPORTING FORMAT**
Every analysis MUST include this exact format:

```
🏆 CALIFORNIA CTCAC RESOURCE AREA CLASSIFICATION:
   Category: [Highest Resource | High Resource | Moderate Resource | Low Resource | Not in Opportunity Area]
   Points Awarded: [8 | 6 | 4 | 0]/8
   Confidence: [High | Medium | Low]
   Data Source: CTCAC 2025 Opportunity Maps
   Determination Method: [Spatial intersection | Manual lookup | API query]
```

**2.2 SPECIFIC CLASSIFICATIONS**

- 🥇 **"Highest Resource"** - 8 points
  - Premium locations with excellent schools, low poverty, high employment
  - Maximum CTCAC opportunity area points

- 🥈 **"High Resource"** - 6 points  
  - Strong locations with good schools, moderate poverty, solid employment
  - High CTCAC opportunity area points

- 🥉 **"Moderate Resource"** - 4 points
  - Acceptable locations with average schools, mixed demographics
  - Moderate CTCAC opportunity area points

- 📍 **"Low Resource"** - 0 points
  - Standard locations within opportunity area boundaries but lower scoring
  - Minimum CTCAC opportunity area points

- ❓ **"Not in Opportunity Area"** - 0 points
  - Site falls outside any designated CTCAC opportunity area
  - Must rely on other scoring categories for points

### ARTICLE 3: DATA SOURCE REQUIREMENTS

**3.1 PRIMARY DATA SOURCE**
- **File**: `final_opp_2025_public.gpkg`
- **Location**: `/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets/california/CA_CTCAC_2025_Opp_MAP_shapefile/`
- **Fields to Query**:
  - `oppcat`: Opportunity category (Highest/High/Moderate/Low Resource)
  - `oppscore`: Numerical opportunity score
  - `fips`: Census tract FIPS code for joining

**3.2 BACKUP DATA SOURCES**
If primary source fails:
1. **Alternative File**: `HQTA_CTCAC_Intersected.geojson`
2. **API Fallback**: CTCAC web services (if available)
3. **Manual Lookup**: TCAC/HCD opportunity area maps website

### ARTICLE 4: IMPLEMENTATION REQUIREMENTS

**4.1 ANALYSIS WORKFLOW**
```python
def determine_resource_area(latitude, longitude):
    # REQUIRED: Attempt spatial intersection
    try:
        gdf = gpd.read_file(OPPORTUNITY_AREA_FILE)
        point = Point(longitude, latitude)
        intersects = gdf[gdf.contains(point)]
        
        if not intersects.empty:
            category = intersects.iloc[0]['oppcat']
            score = intersects.iloc[0]['oppscore']
            return {
                'category': category,
                'points': POINTS_MAPPING[category],
                'confidence': 'High',
                'method': 'Spatial intersection'
            }
        else:
            return {
                'category': 'Not in Opportunity Area',
                'points': 0,
                'confidence': 'High',
                'method': 'Spatial intersection'
            }
    except Exception as e:
        # REQUIRED: Report error and attempt fallback
        return {
            'category': 'Error - Could not determine',
            'points': None,
            'confidence': 'None',
            'error': str(e),
            'method': 'Failed'
        }
```

**4.2 ERROR HANDLING**
When resource area cannot be determined:
- Report the specific error encountered
- List troubleshooting steps attempted
- Provide manual lookup instructions
- Flag for manual review

### ARTICLE 5: QUALITY ASSURANCE

**5.1 VALIDATION CHECKS**
Before returning results, verify:
- [ ] Resource category is one of the 5 valid values
- [ ] Points awarded match the category (8/6/4/0/0)
- [ ] Confidence level is reported
- [ ] Data source is documented
- [ ] Method used is specified

**5.2 SPOT CHECKING**
Periodically validate with known locations:
- **Highest Resource Test**: Beverly Hills, CA (should be Highest)
- **High Resource Test**: Manhattan Beach, CA (should be High)
- **Not in Area Test**: Rural locations (should be Not in Opportunity Area)

### ARTICLE 6: USER COMMUNICATION

**6.1 CLEAR EXPLANATIONS**
Always explain what the resource area classification means:
- Impact on CTCAC scoring
- Competitive implications
- Requirements for different resource areas

**6.2 ACTIONABLE GUIDANCE**
For each classification, provide:
- **Highest/High Resource**: "Excellent location for LIHTC development"
- **Moderate Resource**: "Good location with solid scoring potential"
- **Low Resource**: "Acceptable location but limited opportunity area points"
- **Not in Area**: "Must excel in other scoring categories to be competitive"

## AGREEMENT

This contract ensures that users always receive clear, accurate information about California CTCAC Opportunity Area classifications, which are critical for LIHTC application success.

**Resource area classification directly impacts**:
- CTCAC point scoring (0-8 points)
- Competitive positioning
- Development feasibility
- Application strategy

## ENFORCEMENT

This contract SHALL be implemented by:
- [ ] Updating QAP analyzer to always report resource areas
- [ ] Adding resource area validation to analysis pipeline
- [ ] Creating resource area lookup troubleshooting guide
- [ ] Testing with known resource area locations

---

**CRITICAL**: Every site analysis MUST include a clear, definitive statement about the CTCAC Opportunity Area resource classification. "Unknown" is not an acceptable answer without a clear explanation of why the determination could not be made.