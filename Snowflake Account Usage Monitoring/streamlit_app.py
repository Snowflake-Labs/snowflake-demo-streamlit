from components import (
    aggregation_selector,
    dataframe_with_podium,
    date_selector,
    get_bar_chart,
    get_histogram_chart,
    get_scatter_chart,
    select_warehouse_name,
)
from pages import show_pages, Page
from processing import (
    aggregate_data,
    apply_log1p,
    format_credits,
    format_sql_query,
    format_time,
    get_dataframe,
)
from queries import (
    consumption_per_service_type_query,
    query_count_query,
    queries_query,
    credits_by_users_query,
)
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
import altair as alt
import streamlit as st

st.set_page_config(layout="centered")
session: Session = get_active_session()


# Renders the sidebar with all the pages available in the app.
show_pages(
    [
        Page("streamlit_app.py", "Compute Insights", "📊"),
        Page("storage_page.py", "Storage Insights", "🗄️"),
        Page("data_transfer_page.py", "Data Transfer Insights", "🌐"),
    ]
)

with st.sidebar:
    date_from, date_to = date_selector()
    aggregation = aggregation_selector()

st.header("Compute Insights")

st.write(
    """
    In this section, we will cover credits and compute consumption over time.
    You will be able to see the total credits spent within a specified period by each warehouse,
    along with detailed query information such as duration.
    Additionally, we will highlight the users who have consumed the most resources.
    This comprehensive overview helps in understanding resource utilization and identifying
    patterns or anomalies in consumption.
    """
)
# Credits
st.subheader("Credits Consumption")

# Get data
query = consumption_per_service_type_query(date_from=date_from, date_to=date_to)
consumption_dataframe = get_dataframe(session, query)

# Add filtering widget per Service type
all_values = consumption_dataframe["SERVICE_TYPE"].unique().tolist()
selected_value = st.selectbox(
    "Choose service type",
    ["All"] + all_values,
    0,
)

if selected_value == "All":
    selected_value = all_values
else:
    selected_value = [selected_value]

# Filter dataframe accordingly
consumption_dataframe = consumption_dataframe[
    consumption_dataframe["SERVICE_TYPE"].isin(selected_value)
]

# Get consumption
consumption = int(consumption_dataframe["CREDITS_USED"].sum())

if consumption_dataframe.empty:
    st.caption("No data found.")
elif consumption == 0:
    st.caption("No consumption found.")
else:
    st.write(
        f"A total of __{format_credits(consumption)}__ credits were used during the selected period."
    )

    # Aggregate data
    aggregated_dataframe = aggregate_data(
        consumption_dataframe, date_column="START_TIME", aggregate_by=aggregation
    )

    # Bar chart
    bar_chart = get_bar_chart(
        dataframe=aggregated_dataframe,
        date_column="START_TIME",
        value_column="CREDITS_USED",
        format_function=format_credits,
    )

    st.altair_chart(bar_chart, use_container_width=True)

    # Group by
    agg_config = {"CREDITS_USED": "sum"}
    grouped_dataframe = (
        consumption_dataframe.groupby(["NAME", "SERVICE_TYPE"])
        .agg(agg_config)
        .reset_index()
    )

    # Sort and select the top 10 most consuming warehouses.
    most_consuming_warehouses = grouped_dataframe.sort_values(
        by="CREDITS_USED", ascending=False
    ).head(10)

    most_consuming_warehouses["CREDITS_USED"] = most_consuming_warehouses[
        "CREDITS_USED"
    ].apply(format_credits)

    st.subheader("Most Consuming Warehouses")

    dataframe_with_podium(
        most_consuming_warehouses,
    )

    st.divider()

# Queries
st.subheader("Queries")

# Get data
warehouse = select_warehouse_name(session, "select_warehouse")

with st.spinner("Retreiving Query Data..."):
    query = queries_query(warehouse, date_from, date_to)

    queries_dataframe = get_dataframe(session, query)

    if not queries_dataframe.empty:
        queries_dataframe["DURATION_SECS"] = round(
            (queries_dataframe.TOTAL_ELAPSED_TIME) / 1000
        )
        queries_dataframe["DURATION_SECS_PP"] = queries_dataframe[
            "DURATION_SECS"
        ].apply(format_time)
        queries_dataframe["QUERY_TEXT_PP"] = queries_dataframe["QUERY_TEXT"].apply(
            format_sql_query
        )

        st.subheader("Histogram of queries duration (in secs)")

        # Histogram
        histogram = get_histogram_chart(
            dataframe=queries_dataframe,
            date_column="DURATION_SECS",
        )

        st.altair_chart(histogram, use_container_width=True)

        st.subheader("Query optimization: longest and most frequent queries")

        min_execution_col, limit_col = st.columns(2)

        min_num_execution = min_execution_col.selectbox(
            "Minimun number of query executions", [10, 50, 100]
        )

        limit = limit_col.selectbox("Limit of Queries", [100, 200, 300])

        queries_count_query = query_count_query(
            date_from=date_from,
            date_to=date_to,
            warehouse_name=warehouse,
            min_num_execution=min_num_execution,
            limit=limit,
        )

        queries_count_dataframe = get_dataframe(session, queries_count_query)

        queries_agg = apply_log1p(
            dataframe=queries_count_dataframe,
            columns=["EXECUTION_MINUTES", "NUMBER_OF_QUERIES"],
        )

        scatter_chart = get_scatter_chart(dataframe=queries_agg)

        st.altair_chart(
            scatter_chart,
            use_container_width=True,
        )
    else:
        st.warning(
            "No queries were executed in the selected warehouse during the specified timeframe."
        )


st.divider()

# Users
st.subheader("Users Consumption")

st.write("Users with the largest number of credits spent")
limit = st.selectbox("Limit of users", [10, 20, 30])

with st.spinner("Retreiving Users Data..."):
    # Get data
    query = credits_by_users_query(date_from=date_from, date_to=date_to, limit=limit)

    user_dataframe = get_dataframe(session, query)

    # Bar chart
    chart = (
        alt.Chart(user_dataframe)
        .mark_bar()
        .encode(
            y=alt.Y("USER_NAME:N", title="Username", sort="x"),
            x=alt.X(
                "APPROXIMATE_CREDITS_USED:Q",
                title="Approximate credits used",
                axis=alt.Axis(format=",.2f"),
            ),
        )
    )

    st.altair_chart(chart, use_container_width=True)
