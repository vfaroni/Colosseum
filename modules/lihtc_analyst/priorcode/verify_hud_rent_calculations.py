import pandas as pd
import numpy as np
import math

def verify_hud_rent_calculations():
    """
    Verify HUD AMI rent calculations and ensure proper LIHTC rounding rules.
    LIHTC requires rounding DOWN to nearest dollar (floor function).
    """
    
    # Read the recreated HUD AMI file
    file_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx'
    
    try:
        df = pd.read_excel(file_path, sheet_name='Rent_Data')
        print(f"Successfully loaded HUD AMI data: {len(df)} records")
        print(f"Columns: {list(df.columns)}")
        
        # Check a sample calculation for Anderson County, TX
        anderson = df[(df['State'] == 'TX') & (df['County'].str.contains('Anderson', case=False, na=False))]
        
        if len(anderson) > 0:
            row = anderson.iloc[0]
            print("\n=== ANDERSON COUNTY, TX VERIFICATION ===")
            print(f"Area: {row['HUD_Area']}")
            print(f"100% AMI (4-person): ${row['Median_AMI_100pct']:,}")
            
            # Check specific rent values
            print(f"\nRent values in file:")
            print(f"60% AMI 2BR Rent: ${row['60pct_AMI_2BR_Rent']}")
            print(f"70% AMI 3BR Rent: ${row['70pct_AMI_3BR_Rent']}")
            
        # Check for rounding issues across all rent columns
        print("\n=== CHECKING FOR DECIMAL VALUES IN RENT COLUMNS ===")
        rent_columns = [col for col in df.columns if 'Rent' in col]
        
        has_decimals = False
        decimal_count = 0
        
        for col in rent_columns:
            non_null_values = df[col].dropna()
            
            # Check if any values have decimals (not equal to their floor value)
            mask = non_null_values != np.floor(non_null_values)
            decimal_values = non_null_values[mask]
            
            if len(decimal_values) > 0:
                has_decimals = True
                decimal_count += len(decimal_values)
                print(f"\n❌ {col} has {len(decimal_values)} values with decimals")
                print(f"Sample values that need floor rounding:")
                for idx, val in decimal_values.head(3).items():
                    print(f"   Row {idx}: ${val:.2f} should be ${math.floor(val)}")
        
        if has_decimals:
            print(f"\n❌ ROUNDING ISSUE DETECTED: {decimal_count} total values need to be rounded DOWN")
            print("LIHTC requires rounding DOWN to nearest dollar (not standard rounding)")
            return False
        else:
            print("\n✅ All rent values are whole dollars")
            return True
            
    except Exception as e:
        print(f"Error reading file: {e}")
        print("File may need to be recreated with proper calculations")
        return False

def recreate_with_proper_rounding():
    """
    Recreate the HUD AMI file with proper LIHTC floor rounding
    """
    print("\n=== RECREATING FILE WITH PROPER FLOOR ROUNDING ===")
    
    # Read source HUD data
    source_file = '/Users/williamrice/HERR Dropbox/Bill Rice/Agency Scoring Docs/HUD AMI Info/HUD 2025 AMI Section8-FY25.xlsx'
    
    try:
        df = pd.read_excel(source_file)
        print(f"Loaded source data: {len(df)} records")
        
        # MTSP LIHTC bedroom to household size mapping
        bedroom_mapping = {
            'Studio': 1,  # 1 person
            '1BR': 2,     # 1.5 persons rounded to 2
            '2BR': 3,     # 3 persons
            '3BR': 5,     # 4.5 persons rounded to 5
            '4BR': 6      # 6 persons
        }
        
        # Create new dataframe with rent calculations
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
                for bedroom, household_size in bedroom_mapping.items():
                    # Get income limit for household size at 50% AMI
                    income_col = f'l50_{household_size}'
                    if income_col in row:
                        income_50pct = row[income_col]
                        
                        # Calculate income at desired AMI percentage
                        income_at_ami = income_50pct * (ami_pct / 50)
                        
                        # LIHTC formula: (Annual Income × 0.30) ÷ 12
                        monthly_rent = (income_at_ami * 0.30) / 12
                        
                        # CRITICAL: Round DOWN to nearest dollar
                        rent_rounded = math.floor(monthly_rent)
                        
                        col_name = f'{ami_pct}pct_AMI_{bedroom}_Rent'
                        result[col_name] = rent_rounded
            
            results.append(result)
        
        # Create output dataframe
        output_df = pd.DataFrame(results)
        
        # Save with proper rounding
        output_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static_CORRECTED.xlsx'
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            output_df.to_excel(writer, sheet_name='Rent_Data', index=False)
        
        print(f"\n✅ File recreated with proper floor rounding: {output_path}")
        print(f"Total records: {len(output_df)}")
        
        # Verify a sample
        sample = output_df[output_df['County'].str.contains('Anderson', case=False, na=False)].iloc[0]
        print(f"\nSample verification (Anderson County, TX):")
        print(f"60% AMI 2BR Rent: ${sample['60pct_AMI_2BR_Rent']}")
        
        return output_path
        
    except Exception as e:
        print(f"Error recreating file: {e}")
        return None

if __name__ == "__main__":
    # First verify existing file
    is_correct = verify_hud_rent_calculations()
    
    if not is_correct:
        # Recreate with proper rounding
        new_file = recreate_with_proper_rounding()