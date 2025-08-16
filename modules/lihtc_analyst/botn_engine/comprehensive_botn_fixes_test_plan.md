# Test Plan for Comprehensive BOTN Engine Fixes

## Feature Description
Fix critical issues in BOTN engine: 1) Retain original CostarExport columns, 2) Fix HQTA sites processing, 3) Add terrain analysis to prevent cliff recommendations, 4) Extract CTCAC cost data.

## Contracts

### Input
- **CostarExport Files**: Excel files with original 37 columns including Property Address, Land Area, etc.
- **HQTA Processing**: Sites that previously qualified for 7 points under HQTA boundaries
- **Terrain Analysis**: Elevation data to identify steep slopes/cliffs
- **CTCAC Applications**: Regional cost data for hard costs, architecture, soft costs

### Output
- **Enhanced BOTN Files**: Include all original CostarExport columns
- **HQTA Validation**: Correct 7-point scoring for HQTA sites
- **Terrain Filtering**: Sites flagged/filtered if >15% slope
- **Cost Integration**: CTCAC-based cost estimates in BOTN analysis

### Errors
- **ColumnLossError**: When original CostarExport columns are dropped
- **HQTAMisclassificationError**: When HQTA sites don't get 7 points
- **TerrainDataError**: When elevation API fails or slope calculation errors
- **CTCACDataError**: When cost extraction fails or data is incomplete

## Test Cases

### Unit Tests

#### Test 1: CostarExport Column Preservation (Positive case)
- **Input**: CostarExport-15.xlsx with 37 original columns
- **Expected**: All 37 columns preserved in BOTN processing output
- **Validation**: Check output contains Property Address, Land Area (AC), Zoning, etc.

#### Test 2: HQTA 7-Point Qualification (Positive case)
- **Input**: Site within HQTA boundary from previous analysis
- **Expected**: Site receives 7 points for transit scoring
- **Validation**: CTCAC_HQTA_INTEGRATED_TRANSIT_ANALYSIS confirms 7 points

#### Test 3: Terrain Slope Detection (Edge case)
- **Input**: Site coordinates on steep terrain (>15% slope)
- **Expected**: Site flagged as unsuitable, filtered from recommendations
- **Validation**: USGS elevation data confirms slope calculation

#### Test 4: Missing CTCAC Data Handling (Negative case)
- **Input**: Region with no CTCAC application data
- **Expected**: Graceful fallback to default cost estimates
- **Validation**: Error handling works, system continues processing

### Integration Tests

#### Integration Test 1: End-to-End BOTN Generation
- **Input**: CostarExport file with HQTA sites and terrain data
- **Expected**: Complete BOTN file with all fixes applied
- **Validation**: Output contains original columns, correct HQTA scoring, terrain analysis

#### Integration Test 2: Multi-Stage Filtering Pipeline
- **Input**: 100+ sites from CostarExport through complete analysis
- **Expected**: Sites filtered by terrain, scored by HQTA, with preserved columns
- **Validation**: Final output shows proper filtering and scoring rationale