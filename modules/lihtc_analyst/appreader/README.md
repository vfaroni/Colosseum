# LIHTC 4% Application Data Extractor

This tool extracts specific data fields from California 4% LIHTC (Low-Income Housing Tax Credit) application Excel files.

## Features

- Extracts data from Application tab and Sources & Uses Budget tab
- Filters projects by county
- Outputs results in both JSON and CSV formats
- Provides detailed logging and error handling
- Generates summary statistics

## Requirements

- Python 3.7+
- pandas
- openpyxl

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line
```bash
python3 lihtc_extractor.py "San Francisco"
```

### Interactive Mode
```bash
python3 lihtc_extractor.py
# Enter county name when prompted
```

## Extracted Data Fields

### From Application Tab:
- Project Name
- City
- County
- General Contractor
- New Construction (Yes/No)
- Total Number of Units
- Total Square Footage of Low Income Units

### From Sources and Uses Budget Tab:
- Land Cost or Value
- Total New Construction Costs
- Total Architectural Costs
- Total Survey and Engineering
- Local Development Impact Fees

## Output Files

The tool creates three output files in the `output/` directory:

1. **{County}_extraction_{timestamp}.json** - Detailed JSON with all extracted data
2. **{County}_summary_{timestamp}.csv** - CSV summary table
3. **{County}_summary_{timestamp}.txt** - Summary statistics

## Configuration

The tool is configured to read files from:
```
/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data
```

Only files containing "4pct" in the filename are processed.

## Validation Criteria

1. Filename must contain "4pct"
2. Project county must match specified county (case-insensitive)
3. Numeric fields are validated and default to 0 if invalid
4. Missing fields are marked as "Not found" or "Not specified"

## Logging

The tool creates an `extraction.log` file with detailed processing information and any errors encountered.

## Example Output

```json
{
  "filename": "2024_4pct_R1_24-409.xlsx",
  "application_data": {
    "project_name": "Marina Towers",
    "city": "Vallejo",
    "county": "Solano",
    "general_contractor": "ABC Construction Inc.",
    "new_construction": "Yes",
    "total_units": 150,
    "total_sqft_low_income": 125000
  },
  "sources_uses_data": {
    "land_cost": 660000,
    "total_new_construction": 45000000,
    "total_architectural": 286750,
    "total_survey_engineering": 40000,
    "local_impact_fees": 0
  }
}
```

## Testing

To test the extractor:

```bash
python3 analyze_structure.py  # Analyze file structure first
python3 lihtc_extractor.py "Test County"  # Test extraction
```

## Support

- Check `extraction.log` for detailed error messages
- Review `structure_analysis.json` to understand file layouts
- Verify source file directory path is correct