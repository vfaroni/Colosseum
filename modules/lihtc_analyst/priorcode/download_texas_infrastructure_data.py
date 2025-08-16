#!/usr/bin/env python3
"""
Texas Infrastructure Data Download Script
Downloads comprehensive infrastructure datasets for Texas affordable housing site analysis.

Based on research document: texas-infrastructure-data-download.md
Author: Claude Code
Date: July 2025
"""

import os
import requests
import pandas as pd
import zipfile
import time
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('texas_infrastructure_download.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Base directory for Texas datasets
BASE_DIR = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas")
DOWNLOAD_LOG = []

def create_directory_structure():
    """Create organized directory structure for datasets."""
    subdirs = [
        "Healthcare",
        "Libraries", 
        "City_Boundaries",
        "Water_Sewer_Infrastructure",
        "Electric_Utilities",
        "temp_downloads"
    ]
    
    for subdir in subdirs:
        dir_path = BASE_DIR / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")

def download_file(url, filename, description="", retries=3):
    """Download file with retry logic and progress tracking."""
    for attempt in range(retries):
        try:
            logger.info(f"Downloading {description}: {filename}")
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            file_path = BASE_DIR / "temp_downloads" / filename
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(file_path)
            logger.info(f"Downloaded {filename}: {file_size:,} bytes")
            
            DOWNLOAD_LOG.append({
                'filename': filename,
                'description': description,
                'url': url,
                'file_size': file_size,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            })
            
            return file_path
            
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed for {filename}: {e}")
            if attempt == retries - 1:
                DOWNLOAD_LOG.append({
                    'filename': filename,
                    'description': description,
                    'url': url,
                    'file_size': 0,
                    'timestamp': datetime.now().isoformat(),
                    'status': f'failed: {e}'
                })
            else:
                time.sleep(5)  # Wait before retry
    
    return None

def download_census_tiger_boundaries():
    """Download Census TIGER/Line city boundaries for Texas."""
    logger.info("Starting Census TIGER boundaries download...")
    
    # Direct download URL for Texas places (2024)
    tiger_url = "https://www2.census.gov/geo/tiger/TIGER2024/PLACE/tl_2024_48_place.zip"
    
    zip_file = download_file(
        tiger_url,
        "tl_2024_48_place.zip",
        "Texas Census TIGER Places (Cities/Towns)"
    )
    
    if zip_file:
        # Extract to City_Boundaries directory
        extract_dir = BASE_DIR / "City_Boundaries" / "TX_incorporated_places_2024"
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        logger.info(f"Extracted Census TIGER data to {extract_dir}")
        
        # Convert to GeoJSON using ogr2ogr if available
        try:
            import subprocess
            shp_file = extract_dir / "tl_2024_48_place.shp"
            geojson_file = BASE_DIR / "City_Boundaries" / "TX_cities_2024.geojson"
            
            subprocess.run([
                "ogr2ogr", "-f", "GeoJSON", 
                str(geojson_file), str(shp_file)
            ], check=True)
            
            logger.info(f"Converted to GeoJSON: {geojson_file}")
        except Exception as e:
            logger.warning(f"Could not convert to GeoJSON: {e}")

def download_hifld_electric_territories():
    """Download HIFLD Electric Service Territories."""
    logger.info("Starting HIFLD electric territories download...")
    
    # HIFLD ArcGIS REST API endpoint
    hifld_url = "https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Electric_Retail_Service_Territories/FeatureServer/0/query"
    
    # Parameters for Texas only
    params = {
        'where': "STATE = 'TX'",
        'outFields': '*',
        'outSR': '4326',
        'f': 'geojson',
        'resultOffset': 0,
        'resultRecordCount': 2000
    }
    
    try:
        response = requests.get(hifld_url, params=params, timeout=300)
        response.raise_for_status()
        
        output_file = BASE_DIR / "Electric_Utilities" / "TX_electric_service_territories_HIFLD_2025.geojson"
        
        with open(output_file, 'w') as f:
            f.write(response.text)
        
        logger.info(f"Downloaded HIFLD electric territories: {output_file}")
        
        DOWNLOAD_LOG.append({
            'filename': 'TX_electric_service_territories_HIFLD_2025.geojson',
            'description': 'HIFLD Electric Service Territories (Texas)',
            'url': hifld_url,
            'file_size': os.path.getsize(output_file),
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Failed to download HIFLD data: {e}")

def download_imls_libraries():
    """Download IMLS Public Libraries Survey data."""
    logger.info("Starting IMLS libraries download...")
    
    # IMLS API endpoint (if available) or direct file download
    # Note: This URL may need updating based on current IMLS data availability
    imls_url = "https://www.imls.gov/sites/default/files/2024-02/pls_fy2022_outlet_pud22i.csv"
    
    csv_file = download_file(
        imls_url,
        "pls_fy2022_outlet_pud22i.csv",
        "IMLS Public Libraries Survey FY2022"
    )
    
    if csv_file:
        try:
            # Filter for Texas libraries
            df = pd.read_csv(csv_file)
            tx_libraries = df[df['STABR'] == 'TX'].copy()
            
            output_file = BASE_DIR / "Libraries" / "TX_public_libraries_IMLS_2022.csv"
            tx_libraries.to_csv(output_file, index=False)
            
            logger.info(f"Filtered and saved {len(tx_libraries)} Texas libraries to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to process IMLS data: {e}")

def create_manual_download_instructions():
    """Create instructions for datasets requiring manual download."""
    manual_downloads = """
# Texas Infrastructure Datasets Requiring Manual Download

## 1. Texas Health Care Information Collection (THCIC) Hospitals
- URL: https://www.dshs.texas.gov/thcic/hospitals/Download.shtm
- Reason: Requires data use agreement
- Save as: Healthcare/TX_hospitals_THCIC_2025.csv
- Notes: Navigate through agreement, download hospital directory

## 2. CMS National Provider Identifier (NPI) Registry
- URL: https://download.cms.gov/nppes/NPI_Files.html
- Reason: 9.3 GB file, requires filtering
- Save as: Healthcare/TX_urgent_care_NPI_2025.csv
- Processing: Filter for Texas (TX) + taxonomy code 261QU0200X

## 3. TCEQ Water Districts
- URL: https://gis-tceq.opendata.arcgis.com/
- Reason: Interactive portal
- Save as: Water_Sewer_Infrastructure/TX_water_districts_TCEQ_2025.geojson
- Search: "water districts" or "water service areas"

## 4. Texas Water Development Board
- URL: https://www.twdb.texas.gov/mapping/gisdata.asp
- Reason: Multiple datasets, may require registration
- Save as: Water_Sewer_Infrastructure/TX_*_TWDB_2025.*
- Datasets: PWS service areas, wastewater plants, water supply corps

## 5. Texas State Library Directory
- URL: https://www.tsl.texas.gov/ld/librarydirectory/
- Reason: May require export or scraping
- Save as: Libraries/TX_libraries_TSLAC_2025.csv
- Notes: Look for export option or contact for dataset

## Next Steps After Manual Downloads:
1. Run process_downloaded_data.py to clean and organize
2. Geocode addresses where coordinates are missing
3. Create master index with create_dataset_index.py
"""
    
    manual_file = BASE_DIR / "TX_manual_downloads_needed.txt"
    with open(manual_file, 'w') as f:
        f.write(manual_downloads)
    
    logger.info(f"Created manual download instructions: {manual_file}")

def save_download_log():
    """Save download log to CSV."""
    log_df = pd.DataFrame(DOWNLOAD_LOG)
    log_file = BASE_DIR / f"TX_infrastructure_download_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    log_df.to_csv(log_file, index=False)
    logger.info(f"Saved download log: {log_file}")

def main():
    """Main download orchestration."""
    logger.info("Starting Texas Infrastructure Data Download")
    
    # Create directory structure
    create_directory_structure()
    
    # Download datasets (Priority 1 - Essential)
    logger.info("=== PRIORITY 1 DOWNLOADS ===")
    download_census_tiger_boundaries()
    time.sleep(2)  # Rate limiting
    
    download_hifld_electric_territories()
    time.sleep(2)
    
    # Download datasets (Priority 2 - Enhanced)
    logger.info("=== PRIORITY 2 DOWNLOADS ===")
    download_imls_libraries()
    
    # Create manual download instructions
    create_manual_download_instructions()
    
    # Create download log
    save_download_log()
    
    logger.info("Texas Infrastructure Data Download Complete")
    logger.info(f"Check {BASE_DIR}/TX_manual_downloads_needed.txt for required manual downloads")
    logger.info(f"Total automated downloads attempted: {len(DOWNLOAD_LOG)}")
    
    # Summary
    successful = sum(1 for log in DOWNLOAD_LOG if log['status'] == 'success')
    logger.info(f"Successful downloads: {successful}/{len(DOWNLOAD_LOG)}")

if __name__ == "__main__":
    main()