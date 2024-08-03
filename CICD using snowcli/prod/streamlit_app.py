import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")


@st.cache_data
def generate_fake_data_for_demo(seed=36) -> pd.DataFrame:
    """
    Generates a dataframe of customers and views for
    this demo, and caches it. If you are using this demo,
    you ideally will replace this with your own data.
    """

    df = pd.DataFrame(
        {
            "date": pd.date_range(start="1/1/2020", periods=100),
            "customers": np.random.randint(100, 1000, 100),
        }
    )
    df["customers"] = df["customers"].cumsum()
    np.random.seed(seed)
    df["views"] = np.random.randint(100, 1000, 100)
    df["views"] = df["views"] * np.log(df.index) * np.random.uniform(1, 1.6, 100)
    df["views"][0] = 0

    return df


st.title("Key Metrics App")

session = st.connection('snowflake').session()

df = generate_fake_data_for_demo()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Number of customers")
    taba, tabb = st.tabs(["Chart", "Data"])
    taba.line_chart(df.set_index("date")["customers"])
    tabb.write(df)


with col2:
    st.subheader("Views per day")
    tabc, tabd = st.tabs(["Chart", "Data"])
    tabc.line_chart(df.set_index("date")["views"])
    tabd.write(df)


df["views_per_customer"] = df["views"] / df["customers"]
st.subheader("Views per customer")
st.line_chart(df.set_index("date")["views_per_customer"])
