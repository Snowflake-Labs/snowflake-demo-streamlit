from ui.components import (
    display_logout_button,
    display_sidebar,
    display_message_list,
    display_message_actions,
    display_model_selection,
    display_pending_notification,
)
from snowflake.snowpark import Session
from utils.utils import (
    CHAT1_MESSAGES,
    CHAT1_MODEL,
    CHAT1_MODEL_INDEX,
    CHAT2_MESSAGES,
    CHAT2_MODEL,
    CHAT2_MODEL_INDEX,
    CONVERSATION_TOPIC,
    IS_LOGGED_IN,
    MULTI_MODEL,
    create_connection,
    get_main_topic,
    initialize_session_state,
    load_message_history,
)
import streamlit as st

st.set_page_config(layout="wide")


session: Session = create_connection()


initialize_session_state()
display_sidebar(session)

if st.session_state[IS_LOGGED_IN]:
    display_logout_button()

if st.session_state[CONVERSATION_TOPIC] != "":
    st.header(st.session_state[CONVERSATION_TOPIC])
else:
    st.header("Chat with models")
st.write(
    """
    Engage in conversations with various AI models, save your interactions,
    and provide feedback on the responses.
    Additionally, you can enable the multi-model feature to chat with two AI models simultaneously,
    enhancing your experience by comparing their answers in real-time.
    """
)

st.toggle("Multi-model", key=MULTI_MODEL)


columns_num = 1
if st.session_state[MULTI_MODEL]:
    columns_num = 2


messages_container = st.container()
columns = messages_container.columns(columns_num)


with columns[0]:
    display_model_selection(session=session, model=CHAT1_MODEL, index=CHAT1_MODEL_INDEX)
    chat1_container = st.container(border=True, height=440)
    load_message_history(CHAT1_MESSAGES, chat1_container)

if st.session_state[MULTI_MODEL]:
    with columns[1]:
        display_model_selection(
            session=session, model=CHAT2_MODEL, index=CHAT2_MODEL_INDEX
        )
        chat2_container = st.container(border=True, height=440)
        load_message_history(CHAT2_MESSAGES, chat2_container)

if question := st.chat_input("What do you want to know about your documents?"):
    with columns[0]:
        with chat1_container:
            display_message_list(
                session=session,
                question=question,
                model=CHAT1_MODEL,
                message_list=CHAT1_MESSAGES,
                container=chat1_container,
            )

    if st.session_state[MULTI_MODEL]:
        with columns[1]:
            with chat2_container:
                display_message_list(
                    session=session,
                    question=question,
                    model=CHAT2_MODEL,
                    message_list=CHAT2_MESSAGES,
                    container=chat2_container,
                )

get_main_topic()
display_message_actions(session)
display_pending_notification()
