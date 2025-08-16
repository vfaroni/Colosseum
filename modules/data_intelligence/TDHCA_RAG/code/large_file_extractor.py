#!/usr/bin/env python3
"""
Large File TDHCA Extractor - Specialized for 100MB+ PDFs
Combines multiple strategies for very large files like 25449.pdf (124MB)
"""

from improved_tdhca_extractor import ImprovedTDHCAExtractor
from pathlib import Path
import time
import logging
import re

class LargeFileTDHCAExtractor(ImprovedTDHCAExtractor):
    """Enhanced extractor for very large TDHCA files with aggressive optimization"""
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
        
        # More aggressive skip patterns for large files
        self.large_file_skip_patterns = {
            'market_study': [
                r'market\s+study', r'demographic\s+analysis', r'market\s+analysis',
                r'comparable\s+properties', r'rent\s+survey', r'vacancy\s+analysis',
                r'market\s+feasibility', r'economic\s+impact', r'population\s+projections'
            ],
            'environmental': [
                r'environmental\s+report', r'phase\s+i\s+environmental',
                r'environmental\s+assessment', r'soil\s+analysis', r'contamination\s+report',
                r'hazardous\s+materials', r'environmental\s+due\s+diligence'
            ],
            'appraisal': [
                r'appraisal\s+report', r'property\s+valuation', r'comparable\s+sales',
                r'income\s+approach', r'cost\s+approach', r'sales\s+comparison',
                r'market\s+value\s+analysis'
            ],
            'architectural': [
                r'architectural\s+drawings', r'site\s+plans', r'floor\s+plans',
                r'construction\s+drawings', r'architectural\s+plans',
                r'elevation\s+drawings', r'building\s+sections', r'detail\s+drawings'
            ],
            'legal': [
                r'title\s+report', r'deed\s+restrictions', r'easements',
                r'legal\s+description', r'survey\s+report', r'zoning\s+documentation'
            ],
            'engineering': [
                r'engineering\s+report', r'structural\s+analysis', r'civil\s+engineering',
                r'mechanical\s+systems', r'electrical\s+systems', r'geotechnical\s+report'
            ],
            'financial_third_party': [
                r'audited\s+financial\s+statements', r'tax\s+returns',
                r'bank\s+statements', r'accountant\s+report', r'financial\s+audit'
            ],
            'insurance': [
                r'insurance\s+documentation', r'coverage\s+analysis',
                r'risk\s+assessment', r'liability\s+coverage'
            ]
        }
        
        # Estimated section lengths for large files (more conservative)
        self.large_file_section_lengths = {
            'market_study': 80,      # Market studies can be 60-100 pages
            'environmental': 50,     # Environmental reports 30-70 pages  
            'appraisal': 60,        # Appraisals 40-80 pages
            'architectural': 40,     # Large drawing sets 20-60 pages
            'legal': 25,            # Legal docs 10-40 pages
            'engineering': 35,       # Engineering reports 20-50 pages
            'financial_third_party': 30, # Financial docs 15-45 pages
            'insurance': 20         # Insurance docs 10-30 pages
        }
    
    def _identify_large_file_skip_section(self, page_text: str) -> dict:
        """More aggressive section identification for large files"""
        
        page_text_lower = page_text.lower()
        
        for section_type, patterns in self.large_file_skip_patterns.items():
            for pattern in patterns:
                if re.search(pattern, page_text_lower):
                    return {
                        'type': section_type,
                        'description': f'Large file skip: {section_type}',
                        'confidence': 'high'
                    }
        
        # Additional heuristics for large files
        
        # Skip pages with mostly tables and data (often third-party reports)
        if len(re.findall(r'\$[\d,]+', page_text)) > 20:  # Many dollar amounts
            return {
                'type': 'financial_third_party',
                'description': 'Dense financial data - likely third-party report',
                'confidence': 'medium'
            }
        
        # Skip pages with extensive technical specifications
        if len(re.findall(r'\d+\s*(?:sq\.?\s*ft|sf|feet)', page_text)) > 15:
            return {
                'type': 'architectural',
                'description': 'Technical specifications - likely architectural',
                'confidence': 'medium'
            }
        
        # Skip pages with legal boilerplate
        if any(term in page_text_lower for term in ['whereas', 'hereinafter', 'aforementioned', 'pursuant to']):
            if page_text_lower.count('whereas') > 3:
                return {
                    'type': 'legal',
                    'description': 'Legal boilerplate - likely legal documents',
                    'confidence': 'medium'
                }
        
        return None
    
    def _estimate_large_file_section_length(self, section_type: str) -> int:
        """More conservative section length estimates for large files"""
        return self.large_file_section_lengths.get(section_type, 25)
    
    def process_large_file(self, pdf_path: Path, timeout_minutes: int = 15) -> 'UltimateProjectData':
        """Process large file with extended timeout and aggressive skipping"""
        
        print(f"🔍 LARGE FILE PROCESSING: {pdf_path.name}")
        print(f"📏 File size: {pdf_path.stat().st_size / 1024 / 1024:.1f} MB")
        print(f"⏱️ Timeout: {timeout_minutes} minutes")
        print(f"🚀 Using aggressive skip patterns for efficiency")
        print()
        
        start_time = time.time()
        
        try:
            # First, try to get a quick page count
            with open(pdf_path, 'rb') as file:
                import PyPDF2
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)
                print(f"📄 Total pages: {total_pages}")
            
            # Estimate processing time
            estimated_minutes = total_pages * 0.1  # ~6 seconds per page
            print(f"⏱️ Estimated processing: {estimated_minutes:.1f} minutes")
            
            if estimated_minutes > timeout_minutes:
                print(f"⚠️ WARNING: Estimated time exceeds timeout!")
                print(f"   Consider increasing timeout to {estimated_minutes * 1.2:.0f} minutes")
            
            print()
            
            # Override the skip section detection for this large file
            original_method = self._identify_skip_section
            self._identify_skip_section = lambda text: self._identify_large_file_skip_section(text)
            
            # Override section length estimation
            original_length_method = self._estimate_section_length
            self._estimate_section_length = lambda section_type: self._estimate_large_file_section_length(section_type)
            
            # Process with improved extraction
            result = self.process_application_improved(pdf_path)
            
            # Restore original methods
            self._identify_skip_section = original_method
            self._estimate_section_length = original_length_method
            
            processing_time = time.time() - start_time
            print(f"⏱️ Processing completed in {processing_time/60:.1f} minutes")
            
            if result:
                result.processing_notes.append(f"Large file processing: {processing_time/60:.1f} min")
                result.processing_notes.append("Used aggressive skip patterns for efficiency")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"❌ Large file processing failed after {processing_time/60:.1f} minutes")
            print(f"Error: {str(e)[:100]}...")
            return None

def process_25449_specifically():
    """Specifically process the problematic 25449.pdf file"""
    
    file_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_Applications_Benchmarks/Houston_Priority_1/TDHCA_25449_Enclave_on_Louetta/25449.pdf"
    
    print("🎯 TARGETING 25449.pdf - ENCLAVE ON LOUETTA")
    print("=" * 60)
    print("124MB PDF - Using specialized large file processing")
    print()
    
    # Initialize large file extractor
    extractor = LargeFileTDHCAExtractor("")
    
    # Process with extended timeout (20 minutes)
    result = extractor.process_large_file(Path(file_path), timeout_minutes=20)
    
    if result:
        print("✅ SUCCESS! Data extracted from 25449.pdf")
        print(f"📋 Project Name: '{result.project_name}'")
        print(f"📍 Address: {result.street_address}, {result.city} {result.zip_code}")
        print(f"🏛️ County: {result.county}")
        print(f"🏢 Units: {result.total_units}")
        print(f"📊 Confidence: {result.confidence_scores.get('overall', 0):.2f}")
        
        # Save individual result
        import json
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"25449_recovery_result_{timestamp}.json"
        
        result_data = {
            'filename': '25449.pdf',
            'project_name': result.project_name,
            'street_address': result.street_address,
            'city': result.city,
            'zip_code': result.zip_code,
            'county': result.county,
            'total_units': result.total_units,
            'developer_name': result.developer_name,
            'urban_rural': result.urban_rural,
            'latitude': result.latitude,
            'longitude': result.longitude,
            'confidence_overall': result.confidence_scores.get('overall', 0),
            'processing_notes': result.processing_notes,
            'processing_success': True
        }
        
        with open(output_file, 'w') as f:
            json.dump(result_data, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {output_file}")
        
        return result
    else:
        print("❌ STILL FAILED - Even with large file processing")
        print("This file may have fundamental corruption or require manual inspection")
        return None

if __name__ == "__main__":
    process_25449_specifically()