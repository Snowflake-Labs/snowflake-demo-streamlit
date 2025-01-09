import streamlit as st
from textwrap import dedent
from common import HTML_Template, MainCSS, CodeExportParse


st.header("Tabs")
st.html(HTML_Template.base_style.substitute(css=MainCSS.initial_page_styles))


st.write(
    dedent(
        """Tabs have multiple components, to style a specific tab group, wrap it in a container with a `key` value to generate a class. \n\n
**Stable selectors using data-baseweb property**\n\n
- `data-baseweb="tab-list"` : Main Tab Group
-  `button` : Each tab is a button 
-  `button[aria-selected="true"]` : Selects the current tab
- `data-baseweb="tab-border"` : Selects the ruler under the tabs
- `data-baseweb="tab-highlight"` : Selects the current tab ruler
- `data-baseweb="tab-panel"` : Selects the tab panel where content is rendered
"""
    )
)

st.subheader("Try it!")
code, preview = st.columns(2, vertical_alignment="top")


with code:
    tabs_css = dedent(
        """
/* This is the main container for tabs*/
.st-key-styled_tabs div[data-baseweb="tab-list"]{
    background:transparent;
}
/*Every tab is a button element*/
.st-key-styled_tabs button{
    width:33%;
    border-radius:10px;
}

/*Styles the selected tab*/
.st-key-styled_tabs button[aria-selected="true"]{
    background-color:#eaeaea;
}
.st-key-styled_tabs button[aria-selected="true"] p{
    color:blue;
    font-weight:bold;
}

/* This is the bottom ruler for tabs*/
.st-key-styled_tabs div[data-baseweb="tab-border"]{
    background-color:blue;
}

/* This highlights selected tab*/
.st-key-styled_tabs div[data-baseweb="tab-highlight"]{
    background-color:#5c5c5c;
    height:5px;
}

/* This is the bottom ruler for tabs*/
.st-key-styled_tabs div[data-baseweb="tab-border"]{
    background-color:blue;
}

/* This is the body of the tab content*/
.st-key-styled_tabs div[data-baseweb="tab-panel"]{
    background-color:#eaeaea;
}
           """
    ).strip()
    styles = tabs_css
    st.code(tabs_css)


def tabs_code():
    with st.container(key="styled_tabs"):
        tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])
        with tab1:
            st.write("This is tab 1")
        with tab2:
            st.write("This is tab 2")
        with tab3:
            st.write("This is tab 3")


st_code = str(CodeExportParse(fn=tabs_code).parse_text)
with preview:
    if st.toggle("Preview Style Changes", value=True):
        st.html(HTML_Template.base_style.substitute(css=styles))
    tabs_code()
    st.code(st_code)
