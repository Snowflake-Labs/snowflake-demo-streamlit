# Before running this app install these two datasets
# CARTO Academy - Data for tutorials: https://app.snowflake.com/marketplace/listing/GZT0Z4CM1E9J2/carto-carto-academy-data-for-tutorials
# U.S. ZIP Code Metadata with Geometry: https://app.snowflake.com/marketplace/listing/GZTYZ7P39MI/sfr-analytics-u-s-zip-code-metadata-with-geometry

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import json
from typing import List
import branca.colormap as cm
from snowflake.snowpark.context import get_active_session


#------Visualisation using points -----------

st.title("Geo visualisation using Pydeck and Streamlit in Snowflake")
st.write(
    """
    This quickstart Showcases how to visualise different geospatial objects using Streamlit in Snowlflake.
    Before running this application make sure that you installed following two listings:
    - [CARTO Academy - Data for tutorials](https://app.snowflake.com/marketplace/listing/GZT0Z4CM1E9J2/carto-carto-academy-data-for-tutorials) 
    - [U.S. ZIP Code Metadata with Geometry](https://app.snowflake.com/marketplace/listing/GZTYZ7P39MI/sfr-analytics-u-s-zip-code-metadata-with-geometry)
    """)
session = get_active_session()
df = session.sql('select geom as border from CARTO_Academy__Data_for_tutorials.CARTO.CELL_TOWERS_NY').to_pandas()
df["lon"] = df["BORDER"].apply(lambda row: json.loads(row)["coordinates"][0])
df["lat"] = df["BORDER"].apply(lambda row: json.loads(row)["coordinates"][1])

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=40.782585,
        longitude=-73.994529, pitch=45, zoom=11
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            df,
            get_position=["lon", "lat"],
            id="regions",
            opacity=0.9,
            stroked=True,
            filled=False,
            extruded=True,
            wireframe=True,
            get_fill_color=[189, 219, 0],
            get_line_color=[223, 0, 115],
            get_radius=5,
            auto_highlight=True,
            pickable=False,
        )
    ],
))



#------Visualisation using H3 -----------
st.title("Cell Towers density")
def get_df(h3_resolut_3: int) -> pd.DataFrame:
    return session.sql(f'select h3_point_to_cell_string(geom, {h3_resolut_3}) as h3, count(*) as count\n'\
                       'from CARTO_Academy__Data_for_tutorials.CARTO.CELL_TOWERS_NY\n'\
                       'where 2 = 2\n'\
                       'group by 1\n').to_pandas()


def get_quantiles(df_column: pd.Series, quantiles: List) -> pd.Series:
    return df_column.quantile(quantiles)


def get_color(df_column: pd.Series, colors: List, vmin: int, vmax: int, index: pd.Series) -> pd.Series:
    color_map = cm.LinearColormap(colors, vmin=vmin, vmax=vmax, index=index)
    return df_column.apply(color_map.rgb_bytes_tuple)


def get_layer(df: pd.DataFrame) -> pdk.Layer:
    return pdk.Layer("H3HexagonLayer", 
                     df, 
                     get_hexagon="H3",
                     get_fill_color="COLOR", 
                     get_line_color="COLOR",
                     get_elevation="COUNT/200",
                     auto_highlight=True,
                     elevation_scale=50,
                     pickable=True,
                     elevation_range=[0, 300],
                     extruded=True,
                     coverage=1,
                     opacity=0.3)
   
col1, col2 = st.columns(2)
with col1:
    h3_resolut_3 = st.slider(
        "H3 resolution  ",
        min_value=6, max_value=9, value=7)

with col2:
    style_option_t_3 = st.selectbox("Style schema ",
                                ("Contrast", "Snowflake"), 
                                index=0)

df_3 = get_df(h3_resolut_3)

if style_option_t_3 == "Contrast":
    quantiles_3 = get_quantiles(df_3["COUNT"], [0, 0.25, 0.5, 0.75, 1])
    colors_3 = ['gray','blue','green','yellow','orange','red']
if style_option_t_3 == "Snowflake":
    quantiles_3 = get_quantiles(df_3["COUNT"], [0, 0.33, 0.66, 1])
    colors_3 = ['#666666', '#24BFF2', '#126481', '#D966FF']

df_3['COLOR'] = get_color(df_3['COUNT'], colors_3, quantiles_3.min(), quantiles_3.max(), quantiles_3)
layer_3 = get_layer(df_3)

st.pydeck_chart(pdk.Deck(map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=40.782585,
        longitude=-73.994529, pitch=45, zoom=11),
        tooltip={
            'html': '<b>Towers:</b> {COUNT}',
             'style': {
                 'color': 'white'
                 }
            },
    layers=[layer_3]))

#------Visualisation using Polygons -----------


def get_quantiles(df_column: pd.Series, quantiles: List) -> pd.Series:
    return df_column.quantile(quantiles)


def get_color(df_column: pd.Series, colors: List, vmin: int, vmax: int, index: pd.Series) -> pd.Series:
    color_map = cm.LinearColormap(colors, vmin=vmin, vmax=vmax, index=index)
    return df_column.apply(color_map.rgb_bytes_tuple)
    
st.title("Cell Towers density per zip code")
df_4 = session.sql('''select zip_code, any_value(st_asgeojson(geometry)) as geom, count(*) as count
                        from U_S__ZIP_CODE_METADATA_WITH_GEOMETRY.PUBLIC.ZIP_CODE_GEOMETRY_SHARE t1
                        inner join CARTO_Academy__Data_for_tutorials.CARTO.CELL_TOWERS_NY t2
                        on st_within(t2.geom, to_geography(st_setsrid(t1.geometry, 4326)))
                        group by all;''').to_pandas()

df_4["coordinates"] = df_4["GEOM"].apply(lambda row: json.loads(row)["coordinates"][0])


gc = {
    "type" : "GeometryCollection",
    "geometries" : [json.loads(poly) for poly in df_4.GEOM]
}



quantiles_4 = get_quantiles(df_4["COUNT"], [0, 0.33, 0.66, 1])
colors_4 = ['gray','blue','green','yellow','orange','red']

df_4['COLOR'] = get_color(df_4['COUNT'], colors_4, quantiles_4.min(), quantiles_4.max(), quantiles_4)

layer_4 = pdk.Layer(
            "PolygonLayer",
            df_4,
            id="regions",
            opacity=0.7,
            stroked=True,
            get_polygon="coordinates",
            filled=True,
            extruded=False,
            wireframe=True,
            pickable=True,
            get_fill_color="COLOR", 
            get_line_color="COLOR",
            auto_highlight=True
        )


st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=40.782585,
        longitude=-73.994529, pitch=45, zoom=11),
    tooltip={
            'html': '<b>Zip Code:</b> {ZIP_CODE}<br><b>Cell Towers:</b> {COUNT}',
             'style': {
                 'color': 'white'
                 }
            },
    layers=[layer_4],
))