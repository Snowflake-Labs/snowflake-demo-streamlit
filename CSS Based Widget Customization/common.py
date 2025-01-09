from string import Template
from textwrap import dedent
import streamlit as st
import inspect


class CodeExportParse:
    def __init__(self, fn) -> str:
        self.parse_text = dedent("".join(list(inspect.getsourcelines(fn))[0][1:]))


class HTML_Template:
    base_style = Template(
        dedent(
            """
            <style>
                $css
            </style>"""
        )
    )
    export_css_content = Template(
        dedent(
            '''
        css = """$css"""
        st.html(css)
        '''
        )
    )


class CopyToClipboard:
    def __init__(self, css_text: str, streamlit_code: str):
        self.css_text = css_text
        self.streamlit_code = streamlit_code
        with st.popover("Copy", icon=":material/content_copy:"):
            st.code(self.copy_to_clipboard())

    def copy_to_clipboard(self):
        copied_text = "\n\n".join(
            [
                HTML_Template.export_css_content.substitute(
                    css=HTML_Template.base_style.substitute(css=self.css_text)
                ),
                self.streamlit_code,
            ]
        )
        return copied_text


class MainCSS:
    initial_page_styles = """

.st-key-about_me button{
        border-radius:25px;
        height:50px;
        width:50px;
        box-shadow: 3px 5px 10px 0px rgba(128, 128, 128, 0.245);
        position:fixed;
        bottom:5rem;
        right:3rem;
    }

.st-key-css_main button{
        border-radius:25px;
        height:50px;
        width:50px;
        box-shadow: 3px 5px 10px 0px rgba(128, 128, 128, 0.245);
        position:fixed;
        bottom:9rem;
        right:3rem;
    }
div[data-testid="stAppViewContainer"]{
    background-color:white;
    margin-right:2rem;
    margin-top:2rem;
    margin-left:2rem;
    margin-bottom:4rem;
    border-radius:2rem;
}
div[data-testid="stSidebarCollapsedControl"]{
    margin-top:2rem;
    margin-left:2rem;
}
header[data-testid="stHeader"]{
    background-color:transparent;
    margin-top:2rem;
    margin-right:2rem;
}
div[data-testid="stDecoration"]{
    visibility:hidden;
}
div[data-testid="stApp"]{
    background: rgb(0,107,172);
    background: linear-gradient(180deg, rgba(0,107,172,1) 0%, rgba(34,103,210,1) 47%, rgba(0,212,255,1) 100%);
}
.st-key-about_me_img img{
    border: 2px solid #fff;
    -webkit-border-radius: 50%;
    -moz-border-radius: 50%;
    -ms-border-radius: 50%;
    -o-border-radius: 50%;
    border-radius: 50%;
    box-shadow: 3px 5px 10px 0px rgba(128, 128, 128, 0.245);  
}
.st-key-about_me_img h1{
    font-size:36px; 
    marging-bottom:2px;
}
.st-key-about_me_img h3{
    font-size:16px;
    padding-top:2px;
    padding-bottom:2px;
    padding-left:1rem;
    transform:translateY(-12px);
}
.st-key-about_me_img hr{
    margin-top:2px;
}
    """.strip()
