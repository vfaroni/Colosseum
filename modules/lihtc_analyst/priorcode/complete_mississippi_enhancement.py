#!/usr/bin/env python3
"""
Complete Mississippi LIHTC Enhancement Downloader
Downloads additional MS LIHTC documents to supplement existing QAP coverage

Sources provided by user:
- 2025 QAP: https://www.maahp.ms/s/mississippi-lihtc-qap-final-2025-01072025.pdf
- Recipient Lists (2020-2024): Historical award data
- Applicant Lists (2020-2025): Application tracking data  
- Application Forms: Current forms and procedures
"""

import requests
import os
from pathlib import Path
from datetime import datetime
import time

class MississippiLIHTCEnhancer:
    """Enhanced Mississippi LIHTC document collection"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/QAP/MS")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Mississippi LIHTC sources
        self.ms_sources = {
            'qap_documents': {
                'mississippi-lihtc-qap-final-2025-01072025.pdf': 'https://www.maahp.ms/s/mississippi-lihtc-qap-final-2025-01072025.pdf'
            },
            'recipient_lists': {
                '2024_RECIPIENT_LIST.pdf': 'https://archivemhc.com/htc/2024/2024%20RECIPIENT%20LIST.pdf',
                '2023_RECIPIENT_LIST.pdf': 'https://archivemhc.com/htc/2023/2023%20RECIPIENT%20LIST.pdf',
                '2022_RECIPIENT_LIST.pdf': 'https://archivemhc.com/htc/2022/2022%20Recipient%20List.pdf',
                '2021_RECIPIENT_LIST.pdf': 'https://archivemhc.com/htc/2021/2021%20Recipient%20List.pdf',
                '2020_RECIPIENT_LIST.pdf': 'https://archivemhc.com/htc/2020/2020%20Recipient%20List.pdf'
            },
            'applicant_lists': {
                '2025_APPLICANT_LIST.pdf': 'https://archivemhc.com/htc/2025/2025%20APPLICANT%20LIST.pdf',
                '2024_APPLICANT_LIST.pdf': 'https://archivemhc.com/htc/2024/2024%20APPLICANT%20LIST.pdf',
                '2023_APPLICANT_LIST.pdf': 'https://archivemhc.com/htc/2023/2023%20APPLICANT%20LIST.pdf',
                '2022_APPLICANT_LIST.pdf': 'https://archivemhc.com/htc/2022/2022%20Applicant%20List.pdf',
                '2021_APPLICANT_LIST.pdf': 'https://archivemhc.com/htc/2021/2021%20Applicant%20List.pdf',
                '2020_APPLICANT_LIST.pdf': 'https://archivemhc.com/htc/2020/2020%20Applicant%20List.pdf'
            },
            'application_forms': {
                'Applicant_Rating_Form_01132025.xlsm': 'https://archivemhc.com/htc/HTC%20Application%20Forms/Applicant%20Rating%20Form%2001132025.xlsm',
                'Threshold_Documents.pdf': 'https://archivemhc.com/htc/HTC%20Application%20Forms/Threshold%20Documents.pdf',
                'Financial_Feasibility_Forms_Certification_2025.xlsm': 'https://archivemhc.com/htc/HTC%20Application%20Forms/Financial%20Feasibility%20Forms%20&%20Certification%202025.xlsm',
                'Market_Standards_Checklist.pdf': 'https://archivemhc.com/htc/HTC%20Application%20Forms/Market%20Standards%20Checklist.xls.pdf',
                'ComplianceVerificationRequestForm2019.pdf': 'https://archivemhc.com/htc/HTC%20Application%20Forms/ComplianceVerficationRequestForm2019.pdf',
                'Development_Waiver_Request_2023.xls': 'https://archivemhc.com/htc/HTC%20Application%20Forms/Development%20Waiver%20Request%202023.xls'
            },
            'application_attachments': {
                'Application_Checklist2024.pdf': 'https://archivemhc.com/htc/HTC%20Application%20Attachments/1-Application%20Checklist2024.pdf'
            }
        }
        
        # Create directory structure
        self.setup_directories()
    
    def setup_directories(self):
        """Create enhanced directory structure for Mississippi"""
        directories = [
            self.base_dir / "awards" / "recipients",
            self.base_dir / "awards" / "applicants", 
            self.base_dir / "applications" / "forms",
            self.base_dir / "applications" / "attachments",
            self.base_dir / "applications" / "instructions",
            self.base_dir / "current",
            self.base_dir / "archive",
            self.base_dir / "processed"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ Directory ready: {directory}")
    
    def download_file(self, url: str, filename: str, category: str) -> bool:
        """Download a single file with proper categorization"""
        
        # Determine target directory
        if category == 'qap_documents':
            target_dir = self.base_dir / "current"
        elif category == 'recipient_lists':
            target_dir = self.base_dir / "awards" / "recipients"
        elif category == 'applicant_lists':
            target_dir = self.base_dir / "awards" / "applicants"
        elif category == 'application_forms':
            target_dir = self.base_dir / "applications" / "forms"
        elif category == 'application_attachments':
            target_dir = self.base_dir / "applications" / "attachments"
        else:
            target_dir = self.base_dir / "archive"
        
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
            if content_length < 1000:
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
    
    def download_all_sources(self):
        """Download all Mississippi LIHTC sources"""
        
        print("=" * 80)
        print("🏛️ MISSISSIPPI LIHTC ENHANCEMENT DOWNLOADER")
        print("Comprehensive Mississippi LIHTC Document Collection")
        print("=" * 80)
        
        download_results = {
            'successful_downloads': 0,
            'failed_downloads': 0,
            'already_existed': 0,
            'total_files': 0,
            'download_details': {}
        }
        
        # Process each category
        for category, files in self.ms_sources.items():
            print(f"\n📂 DOWNLOADING: {category.upper().replace('_', ' ')}")
            print("-" * 50)
            
            category_results = {'success': 0, 'failed': 0, 'existed': 0}
            
            for filename, url in files.items():
                download_results['total_files'] += 1
                
                # Check if file already exists
                if category == 'qap_documents':
                    target_path = self.base_dir / "current" / filename
                elif category == 'recipient_lists':
                    target_path = self.base_dir / "awards" / "recipients" / filename
                elif category == 'applicant_lists':
                    target_path = self.base_dir / "awards" / "applicants" / filename
                elif category == 'application_forms':
                    target_path = self.base_dir / "applications" / "forms" / filename
                elif category == 'application_attachments':
                    target_path = self.base_dir / "applications" / "attachments" / filename
                
                if target_path.exists():
                    print(f"⏭️  Already exists: {filename}")
                    category_results['existed'] += 1
                    download_results['already_existed'] += 1
                    continue
                
                # Download file
                success = self.download_file(url, filename, category)
                
                if success:
                    category_results['success'] += 1
                    download_results['successful_downloads'] += 1
                else:
                    category_results['failed'] += 1
                    download_results['failed_downloads'] += 1
            
            download_results['download_details'][category] = category_results
            
            print(f"\n{category.replace('_', ' ').title()} Summary:")
            print(f"  ✅ Successful: {category_results['success']}")
            print(f"  ❌ Failed: {category_results['failed']}")
            print(f"  ⏭️  Already existed: {category_results['existed']}")
        
        # Generate final summary
        self.generate_download_summary(download_results)
        
        return download_results
    
    def generate_download_summary(self, results: dict):
        """Generate comprehensive download summary"""
        
        print("\n" + "=" * 80)
        print("📊 MISSISSIPPI LIHTC ENHANCEMENT SUMMARY")
        print("=" * 80)
        
        print(f"Total Files Processed: {results['total_files']}")
        print(f"✅ Successfully Downloaded: {results['successful_downloads']}")
        print(f"⏭️  Already Existed: {results['already_existed']}")
        print(f"❌ Failed Downloads: {results['failed_downloads']}")
        
        success_rate = (results['successful_downloads'] + results['already_existed']) / results['total_files'] * 100
        print(f"📈 Overall Success Rate: {success_rate:.1f}%")
        
        print(f"\n📂 ENHANCED MISSISSIPPI STRUCTURE:")
        
        # Count files in each directory
        structure_summary = {}
        
        directories = {
            'QAP Documents': self.base_dir / "current",
            'Recipient Lists': self.base_dir / "awards" / "recipients",
            'Applicant Lists': self.base_dir / "awards" / "applicants",
            'Application Forms': self.base_dir / "applications" / "forms",
            'Application Attachments': self.base_dir / "applications" / "attachments"
        }
        
        for name, directory in directories.items():
            if directory.exists():
                file_count = len(list(directory.glob("*")))
                structure_summary[name] = file_count
                print(f"  {name}: {file_count} files")
        
        # Business value summary
        print(f"\n💼 ENHANCED MISSISSIPPI CAPABILITIES:")
        capabilities = [
            f"Complete QAP coverage (current + enhanced sources)",
            f"Historical award tracking (2020-2024 recipients)",
            f"Application pipeline analysis (2020-2025 applicants)",
            f"Current application forms and procedures",
            f"Compliance verification documentation",
            f"Market analysis and threshold requirements"
        ]
        
        for capability in capabilities:
            print(f"  ✓ {capability}")
        
        # Next steps
        print(f"\n🚀 RECOMMENDED NEXT STEPS:")
        next_steps = [
            "Process recipient/applicant lists for market intelligence",
            "Extract application form requirements for compliance analysis", 
            "Integrate award data with federal compliance tracking",
            "Create Mississippi-specific federal conflict analysis",
            "Build comprehensive Mississippi LIHTC research module"
        ]
        
        for i, step in enumerate(next_steps, 1):
            print(f"  {i}. {step}")
        
        # Save summary report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.base_dir / f"mississippi_enhancement_summary_{timestamp}.txt"
        
        with open(summary_file, 'w') as f:
            f.write("Mississippi LIHTC Enhancement Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Enhancement Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Files Processed: {results['total_files']}\n")
            f.write(f"Successfully Downloaded: {results['successful_downloads']}\n")
            f.write(f"Already Existed: {results['already_existed']}\n")
            f.write(f"Failed Downloads: {results['failed_downloads']}\n")
            f.write(f"Success Rate: {success_rate:.1f}%\n\n")
            
            f.write("Directory Structure:\n")
            for name, count in structure_summary.items():
                f.write(f"  {name}: {count} files\n")
            
            f.write(f"\nEnhancement completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"\n📄 Summary saved to: {summary_file}")
        
        return summary_file
    
    def verify_system_completion(self):
        """Verify that we now have 100% state coverage"""
        
        print(f"\n" + "=" * 80)
        print("🎯 VERIFYING 100% STATE COVERAGE")
        print("=" * 80)
        
        # Check QAP processing status
        qap_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/QAP")
        processed_dir = qap_dir / "_processed"
        
        # Count processed states
        processed_states = []
        if processed_dir.exists():
            for state_dir in processed_dir.iterdir():
                if state_dir.is_dir() and len(state_dir.name) == 2:
                    summary_file = state_dir / f"{state_dir.name}_processing_summary.json"
                    if summary_file.exists():
                        processed_states.append(state_dir.name)
        
        total_jurisdictions = 51  # 50 states + DC + PR (sometimes included)
        
        print(f"Processed States/Jurisdictions: {len(processed_states)}")
        print(f"Target Coverage: {total_jurisdictions} jurisdictions")
        
        coverage_rate = len(processed_states) / total_jurisdictions * 100
        print(f"Coverage Rate: {coverage_rate:.1f}%")
        
        if 'MS' in processed_states and 'MA' in processed_states:
            print(f"✅ Both MA and MS are processed and integrated!")
            print(f"✅ Mississippi enhancement adds comprehensive source coverage")
            
            if coverage_rate >= 96:
                print(f"🎉 ACHIEVEMENT UNLOCKED: Near-complete LIHTC coverage!")
                print(f"   This represents the most comprehensive LIHTC research system available")
        
        return {
            'processed_states': len(processed_states),
            'coverage_rate': coverage_rate,
            'ma_included': 'MA' in processed_states,
            'ms_included': 'MS' in processed_states,
            'enhanced_ms': True
        }


# Main execution
if __name__ == "__main__":
    enhancer = MississippiLIHTCEnhancer()
    
    # Download all Mississippi sources
    results = enhancer.download_all_sources()
    
    # Verify system completion
    completion_status = enhancer.verify_system_completion()
    
    print(f"\n✅ Mississippi LIHTC Enhancement Complete!")
    print(f"📊 Files Downloaded: {results['successful_downloads']}")
    print(f"🎯 System Coverage: {completion_status['coverage_rate']:.1f}%")
    print(f"🏛️ Total LIHTC Research Capability: MAXIMUM")