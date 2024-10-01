from snowflake.snowpark import Session
from utils.queries import get_users, save_feedback, save_new_user
from utils.utils import (
    CHAT1_MODEL,
    CHAT2_MODEL,
    CONVERSATION_TOPIC,
    IS_ADMIN,
    IS_LOGGED_IN,
    MULTI_MODEL,
    USERNAME,
    get_conversation_json,
)
import streamlit as st


@st.experimental_dialog("Export Conversations")
def display_export_conversations_modal(session: Session) -> None:
    """
    Displays a modal to export conversation history.
    """
    conversations = get_conversation_json(session, export_to_json=True)
    st.caption("Highlight and copy the output from here:")
    st.code(conversations)
    st.caption("Or download as a .json:")
    st.download_button(
        label="Download Conversations",
        data=conversations,
        file_name="conversations.json",
        mime="application/json",
    )


@st.experimental_dialog("Login")
def display_login_modal(session: Session) -> None:
    """
    Displays a login modal for selecting a user and logging in.
    """
    selected_user = st.selectbox("Select a user", get_users(session))
    new_user = st.text_input("New user", help="Enter a new username.")
    is_admin = st.checkbox(
        "Admin", help="Check if the user is an admin.", key="admin_checkbox"
    )
    if st.button("Login", key="login_button", use_container_width=True):
        if new_user:
            st.session_state[IS_LOGGED_IN] = True
            st.session_state[USERNAME] = new_user
            st.session_state[IS_ADMIN] = is_admin
            save_new_user(session, new_user)
        elif selected_user:
            st.session_state[IS_LOGGED_IN] = True
            st.session_state[IS_ADMIN] = is_admin
            st.session_state[USERNAME] = selected_user
        else:
            st.error("Please select a user or enter a new username.")
        st.rerun()


@st.experimental_dialog("Add Feedback")
def display_feedback_modal(session: Session) -> None:
    """
    Displays a form for users to provide feedback.

    The function prompts the user to select a category, provide a quality score,
    enter comments, and optionally flag the message. If the user clicks the
    "Submit" button, the feedback is saved using the `save_feedback` function.
    """
    selected_model = st.session_state[CHAT1_MODEL]
    if st.session_state[MULTI_MODEL]:
        selected_model = st.radio(
            "Which model response are you providing feedback on?",
            options=[st.session_state[CHAT1_MODEL], st.session_state[CHAT2_MODEL]],
            key="model_radio",
        )

    category = st.selectbox(
        "Category", ["Technical", "Personal Advice", "Other"], key="category_select"
    )
    if category == "Other":
        category = st.text_input(
            "Custom Category", help="Enter your custom category.", key="custom_category"
        )

    score = st.slider(
        "Quality score:",
        0,
        10,
        step=1,
        help="""Enter a score on the quality score. 7-8 indicates a person knowledgeable in the
                topic would be satisfied with the responses. Less than 5 indicates responses
                that are actively incorrect, anti-helpful and/or harmful.
                """,
        key="score_slider",
    )
    comments = st.text_input(
        "Comments", help="Enter any comments you have.", key="comments_input"
    )
    flagged = st.checkbox(
        "Flagged",
        help="Check if the message should be flagged.",
        key="flagged_checkbox",
    )
    reason = ""
    if flagged:
        reason = st.text_input(
            "Reason",
            help="Enter the reason for flagging the message.",
            key="reason_input",
        )

    if st.button("Enter"):
        if st.session_state[USERNAME] == "":
            st.error("Please log in to submit feedback.")
        elif st.session_state[CONVERSATION_TOPIC] == "":
            st.error("Please start a conversation to submit feedback.")
        elif category and score and comments:
            save_feedback(
                session=session,
                model=selected_model,
                category=category,
                score=score,
                comments=comments,
                flagged=flagged,
                reason=reason,
            )
            st.rerun()
        else:
            st.error("Please fill in all the required fields.")
