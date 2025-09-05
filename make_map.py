import osmnx as ox
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster

# Define the place and tags
place = "Curitiba, Brazil"
tags = {"highway": "bus_stop"}
description = "Bus Stop"
zoom_level = 13

# Fields to include in popup
popup_fields = ["name", "operator", "network", "ref"]

# Fetch bus stop features
gdf = ox.features_from_place(place, tags=tags)

# Ensure the GeoDataFrame has the correct CRS
gdf = gdf.to_crs(epsg=4326)

# Ensure requested popup fields exist
for field in popup_fields:
    if field not in gdf.columns:
        gdf[field] = ""

# Compute the centroid of all bus stops
centroid = gdf.union_all().centroid
center_latlon = [centroid.y, centroid.x]

# Create a Folium map centered at the centroid with multiple tile layers
m = folium.Map(location=center_latlon, zoom_start=zoom_level, tiles=None)
folium.TileLayer("CartoDB positron", name="CartoDB Positron").add_to(m)
folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
folium.TileLayer(
    "Stamen Terrain",
    name="Stamen Terrain",
    attr="Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors",
).add_to(m)

# Add bus stop markers to the map using a MarkerCluster plugin
marker_cluster = MarkerCluster(name="Bus Stops (Cluster)").add_to(m)
for _, row in gdf.iterrows():
    coords = row.geometry
    if coords.geom_type == "Point":
        folium.Marker(
            location=[coords.y, coords.x],
            popup=row.get("name", description),
        ).add_to(marker_cluster)

# Add a regular point layer with interactive markers
interactive_layer = folium.GeoJson(
    gdf,
    name="Bus Stops (Points)",
    marker=folium.CircleMarker(
        radius=5, color="blue", fill=True, fill_opacity=0.7
    ),
    highlight_function=lambda x: {"radius": 8},
    popup=folium.GeoJsonPopup(fields=popup_fields, labels=True),
).add_to(m)

# Try to fetch and display the administrative boundary polygon for the place.
# OpenStreetMap uses the "admin_level" tag for such boundaries:
# https://wiki.openstreetmap.org/wiki/Key:admin_level
try:
    boundary_gdf = ox.geocode_to_gdf(place).to_crs(epsg=4326)
    folium.GeoJson(
        boundary_gdf,
        name="Boundary",
        style_function=lambda x: {"fillOpacity": 0, "color": "green"},
    ).add_to(m)
except Exception:
    pass

# Add layer control to toggle tile layers
folium.LayerControl().add_to(m)

# Save the map
m.save("index.html")
