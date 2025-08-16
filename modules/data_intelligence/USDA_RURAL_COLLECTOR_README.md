# 🌾 USDA Rural Development Data Collector

## Quick Start Guide

### Installation
```bash
# Ensure Python 3 is installed
python3 --version

# Install required packages (if needed)
pip3 install requests pandas openpyxl
```

### Basic Usage

#### 1. Test Mode (Quick Test - 5 Counties)
```bash
python3 usda_rural_collector.py --test
```

#### 2. Full Collection (All Counties)
```bash
python3 usda_rural_collector.py
```

#### 3. Specific State Analysis
```bash
python3 usda_rural_collector.py --state CA
python3 usda_rural_collector.py --state TX
```

#### 4. Custom Output Directory
```bash
python3 usda_rural_collector.py --output /path/to/output
```

### Output Files

The script creates a `usda_rural_data/` directory containing:

1. **rucc_codes_processed.csv** - County-level rural classifications
   - FIPS code
   - State and County names
   - RUCC code (1-9, where 4-9 = rural)
   - Population
   - Rural/Urban flag
   - Full classification description

2. **collection_report_[timestamp].json** - Summary statistics
   - Counties processed
   - Rural vs urban breakdown
   - Processing duration
   - File locations

3. **collection_log_[timestamp].log** - Detailed execution log
   - API calls made
   - Processing steps
   - Any errors encountered

### Understanding RUCC Codes

Rural-Urban Continuum Codes (1-9 scale):
- **1-3**: Metro/Urban counties
- **4-9**: Rural counties (USDA eligible)

#### Rural Classifications:
- **4**: Urban population 20,000+, adjacent to metro
- **5**: Urban population 20,000+, not adjacent to metro
- **6**: Urban population 2,500-19,999, adjacent to metro
- **7**: Urban population 2,500-19,999, not adjacent to metro
- **8**: Completely rural, adjacent to metro
- **9**: Completely rural, not adjacent to metro

### LIHTC Benefits of Rural Areas

#### Set-Aside Access
- 10-20% of state credits reserved for rural
- 2.5x better odds than urban competitions

#### Scoring Advantages
- +10 points for rural location (typical)
- +5 points for rural economic development
- +5 points for agricultural worker housing

#### Financial Benefits
- 50-70% lower land costs
- Eligible for 130% basis boost
- Access to USDA 538 loans

### Mission Tracking for Strike Leader

The script automatically generates tracking logs for agent coordination:

```json
{
  "mission": "USDA Rural Development Maps Acquisition",
  "collector": "Strike Leader Implementation",
  "timestamp": "2025-08-07T00:13:50",
  "statistics": {
    "counties_processed": 3143,
    "rural_counties": 1976,
    "urban_counties": 1167,
    "rural_percentage": 62.9
  }
}
```

### Next Steps

1. **Run full collection**: Remove `--test` flag for complete data
2. **Analyze priority states**: TX, CA, MT, IA, NE have best rural LIHTC
3. **Integration**: Overlay with parcel data for site selection
4. **Validation**: Cross-check with known rural LIHTC projects

### Troubleshooting

#### Missing packages error:
```bash
pip3 install requests pandas openpyxl
```

#### Permission denied:
```bash
chmod +x usda_rural_collector.py
```

#### Network timeout:
- Script includes retry logic
- Check internet connection
- API endpoints are public (no auth required)

---

**Mission**: USDA Rural Development Maps Acquisition  
**Agent**: Strike Leader  
**Status**: Production Ready