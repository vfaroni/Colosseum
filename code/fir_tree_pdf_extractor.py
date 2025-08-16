#!/usr/bin/env python3
"""
Safe PDF extraction for Fir Tree Park Apartments financial report
Using PyPDF2 for safe text extraction
"""

import PyPDF2
import re
import sys
from pathlib import Path

def extract_financial_data(pdf_path):
    """
    Extract key financial data from Fir Tree monthly report PDF
    Focus on rent roll, expenses, NOI, and OCAF information
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            all_text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    all_text += f"\n--- PAGE {page_num + 1} ---\n"
                    all_text += page_text
                except Exception as e:
                    print(f"Error extracting page {page_num + 1}: {e}")
                    continue
            
            return all_text
            
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def analyze_financial_content(text):
    """
    Analyze extracted text and identify key financial sections
    """
    if not text:
        return "No content extracted from PDF"
    
    # Look for key financial indicators
    rent_patterns = [
        r'rent\s*roll',
        r'unit\s*rent',
        r'occupancy',
        r'vacant',
        r'occupied',
        r'\$\d+,?\d*\.\d{2}',  # Dollar amounts
    ]
    
    expense_patterns = [
        r'operating\s*expense',
        r'maintenance',
        r'utilities',
        r'insurance',
        r'property\s*tax',
        r'management\s*fee',
    ]
    
    noi_patterns = [
        r'net\s*operating\s*income',
        r'NOI',
        r'total\s*income',
        r'total\s*expense',
    ]
    
    ocaf_patterns = [
        r'OCAF',
        r'operating\s*cost\s*adjustment',
        r'rent\s*increase',
        r'adjustment',
    ]
    
    # Extract relevant sections
    analysis = {
        'rent_info': [],
        'expense_info': [],
        'noi_info': [],
        'ocaf_info': [],
        'full_text': text
    }
    
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        if not line_lower:
            continue
            
        # Check for rent roll information
        for pattern in rent_patterns:
            if re.search(pattern, line_lower, re.IGNORECASE):
                context = get_context_lines(lines, i, 3)
                analysis['rent_info'].append(context)
                break
        
        # Check for expense information  
        for pattern in expense_patterns:
            if re.search(pattern, line_lower, re.IGNORECASE):
                context = get_context_lines(lines, i, 3)
                analysis['expense_info'].append(context)
                break
        
        # Check for NOI information
        for pattern in noi_patterns:
            if re.search(pattern, line_lower, re.IGNORECASE):
                context = get_context_lines(lines, i, 3)
                analysis['noi_info'].append(context)
                break
        
        # Check for OCAF information
        for pattern in ocaf_patterns:
            if re.search(pattern, line_lower, re.IGNORECASE):
                context = get_context_lines(lines, i, 3)
                analysis['ocaf_info'].append(context)
                break
    
    return analysis

def get_context_lines(lines, center_idx, context_size):
    """Get surrounding lines for context"""
    start = max(0, center_idx - context_size)
    end = min(len(lines), center_idx + context_size + 1)
    return '\n'.join(lines[start:end])

def main():
    pdf_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Deals (Good Clean)/Fir_Tree-Shelton_WA/Due_Diligence/1742981 fi p211 Monthly Report.pdf"
    
    if not Path(pdf_path).exists():
        print(f"PDF file not found: {pdf_path}")
        sys.exit(1)
    
    print("Extracting financial data from Fir Tree monthly report...")
    
    # Extract raw text
    raw_text = extract_financial_data(pdf_path)
    
    if raw_text:
        # Analyze content for key financial data
        analysis = analyze_financial_content(raw_text)
        
        # Create formatted output
        output_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/fir_tree_financial_analysis.md"
        
        with open(output_path, 'w') as f:
            f.write("# Fir Tree Park Apartments - Monthly Financial Report Analysis\n\n")
            f.write("**Source**: 1742981 fi p211 Monthly Report.pdf\n")
            f.write("**Extracted**: " + str(Path().resolve()) + "\n\n")
            
            f.write("## 🏠 RENT ROLL INFORMATION\n\n")
            if analysis['rent_info']:
                for i, info in enumerate(analysis['rent_info'][:5]):  # Limit to first 5
                    f.write(f"### Rent Data {i+1}\n")
                    f.write("```\n" + info + "\n```\n\n")
            else:
                f.write("No rent roll data patterns found.\n\n")
            
            f.write("## 💰 OPERATING EXPENSE DETAILS\n\n")
            if analysis['expense_info']:
                for i, info in enumerate(analysis['expense_info'][:5]):
                    f.write(f"### Expense Data {i+1}\n")
                    f.write("```\n" + info + "\n```\n\n")
            else:
                f.write("No operating expense patterns found.\n\n")
            
            f.write("## 📊 NET OPERATING INCOME FIGURES\n\n")
            if analysis['noi_info']:
                for i, info in enumerate(analysis['noi_info'][:5]):
                    f.write(f"### NOI Data {i+1}\n")
                    f.write("```\n" + info + "\n```\n\n")
            else:
                f.write("No NOI patterns found.\n\n")
            
            f.write("## 📈 OCAF RENT ADJUSTMENTS\n\n")
            if analysis['ocaf_info']:
                for i, info in enumerate(analysis['ocaf_info'][:5]):
                    f.write(f"### OCAF Data {i+1}\n")
                    f.write("```\n" + info + "\n```\n\n")
            else:
                f.write("No OCAF adjustment patterns found.\n\n")
            
            # Include sample of raw text for manual review
            f.write("## 📄 RAW TEXT SAMPLE (First 2000 characters)\n\n")
            f.write("```\n" + raw_text[:2000] + "\n...\n```\n\n")
            
            f.write("---\n")
            f.write("*Analysis completed for T-12 update and HTML rent tabs*\n")
        
        print(f"Analysis saved to: {output_path}")
        print("Key sections extracted for financial review.")
        
    else:
        print("Failed to extract content from PDF")

if __name__ == "__main__":
    main()