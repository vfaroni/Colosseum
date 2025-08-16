#!/usr/bin/env python3
"""
Quick D'Marco Comparison Matrix Generator (No Geocoding)

Creates comparison matrix without geocoding for rapid analysis.
Geocoding can be added separately.
"""

from dmarco_comparison_matrix import DMarcoComparisonMatrix
from ultimate_tdhca_extractor import UltimateTDHCAExtractor, UltimateProjectData
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class QuickDMarcoMatrix(DMarcoComparisonMatrix):
    """Quick comparison matrix without geocoding"""
    
    def process_all_applications_quick(self):
        """Extract data from all applications without geocoding"""
        
        logger.info("⚡ Quick processing all applications (no geocoding)")
        
        # Create modified extractor without geocoding
        class QuickExtractor(UltimateTDHCAExtractor):
            def process_application(self, pdf_path):
                logger.info(f"🚀 Processing {pdf_path.name} (Quick Mode)")
                
                # Extract application number
                import re
                app_match = re.search(r'(\d{5})', pdf_path.name)
                if not app_match:
                    logger.error(f"Could not extract application number from {pdf_path.name}")
                    return None
                
                app_number = app_match.group(1)
                
                # Smart extract text
                text, stats = self.smart_extract_pdf_text(pdf_path)
                if not text.strip():
                    logger.error(f"No text extracted from {pdf_path.name}")
                    return None
                
                # Extract comprehensive data WITHOUT geocoding
                project_data = self.extract_comprehensive_data(text, app_number)
                
                # Add processing statistics
                project_data.processing_notes.extend([
                    f"Quick mode: {stats['efficiency_gain']*100:.1f}% pages skipped",
                    f"Processed {stats['processed_pages']}/{stats['total_pages']} pages (no geocoding)"
                ])
                
                logger.info(f"✅ Quick extraction complete for {project_data.project_name or app_number}")
                return project_data
        
        extractor = QuickExtractor(self.base_path)
        
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
        
        logger.info(f"✅ Quick processed {len(results)}/{len(pdf_files)} applications")
        return results


def main():
    """Generate quick D'Marco comparison matrix"""
    
    base_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites"
    
    generator = QuickDMarcoMatrix(base_path)
    
    # Process all applications quickly
    projects = generator.process_all_applications_quick()
    
    if not projects:
        print("❌ No projects processed successfully")
        return
    
    print(f"✅ Quick processed {len(projects)} projects")
    
    # Export in all formats
    print("📊 Generating quick D'Marco comparison matrix...")
    exports = generator.export_all_formats(projects)
    
    print("\n🎉 QUICK D'MARCO COMPARISON MATRIX COMPLETE")
    print("=" * 60)
    print(f"📈 Excel (Multi-sheet): {exports['excel']}")
    print(f"📋 CSV (Main): {exports['csv']}")
    print(f"🔗 JSON (API Ready): {exports['json']}")
    
    print(f"\n📊 SUMMARY STATISTICS:")
    stats = exports['summary']
    print(f"Total Projects: {stats['total_projects']}")
    print(f"Note: Geocoding disabled for speed - can be added later")
    
    return exports


if __name__ == "__main__":
    main()