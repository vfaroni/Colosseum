#!/usr/bin/env python3
"""
Simple Export of D'Marco Site Visit Guide
Creates HTML and RTF versions without additional dependencies

Author: LIHTC Analysis System  
Date: June 26, 2025
"""

import re
from datetime import datetime
from pathlib import Path

def convert_markdown_to_html(md_content):
    """Convert markdown to HTML using basic regex replacements"""
    html = md_content
    
    # Headers
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # Bold text
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    
    # Lists
    html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # Checkboxes
    html = re.sub(r'- \[ \] (.*?)$', r'<li>☐ \1</li>', html, flags=re.MULTILINE)
    
    # Wrap consecutive <li> elements in <ul>
    html = re.sub(r'(<li>.*?</li>(?:\s*<li>.*?</li>)*)', r'<ul>\1</ul>', html, flags=re.DOTALL)
    
    # Line breaks
    html = html.replace('\n\n', '</p><p>')
    html = '<p>' + html + '</p>'
    
    # Clean up empty paragraphs
    html = re.sub(r'<p>\s*</p>', '', html)
    
    return html

def create_professional_html(content, title="D'Marco Site Visit Guide"):
    """Wrap content in professional HTML template"""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a365d;
            border-bottom: 3px solid #3182ce;
            padding-bottom: 15px;
            font-size: 2.5em;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #2b6cb0;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        h3 {{
            color: #2d3748;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.4em;
        }}
        h4 {{
            color: #4a5568;
            margin-top: 25px;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}
        p {{
            margin-bottom: 15px;
            font-size: 1.05em;
        }}
        ul {{
            margin-bottom: 20px;
            padding-left: 25px;
        }}
        li {{
            margin-bottom: 8px;
            font-size: 1.05em;
        }}
        strong {{
            color: #1a365d;
            font-weight: 600;
        }}
        .site-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 25px 0;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        .highlight-box {{
            background-color: #fff3cd;
            border-left: 5px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }}
        .info-box {{
            background-color: #d1ecf1;
            border-left: 5px solid #17a2b8;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }}
        .success-box {{
            background-color: #d4edda;
            border-left: 5px solid #28a745;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }}
        .navigation {{
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #3182ce;
            color: white;
            padding: 12px 18px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(49, 130, 206, 0.4);
            z-index: 1000;
        }}
        .navigation:hover {{
            background-color: #2c5aa0;
            text-decoration: none;
            color: white;
        }}
        @media print {{
            body {{ background-color: white; }}
            .container {{ box-shadow: none; }}
        }}
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            .container {{ padding: 20px; }}
            h1 {{ font-size: 2em; }}
            h2 {{ font-size: 1.5em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
    <a href="#top" class="navigation">↑ Top</a>
</body>
</html>
"""

def export_site_visit_guide():
    """Export the site visit guide to HTML and RTF formats"""
    
    # File paths
    base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code")
    md_file = base_path / "DMarco_Site_Visit_Guide_June2025.md"
    
    # Read the markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Create timestamp for file naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Convert to HTML
    html_content = convert_markdown_to_html(md_content)
    professional_html = create_professional_html(html_content)
    
    # Save HTML file
    html_file = base_path / f"DMarco_Site_Visit_Guide_{timestamp}.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(professional_html)
    
    print(f"✅ HTML export complete: {html_file}")
    
    # Create mobile-optimized version
    mobile_html = create_professional_html(html_content, "D'Marco Site Visit - Mobile")
    mobile_html = mobile_html.replace('max-width: 1200px;', 'max-width: 100%;')
    mobile_html = mobile_html.replace('padding: 40px;', 'padding: 15px;')
    
    mobile_file = base_path / f"DMarco_Site_Visit_Mobile_{timestamp}.html"
    with open(mobile_file, 'w', encoding='utf-8') as f:
        f.write(mobile_html)
    
    print(f"✅ Mobile HTML export complete: {mobile_file}")
    
    # Create simple RTF version
    rtf_content = create_simple_rtf(md_content)
    rtf_file = base_path / f"DMarco_Site_Visit_Guide_{timestamp}.rtf"
    
    with open(rtf_file, 'w', encoding='utf-8') as f:
        f.write(rtf_content)
    
    print(f"✅ RTF export complete: {rtf_file}")
    
    # Create a text version for easy copying
    txt_file = base_path / f"DMarco_Site_Visit_Guide_{timestamp}.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✅ Text export complete: {txt_file}")
    
    print(f"\n📋 Site Visit Guide Export Summary:")
    print(f"   📄 Original Markdown: {md_file.name}")
    print(f"   🌐 HTML (Desktop): {html_file.name}")
    print(f"   📱 HTML (Mobile): {mobile_file.name}")
    print(f"   📄 RTF (Word): {rtf_file.name}")
    print(f"   📝 Text: {txt_file.name}")
    print(f"\n🎯 Ready for D'Marco's site visit tomorrow!")
    
    return {
        'markdown': md_file,
        'html': html_file,
        'mobile': mobile_file,
        'rtf': rtf_file,
        'text': txt_file
    }

def create_simple_rtf(md_content):
    """Create a simple RTF version of the markdown content"""
    
    # RTF header
    rtf = r"""{\rtf1\ansi\ansicpg1252\deff0\nouicompat\deflang1033{\fonttbl{\f0\fnil\fcharset0 Calibri;}}
{\*\generator Riched20 10.0.19041}\viewkind4\uc1 
\pard\sa200\sl276\slmult1\f0\fs22\lang9 """
    
    # Convert content
    content = md_content
    
    # Headers
    content = re.sub(r'^# (.*?)$', r'\\b\\fs32 \1\\b0\\fs22\\par\\par', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.*?)$', r'\\b\\fs28 \1\\b0\\fs22\\par\\par', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.*?)$', r'\\b\\fs26 \1\\b0\\fs22\\par', content, flags=re.MULTILINE)
    content = re.sub(r'^#### (.*?)$', r'\\b\\fs24 \1\\b0\\fs22\\par', content, flags=re.MULTILINE)
    
    # Bold text
    content = re.sub(r'\*\*(.*?)\*\*', r'\\b \1\\b0', content)
    
    # Lists
    content = re.sub(r'^- (.*?)$', r'\\bullet \1\\par', content, flags=re.MULTILINE)
    content = re.sub(r'^- \\[ \\] (.*?)$', r'\\u9744? \1\\par', content, flags=re.MULTILINE)
    
    # Line breaks
    content = content.replace('\n\n', '\\par\\par')
    content = content.replace('\n', '\\par')
    
    # RTF footer
    rtf += content + r"}"
    
    return rtf

if __name__ == "__main__":
    print("🚀 Exporting D'Marco Site Visit Guide...")
    results = export_site_visit_guide()
    print("\n✅ Export complete! All formats ready for tomorrow's site visit.")