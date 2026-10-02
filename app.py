
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Maharashtra Wealth Index",
    layout="wide"
)

st.title("Maharashtra District-wise Wealth Index")

# Load ranking data
df = pd.read_excel(
    "Wealth Index Finall..xlsx",
    sheet_name="ranking "
)

# Load latest map
gdf = gpd.read_file(
    "Maharashtra_Wealth_Index.geojson"
)

# Keep only required columns
gdf = gdf[["District", "geometry"]]

# Merge map with ranking data
map_data = gdf.merge(
    df[["District", "wealth_score", "rank"]],
    on="District",
    how="left"
)

# Create Maharashtra map
m = folium.Map(
    location=[19.75, 75.7],
    zoom_start=6,
    tiles="OpenStreetMap",
    max_bounds=True
)

# Fit map to Maharashtra boundary
minx, miny, maxx, maxy = gdf.total_bounds

m.fit_bounds([
    [miny, minx],
    [maxy, maxx]
])
def get_color(rank):
    if rank <= 7:
        return "#006400"
    elif rank <= 14:
        return "#32CD32"
    elif rank <= 21:
        return "#FFD700"
    elif rank <= 28:
        return "#FFA500"
    else:
        return "#DC143C"

# Add districts
folium.GeoJson(
    map_data,
   style_function=lambda feature: {
    "fillColor": get_color(feature["properties"]["rank"]),
    "color": "black",
    "weight": 1,
    "fillOpacity": 0.7
},
    popup=folium.GeoJsonPopup(
        fields=[
            "District",
            "wealth_score",
            "rank"
        ],
        aliases=[
            "District Name",
            "Wealth Score",
            "Rank"
        ],
        localize=True,
        labels=True
    )
).add_to(m)
# District names directly on the map
for _, row in map_data.iterrows():
    centroid = row.geometry.centroid

    folium.Marker(
        location=[centroid.y, centroid.x],
        icon=folium.DivIcon(
            html=f"""
            <div style="
                font-size: 9px;
                font-weight: bold;
                color: black;
                text-align: center;
                white-space: nowrap;
            ">
                {row['District']}
            </div>
            """
        )
    ).add_to(m)
# Display map directly as HTML
components.html(
    m._repr_html_(),
    height=650,
    scrolling=False
)
