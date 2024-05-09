from datetime import date, datetime, timedelta
from matplotlib.colors import LinearSegmentedColormap
from pandas.io.formats.style import Styler
from typing import Tuple
import pandas as pd
import streamlit as st


def default_start(month: int) -> date:
    """
    Returns default start date, n months ago.
    """
    return (date.today() - timedelta(days=30 * month)).replace(day=1) - timedelta(
        days=1
    )


def default_end() -> date:
    """
    Returns default end date, last day of the current month.
    """
    return (date.today()).replace(day=1) - timedelta(days=1)


def select_cohort_data(
    table: str, start_date: date, end_date: date, timeframe: str
) -> str:
    """
    Returns the query that selects data, by its timeframe.
    It could be `MONTH` or `WEEK`, also filters by the given start and end date.
    """
    return f"""
                SELECT
                    COHORT_{timeframe},
                    ACTION_{timeframe},
                    NUM_USERS
                FROM 
                    {table}{timeframe}
                WHERE 
                    COHORT_{timeframe} >= '{start_date}'::DATE AND COHORT_{timeframe} <='{end_date}'::DATE
                ORDER BY 
                    1 DESC,
                    2 DESC;
            """


def select_power_curve_data(table: str, start_date: date, end_date: date) -> str:
    """
    Returns the query that selects data from `CORE_DEVOLOPER_ACTIVITY_BY_DAY`, `CLOUD_VIEWS_ACTIVITY_BY_DAY` or `CLOUD_DEVOLOPER_ACTIVITY_BY_DAY`.
    It filters based on the given start and end date.
    """
    return f"""
                WITH USER_NUM_DAYS_ACTIVE AS (
                    SELECT
                        USERNAME,
                        COUNT(DISTINCT(DAY_OF_USE)) as NUM_DAYS_ACTIVE
                    FROM
                        {table}
                    WHERE
                        DAY_OF_USE :: DATE BETWEEN '{format_date(start_date)}'
                        AND '{format_date(end_date)}'
                    GROUP BY
                        1
                )
                SELECT
                    NUM_DAYS_ACTIVE,
                    COUNT(DISTINCT USERNAME) as NUM_USERS
                FROM
                    USER_NUM_DAYS_ACTIVE
                GROUP BY
                    NUM_DAYS_ACTIVE
                ORDER BY
                    NUM_DAYS_ACTIVE ASC;
            """


def format_date(date: date) -> str:
    """
    Receives a date in the format `YYYY-MM-DD` and returns a string with `MM/DD/YYYY` format.
    """
    return datetime.strptime(str(date), "%Y-%m-%d").strftime("%m/%d/%Y")


def process_cohort_data(
    data: pd.DataFrame,
    color: LinearSegmentedColormap,
    timeframe: str = "month",
    percentages: bool = True,
) -> Tuple[pd.DataFrame, Styler]:
    """
    Process the raw data from `select_cohort_data` function and trasnformed into a styled and ordered heatmap.
    """
    starting_col = "COHORT_" + timeframe.upper()
    activity_col = "ACTION_" + timeframe.upper()
    numUsers_col = "NUM_USERS"

    # Convert all to datetimes
    data[starting_col] = pd.to_datetime(data[starting_col])
    data[activity_col] = pd.to_datetime(data[activity_col])

    # Pivot to extract the data
    data = data.pivot_table(
        values=numUsers_col, index=starting_col, columns=activity_col
    )

    # For each row, if the column date is greater than the column date, set the value to 0
    for i in range(len(data)):
        for j in range(len(data.columns)):
            if data.columns[j] > data.index[i]:
                # If value exists, skip, else set to 0
                if pd.isna(data.iloc[i, j]):
                    data.iloc[i, j] = 0

    # Remelt the data
    data = data.melt(
        var_name=activity_col, value_name=numUsers_col, ignore_index=False
    ).reset_index()

    # Get the number of week
    if timeframe == "week":
        data["DATE_NUM"] = (data[activity_col] - data[starting_col]).dt.days / 7
    else:
        data["DATE_NUM"] = (
            data[activity_col].dt.year - data[starting_col].dt.year
        ) * 12 + (data[activity_col].dt.month - data[starting_col].dt.month)

    # Repivot the data
    data = data.pivot_table(values=numUsers_col, index=starting_col, columns="DATE_NUM")

    # Rename to Week 1, Week 2 etc. or Month 1, Month 2 etc.
    data.columns = [timeframe.title() + " " + str(int(x) + 1) for x in data.columns]

    data.index.name = "COHORT_" + str(timeframe).upper()
    cohort_analysis_heatmap = data.fillna(-1).astype(int)

    # Improve the index to date strings
    cohort_analysis_heatmap.index = cohort_analysis_heatmap.index.strftime("%Y-%m-%d")

    # Get the max of each row pandas
    cohort_sizes = cohort_analysis_heatmap.max(axis=1)
    subset_cols = cohort_analysis_heatmap.columns

    # Apply percents
    if percentages:
        cohort_analysis_heatmap = cohort_analysis_heatmap.div(
            cohort_analysis_heatmap.max(axis=1), axis=0
        )

    # Insert the cohort sizes
    cohort_analysis_heatmap.insert(0, "Cohort Size", cohort_sizes)

    # Apply the color formatter
    def color_formatter(value):
        """Color formatter for the pandas dataframe"""
        if value < 0:
            return "color: white; background-color: white"
        else:
            return ""

    cohort_analysis_heatmap_styled = (
        cohort_analysis_heatmap.style.background_gradient(
            axis=1, subset=subset_cols, vmin=0, cmap=color
        )
        .format("{:.0%}" if percentages else None, subset=subset_cols)
        .format("{:,.0f}", subset=["Cohort Size"])
        .applymap(lambda x: color_formatter(x), subset=subset_cols)
    )

    return cohort_analysis_heatmap, cohort_analysis_heatmap_styled


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


def get_chart_color(start_point: str, end_point: str) -> LinearSegmentedColormap:
    """
    Gets a gradient of colormap.
    """
    return LinearSegmentedColormap.from_list(
        name="retention_colormap",
        colors=[(0, start_point), (1, end_point)],
    )
