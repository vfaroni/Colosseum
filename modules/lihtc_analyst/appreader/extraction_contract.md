# LIHTC 4% Application Data Extraction Contract

## Purpose
Extract specific data fields from 4% LIHTC applications for projects in a specified county.

## Extraction Criteria

### 1. File Selection Criteria
- **Filename Pattern**: Must contain "4pct" in the filename
- **County Match**: Project County must match the user-specified county
- **File Location**: `/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data`

### 2. Data Fields to Extract

#### From Application Tab:
| Field | Description | Expected Location |
|-------|-------------|-------------------|
| **Project Name** | Name of the development project | Row 18, Column H (or similar) |
| **City** | City where project is located | Application tab, specific row TBD |
| **County** | County where project is located | Application tab, specific row TBD |
| **General Contractor** | Name of general contractor | Application tab, specific row TBD |
| **New Construction** | Yes/No indicator | Application tab, specific row TBD |
| **Total Number of Units** | Total unit count | Application tab, specific row TBD |
| **Total Square Footage of Low Income Units** | Square footage for low income units | Application tab, specific row TBD |

#### From Sources and Uses Budget Tab:
| Field | Description | Expected Location |
|-------|-------------|-------------------|
| **Land Cost or Value** | Total land acquisition cost | Sources & Uses Budget tab, specific row TBD |
| **Total New Construction Costs** | Total construction costs | Sources & Uses Budget tab, specific row TBD |
| **Total Architectural Costs** | Architectural fees | Sources & Uses Budget tab, specific row TBD |
| **Total Survey and Engineering** | Survey and engineering fees | Sources & Uses Budget tab, specific row TBD |
| **Local Development Impact Fees** | Local impact fees | Sources & Uses Budget tab, specific row TBD |

## Output Format

### Per-Project Output Structure:
```json
{
  "filename": "2024_4pct_R1_24-XXX.xlsx",
  "application_data": {
    "project_name": "Example Project Name",
    "city": "San Francisco",
    "county": "San Francisco",
    "general_contractor": "ABC Construction Inc.",
    "new_construction": "Yes",
    "total_units": 150,
    "total_sqft_low_income": 125000
  },
  "sources_uses_data": {
    "land_cost": 5000000,
    "total_new_construction": 45000000,
    "total_architectural": 2500000,
    "total_survey_engineering": 350000,
    "local_impact_fees": 1200000
  }
}
```

### Summary Output Format:
- CSV file with all projects in specified county
- JSON file with detailed extraction results
- Summary statistics (total projects found, total units, total costs)

## Validation Rules
1. Project Name cannot be empty
2. County must match specified county (case-insensitive)
3. Numeric fields must be valid numbers
4. Yes/No fields must contain "Yes", "No", or be marked as "Not specified"

## Error Handling
- Log files that cannot be processed
- Mark missing fields as "Not found" in output
- Continue processing remaining files if one fails