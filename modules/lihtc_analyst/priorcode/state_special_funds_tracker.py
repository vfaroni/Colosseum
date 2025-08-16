#!/usr/bin/env python3
"""
State Special Funds Tracker
Tracks HOME, HTF, CDBG-DR, and state-specific soft loans/grants used with LIHTC
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
import pandas as pd
from enum import Enum

class FundSource(Enum):
    """Federal and state funding sources"""
    # Federal sources
    HOME = "HOME Investment Partnerships"
    HTF = "National Housing Trust Fund"
    CDBG = "Community Development Block Grant"
    CDBG_DR = "CDBG Disaster Recovery"
    USDA_RD = "USDA Rural Development"
    HOPWA = "Housing Opportunities for Persons With AIDS"
    ESG = "Emergency Solutions Grant"
    NSP = "Neighborhood Stabilization Program"
    TCAP = "Tax Credit Assistance Program"
    
    # State-specific (examples)
    STATE_HTF = "State Housing Trust Fund"
    STATE_BOND = "State Housing Bond"
    STATE_GRANT = "State Housing Grant"
    STATE_LOAN = "State Soft Loan"
    LOCAL = "Local Government Funds"

@dataclass
class SpecialFundProgram:
    """Details about a special funding program"""
    state_code: str
    fund_source: FundSource
    program_name: str
    administering_agency: str
    
    # Funding details
    total_allocation_2024: Optional[float] = None
    total_allocation_2025: Optional[float] = None
    allocation_frequency: str = "annual"  # "annual", "biannual", "rolling"
    
    # Eligibility with LIHTC
    combines_with_9pct: bool = True
    combines_with_4pct: bool = True
    requires_lihtc: bool = False  # Some funds require LIHTC
    
    # Limits and requirements
    per_unit_limit: Optional[float] = None
    per_project_limit: Optional[float] = None
    max_percentage_tdc: Optional[float] = None  # Max % of total development cost
    min_affordability_period: int = 0  # Years
    income_targeting: str = ""  # e.g., "30% AMI", "60% AMI"
    
    # Geographic restrictions
    statewide: bool = True
    eligible_counties: List[str] = field(default_factory=list)
    rural_only: bool = False
    urban_only: bool = False
    disaster_areas_only: bool = False
    
    # Application process
    application_url: str = ""
    guidelines_url: str = ""
    application_cycle: str = ""  # e.g., "Concurrent with LIHTC", "Separate NOFA"
    typical_deadline_month: Optional[int] = None
    
    # Scoring/Priority
    scoring_criteria: List[str] = field(default_factory=list)
    set_asides: Dict[str, float] = field(default_factory=dict)  # e.g., {"rural": 0.25}
    
    # Requirements
    davis_bacon: bool = False
    section_3: bool = False
    environmental_review: str = "standard"  # "standard", "enhanced", "NEPA"
    fair_housing_marketing: bool = True
    
    # Historical data
    projects_funded_2023: int = 0
    projects_funded_2024: int = 0
    typical_award_amount: Optional[float] = None
    
    # Status
    active: bool = True
    last_updated: datetime = field(default_factory=datetime.now)
    notes: str = ""

@dataclass
class FundingAward:
    """Track actual funding awards to projects"""
    state_code: str
    project_name: str
    developer: str
    fund_source: FundSource
    program_name: str
    
    # Award details
    award_date: datetime
    award_amount: float
    total_units: int
    per_unit_amount: float
    
    # LIHTC connection
    has_lihtc: bool = True
    lihtc_type: str = ""  # "9%", "4%", "both"
    lihtc_amount: Optional[float] = None
    
    # Location
    city: str = ""
    county: str = ""
    census_tract: str = ""
    rural: bool = False
    
    # Project type
    new_construction: bool = True
    family: bool = True
    senior: bool = False
    special_needs: bool = False
    
    # Compliance
    affordability_period: int = 0
    target_income: str = ""

class StateSpecialFundsTracker:
    """Master system for tracking special funds used with LIHTC"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "QAP" / "_special_funds"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data storage
        self.programs: Dict[str, SpecialFundProgram] = {}
        self.awards: List[FundingAward] = []
        
        # Load existing data
        self.load_data()
        
        # Initialize known programs
        if not self.programs:
            self.initialize_known_programs()
            
    def initialize_known_programs(self):
        """Initialize database with known state programs"""
        
        # California programs
        self.add_program(SpecialFundProgram(
            state_code="CA",
            fund_source=FundSource.STATE_LOAN,
            program_name="Multifamily Housing Program (MHP)",
            administering_agency="California HCD",
            total_allocation_2024=325_000_000,
            combines_with_9pct=True,
            combines_with_4pct=True,
            per_unit_limit=150_000,
            per_project_limit=20_000_000,
            min_affordability_period=55,
            application_url="https://www.hcd.ca.gov/grants-funding/active-funding/mhp.shtml",
            scoring_criteria=["Readiness", "Cost efficiency", "Proximity to transit"],
            davis_bacon=True
        ))
        
        self.add_program(SpecialFundProgram(
            state_code="CA",
            fund_source=FundSource.STATE_GRANT,
            program_name="Affordable Housing and Sustainable Communities (AHSC)",
            administering_agency="California SGC",
            total_allocation_2024=550_000_000,
            combines_with_9pct=True,
            combines_with_4pct=True,
            per_project_limit=30_000_000,
            min_affordability_period=55,
            application_url="https://sgc.ca.gov/programs/ahsc/",
            scoring_criteria=["GHG reduction", "Transit connectivity", "Active transportation"]
        ))
        
        self.add_program(SpecialFundProgram(
            state_code="CA",
            fund_source=FundSource.STATE_LOAN,
            program_name="Veterans Housing and Homelessness Prevention (VHHP)",
            administering_agency="California HCD/CalVet",
            combines_with_9pct=True,
            combines_with_4pct=True,
            per_unit_limit=125_000,
            min_affordability_period=55,
            income_targeting="Veteran households",
            set_asides={"veterans": 1.0}
        ))
        
        # Texas programs
        self.add_program(SpecialFundProgram(
            state_code="TX",
            fund_source=FundSource.HOME,
            program_name="HOME Multifamily Development",
            administering_agency="TDHCA",
            total_allocation_2024=30_000_000,
            combines_with_9pct=True,
            combines_with_4pct=True,
            per_unit_limit=60_000,
            min_affordability_period=30,
            davis_bacon=True,
            application_url="https://www.tdhca.state.tx.us/home-division/index.htm"
        ))
        
        self.add_program(SpecialFundProgram(
            state_code="TX",
            fund_source=FundSource.HTF,
            program_name="National Housing Trust Fund",
            administering_agency="TDHCA",
            total_allocation_2024=25_000_000,
            combines_with_9pct=True,
            combines_with_4pct=True,
            income_targeting="30% AMI",
            min_affordability_period=30,
            davis_bacon=True
        ))
        
        # New Mexico programs
        self.add_program(SpecialFundProgram(
            state_code="NM",
            fund_source=FundSource.STATE_HTF,
            program_name="New Mexico Housing Trust Fund",
            administering_agency="NM MFA",
            total_allocation_2024=10_000_000,
            combines_with_9pct=True,
            combines_with_4pct=True,
            per_project_limit=2_000_000,
            application_url="https://housingnm.org/developers/new-mexico-housing-trust-fund"
        ))
        
        # Colorado programs
        self.add_program(SpecialFundProgram(
            state_code="CO",
            fund_source=FundSource.CDBG_DR,
            program_name="CDBG-DR Marshall Fire Recovery",
            administering_agency="Colorado DOLA",
            total_allocation_2024=150_000_000,
            combines_with_9pct=True,
            combines_with_4pct=True,
            disaster_areas_only=True,
            eligible_counties=["Boulder", "Jefferson"],
            environmental_review="NEPA"
        ))
        
        self.add_program(SpecialFundProgram(
            state_code="CO",
            fund_source=FundSource.STATE_GRANT,
            program_name="Proposition 123 - Affordable Housing Fund",
            administering_agency="Colorado DOLA",
            total_allocation_2024=300_000_000,
            combines_with_9pct=True,
            combines_with_4pct=True,
            application_url="https://cdola.colorado.gov/proposition-123"
        ))
        
        # New York programs
        self.add_program(SpecialFundProgram(
            state_code="NY",
            fund_source=FundSource.STATE_LOAN,
            program_name="Low-Income Housing Trust Fund Program",
            administering_agency="NY HCR",
            total_allocation_2024=40_000_000,
            combines_with_9pct=True,
            combines_with_4pct=False,  # Has own 4% program
            per_unit_limit=125_000,
            min_affordability_period=30
        ))
        
        # Florida programs
        self.add_program(SpecialFundProgram(
            state_code="FL",
            fund_source=FundSource.STATE_LOAN,
            program_name="State Apartment Incentive Loan (SAIL)",
            administering_agency="Florida Housing",
            total_allocation_2024=120_000_000,
            combines_with_9pct=True,
            combines_with_4pct=True,
            per_unit_limit=95_000,
            application_url="https://www.floridahousing.org/programs/developers-multifamily-programs/sail"
        ))
        
    def add_program(self, program: SpecialFundProgram) -> str:
        """Add or update a special fund program"""
        key = f"{program.state_code}_{program.fund_source.name}_{program.program_name.replace(' ', '_')}"
        self.programs[key] = program
        self.save_data()
        return key
        
    def add_award(self, award: FundingAward):
        """Add a funding award record"""
        self.awards.append(award)
        self.save_data()
        
    def get_state_programs(self, state_code: str, active_only: bool = True) -> List[SpecialFundProgram]:
        """Get all programs for a state"""
        programs = []
        for program in self.programs.values():
            if program.state_code == state_code:
                if not active_only or program.active:
                    programs.append(program)
        return programs
        
    def get_lihtc_compatible_funds(self, state_code: str, lihtc_type: str = "9%") -> List[SpecialFundProgram]:
        """Get funds that can be combined with LIHTC"""
        programs = []
        for program in self.programs.values():
            if program.state_code == state_code and program.active:
                if lihtc_type == "9%" and program.combines_with_9pct:
                    programs.append(program)
                elif lihtc_type == "4%" and program.combines_with_4pct:
                    programs.append(program)
        return programs
        
    def generate_state_funding_matrix(self, state_code: str) -> pd.DataFrame:
        """Generate funding source compatibility matrix"""
        programs = self.get_state_programs(state_code)
        
        if not programs:
            return pd.DataFrame()
            
        data = []
        for program in programs:
            data.append({
                'Program': program.program_name,
                'Source': program.fund_source.value,
                'Agency': program.administering_agency,
                '2024 Allocation': f"${program.total_allocation_2024:,.0f}" if program.total_allocation_2024 else "N/A",
                '2025 Allocation': f"${program.total_allocation_2025:,.0f}" if program.total_allocation_2025 else "N/A",
                'Per Unit Limit': f"${program.per_unit_limit:,.0f}" if program.per_unit_limit else "No limit",
                'Per Project Limit': f"${program.per_project_limit:,.0f}" if program.per_project_limit else "No limit",
                'Works with 9%': '✓' if program.combines_with_9pct else '✗',
                'Works with 4%': '✓' if program.combines_with_4pct else '✗',
                'Davis-Bacon': '✓' if program.davis_bacon else '✗',
                'Min Affordability': f"{program.min_affordability_period} years" if program.min_affordability_period else "Varies"
            })
            
        df = pd.DataFrame(data)
        return df
        
    def analyze_funding_combinations(self, state_code: str, project_size: int = 100,
                                   lihtc_type: str = "9%") -> pd.DataFrame:
        """Analyze optimal funding combinations for a project"""
        programs = self.get_lihtc_compatible_funds(state_code, lihtc_type)
        
        combinations = []
        
        # Single source combinations
        for program in programs:
            max_funding = min(
                program.per_unit_limit * project_size if program.per_unit_limit else float('inf'),
                program.per_project_limit if program.per_project_limit else float('inf')
            )
            
            if max_funding < float('inf'):
                combinations.append({
                    'Combination': program.program_name,
                    'Sources': 1,
                    'Max Funding': max_funding,
                    'Per Unit': max_funding / project_size,
                    'Requirements': self._get_requirements_summary(program)
                })
                
        # Two source combinations (simplified)
        for i, prog1 in enumerate(programs):
            for prog2 in programs[i+1:]:
                # Check if sources can be combined (simplified logic)
                if prog1.fund_source != prog2.fund_source:
                    max1 = min(
                        prog1.per_unit_limit * project_size if prog1.per_unit_limit else float('inf'),
                        prog1.per_project_limit if prog1.per_project_limit else float('inf')
                    )
                    max2 = min(
                        prog2.per_unit_limit * project_size if prog2.per_unit_limit else float('inf'),
                        prog2.per_project_limit if prog2.per_project_limit else float('inf')
                    )
                    
                    if max1 < float('inf') and max2 < float('inf'):
                        combinations.append({
                            'Combination': f"{prog1.program_name} + {prog2.program_name}",
                            'Sources': 2,
                            'Max Funding': max1 + max2,
                            'Per Unit': (max1 + max2) / project_size,
                            'Requirements': self._combine_requirements(prog1, prog2)
                        })
                        
        df = pd.DataFrame(combinations)
        if not df.empty:
            df = df.sort_values('Max Funding', ascending=False)
            
        return df
        
    def _get_requirements_summary(self, program: SpecialFundProgram) -> str:
        """Summarize key requirements for a program"""
        reqs = []
        if program.davis_bacon:
            reqs.append("Davis-Bacon")
        if program.section_3:
            reqs.append("Section 3")
        if program.environmental_review != "standard":
            reqs.append(f"{program.environmental_review} review")
        if program.income_targeting:
            reqs.append(program.income_targeting)
        if program.rural_only:
            reqs.append("Rural only")
        elif program.urban_only:
            reqs.append("Urban only")
            
        return ", ".join(reqs) if reqs else "Standard"
        
    def _combine_requirements(self, prog1: SpecialFundProgram, prog2: SpecialFundProgram) -> str:
        """Combine requirements from multiple programs"""
        reqs = set()
        
        for prog in [prog1, prog2]:
            if prog.davis_bacon:
                reqs.add("Davis-Bacon")
            if prog.section_3:
                reqs.add("Section 3")
            if prog.environmental_review != "standard":
                reqs.add(f"{prog.environmental_review} review")
                
        return ", ".join(sorted(reqs)) if reqs else "Standard"
        
    def generate_awards_analysis(self, state_code: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """Analyze historical awards data"""
        awards_to_analyze = self.awards
        if state_code:
            awards_to_analyze = [a for a in self.awards if a.state_code == state_code]
            
        if not awards_to_analyze:
            return {}
            
        reports = {}
        
        # Awards by program
        program_data = {}
        for award in awards_to_analyze:
            key = f"{award.state_code} - {award.program_name}"
            if key not in program_data:
                program_data[key] = {
                    'Count': 0,
                    'Total Amount': 0,
                    'Total Units': 0,
                    'Avg Per Unit': []
                }
            program_data[key]['Count'] += 1
            program_data[key]['Total Amount'] += award.award_amount
            program_data[key]['Total Units'] += award.total_units
            program_data[key]['Avg Per Unit'].append(award.per_unit_amount)
            
        program_summary = []
        for prog, data in program_data.items():
            program_summary.append({
                'Program': prog,
                'Projects Funded': data['Count'],
                'Total Funding': f"${data['Total Amount']:,.0f}",
                'Total Units': data['Total Units'],
                'Avg Award': f"${data['Total Amount'] / data['Count']:,.0f}",
                'Avg Per Unit': f"${sum(data['Avg Per Unit']) / len(data['Avg Per Unit']):,.0f}"
            })
            
        reports['program_summary'] = pd.DataFrame(program_summary)
        
        # Geographic distribution
        geo_data = {}
        for award in awards_to_analyze:
            county = f"{award.state_code} - {award.county}"
            if county not in geo_data:
                geo_data[county] = {
                    'Projects': 0,
                    'Total Funding': 0,
                    'Rural': 0,
                    'Urban': 0
                }
            geo_data[county]['Projects'] += 1
            geo_data[county]['Total Funding'] += award.award_amount
            if award.rural:
                geo_data[county]['Rural'] += 1
            else:
                geo_data[county]['Urban'] += 1
                
        geo_summary = []
        for county, data in geo_data.items():
            geo_summary.append({
                'County': county,
                'Projects': data['Projects'],
                'Total Funding': f"${data['Total Funding']:,.0f}",
                'Rural Projects': data['Rural'],
                'Urban Projects': data['Urban']
            })
            
        reports['geographic_distribution'] = pd.DataFrame(geo_summary)
        
        return reports
        
    def save_data(self):
        """Save all data to files"""
        # Save programs
        programs_data = {k: asdict(v) for k, v in self.programs.items()}
        with open(self.data_dir / "special_fund_programs.json", 'w') as f:
            json.dump(programs_data, f, indent=2, default=str)
            
        # Save awards
        awards_data = [asdict(a) for a in self.awards]
        with open(self.data_dir / "funding_awards.json", 'w') as f:
            json.dump(awards_data, f, indent=2, default=str)
            
        # Generate comprehensive report
        self.generate_comprehensive_report()
        
    def load_data(self):
        """Load existing data from files"""
        # Load programs
        programs_file = self.data_dir / "special_fund_programs.json"
        if programs_file.exists():
            with open(programs_file, 'r') as f:
                programs_data = json.load(f)
                self.programs = {
                    k: SpecialFundProgram(**v) for k, v in programs_data.items()
                }
                
        # Load awards
        awards_file = self.data_dir / "funding_awards.json"
        if awards_file.exists():
            with open(awards_file, 'r') as f:
                awards_data = json.load(f)
                self.awards = [FundingAward(**a) for a in awards_data]
                
    def generate_comprehensive_report(self):
        """Generate comprehensive Excel report of all special funds"""
        report_path = self.data_dir / f"special_funds_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
            # Overview of all programs
            all_programs = []
            for program in self.programs.values():
                all_programs.append({
                    'State': program.state_code,
                    'Program': program.program_name,
                    'Type': program.fund_source.value,
                    'Agency': program.administering_agency,
                    '2024 Allocation': program.total_allocation_2024,
                    '2025 Allocation': program.total_allocation_2025,
                    'Active': program.active,
                    'Works with 9%': program.combines_with_9pct,
                    'Works with 4%': program.combines_with_4pct,
                    'Last Updated': program.last_updated
                })
                
            df_programs = pd.DataFrame(all_programs)
            df_programs.to_excel(writer, sheet_name='All Programs', index=False)
            
            # State summaries
            state_summary = []
            for state_code in set(p.state_code for p in self.programs.values()):
                state_progs = self.get_state_programs(state_code)
                total_2024 = sum(p.total_allocation_2024 or 0 for p in state_progs)
                total_2025 = sum(p.total_allocation_2025 or 0 for p in state_progs)
                
                state_summary.append({
                    'State': state_code,
                    'Total Programs': len(state_progs),
                    'Active Programs': sum(1 for p in state_progs if p.active),
                    'Total 2024 Allocation': total_2024,
                    'Total 2025 Allocation': total_2025,
                    'Federal Programs': sum(1 for p in state_progs if 'Federal' in p.fund_source.value),
                    'State Programs': sum(1 for p in state_progs if 'State' in p.fund_source.value)
                })
                
            df_states = pd.DataFrame(state_summary)
            df_states.to_excel(writer, sheet_name='State Summary', index=False)
            
def main():
    """Run the special funds tracking system"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    
    tracker = StateSpecialFundsTracker(base_dir)
    
    # Generate funding matrix for California
    print("\nCalifornia Special Funds Matrix:")
    ca_matrix = tracker.generate_state_funding_matrix("CA")
    print(ca_matrix.to_string())
    
    # Analyze funding combinations for a 100-unit project
    print("\n\nOptimal Funding Combinations for 100-unit 9% project in California:")
    ca_combos = tracker.analyze_funding_combinations("CA", project_size=100, lihtc_type="9%")
    print(ca_combos.to_string())
    
    # Generate funding matrix for Texas
    print("\n\nTexas Special Funds Matrix:")
    tx_matrix = tracker.generate_state_funding_matrix("TX")
    print(tx_matrix.to_string())
    
    print(f"\n\nReports saved to: {tracker.data_dir}")

if __name__ == "__main__":
    main()