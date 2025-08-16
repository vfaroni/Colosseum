# Getting Started with LIHTC Site Scorer

This guide will help you set up and start using the LIHTC Site Scorer for analyzing Low-Income Housing Tax Credit development sites.

## Prerequisites

- Python 3.8 or higher
- Git (for version control)
- Internet connection (for API calls and data downloads)

## Quick Setup

### 1. Environment Setup

Run the automated setup script:

```bash
python scripts/setup_environment.py
```

This will:
- ✅ Check Python version compatibility
- ✅ Install required dependencies
- ✅ Create configuration files
- ✅ Verify directory structure
- ✅ Create sample test data

### 2. Configuration

Edit the configuration file with your API keys:

```bash
# Copy the example configuration
cp config/config.example.json config/config.json

# Edit with your preferred editor
nano config/config.json
```

Required API keys:
- **PositionStack**: For geocoding (free tier available)
- **Census API**: For demographic data (free)
- **Google Maps** (optional): Enhanced distance calculations

### 3. Basic Usage Test

Test the installation with a simple analysis:

```python
from src.core.site_analyzer import SiteAnalyzer

# Initialize analyzer
analyzer = SiteAnalyzer()

# Analyze a site (Simi Valley example)
result = analyzer.analyze_site(
    latitude=34.282556,
    longitude=-118.708943,
    state='CA'
)

print(f"Analysis completed! Total points: {result.competitive_summary['total_points']}")
```

## Understanding the Results

### Federal Status
- **QCT Qualified**: 30% basis boost eligibility
- **DDA Qualified**: 30% basis boost eligibility
- **Basis Boost**: Percentage increase in eligible basis

### State Scoring (Example: California CTCAC)
- **Amenity Points**: Proximity to required amenities (max 15)
- **Opportunity Area Points**: High/Highest Resource Area designation (max 8)
- **Total Points**: Combined scoring for competitive applications

### Amenity Analysis
Individual scoring for:
- Transit access (0-7 points)
- Public parks (0-3 points)
- Libraries (0-3 points)
- Grocery stores (0-5 points)
- Schools (0-3 points)
- Medical facilities (0-3 points)
- Pharmacies (0-2 points)

## Common Use Cases

### 1. Site Due Diligence
```python
# Analyze a specific address
result = analyzer.analyze_site(
    latitude=your_lat,
    longitude=your_lon,
    state='CA',
    project_type='family'
)

# Check federal benefits
if result.federal_status['qct_qualified']:
    print("✅ Site qualifies for 30% basis boost")

# Check competitive position
total_points = result.state_scoring['total_points']
if total_points >= 20:
    print("🏆 Highly competitive site")
```

### 2. Batch Site Comparison
```python
# Compare multiple sites
sites = [
    (34.282556, -118.708943),  # Site A
    (34.0522, -118.2437),     # Site B
    (37.7749, -122.4194)      # Site C
]

results = analyzer.analyze_batch(sites)

# Compare scores
for i, result in enumerate(results):
    print(f"Site {i+1}: {result.state_scoring['total_points']} points")
```

### 3. Export Analysis Reports
```python
# Export detailed analysis
analyzer.export_analysis(
    result=result,
    output_path='outputs/site_analysis.json',
    format='json'
)

# Export Excel report (if implemented)
analyzer.export_analysis(
    result=result,
    output_path='outputs/site_analysis.xlsx', 
    format='excel'
)
```

## State-Specific Features

### California (CTCAC)
- Complete amenity scoring implementation
- Opportunity area integration
- Rural set-aside adjustments
- Project type specificity (family/senior/special needs)

### Texas (TDHCA)
- QCT/DDA verification
- Rural designation handling
- Basic amenity proximity

### Other States
- Federal-only analysis available
- QCT/DDA verification
- Basic amenity scoring
- Custom QAP integration in development

## Data Sources

The system integrates multiple data sources:

### Federal Data
- **HUD QCT/DDA**: Qualified Census Tracts and Difficult Development Areas
- **Census Bureau**: Demographics, tract boundaries
- **HUD AMI**: Area Median Income data

### State Data
- **QAP Documents**: State allocation plans and scoring criteria
- **Opportunity Maps**: State-specific high-resource designations

### Amenity Data
- **OpenStreetMap**: Points of interest, amenities
- **GTFS Feeds**: Transit data
- **State Datasets**: Schools, medical facilities

## Troubleshooting

### Common Issues

1. **API Key Errors**
   ```
   Error: Invalid API key
   Solution: Check config/config.json for correct API keys
   ```

2. **Coordinate Validation Failures**
   ```
   Error: Invalid coordinates
   Solution: Ensure latitude (-90 to 90) and longitude (-180 to 180) are valid
   ```

3. **Missing Dependencies**
   ```
   Error: ModuleNotFoundError
   Solution: Run: pip install -r requirements.txt
   ```

4. **Data Not Found**
   ```
   Error: QCT/DDA data not found
   Solution: Check data/ directory for required shapefiles
   ```

### Getting Help

1. **Check Documentation**: Review docs/ folder for detailed guides
2. **Run Tests**: Execute `python -m pytest tests/` to verify setup
3. **Example Code**: Review examples/ folder for usage patterns
4. **Error Logs**: Check logs/ directory for detailed error information

## Next Steps

1. **Explore Examples**: Run `python examples/basic_usage.py`
2. **Run Tests**: Execute test suite with `python -m pytest tests/`
3. **Customize Configuration**: Adjust settings in config/config.json
4. **Add Data Sources**: Download additional state-specific datasets
5. **Integrate with Your Workflow**: Build custom scripts for your use cases

## Performance Tips

- **Enable Caching**: Reduces API calls for repeated analyses
- **Batch Processing**: Analyze multiple sites together for efficiency
- **Parallel Processing**: Configure max_workers for faster batch operations
- **Data Locality**: Store frequently-used datasets locally

## Security Notes

- Never commit API keys to version control
- Use environment variables in production
- Implement rate limiting for API calls
- Encrypt sensitive location data

---

**Ready to start analyzing LIHTC sites!** 🏠

For advanced usage, see the full documentation in `docs/` or explore the source code in `src/`.