# 🏛️ COLOSSEUM Shared Intelligence - Dataset Locations

**Updated**: Daily by all agents  
**Access**: Bill + Vitor agents (read/write)

---

## 🗺️ **CRITICAL DATASET LOCATIONS**

### **Federal Data Sources**
**Base Path**: `/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Data_Sets/federal/`

- **HUD QCT/DDA Data**: `HUD_QCT_DDA_Data/`
  - `qct_data_2025.xlsx` (44,933 census tracts)
  - `2025-DDAs-Data-Used-to-Designate.xlsx` (22,192 ZIP areas)
  - **Coverage**: Complete US 54-jurisdiction QCT+DDA analysis ready

- **HUD AMI Rent Data**: `HUD_AMI_Geographic/`
  - `HUD2025_AMI_Rent_Data_Static.xlsx` (4,764 areas nationwide)
  - **VERIFIED**: 100% Novogradac calculator accuracy
  - **Critical**: Use correct household size methodology (1BR=1.5, 2BR=3.0, etc.)

- **Federal LIHTC Sources**: `LIHTC_Federal_Sources/`
  - IRC Section 42, CFR regulations, Revenue Procedures
  - **Authority Hierarchy**: IRC (100) > CFR (80) > Rev Proc (60) > State QAP (30)

### **State Data Sources**
**Base Path**: `/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Data_Sets/`

- **California**: `california/`
  - Transit: `CA_Transit_Data/` (264K+ stops, 22,510 HQTA areas)
  - Schools: `CA_Public Schools/` (official DOE data)
  - Environmental: `environmental/FEMA_Flood_Maps/` (100% CA coverage)

- **Texas**: `texas/`
  - Environmental: `environmental_enhanced/` (797,403 TCEQ records)
  - Schools: `TX_Public_Schools/` (TEA official data)
  - Economic Analysis: Complete TDHCA analysis tools

- **QAP Collection**: `QAP/`
  - **54 jurisdictions**: All 50 states + DC + territories
  - **Processing Rate**: 96.1% automated success
  - **Vector Search**: ChromaDB integration (16,884 documents)

### **Cache System**
**Location**: `/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Cache/`
- Census API responses
- AMI lookups  
- Geocoding results (PositionStack fallback)

---

## 🔑 **API KEYS & ACCESS**

### **Production APIs**
- **Census API**: `06ece0121263282cd9ffd753215b007b8f9a3dfc` (demographic data)
- **PositionStack**: `41b80ed51d92978904592126d2bb8f7e` (geocoding fallback, 1M/month)
- **NOAA Weather**: `oaLvXPjjAWoSCizEBvNoHPNhATmdDmQA` (weather/climate data)

### **Temporary/Development**
- **Google Maps**: `AIzaSyBlOVHaaTw9nbgBlIuF90xlXHbgfzvUWAM` ⚠️ **MUST BE CHANGED**

---

## 📊 **PERFORMANCE BENCHMARKS**

### **System Response Times**
- California QAP Search: **51ms** (ChromaDB vector search)
- QCT/DDA Analysis: **<200ms** (comprehensive lookup)
- Environmental Screening: **797K+ records** indexed and searchable
- Cross-jurisdictional RAG: **27,344+ chunks** available

### **Data Coverage Statistics**
- **LIHTC Coverage**: 96.4% across 54 jurisdictions
- **QCT Accuracy**: 44,933 census tracts (100% HUD official)
- **Environmental Records**: 797,403 Texas TCEQ + expanding nationwide
- **Transit Analysis**: 264K+ California stops + HQTA integration

---

## 🎯 **CRITICAL SUCCESS FACTORS**

### **Data Quality Requirements**
1. **HUD Methodology**: MUST match Novogradac calculator exactly
2. **Distance Measurements**: Truncate to 2 decimals (never round up)
3. **Authority Hierarchy**: Federal law overrides state interpretations
4. **Official Sources**: HUD, Census, FEMA, state agencies only

### **Performance Standards**
1. **Response Times**: Sub-200ms for API calls
2. **Accuracy**: 96%+ automated processing success
3. **Coverage**: 54-jurisdiction comprehensive analysis
4. **Reliability**: Roman engineering standards (built to last)

---

**🏛️ Scientia Potentia Est - "Knowledge is Power" 🏛️**

*This document provides the foundation for all Bill and Vitor agent operations*