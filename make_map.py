# 1. Import required libraries
import osmnx as ox
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster

# 2. Define the geographic area and feature tags to download
place = "Curitiba, Brazil"
tags = {"highway": "bus_stop"}
description = "Bus Stop"
zoom_level = 13

# 3. Specify which fields to show inside marker popups
popup_fields = ["name", "operator", "network", "ref"]

# 4. Download bus stop features from OpenStreetMap for the chosen place
gdf = ox.features_from_place(place, tags=tags)

# 5. Ensure the GeoDataFrame is in the latitude/longitude coordinate system
gdf = gdf.to_crs(epsg=4326)

# 6. Add any missing columns so popups don't break
for field in popup_fields:
    if field not in gdf.columns:
        gdf[field] = ""

# 7. Compute the centroid of all bus stops to center the map
centroid = gdf.union_all().centroid
center_latlon = [centroid.y, centroid.x]

# 8. Create a Folium map and add a few base tile layers
m = folium.Map(location=center_latlon, zoom_start=zoom_level, tiles=None)
folium.TileLayer("CartoDB positron", name="CartoDB Positron").add_to(m)
folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
folium.TileLayer(
    "Stamen Terrain",
    name="Stamen Terrain",
    attr="Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors",
).add_to(m)

# 9. Add bus stop markers to the map using a MarkerCluster plugin
marker_cluster = MarkerCluster(name="Bus Stops (Cluster)").add_to(m)
for _, row in gdf.iterrows():
    coords = row.geometry
    if coords.geom_type == "Point":
        folium.Marker(
            location=[coords.y, coords.x],
            popup=row.get("name", description),
        ).add_to(marker_cluster)

# 10. Add a plain GeoJSON layer with interactive circle markers
interactive_layer = folium.GeoJson(
    gdf,
    name="Bus Stops (Points)",
    marker=folium.CircleMarker(
        radius=5, color="blue", fill=True, fill_opacity=0.7
    ),
    highlight_function=lambda x: {"radius": 8},
    popup=folium.GeoJsonPopup(fields=popup_fields, labels=True),
).add_to(m)

# 11. Try to fetch and display the administrative boundary polygon
#     OpenStreetMap uses the "admin_level" tag for such boundaries:
#     https://wiki.openstreetmap.org/wiki/Key:admin_level
try:
    boundary_gdf = ox.geocode_to_gdf(place).to_crs(epsg=4326)
    folium.GeoJson(
        boundary_gdf,
        name="Boundary",
        style_function=lambda x: {"fillOpacity": 0, "color": "green"},
    ).add_to(m)
except Exception:
    pass

# 12. Allow the user to toggle layers on and off
folium.LayerControl().add_to(m)

# 13. Save the map to an HTML file
m.save("index.html")
