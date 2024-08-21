from snowflake import telemetry
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
from utils import bar_messages_chart, delay_note, messages_table
import random
import streamlit as st
import time

session: Session = get_active_session()


def get_trace_messages_query() -> str:
    """
    Get data from the `EVENT TABLE` where the logs were created by this app.
    """
    return """
            SELECT
                TIMESTAMP,
                RESOURCE_ATTRIBUTES :"db.user" :: VARCHAR AS USER,
                RECORD_TYPE,
                RECORD_ATTRIBUTES
            FROM
                SAMPLE_EVENTS
            WHERE
                RECORD :"name" :: VARCHAR = 'tracing_some_data'
                OR RECORD_ATTRIBUTES :"loggin_demo.tracing" :: VARCHAR = 'begin_span'
            ORDER BY
                TIMESTAMP DESC;
            """


def get_messages_count_query() -> str:
    """
    Get the amount of messages created per user, per record type.
    """
    return """
            SELECT
                RESOURCE_ATTRIBUTES :"db.user" :: VARCHAR AS USER,
                RECORD_TYPE AS TYPE,
                COUNT(RECORD_ATTRIBUTES) AS TOTAL
            FROM
                SAMPLE_EVENTS
            WHERE
                RECORD :"name" :: VARCHAR = 'tracing_some_data'
                OR RECORD_ATTRIBUTES :"loggin_demo.tracing" :: VARCHAR = 'begin_span'
            GROUP BY
                USER,
                TYPE;
            """


def sleep_function() -> int:
    """
    Function that sleeps for a random period of time, between one and ten seconds.
    """
    random_time = random.randint(1, 10)
    time.sleep(random_time)
    return random_time


def trace_message() -> None:
    """
    Add a new trace message into the event table.
    """
    execution_time = sleep_function()
    telemetry.set_span_attribute("loggin_demo.tracing", "begin_span")
    telemetry.add_event(
        "tracing_some_data",
        {"function_name": "sleep_function", "execution_time": execution_time},
    )


st.header("Tracing")

st.write(
    """
    Trace events are a type of telemetry data (like log messages) that can capture when something has happened in the system or the application.
    Unlike log messages, trace events have a structured payload,
    which makes them a good choice for data analysis. For example,
    you can use trace events to capture some numbers that are calculated during the execution of your function,
    and analyze these numbers afterwards.

    Click on the following button to execute a function that sleeps for a random period of time, between one and ten seconds.
    When it finishes, it will register the event as a trace message, this can be accessed through the event table.
    """
)

if st.button("Add telemetry event", use_container_width=True):
    with st.spinner("Executing function..."):
        trace_message()
        st.toast("Succesfully log a trace message!", icon="✅")

delay_note()

with st.expander("**Show All Messages**"):
    messages_table(
        session,
        get_trace_messages_query(),
        {
            "TIMESTAMP": "Date",
            "USER": "User",
            "RECORD_TYPE": "Type",
            "RECORD_ATTRIBUTES": "Attributes",
        },
    )

bar_messages_chart(
    session,
    get_messages_count_query(),
    "TYPE",
    ["#ffcea9", "#fe9d52"],
)
