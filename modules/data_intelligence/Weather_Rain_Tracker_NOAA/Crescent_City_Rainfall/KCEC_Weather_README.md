# KCEC Weather Data Collection System

Automated system for downloading precipitation data from KCEC (Jack McNamara Field Airport) weather station.

## Features

- **NOAA Historical Data**: Downloads daily precipitation totals from NOAA Climate Data Online
- **Real-time Data**: Scrapes current hourly observations from weather.gov
- **Weekly Automation**: Automatically collects data every week
- **Data Organization**: Archives old data and creates summary reports
- **Email Notifications**: Optional email reports on collection status

## Quick Start

1. **Run Setup Script**:
   ```bash
   python3 setup_kcec_weather.py
   ```

2. **Get NOAA API Token**:
   - Visit https://www.ncdc.noaa.gov/cdo-web/token
   - Sign up for a free account
   - Copy your token
   - Add it to `config.json`

3. **Run Data Collection**:
   ```bash
   python3 kcec_weather.py
   ```

## Files Overview

- `setup_kcec_weather.py` - Initial setup script
- `kcec_weather_downloader.py` - NOAA historical data downloader
- `kcec_realtime_scraper.py` - Real-time weather.gov scraper
- `kcec_weekly_automation.py` - Weekly automation controller
- `kcec_weather.py` - Simple wrapper interface
- `config.json` - Configuration file (created by setup)

## Data Sources

1. **NOAA Climate Data Online**
   - Station: GHCND:USW00093814 (KCEC)
   - Data: Daily precipitation totals
   - Format: CSV with date and precipitation in inches

2. **Weather.gov API**
   - Station: KCEC
   - Data: Hourly observations including precipitation
   - Format: JSON converted to CSV

## Directory Structure

```
weather_data/
├── current/          # Recent data files
├── archive/          # Files older than 30 days
├── reports/          # Summary reports
└── automation.log    # Automation log file
```

## Usage Examples

### Download Last 7 Days
```bash
python3 kcec_weather.py
# Select option 1
```

### Download Specific Date Range
```bash
python3 kcec_weather.py
# Select option 2
# Enter start and end dates (YYYY-MM-DD format)
```

### Get Current Real-time Data
```bash
python3 kcec_weather.py
# Select option 3
```

### Run Weekly Collection Manually
```bash
python3 kcec_weekly_automation.py --run-once
```

## Automation Setup

### Linux/macOS (using cron)
```bash
# Add to crontab (runs every Monday at 9 AM)
crontab -e
# Add this line:
0 9 * * 1 /usr/bin/python3 /path/to/kcec_weekly_automation.py --run-once
```

### Windows (using Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Weekly, Monday, 9:00 AM
4. Set action: Start program
5. Program: python.exe
6. Arguments: /path/to/kcec_weekly_automation.py --run-once

## Configuration

Edit `config.json` to customize:

```json
{
    "data_dir": "weather_data",
    "noaa_token": "YOUR_TOKEN_HERE",
    "email_notifications": false,
    "email_to": "your-email@example.com",
    "email_from": "weather-bot@example.com",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "",
    "smtp_password": ""
}
```

## Troubleshooting

### NOAA Data Not Downloading
- Verify your NOAA token is correct in config.json
- Check internet connection
- Token may take a few minutes to activate after creation

### Real-time Data Not Working
- Weather.gov API endpoints may change
- Check automation.log for specific errors
- Fallback Selenium scraper requires Chrome and chromedriver

### Missing Dependencies
```bash
pip install requests pandas beautifulsoup4 selenium schedule lxml
```

## Data Output Format

### NOAA Historical Data
```csv
date,precipitation_inches
2024-01-01,0.25
2024-01-02,0.00
2024-01-03,1.15
```

### Real-time Data
```csv
timestamp,precipitation_inches,temperature_f,humidity,wind_speed_mph
2024-01-15T10:00:00Z,0.05,65.2,78,12.5
```

## Support

For issues with:
- NOAA API: Contact NOAA support at ncdc.info@noaa.gov
- Weather.gov: Check https://www.weather.gov/documentation/services-web-api
- This script: Review automation.log for error details