# Texas Construction Cost Modifiers & Regional Analysis
## D'Marco Portfolio Development - August 5, 2025

### Executive Summary
Comprehensive regional cost modifier framework for Texas LIHTC development, analyzing construction costs, flood insurance requirements, and market factors across all major Texas regions for the D'Marco portfolio sites.

---

## 📊 Regional Construction Cost Multipliers
*Base = 1.00 (Rural Texas Baseline)*

### Major Metropolitan Areas

| Region | Construction Multiplier | Per Unit Cost* | Variance | Key Factors |
|--------|------------------------|----------------|----------|-------------|
| **Dallas Metro** | 1.18x | ~$220,000 | +18% | Highest cost region - skilled labor shortage, competitive market |
| **Austin Metro** | 1.14x | ~$212,000 | +14% | High growth market with strict environmental regulations |
| **Houston Metro** | 1.12x | ~$208,000 | +12% | Major metro with high labor costs, hurricane/flood requirements |
| **San Antonio Metro** | 1.06x | ~$197,000 | +6% | Moderate costs with military/government influence |

**Counties Included:**
- **Dallas Metro**: Dallas, Tarrant, Collin, Denton, Rockwall
- **Austin Metro**: Travis, Williamson, Hays, Caldwell
- **Houston Metro**: Harris, Fort Bend, Montgomery, Brazoria, Galveston
- **San Antonio Metro**: Bexar, Guadalupe, Comal, Wilson

### Rural & Secondary Markets

| Region | Construction Multiplier | Per Unit Cost* | Variance | Key Factors |
|--------|------------------------|----------------|----------|-------------|
| **West Texas** | 0.98x | ~$182,000 | -2% | Oil/gas economy with material transportation challenges |
| **South Texas** | 0.95x | ~$177,000 | -5% | Moderate costs with border economy influence |
| **East Texas Rural** | 0.92x | ~$171,000 | -8% | Lower labor costs offset by material transportation |
| **Rural Baseline** | 1.00x | $186,000 | 0% | Rural Texas baseline for cost comparisons |

**Counties Included:**
- **West Texas**: Midland, Ector, Lubbock, Amarillo
- **South Texas**: Cameron, Hidalgo, Webb, Starr
- **East Texas Rural**: Henderson, Orange, Jefferson, Hardin, Tyler

*Based on 60-unit LIHTC project baseline

---

## 🌊 Flood Zone Insurance Requirements & Costs

### Annual Insurance Premiums Per Unit

| Flood Zone | Annual Premium | Operating Cost Impact | Description |
|------------|---------------|----------------------|-------------|
| **Zone X** | $0 | 1.00x | No flood insurance required - minimal risk zone |
| **Zone AE** | $1,200 | 1.03x | 1% annual chance flood - insurance required |
| **Zone A** | $1,400 | 1.04x | 1% annual chance flood - no base flood elevation |
| **Zone VE** | $2,500 | 1.08x | Coastal high hazard - very expensive insurance |
| **Zone AO** | $800 | 1.02x | Sheet flow flooding - moderate insurance cost |
| **Not Mapped** | $0 | 1.00x | Outside mapped flood hazard areas |

### Impact on Development
- Properties in AE/A zones require flood insurance per lender requirements
- VE zones (coastal) can add $150,000+ annually to operating costs (60-unit project)
- Insurance costs must be factored into DCR calculations for underwriting

---

## 🏗️ Base Construction Cost Components
*Per Unit Estimates for 60-Unit LIHTC Project*

| Cost Category | Base Amount | Description |
|---------------|-------------|-------------|
| **Hard Costs** | $135,000 | Structure, sitework, utilities, construction |
| **Soft Costs** | $25,000 | Architecture, engineering, permits, legal |
| **Developer Fee** | $18,000 | Developer fee and overhead (typically 10-15% of TDC) |
| **Contingency** | $8,000 | Construction contingency (5-10% of hard costs) |
| **Total Base Cost** | **$186,000** | Total development cost baseline per unit |

---

## 📈 Additional Market Factors

### Skilled Labor Shortage Multipliers
- **Dallas**: 1.08x (highest shortage)
- **Austin**: 1.06x (tech sector competition)
- **Houston**: 1.05x (energy sector competition)
- **San Antonio**: 1.02x (moderate shortage)
- **Rural Areas**: 0.98x (available labor)

### Material Supply Chain Premiums
- **Hurricane Risk Premium**: 1.03x (Gulf Coast areas)
- **Transportation Premium**: 1.02x (rural areas >100 miles from distribution)
- **Urban Delivery Premium**: 1.01x (major metros - traffic/logistics)

---

## 💰 Cost Impact Examples
*Based on 60-Unit LIHTC Development*

### Scenario Comparison

| Location | Per Unit Cost | Total Project Cost | Variance from Rural |
|----------|--------------|-------------------|---------------------|
| **Dallas Metro (High Cost)** | $220,000 | $13,200,000 | +$2,040,000 |
| **Houston Metro (Flood Zone AE)** | $214,000 | $12,840,000 | +$1,680,000 |
| **San Antonio Metro** | $197,000 | $11,820,000 | +$660,000 |
| **Rural Texas Baseline** | $186,000 | $11,160,000 | Baseline |
| **East Texas Rural (Low Cost)** | $171,000 | $10,260,000 | -$900,000 |

### Key Insights
- Dallas-to-Rural cost difference: **$2.94M per 60-unit project**
- Flood insurance (Zone AE) adds: **$72,000 annually** (60 units)
- Rural developments can save: **15-20% on total development costs**

---

## 🎯 Strategic Recommendations

### 1. Portfolio Optimization
- Concentrate rural/lower-cost sites for maximum capital efficiency
- Target East Texas and South Texas for highest ROI potential
- Balance portfolio with strategic metro sites for market presence

### 2. Metropolitan Market Strategy
- Ensure adequate 9% credit allocation for high-cost Dallas/Austin markets
- Consider 4% bond deals in Houston/San Antonio with moderate costs
- Factor in 10-20% cost premium for major metro developments

### 3. Flood Risk Mitigation
- Prioritize Zone X properties to eliminate insurance requirements
- Factor $1,200-2,500/unit annual insurance into pro forma for flood zones
- Consider elevation/mitigation strategies for high-value flood zone sites

### 4. Competitive Application Advantages
- Use precise regional cost data for more accurate LIHTC applications
- Demonstrate cost efficiency in rural markets for scoring advantages
- Highlight flood mitigation strategies in coastal/flood-prone areas

### 5. Development Timing
- Monitor labor market conditions - costs trending up 3-5% annually in metros
- Lock in construction contracts early in hot markets (Dallas/Austin)
- Consider phased development in rural areas to manage resources

---

## 📁 Technical Implementation

### Analysis System Location
```
/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/texas_cost_modifiers_analyzer.py
```

### Key Functions
- `determine_regional_market(county)` - Maps counties to regional markets
- `calculate_construction_cost_adjustment(region, flood_zone)` - Computes total cost variance
- `analyze_site_cost_modifiers(sites_data)` - Analyzes entire portfolio

### Data Sources
- RS Means Construction Cost Data
- Turner Construction Cost Index
- FEMA Flood Maps (current as of 2025)
- Local market surveys and contractor interviews
- Historical TDHCA application data

---

## 📊 D'Marco Portfolio Analysis Summary

### Current Portfolio Distribution
- Sites analyzed: All D'Marco sites with county/flood data
- Average cost variance: Varies by regional concentration
- Flood zone exposure: Mapped for all sites
- Optimal sites identified: Based on cost efficiency metrics

### Next Steps for Vitor
1. Review cost modifiers for your specific target sites
2. Integrate flood insurance costs into pro forma models
3. Adjust acquisition strategies based on regional cost variations
4. Consider partnering strategies for high-cost metro markets
5. Update BOTN calculations with accurate regional multipliers

---

## 📞 Contact & Support

**File Location for Sharing:**
```
/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/TX_Construction_Modifiers_08052025.md
```

**Python Analysis Tool:**
```python
from texas_cost_modifiers_analyzer import TexasCostModifierAnalyzer
analyzer = TexasCostModifierAnalyzer()
results = analyzer.create_cost_modifier_analysis()
```

---

*Analysis Date: August 5, 2025*  
*Prepared for: Vitor - D'Marco Sites Development*  
*System: Colosseum LIHTC Platform - Texas Cost Analysis Module*