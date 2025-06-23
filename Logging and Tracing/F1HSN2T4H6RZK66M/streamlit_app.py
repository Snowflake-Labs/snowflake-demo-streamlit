from pages import Page, show_pages
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
from utils import bar_messages_chart, delay_note, messages_table
import logging
import streamlit as st

st.set_page_config(layout="centered")


session: Session = get_active_session()
logger = logging.getLogger("app_logger")


def get_log_messages_query() -> str:
    """
    Get data from the `EVENT TABLE` where the logs were created by this app.
    """
    return """
            SELECT
                TIMESTAMP,
                RECORD:"severity_text"::VARCHAR AS SEVERITY,
                RESOURCE_ATTRIBUTES:"db.user"::VARCHAR AS USER,
                VALUE::VARCHAR AS VALUE
            FROM
                SAMPLEDATABASE.LOGGING_AND_TRACING.SAMPLE_EVENTS
            WHERE
                SCOPE:"name" = 'app_logger'
            ORDER BY
                TIMESTAMP DESC;
            """


def get_messages_count_query() -> str:
    """
    Get the ammount of messages created by using this app.
    """
    return """
            SELECT
                RESOURCE_ATTRIBUTES:"db.user"::VARCHAR AS USER,
                RECORD:"severity_text"::VARCHAR AS SEVERITY,
                COUNT(SEVERITY) AS TOTAL
            FROM
                SAMPLEDATABASE.LOGGING_AND_TRACING.SAMPLE_EVENTS
            WHERE
                SCOPE:"name" = 'app_logger'
            GROUP BY
                USER,
                SEVERITY
            ORDER BY
                USER DESC;
            """


def log_message(should_throw: bool) -> str:
    """
    Simple function that raise an exeption whenever `should_throw` parameter is true, it logs an error.
    Otherwise log an info message.
    """
    try:
        if not should_throw:
            logger.info("Logging an info message through Stremlit App.")
            return "SUCCESS"
        else:
            raise Exception("Something went wrong.")
    except Exception as e:
        logger.error(
            "Logging an error message through Stremlit App: %s",
            e,
        )
        return "ERROR"


st.header("Logging")

st.write(
    """
    You can log messages clicking on any of the following buttons, the success button will log an info messages and the other one will register an error message.
    """
)

success_col, error_col = st.columns(2)

with success_col:
    if st.button("Sucess", type="primary", use_container_width=True):
        log_message(False)
        st.success("Succesfully log an info message!", icon="✅")
with error_col:
    if st.button("Error", use_container_width=True):
        log_message(True)
        st.success("Succesfully log an error message!", icon="❎")

delay_note()

with st.expander("**Show All Messages**"):
    messages_table(
        session,
        get_log_messages_query(),
        {
            "TIMESTAMP": "Date",
            "SEVERITY": "Severity",
            "USER": "User",
            "VALUE": "Value",
        },
    )

bar_messages_chart(
    session,
    get_messages_count_query(),
    "SEVERITY",
    ["#9fcbec", "#dddddd"],
)


# Renders the sidebar with all the pages available in the app ('App Performance' and 'App Users').
show_pages(
    [
        Page("streamlit_app.py", "Logging", "🗄️"),
        Page("tracing.py", "Tracing", "🔍"),
    ]
)