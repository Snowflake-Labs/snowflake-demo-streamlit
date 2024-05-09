# Import python packages
import pandas as pd
import random
import streamlit as st
from snowflake.snowpark.context import get_active_session


def render_tile(query: str, column_config: dict, description: str):
    """Renders the tile with styled dataframe, raw data, description and download data tabs.

    Args:
        query (str): The query that will be executed in the Snowflake database and will be use as a dataframe.
        column_config (dict): Custom column format configuration.
        description (str): The description for the tile.
    """

    # Generate four tabs for the created tile
    t_dataframe, t_raw_data, t_sql, t_description, t_download_data = st.tabs(
        ["Dataframe", "Raw Data", "SQL", "Description", "Download Data"]
    )

    # Obtain dataframe from given query
    df = get_dataframe_from_raw_sql(query)

    with t_dataframe:
        # Generates a dataframe to be displayed as an interactive table with a specific column configuration
        st.dataframe(
            df, column_config=column_config, hide_index=True, use_container_width=True
        )

    with t_raw_data:
        # Raw dataframe visualization
        st.dataframe(df)

    with t_sql:
        st.code(query)

    with t_description:
        st.markdown(description)

    with t_download_data:
        st.download_button(
            label="Download data as .csv",
            data=df.to_csv(),
            file_name="data.csv",
            mime="text/csv",
        )


@st.cache_data
def get_dataframe_from_raw_sql(query: str) -> pd.DataFrame:
    """Executes the given query in the Snowflake database
    and converts the result to a pandas dataframe and changes
    the column names to be capitalized.

    Args:
        query (str): The query to be run against the database.

    Returns:
        pd.DataFrame: The query result as a pandas dataframe.
    """
    # Get active session to query the Snowflake database
    session = get_active_session()

    pandas_df = session.sql(query).to_pandas()
    pandas_df.columns = [column.title() for column in pandas_df.columns]

    return pandas_df


st.set_page_config(layout="wide")
st.title("Customers Engagement :balloon:")
st.write(
    """A dashboard app that visualizes customers engagement 
    with StreamingEdu, an awesome and fictional educational platform.

    """
)


col_m_1, col_m_2, col_m_3 = st.columns(3)

active_customers_count_df = get_dataframe_from_raw_sql(
    """SELECT COUNT(DISTINCT(customer)) AS count
FROM customers_engagement_db.customers_engagement_s.customer_engagement"""
)

project_type_count_df = get_dataframe_from_raw_sql(
    """SELECT count(distinct(f.value)) AS CountProjectTypes
FROM customers_engagement_db.customers_engagement_s.customer_engagement ce,
LATERAL FLATTEN(input => ce.project_types) f"""
)

active_projects_count_df = get_dataframe_from_raw_sql(
    """SELECT SUM(f.value::INT) AS TotalSum
FROM customers_engagement_db.customers_engagement_s.customer_engagement ce,
LATERAL FLATTEN(input => ce.number_active_project_type) f"""
)

col_m_1.metric("Active Customers", active_customers_count_df.iloc[0, 0])
col_m_2.metric("Project Types", project_type_count_df.iloc[0, 0])
col_m_3.metric("Active Projects", active_projects_count_df.iloc[0, 0])

st.subheader("Active Projects and Types")


CUSTOMER_ENGAGEMENT_TABLE_QUERY = """
SELECT customer, number_active_project_type, project_types
FROM customers_engagement_db.customers_engagement_s.customer_engagement
"""

df_column_config = {
    "Number_Active_Project_Type": st.column_config.LineChartColumn(
        "Active Projects",
        width="medium",
        y_min=0,
        y_max=100,
    ),
    "Project_Types": st.column_config.ListColumn(
        "Project Types",
        width="medium",
    ),
}

DESCRIPTION = "This tile shows the number of active projects and types per customer"

render_tile(
    query=CUSTOMER_ENGAGEMENT_TABLE_QUERY,
    column_config=df_column_config,
    description=DESCRIPTION,
)
