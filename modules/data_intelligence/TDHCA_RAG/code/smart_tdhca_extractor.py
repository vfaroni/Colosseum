#!/usr/bin/env python3
"""
Smart TDHCA Extractor with Third-Party Report Skipping

This extractor intelligently skips large third-party report sections
and focuses only on TDHCA application pages for faster processing.

Skipped sections:
- Market Studies (often 50-100 pages)
- Phase I Environmental Reports (20-50 pages)  
- Appraisals (30-80 pages)
- Property Condition Needs Assessments (PCNAs/CNAs) (20-60 pages)
- Architectural drawings and site plans (10-30 pages)
- Legal documents and certificates (10-20 pages)
"""

import PyPDF2
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentSection:
    """Represents a section of the TDHCA application"""
    start_page: int
    end_page: int
    section_type: str
    description: str
    skip: bool = False

class SmartTDHCAExtractor:
    """
    TDHCA extractor that intelligently skips third-party reports
    """
    
    def __init__(self):
        # Third-party report indicators (case-insensitive patterns)
        self.skip_patterns = {
            'market_study': [
                r'market\s+study',
                r'market\s+analysis',
                r'demographic\s+analysis',
                r'rent\s+comparability\s+study',
                r'market\s+research'
            ],
            'environmental': [
                r'phase\s+i\s+environmental',
                r'environmental\s+site\s+assessment',
                r'esa\s+report',
                r'environmental\s+assessment',
                r'phase\s+1\s+esa'
            ],
            'appraisal': [
                r'appraisal\s+report',
                r'real\s+estate\s+appraisal',
                r'property\s+valuation',
                r'appraisal\s+of\s+real\s+estate',
                r'restricted\s+appraisal'
            ],
            'pcna_cna': [
                r'property\s+condition\s+needs\s+assessment',
                r'capital\s+needs\s+assessment',
                r'pcna\s+report',
                r'cna\s+report',
                r'physical\s+condition\s+assessment'
            ],
            'architectural': [
                r'architectural\s+drawings',
                r'site\s+plans',
                r'floor\s+plans',
                r'construction\s+drawings',
                r'architectural\s+plans'
            ],
            'legal': [
                r'deed\s+of\s+trust',
                r'purchase\s+agreement',
                r'title\s+commitment',
                r'legal\s+description',
                r'survey\s+report'
            ],
            'engineering': [
                r'geotechnical\s+report',
                r'soil\s+analysis',
                r'engineering\s+report',
                r'civil\s+engineering',
                r'structural\s+engineering'
            ]
        }
        
        # TDHCA application section indicators (these we WANT to process)
        self.keep_patterns = [
            r'tdhca\s+application',
            r'multifamily\s+uniform\s+application',
            r'tab\s+\d+',
            r'section\s+[a-z]\d*',
            r'development\s+budget',
            r'rent\s+schedule',
            r'unit\s+mix',
            r'site\s+information',
            r'developer\s+information',
            r'general\s+information'
        ]
    
    def analyze_pdf_structure(self, pdf_path: Path) -> List[DocumentSection]:
        """
        Analyze PDF structure and identify sections to skip or process
        """
        sections = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                logger.info(f"Analyzing {total_pages} pages for document structure...")
                
                current_section = None
                skip_until_page = 0
                
                for page_num in range(min(total_pages, 200)):  # Analyze first 200 pages
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text().lower()
                        
                        # Skip if we're in the middle of a third-party report
                        if page_num < skip_until_page:
                            continue
                        
                        # Check if this page starts a third-party report
                        skip_section = self._identify_skip_section(page_text, page_num)
                        
                        if skip_section:
                            # Estimate section length based on type
                            section_length = self._estimate_section_length(skip_section['type'])
                            end_page = min(page_num + section_length, total_pages)
                            
                            sections.append(DocumentSection(
                                start_page=page_num,
                                end_page=end_page,
                                section_type=skip_section['type'],
                                description=skip_section['description'],
                                skip=True
                            ))
                            
                            skip_until_page = end_page
                            logger.info(f"📄 Found {skip_section['type']} at page {page_num+1}, skipping to page {end_page+1}")
                        
                        # Check if this is a TDHCA application section
                        elif self._is_tdhca_section(page_text):
                            # Look ahead to find the end of this section
                            section_end = self._find_section_end(pdf_reader, page_num, total_pages)
                            
                            sections.append(DocumentSection(
                                start_page=page_num,
                                end_page=section_end,
                                section_type='tdhca_application',
                                description='TDHCA Application Section',
                                skip=False
                            ))
                            
                            logger.info(f"✅ Found TDHCA section at page {page_num+1}-{section_end+1}")
                    
                    except Exception as e:
                        logger.warning(f"Error analyzing page {page_num+1}: {e}")
                        continue
                
                # Fill in any gaps as potential TDHCA sections
                sections = self._fill_gaps(sections, total_pages)
                
        except Exception as e:
            logger.error(f"Error analyzing PDF structure: {e}")
            # Fallback: treat everything as TDHCA sections
            sections = [DocumentSection(0, total_pages, 'tdhca_application', 'Full Document', False)]
        
        return sections
    
    def _identify_skip_section(self, page_text: str, page_num: int) -> Dict[str, str]:
        """
        Identify if a page starts a third-party report section
        """
        for section_type, patterns in self.skip_patterns.items():
            for pattern in patterns:
                if re.search(pattern, page_text, re.IGNORECASE):
                    return {
                        'type': section_type,
                        'description': f"{section_type.replace('_', ' ').title()} Report"
                    }
        return None
    
    def _is_tdhca_section(self, page_text: str) -> bool:
        """
        Check if page contains TDHCA application content
        """
        for pattern in self.keep_patterns:
            if re.search(pattern, page_text, re.IGNORECASE):
                return True
        return False
    
    def _estimate_section_length(self, section_type: str) -> int:
        """
        Estimate typical length of different report types
        """
        lengths = {
            'market_study': 60,      # Market studies are often 50-80 pages
            'environmental': 35,     # Phase I ESAs are typically 20-50 pages
            'appraisal': 45,        # Appraisals are usually 30-60 pages
            'pcna_cna': 40,         # PCNAs/CNAs are typically 20-60 pages
            'architectural': 20,     # Drawing sets are usually 10-30 pages
            'legal': 15,            # Legal docs are usually 5-20 pages
            'engineering': 25       # Engineering reports are usually 15-35 pages
        }
        return lengths.get(section_type, 20)
    
    def _find_section_end(self, pdf_reader: PyPDF2.PdfReader, start_page: int, total_pages: int) -> int:
        """
        Find where a TDHCA section ends (typically 5-15 pages)
        """
        max_section_length = 15  # TDHCA sections are usually shorter
        end_page = min(start_page + max_section_length, total_pages)
        
        # Look for next major section break
        for page_num in range(start_page + 3, end_page):
            try:
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text().lower()
                
                # Check if we hit a third-party report
                if self._identify_skip_section(page_text, page_num):
                    return page_num
                    
            except Exception:
                continue
        
        return end_page
    
    def _fill_gaps(self, sections: List[DocumentSection], total_pages: int) -> List[DocumentSection]:
        """
        Fill gaps between identified sections as potential TDHCA content
        """
        if not sections:
            return [DocumentSection(0, total_pages, 'tdhca_application', 'Full Document', False)]
        
        filled_sections = []
        last_end = 0
        
        for section in sorted(sections, key=lambda x: x.start_page):
            # Add gap before this section as TDHCA content
            if section.start_page > last_end:
                filled_sections.append(DocumentSection(
                    start_page=last_end,
                    end_page=section.start_page,
                    section_type='tdhca_application',
                    description='TDHCA Application Content',
                    skip=False
                ))
            
            filled_sections.append(section)
            last_end = section.end_page
        
        # Add remaining pages as TDHCA content
        if last_end < total_pages:
            filled_sections.append(DocumentSection(
                start_page=last_end,
                end_page=total_pages,
                section_type='tdhca_application',
                description='TDHCA Application Content',
                skip=False
            ))
        
        return filled_sections
    
    def extract_smart_text(self, pdf_path: Path) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text only from TDHCA application sections, skipping third-party reports
        """
        sections = self.analyze_pdf_structure(pdf_path)
        
        extraction_stats = {
            'total_pages': 0,
            'processed_pages': 0,
            'skipped_pages': 0,
            'sections_processed': 0,
            'sections_skipped': 0
        }
        
        extracted_text = ""
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                extraction_stats['total_pages'] = len(pdf_reader.pages)
                
                for section in sections:
                    if section.skip:
                        extraction_stats['skipped_pages'] += (section.end_page - section.start_page)
                        extraction_stats['sections_skipped'] += 1
                        logger.info(f"⏭️  Skipping {section.description} (pages {section.start_page+1}-{section.end_page})")
                        continue
                    
                    # Extract text from this TDHCA section
                    logger.info(f"📖 Processing {section.description} (pages {section.start_page+1}-{section.end_page})")
                    
                    for page_num in range(section.start_page, min(section.end_page, len(pdf_reader.pages))):
                        try:
                            page = pdf_reader.pages[page_num]
                            page_text = page.extract_text()
                            if page_text.strip():
                                extracted_text += f"\n--- Page {page_num+1} ---\n{page_text}"
                                extraction_stats['processed_pages'] += 1
                        except Exception as e:
                            logger.warning(f"Error extracting page {page_num+1}: {e}")
                    
                    extraction_stats['sections_processed'] += 1
        
        except Exception as e:
            logger.error(f"Error during smart extraction: {e}")
            return "", extraction_stats
        
        logger.info(f"🎯 Smart extraction complete: {extraction_stats['processed_pages']}/{extraction_stats['total_pages']} pages processed")
        logger.info(f"   Skipped {extraction_stats['skipped_pages']} pages in {extraction_stats['sections_skipped']} third-party reports")
        
        return extracted_text, extraction_stats


def test_smart_extraction():
    """Test the smart extraction on Estates at Ferguson"""
    
    test_file = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_2023_Applications/Dallas_Fort_Worth/TDHCA_23461_Estates_at_Ferguson.pdf")
    
    if not test_file.exists():
        logger.error(f"Test file not found: {test_file}")
        return
    
    logger.info(f"🧪 Testing smart extraction on: {test_file.name}")
    
    extractor = SmartTDHCAExtractor()
    
    # Analyze structure first
    logger.info("📋 Analyzing document structure...")
    sections = extractor.analyze_pdf_structure(test_file)
    
    print(f"\n📊 DOCUMENT STRUCTURE ANALYSIS:")
    print(f"Found {len(sections)} sections:")
    
    total_pages = 0
    skipped_pages = 0
    
    for i, section in enumerate(sections, 1):
        pages = section.end_page - section.start_page
        total_pages += pages
        status = "SKIP" if section.skip else "PROCESS"
        
        if section.skip:
            skipped_pages += pages
        
        print(f"{i:2d}. Pages {section.start_page+1:3d}-{section.end_page:3d} ({pages:2d} pages) | {status:7s} | {section.description}")
    
    print(f"\n📈 EFFICIENCY GAIN:")
    print(f"Total pages: {total_pages}")
    print(f"Pages to skip: {skipped_pages}")
    print(f"Pages to process: {total_pages - skipped_pages}")
    print(f"Time savings: ~{skipped_pages/total_pages*100:.1f}%")
    
    # Extract text using smart method
    logger.info("\n🚀 Performing smart extraction...")
    text, stats = extractor.extract_smart_text(test_file)
    
    print(f"\n✅ EXTRACTION RESULTS:")
    print(f"Total pages in PDF: {stats['total_pages']}")
    print(f"Pages processed: {stats['processed_pages']}")
    print(f"Pages skipped: {stats['skipped_pages']}")
    print(f"Processing efficiency: {stats['processed_pages']/(stats['total_pages']) * 100:.1f}%")
    
    # Show sample of extracted text
    if text:
        print(f"\n📝 SAMPLE EXTRACTED TEXT (first 1000 chars):")
        print("=" * 60)
        print(text[:1000] + "..." if len(text) > 1000 else text)
        print("=" * 60)
        
        # Save extracted text for further processing
        output_file = Path("smart_extracted_text_estates_ferguson.txt")
        with open(output_file, 'w') as f:
            f.write(text)
        logger.info(f"💾 Smart extracted text saved to: {output_file}")
    else:
        logger.error("❌ No text extracted!")


if __name__ == "__main__":
    test_smart_extraction()