# Test Plan for BOTN Template Validation System

## Feature Description
Create a comprehensive system to inspect and validate the 80AMIBOTN.xlsx workforce housing template structure, ensuring accurate cell mapping and data population for BOTN file generation.

## Contracts

### Input
- **Template File**: 80AMIBOTN.xlsx workforce housing template
- **Validation Mode**: inspect, validate, or map
- **Output Format**: JSON structure with cell mappings

### Output
- **Template Structure**: Complete mapping of all input fields and cell references
- **Validation Report**: Field locations, data types, and required inputs
- **Error Detection**: Missing fields, incorrect mappings, template issues

### Errors
- **FileNotFoundError**: When template file doesn't exist
- **TemplateStructureError**: When template format is invalid
- **MappingError**: When cell references are incorrect or missing

## Test Cases

### Unit Tests (Small, focused tests)

#### Test 1: Template File Access (Positive case)
- **Input**: Valid path to 80AMIBOTN.xlsx
- **Expected**: Successfully opens template and reads structure
- **Validation**: File exists, is accessible, contains expected sheets

#### Test 2: Invalid Template Path (Negative case)
- **Input**: Non-existent file path
- **Expected**: Raises FileNotFoundError with clear message
- **Validation**: Error handling works correctly

#### Test 3: Cell Mapping Extraction (Edge case)
- **Input**: Template with complex formatting and merged cells
- **Expected**: Correctly identifies all input cells and their purposes
- **Validation**: All workforce housing fields are mapped accurately

### Integration Tests (How parts work together)

#### Integration Test 1: Template Inspector to Data Mapper
- **Input**: Template analysis results used by data mapping system
- **Expected**: Seamless integration between inspection and mapping
- **Validation**: Cell references match between inspector and mapper

#### Integration Test 2: End-to-end BOTN Creation Validation
- **Input**: Real deal data through complete BOTN creation pipeline
- **Expected**: Generated BOTN files contain data in correct locations
- **Validation**: Manual verification of output files matches template structure