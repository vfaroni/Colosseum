# 🌾 STRIKE LEADER MISSION: USDA Rural Development Maps Acquisition

**Mission ID**: STRIKE-USDA-RURAL-2025-001  
**Priority**: HIGH - LIHTC Rural Set-Aside Critical  
**Lead Agent**: STRIKE LEADER (Bill)  
**Supporting Agents**: WINGMAN (Technical), TOWER (Validation)  
**Mission Start**: 2025-08-08 (Following CA Environmental)  
**Target Completion**: 2025-08-14 (1 week)  

---

## 🎯 MISSION OVERVIEW

### Strategic Objective
Acquire comprehensive USDA Rural Development multifamily housing eligibility maps to identify federally-defined rural areas for LIHTC development. These maps are CRITICAL for accessing rural set-asides (typically 10-20% of state credits) and scoring bonus points in competitive rounds.

### Business Impact
- **Set-Aside Access**: Unlock 10-20% of state LIHTC allocations reserved for rural
- **Reduced Competition**: Rural set-asides have 3-5x better odds than urban
- **Bonus Points**: 5-15 additional scoring points in most QAPs
- **Basis Boost**: Many rural areas qualify for 130% eligible basis boost
- **Cost Advantage**: Lower land costs with same credit pricing

---

## 📊 CRITICAL USDA RURAL DEFINITIONS

### What Qualifies as "Rural" for LIHTC
**USDA Rural Development Definition** (7 CFR 3560.11):
1. **Population Threshold**: Areas with population ≤35,000
2. **Non-Metro Areas**: Outside Metropolitan Statistical Areas (MSAs)
3. **Rural In Character**: Areas USDA determines are rural despite proximity to metros
4. **Grandfathered Areas**: Previously eligible areas maintaining status

### Key Data Layers Needed
1. **USDA Eligible Areas Map**: Primary multifamily housing eligibility
2. **Census Place Boundaries**: Population-based determinations
3. **MSA/CBSA Boundaries**: Metropolitan statistical area exclusions
4. **Tribal Lands**: Special rural designations
5. **Grandfathered Communities**: Historical eligibility preserved

---

## 🗺️ DATA SOURCES & ACQUISITION STRATEGY

### Primary Source: USDA Rural Development

#### **USDA Property Eligibility Map**
**URL**: `https://eligibility.sc.egov.usda.gov/eligibility/`
**API Endpoint**: `https://eligibilityapi.sc.egov.usda.gov/Eligibility/api/v1/`
**Type**: REST API with address/coordinate lookup
**Authentication**: None required (public)

**Key API Calls**:
```python
# Check address eligibility
GET /api/v1/property/eligibility
params: {
    'address': '123 Main St',
    'city': 'Townsville',
    'state': 'CA',
    'zip': '12345'
}

# Check by coordinates
GET /api/v1/property/coordinates
params: {
    'latitude': 34.0522,
    'longitude': -118.2437
}

# Get eligibility layer
GET /api/v1/layer/multifamily
params: {
    'bbox': 'minLon,minLat,maxLon,maxLat',
    'format': 'geojson'
}
```

#### **USDA Census Designated Rural Areas**
**Source**: USDA Economic Research Service
**URL**: `https://www.ers.usda.gov/data-products/rural-urban-continuum-codes/`
**Format**: County-level RUCC codes (Rural-Urban Continuum Codes)

#### **USDA GIS Services**
**ArcGIS Server**: `https://gis.sc.egov.usda.gov/arcgis/rest/services/`
**Available Services**:
- `/RD_Eligibility/MapServer` - Main eligibility layer
- `/Census_Data/MapServer` - Population data
- `/Tribal_Lands/MapServer` - Tribal designations

---

## 📈 PRIORITY ACQUISITION FRAMEWORK

### Phase 1: National Coverage (Days 1-2)
**Objective**: Baseline rural eligibility for all states

1. **County-Level RUCC Codes**
   - Download all 3,143 US counties
   - Classifications 1-9 (1-3 Metro, 4-9 Rural)
   - Identify all rural counties (codes 4-9)

2. **State Rural Percentages**
   - Calculate rural land area per state
   - Identify high-rural states for LIHTC opportunity
   - Map against LIHTC allocation amounts

### Phase 2: Detailed State Maps (Days 3-4)
**Priority States** (Highest rural LIHTC allocations):

**Tier 1 - Maximum Rural Opportunity**:
1. **Texas**: Large rural set-aside, multiple rural regions
2. **California**: Significant rural counties, high credit values
3. **Montana**: 25% rural set-aside requirement
4. **Iowa**: Strong rural preference scoring
5. **Nebraska**: Rural priority in QAP

**Tier 2 - Strong Rural Programs**:
6. **North Dakota**: Majority rural state
7. **South Dakota**: High rural percentage
8. **Wyoming**: Almost entirely rural
9. **New Mexico**: Large rural areas
10. **Kansas**: Significant rural set-aside

### Phase 3: Granular Property Eligibility (Days 5-6)
**Census Place Level Analysis**:
- Download census place boundaries
- Cross-reference with USDA eligibility
- Identify "rural in character" exceptions
- Map grandfathered communities

### Phase 4: Integration & Validation (Day 7)
- Merge with existing parcel data
- Validate against known rural LIHTC projects
- Create composite eligibility layer
- Generate state-specific rural maps

---

## 🎯 SUCCESS CRITERIA

### Quantitative Metrics
- ✅ **Coverage**: All 50 states + territories mapped
- ✅ **Counties**: 3,143 county classifications complete
- ✅ **Accuracy**: 99%+ match with USDA determinations
- ✅ **Granularity**: Census place level (sub-county) detail
- ✅ **Integration**: Seamless overlay with parcel data

### Qualitative Objectives
- ✅ Identify all rural set-aside eligible areas
- ✅ Map grandfathered communities
- ✅ Document "rural in character" exceptions
- ✅ Create state-specific rural opportunity maps
- ✅ Enable rapid rural eligibility checking

---

## 💰 BUSINESS VALUE PROPOSITION

### LIHTC Competitive Advantages

#### **Set-Aside Benefits**
```
Urban Competition: 100 applications for 10 awards = 10% success
Rural Set-Aside: 20 applications for 5 awards = 25% success
Advantage: 2.5x better odds in rural set-aside
```

#### **Scoring Benefits** (Typical QAP)
- Rural location: +10 points
- Rural economic development: +5 points
- Agricultural worker housing: +5 points
- Total potential: +20 points (often decisive)

#### **Financial Benefits**
- Land costs: 50-70% lower than urban
- Construction costs: 10-20% lower
- Same tax credit pricing (often higher demand)
- Eligible for USDA 538 loans (below-market rates)

### Revenue Opportunity
- **Service Offering**: Rural site identification consulting
- **Premium Feature**: Automated rural eligibility checking
- **Market Intelligence**: Rural competition analysis
- **Site Selection**: Optimal rural location finder

---

## 🔧 TECHNICAL IMPLEMENTATION

### Wingman Technical Tasks

#### Data Collection Pipeline
```python
class USDARuralCollector:
    def __init__(self):
        self.eligibility_api = "https://eligibilityapi.sc.egov.usda.gov"
        self.gis_server = "https://gis.sc.egov.usda.gov/arcgis"
        
    def check_eligibility(self, lat, lon):
        """Check USDA rural eligibility for coordinates"""
        endpoint = f"{self.eligibility_api}/Eligibility/api/v1/property/coordinates"
        params = {'latitude': lat, 'longitude': lon}
        return requests.get(endpoint, params=params).json()
        
    def download_county_codes(self):
        """Download Rural-Urban Continuum Codes"""
        rucc_url = "https://www.ers.usda.gov/webdocs/DataFiles/53251/ruralurbancodes2023.xls"
        return pd.read_excel(rucc_url)
        
    def get_eligibility_layer(self, bbox):
        """Download GeoJSON eligibility layer for bounding box"""
        endpoint = f"{self.gis_server}/rest/services/RD_Eligibility/MapServer/0/query"
        params = {
            'geometry': bbox,
            'geometryType': 'esriGeometryEnvelope',
            'outFields': '*',
            'f': 'geojson'
        }
        return requests.get(endpoint, params=params).json()
```

### Tower Validation Requirements

#### Quality Checks
1. **Boundary Accuracy**: Rural areas properly delineated
2. **Population Verification**: Cross-check with Census data
3. **Grandfathering**: Verify historically eligible areas
4. **MSA Exclusions**: Confirm metro areas excluded
5. **State QAP Alignment**: Match state-specific rural definitions

#### Validation Metrics
- Accuracy: 99%+ agreement with USDA tool
- Completeness: 100% county coverage
- Currency: Data within 6 months
- Integration: Successful parcel overlay

---

## 📊 EXPECTED DATA VOLUMES

### Dataset Sizes
| Dataset | Records | Size | Format |
|---------|---------|------|--------|
| County RUCC Codes | 3,143 | 2 MB | CSV/Excel |
| Census Places | 30,000+ | 500 MB | Shapefile |
| Eligibility Polygons | 50,000+ | 1-2 GB | GeoJSON |
| Tribal Lands | 500+ | 100 MB | Shapefile |
| Grandfathered Areas | 5,000+ | 50 MB | CSV |
| **Total Estimate** | **90,000+** | **~3 GB** | Mixed |

---

## 📅 EXECUTION TIMELINE

### Day 1-2: National Framework
- Download RUCC codes for all counties
- Identify rural counties (codes 4-9)
- Create national rural overview map

### Day 3-4: Priority States
- Process Tier 1 states (TX, CA, MT, IA, NE)
- Download detailed eligibility layers
- Create state-specific maps

### Day 5-6: Granular Detail
- Census place boundaries
- Grandfathered communities
- Tribal lands overlay

### Day 7: Integration & Delivery
- Merge with parcel data
- Validation testing
- Final documentation

---

## 🚨 CRITICAL CONSIDERATIONS

### Data Nuances
1. **Dynamic Eligibility**: Some areas change status annually
2. **State Variations**: States may use different rural definitions
3. **Grandfathering**: Complex rules for previously eligible areas
4. **Tribal Sovereignty**: Special considerations for tribal lands
5. **Distance Rules**: Some states use distance from urban areas

### Risk Mitigation
- Implement version tracking for annual updates
- Document state-specific variations
- Maintain grandfathering history
- Respect tribal data sovereignty
- Calculate multiple distance metrics

---

## 🎯 IMMEDIATE ACTIONS

### Strike Leader Tasks
1. Coordinate with USDA data services
2. Prioritize states by rural LIHTC opportunity
3. Establish validation framework with Tower
4. Prepare integration plan with parcel data

### Wingman Queue
1. Build USDA API integration
2. Download county RUCC codes
3. Process priority state eligibility layers
4. Generate GeoJSON outputs

### Tower Validation
1. Verify against known rural projects
2. Cross-check with census data
3. Validate state QAP compliance
4. Quality score assignment

---

## 📈 SUCCESS METRICS

### Immediate Value
- Identify 10,000+ rural-eligible census places
- Map 1,000+ grandfathered communities
- Enable instant rural eligibility checking
- Support 50-state rural analysis

### Long-term Impact
- Increase rural LIHTC success rate by 2x
- Reduce site selection time by 80%
- Enable systematic rural opportunity analysis
- Create competitive advantage in underserved markets

---

## 🏆 MISSION AUTHORIZATION

**Authorized By**: Bill Rice  
**Classification**: Strategic Enhancement  
**Priority**: HIGH - Execute after CA Environmental  
**Resources**: Existing infrastructure sufficient  

---

**Mission Status**: APPROVED - QUEUED FOR EXECUTION  
**Start Trigger**: Completion of CA Environmental Phase 1  
**First Task**: Download national RUCC codes  

---

*"Unlocking Rural Opportunity Through Superior Intelligence"*

**STRIKE LEADER - Mission Command**  
Colosseum LIHTC Platform

**Ruris Victoria** - *"Rural Victory"*