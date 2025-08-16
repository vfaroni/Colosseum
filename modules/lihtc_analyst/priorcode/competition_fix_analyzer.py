#!/usr/bin/env python3
"""
Competition Fix Analyzer - Standalone fix for competition detection
Focuses ONLY on fixing the en-dash character issue in TDHCA coordinates

Author: Claude Code
Date: 2025-06-21
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from geopy.distance import geodesic

class CompetitionFixAnalyzer:
    """Standalone analyzer to fix competition detection issues"""
    
    def __init__(self):
        self.setup_logging()
        self.data_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets")
        self.tdhca_projects = pd.DataFrame()
        
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def load_tdhca_projects(self):
        """Load TDHCA projects with FIXED coordinate handling"""
        project_file = self.data_path / "State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
        
        try:
            # Load raw data
            raw_projects = pd.read_excel(project_file)
            self.logger.info(f"Loaded {len(raw_projects)} total TDHCA projects")
            
            # CRITICAL FIX: Handle en-dash character in Longitude11
            self.logger.info("Applying en-dash character fix...")
            
            # Clean coordinates
            raw_projects['Latitude_Clean'] = pd.to_numeric(raw_projects['Latitude11'], errors='coerce')
            raw_projects['Longitude_Clean'] = pd.to_numeric(
                raw_projects['Longitude11'].astype(str).str.replace('‐', '-', regex=False), 
                errors='coerce'
            )
            
            # Log the fix
            endash_count = raw_projects['Longitude11'].astype(str).str.contains('‐', na=False).sum()
            self.logger.info(f"Fixed {endash_count} en-dash characters in longitude data")
            
            # Map to standard column names
            raw_projects['Latitude'] = raw_projects['Latitude_Clean']
            raw_projects['Longitude'] = raw_projects['Longitude_Clean']
            
            # Filter to recent projects with valid coordinates
            self.tdhca_projects = raw_projects[
                (pd.to_numeric(raw_projects['Year'], errors='coerce').between(2021, 2024)) &
                (raw_projects['Latitude'].notna()) & 
                (raw_projects['Longitude'].notna()) &
                (raw_projects['Latitude'].between(25, 37)) &  # Valid Texas latitude
                (raw_projects['Longitude'].between(-107, -93))  # Valid Texas longitude
            ].copy()
            
            # Convert Year to numeric
            self.tdhca_projects['Year'] = pd.to_numeric(self.tdhca_projects['Year'], errors='coerce')
            
            total_projects = len(self.tdhca_projects)
            self.logger.info(f"Filtered to {total_projects} recent TDHCA projects (2021-2024) with valid coordinates")
            
            # Validation
            if total_projects > 0:
                year_counts = self.tdhca_projects['Year'].value_counts().sort_index()
                self.logger.info(f"Projects by year: {year_counts.to_dict()}")
                
                # Test with sample project
                sample = self.tdhca_projects.iloc[0]
                self.logger.info(f"Sample project: {sample['Development Name']} at ({sample['Latitude']:.4f}, {sample['Longitude']:.4f})")
            
        except Exception as e:
            self.logger.error(f"Error loading TDHCA projects: {e}")
            self.tdhca_projects = pd.DataFrame()
    
    def check_competition_for_site(self, lat, lon, county):
        """Check competition for a single site"""
        results = {
            'One_Mile_Count': 0,
            'Two_Mile_Count': 0,
            'Competing_Projects': '',
            'Competition_Fatal_4pct': False,
            'Competition_Fatal_9pct': False
        }
        
        if self.tdhca_projects.empty or pd.isna(lat) or pd.isna(lon):
            return results
        
        site_point = (lat, lon)
        large_counties = ['Harris', 'Dallas', 'Tarrant', 'Bexar', 'Travis', 'Collin', 'Fort Bend']
        competing_projects = []
        
        for _, project in self.tdhca_projects.iterrows():
            project_lat = project['Latitude']
            project_lon = project['Longitude']
            project_year = project['Year']
            
            if pd.isna(project_lat) or pd.isna(project_lon):
                continue
            
            project_point = (project_lat, project_lon)
            
            try:
                distance = geodesic(site_point, project_point).miles
            except Exception:
                continue
            
            # One Mile Three Year Rule (2022-2024)
            if distance <= 1.0 and project_year >= 2022:
                results['One_Mile_Count'] += 1
                proj_name = project.get('Development Name', 'Unknown')
                competing_projects.append(f"{proj_name} ({int(project_year)}, {distance:.2f}mi)")
                results['Competition_Fatal_9pct'] = True  # Fatal for 9% deals
                
            # Two Mile Same Year Rule (large counties, 2024 only)
            if distance <= 2.0 and county in large_counties and project_year == 2024:
                results['Two_Mile_Count'] += 1
                if distance > 1.0:  # Avoid double counting
                    proj_name = project.get('Development Name', 'Unknown')
                    competing_projects.append(f"{proj_name} ({int(project_year)}, {distance:.2f}mi, 2-mile)")
                    results['Competition_Fatal_9pct'] = True
        
        results['Competing_Projects'] = '; '.join(competing_projects)
        return results
    
    def test_competition_detection(self):
        """Test competition detection with known sites"""
        if self.tdhca_projects.empty:
            self.logger.error("No TDHCA projects loaded - cannot test")
            return
        
        # Test sites (some should have competition in major metros)
        test_sites = [
            {'name': 'Austin Downtown', 'lat': 30.2672, 'lon': -97.7431, 'county': 'Travis'},
            {'name': 'Houston Downtown', 'lat': 29.7604, 'lon': -95.3698, 'county': 'Harris'},
            {'name': 'Dallas Downtown', 'lat': 32.7767, 'lon': -96.7970, 'county': 'Dallas'},
            {'name': 'San Antonio Downtown', 'lat': 29.4241, 'lon': -98.4936, 'county': 'Bexar'},
        ]
        
        self.logger.info("Testing competition detection:")
        for site in test_sites:
            result = self.check_competition_for_site(site['lat'], site['lon'], site['county'])
            self.logger.info(f"{site['name']}: 1-mile: {result['One_Mile_Count']}, 2-mile: {result['Two_Mile_Count']}")
            if result['Competing_Projects']:
                self.logger.info(f"  Competing: {result['Competing_Projects'][:100]}...")

def main():
    """Test the competition fix"""
    analyzer = CompetitionFixAnalyzer()
    analyzer.load_tdhca_projects()
    analyzer.test_competition_detection()

if __name__ == "__main__":
    main()