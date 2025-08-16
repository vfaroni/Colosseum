# Arizona Geospatial Datasets Available for CTCAC Mapping

**Last Updated**: July 14, 2025  
**Data Collection Status**: Phase 2 Complete - Ready for Integration  
**Coverage**: Comprehensive Arizona amenity datasets for CTCAC compliance  

## 📊 DATASET INVENTORY

### Federal Datasets (All States Including Arizona)

#### 1. **NCES School Location Data (2023-24)**
- **Location**: `/Data_Sets/federal/Schools_National/`
- **Coverage**: All US public schools including Arizona subset
- **Format**: Shapefile (.shp, .shx, .dbf, .prj)
- **Files Available**:
  - `EDGE_GEOCODE_PUBLICSCH_2324.zip` (28.8 MB) - Public Schools
  - `EDGE_GEOCODE_PUBLICLEA_2324.zip` (7.89 MB) - School Districts
  - `EDGE_GEOCODE_POSTSECSCH_2324.zip` (2.64 MB) - Postsecondary Schools
- **Coordinate System**: WGS84 (EPSG:4326)
- **Arizona Subset**: ~2,800+ public schools
- **Attributes**: School name, address, type, enrollment, district info

#### 2. **USDA Food Access Research Atlas (2019)**
- **Location**: `/Data_Sets/federal/Grocery_National/`
- **Coverage**: National food access data (Arizona subset available)
- **Format**: Excel/CSV (requires GIS processing)
- **Files Available**:
  - `FoodAccessResearchAtlasData2019.xlsx` - National data
  - `2019_Food_Access_Research_Atlas_Data.zip` - Alternative format
- **Processing Required**: Census tract level → Point locations
- **Arizona Application**: Food desert analysis, grocery store proximity

### Arizona State Datasets

#### 3. **Arizona Public Schools (ADE + AZMAG)**
- **Location**: `/Data_Sets/arizona/AZ_Public_Schools/`
- **Source**: Arizona Department of Education + Maricopa Association of Governments
- **Coverage**: Statewide Arizona public schools
- **Format**: Shapefile, GeoJSON, CSV
- **Download Source**: https://azgeo-data-hub-agic.hub.arcgis.com/datasets/AZMAG::arizona-schools
- **Expected Records**: ~2,800 schools
- **Attributes**: School name, address, type, district, grade levels
- **Update Frequency**: Annual
- **CTCAC Use**: Elementary, middle, high school proximity calculations

#### 4. **Arizona Licensed Hospitals**
- **Location**: `/Data_Sets/arizona/AZ_Hospitals_Medical/`
- **Source**: Arizona Department of Health Services (ADHS)
- **Coverage**: State-licensed hospitals statewide
- **Format**: Shapefile, GeoJSON, CSV
- **Download Source**: https://geodata-adhsgis.hub.arcgis.com/datasets/ADHSGIS::state-licensed-hospitals-in-arizona
- **Expected Records**: ~180 licensed hospitals
- **Attributes**: Hospital name, address, bed count, services, license status
- **Update Frequency**: Monthly
- **CTCAC Use**: Medical facility proximity calculations

#### 5. **Arizona Medical Facilities**
- **Location**: `/Data_Sets/arizona/AZ_Hospitals_Medical/`
- **Source**: Arizona Department of Health Services (ADHS)
- **Coverage**: All licensed medical and childcare facilities
- **Format**: Shapefile, GeoJSON, CSV
- **Download Source**: https://geodata-adhsgis.hub.arcgis.com/datasets/medical-facility-1
- **Expected Records**: ~1,500 licensed facilities
- **Attributes**: Facility name, address, license type, services
- **Update Frequency**: Regular (last update September 2024)
- **CTCAC Use**: Healthcare facility proximity calculations

#### 6. **Arizona Transit Data**
- **Location**: `/Data_Sets/arizona/AZ_Transit_Data/`
- **Sources**: Valley Metro, City of Phoenix, City of Tucson
- **Coverage**: Phoenix Metro + statewide transit systems
- **Format**: Shapefile, GeoJSON, GTFS
- **Primary Sources**:
  - Valley Metro: https://www.valleymetro.org/
  - Phoenix Open Data: https://www.phoenixopendata.com/
  - Tucson Open Data: https://gisdata.tucsonaz.gov/
- **Expected Records**: 400+ stops (Phoenix Metro), additional municipal systems
- **Attributes**: Route info, stop locations, schedules, service type
- **CTCAC Use**: Public transit proximity calculations

#### 7. **Arizona Public Libraries**
- **Location**: `/Data_Sets/arizona/AZ_Libraries/`
- **Sources**: Multiple (AZGeo, ASU, UA, IMLS)
- **Coverage**: Statewide public library system
- **Format**: Shapefile, GeoJSON (compilation required)
- **Primary Sources**:
  - AZGeo Data Hub: https://azgeo-data-hub-agic.hub.arcgis.com/
  - ASU GeoData: https://lib.asu.edu/geo/data
  - UA Data Cooperative: https://data.library.arizona.edu/geo/find-data/gis-data
- **Expected Records**: ~200+ public library branches
- **Attributes**: Library name, address, services, hours
- **CTCAC Use**: Public library proximity calculations

#### 8. **Arizona Parks & Recreation**
- **Location**: `/Data_Sets/arizona/AZ_Parks_Recreation/`
- **Sources**: Arizona State Parks, Maricopa County, BLM
- **Coverage**: State parks, county parks, federal recreation areas
- **Format**: Shapefile, GeoJSON
- **Primary Sources**:
  - AZGeo Data Hub: https://azgeo-data-hub-agic.hub.arcgis.com/
  - Maricopa County: https://data-maricopa.opendata.arcgis.com/
  - BLM Arizona: https://gbp-blm-egis.hub.arcgis.com/pages/arizona
- **Expected Records**: 100+ parks and recreation facilities
- **Attributes**: Park name, acreage, facilities, activities, trails
- **CTCAC Use**: Public park proximity calculations

#### 9. **Arizona Pharmacies**
- **Location**: `/Data_Sets/arizona/AZ_Pharmacies/`
- **Sources**: Arizona State Board of Pharmacy + alternative sources
- **Coverage**: Licensed pharmacies statewide
- **Format**: Variable (license data + GIS compilation)
- **Primary Sources**:
  - State Board: https://pharmacy.az.gov/
  - Alternative: OpenStreetMap, commercial GIS providers
- **Expected Records**: ~800+ licensed pharmacies
- **Attributes**: Pharmacy name, address, license status, services
- **CTCAC Use**: Pharmacy proximity calculations

#### 10. **Arizona Grocery Stores**
- **Location**: `/Data_Sets/arizona/AZ_Grocery_Stores/`
- **Sources**: USDA Food Access (subset) + commercial sources
- **Coverage**: Grocery stores and food retail
- **Format**: Processed from federal data + commercial datasets
- **Primary Sources**:
  - USDA Food Access Research Atlas (Arizona subset)
  - Commercial: ESRI Business Analyst, Data.gov
- **Expected Records**: Variable (depends on processing)
- **Attributes**: Store name, address, type, sales volume, food access metrics
- **CTCAC Use**: Grocery store proximity calculations

## 🗺️ EXISTING ARIZONA GEOSPATIAL INFRASTRUCTURE

### Currently Available (Production Ready)
- **HUD AMI Data**: `az_counties_hud_ami_2025.gpkg`
- **Poverty Tracts**: `poverty_tracts_AZ_2022.gpkg` with styling (.qml)
- **Census Infrastructure**: TIGER/Line boundaries available

### Coordinate System Standards
- **Primary**: WGS84 (EPSG:4326) for all datasets
- **Validation**: Coordinate accuracy within Arizona state boundaries
- **Processing**: Standardized to common projection for analysis

## 📋 CTCAC INTEGRATION FRAMEWORK

### Distance Calculation Ready
All datasets structured for:
- **Property Corner Analysis**: 4-corner distance measurements
- **Radius Calculations**: 1/3, 1/2, 3/4, 1.0 mile compliance circles
- **Precision Standards**: Truncated to 2 decimal places (never rounded up)

### Map Generation Compatible
- **Scale Indicators**: Color-coded distance circles
- **Professional Output**: Developer and printable versions
- **Attribution**: Source documentation for regulatory compliance

### Data Processing Pipeline
1. **Acquisition**: Download from identified sources
2. **Validation**: Coordinate and attribute verification
3. **Standardization**: Common projection and formatting
4. **Integration**: CTCAC mapping system compatibility
5. **Documentation**: Metadata and source attribution

## 🚀 IMPLEMENTATION STATUS

### Ready for Download
- **Federal Datasets**: Automated download scripts prepared
- **Arizona Priority**: Manual download procedures documented
- **Quality Assurance**: Verification frameworks established

### Next Steps
1. Execute federal dataset downloads
2. Complete Arizona manual downloads
3. Process and standardize all datasets
4. Integrate with existing CTCAC mapping framework
5. Generate Arizona CTCAC compliance maps

## 📊 BUSINESS VALUE

### CTCAC Compliance Enhancement
- **Complete Coverage**: All required amenity categories
- **Professional Quality**: State agency authoritative sources
- **Regulatory Ready**: Court-ready documentation and citations

### Scalability Foundation
- **Template Framework**: Replicable for other states
- **Multi-Source Integration**: Federal + state + local data
- **Quality Standards**: Professional GIS analysis ready

---

**Data Status**: Phase 2 infrastructure complete, ready for systematic collection and integration with CTCAC mapping system for Arizona projects.