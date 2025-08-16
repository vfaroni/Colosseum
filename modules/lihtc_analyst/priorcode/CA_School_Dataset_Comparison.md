# California School Dataset Comparison for CTCAC Compliance

## Executive Summary

After analyzing both datasets against CTCAC QAP 2025 requirements, **CA_Public Schools (SchoolSites2324)** is the better choice for CTCAC compliance analysis, though it has limitations regarding community colleges.

## CTCAC Requirements for "Public School"

According to CTCAC QAP 2025 Section 10325(c)(4)(A), the following educational facilities are recognized for scoring:

1. **Public Elementary School** (K-5/6)
2. **Public Middle School** (6-8)
3. **Public High School** (9-12)
4. **Adult Education Campus of a School District**
5. **Community College**

## Dataset Analysis

### CA_Public Schools (SchoolSites2324)

**Source**: California Department of Education (CDE)
**Year**: 2023-24 school year
**Format**: Multiple formats (CSV, GeoJSON, Shapefile, GeoPackage)
**Total Records**: ~10,000 schools

**Strengths:**
- ✅ Comprehensive coverage of K-12 public schools
- ✅ Clear school type classification (Elementary, Middle, High)
- ✅ Includes Adult Education facilities (8 records found)
- ✅ Point-based geometry with lat/long coordinates
- ✅ Detailed attributes including enrollment, demographics, school status
- ✅ Active/Closed status tracking
- ✅ Charter school identification (can be filtered if needed)

**Weaknesses:**
- ❌ **Does NOT include Community Colleges** (0 records found)
- ❌ Includes non-CTCAC eligible schools (e.g., preschools, special education centers)

**School Types in Dataset:**
- Elementary: 5,838 schools
- Middle: 1,304 schools  
- High: 1,291 schools
- Alternative/Continuation: 782 schools
- Adult Education: 8 schools
- Other types: ~1,000 schools

### CA_School_Campus_Database (CSCD_2021)

**Source**: California School Campus Database
**Year**: 2021
**Format**: Geodatabase (.gdb)
**Coverage**: Claims to include K-12, community colleges, and universities

**Strengths:**
- ✅ Polygon boundaries (more accurate for proximity analysis)
- ✅ Claims to include community colleges and universities
- ✅ Assessed at parcel level for accuracy
- ✅ Includes charter school branches

**Weaknesses:**
- ❌ Older data (2021 vs 2023-24)
- ❌ Geodatabase format requires specialized GIS software
- ❌ Cannot verify school type classifications without opening in GIS
- ❌ Unknown if adult education is included
- ❌ May include universities (not CTCAC eligible)

## Recommendation for CTCAC Analysis

**Use CA_Public Schools (SchoolSites2324) as the primary dataset** with the following approach:

1. **Filter for CTCAC-eligible schools:**
   ```python
   # Include only CTCAC-eligible school types
   eligible_types = ['Elementary', 'Middle', 'High']
   eligible_levels = ['Elementary', 'Middle', 'High', 'Adult Education']
   
   # Filter dataset
   schools = schools[
       (schools['School Type'].isin(eligible_types)) |
       (schools['School Level'] == 'Adult Education')
   ]
   
   # Exclude special schools
   schools = schools[schools['School Type'] != 'Special Education']
   schools = schools[schools['Status'] == 'Active']
   ```

2. **Supplement with Community College data:**
   - Download California Community Colleges separately
   - Source: https://www.cccco.edu/ or California Community Colleges Chancellor's Office
   - Merge with the CA_Public Schools dataset

3. **Benefits of this approach:**
   - Most current data (2023-24)
   - Clear school type classification
   - Easy to filter for CTCAC requirements
   - CSV format is accessible without special software
   - Includes necessary attributes for analysis

## Key Considerations

1. **Charter Schools**: CTCAC regulations don't distinguish between traditional public and charter schools. The CA_Public Schools dataset includes a charter flag for filtering if needed.

2. **School Status**: Use only "Active" schools for analysis, as CTCAC requires schools to be operational.

3. **Grade Levels**: Use Grade Low/High fields to verify school classifications match CTCAC categories.

4. **Missing Community Colleges**: This is the main gap that needs to be addressed through supplemental data sources.

5. **Proximity Analysis**: While CSCD has polygon boundaries, point-based analysis from CA_Public Schools is sufficient for CTCAC's distance requirements (1/4 mile, 1/2 mile, 1 mile radii).

## Conclusion

CA_Public Schools provides the most comprehensive and current dataset for CTCAC compliance analysis, with clear school type classifications that align with regulatory requirements. The only significant gap is community colleges, which must be obtained separately.