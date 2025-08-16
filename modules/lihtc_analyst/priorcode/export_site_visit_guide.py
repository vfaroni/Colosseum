#!/usr/bin/env python3
"""
Export D'Marco Site Visit Guide to Multiple Formats
Converts the markdown guide to PDF, HTML, and RTF for field reference

Author: LIHTC Analysis System
Date: June 26, 2025
"""

import markdown
import pdfkit
from datetime import datetime
import os
from pathlib import Path

def export_site_visit_guide():
    """Export the site visit guide to multiple formats"""
    
    # File paths
    base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code")
    md_file = base_path / "DMarco_Site_Visit_Guide_June2025.md"
    
    # Read the markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Create timestamp for file naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'toc'])
    
    # Add CSS styling for professional appearance
    html_styled = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>D'Marco Site Visit Guide - LIHTC Underwriting</title>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #2980b9;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 5px;
                margin-top: 30px;
            }}
            h3 {{
                color: #34495e;
                margin-top: 25px;
            }}
            h4 {{
                color: #7f8c8d;
                margin-top: 20px;
            }}
            .site-header {{
                background-color: #3498db;
                color: white;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .analysis-overview {{
                background-color: #ecf0f1;
                padding: 15px;
                border-left: 4px solid #3498db;
                margin: 15px 0;
            }}
            .critical-questions {{
                background-color: #fff3cd;
                padding: 15px;
                border-left: 4px solid #ffc107;
                margin: 15px 0;
            }}
            .broker-questions {{
                background-color: #d1ecf1;
                padding: 15px;
                border-left: 4px solid #17a2b8;
                margin: 15px 0;
            }}
            ul {{
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 8px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #3498db;
                color: white;
            }}
            .checklist {{
                background-color: #f8f9fa;
                padding: 15px;
                border: 1px solid #dee2e6;
                border-radius: 5px;
            }}
            .export-note {{
                background-color: #e8f5e8;
                padding: 15px;
                border-left: 4px solid #28a745;
                margin: 20px 0;
                font-style: italic;
            }}
            @media print {{
                body {{
                    background-color: white;
                }}
                .container {{
                    box-shadow: none;
                }}
            }}
            @media (max-width: 768px) {{
                body {{
                    padding: 10px;
                }}
                .container {{
                    padding: 15px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {html_content}
        </div>
    </body>
    </html>
    """
    
    # Save HTML file
    html_file = base_path / f"DMarco_Site_Visit_Guide_{timestamp}.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_styled)
    
    print(f"✅ HTML export complete: {html_file}")
    
    # Export to PDF (if pdfkit is available)
    try:
        pdf_file = base_path / f"DMarco_Site_Visit_Guide_{timestamp}.pdf"
        
        # PDF options for professional appearance
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',  
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        # Generate PDF from HTML
        pdfkit.from_string(html_styled, str(pdf_file), options=options)
        print(f"✅ PDF export complete: {pdf_file}")
        
    except Exception as e:
        print(f"⚠️  PDF export failed (wkhtmltopdf may not be installed): {e}")
        print("   Install with: brew install wkhtmltopdf")
    
    # Export to RTF (Rich Text Format)
    try:
        rtf_file = base_path / f"DMarco_Site_Visit_Guide_{timestamp}.rtf"
        
        # Convert markdown to RTF (simplified version)
        rtf_content = convert_md_to_rtf(md_content)
        
        with open(rtf_file, 'w', encoding='utf-8') as f:
            f.write(rtf_content)
        
        print(f"✅ RTF export complete: {rtf_file}")
        
    except Exception as e:
        print(f"⚠️  RTF export failed: {e}")
    
    # Create a quick access HTML file for mobile use
    mobile_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>D'Marco Site Visit - Mobile</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.5;
                color: #333;
                margin: 0;
                padding: 15px;
                font-size: 16px;
            }}
            h1 {{
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 10px;
            }}
            h2 {{
                color: #2980b9;
                font-size: 20px;
                margin-top: 25px;
                margin-bottom: 10px;
            }}
            h3 {{
                color: #34495e;
                font-size: 18px;
                margin-top: 20px;
            }}
            .site-summary {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                border-left: 4px solid #007bff;
            }}
            .questions {{
                background-color: #fff3cd;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
            }}
            ul {{
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 10px;
            }}
            .navigation {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                background-color: #007bff;
                color: white;
                padding: 10px 15px;
                border-radius: 25px;
                text-decoration: none;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            }}
        </style>
    </head>
    <body>
        {html_content}
        <a href="#top" class="navigation">↑ Top</a>
    </body>
    </html>
    """
    
    mobile_file = base_path / f"DMarco_Site_Visit_Mobile_{timestamp}.html"
    with open(mobile_file, 'w', encoding='utf-8') as f:
        f.write(mobile_html)
    
    print(f"✅ Mobile HTML export complete: {mobile_file}")
    
    # Summary
    print(f"\n📋 Site Visit Guide Export Summary:")
    print(f"   Original Markdown: {md_file}")
    print(f"   HTML (Desktop): {html_file}")
    print(f"   HTML (Mobile): {mobile_file}")
    if 'pdf_file' in locals():
        print(f"   PDF: {pdf_file}")
    if 'rtf_file' in locals():
        print(f"   RTF: {rtf_file}")
    
    return {
        'markdown': md_file,
        'html': html_file,
        'mobile': mobile_file,
        'pdf': pdf_file if 'pdf_file' in locals() else None,
        'rtf': rtf_file if 'rtf_file' in locals() else None
    }

def convert_md_to_rtf(md_content):
    """Convert markdown to RTF format (simplified)"""
    
    rtf_header = r"""{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}
{\colortbl;\red0\green0\blue0;\red0\green0\blue255;}
\f0\fs24 """
    
    rtf_footer = r"}"
    
    # Simple conversion - replace markdown syntax with RTF
    rtf_content = md_content
    
    # Headers
    rtf_content = rtf_content.replace('# ', r'\b\fs32 ')
    rtf_content = rtf_content.replace('## ', r'\b\fs28 ')
    rtf_content = rtf_content.replace('### ', r'\b\fs26 ')
    rtf_content = rtf_content.replace('#### ', r'\b\fs24 ')
    
    # Bold text
    rtf_content = rtf_content.replace('**', r'\b ')
    
    # Line breaks
    rtf_content = rtf_content.replace('\n', r'\par ')
    
    # Bullets (simplified)
    rtf_content = rtf_content.replace('- ', r'\bullet ')
    
    return rtf_header + rtf_content + rtf_footer

if __name__ == "__main__":
    print("🚀 Exporting D'Marco Site Visit Guide...")
    results = export_site_visit_guide()
    print("\n✅ Export complete! Files ready for D'Marco's site visit tomorrow.")