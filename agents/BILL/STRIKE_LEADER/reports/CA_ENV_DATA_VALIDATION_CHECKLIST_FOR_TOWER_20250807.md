# ✅ CALIFORNIA ENVIRONMENTAL DATA VALIDATION CHECKLIST

**Document ID**: STRIKE-TOWER-VALIDATION-20250807  
**Mission**: CA Environmental Data Acquisition  
**Purpose**: Quality Assurance Framework for Tower Agent  
**Created By**: STRIKE LEADER  
**Date**: 2025-08-07  

---

## 📋 MASTER VALIDATION CHECKLIST

### 🗺️ FEMA FLOOD MAP VALIDATION

#### Coverage Validation
- [ ] **County Boundary Check**: Flood zones cover entire county area
- [ ] **No Gaps**: Verify no unmapped areas between zones
- [ ] **No Overlaps**: Ensure zones don't duplicate coverage
- [ ] **Edge Matching**: County boundaries align properly

#### Data Quality Checks
- [ ] **Zone Classifications**: Valid FEMA zone codes (A, AE, AH, AO, X, etc.)
- [ ] **BFE Values**: Base Flood Elevations are numeric and reasonable
- [ ] **FIRM Panel Dates**: Current within last 10 years
- [ ] **Coordinate System**: WGS84 (EPSG:4326) standardization

#### Sampling Requirements
- [ ] Sample 100 random parcels per county
- [ ] Cross-reference with FEMA official viewer
- [ ] Document discrepancies with screenshots
- [ ] Calculate accuracy percentage

**Acceptance Criteria**: ≥99% coverage, ≥98% accuracy

---

### 🏭 ENVIRONMENTAL SITE VALIDATION

#### EnviroStor (DTSC) Validation
- [ ] **Site Identifiers**: Unique Site_Code present
- [ ] **Location Accuracy**: Lat/Long within California bounds
- [ ] **Status Values**: Valid cleanup status codes
- [ ] **Address Completeness**: Street, City, ZIP populated
- [ ] **Contamination Data**: Potential contaminants listed

#### GeoTracker (SWRCB) Validation
- [ ] **Global IDs**: Unique identifiers present
- [ ] **Case Types**: Valid LUST/SLIC/Military designations
- [ ] **Status Codes**: Open/Closed/Verified classifications
- [ ] **Regulatory Programs**: Proper program assignments
- [ ] **Coordinates**: Validated against parcel boundaries

#### Cross-Database Checks
- [ ] **Duplicate Detection**: Same site in multiple databases
- [ ] **Distance Validation**: Sites plotted correctly on map
- [ ] **County Assignment**: Sites in correct counties
- [ ] **Data Freshness**: Update dates within 6 months

**Acceptance Criteria**: ≥95% completeness, ≥95% geocoding accuracy

---

### 📊 DATA COMPLETENESS MATRIX

| Database | Required Fields | Target Completeness | Critical Fields |
|----------|----------------|-------------------|-----------------|
| **FEMA Flood** | Zone, Subtype, SFHA | 100% | Zone designation |
| **EnviroStor** | ID, Status, Location | 95% | Coordinates |
| **GeoTracker** | ID, Type, Status | 95% | Case type |
| **EPA ECHO** | Facility, Violations | 90% | Facility ID |
| **CalGEM Wells** | API, Status, Location | 90% | Well status |

---

### 🎯 COUNTY-SPECIFIC VALIDATION

#### Tier 1 Counties (Priority)
**Los Angeles County**
- [ ] Minimum 50,000 flood zone polygons
- [ ] Minimum 2,000 environmental sites
- [ ] Beach/coastal flood zones present
- [ ] Urban contamination sites included

**San Diego County**
- [ ] Coastal flood zones mapped
- [ ] Military site contamination included
- [ ] Border area coverage complete
- [ ] Wildfire area intersections noted

**Orange County**
- [ ] Dense urban coverage verified
- [ ] Beach community flood zones
- [ ] Industrial contamination sites
- [ ] Newport Bay special zones

**San Francisco County**
- [ ] Bay waterfront flood zones
- [ ] Historic fill area sites
- [ ] Brownfield locations mapped
- [ ] Treasure Island special handling

**Alameda County**
- [ ] Oakland industrial sites
- [ ] Bay shoreline flooding
- [ ] Port contamination areas
- [ ] Berkeley/Richmond coverage

---

### 🔍 QUALITY SCORING FRAMEWORK

#### Scoring Methodology
```
Quality Score = (
    (Coverage × 0.25) +
    (Completeness × 0.25) +
    (Accuracy × 0.30) +
    (Freshness × 0.20)
) × 100
```

#### Score Interpretation
- **95-100**: Production Ready ✅
- **90-94**: Minor fixes needed ⚠️
- **85-89**: Significant gaps 🔶
- **<85**: Not acceptable ❌

---

### 📈 PERFORMANCE METRICS

#### Processing Performance
- [ ] Download speed ≥1 MB/s average
- [ ] API response time <2 seconds
- [ ] Processing time <5 min/county
- [ ] Memory usage <4GB peak

#### Data Volume Targets
- [ ] FEMA: 50K+ polygons total
- [ ] Environmental: 20K+ sites minimum
- [ ] Radon: All 58 CA counties
- [ ] Total size: <5GB compressed

---

### 🚨 CRITICAL VALIDATION POINTS

#### Legal/Compliance
- [ ] **Public Domain**: Data freely available
- [ ] **Attribution**: Sources properly credited
- [ ] **Commercial Use**: Permitted for business
- [ ] **PII Check**: No personal information
- [ ] **Copyright**: No proprietary content

#### Integration Testing
- [ ] **Parcel Matching**: Sites match parcel boundaries
- [ ] **Coordinate Systems**: All standardized to WGS84
- [ ] **Format Consistency**: JSON/GeoJSON/CSV validated
- [ ] **API Compatibility**: Works with existing systems
- [ ] **Query Performance**: <100ms response time

---

### 📝 VALIDATION REPORTING TEMPLATE

```markdown
## County Validation Report

**County**: [Name]
**Date Validated**: [Date]
**Validator**: TOWER

### Coverage Metrics
- Geographic Coverage: XX%
- Population Coverage: XX%
- Parcel Coverage: XX%

### Data Quality
- Completeness Score: XX%
- Accuracy Score: XX%
- Freshness: Last updated [Date]

### Issues Found
1. [Issue description]
2. [Issue description]

### Recommendations
- [Action item]
- [Action item]

### Certification
[ ] APPROVED for production
[ ] CONDITIONAL approval with fixes
[ ] REJECTED - requires rework
```

---

### 🎯 ACCEPTANCE CRITERIA SUMMARY

#### Minimum Requirements for Production
1. **Coverage**: 95%+ of county area
2. **Accuracy**: 95%+ coordinate precision
3. **Completeness**: 90%+ required fields
4. **Freshness**: Data <6 months old
5. **Integration**: Successful parcel matching
6. **Performance**: Meeting speed targets
7. **Legal**: All compliance checks passed

#### Stop Conditions
- Coverage <90% → STOP and investigate
- Accuracy <90% → STOP and recalibrate
- Critical fields missing → STOP and fix
- Legal issues identified → STOP immediately

---

### 🔄 VALIDATION WORKFLOW

1. **Initial Receipt** (from Wingman)
   - Log receipt time and file sizes
   - Verify file integrity (checksums)
   - Check format compatibility

2. **Automated Validation** (Scripts)
   - Run completeness checks
   - Execute accuracy tests
   - Generate coverage maps

3. **Manual Sampling** (Tower)
   - Review 100 random records
   - Spot-check problem areas
   - Verify edge cases

4. **Report Generation**
   - Complete validation report
   - Calculate quality scores
   - Document recommendations

5. **Certification Decision**
   - Approve/Conditional/Reject
   - Communicate to Strike Leader
   - Track fixes if needed

---

## ✅ READY FOR TOWER EXECUTION

This comprehensive validation checklist provides Tower with clear quality criteria, scoring methodology, and acceptance thresholds for California environmental data validation.

**Next Step**: Tower to implement validation framework while awaiting first data delivery from Wingman.

---

*"Quality Through Systematic Validation"*

**STRIKE LEADER - Mission Command**  
Colosseum LIHTC Platform