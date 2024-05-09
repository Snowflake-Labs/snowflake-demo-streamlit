import pandas as pd
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import DataFrame
import sqlparse
import streamlit as st


def get_data_frame_from_raw_sql(query: str) -> pd.DataFrame:
    """
    Gets data frame from a given sql string.
    ---------
    query: str
        The given sql query as a string.
    """
    session = get_active_session()
    dataframe = session.sql(query).to_pandas()
    dataframe.columns = [column.lower() for column in dataframe.columns]
    return dataframe
