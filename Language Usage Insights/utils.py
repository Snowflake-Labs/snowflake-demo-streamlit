from typing import List
import numpy as np
import pandas as pd
import streamlit as st


def select_locale_data(locale_list: List[str]) -> str:
    """
    Select all from `LOCALE_USAGE` where the `LOCALE` is in the parameter list.
    """
    return f"""
            SELECT
                   DATE,
                   LOCALE,
                   NUM_DEVELOPERS,
                   COUNTRY
            FROM
                   LOCALE_USAGE
            WHERE
                   LOCALE IN (
                          {str(locale_list).replace('[', '').replace(']', '')}
                   )
            ORDER BY
                LOCALE,
                DATE;
            """


def select_union_data(locale_list: List[str]) -> str:
    """
    Select date and the sum of all the developers that are in that date, filtered by the locale list.
    """
    return f"""
            SELECT
                   DATE,
                   'Union' AS LOCALE,
                   SUM(NUM_DEVELOPERS) AS NUM_DEVELOPERS
            FROM
                   LOCALE_USAGE
            WHERE
                   LOCALE IN (
                          {str(locale_list).replace('[', '').replace(']', '')}
                   )
            GROUP BY
                DATE;
            """


def select_country_data() -> str:
    """
    Select geometry information of some countries around the world.
    """
    return f"""
            SELECT
                COUNTRY,
                GEOMETRY
            FROM
                COUNTRY_INFORMATION
            ORDER BY
                COUNTRY;
            """


def get_column_config(df: pd.DataFrame) -> dict:
    """
    Gets transformed columns.
    """
    return {
        col: st.column_config.Column(
            col.replace("_", " ").replace("num ", "number of ").title()
        )
        for col in df.columns
    }


def gradient_color_array(array_length: int) -> List[List[int]]:
    """
    Generate a color scale based on an array of values with a gradient between two colors.
    """

    start_color = np.array([240, 206, 115])  # RGB for #f0ce73 (light yellow)
    end_color = np.array([241, 39, 17])  # RGB for #f12711 (vibrant red)

    if array_length == 1:
        return [tuple(int(x) for x in end_color)]

    values = np.arange(array_length)
    # Normalize values to range [0, 1]
    normalized_values = (values - np.min(values)) / (np.max(values) - np.min(values))

    # Interpolate RGB values based on normalized values
    interpolated_colors = []
    for value in normalized_values:
        interpolated_color = (1 - value) * start_color + value * end_color
        rgb_tuple = tuple(int(x) for x in interpolated_color)
        interpolated_colors.append(rgb_tuple)

    return interpolated_colors
