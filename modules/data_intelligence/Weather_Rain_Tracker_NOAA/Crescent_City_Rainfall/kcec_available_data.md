# Available NOAA Weather Data for KCEC

## Additional Precipitation-Related Data Available:

### 1. **Precipitation Types** (datatypeid options):
- `PRCP` - Daily precipitation total (what we're using)
- `SNOW` - Daily snowfall
- `SNWD` - Snow depth
- `WESF` - Water equivalent of snowfall
- `DAPR` - Days with precipitation >= 0.01 inch
- `MDPR` - Multiday precipitation total

### 2. **Temperature Data** (important for rain vs snow):
- `TMAX` - Maximum temperature
- `TMIN` - Minimum temperature
- `TAVG` - Average temperature
- `TOBS` - Temperature at observation time

### 3. **Wind Data** (affects rainfall patterns):
- `AWND` - Average wind speed
- `WSF2` - Fastest 2-minute wind speed
- `WSF5` - Fastest 5-second wind speed
- `WDFG` - Wind direction

### 4. **Weather Type Indicators**:
- `WT01` - Fog
- `WT03` - Thunder
- `WT04` - Ice pellets
- `WT05` - Hail
- `WT08` - Smoke or haze
- `WT16` - Rain (may include freezing rain)

### 5. **Extreme Weather**:
- `PGTM` - Peak gust time
- `PSUN` - Percent of possible sunshine
- `TSUN` - Total sunshine

## Recommended Data Collection Strategy:

### Daily Collection:
- Precipitation amount (PRCP)
- Max/Min temperatures (TMAX, TMIN)
- Snow data if applicable (SNOW, SNWD)

### Weekly Summary Should Include:
- Total weekly precipitation
- Number of days with measurable precipitation
- Temperature range (important for contractors)
- Any extreme weather events
- Comparison to historical averages

### Monthly/Seasonal Analysis:
- Cumulative precipitation
- Deviation from normal
- Precipitation patterns
- Seasonal trends

## Use Cases for Construction/Contract Work:

1. **Work Day Planning**: 
   - Days with >0.1" precipitation
   - Temperature ranges for concrete/asphalt work
   - Wind speeds for crane operations

2. **Contract Compliance**:
   - Documented weather delays
   - Force majeure events
   - Historical comparison for disputes

3. **Seasonal Planning**:
   - Wet season vs dry season analysis
   - Best months for outdoor work
   - Year-over-year comparisons