import streamlit as st
import pandas as pd
import json
import plotly.express as px
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

# 2. KEEP REQUIRED COLUMNS
df = df[["District", "wealth_score", "rank"]]

# Make sure rank is numeric
df["rank"] = pd.to_numeric(
    df["rank"], errors="coerce"
).astype("Int64")

# 3. READ GEOJSON
with open(
    "Maharashtra_Wealth_Index.geojson",
    "r",
    encoding="utf-8"
) as f:
    geojson = json.load(f)

# 4. UPDATE DISTRICT NAMES IF REQUIRED
new_names = {
    "Ahmednagar": "Ahilyanagar",
    "Aurangabad": "Chhatrapati Sambhajinagar",
    "Osmanabad": "Dharashiv"
}

df["District"] = df["District"].replace(new_names)

for feature in geojson["features"]:
    old_name = feature["properties"].get("District")

    if old_name in new_names:
        feature["properties"]["District"] = new_names[old_name]

# 5. RANK GROUPS
def get_level(rank):
    if pd.isna(rank):
        return "No Data"
    elif rank <= 7:
        return "Rank 1–7"
    elif rank <= 14:
        return "Rank 8–14"
    elif rank <= 21:
        return "Rank 15–21"
    elif rank <= 28:
        return "Rank 22–28"
    else:
        return "Rank 29–34"

df["Wealth Level"] = df["rank"].apply(get_level)

# 6. CHOROPLETH MAP
st.subheader("District-wise Wealth Index Map")

fig = px.choropleth(
    df,
    geojson=geojson,
    locations="District",
    featureidkey="properties.District",
    color="Wealth Level",
    hover_name="District",
    hover_data={
        "wealth_score": ":.4f",
        "rank": True,
        "Wealth Level": True
    },
    color_discrete_map={
        "Rank 1–7": "#006400",
        "Rank 8–14": "#32CD32",
        "Rank 15–21": "#FFD700",
        "Rank 22–28": "#FFA500",
        "Rank 29–34": "#DC143C",
        "No Data": "#D3D3D3"
    }
)

# 7. DISTRICT LABEL POSITIONS
def get_all_points(coords):
    points = []

    def extract(obj):
        if isinstance(obj, (list, tuple)):
            if (
                len(obj) >= 2
                and isinstance(obj[0], (int, float))
            ):
                points.append((obj[0], obj[1]))
            else:
                for item in obj:
                    extract(item)

    extract(coords)
    return points


label_data = []

for feature in geojson["features"]:

    district_name = feature["properties"].get("District")
    geometry = feature["geometry"]

    points = get_all_points(
        geometry["coordinates"]
    )

    if points:
        avg_lon = sum(
            p[0] for p in points
        ) / len(points)

        avg_lat = sum(
            p[1] for p in points
        ) / len(points)

        label_data.append({
            "District": district_name,
            "lon": avg_lon,
            "lat": avg_lat
        })

labels = pd.DataFrame(label_data)

# 8. MATCH RANK WITH DISTRICT
labels = labels.merge(
    df[["District", "rank"]],
    on="District",
    how="left"
)

# 9. ADD DISTRICT NAME + RANK
fig.add_trace(
    go.Scattergeo(
        lon=labels["lon"],
        lat=labels["lat"],
        text=[
            (
                f"<b>{name}</b><br>Rank: {int(rank)}"
                if pd.notna(rank)
                else f"<b>{name}</b><br>Rank: No Data"
            )
            for name, rank in zip(
                labels["District"],
                labels["rank"]
            )
        ],
        mode="text",
        textfont=dict(
            size=9,
            color="black"
        ),
        hoverinfo="text",
        showlegend=False
    )
)

# 10. KEEP MAP FOCUSED ON MAHARASHTRA
fig.update_geos(
    fitbounds="locations",
    visible=False,
    showcountries=False,
    showcoastlines=False,
    showland=False
)

fig.update_layout(
    height=650,
    margin=dict(
        r=0,
        t=5,
        l=0,
        b=0
    )
)

# 11. DISPLAY MAP
st.plotly_chart(
    fig,
    use_container_width=True
)
