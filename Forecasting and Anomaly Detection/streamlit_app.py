from components import (
    data_chart_container,
    get_anomalies_chart,
    get_anomalies_data,
    get_product_names_select,
    get_products_forecast_chart,
    get_products_forecast_data,
    get_timeframe_selector,
)
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
from utils import anomalies_query, join_dataframes, products_forecast_query
import streamlit as st


session: Session = get_active_session()

# ------------------------------------------------
# -- Forecast
# ------------------------------------------------

st.header("Products Sales Forecast")

st.write(
    """
    This chart allows you to visualize and forecast the units sold for a selected product.
    You can customize the displayed data by choosing a timeframe. The data currently extends up to May 28, 2023.
    """
)

date_col, items_col = st.columns(2)

with date_col:
    start_date = get_timeframe_selector()
with items_col:
    selected_item = get_product_names_select(session)


products_query = products_forecast_query(start_date)
with st.spinner("Loading products data..."):
    forecast_data = get_products_forecast_data(session, products_query, selected_item)
    products_chart = get_products_forecast_chart(forecast_data)
    data_chart_container(
        dataframe=forecast_data,
        chart_data=products_chart,
        sql=products_query,
        key="products_forecast",
    )

# ------------------------------------------------
# -- Anomalies
# ------------------------------------------------

st.subheader("Products Sells Anomalies")

st.write(
    """
    This chart shows the units sold for a selected product over a specified period.
    Red points highlight anomalies in the sales data detected by our machine learning model.
    These anomalies indicate sales figures that significantly deviate from the expected patterns,
    helping to identify unusual spikes or drops in product demand.
    """
)
anomalies_query = anomalies_query()
with st.spinner("Loading anomalous records..."):
    anomalous_data = get_anomalies_data(session, anomalies_query, selected_item)

    if anomalous_data.empty:
        st.warning("No anomalous records found for the selected product.")
    else:
        joined_data = join_dataframes(forecast_data, anomalous_data)
        anomalous_chart = get_anomalies_chart(joined_data)
        data_chart_container(
            dataframe=joined_data,
            chart_data=anomalous_chart,
            sql=anomalies_query,
            key="anomalous_items",
        )
