import pydeck as pdk
import streamlit as st
import sys
import utils.data_access as da
import utils.helpers as hp
import utils.widgets as wdg

st.set_page_config(layout="wide")


POINT_OF_INTEREST_COLOR = "255, 31, 0"
H3_LINE_COLOR = [255, 255, 255]


if "first_run" not in st.session_state:
    st.session_state.first_run = True
else:
    st.session_state.first_run = False

st.title("SmartGeoPOI :satellite_antenna:")
st.write(
    """
    SmartGeoPOI uses advanced H3 geospatial indexing, to bring a seamless 
    exploration experience enriched with detailed information about establishments, 
   and points of interest (POIs).
    """
)

with st.sidebar:
    st.info(
        """
        By selecting a country, city, and category, you can visualize various map 
        layers (H3, POI).

        To view the locations represented on the map, select the POI layer to display 
        a list of points of interest.
        """,
        icon="ℹ️",
    )

    chck_city_filter_active = st.checkbox("Country Filter")

    if chck_city_filter_active:
        with st.spinner("Loading Countries!"):
            wdg.create_countries_widget()
    else:
        st.session_state.s_countries = wdg.CITY_GB_KEY

    with st.spinner("Loading Cities!"):
        wdg.create_cities_widget()

    with st.spinner("Loading Categories!"):
        wdg.create_categories_widget()

    wdg.create_h3_resolution_slider()
    wdg.create_layer_widget()


with st.spinner("Loading Chart!"):
    centrepd = da.get_centered_coordinate()

    layers = []
    total_memory_size_mb_dfs = 0
    if "H3" in st.session_state[wdg.LAYER_KEY]:
        h3_df = da.get_count_h3_df()
        if len(h3_df) > 0:
            h3_df = da.add_h3_color_columns(h3_df)
            total_memory_size_mb_dfs += sys.getsizeof(h3_df) / (1024 * 1024)
            h3_l = pdk.Layer(
                "H3HexagonLayer",
                h3_df,
                pickable=False,
                stroked=False,
                filled=True,
                extruded=False,
                get_hexagon="H3",
                get_fill_color="COLOR",
                get_line_color=H3_LINE_COLOR,
                line_width_min_pixels=2,
                opacity=0.4,
            )
            layers.append(h3_l)
    if "POI" in st.session_state[wdg.LAYER_KEY]:
        poi_df = da.get_poi_df()
        if len(poi_df) > 0:
            total_memory_size_mb_dfs += sys.getsizeof(poi_df) / (1024 * 1024)
            poi_l = pdk.Layer(
                "ScatterplotLayer",
                data=poi_df,
                get_position="[LON, LAT]",
                get_color=f"[{POINT_OF_INTEREST_COLOR}]",
                get_radius="10",
                pickable=False,
            )
            layers.append(poi_l)

    if centrepd.size == 0:
        st.error("No data to render!")
    else:
        centered_lat = 0 if len(layers) == 0 else centrepd.LAT.iloc[0]
        centered_lon = 0 if len(layers) == 0 else centrepd.LON.iloc[0]
        st.image("./assets/gradient.png")
        if len(layers) == 0:
            zoom = 1
        else:
            if st.session_state[wdg.CITY_KEY] == "Not Selected":
                zoom = da.calculate_zoom_for_country()
            else:
                zoom = hp.calculate_zoom_for_h3(
                    centered_lat,
                    centered_lon,
                    8,
                )

        if total_memory_size_mb_dfs > 25:
            st.error(
                "Data is too large. Please be more specific when selecting the filters!"
            )
        else:
            deck = pdk.Deck(
                map_style=None,
                initial_view_state=pdk.ViewState(
                    latitude=centered_lat,
                    longitude=centered_lon,
                    zoom=zoom,
                    height=800,
                    pitch=0,
                ),
                layers=layers,
                tooltip={"text": "Station Name: {NAME} Footfall: {FOOTFALL},MP: {MP}"},
            )
            final_chart = st.pydeck_chart(deck)
            st.write(
                """
                [CARTO](https://app.snowflake.com/marketplace/providers/GZT0ZKUCHE3/CARTO?originTab=providers)
                is a free location platform that served as the data source for this project.
                """
            )
            if "POI" in st.session_state[wdg.LAYER_KEY]:
                st.markdown("##### POI DATA")
                st.dataframe(poi_df, use_container_width=True, hide_index=True)
