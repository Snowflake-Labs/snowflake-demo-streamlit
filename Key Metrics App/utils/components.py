from datetime import date, timedelta
from typing import Any, Optional, Tuple, cast
import streamlit as st


def date_range_picker(
    title: str,
    default_start: Optional[date] = None,
    default_end: Optional[date] = None,
    key: Optional[str] = "dates",
) -> Tuple[date, date]:
    """
    This widget enforces a start and end date being selected.
    Defaults to a range of 30 days ago to today.
    Returns the selected start and end date.
    ---------
    title: str
        The date's input title.
    default_start: Optional[date]
        The default start date.
    default_end: Optional[date]
        The default end date.
    key: Optional[str] = "dates"
        The date's input key.
    """

    if default_start is None:
        default_start = date.today() - timedelta(days=22)
    if default_end is None:
        default_end = date.today() - timedelta(days=1)

    val = st.date_input(
        title,
        value=[default_start, default_end],
        key=key,
    )

    start_date, end_date = cast(Tuple[date, date], val)
    return start_date, end_date


def selectbox_filter(unique_values: list, name: str, key: str) -> str:
    """
    The selectbox filter component/
    ---------
    unique_values list:
        The selectbox values.
    name str:
        The selectbox's name.
    key str:
        The selectbox's key.
    """
    unique_values.loc[-1] = ["All"]
    unique_values.index = unique_values.index + 1
    unique_values = unique_values.sort_index()

    chosen = st.selectbox(name, unique_values, key=key)

    # If the user selects "All", we return None so that the filter is not applied
    if chosen == "All":
        return None
    else:
        return chosen
