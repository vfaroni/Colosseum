import pandas as pd

def compare_novogradac_la():
    """
    Compare our Los Angeles rent calculations to Novogradac's official 2025 data
    """
    
    # Read our file
    hud_file = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx'
    df = pd.read_excel(hud_file, sheet_name='Rent_Data')
    
    # Get Los Angeles County
    la_data = df[df['County'].str.contains('Los Angeles', case=False, na=False)].iloc[0]
    
    print('LOS ANGELES COUNTY - NOVOGRADAC vs OUR CALCULATIONS')
    print('=' * 60)
    print()
    
    # Novogradac data from the image
    novogradac_data = {
        'Efficiency': {'50': 1325, '60': 1590, '70': 1855, '80': 2120},
        '1BR': {'50': 1420, '60': 1704, '70': 1988, '80': 2272},
        '2BR': {'50': 1703, '60': 2044, '70': 2385, '80': 2726},
        '3BR': {'50': 1969, '60': 2363, '70': 2757, '80': 3151},
        '4BR': {'50': 2196, '60': 2635, '70': 3074, '80': 3514}
    }
    
    # Our data
    our_data = {
        'Studio': {
            '50': la_data['50pct_AMI_Studio_Rent'], 
            '60': la_data['60pct_AMI_Studio_Rent'], 
            '70': la_data['70pct_AMI_Studio_Rent'], 
            '80': la_data['80pct_AMI_Studio_Rent']
        },
        '1BR': {
            '50': la_data['50pct_AMI_1BR_Rent'], 
            '60': la_data['60pct_AMI_1BR_Rent'], 
            '70': la_data['70pct_AMI_1BR_Rent'], 
            '80': la_data['80pct_AMI_1BR_Rent']
        },
        '2BR': {
            '50': la_data['50pct_AMI_2BR_Rent'], 
            '60': la_data['60pct_AMI_2BR_Rent'], 
            '70': la_data['70pct_AMI_2BR_Rent'], 
            '80': la_data['80pct_AMI_2BR_Rent']
        },
        '3BR': {
            '50': la_data['50pct_AMI_3BR_Rent'], 
            '60': la_data['60pct_AMI_3BR_Rent'], 
            '70': la_data['70pct_AMI_3BR_Rent'], 
            '80': la_data['80pct_AMI_3BR_Rent']
        },
        '4BR': {
            '50': la_data['50pct_AMI_4BR_Rent'], 
            '60': la_data['60pct_AMI_4BR_Rent'], 
            '70': la_data['70pct_AMI_4BR_Rent'], 
            '80': la_data['80pct_AMI_4BR_Rent']
        }
    }
    
    # Compare each unit type and AMI level
    exact_matches = 0
    total_comparisons = 0
    
    for unit_type in ['1BR', '2BR', '3BR', '4BR']:
        print(f'{unit_type} UNITS:')
        
        for ami in ['50', '60', '70', '80']:
            novogradac_rent = novogradac_data[unit_type][ami]
            our_rent = our_data[unit_type][ami]
            diff = our_rent - novogradac_rent
            
            if diff == 0:
                status = '✅ EXACT MATCH'
                exact_matches += 1
            elif abs(diff) <= 5:
                status = f'✅ CLOSE ({diff:+d})'
            else:
                status = f'❌ DIFF ({diff:+d})'
                
            print(f'  {ami}% AMI: Novogradac ${novogradac_rent:,} | Our ${our_rent:,} | {status}')
            total_comparisons += 1
        print()
    
    # Check Studio vs Efficiency
    print('STUDIO/EFFICIENCY:')
    for ami in ['50', '60', '70', '80']:
        novogradac_rent = novogradac_data['Efficiency'][ami]
        our_rent = our_data['Studio'][ami]
        diff = our_rent - novogradac_rent
        
        if diff == 0:
            status = '✅ EXACT MATCH'
            exact_matches += 1
        elif abs(diff) <= 5:
            status = f'✅ CLOSE ({diff:+d})'
        else:
            status = f'❌ DIFF ({diff:+d})'
            
        print(f'  {ami}% AMI: Novogradac ${novogradac_rent:,} | Our ${our_rent:,} | {status}')
        total_comparisons += 1
    
    print()
    print('SUMMARY:')
    print(f'Exact matches: {exact_matches}/{total_comparisons} ({exact_matches/total_comparisons*100:.1f}%)')
    
    if exact_matches == total_comparisons:
        print('🎉 PERFECT! Our calculations match Novogradac exactly!')
    elif exact_matches > total_comparisons * 0.8:
        print('✅ EXCELLENT! Most calculations match Novogradac')
    else:
        print('⚠️  Some discrepancies found - may need methodology review')
    
    # Show the household size mapping used
    print()
    print('HOUSEHOLD SIZE VERIFICATION:')
    print('Novogradac shows: Efficiency(1), 1BR(1.5), 2BR(3), 3BR(4.5), 4BR(6)')
    print('Our methodology: Studio(1), 1BR(2.5), 2BR(4), 3BR(5.5), 4BR(7)')
    print('❌ MISMATCH - We are using different household size assumptions!')

if __name__ == "__main__":
    compare_novogradac_la()