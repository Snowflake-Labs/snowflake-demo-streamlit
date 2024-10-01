import streamlit as st
from snowflake.snowpark import Session
from ui.components import display_sidebar
from ui.modals import display_export_conversations_modal
from utils.utils import USERNAME, get_conversation_json


st.set_page_config(layout="centered")

session: Session = st.session_state["session"]


st.header("My Account")
st.write(f"**Hi, {st.session_state[USERNAME]}!**")
st.subheader("Conversation History")

conversation_dict = get_conversation_json(session, export_to_json=False)

if len(conversation_dict) == 0:
    st.write("No conversations found.")
    st.stop()

selected_conversation = st.selectbox(
    "Select a conversation", conversation_dict.keys(), key="conversation_select"
)


with st.expander("**Conversation Details**", expanded=True):
    st.write("**Category:**")
    st.write(conversation_dict[selected_conversation]["CATEGORY"])
    st.write("**Score:**")
    st.write(conversation_dict[selected_conversation]["SCORE"])
    st.write("**Conversation:**")
    st.write(conversation_dict[selected_conversation]["CONVERSATION"])
    st.write("**Comments:**")
    st.write(conversation_dict[selected_conversation]["COMMENTS"])
    if conversation_dict[selected_conversation]["FLAGGED"]:
        st.write("**Flagged:**")
        st.write(conversation_dict[selected_conversation]["FLAGGED"])
    if conversation_dict[selected_conversation]["REASON"] != "":
        st.write("**Reason:**")
        st.write(conversation_dict[selected_conversation]["REASON"])


if st.button("Export Conversation", key="export_conversation_button"):
    display_export_conversations_modal(session)

display_sidebar(session)
