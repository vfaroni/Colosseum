#!/usr/bin/env python3
"""
CTCAC Amenity Mapper with Parcel Boundary Support
Enhanced version that calculates distances from parcel edges instead of center point
Includes 1/3 mile circle and maintains all existing amenity data

Author: LIHTC Analysis Team
Date: July 4, 2025
"""

from ctcac_amenity_mapper_complete import CTCACAmenityMapperComplete
import folium
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import nearest_points
import numpy as np
import pandas as pd

class CTCACParcelBoundaryMapper(CTCACAmenityMapperComplete):
    """Enhanced CTCAC mapper that uses parcel boundaries for distance calculations"""
    
    def __init__(self, data_path=None):
        """Initialize with parent class"""
        super().__init__(data_path)
        
    def calculate_distance_from_parcel(self, parcel_polygon, amenity_lat, amenity_lng):
        """
        Calculate shortest distance from amenity to parcel boundary
        
        Args:
            parcel_polygon: Shapely Polygon object representing parcel
            amenity_lat: Latitude of amenity
            amenity_lng: Longitude of amenity
            
        Returns:
            Distance in miles from nearest parcel edge
        """
        # Create point for amenity
        amenity_point = Point(amenity_lng, amenity_lat)
        
        # If amenity is inside parcel, distance is 0
        if parcel_polygon.contains(amenity_point):
            return 0.0
        
        # Find nearest point on parcel boundary
        nearest_point_on_parcel = nearest_points(parcel_polygon.boundary, amenity_point)[0]
        
        # Calculate haversine distance between the two points
        lat1, lon1 = amenity_lat, amenity_lng
        lat2, lon2 = nearest_point_on_parcel.y, nearest_point_on_parcel.x
        
        return self.haversine_distance(lat1, lon1, lat2, lon2)
    
    def create_parcel_enhanced_map(self, parcel_corners, site_name="Development Site",
                                  is_rural=False, project_type='family', 
                                  qualifying_development=False, new_construction=False,
                                  large_family=False, opportunity_area_status=None,
                                  density_per_acre=None, zoom_level=14, project_address=None):
        """
        Create enhanced map with parcel boundaries and distance calculations from edges
        
        Args:
            parcel_corners: Dict with 'nw', 'ne', 'sw', 'se' keys, each with (lat, lng) tuples
            Other args same as parent class
        """
        # Create parcel polygon from corners
        # Order: NW -> NE -> SE -> SW -> NW (to close polygon)
        parcel_coords = [
            (parcel_corners['nw'][1], parcel_corners['nw'][0]),  # (lng, lat) for Shapely
            (parcel_corners['ne'][1], parcel_corners['ne'][0]),
            (parcel_corners['se'][1], parcel_corners['se'][0]),
            (parcel_corners['sw'][1], parcel_corners['sw'][0]),
            (parcel_corners['nw'][1], parcel_corners['nw'][0])   # Close polygon
        ]
        parcel_polygon = Polygon(parcel_coords[:-1])  # Don't include closing point in polygon
        
        # Calculate center point of parcel
        center_lat = (parcel_corners['nw'][0] + parcel_corners['ne'][0] + 
                     parcel_corners['sw'][0] + parcel_corners['se'][0]) / 4
        center_lng = (parcel_corners['nw'][1] + parcel_corners['ne'][1] + 
                     parcel_corners['sw'][1] + parcel_corners['se'][1]) / 4
        
        # Get base amenity data using center point for initial search
        # This gets all amenities within maximum search radius
        results = self.calculate_complete_amenity_scores(
            center_lat, center_lng, is_rural, project_type, density_per_acre,
            qualifying_development, new_construction, large_family, opportunity_area_status
        )
        
        # Recalculate distances from parcel boundaries for all found amenities
        for category, amenities in results['amenities_found'].items():
            for amenity in amenities:
                if 'latitude' in amenity and 'longitude' in amenity:
                    # Recalculate distance from nearest parcel edge
                    edge_distance = self.calculate_distance_from_parcel(
                        parcel_polygon, 
                        amenity['latitude'], 
                        amenity['longitude']
                    )
                    amenity['distance_miles_from_parcel'] = edge_distance
                    amenity['distance_miles_from_center'] = amenity.get('distance_miles', 0)
                    # Use parcel edge distance for scoring
                    amenity['distance_miles'] = edge_distance
        
        # Recalculate scores based on new distances
        results = self._recalculate_scores_with_parcel_distances(
            results, is_rural, project_type, qualifying_development
        )
        
        # Create base map
        m = folium.Map(location=[center_lat, center_lng], zoom_start=zoom_level)
        
        # Add map controls
        from folium import plugins
        plugins.MeasureControl(position='topright', active_color='blue', completed_color='red').add_to(m)
        folium.plugins.MiniMap(toggle_display=True).add_to(m)
        
        # Add parcel boundary
        parcel_folium_coords = [[lat, lng] for lng, lat in parcel_coords]
        folium.Polygon(
            locations=parcel_folium_coords,
            color='darkred',
            weight=3,
            fill=True,
            fillColor='red',
            fillOpacity=0.1,
            popup=f'<b>{site_name} Parcel</b><br>Area: 5.26 acres'
        ).add_to(m)
        
        # Add center marker
        folium.Marker(
            [center_lat, center_lng],
            popup=f"""<b>{site_name}</b><br>
                     {project_address if project_address else 'Development Site'}<br>
                     Parcel Center: {center_lat:.6f}, {center_lng:.6f}<br>
                     Total CTCAC Points: {results['total_points']}/15<br>
                     Project Type: {project_type.replace('_', ' ').title()}<br>
                     Use Rural Dist?: {'Yes' if is_rural else 'No'}""",
            icon=folium.Icon(color='red', icon='home')
        ).add_to(m)
        
        # Add corner markers
        corner_labels = {'nw': 'NW', 'ne': 'NE', 'sw': 'SW', 'se': 'SE'}
        for corner, label in corner_labels.items():
            lat, lng = parcel_corners[corner]
            folium.Marker(
                [lat, lng],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 10pt; color: darkred; font-weight: bold; '
                         f'background: white; padding: 2px 4px; border: 1px solid darkred; '
                         f'border-radius: 3px;">{label}</div>'
                )
            ).add_to(m)
        
        # Add distance circles FROM PARCEL EDGES
        self._add_parcel_based_circles(m, parcel_polygon, parcel_folium_coords, 
                                      is_rural, project_type, qualifying_development)
        
        # Add amenity markers
        legend_data = self._add_enhanced_amenity_markers(m, results)
        
        # Create and add legend
        legend_html = self._create_enhanced_legend(results, legend_data)
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m, results
    
    def _add_parcel_based_circles(self, map_obj, parcel_polygon, parcel_coords,
                                  is_rural, project_type, qualifying_development):
        """Add distance circles measured from parcel boundaries"""
        
        # Add ALL reference distance circles as requested: 0.25, 1/3, 0.5, 1.0 mile
        reference_distances = [
            (0.25, 'black', '0.25 mile', 'Reference', '5,5'),
            (0.333, 'gray', '1/3 mile', 'Reference', '10,5'),
            (0.5, 'darkgray', '0.5 mile', 'Reference', '15,5'),
            (1.0, 'lightgray', '1.0 mile', 'Reference', '20,5')
        ]
        
        for dist, color, label, category, dash in reference_distances:
            self._add_distance_ring_from_parcel(
                map_obj, parcel_polygon, parcel_coords, dist,
                color, label, category, dash_pattern=dash
            )
        
        distance_set = 'rural' if is_rural else 'standard'
        
        # Parks (if data available)
        park_distances = self.distance_rules['public_park']['park_community_center'][distance_set]
        for dist in park_distances:
            self._add_distance_ring_from_parcel(
                map_obj, parcel_polygon, parcel_coords, dist,
                'darkgreen', f'{dist} mi', 'Parks', dash_pattern='10,10'
            )
        
        # Transit circles - don't duplicate if already in reference circles
        transit_special = [0.33]  # Special transit distance not in reference
        for dist in transit_special:
            if dist not in [0.25, 0.333, 0.5, 1.0]:
                self._add_distance_ring_from_parcel(
                    map_obj, parcel_polygon, parcel_coords, dist,
                    'green', f'{dist} mi', 'Transit', dash_pattern='8,4'
                )
        
        # Libraries
        lib_distances = self.distance_rules['library']['public_library'][distance_set]
        for dist in lib_distances:
            if dist not in [0.25, 0.333, 0.5, 1.0]:
                self._add_distance_ring_from_parcel(
                    map_obj, parcel_polygon, parcel_coords, dist,
                    'darkblue', f'{dist} mi', 'Library', dash_pattern='12,6'
                )
        
        # Pharmacies
        pharm_distances = self.distance_rules['pharmacy']['pharmacy'][distance_set]
        for dist in pharm_distances:
            if dist not in [0.25, 0.333, 0.5, 1.0]:
                self._add_distance_ring_from_parcel(
                    map_obj, parcel_polygon, parcel_coords, dist,
                    'hotpink', f'{dist} mi', 'Pharmacy', dash_pattern='15,5'
                )
        
        # Schools (if qualifying development)
        if qualifying_development:
            # Elementary schools
            elem_distances = self.distance_rules['schools']['elementary'][distance_set]
            for dist in elem_distances:
                if dist not in [0.25, 0.333, 0.5, 1.0]:
                    self._add_distance_ring_from_parcel(
                        map_obj, parcel_polygon, parcel_coords, dist,
                        'green', f'{dist} mi', 'Elementary', dash_pattern='6,3'
                    )
            
            # Middle schools  
            middle_distances = self.distance_rules['schools']['middle'][distance_set]
            for dist in middle_distances:
                if dist not in [0.25, 0.333, 0.5, 1.0]:
                    self._add_distance_ring_from_parcel(
                        map_obj, parcel_polygon, parcel_coords, dist,
                        'orange', f'{dist} mi', 'Middle School', dash_pattern='8,4'
                    )
            
            # High schools
            high_distances = self.distance_rules['schools']['high'][distance_set]
            for dist in high_distances:
                if dist not in [0.25, 0.333, 0.5, 1.0]:
                    self._add_distance_ring_from_parcel(
                        map_obj, parcel_polygon, parcel_coords, dist,
                        'red', f'{dist} mi', 'High School', dash_pattern='10,5'
                    )
        
        # Medical facilities
        medical_distances = self.distance_rules['medical']['clinic_hospital'][distance_set]
        for dist in medical_distances:
            if dist not in [0.25, 0.333, 0.5, 1.0]:
                self._add_distance_ring_from_parcel(
                    map_obj, parcel_polygon, parcel_coords, dist,
                    'red', f'{dist} mi', 'Medical', dash_pattern='18,6'
                )
        
        # Grocery stores
        grocery_full_distances = self.distance_rules['grocery']['full_scale'][distance_set]
        for dist in grocery_full_distances:
            if dist not in [0.25, 0.333, 0.5, 1.0]:
                self._add_distance_ring_from_parcel(
                    map_obj, parcel_polygon, parcel_coords, dist,
                    'cadetblue', f'{dist} mi', 'Grocery', dash_pattern='14,7'
                )
    
    def _add_distance_ring_from_parcel(self, map_obj, parcel_polygon, parcel_coords,
                                       distance_miles, color, label, category, dash_pattern='10,5'):
        """Add a distance ring measured from parcel edges"""
        
        # Create offset polygon (buffer) from parcel boundary
        # Convert miles to degrees (approximate)
        distance_degrees = distance_miles / 69.0  # Rough conversion
        
        # Create buffered polygon
        buffered = parcel_polygon.buffer(distance_degrees)
        
        # Extract coordinates for Folium
        if buffered.geom_type == 'Polygon':
            coords = list(buffered.exterior.coords)
            folium_coords = [[lat, lng] for lng, lat in coords]
            
            # Add the distance ring
            folium.Polygon(
                locations=folium_coords,
                color=color,
                weight=2,
                fill=False,
                dashArray=dash_pattern,
                popup=f'{category}: {label} from parcel boundary'
            ).add_to(map_obj)
            
            # Add label
            # Find northernmost point of buffer for label placement
            north_point = max(coords, key=lambda p: p[1])
            folium.Marker(
                [north_point[1], north_point[0]],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 10pt; color: {color}; font-weight: bold; '
                         f'background: white; padding: 1px 3px; border-radius: 3px;">'
                         f'{label} {category}</div>'
                )
            ).add_to(map_obj)
    
    def _recalculate_scores_with_parcel_distances(self, results, is_rural, 
                                                  project_type, qualifying_development):
        """Recalculate CTCAC scores based on distances from parcel edges"""
        
        new_total = 0
        
        # Recalculate Parks score
        if 'public_parks' in results['amenities_found'] and results['amenities_found']['public_parks']:
            parks_df = pd.DataFrame(results['amenities_found']['public_parks'])
            park_score = self._score_parks_complete(parks_df, is_rural)
            results['scoring_summary']['public_park'] = park_score
            new_total += park_score.get('points', 0)
        
        # Recalculate Pharmacy score
        if 'pharmacies' in results['amenities_found'] and results['amenities_found']['pharmacies']:
            pharmacy_df = pd.DataFrame(results['amenities_found']['pharmacies'])
            pharmacy_score = self._score_pharmacies_complete(pharmacy_df, is_rural)
            results['scoring_summary']['pharmacy'] = pharmacy_score
            new_total += pharmacy_score.get('points', 0)
        
        # Recalculate Library score
        if 'libraries' in results['amenities_found'] and results['amenities_found']['libraries']:
            library_df = pd.DataFrame(results['amenities_found']['libraries'])
            library_score = self._score_libraries_complete(library_df, is_rural)
            results['scoring_summary']['library'] = library_score
            new_total += library_score.get('points', 0)
        
        # Recalculate Medical score
        if 'medical' in results['amenities_found'] and results['amenities_found']['medical']:
            medical_df = pd.DataFrame(results['amenities_found']['medical'])
            medical_score = self._score_medical_complete(medical_df, is_rural)
            results['scoring_summary']['medical'] = medical_score
            new_total += medical_score.get('points', 0)
        
        # Recalculate Grocery score  
        if 'grocery' in results['amenities_found'] and results['amenities_found']['grocery']:
            grocery_df = pd.DataFrame(results['amenities_found']['grocery'])
            grocery_score = self._score_grocery_complete(grocery_df, is_rural)
            results['scoring_summary']['grocery'] = grocery_score
            new_total += grocery_score.get('points', 0)
        
        # Keep existing scores for categories not recalculated
        for category, score_data in results['scoring_summary'].items():
            if category not in ['public_park', 'pharmacy', 'library', 'medical', 'grocery']:
                if isinstance(score_data, dict) and 'points' in score_data:
                    new_total += score_data['points']
                elif category == 'schools' and isinstance(score_data, dict):
                    new_total += sum([v for v in score_data.values() if isinstance(v, (int, float))])
        
        # Update total and add note (cap at 15 points maximum per CTCAC rules)
        results['total_points'] = min(new_total, 15)
        results['calculation_note'] = 'Distances calculated from nearest parcel boundary'
        
        return results


def analyze_site_with_parcel_boundary(parcel_corners, address, **kwargs):
    """
    Convenience function to analyze a site using parcel boundaries
    
    Args:
        parcel_corners: Dict with 'nw', 'ne', 'sw', 'se' corners as (lat, lng) tuples
        address: Address string for the site
        **kwargs: Additional arguments for the analysis
    
    Returns:
        Tuple of (map_object, results_dict)
    """
    mapper = CTCACParcelBoundaryMapper()
    
    return mapper.create_parcel_enhanced_map(
        parcel_corners=parcel_corners,
        project_address=address,
        **kwargs
    )


# For backward compatibility - analyze using address with parcel corners
def analyze_complete_site_with_parcel(parcel_corners, address, **kwargs):
    """Wrapper to maintain compatibility with existing code"""
    return analyze_site_with_parcel_boundary(parcel_corners, address, **kwargs)