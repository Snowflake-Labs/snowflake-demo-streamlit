from typing import List
import branca.colormap as cm
import csv
import h3
import math
import numpy as np


def get_resolution_slider_options(computed_resolution: int) -> List:
    """
    Returns a list of resolution options for a slider based on the computed resolution.

    Args:
        computed_resolution (int): The computed resolution.

    Returns:
        List: A list of resolution options for the slider.
    """
    sl_resolution_options = []
    l_shift = 2
    for l_res in range(computed_resolution - 1, 0, -1):
        if l_shift == 0:
            break
        sl_resolution_options.append(l_res)
        l_shift = l_shift - 1
    sl_resolution_options.append(computed_resolution)
    r_shift = 2
    for r_res in range(computed_resolution + 1, 15):
        if r_shift == 0:
            break
        sl_resolution_options.append(r_res)
        r_shift = r_shift - 1
    sl_resolution_options.sort()

    return sl_resolution_options


def generate_linear_color_map(colors: List, quantiles: float):
    """
    Generate a linear color map based on a list of colors and quantiles.

    Args:
        colors (List): A list of colors to be used in the color map.
        quantiles (float): The quantiles used to determine the minimum and maximum values of the color map.

    Returns:
        cm.LinearColormap: A linear color map object.

    """
    return cm.LinearColormap(
        colors,
        vmin=quantiles.min(),
        vmax=quantiles.max(),
        index=quantiles,
    )


def read_csv_file(file_path: str) -> dict:
    """
    Reads a CSV file and returns a dictionary with country codes as keys and country names as values.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        dict: A dictionary with country codes as keys and country names as values.
    """
    country_dict = {}

    with open(file_path, mode="r", newline="", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            country_code = row[0].strip()
            country_name = row[1].strip()
            country_dict[country_code] = country_name

    return country_dict


def calculate_zoom_for_h3(center_lat: float, center_lon: float, resolution: int) -> int:
    """
    Calculates the zoom level for a given H3 hexagon based on the center latitude, center longitude, and resolution.

    Args:
        center_lat (float): The latitude of the center point.
        center_lon (float): The longitude of the center point.
        resolution (int): The resolution of the H3 hexagon.

    Returns:
        int: The calculated zoom level.

    """
    if np.isnan(center_lat) or np.isnan(center_lon):
        return 4
    # Calculate the size of a single H3 hexagon at the given resolution
    hex_size_meters = h3.edge_length(resolution)
    # Assuming a map viewport size (width or height)
    viewport_size_pixels = 150
    # Calculate the zoom level based on the hexagon size and viewport size
    zoom = math.log2(
        (156543.03392 * math.cos(center_lat * math.pi / 180))
        / (hex_size_meters * viewport_size_pixels)
    )

    return int(zoom)
