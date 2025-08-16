#!/usr/bin/env python3
"""
Massachusetts LIHTC Manual Downloader
Direct download of specific Massachusetts LIHTC documents based on manual URL discovery
"""

import requests
import os
from pathlib import Path
from datetime import datetime
import time

class MassachusettsManualDownloader:
    """Manual Massachusetts LIHTC document downloader with specific URLs"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/QAP/MA")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Manual Massachusetts LIHTC document URLs
        # These should be updated based on actual findings from the website
        self.ma_documents = {
            'current_qaps': {
                # Will add specific URLs once we find them
            },
            'application_materials': {
                # Will add specific URLs once we find them
            },
            'historical_qaps': {
                # Will add specific URLs once we find them
            }
        }
        
        # Create directory structure
        self.setup_directories()
    
    def setup_directories(self):
        """Create directory structure"""
        directories = [
            self.base_dir / "current",
            self.base_dir / "archive", 
            self.base_dir / "applications",
            self.base_dir / "notices"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def fetch_page_content(self, url):
        """Fetch and display page content for manual inspection"""
        
        print(f"🔍 Fetching page content from: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Save the HTML content for inspection
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_file = self.base_dir / f"page_content_{timestamp}.html"
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"📄 Page content saved to: {html_file}")
            
            # Look for potential PDF links in the content
            content = response.text.lower()
            potential_links = []
            
            # Simple regex to find PDF references
            import re
            pdf_matches = re.findall(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', content, re.IGNORECASE)
            
            for match in pdf_matches:
                if not match.startswith('http'):
                    if match.startswith('/'):
                        match = 'https://www.mass.gov' + match
                    else:
                        match = 'https://www.mass.gov/' + match
                potential_links.append(match)
            
            print(f"🔗 Found {len(potential_links)} potential PDF links:")
            for i, link in enumerate(potential_links[:10], 1):  # Show first 10
                print(f"  {i}. {link}")
            
            return potential_links
            
        except Exception as e:
            print(f"❌ Error fetching page: {e}")
            return []
    
    def try_common_massachusetts_urls(self):
        """Try common Massachusetts document URL patterns"""
        
        print("\n🎯 TRYING COMMON MASSACHUSETTS URL PATTERNS")
        print("-" * 60)
        
        # Common URL patterns for Massachusetts government documents
        common_patterns = [
            # QAP documents
            'https://www.mass.gov/doc/qualified-allocation-plan-2025/download',
            'https://www.mass.gov/doc/qualified-allocation-plan-2024/download', 
            'https://www.mass.gov/doc/qap-2025/download',
            'https://www.mass.gov/doc/qap-2024/download',
            'https://www.mass.gov/files/documents/2024/qualified-allocation-plan.pdf',
            'https://www.mass.gov/files/documents/2025/qualified-allocation-plan.pdf',
            
            # LIHTC application materials
            'https://www.mass.gov/doc/lihtc-application-2025/download',
            'https://www.mass.gov/doc/low-income-housing-tax-credit-application/download',
            'https://www.mass.gov/files/documents/2024/lihtc-application.pdf',
            'https://www.mass.gov/files/documents/2025/lihtc-application.pdf',
            
            # DHCD documents  
            'https://www.mass.gov/orgs/department-of-housing-and-community-development',
        ]
        
        successful_downloads = []
        
        for url in common_patterns:
            print(f"🔗 Trying: {url}")
            
            try:
                response = self.session.head(url, timeout=10)  # Use HEAD to check existence
                if response.status_code == 200:
                    print(f"✅ Found: {url}")
                    
                    # Try to download
                    filename = url.split('/')[-1]
                    if not filename.endswith('.pdf'):
                        filename += '.pdf'
                    
                    if self.download_file(url, filename, self.base_dir / "current"):
                        successful_downloads.append(url)
                else:
                    print(f"❌ Not found: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            time.sleep(0.5)  # Brief pause
        
        return successful_downloads
    
    def download_file(self, url: str, filename: str, target_dir: Path) -> bool:
        """Download a single file"""
        
        file_path = target_dir / filename
        
        if file_path.exists():
            print(f"⏭️  Already exists: {filename}")
            return True
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            content_length = len(response.content)
            if content_length < 1000:
                print(f"⚠️  Warning: {filename} is only {content_length} bytes")
                return False
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Downloaded: {filename} ({content_length:,} bytes)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
            return False
    
    def search_massachusetts_lihtc(self):
        """Comprehensive Massachusetts LIHTC document search"""
        
        print("=" * 80)
        print("🏛️ MASSACHUSETTS LIHTC MANUAL DOCUMENT SEARCH")
        print("=" * 80)
        
        # Step 1: Fetch page content from both main pages
        print("\n📄 STEP 1: INSPECTING MAIN PAGES")
        
        main_pages = [
            'https://www.mass.gov/info-details/qualified-allocation-plan',
            'https://www.mass.gov/info-details/low-income-housing-tax-credit-lihtc'
        ]
        
        all_links = []
        for page in main_pages:
            links = self.fetch_page_content(page)
            all_links.extend(links)
        
        # Step 2: Try common URL patterns
        print("\n🎯 STEP 2: TRYING COMMON URL PATTERNS")
        successful_urls = self.try_common_massachusetts_urls()
        
        # Step 3: Try to download any found links
        print("\n📥 STEP 3: DOWNLOADING DISCOVERED LINKS")
        
        download_count = 0
        for link in set(all_links):  # Remove duplicates
            filename = link.split('/')[-1].split('?')[0]
            if not filename:
                filename = f"MA_document_{int(time.time())}.pdf"
            
            if self.download_file(link, filename, self.base_dir / "current"):
                download_count += 1
                
        # Step 4: Check what we have in existing MA directory
        print("\n📂 STEP 4: CHECKING EXISTING MASSACHUSETTS FILES")
        self.check_existing_files()
        
        # Summary
        print(f"\n📊 SEARCH SUMMARY:")
        print(f"Links discovered: {len(set(all_links))}")
        print(f"Common URLs tried: {len(successful_urls)}")
        print(f"Files downloaded: {download_count}")
        
        return {
            'links_found': len(set(all_links)),
            'successful_downloads': download_count,
            'discovered_urls': list(set(all_links))
        }
    
    def check_existing_files(self):
        """Check what Massachusetts files we already have"""
        
        existing_files = []
        
        for directory in [self.base_dir / "current", self.base_dir / "archive"]:
            if directory.exists():
                for file_path in directory.glob("*"):
                    if file_path.is_file():
                        size = file_path.stat().st_size
                        existing_files.append({
                            'name': file_path.name,
                            'size': size,
                            'path': str(file_path)
                        })
        
        if existing_files:
            print(f"Found {len(existing_files)} existing Massachusetts files:")
            for file_info in existing_files:
                print(f"  📄 {file_info['name']} ({file_info['size']:,} bytes)")
        else:
            print("No existing Massachusetts files found")
        
        return existing_files
    
    def generate_manual_instructions(self):
        """Generate instructions for manual document collection"""
        
        instructions = """
MASSACHUSETTS LIHTC MANUAL COLLECTION INSTRUCTIONS
================================================

1. Visit the main QAP page:
   https://www.mass.gov/info-details/qualified-allocation-plan
   
   Look for:
   - Current QAP (2025-2026)
   - Previous QAP (2023-2024) 
   - Draft versions
   - Redlined versions

2. Visit the LIHTC application page:
   https://www.mass.gov/info-details/low-income-housing-tax-credit-lihtc
   
   Look for:
   - Application forms
   - Instructions
   - Notices and announcements
   - Scoring criteria

3. Check the DHCD main page:
   https://www.mass.gov/orgs/department-of-housing-and-community-development
   
   Look for:
   - Housing programs
   - LIHTC resources
   - Annual reports

4. Search for specific documents:
   - "Massachusetts Qualified Allocation Plan"
   - "Massachusetts LIHTC Application"
   - "Massachusetts housing tax credit"

5. Manual download process:
   - Right-click -> Save Link As
   - Save to appropriate directory in MA folder
   - Note the original URL for documentation

6. Document the sources:
   - URL where found
   - Date accessed
   - Document date/version
"""
        
        instructions_file = self.base_dir / "manual_collection_instructions.txt"
        with open(instructions_file, 'w') as f:
            f.write(instructions)
        
        print(f"\n📋 Manual collection instructions saved to: {instructions_file}")
        
        return instructions


# Main execution
if __name__ == "__main__":
    downloader = MassachusettsManualDownloader()
    
    # Run comprehensive search
    results = downloader.search_massachusetts_lihtc()
    
    # Generate manual instructions
    downloader.generate_manual_instructions()
    
    print(f"\n✅ Massachusetts LIHTC Search Complete!")
    print(f"🔗 Links discovered: {results['links_found']}")
    print(f"📥 Files downloaded: {results['successful_downloads']}")
    
    if results['discovered_urls']:
        print(f"\n🔗 Discovered URLs:")
        for url in results['discovered_urls'][:5]:  # Show first 5
            print(f"  • {url}")
    
    print(f"\n💡 Next steps:")
    print(f"  1. Review saved page content for manual link extraction")
    print(f"  2. Use manual collection instructions for targeted downloads")
    print(f"  3. Process any downloaded documents into the QAP system")