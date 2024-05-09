import streamlit as st
import datetime


def query_total_sales() -> str:
    """
    Query for getting the sum of money gained in dollars by day.
    """

    _filter = ""
    if st.session_state.customer_account_type != "All":
        _filter += f"and job_cost.customer_account_type = '{st.session_state.customer_account_type}'"
    if st.session_state.cloud != "All":
        _filter += f"and job_cost.cloud = '{st.session_state.cloud}'"

    first_date, last_date = st.session_state.dates
    first_date_minus_8 = first_date - datetime.timedelta(days=8)
    q = f"""
        with stg as (
            select
                job_cost.original_start_at as date,
                sum(SALES) as sales,
                count(job_cost.job_id) as job_counts
            from Key_Metrics_New_Product_DB.Key_Metrics_New_Product_S.JOB_COST job_cost
            where date(job_cost.created_on) >= '{first_date_minus_8}'
                and date(job_cost.created_on) <= '{last_date}'
                {_filter}
            group by 1
        )
        select date,
            round(sales, 0) as sales,
            sum(sales) over (
                order by date asc rows between 6 preceding and current row
            ) / 7 as sales_rolling_avg_7d,
            job_counts
        from stg
        """
    return q


def query_number_of_views_of_wifi_controller():
    """
    Query to get the number of views associated to a wifi controller running on a specific cloud provider and account type.
    """

    _filter = ""
    if st.session_state.customer_account_type != "All":
        _filter += f"and cloud_provider_view.customer_account_type = '{st.session_state.customer_account_type}'"
    if st.session_state.cloud != "All":
        _filter += f"and cloud_provider_view.cloud = '{st.session_state.cloud}'"

    first_date, last_date = st.session_state.dates
    first_date_minus_28 = first_date - datetime.timedelta(days=28)
    q = f"""
        with daily_agg as (
            select
                ds as date,
                sum(num_views) as daily_views
            from Key_Metrics_New_Product_DB.Key_Metrics_New_Product_S.cloud_provider_view cloud_provider_view
            where ds >= '{first_date_minus_28}'
                and ds <= '{last_date}'
                {_filter}
            group by 1)
        select
            date,
            daily_views,
            sum(daily_views) over (
                order by date asc rows between 27 preceding and current row
            ) as last_28_days_views,
            sum(daily_views) over (
                order by date asc rows between 6 preceding and current row
            ) as last_7_days_views
        from daily_agg
        """
    return q


def query_weekly_percentage_signature_customers_using_wifi_controller() -> str:
    """
    The query for our important, signature customers using our wifi controller platform.
    """

    query = """
    select * from Key_Metrics_New_Product_DB.Key_Metrics_New_Product_S.penetration
    """
    return query


def query_active_customer_accounts() -> str:
    """
    Query for active customer accounts using a wifi controller filtered by a cloud provider or an account type.
    """

    _filter = ""
    if st.session_state.customer_account_type != "All":
        _filter += f"and exec.customer_account_type = '{st.session_state.customer_account_type}'"
    if st.session_state.cloud != "All":
        _filter += f"and exec.cloud = '{st.session_state.cloud}'"
    first_date, _ = st.session_state.dates
    first_date_minus_28 = first_date - datetime.timedelta(days=28)
    q = f"""
    with begin_dates as (
        select
            dateadd('month', -1, (min(_date)))::date as bdate
        from Key_Metrics_New_Product_DB.Key_Metrics_New_Product_S.calendar
        ),
    combined as (
        select
            distinct date(created_on) as ds,
            ACCOUNT_ID as account_id
        from Key_Metrics_New_Product_DB.Key_Metrics_New_Product_S.executes exec
        where true
            {_filter}
            and date(created_on) >= '{first_date_minus_28}'
            and date(created_on) >= (
                select bdate -7
                from begin_dates
            )
        ),
        dau as (
            select
                ds,
                count(distinct account_id) as daily_active_cnt,
                avg(daily_active_cnt) over (
                    order by ds rows between 6 preceding and current row
                )::number as daily_moving_avg_7_days
            from combined
            group by 1
        ),
        wau as (
            select
                t1.ds,
                count(distinct t2.account_id) as weekly_active_cnt
            from combined t1
                cross join combined t2
            where to_date(t2.ds) > to_date(t1.ds) - 7
                and to_date(t2.ds) <= to_date(t1.ds)
            group by 1
        ),
        mau as (
            select t1.ds,
                count(distinct t2.account_id) as monthly_active_cnt
            from combined t1
                cross join combined t2
            where to_date(t2.ds) > to_date(t1.ds) -28
                and to_date(t2.ds) <= to_date(t1.ds)
            group by 1
        )
        select mau.ds as date,
            daily_active_cnt as daily,
            weekly_active_cnt as last_7_days,
            monthly_active_cnt as last_28_days,
            daily_moving_avg_7_days
        from mau
            inner join wau on mau.ds = wau.ds
            inner join dau on mau.ds = dau.ds
    """
    return q
