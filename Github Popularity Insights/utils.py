from snowflake.snowpark import Session
from typing import Dict, List
import pandas as pd
import streamlit as st


def top_starred_repositories_query() -> str:
    """
    Get top 20 starred repositories information.
    """
    return """
            WITH STARS_SUM AS (
                SELECT
                    REPO_ID,
                    SUM(STARS.COUNT) AS SUM
                FROM
                    CYBERSYN_GITHUB_ARCHIVE.CYBERSYN.GITHUB_STARS AS STARS
                GROUP BY
                    REPO_ID
            ),
            REPOS_WITH_STARS AS (
                SELECT
                    REPOS.REPO_ID,
                    REPOS.REPO_NAME,
                    SUM(STARS_SUM.SUM) AS STARS_COUNT
                FROM
                    CYBERSYN_GITHUB_ARCHIVE.CYBERSYN.GITHUB_REPOS REPOS
                    JOIN STARS_SUM ON STARS_SUM.REPO_ID = REPOS.REPO_ID
                GROUP BY
                    REPOS.REPO_ID,
                    REPOS.REPO_NAME
            ),
            UNIQUE_TOP_ID_WITH_STARS AS (
                SELECT
                    DISTINCT REPO_ID,
                    STARS_COUNT
                FROM
                    REPOS_WITH_STARS
                ORDER BY
                    STARS_COUNT DESC
                LIMIT
                    20
            ),
            UNIQUE_TOP_ID_WITH_DATE AS (
                SELECT
                    REPOS.REPO_ID,
                    MAX(REPOS.LAST_SEEN) AS LAST_SEEN
                FROM
                    UNIQUE_TOP_ID_WITH_STARS
                    JOIN CYBERSYN_GITHUB_ARCHIVE.CYBERSYN.GITHUB_REPOS REPOS ON UNIQUE_TOP_ID_WITH_STARS.REPO_ID = REPOS.REPO_ID
                GROUP BY
                    REPOS.REPO_ID
            )
            SELECT
                REPOS.REPO_NAME AS NAME,
                UNIQUE_TOP_ID_WITH_STARS.STARS_COUNT AS STARS_COUNT
            FROM
                UNIQUE_TOP_ID_WITH_DATE
                JOIN CYBERSYN_GITHUB_ARCHIVE.CYBERSYN.GITHUB_REPOS REPOS ON UNIQUE_TOP_ID_WITH_DATE.REPO_ID = REPOS.REPO_ID
                JOIN UNIQUE_TOP_ID_WITH_STARS ON UNIQUE_TOP_ID_WITH_DATE.REPO_ID = UNIQUE_TOP_ID_WITH_STARS.REPO_ID
            WHERE
                UNIQUE_TOP_ID_WITH_DATE.LAST_SEEN = REPOS.LAST_SEEN
            ORDER BY
                UNIQUE_TOP_ID_WITH_STARS.STARS_COUNT DESC;
            """


def stars_per_day_by_repository_query(
    repos_names: List[str], aggregate_by: str, start_date: str, end_date: str
) -> str:
    """
    Get stars per day, week or month within a time range for a specific repository.
    """
    if aggregate_by == "Daily":
        aggregate_by = "day"
    elif aggregate_by == "Weekly":
        aggregate_by = "week"
    else:
        aggregate_by = "month"
    return f"""
            WITH ID_NAME AS (
                SELECT
                    REPO_ID AS ID,
                    REPOS.REPO_NAME AS NAME
                FROM
                    CYBERSYN_GITHUB_ARCHIVE.CYBERSYN.GITHUB_REPOS AS REPOS
                WHERE
                    REPO_NAME IN (
                        '{"','".join(repos_names)}'
                    )
            ),
            ACCUMULATIVE_SUM AS (
                SELECT
                    DATE_TRUNC('{aggregate_by}', STARS.DATE) AS STARS_DATE,
                    NAME,
                    SUM(SUM(STARS.COUNT)) OVER (
                        PARTITION BY NAME
                        ORDER BY
                            STARS_DATE
                    ) AS STARS_COUNT,
                FROM
                    CYBERSYN_GITHUB_ARCHIVE.CYBERSYN.GITHUB_STARS AS STARS
                    JOIN ID_NAME
                WHERE
                    STARS.REPO_ID = ID_NAME.ID
                GROUP BY
                    STARS_DATE,
                    NAME
                ORDER BY
                    STARS_DATE DESC
            )
            SELECT
                STARS_DATE,
                NAME,
                STARS_COUNT
            FROM
                ACCUMULATIVE_SUM
            WHERE
                STARS_DATE BETWEEN '{start_date}'
                AND '{end_date}';
            """


def get_column_config(df: pd.DataFrame) -> Dict[str, any]:
    """
    Format dataframe columns text in PascalCase style, also format the repository link.
    """
    general_config = {
        col: st.column_config.Column(col.replace("_", " ").title())
        for col in df.columns
    }

    link_config = {
        # The text of the links will look like this https://github.com/account/repo1,
        # so with this regex, the dataframe will only display 'repo1'
        "NAME": st.column_config.LinkColumn("Name", display_text="/([^/]+)$")
    }

    general_config.update(link_config)
    return general_config


def get_pandas_dataframe(session: Session, query: str) -> pd.DataFrame:
    """
    Using a Snowpark Session get data from Snowflake and trasformed into a Pandas Dataframe.
    """
    dataframe = session.sql(query)
    sql_query = dataframe._plan.queries[0].sql
    pandas_dataframe = dataframe.to_pandas()
    pandas_dataframe.sql_query = sql_query
    return pandas_dataframe


def get_reduce_name_dictionary(dataframe: pd.DataFrame) -> Dict[str, str]:
    """
    Returns a simplified version of the repository name column in a dictionary form. (Example: account1/repo1 -> repo1)
    """
    repository_names = dataframe["NAME"].to_list()
    repo_dictionary = {}
    for name in repository_names:
        repo_dictionary[name.split("/")[1]] = name
    return repo_dictionary


def get_simplified_name_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a simplified version of the repository name column in the same dataframe (Example: account1/repo1 -> repo1)
    """
    df = dataframe.copy(deep=True)
    df["NAME"] = df["NAME"].str.split("/").str[-1]
    return df
