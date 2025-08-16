#!/usr/bin/env python3
"""
Export CTCAC Map to PDF - General Purpose Function
Quick utility to export any CTCAC analysis to printable PDF format
"""

from ctcac_pdf_exporter import create_printable_map, export_to_pdf
from ctcac_parcel_boundary_mapper import analyze_site_with_parcel_boundary

def export_ctcac_map_to_pdf(parcel_corners, project_name, project_address, 
                           output_filename=None, **analysis_kwargs):
    """
    Export any CTCAC site analysis to printable PDF format
    
    Args:
        parcel_corners: Dict with 'nw', 'ne', 'sw', 'se' corners as (lat, lng) tuples
        project_name: Name of the project (e.g., "San Jacinto Vista II")
        project_address: Address (e.g., "202 E. Jarvis St., Perris, CA")  
        output_filename: Optional custom filename (default: auto-generated)
        **analysis_kwargs: Additional arguments for CTCAC analysis
        
    Returns:
        Path to exported HTML file (ready for PDF printing)
    """
    
    # Generate output filename if not provided
    if output_filename is None:
        safe_name = project_name.replace(" ", "_").replace(",", "").lower()
        output_filename = f'{safe_name}_ctcac_printable.html'
    
    print(f"🗺️  Generating CTCAC analysis for: {project_name}")
    print(f"📍 Location: {project_address}")
    
    # Run CTCAC analysis
    map_obj, results = analyze_site_with_parcel_boundary(
        parcel_corners=parcel_corners,
        address=project_address,
        site_name=project_name,
        **analysis_kwargs
    )
    
    print(f"📊 CTCAC Score: {results['total_points']}/15 points")
    
    # Create printable version
    print("🖨️  Creating printable map...")
    printable_map = create_printable_map(
        parcel_corners=parcel_corners,
        project_name=project_name,
        project_address=project_address,
        amenities_data=results,
        site_name=project_name
    )
    
    # Export to HTML
    export_path = export_to_pdf(printable_map, output_filename, open_browser=True)
    
    print("\n✅ PDF Export Complete!")
    print("📋 To create PDF:")
    print("   1. Browser will open automatically")
    print("   2. Press Ctrl+P (Cmd+P on Mac)")
    print("   3. Select 'Save as PDF'")
    print("   4. Choose 'Portrait' orientation")
    print("   5. Select 'US Letter' paper size")
    print("   6. Save the PDF")
    
    return export_path


# Example usage for different project types
def export_san_jacinto_pdf():
    """Example: San Jacinto Vista II"""
    parcel_corners = {
        'nw': (33.79377, -117.22184),
        'ne': (33.79376, -117.22050),
        'sw': (33.79213, -117.22173),
        'se': (33.79211, -117.22048)
    }
    
    return export_ctcac_map_to_pdf(
        parcel_corners=parcel_corners,
        project_name="San Jacinto Vista II",
        project_address="202 E. Jarvis St., Perris, CA",
        is_rural=False,
        project_type='at_risk',
        qualifying_development=True,
        new_construction=False,
        large_family=True
    )


def export_custom_project_pdf():
    """Template for custom projects"""
    
    # CUSTOMIZE THESE VALUES FOR YOUR PROJECT:
    parcel_corners = {
        'nw': (lat, lng),  # Replace with actual coordinates
        'ne': (lat, lng),  # Replace with actual coordinates  
        'sw': (lat, lng),  # Replace with actual coordinates
        'se': (lat, lng)   # Replace with actual coordinates
    }
    
    project_name = "Your Project Name"
    project_address = "Your Project Address"
    
    return export_ctcac_map_to_pdf(
        parcel_corners=parcel_corners,
        project_name=project_name,
        project_address=project_address,
        is_rural=False,                    # True if rural location
        project_type='family',             # 'family', 'senior', 'at_risk'
        qualifying_development=True,       # True for family developments
        new_construction=True,             # False for at-risk/rehab
        large_family=True                  # True for large family developments
    )


if __name__ == "__main__":
    # Run San Jacinto example
    export_san_jacinto_pdf()