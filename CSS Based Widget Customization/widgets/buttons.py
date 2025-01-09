import streamlit as st
from textwrap import dedent
from common import HTML_Template, MainCSS, CodeExportParse

st.header("Buttons")
st.html(HTML_Template.base_style.substitute(css=MainCSS.initial_page_styles))


st.write(
    """
You can isolate and style buttons by adding styles to the generated CSS class in the DOM named after the `key` argument in you widget. 
These styles apply with some minor differences to `st.button`, `st.form_submit_button` and `st.popover`. 
The basic structure of a button will also depend on the precense of an `icon` argument
"""
)

st.subheader("Try it!")
code, preview = st.columns(2, vertical_alignment="top")


with code:
    button_css = dedent(
        """

.st-key-styled_button button{
        border-radius:25px;
        box-shadow: 3px 5px 10px 0px rgba(128, 128, 128, 0.245);
        border-color:white;
    }
.st-key-styled_button:hover button{
        border-color:white;
    }
.st-key-styled_button :focus:not(:active) {
        border-color:white;
    }
.st-key-styled_button p{
        color:grey;
        font-weight: bold;
    }
.st-key-styled_button :active p {
        color:white;
        font-weight: bold;
    }
.st-key-styled_button span[data-testid="stIconMaterial"]{
        color:orange;
    }
.st-key-styled_button :active span[data-testid="stIconMaterial"]{
         color:white;
    }
           """
    ).strip()

    # styles = st_monaco(
    #     value=button_css,
    #     height="400px",
    #     language="css",
    #     lineNumbers=True,
    #     minimap=False,
    # )
    styles = button_css
    st.code(button_css)

def button_st_code():
    st.button(
        "Sample Button",
        key="styled_button",
        icon="🏠",
    )


st_code = str(CodeExportParse(fn=button_st_code).parse_text)

with preview:
    with st.expander("Button widget structure"):
        st.html("src/static/buttons_tree.html")
    if st.toggle("Preview Style Changes", value=True):
        st.html(HTML_Template.base_style.substitute(css=styles))
    button_st_code()
    st.code(st_code)
