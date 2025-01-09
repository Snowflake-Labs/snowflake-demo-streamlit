import streamlit as st
from textwrap import dedent
from common import HTML_Template, MainCSS, CodeExportParse

st.header("Expanders")
st.html(HTML_Template.base_style.substitute(css=MainCSS.initial_page_styles))


st.write(
    dedent(
        """To style a specific tab group, wrap it in a container with a `key` value to generate a class. \n\n
**Selectors**\n\n
- `details` : Controls the main container for the expander
-  `summary` : Controls the top bar
- `summary >  div[data-testid="stMarkdownContainer"] ` : Main container for label
- `summary > svg[data-testid="stExpanderToggleIcon"]` : Controls the expander icon
- `data-testid="stExpanderDetails"` : Selects the expander context"""
    )
)

st.subheader("Try it!")
code, preview = st.columns(2, vertical_alignment="top")


with code:
    expander_css = dedent(
        """

        
.st-key-styled_expander details{
    border-color:blue;
    }       
.st-key-styled_expander summary{
    background-color:#eaeaea;
    border-radius:.5rem;
    }

.st-key-styled_expander svg[data-testid="stExpanderToggleIcon"]{
    color:red;
    }

.st-key-styled_expander div[data-testid="stExpanderDetails"]{
    background-color:grey;
    }
.st-key-styled_expander div[data-testid="stExpanderDetails"] p {
    color:white;
    }




           """
    ).strip()
    styles = expander_css
    st.code(expander_css)


def expanders_code():
    with st.container(key="styled_expander"):
        with st.expander("Styled Expander"):
            st.write("This is a styled container")


st_code = str(CodeExportParse(fn=expanders_code).parse_text)
with preview:
    if st.toggle("Preview Style Changes", value=True):
        st.html(HTML_Template.base_style.substitute(css=styles))
    expanders_code()
    st.code(st_code)
