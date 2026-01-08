
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
import datetime
import math

#############################################
#     HELPER FUNCTIONS
#############################################
def safe_number(value, default=0):
    """Safely convert a value to a number, handling None and NaN."""
    if value is None:
        return default
    try:
        # Handle pandas NA
        if pd.isna(value):
            return default
        # Handle float NaN
        if isinstance(value, float) and math.isnan(value):
            return default
        return value
    except (TypeError, ValueError):
        return default

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
min_date = datetime.datetime.now() - datetime.timedelta(days=31)

if 'starting' not in st.session_state:
    st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=3)

if 'ending' not in st.session_state:
    st.session_state.ending = max_date

st.markdown("Enter your desired date range (7 days on initial load):")
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

if col1.button('1 Days'):
    st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=1)
    st.session_state.ending = datetime.datetime.now()
if col2.button('3 Days'):
    st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=3)
    st.session_state.ending = datetime.datetime.now()
if col3.button('7 Days'):
    st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=7)
    st.session_state.ending = datetime.datetime.now()
if col4.button('14 Days'):
    st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=14)
    st.session_state.ending = datetime.datetime.now()
if col5.button('31 Days'):
    st.session_state.starting = datetime.datetime.now() - datetime.timedelta(days=31)
    st.session_state.ending = datetime.datetime.now()

s, e = st.date_input("", (st.session_state.starting,
                     st.session_state.ending), min_date, max_date)

st.divider()

session = get_active_session()
#############################################
#     Cards at Top
#############################################
# Credits Used Tile - using METERING_DAILY_HISTORY for faster daily rollups
st.markdown("### AI Services Overview")
credits_used_sql = f"""
SELECT ROUND(SUM(credits_used), 0) AS total_credits 
FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY 
WHERE usage_date >= '{s}'::DATE 
  AND usage_date < DATEADD(day, 1, '{e}'::DATE)
  AND SERVICE_TYPE = 'AI_SERVICES'
"""
credits_used_df = session.sql(credits_used_sql)
pandas_credits_used_df = credits_used_df.to_pandas()
# Final Value - handle None/NaN values
credits_used_tile = safe_number(pandas_credits_used_df.iloc[0].values[0]) if len(pandas_credits_used_df) > 0 else 0

# Total LLM INFERENCE
num_jobs_sql = f"""
SELECT ROUND(SUM(token_credits), 0) AS LLM_INFERENCE_CREDITS, SUM(tokens) AS LLM_INFERENCE_TOKENS 
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY 
WHERE function_name IN ('COMPLETE', 'AI_COMPLETE') 
  AND usage_time >= TO_TIMESTAMP_NTZ('{s}') 
  AND usage_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
"""
num_jobs_df = session.sql(num_jobs_sql)
pandas_num_jobs_df = num_jobs_df.to_pandas()
# Final Value - handle None/NaN values
num_credits_tile = safe_number(pandas_num_jobs_df.iloc[0].values[0]) if len(pandas_num_jobs_df) > 0 else 0
num_tokens_tile = safe_number(pandas_num_jobs_df.iloc[0].values[1]) if len(pandas_num_jobs_df) > 0 else 0

# Column formatting and metrics - top level metric only
col1, col2, col3 = st.columns(3)
col1.metric("AI Services Credits Used", "{:,}".format(int(safe_number(credits_used_tile))))

# Get Cortex Analyst Credits
cortex_analyst_credits = f"""
SELECT ROUND(SUM(credits), 0) AS CORTEX_ANALYST_CREDITS, SUM(request_count) AS number_messages 
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY 
WHERE start_time >= TO_TIMESTAMP_NTZ('{s}') 
  AND start_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
"""
cortex_analyst_df = session.sql(cortex_analyst_credits)
pandas_cortex_analyst_df = cortex_analyst_df.to_pandas()
num_ca_credits_tile = safe_number(pandas_cortex_analyst_df.iloc[0].values[0]) if len(pandas_cortex_analyst_df) > 0 else 0
num_ca_messages_tile = safe_number(pandas_cortex_analyst_df.iloc[0].values[1]) if len(pandas_cortex_analyst_df) > 0 else 0

# Document AI Credits - get all metrics in one query (reused later in Document Processing section)
document_ai_credits_sql = f"""
SELECT 
    ROUND(SUM(credits_used), 2) AS total_credits,
    SUM(page_count) AS total_pages,
    SUM(document_count) AS total_documents
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY 
WHERE start_time >= TO_TIMESTAMP_NTZ('{s}') 
  AND start_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
"""
document_ai_df = session.sql(document_ai_credits_sql)
pandas_document_ai_df = document_ai_df.to_pandas()
document_ai_total = safe_number(pandas_document_ai_df.iloc[0]['TOTAL_CREDITS']) if len(pandas_document_ai_df) > 0 else 0
doc_pages_total = safe_number(pandas_document_ai_df.iloc[0]['TOTAL_PAGES']) if len(pandas_document_ai_df) > 0 else 0
doc_documents_total = safe_number(pandas_document_ai_df.iloc[0]['TOTAL_DOCUMENTS']) if len(pandas_document_ai_df) > 0 else 0

# Cortex AI SQL Total Credits
cortex_aisql_total_sql = f"""
SELECT ROUND(SUM(token_credits), 2) AS total_credits 
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY 
WHERE usage_time >= TO_TIMESTAMP_NTZ('{s}') 
  AND usage_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
"""
cortex_aisql_total_df = session.sql(cortex_aisql_total_sql)
pandas_cortex_aisql_total_df = cortex_aisql_total_df.to_pandas()
cortex_aisql_total = safe_number(pandas_cortex_aisql_total_df.iloc[0].values[0]) if len(pandas_cortex_aisql_total_df) > 0 else 0

# AI Services Breakdown Metrics
st.markdown("### AI Services Breakdown")
col1, col2, col3 = st.columns(3)
col1.metric("Cortex Analyst Credits", "{:,}".format(int(safe_number(num_ca_credits_tile))))
col2.metric("Document AI Credits", "{:,}".format(int(safe_number(document_ai_total))))
col3.metric("Cortex AI SQL Credits",
            "{:,}".format(int(safe_number(cortex_aisql_total))))

# Create AI Services Breakdown DataFrame
ai_services_data = {
    'Service_Type': ['Cortex Analyst', 'Document AI', 'Cortex AI SQL'],
    'Credits': [safe_number(num_ca_credits_tile), safe_number(document_ai_total), safe_number(cortex_aisql_total)]
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
credits_by_function_sql = f"""
SELECT DISTINCT(function_name), ROUND(SUM(token_credits), 2) AS total_credits 
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY 
WHERE usage_time >= TO_TIMESTAMP_NTZ('{s}') 
  AND usage_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
GROUP BY 1 
ORDER BY 2 DESC
"""
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
            "{:,}".format(int(safe_number(num_credits_tile))))
col2.metric("Total # of Complete Tokens", "{:,}".format(int(safe_number(num_tokens_tile))))

# Inference Credits Usage by Function, Model (Total)
total_credits_used_sql = f"""
SELECT model_name, SUM(token_credits) AS total_credits_used, SUM(tokens) AS TOTAL_TOKENS_USED 
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY 
WHERE function_name IN ('COMPLETE', 'AI_COMPLETE') 
  AND usage_time >= TO_TIMESTAMP_NTZ('{s}') 
  AND usage_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
GROUP BY 1 
ORDER BY 2 DESC 
LIMIT 10
"""
total_credits_used_df = session.sql(total_credits_used_sql)
pandas_credits_used_df = total_credits_used_df.to_pandas()
# Reuse same dataframe for tokens chart (was running duplicate query)
pandas_tokens_used_df = pandas_credits_used_df

credits_by_warehouse_sql = f"""
SELECT 
    w.warehouse_name,
    c.warehouse_id,
    c.cortex_complete_credits,
    w.total_compute_credits
FROM (
    SELECT warehouse_id, SUM(token_credits) AS cortex_complete_credits 
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY 
    WHERE usage_time >= TO_TIMESTAMP_NTZ('{s}') 
      AND usage_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
    GROUP BY warehouse_id
) AS c
LEFT JOIN (
    SELECT warehouse_id, warehouse_name, SUM(credits_used_compute) AS total_compute_credits 
    FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
    WHERE start_time >= TO_TIMESTAMP_NTZ('{s}') 
      AND start_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
    GROUP BY warehouse_id, warehouse_name
) AS w ON c.warehouse_id = w.warehouse_id
ORDER BY c.cortex_complete_credits DESC
"""
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

# st.markdown("Historical Cortex AI SQL Queries")
# all_cortex_aisql_sql = f"""
# SELECT 
#     c.usage_time,
#     c.query_id, 
#     c.model_name, 
#     c.function_name, 
#     c.tokens, 
#     c.token_credits,
#     c.tokens_granular,
#     c.token_credits_granular,
#     c.query_tag,
#     q.query_text, 
#     q.user_name, 
#     q.role_name, 
#     q.total_elapsed_time 
# FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY AS c 
# JOIN SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY AS q ON c.query_id = q.query_id 
# WHERE c.usage_time >= TO_TIMESTAMP_NTZ('{s}') 
#   AND c.usage_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
# ORDER BY c.usage_time DESC
# LIMIT 500
# """
# all_cortex_aisql = session.sql(all_cortex_aisql_sql)
# all_cortex_aisql_df = all_cortex_aisql.to_pandas()

# if not all_cortex_aisql_df.empty:
#     user_filter = st.multiselect(
#         "Select Users", options=all_cortex_aisql_df['USER_NAME'].unique().tolist(), default=all_cortex_aisql_df['USER_NAME'].unique().tolist()
#     )

#     model_filter = st.multiselect(
#         "Select Models", options=all_cortex_aisql_df['MODEL_NAME'].unique().tolist(), default=all_cortex_aisql_df['MODEL_NAME'].unique().tolist()
#     )
#     filtered_df_model = all_cortex_aisql_df[all_cortex_aisql_df['MODEL_NAME'].isin(
#         model_filter)]
#     filtered_df_user = filtered_df_model[filtered_df_model['USER_NAME'].isin(
#         user_filter)]
#     st.dataframe(filtered_df_user)
# else:
#     st.info("No Cortex AI SQL query history found for the selected date range.")

#############################################
#     CORTEX ANALYST
#############################################
st.markdown("### Cortex Analyst ")
# Reuse num_ca_credits_tile and num_ca_messages_tile from earlier (removed duplicate query)

ca_day_request = f"""
SELECT TO_DATE(start_time) AS day, SUM(request_count) AS total_request_count 
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY 
WHERE start_time >= TO_TIMESTAMP_NTZ('{s}') 
  AND start_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
GROUP BY day 
ORDER BY day
"""
ca_day_df = session.sql(ca_day_request)
pandas_day_df = ca_day_df.to_pandas()

col1, col2 = st.columns(2)
col1.metric("Total Cortex Analyst Credits", "{:,}".format(int(safe_number(num_ca_credits_tile))))
col2.metric("Total # of Cortex Analyst Messages",
            "{:,}".format(int(safe_number(num_ca_messages_tile))))

# Chart using native streamlit
st.markdown("#### Cortex Analyst Requests by Day")
if not pandas_day_df.empty:
    ca_chart_df = pandas_day_df.set_index('DAY')
    st.bar_chart(ca_chart_df['TOTAL_REQUEST_COUNT'])

#############################################
#     DOCUMENT PROCESSING
#############################################
st.markdown("### Document Processing")
# Reuse document_ai_total, doc_pages_total, doc_documents_total from earlier query (removed duplicate)

# Document Processing Credits by Day
doc_credits_by_day_sql = f"""
SELECT 
    TO_DATE(start_time) AS day,
    ROUND(SUM(credits_used), 2) AS daily_credits,
    SUM(page_count) AS daily_pages,
    SUM(document_count) AS daily_documents
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY 
WHERE start_time >= TO_TIMESTAMP_NTZ('{s}') 
  AND start_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
GROUP BY TO_DATE(start_time)
ORDER BY day
"""
doc_credits_by_day_df = session.sql(doc_credits_by_day_sql)
pandas_doc_credits_by_day_df = doc_credits_by_day_df.to_pandas()

# Display metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Document Processing Credits",
            "{:,.2f}".format(float(safe_number(document_ai_total))))
col2.metric("Total Pages Processed", "{:,}".format(int(safe_number(doc_pages_total))))
col3.metric("Total Documents Processed",
            "{:,}".format(int(safe_number(doc_documents_total))))

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
cortex_search_serving_credits = f"""
SELECT ROUND(SUM(credits), 2) AS CORTEX_SEARCH_CREDITS 
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_SERVING_USAGE_HISTORY 
WHERE start_time >= TO_TIMESTAMP_NTZ('{s}') 
  AND start_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
"""
cortex_search_df = session.sql(cortex_search_serving_credits)
pandas_cortex_search_df = cortex_search_df.to_pandas()

cortex_search_by_service = f"""
SELECT service_name, SUM(credits) AS total_credits 
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_SERVING_USAGE_HISTORY 
WHERE start_time >= TO_TIMESTAMP_NTZ('{s}') 
  AND start_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
GROUP BY service_name
"""
cortex_search_by_service_df = session.sql(cortex_search_by_service)
pandas_cortex_search_service_df = cortex_search_by_service_df.to_pandas()

num_cs_credits_tile = safe_number(pandas_cortex_search_df.iloc[0].values[0]) if len(pandas_cortex_search_df) > 0 else 0

st.metric("Total Cortex Search Serving Credits",
          "{:,.2f}".format(float(safe_number(num_cs_credits_tile))))

# Cortex Search Credits by Day
cortex_search_by_day_sql = f"""
SELECT 
    TO_DATE(start_time) AS day,
    ROUND(SUM(credits), 2) AS daily_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_SERVING_USAGE_HISTORY 
WHERE start_time >= TO_TIMESTAMP_NTZ('{s}') 
  AND start_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
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

#
#############################################
#     CORTEX AGENTS
#############################################
st.markdown("### Cortex Agents")

try:
    agents_sql = f"""
    WITH agent_data AS (
        SELECT 
            REQUEST_ID,
            AGENT_NAME,
            TOKEN_CREDITS,
            f.value AS granular_entry,
            TRY_TO_TIMESTAMP_NTZ(
                f.value[OBJECT_KEYS(f.value)[0]]:start_time::STRING
            ) AS extracted_start_time
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY,
        LATERAL FLATTEN(input => CREDITS_GRANULAR) f
    ),
    filtered_requests AS (
        SELECT DISTINCT
            REQUEST_ID,
            TOKEN_CREDITS
        FROM agent_data
        WHERE extracted_start_time >= TO_TIMESTAMP_NTZ('{s}')
          AND extracted_start_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
    )
    SELECT 
        ROUND(SUM(TOKEN_CREDITS), 2) AS total_credits,
        COUNT(DISTINCT REQUEST_ID) AS total_requests
    FROM filtered_requests
    """
    agents_df = session.sql(agents_sql).to_pandas()
    
    if not agents_df.empty and len(agents_df) > 0:
        agents_credits = safe_number(agents_df.iloc[0]['TOTAL_CREDITS'])
        agents_requests = safe_number(agents_df.iloc[0]['TOTAL_REQUESTS'])
        
        if agents_credits > 0:
            col1, col2 = st.columns(2)
            col1.metric("Total Agents Credits", "{:,.2f}".format(float(agents_credits)))
            col2.metric("Total Requests", "{:,}".format(int(agents_requests)))
            
            # Get breakdown by agent
            agents_detail_sql = f"""
            WITH agent_data AS (
                SELECT 
                    REQUEST_ID,
                    AGENT_NAME,
                    TOKEN_CREDITS,
                    f.value AS granular_entry,
                    TRY_TO_TIMESTAMP_NTZ(
                        f.value[OBJECT_KEYS(f.value)[0]]:start_time::STRING
                    ) AS extracted_start_time
                FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY,
                LATERAL FLATTEN(input => CREDITS_GRANULAR) f
            ),
            filtered_requests AS (
                SELECT DISTINCT
                    REQUEST_ID,
                    AGENT_NAME,
                    TOKEN_CREDITS
                FROM agent_data
                WHERE AGENT_NAME IS NOT NULL
                  AND extracted_start_time >= TO_TIMESTAMP_NTZ('{s}')
                  AND extracted_start_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
            )
            SELECT 
                AGENT_NAME,
                ROUND(SUM(TOKEN_CREDITS), 2) AS total_credits
            FROM filtered_requests
            GROUP BY AGENT_NAME
            ORDER BY total_credits DESC
            LIMIT 20
            """
            agents_detail_df = session.sql(agents_detail_sql).to_pandas()
            
            if not agents_detail_df.empty:
                st.markdown("#### Agents Usage by Agent Name")
                st.dataframe(
                    agents_detail_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'AGENT_NAME': 'Agent',
                        'TOTAL_CREDITS': st.column_config.NumberColumn('Credits', format="%.2f")
                    }
                )
            
            # Get daily breakdown
            agents_daily_sql = f"""
            WITH agent_data AS (
                SELECT 
                    REQUEST_ID,
                    TOKEN_CREDITS,
                    f.value AS granular_entry,
                    TRY_TO_TIMESTAMP_NTZ(
                        f.value[OBJECT_KEYS(f.value)[0]]:start_time::STRING
                    ) AS extracted_start_time
                FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY,
                LATERAL FLATTEN(input => CREDITS_GRANULAR) f
            ),
            filtered_requests AS (
                SELECT DISTINCT
                    REQUEST_ID,
                    TOKEN_CREDITS,
                    TO_DATE(extracted_start_time) AS day
                FROM agent_data
                WHERE extracted_start_time >= TO_TIMESTAMP_NTZ('{s}')
                  AND extracted_start_time < TO_TIMESTAMP_NTZ(DATEADD(day, 1, '{e}'::DATE))
            )
            SELECT 
                day,
                ROUND(SUM(TOKEN_CREDITS), 2) AS daily_credits
            FROM filtered_requests
            GROUP BY day
            ORDER BY day
            """
            agents_daily_df = session.sql(agents_daily_sql).to_pandas()
            
            if not agents_daily_df.empty:
                st.markdown("#### Agents Credits by Day")
                agents_credits_chart = agents_daily_df.set_index('DAY')
                st.bar_chart(agents_credits_chart['DAILY_CREDITS'])
        else:
            st.info("No Cortex Agents usage found for the selected date range.")
    else:
        st.info("No Cortex Agents usage found for the selected date range.")
        
except Exception as ex:
    st.error(f"Error querying Cortex Agents data: {str(ex)}")

#############################################
#     FOOTER
#############################################
st.divider()
foot1, foot2 = st.columns([1, 1])

with foot1:
    st.markdown("Version 5.0")
with foot2:
    st.markdown("December 2025")