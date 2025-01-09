import streamlit as st
from textwrap import dedent
from common import HTML_Template, MainCSS, CodeExportParse

st.header("Sliders")
st.html(HTML_Template.base_style.substitute(css=MainCSS.initial_page_styles))


st.write(
    "Sliders can be customized by changing the thumb and track color and changing the thumb shape using clip-paths and svg."
)

st.subheader("Try it!")
code, preview = st.columns(2, vertical_alignment="top")


with code:
    container_css = dedent(
        """
.st-key-slider{
        padding-left:10px;
        padding-right:10px;
        }
.st-key-slider div[data-testid="stSliderThumbValue"]{
    transform:translateY(27px);
    color:white;
    font-size:small;
    position:relative;
}
.st-key-slider div[role="slider"]{
    height:30px;
    width:45px;
    border-radius:0px;
    background-color:red;
    top:10px;
    clip-path: polygon(1% 16%, 18% 95%, 83% 95%, 100% 14%, 68% 45%, 51% 0, 33% 47%);
}
           """
    ).strip()
    styles = container_css
    st.code(container_css)


def sliders_code():
    st.slider(
        "Simple Slider",
        value=1,
        max_value=25,
        min_value=1,
        key="slider",
    )


st_code = str(CodeExportParse(fn=sliders_code).parse_text)
with preview:
    if st.toggle("Preview Style Changes", value=True):
        st.html(HTML_Template.base_style.substitute(css=styles))
    sliders_code()
    st.code(st_code)
