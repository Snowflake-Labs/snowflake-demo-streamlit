import streamlit as st
from streamlit.components.v1 import html
from common import HTML_Template, MainCSS

st.header("Welcome!")
st.html(HTML_Template.base_style.substitute(css=MainCSS.initial_page_styles))


st.write(
    """This application will help you understand the basic structure of some of the most popular Streamlit widgets. 
    Each page contains an editor to allow you to test these CSS changes."""
)

st.subheader("Features")
st.markdown(
    """
:blue[$~~~~$🆕] $~~$ CSS Selectors \n
:blue[$~~~~$🆕] $~~$ Custom Tips and Tricks \n
:blue[$~~~~$🆕] $~~$ Try your own styles \n
:blue[$~~~~$🆕] $~~$ Copy to clipboard  \n
"""
)
st.info(
    "🎈$~~$ This application CSS style requires **Streamlit 1.39** or greater."
)

st.subheader("Basic Structure")
st.html("src/static/main_structures.html")
st.subheader("Same style for multiple widgets")
st.write(
    "The `key` argument in Streamlit needs to be unique. In some cases, you want 1 or more widgets to share the same style. For this, the pseudo selector `:has()` needs be implemented."
)
st.write("**Example**")
example_columns = st.columns((1, 2))
example_columns[0].code(
    """
    st.button("Step 1", key="step_one")
    st.button("Step 2", key="step_two")
    st.button("Step 22", key="step_three")
    """
)
example_columns[1].code(
    """
    div:has(.st-key-step_one,.st-key-step_two, .st-key-step_three) button{
    /* button styles here */
    }
    /* OR */ 
    div[class*="st-key-step_"] button{
     /* button styles here */
    }
    """,
    language="css",
)


@st.dialog("Global Styles", width="large")
def css_show():
    st.code(MainCSS.initial_page_styles)


if st.button("", icon="🎨", type="primary", key="css_main"):
    css_show()
