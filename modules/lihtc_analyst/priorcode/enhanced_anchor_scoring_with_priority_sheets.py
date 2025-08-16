#!/usr/bin/env python3
"""
Enhanced Anchor Scoring with Business Priority Sheets
Combines the new highway/utility scoring with the original business deliverables:
- High Priority Sites sheet
- Recommended Sites sheet  
- Fatal/Isolated Sites sheet
- Detailed Scoring Methodology sheet

Enhanced 6-Factor Scoring:
1. Schools (2.5 mi) - 30% (reduced from 40%)
2. City Incorporation - 15% (reduced from 20%) 
3. LIHTC Market Validation - 25% (reduced from 30%)
4. Community Scale - 10% (unchanged)
5. Highway Access - 15% (NEW)
6. Utility Service - 5% (NEW)

Author: Claude Code
Date: July 2025
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path
import json
import logging
from datetime import datetime
from geopy.distance import geodesic
from shapely.geometry import Point

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedAnchorScoringWithPriorities:
    """Enhanced 6-factor anchor scoring with business priority sheets"""
    
    def __init__(self):
        # Enhanced scoring weights (6-factor)
        self.scoring_weights = {
            'schools_2_5_miles': 0.30,      # Reduced from 0.40
            'city_incorporation': 0.15,     # Reduced from 0.20
            'lihtc_market_validation': 0.25, # Reduced from 0.30
            'community_scale': 0.10,        # Unchanged
            'highway_access': 0.15,         # NEW
            'utility_service': 0.05         # NEW
        }
        
        # Business priority thresholds (0-5 scale)
        self.priority_thresholds = {
            'High Priority': 4.0,     # Score ≥ 4.0 (80%+)
            'Recommended': 3.0,       # Score ≥ 3.0 (60%+)
            'Caution': 2.0,          # Score ≥ 2.0 (40%+)
            'Fatal': 0.0             # Score < 2.0
        }
        
        # Load infrastructure data for recalculation
        self._load_infrastructure_data()
    
    def load_data(self):
        """Load existing anchor analysis and highway proximity data"""
        
        # Load original anchor analysis
        anchor_file = "Complete_Anchor_Analysis_All_195_Sites_20250702_151312.xlsx"
        if not Path(anchor_file).exists():
            raise FileNotFoundError(f"Anchor analysis file not found: {anchor_file}")
        
        self.anchor_df = pd.read_excel(anchor_file, sheet_name='All_195_Sites_Ranked')
        logger.info(f"✅ Loaded {len(self.anchor_df)} sites from anchor analysis")
        
        # Load highway proximity analysis
        highway_files = list(Path('.').glob('Highway_Proximity_Analysis_*.xlsx'))
        if not highway_files:
            raise FileNotFoundError("Highway proximity analysis file not found")
        
        highway_file = max(highway_files)  # Get most recent
        self.highway_df = pd.read_excel(highway_file, sheet_name='Highway_Proximity_Analysis')
        logger.info(f"✅ Loaded {len(self.highway_df)} sites from highway analysis")
        
        # Merge datasets
        self._merge_datasets()
    
    def _merge_datasets(self):
        """Merge anchor and highway datasets"""
        
        # Merge on coordinates (most reliable)
        self.combined_df = pd.merge(
            self.anchor_df,
            self.highway_df[['Latitude', 'Longitude', 'Highway_Access_Score', 'Highway_Access_Rating',
                           'Interstate_Distance_Miles', 'US_Highway_Distance_Miles', 'State_Highway_Distance_Miles']],
            on=['Latitude', 'Longitude'],
            how='left'
        )
        
        logger.info(f"✅ Merged datasets: {len(self.combined_df)} sites total")
        
        # Check for missing highway data
        missing_highway = self.combined_df['Highway_Access_Score'].isna().sum()
        if missing_highway > 0:
            logger.warning(f"⚠️  {missing_highway} sites missing highway data - will use 0 score")
            self.combined_df['Highway_Access_Score'] = self.combined_df['Highway_Access_Score'].fillna(0)
            self.combined_df['Highway_Access_Rating'] = self.combined_df['Highway_Access_Rating'].fillna('Isolated - No highway access')
    
    def calculate_utility_service_score(self):
        """Calculate simplified utility service score"""
        
        logger.info("🔧 Calculating utility service scores...")
        
        utility_scores = []
        
        for _, row in self.combined_df.iterrows():
            score = 0.0
            notes = []
            
            # Base scoring on city incorporation and population
            within_city = row.get('Within_City_Limits', False)
            city_name = row.get('City_Name', '')
            schools_count = row.get('Schools_Within_2_5mi', 0)
            
            if within_city and city_name:
                # Within incorporated city limits
                if schools_count >= 5:
                    score = 1.0
                    notes.append("Large incorporated city")
                elif schools_count >= 2:
                    score = 0.8
                    notes.append("Medium incorporated city")
                else:
                    score = 0.6
                    notes.append("Small incorporated city")
            else:
                # Unincorporated area
                highway_score = row.get('Highway_Access_Score', 0)
                if highway_score >= 0.8:
                    score = 0.4
                    notes.append("Unincorporated, good highway access")
                elif highway_score >= 0.4:
                    score = 0.2
                    notes.append("Unincorporated, limited highway access")
                else:
                    score = 0.0
                    notes.append("Unincorporated, poor access")
            
            utility_scores.append({
                'score': score,
                'notes': '; '.join(notes)
            })
        
        # Add to dataframe
        self.combined_df['Utility_Service_Score'] = [item['score'] for item in utility_scores]
        self.combined_df['Utility_Service_Notes'] = [item['notes'] for item in utility_scores]
        
        logger.info("✅ Utility service scores calculated")
    
    def _load_infrastructure_data(self):
        """Load Texas infrastructure datasets for recalculation"""
        base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas")
        
        try:
            # Load schools
            schools_file = base_dir / "TX_Public_Schools" / "Schools_2024_to_2025.geojson"
            self.schools_gdf = gpd.read_file(schools_file).to_crs('EPSG:4326')
            logger.info(f"✅ Loaded {len(self.schools_gdf)} Texas schools for recalculation")
            
            # Load TDHCA projects
            tdhca_file = base_dir / "State Specific" / "TX" / "Project_List" / "TX_TDHCA_Project_List_05252025.xlsx"
            self.tdhca_df = pd.read_excel(tdhca_file)
            
            # Fix coordinate column names and clean data
            self.tdhca_df = self.tdhca_df.rename(columns={
                'Latitude11': 'Latitude',
                'Longitude11': 'Longitude'
            })
            self.tdhca_df = self.tdhca_df.dropna(subset=['Latitude', 'Longitude'])
            
            # Convert to numeric and filter valid coordinates
            self.tdhca_df['Latitude'] = pd.to_numeric(self.tdhca_df['Latitude'], errors='coerce')
            self.tdhca_df['Longitude'] = pd.to_numeric(self.tdhca_df['Longitude'], errors='coerce')
            self.tdhca_df = self.tdhca_df.dropna(subset=['Latitude', 'Longitude'])
            
            # Filter for reasonable Texas coordinates
            self.tdhca_df = self.tdhca_df[
                (self.tdhca_df['Latitude'] >= 25.0) & (self.tdhca_df['Latitude'] <= 37.0) &
                (self.tdhca_df['Longitude'] >= -107.0) & (self.tdhca_df['Longitude'] <= -93.0)
            ]
            
            logger.info(f"✅ Loaded {len(self.tdhca_df)} TDHCA projects for recalculation")
            
        except Exception as e:
            logger.error(f"Error loading infrastructure data: {e}")
            raise
    
    def recalculate_schools_and_lihtc(self):
        """Recalculate schools and LIHTC proximity for all sites"""
        
        logger.info("🏫 Recalculating schools and LIHTC proximity for all sites...")
        
        schools_counts = []
        lihtc_counts = []
        
        for _, row in self.combined_df.iterrows():
            lat = row.get('Latitude')
            lng = row.get('Longitude')
            
            if pd.isna(lat) or pd.isna(lng):
                schools_counts.append(0)
                lihtc_counts.append(0)
                continue
            
            # Calculate schools within 2.5 miles
            schools_count = 0
            try:
                site_point = Point(lng, lat)
                for _, school in self.schools_gdf.iterrows():
                    if hasattr(school.geometry, 'x') and hasattr(school.geometry, 'y'):
                        distance = geodesic((lat, lng), (school.geometry.y, school.geometry.x)).miles
                        if distance <= 2.5:
                            schools_count += 1
            except Exception as e:
                logger.debug(f"Error counting schools for site {lat}, {lng}: {e}")
            
            schools_counts.append(schools_count)
            
            # Calculate LIHTC projects within 2 miles
            lihtc_count = 0
            try:
                for _, project in self.tdhca_df.iterrows():
                    distance = geodesic((lat, lng), (project['Latitude'], project['Longitude'])).miles
                    if distance <= 2.0:
                        lihtc_count += 1
            except Exception as e:
                logger.debug(f"Error counting LIHTC projects for site {lat}, {lng}: {e}")
            
            lihtc_counts.append(lihtc_count)
        
        # Update the dataframe with recalculated values
        self.combined_df['Schools_Within_2_5mi'] = schools_counts
        self.combined_df['LIHTC_Within_2mi'] = lihtc_counts
        
        schools_avg = np.mean(schools_counts)
        lihtc_avg = np.mean(lihtc_counts)
        
        logger.info(f"✅ Recalculated proximity data:")
        logger.info(f"   Schools: avg {schools_avg:.1f} per site, max {max(schools_counts)}")
        logger.info(f"   LIHTC: avg {lihtc_avg:.1f} per site, max {max(lihtc_counts)}")
    
    def calculate_enhanced_anchor_scores(self):
        """Calculate enhanced 6-factor anchor scores"""
        
        logger.info("📊 Calculating enhanced anchor scores...")
        
        # Debug: Check what data we actually have
        logger.info(f"Sample data columns: {list(self.combined_df.columns)[:10]}...")
        
        # Check if we have the required data
        required_cols = ['Schools_Within_2_5mi', 'LIHTC_Within_2mi', 'Within_City_Limits']
        missing_cols = [col for col in required_cols if col not in self.combined_df.columns]
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            raise ValueError(f"Missing required columns for anchor scoring: {missing_cols}")
        
        # Check for NaN values and handle them
        schools_nan = self.combined_df['Schools_Within_2_5mi'].isna().sum()
        lihtc_nan = self.combined_df['LIHTC_Within_2mi'].isna().sum()
        
        if schools_nan > 0 or lihtc_nan > 0:
            logger.warning(f"Found NaN values: Schools={schools_nan}, LIHTC={lihtc_nan}")
            logger.warning("Filling NaN values with 0 for calculations")
            self.combined_df['Schools_Within_2_5mi'] = self.combined_df['Schools_Within_2_5mi'].fillna(0)
            self.combined_df['LIHTC_Within_2mi'] = self.combined_df['LIHTC_Within_2mi'].fillna(0)
            self.combined_df['Within_City_Limits'] = self.combined_df['Within_City_Limits'].fillna(False)
        
        enhanced_scores = []
        
        for _, row in self.combined_df.iterrows():
            # Extract original anchor components (normalized to 0-1)
            # Convert to numeric and handle any remaining NaN values
            schools_count = pd.to_numeric(row.get('Schools_Within_2_5mi', 0), errors='coerce')
            if pd.isna(schools_count):
                schools_count = 0
            
            lihtc_count = pd.to_numeric(row.get('LIHTC_Within_2mi', 0), errors='coerce')
            if pd.isna(lihtc_count):
                lihtc_count = 0
            
            city_limits = row.get('Within_City_Limits', False)
            if pd.isna(city_limits):
                city_limits = False
            
            # Calculate component scores (normalized to 0-1)
            schools_score = min(schools_count / 2.0, 1.0)  # 2+ schools = max
            city_score = 1.0 if city_limits else 0.0
            lihtc_score = min(lihtc_count / 2.0, 1.0)  # 2+ projects = max
            scale_score = min(schools_count / 5.0, 1.0)  # 5+ schools = max
            
            # New components (already 0-1 normalized)
            highway_score = row.get('Highway_Access_Score', 0)
            if pd.isna(highway_score):
                highway_score = 0
            
            utility_score = row.get('Utility_Service_Score', 0)
            if pd.isna(utility_score):
                utility_score = 0
            
            # Calculate weighted score
            total_score = (
                schools_score * self.scoring_weights['schools_2_5_miles'] +
                city_score * self.scoring_weights['city_incorporation'] +
                lihtc_score * self.scoring_weights['lihtc_market_validation'] +
                scale_score * self.scoring_weights['community_scale'] +
                highway_score * self.scoring_weights['highway_access'] +
                utility_score * self.scoring_weights['utility_service']
            ) * 5.0  # Scale to 0-5
            
            # Determine business priority classification
            priority = self._classify_business_priority(total_score)
            
            enhanced_scores.append({
                'Enhanced_Anchor_Score': round(total_score, 3),
                'Business_Priority_Classification': priority,
                'Schools_Component': round(schools_score * self.scoring_weights['schools_2_5_miles'] * 5, 3),
                'City_Component': round(city_score * self.scoring_weights['city_incorporation'] * 5, 3),
                'LIHTC_Component': round(lihtc_score * self.scoring_weights['lihtc_market_validation'] * 5, 3),
                'Scale_Component': round(scale_score * self.scoring_weights['community_scale'] * 5, 3),
                'Highway_Component': round(highway_score * self.scoring_weights['highway_access'] * 5, 3),
                'Utility_Component': round(utility_score * self.scoring_weights['utility_service'] * 5, 3)
            })
        
        # Add to dataframe
        for key in enhanced_scores[0].keys():
            self.combined_df[key] = [item[key] for item in enhanced_scores]
        
        # Add business recommendations
        self._add_business_recommendations()
        
        logger.info("✅ Enhanced anchor scores calculated")
    
    def _classify_business_priority(self, score):
        """Classify score into business priority categories"""
        if score >= self.priority_thresholds['High Priority']:
            return 'High Priority'
        elif score >= self.priority_thresholds['Recommended']:
            return 'Recommended'
        elif score >= self.priority_thresholds['Caution']:
            return 'Proceed with Caution'
        else:
            return 'Do Not Pursue'
    
    def _add_business_recommendations(self):
        """Add business recommendation columns"""
        
        recommendations = []
        next_steps = []
        
        for _, row in self.combined_df.iterrows():
            priority = row['Business_Priority_Classification']
            score = row['Enhanced_Anchor_Score']
            
            if priority == 'High Priority':
                recommendations.append('HIGHLY RECOMMENDED - Excellent Infrastructure & Highway Access')
                next_steps.append('Proceed with immediate due diligence and LOI')
            elif priority == 'Recommended':
                recommendations.append('RECOMMENDED - Adequate Infrastructure, Good Development Potential')
                next_steps.append('Conduct detailed market study and infrastructure assessment')
            elif priority == 'Proceed with Caution':
                recommendations.append('PROCEED WITH CAUTION - Limited Infrastructure, Requires Mitigation')
                next_steps.append('Address infrastructure and highway access concerns before proceeding')
            else:
                recommendations.append('DO NOT PURSUE - Inadequate Infrastructure/Highway Access')
                next_steps.append('Find alternative locations with better infrastructure connectivity')
        
        self.combined_df['Development_Recommendation'] = recommendations
        self.combined_df['Immediate_Next_Steps'] = next_steps
    
    def save_results_with_priority_sheets(self, output_file):
        """Save enhanced analysis with business priority sheets"""
        
        logger.info(f"💾 Saving enhanced analysis with priority sheets to: {output_file}")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            
            # 1. All Sites Ranked (main sheet)
            self.combined_df.to_excel(writer, sheet_name='All_Sites_Enhanced_Ranking', index=False)
            
            # 2. High Priority Sites (≥4.0 score)
            high_priority = self.combined_df[
                self.combined_df['Business_Priority_Classification'] == 'High Priority'
            ].copy()
            if len(high_priority) > 0:
                high_priority = high_priority.sort_values('Enhanced_Anchor_Score', ascending=False)
                high_priority.to_excel(writer, sheet_name='High_Priority_Sites', index=False)
            
            # 3. Recommended Sites (≥3.0 score)
            recommended = self.combined_df[
                self.combined_df['Business_Priority_Classification'].isin(['High Priority', 'Recommended'])
            ].copy()
            if len(recommended) > 0:
                recommended = recommended.sort_values('Enhanced_Anchor_Score', ascending=False)
                recommended.to_excel(writer, sheet_name='Recommended_Sites', index=False)
            
            # 4. Fatal/Isolated Sites (<2.0 score)
            fatal = self.combined_df[
                self.combined_df['Business_Priority_Classification'] == 'Do Not Pursue'
            ].copy()
            if len(fatal) > 0:
                fatal = fatal.sort_values('Enhanced_Anchor_Score', ascending=True)
                fatal.to_excel(writer, sheet_name='Fatal_Isolated_Sites', index=False)
            
            # 5. Executive Summary
            self._create_executive_summary_sheet(writer)
            
            # 6. Enhanced Methodology Documentation
            self._create_enhanced_methodology_sheet(writer)
            
            # 7. Component Analysis
            self._create_component_analysis_sheet(writer)
        
        logger.info("✅ Results saved with all business priority sheets")
    
    def _create_executive_summary_sheet(self, writer):
        """Create executive summary with enhanced statistics"""
        
        total_sites = len(self.combined_df)
        
        # Count by business priority
        high_priority_count = len(self.combined_df[self.combined_df['Business_Priority_Classification'] == 'High Priority'])
        recommended_count = len(self.combined_df[self.combined_df['Business_Priority_Classification'] == 'Recommended'])
        caution_count = len(self.combined_df[self.combined_df['Business_Priority_Classification'] == 'Proceed with Caution'])
        fatal_count = len(self.combined_df[self.combined_df['Business_Priority_Classification'] == 'Do Not Pursue'])
        
        # Highway access statistics
        excellent_highway = len(self.combined_df[self.combined_df['Highway_Access_Score'] >= 0.8])
        poor_highway = len(self.combined_df[self.combined_df['Highway_Access_Score'] <= 0.2])
        
        summary_data = {
            'Metric': [
                'ENHANCED ANALYSIS SUMMARY',
                '',
                'Total QCT/DDA Sites Analyzed',
                'High Priority Sites (Score ≥4.0)',
                'Recommended Sites (Score ≥3.0)',
                'Proceed with Caution (Score 2.0-3.0)',
                'Do Not Pursue (Score <2.0)',
                '',
                'INFRASTRUCTURE ANALYSIS',
                '',
                'Sites with Excellent Highway Access',
                'Sites with Poor Highway Access',
                'Sites Within City Limits',
                'Sites with LIHTC Market Validation',
                'Sites with 5+ Schools (Major Community)',
                '',
                'INVESTMENT RECOMMENDATIONS',
                '',
                'Immediate Investment Targets',
                'Secondary Investment Targets',
                'Total Viable Investment Universe',
                'Sites to Avoid (Fatal Flaws)',
                '',
                'ENHANCED SCORING IMPACT',
                '',
                'Average Enhanced Score',
                'Average Highway Component',
                'Average Utility Component',
                'Sites Improved by Highway Factor'
            ],
            'Count': [
                '',
                '',
                total_sites,
                high_priority_count,
                recommended_count,
                caution_count,
                fatal_count,
                '',
                '',
                '',
                excellent_highway,
                poor_highway,
                len(self.combined_df[self.combined_df['Within_City_Limits'] == True]),
                len(self.combined_df[self.combined_df['LIHTC_Within_2mi'] > 0]),
                len(self.combined_df[self.combined_df['Schools_Within_2_5mi'] >= 5]),
                '',
                '',
                '',
                high_priority_count,
                high_priority_count + recommended_count,
                high_priority_count + recommended_count,
                fatal_count,
                '',
                '',
                '',
                round(self.combined_df['Enhanced_Anchor_Score'].mean(), 3),
                round(self.combined_df['Highway_Component'].mean(), 3),
                round(self.combined_df['Utility_Component'].mean(), 3),
                len(self.combined_df[self.combined_df['Highway_Component'] >= 0.5])
            ],
            'Percentage': [
                '',
                '',
                '100%',
                f"{round(high_priority_count/total_sites*100, 1)}%",
                f"{round(recommended_count/total_sites*100, 1)}%",
                f"{round(caution_count/total_sites*100, 1)}%",
                f"{round(fatal_count/total_sites*100, 1)}%",
                '',
                '',
                '',
                f"{round(excellent_highway/total_sites*100, 1)}%",
                f"{round(poor_highway/total_sites*100, 1)}%",
                f"{round(len(self.combined_df[self.combined_df['Within_City_Limits'] == True])/total_sites*100, 1)}%",
                f"{round(len(self.combined_df[self.combined_df['LIHTC_Within_2mi'] > 0])/total_sites*100, 1)}%",
                f"{round(len(self.combined_df[self.combined_df['Schools_Within_2_5mi'] >= 5])/total_sites*100, 1)}%",
                '',
                '',
                '',
                f"{round(high_priority_count/total_sites*100, 1)}%",
                f"{round((high_priority_count + recommended_count)/total_sites*100, 1)}%",
                f"{round((high_priority_count + recommended_count)/total_sites*100, 1)}%",
                f"{round(fatal_count/total_sites*100, 1)}%",
                '',
                '',
                '',
                '(0-5 scale)',
                '(0-0.75 possible)',
                '(0-0.25 possible)',
                f"{round(len(self.combined_df[self.combined_df['Highway_Component'] >= 0.5])/total_sites*100, 1)}%"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Executive_Summary', index=False)
    
    def _create_enhanced_methodology_sheet(self, writer):
        """Create enhanced methodology documentation"""
        
        methodology_data = [
            ['ENHANCED 6-FACTOR ANCHOR SCORING METHODOLOGY', '', '', '', ''],
            ['', '', '', '', ''],
            ['SCORING OVERVIEW', '', '', '', ''],
            ['Purpose', 'Evaluate infrastructure viability for LIHTC development', '', '', ''],
            ['Scale', '0-5 points (5 = Excellent, 0 = Fatal)', '', '', ''],
            ['Enhancement', 'Added highway access and utility validation to original 4-factor system', '', '', ''],
            ['', '', '', '', ''],
            ['ENHANCED SCORING COMPONENTS', 'Weight', 'Methodology', 'Max Points', 'Rationale'],
            ['Schools Proximity (2.5 miles)', '30%', 'Count of schools within 2.5 miles, 2+ schools = max', '1.50', 'Essential for family housing, indicates established community'],
            ['City Incorporation', '15%', 'Binary: within city limits = full points', '0.75', 'Indicates infrastructure access and municipal services'],
            ['LIHTC Market Validation', '25%', 'Count of LIHTC projects within 2 miles, 2+ = max', '1.25', 'Proven market demand and operational feasibility'],
            ['Community Scale', '10%', 'School count as population proxy, 5+ schools = max', '0.50', 'Larger communities = better amenities and services'],
            ['Highway Access (NEW)', '15%', 'Distance to Interstate/US/State highways, tiered scoring', '0.75', 'Critical for resident commuting and construction logistics'],
            ['Utility Service (NEW)', '5%', 'Estimated service availability based on location/infrastructure', '0.25', 'Prevents utility extension cost surprises'],
            ['', '', '', '', ''],
            ['HIGHWAY ACCESS SCORING DETAIL', '', '', '', ''],
            ['Interstate within 2 miles', '1.0 (perfect)', 'Major regional connectivity', '', 'Fast access to employment centers'],
            ['Interstate within 5 miles', '0.8', 'Good regional connectivity', '', 'Reasonable commute to major metros'],
            ['US Highway within 2 miles', '0.8', 'Multi-city connectivity', '', 'Access to commercial corridors'],
            ['US Highway within 4 miles', '0.6-0.8', 'Linear scaling by distance', '', 'Moderate highway access'],
            ['State Highway within 3 miles', '0.4-0.6', 'Regional connectivity', '', 'Basic highway access'],
            ['Local roads only', '0.0', 'No major highway access', '', 'Isolation risk for residents and construction'],
            ['', '', '', '', ''],
            ['UTILITY SERVICE SCORING DETAIL', '', '', '', ''],
            ['Large incorporated city (5+ schools)', '1.0', 'Full municipal services expected', '', 'Comprehensive utility infrastructure'],
            ['Medium incorporated city (2-4 schools)', '0.8', 'Municipal services likely', '', 'Standard utility availability'],
            ['Small incorporated city (<2 schools)', '0.6', 'Basic municipal services', '', 'Utilities available but capacity uncertain'],
            ['Unincorporated, good highway access', '0.4', 'Private/district utilities possible', '', 'Development may attract utility extension'],
            ['Unincorporated, limited highway access', '0.2', 'Utility extension required', '', 'Significant utility infrastructure costs'],
            ['Unincorporated, poor highway access', '0.0', 'Isolated location', '', 'Major utility infrastructure investment required'],
            ['', '', '', '', ''],
            ['BUSINESS PRIORITY CLASSIFICATIONS', '', '', '', ''],
            ['High Priority (4.0-5.0)', '80%+ infrastructure score', 'HIGHLY RECOMMENDED for immediate investment', '', 'Excellent infrastructure, low development risk'],
            ['Recommended (3.0-3.9)', '60-79% infrastructure score', 'RECOMMENDED with standard due diligence', '', 'Adequate infrastructure, normal development risk'],
            ['Proceed with Caution (2.0-2.9)', '40-59% infrastructure score', 'Requires infrastructure risk mitigation', '', 'Limited infrastructure, elevated development risk'],
            ['Do Not Pursue (<2.0)', '<40% infrastructure score', 'AVOID - inadequate infrastructure', '', 'Fatal infrastructure flaws, high failure risk'],
            ['', '', '', '', ''],
            ['DATA SOURCES AND VALIDATION', '', '', '', ''],
            ['Texas Public Schools', 'Texas Education Agency', '9,739 schools statewide', '2024-2025', 'Complete coverage, annual updates'],
            ['Texas City Boundaries', 'US Census TIGER/Line', '1,863 incorporated places', '2024', 'Official municipal boundaries'],
            ['TDHCA LIHTC Projects', 'Texas Dept Housing & Community Affairs', '3,189 projects', 'May 2025', 'Complete historical project database'],
            ['TxDOT Highway Network', 'Texas Department of Transportation', '32,830 highway segments', 'July 2025', 'Complete Interstate, US, State highway coverage'],
            ['QCT/DDA Designations', 'HUD/Census Bureau', '195 sites verified', '2025', '100% QCT/DDA eligible confirmed'],
            ['', '', '', '', ''],
            ['ENHANCEMENT VALIDATION', '', '', '', ''],
            ['Original 4-Factor System', 'Schools + City + LIHTC + Scale', '141 High Priority sites', '', '72% of sites rated High Priority'],
            ['Enhanced 6-Factor System', '+ Highway Access + Utility Service', f'{len(self.combined_df[self.combined_df["Business_Priority_Classification"] == "High Priority"])} High Priority sites', '', f'{round(len(self.combined_df[self.combined_df["Business_Priority_Classification"] == "High Priority"])/len(self.combined_df)*100, 1)}% of sites rated High Priority'],
            ['Highway Impact', 'TxDOT data integration', f'{len(self.combined_df[self.combined_df["Highway_Access_Score"] >= 0.8])} sites excellent highway access', '', f'{round(len(self.combined_df[self.combined_df["Highway_Access_Score"] >= 0.8])/len(self.combined_df)*100, 1)}% have excellent highway connectivity'],
            ['Utility Validation', 'Infrastructure risk assessment', f'{len(self.combined_df[self.combined_df["Utility_Service_Score"] >= 0.6])} sites good utility access', '', f'{round(len(self.combined_df[self.combined_df["Utility_Service_Score"] >= 0.6])/len(self.combined_df)*100, 1)}% have reliable utility service expectations'],
            ['', '', '', '', ''],
        ]
        
        methodology_df = pd.DataFrame(methodology_data, columns=['Component', 'Details', 'Value', 'Source', 'Notes'])
        methodology_df.to_excel(writer, sheet_name='Enhanced_Methodology', index=False)
    
    def _create_component_analysis_sheet(self, writer):
        """Create component analysis breakdown"""
        
        # Component statistics
        component_stats = {
            'Component': [
                'Schools Component',
                'City Component', 
                'LIHTC Component',
                'Scale Component',
                'Highway Component (NEW)',
                'Utility Component (NEW)',
                '',
                'COMBINED ANALYSIS',
                'Total Enhanced Score'
            ],
            'Average_Value': [
                round(self.combined_df['Schools_Component'].mean(), 3),
                round(self.combined_df['City_Component'].mean(), 3),
                round(self.combined_df['LIHTC_Component'].mean(), 3),
                round(self.combined_df['Scale_Component'].mean(), 3),
                round(self.combined_df['Highway_Component'].mean(), 3),
                round(self.combined_df['Utility_Component'].mean(), 3),
                '',
                '',
                round(self.combined_df['Enhanced_Anchor_Score'].mean(), 3)
            ],
            'Max_Possible': [1.50, 0.75, 1.25, 0.50, 0.75, 0.25, '', '', 5.00],
            'Utilization_Rate': [
                f"{round(self.combined_df['Schools_Component'].mean()/1.50*100, 1)}%",
                f"{round(self.combined_df['City_Component'].mean()/0.75*100, 1)}%",
                f"{round(self.combined_df['LIHTC_Component'].mean()/1.25*100, 1)}%",
                f"{round(self.combined_df['Scale_Component'].mean()/0.50*100, 1)}%",
                f"{round(self.combined_df['Highway_Component'].mean()/0.75*100, 1)}%",
                f"{round(self.combined_df['Utility_Component'].mean()/0.25*100, 1)}%",
                '',
                '',
                f"{round(self.combined_df['Enhanced_Anchor_Score'].mean()/5.0*100, 1)}%"
            ],
            'Sites_At_Max': [
                len(self.combined_df[self.combined_df['Schools_Component'] >= 1.45]),
                len(self.combined_df[self.combined_df['City_Component'] >= 0.70]),
                len(self.combined_df[self.combined_df['LIHTC_Component'] >= 1.20]),
                len(self.combined_df[self.combined_df['Scale_Component'] >= 0.45]),
                len(self.combined_df[self.combined_df['Highway_Component'] >= 0.70]),
                len(self.combined_df[self.combined_df['Utility_Component'] >= 0.20]),
                '',
                '',
                len(self.combined_df[self.combined_df['Enhanced_Anchor_Score'] >= 4.5])
            ]
        }
        
        component_df = pd.DataFrame(component_stats)
        component_df.to_excel(writer, sheet_name='Component_Analysis', index=False)

def main():
    """Run enhanced anchor scoring with business priority sheets"""
    
    scorer = EnhancedAnchorScoringWithPriorities()
    
    # Load and merge data
    scorer.load_data()
    
    # Recalculate schools and LIHTC proximity (fixes missing data)
    scorer.recalculate_schools_and_lihtc()
    
    # Calculate utility scores
    scorer.calculate_utility_service_score()
    
    # Calculate enhanced anchor scores
    scorer.calculate_enhanced_anchor_scores()
    
    # Save results with business priority sheets
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"Enhanced_Anchor_Analysis_With_Priority_Sheets_{timestamp}.xlsx"
    scorer.save_results_with_priority_sheets(output_file)
    
    # Print summary
    total_sites = len(scorer.combined_df)
    high_priority = len(scorer.combined_df[scorer.combined_df['Business_Priority_Classification'] == 'High Priority'])
    recommended = len(scorer.combined_df[scorer.combined_df['Business_Priority_Classification'] == 'Recommended'])
    fatal = len(scorer.combined_df[scorer.combined_df['Business_Priority_Classification'] == 'Do Not Pursue'])
    
    print("\n🎯 ENHANCED ANCHOR ANALYSIS WITH PRIORITY SHEETS COMPLETE")
    print("=" * 70)
    print(f"Total Sites Analyzed: {total_sites}")
    print(f"\n📊 Business Priority Classifications:")
    print(f"  High Priority Sites:     {high_priority} ({high_priority/total_sites*100:.1f}%)")
    print(f"  Recommended Sites:       {recommended} ({recommended/total_sites*100:.1f}%)")
    print(f"  Total Viable Sites:      {high_priority + recommended} ({(high_priority + recommended)/total_sites*100:.1f}%)")
    print(f"  Fatal/Isolated Sites:    {fatal} ({fatal/total_sites*100:.1f}%)")
    print(f"\n🛣️  Highway Access Impact:")
    highway_excellent = len(scorer.combined_df[scorer.combined_df['Highway_Access_Score'] >= 0.8])
    print(f"  Excellent highway access: {highway_excellent} ({highway_excellent/total_sites*100:.1f}%)")
    print(f"  Average highway component: {scorer.combined_df['Highway_Component'].mean():.3f}")
    print(f"\n✅ Complete analysis saved to: {output_file}")
    print("\n📁 Excel Sheets Created:")
    print("  • All_Sites_Enhanced_Ranking - Complete dataset")
    print("  • High_Priority_Sites - Immediate investment targets")
    print("  • Recommended_Sites - All viable sites")
    print("  • Fatal_Isolated_Sites - Sites to avoid")
    print("  • Executive_Summary - Business overview")
    print("  • Enhanced_Methodology - Complete scoring documentation")
    print("  • Component_Analysis - Detailed score breakdown")

if __name__ == "__main__":
    main()