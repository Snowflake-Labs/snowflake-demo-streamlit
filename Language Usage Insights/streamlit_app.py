from components import (
    data_chart_container,
    locale_line_chart,
    polygon_heatmap_chart,
    group_and_agreaggate_data,
)
from locale_list import LOCALE_OPTIONS
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
from utils import select_union_data, select_locale_data
import streamlit as st

st.set_page_config(layout="wide")
session: Session = get_active_session()

# Let start with some text
st.title("Language Usage of MyApp")
st.write(
    """
    In this Streamlit app, we explore the language being used when visiting MyApp, this information can be useful to get insights where MyApp is most used around the globe, so other deeper analysis based on this languages can be made later.
    In the "Languages" section you can select a predefined set of languages or a region, then you can add or remove the specific languages on the second select.
    At last we have some checkboxes to normalize or union the data. At the very bottom of the Streamlit App, we have a line chart with your languages selections and finally a heatmap that shows where users have being using the app by country.
    """
)

# Now, let us set how the chart will show the data.
st.subheader("Languages")
with st.expander("Filters", expanded=True):

    # The first setting is the actual locales to add in the chart
    locale_options = st.selectbox(
        "Choose language or region starter kit",
        ["—"] + list(LOCALE_OPTIONS.keys()),
        help="These are pre-defined sets of languages or regions.",
        index=2,
    )
    default = []
    if locale_options == "—":
        default = []
    elif isinstance(LOCALE_OPTIONS[str(locale_options)], list):
        default = LOCALE_OPTIONS[str(locale_options)]
    elif callable(LOCALE_OPTIONS[str(locale_options)]):
        default = [option for option in LOCALE_OPTIONS[str(locale_options)]()]

    selection = st.multiselect(
        "Select languages",
        options=LOCALE_OPTIONS["All"],
        default=default,
        label_visibility="collapsed",
        key="locale-selection",
    )

    # Then how the data is going to be aggregate by timeframe.
    rolling_selection = st.selectbox(
        "Choose time aggregation", ["Daily", "Weekly", "Monthly"], index=0
    )
    rolling_label = {"Daily": 1, "Weekly": 7, "Monthly": 28}
    rolling = rolling_label[str(rolling_selection)]

    # And the last one being if the data have to be normalize or union.
    _, left, _, right, _ = st.columns((1, 2, 1, 2, 1))
    normalize = left.checkbox(
        "Normalize",
        key="locale-normalize",
        help="Normalize the metric by the total to get percents.",
    )
    union = right.checkbox(
        "Union",
        value=False,
        key="locale-union",
        help="Look at the usage of all languages together, they behaves as one single one.",
    )

# So with all being set, we can render the charts.
if selection == []:
    st.warning("You must choose a language first.")
else:
    if union:
        dataframe = session.sql(select_union_data(selection))
    else:
        dataframe = session.sql(select_locale_data(selection))

    # Bar chart
    description = "We count the number of daily active views that use a given language."

    sql_query = str(dataframe._plan.queries[0].sql)

    agreggated_data = group_and_agreaggate_data(
        session, dataframe.to_pandas(), normalize, rolling
    )

    line_chart = locale_line_chart(agreggated_data, normalize, union)

    data_chart_container(
        agreggated_data, "line_chart", description, sql_query, line_chart
    )

    # Heatmap chart
    if not union:
        polygon_heatmap_chart(session, agreggated_data, normalize)
