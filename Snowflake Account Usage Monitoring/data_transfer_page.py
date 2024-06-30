from components import (
    aggregation_selector,
    dataframe_with_podium,
    date_selector,
    get_bar_chart,
)
from processing import aggregate_data, format_bytes, get_dataframe
from queries import data_transfer_query
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
import streamlit as st

st.set_page_config(layout="centered")

session: Session = get_active_session()

# Date and aggregations selectors
with st.sidebar:
    date_from, date_to = date_selector()
    aggregation = aggregation_selector()
# Header
st.title("Data Transfer Insights")
st.write(
    """
    In this section, you can explore detailed insights on how data
    has been transferred over time within your account.
    You will be able to track the volume of data movement,
    identify trends and patterns, and understand peak transfer periods.
    Additionally, this section highlights the most targeted region,
    providing a clear view of where the highest data transfer activity is occurring.
    """
)

# Get data
query = data_transfer_query(
    date_from,
    date_to,
)
data_transfer_dataframe = get_dataframe(session, query)

# Add filtering widget
all_values = data_transfer_dataframe["TARGET_REGION"].unique().tolist()
selected_value = st.selectbox("Choose target region", ["All"] + all_values)

if selected_value == "All":
    selected_value = all_values
else:
    selected_value = [selected_value]

# Filter dataframe accordingly
data_transfer_dataframe = data_transfer_dataframe[
    data_transfer_dataframe["TARGET_REGION"].isin(selected_value)
]

# Get consumption
consumption = int(data_transfer_dataframe["BYTES_TRANSFERRED"].sum())

if data_transfer_dataframe.empty:
    st.caption("No data found.")
    st.stop()
if consumption == 0:
    st.caption("No consumption!")
    st.stop()


st.write(f"__{format_bytes(consumption)}__ were used {aggregation.lower()}.")

st.subheader("Data Transfer Spend Over Time")

# Resample by day
df_resampled = aggregate_data(
    data_transfer_dataframe, date_column="START_TIME", aggregate_by=aggregation
)

# Bar chart
chart = get_bar_chart(
    dataframe=df_resampled,
    date_column="START_TIME",
    value_column="BYTES_TRANSFERRED",
    format_function=format_bytes,
)

st.altair_chart(chart, use_container_width=True)

# Group by
agg_config = {"BYTES_TRANSFERRED": "sum"}
df_grouped = (
    data_transfer_dataframe.groupby(["TRANSFER_TYPE", "TARGET_CLOUD", "TARGET_REGION"])
    .agg(agg_config)
    .reset_index()
)

# Sort and pretty print credits
df_grouped_top_10 = df_grouped.sort_values(
    by="BYTES_TRANSFERRED", ascending=False
).head(10)

df_grouped_top_10["BYTES_TRANSFERRED"] = df_grouped_top_10["BYTES_TRANSFERRED"].apply(
    format_bytes
)

st.subheader("Top Trasfered Targets")

dataframe_with_podium(
    df_grouped_top_10[
        [
            "TRANSFER_TYPE",
            "TARGET_CLOUD",
            "TARGET_REGION",
            "BYTES_TRANSFERRED",
        ]
    ]
)
