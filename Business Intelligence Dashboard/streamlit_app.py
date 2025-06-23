import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from snowflake.snowpark.context import get_active_session
from utils import (
    get_data_from_snowflake,
    format_currency,
    format_number,
    format_percentage,
    create_metric_cards,
    create_revenue_trend_chart,
    create_product_performance_chart,
    create_regional_pie_chart,
    create_customer_segment_chart,
    create_monthly_comparison_chart,
    create_sales_rep_performance_chart,
    get_comparison_kpi_data,
    create_cohort_analysis_chart
)

# Page configuration
st.set_page_config(
    page_title="Business Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
    }
    .filter-container {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="main-header">📊 Business Intelligence Dashboard</h1>', unsafe_allow_html=True)

st.markdown("""
Welcome to the **Business Intelligence Dashboard** - a comprehensive analytics platform built with Streamlit in Snowflake.
This dashboard provides real-time insights into sales performance, customer behavior, product analytics, and regional trends.

**Key Features:**
- 📈 Real-time KPI tracking with period-over-period comparisons
- 🎯 Interactive filters for deep-dive analysis
- 📊 Multiple visualization types (line charts, bar charts, pie charts, heatmaps)
- 🌍 Regional and customer segment analysis
- 💰 Revenue, cost, and profitability metrics
- 👥 Sales representative performance tracking
""")

# Sidebar filters
st.sidebar.markdown("## 🔍 Filters & Controls")

# Date range filter
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        value=date.today() - timedelta(days=90),
        max_value=date.today()
    )
with col2:
    end_date = st.date_input(
        "End Date",
        value=date.today(),
        max_value=date.today()
    )

# Quick date range buttons
st.sidebar.markdown("**Quick Ranges:**")
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Last 30 Days", key="30days"):
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        st.rerun()
    if st.button("Last 90 Days", key="90days"):
        start_date = date.today() - timedelta(days=90)
        end_date = date.today()
        st.rerun()

with col2:
    if st.button("Last 180 Days", key="180days"):
        start_date = date.today() - timedelta(days=180)
        end_date = date.today()
        st.rerun()
    if st.button("Last Year", key="1year"):
        start_date = date.today() - timedelta(days=365)
        end_date = date.today()
        st.rerun()

# Additional filters
try:
    regions_query = "SELECT DISTINCT region FROM BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA.CUSTOMERS ORDER BY region"
    regions_df = get_data_from_snowflake(regions_query)
    selected_regions = st.sidebar.multiselect(
        "Select Regions",
        options=regions_df['REGION'].tolist(),
        default=regions_df['REGION'].tolist()
    )

    segments_query = "SELECT DISTINCT customer_segment FROM BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA.CUSTOMERS ORDER BY customer_segment"
    segments_df = get_data_from_snowflake(segments_query)
    selected_segments = st.sidebar.multiselect(
        "Select Customer Segments",
        options=segments_df['CUSTOMER_SEGMENT'].tolist(),
        default=segments_df['CUSTOMER_SEGMENT'].tolist()
    )

    categories_query = "SELECT DISTINCT category FROM BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA.PRODUCTS ORDER BY category"
    categories_df = get_data_from_snowflake(categories_query)
    selected_categories = st.sidebar.multiselect(
        "Select Product Categories",
        options=categories_df['CATEGORY'].tolist(),
        default=categories_df['CATEGORY'].tolist()
    )
except Exception as e:
    st.sidebar.error("Unable to load filter options. Please ensure the database is set up correctly.")
    selected_regions = ['North America', 'Europe', 'Asia Pacific']
    selected_segments = ['Enterprise', 'SMB']
    selected_categories = ['Electronics', 'Furniture', 'Appliances']

# Comparison period for delta calculations
comparison_start = start_date - timedelta(days=(end_date - start_date).days)
comparison_end = start_date - timedelta(days=1)

# Main dashboard content
try:
    # Get KPI data with comparisons
    kpi_data = get_comparison_kpi_data(start_date, end_date, comparison_start, comparison_end)
    
    # KPI Cards Section
    st.markdown('<h2 class="section-header">📈 Key Performance Indicators</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    create_metric_cards(col1, col2, col3, col4, kpi_data)
    
    # Additional KPIs
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        try:
            profit_margin = (kpi_data.get('total_profit', 0) / kpi_data.get('total_revenue', 1)) * 100 if kpi_data.get('total_revenue', 0) > 0 else 0
            st.metric(
                label="Profit Margin",
                value=f"{profit_margin:.1f}%",
                delta=None
            )
        except:
            st.metric("Profit Margin", "0%")
    
    with col6:
        st.metric(
            label="Avg Transaction Value",
            value=format_currency(kpi_data.get('avg_transaction_value', 0)),
            delta=None
        )
    
    with col7:
        # Calculate conversion rate (simplified)
        conversion_rate = 0.23  # Dummy data
        st.metric(
            label="Conversion Rate",
            value=f"{conversion_rate:.1%}",
            delta="0.02%"
        )
    
    with col8:
        # Customer lifetime value (simplified)
        clv = 2450  # Dummy data
        st.metric(
            label="Customer LTV",
            value=format_currency(clv),
            delta=format_currency(150)
        )
    
    # Charts Section
    st.markdown('<h2 class="section-header">📊 Analytics & Insights</h2>', unsafe_allow_html=True)
    
    # Row 1: Revenue Trend and Product Performance
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Revenue Trend Chart
        monthly_query = f"""
        SELECT * FROM BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA.MONTHLY_SALES_SUMMARY
        WHERE month BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY month
        """
        monthly_data = get_data_from_snowflake(monthly_query)
        
        if not monthly_data.empty:
            fig_revenue = create_revenue_trend_chart(monthly_data)
            st.plotly_chart(fig_revenue, use_container_width=True)
        else:
            st.info("No data available for the selected date range")
    
    with col2:
        # Top Products
        product_query = f"""
        SELECT p.product_name, p.category, SUM(s.revenue) as total_revenue, SUM(s.profit) as total_profit
        FROM BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA.SALES s
        JOIN BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA.PRODUCTS p ON s.product_id = p.product_id
        WHERE s.sale_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY p.product_name, p.category
        ORDER BY total_revenue DESC
        LIMIT 10
        """
        product_data = get_data_from_snowflake(product_query)
        
        if not product_data.empty:
            fig_products = create_product_performance_chart(product_data)
            st.plotly_chart(fig_products, use_container_width=True)
        else:
            st.info("No product data available")
    
    # Row 2: Regional Analysis and Customer Segments
    col1, col2 = st.columns(2)
    
    with col1:
        # Regional Performance
        regional_query = f"""
        SELECT c.region, SUM(s.revenue) as total_revenue, SUM(s.profit) as total_profit, COUNT(*) as transactions
        FROM BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA.SALES s
        JOIN BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA.CUSTOMERS c ON s.customer_id = c.customer_id
        WHERE s.sale_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY c.region
        ORDER BY total_revenue DESC
        """
        regional_data = get_data_from_snowflake(regional_query)
        
        if not regional_data.empty:
            fig_regional = create_regional_pie_chart(regional_data)
            st.plotly_chart(fig_regional, use_container_width=True)
        else:
            st.info("No regional data available")
    
    with col2:
        # Customer Segment Analysis
        customer_query = f"""
        SELECT c.customer_name, c.customer_segment, c.region, SUM(s.revenue) as total_revenue, SUM(s.profit) as total_profit
        FROM BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA.SALES s
        JOIN BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA.CUSTOMERS c ON s.customer_id = c.customer_id
        WHERE s.sale_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY c.customer_name, c.customer_segment, c.region
        """
        customer_data = get_data_from_snowflake(customer_query)
        
        if not customer_data.empty:
            fig_segments = create_customer_segment_chart(customer_data)
            st.plotly_chart(fig_segments, use_container_width=True)
        else:
            st.info("No customer data available")
    
    # Row 3: Monthly Comparison and Sales Rep Performance
    col1, col2 = st.columns(2)
    
    with col1:
        if not monthly_data.empty:
            fig_monthly = create_monthly_comparison_chart(monthly_data)
            st.plotly_chart(fig_monthly, use_container_width=True)
    
    with col2:
        # Sales Rep Performance
        sales_rep_query = f"""
        SELECT sales_rep, SUM(revenue) as revenue, SUM(profit) as profit, COUNT(*) as sale_id
        FROM BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA.SALES
        WHERE sale_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY sales_rep
        ORDER BY revenue DESC
        """
        sales_rep_data = get_data_from_snowflake(sales_rep_query)
        
        if not sales_rep_data.empty:
            fig_sales_rep = create_sales_rep_performance_chart(sales_rep_data)
            st.plotly_chart(fig_sales_rep, use_container_width=True)
        else:
            st.info("No sales rep data available")
    
    # Data Tables Section
    st.markdown('<h2 class="section-header">📋 Detailed Data Analysis</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Sales Summary", "🏆 Top Customers", "📈 Product Performance", "🌍 Regional Analysis"])
    
    with tab1:
        if not monthly_data.empty:
            st.subheader("Monthly Sales Summary")
            st.dataframe(
                monthly_data,
                column_config={
                    "MONTH": st.column_config.DateColumn("Month"),
                    "TOTAL_REVENUE": st.column_config.NumberColumn("Revenue", format="$%.2f"),
                    "TOTAL_COST": st.column_config.NumberColumn("Cost", format="$%.2f"),
                    "TOTAL_PROFIT": st.column_config.NumberColumn("Profit", format="$%.2f"),
                    "TOTAL_TRANSACTIONS": st.column_config.NumberColumn("Transactions"),
                    "UNIQUE_CUSTOMERS": st.column_config.NumberColumn("Unique Customers")
                },
                use_container_width=True
            )
        else:
            st.info("No summary data available for the selected period")
    
    with tab2:
        if not customer_data.empty:
            st.subheader("Top Customers by Revenue")
            top_customers = customer_data.head(20)
            st.dataframe(
                top_customers,
                column_config={
                    "TOTAL_REVENUE": st.column_config.NumberColumn("Revenue", format="$%.2f"),
                    "TOTAL_PROFIT": st.column_config.NumberColumn("Profit", format="$%.2f"),
                    "CUSTOMER_NAME": st.column_config.TextColumn("Customer Name"),
                    "CUSTOMER_SEGMENT": st.column_config.TextColumn("Segment"),
                    "REGION": st.column_config.TextColumn("Region")
                },
                use_container_width=True
            )
        else:
            st.info("No customer data available")
    
    with tab3:
        if not product_data.empty:
            st.subheader("Product Performance Analysis")
            st.dataframe(
                product_data,
                column_config={
                    "TOTAL_REVENUE": st.column_config.NumberColumn("Revenue", format="$%.2f"),
                    "TOTAL_PROFIT": st.column_config.NumberColumn("Profit", format="$%.2f"),
                    "PRODUCT_NAME": st.column_config.TextColumn("Product"),
                    "CATEGORY": st.column_config.TextColumn("Category")
                },
                use_container_width=True
            )
        else:
            st.info("No product data available")
    
    with tab4:
        if not regional_data.empty:
            st.subheader("Regional Performance Breakdown")
            st.dataframe(
                regional_data,
                column_config={
                    "TOTAL_REVENUE": st.column_config.NumberColumn("Revenue", format="$%.2f"),
                    "TOTAL_PROFIT": st.column_config.NumberColumn("Profit", format="$%.2f"),
                    "TRANSACTIONS": st.column_config.NumberColumn("Transactions"),
                    "REGION": st.column_config.TextColumn("Region")
                },
                use_container_width=True
            )
        else:
            st.info("No regional data available")

except Exception as e:
    st.error(f"""
    **Database Connection Error**
    
    It appears the sample database hasn't been set up yet. To use this dashboard:
    
    1. Run the SQL script located in the `data/creation_script.sql` file
    2. Ensure you have the appropriate Snowflake permissions
    3. Refresh this page
    
    **Error details:** {str(e)}
    """)
    
    # Show demo with dummy data
    st.markdown("---")
    st.markdown("## 🎯 Demo Mode (Using Sample Data)")
    
    # Create dummy data for demo
    dummy_data = {
        'total_revenue': 1234567.89,
        'total_profit': 456789.12,
        'total_transactions': 1523,
        'unique_customers': 234,
        'revenue_delta': 45678.90,
        'profit_delta': 12345.67,
        'transactions_delta': 89,
        'customers_delta': 12
    }
    
    col1, col2, col3, col4 = st.columns(4)
    create_metric_cards(col1, col2, col3, col4, dummy_data)
    
    st.info("This is a preview with sample data. Set up the database to see real analytics!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Business Intelligence Dashboard</strong> | Built with Streamlit in Snowflake</p>
    <p>🔄 Data refreshes in real-time | 📊 Interactive analytics platform</p>
</div>
""", unsafe_allow_html=True) 