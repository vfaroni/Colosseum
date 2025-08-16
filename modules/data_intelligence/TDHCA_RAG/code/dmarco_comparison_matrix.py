#!/usr/bin/env python3
"""
D'Marco Comparison Matrix Generator

Creates a comprehensive comparison matrix for all extracted TDHCA projects
suitable for D'Marco site analysis with mapping capabilities and missing data handling.

Features:
- Column-wise comparison of all projects
- Missing data indicators ("-" for Not Applicable, "MISSING" for extraction failures)
- Mapping-ready with lat/long coordinates
- Export to Excel, CSV, and JSON formats
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any
from ultimate_tdhca_extractor import UltimateTDHCAExtractor, UltimateProjectData
import logging

logger = logging.getLogger(__name__)

class DMarcoComparisonMatrix:
    """Generate comprehensive comparison matrices for D'Marco site analysis"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.output_dir = self.base_path / 'dmarco_comparison_analysis'
        self.output_dir.mkdir(exist_ok=True)
        
        # Field mapping for clean column names
        self.field_mapping = {
            # Basic Info
            'application_number': 'App #',
            'project_name': 'Project Name',
            'development_type': 'Development Type',
            'property_type': 'Property Type',
            'targeted_population': 'Target Population',
            
            # Location & Mapping
            'full_address': 'Full Address',
            'street_address': 'Street Address',
            'city': 'City',
            'county': 'County', 
            'zip_code': 'ZIP Code',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
            'geocoding_accuracy': 'Geocoding Quality',
            'region': 'TDHCA Region',
            'census_tract': 'Census Tract',
            'urban_rural': 'Urban/Rural',
            'msa': 'MSA',
            
            # Units & Design
            'total_units': 'Total Units',
            'unit_mix': 'Unit Mix',
            'total_building_sf': 'Building SF',
            
            # Financial Core
            'total_development_cost': 'Total Dev Cost',
            'development_cost_per_unit': 'Cost/Unit',
            'land_cost_total': 'Land Cost',
            'land_cost_per_unit': 'Land Cost/Unit',
            'construction_cost_per_unit': 'Construction/Unit',
            'developer_fee': 'Developer Fee',
            'lihtc_equity': 'LIHTC Equity',
            'tax_credit_equity_price': 'Tax Credit Price',
            
            # Financing
            'first_lien_loan': 'First Lien',
            'second_lien_loan': 'Second Lien',
            'loan_to_cost_ratio': 'LTC Ratio',
            'equity_percentage': 'Equity %',
            
            # Team
            'developer_name': 'Developer',
            'general_contractor': 'GC',
            'architect': 'Architect',
            'management_company': 'Manager',
            
            # TDHCA Scoring
            'qct_dda_status': 'QCT/DDA',
            'opportunity_index_score': 'Opportunity Score',
            'total_tdhca_score': 'TDHCA Score',
            
            # Timeline
            'construction_start_date': 'Construction Start',
            'placed_in_service_date': 'Placed in Service',
            
            # Quality Metrics
            'geocoding_source': 'Geocoding Source',
            'overall_confidence': 'Data Confidence'
        }
        
    def process_all_applications(self) -> List[UltimateProjectData]:
        """Extract data from all TDHCA applications"""
        
        logger.info("🚀 Processing all applications for D'Marco comparison matrix")
        
        extractor = UltimateTDHCAExtractor(self.base_path)
        
        # Find all PDF applications
        applications_dir = self.base_path / 'Successful_2023_Applications'
        pdf_files = list(applications_dir.glob('**/*.pdf'))
        
        results = []
        for i, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
            try:
                result = extractor.process_application(pdf_file)
                if result:
                    results.append(result)
                    logger.info(f"  ✅ Success - {result.project_name or 'Unknown'}")
                else:
                    logger.warning(f"  ❌ Failed extraction")
            except Exception as e:
                logger.error(f"  ⚠️ Error: {str(e)}")
        
        logger.info(f"✅ Processed {len(results)}/{len(pdf_files)} applications successfully")
        return results
    
    def create_comparison_matrix(self, projects: List[UltimateProjectData]) -> pd.DataFrame:
        """Create the main comparison matrix DataFrame"""
        
        matrix_data = []
        
        for project in projects:
            row_data = {}
            
            # Process each field with proper missing data handling
            for field_name, column_name in self.field_mapping.items():
                value = getattr(project, field_name, None)
                
                # Handle different data types and missing values
                if value is None or value == "" or value == 0:
                    if field_name in ['latitude', 'longitude', 'total_units', 'total_development_cost']:
                        # Critical fields - mark as MISSING if empty
                        row_data[column_name] = "MISSING"
                    else:
                        # Optional fields - mark as N/A
                        row_data[column_name] = "-"
                elif isinstance(value, dict):
                    # Handle complex fields like unit_mix
                    if value:
                        if field_name == 'unit_mix':
                            # Format as "99x1BR, 65x2BR"
                            mix_parts = [f"{count}x{unit_type}" for unit_type, count in value.items()]
                            row_data[column_name] = ", ".join(mix_parts)
                        else:
                            row_data[column_name] = str(value)
                    else:
                        row_data[column_name] = "-"
                elif isinstance(value, list):
                    # Handle list fields
                    if value:
                        row_data[column_name] = "; ".join(str(item) for item in value)
                    else:
                        row_data[column_name] = "-"
                elif isinstance(value, float):
                    # Format financial numbers
                    if field_name in ['latitude', 'longitude']:
                        row_data[column_name] = f"{value:.6f}" if value != 0 else "MISSING"
                    elif field_name in ['tax_credit_equity_price']:
                        row_data[column_name] = f"${value:.2f}" if value != 0 else "-"
                    elif 'cost' in field_name or 'fee' in field_name or 'equity' in field_name or 'loan' in field_name:
                        row_data[column_name] = f"${value:,.0f}" if value != 0 else "-"
                    elif 'ratio' in field_name or 'percentage' in field_name:
                        row_data[column_name] = f"{value:.1f}%" if value != 0 else "-"
                    else:
                        row_data[column_name] = f"{value:.2f}" if value != 0 else "-"
                else:
                    row_data[column_name] = str(value) if value else "-"
            
            # Add calculated fields
            row_data['Units/Acre'] = self._calculate_units_per_acre(project)
            row_data['Hard Cost %'] = self._calculate_hard_cost_percentage(project)
            row_data['Mapping Ready'] = "YES" if project.latitude and project.longitude else "NO"
            
            # Add overall confidence from quality metrics
            if hasattr(project, 'confidence_scores') and project.confidence_scores:
                row_data['Data Confidence'] = f"{project.confidence_scores.get('overall', 0)*100:.0f}%"
            else:
                row_data['Data Confidence'] = "-"
            
            matrix_data.append(row_data)
        
        # Create DataFrame
        df = pd.DataFrame(matrix_data)
        
        # Sort by TDHCA Region, then by City for logical grouping
        sort_cols = []
        if 'TDHCA Region' in df.columns:
            sort_cols.append('TDHCA Region')
        if 'City' in df.columns:
            sort_cols.append('City')
        if sort_cols:
            df = df.sort_values(sort_cols)
        
        return df
    
    def _calculate_units_per_acre(self, project: UltimateProjectData) -> str:
        """Calculate units per acre if land data available"""
        if project.total_units and hasattr(project, 'land_acres') and project.land_acres:
            try:
                return f"{project.total_units / project.land_acres:.1f}"
            except:
                pass
        return "-"
    
    def _calculate_hard_cost_percentage(self, project: UltimateProjectData) -> str:
        """Calculate hard costs as % of total development cost"""
        if (hasattr(project, 'hard_costs') and project.hard_costs and 
            project.total_development_cost and project.total_development_cost > 0):
            try:
                return f"{(project.hard_costs / project.total_development_cost) * 100:.1f}%"
            except:
                pass
        return "-"
    
    def generate_mapping_dataset(self, projects: List[UltimateProjectData]) -> pd.DataFrame:
        """Generate mapping-specific dataset with geocoded coordinates"""
        
        mapping_data = []
        
        for project in projects:
            if project.latitude and project.longitude:  # Only include geocoded projects
                mapping_data.append({
                    'Project Name': project.project_name or f"App #{project.application_number}",
                    'Address': project.full_address,
                    'City': project.city,
                    'County': project.county,
                    'Latitude': project.latitude,
                    'Longitude': project.longitude,
                    'Total Units': project.total_units,
                    'Property Type': project.property_type,
                    'Development Cost': project.total_development_cost,
                    'Cost per Unit': project.development_cost_per_unit,
                    'QCT/DDA': project.qct_dda_status,
                    'TDHCA Score': project.total_tdhca_score,
                    'TDHCA Region': project.region,
                    'Geocoding Quality': project.geocoding_accuracy,
                    'Data Source': project.geocoding_source
                })
        
        return pd.DataFrame(mapping_data)
    
    def create_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for the comparison matrix"""
        
        stats = {
            'total_projects': len(df),
            'data_completeness': {},
            'geographic_distribution': {},
            'financial_summary': {},
            'mapping_readiness': {}
        }
        
        # Data completeness analysis
        for col in df.columns:
            missing_count = (df[col] == 'MISSING').sum()
            na_count = (df[col] == '-').sum()
            complete_count = len(df) - missing_count - na_count
            
            stats['data_completeness'][col] = {
                'complete': complete_count,
                'missing': missing_count,
                'not_applicable': na_count,
                'completeness_rate': f"{(complete_count / len(df)) * 100:.1f}%"
            }
        
        # Geographic distribution
        if 'City' in df.columns:
            city_counts = df['City'].value_counts()
            stats['geographic_distribution']['cities'] = city_counts.to_dict()
        
        if 'County' in df.columns:
            county_counts = df['County'].value_counts()
            stats['geographic_distribution']['counties'] = county_counts.to_dict()
        
        # Financial summary
        for col in ['Total Dev Cost', 'Cost/Unit', 'Land Cost']:
            if col in df.columns:
                # Convert financial strings back to numbers for analysis
                values = []
                for val in df[col]:
                    if val not in ['MISSING', '-']:
                        try:
                            # Remove $ and , for conversion
                            clean_val = val.replace('$', '').replace(',', '')
                            values.append(float(clean_val))
                        except:
                            pass
                
                if values:
                    stats['financial_summary'][col] = {
                        'count': len(values),
                        'mean': f"${sum(values) / len(values):,.0f}",
                        'min': f"${min(values):,.0f}",
                        'max': f"${max(values):,.0f}"
                    }
        
        # Mapping readiness
        if 'Mapping Ready' in df.columns:
            mapping_counts = df['Mapping Ready'].value_counts()
            stats['mapping_readiness'] = {
                'geocoded_projects': mapping_counts.get('YES', 0),
                'failed_geocoding': mapping_counts.get('NO', 0),
                'geocoding_success_rate': f"{(mapping_counts.get('YES', 0) / len(df)) * 100:.1f}%"
            }
        
        return stats
    
    def export_all_formats(self, projects: List[UltimateProjectData]) -> Dict[str, str]:
        """Export comparison matrix in all formats"""
        
        # Create main comparison matrix
        comparison_df = self.create_comparison_matrix(projects)
        
        # Create mapping dataset
        mapping_df = self.generate_mapping_dataset(projects)
        
        # Generate statistics
        stats = self.create_summary_statistics(comparison_df)
        
        # Export files
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        
        # Main comparison matrix
        excel_path = self.output_dir / f'dmarco_comparison_matrix_{timestamp}.xlsx'
        csv_path = self.output_dir / f'dmarco_comparison_matrix_{timestamp}.csv'
        
        # Excel with multiple sheets
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            comparison_df.to_excel(writer, sheet_name='Comparison Matrix', index=False)
            mapping_df.to_excel(writer, sheet_name='Mapping Dataset', index=False)
            
            # Summary statistics sheet
            stats_df = pd.DataFrame([
                {'Metric': 'Total Projects', 'Value': stats['total_projects']},
                {'Metric': 'Geocoded Projects', 'Value': stats['mapping_readiness'].get('geocoded_projects', 0)},
                {'Metric': 'Geocoding Success Rate', 'Value': stats['mapping_readiness'].get('geocoding_success_rate', '0%')}
            ])
            stats_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # CSV export
        comparison_df.to_csv(csv_path, index=False)
        
        # Mapping-specific exports
        mapping_csv = self.output_dir / f'dmarco_mapping_dataset_{timestamp}.csv'
        mapping_df.to_csv(mapping_csv, index=False)
        
        # JSON export for API/web use
        json_path = self.output_dir / f'dmarco_comparison_data_{timestamp}.json'
        export_data = {
            'metadata': {
                'generated_date': timestamp,
                'total_projects': len(projects),
                'geocoded_projects': len(mapping_df),
                'data_fields': len(comparison_df.columns)
            },
            'statistics': stats,
            'comparison_matrix': comparison_df.to_dict('records'),
            'mapping_dataset': mapping_df.to_dict('records')
        }
        
        with open(json_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return {
            'excel': str(excel_path),
            'csv': str(csv_path), 
            'mapping_csv': str(mapping_csv),
            'json': str(json_path),
            'summary': stats
        }


def main():
    """Generate D'Marco comparison matrix"""
    
    base_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites"
    
    generator = DMarcoComparisonMatrix(base_path)
    
    # Process all applications
    projects = generator.process_all_applications()
    
    if not projects:
        print("❌ No projects processed successfully")
        return
    
    print(f"✅ Processed {len(projects)} projects")
    
    # Export in all formats
    print("📊 Generating D'Marco comparison matrix...")
    exports = generator.export_all_formats(projects)
    
    print("\n🎉 D'MARCO COMPARISON MATRIX COMPLETE")
    print("=" * 60)
    print(f"📈 Excel (Multi-sheet): {exports['excel']}")
    print(f"📋 CSV (Main): {exports['csv']}")
    print(f"🗺️ Mapping CSV: {exports['mapping_csv']}")
    print(f"🔗 JSON (API Ready): {exports['json']}")
    
    print(f"\n📊 SUMMARY STATISTICS:")
    stats = exports['summary']
    print(f"Total Projects: {stats['total_projects']}")
    print(f"Geocoded Projects: {stats['mapping_readiness'].get('geocoded_projects', 0)}")
    print(f"Geocoding Success Rate: {stats['mapping_readiness'].get('geocoding_success_rate', '0%')}")
    
    return exports


if __name__ == "__main__":
    main()