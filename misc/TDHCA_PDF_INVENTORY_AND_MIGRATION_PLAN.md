# 📄 TDHCA PDF INVENTORY & MIGRATION PLAN

**Date**: 2025-08-10  
**Location**: `/modules/data_intelligence/TDHCA_RAG/`  
**Total PDFs Found**: 48 files  

---

## 📊 CURRENT INVENTORY

### Summary Statistics
- **Total PDF Files**: 48
- **2023 Applications**: 22 (TDHCA_23xxx series)
- **2024 Applications**: 3 (24xxx series)
- **2025 Applications**: 16 (25xxx series)
- **Market Reports**: 3 (CoStar reports)
- **Other Reports**: 4 (Desktop reports, development costs)

### Breakdown by Year and Location

#### 2023 Applications (22 files) - All appear to be 9% Competitive
**San Antonio (9 files)**:
- TDHCA_23403_Cattleman_Square.pdf
- TDHCA_23412_Ellison_Apartments.pdf
- TDHCA_23413_Culebra_Road_Apts.pdf
- TDHCA_23424_Tigoni_Villas.pdf
- TDHCA_23428_Eden_Court_Place.pdf
- TDHCA_23433_Trails_at_River_Road.pdf
- TDHCA_23437_Costa_Almadena.pdf
- TDHCA_23440_Palladium_Crestway.pdf
- TDHCA_23455_1518_Apartments.pdf

**Houston (7 files)**:
- TDHCA_23407_Summerdale_Apartments.pdf
- TDHCA_23414_NHH_Berry.pdf
- TDHCA_23418_NHH_Gray.pdf
- TDHCA_23434_Park_at_Humble.pdf
- TDHCA_23442_Oakwood_Trails.pdf
- TDHCA_23454_Brookside_Gardens.pdf
- TDHCA_23460_Bissonnet_Apts.pdf

**Dallas-Fort Worth (6 files)**:
- TDHCA_23401_Northill_Manor.pdf
- TDHCA_23420_Rosemont_at_Ash_Creek.pdf
- TDHCA_23421_The_Positano.pdf
- TDHCA_23444_Tobias_Place.pdf
- TDHCA_23461_Estates_at_Ferguson.pdf

#### 2024 Applications (3 files)
- 24400.pdf
- 24403.pdf
- TDHCA_24600.pdf
- TDHCA_24601.pdf
- 24600_Development_Costs.pdf

#### 2025 Applications (16 files) - Likely 9% based on numbering
- 25403.pdf (Waters at Stone Creek)
- 25404.pdf (Torrington Briarwood)
- 25405.pdf (HiLine Illinois)
- 25409.pdf
- 25410.pdf
- 25411.pdf
- 25412.pdf
- 25413.pdf
- 25427.pdf
- 25429.pdf (Huntington Place Senior)
- 25439.pdf
- 25442.pdf
- 25447.pdf
- 25449.pdf

#### Market Reports (3 files)
- Austin - TX USA-MultiFamily-Market-2025-08-01 copy.pdf
- Dallas-Fort Worth - TX USA-MultiFamily-Market-2025-08-01 copy.pdf
- Houston - TX USA-MultiFamily-Market-2025-08-01 copy.pdf

#### Other Reports (2 files)
- Desktop Report - Richland Hills Drive copy.pdf
- Desktop Report - Richland Hills Drive DATA ONLY.pdf

---

## 🏗️ PROPOSED NAMING CONVENTION

### Format: `TDHCA_[YEAR]_[TYPE]_[ID]_[NAME].pdf`

Where:
- **YEAR**: 2023, 2024, 2025
- **TYPE**: 
  - `9pct` for 9% competitive applications
  - `4pct` for 4% bond applications
  - `MARKET` for market reports
  - `REPORT` for other reports
- **ID**: Application number (e.g., 23403, 25429)
- **NAME**: Project name (simplified, underscores for spaces)

### Examples:
- `TDHCA_2023_9pct_23403_Cattleman_Square.pdf`
- `TDHCA_2025_9pct_25429_Huntington_Place_Senior.pdf`
- `TDHCA_2024_4pct_24600_Project_Name.pdf` (if 4%)
- `TDHCA_2025_MARKET_Austin_Multifamily.pdf`

---

## 📁 PROPOSED DIRECTORY STRUCTURE

```
/data_sets/texas/TDHCA_Applications/
├── 2023/
│   ├── 9pct/
│   │   ├── San_Antonio/
│   │   ├── Houston/
│   │   └── Dallas_Fort_Worth/
│   └── 4pct/
├── 2024/
│   ├── 9pct/
│   └── 4pct/
├── 2025/
│   ├── 9pct/
│   └── 4pct/
├── Market_Reports/
└── Other_Reports/
```

---

## 🔍 DETERMINATION NEEDED

### To Identify 4% vs 9% Applications:

**Indicators for 9% (Competitive)**:
- Application numbers in 400s (e.g., 23403, 25429)
- Generally labeled as "Successful_2023_Applications"
- Competitive scoring documentation

**Indicators for 4% (Bonds)**:
- Application numbers in 600s (e.g., 24600, 24601)
- Often larger developments
- Different documentation requirements

**Need to verify**:
- 24400, 24403 - Unknown type
- 24600, 24601 - Likely 4% based on 600 series
- All 2025 applications (25xxx series)

---

## 🚀 MIGRATION SCRIPT

Would you like me to create a Python script to:
1. Read all PDFs from current location
2. Determine type based on filename patterns
3. Rename according to convention
4. Move to new organized structure in data_sets?

The script would:
- Preserve originals (copy, not move initially)
- Create detailed log of all operations
- Handle duplicates gracefully
- Generate summary report

---

## 📊 NEXT STEPS

1. **Confirm 4% vs 9% determination** for ambiguous files
2. **Review proposed naming convention** and adjust if needed
3. **Approve directory structure** for data_sets
4. **Execute migration script** with logging
5. **Validate moved files** and update documentation

---

## 💡 ADDITIONAL OBSERVATIONS

- All 2023 applications appear to be successful/awarded projects
- The "Successful_Applications_Benchmarks" folder contains reference applications
- D'Marco_Sites suggests these are from a specific developer/consultant
- Having PDFs organized will enable future OCR/extraction projects

Would you like me to:
1. Create the migration script?
2. Research the application numbers to definitively determine 4% vs 9%?
3. Set up the directory structure first?