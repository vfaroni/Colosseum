#!/usr/bin/env python3
"""
Batch Reporter - LIHTC Site Analysis Report Generation

This module provides functionality for generating comprehensive reports from
batch site analysis results, with support for multiple output formats.

Features:
- CSV summary reports with key metrics
- Detailed JSON exports with full analysis data
- Report filtering by various criteria
- Statistical analysis and aggregation
- Multiple output format support
- Error handling and validation
"""

import json
import logging
from typing import List, Dict, Any, Optional, Union, Set
from pathlib import Path
from datetime import datetime
import pandas as pd
from dataclasses import asdict


class ReportGenerationError(Exception):
    """Custom exception for report generation errors"""
    pass


class BatchReporter:
    """
    Report generator for batch LIHTC site analysis results
    
    Generates comprehensive reports in multiple formats with statistical
    analysis, filtering capabilities, and detailed error reporting.
    """
    
    def __init__(
        self,
        output_format: str = 'json',
        include_detailed_analysis: bool = True,
        include_summary_stats: bool = True,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize batch reporter
        
        Args:
            output_format: Default output format ('json', 'csv', or 'both')
            include_detailed_analysis: Include full analysis details in reports
            include_summary_stats: Include statistical summaries
            logger: Optional logger for report generation
        """
        self.output_format = output_format
        self.include_detailed_analysis = include_detailed_analysis
        self.include_summary_stats = include_summary_stats
        self.logger = logger or logging.getLogger(__name__)
        
        # Processing metadata (set by batch processor)
        self._processing_metadata = None
    
    def set_processing_metadata(self, metadata: Dict[str, Any]) -> None:
        """Set processing metadata for inclusion in reports"""
        self._processing_metadata = metadata
    
    def generate_csv_summary(self, results: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Generate CSV summary with key metrics for each site
        
        Args:
            results: List of batch processing results
            
        Returns:
            DataFrame with summary data
        """
        summary_data = []
        
        for result in results:
            site_data = {
                'site_id': result['site_id'],
                'success': result['success']
            }
            
            if result['success'] and result.get('analysis_result'):
                analysis = result['analysis_result']
                
                # Site information
                if hasattr(analysis, 'site_info'):
                    site_data.update({
                        'latitude': analysis.site_info.latitude,
                        'longitude': analysis.site_info.longitude,
                        'census_tract': getattr(analysis.site_info, 'census_tract', None)
                    })
                
                # Federal status
                if hasattr(analysis, 'federal_status'):
                    federal = analysis.federal_status
                    site_data.update({
                        'qct_qualified': federal.get('qct_qualified', False),
                        'dda_qualified': federal.get('dda_qualified', False),
                        'basis_boost_eligible': federal.get('qct_qualified', False) or federal.get('dda_qualified', False),
                        'basis_boost_percentage': federal.get('basis_boost_percentage', 0)
                    })
                
                # State scoring
                if hasattr(analysis, 'state_scoring'):
                    scoring = analysis.state_scoring
                    site_data.update({
                        'total_ctcac_points': scoring.get('total_points', None),
                        'max_possible_points': scoring.get('max_possible_points', 30),
                        'resource_category': scoring.get('resource_category', None),
                        'opportunity_area_points': scoring.get('opportunity_area_points', 0)
                    })
                
                # Amenity analysis
                if hasattr(analysis, 'amenity_analysis'):
                    amenities = analysis.amenity_analysis
                    site_data.update({
                        'amenity_points': amenities.get('total_amenity_points', 0),
                        'max_amenity_points': amenities.get('max_possible_points', 10)
                    })
                
                # Competitive summary
                if hasattr(analysis, 'competitive_summary'):
                    competitive = analysis.competitive_summary
                    site_data.update({
                        'competitive_tier': competitive.get('competitive_tier', None),
                        'mandatory_criteria_met': competitive.get('mandatory_criteria_met', None)
                    })
                
                # Input data from CSV
                if 'input_data' in result:
                    input_data = result['input_data']
                    site_data.update({
                        'input_address': input_data.get('address', None),
                        'input_notes': input_data.get('notes', None)
                    })
            
            else:
                # Failed analysis
                site_data.update({
                    'latitude': None,
                    'longitude': None,
                    'error_message': result.get('error_message', 'Unknown error'),
                    'error_type': result.get('error_type', 'Unknown'),
                    'qct_qualified': None,
                    'dda_qualified': None,
                    'basis_boost_eligible': None,
                    'total_ctcac_points': None,
                    'resource_category': None,
                    'amenity_points': None,
                    'competitive_tier': None
                })
                
                # Still include input data if available
                if 'input_data' in result:
                    input_data = result['input_data']
                    site_data.update({
                        'latitude': input_data.get('latitude'),
                        'longitude': input_data.get('longitude'),
                        'input_address': input_data.get('address', None),
                        'input_notes': input_data.get('notes', None)
                    })
            
            summary_data.append(site_data)
        
        df = pd.DataFrame(summary_data)
        
        # Reorder columns for better readability
        preferred_order = [
            'site_id', 'success', 'latitude', 'longitude', 'input_address',
            'qct_qualified', 'dda_qualified', 'basis_boost_eligible', 'basis_boost_percentage',
            'total_ctcac_points', 'max_possible_points', 'resource_category',
            'amenity_points', 'max_amenity_points', 'competitive_tier',
            'mandatory_criteria_met', 'error_message', 'error_type', 'input_notes'
        ]
        
        # Only include columns that exist
        column_order = [col for col in preferred_order if col in df.columns]
        remaining_cols = [col for col in df.columns if col not in column_order]
        final_order = column_order + remaining_cols
        
        return df[final_order]
    
    def generate_detailed_json(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate detailed JSON export with full analysis data
        
        Args:
            results: List of batch processing results
            
        Returns:
            Complete JSON report dictionary
        """
        report = {
            'batch_metadata': self._get_batch_metadata(results),
            'summary_statistics': self.generate_summary_statistics(results),
            'site_analyses': []
        }
        
        for result in results:
            site_analysis = {
                'site_id': result['site_id'],
                'success': result['success'],
                'processing_info': {
                    'processing_time': result.get('processing_time'),
                    'error_message': result.get('error_message'),
                    'error_type': result.get('error_type')
                }
            }
            
            # Include input data
            if 'input_data' in result:
                site_analysis['input_data'] = result['input_data']
            
            # Include full analysis result if successful
            if result['success'] and result.get('analysis_result'):
                analysis = result['analysis_result']
                site_analysis['analysis'] = self._serialize_analysis_result(analysis)
            
            report['site_analyses'].append(site_analysis)
        
        return report
    
    def generate_summary_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate statistical summary of batch results
        
        Args:
            results: List of batch processing results
            
        Returns:
            Statistical summary dictionary
        """
        total_sites = len(results)
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        stats = {
            'total_sites': total_sites,
            'successful_analyses': len(successful_results),
            'failed_analyses': len(failed_results),
            'success_rate': (len(successful_results) / total_sites * 100) if total_sites > 0 else 0
        }
        
        if successful_results:
            # Extract scoring data for statistics
            scores = []
            qct_count = 0
            dda_count = 0
            resource_categories = {}
            
            for result in successful_results:
                analysis = result.get('analysis_result')
                if analysis:
                    # CTCAC scores
                    if hasattr(analysis, 'state_scoring'):
                        score = analysis.state_scoring.get('total_points')
                        if score is not None:
                            scores.append(score)
                    
                    # Federal qualifications
                    if hasattr(analysis, 'federal_status'):
                        federal = analysis.federal_status
                        if federal.get('qct_qualified'):
                            qct_count += 1
                        if federal.get('dda_qualified'):
                            dda_count += 1
                    
                    # Resource categories
                    if hasattr(analysis, 'state_scoring'):
                        category = analysis.state_scoring.get('resource_category')
                        if category:
                            resource_categories[category] = resource_categories.get(category, 0) + 1
            
            # Scoring statistics
            if scores:
                stats.update({
                    'avg_ctcac_points': sum(scores) / len(scores),
                    'max_ctcac_points': max(scores),
                    'min_ctcac_points': min(scores),
                    'median_ctcac_points': sorted(scores)[len(scores) // 2] if scores else None
                })
            
            # Federal qualification statistics
            stats.update({
                'qct_qualified_count': qct_count,
                'dda_qualified_count': dda_count,
                'qct_qualification_rate': (qct_count / len(successful_results) * 100),
                'dda_qualification_rate': (dda_count / len(successful_results) * 100),
                'federal_qualified_count': len([r for r in successful_results 
                                               if self._is_federally_qualified(r)]),
            })
            
            # Resource category distribution
            stats['resource_category_distribution'] = resource_categories
        
        # Error analysis
        if failed_results:
            error_types = {}
            for result in failed_results:
                error_type = result.get('error_type', 'Unknown')
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            stats['error_type_distribution'] = error_types
        
        return stats
    
    def export_csv_summary(self, results: List[Dict[str, Any]], output_path: str) -> None:
        """
        Export CSV summary to file
        
        Args:
            results: List of batch processing results
            output_path: Path for CSV output file
        """
        try:
            df = self.generate_csv_summary(results)
            df.to_csv(output_path, index=False)
            self.logger.info(f"CSV summary exported to: {output_path}")
        except Exception as e:
            raise ReportGenerationError(f"Failed to export CSV summary: {e}")
    
    def export_detailed_json(self, results: List[Dict[str, Any]], output_path: str) -> None:
        """
        Export detailed JSON report to file
        
        Args:
            results: List of batch processing results
            output_path: Path for JSON output file
        """
        try:
            report = self.generate_detailed_json(results)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            self.logger.info(f"Detailed JSON report exported to: {output_path}")
        except Exception as e:
            raise ReportGenerationError(f"Failed to export JSON report: {e}")
    
    def export_multiple_formats(
        self, 
        results: List[Dict[str, Any]], 
        output_base: str, 
        formats: List[str]
    ) -> Dict[str, str]:
        """
        Export to multiple formats simultaneously
        
        Args:
            results: List of batch processing results
            output_base: Base path/name for output files
            formats: List of formats to export ('csv', 'json')
            
        Returns:
            Dictionary mapping format to output file path
        """
        output_paths = {}
        
        for format_type in formats:
            if format_type == 'csv':
                output_path = f"{output_base}_summary.csv"
                self.export_csv_summary(results, output_path)
                output_paths['csv'] = output_path
            
            elif format_type == 'json':
                output_path = f"{output_base}_detailed.json"
                self.export_detailed_json(results, output_path)
                output_paths['json'] = output_path
            
            else:
                self.logger.warning(f"Unknown format: {format_type}")
        
        return output_paths
    
    def filter_results(
        self,
        results: List[Dict[str, Any]],
        successful_only: bool = False,
        qct_qualified: Optional[bool] = None,
        dda_qualified: Optional[bool] = None,
        federal_qualified: Optional[bool] = None,
        min_ctcac_points: Optional[float] = None,
        max_ctcac_points: Optional[float] = None,
        resource_categories: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter results based on various criteria
        
        Args:
            results: List of batch processing results
            successful_only: Only include successful analyses
            qct_qualified: Filter by QCT qualification status
            dda_qualified: Filter by DDA qualification status
            federal_qualified: Filter by any federal qualification
            min_ctcac_points: Minimum CTCAC score threshold
            max_ctcac_points: Maximum CTCAC score threshold
            resource_categories: List of acceptable resource categories
            
        Returns:
            Filtered list of results
        """
        filtered = results
        
        # Filter by success status
        if successful_only:
            filtered = [r for r in filtered if r['success']]
        
        # Only apply analysis-based filters to successful results
        analysis_filtered = []
        for result in filtered:
            if not result['success']:
                # Keep failed results only if not filtering by successful_only AND no analysis-based filters are applied
                if (not successful_only and 
                    qct_qualified is None and dda_qualified is None and federal_qualified is None and
                    min_ctcac_points is None and max_ctcac_points is None and resource_categories is None):
                    analysis_filtered.append(result)
                continue
            
            analysis = result.get('analysis_result')
            if not analysis:
                continue
            
            # Federal qualification filters
            if qct_qualified is not None:
                if hasattr(analysis, 'federal_status'):
                    if analysis.federal_status.get('qct_qualified') != qct_qualified:
                        continue
                else:
                    continue
            
            if dda_qualified is not None:
                if hasattr(analysis, 'federal_status'):
                    if analysis.federal_status.get('dda_qualified') != dda_qualified:
                        continue
                else:
                    continue
            
            if federal_qualified is not None:
                is_fed_qualified = self._is_federally_qualified(result)
                if is_fed_qualified != federal_qualified:
                    continue
            
            # CTCAC score filters
            if min_ctcac_points is not None or max_ctcac_points is not None:
                if hasattr(analysis, 'state_scoring'):
                    score = analysis.state_scoring.get('total_points')
                    if score is not None:
                        if min_ctcac_points is not None and score < min_ctcac_points:
                            continue
                        if max_ctcac_points is not None and score > max_ctcac_points:
                            continue
                    else:
                        continue
                else:
                    continue
            
            # Resource category filter
            if resource_categories:
                if hasattr(analysis, 'state_scoring'):
                    category = analysis.state_scoring.get('resource_category')
                    if category not in resource_categories:
                        continue
                else:
                    continue
            
            analysis_filtered.append(result)
        
        return analysis_filtered
    
    def generate_output_filename(self, base_name: str, format_type: str) -> str:
        """
        Generate timestamped output filename
        
        Args:
            base_name: Base name for the file
            format_type: File format extension
            
        Returns:
            Timestamped filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.{format_type}"
    
    def validate_output_path(self, output_path: str) -> None:
        """
        Validate output path before writing
        
        Args:
            output_path: Path to validate
            
        Raises:
            ValueError: If path is invalid
        """
        if not output_path:
            raise ValueError("Invalid output path: empty path")
        
        output_file = Path(output_path)
        parent_dir = output_file.parent
        
        if not parent_dir.exists():
            raise ValueError(f"Directory does not exist: {parent_dir}")
        
        if not parent_dir.is_dir():
            raise ValueError(f"Parent path is not a directory: {parent_dir}")
    
    def _get_batch_metadata(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate batch metadata for JSON reports"""
        metadata = {
            'report_generated': datetime.now().isoformat(),
            'total_sites_processed': len(results),
            'successful_analyses': len([r for r in results if r['success']]),
            'failed_analyses': len([r for r in results if not r['success']]),
            'report_generator_version': '1.0.0'
        }
        
        # Include processing metadata if available
        if self._processing_metadata:
            metadata['processing_metadata'] = self._processing_metadata
        
        return metadata
    
    def _serialize_analysis_result(self, analysis) -> Dict[str, Any]:
        """
        Serialize analysis result for JSON export
        
        Args:
            analysis: AnalysisResult object
            
        Returns:
            Serializable dictionary
        """
        serialized = {}
        
        # Handle different attribute types
        for attr_name in dir(analysis):
            if attr_name.startswith('_'):
                continue
            
            attr_value = getattr(analysis, attr_name)
            
            # Skip methods
            if callable(attr_value):
                continue
            
            try:
                # Try direct serialization
                json.dumps(attr_value, default=str)
                serialized[attr_name] = attr_value
            except (TypeError, ValueError):
                # Handle complex objects
                if hasattr(attr_value, '__dict__'):
                    serialized[attr_name] = attr_value.__dict__
                else:
                    serialized[attr_name] = str(attr_value)
        
        return serialized
    
    def _is_federally_qualified(self, result: Dict[str, Any]) -> bool:
        """Check if a site has any federal qualification"""
        if not result['success']:
            return False
        
        analysis = result.get('analysis_result')
        if not analysis or not hasattr(analysis, 'federal_status'):
            return False
        
        federal = analysis.federal_status
        return federal.get('qct_qualified', False) or federal.get('dda_qualified', False)


def main():
    """Command-line interface for testing batch reporter"""
    import sys
    import argparse
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description='Generate reports from batch processing results')
    parser.add_argument('results_json', help='Path to JSON file with batch processing results')
    parser.add_argument('--output', '-o', default='batch_report', help='Output file base name')
    parser.add_argument('--format', choices=['csv', 'json', 'both'], default='both', help='Output format')
    parser.add_argument('--filter-successful', action='store_true', help='Only include successful analyses')
    parser.add_argument('--min-score', type=float, help='Minimum CTCAC score filter')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # Load results
        with open(args.results_json, 'r') as f:
            results_data = json.load(f)
        
        # Extract results array (handle different JSON structures)
        if isinstance(results_data, list):
            results = results_data
        elif 'site_analyses' in results_data:
            results = results_data['site_analyses']
        else:
            results = results_data.get('results', [])
        
        print(f"Loaded {len(results)} processing results from {args.results_json}")
        
        # Initialize reporter
        reporter = BatchReporter()
        
        # Apply filters if specified
        filtered_results = results
        if args.filter_successful or args.min_score:
            filtered_results = reporter.filter_results(
                results,
                successful_only=args.filter_successful,
                min_ctcac_points=args.min_score
            )
            print(f"Filtered to {len(filtered_results)} results")
        
        # Generate reports
        formats = ['csv', 'json'] if args.format == 'both' else [args.format]
        output_paths = reporter.export_multiple_formats(filtered_results, args.output, formats)
        
        # Show summary
        stats = reporter.generate_summary_statistics(filtered_results)
        print(f"\nReport Summary:")
        print(f"  Total Sites: {stats['total_sites']}")
        print(f"  Successful: {stats['successful_analyses']} ({stats['success_rate']:.1f}%)")
        print(f"  Failed: {stats['failed_analyses']}")
        
        if stats.get('avg_ctcac_points'):
            print(f"  Average CTCAC Score: {stats['avg_ctcac_points']:.1f}")
            print(f"  Score Range: {stats['min_ctcac_points']:.1f} - {stats['max_ctcac_points']:.1f}")
        
        print(f"\nOutput Files Generated:")
        for format_type, path in output_paths.items():
            print(f"  {format_type.upper()}: {path}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()