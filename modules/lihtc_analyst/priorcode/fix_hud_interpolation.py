import pandas as pd
import math

def fix_hud_rent_interpolation():
    """
    Fix HUD AMI rent calculations to use proper LIHTC interpolation for fractional household sizes.
    1BR = 1.5 persons (interpolate between 1 and 2)
    3BR = 4.5 persons (interpolate between 4 and 5)
    """
    
    # Read source HUD data
    source_file = '/Users/williamrice/HERR Dropbox/Bill Rice/Agency Scoring Docs/HUD AMI Info/HUD 2025 AMI Section8-FY25.xlsx'
    
    print("RECREATING HUD AMI RENT FILE WITH CORRECT INTERPOLATION")
    print("=" * 60)
    
    df = pd.read_excel(source_file)
    print(f"Loaded source data: {len(df)} records")
    
    # CORRECT MTSP LIHTC bedroom to household size mapping
    print("\nUsing CORRECT household sizes:")
    print("Studio = 1.0 persons")
    print("1BR = 1.5 persons (interpolated)")
    print("2BR = 3.0 persons")
    print("3BR = 4.5 persons (interpolated)")
    print("4BR = 6.0 persons")
    
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
            
            # 1BR - 1.5 persons (interpolate between 1 and 2)
            if 'l50_1' in row and 'l50_2' in row:
                income_1p = row['l50_1']
                income_2p = row['l50_2']
                income_1p5 = (income_1p + income_2p) / 2  # Interpolation
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
                income_4p5 = (income_4p + income_5p) / 2  # Interpolation
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
    
    # Save with proper interpolation
    output_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx'
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        output_df.to_excel(writer, sheet_name='Rent_Data', index=False)
    
    print(f"\n✅ File recreated with CORRECT interpolation: {output_path}")
    print(f"Total records: {len(output_df)}")
    
    # Verify Tarrant County sample
    tarrant = output_df[output_df['County'].str.contains('Tarrant', case=False, na=False)]
    if len(tarrant) > 0:
        sample = tarrant.iloc[0]
        print(f"\nTarrant County verification:")
        print(f"60% AMI 1BR Rent: ${sample['60pct_AMI_1BR_Rent']} (using 1.5 person interpolation)")
        print(f"60% AMI 3BR Rent: ${sample['60pct_AMI_3BR_Rent']} (using 4.5 person interpolation)")

if __name__ == "__main__":
    fix_hud_rent_interpolation()