import pandas as pd
import math

def fix_correct_hud_lihtc_methodology():
    """
    Fix LIHTC rent calculations using the CORRECT HUD/Novogradac methodology:
    
    CORRECT household sizes (verified against Novogradac 2025):
    - Efficiency/Studio: 1 person
    - 1BR: 1.5 persons  
    - 2BR: 3 persons
    - 3BR: 4.5 persons
    - 4BR: 6 persons
    
    NOT the "1 + (bedrooms × 1.5)" formula we incorrectly used!
    """
    
    # Read source HUD data
    source_file = '/Users/williamrice/HERR Dropbox/Bill Rice/Agency Scoring Docs/HUD AMI Info/HUD 2025 AMI Section8-FY25.xlsx'
    
    print("FIXING HUD AMI RENT FILE WITH CORRECT NOVOGRADAC-VERIFIED METHODOLOGY")
    print("=" * 80)
    
    df = pd.read_excel(source_file)
    print(f"Loaded source data: {len(df)} records")
    
    # CORRECT HUD/Novogradac household size mapping
    print("\nUsing CORRECT HUD/Novogradac methodology:")
    print("Studio/Efficiency = 1.0 person")
    print("1BR = 1.5 persons")
    print("2BR = 3.0 persons") 
    print("3BR = 4.5 persons")
    print("4BR = 6.0 persons")
    print()
    
    results = []
    
    for idx, row in df.iterrows():
        result = {
            'fips': row.get('fips'),
            'State': row.get('stusps'),
            'County': row.get('County_Name', row.get('county_town_name')),
            'HUD_Area': row.get('hud_area_name'),
            'Metro_Status': 'Metro' if row.get('metro', 0) == 1 else 'Non-Metro',
            'Median_AMI_100pct': row.get('median2025')
        }
        
        # Calculate rent limits for each AMI level and bedroom type
        for ami_pct in [50, 60, 70, 80]:
            
            # Studio/Efficiency - 1 person
            if 'l50_1' in row:
                income_50pct = row['l50_1']
                income_at_ami = income_50pct * (ami_pct / 50)
                monthly_rent = (income_at_ami * 0.30) / 12
                result[f'{ami_pct}pct_AMI_Studio_Rent'] = math.floor(monthly_rent)
            
            # 1BR - 1.5 persons (interpolate between 1 and 2)
            if 'l50_1' in row and 'l50_2' in row:
                income_1p = row['l50_1']
                income_2p = row['l50_2']
                income_1p5 = income_1p + 0.5 * (income_2p - income_1p)  # Linear interpolation
                income_at_ami = income_1p5 * (ami_pct / 50)
                monthly_rent = (income_at_ami * 0.30) / 12
                result[f'{ami_pct}pct_AMI_1BR_Rent'] = math.floor(monthly_rent)
            
            # 2BR - 3 persons
            if 'l50_3' in row:
                income_50pct = row['l50_3']
                income_at_ami = income_50pct * (ami_pct / 50)
                monthly_rent = (income_at_ami * 0.30) / 12
                result[f'{ami_pct}pct_AMI_2BR_Rent'] = math.floor(monthly_rent)
            
            # 3BR - 4.5 persons (interpolate between 4 and 5)
            if 'l50_4' in row and 'l50_5' in row:
                income_4p = row['l50_4']
                income_5p = row['l50_5']
                income_4p5 = income_4p + 0.5 * (income_5p - income_4p)  # Linear interpolation
                income_at_ami = income_4p5 * (ami_pct / 50)
                monthly_rent = (income_at_ami * 0.30) / 12
                result[f'{ami_pct}pct_AMI_3BR_Rent'] = math.floor(monthly_rent)
            
            # 4BR - 6 persons
            if 'l50_6' in row:
                income_50pct = row['l50_6']
                income_at_ami = income_50pct * (ami_pct / 50)
                monthly_rent = (income_at_ami * 0.30) / 12
                result[f'{ami_pct}pct_AMI_4BR_Rent'] = math.floor(monthly_rent)
        
        results.append(result)
    
    # Create output dataframe
    output_df = pd.DataFrame(results)
    
    # Save with correct methodology
    output_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx'
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        output_df.to_excel(writer, sheet_name='Rent_Data', index=False)
    
    print(f"✅ File recreated with CORRECT HUD/Novogradac methodology: {output_path}")
    print(f"Total records: {len(output_df)}")
    
    # Verify Los Angeles County against Novogradac
    la_data = output_df[output_df['County'].str.contains('Los Angeles', case=False, na=False)]
    if len(la_data) > 0:
        row = la_data.iloc[0]
        print(f"\nLOS ANGELES VERIFICATION (should match Novogradac exactly):")
        print(f"60% AMI Studio: ${row['60pct_AMI_Studio_Rent']} (Novogradac: $1,590)")
        print(f"60% AMI 1BR: ${row['60pct_AMI_1BR_Rent']} (Novogradac: $1,704)")
        print(f"60% AMI 2BR: ${row['60pct_AMI_2BR_Rent']} (Novogradac: $2,044)")
        print(f"60% AMI 3BR: ${row['60pct_AMI_3BR_Rent']} (Novogradac: $2,363)")
        print(f"60% AMI 4BR: ${row['60pct_AMI_4BR_Rent']} (Novogradac: $2,635)")
    
    # Verify Tarrant County for our analysis
    tarrant_data = output_df[output_df['County'].str.contains('Tarrant', case=False, na=False)]
    if len(tarrant_data) > 0:
        row = tarrant_data.iloc[0]
        print(f"\nTARRANT COUNTY (SAGINAW, TX) - CORRECTED RENT LIMITS:")
        print(f"60% AMI 1BR: ${row['60pct_AMI_1BR_Rent']}")
        print(f"60% AMI 2BR: ${row['60pct_AMI_2BR_Rent']}")
        print(f"60% AMI 3BR: ${row['60pct_AMI_3BR_Rent']}")
        print(f"60% AMI 4BR: ${row['60pct_AMI_4BR_Rent']}")
    
    return output_df

if __name__ == "__main__":
    results = fix_correct_hud_lihtc_methodology()