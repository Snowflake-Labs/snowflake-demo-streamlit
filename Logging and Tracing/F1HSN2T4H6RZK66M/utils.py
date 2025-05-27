from typing import Dict, List
from snowflake.snowpark import Session
import altair as alt
import pandas as pd
import streamlit as st


def messages_table(session: Session, query: str, columns: Dict[str, str]) -> None:
    """
    Render a table showing all messages can be logs or traces sent by this app.
    """
    dataframe: pd.DataFrame = session.sql(query).to_pandas()
    dataframe = dataframe.rename(columns=columns)

    st.dataframe(dataframe, use_container_width=True)


def bar_messages_chart(
    session: Session, query: str, color_name: str, color_arr: List[str]
) -> None:
    """
    Create, then render a Bar chart displaying the ammount of messages sent by a user.
    """
    dataframe: pd.DataFrame = session.sql(query).to_pandas()
    chart = (
        alt.Chart(dataframe)
        .mark_bar(
            opacity=0.8,
            cornerRadiusTopLeft=2,
            cornerRadiusTopRight=2,
        )
        .encode(
            x=alt.X("USER:N", axis=alt.Axis(title="User", labelAngle=0)),
            y=alt.Y(
                "TOTAL:Q",
                title="Total messages",
            ),
            color=alt.Color(
                f"{color_name}:N",
                title=color_name.title(),
                scale=alt.Scale(range=color_arr),
            ),
        )
        .properties(height=400)
    )

    st.altair_chart(chart, use_container_width=True)


def delay_note() -> None:
    """
    Dsiplay a text about the delay between the button click and actually showing up in the table and chart.
    """
    st.caption(
        """
        **Note:**
        It can take several seconds for log or trace data emitted by handler code to be recorded in the event table. If you do not see results immediately, try refreshing in a few seconds.
        This delay can be up to two minutes.
        """
    )
