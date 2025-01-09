import streamlit as st
from textwrap import dedent
from common import HTML_Template, MainCSS, CodeExportParse

st.header("Dialogs")
st.html(HTML_Template.base_style.substitute(css=MainCSS.initial_page_styles))


st.write(
    "To style a specific container, assign a value to the `key` argument to create a CSS class. Using the `:has` pseudo selector in combination with containers, dialogs can be diferentiated from each other.  "
)

st.subheader("Try it!")
code, preview = st.columns(2, vertical_alignment="top")


with code:
    dialog_css = dedent(
        """
/*USES THE HAS SELECTOR TO FILTER BY THE NESTED CONTAINER*/

div[role="dialog"]:has(.st-key-large){
    width:85%;
}

div[role="dialog"]:has(.st-key-medium){
    width:65%;
}
           """
    )
    styles = dialog_css
    st.code(dialog_css)


def dialogs_code():
    @st.dialog("Large Dialog")
    def big_dialog():
        with st.container(key="large"):
            st.write("This now uses 85% of the screen")

    @st.dialog("Medium")
    def medium_dialog():
        with st.container(key="medium"):
            st.write("This now uses 65% of the screen")

    if st.button("Open Large", use_container_width=True):
        big_dialog()
    if st.button("Open Medium", use_container_width=True):
        medium_dialog()


st.html(HTML_Template.base_style.substitute(css=styles))
st_code = str(CodeExportParse(fn=dialogs_code).parse_text)
with preview:
    dialogs_code()
    st.code(st_code)
