#!/usr/bin/env python3
"""
CoStar Consolidation Validation Tool - Comprehensive validation of consolidated CoStar data
"""

import pandas as pd
from pathlib import Path
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoStarValidator:
    """Validate consolidated CoStar data for quality and completeness"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.sites_path = self.base_path / "Sites"
        
    def comprehensive_validation(self):
        """Run comprehensive validation on CombinedCostarExportUpdated.xlsx"""
        
        logger.info("🔍 COSTAR CONSOLIDATION VALIDATION - COMPREHENSIVE ANALYSIS")
        logger.info("=" * 70)
        
        # Load the consolidated file
        consolidated_file = self.sites_path / "CombinedCostarExportUpdated.xlsx"
        stats_file = self.sites_path / "CombinedCostarExportUpdated_stats.json"
        
        if not consolidated_file.exists():
            logger.error("❌ CombinedCostarExportUpdated.xlsx not found!")
            return False
        
        logger.info(f"📁 Validating: {consolidated_file.name}")
        logger.info(f"📊 File size: {round(consolidated_file.stat().st_size / (1024*1024), 2)} MB")
        
        # Load consolidated data
        try:
            df = pd.read_excel(consolidated_file, sheet_name='Consolidated_Data')
            logger.info(f"✅ Successfully loaded consolidated data")
            logger.info(f"   📏 Dimensions: {len(df)} rows × {len(df.columns)} columns")
        except Exception as e:
            logger.error(f"❌ Error loading consolidated data: {str(e)}")
            return False
        
        # Load statistics if available
        stats = None
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
                logger.info(f"📄 Consolidation statistics loaded")
            except Exception as e:
                logger.warning(f"⚠️  Could not load statistics: {str(e)}")
        
        # Run validation checks
        validation_results = {
            'file_info': self.validate_file_structure(df),
            'data_quality': self.validate_data_quality(df),
            'column_preservation': self.validate_column_preservation(df),
            'source_tracking': self.validate_source_tracking(df),
            'deduplication': self.validate_deduplication(df),
            'business_logic': self.validate_business_logic(df)
        }
        
        # Generate summary report
        self.generate_validation_report(validation_results, stats)
        
        # Determine overall validation status
        overall_success = all(result.get('status', False) for result in validation_results.values())
        
        if overall_success:
            logger.info(f"\n🎉 VALIDATION SUCCESSFUL: Data is ready for production use!")
        else:
            logger.warning(f"\n⚠️  VALIDATION WARNINGS: Some issues detected")
        
        return overall_success
    
    def validate_file_structure(self, df):
        """Validate file structure and basic integrity"""
        
        logger.info(f"\n📋 VALIDATING FILE STRUCTURE...")
        
        checks = {
            'has_data': len(df) > 0,
            'reasonable_size': 1000 <= len(df) <= 10000,
            'has_columns': len(df.columns) > 0,
            'expected_columns': len(df.columns) >= 50  # Should have many columns from consolidation
        }
        
        results = {
            'status': all(checks.values()),
            'checks': checks,
            'details': {
                'row_count': len(df),
                'column_count': len(df.columns),
                'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024*1024), 2)
            }
        }
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            logger.info(f"   {status} {check}: {passed}")
        
        return results
    
    def validate_data_quality(self, df):
        """Validate data quality metrics"""
        
        logger.info(f"\n📊 VALIDATING DATA QUALITY...")
        
        # Check for required columns
        required_cols = ['Property Name', 'Property Address', 'For Sale Price', 'City', 'State']
        missing_required = [col for col in required_cols if col not in df.columns]
        
        # Check data completeness
        completeness_stats = {}
        for col in required_cols:
            if col in df.columns:
                non_null_pct = (df[col].notna().sum() / len(df)) * 100
                completeness_stats[col] = round(non_null_pct, 2)
        
        # Check for reasonable data ranges
        price_issues = 0
        if 'For Sale Price' in df.columns:
            price_series = pd.to_numeric(df['For Sale Price'], errors='coerce')
            price_issues = ((price_series < 10000) | (price_series > 100000000)).sum()
        
        checks = {
            'all_required_columns_present': len(missing_required) == 0,
            'good_overall_completeness': all(pct >= 70 for pct in completeness_stats.values()),
            'reasonable_price_ranges': price_issues < len(df) * 0.05,  # Less than 5% price issues
            'has_metadata_columns': any('Source_File' in col or 'Data_Completeness' in col for col in df.columns)
        }
        
        results = {
            'status': all(checks.values()),
            'checks': checks,
            'details': {
                'missing_required_columns': missing_required,
                'completeness_stats': completeness_stats,
                'price_issues_count': price_issues
            }
        }
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            logger.info(f"   {status} {check}: {passed}")
        
        if completeness_stats:
            logger.info(f"   📈 Completeness rates: {completeness_stats}")
        
        return results
    
    def validate_column_preservation(self, df):
        """Validate that columns from all source files were preserved"""
        
        logger.info(f"\n📋 VALIDATING COLUMN PRESERVATION...")
        
        # Expected columns based on our analysis
        expected_core_columns = [
            'Property Address', 'Property Name', 'Land Area (AC)', 'Land Area (SF)',
            'Property Type', 'Market Name', 'City', 'State', 'For Sale Price',
            'County Name', 'Zip', 'Zoning'
        ]
        
        # Check for core columns
        missing_core = [col for col in expected_core_columns if col not in df.columns]
        
        # Check for metadata columns added during consolidation
        metadata_columns = [col for col in df.columns if any(
            keyword in col for keyword in ['Source_', 'Consolidation_', 'Data_Completeness', 'Record_Quality']
        )]
        
        checks = {
            'core_columns_preserved': len(missing_core) == 0,
            'has_metadata_columns': len(metadata_columns) >= 5,
            'reasonable_total_columns': 50 <= len(df.columns) <= 100,
            'no_empty_column_names': not any(pd.isna(col) or str(col).strip() == '' for col in df.columns)
        }
        
        results = {
            'status': all(checks.values()),
            'checks': checks,
            'details': {
                'total_columns': len(df.columns),
                'missing_core_columns': missing_core,
                'metadata_columns_count': len(metadata_columns),
                'sample_columns': list(df.columns)[:10]
            }
        }
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            logger.info(f"   {status} {check}: {passed}")
        
        logger.info(f"   📊 Total columns: {len(df.columns)}")
        logger.info(f"   📋 Metadata columns: {len(metadata_columns)}")
        
        return results
    
    def validate_source_tracking(self, df):
        """Validate source file tracking functionality"""
        
        logger.info(f"\n📁 VALIDATING SOURCE TRACKING...")
        
        source_file_col = None
        for col in df.columns:
            if 'Source_File' in col:
                source_file_col = col
                break
        
        checks = {
            'has_source_tracking': source_file_col is not None,
            'all_rows_have_source': True,
            'reasonable_source_count': True,
            'source_files_named_correctly': True
        }
        
        details = {
            'source_column': source_file_col,
            'unique_sources': [],
            'source_distribution': {}
        }
        
        if source_file_col:
            source_values = df[source_file_col]
            checks['all_rows_have_source'] = source_values.notna().all()
            
            unique_sources = source_values.dropna().unique()
            details['unique_sources'] = list(unique_sources)
            details['source_distribution'] = source_values.value_counts().to_dict()
            
            # Should have sources from CostarExport-8 through CostarExport-15
            checks['reasonable_source_count'] = 6 <= len(unique_sources) <= 10
            checks['source_files_named_correctly'] = all(
                'CostarExport-' in str(source) or 'Combined' in str(source)
                for source in unique_sources
            )
        
        results = {
            'status': all(checks.values()),
            'checks': checks,
            'details': details
        }
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            logger.info(f"   {status} {check}: {passed}")
        
        if details['unique_sources']:
            logger.info(f"   📊 Sources found: {len(details['unique_sources'])}")
            logger.info(f"   📁 Source files: {details['unique_sources'][:5]}...")
        
        return results
    
    def validate_deduplication(self, df):
        """Validate deduplication effectiveness"""
        
        logger.info(f"\n🧹 VALIDATING DEDUPLICATION...")
        
        # Check for remaining duplicates
        duplicate_check_cols = ['Property Name', 'Property Address']
        available_cols = [col for col in duplicate_check_cols if col in df.columns]
        
        remaining_duplicates = 0
        duplicate_examples = []
        
        if len(available_cols) >= 2:
            # Create composite key for duplicate checking
            composite_key = df[available_cols[0]].astype(str).str.strip().str.lower() + '|' + df[available_cols[1]].astype(str).str.strip().str.lower()
            duplicates_mask = composite_key.duplicated(keep=False)
            remaining_duplicates = duplicates_mask.sum()
            
            if remaining_duplicates > 0:
                duplicate_examples = df[duplicates_mask][available_cols].head(5).to_dict('records')
        
        checks = {
            'can_check_duplicates': len(available_cols) >= 2,
            'low_duplicate_rate': remaining_duplicates < len(df) * 0.02,  # Less than 2%
            'has_unique_properties': df['Property Name'].nunique() > len(df) * 0.3 if 'Property Name' in df.columns else True
        }
        
        results = {
            'status': all(checks.values()),
            'checks': checks,
            'details': {
                'remaining_duplicates': remaining_duplicates,
                'duplicate_rate_percent': round((remaining_duplicates / len(df)) * 100, 2) if len(df) > 0 else 0,
                'unique_properties': df['Property Name'].nunique() if 'Property Name' in df.columns else 0,
                'duplicate_examples': duplicate_examples
            }
        }
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            logger.info(f"   {status} {check}: {passed}")
        
        logger.info(f"   📊 Remaining duplicates: {remaining_duplicates}")
        logger.info(f"   📈 Duplicate rate: {results['details']['duplicate_rate_percent']}%")
        
        return results
    
    def validate_business_logic(self, df):
        """Validate business logic and data reasonableness"""
        
        logger.info(f"\n💼 VALIDATING BUSINESS LOGIC...")
        
        # Check price ranges
        price_stats = {}
        if 'For Sale Price' in df.columns:
            prices = pd.to_numeric(df['For Sale Price'], errors='coerce').dropna()
            if len(prices) > 0:
                price_stats = {
                    'min_price': float(prices.min()),
                    'max_price': float(prices.max()),
                    'median_price': float(prices.median()),
                    'count_with_price': len(prices)
                }
        
        # Check geographic distribution
        geographic_stats = {}
        if 'State' in df.columns:
            geographic_stats['states'] = df['State'].value_counts().to_dict()
        if 'City' in df.columns:
            geographic_stats['unique_cities'] = df['City'].nunique()
        
        checks = {
            'has_price_data': len(price_stats) > 0,
            'reasonable_price_ranges': (
                price_stats.get('min_price', 0) >= 10000 and 
                price_stats.get('max_price', 0) <= 50000000
            ) if price_stats else True,
            'geographic_diversity': geographic_stats.get('unique_cities', 0) > 10,
            'primarily_california': (
                geographic_stats.get('states', {}).get('CA', 0) > len(df) * 0.8
            ) if geographic_stats else True
        }
        
        results = {
            'status': all(checks.values()),
            'checks': checks,
            'details': {
                'price_stats': price_stats,
                'geographic_stats': geographic_stats
            }
        }
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            logger.info(f"   {status} {check}: {passed}")
        
        if price_stats:
            logger.info(f"   💰 Price range: ${price_stats['min_price']:,.0f} - ${price_stats['max_price']:,.0f}")
            logger.info(f"   📊 Median price: ${price_stats['median_price']:,.0f}")
        
        return results
    
    def generate_validation_report(self, validation_results, stats):
        """Generate comprehensive validation report"""
        
        logger.info(f"\n📄 COMPREHENSIVE VALIDATION REPORT")
        logger.info("=" * 60)
        
        # Overall summary
        passed_categories = sum(1 for result in validation_results.values() if result.get('status', False))
        total_categories = len(validation_results)
        
        logger.info(f"📊 VALIDATION SUMMARY:")
        logger.info(f"   ✅ Passed categories: {passed_categories}/{total_categories}")
        logger.info(f"   📈 Success rate: {(passed_categories/total_categories)*100:.1f}%")
        
        # Category-by-category results
        for category, result in validation_results.items():
            status = "✅ PASSED" if result.get('status', False) else "⚠️  ISSUES"
            logger.info(f"   {status}: {category.replace('_', ' ').title()}")
        
        # Key metrics
        if stats:
            logger.info(f"\n📈 KEY METRICS:")
            final_stats = stats.get('final_dataset', {})
            consolidation_stats = stats.get('consolidation_impact', {})
            
            logger.info(f"   🏠 Unique properties: {final_stats.get('unique_properties', 'N/A'):,}")
            logger.info(f"   📉 Deduplication rate: {consolidation_stats.get('deduplication_rate', 'N/A')}%")
            logger.info(f"   ⭐ Data completeness: {consolidation_stats.get('data_completeness_avg', 'N/A')}%")
        
        # Save detailed report
        report_file = self.sites_path / "CoStar_Validation_Report.json"
        full_report = {
            'validation_timestamp': pd.Timestamp.now().isoformat(),
            'overall_status': passed_categories == total_categories,
            'categories_passed': passed_categories,
            'total_categories': total_categories,
            'detailed_results': validation_results,
            'consolidation_stats': stats
        }
        
        with open(report_file, 'w') as f:
            json.dump(full_report, f, indent=2, default=str)
        
        logger.info(f"\n📄 Detailed validation report saved: {report_file.name}")

def main():
    validator = CoStarValidator()
    
    print("🔍 CoStar Consolidation Validation Tool")
    print("Validating CombinedCostarExportUpdated.xlsx...")
    print()
    
    success = validator.comprehensive_validation()
    
    if success:
        print(f"\n🎉 All validations passed! Data is ready for production use.")
    else:
        print(f"\n⚠️  Some validation warnings detected. Check the detailed report.")

if __name__ == "__main__":
    main()