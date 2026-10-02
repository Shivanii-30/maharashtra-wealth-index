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
excel_file = "Wealth Index Finall..xlsx"

excel = pd.ExcelFile(excel_file)

if "ranking" not in excel.sheet_names:
    st.error(
        f"Sheet 'ranking' not found. "
        f"Available sheets: {excel.sheet_names}"
    )
    st.stop()

df = pd.read_excel(
    excel_file,
    sheet_name="ranking"
)

# Load Maharashtra GeoJSON
gdf = gpd.read_file(
    "Maharashtra_Wealth_Index-1.geojson"
)

# Keep required columns
gdf = gdf[["District", "geometry"]]

# Merge ranking data with map
map_data = gdf.merge(
    df[["District", "wealth_score", "rank"]],
    on="District",
    how="left"
)

# Rank-based colours
def get_color(rank):
    if pd.isna(rank):
        return "#D3D3D3"
    elif rank <= 7:
        return "#006400"
    elif rank <= 14:
        return "#32CD32"
    elif rank <= 21:
        return "#FFD700"
    elif rank <= 28:
        return "#FFA500"
    else:
        return "#DC143C"


# Create map
# No OpenStreetMap background
m = folium.Map(
    location=[19.75, 75.7],
    zoom_start=6,
    tiles=None,
    control_scale=True
)

# Fit map exactly to Maharashtra GeoJSON
minx, miny, maxx, maxy = gdf.total_bounds

m.fit_bounds([
    [miny, minx],
    [maxy, maxx]
])


# Add Maharashtra districts
folium.GeoJson(
    map_data,
    style_function=lambda feature: {
        "fillColor": get_color(
            feature["properties"]["rank"]
        ),
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.75
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
    ),
    highlight_function=lambda feature: {
        "weight": 2,
        "color": "black",
        "fillOpacity": 0.85
    }
).add_to(m)


# Add district names
for _, row in map_data.iterrows():

    if row.geometry is None:
        continue

    centroid = row.geometry.centroid

    folium.Marker(
        location=[
            centroid.y,
            centroid.x
        ],
        icon=folium.DivIcon(
            html=f"""
            <div style="
                font-size: 9px;
                font-weight: bold;
                color: black;
                text-align: center;
                white-space: nowrap;
                text-shadow:
                    1px 1px 2px white,
                    -1px -1px 2px white,
                    1px -1px 2px white,
                    -1px 1px 2px white;
            ">
                {row['District']}
            </div>
            """
        )
    ).add_to(m)


# Legend
legend_html = """
<div style="
    position: fixed;
    top: 20px;
    right: 20px;
    width: 175px;
    background-color: white;
    border: 2px solid grey;
    border-radius: 5px;
    z-index: 9999;
    font-size: 13px;
    padding: 10px;
    box-shadow: 0 0 6px rgba(0,0,0,0.3);
">

<b>Wealth Index Level</b>
<br><br>

<span style="color:#006400; font-size:18px;">■</span>
Very High
<br>

<span style="color:#32CD32; font-size:18px;">■</span>
High
<br>

<span style="color:#FFD700; font-size:18px;">■</span>
Medium
<br>

<span style="color:#FFA500; font-size:18px;">■</span>
Low
<br>

<span style="color:#DC143C; font-size:18px;">■</span>
Very Low

</div>
"""

m.get_root().html.add_child(
    folium.Element(legend_html)
)


# Display map in Streamlit
components.html(
    m._repr_html_(),
    height=700,
    scrolling=False
)
