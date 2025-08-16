#!/usr/bin/env python3
"""
Examine CoStar Data Structure
"""

import pandas as pd
from pathlib import Path

def examine_costar_file():
    costar_file = Path("/Users/williamrice/Downloads/CostarExport-11.xlsx")
    
    try:
        df = pd.read_excel(costar_file)
        
        print(f"📊 COSTAR DATA EXAMINATION")
        print(f"=" * 40)
        print(f"Total Records: {len(df)}")
        print(f"Total Columns: {len(df.columns)}")
        
        print(f"\n📋 ALL COLUMNS:")
        for i, col in enumerate(df.columns):
            print(f"   {i+1:2d}. {col}")
        
        print(f"\n📋 SAMPLE DATA (First 3 rows):")
        for col in df.columns:
            print(f"\n{col}:")
            for i in range(min(3, len(df))):
                value = df.iloc[i][col]
                print(f"   Row {i+1}: {value}")
        
        print(f"\n🔍 DATA TYPES:")
        print(df.dtypes)
        
        print(f"\n📍 ADDRESSES FOUND:")
        if 'Property Address' in df.columns:
            addresses = df['Property Address'].dropna().unique()
            for i, addr in enumerate(addresses[:10]):
                print(f"   {i+1:2d}. {addr}")
            if len(addresses) > 10:
                print(f"   ... and {len(addresses)-10} more")
        
        print(f"\n💰 PRICE RELATED COLUMNS:")
        price_cols = [col for col in df.columns if 'price' in col.lower() or 'cost' in col.lower() or 'sale' in col.lower()]
        for col in price_cols:
            print(f"   • {col}: {df[col].dtype}")
            sample_values = df[col].dropna().head(3).tolist()
            print(f"     Sample: {sample_values}")
        
        print(f"\n📏 SIZE/ACREAGE RELATED COLUMNS:")
        size_cols = [col for col in df.columns if any(word in col.lower() for word in ['acre', 'size', 'area', 'sqft', 'sf'])]
        for col in size_cols:
            print(f"   • {col}: {df[col].dtype}")
            sample_values = df[col].dropna().head(3).tolist()
            print(f"     Sample: {sample_values}")
    
    except Exception as e:
        print(f"❌ Error examining file: {e}")

if __name__ == "__main__":
    examine_costar_file()