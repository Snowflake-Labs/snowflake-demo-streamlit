from datetime import timedelta, datetime
from snowflake.snowpark import Session
from utils import (
    get_column_config,
    get_dataframe,
    product_name_query,
)
import altair as alt
import pandas as pd
import sqlparse
import streamlit as st


def data_chart_container(
    dataframe: pd.DataFrame,
    chart_data: alt.Chart,
    sql: str,
    key: str,
) -> None:
    """
    Render a tab control component, that contains a chart, table,
    sql query executed to get the data, brief description and a download button in order to get the data.
    """
    chart_tab, data_tab, sql_tab, download_tab = st.tabs(
        ["Chart", "Data Preview", "SQL", "Download Data"]
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

    # Download Tab
    download_tab.download_button(
        label="Download data as .csv",
        data=dataframe.to_csv(),
        file_name="data.csv",
        mime="text/csv",
        key=str(key),
    )


def get_anomalies_data(
    session: Session, query: str, selected_item: str
) -> pd.DataFrame:
    """
    Retrieves a DataFrame containing anomalous items based on the selected item.
    """
    anomalies_dataframe = get_dataframe(session, query)
    anomalies_dataframe["SERIES"] = anomalies_dataframe["SERIES"].str.replace('"', "")
    anomalies_dataframe = anomalies_dataframe[
        anomalies_dataframe["SERIES"].str.contains(selected_item)
        & anomalies_dataframe["IS_ANOMALY"]
    ]

    return anomalies_dataframe[["SERIES", "TS", "FORECAST", "IS_ANOMALY"]]


def get_anomalies_chart(anomalies_data: pd.DataFrame) -> alt.Chart:
    """
    Generate a chart showing the amount sold over time, with anomalies highlighted.
    """
    # Base line chart for amount sold
    line = (
        alt.Chart(anomalies_data)
        .mark_line()
        .encode(
            x=alt.X("TIMESTAMP:T", title="Date"),
            y=alt.Y("AMOUNT SOLD:Q", title="Amount Sold"),
            tooltip=[
                alt.Tooltip("TIMESTAMP:T", title="Date:"),
                alt.Tooltip("AMOUNT SOLD:Q", title="Amount Sold:", format=".2f"),
            ],
        )
        .properties(title="Amount Sold Over Time")
    )

    # Points for anomalies
    points = (
        alt.Chart(anomalies_data[anomalies_data["IS_ANOMALY"]])
        .mark_point(color="red", size=100)
        .encode(
            x=alt.X("TIMESTAMP:T", title="Date"),
            y=alt.Y("AMOUNT SOLD:Q", title="Amount Sold"),
            tooltip=[
                alt.Tooltip("TIMESTAMP:T", title="Date:"),
                alt.Tooltip("AMOUNT SOLD:Q", title="Amount Sold:", format=".2f"),
                alt.Tooltip("FORECAST:Q", title="Forecast:", format=".2f"),
            ],
        )
    )

    # Combine the charts
    chart = line + points

    return chart


def get_product_names_select(session: Session) -> str:
    """
    Retrieves a list of product names from the session's dataframe and allows the user to select a product.
    """
    product_dataframe = get_dataframe(session, product_name_query())
    product_names = product_dataframe["MENU_ITEM_NAME"].tolist()
    selected_product = st.selectbox(
        "Select product",
        product_names,
        help="Select the product to forecast.",
        key="selected_product",
    )
    return selected_product


def get_products_forecast_chart(
    forecast_data: pd.DataFrame,
) -> alt.Chart:
    """
    Generates a line chart showing the forecasted amount sold for a selected item.
    """
    return (
        alt.Chart(forecast_data)
        .mark_line()
        .encode(
            x=alt.X("TIMESTAMP:T", title="Date"),
            y=alt.Y("AMOUNT SOLD:Q", title="Amount Sold"),
            color=alt.Color("TYPE", title="Type"),
            tooltip=[
                alt.Tooltip("TIMESTAMP:T", title="Date:"),
                alt.Tooltip("AMOUNT SOLD:Q", title="Amount Sold:", format=".2f"),
                alt.Tooltip("ITEM", title="Item:"),
                alt.Tooltip("TYPE", title="Type:"),
            ],
        )
        .properties(
            height=500,
        )
    )


def get_products_forecast_data(
    session: Session,
    query: str,
    selected_item: str,
) -> pd.DataFrame:
    """
    Retrieves forecast data for selected products.
    """
    forecast_dataframe = get_dataframe(session, query, display_loading=True)

    forecast_dataframe = forecast_dataframe[
        forecast_dataframe["ITEM"].str.contains(selected_item)
    ]
    forecast_dataframe = pd.melt(
        forecast_dataframe,
        id_vars=["TIMESTAMP", "ITEM"],
        value_vars=["TOTAL_SOLD", "FORECAST"],
    )
    forecast_dataframe = forecast_dataframe.replace({"TOTAL_SOLD": "ACTUAL"})
    forecast_dataframe.columns = ["TIMESTAMP", "ITEM", "TYPE", "AMOUNT SOLD"]

    return forecast_dataframe


def get_timeframe_selector() -> str:
    """
    Returns the start date based on the selected timeframe.
    """
    DEFAULT_DATE = datetime.strptime("2023-05-28", "%Y-%m-%d")
    timeframe = st.selectbox(
        "Select timeframe",
        ["One month", "Two months", "Three months"],
        help="Select the timeframe to display in the chart.",
        key="timeframe_prediction",
    )

    if timeframe == "One month":
        start_date = DEFAULT_DATE - timedelta(days=30)
    elif timeframe == "Two months":
        start_date = DEFAULT_DATE - timedelta(days=60)
    else:
        start_date = DEFAULT_DATE - timedelta(days=90)

    return start_date.strftime("%Y-%m-%d")
