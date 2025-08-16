# KCEC Weather Data Collection System - Project Handoff Summary

## Project Overview
This project implements an automated weather data collection system for KCEC (Jack McNamara Field Airport) in Crescent City, California. The system tracks daily precipitation with specific thresholds for construction planning and contract documentation.

## Key Components

### 1. Data Source
- **Station**: CRESCENT CITY MCNAMARA AIRPORT (KCEC)
- **NOAA Station ID**: GHCND:USW00024286
- **Location**: 41.78361°N, 124.23796°W
- **API**: NOAA Climate Data Online (CDO)
- **API Token**: `oaLvXPjjAWoSCizEBvNoHPNhATmdDmQA`

### 2. Precipitation Thresholds
The system tracks four specific precipitation categories:
- **Measurable**: ≥0.01" (any measurable precipitation)
- **Moderate**: ≥0.25" (likely work delays)
- **Heavy**: ≥0.5" (definite work delays)
- **Very Heavy**: ≥1.0" (major work impacts)

### 3. Google Sheet Integration
- **URL**: https://docs.google.com/spreadsheets/d/1sVo6MOtIwqX2_0nxANHnkOODQnUvzlCSynr91ORI1Ms/edit
- **Sheet ID**: `1sVo6MOtIwqX2_0nxANHnkOODQnUvzlCSynr91ORI1Ms`
- **Permissions**: Anyone with link can edit
- **Contains**: Historical data from May 1, 2024 to present

### 4. n8n Automation Workflow
- **File**: `n8n_kcec_corrected_final.json`
- **Daily Schedule**: 9:00 AM PT - Collects previous day's weather data
- **Weekly Schedule**: Monday 9:15 AM PT - Sends summary email report

### 5. Email Recipients
Weekly reports are sent to:
- bill@synergycdc.org
- carmenjohnston67@gmail.com
- duane.henry@stepforwardcommunities.com

## Data Collection Details

### Daily Data Points
- **Date**: Collection date
- **Total_Inches**: Daily precipitation total
- **Category**: None/Trace/Light/Moderate/Heavy/Very Heavy
- **Threshold Flags**: Yes/No for each threshold level
- **Temperature**: Max/Min in Fahrenheit
- **Wind**: Average speed in MPH
- **Work_Suitable**: Yes/No based on conditions
- **Weather_Delay_Likely**: Yes/No (triggered at ≥0.25")

### Historical Data Summary (May 2024 - June 2025)
- **Total Precipitation**: 67.54 inches
- **Days with Measurable Rain**: 30.2%
- **Days with Work-Impacting Rain (≥0.25")**: 17.8%
- **Days Suitable for Outdoor Work**: 64.4%
- **Maximum Daily Rainfall**: 2.61 inches

## Technical Implementation

### Python Scripts
1. **`kcec_corrected_historical.py`**: Backfills historical data with proper conversions
2. **`kcec_n8n_simple.py`**: Standalone script for n8n Execute Command node
3. **`setup_kcec_weather.py`**: Initial setup and configuration script

### Data Conversions (CORRECTED)
- **Precipitation**: NOAA provides data in inches with units=standard (no conversion needed)
- **Temperature**: NOAA provides data in Fahrenheit with units=standard (no conversion needed)
- **Wind Speed**: Convert from m/s to mph (multiply by 2.237)

### Known Issues Resolved
1. ✅ Fixed incorrect station ID (was pulling Cincinnati, KY data)
2. ✅ Fixed temperature double-conversion (was treating F as C)
3. ✅ Fixed precipitation over-conversion (values are already in inches)

## Setup Instructions for n8n

### 1. Import Workflow
- Open n8n interface
- Go to Workflows → Import
- Upload `n8n_kcec_corrected_final.json`

### 2. Configure Google Sheets OAuth
- Click on any Google Sheets node
- Add credentials → Google Sheets OAuth2
- Sign in with Google account
- Grant permissions for Sheets access

### 3. Configure Gmail OAuth
- Click on the email node
- Add credentials → Gmail OAuth2
- Sign in with Google account
- Grant permissions for sending emails

### 4. Google Workspace Admin (if needed)
- Enable API access in admin.google.com
- Configure OAuth consent screen as Internal
- Add required scopes for Sheets and Gmail
- Trust n8n as third-party app if prompted

### 5. Activate Workflow
- Toggle workflow to "Active" status
- Test with manual execution first
- Verify data appears in Google Sheet
- Confirm email delivery works

## Weekly Email Report Features
- **HTML formatted** with professional styling
- **Visual alerts** for high precipitation weeks
- **Statistics grid** showing key metrics
- **Precipitation categories table** with work impact indicators
- **Daily breakdown** with color-coded impact assessment
- **Summary section** with temperature and work suitability percentages
- **Direct link** to Google Sheet for full data access

## Maintenance Notes

### Regular Checks
- Verify NOAA API token remains valid
- Monitor Google Sheet for daily data additions
- Confirm weekly emails are being received
- Check n8n execution logs for any errors

### Data Quality
- NOAA data typically has 1-2 day delay
- Missing data points show as null values
- Temperature/wind data may not always be available
- Precipitation is the most reliable data point

### Future Enhancements
- Add seasonal precipitation comparisons
- Include year-over-year analysis
- Create monthly summary reports
- Add SMS alerts for heavy rain events
- Integrate with project management systems

## Contact Information
**Project Lead**: Bill Rice (bill@synergycdc.org)
**Technical Implementation**: Completed June 2025
**Documentation**: This handoff summary

## File Inventory
```
/Crescent_City_Rainfall/
├── PROJECT_HANDOFF_SUMMARY.md (this file)
├── n8n_kcec_corrected_final.json (n8n workflow)
├── kcec_corrected_historical.py (historical data script)
├── kcec_corrected_historical_2024-05-01_to_2025-06-11.csv (data file)
├── kcec_n8n_simple.py (standalone script)
├── setup_kcec_weather.py (setup script)
├── config.json (configuration with API key)
└── .gitignore (excludes sensitive files)
```

## Success Metrics
- ✅ Daily precipitation data collection accuracy
- ✅ Weekly email delivery to all recipients
- ✅ Google Sheet updates without errors
- ✅ Proper categorization of precipitation levels
- ✅ Accurate work impact assessments

---

*System operational as of June 2025 with corrected KCEC station data and proper unit conversions.*