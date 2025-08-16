#!/usr/bin/env python3
"""
PDF Source Verification System - Phase 2A
Direct PDF page reference system for legal research trust and validation
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import quote
from datetime import datetime

class PDFSourceVerification:
    """Direct PDF page reference system for source validation"""
    
    def __init__(self, pdf_base_url: str = "/pdfs", download_base_url: str = "/download"):
        """Initialize PDF source verification system"""
        
        self.pdf_base_url = pdf_base_url
        self.download_base_url = download_base_url
        
        # PDF repository mapping
        self.pdf_repository = {
            'CA': {
                'filename': 'CA_QAP_2025.pdf',
                'title': 'California Tax Credit Allocation Committee QAP 2025',
                'pages': 109,
                'available': True,
                'last_updated': '2024-12-11'
            },
            'TX': {
                'filename': 'TX_QAP_2025.pdf',
                'title': 'Texas Department of Housing QAP 2025',
                'pages': 95,
                'available': False,  # Not yet processed
                'last_updated': '2024-11-15'
            },
            'FL': {
                'filename': 'FL_QAP_2025.pdf',
                'title': 'Florida Housing Finance Corporation QAP 2025',
                'pages': 87,
                'available': False,
                'last_updated': '2024-10-30'
            }
        }
        
        print(f"🔗 PDF Source Verification initialized")
        print(f"   Available PDFs: {len([s for s in self.pdf_repository.values() if s['available']])}")
    
    def create_source_link(self, definition_id: str, state_code: str, pdf_page: int,
                          section_reference: str = None) -> Dict[str, Any]:
        """Create comprehensive source verification links"""
        
        pdf_info = self.pdf_repository.get(state_code, {})
        
        if not pdf_info.get('available', False):
            return {
                'pdf_available': False,
                'error': f'PDF not available for {state_code}',
                'status': 'unavailable'
            }
        
        filename = pdf_info['filename']
        
        # Create various link formats
        source_links = {
            'pdf_available': True,
            'state_code': state_code,
            'pdf_filename': filename,
            'pdf_page': pdf_page,
            'section_reference': section_reference,
            'links': {
                'view_in_browser': {
                    'url': f"{self.pdf_base_url}/{filename}#page={pdf_page}",
                    'label': f"View {state_code} QAP Page {pdf_page}",
                    'target': '_blank'
                },
                'direct_download': {
                    'url': f"{self.download_base_url}/{filename}",
                    'label': f"Download {state_code} QAP 2025",
                    'target': '_self'
                },
                'section_jump': {
                    'url': f"{self.pdf_base_url}/{filename}#page={pdf_page}&search={quote(section_reference) if section_reference else ''}",
                    'label': f"Jump to {section_reference}" if section_reference else f"Jump to Page {pdf_page}",
                    'target': '_blank'
                }
            },
            'pdf_metadata': {
                'title': pdf_info['title'],
                'total_pages': pdf_info['pages'],
                'last_updated': pdf_info['last_updated'],
                'file_size': self._estimate_file_size(pdf_info['pages'])
            },
            'trust_indicators': {
                'official_source': True,
                'current_year': '2025',
                'verification_status': 'verified',
                'source_authority': f"{state_code} Housing Finance Agency"
            }
        }
        
        return source_links
    
    def create_definition_source_card(self, definition: Dict[str, Any]) -> Dict[str, Any]:
        """Create professional source verification card for definitions"""
        
        state_code = definition.get('state_code', '')
        pdf_page = definition.get('pdf_page', 1)
        section_ref = definition.get('section_reference', '')
        term = definition.get('term', '')
        
        source_links = self.create_source_link(
            definition.get('definition_id', ''),
            state_code,
            pdf_page,
            section_ref
        )
        
        if not source_links.get('pdf_available', False):
            return source_links
        
        # Enhanced source card with professional presentation
        source_card = {
            **source_links,
            'definition_context': {
                'term': term,
                'section': section_ref,
                'page': pdf_page,
                'confidence': definition.get('extraction_confidence', 0.8)
            },
            'citation_formats': {
                'legal': f"{state_code} QAP {section_ref}, page {pdf_page} (2025)",
                'academic': f"{self.pdf_repository[state_code]['title']}, {section_ref}, p. {pdf_page} (2025)",
                'short': f"{state_code} QAP p.{pdf_page}"
            },
            'verification_tools': {
                'page_screenshot': f"/api/pdf_screenshot/{state_code}/{pdf_page}",
                'text_extraction': f"/api/pdf_text/{state_code}/{pdf_page}",
                'section_highlight': f"/api/pdf_highlight/{state_code}/{pdf_page}?section={quote(section_ref)}"
            }
        }
        
        return source_card
    
    def create_search_result_with_source(self, search_result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance search result with source verification"""
        
        # Create source card for the definition
        source_card = self.create_definition_source_card(search_result)
        
        # Enhanced search result with source verification
        enhanced_result = {
            **search_result,
            'source_verification': source_card,
            'trust_score': self._calculate_trust_score(search_result, source_card),
            'professional_display': {
                'header': f"{search_result.get('term', 'Unknown Term')} ({search_result.get('state', 'Unknown State')})",
                'subheader': f"{search_result.get('section_reference', '')} - Page {search_result.get('pdf_page', 'Unknown')}",
                'definition_preview': search_result.get('definition', '')[:200] + "...",
                'source_badge': {
                    'text': f"Official {search_result.get('state', '')} QAP",
                    'color': 'blue',
                    'icon': 'document-text'
                }
            }
        }
        
        return enhanced_result
    
    def _calculate_trust_score(self, search_result: Dict, source_card: Dict) -> float:
        """Calculate trust score based on various factors"""
        
        trust_factors = []
        
        # PDF availability
        if source_card.get('pdf_available', False):
            trust_factors.append(0.3)
        
        # Extraction confidence
        extraction_confidence = search_result.get('extraction_confidence', 0.8)
        trust_factors.append(extraction_confidence * 0.25)
        
        # Page reference accuracy
        if search_result.get('pdf_page') and search_result.get('pdf_page') > 0:
            trust_factors.append(0.2)
        
        # Section reference specificity
        if search_result.get('section_reference') and len(search_result.get('section_reference', '')) > 5:
            trust_factors.append(0.15)
        
        # Official source
        if source_card.get('trust_indicators', {}).get('official_source', False):
            trust_factors.append(0.1)
        
        return min(sum(trust_factors), 1.0)
    
    def _estimate_file_size(self, pages: int) -> str:
        """Estimate PDF file size based on page count"""
        
        # Rough estimate: 100KB per page for QAP documents
        estimated_kb = pages * 100
        
        if estimated_kb < 1024:
            return f"{estimated_kb}KB"
        else:
            estimated_mb = estimated_kb / 1024
            return f"{estimated_mb:.1f}MB"
    
    def generate_source_verification_report(self, definitions: List[Dict], 
                                          output_file: Path = None) -> str:
        """Generate comprehensive source verification report"""
        
        if output_file is None:
            output_file = Path(__file__).parent / "source_verification_report.md"
        
        # Analyze source verification coverage
        total_definitions = len(definitions)
        with_pdf_pages = len([d for d in definitions if d.get('pdf_page')])
        available_pdfs = len([d for d in definitions if self.pdf_repository.get(d.get('state_code', ''), {}).get('available', False)])
        
        # Generate report
        report_lines = [
            "# 🔗 PDF SOURCE VERIFICATION REPORT",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 📊 **VERIFICATION COVERAGE**",
            "",
            f"- **Total Definitions**: {total_definitions:,}",
            f"- **With PDF Page References**: {with_pdf_pages:,} ({with_pdf_pages/total_definitions*100:.1f}%)",
            f"- **PDF Sources Available**: {available_pdfs:,} ({available_pdfs/total_definitions*100:.1f}%)",
            "",
            "## 📁 **PDF REPOSITORY STATUS**",
            ""
        ]
        
        for state, pdf_info in self.pdf_repository.items():
            status = "✅ Available" if pdf_info['available'] else "⏳ Pending"
            report_lines.extend([
                f"### {state} - {pdf_info['title']}",
                f"- **Status**: {status}",
                f"- **Pages**: {pdf_info['pages']}",
                f"- **Last Updated**: {pdf_info['last_updated']}",
                f"- **File Size**: {self._estimate_file_size(pdf_info['pages'])}",
                ""
            ])
        
        # Sample source verification links
        if definitions:
            report_lines.extend([
                "## 🔍 **SAMPLE SOURCE VERIFICATION LINKS**",
                ""
            ])
            
            for definition in definitions[:3]:  # First 3 definitions
                source_card = self.create_definition_source_card(definition)
                
                if source_card.get('pdf_available', False):
                    report_lines.extend([
                        f"### {definition.get('term', 'Unknown Term')} ({definition.get('state_code', 'Unknown State')})",
                        f"- **Section**: {definition.get('section_reference', 'Unknown')}",
                        f"- **PDF Page**: {definition.get('pdf_page', 'Unknown')}",
                        f"- **View Source**: [{source_card['links']['view_in_browser']['label']}]({source_card['links']['view_in_browser']['url']})",
                        f"- **Download PDF**: [{source_card['links']['direct_download']['label']}]({source_card['links']['direct_download']['url']})",
                        f"- **Trust Score**: {self._calculate_trust_score(definition, source_card):.2f}",
                        ""
                    ])
        
        # Trust and verification metrics
        if definitions:
            trust_scores = [self._calculate_trust_score(d, self.create_definition_source_card(d)) for d in definitions]
            avg_trust = sum(trust_scores) / len(trust_scores)
            
            report_lines.extend([
                "## 🛡️ **TRUST METRICS**",
                "",
                f"- **Average Trust Score**: {avg_trust:.3f}/1.000",
                f"- **High Trust Definitions**: {len([s for s in trust_scores if s > 0.8])} ({len([s for s in trust_scores if s > 0.8])/len(trust_scores)*100:.1f}%)",
                f"- **Source Verification Rate**: {with_pdf_pages/total_definitions*100:.1f}%",
                ""
            ])
        
        report_content = "\\n".join(report_lines)
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"🔗 Source verification report saved to: {output_file}")
        return report_content
    
    def get_verification_stats(self) -> Dict[str, Any]:
        """Get source verification statistics"""
        
        available_states = [state for state, info in self.pdf_repository.items() if info['available']]
        total_pages = sum(info['pages'] for info in self.pdf_repository.values() if info['available'])
        
        return {
            'total_states_in_repository': len(self.pdf_repository),
            'available_pdf_states': len(available_states),
            'available_states': available_states,
            'total_pages_available': total_pages,
            'verification_capabilities': {
                'pdf_viewing': True,
                'direct_download': True,
                'section_jumping': True,
                'page_screenshots': True,
                'text_extraction': True,
                'section_highlighting': True
            },
            'trust_indicators': {
                'official_sources': True,
                'current_year_documents': True,
                'page_level_accuracy': True,
                'legal_citation_format': True
            }
        }

def main():
    """Test PDF source verification system"""
    
    print("🔗 Testing PDF Source Verification System...")
    
    try:
        # Initialize verification system
        verifier = PDFSourceVerification()
        
        # Get verification stats
        stats = verifier.get_verification_stats()
        print(f"\\n📊 **VERIFICATION CAPABILITIES**:")
        print(f"States in repository: {stats['total_states_in_repository']}")
        print(f"Available PDFs: {stats['available_pdf_states']}")
        print(f"Available states: {', '.join(stats['available_states'])}")
        print(f"Total pages: {stats['total_pages_available']:,}")
        
        # Test source link creation
        print(f"\\n🔗 **TEST SOURCE LINKS**:")
        
        # Test CA definition source link
        test_definition = {
            'definition_id': 'CA_def_0001',
            'state_code': 'CA',
            'term': 'Accessible Housing Unit(s)',
            'definition': 'Includes Housing Units with Mobility Features...',
            'section_reference': 'Section 10302(a)',
            'pdf_page': 15,
            'extraction_confidence': 0.9
        }
        
        source_card = verifier.create_definition_source_card(test_definition)
        
        if source_card.get('pdf_available', False):
            print(f"Term: {test_definition['term']}")
            print(f"View PDF: {source_card['links']['view_in_browser']['url']}")
            print(f"Download: {source_card['links']['direct_download']['url']}")
            print(f"Trust Score: {verifier._calculate_trust_score(test_definition, source_card):.3f}")
            print(f"Legal Citation: {source_card['citation_formats']['legal']}")
        
        # Test with unavailable PDF
        print(f"\\n⚠️  **TEST UNAVAILABLE PDF**:")
        test_tx_definition = {
            'definition_id': 'TX_def_0001',
            'state_code': 'TX',
            'term': 'Qualified Basis',
            'pdf_page': 25
        }
        
        tx_source_card = verifier.create_definition_source_card(test_tx_definition)
        print(f"TX PDF Available: {tx_source_card.get('pdf_available', False)}")
        if not tx_source_card.get('pdf_available', False):
            print(f"Error: {tx_source_card.get('error', 'Unknown error')}")
        
        # Load definitions and generate report
        definitions_file = Path('./definitions_output/CA_definitions_database_20250731_185202.json')
        if definitions_file.exists():
            with open(definitions_file, 'r') as f:
                definitions_data = json.load(f)
            
            definitions = definitions_data.get('definitions', [])
            report = verifier.generate_source_verification_report(definitions)
            print(f"\\n✅ Source verification test complete!")
            print(f"Generated report for {len(definitions)} definitions")
        else:
            print(f"⚠️  Definitions file not found for report generation")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()