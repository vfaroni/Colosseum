# AcqUnderwriter - Real Estate Acquisition Analysis Tool

An AI-powered Streamlit application that automates real estate acquisition underwriting by extracting data from offering memorandums, financial statements, and rent rolls.

## Features

- **AI-Powered Data Extraction**: Automatically extracts property information from PDFs using OpenAI's GPT-4
- **Financial Analysis**: Processes T12 statements, rent rolls, and operating expenses
- **Google Sheets Integration**: Exports data directly to Google Sheets for further analysis
- **Multi-format Support**: Handles PDF, Excel, and various financial document formats
- **Session Persistence**: Saves extracted data to avoid re-processing

## Setup

### Prerequisites

- Python 3.8+
- OpenAI API key
- Google Cloud service account credentials (for Sheets integration)
- Dropbox folder with deal documents

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AcqUnderwriter.git
cd AcqUnderwriter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. **Google Authentication Setup (IMPORTANT)**:
   
   **Problem**: The app requires repeated Google authentication every session due to expired OAuth2 tokens.
   
   **Permanent Solution - Service Account Setup**:
   
   a. Go to [Google Cloud Console](https://console.cloud.google.com/)
   b. Create/select a project and enable these APIs:
      - Google Sheets API
      - Google Drive API
   c. Go to IAM & Admin → Service Accounts
   d. Create Service Account: "acq-underwriter"
   e. Grant roles: "Editor" (for Sheets and Drive access)
   f. Download JSON key file and save as `service-account-key.json` in project directory
   g. Run the setup script:
   ```bash
   python3 fix_google_auth.py install
   ```
   
   **Alternative - OAuth2 (requires re-auth periodically)**:
   ```bash
   gcloud auth application-default login
   ```
   
   The service account approach eliminates repeated authentication.

4. Configure OpenAI API key in the application sidebar

5. Run the application:
```bash
# Enhanced startup with connectivity fixes
python3 run_fixed.py
```
Or standard launch:
```bash
streamlit run AcquisitionAnalyst.py
```

## Usage

1. **Select a Deal**: Browse deals from your configured Dropbox folder
2. **Extract Data**: AI automatically extracts property details, financials, and rent information
3. **Review & Edit**: Verify and modify extracted data as needed
4. **Add to Pipeline**: Automatically add deal to your Pipeline Summary Excel file
5. **Export to Sheets**: Send data to Google Sheets for underwriting analysis

## System Reliability Contract

**The AcqUnderwriter application commits to the following guaranteed behaviors:**

### 🚀 **Streamlit Launch Contract**
1. **Automatic Session Management**: 
   - ✅ **Detects existing Streamlit processes** running on ports 8501-8510
   - ✅ **Gracefully terminates** conflicting Streamlit sessions on first startup
   - ✅ **Finds available port** automatically if conflicts exist
   - ✅ **No manual intervention required** - handles all session cleanup automatically

2. **Connection Reliability**:
   - ✅ **No timeout failures** - implements retry logic with exponential backoff
   - ✅ **Health checks** ensure application is fully ready before declaring success
   - ✅ **Automatic recovery** from connection failures without user intervention
   - ✅ **Clear status messages** throughout startup process with progress indicators

3. **Launch Guarantee**:
   - ✅ **One-command startup**: `python3 run_fixed.py` handles everything automatically
   - ✅ **Browser auto-launch** when application is confirmed ready
   - ✅ **Maximum 60-second startup time** or clear error message with recovery steps
   - ✅ **Fallback options** if primary launch method fails

### 🔐 **Google Authentication Contract**
1. **Persistent Authentication**:
   - ✅ **One-time setup** using service account eliminates repeated authentication
   - ✅ **Automatic credential refresh** for OAuth2 tokens when possible
   - ✅ **Credential persistence** between application sessions
   - ✅ **No re-authentication required** once properly configured

2. **Authentication Reliability**:
   - ✅ **Service account priority** - uses most reliable authentication method first
   - ✅ **Fallback authentication** methods if primary fails
   - ✅ **Clear setup instructions** for permanent authentication
   - ✅ **Immediate authentication status** visible on application startup

3. **Authentication Guarantee**:
   - ✅ **Setup once, use forever** - service account setup eliminates authentication issues
   - ✅ **Auto-detection** of available authentication methods
   - ✅ **Graceful degradation** to basic mode if authentication unavailable
   - ✅ **Recovery tools** built-in to fix authentication issues

### 📋 **Implementation Status**
- **Session Management**: ✅ **IMPLEMENTED** via SessionManager class
- **Connection Resilience**: ✅ **IMPLEMENTED** via ConnectionManager class  
- **Authentication Persistence**: ✅ **IMPLEMENTED** via GoogleAuthManager class
- **Enhanced Startup**: ✅ **IMPLEMENTED** via run_fixed.py script
- **User Experience**: ✅ **IMPLEMENTED** via AppLauncher class

### 🛠️ **How to Activate These Guarantees**

**For Streamlit Launch Contract:**
```bash
# Use the enhanced startup script (automatically handles everything)
python3 run_fixed.py
```

**For Google Authentication Contract:**
```bash
# One-time service account setup (permanent solution)
python3 fix_google_auth.py setup    # Get instructions
python3 fix_google_auth.py install  # After downloading service account key

# Or fix current OAuth2 authentication
python3 fix_google_auth.py fix
```

### ⚠️ **Contract Breach Resolution**
If these guarantees are not met:
1. **IMMEDIATE FIX**: Run `python3 implement_auth_contract.py` - This enforces the contract
2. **Check implementation**: Ensure you're using `python3 run_fixed.py` for startup
3. **Emergency fallback**: If contract fails, issue must be resolved before use
4. **No workarounds**: The application must fulfill these guarantees - no exceptions

### 🔒 **Contract Enforcement**
- **Zero tolerance policy**: Repeated authentication requests violate the contract
- **Automatic implementation**: `implement_auth_contract.py` enforces all guarantees
- **Verification**: Built-in compliance checking ensures contract adherence
- **Accountability**: Any breach triggers immediate contract enforcement

### 🔒 **Technical Implementation Details**
- **SessionManager**: Detects PIDs of existing Streamlit processes using psutil
- **ConnectionManager**: Implements exponential backoff with 3 retry attempts
- **GoogleAuthManager**: Saves credentials to ~/.acq_underwriter/ with proper permissions
- **AppLauncher**: Orchestrates entire startup process with health checks
- **Enhanced startup**: Provides real-time progress updates and error recovery

---

## Contracts & Templates

The application integrates with several contract templates and automated processes:

### BOTN (Back of the Napkin) Analysis
- **Template Integration**: Uses Google Sheets template for quick deal analysis
- **Automated Population**: Fills template with extracted property data
- **Financial Calculations**: Performs initial underwriting calculations
- **Template ID Configuration**: Set your BOTN template ID in the application sidebar

### Pipeline Summary Integration
- **Excel Export**: Creates standardized pipeline entries
- **29-Column Format**: Matches your existing Pipeline Summary structure
- **Automated Fields**: 
  - Asset Quality Assessment (A-D rating based on year built and unit count)
  - Location Quality Assessment (A-D rating based on city and market knowledge)
  - Median Household Income lookup by ZIP code
  - Broker information extraction
- **Export Process**: 
  1. Extract deal data using main application
  2. Click "📊 Export for Pipeline" button  
  3. Copy data from generated Excel file into main Pipeline Summary

### Contract Templates & Workflows

#### Letter of Intent (LOI) Generation
- **Data Integration**: Uses extracted property details for LOI creation
- **Market Analysis**: Incorporates comparable data and market conditions
- **Financial Terms**: Auto-calculates proposed pricing based on underwriting

#### Due Diligence Checklists
- **Property-Specific**: Generates checklists based on property type and location
- **Regulatory Requirements**: Includes local zoning and permit requirements
- **Financial Verification**: Creates tasks for income/expense verification

#### Purchase Agreement Support
- **Key Terms Population**: Auto-fills standard purchase agreement fields
- **Contingency Periods**: Suggests appropriate timelines based on property complexity
- **Special Conditions**: Identifies property-specific conditions needed

### Template Management

#### Setting Up Templates
1. **BOTN Template**: 
   - Create Google Sheets template with standard underwriting format
   - Add template ID to application configuration
   - Test template access using built-in test function

2. **Contract Templates**:
   - Store standard contract templates in designated Dropbox folder
   - Configure template paths in application settings
   - Set up version control for template updates

#### Template Customization
- **Field Mapping**: Configure which extracted fields populate which template sections
- **Conditional Logic**: Set rules for when certain clauses or terms apply
- **Market-Specific**: Create variations for different markets or property types

### Best Practices

#### Template Maintenance
- **Regular Updates**: Review and update templates quarterly
- **Version Control**: Keep dated versions of all contract templates  
- **Legal Review**: Have attorney review any template changes
- **Testing**: Validate template functionality with sample deals

#### Data Validation
- **Cross-Reference**: Verify extracted data against source documents
- **Range Checks**: Ensure financial data falls within reasonable ranges
- **Completeness**: Check that all required fields are populated before contract generation

#### Workflow Integration
- **Deal Stages**: Align contract generation with deal pipeline stages
- **Approval Process**: Implement review/approval workflow for generated contracts
- **Document Management**: Organize generated contracts in clear folder structure

## Project Structure

```
AcqUnderwriter/
├── AcquisitionAnalyst.py    # Main Streamlit application
├── app_config.json          # Application configuration
├── requirements.txt         # Python dependencies
├── run.sh                   # Launch script
├── SETUP_GUIDE.md          # Detailed setup instructions
└── test_app.py             # Test utilities
```

## Key Components

- **DataExtractor**: Handles AI-powered extraction from various document types
- **Form Fields**: Comprehensive property data model including:
  - Basic property information (name, address, units)
  - Financial metrics (T12 income, expenses, rents)
  - Unit mix and rent details by bedroom type
- **Session State Management**: Preserves extracted data between runs

## Recent Updates

- **NEW**: Comprehensive connectivity fixes for session management and authentication
- **NEW**: Google authentication persistence - no more repeated re-authentication 
- **NEW**: Enhanced startup script with automatic error recovery
- **NEW**: Unit count and rent calculation accuracy fixes (102 units, $2,243 avg)
- Fixed critical form field population bug
- Added comprehensive error handling
- Improved session state persistence
- Added T12 RUBS Income field support

## Connectivity Fixes

The application now includes comprehensive connectivity improvements:

### Session Management
- **Automatic detection** of existing Streamlit processes
- **Graceful shutdown** of conflicting sessions
- **Port conflict resolution** with automatic alternative port selection
- **Clear status messages** during startup

### Connection Resilience  
- **Retry logic** with exponential backoff for connection failures
- **Automatic recovery** from timeout errors
- **Health checks** to ensure application readiness
- **User-friendly error messages** with actionable recovery steps

### Google Authentication Persistence
- **Service account support** for permanent authentication
- **OAuth2 token persistence** with automatic refresh
- **Fallback to basic mode** when authentication unavailable
- **Clear setup instructions** to eliminate repeated authentication

### Enhanced User Experience
- **One-click launch** with `python3 run_fixed.py`
- **Progress indicators** during startup
- **Automatic browser opening** when ready
- **Comprehensive error handling** with recovery suggestions

## Troubleshooting

### Connection Issues
If you encounter connection problems:
1. Use the enhanced startup: `python3 run_fixed.py`
2. Check for existing Streamlit processes
3. Try alternative port if 8501 is busy
4. Clear browser cache and refresh

### Authentication Issues  
If Google authentication keeps failing:
1. **Permanent fix**: Set up service account (see installation step 3)
2. **Temporary fix**: Complete OAuth2 flow without interruption
3. Check that Google APIs are enabled in Cloud Console
4. Verify credentials have proper permissions

### Performance Issues
If the application is slow or unresponsive:
1. Check internet connection
2. Verify Dropbox folder access
3. Clear deal cache if needed
4. Check OpenAI API key status

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Private repository - All rights reserved

## Contact

Vitor Faroni - vitorfaroni@example.com