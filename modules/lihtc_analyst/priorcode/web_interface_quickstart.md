# Texas Land Analysis Web Interface - Quick Start Guide

## Installation

First, install Streamlit and required dependencies:

```bash
pip3 install streamlit pandas plotly openpyxl
```

Note: Use `pip3` to ensure compatibility with `python3`

## Running the Web Interface

### Option 1: Full Dashboard
The comprehensive dashboard with maps, charts, and analytics:

```bash
streamlit run texas_land_dashboard.py
```

Features:
- Interactive filters (eligibility, county, distances, population)
- Data table with column selection
- Analytics charts (pie charts, histograms, scatter plots)
- Geographic map view
- Summary reports
- CSV/Excel export

### Option 2: Simple Table Viewer
Focused on data viewing and filtering:

```bash
streamlit run texas_land_simple_viewer.py
```

Features:
- Sortable data table
- Quick filters
- Column selection
- Export to CSV/Excel
- Summary statistics

## Usage Instructions

### Loading Data
1. **Upload File**: Click "Browse files" to upload your merged Excel file
2. **Select Existing**: Choose from dropdown if files exist in current directory

### Filtering Data
1. Use sidebar filters to narrow down properties
2. Select specific counties, eligibility status
3. Adjust distance range sliders
4. Apply quick filters for common queries

### Exporting Results
1. Click "Download as CSV" for filtered data
2. Use "Prepare Excel Download" for formatted Excel export
3. All exports include only filtered/displayed data

## File Requirements

Your Excel file should have these columns:
- Basic: Address, City, County
- Coordinates: Latitude, Longitude
- Analysis: eligibility, distance columns (*_distance_miles)
- Competition: one_mile_compliant, one_mile_competing_count
- Population: city_population

## Troubleshooting

### "No file found" error
- Ensure you're running from the directory containing your Excel files
- Upload a file using the file uploader

### Map not displaying
- Check that Latitude/Longitude columns exist and have valid values
- Ensure plotly is installed: `pip3 install plotly`

### Slow performance
- For large datasets (>10,000 properties), filtering may take a moment
- Consider pre-filtering data before loading

### Module not found errors
- Use `pip3` instead of `pip` to match your Python 3 installation
- Check installation: `pip3 list | grep streamlit`

## Customization

### Adding New Filters
Edit the sidebar section in either app:
```python
# Add new filter
new_filter = st.sidebar.selectbox(
    "My New Filter",
    options=df['column_name'].unique()
)
```

### Changing Default Columns
Edit the `default_display_cols` list:
```python
default_display_cols = [
    'Address', 'City', 'County', 
    'your_column_here'
]
```

### Adding New Charts
In the Analytics tab, add:
```python
fig = px.chart_type(
    df,
    x='column1',
    y='column2',
    title="My Chart"
)
st.plotly_chart(fig)
```

## Deployment Options

### Local Network Sharing
Share within your network:
```bash
streamlit run texas_land_dashboard.py --server.address 0.0.0.0
```

### Streamlit Cloud (Free)
1. Push code to GitHub
2. Visit share.streamlit.io
3. Connect your repository
4. Deploy automatically

### Docker Deployment
Create Dockerfile:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "texas_land_dashboard.py"]
```

## Next Steps

1. **Test with your data**: Run with your merged Excel file
2. **Customize filters**: Add filters specific to your needs
3. **Add visualizations**: Create charts for your metrics
4. **Deploy**: Share with your team using Streamlit Cloud

## Support

For issues or enhancements:
1. Check column names match expected format
2. Ensure data types are correct (numeric for distances)
3. Verify Excel file has 'Complete Data' sheet (for dashboard)