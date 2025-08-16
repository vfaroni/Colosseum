import pandas as pd
import math

# Read the source data
source_file = '/Users/williamrice/HERR Dropbox/Bill Rice/Agency Scoring Docs/HUD AMI Info/HUD 2025 AMI Section8-FY25.xlsx'
df = pd.read_excel(source_file)

# Get Tarrant County
tarrant = df[df['County_Name'].str.contains('Tarrant County', case=False, na=False)].iloc[0]

print('INVESTIGATING 3BR RENT CALCULATION')
print('=' * 50)
print('Tarrant County Income Limits at 50% AMI:')
print(f'4-person: ${tarrant["l50_4"]:,}')
print(f'5-person: ${tarrant["l50_5"]:,}')

# Calculate interpolated 4.5 person
income_4p5 = (tarrant['l50_4'] + tarrant['l50_5']) / 2
print(f'4.5-person (average of 4 & 5): ${income_4p5:,.2f}')

# Calculate 60% AMI rents for comparison
print('\n60% AMI Monthly Rent Calculations:')

# Using 4-person
income_4p_60 = tarrant['l50_4'] * 1.2
rent_4p = math.floor((income_4p_60 * 0.30) / 12)
print(f'Using 4-person: ${rent_4p}')

# Using 4.5-person interpolated
income_4p5_60 = income_4p5 * 1.2
rent_4p5 = math.floor((income_4p5_60 * 0.30) / 12)
print(f'Using 4.5-person: ${rent_4p5}')

# Using 5-person
income_5p_60 = tarrant['l50_5'] * 1.2
rent_5p = math.floor((income_5p_60 * 0.30) / 12)
print(f'Using 5-person: ${rent_5p}')

print('\nLogic check:')
print(f'4-person < 4.5-person < 5-person')
print(f'${rent_4p} < ${rent_4p5} < ${rent_5p}')

if rent_4p < rent_4p5 < rent_5p:
    print('✅ CORRECT ordering')
else:
    print('❌ INCORRECT ordering')

# Check the file values
rent_file = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx'
rent_df = pd.read_excel(rent_file)
tarrant_rent = rent_df[rent_df['County'].str.contains('Tarrant', case=False, na=False)].iloc[0]

print(f'\nCurrent file value for 60% AMI 3BR: ${tarrant_rent["60pct_AMI_3BR_Rent"]}')

# Check which calculation it matches
if tarrant_rent["60pct_AMI_3BR_Rent"] == rent_4p:
    print('File is using 4-person (too low)')
elif tarrant_rent["60pct_AMI_3BR_Rent"] == rent_4p5:
    print('File is using 4.5-person interpolation (CORRECT)')
elif tarrant_rent["60pct_AMI_3BR_Rent"] == rent_5p:
    print('File is using 5-person (too high)')
else:
    print('File value does not match any calculation!')