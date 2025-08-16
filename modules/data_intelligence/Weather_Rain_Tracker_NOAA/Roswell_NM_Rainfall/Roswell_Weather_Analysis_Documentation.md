# Roswell, NM Weather Analysis System

**Project Date**: June 25, 2025  
**Location**: Roswell, New Mexico (33°22'25.5"N 104°32'28.0"W)  
**NOAA Station**: USW00023009 (Roswell Industrial Air Park)  
**Data Period**: July 1, 2024 to present  

## Project Overview

This project creates a comprehensive weather analysis system for Roswell, NM, adapted from the existing KCEC (Crescent City) Battery Point weather tracking system. The system downloads precipitation, temperature, and wind data from NOAA's GHCN database and formats it for construction contract analysis and general weather tracking.

## What We Built

### Core System: `roswell_weather_analyzer.py`
A complete weather data analysis tool that:

1. **Downloads Weather Data** from NOAA API using GHCN station USW00023009
2. **Processes Multiple Weather Variables**:
   - Daily precipitation (inches)
   - High temperature (°F)
   - Low temperature (°F)
   - Average wind speed (mph)
3. **Calculates Rainfall Thresholds** for construction/contract analysis:
   - Any precipitation (≥0.01")
   - Contract threshold (≥0.10")
   - Normal rain (≥0.25")
   - Heavy rain (≥0.50")
   - Very heavy rain (≥1.00")
4. **Integrates Holiday Data** (Federal + New Mexico state holidays)
5. **Exports to Excel** with professional formatting

### Key Features
- **Exact KCEC Format Compliance**: Uses identical 25-column structure for consistency
- **Monthly Data Chunking**: Avoids NOAA API limits by downloading in monthly segments
- **Complete Date Coverage**: Fills gaps with zero precipitation for missing dates
- **Holiday Integration**: Includes both federal and New Mexico-specific holidays
- **Professional Excel Output**: Formatted tables with headers, borders, and styling

## Technical Implementation

### NOAA Station Selection Process
1. **Target Coordinates**: 33°22'25.5"N 104°32'28.0"W (eastern New Mexico)
2. **Station Research**: Identified Roswell International Air Center as closest option
3. **Station Verification**: USW00023009 located ~5 miles from target coordinates
4. **Data Validation**: Confirmed active GHCN station with complete weather variables

### Data Architecture
The system uses NOAA's Climate Data Online (CDO) API v2 with these parameters:
- **Dataset**: GHCND (Global Historical Climatology Network Daily)
- **Station**: USW00023009 (Roswell Industrial Air Park)
- **Data Types**: PRCP, TMAX, TMIN, AWND
- **Units**: Standard (inches, °F, mph)
- **Rate Limiting**: 1-second delays between API calls

### Holiday System
**Federal Holidays**: Standard US federal holiday calendar
**New Mexico State Holidays**: 
- All federal holidays plus:
- Statehood Day (August 9th - commemorating 1912 statehood)
- Day After Thanksgiving (state employee holiday)

## Excel Output Structure (25 Columns)

| Column | Name | Description |
|--------|------|-------------|
| 1 | Date | M/D/YY format |
| 2 | Year | 4-digit year |
| 3 | Month | Month number (1-12) |
| 4 | Day | Day of month |
| 5 | Month_Name | Full month name |
| 6 | Day_of_Week | Full day name |
| 7 | Total_Inches | Daily precipitation |
| 8 | High_Temp_F | Daily high temperature |
| 9 | Low_Temp_F | Daily low temperature |
| 10 | Avg_Wind_MPH | Average wind speed |
| 11 | Category | Rain category (Light/Moderate/Heavy/Very Heavy) |
| 12 | Measurable_0.01 | Binary flag for ≥0.01" |
| 13 | Contract_0.10 | Binary flag for ≥0.10" |
| 14 | Normal_0.25 | Binary flag for ≥0.25" |
| 15 | Heavy_0.50 | Binary flag for ≥0.50" |
| 16 | Light_0.01 | Binary flag for 0.01-0.25" |
| 17 | Moderate_0.25 | Binary flag for 0.25-0.50" |
| 18 | Heavy_0.5 | Binary flag for 0.50-1.0" |
| 19 | Very_Heavy_1.0 | Binary flag for ≥1.0" |
| 20 | Work_Suitable | Binary flag for <0.50" (work suitability) |
| 21 | Timestamp | ISO format processing timestamp |
| 22 | Federal_Holiday | Binary flag for federal holidays |
| 23 | Federal_Holiday_Name | Federal holiday name |
| 24 | NM_State_Holiday | Binary flag for NM state holidays |
| 25 | NM_State_Holiday_Name | NM state holiday name |

## Usage Instructions

### Prerequisites
```bash
pip install pandas requests openpyxl
```

### Running the Analysis
```bash
cd "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code"
python3 roswell_weather_analyzer.py
```

### Output Files
- **Excel File**: `Roswell_rainfall_YYYY-MM-DD_to_YYYY-MM-DD_YYYYMMDD_HHMMSS_WER.xlsx`
- **Location**: Same directory as script
- **Format**: Professional Excel workbook with formatted headers and data

## Replicating for Other Locations

### Step 1: Find NOAA Weather Station
1. **Identify Target Coordinates**: Get precise lat/lng for your location
2. **Search NOAA Stations**: Use NOAA's station finder at https://www.ncei.noaa.gov/cdo-web/datatools/findstation
3. **Verify Station Type**: Look for GHCND stations (Global Historical Climatology Network Daily)
4. **Check Data Availability**: Ensure station has PRCP, TMAX, TMIN, and AWND data
5. **Distance Assessment**: Stations within 20-30 miles typically provide good weather representation

### Step 2: Adapt the Code
**Key Variables to Change**:
```python
# Station ID (most important change)
self.station_id = "GHCND:USW00023009"  # Replace with your station

# Start date (adjust as needed)
start_date = "2024-07-01"  # Change to desired start date

# State holidays (adapt for your state)
def get_state_holidays(self):
    # Replace New Mexico holidays with your state's holidays
```

### Step 3: State Holiday Research
Each state has different holiday observances:
- **Research State Government Holidays**: Check your state's official website
- **Common State-Specific Holidays**: 
  - Texas: Confederate Heroes Day, Texas Independence Day
  - California: César Chávez Day, Day After Thanksgiving
  - New Mexico: Statehood Day, Day After Thanksgiving
- **Update Holiday Dictionary**: Replace NM holidays with your state's holidays

### Step 4: Test and Validate
1. **Run Small Date Range First**: Test with 1-2 months of data
2. **Verify Station Data**: Check that temperature and wind data are available
3. **Validate Holiday Calendar**: Ensure holidays are correctly identified
4. **Compare with Local Weather**: Spot-check a few days against local weather reports

## NOAA API Configuration

### Required API Token
- **Obtain Token**: Register at https://www.ncdc.noaa.gov/cdo-web/token
- **Rate Limits**: 1,000 requests per day for free accounts
- **Usage Pattern**: This script uses ~12-24 requests for a full year of data

### API Parameters Reference
```python
params = {
    "datasetid": "GHCND",           # Global Historical Climatology Network Daily
    "stationid": "GHCND:USW00023009", # Your station ID
    "datatypeid": "PRCP,TMAX,TMIN,AWND", # Data types needed
    "startdate": "2024-07-01",      # Start date (YYYY-MM-DD)
    "enddate": "2024-07-31",        # End date (YYYY-MM-DD)
    "units": "standard",            # Returns inches, °F, mph
    "limit": 1000                   # Records per request
}
```

## Common Station Types and Codes

### Airport Stations (Most Reliable)
- **Format**: USW00023009 (US Weather station)
- **Advantages**: Automated equipment, complete data coverage, professional maintenance
- **Examples**: Major airports, military bases, weather service offices

### Cooperative Observer Stations
- **Format**: USC00297612 (US Cooperative station)
- **Advantages**: Long historical records, precipitation focus
- **Limitations**: May lack temperature/wind data

### Climate Reference Network
- **Format**: USR0000XXXX (Research quality stations)
- **Advantages**: Highest quality data, research-grade instruments
- **Limitations**: Limited geographic coverage

## Best Practices for Site Selection

### Distance Considerations
- **≤10 miles**: Excellent representation for local weather
- **10-30 miles**: Good representation, especially for airports
- **30-50 miles**: Acceptable if similar elevation/terrain
- **>50 miles**: Use caution, verify climate similarity

### Terrain and Climate Factors
- **Elevation Differences**: <1,000ft typically acceptable
- **Climate Zones**: Stay within same Köppen climate classification
- **Geographic Features**: Avoid crossing major mountain ranges or large water bodies
- **Urban Heat Islands**: Airport stations often avoid UHI effects

## Troubleshooting Common Issues

### API Rate Limiting
- **Problem**: "Too many requests" errors
- **Solution**: Increase sleep time between requests (currently 1 second)
- **Alternative**: Use larger date chunks but request fewer data types per call

### Missing Data Handling
- **Temperature/Wind**: Script handles None values gracefully
- **Precipitation**: Missing values default to 0.0 inches
- **Data Gaps**: Check NOAA station status for equipment outages

### Date Format Issues
- **Excel Date Column**: Uses M/D/YY format (matching KCEC)
- **API Dates**: Always use YYYY-MM-DD format
- **Timezone**: NOAA data is in local standard time

### Holiday Calendar Updates
- **Annual Updates**: Federal holidays change dates annually
- **State Changes**: Monitor state government websites for holiday modifications
- **Observed Dates**: Account for when holidays fall on weekends

## File Organization Recommendations

### Directory Structure
```
Weather_Rain_Tracker_NOAA/
├── [Location_Name]_Rainfall/
│   ├── [location]_weather_analyzer.py
│   ├── config.json (NOAA API token)
│   ├── [Location]_Weather_Analysis_Documentation.md
│   └── output/
│       └── [Location]_rainfall_[dates]_[timestamp]_WER.xlsx
```

### Naming Conventions
- **Scripts**: `[location]_weather_analyzer.py`
- **Output Files**: `[Location]_rainfall_[start-date]_to_[end-date]_[timestamp]_WER.xlsx`
- **Documentation**: `[Location]_Weather_Analysis_Documentation.md`

## Integration with Construction/Contract Analysis

### Contract Rain Days
- **Standard Threshold**: 0.10" (Contract_0.10 column)
- **Work Stoppage**: Typically 0.50" or higher
- **Monthly Summaries**: Sum binary columns for monthly rain day counts

### Seasonal Pattern Analysis
- **Data Export**: Excel format allows pivot tables and charts
- **Trend Analysis**: Multi-year data enables seasonal pattern identification
- **Risk Assessment**: Historical percentiles help estimate future rain probabilities

## Future Enhancements

### Potential Additions
1. **Multi-Station Analysis**: Compare nearby stations for data validation
2. **Historical Baseline**: Extend data back 10-30 years for climate context
3. **Extreme Weather Alerts**: Flag unusual weather events
4. **Monthly/Annual Summaries**: Pre-calculated summary statistics
5. **Web Dashboard**: Streamlit/Dash interface for interactive analysis

### Data Source Diversification
- **Backup Stations**: Identify secondary stations for redundancy
- **Satellite Data**: Integrate NOAA precipitation radar data
- **Local Weather Networks**: CoCoRaHS, Weather Underground personal stations
- **Climate Projections**: NOAA climate models for future trend analysis

---

## Contact and Support

For questions about adapting this system for other locations or technical issues:
- **NOAA CDO API Documentation**: https://www.ncei.noaa.gov/cdo-web/webservices/v2
- **Station Finder Tool**: https://www.ncei.noaa.gov/cdo-web/datatools/findstation
- **GHCN Database Info**: https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily

**Created**: June 25, 2025  
**System**: Adapted from KCEC Battery Point Weather Analysis System  
**Purpose**: Construction contract weather analysis and general meteorological tracking