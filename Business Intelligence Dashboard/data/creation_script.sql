-- Business Intelligence Dashboard Demo - Data Creation Script
-- This script creates sample data for a comprehensive BI dashboard

-- Create database and schema
CREATE DATABASE IF NOT EXISTS BI_DASHBOARD_DB;
CREATE SCHEMA IF NOT EXISTS BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA;

USE DATABASE BI_DASHBOARD_DB;
USE SCHEMA BI_DASHBOARD_SCHEMA;

-- Create Products table
CREATE OR REPLACE TABLE PRODUCTS (
    PRODUCT_ID INT PRIMARY KEY,
    PRODUCT_NAME VARCHAR(100),
    CATEGORY VARCHAR(50),
    PRICE DECIMAL(10,2),
    COST DECIMAL(10,2)
);

-- Create Customers table
CREATE OR REPLACE TABLE CUSTOMERS (
    CUSTOMER_ID INT PRIMARY KEY,
    CUSTOMER_NAME VARCHAR(100),
    CUSTOMER_SEGMENT VARCHAR(50),
    REGION VARCHAR(50),
    COUNTRY VARCHAR(50),
    ACQUISITION_DATE DATE
);

-- Create Sales table
CREATE OR REPLACE TABLE SALES (
    SALE_ID INT PRIMARY KEY,
    CUSTOMER_ID INT,
    PRODUCT_ID INT,
    SALE_DATE DATE,
    QUANTITY INT,
    REVENUE DECIMAL(12,2),
    COST DECIMAL(12,2),
    PROFIT DECIMAL(12,2),
    SALES_REP VARCHAR(100),
    FOREIGN KEY (CUSTOMER_ID) REFERENCES CUSTOMERS(CUSTOMER_ID),
    FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCTS(PRODUCT_ID)
);

-- Create Marketing Campaigns table
CREATE OR REPLACE TABLE MARKETING_CAMPAIGNS (
    CAMPAIGN_ID INT PRIMARY KEY,
    CAMPAIGN_NAME VARCHAR(100),
    CAMPAIGN_TYPE VARCHAR(50),
    START_DATE DATE,
    END_DATE DATE,
    BUDGET DECIMAL(12,2),
    CLICKS INT,
    IMPRESSIONS INT,
    CONVERSIONS INT
);

-- Insert sample Products data
INSERT INTO PRODUCTS VALUES
(1, 'Laptop Pro', 'Electronics', 1299.99, 800.00),
(2, 'Smartphone X', 'Electronics', 899.99, 500.00),
(3, 'Tablet Ultra', 'Electronics', 599.99, 350.00),
(4, 'Wireless Headphones', 'Electronics', 199.99, 80.00),
(5, 'Smart Watch', 'Electronics', 299.99, 150.00),
(6, 'Gaming Console', 'Electronics', 499.99, 300.00),
(7, 'Office Chair', 'Furniture', 249.99, 120.00),
(8, 'Standing Desk', 'Furniture', 449.99, 200.00),
(9, 'Bookshelf', 'Furniture', 149.99, 70.00),
(10, 'Coffee Maker', 'Appliances', 79.99, 35.00);

-- Insert sample Customers data
INSERT INTO CUSTOMERS VALUES
(1, 'TechCorp Inc', 'Enterprise', 'North America', 'USA', '2020-01-15'),
(2, 'StartupHub', 'SMB', 'North America', 'Canada', '2021-03-22'),
(3, 'GlobalTech Ltd', 'Enterprise', 'Europe', 'UK', '2019-11-08'),
(4, 'InnovateCo', 'SMB', 'Europe', 'Germany', '2022-05-10'),
(5, 'FutureTech', 'Enterprise', 'Asia Pacific', 'Japan', '2020-09-14'),
(6, 'SmallBiz Solutions', 'SMB', 'Asia Pacific', 'Australia', '2021-12-03'),
(7, 'MegaCorp', 'Enterprise', 'North America', 'USA', '2018-06-25'),
(8, 'LocalTech', 'SMB', 'Europe', 'France', '2022-01-18'),
(9, 'TechStart', 'SMB', 'Asia Pacific', 'Singapore', '2021-07-30'),
(10, 'EnterpriseMax', 'Enterprise', 'North America', 'USA', '2019-04-12');

-- Insert sample Marketing Campaigns data
INSERT INTO MARKETING_CAMPAIGNS VALUES
(1, 'Q1 Product Launch', 'Product Launch', '2024-01-01', '2024-03-31', 50000, 125000, 2500000, 3200),
(2, 'Summer Sale', 'Seasonal', '2024-06-01', '2024-08-31', 30000, 80000, 1600000, 2100),
(3, 'Back to School', 'Seasonal', '2024-08-01', '2024-09-30', 25000, 65000, 1300000, 1800),
(4, 'Holiday Campaign', 'Seasonal', '2024-11-01', '2024-12-31', 75000, 180000, 3600000, 4500),
(5, 'Brand Awareness', 'Brand', '2024-01-01', '2024-12-31', 40000, 200000, 8000000, 1500);

-- Generate sample Sales data using a more sophisticated approach
INSERT INTO SALES
WITH date_range AS (
    SELECT DATEADD(day, seq4(), '2023-01-01') AS sale_date
    FROM TABLE(GENERATOR(rowcount => 730)) -- 2 years of data
),
sales_data AS (
    SELECT 
        row_number() OVER (ORDER BY d.sale_date, ABS(RANDOM()) % 1000) AS sale_id,
        (ABS(RANDOM()) % 10) + 1 AS customer_id,
        (ABS(RANDOM()) % 10) + 1 AS product_id,
        d.sale_date,
        (ABS(RANDOM()) % 10) + 1 AS quantity,
        CASE 
            WHEN EXTRACT(MONTH FROM d.sale_date) IN (11, 12) THEN 1.3 -- Holiday boost
            WHEN EXTRACT(MONTH FROM d.sale_date) IN (6, 7, 8) THEN 1.15 -- Summer boost
            ELSE 1.0
        END AS seasonal_factor,
        ARRAY_CONSTRUCT('John Smith', 'Sarah Johnson', 'Mike Davis', 'Lisa Wilson', 'Tom Brown')[ABS(RANDOM()) % 5] AS sales_rep
    FROM date_range d
    WHERE ABS(RANDOM()) % 100 < 70 -- 70% chance of sale on any given day
)
SELECT 
    s.sale_id,
    s.customer_id,
    s.product_id,
    s.sale_date,
    s.quantity,
    ROUND(p.price * s.quantity * s.seasonal_factor, 2) AS revenue,
    ROUND(p.cost * s.quantity, 2) AS cost,
    ROUND((p.price - p.cost) * s.quantity * s.seasonal_factor, 2) AS profit,
    s.sales_rep
FROM sales_data s
JOIN PRODUCTS p ON s.product_id = p.product_id
WHERE s.sale_date <= CURRENT_DATE();

-- Create some summary views for the dashboard
CREATE OR REPLACE VIEW MONTHLY_SALES_SUMMARY AS
SELECT 
    DATE_TRUNC('MONTH', sale_date) AS month,
    SUM(revenue) AS total_revenue,
    SUM(cost) AS total_cost,
    SUM(profit) AS total_profit,
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM SALES
GROUP BY DATE_TRUNC('MONTH', sale_date)
ORDER BY month;

CREATE OR REPLACE VIEW PRODUCT_PERFORMANCE AS
SELECT 
    p.product_name,
    p.category,
    SUM(s.quantity) AS total_quantity_sold,
    SUM(s.revenue) AS total_revenue,
    SUM(s.profit) AS total_profit,
    AVG(s.profit / s.quantity) AS avg_profit_per_unit,
    COUNT(DISTINCT s.customer_id) AS unique_customers
FROM SALES s
JOIN PRODUCTS p ON s.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC;

CREATE OR REPLACE VIEW CUSTOMER_PERFORMANCE AS
SELECT 
    c.customer_name,
    c.customer_segment,
    c.region,
    c.country,
    SUM(s.revenue) AS total_revenue,
    SUM(s.profit) AS total_profit,
    COUNT(*) AS total_transactions,
    AVG(s.revenue) AS avg_transaction_value,
    MAX(s.sale_date) AS last_purchase_date,
    DATEDIFF('day', MAX(s.sale_date), CURRENT_DATE()) AS days_since_last_purchase
FROM SALES s
JOIN CUSTOMERS c ON s.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_segment, c.region, c.country
ORDER BY total_revenue DESC;

CREATE OR REPLACE VIEW REGIONAL_PERFORMANCE AS
SELECT 
    c.region,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    SUM(s.revenue) AS total_revenue,
    SUM(s.profit) AS total_profit,
    AVG(s.revenue) AS avg_transaction_value,
    COUNT(*) AS total_transactions
FROM SALES s
JOIN CUSTOMERS c ON s.customer_id = c.customer_id
GROUP BY c.region
ORDER BY total_revenue DESC;

-- Grant permissions (adjust as needed for your environment)
GRANT USAGE ON DATABASE BI_DASHBOARD_DB TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA TO ROLE PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA TO ROLE PUBLIC;
GRANT SELECT ON ALL VIEWS IN SCHEMA BI_DASHBOARD_DB.BI_DASHBOARD_SCHEMA TO ROLE PUBLIC; 