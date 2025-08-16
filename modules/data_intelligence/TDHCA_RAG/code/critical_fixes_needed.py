#!/usr/bin/env python3
"""
Critical Fixes for TDHCA Extractor
Based on batch processing results analysis
"""

# FIX 1: County extraction always showing "Zip"
def fix_county_extraction(self, text: str, zip_code: str) -> str:
    """Fix county extraction - currently always returns 'Zip'"""
    
    # Texas ZIP to County mapping (partial example)
    zip_to_county = {
        '77520': 'Harris',
        '77521': 'Harris', 
        '77020': 'Harris',
        '78701': 'Travis',
        '75001': 'Dallas',
        # Add complete mapping or use spatial join
    }
    
    # Try direct extraction first
    county_patterns = [
        r'County[:\s]+([A-Za-z\s]+)(?=\s+(?:ZIP|Zip))',
        r'([A-Za-z\s]+)\s+County',
    ]
    
    for pattern in county_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            county = match.group(1).strip()
            if county and county.lower() not in ['zip', 'urban', 'rural']:
                return county
    
    # Fallback to ZIP mapping
    if zip_code and zip_code[:5] in zip_to_county:
        return zip_to_county[zip_code[:5]]
    
    return "Unknown"  # Better than "Zip"


# FIX 2: Project name showing "Property City ProgramControl began"
def fix_project_name_pattern(self, text: str) -> str:
    """Fix project name extraction to avoid generic text"""
    
    # Exclude these generic patterns
    exclude_patterns = [
        r'Property\s+City\s+ProgramControl',
        r'For\s+Applicants\s+who',
        r'Application\s+Number',
    ]
    
    # Better project name patterns
    name_patterns = [
        # Specific project name fields
        r'Project\s+Name[:\s]+([A-Za-z0-9\s&\'-]{5,50})(?=\s*\n)',
        r'Development\s+Name[:\s]+([A-Za-z0-9\s&\'-]{5,50})(?=\s*\n)',
        r'Property\s+Name[:\s]+([A-Za-z0-9\s&\'-]{5,50})(?=\s*\n)',
        
        # Names with "Apartments" or similar
        r'([A-Za-z\s]+(?:Apartments|Villas|Place|Court|Terrace|Park))\b',
        
        # Names in headers/titles
        r'^\s*([A-Z][A-Za-z\s&\'-]{5,40}[A-Za-z])\s*$',
    ]
    
    candidates = []
    
    for pattern in name_patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        for match in matches:
            match = match.strip()
            
            # Skip if contains excluded patterns
            if any(re.search(exc, match, re.IGNORECASE) for exc in exclude_patterns):
                continue
            
            # Skip generic words
            if match.lower() in ['property', 'city', 'county', 'urban', 'rural']:
                continue
                
            # Score based on quality
            score = 0
            if 'apartment' in match.lower() or 'villa' in match.lower():
                score += 10
            if len(match.split()) >= 2:  # Multi-word names
                score += 5
            
            candidates.append((match, score))
    
    # Return highest scoring candidate
    if candidates:
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    
    return ""


# FIX 3: Address comma insertion issue
def fix_address_parsing(self, text: str) -> tuple:
    """Fix address extraction to prevent comma insertion"""
    
    # Clean address patterns
    address_patterns = [
        # Standard address format
        r'(\d{3,5}\s+[A-Za-z0-9\s]+(?:Drive|Dr|Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Parkway|Pkwy|Way|Lane|Ln|Court|Ct)\.?)',
        
        # Property Address field
        r'Property\s+Address[:\s]+(\d+\s+[A-Za-z0-9\s]+)',
        
        # Site Address field  
        r'Site\s+Address[:\s]+(\d+\s+[A-Za-z0-9\s]+)',
    ]
    
    street = ""
    city = ""
    zip_code = ""
    
    for pattern in address_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean the match - remove extra spaces, fix commas
            cleaned = ' '.join(match.split())  # Normalize spaces
            cleaned = cleaned.replace(' ,', ',').replace(', ', ' ')  # Fix comma issues
            
            # Validate it looks like an address
            if re.match(r'\d+\s+[A-Za-z]', cleaned):
                street = cleaned
                break
    
    # Extract city and ZIP separately
    city_zip_pattern = r'([A-Za-z\s]+),?\s+TX\s+(\d{5})'
    matches = re.findall(city_zip_pattern, text, re.IGNORECASE)
    if matches:
        city = matches[0][0].strip().replace(',', '')
        zip_code = matches[0][1]
    
    return street, city, zip_code


# FIX 4: Add retry logic for timeout PDFs
def process_with_retry(self, pdf_path, max_retries=3):
    """Process PDF with retry logic for timeouts"""
    
    for attempt in range(max_retries):
        try:
            # Try normal extraction
            result = self.process_application_improved(pdf_path)
            if result and result.project_name:
                return result
                
            # If failed, try with reduced page limit
            if attempt > 0:
                self.logger.info(f"Retry {attempt+1}: Using reduced extraction")
                result = self.process_application_quick(pdf_path, max_pages=50)
                if result:
                    return result
                    
        except Exception as e:
            self.logger.warning(f"Attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                
    return None


# FIX 5: Validate geocoding results
def validate_geocoding(self, lat: float, lon: float, state: str = "TX") -> bool:
    """Validate geocoding results are in correct region"""
    
    # Texas bounding box (approximate)
    texas_bounds = {
        'min_lat': 25.83,
        'max_lat': 36.5,
        'min_lon': -106.65,
        'max_lon': -93.5
    }
    
    # Check if coordinates are within Texas
    if state == "TX":
        return (texas_bounds['min_lat'] <= lat <= texas_bounds['max_lat'] and
                texas_bounds['min_lon'] <= lon <= texas_bounds['max_lon'])
    
    return True  # Assume valid for other states


print("Critical fixes identified and ready to implement!")
print("Priority order:")
print("1. Fix county extraction (always showing 'Zip')")
print("2. Fix project name patterns (generic text issue)")  
print("3. Fix address comma insertion")
print("4. Add retry logic for timeout PDFs")
print("5. Validate geocoding results")