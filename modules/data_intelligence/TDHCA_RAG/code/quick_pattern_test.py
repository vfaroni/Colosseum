#!/usr/bin/env python3
"""
Quick test of extraction patterns without full processing
"""

from improved_tdhca_extractor import ImprovedTDHCAExtractor

def test_extraction_patterns():
    """Test county and project name patterns on sample text"""
    
    extractor = ImprovedTDHCAExtractor("")
    
    # Sample text from debug analysis
    sample_text = """
    Property Name: Bay Terrace Apartments  
    Development Name: Property City ProgramControl began 
    
    City/State: Dallas, Dallas County, Texas
    Census Tract 122.10, Dallas County, Texas 48113 Dallas 3
    
    County: Harris    TX 77520
    Located in Harris County
    
    Property Name: Wyndham Park
    jeremy@resolutioncompanies.com
    Wyndham Park
    2700 Rollingbrook Dr
    """
    
    print("🧪 Quick Pattern Testing")
    print("=" * 50)
    
    # Test county extraction
    print("Testing County Extraction:")
    county = extractor._extract_county_improved(sample_text, "77520")
    print(f"County Result: '{county}' (should be Harris or Dallas, NOT 'Zip')")
    
    # Test another ZIP
    county2 = extractor._extract_county_improved(sample_text, "75001")
    print(f"County for 75001: '{county2}' (should be Dallas)")
    
    print()
    
    # Test project name extraction  
    print("Testing Project Name Extraction:")
    project_name = extractor._extract_project_name_improved(sample_text)
    print(f"Project Name: '{project_name}' (should avoid 'Property City ProgramControl')")
    
    print()
    
    # Test with problematic text
    bad_text = """
    Property Name: Property City ProgramControl began
    Development Name: For Applicants who participate  
    Application Number: 25427
    """
    
    print("Testing with Problematic Text:")
    bad_name = extractor._extract_project_name_improved(bad_text)
    print(f"Bad Text Result: '{bad_name}' (should be empty or good alternative)")
    
    print()
    
    # Test address extraction 
    print("Testing Address Extraction:")
    street, city, zip_code = extractor._extract_address_improved(sample_text)
    print(f"Address: '{street}', '{city}', '{zip_code}'")
    
    print()
    print("✅ Pattern testing complete!")

if __name__ == "__main__":
    test_extraction_patterns()