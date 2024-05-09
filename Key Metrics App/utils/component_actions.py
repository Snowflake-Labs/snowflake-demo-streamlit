from typing import Any
import streamlit as st
import altair as alt
import snowflake.snowpark as spark
import sqlparse
import pandas as pd
from snowflake.snowpark.context import get_active_session
from utils.components import date_range_picker, selectbox_filter


def render_tile(
    df,
    description: str,
    sql: str = None,
    chart=None,
):
    """Create a tile with a chart, a dataframe preview, the SQL query and a description.

    Args:
        df (spark.DataFrame | pd.DataFrame): Data.
        description (str): Description of the what the tile is about.
        sql (str | None, optional): Underlying SQL query. Defaults to None.
        chart (alt.Chart): Chart. Defaults to None.
    """
    data = df
    t1, t2, t3, t4, t5 = st.tabs(
        ["Chart", "Data Preview", "SQL", "Description", "Download Data"]
    )

    t4.markdown(description)

    if chart is not None:
        t1.altair_chart(chart, use_container_width=True)

    if data.empty:
        t2.error("No data")
    else:
        with t2:
            st.dataframe(data, use_container_width=True)

        with t5:
            import random

            key = f"{random.random()}"

            st.download_button(
                label="Download data as .csv",
                data=data.to_csv(),
                file_name="data.csv",  # SiS doesn't currently respect the passed filename STREAMLIT-5264
                key=key,
                mime="text/csv",
            )

    if sql is None:
        t3.caption("No SQL query was provided.")
    else:
        t3.code(
            sqlparse.format(sql, reindent=True, keyword_case="lower"), language="sql"
        )

    with t1:
        if data.empty:
            st.error("No data")


def get_dataframe_from_query_with_lowercase_columns(query):
    """
    Executes given query. Converts dataframe to a pandas dataframe and changes columns names to lowercase.
    """

    session = get_active_session()
    data_snowpark = session.sql(query)

    data = data_snowpark.to_pandas()
    data.columns = [column.lower() for column in data.columns]
    return data
