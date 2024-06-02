from components import (
    data_chart_container,
    date_picker,
    stars_growing_over_time_chart,
    top_starred_repositories_chart,
)
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
from utils import (
    get_pandas_dataframe,
    get_reduce_name_dictionary,
    stars_per_day_by_repository_query,
    top_starred_repositories_query,
)
import streamlit as st

session: Session = get_active_session()

st.title("GitHub Repositories Stars")
st.write(
    """
    Explore detailed metrics tracking the accumulation of stars across GitHub repositories, revealing trends and patterns in repository popularity over time.
    """
)

st.subheader("Top starred repositories")
with st.container(border=True):
    # Get data
    repos_dataframe = get_pandas_dataframe(session, top_starred_repositories_query())
    description = """
    This chart displays the top 20 GitHub repositories based on the number of stars they have received.
    The repositories are ranked from highest to lowest stars, providing an overview of the most popular repositories on GitHub. 
    """
    top_starred_chart = top_starred_repositories_chart(repos_dataframe)

    # Display the chart.
    data_chart_container(
        repos_dataframe,
        description,
        top_starred_chart,
        str(repos_dataframe.sql_query),
        "repository_chart",
    )

st.subheader("Repository Stars Over Time")
with st.container(border=True):
    # Create some columns to arrange the inputs.
    date_col, aggregation_col = st.columns(2)
    with date_col:
        start_date, end_date = date_picker()

    with aggregation_col:
        aggregation_period = str(
            st.selectbox(
                "Select weekly or monthly downloads", ("Daily", "Weekly", "Monthly"), 2
            )
        )

    # Get the names of the most starred repositories, then added into the select.
    repository_names = get_reduce_name_dictionary(repos_dataframe)

    selected_repos = st.multiselect(
        "Select repositories to add in the chart",
        repository_names.keys(),
        # By default, only the top 5 repositories will be selected.
        # But all the top 20 are avaliable to select.
        default=list(repository_names.keys())[:5],
    )

    # Get data to add in the chart.
    stars_dataframe = get_pandas_dataframe(
        session,
        stars_per_day_by_repository_query(
            [
                repository_names[key]
                for key in selected_repos
                if key in repository_names
            ],
            aggregation_period,
            start_date,
            end_date,
        ),
    )

    time_series_chart = stars_growing_over_time_chart(stars_dataframe)
    description = """
    This chart allows users to explore the trend of stars received by selected repositories over a specified time period.
    Users can filter repositories by start and end dates and choose from the top 20 repositories displayed in the first chart.
    Once configured, this chart illustrates how the number of stars has evolved over time for the selected repositories
    """

    # Display some cool charts.
    data_chart_container(
        stars_dataframe,
        description,
        time_series_chart,
        str(stars_dataframe.sql_query),
        "stars_chart",
    )
