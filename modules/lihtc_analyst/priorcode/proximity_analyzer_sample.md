# Google Maps Proximity Analyzer - Sample Output

## New Excel Fields to be Added

### Distance Fields (in miles):
- `elementary_school_nearest_miles` - Distance to nearest elementary school
- `elementary_school_nearest_name` - Name of nearest elementary school
- `elementary_school_count` - Number of elementary schools within 2 miles

- `middle_school_nearest_miles` - Distance to nearest middle school
- `middle_school_nearest_name` - Name of nearest middle school
- `middle_school_count` - Number of middle schools within 3 miles

- `high_school_nearest_miles` - Distance to nearest high school
- `high_school_nearest_name` - Name of nearest high school
- `high_school_count` - Number of high schools within 3 miles

- `grocery_store_nearest_miles` - Distance to nearest grocery store
- `grocery_store_nearest_name` - Name of nearest grocery store (e.g., "H-E-B", "Kroger", "Walmart Supercenter")
- `grocery_store_count` - Number of grocery stores within 1 mile

- `transit_stop_nearest_miles` - Distance to nearest transit stop
- `transit_stop_nearest_name` - Name of nearest transit stop
- `transit_stop_count` - Number of transit stops within 0.5 miles

- `pharmacy_nearest_miles` - Distance to nearest pharmacy
- `pharmacy_nearest_name` - Name of nearest pharmacy (e.g., "CVS Pharmacy", "Walgreens")
- `pharmacy_count` - Number of pharmacies within 2 miles

- `hospital_nearest_miles` - Distance to nearest hospital
- `hospital_nearest_name` - Name of nearest hospital
- `hospital_count` - Number of hospitals within 5 miles

- `park_nearest_miles` - Distance to nearest public park
- `park_nearest_name` - Name of nearest park
- `park_count` - Number of parks within 1 mile

### Scoring Fields:
- `score_elementary_school` - Weighted score for elementary school proximity (0-15)
- `score_middle_school` - Weighted score for middle school proximity (0-10)
- `score_high_school` - Weighted score for high school proximity (0-10)
- `score_grocery_store` - Weighted score for grocery proximity (0-20)
- `score_transit_stop` - Weighted score for transit proximity (0-15)
- `score_pharmacy` - Weighted score for pharmacy proximity (0-10)
- `score_hospital` - Weighted score for hospital proximity (0-10)
- `score_park` - Weighted score for park proximity (0-10)
- `score_total_proximity_score` - Overall proximity score (0-100)
- `score_proximity_rating` - Categorical rating ("Excellent", "Good", "Fair", "Poor")

## Sample Terminal Output

```
Analyzing proximity for site at 30.1516, -97.7919
Processing site 1 of 227
INFO:__main__:Analyzing proximity for site at 30.1516, -97.7919
INFO:__main__:Searching elementary_school...
INFO:__main__:Found 3 elementary schools within 2 miles
INFO:__main__:Searching middle_school...
INFO:__main__:Found 2 middle schools within 3 miles
INFO:__main__:Searching high_school...
INFO:__main__:Found 2 high schools within 3 miles
INFO:__main__:Searching grocery_store...
INFO:__main__:Found 4 grocery stores within 1 mile
INFO:__main__:Searching transit_stop...
INFO:__main__:Found 1 transit stops within 0.5 miles
INFO:__main__:Searching pharmacy...
INFO:__main__:Found 3 pharmacies within 2 miles
INFO:__main__:Searching hospital...
INFO:__main__:Found 1 hospitals within 5 miles
INFO:__main__:Searching park...
INFO:__main__:Found 2 parks within 1 mile

Site: 13921 Nutty Brown Rd, Austin, TX 78737
Proximity Score: 72.5/100 (Good)
- Nearest Elementary: Baranoff Elementary School (1.2 mi)
- Nearest Grocery: H-E-B Plus (0.8 mi)
- Nearest Transit: Capital Metro Bus Stop 334 (0.4 mi)
- Nearest Hospital: Seton Southwest Hospital (3.5 mi)

Processing site 2 of 227
...
```

## Sample Excel Output Preview

| Address | ... | elementary_school_nearest_miles | elementary_school_nearest_name | grocery_store_nearest_miles | grocery_store_nearest_name | transit_stop_nearest_miles | score_total_proximity_score | score_proximity_rating |
|---------|-----|--------------------------------|-------------------------------|----------------------------|---------------------------|---------------------------|---------------------------|---------------------|
| 13921 Nutty Brown Rd, Austin, TX 78737 | ... | 1.2 | Baranoff Elementary School | 0.8 | H-E-B Plus | 0.4 | 72.5 | Good |
| 9104 Atwater Cv, Austin, TX 78733-3233 | ... | 0.7 | Hill Elementary School | 1.2 | Whole Foods Market | 1.1 | 65.3 | Good |
| 19003 Chimney, Helotes, TX 78023 | ... | 0.5 | Los Reyes Elementary School | 0.6 | H-E-B | 2.5 | 68.9 | Good |

## Test File Selection

The file `/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Costar/TX/CoStar_TX_Land_TDHCA_FLOOD_Analysis_20250606_113809.xlsx` is an excellent candidate because:

1. **Has all required location data**: Full addresses, latitude, longitude
2. **Already analyzed**: Contains QCT/DDA/Flood analysis, so we can compare proximity scores with existing strategic scores
3. **Good sample size**: 227 properties across Texas
4. **Diverse locations**: Multiple counties and cities
5. **Land-specific**: These are actual land parcels for potential development

Would you like me to:
1. Create a test script that processes just the first 5-10 properties to demonstrate the functionality?
2. Show you how to obtain and configure a Google Maps API key?
3. Create the full integration with your existing Texas analysis pipeline?