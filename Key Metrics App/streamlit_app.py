import streamlit as st
import pandas as pd
from datetime import timedelta
from utils.data_retrieval import (
    get_data_frame_from_raw_sql,
)
from utils.query_texts import (
    query_weekly_percentage_signature_customers_using_wifi_controller,
    query_total_sales,
    query_number_of_views_of_wifi_controller,
    query_active_customer_accounts,
)
from utils.component_actions import (
    get_dataframe_from_query_with_lowercase_columns,
    render_tile,
)
from utils.chart import altair_line_chart
from utils.components import date_range_picker, selectbox_filter

st.set_page_config(layout="wide")
st.title("Key Metrics: CloudWiFiControllers :balloon:")
st.markdown(
    "This app measures metrics related to the customer's cloud "
    "provider, customer's online status and sales statistics. "
    "Use the filters to explore :bar_chart: "
    "and leave feedback in our #CloudWiFiControllers slack channel."
)
max_date_jobs_data = get_data_frame_from_raw_sql(
    """
    select
        max(created_on) as max_date,
        date(max_date) as max_date_day,
        time(max_date) as max_date_time
    from Key_Metrics_New_Product_DB.Key_Metrics_New_Product_S.executes
"""
)
max_day = max_date_jobs_data["max_date_day"][0]
max_time = str(max_date_jobs_data["max_date_time"][0])
st.write(f"Underlying data is up to date as of **{max_day}** at **{max_time}** UTC")
with st.expander("Filters"):
    st.markdown("**Breakdown the graphs using these inputs:**")
    with st.form("key_metrics"):
        col1, col2 = st.columns(2)
        with col1:
            # Dates Filter Component
            if max_day is None:
                selected_dates = date_range_picker("Date Range")
            else:
                seven_days_ago = max_day - timedelta(days=7)
                selected_dates = date_range_picker(
                    "Date Range:", seven_days_ago, max_day
                )
        with col2:
            # Customer Type Component
            customer_type = "customer_account_type"
            selected_customer_type = selectbox_filter(
                get_data_frame_from_raw_sql(
                    "select distinct customer_account_type from Key_Metrics_New_Product_DB.Key_Metrics_New_Product_S.metadata_executes"
                ),
                "Customer Type:",
                key=customer_type,
            )
            # Cloud Type Component
            cloud = "cloud"
            selected_cloud = selectbox_filter(
                get_data_frame_from_raw_sql(
                    "select distinct cloud from Key_Metrics_New_Product_DB.Key_Metrics_New_Product_S.metadata_executes"
                ),
                "Cloud Type:",
                key=cloud,
            )
        st.form_submit_button(label="Submit")
# Sidebar Filter Information
st.sidebar.markdown("**Current filter selections:**")
st.sidebar.write("Dates: {} ➡️ {}".format(selected_dates[0], selected_dates[1]))
st.sidebar.write(
    "Account Type: {}".format(
        selected_customer_type if selected_customer_type is not None else "All"
    )
)
st.sidebar.write("Cloud: {}".format(selected_cloud))
col1, col2 = st.columns(2, gap="large")
col1.subheader("Active Customer Accounts")
col2.subheader("Weekly Use of Signature Customers %")
cola, colb = st.columns(2, gap="large")
with cola:
    description: str = (
        """The total number of customer accounts who have used CloudWiFiControllers in the provided timeframe. **Filtered by Customer Type and Cloud."""
    )
    active_customer_accounts_query = query_active_customer_accounts()
    active_customer_accounts_df = get_dataframe_from_query_with_lowercase_columns(
        active_customer_accounts_query
    )
    # Changes daily, last_7_days, last_28_days columns to row values using date as pivot
    active_customer_accounts_df = active_customer_accounts_df.melt(
        id_vars=["date"], value_vars=["daily", "last_7_days", "last_28_days"]
    )
    # Filter active customer account dataframe by filtered data range
    active_customer_accounts_df = active_customer_accounts_df[
        (active_customer_accounts_df["date"] >= selected_dates[0])
        & (active_customer_accounts_df["date"] <= selected_dates[1])
    ]
    active_customer_accounts_df = active_customer_accounts_df.reset_index(drop=True)
    # Creates chart for active customer accounts
    active_customer_accounts_chart = altair_line_chart(
        active_customer_accounts_df, "Active Accounts", "d"
    )
    render_tile(
        df=active_customer_accounts_df,
        description=description,
        sql=active_customer_accounts_query,
        chart=active_customer_accounts_chart,
    )
with colb:
    description_weekly_penetration: str = (
        """The percentage of our important, signature customers using our wifi controller platform."""
    )
    query_weekly_penetration = (
        query_weekly_percentage_signature_customers_using_wifi_controller()
    )
    data_weekly_penetration = get_dataframe_from_query_with_lowercase_columns(
        query_weekly_penetration
    )
    # Changes penetration_percentage columns to row values using date as pivot
    data_weekly_penetration = data_weekly_penetration.melt(
        id_vars=["date"], value_vars=["penetration_percentage"]
    )
    data_weekly_penetration = data_weekly_penetration.reset_index(drop=True)
    data_weekly_penetration["value"] = data_weekly_penetration["value"].astype("float")
    # Creates chart for weekly penetration percentage
    chart_weekly_penetration = altair_line_chart(
        data_weekly_penetration,
        "Active Signature Customers (%)",
        ".03%",
    )
    render_tile(
        df=data_weekly_penetration,
        description=description_weekly_penetration,
        sql=query_weekly_penetration,
        chart=chart_weekly_penetration,
    )
col1, col2 = st.columns(2, gap="large")
col1.subheader("Total Sales")
col2.subheader("Number of Product Views")
colc, cold = st.columns(2, gap="large")
with colc:
    description_dollars_consumed: str = (
        """Total sales over the past 7 days attributed to CloudWiFiControllers."""
    )
    query_dollars_consumed = query_total_sales()
    data_dollars_consumed = get_dataframe_from_query_with_lowercase_columns(
        query_dollars_consumed
    )
    # Changes sales and sales_rolling_avg_7d columns to row values using date as pivot
    data_dollars_consumed = data_dollars_consumed.melt(
        id_vars=["date"], value_vars=["sales", "sales_rolling_avg_7d"]
    )
    data_dollars_consumed["date"] = pd.to_datetime(
        data_dollars_consumed["date"]
    ).dt.date
    # Filter dollar consumed dataframe by filtered data range
    data_dollars_consumed = data_dollars_consumed[
        (data_dollars_consumed["date"] >= selected_dates[0])
        & (data_dollars_consumed["date"] <= selected_dates[1])
    ]
    data_dollars_consumed = data_dollars_consumed.reset_index(drop=True)
    # Creates chart for dollars consumed
    chart_dollars_consumed = altair_line_chart(
        data_dollars_consumed, "Sales in Dollars", ",.0f"
    )
    render_tile(
        df=data_dollars_consumed,
        description=description_dollars_consumed,
        sql=query_dollars_consumed,
        chart=chart_dollars_consumed,
    )
with cold:
    description_numbers_of_views: str = (
        """Gets the number of unique views associated with the use of CloudWiFiControllers rolling 28 day, 7 day, and 1 day."""
    )
    query_numbers_of_views = query_number_of_views_of_wifi_controller()
    data_numbers_of_views = get_dataframe_from_query_with_lowercase_columns(
        query_numbers_of_views
    )
    # Changes daily_views, last_7_days_views and last_28_days_views columns to row values using date as pivot
    data_numbers_of_views = data_numbers_of_views.melt(
        id_vars=["date"],
        value_vars=["daily_views", "last_7_days_views", "last_28_days_views"],
    )
    # Filter number of views dataframe by filtered data range
    data_numbers_of_views = data_numbers_of_views[
        (data_numbers_of_views["date"] >= selected_dates[0])
        & (data_numbers_of_views["date"] <= selected_dates[1])
    ]
    data_numbers_of_views = data_numbers_of_views.reset_index(drop=True)
    # Creates chart for number of views
    chart_numbers_of_views = altair_line_chart(
        data_numbers_of_views, "Unique Views", ",.0f"
    )
    render_tile(
        df=data_numbers_of_views,
        description=description_numbers_of_views,
        sql=query_numbers_of_views,
        chart=chart_numbers_of_views,
    )
