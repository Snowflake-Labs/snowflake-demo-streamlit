from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.table import Table
from snowflake.snowpark.types import StringType
from typing import List
import h3
import math
import numpy as np
import pandas as pd
import snowflake.snowpark.functions as fnc
import streamlit as st
import utils.helpers as hp
import utils.widgets as wdg

COUNTRY_NAMES_FILE_PATH = base_dir = "./assets/country_names_code.csv"
session = get_active_session()


@st.cache_data
def get_countries() -> List:
    """
    Retrieves a list of distinct country codes from the 'overturemaps.public.place' table.

    Returns:
        List: A list of distinct country codes.
    """
    countries_df = (
        session.table("overturemaps.public.place")
        .select(
            fnc.col("ADDRESSES")["list"][0]["element"]["country"]
            .astype(StringType())
            .alias("country_code")
        )
        .distinct()
        .filter(fnc.col("country_code").isNotNull())
        .to_pandas()
    )

    countries_dic = hp.read_csv_file(COUNTRY_NAMES_FILE_PATH)

    countries_df["COUNTRY_NAME"] = countries_df["COUNTRY_CODE"].apply(
        lambda country_name: countries_dic.get(country_name, None)
    )
    countries_df = countries_df.sort_values("COUNTRY_NAME")

    return countries_df


@st.cache_data
def get_cities(country: str) -> pd.DataFrame:
    """
    Retrieves a DataFrame of cities based on the specified country.

    Parameters:
    - country (str): The country to filter the cities by.

    Returns:
    - pd.DataFrame: A DataFrame containing the cities that meet the filter criteria.
    """
    cities = (
        session.table("overturemaps.public.place")
        .filter(fnc.col("addresses")["list"][0]["element"]["country"] == country)
        .filter(fnc.col("addresses")["list"][0]["element"]["locality"].isNotNull())
        .select(
            fnc.col("addresses")["list"][0]["element"]["locality"]
            .astype(StringType())
            .alias("city_name")
        )
        .group_by("city_name")
        .count()
        .filter(fnc.col("count") > 1000)
        .distinct()
        .sort(fnc.col("city_name"))
        .to_pandas()
    )

    no_city_selected_row = {"CITY_NAME": "Not Selected"}
    cities.loc[0] = no_city_selected_row

    return cities


def get_centered_coordinate() -> pd.DataFrame:
    """
    Retrieves the centered coordinates of places, countries, and cities from the database.

    Returns:
        pd.DataFrame: A DataFrame containing the centered coordinates with columns 'LON' and 'LAT'.
    """
    dataframe = get_places_country_city_sp_table()
    centered = dataframe.select(
        fnc.avg(fnc.call_builtin("ST_X", fnc.col("geometry"))).alias("LON"),
        fnc.avg(fnc.call_builtin("ST_Y", fnc.col("geometry"))).alias("LAT"),
    ).to_pandas()
    return centered


def get_places_country_city_sp_table(filter_category: bool = True) -> Table:
    """
    Retrieves a table of places filtered by country, city, and category.

    Args:
        filter_category (bool, optional): Whether to filter by category. Defaults to True.

    Returns:
        Table: A table of places filtered by country, city, and category.
    """
    x_min = get_percentile("ST_X", 0.001, filter_category)
    x_max = get_percentile("ST_X", 0.999, filter_category)
    y_min = get_percentile("ST_Y", 0.001, filter_category)
    y_max = get_percentile("ST_Y", 0.999, filter_category)

    places_country_city = (
        session.table("overturemaps.public.place")
        .filter(
            fnc.col("addresses")["list"][0]["element"]["country"]
            == st.session_state["s_countries"]
        )
        .filter(fnc.col("ADDRESSES")["list"][0]["element"]["locality"].isNotNull())
        .filter(fnc.col("CATEGORIES")["main"].isNotNull())
    )
    if (
        "s_cities" in st.session_state
        and st.session_state["s_cities"] is not None
        and st.session_state["s_cities"] != "Not Selected"
    ):
        places_country_city = places_country_city.filter(
            fnc.col("addresses")["list"][0]["element"]["locality"]
            == st.session_state["s_cities"]
        )
    if filter_category:
        if (
            "r_category" in st.session_state
            and st.session_state.r_category is not None
            and len(st.session_state.r_category) > 0
        ):
            places_country_city = places_country_city.filter(
                fnc.col("categories")["main"].isin(st.session_state.r_category)
            )
        else:
            places_country_city = places_country_city.filter(
                fnc.col("categories")["main"] == ""
            )

    places_country_city = places_country_city.filter(
        fnc.call_builtin("ST_X", fnc.col("geometry")) >= x_min
    )
    places_country_city = places_country_city.filter(
        fnc.call_builtin("ST_X", fnc.col("geometry")) < x_max
    )
    places_country_city = places_country_city.filter(
        fnc.call_builtin("ST_Y", fnc.col("geometry")) >= y_min
    )
    places_country_city = places_country_city.filter(
        fnc.call_builtin("ST_Y", fnc.col("geometry")) < y_max
    )
    return places_country_city


def get_percentile(function_name, approx_per, filter_category):
    """
    Calculate the percentile of a given function_name on the geometry column,
    filtered by the specified approx_per and filter_category.

    Args:
        function_name (str): The name of the function to be applied on the geometry column.
        approx_per (float): The approximate percentile value to calculate.
        filter_category (bool): Whether to filter by category or not.

    Returns:
        float: The calculated percentile value.

    """
    perce = (
        session.table("overturemaps.public.place")
        .select(
            fnc.approx_percentile(
                fnc.call_builtin(function_name, fnc.col("geometry")), approx_per
            )
        )
        .filter(
            fnc.col("addresses")["list"][0]["element"]["country"]
            == st.session_state["s_countries"]
        )
        .filter(fnc.col("ADDRESSES")["list"][0]["element"]["locality"].isNotNull())
        .filter(fnc.col("CATEGORIES")["main"].isNotNull())
    )
    if (
        "s_cities" in st.session_state
        and st.session_state["s_cities"] is not None
        and st.session_state["s_cities"] != "Not Selected"
    ):
        perce = perce.filter(
            fnc.col("addresses")["list"][0]["element"]["locality"]
            == st.session_state["s_cities"]
        )
    if (
        "r_category" in st.session_state
        and st.session_state.r_category is not None
        and filter_category
        and len(st.session_state.r_category) > 0
    ):
        perce = perce.filter(
            fnc.col("categories")["main"].isin(st.session_state.r_category)
        )
    return perce.to_pandas().iloc[0, 0]


def get_top_10_categories_by_places() -> pd.DataFrame:
    """
    Retrieves the top 10 categories by places.

    Returns:
        pd.DataFrame: A DataFrame containing the top 10 categories and their counts.
    """
    places_table = get_places_country_city_sp_table(False)

    places_table = places_table.select(
        fnc.col("categories")["main"].astype(StringType()).alias("CATEGORY"),
    )

    categories = places_table.group_by("CATEGORY").count()
    categories = (
        categories.filter(fnc.col("CATEGORY") != "None")
        .sort(fnc.col("count").desc(), fnc.col("CATEGORY"))
        .limit(10)
    )

    return categories.to_pandas()


def get_poi_df() -> pd.DataFrame:
    """
    Retrieves a pandas DataFrame containing points of interest (POI) data.

    Returns:
        pd.DataFrame: A DataFrame with columns for NAME, CATEGORY, LON, and LAT.
    """
    poi_df = get_places_country_city_sp_table().with_column(
        "LON", fnc.call_function("ST_X", fnc.col("GEOMETRY"))
    )
    poi_df = poi_df.with_column("LAT", fnc.call_function("ST_Y", fnc.col("GEOMETRY")))
    poi_df = poi_df.select(
        fnc.col("NAMES")["primary"].astype(StringType()).alias("NAME"),
        fnc.col("CATEGORIES")["main"].astype(StringType()).alias("CATEGORY"),
        fnc.col("LON"),
        fnc.col("LAT"),
    ).to_pandas()
    return poi_df


def get_count_h3_df():
    """
    Retrieves a DataFrame with the count of occurrences for each H3 cell.

    Returns:
        pandas.DataFrame: A DataFrame with two columns: 'H3' and 'count'.
    """
    h3_df = get_places_country_city_sp_table().with_column(
        "H3",
        fnc.call_function(
            "H3_POINT_TO_CELL_STRING",
            fnc.col("GEOMETRY"),
            fnc.lit(st.session_state[wdg.H3_RESOLUTION_KEY]),
        ),
    )
    h3_df = h3_df.group_by("H3").count().to_pandas()
    return h3_df


def add_h3_color_columns(h3_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds color columns to the H3 DataFrame based on the count values.

    Args:
        h3_df (pd.DataFrame): The DataFrame containing the H3 data.

    Returns:
        pd.DataFrame: The DataFrame with the added color columns.
    """
    max = h3_df["COUNT"].max()
    h3_df["R"] = h3_df["COUNT"] / max * 255
    h3_df["B"] = abs(((h3_df["COUNT"] / max) - 1) * 255)
    colors_list = ["gray", "blue", "green", "yellow", "orange", "red"]
    quantiles_pickups = h3_df["COUNT"].quantile([0, 0.25, 0.5, 0.75, 1])
    color_map_pickups = hp.generate_linear_color_map(colors_list, quantiles_pickups)
    h3_df["COLOR"] = h3_df["COUNT"].apply(color_map_pickups.rgb_bytes_tuple)
    return h3_df


def calculate_zoom_for_country() -> int:
    try:
        min_max_st_x_y = (
            get_places_country_city_sp_table()
            .select(
                fnc.min(fnc.call_builtin("ST_X", fnc.col("geometry"))).alias(
                    "min_st_lon"
                ),
                fnc.max(fnc.call_builtin("ST_X", fnc.col("geometry"))).alias(
                    "max_st_lon"
                ),
                fnc.min(fnc.call_builtin("ST_Y", fnc.col("geometry"))).alias(
                    "min_st_lat"
                ),
                fnc.max(fnc.call_builtin("ST_Y", fnc.col("geometry"))).alias(
                    "max_st_lat"
                ),
            )
            .to_pandas()
        )

        min_lon = min_max_st_x_y.iloc[0, 0]
        max_lon = min_max_st_x_y.iloc[0, 1]
        min_lat = min_max_st_x_y.iloc[0, 2]
        max_lat = min_max_st_x_y.iloc[0, 3]

        if (
            np.isnan(min_lat)
            or np.isnan(max_lat)
            or np.isnan(min_lon)
            or np.isnan(max_lon)
        ):
            return None

        hex_size_meters = h3.edge_length(8)

        lat_diff_meters = (
            h3.h3_distance(
                h3.geo_to_h3(min_lat, min_lon, 8), h3.geo_to_h3(max_lat, min_lon, 8)
            )
            * hex_size_meters
        )
        lon_diff_meters = (
            h3.h3_distance(
                h3.geo_to_h3(min_lat, min_lon, 8), h3.geo_to_h3(min_lat, max_lon, 8)
            )
            * hex_size_meters
        )

        viewport_size_pixels = 500

        zoom = math.log2(
            (156543.03392 * math.cos((min_lat + max_lat) / 2 * math.pi / 180))
            / max(
                lat_diff_meters, lon_diff_meters, hex_size_meters * viewport_size_pixels
            )
        )
    except Exception as _:
        zoom = 4

    return int(zoom)
