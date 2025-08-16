import requests
import pandas as pd
import geopandas as gpd
from zipfile import ZipFile
from io import BytesIO
import os

# === SETUP ===
output_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Poverty Rate Census Tracts (ACS)"
os.makedirs(output_dir, exist_ok=True)
print("[1/7] Output directory verified or created.")

# === DOWNLOAD SHAPEFILE ===
print("[2/7] Downloading Texas 2020 Census Tracts shapefile...")
tiger_url = "https://www2.census.gov/geo/tiger/TIGER2020/TRACT/tl_2020_48_tract.zip"
r = requests.get(tiger_url)
z = ZipFile(BytesIO(r.content))
z.extractall(output_dir)
print("[2/7] Shapefile downloaded and extracted.")

# === LOAD SHAPEFILE ===
shapefile_path = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith(".shp")][0]
gdf = gpd.read_file(shapefile_path)
print(f"[3/7] Shapefile loaded with {len(gdf)} tracts.")

# === GET CENSUS DATA ===
print("[4/7] Fetching ACS poverty data from Census API...")
acs_url = "https://api.census.gov/data/2021/acs/acs5/subject"
params = {
    "get": "NAME,S1701_C03_001E",  # % below poverty
    "for": "tract:*",
    "in": "state:48"
}
resp = requests.get(acs_url, params=params)
acs_data = resp.json()
acs_df = pd.DataFrame(acs_data[1:], columns=acs_data[0])
acs_df["GEOID"] = acs_df["state"] + acs_df["county"] + acs_df["tract"]
acs_df["poverty_pct"] = pd.to_numeric(acs_df["S1701_C03_001E"], errors="coerce")
print(f"[4/7] Retrieved and parsed poverty data for {len(acs_df)} tracts.")

# === MERGE ===
print("[5/7] Merging shapefile with poverty data...")
merged = gdf.merge(acs_df[["GEOID", "poverty_pct"]], on="GEOID")
print(f"[5/7] Merge complete. {len(merged)} records matched.")

# === FILTER & STYLE ===
print("[6/7] Filtering for tracts with poverty rate ≤ 20%...")
low_poverty = merged[merged["poverty_pct"] <= 20].copy()
low_poverty["fill"] = "rgba(33, 37, 41, 0.5)"
print(f"[6/7] {len(low_poverty)} tracts identified as low-poverty.")

# === EXPORT ===
geojson_out = os.path.join(output_dir, "texas_low_poverty_tracts.geojson")
gpkg_out = os.path.join(output_dir, "texas_low_poverty_tracts.gpkg")
print("[7/7] Exporting to GeoJSON and GPKG...")
low_poverty.to_file(geojson_out, driver="GeoJSON")
low_poverty.to_file(gpkg_out, driver="GPKG")
print("✅ All done! Files saved to:", output_dir)