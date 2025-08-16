# Enhanced TDHCA Extractor with Address and Scoring Information

## Overview
I've created an enhanced TDHCA data extractor (`tdhca_enhanced_extractor_with_address_scoring.py`) that extends the original extraction capabilities to include:

1. **Complete Property Addresses**
2. **TDHCA Scoring Information** that helped projects get awarded

## New Features Added

### 1. Enhanced Address Extraction
The extractor now captures:
- **Street Address**: Full street address with number and street name
- **City**: Municipality where the project is located
- **County**: Texas county
- **State**: Default to "TX"
- **ZIP Code**: 5-digit postal code
- **Full Address**: Combined address string ready for geocoding

**Extraction Patterns Used**:
- `Property Address: [street], [city], TX [zip]`
- `Site Address: [street], [city], TX [zip]`
- Generic pattern for addresses starting with street numbers
- Separate county extraction from various formats

### 2. TDHCA Scoring Information
The extractor now captures critical scoring data:

**Opportunity Index**:
- Score value (0-7 points for 9% deals, 0-5 for 4% deals)
- Details about proximity to amenities

**QCT/DDA Status**:
- Qualified Census Tract (QCT) designation
- Difficult Development Area (DDA) designation
- Combined status: "Both", "QCT", "DDA", or "Neither"
- 130% basis boost eligibility

**Proximity Scores**:
- Distance to grocery stores
- Distance to elementary schools
- Distance to public transit stops
- Distance to health facilities

**Competition Analysis**:
- Nearby competing LIHTC properties
- Market saturation indicators

**Award Factors**:
- High opportunity area designation
- Excellent proximity to amenities
- Strong local support
- Experienced development team
- Cost-effective design
- Serves high-need population
- Rural or at-risk set-asides

**Total TDHCA Score**:
- Overall application score
- Breakdown by scoring categories

### 3. Enhanced AMI Matrix Extraction
Now extracts AMI set-asides by bedroom type:
- 30% AMI units by bedroom count
- 50% AMI units by bedroom count
- 60% AMI units by bedroom count
- 80% AMI units by bedroom count

### 4. Additional Financial Data
Enhanced to capture:
- **Developer Fee**: Development fee amount
- **Architect & Engineering Fees**: Professional service costs
- **LIHTC Equity**: Tax credit equity investment
- **First Lien Loan**: Primary debt amount
- **Second Lien Loan**: Secondary debt amount
- **Other Financing Sources**: Additional funding layers

### 5. Data Quality Metrics
Added confidence scoring system:
- **Address Confidence**: Based on completeness of address fields
- **Unit Data Confidence**: Validation of unit totals vs. unit mix
- **Financial Data Confidence**: Completeness of financial fields
- **Scoring Data Confidence**: Availability of TDHCA scoring information
- **Overall Confidence Score**: Weighted average for data quality

### 6. Processing Notes
Automatic flags for:
- Low confidence extractions requiring manual review
- Failed address extractions needing manual lookup
- Missing TDHCA scores indicating incomplete application data

## Usage Instructions

### Basic Usage
```python
from tdhca_enhanced_extractor_with_address_scoring import EnhancedTDHCAExtractor

# Initialize extractor
extractor = EnhancedTDHCAExtractor(base_path)

# Process single application
project_data = extractor.process_application(pdf_path)

# Process all applications in directory
all_projects = extractor.process_all_applications(input_dir)

# Save results
extractor.save_results(all_projects, "output_name")
```

### Output Formats
The extractor generates:
1. **JSON file**: Complete structured data for all extracted fields
2. **CSV file**: Tabular format for spreadsheet analysis
3. **Summary Report**: Text file with extraction statistics and insights

### Example Output Structure
```json
{
  "application_number": "23461",
  "project_name": "Estates at Ferguson",
  "street_address": "9220 Ferguson Road",
  "city": "Dallas",
  "county": "Dallas",
  "state": "TX",
  "zip_code": "75228",
  "full_address": "9220 Ferguson Road, Dallas, TX 75228",
  "total_units": 164,
  "unit_mix": {"1BR": 99, "2BR": 65},
  "ami_matrix": {
    "50_ami": {"1BR": 8, "2BR": 8},
    "60_ami": {"1BR": 91, "2BR": 57}
  },
  "opportunity_index_score": 5,
  "qct_dda_status": "QCT",
  "total_tdhca_score": 112,
  "award_factors": ["located in QCT", "high opportunity area"],
  "confidence_score": 0.85
}
```

## Implementation Notes

### Technical Approach
1. **Multi-method PDF extraction**: Uses both `pdfplumber` (better for tables) and `PyPDF2` (fallback)
2. **Pattern-based extraction**: Regular expressions tuned for TDHCA application formats
3. **Table-aware processing**: Special handling for rent schedules and budget tables
4. **Confidence scoring**: Automated data quality assessment

### Known Limitations
1. **PDF Quality**: Some older PDFs may have extraction issues
2. **Form Variations**: Different TDHCA form versions may require pattern updates
3. **Scoring Sheets**: Not all applications include detailed scoring breakdowns
4. **Processing Time**: Large PDFs (>100MB) may take several minutes

### Recommendations for M4 Beast Processing
1. **Use page limits**: Process only relevant pages (typically 1-150) for faster extraction
2. **Batch processing**: Process applications by region to manage memory
3. **Validation checkpoints**: Review low-confidence extractions before database insertion
4. **Parallel processing**: Consider multiprocessing for large batches

## Path Compatibility Note
The enhanced extractor has been updated to work with the current M1 directory structure:
```
/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/
```

This path structure should be verified on the M4 system and adjusted if needed.

## Next Steps
1. Test on full batch of 36 applications
2. Validate address extraction accuracy with geocoding
3. Cross-reference scoring data with TDHCA award announcements
4. Integrate with D'Marco site comparison analysis
5. Set up automated processing pipeline for future applications