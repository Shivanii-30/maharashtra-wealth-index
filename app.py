import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go

st.set_page_config(
    page_title="Maharashtra District-wise Wealth Index",
    layout="wide"
)

st.title("Maharashtra District-wise Wealth Index")

# 1. READ EXCEL
df = pd.read_excel(
    "Wealth Index Finall..xlsx",
    sheet_name="ranking "
)

df = df[["District", "wealth_score", "rank"]]

df["rank"] = pd.to_numeric(
    df["rank"], errors="coerce"
)

# 2. DISTRICT NAME CORRECTION
new_names = {
    "Ahmednagar": "Ahilyanagar",
    "Aurangabad": "Chhatrapati Sambhajinagar",
    "Osmanabad": "Dharashiv"
}

df["District"] = df["District"].replace(new_names)

# 3. READ GEOJSON
with open(
    "Maharashtra_Wealth_Index.geojson",
    "r",
    encoding="utf-8"
) as f:
    geojson = json.load(f)

# Correct GeoJSON district names
for feature in geojson["features"]:
    name = feature["properties"].get("District")

    if name in new_names:
        feature["properties"]["District"] = new_names[name]

# 4. RANK COLOUR
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

# 5. CREATE MAP
fig = go.Figure()

# Add each district separately
for feature in geojson["features"]:

    district = feature["properties"].get("District")

    row = df[df["District"] == district]

    if row.empty:
        continue

    rank = row.iloc[0]["rank"]
    score = row.iloc[0]["wealth_score"]

    color = get_color(rank)

    geometry = feature["geometry"]

    def add_polygon(coords):

        lons = []
        lats = []

        for point in coords:
            lons.append(point[0])
            lats.append(point[1])

        fig.add_trace(
            go.Scattergeo(
                lon=lons,
                lat=lats,
                mode="lines",
                fill="toself",
                fillcolor=color,
                line=dict(
                    color="black",
                    width=1
                ),
                text=(
                    f"<b>{district}</b><br>"
                    f"Wealth Score: {score:.4f}<br>"
                    f"Rank: {int(rank)}"
                ),
                hoverinfo="text",
                showlegend=False
            )
        )

    if geometry["type"] == "Polygon":

        for polygon in geometry["coordinates"]:
            add_polygon(polygon)

    elif geometry["type"] == "MultiPolygon":

        for multipolygon in geometry["coordinates"]:
            for polygon in multipolygon:
                add_polygon(polygon)

# 6. DISTRICT LABELS
for feature in geojson["features"]:

    district = feature["properties"].get("District")

    row = df[df["District"] == district]

    if row.empty:
        continue

    rank = row.iloc[0]["rank"]
    geometry = feature["geometry"]

    # Collect coordinates
    points = []

    def collect_points(obj):
        if isinstance(obj, list):

            if (
                len(obj) >= 2
                and isinstance(obj[0], (int, float))
            ):
                points.append((obj[0], obj[1]))

            else:
                for item in obj:
                    collect_points(item)

    collect_points(geometry["coordinates"])

    if points:

        lon = sum(p[0] for p in points) / len(points)
        lat = sum(p[1] for p in points) / len(points)

        fig.add_trace(
            go.Scattergeo(
                lon=[lon],
                lat=[lat],
                text=f"<b>{district}</b><br>Rank: {int(rank)}",
                mode="text",
                textfont=dict(
                    size=9,
                    color="black"
                ),
                hoverinfo="text",
                showlegend=False
            )
        )

# 7. MAP SETTINGS
fig.update_geos(
    visible=False,
    projection_type="mercator",
    showland=True,
    landcolor="white",
    showocean=True,
    oceancolor="white",
    showcountries=False,
    showcoastlines=False
)

fig.update_layout(
    height=650,
    margin=dict(
        r=0,
        t=5,
        l=0,
        b=0
    ),
    paper_bgcolor="white",
    plot_bgcolor="white"
)

# 8. DISPLAY
st.plotly_chart(
    fig,
    use_container_width=True
)
