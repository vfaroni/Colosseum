# Data Usage Agreement - LIHTC Site Scorer

## Data Sources and Attribution

### Public Domain Data Sources

1. **HUD QCT/DDA Data**
   - Source: U.S. Department of Housing and Urban Development
   - License: Public Domain
   - Usage: Federal qualification verification
   - Attribution: Not required but recommended

2. **Census Bureau Data**
   - Source: U.S. Census Bureau
   - License: Public Domain
   - Usage: Demographics, tract boundaries
   - Attribution: Required for commercial use

3. **State QAP Documents**
   - Source: State Housing Finance Agencies
   - License: Public Domain
   - Usage: Scoring criteria and requirements
   - Attribution: Required - cite source agency

### Third-Party Licensed Data

1. **OpenStreetMap (OSM)**
   - License: Open Database License (ODbL)
   - Usage: Amenity locations, POI data
   - Requirements:
     - Attribute OpenStreetMap contributors
     - Share-alike for derived databases
     - Link to ODbL license

2. **PositionStack API**
   - License: Commercial API license
   - Usage: Geocoding services
   - Requirements:
     - Comply with rate limits
     - No redistribution of results
     - Attribution in applications

3. **Google Maps API** (Optional)
   - License: Google Maps Platform Terms
   - Usage: Enhanced distance calculations
   - Requirements:
     - Display Google attribution
     - Comply with usage policies
     - Pay applicable fees

### Data Handling Requirements

#### Security
- Encrypt sensitive location data in transit and at rest
- Implement access controls for confidential analysis results
- Regular security audits of data handling processes

#### Privacy
- Do not store personally identifiable information
- Anonymize analysis results when sharing
- Respect location privacy in reporting

#### Retention
- Cache public data for maximum 30 days unless otherwise specified
- Delete user-provided coordinates after analysis completion
- Maintain audit logs for compliance purposes

### Attribution Requirements

When using this software or its results:

```
Analysis powered by LIHTC Site Scorer
Data sources: HUD, U.S. Census Bureau, OpenStreetMap contributors, 
State Housing Finance Agencies

Map data © OpenStreetMap contributors, available under ODbL
[Include link to openstreetmap.org/copyright]
```

### Compliance Obligations

#### Users Must:
1. Verify data accuracy before making business decisions
2. Comply with all third-party data source terms
3. Provide proper attribution in published materials
4. Report data quality issues to maintainers
5. Use data only for legitimate LIHTC development purposes

#### Users Must Not:
1. Redistribute raw data from licensed sources
2. Use data for discriminatory purposes
3. Violate rate limits or terms of API services
4. Store sensitive data beyond required retention periods
5. Reverse engineer proprietary scoring algorithms

### Data Quality Disclaimer

- Data accuracy depends on source data quality and timeliness
- Users must verify critical information independently
- No warranty provided for data completeness or accuracy
- Analysis results are estimates and should not be sole basis for investment decisions

### Updates and Changes

- Data sources may change without notice
- Users responsible for ensuring current data usage terms
- Notification provided for major licensing changes
- Grandfathering may apply to existing users

### Contact Information

For data licensing questions:
- Email: [data-licensing@company.com]
- Documentation: docs/data-sources.md
- Issue reporting: [GitHub issues or support system]

---

**Last Updated: July 2025**
**Review Date: January 2026**