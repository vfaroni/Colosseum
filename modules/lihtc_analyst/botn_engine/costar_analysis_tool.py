#!/usr/bin/env python3
"""
CoStar Data Analysis Tool - Analyze structure and content of CoStar export files
Prepare for consolidation while preserving all columns
"""

import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoStarAnalyzer:
    """Analyze CoStar export files for consolidation planning"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.sites_path = self.base_path / "Sites"
        self.analysis_results = {}
        
    def analyze_all_costar_files(self):
        """Analyze all CoStar export files (8-15) plus existing combined file"""
        
        logger.info("🔍 COSTAR DATA ANALYSIS - COMPREHENSIVE STRUCTURE REVIEW")
        logger.info("=" * 70)
        
        # Files to analyze
        files_to_analyze = [
            'CostarExport-8.xlsx',
            'CostarExport-9.xlsx', 
            'CostarExport-10.xlsx',
            'CostarExport-11.xlsx',
            'CostarExport-12.xlsx',
            'CostarExport-13.xlsx',
            'CostarExport-14.xlsx',
            'CostarExport-15.xlsx',
            'Combined_CostarExport_Final.xlsx'
        ]
        
        for filename in files_to_analyze:
            file_path = self.sites_path / filename
            if file_path.exists():
                logger.info(f"\n📊 ANALYZING: {filename}")
                logger.info("-" * 50)
                
                result = self.analyze_single_file(file_path)
                self.analysis_results[filename] = result
            else:
                logger.warning(f"⚠️  File not found: {filename}")
        
        # Generate comprehensive summary
        self.generate_consolidation_summary()
        
        return self.analysis_results
    
    def analyze_single_file(self, file_path):
        """Analyze a single CoStar export file"""
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=0)  # First sheet
            
            analysis = {
                'file_path': str(file_path),
                'file_size_mb': round(file_path.stat().st_size / (1024*1024), 2),
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': list(df.columns),
                'data_types': df.dtypes.to_dict(),
                'null_counts': df.isnull().sum().to_dict(),
                'sample_data': {},
                'unique_properties': None,
                'duplicate_check': None
            }
            
            # Get sample data from first few rows
            for col in df.columns[:10]:  # First 10 columns as sample
                sample_values = df[col].dropna().head(3).tolist()
                analysis['sample_data'][col] = sample_values
            
            # Check for unique identifier columns
            for potential_id_col in ['Property Name', 'PropertyID', 'Property Address', 'Address']:
                if potential_id_col in df.columns:
                    unique_count = df[potential_id_col].nunique()
                    total_count = df[potential_id_col].count()  # Non-null count
                    analysis['unique_properties'] = {
                        'column': potential_id_col,
                        'unique_count': unique_count,
                        'total_count': total_count,
                        'duplicate_ratio': round((total_count - unique_count) / total_count * 100, 2) if total_count > 0 else 0
                    }
                    break
            
            # Check for potential duplicates
            if 'Property Name' in df.columns:
                duplicates = df[df.duplicated(['Property Name'], keep=False)]
                analysis['duplicate_check'] = {
                    'has_duplicates': len(duplicates) > 0,
                    'duplicate_count': len(duplicates),
                    'sample_duplicates': duplicates['Property Name'].head(5).tolist() if len(duplicates) > 0 else []
                }
            
            logger.info(f"   📏 Dimensions: {analysis['row_count']} rows × {analysis['column_count']} columns")
            logger.info(f"   💾 File size: {analysis['file_size_mb']} MB")
            
            if analysis['unique_properties']:
                up = analysis['unique_properties']
                logger.info(f"   🏠 Properties: {up['unique_count']} unique out of {up['total_count']} total")
                if up['duplicate_ratio'] > 0:
                    logger.info(f"   ⚠️  Duplicates: {up['duplicate_ratio']}%")
            
            # Show first few columns
            logger.info(f"   📋 Sample columns: {analysis['columns'][:5]}...")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing {file_path.name}: {str(e)}")
            return {
                'file_path': str(file_path),
                'error': str(e),
                'analysis_failed': True
            }
    
    def generate_consolidation_summary(self):
        """Generate summary for consolidation planning"""
        
        logger.info(f"\n🎯 CONSOLIDATION ANALYSIS SUMMARY")
        logger.info("=" * 60)
        
        successful_analyses = [r for r in self.analysis_results.values() if 'analysis_failed' not in r]
        
        if not successful_analyses:
            logger.error("❌ No files could be analyzed successfully")
            return
        
        # Total data overview
        total_rows = sum(r['row_count'] for r in successful_analyses)
        total_size_mb = sum(r['file_size_mb'] for r in successful_analyses)
        
        logger.info(f"📊 TOTAL DATA VOLUME:")
        logger.info(f"   Files analyzed: {len(successful_analyses)}")
        logger.info(f"   Total rows: {total_rows:,}")
        logger.info(f"   Total size: {total_size_mb:.2f} MB")
        
        # Column analysis
        all_columns = {}
        for filename, analysis in self.analysis_results.items():
            if 'columns' in analysis:
                for col in analysis['columns']:
                    if col not in all_columns:
                        all_columns[col] = []
                    all_columns[col].append(filename)
        
        logger.info(f"\n📋 COLUMN ANALYSIS:")
        logger.info(f"   Unique columns found: {len(all_columns)}")
        
        # Find common columns (appear in all files)
        common_columns = [col for col, files in all_columns.items() if len(files) == len(successful_analyses)]
        unique_columns = [col for col, files in all_columns.items() if len(files) == 1]
        
        logger.info(f"   Common to all files: {len(common_columns)}")
        logger.info(f"   Unique to one file: {len(unique_columns)}")
        
        if common_columns:
            logger.info(f"   📌 Common columns sample: {common_columns[:10]}")
        
        if unique_columns:
            logger.info(f"   🔸 Unique columns sample: {unique_columns[:10]}")
        
        # Property identification analysis
        property_counts = []
        for analysis in successful_analyses:
            if analysis.get('unique_properties'):
                property_counts.append(analysis['unique_properties']['unique_count'])
        
        if property_counts:
            logger.info(f"\n🏠 PROPERTY COUNT ANALYSIS:")
            logger.info(f"   Min properties per file: {min(property_counts):,}")
            logger.info(f"   Max properties per file: {max(property_counts):,}")
            logger.info(f"   Average per file: {sum(property_counts) / len(property_counts):,.0f}")
        
        # Consolidation recommendations
        logger.info(f"\n💡 CONSOLIDATION RECOMMENDATIONS:")
        logger.info("   ✅ Preserve ALL columns to maintain data completeness")
        logger.info("   ✅ Use outer join to capture all unique properties")
        logger.info("   ✅ Flag data source for each row")
        logger.info("   ✅ Handle duplicate properties with merge priority logic")
        
        # Save detailed analysis to file
        self.save_analysis_report()
    
    def save_analysis_report(self):
        """Save detailed analysis to JSON file"""
        
        output_file = self.base_path / "costar_analysis_report.json"
        
        # Convert pandas types to JSON-serializable types
        json_results = {}
        for filename, analysis in self.analysis_results.items():
            json_analysis = analysis.copy()
            
            if 'data_types' in json_analysis:
                # Convert pandas dtypes to strings
                json_analysis['data_types'] = {k: str(v) for k, v in json_analysis['data_types'].items()}
            
            json_results[filename] = json_analysis
        
        # Add metadata
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'files_analyzed': list(self.analysis_results.keys()),
            'analysis_results': json_results,
            'consolidation_plan': {
                'strategy': 'preserve_all_columns',
                'merge_approach': 'outer_join',
                'duplicate_handling': 'merge_with_priority',
                'source_tracking': True
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Detailed analysis saved to: {output_file.name}")
    
    def recommend_consolidation_strategy(self):
        """Recommend the best approach for consolidating the files"""
        
        logger.info(f"\n🚀 CONSOLIDATION STRATEGY RECOMMENDATIONS")
        logger.info("=" * 60)
        
        logger.info("📋 RECOMMENDED APPROACH:")
        logger.info("   1. 🔄 Use pandas concat() with outer join")
        logger.info("   2. 📊 Add 'source_file' column to track data origin")
        logger.info("   3. 🏠 Identify duplicates by Property Name + Address")
        logger.info("   4. 📈 Prioritize newer exports (higher numbers) for conflicts")
        logger.info("   5. 💾 Preserve ALL unique columns from all files")
        logger.info("   6. ✅ Create comprehensive validation report")
        
        logger.info(f"\n⚡ EXPECTED BENEFITS:")
        logger.info("   ✅ No data loss - all columns preserved")
        logger.info("   ✅ Clear data lineage tracking")
        logger.info("   ✅ Improved data quality through deduplication")
        logger.info("   ✅ Single source of truth for BOTN processing")

def main():
    analyzer = CoStarAnalyzer()
    
    print("🔍 CoStar Data Analysis Tool")
    print("Analyzing exports 8-15 and existing combined file...")
    print()
    
    # Run comprehensive analysis
    results = analyzer.analyze_all_costar_files()
    
    # Generate consolidation recommendations
    analyzer.recommend_consolidation_strategy()
    
    print(f"\n✅ Analysis complete! Check costar_analysis_report.json for details")

if __name__ == "__main__":
    main()