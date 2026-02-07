import streamlit as st

# Configure page to use wide mode
st.set_page_config(layout="wide", page_title="Custom Components Demo")


st.title("Streamlit Custom Components Demo 🎨")

st.markdown("""
    This app demonstrates various custom components available in Streamlit.
    Select a demo from the sidebar to explore different components!
""")

st.header("Welcome to Custom Components! 👋")
st.markdown("""
        ### What are Custom Components?
        Custom components extend Streamlit's capabilities by allowing you to:
        - Add interactive elements
        - Integrate third-party libraries
        - Create unique visualizations
        
        ### Featured Components in this Demo:
        1. **AgGrid**: AgGrid is an awesome grid for web frontend. 
        2. **ECharts**: ECharts is an awesome charting library for web frontend. 
""")