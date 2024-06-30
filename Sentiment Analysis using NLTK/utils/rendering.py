from math import floor
from typing import List, Union
import altair as alt
import pandas as pd
import streamlit as st


def display_count_table(label: str, df: pd.DataFrame, init_filter_divider: int) -> None:
    """Display a count dataframe as an interactive table with a slider.

    Args:
        label (str): The label name for the slider.
        df (pd.DataFrame): The provided data frame to be rendered.
        init_filter_divider (int): The filter devider.
    """
    xmax = int(floor(df["count"].max()))
    x = st.slider(label, 0, xmax, xmax // init_filter_divider)
    df = df[df["count"] > x]
    df = df.sort_values(by="count", ascending=False)
    st.dataframe(df, use_container_width=True)


def encode_chart(
    chart_object, time_unit: str, field: str, title: str, scale: Union[List[int], None]
):
    """Encodes altair chart.

    Args:
        chart_object (Chart): The chart to be encoded.
        time_unit (str): The time unit as a string.
        field (str): The data field that will be used for the y-axis.
        title (str): Custom title for the y-axis.
        scale (Union[List[int], None]): Configures the scale of the y-axis.

    Returns:
        _type_: Returns enconded chart.
    """
    if scale is None:
        y = alt.Y(field, title=title)
    else:
        y = alt.Y(field, title=title, scale=alt.Scale(domain=scale))

    return chart_object.encode(
        x=alt.X("date:T", timeUnit=time_unit, title="date"),
        y=y,
    )


def chart_mark_line(
    chart, time_unit: str, field: str, title: str, scale: Union[List[int], None]
):
    """Mark line for an altair chart.

    Args:
        chart (_type_): The chart object.
        time_unit (str): The time unit as a string.
        field (str): The data field that will be used for the y-axis.
        title (str): Custom title for the y-axis.
        scale (Union[List[int], None]): Configures the scale of the y-axis.

    Returns:
        _type_: Returns the chart mark line object.
    """
    c_mark_line = chart.mark_line(
        interpolate="catmull-rom",
        tooltip=True,
    )

    return encode_chart(c_mark_line, time_unit, field, title, scale)


def chart_mark_point(
    chart, time_unit: str, field: str, title: str, scale: Union[List[int], None]
):
    """Mark point for an altair chart.

    Args:
        chart (_type_): The chart object.
        time_unit (str): The time unit as a string.
        field (str): The data field that will be used for the y-axis.
        title (str): Custom title for the y-axis.
        scale (Union[List[int], None]): Configures the scale of the y-axis.

    Returns:
        _type_: Returns the chart mark point object.
    """
    c_mark_point = chart.mark_point(
        tooltip=True,
        size=75,
        filled=True,
    )

    return encode_chart(c_mark_point, time_unit, field, title, scale)
