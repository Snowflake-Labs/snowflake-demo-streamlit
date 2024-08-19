from typing import List, Union
import streamlit as st
import utils.data_access as da
import utils.helpers as hp

CITY_KEY = "s_cities"
CITY_LABEL = "City:"
COUNTRY_KEY = "s_countries"
COUNTRY_LABEL = "Country:"
CITY_COLUMN_NAME = "CITY_NAME"
CITY_GB_KEY = "GB"
FIRST_RUN_KEY = "first_run"
CATEGORY_PUB_VALUE = "pub"
CATEGORY_LABEL = "Select Category:"
CATEGORY_KEY = "r_category"
CATEGORY_COLUMN_NAME = "CATEGORY"
H3_RESOLUTION_KEY = "sl_resolution"
H3_RESOLUTION_LABEL = "H3 Resolution:"
LAYER_LABEL = "Select Layers:"
LAYER_DEFAULT = "H3"
LAYER_KEY = "ms_layer"


def create_selectbox(
    key: str, label: str, options: List, index: Union[int, None] = None
) -> None:
    """
    Creates a selectbox widget using Streamlit.

    Parameters:
        key (str): The key used to store the selected value in the session state.
        label (str): The label to display for the selectbox.
        options (List): The list of options to display in the selectbox.
        index (Union[int, None], optional): The index of the default selected option. Defaults to None.

    Returns:
        None
    """
    if index is None:
        st.selectbox(
            label,
            options,
            key=key,
        )
    else:
        st.selectbox(
            label,
            options,
            key=key,
            index=index,
        )


def create_cities_widget() -> None:
    """
    Creates a widget for selecting cities based on the country selected.

    This function retrieves the cities data based on the selected country and creates a selectbox widget
    for selecting a city. If a city was previously selected, it selects that city in the widget. If no city
    was previously selected, it selects the first city in the list.

    Returns:
        None
    """
    s_cities_data = da.get_cities(st.session_state[COUNTRY_KEY])
    if st.session_state[COUNTRY_KEY] == CITY_GB_KEY and st.session_state[FIRST_RUN_KEY]:
        create_selectbox(CITY_KEY, CITY_LABEL, s_cities_data, 208)
    else:
        # City was previously selected
        if CITY_KEY in st.session_state:
            found_cities_with_session_city = s_cities_data.index[
                s_cities_data[CITY_COLUMN_NAME] == st.session_state[CITY_KEY]
            ].tolist()

            # Selected city is in the list.
            if len(
                found_cities_with_session_city
            ) > 0 and found_cities_with_session_city[0] < len(s_cities_data):
                create_selectbox(
                    CITY_KEY,
                    CITY_LABEL,
                    s_cities_data,
                    found_cities_with_session_city[0],
                )
            else:
                # Select the first city in the list.
                if len(s_cities_data) > 1:
                    create_selectbox(
                        CITY_KEY,
                        CITY_LABEL,
                        s_cities_data,
                        1,
                    )
                else:
                    create_selectbox(
                        CITY_KEY,
                        CITY_LABEL,
                        s_cities_data,
                    )
        else:
            # No city was previously selected. Select the first city in the list.
            if len(s_cities_data) > 0:
                create_selectbox(
                    CITY_KEY,
                    CITY_LABEL,
                    s_cities_data,
                    1,
                )
            else:
                create_selectbox(
                    CITY_KEY,
                    CITY_LABEL,
                    s_cities_data,
                )


def create_countries_widget() -> None:
    """
    Creates a selectbox widget for selecting countries.

    Returns:
        None
    """
    countries_df = da.get_countries()
    st.selectbox(
        COUNTRY_LABEL,
        countries_df["COUNTRY_CODE"],
        key=COUNTRY_KEY,
        index=237,  # 218
        format_func=lambda x: countries_df[countries_df["COUNTRY_CODE"] == x][
            "COUNTRY_NAME"
        ].iloc[0],
    )


def create_multiselect(
    key: str,
    label: str,
    options: List,
    default_value: Union[str, None] = None,
    help: str = None,
) -> None:
    """
    Create a multiselect widget using Streamlit.

    Parameters:
        key (str): The key to store the selected values in the session state.
        label (str): The label to display for the multiselect widget.
        options (List): The list of options to display in the multiselect widget.
        default_value (Union[str, None], optional): The default value(s) to select in the multiselect widget. Defaults to None.

    Returns:
        None
    """
    if default_value is None:
        st.session_state[key] = st.multiselect(
            label,
            options,
            key=key,
            format_func=lambda x: x.title().replace("_", " "),
            help=help,
        )
    else:
        st.multiselect(
            label,
            options,
            key=key,
            format_func=lambda x: x.title().replace("_", " "),
            default=default_value,
            help=help,
        )


def create_categories_widget():
    """
    Creates a widget for selecting categories.

    This function retrieves the top 10 categories by places and creates a multiselect widget for selecting categories.
    If the country key is CITY_GB_KEY and it is the first run, the widget will be created with the previously selected categories.
    Otherwise, the widget will be created with the categories that exist in the current top 10 categories by places.

    Parameters:
        None

    Returns:
        None
    """
    ms_categories_data = da.get_top_10_categories_by_places()
    if st.session_state[COUNTRY_KEY] == CITY_GB_KEY and st.session_state[FIRST_RUN_KEY]:
        create_multiselect(
            CATEGORY_KEY, CATEGORY_LABEL, ms_categories_data, CATEGORY_PUB_VALUE
        )
    else:
        # Checks if the category was previously selected.
        if CATEGORY_KEY in st.session_state:
            # Get previously selected categories that exist in the current top 10 categories by places.
            cat_values = ms_categories_data[CATEGORY_COLUMN_NAME].values
            list_selected_values = []
            for cate in st.session_state[CATEGORY_KEY]:
                if cate in cat_values and cate not in list_selected_values:
                    list_selected_values.append(cate)

            if len(list_selected_values) > 0:
                create_multiselect(
                    CATEGORY_KEY,
                    CATEGORY_LABEL,
                    ms_categories_data,
                    list_selected_values,
                )
            else:
                # Select the first category in the list.
                if len(ms_categories_data) > 0:
                    create_multiselect(
                        CATEGORY_KEY,
                        CATEGORY_LABEL,
                        ms_categories_data,
                        [ms_categories_data.iloc[0, 0]],
                    )
                else:
                    create_multiselect(
                        CATEGORY_KEY,
                        CATEGORY_LABEL,
                        ms_categories_data,
                    )
        else:
            create_multiselect(
                CATEGORY_KEY,
                CATEGORY_LABEL,
                ms_categories_data,
            )


def create_slider(
    label: str, options: List, value: int, key: str, help: str = None
) -> None:
    """
    Creates a slider widget using the Streamlit library.

    Parameters:
        label (str): The label to display next to the slider.
        options (List): The list of options for the slider.
        value (int): The initial value of the slider.
        key (str): The key to identify the slider.

    Returns:
        None
    """
    st.select_slider(label, options=options, value=value, key=key, help=help)


def create_h3_resolution_slider() -> None:
    """
    Creates a slider widget for selecting the H3 resolution.

    This function creates a slider widget that allows the user to select the H3 resolution.
    The available resolution options are determined by the `get_resolution_slider_options` function.
    The default resolution is set to 8.

    Returns:
        None
    """
    create_slider(
        H3_RESOLUTION_LABEL,
        hp.get_resolution_slider_options(8),
        8,
        H3_RESOLUTION_KEY,
        "Determines hexagon size for mapping Earth's surface. Higher numbers mean smaller hexagons, more detail; lower numbers, larger hexagons, broader coverage.",
    )


def create_layer_widget() -> None:
    """
    Creates a layer widget with a multiselect dropdown.

    This function creates a widget that allows the user to select multiple layers
    from a dropdown menu.

    Returns:
        None
    """
    options = ["H3", "POI"]
    create_multiselect(
        LAYER_KEY,
        LAYER_LABEL,
        options,
        LAYER_DEFAULT,
        "Choose the layers to display on the map. H3 is the default layer representing geographic regions. POI indicates points of interest. To view the Train Stations layer, choose Manchester from the city dropdown menu.",
    )
