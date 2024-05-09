from altair.utils.schemapi import Undefined
from snowflake.snowpark import Session
from typing import Tuple
from utils import get_column_config
from utils import gradient_color_array, select_country_data
import altair as alt
import json
import pandas as pd
import pydeck as pdk
import sqlparse
import streamlit as st


def data_chart_container(
    dataframe: pd.DataFrame,
    key: str,
    description: str,
    sql: str,
    chart_data: alt.Chart,
) -> None:
    """
    Render a tab control component, that contains a chart, table, sql query executed to get the data, brief description and a download button in order to get the data.
    """
    chart_tab, data_tab, sql_tab, description_tab, download_tab = st.tabs(
        ["Chart", "Data Preview", "SQL", "Description", "Download Data"]
    )

    # Chart Tab
    if dataframe.empty:
        chart_tab.warning("No data")
        data_tab.warning("No data")
    else:
        chart_tab.altair_chart(chart_data, use_container_width=True)

    # Data Preview Tab
    data_tab.dataframe(
        dataframe,
        use_container_width=True,
        column_config=get_column_config(dataframe),
    )

    # SQL Tab
    sql_tab.code(sqlparse.format(sql, reindent=True), language="sql")

    # Description Tab
    description_tab.markdown(description)

    # Download Tab
    download_tab.download_button(
        label="Download data as .csv",
        data=dataframe.to_csv(),
        file_name="data.csv",
        mime="text/csv",
        key=str(key),
    )


def group_and_agreaggate_data(
    session: Session, data: pd.DataFrame, normalize: bool, rolling: int
) -> pd.DataFrame:
    """
    Group data by locale, to get the mean in a given period of time, this is based on the rolling parameter. Could be 1 (Daily), 7 (Weekly), 28 (Monthly).
    If normalize is enable, the original data is joined with other query that get absolute values, in order to get percentages values.
    """
    if normalize:
        totals = session.sql(
            "SELECT DATE, SUM(NUM_DEVELOPERS) AS NUM_DEVELOPERS_TOTAL FROM LOCALE_USAGE GROUP BY DATE ORDER BY DATE;"
        ).to_pandas()

        data = data.merge(totals, on="DATE", suffixes=(None, "_TOTAL"))
        data["NUM_DEVELOPERS"] = data["NUM_DEVELOPERS"].astype(float) / data[
            "NUM_DEVELOPERS_TOTAL"
        ].astype(float)

    data = data.sort_values(["LOCALE", "DATE"])
    data["NUM_DEVELOPERS"] = (
        data.groupby("LOCALE")["NUM_DEVELOPERS"]
        .rolling(window=rolling)
        .mean()
        .reset_index(level=0, drop=True)
    )

    data = data.dropna(subset=["NUM_DEVELOPERS"])

    return data


def locale_line_chart(
    data: pd.DataFrame, normalize: bool, union: bool
) -> Tuple[alt.Chart, pd.DataFrame]:
    """
    Renders an altair bar chart.
    """
    return (
        alt.Chart(data)
        .mark_line()
        .encode(
            x=alt.X("yearmonthdate(DATE):T", title="Date"),
            y=alt.Y(
                "NUM_DEVELOPERS:Q",
                title="Number of Developers",
                axis=alt.Axis(format="%") if normalize else Undefined,
            ),
            color=(
                alt.Color(
                    "LOCALE:N",
                    legend=alt.Legend(
                        orient="bottom", columns=5, title="Number of Developers"
                    ),
                )
                if not union
                else alt.Color()
            ),
        )
        .properties(height=600)
    )


def polygon_heatmap_chart(
    session: Session, data: pd.DataFrame, normalize: bool
) -> None:
    """
    Arranged language data in order to create pydeck GeoJson layers, that are rendered in a pydeck heatmap chart.
    """
    country_data = session.sql(select_country_data()).to_pandas()

    data = (
        data.sort_values(by=["NUM_DEVELOPERS"], ascending=[False])
        .drop_duplicates(subset=["COUNTRY"])
        .sort_values(by=["NUM_DEVELOPERS"], ascending=[True])
    )

    data.reset_index(drop=True, inplace=True)

    color_array = gradient_color_array(len(data))

    layer_arr = []
    for index, row in data.iterrows():
        found_country = country_data[
            country_data["COUNTRY"].str.lower() == row["COUNTRY"].lower()
        ]

        if len(found_country) != 0:
            polygon_layer = pdk.Layer(
                "GeoJsonLayer",
                data={
                    "type": "Feature",
                    "name": found_country.iloc[0, 0],
                    "geometry": json.loads(found_country.iloc[0, 1].replace("'", '"')),
                    "num_dev": int(row.iloc[2]),
                },
                filled=True,
                get_fill_color=color_array[index],
                stroked=True,
                pickable=True,
                opacity=0.5,
            )
            layer_arr.append(polygon_layer)

    tooltip = {
        "html": "<b>Name:</b> {name}"
        + ("" if normalize else "<br/><b>Number of Developers</b>: {num_dev}")
    }

    # Create a Pydeck Deck with the polygon layer
    deck = pdk.Deck(map_style=None, layers=layer_arr, tooltip=tooltip)

    # Render the Pydeck chart using Streamlit
    st.pydeck_chart(deck)
