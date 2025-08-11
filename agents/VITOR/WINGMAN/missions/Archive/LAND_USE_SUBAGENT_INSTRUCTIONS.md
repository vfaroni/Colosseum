# 🏗️ SUB-AGENT INSTRUCTIONS: LAND USE ANALYZER DEVELOPMENT
## MISSION: VITOR-WINGMAN-LANDUSE-001

**Target Sub-Agent**: Any available Colosseum agent  
**Priority**: Critical (Phase 6 of BOTN filtering system)  
**Coordination**: VITOR-WINGMAN primary mission support  
**Expected Duration**: 2-3 weeks  

---

## 🎯 MISSION CONTEXT

**Primary Mission**: VITOR-WINGMAN is executing comprehensive BOTN filtering system on 2,676 LIHTC sites. The land use analyzer is **Phase 6 (final filtering step)** that eliminates sites with prohibited uses incompatible with residential LIHTC development.

**Business Critical**: This component completes the 4-mandatory-criteria BOTN system, creating production-ready LIHTC site screening platform with competitive advantage.

**Integration Requirement**: Must integrate seamlessly with existing BOTN pipeline and deliver results in format compatible with current elimination logic.

---

## 📂 STARTING DIRECTORY

**Primary Working Directory**:
```
/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/botn_engine/src/analyzers/
```

**Key Integration Points**:
- **Main Pipeline**: `/modules/lihtc_analyst/botn_engine/src/core/site_analyzer.py`
- **Existing Analyzers**: Review other `*_analyzer.py` files for patterns
- **Test Framework**: `/modules/lihtc_analyst/botn_engine/tests/`
- **Data Sources**: `/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets/`

---

## 🎯 DELIVERABLE REQUIREMENTS

### **Primary Deliverable**: `land_use_analyzer.py`

**Required Class Structure**:
```python
class LandUseAnalyzer:
    def __init__(self):
        self.prohibited_uses = [
            "agriculture", 
            "industrial", 
            "auto",  # Auto dealerships
            "gas_station", 
            "dry_cleaning"
        ]
    
    def verify_acceptable_use(self, latitude: float, longitude: float, site_address: str = "") -> dict:
        """
        Verify site has acceptable land use for LIHTC development
        
        Returns:
        {
            "acceptable_use": bool,           # True if site is acceptable
            "current_use": str,              # Detected current use
            "prohibited_use_found": str,     # Specific prohibited use (if any)
            "data_source": str,              # Source of land use data
            "confidence": str,               # "High", "Medium", "Low"
            "requires_manual_verification": bool,
            "analysis_notes": str
        }
        """
```

### **Integration Format**:
**Must match existing analyzer patterns**. Study these files:
- `qct_dda_analyzer.py` (coordinates → qualification result)
- `fire_hazard_analyzer.py` (coordinates → risk assessment)

---

## 🔍 RESEARCH REQUIREMENTS

### **Phase 1: Data Source Research (Week 1)**

**Investigate These Data Sources**:

1. **County Assessor Databases**
   - **Focus**: Property use codes and descriptions
   - **Coverage**: California counties (primary focus)
   - **APIs**: Research county-specific assessor APIs

2. **CoStar/Commercial Property Data**
   - **Existing**: CoStar data already in our dataset
   - **Analysis**: Check existing dataset columns for current use data
   - **Column Names**: Look for "Property Type", "Current Use", "Land Use", etc.

3. **Zoning Data APIs**
   - **Municipal**: City/county zoning databases
   - **State**: California statewide zoning data
   - **APIs**: Research available zoning web services

4. **Google Places API / Similar**
   - **Business Types**: Detect current business operations
   - **Categories**: Map business categories to prohibited uses
   - **Limitations**: May not cover all property types

**Expected Research Output**: Document of available data sources with:
- API endpoints and access requirements
- Data quality and coverage assessment  
- Cost analysis (free vs paid services)
- Accuracy testing on known sites

### **Phase 2: Implementation Priority**

**Recommended Implementation Order**:
1. **Existing Dataset Analysis**: Check current CoStar data for use information
2. **County Assessor APIs**: Most authoritative for property use
3. **Google Places/Business APIs**: Fill gaps for commercial properties
4. **Zoning Data**: Backup/validation source

---

## 🧪 TESTING REQUIREMENTS

### **Test Sites for Validation**

**Known Prohibited Use Sites** (for accuracy testing):
```python
prohibited_test_sites = [
    {
        "address": "[Research: Known gas station address in CA]",
        "lat": "[latitude]", 
        "lng": "[longitude]",
        "expected_use": "gas_station",
        "should_eliminate": True
    },
    {
        "address": "[Research: Known agricultural land in CA]", 
        "lat": "[latitude]",
        "lng": "[longitude]", 
        "expected_use": "agriculture",
        "should_eliminate": True
    }
    # Add more test cases for each prohibited use
]
```

**Known Acceptable Sites**:
```python
acceptable_test_sites = [
    {
        "address": "Residential area in high resource zone",
        "expected_use": "residential", 
        "should_eliminate": False
    }
]
```

### **Required Test Coverage**
- **90%+ accuracy** on prohibited use detection
- **No false positives** (acceptable sites incorrectly flagged)
- **Coverage testing** across different California counties
- **Performance testing** (sub-5 second response per site)

---

## 🔗 COORDINATION WITH VITOR-WINGMAN

### **Communication Protocol**
- **Shared Files**: Place all development files in specified analyzer directory
- **Progress Updates**: Create progress files in `/agents/VITOR/WINGMAN/coordination/`
- **Questions**: Use clear file naming for coordination questions

### **Data Integration Requirements**
**Input Format**: 
- Latitude, longitude coordinates (same as other analyzers)
- Optional site address for improved accuracy

**Output Format**:
- Must match other analyzer return formats
- Boolean elimination decision + detailed analysis
- Error handling for API failures
- Manual verification pathway for uncertain cases

### **Timeline Coordination**
- **Week 1**: Research and data source evaluation
- **Week 2**: Core implementation and basic testing  
- **Week 3**: Integration testing and performance optimization
- **Handoff**: When VITOR-WINGMAN reaches Phase 6 of BOTN filtering

---

## 📊 SUCCESS CRITERIA

### **Technical Success**
- [ ] `LandUseAnalyzer` class implemented and tested
- [ ] Integration with existing BOTN pipeline verified
- [ ] 90%+ accuracy on prohibited use detection
- [ ] Performance: <5 seconds per site analysis
- [ ] Comprehensive error handling for API failures

### **Business Success**
- [ ] Can eliminate agriculture, industrial, auto, gas station, dry cleaning sites
- [ ] False positive rate <5% (don't eliminate viable sites)
- [ ] Covers California statewide (2,676 site dataset)
- [ ] Production-ready code quality

### **Integration Success**
- [ ] Seamless integration with VITOR-WINGMAN BOTN pipeline
- [ ] Compatible output format with existing elimination logic
- [ ] Comprehensive test suite following Colosseum standards
- [ ] Documentation for maintenance and updates

---

## 🚨 CRITICAL CONSIDERATIONS

### **Data Quality Priorities**
1. **Accuracy > Coverage**: Better to have high confidence results on fewer sites
2. **Authoritative Sources**: County assessor data preferred over commercial APIs
3. **False Positive Prevention**: Don't eliminate viable residential sites
4. **Manual Verification Path**: Provide mechanism for uncertain cases

### **Geographic Scope**
- **Primary**: California (2,676 sites in current dataset)
- **Northern CA Focus**: Ensure coverage of Bay Area, Sacramento (728 sites)
- **Scalability**: Design for future multi-state expansion

### **Performance Requirements**
- **Batch Processing**: Must handle 200-350 sites efficiently  
- **API Rate Limits**: Design for API throttling and retry logic
- **Caching**: Implement intelligent caching for repeat coordinates
- **Timeout Handling**: Graceful degradation for slow/failed API calls

---

## 🛠️ RECOMMENDED DEVELOPMENT APPROACH

### **Week 1: Foundation**
1. **Study existing analyzers** (qct_dda_analyzer.py, fire_hazard_analyzer.py)
2. **Analyze CoStar dataset** for existing land use columns
3. **Research data sources** and create evaluation matrix
4. **Create basic class structure** and test framework

### **Week 2: Core Implementation** 
1. **Implement top data source** (likely county assessor or CoStar analysis)
2. **Create classification logic** for prohibited uses
3. **Build test suite** with known prohibited/acceptable sites
4. **Add error handling** and fallback logic

### **Week 3: Integration & Optimization**
1. **Integration testing** with BOTN pipeline
2. **Performance optimization** for batch processing
3. **Comprehensive testing** across California regions
4. **Documentation** and handoff preparation

---

## 📋 DELIVERABLES CHECKLIST

### **Code Deliverables**
- [ ] `land_use_analyzer.py` - Main analyzer class
- [ ] `test_land_use_analyzer.py` - Comprehensive test suite
- [ ] Integration code for main pipeline
- [ ] Configuration files for data sources

### **Documentation Deliverables**
- [ ] Data source research report
- [ ] API documentation and access requirements
- [ ] Test results and accuracy metrics
- [ ] Integration instructions for VITOR-WINGMAN

### **Coordination Deliverables**
- [ ] Progress updates in coordination folder
- [ ] Final handoff report with implementation details
- [ ] Known limitations and future enhancement opportunities

---

## 🎖️ MISSION SUCCESS DEFINITION

**COMPLETE SUCCESS**: Land Use Analyzer seamlessly integrates with VITOR-WINGMAN BOTN filtering system, accurately identifying and eliminating sites with prohibited uses (agriculture, industrial, auto, gas stations, dry cleaning) while preserving viable residential development opportunities, enabling completion of production-ready 4-mandatory-criteria LIHTC site screening platform.

**Business Impact**: Completes final component of automated LIHTC site screening system, enabling systematic elimination of development-incompatible sites and delivery of clean, viable development portfolio.

---

**Coordination Agent**: VITOR-WINGMAN  
**Timeline**: 2-3 weeks  
**Success Probability**: High (clear requirements + research phase)  
**Business Criticality**: Essential (completes BOTN system)

**🏛️ Built to Roman Engineering Standards - Excellence in Every Component 🏛️**