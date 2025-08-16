# CTCAC QAP OCR TEMPLATE AND INSTRUCTIONS
## For Converting December_11_2024_QAP_Regulations_FINAL.pdf

### OCR HEADER TEMPLATE (Place at beginning of document)
```
################################################################################
# CALIFORNIA TAX CREDIT ALLOCATION COMMITTEE REGULATIONS
# Title 4, Division 17, Chapter 1
# Implementing Health and Safety Code Sections 50199.4-50199.22
# 
# SOURCE DOCUMENT: December_11_2024_QAP_Regulations_FINAL.pdf
# EFFECTIVE DATE: December 11, 2024
# OCR CONVERSION DATE: [INSERT DATE]
# TOTAL PAGES: [INSERT TOTAL]
#
# IMPORTANT: This is an OCR conversion. For legal purposes, refer to the
# official PDF version available at www.treasurer.ca.gov/ctcac/
################################################################################
```

### TABLE OF CONTENTS / INDEX HANDLING

**For the hyperlinked index at the beginning:**

```
================================================================================
TABLE OF CONTENTS
[Preserve original formatting with section numbers and titles]
[Add notation: (PDF Page X / Doc Page Y) after each entry]
================================================================================

ARTICLE 1. GENERAL................................... (PDF Page 3 / Doc Page 1)
  Section 10300. Purpose and Scope.................... (PDF Page 3 / Doc Page 1)
  Section 10301. Definitions.......................... (PDF Page 3 / Doc Page 1)
  Section 10302. Definitions.......................... (PDF Page 8 / Doc Page 6)
  [etc.]

ARTICLE 2. TAX CREDIT ALLOCATION PROCEDURES........... (PDF Page 25 / Doc Page 23)
  Section 10310. Files and Applications............... (PDF Page 25 / Doc Page 23)
  [etc.]

[IMPORTANT: Create a searchable anchor for each section using format: <<SECTION_10300>>]
```

### DEFINITIONS SECTION SPECIAL HANDLING

**For Section 10301/10302 Definitions:**

```
================================================================================
[Page 3]
SECTION 10301. DEFINITIONS
[Last Updated: December 11, 2024]
================================================================================

<<SECTION_10301>>

The following definitions shall apply to the terms used in these regulations:

(a) <<DEF_ANNUAL_INCOME>> "Annual Income" means the gross income as defined in 
    Title 25, California Code of Regulations, Section 6914.
    [Cross-references: Section 10325(c)(3), Section 10327(c)(2)(A)]

(b) <<DEF_APPLICABLE_FRACTION>> "Applicable fraction" means the fraction defined 
    in IRC Section 42(c)(1)(B).
    [Cross-references: Section 10325(f)(9)(B), Section 10327(c)(5)]

(c) <<DEF_AT_RISK>> "At-risk" means:
    (1) With respect to an existing property that is to be used for an allocation 
        of Credit pursuant to Section 10325(c)(4), that both of the following 
        conditions exist:
        (A) the property is subject to one or more of the following:
            (i) has project-based rental assistance from HUD, RD, or state/local 
                agencies AND is eligible for prepayment/termination; OR
            (ii) has restrictions that will terminate within 5 years; OR
            (iii) is owned by a qualified nonprofit with demonstrated hardship
        (B) would convert to market-rate without tax credit allocation
    [Key Cross-references: Section 10325(c)(4) - At-Risk Set-Aside]
    [See also: Section 10325(g)(4) - Documentation Requirements]

[FORMATTING NOTES:
- Each definition gets an anchor tag <<DEF_TERM_NAME>>
- Include cross-references in brackets
- Preserve sub-items with proper indentation
- Note any amendments with [AMENDED 2024] tags]
```

### MAIN CONTENT FORMATTING

```
================================================================================
[Page 25]
ARTICLE 2. TAX CREDIT ALLOCATION PROCEDURES
SECTION 10310. FILES AND APPLICATIONS
[Regulation Reference: 4 CCR § 10310]
================================================================================

<<SECTION_10310>>

(a) <<10310_a>> Maintenance and inspection of Committee files.
    (1) <<10310_a_1>> The Committee shall maintain files which shall include, 
        but not be limited to the following:
        (A) <<10310_a_1_A>> all applications for Credit reservations, carryover 
            allocations, and building allocations;
        
[CROSS-REFERENCE NOTE: See Section 10301(x) for definition of "Committee"]
[AMENDMENT NOTE: Subsection (a)(2) amended December 11, 2024]

---PAGE BREAK--- [Page 26]

        (B) <<10310_a_1_B>> all point score worksheets and related documentation;
        [Continue...]
```

### SPECIAL ELEMENTS HANDLING

**Tables:**
```
[TABLE: Title of Table]
[TABLE REFERENCE: Section 10325(c)(9) - Tiebreaker Scores]
+------------------------+------------------+------------------+
| Column Header 1        | Column Header 2  | Column Header 3  |
+------------------------+------------------+------------------+
| Data Row 1            | Value            | Notes            |
| Data Row 2            | Value            | Notes            |
+------------------------+------------------+------------------+
[END TABLE]
```

**Footnotes:**
```
Text with footnote reference¹

[FOOTNOTE 1: Explanation text from bottom of page]
```

**Cross-References:**
```
as defined in Section 10301(c) <<XREF:10301_c>> means...
[Creates searchable cross-reference]
```

**Formulas/Calculations:**
```
[FORMULA]
Applicable Percentage = (Qualified Basis / Eligible Basis) × 100
[END FORMULA]
```

### ANCHOR TAG SYSTEM

Create hierarchical anchor tags for easy navigation:
- Sections: `<<SECTION_10325>>`
- Subsections: `<<10325_c>>`, `<<10325_c_4>>`
- Definitions: `<<DEF_AT_RISK>>`
- Tables: `<<TABLE_10325_c_9>>`
- Cross-references: `<<XREF:section_subsection>>`

### METADATA PRESERVATION

At the start of each major section, include:
```
[METADATA]
Original PDF Pages: 45-67
Section Version: December 11, 2024
Related Sections: 10301(c), 10327(g)(4)
Key Changes from Previous Version: [if applicable]
[END METADATA]
```

### QUALITY CONTROL MARKERS

Include these markers for verification:
```
[QC:CHECK] - For unclear text requiring manual verification
[QC:TABLE] - For complex tables that may need formatting review
[QC:FORMULA] - For mathematical formulas requiring validation
[QC:MISSING] - For any content that couldn't be extracted
```

### POST-OCR SEARCH INDEX

At the end of the document, create a search index:
```
================================================================================
SEARCH INDEX
================================================================================

AT-RISK PROVISIONS:
- Definition: <<DEF_AT_RISK>> (Page 3)
- Set-aside requirements: <<10325_c_4>> (Page 47)
- Documentation: <<10325_g_4>> (Page 89)
- Scoring: <<10325_c_4_A>> (Page 48)

DEVELOPER FEE REFERENCES:
- At-risk 15% allowance: <<10327_c_2_A_3>> (Page 124)
- Standard limits: <<10327_c_2>> (Page 122)
[etc.]
```

### IMPLEMENTATION NOTES FOR CLAUDE CODE

When using with Claude Code, you can create a script that:
1. Extracts text while preserving structure
2. Adds anchor tags programmatically
3. Creates the search index automatically
4. Validates cross-references
5. Generates a separate "quick reference" file for common searches

Example usage pattern:
```python
# Search for all at-risk related sections
grep -n "<<DEF_AT_RISK\\|at-risk\\|At-Risk" QAP_2025_OCR.txt

# Extract specific section
sed -n '/<<SECTION_10325>>/,/<<SECTION_10326>>/p' QAP_2025_OCR.txt
```