"""
Utility functions for the Business Intelligence Dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta


@st.cache_data
def get_data_from_snowflake(query: str) -> pd.DataFrame:
    """
    Execute a SQL query against Snowflake and return the result as a pandas DataFrame.
    
    Args:
        query (str): SQL query to execute
        
    Returns:
        pd.DataFrame: Query results
    """
    session = get_active_session()
    return session.sql(query).to_pandas()


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