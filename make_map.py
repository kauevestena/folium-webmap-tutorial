import osmnx as ox
import geopandas as gpd
import folium

# Define the place and tags
place = "Curitiba, Brazil"
tags = {"highway": "bus_stop"}
description = "Bus Stop"
zoom_level = 13

# Fetch bus stop features
gdf = ox.features_from_place(place, tags=tags)

# Ensure the GeoDataFrame has the correct CRS
gdf = gdf.to_crs(epsg=4326)

# Compute the centroid of all bus stops
centroid = gdf.unary_union.centroid
center_latlon = [centroid.y, centroid.x]

# Create a Folium map centered at the centroid
m = folium.Map(location=center_latlon, zoom_start=zoom_level, tiles="CartoDB positron")

# Add bus stop markers to the map
for _, row in gdf.iterrows():
    coords = row.geometry
    if coords.geom_type == 'Point':
        folium.CircleMarker(
            location=[coords.y, coords.x],
            radius=3,
            color="blue",
            fill=True,
            fill_opacity=0.7,
            popup=row.get("name", description)
        ).add_to(m)

# Save the map
m.save("index.html")
