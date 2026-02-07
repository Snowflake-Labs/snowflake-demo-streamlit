"""
Dummy data for local development of the Business Intelligence Dashboard.
This data mirrors the structure created by creation_script.sql
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import random

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

# =============================================================================
# PRODUCTS DATA
# =============================================================================
PRODUCTS_DATA = pd.DataFrame({
    'PRODUCT_ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'PRODUCT_NAME': [
        'Laptop Pro', 'Smartphone X', 'Tablet Ultra', 'Wireless Headphones',
        'Smart Watch', 'Gaming Console', 'Office Chair', 'Standing Desk',
        'Bookshelf', 'Coffee Maker'
    ],
    'CATEGORY': [
        'Electronics', 'Electronics', 'Electronics', 'Electronics',
        'Electronics', 'Electronics', 'Furniture', 'Furniture',
        'Furniture', 'Appliances'
    ],
    'PRICE': [1299.99, 899.99, 599.99, 199.99, 299.99, 499.99, 249.99, 449.99, 149.99, 79.99],
    'COST': [800.00, 500.00, 350.00, 80.00, 150.00, 300.00, 120.00, 200.00, 70.00, 35.00]
})

# =============================================================================
# CUSTOMERS DATA
# =============================================================================
CUSTOMERS_DATA = pd.DataFrame({
    'CUSTOMER_ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'CUSTOMER_NAME': [
        'TechCorp Inc', 'StartupHub', 'GlobalTech Ltd', 'InnovateCo',
        'FutureTech', 'SmallBiz Solutions', 'MegaCorp', 'LocalTech',
        'TechStart', 'EnterpriseMax'
    ],
    'CUSTOMER_SEGMENT': [
        'Enterprise', 'SMB', 'Enterprise', 'SMB', 'Enterprise',
        'SMB', 'Enterprise', 'SMB', 'SMB', 'Enterprise'
    ],
    'REGION': [
        'North America', 'North America', 'Europe', 'Europe', 'Asia Pacific',
        'Asia Pacific', 'North America', 'Europe', 'Asia Pacific', 'North America'
    ],
    'COUNTRY': [
        'USA', 'Canada', 'UK', 'Germany', 'Japan',
        'Australia', 'USA', 'France', 'Singapore', 'USA'
    ],
    'ACQUISITION_DATE': pd.to_datetime([
        '2020-01-15', '2021-03-22', '2019-11-08', '2022-05-10', '2020-09-14',
        '2021-12-03', '2018-06-25', '2022-01-18', '2021-07-30', '2019-04-12'
    ])
})

# =============================================================================
# MARKETING CAMPAIGNS DATA
# =============================================================================
MARKETING_CAMPAIGNS_DATA = pd.DataFrame({
    'CAMPAIGN_ID': [1, 2, 3, 4, 5],
    'CAMPAIGN_NAME': [
        'Q1 Product Launch', 'Summer Sale', 'Back to School',
        'Holiday Campaign', 'Brand Awareness'
    ],
    'CAMPAIGN_TYPE': ['Product Launch', 'Seasonal', 'Seasonal', 'Seasonal', 'Brand'],
    'START_DATE': pd.to_datetime(['2024-01-01', '2024-06-01', '2024-08-01', '2024-11-01', '2024-01-01']),
    'END_DATE': pd.to_datetime(['2024-03-31', '2024-08-31', '2024-09-30', '2024-12-31', '2024-12-31']),
    'BUDGET': [50000, 30000, 25000, 75000, 40000],
    'CLICKS': [125000, 80000, 65000, 180000, 200000],
    'IMPRESSIONS': [2500000, 1600000, 1300000, 3600000, 8000000],
    'CONVERSIONS': [3200, 2100, 1800, 4500, 1500]
})

# =============================================================================
# SALES DATA - Generated programmatically
# =============================================================================
def generate_sales_data():
    """Generate realistic sales data for 2 years."""
    sales_reps = ['John Smith', 'Sarah Johnson', 'Mike Davis', 'Lisa Wilson', 'Tom Brown']
    
    # Generate dates for 2 years
    start_date = datetime(2023, 1, 1)
    end_date = datetime.now()
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    sales_records = []
    sale_id = 1
    
    for sale_date in date_range:
        # Variable number of sales per day (more on weekdays, seasonal boost)
        month = sale_date.month
        day_of_week = sale_date.weekday()
        
        # Base sales per day
        base_sales = 2 if day_of_week < 5 else 1
        
        # Seasonal adjustments
        if month in [11, 12]:  # Holiday boost
            base_sales = int(base_sales * 1.5)
        elif month in [6, 7, 8]:  # Summer boost
            base_sales = int(base_sales * 1.2)
        
        # Random variation
        num_sales = max(1, base_sales + random.randint(-1, 2))
        
        for _ in range(num_sales):
            customer_id = random.randint(1, 10)
            product_id = random.randint(1, 10)
            quantity = random.randint(1, 5)
            
            # Get product info
            product = PRODUCTS_DATA[PRODUCTS_DATA['PRODUCT_ID'] == product_id].iloc[0]
            price = product['PRICE']
            cost = product['COST']
            
            # Seasonal price factor
            seasonal_factor = 1.0
            if month in [11, 12]:
                seasonal_factor = 1.3
            elif month in [6, 7, 8]:
                seasonal_factor = 1.15
            
            revenue = round(price * quantity * seasonal_factor, 2)
            total_cost = round(cost * quantity, 2)
            profit = round(revenue - total_cost, 2)
            
            sales_records.append({
                'SALE_ID': sale_id,
                'CUSTOMER_ID': customer_id,
                'PRODUCT_ID': product_id,
                'SALE_DATE': sale_date.date(),
                'QUANTITY': quantity,
                'REVENUE': revenue,
                'COST': total_cost,
                'PROFIT': profit,
                'SALES_REP': random.choice(sales_reps)
            })
            sale_id += 1
    
    return pd.DataFrame(sales_records)


# Generate sales data once
SALES_DATA = generate_sales_data()


# =============================================================================
# COMPUTED VIEWS
# =============================================================================
def get_monthly_sales_summary():
    """Compute monthly sales summary from sales data."""
    df = SALES_DATA.copy()
    df['SALE_DATE'] = pd.to_datetime(df['SALE_DATE'])
    df['MONTH'] = df['SALE_DATE'].dt.to_period('M').dt.to_timestamp()
    
    summary = df.groupby('MONTH').agg({
        'REVENUE': 'sum',
        'COST': 'sum',
        'PROFIT': 'sum',
        'SALE_ID': 'count',
        'CUSTOMER_ID': 'nunique'
    }).reset_index()
    
    summary.columns = ['MONTH', 'TOTAL_REVENUE', 'TOTAL_COST', 'TOTAL_PROFIT', 
                       'TOTAL_TRANSACTIONS', 'UNIQUE_CUSTOMERS']
    return summary


def get_product_performance():
    """Compute product performance from sales data."""
    df = SALES_DATA.merge(PRODUCTS_DATA, on='PRODUCT_ID')
    
    performance = df.groupby(['PRODUCT_ID', 'PRODUCT_NAME', 'CATEGORY']).agg({
        'QUANTITY': 'sum',
        'REVENUE': 'sum',
        'PROFIT': 'sum',
        'CUSTOMER_ID': 'nunique'
    }).reset_index()
    
    performance.columns = ['PRODUCT_ID', 'PRODUCT_NAME', 'CATEGORY', 
                          'TOTAL_QUANTITY_SOLD', 'TOTAL_REVENUE', 'TOTAL_PROFIT',
                          'UNIQUE_CUSTOMERS']
    performance['AVG_PROFIT_PER_UNIT'] = performance['TOTAL_PROFIT'] / performance['TOTAL_QUANTITY_SOLD']
    return performance.sort_values('TOTAL_REVENUE', ascending=False)


def get_customer_performance():
    """Compute customer performance from sales data."""
    df = SALES_DATA.merge(CUSTOMERS_DATA, on='CUSTOMER_ID')
    
    performance = df.groupby(['CUSTOMER_ID', 'CUSTOMER_NAME', 'CUSTOMER_SEGMENT', 
                              'REGION', 'COUNTRY']).agg({
        'REVENUE': 'sum',
        'PROFIT': 'sum',
        'SALE_ID': 'count',
        'SALE_DATE': 'max'
    }).reset_index()
    
    performance.columns = ['CUSTOMER_ID', 'CUSTOMER_NAME', 'CUSTOMER_SEGMENT',
                          'REGION', 'COUNTRY', 'TOTAL_REVENUE', 'TOTAL_PROFIT',
                          'TOTAL_TRANSACTIONS', 'LAST_PURCHASE_DATE']
    performance['AVG_TRANSACTION_VALUE'] = performance['TOTAL_REVENUE'] / performance['TOTAL_TRANSACTIONS']
    performance['LAST_PURCHASE_DATE'] = pd.to_datetime(performance['LAST_PURCHASE_DATE'])
    performance['DAYS_SINCE_LAST_PURCHASE'] = (datetime.now() - performance['LAST_PURCHASE_DATE']).dt.days
    return performance.sort_values('TOTAL_REVENUE', ascending=False)


def get_regional_performance():
    """Compute regional performance from sales and customer data."""
    df = SALES_DATA.merge(CUSTOMERS_DATA, on='CUSTOMER_ID')
    
    performance = df.groupby('REGION').agg({
        'CUSTOMER_ID': 'nunique',
        'REVENUE': 'sum',
        'PROFIT': 'sum',
        'SALE_ID': 'count'
    }).reset_index()
    
    performance.columns = ['REGION', 'TOTAL_CUSTOMERS', 'TOTAL_REVENUE', 
                          'TOTAL_PROFIT', 'TOTAL_TRANSACTIONS']
    performance['AVG_TRANSACTION_VALUE'] = performance['TOTAL_REVENUE'] / performance['TOTAL_TRANSACTIONS']
    return performance.sort_values('TOTAL_REVENUE', ascending=False)


# Pre-compute views
MONTHLY_SALES_SUMMARY = get_monthly_sales_summary()
PRODUCT_PERFORMANCE = get_product_performance()
CUSTOMER_PERFORMANCE = get_customer_performance()
REGIONAL_PERFORMANCE = get_regional_performance()


# =============================================================================
# QUERY HELPER FUNCTIONS
# =============================================================================
def filter_sales_by_date(start_date, end_date):
    """Filter sales data by date range."""
    df = SALES_DATA.copy()
    df['SALE_DATE'] = pd.to_datetime(df['SALE_DATE'])
    mask = (df['SALE_DATE'] >= pd.to_datetime(start_date)) & (df['SALE_DATE'] <= pd.to_datetime(end_date))
    return df[mask]


def get_kpi_metrics(start_date, end_date):
    """Get KPI metrics for a date range."""
    filtered = filter_sales_by_date(start_date, end_date)
    
    if filtered.empty:
        return {
            'TOTAL_REVENUE': 0,
            'TOTAL_PROFIT': 0,
            'TOTAL_TRANSACTIONS': 0,
            'UNIQUE_CUSTOMERS': 0,
            'AVG_TRANSACTION_VALUE': 0
        }
    
    return {
        'TOTAL_REVENUE': filtered['REVENUE'].sum(),
        'TOTAL_PROFIT': filtered['PROFIT'].sum(),
        'TOTAL_TRANSACTIONS': len(filtered),
        'UNIQUE_CUSTOMERS': filtered['CUSTOMER_ID'].nunique(),
        'AVG_TRANSACTION_VALUE': filtered['REVENUE'].mean()
    }


def get_monthly_summary_for_range(start_date, end_date):
    """Get monthly summary filtered by date range."""
    df = MONTHLY_SALES_SUMMARY.copy()
    mask = (df['MONTH'] >= pd.to_datetime(start_date)) & (df['MONTH'] <= pd.to_datetime(end_date))
    return df[mask]


def get_product_revenue_for_range(start_date, end_date):
    """Get product revenue data for a date range."""
    filtered = filter_sales_by_date(start_date, end_date)
    df = filtered.merge(PRODUCTS_DATA, on='PRODUCT_ID')
    
    result = df.groupby(['PRODUCT_NAME', 'CATEGORY']).agg({
        'REVENUE': 'sum',
        'PROFIT': 'sum'
    }).reset_index()
    
    result.columns = ['PRODUCT_NAME', 'CATEGORY', 'TOTAL_REVENUE', 'TOTAL_PROFIT']
    return result.sort_values('TOTAL_REVENUE', ascending=False)


def get_regional_revenue_for_range(start_date, end_date):
    """Get regional revenue data for a date range."""
    filtered = filter_sales_by_date(start_date, end_date)
    df = filtered.merge(CUSTOMERS_DATA, on='CUSTOMER_ID')
    
    result = df.groupby('REGION').agg({
        'REVENUE': 'sum',
        'PROFIT': 'sum',
        'SALE_ID': 'count'
    }).reset_index()
    
    result.columns = ['REGION', 'TOTAL_REVENUE', 'TOTAL_PROFIT', 'TRANSACTIONS']
    return result.sort_values('TOTAL_REVENUE', ascending=False)


def get_customer_revenue_for_range(start_date, end_date):
    """Get customer revenue data for a date range."""
    filtered = filter_sales_by_date(start_date, end_date)
    df = filtered.merge(CUSTOMERS_DATA, on='CUSTOMER_ID')
    
    result = df.groupby(['CUSTOMER_NAME', 'CUSTOMER_SEGMENT', 'REGION']).agg({
        'REVENUE': 'sum',
        'PROFIT': 'sum'
    }).reset_index()
    
    result.columns = ['CUSTOMER_NAME', 'CUSTOMER_SEGMENT', 'REGION', 'TOTAL_REVENUE', 'TOTAL_PROFIT']
    return result.sort_values('TOTAL_REVENUE', ascending=False)


def get_sales_rep_performance_for_range(start_date, end_date):
    """Get sales rep performance for a date range."""
    filtered = filter_sales_by_date(start_date, end_date)
    
    result = filtered.groupby('SALES_REP').agg({
        'REVENUE': 'sum',
        'PROFIT': 'sum',
        'SALE_ID': 'count'
    }).reset_index()
    
    # Ensure column names match Snowflake's uppercase convention
    result.columns = ['SALES_REP', 'REVENUE', 'PROFIT', 'SALE_ID']
    return result.sort_values('REVENUE', ascending=False)
