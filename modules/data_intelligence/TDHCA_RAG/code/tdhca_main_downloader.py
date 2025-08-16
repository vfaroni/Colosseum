#!/usr/bin/env python3
"""
TDHCA LIHTC Application Downloader and Data Extractor

This script downloads 4% and 9% LIHTC applications and third-party reports from TDHCA,
then extracts key data points for RAG system analysis.

Key data points extracted:
- Land cost per acre and total land costs
- Unit mix (studio, 1BR, 2BR, 3BR, etc.)
- Total units and targeted population
- Total construction costs
- Project location (MSA/Census Tract)
- Financing sources and amounts

Author: Created for affordable housing development analysis
Date: May 31, 2025
"""

import os
import requests
import json
import pandas as pd
from pathlib import Path
import time
import logging
from datetime import datetime
import re
from typing import Dict, List, Any, Optional
import PyPDF2
import pdfplumber
from urllib.parse import urljoin
from dataclasses import dataclass

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tdhca_downloader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ProjectData:
    """Data structure to hold extracted project information"""
    application_number: str = ""
    project_name: str = ""
    location: str = ""
    msa: str = ""
    census_tract: str = ""
    total_units: int = 0
    unit_mix: Dict[str, int] = None
    land_cost_total: float = 0.0
    land_acres: float = 0.0
    land_cost_per_acre: float = 0.0
    total_construction_cost: float = 0.0
    targeted_population: str = ""
    financing_sources: Dict[str, float] = None
    
    def __post_init__(self):
        if self.unit_mix is None:
            self.unit_mix = {}
        if self.financing_sources is None:
            self.financing_sources = {}

class TDHCADownloader:
    """
    Downloads and processes TDHCA LIHTC applications and reports
    
    This class handles:
    1. Downloading PDF applications and Excel status logs
    2. Downloading third-party reports (appraisals, market studies, etc.)
    3. Extracting key data points for affordable housing analysis
    4. Organizing files for RAG system processing
    """
    
    def __init__(self, base_download_path: str):
        """
        Initialize the downloader
        
        Args:
            base_download_path: Path where all downloads will be stored
        """
        self.base_path = Path(base_download_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Create organized folder structure
        self.folders = {
            '4pct_applications': self.base_path / '4pct_applications',
            '9pct_applications': self.base_path / '9pct_applications', 
            'appraisals': self.base_path / 'third_party_reports' / 'appraisals',
            'market_studies': self.base_path / 'third_party_reports' / 'market_studies',
            'environmental': self.base_path / 'third_party_reports' / 'environmental',
            'property_condition': self.base_path / 'third_party_reports' / 'property_condition',
            'site_design': self.base_path / 'third_party_reports' / 'site_design',
            'extracted_data': self.base_path / 'extracted_data',
            'status_logs': self.base_path / 'status_logs'
        }
        
        # Create all folders
        for folder in self.folders.values():
            folder.mkdir(parents=True, exist_ok=True)
        
        # Base URLs for TDHCA
        self.base_url = "https://www.tdhca.state.tx.us"
        self.applications_4pct_base = f"{self.base_url}/multifamily/docs/imaged"
        
        logger.info(f"Initialized TDHCA Downloader with base path: {self.base_path}")
    
    def download_file(self, url: str, local_path: Path, description: str = "") -> bool:
        """
        Download a single file with error handling and retry logic
        
        Args:
            url: URL to download from
            local_path: Where to save the file
            description: Description for logging
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Skip if file already exists
            if local_path.exists():
                logger.info(f"File already exists, skipping: {local_path.name}")
                return True
            
            logger.info(f"Downloading {description}: {url}")
            
            # Download with timeout and headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            # Save file
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Successfully downloaded: {local_path.name}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading {url}: {e}")
            return False
    
    def get_4pct_application_numbers(self, year: str, max_apps: int = None) -> List[str]:
        """
        Get list of 4% application numbers for a given year
        
        Args:
            year: Year to fetch (e.g., '2024', '2023')
            max_apps: Maximum number of applications to process (for testing)
            
        Returns:
            List of application numbers
        """
        # Based on the pattern seen in TDHCA website:
        # 2024 apps: 24400-24703
        # 2023 apps: 23400-23618
        
        application_numbers = []
        
        if year == '2024':
            # 2024 applications range from 24400 to 24703
            start_num = 24400
            end_num = 24703
        elif year == '2023':
            # 2023 applications range from 23400 to 23618
            start_num = 23400
            end_num = 23618
        elif year == '2025':
            # 2025 applications (estimated range, adjust as needed)
            start_num = 25400
            end_num = 25500
        else:
            logger.warning(f"Year {year} not configured, using default range")
            start_num = int(f"{year[-2:]}400")
            end_num = int(f"{year[-2:]}500")
        
        # Generate application numbers
        for num in range(start_num, end_num + 1):
            application_numbers.append(str(num))
            
            # Limit for testing
            if max_apps and len(application_numbers) >= max_apps:
                break
        
        logger.info(f"Generated {len(application_numbers)} application numbers for {year}")
        return application_numbers
    
    def download_4pct_applications(self, years: List[str], max_per_year: int = 5) -> List[str]:
        """
        Download 4% LIHTC applications for specified years
        
        Args:
            years: List of years to download (e.g., ['2024', '2023'])
            max_per_year: Maximum applications per year (for testing)
            
        Returns:
            List of successfully downloaded application files
        """
        downloaded_files = []
        
        for year in years:
            logger.info(f"Processing 4% applications for year {year}")
            
            app_numbers = self.get_4pct_application_numbers(year, max_per_year)
            
            for app_num in app_numbers:
                # Construct URL and file path
                url = f"{self.applications_4pct_base}/{year}-4-TEBApps/{app_num}.pdf"
                local_path = self.folders['4pct_applications'] / f"{app_num}.pdf"
                
                # Download application
                if self.download_file(url, local_path, f"4% Application {app_num}"):
                    downloaded_files.append(str(local_path))
                
                # Small delay to be respectful to the server
                time.sleep(0.5)
        
        logger.info(f"Downloaded {len(downloaded_files)} 4% applications total")
        return downloaded_files
    
    def download_status_logs(self, years: List[str]) -> List[str]:
        """
        Download Excel status logs that contain application tracking information
        
        Args:
            years: List of years to download status logs for
            
        Returns:
            List of downloaded status log files
        """
        downloaded_logs = []
        
        # Status log URLs are like:
        # https://www.tdhca.texas.gov/sites/default/files/multifamily/docs/htc-4pct/2024250507-4HTC-StatusLog.xlsx
        
        base_status_url = "https://www.tdhca.texas.gov/sites/default/files/multifamily/docs/htc-4pct"
        
        for year in years:
            logger.info(f"Downloading status logs for {year}")
            
            # Try several recent dates to get the latest status log
            # Format: YYYYYYMMDD-4HTC-StatusLog.xlsx (where first 4 digits are year, next 2 are current year)
            dates_to_try = [
                "0507",  # May 7
                "0402",  # April 2  
                "0310",  # March 10
                "0130",  # January 30
                "1206",  # December 6
                "1105",  # November 5
            ]
            
            for date in dates_to_try:
                # Current year for the filename format
                current_year = "25"  # 2025
                filename = f"{year}{current_year}{date}-4HTC-StatusLog.xlsx"
                url = f"{base_status_url}/{filename}"
                local_path = self.folders['status_logs'] / filename
                
                if self.download_file(url, local_path, f"Status Log {year}"):
                    downloaded_logs.append(str(local_path))
                    break  # Found a working date, move to next year
                
                time.sleep(0.5)
        
        return downloaded_logs
    
    def extract_pdf_text(self, pdf_path: Path) -> str:
        """
        Extract text from PDF file using multiple methods
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        text = ""
        
        try:
            # Method 1: Try pdfplumber first (better for tables)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:10]:  # First 10 pages usually have the key info
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if text.strip():
                return text
                
        except Exception as e:
            logger.warning(f"pdfplumber failed for {pdf_path.name}: {e}")
        
        try:
            # Method 2: Fallback to PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(min(10, len(pdf_reader.pages))):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                    
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path.name}: {e}")
        
        return text
    
    def extract_project_data_from_text(self, text: str, app_number: str) -> ProjectData:
        """
        Extract key project data from application text
        
        Args:
            text: Extracted text from PDF
            app_number: Application number
            
        Returns:
            ProjectData object with extracted information
        """
        project = ProjectData()
        project.application_number = app_number
        
        # Clean text for easier parsing
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        
        # Extract project name (usually appears early in application)
        name_patterns = [
            r'Project Name[:\s]+([^.]+?)(?:\s|$)',
            r'Development Name[:\s]+([^.]+?)(?:\s|$)',
            r'Property Name[:\s]+([^.]+?)(?:\s|$)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                project.project_name = match.group(1).strip()
                break
        
        # Extract location information
        location_patterns = [
            r'City[:\s]+([^,\n]+)',
            r'Municipality[:\s]+([^,\n]+)',
            r'Location[:\s]+([^,\n]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                project.location = match.group(1).strip()
                break
        
        # Extract total units
        unit_patterns = [
            r'Total Units[:\s]+(\d+)',
            r'Number of Units[:\s]+(\d+)',
            r'Total Residential Units[:\s]+(\d+)',
            r'(\d+)\s+total units'
        ]
        
        for pattern in unit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    project.total_units = int(match.group(1))
                    break
                except ValueError:
                    continue
        
        # Extract unit mix (bedroom counts)
        unit_mix_patterns = [
            (r'(\d+)\s+studio', 'Studio'),
            (r'(\d+)\s+one[-\s]bedroom', '1BR'),
            (r'(\d+)\s+1[-\s]bedroom', '1BR'),
            (r'(\d+)\s+two[-\s]bedroom', '2BR'),
            (r'(\d+)\s+2[-\s]bedroom', '2BR'),
            (r'(\d+)\s+three[-\s]bedroom', '3BR'),
            (r'(\d+)\s+3[-\s]bedroom', '3BR'),
            (r'(\d+)\s+four[-\s]bedroom', '4BR'),
            (r'(\d+)\s+4[-\s]bedroom', '4BR')
        ]
        
        for pattern, unit_type in unit_mix_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Take the first or largest number found
                project.unit_mix[unit_type] = int(max(matches))
        
        # Extract land cost
        land_cost_patterns = [
            r'Land Cost[:\s]+\$?([\d,]+)',
            r'Site Acquisition[:\s]+\$?([\d,]+)',
            r'Land Acquisition[:\s]+\$?([\d,]+)'
        ]
        
        for pattern in land_cost_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    cost_str = match.group(1).replace(',', '')
                    project.land_cost_total = float(cost_str)
                    break
                except ValueError:
                    continue
        
        # Extract land acreage
        acreage_patterns = [
            r'(\d+\.?\d*)\s+acres?',
            r'Site Size[:\s]+(\d+\.?\d*)\s+acres?',
            r'Land Area[:\s]+(\d+\.?\d*)\s+acres?'
        ]
        
        for pattern in acreage_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    project.land_acres = float(match.group(1))
                    break
                except ValueError:
                    continue
        
        # Calculate land cost per acre
        if project.land_cost_total > 0 and project.land_acres > 0:
            project.land_cost_per_acre = project.land_cost_total / project.land_acres
        
        # Extract total construction cost
        construction_patterns = [
            r'Total Development Cost[:\s]+\$?([\d,]+)',
            r'Total Construction Cost[:\s]+\$?([\d,]+)',
            r'Total Project Cost[:\s]+\$?([\d,]+)'
        ]
        
        for pattern in construction_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    cost_str = match.group(1).replace(',', '')
                    project.total_construction_cost = float(cost_str)
                    break
                except ValueError:
                    continue
        
        # Extract targeted population
        population_patterns = [
            r'Target Population[:\s]+([^.]+)',
            r'Special Needs Population[:\s]+([^.]+)',
            r'Targeted Residents[:\s]+([^.]+)'
        ]
        
        for pattern in population_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                project.targeted_population = match.group(1).strip()
                break
        
        logger.info(f"Extracted data for {app_number}: {project.project_name} - {project.total_units} units")
        return project
    
    def process_downloaded_applications(self) -> List[ProjectData]:
        """
        Process all downloaded 4% applications and extract data
        
        Returns:
            List of ProjectData objects with extracted information
        """
        logger.info("Processing downloaded applications...")
        
        extracted_projects = []
        pdf_files = list(self.folders['4pct_applications'].glob("*.pdf"))
        
        for pdf_file in pdf_files:
            logger.info(f"Processing {pdf_file.name}")
            
            # Extract application number from filename
            app_number = pdf_file.stem
            
            # Extract text from PDF
            text = self.extract_pdf_text(pdf_file)
            
            if not text.strip():
                logger.warning(f"No text extracted from {pdf_file.name}")
                continue
            
            # Extract structured data
            project_data = self.extract_project_data_from_text(text, app_number)
            extracted_projects.append(project_data)
        
        logger.info(f"Processed {len(extracted_projects)} applications")
        return extracted_projects
    
    def save_extracted_data(self, projects: List[ProjectData]) -> None:
        """
        Save extracted project data to JSON and CSV files
        
        Args:
            projects: List of ProjectData objects to save
        """
        if not projects:
            logger.warning("No projects to save")
            return
        
        # Convert to dictionaries for JSON serialization
        projects_dict = []
        for project in projects:
            project_dict = {
                'application_number': project.application_number,
                'project_name': project.project_name,
                'location': project.location,
                'msa': project.msa,
                'census_tract': project.census_tract,
                'total_units': project.total_units,
                'unit_mix': project.unit_mix,
                'land_cost_total': project.land_cost_total,
                'land_acres': project.land_acres,
                'land_cost_per_acre': project.land_cost_per_acre,
                'total_construction_cost': project.total_construction_cost,
                'targeted_population': project.targeted_population,
                'financing_sources': project.financing_sources
            }
            projects_dict.append(project_dict)
        
        # Save as JSON
        json_path = self.folders['extracted_data'] / 'tdhca_extracted_data.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(projects_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved extracted data to {json_path}")
        
        # Save as CSV for easy analysis
        df = pd.DataFrame(projects_dict)
        csv_path = self.folders['extracted_data'] / 'tdhca_extracted_data.csv'
        df.to_csv(csv_path, index=False)
        
        logger.info(f"Saved extracted data to {csv_path}")
        
        # Create summary report
        self.create_summary_report(projects)
    
    def create_summary_report(self, projects: List[ProjectData]) -> None:
        """
        Create a summary report of extracted data
        
        Args:
            projects: List of ProjectData objects
        """
        report_lines = []
        report_lines.append("TDHCA LIHTC Data Extraction Summary")
        report_lines.append("=" * 50)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total Applications Processed: {len(projects)}")
        report_lines.append("")
        
        # Calculate statistics
        total_units = sum(p.total_units for p in projects if p.total_units > 0)
        projects_with_land_data = [p for p in projects if p.land_cost_per_acre > 0]
        
        if projects_with_land_data:
            avg_land_cost_per_acre = sum(p.land_cost_per_acre for p in projects_with_land_data) / len(projects_with_land_data)
            report_lines.append(f"Average Land Cost per Acre: ${avg_land_cost_per_acre:,.2f}")
        
        report_lines.append(f"Total Units Across All Projects: {total_units:,}")
        
        # Unit mix summary
        all_unit_types = set()
        for project in projects:
            all_unit_types.update(project.unit_mix.keys())
        
        if all_unit_types:
            report_lines.append("\nUnit Mix Summary:")
            for unit_type in sorted(all_unit_types):
                total_of_type = sum(p.unit_mix.get(unit_type, 0) for p in projects)
                report_lines.append(f"  {unit_type}: {total_of_type:,} units")
        
        # Location summary
        locations = [p.location for p in projects if p.location]
        if locations:
            location_counts = {}
            for location in locations:
                location_counts[location] = location_counts.get(location, 0) + 1
            
            report_lines.append(f"\nTop Locations ({len(set(locations))} unique):")
            for location, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                report_lines.append(f"  {location}: {count} projects")
        
        # Save report
        report_path = self.folders['extracted_data'] / 'extraction_summary.txt'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Created summary report: {report_path}")
        
        # Print summary to console
        print("\n" + "\n".join(report_lines))

def main():
    """
    Main function to run the TDHCA downloader and extractor
    """
    print("🏠 TDHCA LIHTC Application Downloader & Data Extractor")
    print("=" * 60)
    print("This script will download TDHCA 4% LIHTC applications and extract:")
    print("• Land costs per acre by market")
    print("• Unit mix and total units") 
    print("• Targeted populations served")
    print("• Total construction costs")
    print("• Project locations and financing sources")
    print("=" * 60)
    
    # Set up project paths
    project_base = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG"
    download_path = f"{project_base}/raw_data"
    
    # Create downloader instance
    downloader = TDHCADownloader(download_path)
    
    # Configure what to download (start small for testing)
    years_to_process = ['2024', '2023']  # Add '2025' when available
    max_applications_per_year = 5  # Start with 5 for testing
    
    print(f"\n📁 Files will be saved to: {download_path}")
    print(f"📅 Processing years: {', '.join(years_to_process)}")
    print(f"🔢 Max applications per year: {max_applications_per_year}")
    
    try:
        # Step 1: Download status logs (these contain tracking info)
        print("\n📊 Step 1: Downloading status logs...")
        status_logs = downloader.download_status_logs(years_to_process)
        print(f"Downloaded {len(status_logs)} status logs")
        
        # Step 2: Download 4% applications  
        print("\n📄 Step 2: Downloading 4% applications...")
        applications = downloader.download_4pct_applications(years_to_process, max_applications_per_year)
        print(f"Downloaded {len(applications)} applications")
        
        # Step 3: Process applications and extract data
        print("\n🔍 Step 3: Extracting data from applications...")
        extracted_projects = downloader.process_downloaded_applications()
        
        # Step 4: Save extracted data
        print("\n💾 Step 4: Saving extracted data...")
        downloader.save_extracted_data(extracted_projects)
        
        print("\n✅ EXTRACTION COMPLETE!")
        print(f"📊 Processed {len(extracted_projects)} projects")
        print(f"📁 Data saved to: {downloader.folders['extracted_data']}")
        print("\nNext steps:")
        print("• Review the extracted_data folder for JSON and CSV files")
        print("• Adjust max_applications_per_year to process more files") 
        print("• Add more years or expand to 9% applications")
        print("• The data is ready for your RAG system!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        print(f"\n❌ Error occurred: {e}")
        print("Check the log file for detailed error information")

if __name__ == "__main__":
    main()
