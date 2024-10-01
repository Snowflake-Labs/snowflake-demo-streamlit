from snowflake.snowpark import Session
from typing import List
from utils.utils import (
    CONVERSATION_TOPIC,
    PENDING_NOTIFICATION,
    PENDING_NOTIFICATION_MESSAGE,
    USERNAME,
    get_formated_conversations,
)
import streamlit as st


def get_users(session: Session) -> List[str]:
    """
    Returns a list of users.
    """
    user_dataframe = session.table("USERS").select("USERNAME").to_pandas()
    users = user_dataframe["USERNAME"].to_list()
    return users


def get_cortex_services(session: Session) -> List[str]:
    """
    Retrieves the list of Cortex search services in the specified schema.

    Returns:
        List[str]: A list of Cortex search services in the schema, prefixed with 'SC_'.
    """

    services = session.sql("SHOW CORTEX SEARCH SERVICES IN SCHEMA").collect()

    return [f"SC_{service['name']}" for service in services]


def save_feedback(
    session: Session,
    model: str,
    category: str,
    score: int,
    comments: str,
    flagged: bool,
    reason: str,
) -> None:
    """
    Saves the feedback provided by the user.
    """
    session.sql(
        """
        INSERT INTO AI_FEEDBACK (
            USER,
            TOPIC,
            MODEL,
            CATEGORY,
            SCORE,
            COMMENTS,
            FLAGGED,
            REASON,
            CONVERSATION
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        [
            st.session_state[USERNAME],
            st.session_state[CONVERSATION_TOPIC],
            model,
            category,
            score,
            comments,
            flagged,
            reason,
            get_formated_conversations(model),
        ],
    ).collect()
    st.session_state[PENDING_NOTIFICATION] = True
    st.session_state[PENDING_NOTIFICATION_MESSAGE] = [
        "Feedback submitted successfully!",
        "📬",
    ]


def save_new_user(session: Session, username: str) -> None:
    """
    Saves the feedback provided by the user.
    """
    session.sql(
        """
        INSERT INTO USERS (
            USERNAME
        )
        VALUES(?);
        """,
        [username],
    ).collect()
