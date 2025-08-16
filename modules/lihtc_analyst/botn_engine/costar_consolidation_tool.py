#!/usr/bin/env python3
"""
CoStar Data Consolidation Tool - Merge CoStar exports 8-15 with full column preservation
Creates CombinedCostarExportUpdated.xlsx with enhanced data integrity
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoStarConsolidator:
    """Consolidate multiple CoStar export files while preserving all columns"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.sites_path = self.base_path / "Sites"
        self.consolidated_data = None
        self.consolidation_stats = {}
        
    def consolidate_costar_exports(self, export_range=(8, 16)):
        """Consolidate CoStar export files from range (inclusive start, exclusive end)"""
        
        logger.info("🚀 COSTAR DATA CONSOLIDATION - FULL COLUMN PRESERVATION")
        logger.info("=" * 70)
        
        # Files to consolidate
        files_to_process = []
        for i in range(export_range[0], export_range[1]):
            filename = f"CostarExport-{i}.xlsx"
            file_path = self.sites_path / filename
            if file_path.exists():
                files_to_process.append(file_path)
                logger.info(f"✅ Found: {filename}")
            else:
                logger.warning(f"⚠️  Missing: {filename}")
        
        if not files_to_process:
            logger.error("❌ No CoStar export files found!")
            return None
        
        logger.info(f"\n📊 Processing {len(files_to_process)} CoStar export files...")
        
        # Load and consolidate all files
        all_dataframes = []
        
        for i, file_path in enumerate(files_to_process, 1):
            logger.info(f"\n📝 Loading {i}/{len(files_to_process)}: {file_path.name}")
            
            try:
                df = pd.read_excel(file_path, sheet_name=0)
                
                # Add source tracking
                df['Source_File'] = file_path.name
                df['Source_File_Number'] = int(file_path.name.split('-')[1].split('.')[0])
                df['Load_Timestamp'] = datetime.now().isoformat()
                
                # Add row-level metadata
                df['Original_Row_Index'] = df.index
                df['File_Row_Count'] = len(df)
                
                all_dataframes.append(df)
                
                logger.info(f"   ✅ Loaded: {len(df)} rows, {len(df.columns)} columns")
                
            except Exception as e:
                logger.error(f"   ❌ Error loading {file_path.name}: {str(e)}")
        
        if not all_dataframes:
            logger.error("❌ No data could be loaded!")
            return None
        
        # Perform smart consolidation
        logger.info(f"\n🔄 CONSOLIDATING DATA...")
        consolidated_df = self.smart_consolidate_dataframes(all_dataframes)
        
        # Enhanced deduplication
        logger.info(f"\n🧹 REMOVING DUPLICATES WITH SMART LOGIC...")
        final_df = self.smart_deduplication(consolidated_df)
        
        # Add consolidation metadata
        final_df = self.add_consolidation_metadata(final_df)
        
        self.consolidated_data = final_df
        
        # Generate consolidation statistics
        self.generate_consolidation_stats(all_dataframes, final_df)
        
        logger.info(f"\n✅ CONSOLIDATION COMPLETE!")
        logger.info(f"   📊 Final dataset: {len(final_df)} rows × {len(final_df.columns)} columns")
        
        return final_df
    
    def smart_consolidate_dataframes(self, dataframes):
        """Smart consolidation using outer join to preserve all columns"""
        
        logger.info("   🔗 Using outer join to preserve ALL columns...")
        
        # Use concat with outer join to preserve all columns
        consolidated = pd.concat(dataframes, ignore_index=True, sort=False)
        
        # Fill source tracking for any missing values
        consolidated['Source_File'] = consolidated['Source_File'].fillna('Unknown')
        consolidated['Source_File_Number'] = consolidated['Source_File_Number'].fillna(0)
        
        logger.info(f"   ✅ Consolidated: {len(consolidated)} total rows")
        logger.info(f"   📋 All columns preserved: {len(consolidated.columns)} columns")
        
        return consolidated
    
    def smart_deduplication(self, df):
        """Smart deduplication with priority logic"""
        
        logger.info("   🎯 Identifying duplicates by Property Name + Address...")
        
        # Create composite key for duplicate detection
        df['_duplicate_key'] = (df['Property Name'].astype(str).str.strip().str.lower() + 
                               '|' + df['Property Address'].astype(str).str.strip().str.lower())
        
        # Identify duplicates
        duplicates_mask = df.duplicated(['_duplicate_key'], keep=False)
        duplicate_count = duplicates_mask.sum()
        
        logger.info(f"   📊 Found {duplicate_count} duplicate records")
        
        if duplicate_count > 0:
            # For duplicates, keep the one from the highest numbered source file
            # (assuming higher numbers are more recent)
            logger.info("   📈 Prioritizing records from higher-numbered source files...")
            
            # Sort by duplicate key and source file number (descending)
            df_sorted = df.sort_values(['_duplicate_key', 'Source_File_Number'], 
                                     ascending=[True, False])
            
            # Keep first occurrence (which will be from highest numbered file)
            deduplicated = df_sorted.drop_duplicates(['_duplicate_key'], keep='first')
            
            logger.info(f"   ✅ After deduplication: {len(deduplicated)} rows")
            logger.info(f"   📉 Removed {len(df) - len(deduplicated)} duplicate records")
        else:
            deduplicated = df
            logger.info("   ✅ No duplicates found - all records unique")
        
        # Remove the temporary duplicate key
        if '_duplicate_key' in deduplicated.columns:
            deduplicated = deduplicated.drop('_duplicate_key', axis=1)
        
        return deduplicated
    
    def add_consolidation_metadata(self, df):
        """Add comprehensive metadata to the consolidated dataset"""
        
        logger.info("   📋 Adding consolidation metadata...")
        
        # Add consolidation timestamp
        df['Consolidation_Timestamp'] = datetime.now().isoformat()
        df['Consolidation_Version'] = 'CombinedCostarExportUpdated_v1.0'
        
        # Add data quality indicators
        df['Has_Property_Name'] = df['Property Name'].notna() & (df['Property Name'] != '')
        df['Has_Address'] = df['Property Address'].notna() & (df['Property Address'] != '')
        df['Has_Price'] = df['For Sale Price'].notna() & (df['For Sale Price'] > 0)
        
        # Calculate data completeness score (0-100)
        critical_fields = ['Property Name', 'Property Address', 'City', 'State', 'For Sale Price']
        
        completeness_scores = []
        for _, row in df.iterrows():
            filled_fields = sum(1 for field in critical_fields if pd.notna(row.get(field)) and str(row.get(field)).strip() != '')
            score = (filled_fields / len(critical_fields)) * 100
            completeness_scores.append(round(score, 1))
        
        df['Data_Completeness_Score'] = completeness_scores
        
        # Add record quality classification
        df['Record_Quality'] = df['Data_Completeness_Score'].apply(lambda x: 
            'Excellent' if x >= 90 else
            'Good' if x >= 70 else
            'Fair' if x >= 50 else
            'Poor'
        )
        
        logger.info(f"   ✅ Added metadata columns for data quality tracking")
        
        return df
    
    def generate_consolidation_stats(self, original_dataframes, final_df):
        """Generate comprehensive consolidation statistics"""
        
        self.consolidation_stats = {
            'consolidation_timestamp': datetime.now().isoformat(),
            'source_files': {
                'count': len(original_dataframes),
                'total_original_rows': sum(len(df) for df in original_dataframes),
                'file_details': {}
            },
            'final_dataset': {
                'total_rows': len(final_df),
                'total_columns': len(final_df.columns),
                'unique_properties': final_df['Property Name'].nunique(),
                'data_quality_distribution': final_df['Record_Quality'].value_counts().to_dict()
            },
            'consolidation_impact': {
                'rows_removed': sum(len(df) for df in original_dataframes) - len(final_df),
                'deduplication_rate': round((sum(len(df) for df in original_dataframes) - len(final_df)) / sum(len(df) for df in original_dataframes) * 100, 2),
                'data_completeness_avg': round(final_df['Data_Completeness_Score'].mean(), 2)
            }
        }
        
        # Add per-file details
        for df in original_dataframes:
            source_file = df['Source_File'].iloc[0]
            self.consolidation_stats['source_files']['file_details'][source_file] = {
                'rows': len(df),
                'columns': len(df.columns),
                'unique_properties': df['Property Name'].nunique()
            }
        
        logger.info(f"\n📈 CONSOLIDATION STATISTICS:")
        logger.info(f"   📊 Original total rows: {self.consolidation_stats['source_files']['total_original_rows']:,}")
        logger.info(f"   📊 Final rows: {self.consolidation_stats['final_dataset']['total_rows']:,}")
        logger.info(f"   📉 Rows removed: {self.consolidation_stats['consolidation_impact']['rows_removed']:,}")
        logger.info(f"   📈 Deduplication rate: {self.consolidation_stats['consolidation_impact']['deduplication_rate']}%")
        logger.info(f"   🏠 Unique properties: {self.consolidation_stats['final_dataset']['unique_properties']:,}")
        logger.info(f"   ⭐ Avg data completeness: {self.consolidation_stats['consolidation_impact']['data_completeness_avg']}%")
    
    def save_consolidated_data(self, filename="CombinedCostarExportUpdated.xlsx"):
        """Save the consolidated data to Excel file"""
        
        if self.consolidated_data is None:
            logger.error("❌ No consolidated data to save!")
            return None
        
        output_path = self.sites_path / filename
        
        logger.info(f"\n💾 SAVING CONSOLIDATED DATA...")
        logger.info(f"   📁 Output file: {filename}")
        
        try:
            # Save with multiple sheets for better organization
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                
                # Main consolidated data
                self.consolidated_data.to_excel(writer, sheet_name='Consolidated_Data', index=False)
                
                # Data quality summary
                quality_summary = self.consolidated_data.groupby(['Record_Quality', 'Source_File']).size().unstack(fill_value=0)
                quality_summary.to_excel(writer, sheet_name='Quality_Summary')
                
                # Source file statistics
                source_stats = pd.DataFrame([
                    {
                        'Source_File': source_file,
                        'Row_Count': details['rows'],
                        'Column_Count': details['columns'],
                        'Unique_Properties': details['unique_properties']
                    }
                    for source_file, details in self.consolidation_stats['source_files']['file_details'].items()
                ])
                source_stats.to_excel(writer, sheet_name='Source_File_Stats', index=False)
            
            logger.info(f"   ✅ Successfully saved: {output_path}")
            logger.info(f"   📊 File size: {round(output_path.stat().st_size / (1024*1024), 2)} MB")
            
            # Save consolidation stats as JSON
            stats_file = self.sites_path / f"{filename.split('.')[0]}_stats.json"
            with open(stats_file, 'w') as f:
                json.dump(self.consolidation_stats, f, indent=2, default=str)
            
            logger.info(f"   📄 Statistics saved: {stats_file.name}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error saving consolidated data: {str(e)}")
            return None
    
    def validate_consolidated_data(self):
        """Comprehensive validation of consolidated data"""
        
        if self.consolidated_data is None:
            logger.error("❌ No consolidated data to validate!")
            return False
        
        logger.info(f"\n🔍 VALIDATING CONSOLIDATED DATA...")
        
        validation_results = {
            'total_rows': len(self.consolidated_data),
            'total_columns': len(self.consolidated_data.columns),
            'validation_checks': {}
        }
        
        # Check 1: Required columns present
        required_columns = ['Property Name', 'Property Address', 'For Sale Price', 'Source_File']
        missing_required = [col for col in required_columns if col not in self.consolidated_data.columns]
        
        if missing_required:
            validation_results['validation_checks']['missing_required_columns'] = missing_required
            logger.error(f"   ❌ Missing required columns: {missing_required}")
        else:
            logger.info(f"   ✅ All required columns present")
        
        # Check 2: Data quality distribution
        quality_dist = self.consolidated_data['Record_Quality'].value_counts()
        validation_results['validation_checks']['quality_distribution'] = quality_dist.to_dict()
        
        excellent_pct = (quality_dist.get('Excellent', 0) / len(self.consolidated_data)) * 100
        logger.info(f"   📊 Data quality: {excellent_pct:.1f}% excellent records")
        
        # Check 3: Source file representation
        source_dist = self.consolidated_data['Source_File'].value_counts()
        validation_results['validation_checks']['source_file_distribution'] = source_dist.to_dict()
        logger.info(f"   📁 Data from {len(source_dist)} source files")
        
        # Check 4: Duplicate detection
        duplicate_check = self.consolidated_data[['Property Name', 'Property Address']].duplicated().sum()
        validation_results['validation_checks']['remaining_duplicates'] = duplicate_check
        
        if duplicate_check > 0:
            logger.warning(f"   ⚠️  {duplicate_check} potential duplicates remaining")
        else:
            logger.info(f"   ✅ No duplicates detected")
        
        # Check 5: Data completeness
        avg_completeness = self.consolidated_data['Data_Completeness_Score'].mean()
        validation_results['validation_checks']['average_completeness'] = round(avg_completeness, 2)
        
        if avg_completeness >= 80:
            logger.info(f"   ✅ High data completeness: {avg_completeness:.1f}%")
        elif avg_completeness >= 60:
            logger.warning(f"   ⚠️  Moderate data completeness: {avg_completeness:.1f}%")
        else:
            logger.error(f"   ❌ Low data completeness: {avg_completeness:.1f}%")
        
        # Overall validation
        critical_issues = len([k for k, v in validation_results['validation_checks'].items() 
                             if isinstance(v, list) and len(v) > 0])
        
        if critical_issues == 0 and avg_completeness >= 70:
            logger.info(f"   🎉 VALIDATION PASSED: Data ready for use")
            return True
        else:
            logger.warning(f"   ⚠️  VALIDATION WARNINGS: Check data quality")
            return False

def main():
    consolidator = CoStarConsolidator()
    
    print("🚀 CoStar Data Consolidation Tool")
    print("Consolidating exports 8-15 with full column preservation...")
    print()
    
    # Consolidate the data
    consolidated_df = consolidator.consolidate_costar_exports()
    
    if consolidated_df is not None:
        # Validate the results
        consolidator.validate_consolidated_data()
        
        # Save the consolidated data
        output_file = consolidator.save_consolidated_data()
        
        if output_file:
            print(f"\n🎉 SUCCESS! CombinedCostarExportUpdated.xlsx created")
            print(f"📁 Location: {output_file}")
            print(f"📊 Final dataset: {len(consolidated_df):,} rows × {len(consolidated_df.columns)} columns")
        else:
            print(f"\n❌ Failed to save consolidated data")
    else:
        print(f"\n❌ Consolidation failed")

if __name__ == "__main__":
    main()