#!/usr/bin/env python3
"""
Regenerate San Antonio and Tyler BOTNs using updated Belfort Ave template
"""

from botn_texas_dmarco_generator import TexasDMarcoBOTNGenerator
import pandas as pd

def regenerate_remaining_sites():
    """Regenerate only San Antonio and Tyler sites using updated template"""
    
    generator = TexasDMarcoBOTNGenerator()
    
    # Filter to only process San Antonio and Tyler sites (exclude Houston/Belfort)
    remaining_sites = generator.sites_data[
        ~generator.sites_data['Address'].str.contains('Bellfort', case=False, na=False)
    ].copy()
    
    print(f"Regenerating {len(remaining_sites)} sites using updated Belfort Ave template:")
    for _, site in remaining_sites.iterrows():
        print(f"  - {site['Address'].split(',')[0]} ({site['County']} County)")
    
    generated_files = []
    
    for idx, site in remaining_sites.iterrows():
        print(f"\\nProcessing Site {site['Site_Number']}: {site['Address']}")
        print(f"  County: {site['County']} (TDHCA Region {site['TDHCA_Region']})")
        print(f"  Units: {site['Estimated_Units']} at {site['Construction_Multiplier']}x cost modifier")
        
        output_path = generator.generate_site_botn(site)
        if output_path:
            generated_files.append(output_path)
    
    print(f"\\n=== REGENERATION COMPLETE ===")
    print(f"Generated {len(generated_files)} updated BOTN files:")
    for file_path in generated_files:
        import os
        print(f"  - {os.path.basename(file_path)}")
    
    return generated_files

if __name__ == "__main__":
    regenerate_remaining_sites()