"""
TDHCA RAG System Configuration

Simple configuration file for easy customization of the TDHCA downloader and extractor.
Modify these settings based on your analysis needs.
"""

from pathlib import Path

# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_BASE = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG")

PATHS = {
    "raw_data": PROJECT_BASE / "raw_data",
    "4pct_apps": PROJECT_BASE / "raw_data" / "4pct_applications",
    "9pct_apps": PROJECT_BASE / "raw_data" / "9pct_applications", 
    "extracted_data": PROJECT_BASE / "raw_data" / "extracted_data",
    "third_party": PROJECT_BASE / "raw_data" / "third_party_reports",
    "status_logs": PROJECT_BASE / "raw_data" / "status_logs",
    "analysis": PROJECT_BASE / "analysis",
    "logs": PROJECT_BASE / "logs"
}

# =============================================================================
# DOWNLOAD SETTINGS
# =============================================================================

# Years to process (add more as needed)
YEARS_TO_PROCESS = ["2024", "2023"]

# Testing vs Production settings
TESTING_MODE = True  # Set to False for full processing

if TESTING_MODE:
    MAX_APPLICATIONS_PER_YEAR = 5    # Small number for testing
    PROCESS_THIRD_PARTY_REPORTS = False
else:
    MAX_APPLICATIONS_PER_YEAR = None  # Process all available
    PROCESS_THIRD_PARTY_REPORTS = True

# Application types to include
INCLUDE_4PCT_APPLICATIONS = True
INCLUDE_9PCT_APPLICATIONS = False  # Set to True when ready to expand

# Download behavior
DOWNLOAD_DELAY = 0.5  # Seconds between downloads (be respectful)
REQUEST_TIMEOUT = 30  # Seconds
SKIP_EXISTING_FILES = True  # Don't re-download existing files

# =============================================================================
# DATA EXTRACTION SETTINGS  
# =============================================================================

# PDF processing
MAX_PAGES_TO_PROCESS = 10  # Only process first N pages for speed
EXTRACT_FULL_TEXT = True   # Save full text for RAG system

# Data validation thresholds
MIN_VALID_UNITS = 5        # Minimum units for a valid project
MAX_VALID_UNITS = 2000     # Maximum units for a valid project
MIN_LAND_ACRES = 0.1       # Minimum land size in acres
MAX_COST_PER_ACRE = 2000000  # Maximum reasonable cost per acre

# =============================================================================
# ANALYSIS SETTINGS
# =============================================================================

# Major Texas MSAs for land cost analysis
TEXAS_MSA_MAPPINGS = {
    "Houston": "Houston-The Woodlands-Sugar Land, TX",
    "Dallas": "Dallas-Fort Worth-Arlington, TX", 
    "Austin": "Austin-Round Rock, TX",
    "San Antonio": "San Antonio-New Braunfels, TX",
    "Fort Worth": "Dallas-Fort Worth-Arlington, TX",
    "El Paso": "El Paso, TX",
    "McAllen": "McAllen-Edinburg-Mission, TX",
    "Corpus Christi": "Corpus Christi, TX"
}

# Unit mix categories to track
UNIT_TYPES = ["Studio", "1BR", "2BR", "3BR", "4BR", "5BR+"]

# Cost analysis ranges (for categorizing projects)
COST_PER_UNIT_CATEGORIES = {
    "low_cost": (0, 150000),
    "moderate_cost": (150000, 250000), 
    "high_cost": (250000, 400000),
    "very_high_cost": (400000, float('inf'))
}

# =============================================================================
# TDHCA WEBSITE URLS
# =============================================================================

TDHCA_BASE_URL = "https://www.tdhca.state.tx.us"
TDHCA_APPLICATIONS_BASE = f"{TDHCA_BASE_URL}/multifamily/docs/imaged"
TDHCA_STATUS_LOGS_BASE = "https://www.tdhca.texas.gov/sites/default/files/multifamily/docs/htc-4pct"

# URL patterns for different types of documents
URL_PATTERNS = {
    "4pct_application": "{base}/{year}-4-TEBApps/{app_num}.pdf",
    "9pct_application": "{base}/{year}-9-Apps/{app_num}.pdf", 
    "status_log": "{base}/{year}{current_year}{date}-4HTC-StatusLog.xlsx",
    "appraisal": "{base}/{year}-4-Appraisals/{app_num}.pdf",
    "market_study": "{base}/{year}-4-MarketStudies/{app_num}.pdf"
}

# =============================================================================
# EXTRACTION PATTERNS (for improving data extraction)
# =============================================================================

# Regular expression patterns for finding key data in PDFs
EXTRACTION_PATTERNS = {
    "project_name": [
        r'Project Name[:\s]+([^.\n]+)',
        r'Development Name[:\s]+([^.\n]+)',
        r'Property Name[:\s]+([^.\n]+)'
    ],
    
    "total_units": [
        r'Total Units[:\s]+(\d+)',
        r'Number of Units[:\s]+(\d+)',
        r'Total Residential Units[:\s]+(\d+)',
        r'(\d+)\s+total units'
    ],
    
    "land_cost": [
        r'Land Cost[:\s]+\$?([\d,]+)',
        r'Site Acquisition[:\s]+\$?([\d,]+)',
        r'Land Acquisition[:\s]+\$?([\d,]+)'
    ],
    
    "land_acres": [
        r'(\d+\.?\d*)\s+acres?',
        r'Site Size[:\s]+(\d+\.?\d*)\s+acres?',
        r'Land Area[:\s]+(\d+\.?\d*)\s+acres?'
    ],
    
    "construction_cost": [
        r'Total Development Cost[:\s]+\$?([\d,]+)',
        r'Total Construction Cost[:\s]+\$?([\d,]+)', 
        r'Total Project Cost[:\s]+\$?([\d,]+)'
    ]
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_TO_CONSOLE = True
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# =============================================================================
# EXPORT SETTINGS
# =============================================================================

# Output file formats
EXPORT_JSON = True    # For RAG system
EXPORT_CSV = True     # For Excel analysis
EXPORT_SUMMARY = True # Summary report

# JSON export settings
JSON_INDENT = 2
JSON_ENSURE_ASCII = False

# CSV export settings  
CSV_INDEX = False

# Summary report settings
INCLUDE_STATISTICS = True
INCLUDE_TOP_LOCATIONS = 10
INCLUDE_UNIT_MIX_BREAKDOWN = True