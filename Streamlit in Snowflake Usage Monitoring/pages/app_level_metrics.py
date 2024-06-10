# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import datetime 
import altair as alt
import pandas as pd


today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
week_ago = today - datetime.timedelta(days=7)
last_30_days = today - datetime.timedelta(days=30)


# Write directly to the app
st.title("App Level Usage Monitoring :balloon:")
st.write(
    """Metrics about the usage of a specific app in your account
    """
)

def generate_sql(start_date):
    sql = f"""
    select 
        user_name as User,
        total_elapsed_time/60000 as Minutes_Used, 
        date(start_time) as Date,
        try_parse_json(query_tag):StreamlitName as AppName,
        query_text
    from snowflake.monitoring.query_history
    where start_time >= '{start_date}'
    and try_parse_json(query_tag):StreamlitEngine = 'ExecuteStreamlit'
    and try_parse_json(query_tag):ChildQuery IS NULL
    and contains(query_text, 'execute streamlit') 
    order by Date desc;
    """
    return sql

@st.cache_data
def query_sf(sql):
    df = session.sql(sql).to_pandas()
    return df


def generate_bar_chart(views_over_time):
    views_over_time.index = pd.to_datetime(views_over_time.index)  # Convert index to datetime

    # Convert Series to DataFrame for Altair
    df = views_over_time.reset_index()
    df.columns = ['Date', 'Value']  # Rename columns for clarity
    
    # Create bar chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Value:Q', title='Number of Views'),
        tooltip=['Date', 'Value']  # Add tooltips to display the date and value on hover
    ).properties(
    width=600,
    height=400
    )
    
    st.altair_chart(chart)    
    

@st.cache_data
def calculate_metrics(df):
    num_users = df['USER'].nunique()
    num_apps = df['APPNAME'].nunique()
    num_views = len(df.index) 

    st.subheader('Summary Stats')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label='Unique Users', value=num_users)
    
    with col2:
        st.metric(label='Apps Used', value=num_apps)

    with col3:
        st.metric(label='Total Views', value=num_views)

    st.subheader('Views over time')
    views_over_time = df.groupby(['DATE']).size()
    generate_bar_chart(views_over_time)

    st.subheader('Raw Data')
    st.dataframe(df)

session = get_active_session()

sql = generate_sql(last_30_days)
df = query_sf(sql)
list_of_apps = df['APPNAME'].unique()

app = st.selectbox('Choose App Name', list_of_apps)

tab_yesterday, tab_last_week, tab_last_30_days = st.tabs(["Last Day", "Last Week", "Last 30 Days"])

with tab_yesterday:
    sql = generate_sql(yesterday)
    df = query_sf(sql)
    df2 = df[df['APPNAME'] == app]
    calculate_metrics(df2)


with tab_last_week:
    sql = generate_sql(week_ago)
    df = query_sf(sql)
    df2 = df[df['APPNAME'] == app]
    calculate_metrics(df2)

with tab_last_30_days:
    sql = generate_sql(last_30_days)
    df = query_sf(sql)
    df2 = df[df['APPNAME'] == app]
    calculate_metrics(df2)