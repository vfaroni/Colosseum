#!/usr/bin/env python3
import sys
import subprocess

# Try to install PyPDF2 if not available
try:
    import PyPDF2
except ImportError:
    print("Installing PyPDF2...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    import PyPDF2

def extract_pdf_text(pdf_path, output_path):
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += f"\n\n--- Page {page_num + 1} ---\n\n"
                text += page.extract_text()
            
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(text)
        
        print(f"Successfully extracted text to {output_path}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    pdf_path = "CTCAC_Rules/December_11_2024_QAP_Regulations_FINAL.pdf"
    output_path = "CTCAC_Rules/December_11_2024_QAP_Regulations_FINAL.txt"
    extract_pdf_text(pdf_path, output_path)