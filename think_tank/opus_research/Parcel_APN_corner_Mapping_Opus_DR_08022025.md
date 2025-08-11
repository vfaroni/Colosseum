# The complete guide to obtaining US parcel boundary data for affordable housing development

For affordable housing developers needing precise parcel boundaries rather than just address points, the landscape of available data sources ranges from free government portals to sophisticated commercial APIs. This comprehensive research covers all 50 states with special focus on California and Texas, providing practical guidance for your Colosseum module implementation.

## Free sources vary dramatically by state

The availability of free parcel boundary data across the US follows **three distinct patterns**: states with centralized programs offering easy statewide access, states requiring county-by-county searches, and states with minimal digital availability.

**New York and Arkansas lead in free access**, providing standardized statewide downloads covering 36 and 69 counties respectively. New York's program at gis.ny.gov/parcels offers direct download of a comprehensive geodatabase, while Arkansas provides shapefile downloads through their state GIS portal. Connecticut aggregates all municipal data annually, and Texas maintains an ongoing collection through TxGIO covering approximately 200 of 254 counties.

Federal sources like data.gov provide limited coverage, mainly offering scattered county datasets rather than comprehensive national data. The USGS National Map focuses on administrative boundaries rather than private parcels, making it unsuitable for housing development needs.

For states without centralized programs, developers must contact individual county assessor offices. This approach works well in tech-forward counties like King County, WA, and Cook County, IL, but becomes time-intensive when dealing with multiple jurisdictions.

## Commercial providers offer comprehensive solutions

**Regrid emerges as the most transparent commercial option**, covering 150+ million parcels (99% of US residents) with pricing starting around $80,000 annually for nationwide bulk access. Their partnership with Esri, excellent API documentation, and "Data with Purpose" nonprofit program make them particularly suitable for affordable housing organizations. Individual county purchases range from $200-2,000 depending on size.

ATTOM Data and CoreLogic represent the enterprise-grade options, offering the highest data quality but requiring custom pricing negotiations. CoreLogic's ParcelPoint is considered the "Cadillac of parcel data" with near real-time updates but comes with complex licensing and transaction limits through the ArcGIS Marketplace.

ReportAll offers 30-day free trials covering 159.4 million parcels, while newer entrants like GetParcelData claim 30% below-market pricing. Regional specialists like TaxNetUSA provide more affordable options for Texas and Florida projects.

LightBox SmartFabric stands out for comprehensive real estate data beyond just boundaries, including 25+ years of historical data and building-level details, though its enterprise focus and multi-API approach may exceed typical affordable housing project needs.

## Government sources provide the foundation

County assessor offices remain the authoritative source for parcel data, though accessibility varies significantly. Urban counties typically maintain robust GIS departments with regular data updates, while rural counties may still operate with paper-based systems.

**State GIS portals aggregate county data with varying success**. California's state geoportal (gis.data.ca.gov) provides some aggregated datasets, though most comprehensive access still requires county-level searches. Regional councils of governments (COGs) like Southern California Association of Governments (SCAG) and Association of Bay Area Governments (ABAG) offer standardized regional data covering multiple counties.

The distinction between assessment parcels and legal parcels proves crucial for development. Assessment parcels (used for tax purposes) may not reflect legal lot boundaries required for building permits. California's Subdivision Map Act clearly defines this distinction, requiring developers to verify legal parcel status for development feasibility.

## California offers multiple pathways to parcel data

California's fragmented data landscape reflects its size and diversity, but several resources provide comprehensive coverage. The **California Strategic Growth Council's statewide collection** covers 51 of 58 counties in a single 3.4GB geodatabase, though with limited attributes and potentially dated information.

**ParcelQuest dominates California's commercial market** as the only provider with daily updates from all 58 county assessors. With pricing starting around $100-300/month for basic access, they maintain an in-house cadastral mapping team ensuring data quality. Their standardization of formats across counties saves significant processing time.

Regional consortiums provide middle-ground solutions: SCAG covers 6 Southern California counties (including Los Angeles and Orange) with free registration-based access, while ABAG provides similar services for 9 Bay Area counties. These regional datasets include demographic and planning layers valuable for affordable housing analysis.

Los Angeles County sets the standard for free county-level access through their Enterprise GIS Hub, offering regular updates and comprehensive attribute data. San Francisco, Alameda, and Santa Clara counties provide good online access, while rural Central Valley counties often require direct contact.

## Texas data access relies on CAD systems

Texas's 254 counties maintain parcel data through **253 independent Central Appraisal Districts (CADs)**, creating unique challenges and opportunities. The Texas Geographic Information Office (TxGIO) provides free statewide aggregation through data.tnris.org, though coverage remains incomplete with approximately 200 counties participating.

**Major metropolitan CADs offer excellent free access**. Harris County (Houston) provides quarterly shapefile updates, Dallas CAD maintains regular GIS data products, and Travis County (Austin) data integrates with both local and state systems. These urban districts typically offer the highest quality data with minimal barriers.

The North Central Texas Council of Governments (NCTCOG) coordinates regional data for the 16-county Dallas-Fort Worth metroplex, providing standardized access and cost-sharing opportunities through cooperative purchasing agreements.

Commercial options for Texas include Regrid's county-by-county purchases (roughly $200-2,000 per county depending on size) and Texas County GIS Data's tiered offerings ranging from basic "as-is" data to premium nightly-updated cleaned datasets. TaxNetUSA specializes in Texas and Florida markets with more affordable regional pricing.

## APIs provide scalable integration options

Modern parcel data APIs follow RESTful design patterns, with most providers offering both individual parcel lookups and bulk operations. **Regrid's API stands out for developer experience**, providing OpenAPI specifications, 200 requests/minute rate limits, real-time usage monitoring, and a free sandbox environment.

Response formats typically include GeoJSON for web applications and shapefiles for GIS software. Coordinate data comes as arrays of longitude/latitude pairs forming polygon boundaries. Multi-polygon parcels (common for properties split by roads or waterways) require special handling in processing logic.

Authentication varies from simple API keys to OAuth implementations. Rate limiting protects infrastructure while batch endpoints enable efficient bulk operations. Pagination handles large result sets, with most providers limiting individual responses to 1,000 parcels.

## Bulk downloads suit large-scale analysis

For comprehensive analysis across multiple counties or states, bulk downloads prove more economical than API calls. **File formats include shapefiles** (industry standard requiring .shp, .dbf, .shx, and .prj files), GeoJSON (web-friendly text format), and geodatabases (ESRI's format with advanced capabilities).

California's Strategic Growth Council provides a 3.4GB statewide geodatabase, while individual counties typically offer shapefile downloads ranging from 50MB to several gigabytes. Texas counties through TxGIO come in standardized geodatabase format facilitating easier integration.

Processing considerations include coordinate system conversions (most data comes in state plane coordinates requiring transformation to WGS84), attribute standardization across sources, and handling of multi-polygon parcels. Memory-efficient processing using libraries like GeoPandas with chunking prevents system overload on large datasets.

## Technical implementation requires careful planning

**Python dominates parcel data processing** with GeoPandas providing high-level operations, Shapely handling geometric calculations, and Fiona managing file I/O. A typical vertex extraction workflow reads shapefiles, iterates through polygon features, extracts coordinate pairs, and handles both single and multi-polygon geometries.

JavaScript developers can leverage Turf.js for browser and Node.js applications, providing modular geospatial functions without heavyweight dependencies. The @turf/helpers and @turf/distance modules prove particularly useful for distance calculations to schools, transit, and environmental hazards.

Coordinate reference system (CRS) handling remains critical, as mixing projections causes significant errors. Most parcel data arrives in state plane coordinates optimized for local accuracy, requiring transformation to WGS84 (EPSG:4326) for web mapping. PyProj and proj4js handle these transformations reliably.

Performance optimization strategies include spatial indexing with R-tree structures for fast lookups, parallel processing for vertex extraction across multiple CPU cores, and PostgreSQL/PostGIS for persistent storage with built-in spatial operations.

## Legal considerations shape data usage

**Public parcel boundary data generally carries no copyright restrictions**, though attribution requirements vary by source. California and Texas both treat parcel boundaries as public records, with the main distinction being assessment versus legal parcels for development purposes.

Commercial data licenses typically prohibit redistribution while permitting internal use and derived products. Regrid explicitly allows commercial use with their standard license, while some providers require enterprise agreements for commercial applications. Nonprofit organizations should inquire about discounted "social impact" pricing from all major providers.

Privacy considerations apply mainly to owner information rather than boundaries themselves. Some jurisdictions redact addresses for judges, law enforcement, and domestic violence victims. Building automated systems should implement appropriate privacy filters.

Data accuracy disclaimers universally state that GIS parcel data isn't survey-grade and shouldn't be used for legal boundary determination. For affordable housing development, this limitation rarely poses problems as survey work occurs later in the development process.

## Integration recommendations for Colosseum

Based on this research, a **hybrid approach maximizes value** for the Colosseum affordable housing module:

Start with free sources for initial site identification - California's Strategic Growth Council data and Texas TxGIO provide sufficient coverage for preliminary analysis. Use regional consortium data (SCAG, ABAG, NCTCOG) where available for better quality and additional demographic layers.

Implement Regrid's API for production use, taking advantage of their nonprofit pricing and standardized national schema. Their vertex extraction eliminates preprocessing overhead while daily updates ensure data currency.

Design the system architecture around PostgreSQL/PostGIS for spatial queries, implement coordinate transformation pipelines for standardizing different source projections, and use spatial indexing for efficient distance calculations. Build validation routines to identify and flag multi-polygon parcels requiring special handling.

For batch processing, Python with GeoPandas provides the most mature ecosystem, while Node.js with Turf.js enables lighter-weight processing for web-based tools. Implement chunked processing for large counties to manage memory usage, and use parallel processing for vertex extraction operations.

This comprehensive approach to parcel boundary data acquisition and processing will enable the Colosseum module to perform accurate distance calculations for larger parcels, significantly improving site selection accuracy for affordable housing development compared to simple address-point geocoding.