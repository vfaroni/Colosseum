# Enhanced LIHTC 4% Application Data Extraction Contract

## Purpose
Extract comprehensive data fields from 4% LIHTC applications for projects in a specified county.

## MANDATORY EXTRACTION REQUIREMENTS

### 1. File Selection Criteria
- **Filename Pattern**: Must contain "4pct" in the filename
- **County Match**: Project County must match the user-specified county
- **File Location**: `/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data`

### 2. Application Tab - REQUIRED FIELDS

| Field | Description | Status | Validation |
|-------|-------------|--------|------------|
| **Project Name** | Name of the development project | MANDATORY | Must not be empty |
| **CTCAC Project Number** | TCAC/CTCAC assigned project number | MANDATORY | Format: XX-XXX pattern |
| **Year** | Year of application | MANDATORY | 4-digit year (2020-2025) |
| **City** | City where project is located | MANDATORY | Valid city name |
| **County** | County where project is located | MANDATORY | Must match filter county |
| **General Contractor** | Name of general contractor | MANDATORY | Company name format |
| **New Construction** | Yes/No indicator | MANDATORY | Must be Yes or No |
| **Housing Type** | Family/Senior/Non-Targeted/etc. | MANDATORY | Valid housing type |
| **Total Number of Units** | Total unit count | MANDATORY | Integer > 0 |
| **Total Square Footage of Low Income Units** | Square footage for low income units | MANDATORY | Integer > 1000 |

### 3. Sources and Uses Budget Tab - REQUIRED FIELDS

| Field | Description | Status | Validation |
|-------|-------------|--------|------------|
| **Land Cost or Value** | Total land acquisition cost | MANDATORY | Dollar amount ≥ 0 |
| **Total New Construction Costs** | Total construction costs | MANDATORY | Dollar amount > 0 |
| **Total Architectural Costs** | Architectural fees | MANDATORY | Dollar amount ≥ 0 |
| **Total Survey and Engineering** | Survey and engineering fees | MANDATORY | Dollar amount ≥ 0 |
| **Local Development Impact Fees** | Local impact fees | MANDATORY | Dollar amount ≥ 0 |
| **Soft Cost Contingency** | Contingency for soft costs | MANDATORY | Dollar amount ≥ 0 |

## CONTRACT COMPLIANCE REQUIREMENTS

### Success Criteria:
- **100% field extraction rate** for all MANDATORY fields
- **Zero "Not found" results** for critical fields (Project Name, County, Units, Construction Cost)
- **Valid data types** for all numeric and text fields
- **Logical consistency** (e.g., costs should sum reasonably, units should match sqft)

### Quality Assurance:
1. **Multi-strategy extraction** - Use coordinate-based + content search + pattern matching
2. **Data validation** - Verify all extracted values meet logical constraints
3. **Cross-field validation** - Check relationships between related fields
4. **Error reporting** - Log specific issues for any missing mandatory fields

### Output Requirements:
- **Detailed JSON** with extraction metadata (confidence scores, locations found)
- **CSV summary** for analysis
- **Validation report** showing compliance with contract requirements
- **Missing field report** if any mandatory fields not found

## SEARCH STRATEGIES BY FIELD

### CTCAC Project Number:
- Search terms: ["CTCAC Project Number", "TCAC Project Number", "Project Number", "CTCAC #", "TCAC #"]
- Pattern: XX-XXX format (e.g., "24-409")
- Location: Typically in header or project info section

### Year:
- Search terms: ["Year", "Application Year", "Round Year"]
- Pattern: 4-digit year (2020-2025)
- Fallback: Extract from filename

### Housing Type:
- Search terms: ["Housing Type", "Target Population", "Tenant Type", "Population Served"]
- Valid values: ["Family", "Senior", "Non-Targeted", "Special Needs", "Transitional", "SRO"]
- Pattern matching for variations

### Soft Cost Contingency:
- Search terms: ["Soft Cost Contingency", "Contingency", "Soft Contingency", "Development Contingency"]
- Context: Must be associated with "soft" costs, not "hard" costs
- Validation: Reasonable percentage of total soft costs

## MANDATORY TESTING PROTOCOL

Before deployment, the extractor MUST:
1. **Pass Marina Towers test** - Extract all 16 mandatory fields successfully
2. **Validate data quality** - All fields must contain reasonable values
3. **Cross-check consistency** - Verify logical relationships between fields
4. **Generate compliance report** - Show 100% success rate on test file

## FAILURE HANDLING

If any mandatory field cannot be found:
1. **Escalate search intensity** - Use broader pattern matching
2. **Manual review flag** - Mark file for human verification
3. **Detailed error log** - Record exactly what was searched and where
4. **Alternative strategies** - Try different sheet names, merged cell handling

This contract ensures comprehensive, reliable extraction of all required LIHTC application data.