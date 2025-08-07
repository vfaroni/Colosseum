# TEXAS D'MARCO BOTN M1 EXECUTION MISSION

**Mission ID**: QAP-RAG-TX-BOTN-001  
**Priority**: HIGH  
**Agent**: QAP RAG (M1 Prototype)  
**Target**: Working Texas 4% BOTN with D'Marco integrations  
**Timeline**: 2-3 hours for complete prototype  

## Mission Objective

Build and demonstrate a working Texas D'Marco 4% new construction BOTN system on M1, integrating existing QCT/DDA, FEMA, and LPST analysis capabilities. Create a production-ready prototype for client demonstration before scaling to M4 Beast.

## Phase 1: Foundation Setup (30 minutes)

### 1.1 Verify M1 Environment
```bash
cd /Users/williamrice/HERR\ Dropbox/Bill\ Rice/Structured\ Consultants/AI\ Projects/CTCAC_RAG/code/qap_rag/backend

# Verify xlwings is working
python3 -c "import xlwings; print('xlwings ready!')"

# Verify Excel license
# Open Excel manually to confirm it works
```

### 1.2 Test Existing Integrations
```python
# Test QCT/DDA analyzer
from comprehensive_qct_dda_analyzer import ComprehensiveQCTDDAAnalyzer
analyzer = ComprehensiveQCTDDAAnalyzer()
test_result = analyzer.lookup_qct_status(32.7767, -96.7970)  # Dallas test
print(f"QCT/DDA Test: {test_result}")

# Verify LPST system exists
ls ../../../TDHCA_RAG/code/create_lpst_concern_maps.py

# Verify AMI data
ls /Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill\ Rice/Data_Sets/federal/HUD_AMI_Geographic/HUD2025_AMI_Rent_Data_Static.xlsx
```

## Phase 2: BOTN Template Creation (45 minutes)

### 2.1 Execute Template Builder
```bash
python3 texas_dmarco_botn_template.py
```

**Expected Output**: Excel file with 6 sheets
- Site Analysis (with integration placeholders)
- Development Budget (Texas construction costs)
- Financing Sources (4% credit structure)
- Operating Pro Forma (15-year projection)
- Returns Analysis (IRR/equity multiple)
- Assumptions (all parameters)

### 2.2 Validate Template Structure
- Open created Excel file in Excel
- Verify all sheets present
- Check formula references work
- Confirm formatting is professional

## Phase 3: System Integration (60 minutes)

### 3.1 QCT/DDA Integration (20 minutes)
```python
# Create integration script
def integrate_qct_dda_lookup(workbook, lat, lon):
    analyzer = ComprehensiveQCTDDAAnalyzer()
    result = analyzer.lookup_qct_status(lat, lon)
    
    site_sheet = workbook.sheets['Site Analysis']
    site_sheet.range('B10').value = result.get('qct_status', 'Not Found')
    site_sheet.range('B11').value = 'YES' if result.get('basis_boost_eligible') else 'NO'
    
    return result
```

### 3.2 FEMA Flood Integration (20 minutes)
```python
# Simplified FEMA lookup (use existing flood data if available)
def integrate_flood_lookup(workbook, lat, lon):
    # Use existing FEMA integration or placeholder
    site_sheet = workbook.sheets['Site Analysis']
    site_sheet.range('B12').value = 'X'  # Placeholder - integrate actual lookup
    site_sheet.range('B13').value = 'YES'  # Assume flood insurance required
```

### 3.3 LPST Environmental Integration (20 minutes)
```python
# Connect to LPST screening system
def integrate_lpst_screening(workbook, lat, lon):
    # Use existing LPST analysis or simplified version
    site_sheet = workbook.sheets['Site Analysis']
    site_sheet.range('B14').value = 'LOW'  # Environmental risk level
    site_sheet.range('B15').value = '0.5 miles'  # Distance to nearest LPST
```

## Phase 4: Demo Site Testing (30 minutes)

### 4.1 Test with D'Marco Site Example
**Test Site**: Hutchins, TX (from environmental analysis)
- **Coordinates**: 32.6501, -96.6083
- **Known Data**: MEDIUM environmental risk (0.433 miles to LPST)

### 4.2 Complete BOTN Workflow
```python
def create_dmarco_botn_demo(site_address, lat, lon):
    # 1. Create template
    wb = create_texas_botn_template()
    
    # 2. Input site data
    site_sheet = wb.sheets['Site Analysis']
    site_sheet.range('B4').value = site_address
    site_sheet.range('B6').value = lat
    site_sheet.range('B7').value = lon
    
    # 3. Run integrations
    qct_result = integrate_qct_dda_lookup(wb, lat, lon)
    flood_result = integrate_flood_lookup(wb, lat, lon)
    lpst_result = integrate_lpst_screening(wb, lat, lon)
    
    # 4. Input development assumptions
    budget_sheet = wb.sheets['Development Budget']
    budget_sheet.range('B12').value = 50000  # Square footage
    budget_sheet.range('B39').value = 100    # Unit count ('Site Analysis'!B39)
    
    # 5. Calculate returns
    # Excel formulas will auto-calculate
    
    # 6. Save demo file
    demo_path = f"DMarco_BOTN_Demo_{datetime.now().strftime('%m%d%Y')}.xlsx"
    wb.save(demo_path)
    
    return demo_path, qct_result
```

## Phase 5: Results Validation (15 minutes)

### 5.1 Verify Key Calculations
- **QCT/DDA Status**: Correctly identifies basis boost eligibility
- **Construction Costs**: Reasonable $/SF for Texas
- **Tax Credit Equity**: 4% credits × $0.90 rate × 10 years
- **Financing Gap**: Development cost vs available sources
- **Returns**: Developer fee and investor IRR

### 5.2 Demo Readiness Check
- Professional Excel formatting
- All integrations working
- Calculations flowing correctly
- Ready for client presentation

## Success Criteria

### Technical Validation ✅
- [ ] Excel template creates successfully
- [ ] QCT/DDA lookup returns accurate results
- [ ] All 6 sheets properly linked with formulas
- [ ] Demo site analysis completes in <5 minutes
- [ ] Results are financially reasonable

### Business Validation ✅
- [ ] Demonstrates D'Marco site analysis automation
- [ ] Shows 130% basis boost impact on feasibility
- [ ] Environmental risk properly factored into costs
- [ ] Complete pro forma ready for investor review
- [ ] Scalable to all D'Marco sites

## Deliverables

1. **Working BOTN Template**: Excel file with all integrations
2. **Demo Analysis**: Complete Hutchins site example
3. **Integration Scripts**: Python code connecting all systems
4. **Performance Metrics**: Speed and accuracy measurements
5. **M4 Migration Plan**: Scaling strategy for production

## M1 Limitations & Workarounds

**Memory Management**:
- Process one site at a time
- Close Excel between large operations
- Use simplified LPST analysis if needed

**Performance Optimization**:
- Cache QCT/DDA lookups
- Pre-load AMI data
- Batch similar calculations

**Excel Stability**:
- Save frequently during development
- Use xlwings context managers
- Have backup/recovery procedures

## Post-Demo: M4 Migration Benefits

**Performance Gains**:
- 3-5x faster template creation
- Simultaneous multi-site analysis
- Real-time integration updates
- Enhanced memory for complex calculations

**Production Features**:
- Batch processing all D'Marco sites
- API service for real-time analysis
- Advanced environmental integration
- Client dashboard interface

## Notes for QAP RAG M1

**Priority Focus**:
1. Get basic template working first
2. QCT/DDA integration is highest value
3. Demo with one complete site
4. Document any M1 limitations encountered

**Fallback Plans**:
- If xlwings has issues, create template manually and import data
- If integrations fail, use hardcoded demo values
- If Excel crashes, work in smaller chunks

**Success Metric**: 
Working demo that shows automated D'Marco site analysis with 130% basis boost calculation - this alone will demonstrate the system's value.

---

**Mission Status**: READY FOR M1 EXECUTION  
**Prepared by**: QAP RAG Lead  
**Target Agent**: QAP RAG (M1)  
**Expected Demo**: Complete Texas D'Marco BOTN in 2-3 hours