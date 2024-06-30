from components import (
    aggregation_selector,
    dataframe_with_podium,
    get_bar_chart,
    date_selector,
)
from processing import aggregate_data, format_bytes, get_dataframe
from queries import storage_query
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
import streamlit as st

session: Session = get_active_session()


# Date selector widget
with st.sidebar:
    date_from, date_to = date_selector()
    aggregation = aggregation_selector()

# Header
st.title("Storage Insights")
st.write(
    """
    In this section, we will delve into storage consumption trends over time,
    providing insights into the average storage usage on a daily, weekly,
    or monthly basis. Additionally, we will identify the databases that contribute
    most significantly to the overall storage consumption.
    """
)

# Get data
query = storage_query(date_from=date_from, date_to=date_to)
dataframe = get_dataframe(session, query)

# Get consumption
consumption = dataframe["DATABASE_BYTES"].sum()

if dataframe.empty:
    st.caption("No data found.")
    st.stop()
if consumption == 0:
    st.caption("No consumption!")
    st.stop()

# Resample by day
dataframe_resampled = aggregate_data(
    dataframe, date_column="USAGE_DATE", aggregate_by=aggregation
)

st.subheader("Storage Spend Over Time")
st.write(
    f"Average __{format_bytes(int(dataframe_resampled.DATABASE_BYTES.mean()))}__ were used {aggregation.lower()}."
)

# Bar chart
chart = get_bar_chart(
    dataframe=dataframe_resampled,
    date_column="USAGE_DATE",
    value_column="DATABASE_BYTES",
    format_function=format_bytes,
)

st.altair_chart(chart, use_container_width=True)

# Group by
top_storage_consumption = (
    (
        dataframe.groupby(["OBJECT_NAME", "USAGE_DATE"])
        .DATABASE_BYTES.mean()
        .reset_index()
        .groupby("OBJECT_NAME")
        .mean()
        .reset_index()
    )
    .sort_values(by="DATABASE_BYTES", ascending=False)
    .head(10)
)

top_storage_consumption["AVG_DAILY_STORAGE_SIZE"] = top_storage_consumption[
    "DATABASE_BYTES"
].apply(format_bytes)

st.subheader("Top Storage Consuming Databases")
dataframe_with_podium(
    top_storage_consumption[["OBJECT_NAME", "AVG_DAILY_STORAGE_SIZE"]],
)
