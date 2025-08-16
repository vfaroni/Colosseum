#!/usr/bin/env python3
"""
Create Excel sample of improved TDHCA extraction results
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from improved_tdhca_extractor import ImprovedTDHCAExtractor

def create_sample_excel():
    """Create Excel file with improved extraction results"""
    
    base_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites"
    extractor = ImprovedTDHCAExtractor(base_path)
    
    # Test files we know work well
    test_files = [
        "25427.pdf",  # Bay Terrace
        "25412.pdf",  # Wyndham Park
    ]
    
    # Also grab a few more for a better sample
    pdf_path = Path(base_path)
    all_pdfs = list(pdf_path.glob("**/*.pdf"))
    additional_files = [pdf.name for pdf in all_pdfs[:5] if pdf.name not in test_files]
    test_files.extend(additional_files[:3])  # Add 3 more for 5 total
    
    results = []
    
    print("🔧 Creating Excel sample with improved extraction...")
    print("=" * 60)
    
    for filename in test_files:
        print(f"\n📁 Processing {filename}")
        
        pdf_files = list(Path(base_path).glob(f"**/{filename}"))
        if pdf_files:
            try:
                # Use the improved extraction method
                result = extractor.process_application_improved(pdf_files[0])
                
                if result:
                    results.append({
                        'File Name': filename,
                        'Project Name': result.project_name,
                        'Street Address': result.street_address,
                        'City': result.city,
                        'ZIP Code': result.zip_code,
                        'County': result.county,
                        'Total Units': result.total_units,
                        'Developer': result.developer_name,
                        'Application Number': result.application_number,
                        'Region': result.region,
                        'Urban/Rural': result.urban_rural,
                        'Latitude': result.latitude,
                        'Longitude': result.longitude,
                        'Confidence Score': f"{result.confidence_scores.get('overall', 0):.2f}",
                        'Processing Notes': '; '.join(result.processing_notes[-3:]) if result.processing_notes else ""
                    })
                    
                    print(f"  ✅ Project: '{result.project_name}'")
                    print(f"  📍 Address: '{result.street_address}', {result.city} {result.zip_code}")
                    print(f"  🏢 Units: {result.total_units}")
                else:
                    results.append({
                        'File Name': filename,
                        'Project Name': 'EXTRACTION_FAILED',
                        'Street Address': '',
                        'City': '',
                        'ZIP Code': '',
                        'County': '',
                        'Total Units': 0,
                        'Developer': '',
                        'Application Number': '',
                        'Region': '',
                        'Urban/Rural': '',
                        'Latitude': '',
                        'Longitude': '',
                        'Confidence Score': '0.00',
                        'Processing Notes': 'Failed to extract data'
                    })
                    print(f"  ❌ Extraction failed")
                    
            except Exception as e:
                results.append({
                    'File Name': filename,
                    'Project Name': 'ERROR',
                    'Street Address': '',
                    'City': '',
                    'ZIP Code': '',
                    'County': '',
                    'Total Units': 0,
                    'Developer': '',
                    'Application Number': '',
                    'Region': '',
                    'Urban/Rural': '',
                    'Latitude': '',
                    'Longitude': '',
                    'Confidence Score': '0.00',
                    'Processing Notes': f'Error: {str(e)}'
                })
                print(f"  ❌ Error: {e}")
        else:
            print(f"  ❌ File not found: {filename}")
    
    # Create DataFrame and Excel file
    df = pd.DataFrame(results)
    
    # Create timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"improved_tdhca_extraction_sample_{timestamp}.xlsx"
    
    # Write to Excel with formatting
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='TDHCA Extraction Results', index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['TDHCA Extraction Results']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"\n✅ Excel file created: {excel_filename}")
    print(f"📊 Processed {len(results)} applications")
    print(f"📈 Success rate: {len([r for r in results if r['Project Name'] not in ['EXTRACTION_FAILED', 'ERROR']])}/{len(results)}")
    
    return excel_filename

if __name__ == "__main__":
    create_sample_excel()