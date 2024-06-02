from datetime import datetime
from typing import Tuple, cast
from utils import get_column_config, get_simplified_name_dataframe
import altair as alt
import pandas as pd
import sqlparse
import streamlit as st


def data_chart_container(
    dataframe: pd.DataFrame,
    description: str,
    chart_data: alt.Chart,
    sql: str,
    key: str,
) -> None:
    """
    Render a tab control component, that contains a chart, table,
    SQL query executed to get the data, brief description and a download button in order to get the data.
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
    # Add the github part to the repos URLs.
    df = dataframe.copy(deep=True)
    df["NAME"] = "https://github.com/" + df["NAME"]
    data_tab.dataframe(
        df,
        use_container_width=True,
        column_config=get_column_config(dataframe),
        hide_index=True,
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


def top_starred_repositories_chart(dataframe: pd.DataFrame) -> alt.Chart:
    """
    Get chart with the most starred repositories of all time.
    """
    df = get_simplified_name_dataframe(dataframe)
    return (
        alt.Chart(df)
        .mark_bar(
            color="#BA5370",
            opacity=0.8,
            cornerRadiusTopLeft=2,
            cornerRadiusTopRight=2,
        )
        .encode(
            x=alt.X("NAME:N", title="Name", sort="y"),
            y=alt.Y("STARS_COUNT:Q", title="Stars count"),
        )
        .properties(height=600)
    )


def stars_growing_over_time_chart(dataframe: pd.DataFrame) -> alt.Chart:
    """
    Display how repositories stars have increased over a period of time.
    """
    df = get_simplified_name_dataframe(dataframe)
    return (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("STARS_DATE", title="Date"),
            y=alt.Y(
                "STARS_COUNT:Q",
                title="Stars Count",
            ),
            tooltip=[
                alt.Tooltip("STARS_DATE", format="%Y-%m-%d", title="Date:"),
                alt.Tooltip("NAME:N", title="Name:"),
                alt.Tooltip("STARS_COUNT:Q", title="Stars Count:"),
            ],
            color=alt.Color("NAME", title="Name"),
        )
        .properties(height=400)
    )


def date_picker() -> Tuple[str, str]:
    """
    Render a date picker component, it returns the selected dates.
    """
    time_range = st.date_input(
        "Select time range",
        value=[datetime.strptime("2024-01-01", "%Y-%m-%d"), datetime.now()],
        min_value=datetime.strptime("2011-02-12", "%Y-%m-%d"),
        max_value=datetime.now(),
    )

    try:
        start_date, end_date = cast(Tuple[str, str], time_range)
    except:
        st.error("Please select start and end date")
        st.stop()

    return start_date, end_date
