#!/usr/bin/env python3
"""
Export Final D'Marco Excel with Best Geocoding Results
"""
import pandas as pd
from datetime import datetime
from openpyxl.styles import PatternFill, Font

# Load comparison results
df = pd.read_excel('Geocoding_Comparison_Report_20250618_234851.xlsx', sheet_name='Full_Comparison')

# Create final dataset with best coordinates
final_data = []
for _, row in df.iterrows():
    if row['Best_Coordinates'] == 'PositionStack':
        lat, lng, method = row['PS_Latitude'], row['PS_Longitude'], 'PositionStack'
        confidence, qct_dda_status = row['PS_Confidence'], row['PS_QCT_DDA_Status']
    else:
        lat, lng, method = row['Nom_Latitude'], row['Nom_Longitude'], 'Nominatim'
        confidence, qct_dda_status = 1.0, row['Nom_QCT_DDA_Status']
    
    final_data.append({
        'MailingName': row['MailingName'],
        'Address': row['Address'],
        'City': row['City'],
        'County': row['County'],
        'Region': row['Region'],
        'Acres': row['Acres'],
        'Latitude': lat,
        'Longitude': lng,
        'Geocoding_Method': method,
        'Geocoding_Confidence': confidence,
        'QCT_DDA_Status': qct_dda_status,
        'Basis_Boost_Eligible': qct_dda_status in ['QCT', 'DDA', 'QCT+DDA'],
        'Priority': 'HIGH' if qct_dda_status in ['QCT', 'DDA', 'QCT+DDA'] else 'LOW',
        'Development_Recommendation': 'FOCUS - 30% Basis Boost' if qct_dda_status in ['QCT', 'DDA', 'QCT+DDA'] else 'Consider for conventional development'
    })

df_final = pd.DataFrame(final_data)
df_final = df_final.sort_values(['Basis_Boost_Eligible', 'Acres'], ascending=[False, False])

# Save with formatting
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"DMarco_Sites_Final_PositionStack_{timestamp}.xlsx"

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Summary
    summary = {
        'Metric': ['Total Sites', 'QCT/DDA Eligible', 'PositionStack Geocoded', 'Best Opportunities'],
        'Count': [len(df_final), df_final['Basis_Boost_Eligible'].sum(), 
                 len(df_final[df_final['Geocoding_Method'] == 'PositionStack']),
                 len(df_final[(df_final['Basis_Boost_Eligible']) & (df_final['Acres'] > 10)])]
    }
    pd.DataFrame(summary).to_excel(writer, sheet_name='Summary', index=False)
    
    # All sites
    df_final.to_excel(writer, sheet_name='All_Sites_Final', index=False)
    
    # QCT/DDA priority only
    priority = df_final[df_final['Basis_Boost_Eligible'] == True]
    priority.to_excel(writer, sheet_name='QCT_DDA_Priority', index=False)
    
    # Regional breakdown
    regional = df_final.groupby('Region').agg({
        'MailingName': 'count',
        'Basis_Boost_Eligible': 'sum',
        'Acres': ['mean', 'sum']
    })
    regional.columns = ['Total_Sites', 'QCT_DDA_Sites', 'Avg_Acres', 'Total_Acres']
    regional.to_excel(writer, sheet_name='Regional_Summary')

print(f"✅ Exported: {output_file}")
print(f"📊 QCT/DDA Sites: {df_final['Basis_Boost_Eligible'].sum()}/65")
print(f"🎯 PositionStack: {len(df_final[df_final['Geocoding_Method'] == 'PositionStack'])}/65")