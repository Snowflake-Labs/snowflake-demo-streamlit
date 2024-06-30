from typing import List
from snowflake.cortex import Complete

import streamlit as st

st.set_page_config(layout="wide")

CHAT_MODEL_COMPONENT_NAME = "chat_model_component_0"
CHAT_MODEL_COMPONENT_NAME_1 = "chat_model_component_1"
CHAT_HISTORY_M = "chat_history_m_0"
CHAT_HISTORY_M_1 = "chat_history_m_1"


def get_cortex_answer_add_response_to_container(
    messages_container: st.delta_generator.DeltaGenerator,
    inquiry: str,
    model_name: str,
    chat_history_session_key: str,
) -> str:
    """Asks cortex a question with the provided inquiry and adds it to the container.

    Args:
        messages_container (st.delta_generator.DeltaGenerator): The container where
            the response is going to be added.
        inquiry (str): The inquiry to be asked to the IA model.
        model_name (str): The model name to be used.
        chat_history_session_key (str): The session's chat history key.

    Returns:
        str: The cortex response as a string.
    """
    with messages_container.chat_message("assistant"):
        with st.spinner(f"{model_name} thinking..."):
            cortex_response = Complete(
                model_name,
                get_context_prompt(st.session_state[chat_history_session_key], inquiry),
            )
            st.markdown(cortex_response)
    return cortex_response


def append_question_response_chat_history(
    inquiry: str, ia_model_response, ia_model_response_1
) -> None:
    """Appends question and model responses to chat history
        stored in session variable.

    Args:
        inquiry (str): The question to be asked to both IA models.
        ia_model_response (_type_): First IA model response.
        ia_model_response_1 (_type_): Second IA model reponse.
    """
    st.session_state[CHAT_HISTORY_M].append({"role": "user", "content": inquiry})
    st.session_state[CHAT_HISTORY_M_1].append({"role": "user", "content": inquiry})
    st.session_state[CHAT_HISTORY_M].append(
        {"role": "assistant", "content": ia_model_response}
    )
    st.session_state[CHAT_HISTORY_M_1].append(
        {"role": "assistant", "content": ia_model_response_1}
    )


def add_message_to_container(
    messages_container: st.delta_generator.DeltaGenerator, message_obj: dict
) -> None:
    """Add message to container.

    Args:
        messages_container (st.delta_generator.DeltaGenerator): The container
            where the message is going to be added.
        message_obj (dict): The message object.
    """
    with messages_container.chat_message(message_obj["role"]):
        st.markdown(message_obj["content"])


def load_message_history_to_container(
    messages_container: st.delta_generator.DeltaGenerator, msg_session_key: str
) -> None:
    """Loads chat history into specified container.

    Args:
        messages_container (st.delta_generator.DeltaGenerator): The container
            where the chat is going to be loaded.
        msg_session_key (str): The chat history session key.
    """
    for message_obj in st.session_state[msg_session_key]:
        add_message_to_container(messages_container, message_obj)


def get_context_prompt(chat_history: List, inquiry: str) -> str:
    """Gets context for asked inquiry.

    Args:
        chat_history (str): The chat history as a list.
        inquiry (str): The question to be asked to the IA.

    Returns:
        str: _description_
    """
    f_chat_history = []
    for chat_entry in chat_history:
        f_chat_history.append(chat_entry["content"])

    return f"""
        You offer a chat experience considering the information included in the CHAT HISTORY
        provided between <chat_history> and </chat_history> tags.
        When answering the question contained between <question> and </question> tags
        be concise. 

        Do not mention the CHAT HISTORY used in your answer.
        
        <chat_history>
        {f_chat_history}
        </chat_history>
        <question>  
        {inquiry}
        </question>
        Answer: 
    """


def model_sel_container(component_key: str, selected_model_index: int = 0) -> None:
    """Renders model selector commponent. Where a chat model can be selected.

    Args:
        component_key (str): Key as a string that will be assigned to the select component.
        selected_model_index (int, optional): Selected model's index. Defaults to 0.
    """
    st.session_state[f"{component_key}_previous_value"] = st.selectbox(
        "Select your model:",
        (
            "mixtral-8x7b",
            "snowflake-arctic",
            "mistral-large",
            "llama3-8b",
            "llama3-70b",
            "reka-flash",
            "mistral-7b",
            "llama2-70b-chat",
            "gemma-7b",
        ),
        index=selected_model_index,
        key=component_key,
    )
    st.session_state[f"m_{component_key}"] = st.container(height=495)


if CHAT_HISTORY_M not in st.session_state:
    st.session_state[CHAT_HISTORY_M] = []
if CHAT_HISTORY_M_1 not in st.session_state:
    st.session_state[CHAT_HISTORY_M_1] = []

st.header("IAModel Analyzer :balloon:")
st.write(
    """
        IAModel Analyzer is an application that provides a side by side 
        comparison of the features, performance, and capabilities 
        of different chat models.
    """
)
if st.button("Reset Chat Histories"):
    st.session_state[CHAT_HISTORY_M] = []
    st.session_state[CHAT_HISTORY_M_1] = []
col_chat_model_0, col_chat_model_1 = st.columns(2)
with col_chat_model_0:
    model_sel_container(CHAT_MODEL_COMPONENT_NAME, 0)

with col_chat_model_1:
    model_sel_container(CHAT_MODEL_COMPONENT_NAME_1, 1)

if (
    st.session_state[CHAT_MODEL_COMPONENT_NAME]
    == st.session_state[CHAT_MODEL_COMPONENT_NAME_1]
):
    st.error("Please select different chat models!")
    st.stop()

messages_container_0 = st.session_state.m_chat_model_component_0
messages_container_1 = st.session_state.m_chat_model_component_1

load_message_history_to_container(messages_container_0, CHAT_HISTORY_M)
load_message_history_to_container(messages_container_1, CHAT_HISTORY_M_1)


if question := st.chat_input("Your message"):
    st.session_state.message_sent = True
    add_message_to_container(
        messages_container_0, {"role": "user", "content": question}
    )
    add_message_to_container(
        messages_container_1, {"role": "user", "content": question}
    )
    model_0_response = get_cortex_answer_add_response_to_container(
        messages_container_0,
        question,
        st.session_state.chat_model_component_0,
        CHAT_HISTORY_M,
    )
    model_1_response = get_cortex_answer_add_response_to_container(
        messages_container_1,
        question,
        st.session_state.chat_model_component_1,
        CHAT_HISTORY_M_1,
    )

    append_question_response_chat_history(question, model_0_response, model_1_response)
