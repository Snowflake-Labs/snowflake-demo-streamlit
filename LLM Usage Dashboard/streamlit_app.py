import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
import datetime

#############################################
#     FORMATTING
#############################################
st.set_page_config(layout="wide")
st.title("Snowflake LLM Usage App :snowflake:")
st.divider()

st.markdown("This app is developed to go off of the account usage schema in your Snowflake account. For detailed information please see the documentation page below.")
st.markdown(
    "https://docs.snowflake.com/en/sql-reference/account-usage#account-usage-views")

#############################################
#     DATE FILTER
#############################################
max_date = datetime.datetime.now()
min_date = datetime.datetime.now() - datetime.timedelta(days=365)

if 'starting' not in st.session_state:
    st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=30)

if 'ending' not in st.session_state:
    st.session_state.ending = max_date

st.markdown("Enter your desired date range (30 days on initial load):")
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

if col1.button('30 Days'):
    st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=30)
    st.session_state.ending = datetime.datetime.now()
if col2.button('60 Days'):
    st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=60)
    st.session_state.ending = datetime.datetime.now()
if col3.button('90 Days'):
    st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=90)
    st.session_state.ending = datetime.datetime.now()
if col4.button('180 Days'):
    st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=180)
    st.session_state.ending = datetime.datetime.now()
if col5.button('365 Days'):
    st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=365)
    st.session_state.ending = datetime.datetime.now()

s, e = st.date_input("", (st.session_state.starting,
                     st.session_state.ending), min_date, max_date)

st.divider()

session = get_active_session()
#############################################
#     Cards at Top
#############################################
# Credits Used Tile
st.markdown("### AI Services Overview")
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

# Column formatting and metrics - top level metric only
col1, col2, col3 = st.columns(3)
col1.metric("AI Services Credits Used", "{:,}".format(int(credits_used_tile)))

# Get Cortex Analyst Credits
cortex_analyst_credits = f"SELECT round(SUM(credits), 0) AS CORTEX_ANALYST_CREDITS, SUM(request_count) as number_messages FROM SNOWFLAKE.account_usage.CORTEX_ANALYST_USAGE_HISTORY where start_time between '{s}' and '{e}'"
cortex_analyst_df = session.sql(cortex_analyst_credits)
pandas_cortex_analyst_df = cortex_analyst_df.to_pandas()
num_ca_credits_tile = pandas_cortex_analyst_df.iloc[0].values[0]
num_ca_messages_tile = pandas_cortex_analyst_df.iloc[0].values[1]

# Document AI Credits
document_ai_credits_sql = f"SELECT ROUND(SUM(credits_used),2) as total_credits FROM SNOWFLAKE.account_usage.CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY WHERE start_time BETWEEN '{s}' AND '{e}'"
document_ai_df = session.sql(document_ai_credits_sql)
pandas_document_ai_df = document_ai_df.to_pandas()
document_ai_total = pandas_document_ai_df.iloc[0].values[0] if len(
    pandas_document_ai_df) > 0 and pandas_document_ai_df.iloc[0].values[0] is not None else 0

# Cortex Functions Total Credits
cortex_functions_total_sql = f"SELECT ROUND(SUM(token_credits),2) as total_credits FROM SNOWFLAKE.account_usage.CORTEX_FUNCTIONS_USAGE_HISTORY WHERE start_time BETWEEN '{s}' AND '{e}'"
cortex_functions_total_df = session.sql(cortex_functions_total_sql)
pandas_cortex_functions_total_df = cortex_functions_total_df.to_pandas()
cortex_functions_total = pandas_cortex_functions_total_df.iloc[0].values[0] if len(
    pandas_cortex_functions_total_df) > 0 and pandas_cortex_functions_total_df.iloc[0].values[0] is not None else 0

# AI Services Breakdown Metrics
st.markdown("### AI Services Breakdown")
col1, col2, col3 = st.columns(3)
col1.metric("Cortex Analyst Credits", "{:,}".format(int(num_ca_credits_tile)))
col2.metric("Document AI Credits", "{:,}".format(int(document_ai_total)))
col3.metric("Cortex Functions Credits",
            "{:,}".format(int(cortex_functions_total)))

# Create AI Services Breakdown DataFrame
ai_services_data = {
    'Service_Type': ['Cortex Analyst', 'Document AI', 'Cortex Functions'],
    'Credits': [num_ca_credits_tile, document_ai_total, cortex_functions_total]
}
ai_services_df = pd.DataFrame(ai_services_data)
# Filter out zero values for cleaner chart
ai_services_df = ai_services_df[ai_services_df['Credits'] > 0]

# Create AI Services breakdown chart using native streamlit
if not ai_services_df.empty:
    st.markdown("#### AI Services Credit Breakdown")
    # Set Service_Type as index for the chart
    ai_services_chart_df = ai_services_df.set_index('Service_Type')
    st.bar_chart(ai_services_chart_df['Credits'])

# Credits by Function Name (Bar Chart)
credits_by_function_sql = f"SELECT DISTINCT(function_name), ROUND(SUM(token_credits),2) as total_credits FROM SNOWFLAKE.account_usage.CORTEX_FUNCTIONS_USAGE_HISTORY WHERE start_time BETWEEN '{s}' AND '{e}' GROUP BY 1 ORDER BY 2 DESC"
credits_by_function_df = session.sql(credits_by_function_sql)
pandas_credits_by_function_df = credits_by_function_df.to_pandas()

# Create bar chart for function distribution using native streamlit
if not pandas_credits_by_function_df.empty:
    st.markdown("#### Credit Spend Distribution by Function Name")
    function_chart_df = pandas_credits_by_function_df.set_index(
        'FUNCTION_NAME')
    st.bar_chart(function_chart_df['TOTAL_CREDITS'])

#############################################
#     Credit Usage Total (Bar Chart)
#############################################

st.markdown("### LLM Inference Usage")
col1, col2 = st.columns(2)
col1.metric("Total # of Complete Credits",
            "{:,}".format(int(num_credits_tile)))
col2.metric("Total # of Complete Tokens", num_tokens_tile)

# Inference Credits Usage by Function, Model (Total)
total_credits_used_sql = f"select model_name,sum(token_credits) as total_credits_used, SUM(tokens) as TOTAL_TOKENS_USED from snowflake.account_usage.CORTEX_FUNCTIONS_USAGE_HISTORY where function_name = 'COMPLETE' and start_time between '{s}' and '{e}' group by 1 order by 2 desc limit 10 "
total_credits_used_df = session.sql(total_credits_used_sql)
pandas_credits_used_df = total_credits_used_df.to_pandas()

# Convert to a pandas df
total_tokens_used_df = session.sql(total_credits_used_sql)
pandas_tokens_used_df = total_tokens_used_df.to_pandas()

credits_by_warehouse_sql = f"SELECT warehouse_name,w.warehouse_id,  sum(token_credits) as cortex_complete_credits, sum(credits_used_compute) as total_compute_credits FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY as w JOIN SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY as c on c.warehouse_id = w.warehouse_id where c.start_time between '{s}' and '{e}' group by warehouse_name, w.warehouse_id order by 3 desc;"
credits_by_wh_df = session.sql(credits_by_warehouse_sql)
pandas_wh_df = credits_by_wh_df.to_pandas()

#############################################
#     Container 1: Credits & Jobs
#############################################

container1 = st.container()

with container1:
    # Third row: Bar Charts
    plot1, plot2, plot3 = st.columns(3)
    with plot1:
        st.markdown("##### Credits Used by Model")
        if not pandas_credits_used_df.empty:
            credits_model_chart = pandas_credits_used_df.set_index(
                'MODEL_NAME')
            st.bar_chart(credits_model_chart['TOTAL_CREDITS_USED'])

    with plot2:
        st.markdown("##### Tokens Used by Model")
        if not pandas_tokens_used_df.empty:
            tokens_model_chart = pandas_tokens_used_df.set_index('MODEL_NAME')
            st.bar_chart(tokens_model_chart['TOTAL_TOKENS_USED'])

    with plot3:
        st.markdown("##### Credits Used by Warehouse")
        if not pandas_wh_df.empty:
            wh_chart = pandas_wh_df.set_index('WAREHOUSE_NAME')
            st.bar_chart(wh_chart['CORTEX_COMPLETE_CREDITS'])

st.markdown("LLM & Compute Credits by WH")
credits_by_wh = st.dataframe(
    pandas_wh_df,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="multi-row",
)
st.markdown("Credits by Model")
credits_by_model = st.dataframe(
    pandas_credits_used_df,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="multi-row",
)

st.markdown("Credits by Function")
credits_by_function = st.dataframe(
    pandas_credits_by_function_df,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="multi-row",
)

st.markdown("Historical Cortex Queries")
all_cortex_functions = session.sql(
    f"select q.query_id, model_name, function_name, tokens, token_credits, query_text, user_name, role_name, total_elapsed_time from SNOWFLAKE.account_usage.CORTEX_FUNCTIONS_QUERY_USAGE_HISTORY as c join snowflake.account_usage.query_history as q on c.query_id = q.query_id where q.start_time between '{s}' and '{e}';")
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

ca_day_request = f"SELECT TO_DATE(cortex_analyst_usage_history.start_time) AS day,SUM(cortex_analyst_usage_history.request_count) AS total_request_count FROM SNOWFLAKE.account_usage.CORTEX_ANALYST_USAGE_HISTORY WHERE start_time BETWEEN '{s}' AND '{e}' GROUP BY day ORDER BY day"
ca_day_df = session.sql(ca_day_request)
pandas_day_df = ca_day_df.to_pandas()

num_ca_credits_tile = pandas_cortex_analyst_df.iloc[0].values[0]
num_ca_messages_tile = pandas_cortex_analyst_df.iloc[0].values[1]

col1, col2 = st.columns(2)
col1.metric("Total Cortex Analyst Credits", "{:,}".format(num_ca_credits_tile))
col2.metric("Total # of Cortex Analyst Messages",
            "{:,}".format(num_ca_messages_tile))

# Chart using native streamlit
st.markdown("#### Cortex Analyst Requests by Day")
if not pandas_day_df.empty:
    ca_chart_df = pandas_day_df.set_index('DAY')
    st.bar_chart(ca_chart_df['TOTAL_REQUEST_COUNT'])

#############################################
#     DOCUMENT PROCESSING
#############################################
st.markdown("### Document Processing")

# Document Processing Metrics
doc_processing_metrics_sql = f"""
SELECT 
    ROUND(SUM(credits_used),2) as total_credits,
    SUM(page_count) as total_pages,
    SUM(document_count) as total_documents
FROM SNOWFLAKE.account_usage.CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY 
WHERE start_time BETWEEN '{s}' AND '{e}'
"""
doc_processing_metrics_df = session.sql(doc_processing_metrics_sql)
pandas_doc_processing_metrics_df = doc_processing_metrics_df.to_pandas()

# Extract individual metrics
if len(pandas_doc_processing_metrics_df) > 0 and not pandas_doc_processing_metrics_df.empty:
    doc_credits_total = pandas_doc_processing_metrics_df.iloc[0]['TOTAL_CREDITS'] or 0
    doc_pages_total = pandas_doc_processing_metrics_df.iloc[0]['TOTAL_PAGES'] or 0
    doc_documents_total = pandas_doc_processing_metrics_df.iloc[0]['TOTAL_DOCUMENTS'] or 0
else:
    doc_credits_total = 0
    doc_pages_total = 0
    doc_documents_total = 0

# Document Processing Credits by Day
doc_credits_by_day_sql = f"""
SELECT 
    TO_DATE(start_time) AS day,
    ROUND(SUM(credits_used),2) AS daily_credits,
    SUM(page_count) as daily_pages,
    SUM(document_count) as daily_documents
FROM SNOWFLAKE.account_usage.CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY 
WHERE start_time BETWEEN '{s}' AND '{e}'
GROUP BY TO_DATE(start_time)
ORDER BY day
"""
doc_credits_by_day_df = session.sql(doc_credits_by_day_sql)
pandas_doc_credits_by_day_df = doc_credits_by_day_df.to_pandas()

# Display metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Document Processing Credits",
            "{:,}".format(float(doc_credits_total)))
col2.metric("Total Pages Processed", "{:,}".format(int(doc_pages_total)))
col3.metric("Total Documents Processed",
            "{:,}".format(int(doc_documents_total)))

# Create charts if we have data
if not pandas_doc_credits_by_day_df.empty:
    # Display charts using native streamlit
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Document Processing Credits by Day")
        doc_credits_chart = pandas_doc_credits_by_day_df.set_index('DAY')
        st.bar_chart(doc_credits_chart['DAILY_CREDITS'])
    with col2:
        st.markdown("#### Pages Processed by Day")
        doc_pages_chart = pandas_doc_credits_by_day_df.set_index('DAY')
        st.bar_chart(doc_pages_chart['DAILY_PAGES'])

    # Show data table
    st.markdown("#### Daily Document Processing Details")
    st.dataframe(
        pandas_doc_credits_by_day_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'DAY': st.column_config.DateColumn("Date"),
            'DAILY_CREDITS': st.column_config.NumberColumn("Credits", format="%.2f"),
            'DAILY_PAGES': st.column_config.NumberColumn("Pages", format="%d"),
            'DAILY_DOCUMENTS': st.column_config.NumberColumn("Documents", format="%d")
        }
    )
else:
    st.info("No document processing activity found for the selected date range.")

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

# Cortex Search Credits by Day
cortex_search_by_day_sql = f"""
SELECT 
    TO_DATE(start_time) AS day,
    ROUND(SUM(credits),2) AS daily_credits
FROM SNOWFLAKE.account_usage.CORTEX_SEARCH_SERVING_USAGE_HISTORY 
WHERE start_time BETWEEN '{s}' AND '{e}'
GROUP BY TO_DATE(start_time)
ORDER BY day
"""
cortex_search_by_day_df = session.sql(cortex_search_by_day_sql)
pandas_cortex_search_by_day_df = cortex_search_by_day_df.to_pandas()

# Create charts using native streamlit
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Cortex Search Credits by Service")
    if not pandas_cortex_search_service_df.empty:
        cs_service_chart = pandas_cortex_search_service_df.set_index(
            'SERVICE_NAME')
        st.bar_chart(cs_service_chart['TOTAL_CREDITS'])

with col2:
    st.markdown("#### Cortex Search Credits by Day")
    if not pandas_cortex_search_by_day_df.empty:
        cs_day_chart = pandas_cortex_search_by_day_df.set_index('DAY')
        st.bar_chart(cs_day_chart['DAILY_CREDITS'])
    else:
        st.info("No daily Cortex Search activity found for the selected date range.")

#############################################
#     FOOTER
#############################################
st.divider()
foot1, foot2 = st.columns([1, 1])

with foot1:
    st.markdown("Version 3.0")
with foot2:
    st.markdown("August 2025")
#
