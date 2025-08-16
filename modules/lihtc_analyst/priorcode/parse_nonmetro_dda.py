#!/usr/bin/env python3
"""
Parse Non-Metro DDA PDF and create structured data
Based on HUD's DDA2025NM.PDF (Non-Metro Difficult Development Areas)
"""

import PyPDF2
import pandas as pd
import json
from pathlib import Path

def parse_nonmetro_dda_pdf():
    """Parse the Non-Metro DDA PDF and extract county-level data"""
    
    pdf_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data/DDA2025NM_NonMetro.pdf"
    
    print("📄 Parsing Non-Metro DDA PDF...")
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            full_text = ''
            for page in pdf_reader.pages:
                full_text += page.extract_text() + '\n'
        
        print(f"✅ Extracted {len(full_text)} characters from PDF")
        
        # Parse state and county data
        nonmetro_ddas = []
        lines = full_text.split('\n')
        
        # Known states to look for
        states = [
            'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Florida',
            'Georgia', 'Hawaii', 'Idaho', 'Kansas', 'Kentucky', 'Louisiana', 'Maine',
            'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri',
            'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Mexico', 'New York',
            'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
            'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
            'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
        ]
        
        current_state = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line starts with a state name
            for state in states:
                if line.startswith(state + ' '):
                    current_state = state
                    # Extract counties from this line
                    counties_text = line.replace(state + ' ', '')
                    counties = parse_counties_from_text(counties_text)
                    
                    for county in counties:
                        nonmetro_ddas.append({
                            'state': state,
                            'county': county,
                            'nonmetro_dda': True,
                            'source': 'HUD DDA2025NM.PDF'
                        })
                    break
        
        print(f"✅ Parsed {len(nonmetro_ddas)} Non-Metro DDA counties")
        
        # Create DataFrame
        df = pd.DataFrame(nonmetro_ddas)
        
        # Save as CSV and JSON
        csv_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data/nonmetro_dda_2025.csv"
        json_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data/nonmetro_dda_2025.json"
        
        df.to_csv(csv_path, index=False)
        df.to_json(json_path, orient='records', indent=2)
        
        print(f"✅ Saved to: {csv_path}")
        print(f"✅ Saved to: {json_path}")
        
        # Show Arizona counties specifically
        az_counties = df[df['state'] == 'Arizona']
        print(f"\n🌵 ARIZONA NON-METRO DDA COUNTIES ({len(az_counties)}):")
        for idx, row in az_counties.iterrows():
            print(f"  • {row['county']}")
        
        # Confirm Santa Cruz County
        if 'Santa Cruz County' in az_counties['county'].values:
            print(f"\n✅ CONFIRMED: Santa Cruz County, AZ is a Non-Metro DDA")
            print(f"   United Church Village Apts (Nogales, AZ) qualifies for 130% basis boost")
        
        return df
        
    except Exception as e:
        print(f"❌ Error parsing PDF: {e}")
        return None

def parse_counties_from_text(text):
    """Parse county names from text string"""
    counties = []
    
    # Split by 'County' and reconstruct
    if 'County' in text:
        parts = text.split(' County')
        for part in parts:
            if part.strip():
                county_name = part.strip() + ' County'
                counties.append(county_name)
    
    return counties

if __name__ == "__main__":
    df = parse_nonmetro_dda_pdf()
    
    if df is not None:
        print(f"\n📊 SUMMARY:")
        print(f"   Total Non-Metro DDA Counties: {len(df)}")
        print(f"   States Covered: {df['state'].nunique()}")
        print(f"   Arizona Counties: {len(df[df['state'] == 'Arizona'])}")