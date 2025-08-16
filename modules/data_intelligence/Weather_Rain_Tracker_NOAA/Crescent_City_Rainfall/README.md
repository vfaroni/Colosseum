# KCEC Weather Data Excel Export System

## Overview
This system automatically downloads weather data from NOAA and creates Excel exports that match your existing Battery Point contract spreadsheet format exactly. Perfect for construction site weather tracking and contract compliance.

## Quick Start (Regular Use)

### Get Latest Weather Data
```bash
cd "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Weather_Rain_Tracker_NOAA/Crescent_City_Rainfall"
python3 update_kcec_data.py
```

This creates a new Excel file with the latest weather data that you can copy/paste into your existing spreadsheet.

### Interactive Menu (More Options)
```bash
python3 kcec_excel_export.py
```

Choose from:
1. Export existing complete dataset to Excel format
2. Download and export recent data (last 30 days)
3. Export specific date range
4. Update with latest data (last 7 days)

## Setup for New Construction Site

### 1. Clone to New Location
```bash
# Copy the entire folder to your new project location
cp -r "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Weather_Rain_Tracker_NOAA/Crescent_City_Rainfall" "/path/to/new/project/weather_system"
```

### 2. Configure for New Site
```bash
cd "/path/to/new/project/weather_system"

# Copy the config template
cp config.json.template config.json

# Edit config.json with your settings
```

### 3. Update Station ID
Edit `kcec_excel_export.py` and change line 23:
```python
# FROM:
self.station_id = "GHCND:USW00024286"  # CRESCENT CITY MCNAMARA AIRPORT

# TO:
self.station_id = "GHCND:YOUR_STATION_ID"  # YOUR NEW LOCATION
```

### 4. Find Your NOAA Station ID
- Visit: https://www.ncdc.noaa.gov/cdo-web/datasets
- Search for weather stations near your construction site
- Copy the station ID (format: GHCND:USW00012345)

### 5. Add Your NOAA API Token
Edit `config.json`:
```json
{
    "noaa_token": "YOUR_API_TOKEN_HERE"
}
```

Get a free token at: https://www.ncdc.noaa.gov/cdo-web/token

## File Structure

### Main Files (You'll Use These)
- **`update_kcec_data.py`** - Quick script for regular updates
- **`kcec_excel_export.py`** - Full-featured export system
- **`config.json`** - Your settings and API token

### System Files (Don't Modify)
- **`test_kcec_export.py`** - Testing script
- **`verify_export_format.py`** - Format validation
- **`config.json.template`** - Template for new sites

### Documentation
- **`README.md`** - This file
- **`KCEC_Weather_README.md`** - Detailed technical documentation
- **`PROJECT_HANDOFF_SUMMARY.md`** - Complete project history

## Excel Output Format

The system creates Excel files with exactly 21 columns (A-U) matching your existing spreadsheet:

| Column | Name | Description |
|--------|------|-------------|
| A | Date | YYYY-MM-DD format |
| B | Year | 2024, 2025, etc. |
| C | Month | 1-12 |
| D | Day | 1-31 |
| E | Month_Name | January, February, etc. |
| F | Day_of_Week | Monday, Tuesday, etc. |
| G | Total_Inches | Precipitation amount |
| H | High_Temp_F | Daily high temperature |
| I | Low_Temp_F | Daily low temperature |
| J | Avg_Wind_MPH | Average wind speed |
| K | Category | Light/Moderate/Heavy/Very Heavy |
| L | Measurable_0.01 | 1 if ≥0.01" precipitation |
| M | Contract_0.10 | 1 if ≥0.10" precipitation |
| N | Normal_0.25 | 1 if ≥0.25" precipitation |
| O | Heavy_0.50 | 1 if ≥0.50" precipitation |
| P | Very_Heavy_1.0 | 1 if ≥1.0" precipitation |
| Q | Work_Suitable_Area | 1 if suitable for outdoor work |
| R | Federal_Holiday | 1 if federal holiday |
| S | Federal_Holiday_Name | Holiday name |
| T | CA_State_Holiday | 1 if California state holiday |
| U | CA_State_Holiday_Name | CA holiday name |

## Common Tasks

### Update Your Existing Spreadsheet
1. Run `python3 update_kcec_data.py`
2. Open the new Excel file created in `weather_data/`
3. Copy all data from the new file
4. Paste into your existing spreadsheet starting after the last date
5. Your formulas and formatting are preserved

### Get Data for Specific Date Range
```bash
python3 kcec_excel_export.py
# Choose option 3
# Enter start date: 2025-06-01
# Enter end date: 2025-07-31
```

### Export All Historical Data
```bash
python3 kcec_excel_export.py
# Choose option 1
```

## Troubleshooting

### "No NOAA token" Error
- Check that `config.json` exists and has your API token
- Verify your token is valid at https://www.ncdc.noaa.gov/cdo-web/token
- Make sure you copied `config.json.template` to `config.json`

### "No data found" Error
- Check that your station ID is correct
- Verify the date range (NOAA data may have 1-2 day delay)
- Some older stations may not have complete data

### Wrong Location Data
- Verify your station ID in `kcec_excel_export.py` line 23
- Make sure it matches your construction site location
- Use the NOAA station search to find the correct ID

### Excel Format Doesn't Match
- The system creates exact column matches to your original spreadsheet
- If columns don't align, check that you're using the latest version
- Run `python3 verify_export_format.py` to check format

## Data Sources

### NOAA Weather Station
- **Current Station**: CRESCENT CITY MCNAMARA AIRPORT
- **Station ID**: GHCND:USW00024286
- **Location**: 41.78°N, 124.24°W
- **Data**: Official precipitation, temperature, wind measurements

### Data Quality
- **Precipitation**: Most reliable, available daily
- **Temperature**: Usually available, may have occasional gaps
- **Wind**: Available but less consistent than precipitation
- **Delay**: NOAA data typically 1-2 days behind real-time

### Holiday Database
- **Federal Holidays**: Complete through 2026
- **California State Holidays**: Includes César Chávez Day, Day After Thanksgiving
- **Automatic Updates**: Holidays flagged automatically in exports

## Business Applications

### Contract Compliance
- **Official Weather Source**: NOAA data is legally acceptable for contracts
- **Rainfall Thresholds**: Automatically calculates contract rain days (≥0.10")
- **Work Delays**: Clear indicators for weather-related work stoppages
- **Documentation**: Professional reports for change orders and disputes

### Project Planning
- **Weather Patterns**: Historical data for seasonal planning
- **Risk Assessment**: Identify high-precipitation periods
- **Resource Planning**: Schedule weather-sensitive activities
- **Budget Impact**: Quantify weather-related delays and costs

## Support

### Getting Help
- Check `automation.log` for error messages
- Review NOAA API documentation: https://www.ncdc.noaa.gov/cdo-web/webservices/v2
- Verify your station ID at: https://www.ncdc.noaa.gov/cdo-web/datasets

### Contact Information
- **System Created**: July 2025
- **Documentation**: This README file
- **Repository**: Git version control enabled

## Version Control

This system uses Git for version control. Key commands:

```bash
# Check current status
git status

# See commit history
git log --oneline

# Create new branch for modifications
git checkout -b new-site-customization

# Commit changes
git add .
git commit -m "Update station ID for new construction site"
```

## Future Enhancements

### Potential Additions
- **Multiple Station Support**: Track weather from multiple nearby stations
- **Email Alerts**: Automatic notifications for heavy rain events
- **Monthly Reports**: Automated summary reports
- **Integration**: Connect with project management software
- **Mobile Access**: Web interface for mobile weather checks

### Customization Options
- **Threshold Adjustments**: Modify precipitation thresholds for different contracts
- **Additional Weather Parameters**: Add humidity, pressure, visibility
- **Custom Categories**: Create site-specific weather classifications
- **Reporting Formats**: Add PDF reports, dashboard views

---

**Remember**: This system is designed to be copied and customized for each construction site. The NOAA API provides official weather data that's legally acceptable for contract documentation and dispute resolution.

**Last Updated**: July 2025