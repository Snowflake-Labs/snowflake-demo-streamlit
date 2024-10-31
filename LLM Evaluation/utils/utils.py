from snowflake.core import Root
from snowflake.cortex import Complete
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
from streamlit.delta_generator import DeltaGenerator
from typing import Dict, List
import pandas as pd
import streamlit as st
import time

MULTI_MODEL = "multi_model"
CHAT1_MODEL = "chat1_model"
CHAT1_MODEL_INDEX = "chat1_model_index"
CHAT2_MODEL = "chat2_model"
CHAT2_MODEL_INDEX = "chat2_model_index"
CHAT1_MESSAGES = "chat1_messages"
CHAT2_MESSAGES = "chat2_messages"
PENDING_NOTIFICATION = "pending_notification"
PENDING_NOTIFICATION_MESSAGE = "pending_notification_message"
IS_LOGGED_IN = "is_logged_in"
USERNAME = "username"
IS_ADMIN = "is_admin"
CONVERSATION_TOPIC = "conversation_topic"


def complete_gpt(session: Session, model: str, prompt: str) -> str:
    """
    Completes the given prompt using the GPT model.
    """
    completion_df = session.sql(
        "SELECT GPT_COMPLETION(?, ?);", [model, prompt]
    ).to_pandas()
    return completion_df.iloc[0, 0]


def get_complete_response(session: Session, model: str, prompt: str) -> str:
    """
    Returns the complete response based on the given model and prompt.
    """
    if model.startswith("gpt"):
        return complete_gpt(session, model, prompt)
    elif model.startswith("SC_"):
        return cortex_search_service(
            prompt=prompt,
            model=model.replace("SC_", ""),
            limit=1,
            column_name="DESCRIPTION",
            session=session,
        )
    else:
        return Complete(model, prompt, session=session)


def get_formated_conversations(model: str) -> str:
    """
    Returns a formatted string representation of the conversations.
    """
    conversation = ""
    if model == st.session_state[CHAT1_MODEL]:
        for index, message in enumerate(st.session_state[CHAT1_MESSAGES]):
            conversation += (
                f"{index} - {message['role'].title()}: {message['content']}\n"
            )
    else:
        for index, message in enumerate(st.session_state[CHAT2_MESSAGES]):
            conversation += (
                f"{index} - {message['role'].title()}: {message['content']}\n"
            )
    return conversation


def get_main_topic() -> None:
    """
    Returns the main topic of the conversation.
    """
    if (
        len(st.session_state[CHAT1_MESSAGES]) != 0
        and st.session_state[CONVERSATION_TOPIC] != ""
    ):
        return

    elif len(st.session_state[CHAT1_MESSAGES]) > 0:
        user_message = st.session_state[CHAT1_MESSAGES][-2]["content"]
        assistant_message = st.session_state[CHAT1_MESSAGES][-1]["content"]
        prompt = f"""Based on the following conversation,
        get the main topic in a maximun of four words but
        remove the phrase \'Main Topic:\' from your response.
        Conversation:\n\nUser: {user_message}\nAssistant: {assistant_message}"""
        topic = Complete("mixtral-8x7b", prompt, session=st.session_state["session"])
        st.session_state[CONVERSATION_TOPIC] = topic
        st.rerun()


def get_conversation_json(session: Session, export_to_json: bool) -> Dict[str, Dict]:
    """
    Returns a list of conversation history.
    """
    user_dataframe = (
        session.table("AI_FEEDBACK")
        .filter(col("USER") == st.session_state[USERNAME])
        .to_pandas()
    )
    if export_to_json:
        return user_dataframe.to_json(orient="index")
    else:
        conversations = user_dataframe.to_dict(orient="records")
        json_result = {
            f"{index + 1} - {record['TOPIC']}": record
            for index, record in enumerate(conversations)
        }
        return json_result


def initialize_session_state() -> None:
    """
    Initializes the session state variables if they don't exist.
    """
    if CHAT1_MODEL not in st.session_state:
        st.session_state[CHAT1_MODEL] = "mixtral-8x7b"
    if CHAT2_MODEL not in st.session_state:
        st.session_state[CHAT2_MODEL] = "snowflake-arctic"
    if CHAT1_MESSAGES not in st.session_state:
        st.session_state[CHAT1_MESSAGES] = []
    if CHAT2_MESSAGES not in st.session_state:
        st.session_state[CHAT2_MESSAGES] = []
    if PENDING_NOTIFICATION not in st.session_state:
        st.session_state[PENDING_NOTIFICATION] = False
    if PENDING_NOTIFICATION_MESSAGE not in st.session_state:
        st.session_state[PENDING_NOTIFICATION_MESSAGE] = []
    if IS_LOGGED_IN not in st.session_state:
        st.session_state[IS_LOGGED_IN] = False
    if USERNAME not in st.session_state:
        st.session_state[USERNAME] = ""
    if IS_ADMIN not in st.session_state:
        st.session_state[IS_ADMIN] = False
    if CONVERSATION_TOPIC not in st.session_state:
        st.session_state[CONVERSATION_TOPIC] = ""
    if MULTI_MODEL not in st.session_state:
        st.session_state[MULTI_MODEL] = False
    if CHAT1_MODEL_INDEX not in st.session_state:
        st.session_state[CHAT1_MODEL_INDEX] = 0
    if CHAT2_MODEL_INDEX not in st.session_state:
        st.session_state[CHAT2_MODEL_INDEX] = 1


def load_message_history(messages_list: List, container: DeltaGenerator) -> None:
    """
    Load message history to the specified container.
    """
    for message in st.session_state[messages_list]:
        with container.chat_message(message["role"]):
            st.markdown(message["content"])


def start_new_chat() -> None:
    """
    Start a new chat.
    """
    st.session_state[CHAT1_MODEL_INDEX] = 0
    st.session_state[CHAT2_MODEL_INDEX] = 1
    st.session_state[CHAT1_MESSAGES] = []
    st.session_state[CHAT2_MESSAGES] = []
    st.session_state[CONVERSATION_TOPIC] = ""
    st.session_state[PENDING_NOTIFICATION] = True
    st.session_state[PENDING_NOTIFICATION_MESSAGE] = [
        "New chat started successfully!",
        "📝",
    ]
    st.rerun()


def regenerate_message(session: Session) -> None:
    """
    Regenerate the last message.
    """
    last_user_message = st.session_state[CHAT1_MESSAGES][-2]

    with st.spinner("Regenerating message..."):
        time.sleep(0.6)
        new_message_chat1 = {
            "role": "assistant",
            "content": get_complete_response(
                session, st.session_state[CHAT1_MODEL], last_user_message["content"]
            ),
        }
        st.session_state[CHAT1_MESSAGES][-1] = new_message_chat1

    if st.session_state[MULTI_MODEL]:
        with st.spinner("Regenerating message..."):
            time.sleep(0.6)
            new_message_chat2 = {
                "role": "assistant",
                "content": get_complete_response(
                    session, st.session_state[CHAT2_MODEL], last_user_message["content"]
                ),
            }
            st.session_state[CHAT2_MESSAGES][-1] = new_message_chat2

    st.toast("Message regenerated successfully!", icon="🔄")


def get_conversations_data(session: Session, user_filter: bool) -> pd.DataFrame:
    """
    Retrieves conversations from the AI_FEEDBACK table.
    """
    if user_filter:
        user_dataframe = (
            session.table("AI_FEEDBACK")
            .filter(col("USER") == st.session_state[USERNAME])
            .to_pandas()
        )
    else:
        user_dataframe = session.table("AI_FEEDBACK").to_pandas()

    return user_dataframe


def get_column_config(dataframe: pd.DataFrame) -> Dict:
    """
    Format dataframe columns text in PascalCase style.
    """
    return {
        col: st.column_config.Column(col.replace("_", " ").title())
        for col in dataframe.columns
    }


def set_previous_model(
    options: List[str], previous_model: str, index: str, model: str
) -> None:
    """
    Sets the previous model selection in the session state and updates the selected model.
    """
    if previous_model in options:
        st.session_state[index] = options.index(previous_model)
    else:
        st.session_state[index] = 0

    selected_model = st.selectbox(
        "Select model",
        options,
        index=st.session_state[index],
        key=model,
    )

    st.session_state[index] = options.index(selected_model)


def create_connection() -> Session:
    """
    Creates a connection to the Snowflake database.
    """

    if "session" not in st.session_state:
        st.session_state["session"] = st.connection("snowflake").session()

    return st.session_state["session"]


def cortex_search_service(
    prompt: str, model: str, limit: int, column_name: str, session: Session
):
    """
    Searches for context documents using the Cortex Search Service.

    Args:
        prompt (str): The search prompt.
        model (str): The name of the model to use for the search.
        limit (int): The maximum number of results to return.
        column_name (str): The name of the column to retrieve from the search results.
        session (Session): The session object used to interact with the database.
    """
    root = Root(session)
    db = session.get_current_database()
    schema = session.get_current_schema()
    cortex_search_service = (
        root.databases[db].schemas[schema].cortex_search_services[model]
    )
    context_documents = cortex_search_service.search(prompt, [], limit=limit)
    return context_documents.results[0][column_name]
