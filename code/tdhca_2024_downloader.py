#!/usr/bin/env python3
"""
TDHCA 2024 Applications Downloader
Downloads specific 2024 TDHCA applications including 24600
Based on URL pattern: https://www.tdhca.state.tx.us/multifamily/docs/imaged/2024-4-TEBApps/{app_num}.pdf
"""

import os
import requests
import time
from pathlib import Path
from datetime import datetime

class TDHCA2024Downloader:
    """Download 2024 TDHCA applications"""
    
    def __init__(self):
        self.base_url = "https://www.tdhca.state.tx.us/multifamily/docs/imaged/2024-4-TEBApps"
        
        # Separate directories for applications vs awarded projects
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
        self.applications_dir = self.base_dir / "2024_Applications_All"  # All applications submitted
        self.awarded_dir = self.base_dir / "2024_Applications_Awarded"   # Only awarded applications
        
        # Create directories
        self.applications_dir.mkdir(exist_ok=True)
        self.awarded_dir.mkdir(exist_ok=True)
        
        # Track known awarded applications (add more as we identify them)
        self.known_awarded = {
            "24600": {"project_name": "Unknown", "developer": "TBD", "award_date": "2024"}
            # Add more awarded applications as we identify them
        }
        
        # Complete list of available 2024 TDHCA applications
        self.priority_apps = [
            # Core applications including 24600
            "24600", "24601", "24602", "24603", "24604", "24605",
            # Full range of available 2024 applications
            "24400", "24401", "24402", "24403", "24404", "24405", "24406", "24407", "24408", "24409",
            "24410", "24411", "24412", "24413", "24414", "24415", "24416", "24417", "24418", "24419",
            "24420", "24421", "24422", "24423", "24424", "24425", "24426", "24427", "24428", "24429",
            "24430", "24431", "24432", "24433", "24434", "24435", "24436", "24437", "24438", "24439",
            "24440", "24441", "24442", "24443", "24444", "24445", "24446", "24447", "24448", "24449",
            "24450", "24451", "24452", "24453", "24454", "24455", "24456", "24457", "24458", "24459",
            "24460", "24461", "24462", "24463", "24464", "24465", "24466", "24467", "24468", "24469",
            "24470", "24471", "24472", "24473", "24474", "24475", "24476", "24477", "24478", "24479",
            "24480", "24481", "24482", "24483", "24484", "24485", "24486", "24487", "24488", "24489",
            "24490", "24491", "24492", "24493", "24494", "24495", "24496", "24497", "24498", "24499",
            "24500", "24501", "24502", "24503", "24504", "24505", "24506", "24507", "24508", "24509",
            "24510", "24511", "24512", "24513", "24514", "24515", "24516", "24517", "24518", "24519",
            "24520", "24521", "24522", "24523", "24524", "24525", "24526", "24527", "24528", "24529",
            "24530", "24531", "24532", "24533", "24534", "24535", "24536", "24537", "24538", "24539",
            "24540", "24541", "24542", "24543", "24544", "24545", "24546", "24547", "24548", "24549",
            "24550", "24551", "24552", "24553", "24554", "24555", "24556", "24557", "24558", "24559",
            "24560", "24561", "24562", "24563", "24564", "24565", "24566", "24567", "24568", "24569",
            "24570", "24571", "24572", "24573", "24574", "24575", "24576", "24577", "24578", "24579",
            "24580", "24581", "24582", "24583", "24584", "24585", "24586", "24587", "24588", "24589",
            "24590", "24591", "24592", "24593", "24594", "24595", "24596", "24597", "24598", "24599",
            "24606", "24607", "24608", "24609", "24610", "24611", "24612", "24613", "24614", "24615",
            "24616", "24617", "24618", "24619", "24620", "24621", "24622", "24623", "24624", "24625",
            "24626", "24627", "24628", "24629", "24630", "24631", "24632", "24633", "24634", "24635",
            "24636", "24637", "24638", "24639", "24640", "24641", "24642", "24643", "24644", "24645",
            "24646", "24647", "24648", "24649", "24650", "24651", "24652", "24653", "24654", "24655",
            "24656", "24657", "24658", "24659", "24660", "24661", "24662", "24663", "24664", "24665",
            "24666", "24667", "24668", "24669", "24670", "24671", "24672", "24673", "24674", "24675",
            "24676", "24677", "24678", "24679", "24680", "24681", "24682", "24683", "24684", "24685",
            "24686", "24687", "24688", "24689", "24690", "24691", "24692", "24693", "24694", "24695",
            "24696", "24697", "24698", "24699", "24700", "24701", "24702", "24703"
        ]
    
    def download_application(self, app_num):
        """Download a specific TDHCA application and organize by status"""
        url = f"{self.base_url}/{app_num}.pdf"
        
        # Determine if this is an awarded application
        is_awarded = app_num in self.known_awarded
        target_dir = self.awarded_dir if is_awarded else self.applications_dir
        status_label = "AWARDED" if is_awarded else "APPLICATION"
        
        output_file = target_dir / f"TDHCA_{app_num}.pdf"
        
        # Skip if already downloaded
        if output_file.exists():
            print(f"✅ Already exists ({status_label}): TDHCA_{app_num}.pdf")
            return True
            
        try:
            print(f"📥 Downloading TDHCA {app_num} ({status_label})...")
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check if it's actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type:
                print(f"❌ TDHCA {app_num}: Not a PDF file (content-type: {content_type})")
                return False
                
            # Save the file to appropriate directory
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"✅ Downloaded ({status_label}): TDHCA_{app_num}.pdf ({file_size_mb:.1f} MB)")
            
            # If awarded, also create metadata file
            if is_awarded:
                self.create_awarded_metadata(app_num, output_file)
            
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"❌ TDHCA {app_num}: Application not found (404)")
            else:
                print(f"❌ TDHCA {app_num}: HTTP error {e.response.status_code}")
            return False
        except Exception as e:
            print(f"❌ TDHCA {app_num}: Download failed - {str(e)}")
            return False
    
    def create_awarded_metadata(self, app_num, pdf_path):
        """Create metadata file for awarded applications"""
        metadata = {
            "application_number": app_num,
            "status": "AWARDED",
            "download_date": datetime.now().isoformat(),
            "pdf_path": str(pdf_path),
            "award_info": self.known_awarded.get(app_num, {}),
            "source_url": f"{self.base_url}/{app_num}.pdf"
        }
        
        metadata_file = self.awarded_dir / f"TDHCA_{app_num}_metadata.json"
        with open(metadata_file, 'w') as f:
            import json
            json.dump(metadata, f, indent=2)
    
    def download_priority_applications(self):
        """Download priority applications including 24600"""
        print("🏆 TDHCA 2024 APPLICATIONS DOWNLOADER")
        print("=" * 60)
        print(f"Target URL pattern: {self.base_url}/{{app_num}}.pdf")
        print(f"Applications directory: {self.applications_dir}")
        print(f"Awarded directory: {self.awarded_dir}")
        print(f"Total applications to process: {len(self.priority_apps)}")
        print(f"Known awarded applications: {len(self.known_awarded)}")
        print()
        
        successful_apps = []
        successful_awarded = []
        failed = []
        
        for app_num in self.priority_apps:
            success = self.download_application(app_num)
            if success:
                if app_num in self.known_awarded:
                    successful_awarded.append(app_num)
                else:
                    successful_apps.append(app_num)
            else:
                failed.append(app_num)
            
            # Be respectful to the server
            time.sleep(0.5)
        
        print(f"\n📊 DOWNLOAD SUMMARY:")
        print(f"   ✅ Applications downloaded: {len(successful_apps)}")
        print(f"   🏆 Awarded projects downloaded: {len(successful_awarded)}")
        print(f"   ❌ Failed downloads: {len(failed)}")
        
        if successful_awarded:
            print(f"\n🏆 AWARDED PROJECTS DOWNLOADED:")
            for app_num in successful_awarded:
                file_path = self.awarded_dir / f"TDHCA_{app_num}.pdf"
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"   • TDHCA_{app_num}.pdf ({file_size_mb:.1f} MB) - AWARDED")
        
        if successful_apps:
            print(f"\n✅ APPLICATIONS DOWNLOADED (showing first 10):")
            for app_num in successful_apps[:10]:
                file_path = self.applications_dir / f"TDHCA_{app_num}.pdf"
                if file_path.exists():
                    file_size_mb = file_path.stat().st_size / (1024 * 1024)
                    print(f"   • TDHCA_{app_num}.pdf ({file_size_mb:.1f} MB)")
            if len(successful_apps) > 10:
                print(f"   • ... and {len(successful_apps) - 10} more applications")
        
        if failed:
            print(f"\n❌ FAILED DOWNLOADS (showing first 10):")
            for app_num in failed[:10]:
                print(f"   • TDHCA_{app_num} - Not available")
            if len(failed) > 10:
                print(f"   • ... and {len(failed) - 10} more failed downloads")
        
        return successful_apps + successful_awarded, failed
    
    def scan_application_range(self, start_num=24000, end_num=24999, sample_size=50):
        """Scan a range of application numbers to find available PDFs"""
        print(f"\n🔍 SCANNING TDHCA 2024 APPLICATION RANGE")
        print(f"Range: {start_num} to {end_num} (sampling {sample_size} applications)")
        print("=" * 60)
        
        # Sample applications across the range
        import random
        sample_apps = random.sample(range(start_num, end_num + 1), min(sample_size, end_num - start_num + 1))
        sample_apps.sort()
        
        available = []
        for app_num in sample_apps:
            url = f"{self.base_url}/{app_num}.pdf"
            try:
                response = requests.head(url, timeout=10)
                if response.status_code == 200:
                    available.append(str(app_num))
                    print(f"✅ Available: TDHCA {app_num}")
                else:
                    print(f"❌ Not found: TDHCA {app_num}")
            except:
                print(f"❌ Error checking: TDHCA {app_num}")
            
            time.sleep(0.3)  # Be respectful
        
        print(f"\n📊 SCAN RESULTS:")
        print(f"   • Applications scanned: {len(sample_apps)}")
        print(f"   • Applications available: {len(available)}")
        print(f"   • Availability rate: {len(available)/len(sample_apps)*100:.1f}%")
        
        if available:
            print(f"\n✅ AVAILABLE 2024 APPLICATIONS:")
            for app_num in available[:10]:  # Show first 10
                print(f"   • TDHCA {app_num}")
            if len(available) > 10:
                print(f"   • ... and {len(available) - 10} more")
        
        return available
    
    def add_awarded_application(self, app_num, project_name=None, developer=None, award_date=None):
        """Add an application to the awarded list and move file if needed"""
        self.known_awarded[app_num] = {
            "project_name": project_name or "TBD",
            "developer": developer or "TBD", 
            "award_date": award_date or "2024"
        }
        
        # Move file from applications to awarded directory if it exists
        app_file = self.applications_dir / f"TDHCA_{app_num}.pdf"
        awarded_file = self.awarded_dir / f"TDHCA_{app_num}.pdf"
        
        if app_file.exists() and not awarded_file.exists():
            import shutil
            shutil.move(str(app_file), str(awarded_file))
            print(f"✅ Moved TDHCA_{app_num}.pdf to awarded directory")
            
            # Create metadata for the awarded project
            self.create_awarded_metadata(app_num, awarded_file)
    
    def save_awarded_list(self):
        """Save the current awarded applications list to JSON"""
        awarded_list_file = self.base_dir / "2024_awarded_applications.json"
        with open(awarded_list_file, 'w') as f:
            import json
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "awarded_applications": self.known_awarded,
                "total_count": len(self.known_awarded)
            }, f, indent=2)
        print(f"✅ Saved awarded applications list to {awarded_list_file}")

def main():
    print("🏢 TDHCA 2024 APPLICATIONS ACQUISITION SYSTEM")
    print("=" * 65)
    print("Mission: Download 2024 TDHCA applications including 24600")
    print("URL Pattern: https://www.tdhca.state.tx.us/multifamily/docs/imaged/2024-4-TEBApps/{app_num}.pdf")
    print()
    
    downloader = TDHCA2024Downloader()
    
    # Download priority applications (including 24600)
    successful, failed = downloader.download_priority_applications()
    
    # Check if we got 24600 (awarded application)
    if "24600" in successful:
        print(f"\n🎯 SUCCESS: TDHCA Application 24600 downloaded!")
        file_path = downloader.awarded_dir / "TDHCA_24600.pdf"
        if file_path.exists():
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"📂 Location: {file_path}")
            print(f"📦 Size: {file_size_mb:.1f} MB")
            print(f"🏆 Status: AWARDED PROJECT (saved to awarded directory)")
        else:
            # Check if it's in applications directory
            file_path = downloader.applications_dir / "TDHCA_24600.pdf"
            if file_path.exists():
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"📂 Location: {file_path}")
                print(f"📦 Size: {file_size_mb:.1f} MB")
                print(f"📄 Status: APPLICATION (needs award status verification)")
    else:
        print(f"\n⚠️  TDHCA Application 24600 was not found at the expected URL")
        print(f"🔍 URL attempted: {downloader.base_url}/24600.pdf")
        
        # Scan for available applications in the range
        available = downloader.scan_application_range(24500, 24700, 20)
        
        if available:
            print(f"\n💡 ALTERNATIVE: Found {len(available)} available 2024 applications")
            print("Would you like to download any of these instead?")
    
    print(f"\n🏁 DOWNLOAD COMPLETE")
    print(f"📁 Applications saved to: {downloader.applications_dir}")
    print(f"🏆 Awarded projects saved to: {downloader.awarded_dir}")
    print(f"\n💡 ORGANIZATION NOTES:")
    print(f"   • All 2024 applications are saved separately from awarded projects")
    print(f"   • 24600 is currently marked as AWARDED (verify status as needed)")
    print(f"   • Add more awarded applications to known_awarded list as identified")

if __name__ == "__main__":
    main()