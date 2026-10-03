
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
    "maharashtra wealth index final.xlsx",
    sheet_name="ranking"
)

# Load Maharashtra map
gdf = gpd.read_file(
    "Maharashtra_Wealth_Index.geojson"
)

# Keep required columns
gdf = gdf[["District", "geometry"]]

# Merge map and ranking data
map_data = gdf.merge(
    df[["District", "wealth_score", "rank"]],
    on="District",
    how="left"
)

# -------------------------
# CREATE MAHARASHTRA MAP
# -------------------------

minx, miny, maxx, maxy = map_data.total_bounds

m = folium.Map(
    tiles="OpenStreetMap",
    zoom_control=True,
    scrollWheelZoom=True
)

# Focus only on Maharashtra
m.fit_bounds([
    [miny, minx],
    [maxy, maxx]
])

# Prevent moving too far away from Maharashtra
m.options["maxBounds"] = [
    [miny - 0.5, minx - 0.5],
    [maxy + 0.5, maxx + 0.5]
]

m.options["maxBoundsViscosity"] = 1.0


# -------------------------
# WEALTH LEVEL COLOURS
# -------------------------

def get_color(rank):

    if pd.isna(rank):
        return "lightgray"

    elif rank <= 7:
        return "#006400"       # High Wealth

    elif rank <= 14:
        return "#32CD32"       # Medium-High Wealth

    elif rank <= 21:
        return "#FFD700"       # Medium Wealth

    elif rank <= 28:
        return "#FFA500"       # Medium-Low Wealth

    else:
        return "#DC143C"       # Low Wealth


# -------------------------
# DISTRICT MAP
# -------------------------

folium.GeoJson(
    map_data,

    style_function=lambda feature: {
        "fillColor": get_color(
            feature["properties"]["rank"]
        ),
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


# -------------------------
# DISTRICT NAMES
# -------------------------

for _, row in map_data.iterrows():

    if row.geometry is not None:

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
                ">
                    {row['District']}
                </div>
                """
            )
        ).add_to(m)


# -------------------------
# LEGEND
# -------------------------

legend_html = """
<div style="
position: fixed;
bottom: 40px;
right: 20px;
width: 190px;
z-index: 9999;
background-color: white;
border: 2px solid grey;
border-radius: 8px;
padding: 12px;
font-size: 13px;
">

<b>Wealth Level</b><br><br>

<div>
<span style="
background:#006400;
width:18px;
height:18px;
display:inline-block;
margin-right:8px;
"></span>
High Wealth
</div>

<div>
<span style="
background:#32CD32;
width:18px;
height:18px;
display:inline-block;
margin-right:8px;
"></span>
Medium-High Wealth
</div>

<div>
<span style="
background:#FFD700;
width:18px;
height:18px;
display:inline-block;
margin-right:8px;
"></span>
Medium Wealth
</div>

<div>
<span style="
background:#FFA500;
width:18px;
height:18px;
display:inline-block;
margin-right:8px;
"></span>
Medium-Low Wealth
</div>

<div>
<span style="
background:#DC143C;
width:18px;
height:18px;
display:inline-block;
margin-right:8px;
"></span>
Low Wealth
</div>

</div>
"""

m.get_root().html.add_child(
    folium.Element(legend_html)
)


# -------------------------
# DISPLAY MAP
# -------------------------

components.html(
    m._repr_html_(),
    height=650,
    scrolling=False
)
