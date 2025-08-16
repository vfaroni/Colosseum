#!/usr/bin/env python3
"""
🏛️ CALIFORNIA RHNA COMPLIANCE INTELLIGENCE ENGINE
Roman Engineering Standards: Built to Last 2000+ Years
Built by Structured Consultants LLC for Colosseum Platform

Advanced intelligence algorithms for RHNA compliance calculation,
city classification, and strategic development opportunity identification
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging
import json
from pathlib import Path
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='🏛️ %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rhna_intelligence.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RHNAIntelligenceConfig:
    """Configuration for RHNA compliance intelligence"""
    database_config: Dict[str, Any]
    rhna_cycle_start: date = date(2021, 1, 1)
    rhna_cycle_end: date = date(2029, 12, 31)
    compliance_threshold: float = 0.20  # 20% progress minimum
    streamlining_threshold: float = 0.10  # Below 10% triggers streamlining
    
@dataclass
class JurisdictionIntelligence:
    """Comprehensive jurisdiction intelligence profile"""
    jurisdiction_id: int
    jurisdiction_name: str
    county_name: str
    
    # RHNA Progress
    rhna_allocation: Dict[str, int]
    current_progress: Dict[str, int]
    progress_percentages: Dict[str, float]
    overall_progress: float
    
    # Performance Metrics
    permitting_velocity: float  # permits per month
    approval_timeline: float    # average days
    completion_rate: float      # CO/BP ratio
    
    # Classification
    performance_category: str   # 'Excellent', 'Good', 'Behind', 'Critical'
    compliance_status: str      # 'Compliant', 'Non-Compliant', 'At Risk'
    risk_score: float          # 0-100 risk assessment
    
    # Opportunities
    streamlining_required: bool
    streamlining_percentage: int
    builders_remedy_active: bool
    pro_housing_eligible: bool
    
    # Strategic Intelligence
    development_opportunities: List[str]
    risk_factors: List[str]
    competitive_advantages: List[str]

class ColasseumRHNAIntelligence:
    """Advanced RHNA Compliance Intelligence Engine"""
    
    def __init__(self, config: RHNAIntelligenceConfig):
        """Initialize intelligence engine"""
        self.config = config
        self.engine = None
        self.connection = None
        
        # RHNA 6th Cycle Parameters (2021-2029)
        self.rhna_cycle_years = 8
        self.current_year = datetime.now().year
        self.cycle_progress = (self.current_year - 2021) / self.rhna_cycle_years
        
        # Income category definitions
        self.income_categories = {
            'very_low': 'Very Low Income (0-50% AMI)',
            'low': 'Low Income (50-80% AMI)', 
            'moderate': 'Moderate Income (80-120% AMI)',
            'above_moderate': 'Above Moderate Income (>120% AMI)'
        }
        
        # Performance thresholds
        self.performance_thresholds = {
            'excellent': 0.80,    # 80%+ progress
            'good': 0.50,         # 50-80% progress
            'behind': 0.20,       # 20-50% progress
            'critical': 0.20      # <20% progress
        }
        
        # Streamlining requirements (SB 35)
        self.sb35_thresholds = {
            'above_moderate_only': 0.25,  # 25% above moderate = 10% affordable streamlining
            'all_income_levels': 0.75     # 75% all levels = 50% affordable streamlining
        }
    
    def connect_database(self) -> bool:
        """Establish database connection"""
        try:
            db_config = self.config.database_config
            connection_string = (
                f"postgresql://{db_config['user']}:{db_config['password']}@"
                f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
            )
            
            self.engine = create_engine(connection_string)
            self.connection = self.engine.connect()
            
            logger.info("✅ Intelligence engine database connection established")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def get_jurisdiction_rhna_allocation(self, jurisdiction_id: int) -> Dict[str, int]:
        """Get RHNA allocation for jurisdiction"""
        try:
            query = text("""
                SELECT 
                    very_low_income_units,
                    low_income_units,
                    moderate_income_units,
                    above_moderate_units,
                    total_units
                FROM rhna_allocations 
                WHERE jurisdiction_id = :jurisdiction_id
            """)
            
            result = self.connection.execute(query, {'jurisdiction_id': jurisdiction_id}).fetchone()
            
            if result:
                return {
                    'very_low': result[0] or 0,
                    'low': result[1] or 0,
                    'moderate': result[2] or 0,
                    'above_moderate': result[3] or 0,
                    'total': result[4] or 0
                }
            else:
                # If no allocation found, estimate based on state averages
                logger.warning(f"⚠️ No RHNA allocation found for jurisdiction {jurisdiction_id}")
                return self._estimate_rhna_allocation(jurisdiction_id)
                
        except Exception as e:
            logger.error(f"❌ Failed to get RHNA allocation for jurisdiction {jurisdiction_id}: {e}")
            return {'very_low': 0, 'low': 0, 'moderate': 0, 'above_moderate': 0, 'total': 0}
    
    def calculate_jurisdiction_progress(self, jurisdiction_id: int) -> Dict[str, int]:
        """Calculate current RHNA progress from building permits"""
        try:
            # Use building permits (Table A2) as the official RHNA compliance metric
            query = text("""
                SELECT 
                    COALESCE(SUM(bp_vlow_income_dr + bp_vlow_income_ndr), 0) as very_low_progress,
                    COALESCE(SUM(bp_low_income_dr + bp_low_income_ndr), 0) as low_progress,
                    COALESCE(SUM(bp_mod_income_dr + bp_mod_income_ndr), 0) as moderate_progress,
                    COALESCE(SUM(bp_above_mod_income), 0) as above_moderate_progress,
                    COALESCE(SUM(bp_vlow_income_dr + bp_vlow_income_ndr + 
                                bp_low_income_dr + bp_low_income_ndr + 
                                bp_mod_income_dr + bp_mod_income_ndr + 
                                bp_above_mod_income), 0) as total_progress
                FROM building_permits 
                WHERE jurisdiction_id = :jurisdiction_id
                AND bp_issue_date BETWEEN :cycle_start AND :cycle_end
            """)
            
            result = self.connection.execute(query, {
                'jurisdiction_id': jurisdiction_id,
                'cycle_start': self.config.rhna_cycle_start,
                'cycle_end': self.config.rhna_cycle_end
            }).fetchone()
            
            if result:
                return {
                    'very_low': result[0],
                    'low': result[1],
                    'moderate': result[2],
                    'above_moderate': result[3],
                    'total': result[4]
                }
            else:
                return {'very_low': 0, 'low': 0, 'moderate': 0, 'above_moderate': 0, 'total': 0}
                
        except Exception as e:
            logger.error(f"❌ Failed to calculate progress for jurisdiction {jurisdiction_id}: {e}")
            return {'very_low': 0, 'low': 0, 'moderate': 0, 'above_moderate': 0, 'total': 0}
    
    def calculate_progress_percentages(self, allocation: Dict[str, int], progress: Dict[str, int]) -> Dict[str, float]:
        """Calculate progress percentages by income category"""
        percentages = {}
        
        for category in ['very_low', 'low', 'moderate', 'above_moderate', 'total']:
            if allocation[category] > 0:
                percentages[category] = (progress[category] / allocation[category]) * 100
            else:
                percentages[category] = 0.0
        
        return percentages
    
    def assess_sb35_streamlining_requirements(self, progress_percentages: Dict[str, float]) -> Tuple[bool, int]:
        """Assess SB 35 streamlining requirements"""
        above_moderate_progress = progress_percentages.get('above_moderate', 0)
        overall_progress = progress_percentages.get('total', 0)
        
        # SB 35 Streamlining Rules:
        # 1. If above moderate < 25% AND overall < 75% = 10% affordable streamlining
        # 2. If above moderate < 25% AND overall >= 75% = 50% affordable streamlining
        
        if above_moderate_progress < 25:
            if overall_progress >= 75:
                return True, 50  # 50% affordable streamlining required
            else:
                return True, 10  # 10% affordable streamlining required
        
        return False, 0  # No streamlining required
    
    def calculate_permitting_velocity(self, jurisdiction_id: int) -> float:
        """Calculate permitting velocity (permits per month)"""
        try:
            query = text("""
                SELECT 
                    COUNT(*) as total_permits,
                    EXTRACT(YEAR FROM MAX(bp_issue_date)) - EXTRACT(YEAR FROM MIN(bp_issue_date)) + 1 as years_span
                FROM building_permits 
                WHERE jurisdiction_id = :jurisdiction_id
                AND bp_issue_date IS NOT NULL
                AND bp_issue_date BETWEEN :cycle_start AND :cycle_end
            """)
            
            result = self.connection.execute(query, {
                'jurisdiction_id': jurisdiction_id,
                'cycle_start': self.config.rhna_cycle_start,
                'cycle_end': self.config.rhna_cycle_end
            }).fetchone()
            
            if result and result[0] > 0 and result[1] > 0:
                permits_per_year = result[0] / result[1]
                return permits_per_year / 12  # Convert to monthly
            
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate permitting velocity: {e}")
            return 0.0
    
    def calculate_completion_rate(self, jurisdiction_id: int) -> float:
        """Calculate completion rate (CO/BP ratio)"""
        try:
            query = text("""
                SELECT 
                    COALESCE(SUM(bp_vlow_income_dr + bp_vlow_income_ndr + 
                                bp_low_income_dr + bp_low_income_ndr + 
                                bp_mod_income_dr + bp_mod_income_ndr + 
                                bp_above_mod_income), 0) as total_permitted,
                    COALESCE(SUM(co_vlow_income_dr + co_vlow_income_ndr + 
                                co_low_income_dr + co_low_income_ndr + 
                                co_mod_income_dr + co_mod_income_ndr + 
                                co_above_mod_income), 0) as total_completed
                FROM building_permits 
                WHERE jurisdiction_id = :jurisdiction_id
                AND bp_issue_date BETWEEN :cycle_start AND :cycle_end
            """)
            
            result = self.connection.execute(query, {
                'jurisdiction_id': jurisdiction_id,
                'cycle_start': self.config.rhna_cycle_start,
                'cycle_end': self.config.rhna_cycle_end
            }).fetchone()
            
            if result and result[0] > 0:
                return (result[1] / result[0]) * 100
            
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate completion rate: {e}")
            return 0.0
    
    def classify_jurisdiction_performance(self, overall_progress: float) -> str:
        """Classify jurisdiction performance based on RHNA progress"""
        if overall_progress >= self.performance_thresholds['excellent']:
            return 'Excellent'
        elif overall_progress >= self.performance_thresholds['good']:
            return 'Good'
        elif overall_progress >= self.performance_thresholds['behind']:
            return 'Behind Schedule'
        else:
            return 'Critical'
    
    def assess_compliance_status(self, progress_percentages: Dict[str, float], expected_progress: float) -> str:
        """Assess overall compliance status"""
        overall_progress = progress_percentages.get('total', 0)
        
        if overall_progress >= expected_progress:
            return 'Compliant'
        elif overall_progress >= (expected_progress * 0.75):
            return 'At Risk'
        else:
            return 'Non-Compliant'
    
    def calculate_risk_score(self, progress_percentages: Dict[str, float], 
                           permitting_velocity: float, completion_rate: float) -> float:
        """Calculate comprehensive risk score (0-100)"""
        # Base risk from RHNA progress (40% weight)
        overall_progress = progress_percentages.get('total', 0)
        expected_progress = self.cycle_progress * 100
        progress_risk = max(0, (expected_progress - overall_progress) / expected_progress * 40)
        
        # Permitting velocity risk (30% weight)
        # Low velocity indicates future problems
        avg_velocity = 5.0  # Assume 5 permits/month as average
        velocity_risk = max(0, (avg_velocity - permitting_velocity) / avg_velocity * 30)
        
        # Completion rate risk (30% weight)
        # Low completion rate indicates execution problems
        completion_risk = max(0, (75 - completion_rate) / 75 * 30)  # 75% as target completion rate
        
        total_risk = min(100, progress_risk + velocity_risk + completion_risk)
        return round(total_risk, 2)
    
    def identify_development_opportunities(self, intelligence: JurisdictionIntelligence) -> List[str]:
        """Identify strategic development opportunities"""
        opportunities = []
        
        # Streamlining opportunities
        if intelligence.streamlining_required:
            if intelligence.streamlining_percentage == 50:
                opportunities.append("50% Affordable SB 35 Streamlining - Ministerial Approval Required")
            else:
                opportunities.append("10% Affordable SB 35 Streamlining - Ministerial Approval Available")
        
        # Builder's remedy
        if intelligence.builders_remedy_active:
            opportunities.append("Builder's Remedy Active - 20% Affordable on Any Residential Site")
        
        # Pro-housing opportunities
        if intelligence.pro_housing_eligible:
            opportunities.append("Pro-Housing Designation Eligible - State Funding Priority")
        
        # Low competition markets
        if intelligence.permitting_velocity < 2.0:  # Less than 2 permits/month
            opportunities.append("Low Competition Market - Limited Development Activity")
        
        # High completion rate jurisdictions
        if intelligence.completion_rate > 80:
            opportunities.append("High Execution Capability - Strong Project Completion Record")
        
        return opportunities
    
    def identify_risk_factors(self, intelligence: JurisdictionIntelligence) -> List[str]:
        """Identify strategic risk factors"""
        risks = []
        
        # Compliance risks
        if intelligence.compliance_status == 'Non-Compliant':
            risks.append("Non-Compliant Status - Potential Enforcement Actions")
        
        # Progress risks
        if intelligence.overall_progress < 20:
            risks.append("Critically Behind Schedule - Less than 20% RHNA Progress")
        
        # Execution risks
        if intelligence.completion_rate < 50:
            risks.append("Poor Execution Track Record - Low Project Completion Rate")
        
        # Market risks
        if intelligence.permitting_velocity > 10:  # Very high velocity
            risks.append("High Competition Market - Saturated Development Activity")
        
        return risks
    
    def analyze_jurisdiction_intelligence(self, jurisdiction_id: int) -> Optional[JurisdictionIntelligence]:
        """Perform comprehensive jurisdiction intelligence analysis"""
        try:
            # Get jurisdiction basic info
            query = text("""
                SELECT jurisdiction_name, county_name 
                FROM jurisdictions 
                WHERE jurisdiction_id = :jurisdiction_id
            """)
            
            result = self.connection.execute(query, {'jurisdiction_id': jurisdiction_id}).fetchone()
            if not result:
                logger.error(f"❌ Jurisdiction {jurisdiction_id} not found")
                return None
            
            jurisdiction_name, county_name = result
            
            # Get RHNA data
            allocation = self.get_jurisdiction_rhna_allocation(jurisdiction_id)
            progress = self.calculate_jurisdiction_progress(jurisdiction_id)
            progress_percentages = self.calculate_progress_percentages(allocation, progress)
            
            # Calculate performance metrics
            permitting_velocity = self.calculate_permitting_velocity(jurisdiction_id)
            completion_rate = self.calculate_completion_rate(jurisdiction_id)
            overall_progress = progress_percentages.get('total', 0)
            
            # Assess classifications
            performance_category = self.classify_jurisdiction_performance(overall_progress)
            expected_progress = self.cycle_progress * 100
            compliance_status = self.assess_compliance_status(progress_percentages, expected_progress)
            risk_score = self.calculate_risk_score(progress_percentages, permitting_velocity, completion_rate)
            
            # Assess streamlining requirements
            streamlining_required, streamlining_percentage = self.assess_sb35_streamlining_requirements(progress_percentages)
            builders_remedy_active = compliance_status == 'Non-Compliant'
            pro_housing_eligible = overall_progress >= 50 and completion_rate >= 70
            
            # Create intelligence profile
            intelligence = JurisdictionIntelligence(
                jurisdiction_id=jurisdiction_id,
                jurisdiction_name=jurisdiction_name,
                county_name=county_name,
                rhna_allocation=allocation,
                current_progress=progress,
                progress_percentages=progress_percentages,
                overall_progress=overall_progress,
                permitting_velocity=permitting_velocity,
                approval_timeline=0.0,  # TODO: Calculate from application data
                completion_rate=completion_rate,
                performance_category=performance_category,
                compliance_status=compliance_status,
                risk_score=risk_score,
                streamlining_required=streamlining_required,
                streamlining_percentage=streamlining_percentage,
                builders_remedy_active=builders_remedy_active,
                pro_housing_eligible=pro_housing_eligible,
                development_opportunities=[],
                risk_factors=[],
                competitive_advantages=[]
            )
            
            # Add strategic intelligence
            intelligence.development_opportunities = self.identify_development_opportunities(intelligence)
            intelligence.risk_factors = self.identify_risk_factors(intelligence)
            
            return intelligence
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze jurisdiction {jurisdiction_id}: {e}")
            return None
    
    def update_compliance_status_table(self, intelligence: JurisdictionIntelligence) -> bool:
        """Update compliance_status table with latest intelligence"""
        try:
            # Check if record exists
            check_query = text("""
                SELECT status_id FROM compliance_status 
                WHERE jurisdiction_id = :jurisdiction_id
            """)
            
            existing = self.connection.execute(check_query, {
                'jurisdiction_id': intelligence.jurisdiction_id
            }).fetchone()
            
            if existing:
                # Update existing record
                update_query = text("""
                    UPDATE compliance_status SET
                        progress_very_low = :progress_very_low,
                        progress_low = :progress_low,
                        progress_moderate = :progress_moderate,
                        progress_above_moderate = :progress_above_moderate,
                        overall_progress = :overall_progress,
                        sb35_10_percent_required = :sb35_10_percent,
                        sb35_50_percent_required = :sb35_50_percent,
                        ministerial_approval_required = :ministerial_required,
                        builders_remedy_exposed = :builders_remedy_exposed,
                        status_effective_date = :effective_date,
                        updated_at = :updated_at
                    WHERE jurisdiction_id = :jurisdiction_id
                """)
                
                self.connection.execute(update_query, {
                    'jurisdiction_id': intelligence.jurisdiction_id,
                    'progress_very_low': intelligence.progress_percentages['very_low'],
                    'progress_low': intelligence.progress_percentages['low'],
                    'progress_moderate': intelligence.progress_percentages['moderate'],
                    'progress_above_moderate': intelligence.progress_percentages['above_moderate'],
                    'overall_progress': intelligence.overall_progress,
                    'sb35_10_percent': intelligence.streamlining_required and intelligence.streamlining_percentage == 10,
                    'sb35_50_percent': intelligence.streamlining_required and intelligence.streamlining_percentage == 50,
                    'ministerial_required': intelligence.streamlining_required,
                    'builders_remedy_exposed': intelligence.builders_remedy_active,
                    'effective_date': date.today(),
                    'updated_at': datetime.now()
                })
            else:
                # Insert new record
                insert_query = text("""
                    INSERT INTO compliance_status (
                        jurisdiction_id, progress_very_low, progress_low, 
                        progress_moderate, progress_above_moderate, overall_progress,
                        sb35_10_percent_required, sb35_50_percent_required,
                        ministerial_approval_required, builders_remedy_exposed,
                        status_effective_date
                    ) VALUES (
                        :jurisdiction_id, :progress_very_low, :progress_low,
                        :progress_moderate, :progress_above_moderate, :overall_progress,
                        :sb35_10_percent, :sb35_50_percent, :ministerial_required,
                        :builders_remedy_exposed, :effective_date
                    )
                """)
                
                self.connection.execute(insert_query, {
                    'jurisdiction_id': intelligence.jurisdiction_id,
                    'progress_very_low': intelligence.progress_percentages['very_low'],
                    'progress_low': intelligence.progress_percentages['low'],
                    'progress_moderate': intelligence.progress_percentages['moderate'],
                    'progress_above_moderate': intelligence.progress_percentages['above_moderate'],
                    'overall_progress': intelligence.overall_progress,
                    'sb35_10_percent': intelligence.streamlining_required and intelligence.streamlining_percentage == 10,
                    'sb35_50_percent': intelligence.streamlining_required and intelligence.streamlining_percentage == 50,
                    'ministerial_required': intelligence.streamlining_required,
                    'builders_remedy_exposed': intelligence.builders_remedy_active,
                    'effective_date': date.today()
                })
            
            self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update compliance status: {e}")
            self.connection.rollback()
            return False
    
    def analyze_all_jurisdictions(self) -> List[JurisdictionIntelligence]:
        """Analyze all jurisdictions and generate comprehensive intelligence"""
        logger.info("🔄 Starting comprehensive jurisdiction intelligence analysis...")
        
        if not self.connect_database():
            return []
        
        try:
            # Get all jurisdiction IDs
            query = text("SELECT jurisdiction_id FROM jurisdictions ORDER BY jurisdiction_name")
            jurisdiction_ids = [row[0] for row in self.connection.execute(query).fetchall()]
            
            logger.info(f"📊 Analyzing {len(jurisdiction_ids)} jurisdictions...")
            
            intelligence_results = []
            processed_count = 0
            
            for jurisdiction_id in jurisdiction_ids:
                intelligence = self.analyze_jurisdiction_intelligence(jurisdiction_id)
                if intelligence:
                    intelligence_results.append(intelligence)
                    
                    # Update database
                    self.update_compliance_status_table(intelligence)
                    
                    processed_count += 1
                    if processed_count % 50 == 0:
                        logger.info(f"✅ Processed {processed_count}/{len(jurisdiction_ids)} jurisdictions")
            
            logger.info(f"✅ Completed analysis of {processed_count} jurisdictions")
            
            # Generate summary statistics
            self._generate_intelligence_summary(intelligence_results)
            
            return intelligence_results
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze jurisdictions: {e}")
            return []
        
        finally:
            if self.connection:
                self.connection.close()
    
    def _generate_intelligence_summary(self, intelligence_results: List[JurisdictionIntelligence]):
        """Generate intelligence analysis summary"""
        if not intelligence_results:
            return
        
        # Performance category distribution
        performance_dist = {}
        compliance_dist = {}
        streamlining_count = 0
        builders_remedy_count = 0
        
        for intel in intelligence_results:
            # Performance categories
            category = intel.performance_category
            performance_dist[category] = performance_dist.get(category, 0) + 1
            
            # Compliance status
            status = intel.compliance_status
            compliance_dist[status] = compliance_dist.get(status, 0) + 1
            
            # Opportunities
            if intel.streamlining_required:
                streamlining_count += 1
            if intel.builders_remedy_active:
                builders_remedy_count += 1
        
        logger.info("=" * 80)
        logger.info("📊 CALIFORNIA HOUSING ELEMENT INTELLIGENCE SUMMARY")
        logger.info("=" * 80)
        logger.info("🎯 PERFORMANCE DISTRIBUTION:")
        for category, count in performance_dist.items():
            percentage = (count / len(intelligence_results)) * 100
            logger.info(f"   {category}: {count} jurisdictions ({percentage:.1f}%)")
        
        logger.info("\n⚖️ COMPLIANCE STATUS:")
        for status, count in compliance_dist.items():
            percentage = (count / len(intelligence_results)) * 100
            logger.info(f"   {status}: {count} jurisdictions ({percentage:.1f}%)")
        
        logger.info(f"\n🏗️ DEVELOPMENT OPPORTUNITIES:")
        logger.info(f"   SB 35 Streamlining Required: {streamlining_count} jurisdictions")
        logger.info(f"   Builder's Remedy Active: {builders_remedy_count} jurisdictions")
        
        # Top performers and underperformers
        sorted_intel = sorted(intelligence_results, key=lambda x: x.overall_progress, reverse=True)
        
        logger.info(f"\n🏆 TOP 10 PERFORMING JURISDICTIONS:")
        for intel in sorted_intel[:10]:
            logger.info(f"   {intel.jurisdiction_name} ({intel.county_name}): {intel.overall_progress:.1f}% progress")
        
        logger.info(f"\n⚠️ BOTTOM 10 PERFORMING JURISDICTIONS:")
        for intel in sorted_intel[-10:]:
            logger.info(f"   {intel.jurisdiction_name} ({intel.county_name}): {intel.overall_progress:.1f}% progress")
        
        logger.info("=" * 80)
    
    def _estimate_rhna_allocation(self, jurisdiction_id: int) -> Dict[str, int]:
        """Estimate RHNA allocation based on historical data"""
        # This is a fallback method - in production, all jurisdictions should have RHNA data
        logger.warning(f"⚠️ Estimating RHNA allocation for jurisdiction {jurisdiction_id}")
        
        # Use state averages as estimate
        return {
            'very_low': 500,
            'low': 300,
            'moderate': 400,
            'above_moderate': 800,
            'total': 2000
        }

def main():
    """Main intelligence analysis function"""
    # Configuration
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'user': os.getenv('CA_HCD_USER', 'ca_hcd_user'),
        'password': os.getenv('CA_HCD_PASSWORD', 'colosseum_hcd_2025'),
        'database': 'ca_hcd_housing_element'
    }
    
    config = RHNAIntelligenceConfig(database_config=db_config)
    
    # Initialize intelligence engine
    intelligence_engine = ColasseumRHNAIntelligence(config)
    
    logger.info("🏛️ STARTING CALIFORNIA RHNA COMPLIANCE INTELLIGENCE ANALYSIS")
    logger.info("=" * 80)
    logger.info("📊 COLOSSEUM PLATFORM - Roman Engineering Standards")
    logger.info("🏗️ Built by Structured Consultants LLC")
    logger.info("=" * 80)
    
    # Run comprehensive analysis
    results = intelligence_engine.analyze_all_jurisdictions()
    
    if results:
        logger.info("🎉 RHNA INTELLIGENCE ANALYSIS COMPLETE!")
        logger.info("🏛️ Ready for Roman Empire dashboard deployment")
        return 0
    else:
        logger.error("❌ RHNA intelligence analysis failed")
        return 1

if __name__ == "__main__":
    exit(main())