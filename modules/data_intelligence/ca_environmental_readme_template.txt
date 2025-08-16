DATASET: California Environmental Sites - [COUNTY] County
SOURCE: Multiple California Environmental Databases
SOURCE DATE: 2025-08-09
DOWNLOAD DATE: 2025-08-09
DESCRIPTION: Comprehensive environmental contamination data including FEMA flood zones, EnviroStor cleanup sites, GeoTracker LUST/SLIC sites, EPA Superfund locations, and dry cleaner registrations
FORMAT: CSV, GeoJSON
RECORDS: [AUTO-POPULATE]
COVERAGE: [COUNTY] County, California
UPDATE FREQUENCY: Quarterly (FEMA), Monthly (EnviroStor/GeoTracker), Annual (EPA)
NOTES: Data filtered from statewide databases to county boundaries. Coordinates in WGS84 (EPSG:4326). For LIHTC environmental screening per ASTM E1527-21 standards.

FILE INVENTORY:
- [COUNTY]_fema_flood.geojson - FEMA National Flood Hazard Layer zones
- [COUNTY]_envirostor.csv - DTSC EnviroStor cleanup sites  
- [COUNTY]_lust.csv - GeoTracker Leaking Underground Storage Tank sites
- [COUNTY]_slic.csv - GeoTracker Spills, Leaks, Investigation & Cleanup sites
- [COUNTY]_metadata.json - Processing metadata and statistics

PROCESSING NOTES:
- Downloaded via Colosseum LIHTC Platform automated collection system
- Part of 19-county California environmental intelligence initiative
- Integrated with 10M+ parcel database for property-level analysis
- Quality validated before production deployment