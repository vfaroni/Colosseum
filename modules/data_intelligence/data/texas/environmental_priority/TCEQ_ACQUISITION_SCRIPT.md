
# TCEQ Priority Data Acquisition Script
# Generated: 2025-08-09T14:50:26.057453
# Purpose: Acquire missing databases for 90% coverage

## PRIORITY 1: CRITICAL DATABASES (Deal Killers)

### 1. State Superfund Sites
- URL: https://www.tceq.texas.gov/remediation/superfund/sites
- Method: Web scraping or manual download
- Look for: Site list with addresses and status
- Expected: ~500 sites

### 2. Voluntary Cleanup Program (VCP)
- URL: https://www.tceq.texas.gov/remediation/vcp/vcp-sites  
- Method: Check for downloadable list or API
- Look for: VCP ID, site name, address, status
- Expected: ~1,000 sites

### 3. RCRA Corrective Action
- URL: https://www.tceq.texas.gov/permitting/waste_permits/ihw_permits/ihw_ca.html
- Method: May require EPA RCRA Info crosswalk
- Look for: Facility ID, corrective action status
- Expected: ~2,000 facilities

### 4. Active LUST Sites
- URL: https://www.tceq.texas.gov/remediation/pst/pst_lists.html
- Method: Direct download if available
- Look for: LPST number, address, status, closure date
- Expected: ~5,000 active sites

## PRIORITY 2: HIGH VALUE DATABASES

### 5. UST/AST Registry
- URL: https://www.tceq.texas.gov/remediation/pst/registered_tanks.html
- Method: Database query or bulk download
- Look for: Tank ID, facility, registration status
- Expected: ~20,000 tanks

### 6. Municipal Solid Waste Landfills
- URL: https://www.tceq.texas.gov/permitting/waste_permits/msw_permits/msw_data.html
- Method: Excel/CSV download
- Look for: Permit number, location, status, type
- Expected: ~2,000 facilities

### 7. Brownfields
- URL: https://www.tceq.texas.gov/remediation/brownfields
- Method: Site list or database query
- Look for: Site ID, address, contaminants, status
- Expected: ~500 sites

### 8. Spills Database
- URL: https://www.tceq.texas.gov/remediation/spills
- Method: May require formal data request
- Look for: Incident ID, location, material, date
- Expected: ~10,000 incidents

## ALTERNATIVE DATA SOURCES

### TCEQ Data Download Site
- URL: https://www.tceq.texas.gov/agency/data/download-data
- Check for bulk downloads and GIS data

### Texas Open Data Portal
- URL: https://data.texas.gov/
- Search for TCEQ environmental datasets

### EPA Envirofacts (Texas subset)
- URL: https://enviro.epa.gov/
- Can filter for Texas facilities

## MANUAL ACQUISITION STEPS

1. Visit each URL and look for:
   - "Download Data" links
   - "Export to Excel/CSV" options
   - "GIS Data" or "Shapefile" downloads
   - API documentation

2. If no direct download:
   - Check for data request forms
   - Look for FOIA/Public Information Request process
   - Contact TCEQ data team: datahelp@tceq.texas.gov

3. For web-only data:
   - Use web scraping tools (BeautifulSoup, Selenium)
   - Consider semi-automated extraction
   - Verify data quality after scraping

## GEOCODING REQUIREMENTS

All databases need addresses geocoded:
- Use Census geocoder for batch processing
- Fallback to PositionStack API
- Target: 90%+ geocoding success rate

## INTEGRATION CHECKLIST

[ ] Download raw data files
[ ] Standardize column names
[ ] Geocode addresses
[ ] Remove duplicates
[ ] Link to existing 797K records
[ ] Create unified Texas database
[ ] Generate risk scores
[ ] Test BOTN integration
        