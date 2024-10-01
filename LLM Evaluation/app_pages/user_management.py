import streamlit as st
from snowflake.snowpark import Session
from ui.components import display_sidebar
from utils.utils import get_conversations_data

st.set_page_config(layout="centered")

session: Session = st.session_state["session"]


st.header("User Management")
st.write(
    """
    On this app page, you can quickly visualize the total number of users registered in the app.
    Additionally, you can see a breakdown of how much feedback each user has contributed,
    providing insights into user engagement and activity levels.
    """
)

conversations_data = get_conversations_data(session, user_filter=False)
conversation_by_user = conversations_data["USER"].value_counts().to_dict()

for user, count in conversation_by_user.items():
    st.write(f"**User: {user}**")
    st.write(f"Total feedback added by user: {count}")

display_sidebar(session)
