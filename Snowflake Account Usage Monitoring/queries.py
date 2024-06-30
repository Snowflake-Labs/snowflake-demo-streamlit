def queries_query(name: str, date_from: str, date_to: str) -> str:
    """
    Get queries executed in a given warehouse.
    """
    return f"""
            SELECT
                TOTAL_ELAPSED_TIME,
                QUERY_TEXT,
                WAREHOUSE_NAME
            FROM
                SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
            WHERE
                WAREHOUSE_NAME = '{name}'
                AND START_TIME BETWEEN '{date_from}' :: DATE
                AND '{date_to}' :: DATE;
            """


def query_count_query(
    date_from: str,
    date_to: str,
    warehouse_name: str,
    min_num_execution: str,
    limit: str,
) -> str:
    """
    Get how many times does a query have been executed and the max duration of execution time.
    """
    return f"""
            SELECT
                QUERY_TEXT,
                COUNT(*) AS NUMBER_OF_QUERIES,
                SUM(TOTAL_ELAPSED_TIME) / 1000 AS EXECUTION_SECONDS,
                SUM(TOTAL_ELAPSED_TIME) /(1000 * 60) AS EXECUTION_MINUTES,
                SUM(TOTAL_ELAPSED_TIME) /(1000 * 60 * 60) AS EXECUTION_HOURS
            FROM
                SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY Q
            WHERE
                TOTAL_ELAPSED_TIME > 0
                AND WAREHOUSE_NAME = '{warehouse_name}'
                AND Q.START_TIME BETWEEN '{date_from}' :: DATE
                AND '{date_to}' :: DATE
            GROUP BY
                QUERY_TEXT
            HAVING
                COUNT(*) >= {min_num_execution}
            ORDER BY
                NUMBER_OF_QUERIES DESC
            LIMIT
                {limit};
            """


def consumption_per_service_type_query(date_from: str, date_to: str) -> str:
    """
    Get how many credits have been spent by differents services (Warehouses, pipes, etc)
    """
    return f"""
            SELECT
                DATE_TRUNC('HOUR', START_TIME) AS START_TIME,
                NAME,
                SERVICE_TYPE,
                SUM(CREDITS_USED) AS CREDITS_USED,
                SUM(CREDITS_USED_COMPUTE) AS CREDITS_COMPUTE,
                SUM(CREDITS_USED_CLOUD_SERVICES) AS CREDITS_CLOUD
            FROM
                SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
            WHERE
                START_TIME BETWEEN '{date_from}' :: DATE
                AND '{date_to}' :: DATE
            GROUP BY
                START_TIME,
                NAME,
                SERVICE_TYPE;
            """


def storage_query(date_from: str, date_to: str) -> str:
    """
    Get storage consumption by warehouse.
    """
    return f"""
            SELECT
                CONVERT_TIMEZONE('UTC', USAGE_DATE) AS USAGE_DATE,
                DATABASE_NAME AS OBJECT_NAME,
                'DATABASE' AS OBJECT_TYPE,
                MAX(AVERAGE_DATABASE_BYTES) AS DATABASE_BYTES,
                MAX(AVERAGE_FAILSAFE_BYTES) AS FAILSAFE_BYTES,
                0 AS STAGE_BYTES
            FROM
                SNOWFLAKE.ACCOUNT_USAGE.DATABASE_STORAGE_USAGE_HISTORY
            WHERE
                USAGE_DATE >= DATE_TRUNC(
                    'DAY',
                    ('{date_from}T00:00:00Z') :: TIMESTAMP_NTZ
                )
                AND USAGE_DATE < DATE_TRUNC('DAY', ('{date_to}T00:00:00Z') :: TIMESTAMP_NTZ)
            GROUP BY
                USAGE_DATE,
                OBJECT_NAME,
                OBJECT_TYPE
            UNION
            ALL
            SELECT
                CONVERT_TIMEZONE('UTC', USAGE_DATE) AS USAGE_DATE,
                'STAGES' AS OBJECT_NAME,
                'STAGE' AS OBJECT_TYPE,
                0 AS DATABASE_BYTES,
                0 AS FAILSAFE_BYTES,
                MAX(AVERAGE_STAGE_BYTES) AS STAGE_BYTES
            FROM
                SNOWFLAKE.ACCOUNT_USAGE.STAGE_STORAGE_USAGE_HISTORY
            WHERE
                USAGE_DATE >= DATE_TRUNC(
                    'DAY',
                    ('{date_from}T00:00:00Z') :: TIMESTAMP_NTZ
                )
                AND USAGE_DATE < DATE_TRUNC('DAY', ('{date_to}T00:00:00Z') :: TIMESTAMP_NTZ)
            GROUP BY
                USAGE_DATE,
                OBJECT_NAME,
                OBJECT_TYPE;
            """


def data_transfer_query(date_from: str, date_to: str) -> str:
    """
    Get how much data have been trasfered over different regions.
    """
    return f"""
            SELECT
                DATE_TRUNC('HOUR', CONVERT_TIMEZONE('UTC', START_TIME)) AS START_TIME,
                TARGET_CLOUD,
                TARGET_REGION,
                TRANSFER_TYPE,
                SUM(BYTES_TRANSFERRED) AS BYTES_TRANSFERRED
            FROM
                SNOWFLAKE.ACCOUNT_USAGE.DATA_TRANSFER_HISTORY
            WHERE
                START_TIME BETWEEN '{date_from}' :: DATE
                AND '{date_to}' :: DATE
            GROUP BY
                START_TIME,
                TARGET_CLOUD,
                TARGET_REGION,
                TRANSFER_TYPE;
            """


def credits_by_users_query(date_from: str, date_to: str, limit: str) -> str:
    """
    Get approximately how many credits have spent users in a specific timeframe.
    """
    return f"""
            WITH USER_HOUR_EXECUTION_CTE AS (
                SELECT
                        USER_NAME,
                        WAREHOUSE_NAME,
                        DATE_TRUNC('HOUR', START_TIME) AS START_TIME_HOUR,
                        SUM(EXECUTION_TIME) AS USER_HOUR_EXECUTION_TIME
                FROM
                        SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
                WHERE
                        WAREHOUSE_NAME IS NOT NULL
                        AND EXECUTION_TIME > 0
                        AND START_TIME BETWEEN '{date_from}' :: DATE
                        AND '{date_to}' :: DATE
                GROUP BY
                        USER_NAME,
                        WAREHOUSE_NAME,
                        START_TIME_HOUR
            ),
            HOUR_EXECUTION_CTE AS (
                SELECT
                        START_TIME_HOUR,
                        WAREHOUSE_NAME,
                        SUM(USER_HOUR_EXECUTION_TIME) AS HOUR_EXECUTION_TIME
                FROM
                        USER_HOUR_EXECUTION_CTE
                GROUP BY
                        START_TIME_HOUR,
                        WAREHOUSE_NAME
            ),
            APPROXIMATE_CREDITS AS (
                SELECT
                        UHE.USER_NAME,
                        WMH.WAREHOUSE_NAME,
                        (
                                UHE.USER_HOUR_EXECUTION_TIME / HE.HOUR_EXECUTION_TIME
                        ) * WMH.CREDITS_USED AS APPROXIMATE_CREDITS_USED
                FROM
                        USER_HOUR_EXECUTION_CTE UHE
                        JOIN HOUR_EXECUTION_CTE HE ON UHE.START_TIME_HOUR = HE.START_TIME_HOUR
                        AND HE.WAREHOUSE_NAME = UHE.WAREHOUSE_NAME
                        JOIN SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY WMH ON WMH.WAREHOUSE_NAME = UHE.WAREHOUSE_NAME
                        AND WMH.START_TIME = UHE.START_TIME_HOUR
            )
            SELECT
                USER_NAME,
                WAREHOUSE_NAME,
                SUM(APPROXIMATE_CREDITS_USED) AS APPROXIMATE_CREDITS_USED
            FROM
                APPROXIMATE_CREDITS
            GROUP BY
                USER_NAME,
                WAREHOUSE_NAME
            ORDER BY
                APPROXIMATE_CREDITS_USED DESC
            LIMIT
                {limit};
            """
