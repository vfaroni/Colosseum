#!/usr/bin/env python3
"""
Test Docling's native table extraction capabilities
Let's see what Docling can extract WITHOUT LLMs first
"""

import json
from pathlib import Path
from docling.document_converter import DocumentConverter
import pandas as pd

def test_docling_extraction():
    """Test Docling's native extraction capabilities"""
    
    print("=" * 60)
    print("🔬 TESTING DOCLING'S NATIVE EXTRACTION")
    print("=" * 60)
    
    # Setup paths
    base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Deals (Good Clean)/Fir_Tree-Shelton_WA/Due_Diligence")
    
    # Configure Docling for maximum extraction
    # Using default converter - will handle tables automatically
    converter = DocumentConverter()
    
    # Test on the audited financials
    audit_path = base_dir / "Fir Tree Park Audited Financial Statements (final 2024).pdf"
    
    print(f"\n📄 Processing: {audit_path.name}")
    print("-" * 40)
    
    # Convert document
    result = converter.convert(str(audit_path))
    
    # 1. Check what Docling found
    print("\n📊 DOCLING EXTRACTION RESULTS:")
    print(f"Document title: {result.document.name}")
    
    # 2. Extract tables if found
    tables = []
    for item, level in result.document.iterate_items():
        if hasattr(item, 'table') and item.table:
            tables.append(item)
            print(f"\n📋 Found table with {len(item.table.rows)} rows")
            
    print(f"\nTotal tables found: {len(tables)}")
    
    # 3. Export to different formats
    print("\n📁 EXPORT FORMATS:")
    
    # Markdown export
    markdown_text = result.document.export_to_markdown()
    print(f"Markdown length: {len(markdown_text)} characters")
    
    # Save markdown for inspection
    output_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/lihtc_analyst/fir_tree_output")
    output_dir.mkdir(exist_ok=True)
    
    md_file = output_dir / "docling_extracted_financials.md"
    with open(md_file, 'w') as f:
        f.write(markdown_text)
    print(f"Saved markdown to: {md_file}")
    
    # 4. Look for financial data in tables
    print("\n💰 SEARCHING FOR FINANCIAL DATA IN TABLES:")
    
    financial_keywords = [
        'revenue', 'income', 'hap', 'section 8', 'rental',
        'expense', 'operating', 'noi', 'net income',
        'assets', 'liabilities', 'cash', 'reserves'
    ]
    
    for idx, table_item in enumerate(tables[:5]):  # First 5 tables
        print(f"\n📊 Table {idx + 1}:")
        
        # Convert table to text for analysis
        table_text = str(table_item.table)
        
        # Check for financial keywords
        found_keywords = []
        for keyword in financial_keywords:
            if keyword.lower() in table_text.lower():
                found_keywords.append(keyword)
        
        if found_keywords:
            print(f"  Found financial terms: {', '.join(found_keywords)}")
            
            # Try to extract the table data
            if hasattr(table_item.table, 'rows'):
                print(f"  Table has {len(table_item.table.rows)} rows")
                
                # Print first few rows
                for row_idx, row in enumerate(table_item.table.rows[:3]):
                    print(f"    Row {row_idx}: {row}")
    
    # 5. Search for specific financial statement sections
    print("\n🔍 SEARCHING TEXT FOR KEY FINANCIAL SECTIONS:")
    
    text_lower = markdown_text.lower()
    
    # Look for specific statements
    statements = {
        "Statement of Financial Position": "financial position" in text_lower,
        "Statement of Activities": "statement of activities" in text_lower,
        "Statement of Cash Flows": "cash flows" in text_lower,
        "Balance Sheet": "balance sheet" in text_lower,
        "Income Statement": "income statement" in text_lower,
        "Notes to Financial Statements": "notes to" in text_lower
    }
    
    for statement, found in statements.items():
        status = "✅" if found else "❌"
        print(f"  {status} {statement}")
    
    # 6. Extract specific values using text search
    print("\n📈 ATTEMPTING TO EXTRACT SPECIFIC VALUES:")
    
    import re
    
    # Pattern to find dollar amounts
    dollar_pattern = r'\$[\d,]+(?:\.\d{2})?'
    
    # Find all dollar amounts
    dollar_amounts = re.findall(dollar_pattern, markdown_text)
    
    if dollar_amounts:
        print(f"  Found {len(dollar_amounts)} dollar amounts")
        print(f"  Largest amounts: {sorted(set(dollar_amounts), key=lambda x: float(x.replace('$','').replace(',','')), reverse=True)[:5]}")
    
    # Look for specific line items
    patterns = {
        "Total Revenue": r'total revenue[:\s]+\$?([\d,]+)',
        "Rental Income": r'rental income[:\s]+\$?([\d,]+)',
        "HAP/Section 8": r'(?:hap|section 8|housing assistance)[:\s]+\$?([\d,]+)',
        "Net Operating Income": r'(?:noi|net operating income)[:\s]+\$?([\d,]+)',
        "Total Expenses": r'total expense[:\s]+\$?([\d,]+)'
    }
    
    for item, pattern in patterns.items():
        matches = re.findall(pattern, text_lower)
        if matches:
            print(f"  {item}: ${matches[0]}")
        else:
            print(f"  {item}: Not found with simple regex")
    
    # 7. Try DataFrame export if tables exist
    if tables:
        print("\n📊 CONVERTING TABLES TO DATAFRAMES:")
        
        for idx, table_item in enumerate(tables[:3]):
            try:
                # Extract table data
                if hasattr(table_item.table, 'rows'):
                    rows = []
                    for row in table_item.table.rows:
                        if hasattr(row, 'cells'):
                            row_data = [cell.text if hasattr(cell, 'text') else str(cell) for cell in row.cells]
                            rows.append(row_data)
                    
                    if rows:
                        df = pd.DataFrame(rows)
                        print(f"\n  Table {idx + 1} as DataFrame:")
                        print(f"  Shape: {df.shape}")
                        print(f"  First 3 rows:")
                        print(df.head(3))
                        
                        # Save to CSV
                        csv_file = output_dir / f"table_{idx + 1}.csv"
                        df.to_csv(csv_file, index=False)
                        print(f"  Saved to: {csv_file}")
                        
            except Exception as e:
                print(f"  Could not convert table {idx + 1}: {e}")
    
    return markdown_text, tables

def test_with_gpt_oss(markdown_text):
    """Now try with GPT-OSS on the Docling output"""
    
    print("\n" + "=" * 60)
    print("🤖 ENHANCING WITH GPT-OSS 20B")
    print("=" * 60)
    
    import requests
    
    # Use first 8000 chars of markdown
    text_chunk = markdown_text[:8000]
    
    # Focused prompt using Docling's structured output
    prompt = f"""<task>Extract financial data from this Docling-processed financial statement</task>

<context>
This is markdown output from Docling's document extraction. Tables may be formatted as markdown tables.
</context>

<extraction_targets>
Find these specific numbers:
1. Total Revenue or Total Income
2. Rental Income 
3. HAP Revenue or Section 8 Revenue
4. Total Operating Expenses
5. Net Operating Income (NOI) or Change in Net Assets
6. Cash and Cash Equivalents
7. Replacement Reserve balance
</extraction_targets>

<document>
{text_chunk}
</document>

<output>
Return only the JSON with numbers you find:
{{
  "total_revenue": number or null,
  "rental_income": number or null,  
  "hap_revenue": number or null,
  "total_expenses": number or null,
  "noi": number or null,
  "cash": number or null,
  "replacement_reserve": number or null
}}
</output>"""
    
    print("Calling GPT-OSS with Docling-extracted text...")
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                "model": "gpt-oss:20b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json().get('response', '')
            print(f"\nGPT-OSS Response: {result}")
            
            # Try to parse JSON
            import re
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, result)
            
            if matches:
                try:
                    extracted = json.loads(matches[0])
                    print("\n✅ EXTRACTED FINANCIAL DATA:")
                    for key, value in extracted.items():
                        if value:
                            print(f"  {key}: ${value:,}" if isinstance(value, (int, float)) else f"  {key}: {value}")
                except:
                    print("Could not parse JSON from response")
        else:
            print(f"API error: {response.status_code}")
            
    except Exception as e:
        print(f"Error calling GPT-OSS: {e}")

def main():
    """Run the complete test"""
    
    # First test Docling alone
    markdown_text, tables = test_docling_extraction()
    
    # Then enhance with GPT-OSS
    if markdown_text:
        test_with_gpt_oss(markdown_text)
    
    print("\n" + "=" * 60)
    print("✅ DOCLING TEST COMPLETE")
    print("=" * 60)
    print("\nKey Findings:")
    print("1. Check docling_extracted_financials.md for full markdown")
    print("2. Check table_*.csv files for any extracted tables")
    print("3. GPT-OSS can work with Docling's structured output")

if __name__ == "__main__":
    main()