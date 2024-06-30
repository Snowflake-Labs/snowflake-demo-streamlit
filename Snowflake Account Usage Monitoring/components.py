from processing import get_column_config
from snowflake.snowpark import Session
from typing import Callable, Tuple
import altair as alt
import datetime
import pandas as pd
import streamlit as st


def get_bar_chart(
    dataframe: pd.DataFrame,
    date_column: str,
    value_column: str,
    format_function: Callable[..., int],
) -> alt.Chart:
    """
    Get a new bar chart based on the given dataframe.
    """
    formated_value_name = f"formatted_{value_column}"
    dataframe[formated_value_name] = dataframe[value_column].apply(format_function)
    chart = (
        alt.Chart(dataframe)
        .mark_bar(opacity=1, color="#1c83e1")
        .encode(
            x=alt.X(f"yearmonthdate({date_column})", title="Day"),
            y=alt.Y(f"sum({value_column})", title="Consumption"),
            tooltip=[
                alt.Tooltip(
                    date_column, title=f"{date_column.replace('_', ' ').title()}:"
                ),
                alt.Tooltip(
                    formated_value_name,
                    title=f"{value_column.replace('_', ' ').title()}:",
                ),
            ],
        )
    )

    return chart


def get_histogram_chart(
    dataframe: pd.DataFrame,
    date_column: str,
) -> alt.Chart:
    """
    Get a new histogram based on the given dataframe.
    """
    chart = (
        alt.Chart(dataframe)
        .mark_bar(color="#1c83e1")
        .encode(
            x=alt.X(
                date_column,
                title="Duration in Seconds",
                bin=alt.BinParams(
                    maxbins=100,
                ),
            ),
            y=alt.Y(
                "count()",
                title="Count of Records",
                scale=alt.Scale(type="symlog"),
            ),
            tooltip=[
                alt.Tooltip(date_column, title=date_column.replace("_", "").title()),
                "count()",
            ],
        )
    )

    return chart


def get_scatter_chart(
    dataframe: pd.DataFrame,
) -> alt.Chart:
    """
    Get a new scatter chart based on the given dataframe.
    """
    chart = (
        alt.Chart(dataframe)
        .mark_circle(size=200, opacity=0.7, color="#1c83e1")
        .encode(
            x=alt.X(
                "NUMBER_OF_QUERIES_LOG:Q",
                title="Number of queries (log scale)",
                scale=alt.Scale(
                    domain=[
                        dataframe["NUMBER_OF_QUERIES_LOG"].min() - 0.5,
                        dataframe["NUMBER_OF_QUERIES_LOG"].max() + 0.5,
                    ]
                ),
            ),
            y=alt.Y(
                "EXECUTION_MINUTES_LOG:Q",
                title="Execution minutes (log scale)",
                scale=alt.Scale(
                    domain=[
                        dataframe["EXECUTION_MINUTES_LOG"].min() - 0.5,
                        dataframe["EXECUTION_MINUTES_LOG"].max() + 0.5,
                    ]
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "NUMBER_OF_QUERIES_LOG:Q", title="Number of executions (Log):"
                ),
                alt.Tooltip(
                    "EXECUTION_MINUTES_LOG:Q",
                    title="Execution duration (Minutes) (Log):",
                ),
            ],
        )
    )

    return chart


def dataframe_with_podium(dataframe: pd.DataFrame, sort_by: str = None) -> None:
    """
    Replaces dataframe indices 1, 2, 3 with medals 🥇, 🥈, 🥉
    """
    if sort_by:
        # Sort dataframe and take top-10
        sorted_df = (
            dataframe.sort_values(by=sort_by, ascending=False)
            .reset_index(drop=True)
            .head(10)
        )
    else:
        sorted_df = dataframe.head(10).copy()

    # Replace index to highlight the podium (gold, metal, bronze)
    new_index = ["🥇", "🥈", "🥉"] + list(map(str, range(4, 11)))
    sorted_df.index = new_index[: len(sorted_df)]
    st.dataframe(
        sorted_df, use_container_width=True, column_config=get_column_config(dataframe)
    )


def date_selector() -> Tuple[datetime.date, datetime.date]:
    """
    Adds a date selector with a few different options.
    """
    date_range = st.selectbox(
        "Date range",
        options=[
            "Last 7 days",
            "Last 28 days",
            "Last 3 months",
            "Last 6 months",
            "Last 12 months",
            "Custom",
        ],
        index=0,
        key="date_range",
    )

    if date_range != "Custom":
        date_to = datetime.date.today()
        if date_range == "Last 7 days":
            date_from = date_to - datetime.timedelta(days=7)
        elif date_range == "Last 28 days":
            date_from = date_to - datetime.timedelta(days=28)
        elif date_range == "Last 3 months":
            date_from = date_to - datetime.timedelta(weeks=12)
        elif date_range == "Last 6 months":
            date_from = date_to - datetime.timedelta(weeks=24)
        elif date_range == "Last 12 months":
            date_from = date_to - datetime.timedelta(days=365)
    else:
        date_from, date_to = st.date_input(
            "Choose start and end date",
            key="custom",
        )

    st.caption(f"Your selection is from **{date_from}** to **{date_to}**")

    return date_from, date_to


def aggregation_selector() -> str:
    """
    Render an aggregate selector, return the user selection.
    """
    selection = st.selectbox(
        "Aggregation period",
        options=[
            "Daily",
            "Weekly",
            "Monthly",
        ],
        key="aggregation_selector",
    )
    return selection


def select_warehouse_name(session: Session, key: str) -> str:
    """
    Display a selectbox with all the warehouses names, then return the selected warehouse name.
    """
    warehouse = session.sql("SHOW WAREHOUSES;").collect()
    warehouse_dataframe = pd.DataFrame(warehouse)
    selected_warehouse = st.selectbox(
        "Select a Warehouse", warehouse_dataframe["name"], key=key
    )

    return selected_warehouse
