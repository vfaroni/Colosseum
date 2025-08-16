# 🏠 LIHTC Site Scorer

A comprehensive tool for analyzing and scoring Low-Income Housing Tax Credit (LIHTC) development sites across the United States, with enhanced Bay Area transit data integration.

## 🎯 Overview

The LIHTC Site Scorer takes GPS coordinates as input and provides comprehensive scoring based on:

- ✅ Federal QCT/DDA designations (30% basis boost qualification)
- ✅ State-specific QAP (Qualified Allocation Plan) requirements  
- ✅ Enhanced amenity proximity scoring (transit, schools, medical, grocery, etc.)
- ✅ Maximum allowable LIHTC rents by location and AMI
- ✅ Walking/driving distance calculations to key amenities
- ✅ Opportunity area designations (where applicable)
- ✅ **NEW**: Comprehensive Bay Area transit data (90,924+ stops)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- 511 Bay Area API key (optional, for enhanced transit coverage)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd CALIHTCScorer

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config/config.example.json config/config.json
# Edit config.json with your API keys
```

### Basic Usage
```python
from src.core.site_analyzer import SiteAnalyzer

# Initialize analyzer
analyzer = SiteAnalyzer()

# Analyze a site
result = analyzer.analyze_site(
    latitude=37.3897,
    longitude=-121.9927,
    state='CA'
)

# Print results
print(f"Total CTCAC Points: {result.state_scoring['total_points']}")
print(f"QCT Status: {result.federal_status['qct_qualified']}")
print(f"DDA Status: {result.federal_status['dda_qualified']}")
print(f"Transit Points: {result.amenity_analysis['amenity_breakdown']['transit']['points_earned']}")
```

### Batch Processing Usage
```python
from src.code.botn_comprehensive_processor import BOTNProcessor
from src.batch.csv_reader import CSVReader

# For processing multiple sites from CSV
csv_reader = CSVReader()
sites = csv_reader.read_sites('Sites/CostarExport_Combined.xlsx')

# Initialize BOTN processor
processor = BOTNProcessor()

# Process all sites with comprehensive analysis
results = processor.process_batch(sites)

# Generate elimination report
processor.generate_elimination_report(results, 'outputs/elimination_report.xlsx')
```

### Custom Analysis Usage  
```python
from src.code.enhanced_flood_analyzer import FloodAnalyzer
from src.code.enhanced_fire_hazard_analyzer import FireHazardAnalyzer
from src.analyzers.land_use_analyzer import LandUseAnalyzer

# Initialize specialized analyzers
flood_analyzer = FloodAnalyzer()
fire_analyzer = FireHazardAnalyzer() 
land_use_analyzer = LandUseAnalyzer()

# Analyze specific hazards
flood_risk = flood_analyzer.analyze_flood_risk(latitude, longitude)
fire_risk = fire_analyzer.analyze_fire_hazard(latitude, longitude)
land_use = land_use_analyzer.classify_land_use(address)

print(f"Flood Risk: {flood_risk['risk_level']}")
print(f"Fire Risk: {fire_risk['hazard_level']}")
print(f"Land Use: {land_use['classification']}")
```

## 🚌 Enhanced Transit Data Integration

### What's New
- **90,924 unique transit stops** across California
- **VTA GTFS data** with 3,335 Bay Area stops
- **511 Regional GTFS** with 21,024 regional stops (Caltrain, BART, all agencies)
- **Master dataset** with spatial deduplication
- **Enhanced classification** (bus stops vs rail stations)

### Getting Transit Data
```bash
# For VTA data only (no API key required)
python3 scripts/update_transit_data.py

# For full Bay Area coverage (requires free 511 API key)
# Get your key at: https://511.org/open-data/token
python3 scripts/update_transit_data_511.py YOUR_API_KEY

# Or set environment variable
export SF_511_API_KEY=YOUR_API_KEY
python3 scripts/update_transit_data_511.py

# Process CSV sites for batch analysis
python3 scripts/process_csv_sites.py Sites/CostarExport_Combined.xlsx

# Set up development environment
python3 scripts/setup_environment.py
```

### Transit Scoring
- **Bus Stops**: 3-7 points based on route density within 0.25 miles
- **Rail Stations**: 7 points within 0.5 miles
- **Detection Radius**: 3 miles for comprehensive coverage

### CTCAC 2025 4% LIHTC Amenity Scoring (Max 10 points)
- **Transit**: 3-7 points (based on density and distance)
- **Grocery/Supermarket**: 1-5 points (based on distance)
- **Public Park**: 2-3 points
- **Public Library**: 2-3 points
- **Medical Clinic/Hospital**: 2-3 points
- **Public Schools**: 2-3 points (for projects with 25%+ 3BR units)
- **Pharmacy**: 1-2 points
- **Internet Service**: 2-3 points
- **Senior Center**: 2-3 points (senior projects only)
- **Special Needs Facility**: 2-3 points (special needs projects only)

## ⚠️ CRITICAL: Mandatory Site Qualification Criteria

**NO SITE SHALL BE RECOMMENDED** unless it meets ALL four mandatory criteria:

1. ✅ **High or Highest Resource Area** (CTCAC opportunity maps)
2. ✅ **QCT or DDA Qualified** (Federal qualification required)
3. ✅ **Acceptable Land Use** (No agriculture, industrial, auto, gas, dry cleaning)
4. ✅ **Low Fire Risk** (California fire hazard mapping verification required)

### Resource Area Classifications
- 🥇 **Highest Resource**: 8 CTCAC points
- 🥈 **High Resource**: 6 CTCAC points
- 🥉 **Moderate Resource**: 4 CTCAC points
- 📍 **Low Resource**: 0 CTCAC points

### Federal Qualification Status
- 🏆 **QCT Qualified**: 30% basis boost
- 🏆 **DDA Qualified**: 30% basis boost
- 🏆 **Dual Qualified**: 30% basis boost (maximum benefit)

### Prohibited Land Uses
- ❌ Agriculture (farms, orchards, livestock)
- ❌ Industrial (manufacturing, warehousing)
- ❌ Auto-Related (dealerships, repair shops)
- ❌ Gas Stations (fuel stations, service stations)
- ❌ Dry Cleaners (chemical cleaning facilities)

### Fire Risk Assessment
- ✅ **Low Risk**: Ideal for development
- ⚠️ **Moderate Risk**: Acceptable with disclosure
- ❌ **High/Very High Risk**: **SITE DISQUALIFIED**

## 📁 Project Structure

### ✅ **Reorganized for Best Practices**
The BOTN Engine follows Python project best practices with clear separation of concerns:

**🏗️ Code Organization Philosophy:**
- **`src/code/`**: Business logic & processing modules (algorithms, analysis engines)
- **`src/core/`**: Framework modules (stable interfaces, core functionality)  
- **`src/analyzers/`**: Specialized analysis modules (domain-specific logic)
- **`scripts/`**: Utility & automation scripts (command-line tools, setup)
- **`tests/`**: Complete test suite organized by type and purpose
- **`Sites/`**: Data files only (no mixed code files)

```
botn_engine/
├── src/                    # Source code
│   ├── code/              # ✅ **NEW**: Business logic & processing modules
│   │   ├── __init__.py           # Package initialization
│   │   ├── botn_comprehensive_processor.py # Main BOTN processing engine
│   │   ├── enhanced_flood_analyzer.py # Flood risk analysis algorithms
│   │   ├── enhanced_fire_hazard_analyzer.py # Fire hazard assessment
│   │   ├── coordinate_checker.py # GPS validation & processing
│   │   ├── multi_source_flood_analyzer.py # Multi-source flood data
│   │   ├── batch_hazard_processor.py # Batch hazard processing
│   │   ├── analyze_oakmead.py    # Site-specific analysis examples
│   │   └── ... (20+ processing modules)
│   ├── core/              # Core framework modules
│   │   ├── site_analyzer.py      # Main analysis engine ✅
│   │   └── coordinate_validator.py # GPS validation ✅
│   ├── analyzers/         # Specialized analysis modules
│   │   ├── qct_dda_analyzer.py   # Federal qualification ✅
│   │   ├── qap_analyzer.py       # State-specific scoring ✅
│   │   ├── amenity_analyzer.py   # Enhanced proximity analysis ✅
│   │   ├── rent_analyzer.py      # LIHTC rent calculations ✅
│   │   ├── fire_hazard_analyzer.py # Fire risk assessment ✅
│   │   └── land_use_analyzer.py  # Land use classification ✅
│   ├── batch/             # Batch processing modules
│   │   ├── batch_processor.py    # Batch analysis engine
│   │   ├── batch_reporter.py     # Batch reporting
│   │   └── csv_reader.py         # CSV data processing
│   └── utils/             # Utility functions
│       └── report_generator.py   # JSON export ✅
├── tests/                 # ✅ **REORGANIZED**: Complete test suite
│   ├── unit/              # Unit tests
│   │   ├── test_enhanced_reader.py
│   │   ├── test_excel_reader.py
│   │   ├── test_batch_processor.py
│   │   ├── test_batch_reporter.py
│   │   └── test_csv_reader.py
│   ├── integration/       # Integration tests
│   │   ├── test_csv_batch_integration.py
│   │   ├── test_flood_elimination.py
│   │   ├── test_land_use_integration.py
│   │   ├── test_openfema_api.py
│   │   └── hazard_validation_test.py
│   └── sample_data/       # Test data files
│       ├── test_sites.csv
│       ├── test_sites.xlsx
│       └── invalid_sites.csv
├── Sites/                 # ✅ **CLEANED**: Data files only
│   ├── *.xlsx            # CoStar export files & BOTN results
│   ├── archive/          # Archived data files
│   └── hazard_analysis_outputs/ # Analysis output data
├── scripts/               # ✅ Utility & automation scripts
│   ├── update_transit_data.py # VTA GTFS downloader
│   ├── update_transit_data_511.py # Enhanced regional updater
│   ├── process_csv_sites.py # CSV batch processing utility
│   └── setup_environment.py # Environment configuration
├── data/                  # Reference data storage
│   ├── transit/          # Enhanced transit datasets
│   │   ├── vta_transit_stops.geojson # VTA stops
│   │   ├── 511_regional_transit_stops.geojson # Regional
│   │   └── california_transit_stops_master.geojson # Master
│   ├── qap/              # State QAP documents
│   ├── rents/            # LIHTC rent data
│   ├── amenities/        # Amenity datasets
│   ├── boundaries/       # Geographic boundaries
│   └── cache/            # Cached API responses
├── outputs/               # Analysis outputs & reports
├── docs/                  # Documentation
├── contracts/             # Legal agreements
├── config/                # Configuration files
└── examples/              # Usage examples
```

## 🛠️ Configuration

### Data Sources
The system uses the following authoritative data repository:
**Primary Data Source**: `/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets`

### Configuration File (`config/config.json`)
```json
{
  "data_sources": {
    "base_path": "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets",
    "federal": {
      "qct_dda_path": "federal/HUD_QCT_DDA_Data/HUD QCT DDA 2025 Merged.gpkg"
    },
    "california": {
      "opportunity_areas": "california/CA_CTCAC_2025_Opp_MAP_shapefile/final_opp_2025_public.gpkg",
      "transit_stops_enhanced": "/path/to/california_transit_stops_master.geojson",
      "schools": "california/CA_Public Schools/SchoolSites2324_661351912866317522.gpkg",
      "medical": "california/CA_Hospitals_Medical/Licensed_and_Certified_Healthcare_Facilities.geojson"
    }
  },
  "analysis_settings": {
    "amenity_search_radius_miles": 3.0,
    "hqta_proximity_miles": 0.25,
    "cache_enabled": true
  }
}
```

## 📊 Supported States

### Fully Implemented
- **California (CTCAC)**: Complete amenity scoring, opportunity areas, enhanced transit
- **Texas (TDHCA)**: QCT/DDA analysis, rural designations
- **New York**: Basic QAP compliance

### Federal Analysis Available
- All 50 states + DC: QCT/DDA verification and basic scoring

## 🧪 Testing

### Basic Functionality Test
```bash
# Test core analyzer import
python3 -c "from src.core.site_analyzer import SiteAnalyzer; print('✅ Core analyzer import successful')"

# Test business logic imports
python3 -c "from src.code.botn_comprehensive_processor import BOTNProcessor; print('✅ BOTN processor import successful')"

# Test batch processing imports
python3 -c "from src.batch.csv_reader import CSVReader; print('✅ CSV reader import successful')"
```

### Run Unit Tests
```bash
# Run all unit tests
python3 -m pytest tests/unit/ -v

# Run specific test modules
python3 -m pytest tests/unit/test_batch_processor.py -v
python3 -m pytest tests/unit/test_enhanced_reader.py -v
python3 -m pytest tests/unit/test_csv_reader.py -v
```

### Run Integration Tests
```bash
# Run all integration tests
python3 -m pytest tests/integration/ -v

# Run specific integration tests
python3 -m pytest tests/integration/test_flood_elimination.py -v
python3 -m pytest tests/integration/test_land_use_integration.py -v
python3 -m pytest tests/integration/hazard_validation_test.py -v
```

### Full Analysis Test (Test Site: 1205 Oakmead Parkway, Sunnyvale)
```bash
python3 -c "
from src.core.site_analyzer import SiteAnalyzer
analyzer = SiteAnalyzer()
result = analyzer.analyze_site(37.3897, -121.9927, state='CA')
federal = result.federal_status
scoring = result.state_scoring
print(f'QCT: {federal.get(\"qct_qualified\")}')
print(f'DDA: {federal.get(\"dda_qualified\")}')
print(f'Basis Boost: {federal.get(\"basis_boost_percentage\")}%')
print(f'CTCAC Points: {scoring.get(\"total_points\")}/30')
print(f'Resource Category: {scoring.get(\"resource_category\")}')
"
```

### Test with Sample Data
```bash
# Test CSV reading with sample data
python3 -c "
from src.batch.csv_reader import CSVReader
reader = CSVReader()
sites = reader.read_sites('tests/sample_data/test_sites.csv')
print(f'✅ Successfully loaded {len(sites)} test sites')
"

# Test BOTN processing with sample data
python3 -c "
from src.code.botn_comprehensive_processor import BOTNProcessor
processor = BOTNProcessor()
# Process using test data
processor.process_test_sites('tests/sample_data/test_sites.xlsx')
print('✅ BOTN test processing completed')
"
```

### Expected Test Output
```
QCT: False
DDA: True
Basis Boost: 30.0%
CTCAC Points: 21/30
Resource Category: High Resource
```

## 📈 Example Analysis Output

### Test Site Results: 1205 Oakmead Parkway, Sunnyvale CA 94085

```json
{
  "site_info": {
    "latitude": 37.3897,
    "longitude": -121.9927,
    "census_tract": "06085508708",
    "state": "CA"
  },
  "federal_status": {
    "qct_qualified": false,
    "dda_qualified": true,
    "basis_boost_percentage": 30.0,
    "analysis_notes": "Site qualifies for 30% basis boost as DDA: San Jose-Sunnyvale-Santa Clara, CA HUD Metro FMR Area"
  },
  "state_scoring": {
    "total_points": 21,
    "max_possible_points": 30,
    "resource_category": "High Resource",
    "opportunity_area_points": 6,
    "scoring_breakdown": {
      "opportunity_area_points": 6,
      "amenity_points": 15,
      "transit_points": 0,
      "federal_bonus": 0
    }
  },
  "amenity_analysis": {
    "total_amenity_points": 24,
    "amenity_breakdown": {
      "transit": {
        "points_earned": 15,
        "details": [
          {"name": "Lawrence & Oakmead", "distance": 0.21, "points_earned": 5},
          {"name": "Duane & Lawrence", "distance": 0.29, "points_earned": 5}
        ]
      },
      "schools": {
        "points_earned": 6,
        "details": [
          {"name": "Fairwood Elementary", "distance": 0.48, "points_earned": 3}
        ]
      }
    },
    "nearby_amenities": {
      "transit": [
        {
          "name": "Lawrence & Oakmead",
          "type": "bus_stop",
          "distance_miles": 0.21,
          "agency": "VTA"
        }
      ]
    }
  },
  "competitive_summary": {
    "total_points": 21,
    "competitive_tier": "On Hold",
    "mandatory_criteria_met": false,
    "disqualifying_factors": [
      "Fire hazard status unknown - manual verification required"
    ]
  }
}
```

## 🔧 Critical Technical Notes

### HUD QCT/DDA Data - Correct File Paths
**✅ CORRECT FILE**: `HUD QCT DDA 2025 Merged.gpkg`
- Size: 154.7 MB  
- Records: 18,685 total (15,727 QCT + 2,958 DDA)
- California QCT: 1,757 features

### Dual Qualification Logic (Fixed)
Sites can qualify for both QCT and DDA simultaneously. The system correctly checks both:
```python
# CORRECT - always check both:
if self.qct_data is not None:
    # Check QCT qualification
    
if self.dda_data is not None:  # No mutual exclusivity
    # Check DDA qualification
```

### Proven Geospatial Patterns
```python
import geopandas as gpd
from shapely.geometry import Point

# Load and standardize CRS
gdf = gpd.read_file(file_path)
if gdf.crs != 'EPSG:4326':
    gdf = gdf.to_crs('EPSG:4326')

# Spatial intersection
point = Point(longitude, latitude)
intersects = gdf[gdf.contains(point)]
```

## 📊 Transit Enhancement Results

### Before Enhancement
- **Transit Stops Found**: 0
- **Transit Points**: 0
- **Issue**: No transit connectivity detected

### After Enhancement  
- **Transit Stops Found**: 475 within 3 miles of test site
- **Transit Points**: 15 points earned
- **Coverage**: VTA buses, light rail, and regional connections
- **Master Dataset**: 90,924 unique stops statewide

### Data Sources Used
- **VTA GTFS**: 3,335 stops (Santa Clara Valley Transportation Authority)
- **511 Regional GTFS**: 21,024 stops (all Bay Area agencies)
- **California Statewide**: 264,311 stops (baseline coverage)
- **Final Deduplicated**: 90,924 unique transit stops

## 🚀 Roadmap

### Phase 1 (Completed ✅)
- ✅ Core analysis engine
- ✅ California (CTCAC) complete implementation
- ✅ Federal QCT/DDA verification with real HUD data
- ✅ Enhanced transit data integration (90,924+ stops)
- ✅ Dual qualification logic fixes
- ✅ JSON export functionality

### Phase 2 (Next 3 months)
- 🔄 Complete fire hazard data integration
- 🔄 Land use verification system
- 🔄 API endpoints for external integration
- 🔄 Enhanced reporting (PDF exports)
- 🔄 Batch processing capabilities

### Phase 3 (Future)
- 📋 Web interface
- 📋 Database integration
- 📋 Machine learning scoring enhancements
- 📋 Real-time data feeds
- 📋 Multi-state expansion

## 👨‍💻 Developer Guide

### Adding New Processing Modules
```bash
# Create new business logic in src/code/
touch src/code/my_new_processor.py

# Add corresponding tests
touch tests/unit/test_my_new_processor.py
touch tests/integration/test_my_new_integration.py

# Add sample data if needed
touch tests/sample_data/my_test_data.csv
```

### Adding New Utility Scripts
```bash
# Create automation scripts in scripts/
touch scripts/my_utility_script.py

# Make executable
chmod +x scripts/my_utility_script.py

# Follow naming convention: action_subject.py
# Examples: update_transit_data.py, process_csv_sites.py
```

### Directory Guidelines
- **`src/code/`**: Put all processing algorithms, analysis engines, data processors
- **`src/core/`**: Only framework-level, stable interface modules
- **`src/analyzers/`**: Domain-specific analysis modules (QCT, amenity, fire, etc.)
- **`scripts/`**: Command-line utilities, data downloaders, environment setup
- **`tests/unit/`**: Fast, isolated tests for individual functions/classes
- **`tests/integration/`**: Tests that require multiple components or external data
- **`tests/sample_data/`**: Test data files (keep small)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the directory structure guidelines above
4. Add your changes to appropriate directories (`src/code/` vs `scripts/`)
5. Add comprehensive tests in `tests/unit/` or `tests/integration/`
6. Ensure all tests pass (`python3 -m pytest tests/ -v`)
7. Submit a pull request

## 📄 License

This project is proprietary software. See `contracts/` folder for licensing agreements.

## 🆘 Support

For technical support or questions:
- Create an issue in the repository
- Review documentation in `docs/`
- Check example usage in `examples/`

---

**Built for LIHTC developers, by LIHTC experts.**  
**Enhanced with comprehensive Bay Area transit data integration.**

*Last Updated: January 2025*  
*Transit Enhancement: 90,924 unique stops integrated*  
*Test Site: 1205 Oakmead Parkway, Sunnyvale CA 94085*