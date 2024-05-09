import altair as alt
import pandas as pd


def altair_line_chart(
    data: pd.DataFrame,
    y_title: str,
    y_axis_format: str = ".0f",
    line_color="blue",
    color_var="variable",
):
    """Plot a time series using Altair
    Args:
        data (pd.DataFrame): Original dataframe
        y_title (str): Title for y axis
        y_axis_format (str): Format for y axis
        line_color (str): Color for the line
        color_var (str): Column to use for color
        horizontal_dash_line (float): If set, this will add a dashed line to the chart
            and will be used as the maximum value for the y axis
    """

    # If the data is empty, return an empty chart
    if data.empty:
        return None

    data = data.copy()
    base = alt.Chart(data).mark_line(color=line_color, point=True)
    domain = [0, float(data["value"].max()) * 1.2]

    chart = base.encode(
        x=alt.X(f"yearmonthdate(date):O", axis=alt.Axis(title="Date")),
        y=alt.Y(
            "value",
            axis=alt.Axis(
                title=y_title,
                format=y_axis_format,
            ),
            scale=alt.Scale(domain=domain),
        ),
        color=alt.Color(color_var, title="Variable"),
    )

    return chart.configure_legend(orient="bottom").configure_point(size=20)
