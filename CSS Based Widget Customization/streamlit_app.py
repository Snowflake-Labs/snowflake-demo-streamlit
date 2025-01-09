import streamlit as st
from common import HTML_Template, MainCSS

st.set_page_config(layout="wide")
st.html(HTML_Template.base_style.substitute(css=MainCSS.initial_page_styles))
nav_menu = {
    "Main": [
        st.Page(
            title="Welcome",
            page="home/home.py",
            icon="🏠",
        )
    ],
    "Widgets": [
        st.Page(
            title="Buttons",
            page="widgets/buttons.py",
            icon="🔘",
        ),
        st.Page(
            title="Headers",
            page="widgets/headers.py",
            icon="📃",
        ),
        st.Page(
            title="Sliders",
            page="widgets/sliders.py",
            icon="🎚️",
        ),
    ],
    "Layouts": [
        st.Page(
            title="Containers",
            page="layouts/containers.py",
            icon="🫙",
        ),
        st.Page(title="Dialogs", page="layouts/dialogs.py", icon="💬"),
        st.Page(title="Tabs", page="layouts/tabs.py", icon="📁"),
        st.Page(
            title="Expanders",
            page="layouts/expanders.py",
            icon="🗃️",
        ),
    ],
}
nav = st.navigation(nav_menu, position="sidebar")
nav.run()
