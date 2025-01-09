import streamlit as st
from textwrap import dedent
from common import HTML_Template, MainCSS, CodeExportParse


st.header("Headers", anchor=False, divider=True)
st.html(HTML_Template.base_style.substitute(css=MainCSS.initial_page_styles))

st.write(
    dedent(
        """Headers do not have a `key` argument on the widget definition. 
    To style a specific widget, wrapping it in a `st.container` will allow you to isolate the specific widget.\n\n
- `st.title` -> `H1`
- `st.header` -> `H2`
- `st.subheader` -> `H3`
    """
    )
)

st.subheader("Try it!")
code, preview = st.columns(2, vertical_alignment="top")


with code:
    headers_css = dedent(
        """

.st-key-header_style_one h1{
        color:red;
        font-weight:bold;
        }
.st-key-header_style_one h2{
        background-color:grey;
        color:black;
        padding-left:10px;
        border-radius:25px;
    }
.st-key-header_style_one h3{
        background-color:black;
        color:white;
        padding-left:10px;
        margin:10px;
    }

           """
    )
    styles = headers_css
    st.code(headers_css)
    


def headers_code():
    with st.container(key="header_style_one"):
        st.title("Streamlit", anchor=False)
        st.header("Styles", anchor=False)
        st.subheader("Sample", anchor=False)


st_code = str(CodeExportParse(fn=headers_code).parse_text)

with preview:
    if st.toggle("Preview Style Changes", value=True):
        st.html(HTML_Template.base_style.substitute(css=styles))
    headers_code()
    st.code(st_code)
