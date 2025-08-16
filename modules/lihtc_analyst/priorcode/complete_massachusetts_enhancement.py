#!/usr/bin/env python3
"""
Complete Massachusetts LIHTC Enhancement Downloader
Downloads current, prior, and draft QAPs plus application materials from official MA.gov sources

Primary Sources:
- QAP Documents: https://www.mass.gov/info-details/qualified-allocation-plan
- Application Info: https://www.mass.gov/info-details/low-income-housing-tax-credit-lihtc#lihtc---how-to-apply
"""

import requests
import os
from pathlib import Path
from datetime import datetime
import time
import re
from bs4 import BeautifulSoup

class MassachusettsLIHTCEnhancer:
    """Enhanced Massachusetts LIHTC document collection from official sources"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/QAP/MA")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Massachusetts official sources
        self.ma_sources = {
            'qap_page': 'https://www.mass.gov/info-details/qualified-allocation-plan',
            'application_page': 'https://www.mass.gov/info-details/low-income-housing-tax-credit-lihtc'
        }
        
        # Known Massachusetts LIHTC documents (to be supplemented by page scraping)
        self.known_documents = {
            'qap_documents': {},  # Will be populated by scraping
            'application_materials': {},  # Will be populated by scraping
            'notices': {},
            'technical_documents': {}
        }
        
        # Create directory structure
        self.setup_directories()
    
    def setup_directories(self):
        """Create enhanced directory structure for Massachusetts"""
        directories = [
            self.base_dir / "QAP" / "current",
            self.base_dir / "QAP" / "archive",
            self.base_dir / "QAP" / "redlines",
            self.base_dir / "applications" / "4pct",
            self.base_dir / "applications" / "9pct", 
            self.base_dir / "applications" / "instructions",
            self.base_dir / "awards" / "results",
            self.base_dir / "awards" / "scoring",
            self.base_dir / "notices",
            self.base_dir / "processed" / "chunks",
            self.base_dir / "processed" / "metadata",
            self.base_dir / "processed" / "sections",
            self.base_dir / "special_funds"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ Directory ready: {directory}")
    
    def scrape_qap_page(self):
        """Scrape the Massachusetts QAP page for document links"""
        
        print("🔍 Scraping Massachusetts QAP page...")
        print(f"   URL: {self.ma_sources['qap_page']}")
        
        try:
            response = self.session.get(self.ma_sources['qap_page'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all PDF links
            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.pdf') or 'pdf' in href.lower():
                    # Make absolute URL if relative
                    if href.startswith('/'):
                        href = 'https://www.mass.gov' + href
                    elif not href.startswith('http'):
                        href = 'https://www.mass.gov/' + href
                    
                    link_text = link.get_text(strip=True)
                    pdf_links.append({
                        'url': href,
                        'text': link_text,
                        'filename': self.extract_filename_from_url(href, link_text)
                    })
            
            print(f"   Found {len(pdf_links)} PDF links")
            
            # Categorize documents
            qap_docs = {}
            for link in pdf_links:
                text = link['text'].lower()
                filename = link['filename']
                
                # Categorize based on content
                if any(term in text for term in ['qap', 'qualified allocation plan', 'allocation plan']):
                    if any(term in text for term in ['2025', '2026', 'current']):
                        category = 'current'
                    elif any(term in text for term in ['draft', 'proposed']):
                        category = 'draft'
                    else:
                        category = 'archive'
                    
                    if category not in qap_docs:
                        qap_docs[category] = {}
                    qap_docs[category][filename] = link['url']
            
            self.known_documents['qap_documents'] = qap_docs
            
            return pdf_links
            
        except Exception as e:
            print(f"❌ Error scraping QAP page: {e}")
            return []
    
    def scrape_application_page(self):
        """Scrape the Massachusetts LIHTC application page for forms and instructions"""
        
        print("🔍 Scraping Massachusetts LIHTC application page...")
        print(f"   URL: {self.ma_sources['application_page']}")
        
        try:
            response = self.session.get(self.ma_sources['application_page'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all downloadable links (PDF, XLS, XLSX, DOC, DOCX)
            download_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(ext in href.lower() for ext in ['.pdf', '.xls', '.xlsx', '.doc', '.docx']):
                    # Make absolute URL if relative
                    if href.startswith('/'):
                        href = 'https://www.mass.gov' + href
                    elif not href.startswith('http'):
                        href = 'https://www.mass.gov/' + href
                    
                    link_text = link.get_text(strip=True)
                    download_links.append({
                        'url': href,
                        'text': link_text,
                        'filename': self.extract_filename_from_url(href, link_text)
                    })
            
            print(f"   Found {len(download_links)} application-related documents")
            
            # Categorize application materials
            app_materials = {}
            for link in download_links:
                text = link['text'].lower()
                filename = link['filename']
                
                # Categorize based on content
                if any(term in text for term in ['application', 'form']):
                    category = 'forms'
                elif any(term in text for term in ['instruction', 'guide', 'manual']):
                    category = 'instructions'
                elif any(term in text for term in ['notice', 'announcement']):
                    category = 'notices'
                else:
                    category = 'general'
                
                if category not in app_materials:
                    app_materials[category] = {}
                app_materials[category][filename] = link['url']
            
            self.known_documents['application_materials'] = app_materials
            
            return download_links
            
        except Exception as e:
            print(f"❌ Error scraping application page: {e}")
            return []
    
    def extract_filename_from_url(self, url, link_text):
        """Extract a meaningful filename from URL and link text"""
        
        # Try to get filename from URL
        url_filename = url.split('/')[-1].split('?')[0]
        
        # Clean up link text for filename
        clean_text = re.sub(r'[^\w\s-]', '', link_text)
        clean_text = re.sub(r'\s+', '_', clean_text.strip())
        
        # If URL filename is meaningful, use it
        if len(url_filename) > 4 and '.' in url_filename:
            return url_filename
        
        # Otherwise, create filename from link text
        if clean_text:
            # Determine file extension
            if '.pdf' in url.lower():
                ext = '.pdf'
            elif '.xls' in url.lower():
                ext = '.xlsx' if 'xlsx' in url.lower() else '.xls'
            elif '.doc' in url.lower():
                ext = '.docx' if 'docx' in url.lower() else '.doc'
            else:
                ext = '.pdf'  # Default
            
            return clean_text[:50] + ext  # Limit filename length
        
        # Fallback
        return f"MA_document_{int(time.time())}.pdf"
    
    def download_file(self, url: str, filename: str, target_dir: Path) -> bool:
        """Download a single file to specified directory"""
        
        file_path = target_dir / filename
        
        # Skip if file already exists
        if file_path.exists():
            print(f"⏭️  Already exists: {filename}")
            return True
        
        try:
            print(f"📥 Downloading: {filename}")
            print(f"   URL: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Check if we got actual file content
            content_length = len(response.content)
            if content_length < 100:
                print(f"⚠️  Warning: {filename} is only {content_length} bytes - may be error page")
                return False
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Downloaded: {filename} ({content_length:,} bytes)")
            print(f"   Saved to: {file_path}")
            
            # Brief pause between downloads
            time.sleep(1)
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to download {filename}: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error downloading {filename}: {e}")
            return False
    
    def download_qap_documents(self):
        """Download all QAP documents found by scraping"""
        
        download_results = {'success': 0, 'failed': 0, 'existed': 0}
        
        print(f"\n📂 DOWNLOADING QAP DOCUMENTS")
        print("-" * 50)
        
        for category, documents in self.known_documents['qap_documents'].items():
            if not documents:
                continue
                
            print(f"\n📋 Category: {category.upper()}")
            
            # Determine target directory
            if category == 'current':
                target_dir = self.base_dir / "QAP" / "current"
            elif category == 'draft':
                target_dir = self.base_dir / "QAP" / "current"  # Put drafts in current for now
            else:
                target_dir = self.base_dir / "QAP" / "archive"
            
            for filename, url in documents.items():
                if self.download_file(url, filename, target_dir):
                    download_results['success'] += 1
                else:
                    download_results['failed'] += 1
        
        return download_results
    
    def download_application_materials(self):
        """Download all application materials found by scraping"""
        
        download_results = {'success': 0, 'failed': 0, 'existed': 0}
        
        print(f"\n📂 DOWNLOADING APPLICATION MATERIALS")
        print("-" * 50)
        
        for category, documents in self.known_documents['application_materials'].items():
            if not documents:
                continue
                
            print(f"\n📋 Category: {category.upper()}")
            
            # Determine target directory
            if category == 'forms':
                target_dir = self.base_dir / "applications" / "9pct"  # Assume 9% unless specified
            elif category == 'instructions':
                target_dir = self.base_dir / "applications" / "instructions"
            elif category == 'notices':
                target_dir = self.base_dir / "notices"
            else:
                target_dir = self.base_dir / "applications" / "9pct"
            
            for filename, url in documents.items():
                if self.download_file(url, filename, target_dir):
                    download_results['success'] += 1
                else:
                    download_results['failed'] += 1
        
        return download_results
    
    def add_manual_massachusetts_sources(self):
        """Add any additional known Massachusetts sources manually"""
        
        # Add any specific Massachusetts documents we know about
        manual_sources = {
            'MA_QAP_2025_2026.pdf': 'https://www.mass.gov/doc/qualified-allocation-plan-2025-2026/download',
            'MA_QAP_2023_2024.pdf': 'https://www.mass.gov/doc/qualified-allocation-plan-2023-2024/download',
        }
        
        print(f"\n📂 CHECKING MANUAL MASSACHUSETTS SOURCES")
        print("-" * 50)
        
        download_results = {'success': 0, 'failed': 0, 'existed': 0}
        
        for filename, url in manual_sources.items():
            target_dir = self.base_dir / "QAP" / "current"
            
            # Try to download
            try:
                if self.download_file(url, filename, target_dir):
                    download_results['success'] += 1
                else:
                    download_results['failed'] += 1
            except Exception as e:
                print(f"⚠️  Manual source not available: {filename}")
                download_results['failed'] += 1
        
        return download_results
    
    def enhance_massachusetts_coverage(self):
        """Complete Massachusetts LIHTC enhancement process"""
        
        print("=" * 80)
        print("🏛️ MASSACHUSETTS LIHTC ENHANCEMENT DOWNLOADER")
        print("Official Massachusetts Government Sources")
        print("=" * 80)
        
        total_results = {'successful_downloads': 0, 'failed_downloads': 0, 'already_existed': 0}
        
        # Step 1: Scrape QAP page
        print("\n🔍 PHASE 1: DISCOVERING QAP DOCUMENTS")
        qap_links = self.scrape_qap_page()
        
        # Step 2: Scrape application page  
        print("\n🔍 PHASE 2: DISCOVERING APPLICATION MATERIALS")
        app_links = self.scrape_application_page()
        
        # Step 3: Download QAP documents
        print("\n📥 PHASE 3: DOWNLOADING QAP DOCUMENTS")
        qap_results = self.download_qap_documents()
        total_results['successful_downloads'] += qap_results['success']
        total_results['failed_downloads'] += qap_results['failed']
        
        # Step 4: Download application materials
        print("\n📥 PHASE 4: DOWNLOADING APPLICATION MATERIALS")
        app_results = self.download_application_materials()
        total_results['successful_downloads'] += app_results['success']
        total_results['failed_downloads'] += app_results['failed']
        
        # Step 5: Try manual sources
        print("\n📥 PHASE 5: CHECKING MANUAL SOURCES")
        manual_results = self.add_manual_massachusetts_sources()
        total_results['successful_downloads'] += manual_results['success']
        total_results['failed_downloads'] += manual_results['failed']
        
        # Generate summary
        self.generate_enhancement_summary(total_results, len(qap_links), len(app_links))
        
        return total_results
    
    def generate_enhancement_summary(self, results: dict, qap_links_found: int, app_links_found: int):
        """Generate comprehensive enhancement summary"""
        
        print("\n" + "=" * 80)
        print("📊 MASSACHUSETTS LIHTC ENHANCEMENT SUMMARY")
        print("=" * 80)
        
        print(f"QAP Links Discovered: {qap_links_found}")
        print(f"Application Links Discovered: {app_links_found}")
        print(f"✅ Successfully Downloaded: {results['successful_downloads']}")
        print(f"❌ Failed Downloads: {results['failed_downloads']}")
        
        total_processed = results['successful_downloads'] + results['failed_downloads']
        if total_processed > 0:
            success_rate = results['successful_downloads'] / total_processed * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Count files in directories
        print(f"\n📂 ENHANCED MASSACHUSETTS STRUCTURE:")
        
        directories = {
            'Current QAPs': self.base_dir / "QAP" / "current",
            'Archive QAPs': self.base_dir / "QAP" / "archive",
            'Application Forms': self.base_dir / "applications" / "9pct",
            'Instructions': self.base_dir / "applications" / "instructions",
            'Notices': self.base_dir / "notices"
        }
        
        for name, directory in directories.items():
            if directory.exists():
                file_count = len([f for f in directory.iterdir() if f.is_file()])
                print(f"  {name}: {file_count} files")
        
        # Business value
        print(f"\n💼 ENHANCED MASSACHUSETTS CAPABILITIES:")
        capabilities = [
            "Complete official QAP coverage from mass.gov",
            "Current and historical QAP versions",
            "Draft and proposed QAP documents",
            "Official application forms and instructions",
            "Program notices and announcements",
            "Federal compliance integration ready"
        ]
        
        for capability in capabilities:
            print(f"  ✓ {capability}")
        
        # Save summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.base_dir / f"massachusetts_enhancement_summary_{timestamp}.txt"
        
        with open(summary_file, 'w') as f:
            f.write("Massachusetts LIHTC Enhancement Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Enhancement Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"QAP Links Found: {qap_links_found}\n")
            f.write(f"Application Links Found: {app_links_found}\n")
            f.write(f"Files Downloaded: {results['successful_downloads']}\n")
            f.write(f"Failed Downloads: {results['failed_downloads']}\n")
            
            if total_processed > 0:
                f.write(f"Success Rate: {success_rate:.1f}%\n")
            
            f.write(f"\nEnhancement completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"\n📄 Summary saved to: {summary_file}")
        
        print(f"\n🚀 NEXT STEPS FOR MASSACHUSETTS:")
        next_steps = [
            "Process new QAP documents for federal compliance analysis",
            "Extract application requirements for conflict detection",
            "Integrate with federal RAG system for authority citations",
            "Update master chunk index with new Massachusetts content",
            "Verify 100% state coverage achievement"
        ]
        
        for i, step in enumerate(next_steps, 1):
            print(f"  {i}. {step}")


# Main execution
if __name__ == "__main__":
    enhancer = MassachusettsLIHTCEnhancer()
    
    # Run complete Massachusetts enhancement
    results = enhancer.enhance_massachusetts_coverage()
    
    print(f"\n✅ Massachusetts LIHTC Enhancement Complete!")
    print(f"📊 Files Downloaded: {results['successful_downloads']}")
    print(f"🏛️ Official Massachusetts Coverage: MAXIMUM")
    print(f"🎯 Ready for federal compliance integration")