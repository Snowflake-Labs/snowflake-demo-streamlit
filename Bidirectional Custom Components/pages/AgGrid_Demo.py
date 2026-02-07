# Import python packages
import streamlit as st

from st_aggrid import AgGrid
import pandas as pd


# Write directly to the app
st.title(f"st-aggrid Demo in SiS :balloon:")

df = pd.read_csv('./data/airline-safety.csv')

st.subheader('Dataframe view')
st.dataframe(df)

st.subheader('AgGrid view')
AgGrid(df)