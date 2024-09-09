from snowflake.snowpark import Session
from snowflake.snowpark.exceptions import SnowparkFetchDataException
import pandas as pd
import streamlit as st
import time


def anomalies_query() -> str:
    """
    Executes a query to detect anomalies in the PRODUCTS_ANOMALY_ANALYSIS_SET table.
    """
    return """
        CALL PRODUCTS_ANOMALY_MODEL!DETECT_ANOMALIES(
            INPUT_DATA => TABLE(PRODUCTS_ANOMALY_ANALYSIS_SET),
            SERIES_COLNAME => 'MENU_ITEM_NAME',
            TIMESTAMP_COLNAME => 'TIMESTAMP',
            TARGET_COLNAME => 'TOTAL_SOLD',
            CONFIG_OBJECT => {'prediction_interval': 0.95}
        )
        """


def product_name_query() -> str:
    """
    Returns a SQL query to retrieve distinct menu item names from the PRODUCTS_FORECAST_DATA table.
    """
    return """
        SELECT
            DISTINCT MENU_ITEM_NAME
        FROM
            PRODUCTS_FORECAST_DATA
        ORDER BY
            MENU_ITEM_NAME;
        """


def products_forecast_query(start_date: str) -> str:
    """
    Generates a SQL query to retrieve product sales data and forecasted values.
    """
    return f"""
        WITH ITEMS_PREDICTIONS AS (
            SELECT
                SERIES :: VARCHAR AS SERIES,
                TS,
                FORECAST
            FROM
                TABLE(
                    PRODUCTS_FORECAST!FORECAST(
                        SERIES_COLNAME => 'MENU_ITEM_NAME',
                        INPUT_DATA => TABLE(PRODUCTS_FORECAST_DATA),
                        TIMESTAMP_COLNAME => 'TIMESTAMP'
                    )
                )
        )
        SELECT
            TIMESTAMP,
            TOTAL_SOLD,
            MENU_ITEM_NAME AS ITEM,
            NULL AS FORECAST
        FROM
            PRODUCTS_SALES
        WHERE
            TIMESTAMP >= '{start_date}'
        UNION
        SELECT
            TS AS TIMESTAMP,
            NULL AS TOTAL_SOLD,
            SERIES AS ITEM,
            FORECAST
        FROM
            ITEMS_PREDICTIONS
        ORDER BY
            TIMESTAMP;
        """


def join_dataframes(dataframe1: pd.DataFrame, dataframe2: pd.DataFrame) -> pd.DataFrame:
    """
    Joins two dataframes based on the 'TIMESTAMP' and 'ITEM' columns and performs some data cleaning.
    """
    dataframe1 = dataframe1.dropna()
    dataframe1 = dataframe1.reset_index(drop=True)
    dataframe2 = dataframe2.rename(columns={"TS": "TIMESTAMP", "SERIES": "ITEM"})
    merged_dataframe = pd.merge(
        dataframe1, dataframe2, on=["TIMESTAMP", "ITEM"], how="left"
    )
    merged_dataframe["IS_ANOMALY"] = merged_dataframe["IS_ANOMALY"].fillna(False)
    merged_dataframe["FORECAST"] = merged_dataframe["FORECAST"].where(
        pd.notnull(merged_dataframe["FORECAST"]), None
    )
    result = merged_dataframe[
        ["TIMESTAMP", "ITEM", "TYPE", "AMOUNT SOLD", "IS_ANOMALY", "FORECAST"]
    ]

    return result


def get_column_config(df: pd.DataFrame) -> dict:
    """
    Format dataframe columns text in PascalCase style.
    """
    return {
        col: st.column_config.Column(col.replace("_", " ").title())
        for col in df.columns
    }


@st.cache_data(show_spinner=False)
def get_dataframe(
    _session: Session, query: str, display_loading: bool = False
) -> pd.DataFrame:
    """
    Retrieves a pandas DataFrame from a Snowpark session using the provided query.
    """
    if display_loading:
        time.sleep(1)

    try:
        dataframe = _session.sql(query).to_pandas()
    except SnowparkFetchDataException:
        rows_array = _session.sql(query).collect()
        dataframe = pd.DataFrame(rows_array)
    return dataframe
