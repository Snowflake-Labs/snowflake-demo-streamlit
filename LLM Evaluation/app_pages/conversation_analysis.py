from ui.components import display_sidebar, get_conversations_chart
from snowflake.snowpark import Session
from utils.utils import get_column_config, get_conversations_data
import streamlit as st


st.set_page_config(layout="centered")

session: Session = st.session_state["session"]


st.header("Conversation Analysis")
st.write(
    """
    On this app page, you can visualize conversations where feedback has been provided.
    The interactive chart allow you to filter and refine the data displayed in the table below,
    enabling a more detailed analysis of user feedback and conversation trends.
    """
)
user_filter = st.toggle(
    "Display only current user's conversations", value=False, key="user_filter"
)

conversations_data = get_conversations_data(session, user_filter=user_filter)

st.subheader("Conversations Chart")
chart_info = get_conversations_chart(conversations_data)


if chart_info.selection.group:
    category = chart_info.selection.group[0]["CATEGORY"]
    model = chart_info.selection.group[0]["MODEL"]

    conversations_data = conversations_data[
        (conversations_data["CATEGORY"] == category)
        & (conversations_data["MODEL"] == model)
    ]


st.subheader("Conversations Data")
selected_row = st.dataframe(
    conversations_data,
    use_container_width=True,
    column_config=get_column_config(conversations_data),
    on_select="rerun",
    selection_mode="single-row",
    key="conversations_data",
)

if selected_row.selection.rows:
    with st.expander("**Additional Details**", expanded=True):
        selected_row_dict = (
            conversations_data.copy()
            .reset_index()
            .loc[selected_row.selection.rows[0]]
            .to_dict()
        )
        for key, value in selected_row_dict.items():
            st.write(f"**{str(key).title()}**:")
            st.write(str(value))

display_sidebar(session)
