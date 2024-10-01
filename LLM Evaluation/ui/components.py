import time
from ui.modals import display_feedback_modal, display_login_modal
from utils.pages import Page, show_pages
from utils.queries import get_cortex_services
from snowflake.snowpark import Session
from streamlit.delta_generator import DeltaGenerator
from typing import Dict, List
from utils.utils import (
    CHAT1_MESSAGES,
    IS_ADMIN,
    IS_LOGGED_IN,
    PENDING_NOTIFICATION,
    PENDING_NOTIFICATION_MESSAGE,
    USERNAME,
    get_complete_response,
    regenerate_message,
    set_previous_model,
    start_new_chat,
)
import pandas as pd
import altair as alt
import streamlit as st


def display_logout_button() -> None:
    """
    Displays a logout button in the sidebar popover.

    When the logout button is clicked, it sets the session state variables
    `IS_LOGGED_IN`, `IS_ADMIN`, and `USERNAME` to False, False, and an empty
    string, respectively.
    """
    with st.sidebar.popover("⚙️ Settings", use_container_width=True):
        st.write(f"Hello, you are logged in as **{st.session_state[USERNAME]}**")
        if st.button("Logout", use_container_width=True, key="sidebar_logout_button"):
            st.session_state[IS_LOGGED_IN] = False
            st.session_state[IS_ADMIN] = False
            st.session_state[USERNAME] = ""
            st.rerun()


def display_message_actions(session: Session) -> None:
    """
    Displays the message actions in the Streamlit app.

    This function creates three buttons for different message actions:
    - Regenerate: Calls the `regenerate_message` function when clicked.
    - New chat: Calls the `start_new_chat` function when clicked.
    - Feedback: Calls the `add_feedback` function when clicked.
    """
    if len(st.session_state[CHAT1_MESSAGES]) == 0:
        return
    regenerate_col, new_chat_col, feedback_col = st.columns(3)

    if regenerate_col.button("Regenerate 🔄", use_container_width=True):
        regenerate_message(session)

    if new_chat_col.button("New chat 📝", use_container_width=True):
        start_new_chat()

    if feedback_col.button("Feedback 📬", use_container_width=True):
        display_feedback_modal(session)


def display_message_list(
    session: Session,
    question: str,
    model: str,
    message_list: List,
    container: DeltaGenerator,
) -> None:
    """
    Display a chat message in the specified container.
    """
    with container.chat_message("user"):
        st.markdown(question)
        st.session_state[message_list].append({"role": "user", "content": question})

    with container.chat_message("assistant"):
        question = question.replace("'", "")
        with st.spinner("Assistant thinking..."):
            time.sleep(0.6)
            response = get_complete_response(
                session=session, model=st.session_state[model], prompt=question
            )
            st.markdown(response)
            st.session_state[message_list].append(
                {"role": "assistant", "content": response}
            )


def display_model_selection(session: Session, model: str, index: str) -> None:
    """
    Display a popover with a selectbox to choose a model.
    """
    st.write(f"#### Chat with  {st.session_state[model]}")
    with st.popover(
        f"Configure {st.session_state[model]}",
        use_container_width=True,
    ):
        ai_provider = st.selectbox(
            "Select AI Provider",
            ["Cortex", "Cortex Search", "OpenAI"],
            key=f"ai_provider_{model}",
        )
        previous_model = st.session_state[model]

        if model in st.session_state:
            del st.session_state[model]

        if ai_provider == "Cortex":
            options = [
                "mixtral-8x7b",
                "snowflake-arctic",
                "llama3-8b",
                "llama3-70b",
                "llama2-70b-chat",
                "gemma-7b",
            ]
            set_previous_model(options, previous_model, index, model)
        elif ai_provider == "Cortex Search":
            options = get_cortex_services(session)
            set_previous_model(options, previous_model, index, model)
        else:
            options = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
            set_previous_model(options, previous_model, index, model)


def display_pending_notification() -> None:
    """
    Displays a pending notification if there is one in the session state.

    The function checks if the `PENDING_NOTIFICATION` flag is set to True in the session state.
    If it is, it displays a toast notification using the message and icon stored in the session state.
    After displaying the notification, it sets the `PENDING_NOTIFICATION` flag to False.
    """
    if st.session_state[PENDING_NOTIFICATION]:
        st.toast(
            st.session_state[PENDING_NOTIFICATION_MESSAGE][0],
            icon=st.session_state[PENDING_NOTIFICATION_MESSAGE][1],
        )
        st.session_state[PENDING_NOTIFICATION] = False


def display_sidebar(session: Session) -> None:
    """
    Creates the sidebar based on the user's login status and role.
    """
    if st.session_state[IS_LOGGED_IN] and st.session_state[IS_ADMIN]:
        show_pages(
            [
                Page("streamlit_app.py", "Chat", "💬"),
                Page("./app_pages/account.py", "Account", "👤"),
                Page(
                    "./app_pages/conversation_analysis.py",
                    "Conversation Analysis",
                    "📊",
                ),
                Page("./app_pages/user_management.py", "User Management", "🛠️"),
            ]
        )
    elif st.session_state[IS_LOGGED_IN]:
        show_pages(
            [
                Page("streamlit_app.py", "Chat", "💬"),
                Page("./app_pages/account.py", "Account", "👤"),
            ]
        )
    else:
        if st.sidebar.button("Login", key="sidebar_login", use_container_width=True):
            display_login_modal(session)

        show_pages(
            [
                Page("streamlit_app.py", "Chat", "💬"),
            ]
        )


def get_conversations_chart(data: pd.DataFrame) -> Dict:
    """
    Displays a chart of the conversation data.
    """
    chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X("MODEL", title="Model"),
            y=alt.Y("count()", title="Number of Conversations"),
            color=alt.Color("CATEGORY", title="Category"),
            tooltip=[
                alt.Tooltip("MODEL", title="Model:"),
                alt.Tooltip("CATEGORY", title="Category:"),
                alt.Tooltip("count()", title="Number of Conversations:"),
            ],
        )
        .properties(height=400)
        .add_params(alt.selection_point(name="group"))
    )
    return st.altair_chart(chart, use_container_width=True, on_select="rerun")
