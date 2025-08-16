#!/usr/bin/env python3
"""
Transit Analyzer - LIHTC Transit Scoring Integration

Integrates the existing CA LIHTC Scorer system with BOTN engine for comprehensive
transit analysis of filtered development portfolios.

Key Features:
- Leverages 90,924+ California transit stops database
- CTCAC-compliant scoring (3-7 points for buses, 7 points for rail)
- Professional reporting with distance/frequency analysis
- Batch processing for entire filtered portfolios
"""

import sys
import os
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Add CA LIHTC Scorer to path
ca_scorer_path = str(Path(__file__).parent.parent.parent.parent / "priorcode/!VFupload/CALIHTCScorer")
sys.path.insert(0, ca_scorer_path)
sys.path.insert(0, str(Path(ca_scorer_path) / "src"))

try:
    # Direct imports with absolute paths
    import importlib.util
    
    # Load site analyzer
    site_analyzer_spec = importlib.util.spec_from_file_location(
        "site_analyzer", 
        Path(ca_scorer_path) / "src/core/site_analyzer.py"
    )
    site_analyzer_module = importlib.util.module_from_spec(site_analyzer_spec)
    site_analyzer_spec.loader.exec_module(site_analyzer_module)
    SiteAnalyzer = site_analyzer_module.SiteAnalyzer
    
    # Load batch processor
    batch_processor_spec = importlib.util.spec_from_file_location(
        "batch_processor", 
        Path(ca_scorer_path) / "src/batch/batch_processor.py"
    )
    batch_processor_module = importlib.util.module_from_spec(batch_processor_spec)
    batch_processor_spec.loader.exec_module(batch_processor_module)
    BatchSiteProcessor = batch_processor_module.BatchSiteProcessor
    
    SCORER_AVAILABLE = True
except Exception as e:
    logging.warning(f"CA LIHTC Scorer import failed: {e}")
    SCORER_AVAILABLE = False
    SiteAnalyzer = None
    BatchSiteProcessor = None


class TransitAnalyzer:
    """
    Transit Analysis Engine for BOTN Portfolio
    
    Integrates CA LIHTC Scorer's 90,924+ transit stops with filtered BOTN portfolios
    for comprehensive transit scoring and compliance analysis.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Transit Analyzer"""
        self.logger = self._setup_logging()
        
        if not SCORER_AVAILABLE:
            raise RuntimeError("CA LIHTC Scorer system not available - check import paths")
            
        # Initialize CA LIHTC Scorer
        try:
            self.site_analyzer = SiteAnalyzer(config_path)
            self.batch_processor = BatchSiteProcessor(
                max_workers=3,  # Conservative for reliability
                error_handling='continue',
                progress_callback=self._progress_callback
            )
            self.logger.info("CA LIHTC Scorer initialized - 90,924+ transit stops ready")
        except Exception as e:
            self.logger.error(f"Failed to initialize CA LIHTC Scorer: {e}")
            raise
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for transit analysis"""
        logger = logging.getLogger('TransitAnalyzer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _progress_callback(self, progress):
        """Progress callback for batch processing"""
        self.logger.info(
            f"Transit Analysis Progress: {progress.completed}/{progress.total} "
            f"({progress.percentage:.1f}%) - Success: {progress.successful}, "
            f"Failed: {progress.failed}, Rate: {progress.current_rate:.2f} sites/sec"
        )
    
    def analyze_portfolio_excel(
        self, 
        excel_path: str, 
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze complete filtered portfolio from Excel file
        
        Args:
            excel_path: Path to filtered portfolio Excel file
            output_path: Optional output path for results
            
        Returns:
            Dictionary containing analysis results and summary
        """
        self.logger.info(f"Starting transit analysis of portfolio: {excel_path}")
        
        try:
            # Load portfolio data
            df = pd.read_excel(excel_path)
            self.logger.info(f"Loaded {len(df)} sites from portfolio")
            
            # Validate required columns
            required_cols = ['Latitude', 'Longitude']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Process sites
            sites_data = []
            for idx, row in df.iterrows():
                site_data = {
                    'site_id': f"site_{idx:04d}",
                    'latitude': float(row['Latitude']),
                    'longitude': float(row['Longitude']),
                    'state': 'CA',  # Primary focus on California
                    'original_data': row.to_dict()
                }
                sites_data.append(site_data)
            
            # Execute batch transit analysis
            self.logger.info("Executing batch transit analysis with CA LIHTC Scorer...")
            results = self.batch_processor.process_sites(sites_data)
            
            # Generate comprehensive report
            analysis_summary = self._generate_analysis_summary(results, df)
            
            # Save results if output path specified
            if output_path:
                self._save_results(results, analysis_summary, output_path)
            
            self.logger.info("Transit analysis completed successfully")
            return {
                'results': results,
                'summary': analysis_summary,
                'metadata': {
                    'total_sites': len(sites_data),
                    'successful_analyses': len([r for r in results if r.get('success', False)]),
                    'analysis_timestamp': datetime.now().isoformat(),
                    'scorer_version': '1.0.0'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Portfolio analysis failed: {e}")
            raise
    
    def _generate_analysis_summary(
        self, 
        results: List[Dict[str, Any]], 
        original_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Generate comprehensive analysis summary"""
        
        successful_results = [r for r in results if r.get('success', False)]
        
        # Transit scoring statistics
        transit_scores = []
        high_transit_sites = 0
        
        for result in successful_results:
            if 'analysis_result' in result:
                analysis = result['analysis_result']
                if hasattr(analysis, 'amenity_analysis'):
                    amenity_data = analysis.amenity_analysis
                    if isinstance(amenity_data, dict) and 'amenity_breakdown' in amenity_data:
                        transit_info = amenity_data['amenity_breakdown'].get('transit', {})
                        transit_score = transit_info.get('points_earned', 0)
                        transit_scores.append(transit_score)
                        if transit_score >= 5:  # High transit threshold
                            high_transit_sites += 1
        
        # Calculate statistics
        avg_transit_score = sum(transit_scores) / len(transit_scores) if transit_scores else 0
        max_transit_score = max(transit_scores) if transit_scores else 0
        
        return {
            'portfolio_summary': {
                'total_sites_analyzed': len(results),
                'successful_analyses': len(successful_results),
                'analysis_success_rate': len(successful_results) / len(results) * 100 if results else 0
            },
            'transit_scoring_summary': {
                'sites_with_transit_data': len(transit_scores),
                'average_transit_score': round(avg_transit_score, 2),
                'maximum_transit_score': max_transit_score,
                'high_transit_sites_count': high_transit_sites,
                'high_transit_percentage': round(high_transit_sites / len(transit_scores) * 100, 1) if transit_scores else 0
            },
            'ca_lihtc_scorer_stats': {
                'transit_stops_database': '90,924+ unique stops',
                'gtfs_sources': ['VTA (3,335 stops)', '511 Regional (21,024 stops)'],
                'scoring_system': 'CTCAC 2025 compliant'
            }
        }
    
    def _save_results(
        self, 
        results: List[Dict[str, Any]], 
        summary: Dict[str, Any], 
        output_path: str
    ):
        """Save analysis results to files"""
        base_path = Path(output_path)
        base_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results as JSON
        results_file = base_path / f"transit_analysis_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'results': results,
                'summary': summary,
                'generated_at': datetime.now().isoformat()
            }, f, indent=2, default=str)
        
        # Save summary as Excel
        summary_file = base_path / f"transit_analysis_summary_{timestamp}.xlsx"
        
        # Create summary DataFrame
        summary_data = []
        for i, result in enumerate(results):
            if result.get('success', False) and 'analysis_result' in result:
                analysis = result['analysis_result']
                if hasattr(analysis, 'site_info') and hasattr(analysis, 'amenity_analysis'):
                    site_info = analysis.site_info
                    amenity_data = analysis.amenity_analysis
                    
                    if isinstance(amenity_data, dict) and 'amenity_breakdown' in amenity_data:
                        transit_info = amenity_data['amenity_breakdown'].get('transit', {})
                        
                        summary_data.append({
                            'Site_ID': f"site_{i:04d}",
                            'Latitude': site_info.latitude,
                            'Longitude': site_info.longitude,
                            'Transit_Points': transit_info.get('points_earned', 0),
                            'Transit_Stops_Found': len(transit_info.get('details', [])),
                            'Closest_Stop_Distance': min([d.get('distance', 999) for d in transit_info.get('details', [])]) if transit_info.get('details') else None,
                            'Analysis_Status': 'Success'
                        })
                else:
                    summary_data.append({
                        'Site_ID': f"site_{i:04d}",
                        'Analysis_Status': 'Data Format Error'
                    })
            else:
                summary_data.append({
                    'Site_ID': f"site_{i:04d}",
                    'Analysis_Status': 'Failed'
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(summary_file, index=False)
        
        self.logger.info(f"Results saved to: {results_file}")
        self.logger.info(f"Summary saved to: {summary_file}")


def main():
    """Main execution function for testing"""
    try:
        # Initialize analyzer
        analyzer = TransitAnalyzer()
        
        # Define portfolio file path
        portfolio_file = (
            "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/"
            "modules/lihtc_analyst/botn_engine/Sites/"
            "BOTN_TRANSIT_ANALYSIS_INPUT_BACKUP_20250731_211324.xlsx"
        )
        
        # Define output path
        output_path = (
            "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/"
            "modules/lihtc_analyst/botn_engine/outputs"
        )
        
        # Execute analysis
        print("🚌 Starting Transit Analysis Mission...")
        print("📊 Leveraging CA LIHTC Scorer with 90,924+ transit stops")
        
        results = analyzer.analyze_portfolio_excel(portfolio_file, output_path)
        
        # Display summary
        summary = results['summary']
        print("\n✅ Transit Analysis Complete!")
        print(f"📈 Sites Analyzed: {summary['portfolio_summary']['successful_analyses']}")
        print(f"🚌 Avg Transit Score: {summary['transit_scoring_summary']['average_transit_score']}")
        print(f"🎯 High Transit Sites: {summary['transit_scoring_summary']['high_transit_sites_count']}")
        
    except Exception as e:
        print(f"❌ Transit Analysis Failed: {e}")
        raise


if __name__ == "__main__":
    main()