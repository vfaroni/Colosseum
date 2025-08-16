# DATASET ACQUISITION STANDARDS
## Colosseum Data Intelligence Framework

### MANDATORY METADATA REQUIREMENTS

**For EVERY dataset acquired, create `DATASET_METADATA.md` with:**

#### 1. Source Information
```
**Dataset Name**: [Official dataset title]
**Source Organization**: [Government agency, organization]
**Source URL**: [Direct link to dataset page]
**Download URL**: [Direct download link]
**Source Contact**: [Email or contact information if available]
```

#### 2. Acquisition Details
```
**Acquisition Date**: [YYYY-MM-DD HH:MM:SS timezone]
**Acquired By**: [Agent/person name]
**Original Filename**: [Exact filename as downloaded]
**File Size**: [Size in MB/GB]
**Available Formats**: [CSV, GeoJSON, Shapefile, etc.]
**Format Downloaded**: [Which format we chose]
```

#### 3. Dataset Timeline
```
**Dataset Creation Date**: [When source compiled/created it]
**Dataset Last Updated**: [Most recent update by source]
**Update Frequency**: [Daily, weekly, monthly, annually, as-needed]
**Version/Release**: [If applicable]
```

#### 4. Update Monitoring
```
**Update Check URL**: [Where to check for newer versions]
**Update Notification**: [RSS, email list, or manual check method]
**Next Scheduled Check**: [When we should check for updates]
**Update Responsibility**: [Which agent/person monitors]
```

#### 5. Technical Specifications
```
**Coordinate System**: [EPSG code, e.g., EPSG:4326]
**Data Type**: [Point, Line, Polygon, Tabular]
**Record Count**: [Number of features/records]
**Geographic Coverage**: [State, region, nationwide]
**Key Fields**: [Most important columns/attributes]
```

#### 6. Quality Assessment
```
**Completeness**: [Percentage of complete records]
**Accuracy Assessment**: [Known issues, validation results]
**Coordinate Validation**: [Geographic bounds check]
**Data Issues**: [Missing data, formatting problems, etc.]
**Fitness for LIHTC Analysis**: [How suitable for our use cases]
```

#### 7. Usage Notes
```
**Primary Use Cases**: [Site analysis, transit scoring, etc.]
**Integration Requirements**: [How it connects with other datasets]
**Processing Applied**: [Coordinate transforms, cleaning, etc.]
**Known Limitations**: [What this dataset cannot be used for]
```

### FILE ORGANIZATION STANDARDS

```
/Data_Sets/[state]/[category]/[dataset_name]/
├── [dataset_files].[format]
├── DATASET_METADATA.md
└── processing_log.txt (if processing applied)
```

### PYTHON METADATA GENERATION TEMPLATE

```python
def generate_dataset_metadata(
    dataset_name, source_org, source_url, download_url,
    original_filename, file_size, format_downloaded,
    creation_date, last_updated, update_frequency,
    coord_system, record_count, geographic_coverage
):
    metadata_template = f"""# {dataset_name}
## Dataset Metadata

### Source Information
**Dataset Name**: {dataset_name}
**Source Organization**: {source_org}
**Source URL**: {source_url}
**Download URL**: {download_url}

### Acquisition Details
**Acquisition Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}
**Acquired By**: [Agent Name]
**Original Filename**: {original_filename}
**File Size**: {file_size}
**Format Downloaded**: {format_downloaded}

### Dataset Timeline
**Dataset Creation Date**: {creation_date}
**Dataset Last Updated**: {last_updated}
**Update Frequency**: {update_frequency}

### Technical Specifications
**Coordinate System**: {coord_system}
**Record Count**: {record_count}
**Geographic Coverage**: {geographic_coverage}

### Quality Assessment
**Completeness**: [To be assessed]
**Coordinate Validation**: [To be performed]
**Fitness for LIHTC Analysis**: [To be evaluated]

---
*Metadata generated automatically by Colosseum Data Acquisition Infrastructure*
*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    return metadata_template
```

### UPDATE TRACKING REQUIREMENTS

1. **Monthly Update Checks**: Review all datasets for updates
2. **Version Control**: Track changes when datasets are updated
3. **Impact Assessment**: Determine if updates affect existing analysis
4. **Documentation**: Log all update activities and decisions

### QUALITY ASSURANCE CHECKLIST

- [ ] Source URL accessible and verified
- [ ] Metadata file complete with all required sections
- [ ] Coordinate system validated
- [ ] Geographic bounds checked
- [ ] File integrity verified
- [ ] Integration with existing datasets tested
- [ ] Update monitoring strategy established

---

**CRITICAL**: No dataset should be used in production analysis without complete metadata documentation following these standards.

**Created**: August 3, 2025  
**Version**: 1.0  
**Applies To**: All Colosseum data acquisition activities