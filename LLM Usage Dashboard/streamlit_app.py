# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
from snowflake.snowpark.window import Window
from snowflake.ml.registry import Registry
import plotly.express as px
import datetime
import json

#############################################
#     FORMATTING
#############################################
# set to wide format
st.set_page_config(layout="wide")

# Write directly to the app
st.title("Snowflake LLM Usage App :snowflake:")
st.divider()

# Sub heading info
st.markdown("This app is developed to go off of the account usage schema in your Snowflake account. For detailed information please see the documentation page below.")
st.markdown(
    "https://docs.snowflake.com/en/sql-reference/account-usage#account-usage-views")

#############################################
#     DATE FILTER
#############################################
max_date = datetime.datetime.now()
min_date = datetime.datetime.now() - datetime.timedelta(days=365)
this_year = max_date.year
jan_1 = datetime.date(this_year, 1, 1)
dec_31 = datetime.date(this_year, 12, 31)


if 'starting' not in st.session_state:
    st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=30)

if 'ending' not in st.session_state:
    st.session_state.ending = max_date


st.markdown("Enter your desired date range (30 days on initial load):")

# Column for Date Picker Buttons
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

with col1:
    if st.button('30 Days'):
        st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=30)
        st.session_state.ending = datetime.datetime.now()
with col2:
    if st.button('60 Days'):
        st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=60)
        st.session_state.ending = datetime.datetime.now()
with col3:
    if st.button('90 Days'):
        st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=90)
        st.session_state.ending = datetime.datetime.now()
with col4:
    if st.button('180 Days'):
        st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=180)
        st.session_state.ending = datetime.datetime.now()
with col5:
    if st.button('365 Days'):
        st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=365)
        st.session_state.ending = datetime.datetime.now()

# Date Input
date_input_filter = st.date_input(
    "",
    (st.session_state.starting, st.session_state.ending),
    min_date,
    max_date,
)

# Start and End Date (s = start, e = end)
s, e = date_input_filter

st.divider()

# Get the current credentials
session = get_active_session()
credits_used_df = session.sql

#############################################
#     Cards at Top
#############################################
# Credits Used Tile
st.markdown("### LLM Inference Usage")
credits_used_sql = f"select round(sum(credits_used),0) as total_credits from snowflake.account_usage.metering_history where start_time between '{s}' and '{e}' and SERVICE_TYPE = 'AI_SERVICES'"
credits_used_df = session.sql(credits_used_sql)
pandas_credits_used_df = credits_used_df.to_pandas()
# Final Value
credits_used_tile = pandas_credits_used_df.iloc[0].values

# Total LLM INFERENCE
num_jobs_sql = f"SELECT round(SUM(token_credits), 0) AS LLM_INFERENCE_CREDITS, SUM(tokens) as LLM_INFERENCE_TOKENS FROM SNOWFLAKE.account_usage.CORTEX_FUNCTIONS_USAGE_HISTORY where function_name = 'COMPLETE' and start_time between '{s}' and '{e}'"
num_jobs_df = session.sql(num_jobs_sql)
pandas_num_jobs_df = num_jobs_df.to_pandas()
# Final Value
num_credits_tile = pandas_num_jobs_df.iloc[0].values[0]
num_tokens_tile = pandas_num_jobs_df.iloc[0].values[1]

# # Current Storage
# current_storage_sql = f"select round(avg(storage_bytes + stage_bytes + failsafe_bytes) / power(1024, 4),2) as billable_tb from snowflake.account_usage.storage_usage where USAGE_DATE = current_date() -1;"
# current_storage_df = session.sql(current_storage_sql)
# pandas_current_storage_df = current_storage_df.to_pandas()
# #Final Value
# current_storage_tile = pandas_current_storage_df.iloc[0].values

# Column formatting and metrics of header 3 metrics
col1, col2, col3 = st.columns(3)
col1.metric("AI Services Credits Used", "{:,}".format(int(credits_used_tile)))
col2.metric("Total # of Complete Credits",
            "{:,}".format(int(num_credits_tile)))
col3.metric("Total # of Complete Tokens", num_tokens_tile)

cortex_analyst_credits = f"SELECT round(SUM(credits), 0) AS CORTEX_ANALYST_CREDITS, SUM(request_count) as number_messages FROM SNOWFLAKE.account_usage.CORTEX_ANALYST_USAGE_HISTORY where start_time between '{s}' and '{e}'"
cortex_analyst_df = session.sql(cortex_analyst_credits)
pandas_cortex_analyst_df = cortex_analyst_df.to_pandas()

num_ca_credits_tile = pandas_cortex_analyst_df.iloc[0].values[0]
num_ca_messages_tile = pandas_cortex_analyst_df.iloc[0].values[1]
st.markdown("### LLM Inference Usage")
col1, col2 = st.columns(2)


#############################################
#     Credit Usage Total (Bar Chart)
#############################################

# Inference Credits Usage by Function, Model (Total)
total_credits_used_sql = f"select model_name,sum(token_credits) as total_credits_used, SUM(tokens) as TOTAL_TOKENS_USED from snowflake.account_usage.CORTEX_FUNCTIONS_USAGE_HISTORY where function_name = 'COMPLETE' and start_time between '{s}' and '{e}' group by 1 order by 2 desc limit 10 "
total_credits_used_df = session.sql(total_credits_used_sql)
pandas_credits_used_df = total_credits_used_df.to_pandas()

# #Chart
fig_credits_used = px.bar(pandas_credits_used_df, x='TOTAL_CREDITS_USED',
                          y='MODEL_NAME', orientation='h', title="Credits Used by Model")
fig_credits_used.update_traces(marker_color='green')

# Convert to a pandas df
# pandas_total_tokens_used_df = pandas_credits_used_df
total_tokens_used_df = session.sql(total_credits_used_sql)
pandas_tokens_used_df = total_tokens_used_df.to_pandas()

# Chart

fig_tokens_used = px.bar(pandas_tokens_used_df, x='TOTAL_TOKENS_USED',
                         y='MODEL_NAME', orientation='h', title="Tokens Used by Model")
fig_tokens_used.update_traces(marker_color='purple')

credits_by_warehouse_sql = f"SELECT warehouse_name,w.warehouse_id,  sum(token_credits) as cortex_complete_credits, sum(credits_used_compute) as total_compute_credits FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY as w JOIN SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY as c on c.warehouse_id = w.warehouse_id where function_name = 'COMPLETE' and c.start_time between '{s}' and '{e}' group by warehouse_name, w.warehouse_id order by 3 desc;"
credits_by_wh_df = session.sql(credits_by_warehouse_sql)
pandas_wh_df = credits_by_wh_df.to_pandas()

fig_wh_used = px.bar(pandas_wh_df, x='CORTEX_COMPLETE_CREDITS',
                     y='WAREHOUSE_NAME', orientation='h', title="Credits Used by Warehouse")
fig_wh_used.update_traces(marker_color='green')


#############################################
#     Container 1: Credits & Jobs
#############################################

container1 = st.container()

with container1:
    plot1, plot2, plot3 = st.columns(3)
    with plot1:
        st.plotly_chart(fig_credits_used, use_container_width=True)
    with plot2:
        st.plotly_chart(fig_tokens_used, use_container_width=True)
    with plot3:
        st.plotly_chart(fig_wh_used, use_container_width=True)
st.markdown("LLM & Compute Credits by WH")
credits_by_wh = st.dataframe(
    pandas_wh_df,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="multi-row",
)
st.markdown("Credits by Model")
credits_by_wh = st.dataframe(
    pandas_credits_used_df,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="multi-row",
)

st.markdown("Historical Cortex Queries")
all_cortex_functions = session.sql(
    f"select q.query_id, model_name, tokens, token_credits, query_text, user_name, role_name, total_elapsed_time from SNOWFLAKE.account_usage.CORTEX_FUNCTIONS_QUERY_USAGE_HISTORY as c join snowflake.account_usage.query_history as q on c.query_id = q.query_id where q.start_time between '{s}' and '{e}';")
all_cortex_functions_df = all_cortex_functions.to_pandas()

user_filter = st.multiselect(
    "Select Users", options=all_cortex_functions_df['USER_NAME'].unique().tolist(), default=all_cortex_functions_df['USER_NAME'].unique().tolist()
)

model_filter = st.multiselect(
    "Select Models", options=all_cortex_functions_df['MODEL_NAME'].unique().tolist(), default=all_cortex_functions_df['MODEL_NAME'].unique().tolist()
)
filtered_df_model = all_cortex_functions_df[all_cortex_functions_df['MODEL_NAME'].isin(
    model_filter)]
filtered_df_user = filtered_df_model[filtered_df_model['USER_NAME'].isin(
    user_filter)]
st.dataframe(filtered_df_user)

#############################################
#     CORTEX ANALYST
#############################################
st.markdown("### Cortex Analyst ")
cortex_analyst_credits = f"SELECT round(SUM(credits), 0) AS CORTEX_ANALYST_CREDITS, SUM(request_count) as number_messages FROM SNOWFLAKE.account_usage.CORTEX_ANALYST_USAGE_HISTORY where start_time between '{s}' and '{e}'"
cortex_analyst_df = session.sql(cortex_analyst_credits)
pandas_cortex_analyst_df = cortex_analyst_df.to_pandas()

ca_day_request = f"SELECT TO_DATE(cortex_analyst_usage_history.start_time) AS day,SUM(cortex_analyst_usage_history.request_count) AS total_request_count FROM SNOWFLAKE.account_usage.CORTEX_ANALYST_USAGE_HISTORY GROUP BY day ORDER BY day"
ca_day_df = session.sql(ca_day_request)
pandas_day_df = ca_day_df.to_pandas()

num_ca_credits_tile = pandas_cortex_analyst_df.iloc[0].values[0]
num_ca_messages_tile = pandas_cortex_analyst_df.iloc[0].values[1]

col1, col2 = st.columns(2)
col1.metric("Total Cortex Analyst Credits", "{:,}".format(num_ca_credits_tile))
col2.metric("Total # of Cortex Analyst Messages",
            "{:,}".format(num_ca_messages_tile))

# #Chart
fig_credits_used_ca = px.bar(
    pandas_day_df, y='TOTAL_REQUEST_COUNT', x='DAY', title="Requests by Day")
fig_credits_used_ca.update_traces(marker_color='green')

# Display the bar chart
st.plotly_chart(fig_credits_used_ca, use_container_width=True)

#############################################
#     CORTEX SEARCH
#############################################
st.markdown("### Cortex Search ")
cortex_search_serving_credits = f"SELECT round(sum(credits),2) AS CORTEX_SEARCH_CREDITS FROM SNOWFLAKE.account_usage.CORTEX_SEARCH_SERVING_USAGE_HISTORY where start_time between '{s}' and '{e}'"
cortex_search_df = session.sql(cortex_search_serving_credits)
pandas_cortex_search_df = cortex_search_df.to_pandas()

cortex_search_by_service = f"select service_name, sum(credits) as total_credits from SNOWFLAKE.account_usage.CORTEX_SEARCH_SERVING_USAGE_HISTORY where start_time between '{s}' and '{e}' GROUP BY service_name"
cortex_search_by_service_df = session.sql(cortex_search_by_service)
pandas_cortex_search_service_df = cortex_search_by_service_df.to_pandas()

num_cs_credits_tile = pandas_cortex_search_df.iloc[0].values[0]


st.metric("Total Cortex Search Serving Credits",
          "{:,}".format(num_cs_credits_tile))

# #Chart

fig_credits_used_cs = px.bar(pandas_cortex_search_service_df, x='TOTAL_CREDITS',
                             y='SERVICE_NAME', orientation='h', title="Credits Used by Service")
fig_credits_used_cs.update_traces(marker_color='green')
st.plotly_chart(fig_credits_used_cs, use_container_width=True)


#############################################
#     FOOTER
#############################################
st.divider()
foot1, foot2 = st.columns([1, 1])


with foot1:
    st.markdown("Version 1.0")
with foot2:
    st.markdown("March 2025")
