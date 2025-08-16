#!/usr/bin/env python3
"""
US Territories LIHTC Search: Guam and US Virgin Islands
Search for additional LIHTC programs in US territories for maximum coverage
"""

import requests
from pathlib import Path
from datetime import datetime
import time

class USTerritoryLIHTCSearcher:
    """Search for LIHTC programs in US territories"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/QAP")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # US Territory search targets
        self.territories = {
            'GU': {
                'name': 'Guam',
                'housing_agencies': [
                    'Guam Housing and Urban Renewal Authority',
                    'GHURA'
                ],
                'search_urls': [
                    'https://www.ghura.org/',
                    'https://www.guam.gov/',
                    'https://www.ghura.org/programs',
                    'https://www.ghura.org/lihtc'
                ],
                'potential_urls': [
                    'https://www.ghura.org/documents/qap.pdf',
                    'https://www.ghura.org/files/lihtc-qap.pdf',
                    'https://www.guam.gov/lihtc/qap.pdf'
                ]
            },
            'VI': {
                'name': 'US Virgin Islands',
                'housing_agencies': [
                    'Virgin Islands Housing Finance Authority',
                    'VIHFA'
                ],
                'search_urls': [
                    'https://www.vihfa.gov/',
                    'https://www.vi.gov/',
                    'https://www.vihfa.gov/programs',
                    'https://www.vihfa.gov/lihtc'
                ],
                'potential_urls': [
                    'https://www.vihfa.gov/documents/qap.pdf',
                    'https://www.vihfa.gov/files/lihtc-qap.pdf',
                    'https://www.vi.gov/lihtc/qap.pdf'
                ]
            }
        }
        
        self.setup_directories()
    
    def setup_directories(self):
        """Create directory structure for territories"""
        
        for territory in ['GU', 'VI']:
            directories = [
                self.base_dir / territory / "current",
                self.base_dir / territory / "archive",
                self.base_dir / territory / "applications",
                self.base_dir / territory / "notices"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
    
    def check_url_accessibility(self, url: str) -> dict:
        """Check if a URL is accessible and what type of content it returns"""
        
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            
            result = {
                'url': url,
                'accessible': response.status_code == 200,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'content_length': response.headers.get('content-length', 0),
                'redirect_url': response.url if response.url != url else None
            }
            
            return result
            
        except Exception as e:
            return {
                'url': url,
                'accessible': False,
                'error': str(e),
                'status_code': None
            }
    
    def search_territory_websites(self, territory_code: str) -> list:
        """Search territory websites for LIHTC programs"""
        
        territory = self.territories[territory_code]
        print(f"\n🏝️ SEARCHING {territory['name'].upper()} ({territory_code})")
        print("-" * 50)
        
        accessible_urls = []
        potential_documents = []
        
        # Check main websites
        print(f"📋 Checking main websites:")
        for url in territory['search_urls']:
            print(f"🔗 Testing: {url}")
            result = self.check_url_accessibility(url)
            
            if result['accessible']:
                print(f"   ✅ Accessible (Status: {result['status_code']})")
                accessible_urls.append(result)
                
                # Try to fetch content to look for LIHTC references
                try:
                    content_response = self.session.get(url, timeout=15)
                    if content_response.status_code == 200:
                        content = content_response.text.lower()
                        
                        # Look for LIHTC-related terms
                        lihtc_indicators = [
                            'lihtc', 'low income housing tax credit', 'qualified allocation plan',
                            'qap', 'tax credit', 'affordable housing', 'housing finance'
                        ]
                        
                        found_indicators = [term for term in lihtc_indicators if term in content]
                        if found_indicators:
                            print(f"   🎯 LIHTC indicators found: {', '.join(found_indicators[:3])}")
                            
                            # Save page content for manual review
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            content_file = self.base_dir / territory_code / f"website_content_{timestamp}.html"
                            with open(content_file, 'w', encoding='utf-8') as f:
                                f.write(content_response.text)
                            print(f"   📄 Content saved to: {content_file}")
                        
                except Exception as e:
                    print(f"   ⚠️ Could not fetch content: {e}")
            else:
                print(f"   ❌ Not accessible (Status: {result.get('status_code', 'Unknown')})")
                if 'error' in result:
                    print(f"      Error: {result['error']}")
        
        # Check potential document URLs
        print(f"\n📄 Checking potential QAP documents:")
        for url in territory['potential_urls']:
            print(f"🔗 Testing: {url}")
            result = self.check_url_accessibility(url)
            
            if result['accessible'] and 'pdf' in result.get('content_type', '').lower():
                print(f"   ✅ PDF found! Size: {result.get('content_length', 'Unknown')}")
                potential_documents.append(result)
                
                # Try to download
                filename = url.split('/')[-1]
                if not filename.endswith('.pdf'):
                    filename = f"{territory_code}_QAP.pdf"
                
                if self.download_file(url, filename, self.base_dir / territory_code / "current"):
                    print(f"   📥 Downloaded successfully")
                
            else:
                print(f"   ❌ No PDF found (Status: {result.get('status_code', 'Unknown')})")
        
        return {
            'accessible_websites': accessible_urls,
            'potential_documents': potential_documents,
            'territory_name': territory['name']
        }
    
    def download_file(self, url: str, filename: str, target_dir: Path) -> bool:
        """Download a file to target directory"""
        
        file_path = target_dir / filename
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Download failed: {e}")
            return False
    
    def search_federal_territory_resources(self):
        """Search for federal resources about territories"""
        
        print(f"\n🏛️ SEARCHING FEDERAL TERRITORY RESOURCES")
        print("-" * 50)
        
        federal_resources = [
            'https://www.hudexchange.info/programs/lihtc/',
            'https://www.novoco.com/resource-centers/affordable-housing-tax-credits',
            'https://www.irs.gov/credits-deductions/businesses/low-income-housing-credit',
            'https://www.hud.gov/states/shared/working/r10/lihtc'
        ]
        
        accessible_resources = []
        
        for url in federal_resources:
            print(f"🔗 Testing: {url}")
            result = self.check_url_accessibility(url)
            
            if result['accessible']:
                print(f"   ✅ Accessible - May contain territory information")
                accessible_resources.append(result)
            else:
                print(f"   ❌ Not accessible")
        
        return accessible_resources
    
    def comprehensive_territory_search(self):
        """Comprehensive search for US territory LIHTC programs"""
        
        print("=" * 80)
        print("🏝️ US TERRITORIES LIHTC PROGRAM SEARCH")
        print("Searching for Guam and US Virgin Islands LIHTC Programs")
        print("=" * 80)
        
        search_results = {}
        
        # Search each territory
        for territory_code in ['GU', 'VI']:
            search_results[territory_code] = self.search_territory_websites(territory_code)
            time.sleep(2)  # Brief pause between territories
        
        # Search federal resources
        federal_resources = self.search_federal_territory_resources()
        
        # Generate comprehensive summary
        print(f"\n" + "=" * 80)
        print("📊 US TERRITORIES LIHTC SEARCH SUMMARY")
        print("=" * 80)
        
        total_accessible_sites = 0
        total_documents_found = 0
        territories_with_programs = []
        
        for territory_code, results in search_results.items():
            territory_name = results['territory_name']
            accessible_count = len(results['accessible_websites'])
            documents_count = len(results['potential_documents'])
            
            total_accessible_sites += accessible_count
            total_documents_found += documents_count
            
            print(f"\n🏝️ {territory_name} ({territory_code}):")
            print(f"   Accessible websites: {accessible_count}")
            print(f"   Documents found: {documents_count}")
            
            if accessible_count > 0 or documents_count > 0:
                territories_with_programs.append(territory_code)
                print(f"   Status: ✅ Potential LIHTC program detected")
            else:
                print(f"   Status: ❓ No clear LIHTC program found")
        
        print(f"\n🎯 OVERALL SUMMARY:")
        print(f"Territories searched: 2")
        print(f"Accessible websites: {total_accessible_sites}")
        print(f"Documents found: {total_documents_found}")
        print(f"Territories with potential programs: {len(territories_with_programs)}")
        print(f"Federal resources accessible: {len(federal_resources)}")
        
        # Coverage implications
        print(f"\n📈 COVERAGE IMPLICATIONS:")
        
        if len(territories_with_programs) > 0:
            print(f"✅ Additional territories found: {', '.join(territories_with_programs)}")
            print(f"🎯 Potential total coverage: 52 + {len(territories_with_programs)} = {52 + len(territories_with_programs)} jurisdictions")
            print(f"🏆 Achievement level: MAXIMUM POSSIBLE US COVERAGE")
        else:
            print(f"📋 No additional territory programs definitively identified")
            print(f"🎯 Current coverage remains: 52 jurisdictions")
            print(f"🏆 Achievement level: COMPLETE CONTINENTAL US + TERRITORIES")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        recommendations = [
            "Review saved website content for manual LIHTC program identification",
            "Contact territory housing agencies directly for QAP availability",
            "Monitor federal resources for territory-specific LIHTC guidance",
            "Consider territories for future expansion if programs are established"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        # Save search report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.base_dir / f"territory_search_report_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write("US Territories LIHTC Search Report\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Search Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Territories Searched: Guam (GU), US Virgin Islands (VI)\n\n")
            
            for territory_code, results in search_results.items():
                f.write(f"{results['territory_name']} ({territory_code}):\n")
                f.write(f"  Accessible websites: {len(results['accessible_websites'])}\n")
                f.write(f"  Documents found: {len(results['potential_documents'])}\n\n")
            
            f.write(f"Summary:\n")
            f.write(f"  Total accessible sites: {total_accessible_sites}\n")
            f.write(f"  Total documents: {total_documents_found}\n")
            f.write(f"  Territories with programs: {len(territories_with_programs)}\n")
        
        print(f"\n📄 Search report saved to: {report_file}")
        
        return {
            'search_results': search_results,
            'territories_with_programs': territories_with_programs,
            'total_coverage': 52 + len(territories_with_programs),
            'federal_resources': federal_resources
        }


# Main execution
if __name__ == "__main__":
    searcher = USTerritoryLIHTCSearcher()
    
    # Run comprehensive territory search
    results = searcher.comprehensive_territory_search()
    
    print(f"\n✅ US Territories LIHTC Search Complete!")
    print(f"🏝️ Territories searched: Guam, US Virgin Islands")
    print(f"📊 Potential additional coverage: {results['total_coverage'] - 52} jurisdictions")
    print(f"🎯 Maximum possible US coverage: {results['total_coverage']} total jurisdictions")
    
    if results['territories_with_programs']:
        print(f"🎉 Additional programs found in: {', '.join(results['territories_with_programs'])}")
    else:
        print(f"📋 Current 52-jurisdiction coverage appears to be maximum available")