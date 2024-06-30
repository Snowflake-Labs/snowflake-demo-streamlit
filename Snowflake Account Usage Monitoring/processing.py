from snowflake.snowpark import Session
import numpy as np
import pandas as pd
import sqlparse
import streamlit as st


@st.cache_data
def aggregate_data(
    dataframe: pd.DataFrame, date_column: str, aggregate_by: str
) -> pd.DataFrame:
    """
    Resample a dataframe's date_column by day, week or month based on aggregate_by, summing values.
    """
    if aggregate_by == "Daily":
        aggregate_by = "1D"
    elif aggregate_by == "Weekly":
        aggregate_by = "1W"
    else:
        aggregate_by = "1M"
    return (
        dataframe.set_index(date_column)
        .resample(aggregate_by)
        .sum()
        .reset_index(date_column)
    )


@st.cache_data
def apply_log1p(dataframe: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Apply log1p on input columns and store into new columns in input df
    with suffix _LOG.
    """
    log_columns = [f"{column}_LOG" for column in columns]
    dataframe[log_columns] = dataframe[columns].apply(np.log1p)
    return dataframe


def format_credits(value: int) -> str:
    """
    Format credits text.
    """
    if value < 1000:
        return f"{value:.2f}"
    elif value < 10000:
        return f"{value / 1000:.2f}K"
    else:
        return f"{value // 1000}K"


def format_bytes(value: int) -> str:
    """
    Format bytes text.
    """
    # Define the size units
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]

    # Loop to determine the appropriate unit
    unit_index = 0
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024.0
        unit_index += 1

    # Format the bytes with one decimal place
    return f"{value:.2f} {units[unit_index]}"


def format_time(seconds: int) -> str:
    """
    Format time text.
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    formated_date = ""
    if hours:
        formated_date += f"{hours} hr{'s' if hours > 1 else ''} "
    if minutes:
        formated_date += f"{minutes} min{'s' if minutes > 1 else ''} "
    if seconds:
        formated_date += f"{seconds} sec{'s' if seconds > 1 else ''}"
    return formated_date


def format_sql_query(query: str) -> str:
    """
    Format SQL query text.
    """
    return sqlparse.format(
        query,
        reindent=True,
        keyword_case="upper",
    )


def get_column_config(dataframe: pd.DataFrame) -> dict:
    """
    Format dataframe columns text in PascalCase style.
    """
    return {
        col: st.column_config.Column(col.replace("_", " ").title())
        for col in dataframe.columns
    }


@st.cache_data(show_spinner=True)
def get_dataframe(_session: Session, query: str) -> pd.DataFrame:
    """
    Executes a SQL query on the given session and returns the result as a pandas DataFrame.
    """
    return _session.sql(query).to_pandas()
