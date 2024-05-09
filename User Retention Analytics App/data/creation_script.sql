------------------------------------------------------------
-- Database and Schema creation
------------------------------------------------------------

-- Database and Schema creation
CREATE DATABASE SampleDatabase;
CREATE SCHEMA UserRetention;
CREATE STAGE UserRetentionStage;

------------------------------------------------------------
-- Table Creation
------------------------------------------------------------

CREATE OR REPLACE TABLE PRODUCT_1_RETENTION_BY_MONTH (
    COHORT_MONTH DATE,
    ACTION_MONTH DATE,
    NUM_USERS NUMBER
);

CREATE OR REPLACE TABLE PRODUCT_2_RETENTION_BY_MONTH (
    COHORT_MONTH DATE,
    ACTION_MONTH DATE,
    NUM_USERS NUMBER
);

CREATE OR REPLACE TABLE PRODUCT_1_RETENTION_BY_WEEK (
    COHORT_WEEK DATE,
    ACTION_WEEK DATE,
    NUM_USERS NUMBER
);

CREATE OR REPLACE TABLE PRODUCT_2_RETENTION_BY_WEEK (
    COHORT_WEEK DATE,
    ACTION_WEEK DATE,
    NUM_USERS NUMBER
);

CREATE OR REPLACE TABLE PRODUCT_1_ACTIVITY_BY_DAY (
    USERNAME VARCHAR,
    DAY_OF_USE DATE
);

CREATE OR REPLACE TABLE PRODUCT_2_VIEWS_ACTIVITY_BY_DAY (
    USERNAME VARCHAR,
    DAY_OF_USE DATE
);

CREATE OR REPLACE TABLE PRODUCT_2_ACTIVITY_BY_DAY (
    USERNAME VARCHAR,
    DAY_OF_USE DATE
);


------------------------------------------------------------
-- Copy into tables
------------------------------------------------------------

COPY INTO PRODUCT_1_RETENTION_BY_MONTH
FROM '@UserRetentionStage'
FILES = ('product_1_retention_by_month.csv')
FILE_FORMAT = (
    TYPE = CSV
    SKIP_HEADER = 1
);

COPY INTO PRODUCT_2_RETENTION_BY_MONTH
FROM '@UserRetentionStage'
FILES = ('product_2_retention_by_month.csv')
FILE_FORMAT = (
    TYPE = CSV
    SKIP_HEADER = 1
);

COPY INTO PRODUCT_1_RETENTION_BY_WEEK
FROM '@UserRetentionStage'
FILES = ('product_1_retention_by_week.csv')
FILE_FORMAT = (
    TYPE = CSV
    SKIP_HEADER = 1
);

COPY INTO PRODUCT_2_RETENTION_BY_WEEK
FROM '@UserRetentionStage'
FILES = ('product_2_retention_by_week.csv')
FILE_FORMAT = (
    TYPE = CSV
    SKIP_HEADER = 1
);

COPY INTO PRODUCT_1_ACTIVITY_BY_DAY
FROM '@UserRetentionStage'
FILES = ('product_1_activity_by_day.csv')
FILE_FORMAT = (
    TYPE = CSV
    SKIP_HEADER = 1
);

COPY INTO PRODUCT_2_VIEWS_ACTIVITY_BY_DAY
FROM '@UserRetentionStage'
FILES = ('product_2_views_activity_by_day.csv')
FILE_FORMAT = (
    TYPE = CSV
    SKIP_HEADER = 1
);

COPY INTO PRODUCT_2_ACTIVITY_BY_DAY
FROM '@UserRetentionStage'
FILES = ('product_2_activity_by_day.csv')
FILE_FORMAT = (
    TYPE = CSV
    SKIP_HEADER = 1
);