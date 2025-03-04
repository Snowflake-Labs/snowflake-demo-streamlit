import branca.colormap as cm
import datetime
import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st


@st.cache_data
def get_dataframe_from_raw_sql(query: str) -> pd.DataFrame:
    """Executes the given query in the Snowflake database
    and converts the result to a pandas dataframe and changes
    the column names to be capitalized.

    Args:
        query (str): The query to be run against the database.

    Returns:
        pd.DataFrame: The query result as a pandas dataframe.
    """
    # Get active session to query the Snowflake database
    session = st.connection("snowflake").session()
    pandas_df = session.sql(query).to_pandas()
    return pandas_df


def pydeck_chart_creation(
    chart_df: pd.DataFrame,
    coordinates: tuple = (40.74258515841464, -73.98452997207642),
    elevation_3d: bool = False,
):
    """Renders pydeck chart for the given dataframe.

    Args:
        chart_df (pd.Dataframe): The dataframe use to render the chart.
        coordinates (tuple, optional): Initial coordinates for pydeck chart.
            Defaults to NY City coordinates (40.74258515841464, -73.98452997207642).
    """
    highest_count_df = 0 if chart_df is None else chart_df["COUNT"].max()
    st.pydeck_chart(
        pdk.Deck(
            map_style=None,
            initial_view_state=pdk.ViewState(
                latitude=coordinates[0],
                longitude=coordinates[1],
                pitch=45,
                zoom=10,
            ),
            tooltip={"html": "<b>{H3}:</b> {COUNT}", "style": {"color": "white"}},
            layers=[
                pdk.Layer(
                    "H3HexagonLayer",
                    chart_df,
                    get_hexagon="H3",
                    get_fill_color="COLOR",
                    get_line_color="COLOR",
                    get_elevation=f"COUNT/{highest_count_df}",
                    auto_highlight=True,
                    elevation_scale=10000 if elevation_3d else 0,
                    pickable=True,
                    elevation_range=[0, 300],
                    extruded=True,
                    coverage=1,
                    opacity=0.3,
                )
            ],
        )
    )


def generate_linear_color_map(colors: list, quantiles):
    """Creates a linear color map.

    Args:
        colors (list): The color list for the linear color map.
        quantiles: The quantiles to be used in the linear color map.
    """
    return cm.LinearColormap(
        colors,
        vmin=quantiles.min(),
        vmax=quantiles.max(),
        index=quantiles,
    )


def render_plotly_line_chart(chart_df: pd.DataFrame):
    """Renders plotly chart.

    Args:
        chart_df (pd.DataFrame): The dataframe use to render the chart.
    """
    fig = px.line(
        chart_df,
        x="PICKUP_TIME",
        y=["PICKUPS", "FORECAST"],
        color_discrete_sequence=["#D966FF", "#126481"],
        markers=True,
    )

    fig.update_layout(yaxis_title="Pickups", xaxis_title="")
    st.plotly_chart(
        fig,
        theme="streamlit",
        use_container_width=True,
        config={"displayModeBar": False},
    )


st.set_page_config(
    page_title="NY Pickup Location App", layout="wide", initial_sidebar_state="expanded"
)
st.title("NY Pickup Location App :taxi:")
st.write(
    """An app that visualizes geo-temporal data from NY taxi pickups using H3 and time series. 
It can be useful to visualize marketplace signals that are distributed spatially and temporally.

By leveraging intuitive filters in the sidebar, users can refine their analysis based on date,
time, or specific H3 cell, allowing for a granular exploration of demand patterns. Whether
seeking real-time or forecasted demand, the application generates dynamic charts that precisely
reflect the selected parameters across all H3 hexagons or a singular focus.

Additionally, the sidebar features a SMAPE metric table, providing an insightful comparison of
prediction accuracy across H3 cells. A lower SMAPE score indicates a more accurate prediction,
empowering users to identify the most reliable forecasts effortlessly.

Check "Getting started with Geospatial AI and ML using Snowflake Cortex" 
[quickstart](https://quickstarts.snowflake.com/guide/geo-for-machine-learning/index.html?index=..%2F..index#2) 
for more details about the demand prediciton use case.

"""
)

AVGLATITUDELONGITUDE = """
SELECT
    AVG(ST_Y(H3_CELL_TO_POINT(h3))) AS lat,
    AVG(ST_X(h3_cell_to_point(h3))) AS lon,
FROM
    h3_timeseries_visualization_db.h3_timeseries_visualization_s.ny_taxi_rides_compare
"""

SQLQUERYTIMESERIES = """
SELECT
    pickup_time,
    h3,
    forecast,
    pickups
FROM
    h3_timeseries_visualization_db.h3_timeseries_visualization_s.ny_taxi_rides_compare
"""
SQLQUERYMETRICS = """
SELECT
    *
FROM
    h3_timeseries_visualization_db.h3_timeseries_visualization_s.ny_taxi_rides_metrics
"""

df_avg_lat_long = get_dataframe_from_raw_sql(AVGLATITUDELONGITUDE)
avg_coordinate = (df_avg_lat_long.iloc[0, 0], df_avg_lat_long.iloc[0, 1])
df_metrics = get_dataframe_from_raw_sql(SQLQUERYMETRICS)

with st.sidebar:
    initial_start_date = datetime.date(2015, 6, 6)
    selected_date_range = st.date_input(
        "Date Range:",
        (initial_start_date, initial_start_date + datetime.timedelta(days=7)),
        format="MM.DD.YYYY",
    )

    tr_col_l, tr_col_r = st.columns(2)
    with tr_col_l:
        selected_start_time_range = st.time_input(
            "Start Time Range",
            datetime.time(0, 0),
            key="selected_start_time_range",
            step=3600,
        )
    with tr_col_r:
        selected_end_time_range = st.time_input(
            "End Time Range:",
            datetime.time(23, 00),
            key="selected_end_time_range",
            step=3600,
        )
    h3_options = st.selectbox(
        "H3 cells to display", (["All"] + df_metrics["H3"].to_list())
    )

    with st.expander(":orange[Expand to see SMAPE metric]"):
        df_metrics_filtered = df_metrics
        if h3_options != "All":
            df_metrics_filtered = df_metrics[df_metrics["H3"] == h3_options]

        st.dataframe(df_metrics_filtered, hide_index=True, width=300)
    chckbox_3d_value = st.checkbox(
        "3D", key="chkbx_forecast", help="Renders H3 Hexagons in 3D"
    )

DF_PICKUPS = None
DF_FORECAST = None

start_end_date_selected = len(selected_date_range) == 2

if start_end_date_selected:
    sql_query_pickups = f"""
SELECT
    h3,
    SUM(pickups) AS count
FROM
    h3_timeseries_visualization_db.h3_timeseries_visualization_s.ny_taxi_rides_compare
WHERE
    pickup_time BETWEEN DATE('{selected_date_range[0]}')
    AND DATE('{selected_date_range[1]}')
    AND TIME(pickup_time) BETWEEN '{selected_start_time_range}'
    AND '{selected_end_time_range}'
GROUP BY
    1
    """
    sql_query_forecast = f"""
SELECT
    h3,
    sum(forecast) AS count
FROM
    h3_timeseries_visualization_db.h3_timeseries_visualization_s.ny_taxi_rides_compare
WHERE
    pickup_time BETWEEN DATE('{selected_date_range[0]}')
    AND DATE('{selected_date_range[1]}')
    AND TIME(pickup_time) BETWEEN '{selected_start_time_range}'
    AND '{selected_end_time_range}'
GROUP BY
    1
    """

    colors_list = ["gray", "blue", "green", "yellow", "orange", "red"]
    DF_PICKUPS = get_dataframe_from_raw_sql(sql_query_pickups)
    quantiles_pickups = DF_PICKUPS["COUNT"].quantile([0, 0.25, 0.5, 0.75, 1])
    color_map_pickups = generate_linear_color_map(colors_list, quantiles_pickups)
    DF_PICKUPS["COLOR"] = DF_PICKUPS["COUNT"].apply(color_map_pickups.rgb_bytes_tuple)

    DF_FORECAST = get_dataframe_from_raw_sql(sql_query_forecast)
    quantiles_forecast = DF_FORECAST["COUNT"].quantile([0, 0.25, 0.5, 0.75, 1])
    color_map_forecast = generate_linear_color_map(colors_list, quantiles_forecast)
    DF_FORECAST["COLOR"] = DF_FORECAST["COUNT"].apply(
        color_map_forecast.rgb_bytes_tuple
    )

    if h3_options != "All":
        DF_PICKUPS = DF_PICKUPS[DF_PICKUPS["H3"] == h3_options]
        DF_FORECAST = DF_FORECAST[DF_FORECAST["H3"] == h3_options]

col1, col2 = st.columns(2)
with col1:
    st.write("**Actual Demand**")
    pydeck_chart_creation(DF_PICKUPS, avg_coordinate, chckbox_3d_value)
with col2:
    st.write("**Forecasted Demand**")
    pydeck_chart_creation(DF_FORECAST, avg_coordinate, chckbox_3d_value)

df_time_series = get_dataframe_from_raw_sql(SQLQUERYTIMESERIES)
if DF_FORECAST is None or len(DF_FORECAST) == 0:
    st.stop()

comparision_df_filter = (
    (pd.to_datetime(df_time_series["PICKUP_TIME"]).dt.date >= selected_date_range[0])
    & (pd.to_datetime(df_time_series["PICKUP_TIME"]).dt.date < selected_date_range[1])
    & (
        pd.to_datetime(df_time_series["PICKUP_TIME"]).dt.time
        >= selected_start_time_range
    )
    & (pd.to_datetime(df_time_series["PICKUP_TIME"]).dt.time < selected_end_time_range)
)

if h3_options == "All":
    st.markdown("### Comparison for All Hexagons")
    df_time_series_filtered = (
        df_time_series[comparision_df_filter]
        .groupby(["PICKUP_TIME"], as_index=False)
        .sum()
    )
    df_time_series_filtered = df_time_series_filtered[
        ["PICKUP_TIME", "FORECAST", "PICKUPS"]
    ]
    with st.expander("Raw Data"):
        st.dataframe(df_time_series_filtered, use_container_width=True)
else:
    st.markdown(f"### Comparison for Hexagon ID {h3_options}")
    df_time_series_filtered = (
        df_time_series[(df_time_series["H3"] == h3_options) & comparision_df_filter]
        .groupby(["PICKUP_TIME"], as_index=False)
        .sum()
    )
    with st.expander("Raw Data"):
        st.dataframe(df_time_series_filtered, use_container_width=True)

render_plotly_line_chart(df_time_series_filtered)
