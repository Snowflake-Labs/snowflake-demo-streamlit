from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
from utils import (
    select_power_curve_data,
    get_chart_color,
    default_start,
    default_end,
)
from components import date_range_picker, cohort_chart, power_curve_chart
import streamlit as st

# Connection
session: Session = get_active_session()


# Streamlit settings
st.set_page_config(layout="wide")


# We need to add filters for the cohort section, to use those in our query.
st.header("SnowSports: Snowboard and ski rental company")
st.subheader("Cohort Analysis")

with st.expander("Filters"):
    cohort_start_date, cohort_end_date = date_range_picker(
        title="Pick a start and end date",
        default_start=default_start(6),
        default_end=default_end(),
    )

    left, right, _ = st.columns((0.7, 1, 0.5))
    timeframe = left.radio(
        "Timeframe",
        ["week", "month"],
        horizontal=True,
        format_func=str.title,
        key="timeframe",
    )

    percentage = right.radio(
        "Format", ["Percentages", "Absolute"], horizontal=True, key="percentage"
    )


# With the data filtered, we can rendered the cohort charts.
left, right = st.columns(2, gap="large")

with left:
    st.subheader("Skis")
    description = "Cohort based analysis of retention for ski usage during the time period."
    st.write(description)

    cohort_chart(
        "PRODUCT_1_RETENTION_BY_",
        description,
        cohort_start_date,
        cohort_end_date,
        "cohort_chart_1",
        timeframe,
        percentage,
        session,
        get_chart_color(
            "#ffdde1", "#ee9ca7"
        ),  # Gradient of colors from pink to light pink.
    )


with right:
    st.subheader("Snowboards")
    description = "Cohort based analysis of retention for snowboard usage during the time period."
    st.write(description)

    cohort_chart(
        "PRODUCT_2_RETENTION_BY_",
        description,
        cohort_start_date,
        cohort_end_date,
        "cohort_chart_2",
        timeframe,
        percentage,
        session,
        get_chart_color(
            "#654ea3", "#eaafc8"
        ),  # Gradient of colors from light pink to purple.
    )

# Now create a new chart, first let us filter the data.
st.subheader("Power User Curves")
with st.expander("Filters"):
    power_start_date, power_end_date = date_range_picker(
        title="Pick a start and end date",
        default_start=default_start(10),
        default_end=default_end(),
        key="date_range_picker_2",
    )
st.subheader("Snowboard Usage")
left, right = st.columns(2)

# Then, render some new cool power user curves charts.
power_curve_chart(
    select_power_curve_data(
        "PRODUCT_1_ACTIVITY_BY_DAY",
        power_start_date,
        power_end_date,
    ),
    "In this chart, users are defined as active when they have used at least once within the set time frame.",
    "power_curve_1",
    session,
    "#CF8BF3",  # Magenta color.
)

left, right = st.columns(2)
with left:
    st.subheader("Skis Views")
    power_curve_chart(
        select_power_curve_data(
            "PRODUCT_2_VIEWS_ACTIVITY_BY_DAY",
            power_start_date,
            power_end_date,
        ),
        "In this chart, users are defined as active when they have viewed at least once within the set time frame.",
        "power_curve_2",
        session,
        "#6A82FB",  # Light blue color.
    )
with right:
    st.subheader("Skis Usage")
    power_curve_chart(
        select_power_curve_data(
            "PRODUCT_2_ACTIVITY_BY_DAY",
            power_start_date,
            power_end_date,
        ),
        "In this chart, users are defined as active when they have used at least once within the set time frame.",
        "power_curve_3",
        session,
        "#D3CCE3",  # Lilac color.
    )
