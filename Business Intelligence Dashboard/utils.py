"""
Utility functions for the Business Intelligence Dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import re


# =============================================================================
# ENVIRONMENT DETECTION
# =============================================================================
def is_running_in_snowflake() -> bool:
    """
    Detect if the app is running in Snowflake or locally.
    
    Returns:
        bool: True if running in Snowflake, False if running locally
    """
    try:
        from snowflake.snowpark.context import get_active_session
        get_active_session()
        return True
    except Exception:
        return False


# Cache the environment check
_IS_SNOWFLAKE = None

def get_execution_environment() -> bool:
    """Get cached execution environment."""
    global _IS_SNOWFLAKE
    if _IS_SNOWFLAKE is None:
        _IS_SNOWFLAKE = is_running_in_snowflake()
    return _IS_SNOWFLAKE


# =============================================================================
# DATA FETCHING
# =============================================================================
@st.cache_data
def get_data_from_snowflake(query: str) -> pd.DataFrame:
    """
    Execute a SQL query against Snowflake and return the result as a pandas DataFrame.
    Falls back to dummy data when running locally.
    
    Args:
        query (str): SQL query to execute
        
    Returns:
        pd.DataFrame: Query results
    """
    if get_execution_environment():
        # Running in Snowflake - execute real query
        from snowflake.snowpark.context import get_active_session
        session = get_active_session()
        return session.sql(query).to_pandas()
    else:
        # Running locally - return dummy data
        return get_dummy_data_for_query(query)


def get_dummy_data_for_query(query: str) -> pd.DataFrame:
    """
    Parse a SQL query and return appropriate dummy data.
    
    Args:
        query (str): SQL query to parse
        
    Returns:
        pd.DataFrame: Matching dummy data
    """
    from data.dummy_data import (
        PRODUCTS_DATA, CUSTOMERS_DATA, SALES_DATA, MARKETING_CAMPAIGNS_DATA,
        MONTHLY_SALES_SUMMARY, PRODUCT_PERFORMANCE, CUSTOMER_PERFORMANCE, REGIONAL_PERFORMANCE,
        get_kpi_metrics, get_monthly_summary_for_range, get_product_revenue_for_range,
        get_regional_revenue_for_range, get_customer_revenue_for_range,
        get_sales_rep_performance_for_range, filter_sales_by_date
    )
    
    query_upper = query.upper()
    
    # Extract date range from query if present
    date_match = re.search(r"BETWEEN\s+'(\d{4}-\d{2}-\d{2})'\s+AND\s+'(\d{4}-\d{2}-\d{2})'", query, re.IGNORECASE)
    start_date = None
    end_date = None
    if date_match:
        start_date = date_match.group(1)
        end_date = date_match.group(2)
    
    # Match query patterns to dummy data
    
    # Distinct regions query
    if 'DISTINCT' in query_upper and 'REGION' in query_upper and 'CUSTOMERS' in query_upper:
        return pd.DataFrame({'REGION': CUSTOMERS_DATA['REGION'].unique()})
    
    # Distinct customer segments query
    if 'DISTINCT' in query_upper and 'CUSTOMER_SEGMENT' in query_upper:
        return pd.DataFrame({'CUSTOMER_SEGMENT': CUSTOMERS_DATA['CUSTOMER_SEGMENT'].unique()})
    
    # Distinct categories query
    if 'DISTINCT' in query_upper and 'CATEGORY' in query_upper:
        return pd.DataFrame({'CATEGORY': PRODUCTS_DATA['CATEGORY'].unique()})
    
    # Monthly sales summary view
    if 'MONTHLY_SALES_SUMMARY' in query_upper:
        if start_date and end_date:
            return get_monthly_summary_for_range(start_date, end_date)
        return MONTHLY_SALES_SUMMARY
    
    # Sales rep performance query (check BEFORE KPI aggregation since both have SUM/COUNT)
    if 'SALES_REP' in query_upper and 'GROUP BY' in query_upper:
        if start_date and end_date:
            return get_sales_rep_performance_for_range(start_date, end_date)
        result = SALES_DATA.groupby('SALES_REP').agg({
            'REVENUE': 'sum',
            'PROFIT': 'sum',
            'SALE_ID': 'count'
        }).reset_index()
        return result
    
    # KPI aggregation query (SUM revenue, profit, etc.)
    if ('SUM(REVENUE)' in query_upper or 'SUM(PROFIT)' in query_upper) and 'COUNT(*)' in query_upper:
        if start_date and end_date:
            metrics = get_kpi_metrics(start_date, end_date)
            return pd.DataFrame([metrics])
        # Default to all time
        return pd.DataFrame([{
            'TOTAL_REVENUE': SALES_DATA['REVENUE'].sum(),
            'TOTAL_PROFIT': SALES_DATA['PROFIT'].sum(),
            'TOTAL_TRANSACTIONS': len(SALES_DATA),
            'UNIQUE_CUSTOMERS': SALES_DATA['CUSTOMER_ID'].nunique(),
            'AVG_TRANSACTION_VALUE': SALES_DATA['REVENUE'].mean()
        }])
    
    # Product performance query
    if 'PRODUCT_NAME' in query_upper and 'PRODUCTS' in query_upper and 'SALES' in query_upper:
        if start_date and end_date:
            return get_product_revenue_for_range(start_date, end_date)
        return PRODUCT_PERFORMANCE[['PRODUCT_NAME', 'CATEGORY', 'TOTAL_REVENUE', 'TOTAL_PROFIT']]
    
    # Regional performance query
    if 'REGION' in query_upper and 'CUSTOMERS' in query_upper and 'SALES' in query_upper and 'GROUP BY' in query_upper:
        if 'CUSTOMER_NAME' in query_upper:
            # Customer detail query
            if start_date and end_date:
                return get_customer_revenue_for_range(start_date, end_date)
            return CUSTOMER_PERFORMANCE[['CUSTOMER_NAME', 'CUSTOMER_SEGMENT', 'REGION', 'TOTAL_REVENUE', 'TOTAL_PROFIT']]
        else:
            # Regional aggregate query
            if start_date and end_date:
                return get_regional_revenue_for_range(start_date, end_date)
            return REGIONAL_PERFORMANCE[['REGION', 'TOTAL_REVENUE', 'TOTAL_PROFIT', 'TOTAL_TRANSACTIONS']]
    
    # Product performance view
    if 'PRODUCT_PERFORMANCE' in query_upper:
        return PRODUCT_PERFORMANCE
    
    # Customer performance view
    if 'CUSTOMER_PERFORMANCE' in query_upper:
        return CUSTOMER_PERFORMANCE
    
    # Regional performance view
    if 'REGIONAL_PERFORMANCE' in query_upper:
        return REGIONAL_PERFORMANCE
    
    # Base tables
    if 'PRODUCTS' in query_upper and 'JOIN' not in query_upper:
        return PRODUCTS_DATA
    
    if 'CUSTOMERS' in query_upper and 'JOIN' not in query_upper:
        return CUSTOMERS_DATA
    
    if 'MARKETING_CAMPAIGNS' in query_upper:
        return MARKETING_CAMPAIGNS_DATA
    
    if 'SALES' in query_upper and 'JOIN' not in query_upper:
        if start_date and end_date:
            return filter_sales_by_date(start_date, end_date)
        return SALES_DATA
    
    # Default: return empty DataFrame with a warning
    st.warning(f"Query pattern not recognized for dummy data: {query[:100]}...")
    return pd.DataFrame()


# =============================================================================
# FORMATTING FUNCTIONS
# =============================================================================
def format_currency(value):
    """Format a number as currency."""
    if pd.isna(value):
        return "$0"
    return f"${value:,.2f}"


def format_number(value):
    """Format a number with thousand separators."""
    if pd.isna(value):
        return "0"
    return f"{value:,.0f}" if value == int(value) else f"{value:,.2f}"


def format_percentage(value):
    """Format a number as a percentage."""
    if pd.isna(value):
        return "0%"
    return f"{value:.1%}"


# =============================================================================
# METRIC CARDS
# =============================================================================
def create_metric_cards(col1, col2, col3, col4, metrics_data):
    """
    Create metric cards in the specified columns.
    
    Args:
        col1, col2, col3, col4: Streamlit columns
        metrics_data: Dictionary containing metric values
    """
    with col1:
        st.metric(
            label="Total Revenue",
            value=format_currency(metrics_data.get('total_revenue', 0)),
            delta=format_currency(metrics_data.get('revenue_delta', 0))
        )
    
    with col2:
        st.metric(
            label="Total Profit",
            value=format_currency(metrics_data.get('total_profit', 0)),
            delta=format_currency(metrics_data.get('profit_delta', 0))
        )
    
    with col3:
        st.metric(
            label="Total Transactions",
            value=format_number(metrics_data.get('total_transactions', 0)),
            delta=format_number(metrics_data.get('transactions_delta', 0))
        )
    
    with col4:
        st.metric(
            label="Unique Customers",
            value=format_number(metrics_data.get('unique_customers', 0)),
            delta=format_number(metrics_data.get('customers_delta', 0))
        )


# =============================================================================
# CHART FUNCTIONS
# =============================================================================
def create_revenue_trend_chart(data):
    """
    Create a revenue trend line chart using Plotly.
    
    Args:
        data: DataFrame with columns 'month' and 'total_revenue'
        
    Returns:
        plotly.graph_objects.Figure
    """
    fig = px.line(
        data, 
        x='MONTH', 
        y='TOTAL_REVENUE',
        title='Revenue Trend Over Time',
        labels={'TOTAL_REVENUE': 'Revenue ($)', 'MONTH': 'Month'}
    )
    
    fig.update_traces(
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        hovermode='x unified',
        xaxis_title="",
        yaxis_title="Revenue ($)"
    )
    
    return fig


def create_product_performance_chart(data):
    """
    Create a horizontal bar chart for product performance.
    
    Args:
        data: DataFrame with product performance data
        
    Returns:
        plotly.graph_objects.Figure
    """
    fig = px.bar(
        data.head(10), 
        x='TOTAL_REVENUE',
        y='PRODUCT_NAME',
        orientation='h',
        title='Top 10 Products by Revenue',
        labels={'TOTAL_REVENUE': 'Revenue ($)', 'PRODUCT_NAME': 'Product'}
    )
    
    fig.update_layout(
        height=500,
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    
    return fig


def create_regional_pie_chart(data):
    """
    Create a pie chart for regional revenue distribution.
    
    Args:
        data: DataFrame with regional data
        
    Returns:
        plotly.graph_objects.Figure
    """
    fig = px.pie(
        data,
        values='TOTAL_REVENUE',
        names='REGION',
        title='Revenue Distribution by Region'
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    
    fig.update_layout(height=400)
    
    return fig


def create_customer_segment_chart(data):
    """
    Create a donut chart for customer segment analysis.
    
    Args:
        data: DataFrame with customer segment data
        
    Returns:
        plotly.graph_objects.Figure
    """
    segment_data = data.groupby('CUSTOMER_SEGMENT').agg({
        'TOTAL_REVENUE': 'sum',
        'CUSTOMER_NAME': 'count'
    }).reset_index()
    
    fig = px.pie(
        segment_data,
        values='TOTAL_REVENUE',
        names='CUSTOMER_SEGMENT',
        title='Revenue by Customer Segment',
        hole=0.4
    )
    
    fig.update_layout(height=400)
    
    return fig


def create_monthly_comparison_chart(data):
    """
    Create a grouped bar chart comparing revenue, cost, and profit by month.
    
    Args:
        data: DataFrame with monthly summary data
        
    Returns:
        plotly.graph_objects.Figure
    """
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Revenue',
        x=data['MONTH'],
        y=data['TOTAL_REVENUE'],
        marker_color='#2E86AB'
    ))
    
    fig.add_trace(go.Bar(
        name='Cost',
        x=data['MONTH'],
        y=data['TOTAL_COST'],
        marker_color='#A23B72'
    ))
    
    fig.add_trace(go.Bar(
        name='Profit',
        x=data['MONTH'],
        y=data['TOTAL_PROFIT'],
        marker_color='#F18F01'
    ))
    
    fig.update_layout(
        title='Monthly Revenue, Cost, and Profit Comparison',
        xaxis_title='Month',
        yaxis_title='Amount ($)',
        barmode='group',
        height=400
    )
    
    return fig


def create_sales_rep_performance_chart(data):
    """
    Create a bar chart showing sales rep performance.
    
    Args:
        data: DataFrame with sales rep data
        
    Returns:
        plotly.graph_objects.Figure
    """
    rep_data = data.groupby('SALES_REP').agg({
        'REVENUE': 'sum',
        'PROFIT': 'sum',
        'SALE_ID': 'count'
    }).reset_index().sort_values('REVENUE', ascending=False)
    
    fig = px.bar(
        rep_data,
        x='SALES_REP',
        y='REVENUE',
        title='Sales Representative Performance',
        labels={'REVENUE': 'Total Revenue ($)', 'SALES_REP': 'Sales Rep'}
    )
    
    fig.update_layout(height=400)
    
    return fig


# =============================================================================
# KPI DATA FUNCTIONS
# =============================================================================
def get_kpi_data(start_date, end_date):
    """
    Get KPI data for the specified date range.
    
    Args:
        start_date: Start date for the analysis
        end_date: End date for the analysis
        
    Returns:
        dict: Dictionary containing KPI metrics
    """
    query = f"""
    SELECT 
        SUM(revenue) as total_revenue,
        SUM(profit) as total_profit,
        COUNT(*) as total_transactions,
        COUNT(DISTINCT customer_id) as unique_customers,
        AVG(revenue) as avg_transaction_value
    FROM BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA.SALES
    WHERE sale_date BETWEEN '{start_date}' AND '{end_date}'
    """
    
    data = get_data_from_snowflake(query)
    if not data.empty:
        return {
            'total_revenue': data.iloc[0]['TOTAL_REVENUE'],
            'total_profit': data.iloc[0]['TOTAL_PROFIT'],
            'total_transactions': data.iloc[0]['TOTAL_TRANSACTIONS'],
            'unique_customers': data.iloc[0]['UNIQUE_CUSTOMERS'],
            'avg_transaction_value': data.iloc[0]['AVG_TRANSACTION_VALUE']
        }
    return {}


def get_comparison_kpi_data(start_date, end_date, comparison_start, comparison_end):
    """
    Get KPI data with comparison to previous period.
    
    Args:
        start_date: Current period start date
        end_date: Current period end date
        comparison_start: Previous period start date
        comparison_end: Previous period end date
        
    Returns:
        dict: Dictionary containing current and delta metrics
    """
    current_data = get_kpi_data(start_date, end_date)
    previous_data = get_kpi_data(comparison_start, comparison_end)
    
    result = current_data.copy()
    
    if previous_data:
        result['revenue_delta'] = current_data.get('total_revenue', 0) - previous_data.get('total_revenue', 0)
        result['profit_delta'] = current_data.get('total_profit', 0) - previous_data.get('total_profit', 0)
        result['transactions_delta'] = current_data.get('total_transactions', 0) - previous_data.get('total_transactions', 0)
        result['customers_delta'] = current_data.get('unique_customers', 0) - previous_data.get('unique_customers', 0)
    
    return result


def create_cohort_analysis_chart(data):
    """
    Create a cohort analysis heatmap.
    
    Args:
        data: DataFrame with cohort data
        
    Returns:
        plotly.graph_objects.Figure
    """
    # This is a simplified version - in a real scenario, you'd calculate proper cohort data
    fig = px.imshow(
        [[0.8, 0.6, 0.4, 0.3], [0.7, 0.5, 0.3, 0.2], [0.6, 0.4, 0.2, 0.1]],
        title="Customer Retention Cohort Analysis",
        labels=dict(x="Period", y="Cohort", color="Retention Rate"),
        x=['Month 1', 'Month 2', 'Month 3', 'Month 4'],
        y=['Q1 Cohort', 'Q2 Cohort', 'Q3 Cohort']
    )
    
    fig.update_layout(height=300)
    
    return fig
