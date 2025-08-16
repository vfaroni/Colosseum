import pandas as pd
import math

def fix_hud_lihtc_methodology():
    """
    Fix LIHTC rent calculations using the CORRECT HUD methodology:
    "Maximum rents for larger units are set by assuming an additional 1.5 persons per bedroom"
    
    This means:
    Studio = 1 person (base)
    1BR = 1 + 1.5 = 2.5 persons  
    2BR = 1 + (2 × 1.5) = 4.0 persons
    3BR = 1 + (3 × 1.5) = 5.5 persons
    4BR = 1 + (4 × 1.5) = 7.0 persons
    """
    
    # Read source HUD data
    source_file = '/Users/williamrice/HERR Dropbox/Bill Rice/Agency Scoring Docs/HUD AMI Info/HUD 2025 AMI Section8-FY25.xlsx'
    
    print("FIXING HUD AMI RENT FILE WITH CORRECT 1.5 PERSONS PER BEDROOM METHODOLOGY")
    print("=" * 80)
    
    df = pd.read_excel(source_file)
    print(f"Loaded source data: {len(df)} records")
    
    # CORRECT HUD LIHTC bedroom to household size mapping
    print("\nUsing CORRECT HUD methodology:")
    print("Studio = 1.0 person (base)")
    print("1BR = 1 + (1 × 1.5) = 2.5 persons")
    print("2BR = 1 + (2 × 1.5) = 4.0 persons") 
    print("3BR = 1 + (3 × 1.5) = 5.5 persons")
    print("4BR = 1 + (4 × 1.5) = 7.0 persons")
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
            
            # Studio - 1 person
            if 'l50_1' in row:
                income_50pct = row['l50_1']
                income_at_ami = income_50pct * (ami_pct / 50)
                monthly_rent = (income_at_ami * 0.30) / 12
                result[f'{ami_pct}pct_AMI_Studio_Rent'] = math.floor(monthly_rent)
            
            # 1BR - 2.5 persons (interpolate between 2 and 3)
            if 'l50_2' in row and 'l50_3' in row:
                income_2p = row['l50_2']
                income_3p = row['l50_3']
                income_2p5 = income_2p + 0.5 * (income_3p - income_2p)  # Linear interpolation
                income_at_ami = income_2p5 * (ami_pct / 50)
                monthly_rent = (income_at_ami * 0.30) / 12
                result[f'{ami_pct}pct_AMI_1BR_Rent'] = math.floor(monthly_rent)
            
            # 2BR - 4 persons
            if 'l50_4' in row:
                income_50pct = row['l50_4']
                income_at_ami = income_50pct * (ami_pct / 50)
                monthly_rent = (income_at_ami * 0.30) / 12
                result[f'{ami_pct}pct_AMI_2BR_Rent'] = math.floor(monthly_rent)
            
            # 3BR - 5.5 persons (interpolate between 5 and 6)
            if 'l50_5' in row and 'l50_6' in row:
                income_5p = row['l50_5']
                income_6p = row['l50_6']
                income_5p5 = income_5p + 0.5 * (income_6p - income_5p)  # Linear interpolation
                income_at_ami = income_5p5 * (ami_pct / 50)
                monthly_rent = (income_at_ami * 0.30) / 12
                result[f'{ami_pct}pct_AMI_3BR_Rent'] = math.floor(monthly_rent)
            
            # 4BR - 7 persons
            if 'l50_7' in row:
                income_50pct = row['l50_7']
                income_at_ami = income_50pct * (ami_pct / 50)
                monthly_rent = (income_at_ami * 0.30) / 12
                result[f'{ami_pct}pct_AMI_4BR_Rent'] = math.floor(monthly_rent)
        
        results.append(result)
    
    # Create output dataframe
    output_df = pd.DataFrame(results)
    
    # Save with correct HUD methodology
    output_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx'
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        output_df.to_excel(writer, sheet_name='Rent_Data', index=False)
    
    print(f"✅ File recreated with CORRECT HUD methodology: {output_path}")
    print(f"Total records: {len(output_df)}")
    
    # Verify major metros
    test_counties = [
        ("Tarrant County", "TX"),
        ("Los Angeles County", "CA"), 
        ("Cook County", "IL"),
        ("Harris County", "TX")
    ]
    
    print(f"\nVERIFICATION - 60% AMI RENT LIMITS:")
    print("-" * 60)
    
    for county_name, state in test_counties:
        county_data = output_df[(output_df['State'] == state) & 
                               (output_df['County'].str.contains(county_name.split()[0], case=False, na=False))]
        
        if len(county_data) > 0:
            row = county_data.iloc[0]
            print(f"{county_name}, {state}:")
            print(f"  1BR: ${row['60pct_AMI_1BR_Rent']} (2.5 person household)")
            print(f"  2BR: ${row['60pct_AMI_2BR_Rent']} (4.0 person household)")
            print(f"  3BR: ${row['60pct_AMI_3BR_Rent']} (5.5 person household)")
            print(f"  4BR: ${row['60pct_AMI_4BR_Rent']} (7.0 person household)")
            print()
    
    return output_df

if __name__ == "__main__":
    results = fix_hud_lihtc_methodology()