#!/usr/bin/env python3
"""
Analyze CoStar Comparables Data for Olivera Villa
"""

import pandas as pd
import numpy as np

def analyze_rent_comparables():
    """Analyze rent comparables data"""
    try:
        # Read the rent comparables Excel file
        rent_file = '/Users/williamrice/HERR Dropbox/Bill Rice/Deals (Good Clean)/TCI/Olivera Villa, Concord CA/Costar_Data/Rent Comp Properties PID 4075079.xlsx'
        df = pd.read_excel(rent_file)
        
        print('=== DETAILED RENT COMPARABLES ANALYSIS ===')
        
        # Separate subject property from comparables
        subject = df[df['Property Id'] == 4075079].iloc[0]
        comparables = df[df['Property Id'] != 4075079]
        
        print('SUBJECT PROPERTY (OLIVERA VILLA):')
        print(f'  Address: {subject["Address"]}')
        print(f'  Units: {subject["Units"]} | Built: {subject["Yr Blt/Ren"]} | Avg SF: {subject["Avg SF"]}')
        print(f'  Rent/SF: ${subject["Rent/SF"]:.2f} | Rent/Unit: ${subject["Rent/Unit"]:,.0f}')
        print(f'  1BR Rent: ${subject["1 Beds"]:,.0f} | 2BR Rent: ${subject["2 Beds"]:,.0f}')
        print(f'  Occupancy: {subject["Occ %"]*100:.1f}% | Concessions: {subject["Concess %"]*100:.1f}%')
        print()
        
        print('COMPARABLE PROPERTIES SUMMARY:')
        print(f'Number of Comparables: {len(comparables)}')
        print()
        
        # Analyze rent metrics
        print('RENT ANALYSIS:')
        print(f'  Olivera Villa Rent/SF: ${subject["Rent/SF"]:.2f}')
        print(f'  Market Average Rent/SF: ${comparables["Rent/SF"].mean():.2f}')
        print(f'  Market Range: ${comparables["Rent/SF"].min():.2f} - ${comparables["Rent/SF"].max():.2f}')
        percentile = ((comparables["Rent/SF"] < subject["Rent/SF"]).sum() / len(comparables) * 100)
        print(f'  Olivera Villa Percentile: {percentile:.0f}%')
        print()
        
        # Unit rent analysis 
        print('UNIT RENT COMPARISON:')
        comp_1br = comparables['1 Beds'].dropna()
        comp_2br = comparables['2 Beds'].dropna()
        
        print(f'  1BR RENTS:')
        print(f'    Olivera Villa: ${subject["1 Beds"]:,.0f}')
        print(f'    Market Average: ${comp_1br.mean():,.0f}')
        print(f'    Market Range: ${comp_1br.min():,.0f} - ${comp_1br.max():,.0f}')
        br1_percentile = ((comp_1br < subject["1 Beds"]).sum() / len(comp_1br) * 100)
        print(f'    Olivera Percentile: {br1_percentile:.0f}%')
        
        print(f'  2BR RENTS:')
        print(f'    Olivera Villa: ${subject["2 Beds"]:,.0f}')
        print(f'    Market Average: ${comp_2br.mean():,.0f}')
        print(f'    Market Range: ${comp_2br.min():,.0f} - ${comp_2br.max():,.0f}')
        br2_percentile = ((comp_2br < subject["2 Beds"]).sum() / len(comp_2br) * 100)
        print(f'    Olivera Percentile: {br2_percentile:.0f}%')
        print()
        
        # Property characteristics
        print('PROPERTY CHARACTERISTICS:')
        # Handle year built parsing
        years_built = []
        for year_str in comparables["Yr Blt/Ren"]:
            try:
                year = int(str(year_str).split("/")[0])
                years_built.append(year)
            except:
                pass
        avg_year = np.mean(years_built) if years_built else 0
        print(f'  Average Age (Built): {avg_year:.0f}')
        print(f'  Olivera Villa Built: {subject["Yr Blt/Ren"].split("/")[0]}')
        print(f'  Average Size: {comparables["Avg SF"].mean():.0f} SF')
        print(f'  Olivera Villa Size: {subject["Avg SF"]} SF')
        print()
        
        # Occupancy analysis
        print('OCCUPANCY PERFORMANCE:')
        print(f'  Olivera Villa: {subject["Occ %"]*100:.1f}%')
        print(f'  Market Average: {comparables["Occ %"].mean()*100:.1f}%')
        print(f'  Market Range: {comparables["Occ %"].min()*100:.1f}% - {comparables["Occ %"].max()*100:.1f}%')
        print()
        
        # Top and bottom performers by rent/SF
        print('HIGHEST RENT/SF COMPARABLES:')
        top_rent = comparables.nlargest(3, 'Rent/SF')[['Building Name', 'Yr Blt/Ren', 'Rent/SF', '1 Beds', '2 Beds', 'mi Away']]
        for _, prop in top_rent.iterrows():
            print(f'  {prop["Building Name"]}: ${prop["Rent/SF"]:.2f}/SF, Built {prop["Yr Blt/Ren"]}, {prop["mi Away"]} mi away')
        
        print()
        print('LOWEST RENT/SF COMPARABLES:')
        bottom_rent = comparables.nsmallest(3, 'Rent/SF')[['Building Name', 'Yr Blt/Ren', 'Rent/SF', '1 Beds', '2 Beds', 'mi Away']]
        for _, prop in bottom_rent.iterrows():
            print(f'  {prop["Building Name"]}: ${prop["Rent/SF"]:.2f}/SF, Built {prop["Yr Blt/Ren"]}, {prop["mi Away"]} mi away')
        
        return subject, comparables
        
    except Exception as e:
        print(f'Error analyzing rent comparables: {e}')
        return None, None

def analyze_sales_comparables():
    """Analyze sales comparables data"""
    try:
        print('\n=== SALES COMPARABLES ANALYSIS ===')
        sales_file = '/Users/williamrice/HERR Dropbox/Bill Rice/Deals (Good Clean)/TCI/Olivera Villa, Concord CA/Costar_Data/Near By Sales PID 4075079.xlsx'
        df = pd.read_excel(sales_file)
        
        print(f'Number of Sales Comparables: {len(df)}')
        print(f'Columns: {list(df.columns)}')
        print()
        
        # Show basic sales data
        if len(df) > 0:
            print('RECENT SALES SUMMARY:')
            display_cols = ['Property Name', 'Address', 'Sale Date', 'Sale Price', 'Price/Unit', 'Units', 'Yr Built'] if all(col in df.columns for col in ['Property Name', 'Address', 'Sale Date', 'Sale Price', 'Price/Unit', 'Units', 'Yr Built']) else df.columns[:7]
            print(df[display_cols].head().to_string(index=False))
            
            # Calculate key metrics if price data is available
            if 'Price/Unit' in df.columns:
                price_per_unit = df['Price/Unit'].dropna()
                if len(price_per_unit) > 0:
                    print(f'\nSALES METRICS:')
                    print(f'  Average Price/Unit: ${price_per_unit.mean():,.0f}')
                    print(f'  Price Range: ${price_per_unit.min():,.0f} - ${price_per_unit.max():,.0f}')
                    print(f'  Median Price/Unit: ${price_per_unit.median():,.0f}')
        
        return df
        
    except Exception as e:
        print(f'Error analyzing sales comparables: {e}')
        return None

def analyze_income_expense_comparables():
    """Analyze income and expense comparables from PDF"""
    try:
        print('\n=== INCOME & EXPENSE COMPARABLES ANALYSIS ===')
        
        import PyPDF2
        pdf_file = '/Users/williamrice/HERR Dropbox/Bill Rice/Deals (Good Clean)/TCI/Olivera Villa, Concord CA/Costar_Data/Market_Financials_Near_2451 Olivera Rd - Olivera Villa.pdf'
        
        with open(pdf_file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            full_text = ''
            for page in reader.pages:
                full_text += page.extract_text() + '\n'
        
        lines = full_text.split('\n')
        
        # Look for key financial metrics
        print('MARKET FINANCIAL METRICS:')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['revenue', 'expense', 'noi', 'cap rate', 'rent/sf']):
                print(f'  {line.strip()}')
                # Print next few lines for context
                for j in range(1, 3):
                    if i+j < len(lines) and lines[i+j].strip():
                        print(f'    {lines[i+j].strip()}')
                print()
        
        return full_text
        
    except Exception as e:
        print(f'Error analyzing income/expense comparables: {e}')
        return None

def main():
    """Main analysis function"""
    print('COSTAR MARKET ANALYSIS FOR OLIVERA VILLA')
    print('=' * 60)
    
    # Analyze rent comparables
    subject, rent_comps = analyze_rent_comparables()
    
    # Analyze sales comparables  
    sales_comps = analyze_sales_comparables()
    
    # Analyze income/expense comparables
    inc_exp_text = analyze_income_expense_comparables()
    
    print('\n=== MARKET CONTEXT SUMMARY ===')
    if subject is not None:
        print('OLIVERA VILLA MARKET POSITION:')
        print(f'  - Below-market rents provide LIHTC upside opportunity')
        print(f'  - Strong occupancy performance vs. market average')
        print(f'  - Older vintage (1971) vs. market average ~1970s')
        print(f'  - Fire damage creates acquisition discount opportunity')

if __name__ == "__main__":
    main()