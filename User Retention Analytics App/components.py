from datetime import date
from matplotlib.colors import LinearSegmentedColormap
from snowflake.snowpark import Session
from typing import Tuple, cast, Union, Dict
from utils import select_cohort_data, process_cohort_data, get_column_config
import altair as alt
import pandas as pd
import sqlparse
import streamlit as st


# Components
def date_range_picker(
    title: str,
    default_start: date = None,
    default_end: date = None,
    min_date: date = None,
    max_date: date = None,
    key: str = "",
) -> Tuple[date, date]:
    """
    Render a range picker component, it returns the selected dates.
    """
    val = st.date_input(
        title,
        value=[default_start, default_end],
        min_value=min_date,
        max_value=max_date,
        key=str(key),
    )
    try:
        start_date, end_date = cast(Tuple[date, date], val)
    except ValueError:
        st.error("Please select start and end date")
        st.stop()

    return start_date, end_date


def data_chart_container(
    dataframe: pd.DataFrame,
    key: str,
    description: str = None,
    sql: str = None,
    is_chart: bool = True,
    chart_data: Union[alt.Chart, pd.DataFrame] = None,
    chart_settings: Dict = None
) -> None:
    """
    Render a tab control component.
    """
    chart_tab, data_tab, sql_tab, description_tab, download_tab = st.tabs(
        ["Chart", "Data Preview", "SQL", "Description", "Download Data"]
    )

    # Chart Tab
    if dataframe.empty:
        chart_tab.warning("No data")
        data_tab.warning("No data")
    elif type(chart_data) is alt.Chart:
        chart_tab.altair_chart(chart_data, use_container_width=True)
    elif is_chart:
        chart_tab.bar_chart(chart_data, x=chart_settings['x'], y=chart_settings['y'], color=chart_settings['color'])
    else:
        chart_tab.dataframe(chart_data)

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


def cohort_chart(
    table_name: str,
    description: str,
    start_date: date,
    end_date: date,
    key: str,
    timeframe: str,
    percentages: str,
    session: Session,
    color: LinearSegmentedColormap,
) -> None:
    """
    Get data from Snowflake, in order to render the cohort chart.
    """
    query = select_cohort_data(table_name, start_date, end_date, timeframe)
    df = session.sql(query).toPandas()
    unprocessedData, processedData = process_cohort_data(
        df, color, timeframe, percentages=percentages == "Percentages"
    )
    data_chart_container(
        unprocessedData,
        description=description,
        sql=query,
        chart_data=processedData,
        key=key,
        is_chart=False
    )


def power_curve_chart(
    query: str, description: str, id: str, session: Session, color: str
) -> None:
    """
    Get data from Snowflake, in order to render the power user curve chart.
    """
    df = session.sql(query).toPandas()

    df.rename(
        columns={
            "NUM_DAYS_ACTIVE": "Number of days active",
            "NUM_USERS": "Number of users",
        },
        inplace=True,
    )

    chart_settings = {
        "color": color,
        "x": "Number of days active",
        "y": "Number of users"
    }

    data_chart_container(df, description=description, sql=query, chart_data=df, key=id, is_chart=True, chart_settings=chart_settings)
