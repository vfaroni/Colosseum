# 🗺️ ARIZONA GEOSPATIAL DATA CATALOG - COMPREHENSIVE RESOURCE

**Report ID**: TOWER-GIS-001  
**Date**: July 14, 2025  
**Mission**: Arizona Public Dataset Discovery  
**Subject**: Complete catalog of Arizona geospatial datasets for CTCAC amenity mapping  

## 🎯 EXECUTIVE SUMMARY

**DISCOVERY SCOPE**: Comprehensive catalog of Arizona public geospatial datasets across 7 amenity categories essential for CTCAC compliance mapping, including schools, healthcare, transit, libraries, grocery, parks, and pharmacies.

**DATA AVAILABILITY**: High-quality geospatial data available through state repositories, federal sources, and local government portals in standard GIS formats (shapefile, GeoJSON, GPKG).

**STRATEGIC VALUE**: Essential infrastructure for Arizona CTCAC site amenity mapping, distance calculations, and regulatory compliance documentation.

## 📊 EXISTING DATASET FOUNDATION

### **Current Arizona Holdings** (Reference: `/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/`)
```
EXISTING ARIZONA DATASETS:
├── HUD Data: `az_counties_hud_ami_2025.gpkg`
├── Poverty Data: `poverty_tracts_AZ_2022.gpkg`
├── Federal Infrastructure: FEMA flood zones, Census boundaries
└── Gap Analysis: Missing 7 key amenity categories
```

### **Proven Collection Patterns** (From CA/TX Analysis)
```
SUCCESSFUL FRAMEWORK:
├── State Government: Primary authoritative sources
├── Federal Integration: HUD, Census, FEMA data
├── Local Portals: City/county open data platforms
├── File Formats: .shp, .geojson, .gpkg, .kml
└── Processing: Summary JSON, QML styling, coordinate validation
```

## 🏛️ PRIMARY STATE DATA REPOSITORIES

### **AZGeo Data Hub** - Arizona's Official Geospatial Repository
```
AZGEO SPECIFICATIONS:
├── Website: https://azgeo-data-hub-agic.hub.arcgis.com/
├── Open Data Portal: https://azgeo-open-data-agic.hub.arcgis.com/
├── Authority: Arizona Geographic Information Council (AGIC)
├── Host: Arizona State Land Department
├── Staff: Arizona Land Resources Information System (ALRIS)
├── Coverage: Statewide authoritative datasets
├── Formats: Shapefile, KML, GeoJSON, GPKG
├── Update Frequency: Quarterly or as needed
└── Access: Free public download
```

**Value Proposition**: Single-source authoritative data from state agencies, highest quality and most current datasets available.

### **Arizona Geographic Information Council (AGIC)**
```
AGIC RESOURCES:
├── Website: https://agic.az.gov/agic/geospatial-data-collections-and-resources
├── AZGEO Clearinghouse: Legacy catalog of Arizona GIS data
├── Coverage: Multi-agency coordination and standards
├── Resources: Metadata, documentation, data standards
├── Integration: State and local agency partnerships
└── Authority: Official state GIS coordination body
```

## 🎓 SCHOOLS - EDUCATIONAL FACILITIES

### **Arizona Schools Dataset** (AZGeo Data Hub)
```
ARIZONA SCHOOLS SPECIFICATIONS:
├── Source: Arizona Department of Education + AZMAG
├── URL: https://azgeo-data-hub-agic.hub.arcgis.com/datasets/AZMAG::arizona-schools/explore
├── Coverage: Public elementary, secondary, and unified schools
├── Attributes: School name, address, type, district, enrollment
├── Geometry: Point locations with coordinates
├── Update: Annual (2021-2022 academic year base)
├── Format: Shapefile, GeoJSON, KML, CSV
└── Quality: Official state education department data
```

### **School District Boundaries**
```
SCHOOL DISTRICT BOUNDARIES:
├── Source: Arizona Department of Health Services GIS Portal
├── URL: https://geodata-adhsgis.hub.arcgis.com/datasets/school-districts-in-arizona
├── Coverage: Elementary, secondary, unified district boundaries
├── Attributes: District name, type, enrollment statistics
├── Geometry: Polygon boundaries
├── Base Year: 2021-2022 academic year
├── Authority: U.S. Census Bureau TIGER/Line 2022
└── Integration: National Center for Education Statistics (NCES)
```

### **Federal School Location Data**
```
NCES SCHOOL GEOCODES:
├── Source: National Center for Education Statistics
├── URL: https://nces.ed.gov/programs/edge/geographic/schoollocations
├── Coverage: Public schools and district administrative offices
├── Data Source: Common Core of Data (CCD)
├── Attributes: Enrollment, staffing, program participation
├── Geometry: Geocoded point locations
├── Format: Shapefile, GIS web services
└── Update: Annual collection
```

## 🏥 HEALTHCARE - MEDICAL FACILITIES

### **Arizona Medical Facilities** (ADHS Official)
```
MEDICAL FACILITIES SPECIFICATIONS:
├── Source: Arizona Department of Health Services
├── URL: https://geodata-adhsgis.hub.arcgis.com/datasets/medical-facility-1
├── Coverage: Medical and childcare providers, healthcare facilities
├── Authority: Licensed by Arizona Department of Health Services
├── Attributes: Facility name, address, type, license status
├── Geometry: Point locations with coordinates
├── Update: September 2024 (recent)
├── Format: Shapefile, GeoJSON, KML
└── Quality: Official state licensing data
```

### **Arizona Hospitals Dataset** (ADHS Official)
```
HOSPITALS SPECIFICATIONS:
├── Source: Arizona Department of Health Services
├── URL: https://geodata-adhsgis.hub.arcgis.com/maps/ADHSGIS::hospitals-2
├── Coverage: Licensed hospitals and medical centers
├── Attributes: Hospital name, address, bed count, services
├── Geometry: Point locations with coordinates
├── Update: February 2025 (current)
├── Format: Shapefile, GeoJSON, KML
└── Authority: ADHS official licensing database
```

### **Comprehensive Healthcare Facilities** (Third-Party)
```
HEALTHCARE DATASET (FELT.COM):
├── Source: Felt.com Arizona Healthcare Dataset
├── URL: https://felt.com/explore/hospitals-clinics-arizona
├── Coverage: 354 hospital and clinic locations
├── Attributes: Emergency services, bed count, contact info
├── Geometry: Point locations with detailed attributes
├── Features: Comprehensive facility information
├── Format: Various GIS formats available
└── Usage: GIS professional analysis ready
```

## 🚌 TRANSIT - PUBLIC TRANSPORTATION

### **Valley Metro (Phoenix Area)** - Primary Transit Authority
```
VALLEY METRO SPECIFICATIONS:
├── Source: Valley Metro Public Transit Agency
├── URL: https://www.valleymetro.org/
├── Coverage: 16 jurisdictions in Phoenix metropolitan area
├── Services: Bus routes, light rail, ridership data
├── GIS Portal: Valley Metro GeoCenter
├── Features: Bus routes, light-rail stations, transit centers
├── Attributes: Route information, ridership, park-and-ride
├── Format: Shapefile, GeoJSON, GTFS
└── Authority: Regional transit authority
```

### **Arizona Transit Data** (Federal/State)
```
ARIZONA TRANSIT RESOURCES:
├── Source: Bureau of Transportation Statistics
├── URL: https://www.bts.gov/national-transit-map
├── Coverage: National Transit Map (NTM) - Arizona subset
├── Authority: Federal Transit Administration (FTA)
├── Data Source: GTFS Schedule data
├── Attributes: Fixed-guideway and fixed-route transit
├── Format: Shapefile, GeoJSON
└── Integration: National Transportation Atlas Database
```

### **Local Transit Agencies**
```
LOCAL TRANSIT SYSTEMS:
├── Tucson Open Data: https://gisdata.tucsonaz.gov/
├── Phoenix Open Data: https://www.phoenixopendata.com/
├── Coverage: City-specific transit routes and stops
├── Attributes: Local bus routes, schedules, stops
├── Format: Shapefile, GeoJSON, GTFS
└── Authority: Municipal transit departments
```

## 📚 LIBRARIES - PUBLIC LIBRARY SYSTEMS

### **Arizona Public Libraries** (Multiple Sources)
```
LIBRARY DATA SOURCES:
├── Primary: AZGeo Data Hub library searches
├── Secondary: Institute of Museum and Library Services
├── Tertiary: OpenStreetMap Arizona library data
├── Coverage: Public library branches statewide
├── Attributes: Library name, address, services, hours
├── Geometry: Point locations with coordinates
├── Format: Shapefile, GeoJSON, KML
└── Compilation: May require multi-source integration
```

### **University Library Resources**
```
ACADEMIC LIBRARY GIS:
├── ASU GeoData: https://lib.asu.edu/geo/data
├── UA Data Cooperative: https://data.library.arizona.edu/geo/find-data/gis-data
├── Coverage: Academic library locations and services
├── Attributes: Institution, services, research focus
├── Format: Various GIS formats
└── Integration: Higher education facility data
```

## 🛒 GROCERY STORES - FOOD RETAIL

### **USDA Food Access Research Atlas**
```
USDA FOOD ACCESS SPECIFICATIONS:
├── Source: USDA Economic Research Service
├── URL: https://www.ers.usda.gov/data-products/food-access-research-atlas/download-the-data
├── Coverage: Supermarkets and large grocery stores
├── Authority: SNAP-authorized retailers + TDLinx directory
├── Criteria: $2M+ annual sales, major food departments
├── Attributes: Store name, address, sales volume, SNAP status
├── Geometry: Geocoded point locations
├── Format: Excel, GIS-compatible after processing
└── Analysis: Food access by census tract
```

### **Commercial Grocery Data**
```
COMMERCIAL FOOD RETAIL:
├── Source: ESRI Business Analyst
├── Coverage: Phoenix grocery store mapping demonstrated
├── Attributes: Store type, sales, demographics
├── Analysis: Food desert assessment capability
├── Format: Shapefile, GeoJSON through Business Analyst
└── Access: Requires ESRI licensing
```

### **Data.gov Grocery Resources**
```
FEDERAL GROCERY DATA:
├── Source: Data.gov grocery store datasets
├── URL: https://catalog.data.gov/dataset?tags=grocery-stores
├── Coverage: Disaster-essential grocery stores
├── Attributes: Store locations, emergency status
├── Format: Shapefile, CSV, GeoJSON
└── Authority: Federal emergency management data
```

## 🏞️ PARKS - RECREATION FACILITIES

### **Arizona State Parks**
```
STATE PARKS SPECIFICATIONS:
├── Source: Arizona State Parks (via AZGeo Data Hub)
├── Coverage: State park locations and boundaries
├── Attributes: Park name, acreage, facilities, activities
├── Geometry: Point locations and polygon boundaries
├── Format: Shapefile, GeoJSON, KML
└── Authority: Arizona State Parks Department
```

### **Maricopa County Parks**
```
MARICOPA COUNTY PARKS:
├── Source: Maricopa County GIS Open Data
├── URL: https://data-maricopa.opendata.arcgis.com/
├── Coverage: County parks, trails, amenities
├── Attributes: Park name, facilities, trail systems
├── Features: Complete trail segments and connections
├── Geometry: Points and polygons
├── Format: Shapefile, GeoJSON, KML
└── Update: Daily to monthly schedules
```

### **Federal Recreation Areas**
```
FEDERAL RECREATION DATA:
├── Source: Bureau of Land Management Arizona
├── URL: https://gbp-blm-egis.hub.arcgis.com/pages/arizona
├── Coverage: BLM recreation areas, wilderness
├── Attributes: Recreation type, access, facilities
├── Format: Multiple GIS formats
└── Authority: Federal land management agencies
```

## 💊 PHARMACIES - RETAIL PHARMACIES

### **Arizona State Board of Pharmacy**
```
PHARMACY LICENSING DATA:
├── Source: Arizona State Board of Pharmacy
├── URL: https://pharmacy.az.gov/
├── Coverage: Licensed pharmacies statewide
├── Authority: State pharmacy regulatory board
├── Access: Individual license verification available
├── Limitation: No bulk geospatial data download
├── Contact: (602) 771-2727 for data requests
└── Legal: A.R.S. § 32-3214(C) public records
```

### **Alternative Pharmacy Data Sources**
```
PHARMACY DATA ALTERNATIVES:
├── Commercial GIS: MAPOG pharmacy location data
├── OpenStreetMap: Community-contributed pharmacy data
├── Local Portals: City open data pharmacy listings
├── Healthcare Integration: ADHS medical facility data
├── Format: Shapefile, KML, GeoJSON
└── Licensing: ODbL (OpenStreetMap), commercial terms
```

## 🏢 ADDITIONAL DATA SOURCES

### **Arizona State Land Department**
```
ASLD RESOURCES:
├── Website: https://land.az.gov/maps-gis
├── Coverage: Land parcels, boundaries, ownership
├── Authority: State land management
├── Format: Shapefile, GeoJSON, web services
└── Integration: Property boundary data
```

### **Arizona Department of Water Resources**
```
ADWR GIS DATA:
├── Coverage: Water resources, wells, boundaries
├── Authority: State water management
├── Format: Downloadable GIS datasets
└── Integration: Utility and infrastructure data
```

### **Local Government Open Data Portals**
```
MUNICIPAL DATA SOURCES:
├── Phoenix: https://www.phoenixopendata.com/
├── Tucson: https://gisdata.tucsonaz.gov/
├── Scottsdale: https://data.scottsdaleaz.gov/
├── Gilbert: https://alex.gilbertaz.gov/how-to/
├── Coverage: City-specific amenity data
├── Format: Shapefile, GeoJSON, KML
└── Update: Various frequencies
```

## 📋 RECOMMENDED COLLECTION STRATEGY

### **Phase 1: State Repository Priority** (Week 1)
```
PRIORITY COLLECTION:
├── AZGeo Data Hub: Complete dataset search
├── ADHS Portal: Healthcare and hospital data
├── School Data: Arizona schools + district boundaries
├── Transit Data: Valley Metro and federal sources
├── Parks Data: State parks and recreation areas
└── Expected Yield: 5-6 complete datasets
```

### **Phase 2: Federal Integration** (Week 2)
```
FEDERAL DATA INTEGRATION:
├── USDA: Food access and grocery store data
├── Census: School district boundaries
├── BTS: National transit data for Arizona
├── BLM: Federal recreation and park data
└── Expected Yield: 3-4 supporting datasets
```

### **Phase 3: Local Supplementation** (Week 3)
```
LOCAL DATA COLLECTION:
├── Maricopa County: Parks and recreation
├── Phoenix: City amenity data
├── Tucson: Municipal facility data
├── Pharmacy Data: Commercial or OSM sources
└── Expected Yield: 2-3 localized datasets
```

## 🗂️ PROPOSED FILE STRUCTURE

### **Arizona Dataset Organization**
```
/arizona/
├── AZ_Transit_Data/
│   ├── valley_metro_routes.shp
│   ├── arizona_transit_stops.geojson
│   ├── gtfs_arizona_feeds.zip
│   └── transit_summary.json
├── AZ_Public_Schools/
│   ├── arizona_schools_2024.shp
│   ├── school_districts_boundaries.geojson
│   └── schools_summary.json
├── AZ_Hospitals_Medical/
│   ├── adhs_medical_facilities.shp
│   ├── arizona_hospitals.geojson
│   └── healthcare_summary.json
├── AZ_Libraries/
│   ├── arizona_public_libraries.shp
│   ├── library_locations.geojson
│   └── libraries_summary.json
├── AZ_Grocery_Stores/
│   ├── usda_food_access_az.shp
│   ├── grocery_stores_arizona.geojson
│   └── grocery_summary.json
├── AZ_Parks_Recreation/
│   ├── arizona_state_parks.shp
│   ├── county_parks_maricopa.geojson
│   └── parks_summary.json
├── AZ_Pharmacies/
│   ├── arizona_pharmacies.shp
│   ├── pharmacy_locations.geojson
│   └── pharmacies_summary.json
└── AZ_Boundaries/
    ├── arizona_counties.shp
    ├── arizona_cities.geojson
    └── boundaries_summary.json
```

## 📊 DATA QUALITY ASSESSMENT

### **Expected Data Quality by Category**
```
QUALITY ASSESSMENT:
├── Schools: HIGH (Official ADE data)
├── Healthcare: HIGH (ADHS licensing data)
├── Transit: HIGH (Valley Metro + federal)
├── Parks: MEDIUM-HIGH (State + county sources)
├── Libraries: MEDIUM (Multi-source compilation)
├── Grocery: MEDIUM (Federal + commercial)
├── Pharmacies: MEDIUM (Board licensing + alternatives)
└── Overall: HIGH QUALITY with authoritative sources
```

### **Coordinate System Standards**
```
COORDINATE SYSTEM REQUIREMENTS:
├── Primary: WGS84 (EPSG:4326)
├── Secondary: NAD83 Arizona zones as needed
├── Validation: Coordinate accuracy verification
├── Processing: Reproject all to WGS84
└── Quality: Maintain sub-meter accuracy
```

## 🎯 STRATEGIC RECOMMENDATIONS

### **Collection Priorities**
1. **Start with AZGeo Data Hub**: Single-source authoritative data
2. **ADHS Portal**: Healthcare facilities critical for CTCAC
3. **Valley Metro**: Transit data essential for compliance
4. **Federal Sources**: Standardized national datasets
5. **Local Supplementation**: Fill gaps with city/county data

### **Data Validation Strategy**
1. **Coordinate Validation**: Verify all locations within Arizona
2. **Attribute Completeness**: Ensure name, address, type fields
3. **CTCAC Compliance**: Filter for eligible amenity types
4. **Distance Calculations**: Validate coordinate accuracy
5. **Documentation**: Create metadata for each dataset

### **Processing Framework**
1. **Standardization**: Common coordinate system and attributes
2. **Quality Control**: Automated validation and error checking
3. **Summarization**: JSON summary files for each category
4. **Integration**: Compatible with existing CA/TX framework
5. **Documentation**: Complete metadata and source attribution

## 📈 EXPECTED OUTCOMES

### **Dataset Completeness**
- **7 Primary Categories**: Complete coverage expected
- **Coverage Area**: Statewide Arizona with local enhancement
- **Quality Level**: Professional GIS analysis ready
- **Format Compatibility**: Standard GIS formats (SHP, GeoJSON, GPKG)

### **CTCAC Integration**
- **Compliance Ready**: Distance calculations and mapping
- **Professional Quality**: Court-ready documentation
- **Comprehensive Coverage**: All required amenity categories
- **Scalable Framework**: Template for other states

## 📋 CONCLUSION

**DATA AVAILABILITY**: Excellent - Arizona provides comprehensive public geospatial data through well-organized state repositories and federal sources.

**COLLECTION FEASIBILITY**: High - Systematic collection strategy with proven patterns from CA/TX experience.

**QUALITY EXPECTATION**: High - Authoritative state sources with regular updates and professional standards.

**STRATEGIC VALUE**: Essential - Complete Arizona geospatial infrastructure enables CTCAC compliance mapping and distance calculations.

**RECOMMENDATION**: **PROCEED WITH SYSTEMATIC COLLECTION** - Begin with AZGeo Data Hub priority datasets, then integrate federal and local sources for comprehensive coverage.

---

**TOWER Geospatial Intelligence**: Arizona public dataset catalog complete. Comprehensive collection strategy ready for implementation with high-quality authoritative data sources identified across all essential amenity categories.