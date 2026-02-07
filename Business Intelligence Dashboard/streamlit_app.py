import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from utils import (
    get_data_from_snowflake,
    get_execution_environment,
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
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title(":material/analytics: Business intelligence dashboard")

# Show environment indicator
if not get_execution_environment():
    st.caption(":material/home: Running locally with sample data. Deploy to Snowflake for live data.")

# Sidebar filters
with st.sidebar:
    st.header(":material/filter_list: Filters")
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start date",
            value=date.today() - timedelta(days=90),
            max_value=date.today()
        )
    with col2:
        end_date = st.date_input(
            "End date",
            value=date.today(),
            max_value=date.today()
        )
    
    # Quick date range buttons
    st.caption("Quick ranges")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("30 days", key="30days", use_container_width=True):
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()
            st.rerun()
        if st.button("90 days", key="90days", use_container_width=True):
            start_date = date.today() - timedelta(days=90)
            end_date = date.today()
            st.rerun()
    
    with col2:
        if st.button("180 days", key="180days", use_container_width=True):
            start_date = date.today() - timedelta(days=180)
            end_date = date.today()
            st.rerun()
        if st.button("1 year", key="1year", width="stretch"):
            start_date = date.today() - timedelta(days=365)
            end_date = date.today()
            st.rerun()
    
    st.divider()
    
    # Additional filters
    try:
        regions_query = "SELECT DISTINCT region FROM BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA.CUSTOMERS ORDER BY region"
        regions_df = get_data_from_snowflake(regions_query)
        selected_regions = st.multiselect(
            "Regions",
            options=regions_df['REGION'].tolist(),
            default=regions_df['REGION'].tolist()
        )

        segments_query = "SELECT DISTINCT customer_segment FROM BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA.CUSTOMERS ORDER BY customer_segment"
        segments_df = get_data_from_snowflake(segments_query)
        selected_segments = st.multiselect(
            "Customer segments",
            options=segments_df['CUSTOMER_SEGMENT'].tolist(),
            default=segments_df['CUSTOMER_SEGMENT'].tolist()
        )

        categories_query = "SELECT DISTINCT category FROM BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA.PRODUCTS ORDER BY category"
        categories_df = get_data_from_snowflake(categories_query)
        selected_categories = st.multiselect(
            "Product categories",
            options=categories_df['CATEGORY'].tolist(),
            default=categories_df['CATEGORY'].tolist()
        )
    except Exception as e:
        st.error("Unable to load filter options", icon=":material/error:")
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
    st.subheader(":material/monitoring: Key performance indicators")
    
    # Calculate additional metrics
    profit_margin = (kpi_data.get('total_profit', 0) / kpi_data.get('total_revenue', 1)) * 100 if kpi_data.get('total_revenue', 0) > 0 else 0
    avg_transaction = kpi_data.get('avg_transaction_value', 0)
    
    # KPI row with horizontal container and borders
    with st.container(horizontal=True):
        st.metric(
            label="Total revenue",
            value=format_currency(kpi_data.get('total_revenue', 0)),
            delta=f"{kpi_data.get('revenue_delta', 0):.1f}%",
            border=True
        )
        st.metric(
            label="Total profit",
            value=format_currency(kpi_data.get('total_profit', 0)),
            delta=f"{kpi_data.get('profit_delta', 0):.1f}%",
            border=True
        )
        st.metric(
            label="Total orders",
            value=format_number(kpi_data.get('total_orders', 0)),
            delta=f"{kpi_data.get('orders_delta', 0):.1f}%",
            border=True
        )
        st.metric(
            label="Unique customers",
            value=format_number(kpi_data.get('unique_customers', 0)),
            delta=f"{kpi_data.get('customers_delta', 0):.1f}%",
            border=True
        )
    
    # Second KPI row
    with st.container(horizontal=True):
        st.metric(
            label="Profit margin",
            value=f"{profit_margin:.1f}%",
            border=True
        )
        st.metric(
            label="Avg transaction value",
            value=format_currency(avg_transaction),
            border=True
        )
        st.metric(
            label="Conversion rate",
            value="23.0%",
            delta="+2.0%",
            border=True
        )
        st.metric(
            label="Customer LTV",
            value=format_currency(2450),
            delta="+$150",
            border=True
        )
    
    # Charts Section
    st.subheader(":material/bar_chart: Analytics and insights")
    
    # Row 1: Revenue Trend and Product Performance
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.container(border=True):
            st.markdown("**Revenue trend**")
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
                st.info("No data available for the selected date range", icon=":material/info:")
    
    with col2:
        with st.container(border=True):
            st.markdown("**Top products**")
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
                st.info("No product data available", icon=":material/info:")
    
    # Row 2: Regional Analysis and Customer Segments
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("**Revenue by region**")
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
                st.info("No regional data available", icon=":material/info:")
    
    with col2:
        with st.container(border=True):
            st.markdown("**Customer segments**")
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
                st.info("No customer data available", icon=":material/info:")
    
    # Row 3: Monthly Comparison and Sales Rep Performance
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("**Monthly comparison**")
            if not monthly_data.empty:
                fig_monthly = create_monthly_comparison_chart(monthly_data)
                st.plotly_chart(fig_monthly, use_container_width=True)
            else:
                st.info("No monthly data available", icon=":material/info:")
    
    with col2:
        with st.container(border=True):
            st.markdown("**Sales rep performance**")
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
                st.info("No sales rep data available", icon=":material/info:")
    
    # Data Tables Section
    st.subheader(":material/table_chart: Detailed data analysis")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        ":material/summarize: Sales summary",
        ":material/groups: Top customers", 
        ":material/inventory: Product performance",
        ":material/public: Regional analysis"
    ])
    
    with tab1:
        if not monthly_data.empty:
            st.dataframe(
                monthly_data,
                column_config={
                    "MONTH": st.column_config.DateColumn("Month"),
                    "TOTAL_REVENUE": st.column_config.NumberColumn("Revenue", format="$%.2f"),
                    "TOTAL_COST": st.column_config.NumberColumn("Cost", format="$%.2f"),
                    "TOTAL_PROFIT": st.column_config.NumberColumn("Profit", format="$%.2f"),
                    "TOTAL_TRANSACTIONS": st.column_config.NumberColumn("Transactions"),
                    "UNIQUE_CUSTOMERS": st.column_config.NumberColumn("Unique customers")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No summary data available for the selected period", icon=":material/info:")
    
    with tab2:
        if not customer_data.empty:
            top_customers = customer_data.head(20)
            st.dataframe(
                top_customers,
                column_config={
                    "TOTAL_REVENUE": st.column_config.NumberColumn("Revenue", format="$%.2f"),
                    "TOTAL_PROFIT": st.column_config.NumberColumn("Profit", format="$%.2f"),
                    "CUSTOMER_NAME": st.column_config.TextColumn("Customer name"),
                    "CUSTOMER_SEGMENT": st.column_config.TextColumn("Segment"),
                    "REGION": st.column_config.TextColumn("Region")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No customer data available", icon=":material/info:")
    
    with tab3:
        if not product_data.empty:
            st.dataframe(
                product_data,
                column_config={
                    "TOTAL_REVENUE": st.column_config.NumberColumn("Revenue", format="$%.2f"),
                    "TOTAL_PROFIT": st.column_config.NumberColumn("Profit", format="$%.2f"),
                    "PRODUCT_NAME": st.column_config.TextColumn("Product"),
                    "CATEGORY": st.column_config.TextColumn("Category")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No product data available", icon=":material/info:")
    
    with tab4:
        if not regional_data.empty:
            st.dataframe(
                regional_data,
                column_config={
                    "TOTAL_REVENUE": st.column_config.NumberColumn("Revenue", format="$%.2f"),
                    "TOTAL_PROFIT": st.column_config.NumberColumn("Profit", format="$%.2f"),
                    "TRANSACTIONS": st.column_config.NumberColumn("Transactions"),
                    "REGION": st.column_config.TextColumn("Region")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No regional data available", icon=":material/info:")

except Exception as e:
    st.error(f"""
    **Error loading dashboard**
    
    An error occurred while loading the dashboard data.
    
    **Error details:** {str(e)}
    
    **Troubleshooting:**
    - If running in Snowflake: Ensure the database is set up using `data/creation_script.sql`
    - If running locally: Check that all dependencies are installed
    """, icon=":material/error:")

# Footer
st.caption("Business Intelligence Dashboard | Built with Streamlit in Snowflake")
