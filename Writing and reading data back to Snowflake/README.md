![](../shared_assets/sis-header.jpeg)

# CRUD App: Reading and Writing data from Snowflake
This app demonstrates how to read and write back data into Snowflake from a Streamlit app

## Prerequisites

#### Creating a Table

This step requires having `CREATE TABLE` and `SELECT` privileges on Tables or Schema ownership on a Schema. 

```sql
create or replace TABLE DB.SCHEMA.BUG_REPORT_DATA (
	AUTHOR VARCHAR(25),
	BUG_TYPE VARCHAR(25),
	COMMENT VARCHAR(100),
	DATE DATE,
	BUG_SEVERITY NUMBER(38,0)
);
```

#### Adding sample data  

Let's add some sample data into the table above

```sql
INSERT INTO DB.SCHEMA.BUG_REPORT_DATA (AUTHOR, BUG_TYPE, COMMENT, DATE, BUG_SEVERITY)
VALUES 
('John Doe', 'UI', 'The button is not aligned properly', '2024-03-01', 3),
('Aisha Patel', 'Performance', 'Page load time is too long', '2024-03-02', 5),
('Bob Johnson', 'Functionality', 'Unable to submit the form', '2024-03-03', 4),
('Sophia Kim', 'Security', 'SQL injection vulnerability found', '2024-03-04', 8),
('Michael Lee', 'Compatibility', 'Does not work on Internet Explorer', '2024-03-05', 2),
('Tyrone Johnson', 'UI', 'Font size is too small', '2024-03-06', 3),
('David Martinez', 'Performance', 'Search feature is slow', '2024-03-07', 4),
('Fatima Abadi', 'Functionality', 'Logout button not working', '2024-03-08', 3),
('William Taylor', 'Security', 'Sensitive data exposed in logs', '2024-03-09', 7),
('Nikolai Petrov', 'Compatibility', 'Not compatible with Safari', '2024-03-10', 2);
```


#### Viewing data

To view the most recent bugs filed

```sql
select * from DB.SCHEMA.BUG_REPORT_DATA order by DATE desc;
```