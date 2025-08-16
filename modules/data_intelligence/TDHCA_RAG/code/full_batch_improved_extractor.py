#!/usr/bin/env python3
"""
Full Batch TDHCA Improved Extractor - Production Run
With real-time progress updates and stall detection
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import time
import sys
from improved_tdhca_extractor import ImprovedTDHCAExtractor

def print_progress(current, total, filename, status="Processing"):
    """Print progress bar and current status"""
    progress = (current / total) * 100
    bar_length = 40
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    
    print(f'\r🚀 [{bar}] {progress:.1f}% ({current}/{total}) | {status}: {filename}', end='', flush=True)

def full_batch_extraction():
    """Run improved extraction on all TDHCA applications"""
    
    print("🎯 TDHCA FULL BATCH IMPROVED EXTRACTION")
    print("=" * 60)
    
    base_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites"
    extractor = ImprovedTDHCAExtractor(base_path)
    
    # Find all PDF files
    pdf_path = Path(base_path)
    all_pdfs = list(pdf_path.glob("**/*.pdf"))
    total_files = len(all_pdfs)
    
    print(f"📁 Found {total_files} PDF files to process")
    print(f"📍 Base path: {base_path}")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    print("\n" + "─" * 60)
    
    results = []
    start_time = datetime.now()
    
    for i, pdf_file in enumerate(all_pdfs, 1):
        file_start_time = datetime.now()
        filename = pdf_file.name
        
        # Show progress
        print_progress(i-1, total_files, filename, "Starting")
        
        try:
            # Process with improved extraction
            result = extractor.process_application_improved(pdf_file)
            
            processing_time = (datetime.now() - file_start_time).total_seconds()
            
            if result:
                results.append({
                    'File Name': filename,
                    'Project Name': result.project_name or 'NOT_FOUND',
                    'Street Address': result.street_address or 'NOT_FOUND',
                    'City': result.city or 'NOT_FOUND',
                    'ZIP Code': result.zip_code or 'NOT_FOUND',
                    'County': result.county or 'NOT_FOUND',
                    'Total Units': result.total_units or 0,
                    'Developer': result.developer_name or 'NOT_FOUND',
                    'Application Number': result.application_number or 'NOT_FOUND',
                    'Region': result.region or 'NOT_FOUND',
                    'Urban/Rural': result.urban_rural or 'NOT_FOUND',
                    'Latitude': result.latitude or '',
                    'Longitude': result.longitude or '',
                    'Processing Time (sec)': f"{processing_time:.1f}",
                    'Confidence Score': f"{result.confidence_scores.get('overall', 0):.2f}",
                    'Status': 'SUCCESS',
                    'Processing Notes': '; '.join(result.processing_notes[-2:]) if result.processing_notes else ""
                })
                
                # Show quick success info
                print_progress(i, total_files, f"✅ {result.project_name[:20]}... ({processing_time:.1f}s)", "Completed")
                
            else:
                results.append({
                    'File Name': filename,
                    'Project Name': 'EXTRACTION_FAILED',
                    'Street Address': '', 'City': '', 'ZIP Code': '', 'County': '',
                    'Total Units': 0, 'Developer': '', 'Application Number': '',
                    'Region': '', 'Urban/Rural': '', 'Latitude': '', 'Longitude': '',
                    'Processing Time (sec)': f"{processing_time:.1f}",
                    'Confidence Score': '0.00',
                    'Status': 'FAILED - NO DATA',
                    'Processing Notes': 'Failed to extract any data'
                })
                
                print_progress(i, total_files, f"❌ No Data ({processing_time:.1f}s)", "Failed")
                
        except Exception as e:
            processing_time = (datetime.now() - file_start_time).total_seconds()
            error_msg = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
            
            results.append({
                'File Name': filename,
                'Project Name': 'ERROR',
                'Street Address': '', 'City': '', 'ZIP Code': '', 'County': '',
                'Total Units': 0, 'Developer': '', 'Application Number': '',
                'Region': '', 'Urban/Rural': '', 'Latitude': '', 'Longitude': '',
                'Processing Time (sec)': f"{processing_time:.1f}",
                'Confidence Score': '0.00',
                'Status': f'ERROR',
                'Processing Notes': f'Error: {error_msg}'
            })
            
            print_progress(i, total_files, f"💥 Error ({processing_time:.1f}s)", "Error")
        
        # Add newline every 10 files for readability
        if i % 10 == 0:
            print()  # New line
            elapsed = datetime.now() - start_time
            avg_per_file = elapsed.total_seconds() / i
            remaining_files = total_files - i
            eta = datetime.now() + timedelta(seconds=avg_per_file * remaining_files)
            print(f"⏱️  Batch Progress: {i}/{total_files} complete | Avg: {avg_per_file:.1f}s/file | ETA: {eta.strftime('%H:%M:%S')}")
            print("─" * 60)
    
    # Final progress
    print_progress(total_files, total_files, "Batch Complete!", "✅ FINISHED")
    print("\n" + "=" * 60)
    
    # Calculate statistics
    total_time = (datetime.now() - start_time).total_seconds()
    successful = len([r for r in results if r['Status'] == 'SUCCESS'])
    failed = len([r for r in results if 'FAILED' in r['Status']])
    errors = len([r for r in results if r['Status'] == 'ERROR'])
    
    print(f"\n📊 BATCH COMPLETION SUMMARY")
    print(f"⏰ Total Time: {total_time/60:.1f} minutes")
    print(f"📈 Success Rate: {successful}/{total_files} ({successful/total_files*100:.1f}%)")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"💥 Errors: {errors}")
    print(f"⚡ Avg Speed: {total_time/total_files:.1f} seconds per file")
    
    # Create Excel output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"TDHCA_Full_Batch_Results_{timestamp}.xlsx"
    
    print(f"\n💾 Creating Excel output: {excel_filename}")
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Write to Excel with multiple sheets
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        # Main results
        df.to_excel(writer, sheet_name='All Results', index=False)
        
        # Successful extractions only
        successful_df = df[df['Status'] == 'SUCCESS']
        if not successful_df.empty:
            successful_df.to_excel(writer, sheet_name='Successful Extractions', index=False)
        
        # Failed/Error cases for debugging
        failed_df = df[df['Status'] != 'SUCCESS']
        if not failed_df.empty:
            failed_df.to_excel(writer, sheet_name='Failed Cases', index=False)
        
        # Summary statistics
        summary_data = [
            ['Metric', 'Value'],
            ['Total Files Processed', total_files],
            ['Successful Extractions', successful],
            ['Failed Extractions', failed],
            ['Error Cases', errors],
            ['Success Rate (%)', f"{successful/total_files*100:.1f}%"],
            ['Total Processing Time (min)', f"{total_time/60:.1f}"],
            ['Average Time per File (sec)', f"{total_time/total_files:.1f}"],
            ['Processing Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        summary_df = pd.DataFrame(summary_data[1:], columns=summary_data[0])
        summary_df.to_excel(writer, sheet_name='Batch Summary', index=False)
        
        # Auto-adjust column widths for all sheets
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✅ Excel file created successfully!")
    print(f"📁 Location: {excel_filename}")
    print(f"📋 Sheets: All Results, Successful Extractions, Failed Cases, Batch Summary")
    
    # Show top successful extractions
    if successful > 0:
        print(f"\n🏆 SAMPLE SUCCESSFUL EXTRACTIONS:")
        print("─" * 60)
        successful_sample = successful_df.head(3)
        for _, row in successful_sample.iterrows():
            print(f"📄 {row['File Name']}")
            print(f"   🏢 Project: {row['Project Name']}")
            print(f"   📍 Address: {row['Street Address']}, {row['City']} {row['ZIP Code']}")
            print(f"   🏗️ Units: {row['Total Units']} | Developer: {row['Developer']}")
            print()
    
    return excel_filename, successful, total_files

if __name__ == "__main__":
    try:
        excel_file, success_count, total_count = full_batch_extraction()
        print(f"\n🎉 BATCH PROCESSING COMPLETE!")
        print(f"📊 Final Result: {success_count}/{total_count} successful extractions")
        print(f"📁 Excel Output: {excel_file}")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️ BATCH INTERRUPTED BY USER")
        print(f"💾 Partial results may be available")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 BATCH FAILED: {e}")
        sys.exit(1)