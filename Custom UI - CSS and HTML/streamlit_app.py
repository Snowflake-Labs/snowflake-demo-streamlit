import inspect
import streamlit as st
from streamlit.errors import StreamlitAPIException
from streamlit_extras.echo_expander import echo_expander


st.set_page_config(layout="wide")


def stylable_container(key, css_styles, wrapper_style=""):
    """
    Insert a container into your app which you can style using CSS.
    This is useful to style specific elements in your app.

    Args:
        key (str): The key associated with this container. This needs to be unique since all styles will be
            applied to the container with this key.
        css_styles (str | List[str]): The CSS styles to apply to the container elements.
            This can be a single CSS block or a list of CSS blocks.
        wrapper_style (str): (optional) Styles to apply to the wrapping container. Do not wrap in { }.

    Returns: A container object.
    """
    if isinstance(css_styles, str):
        css_styles = [css_styles]

    # Remove unneeded spacing that is added by the style markdown:
    css_styles.append(
        """
> div:first-child {
    display: none;
}
"""
    )

    style_text = """
<style>
"""
    if wrapper_style:
        style_text += f"""
    div[data-testid="stVerticalBlockBorderWrapper"]:has(
            > div
            > div[data-testid="stVerticalBlock"]
            > div.element-container
            > div.stMarkdown
            > div[data-testid="stMarkdownContainer"]
            > p
            > span.{key}
        ) {{
        {wrapper_style}
        }}
"""

    for style in css_styles:
        style_text += f"""

div[data-testid="stVerticalBlock"]:has(> div.element-container > div.stMarkdown > div[data-testid="stMarkdownContainer"] > p > span.{key}) {style}

"""

    style_text += f"""
    </style>

<span class="{key}"></span>
"""

    container = st.container()
    container.markdown(style_text, unsafe_allow_html=True)
    return container


class GridDeltaGenerator:
    def __init__(
        self,
        parent_dg,
        spec,
        *,
        gap = "small",
        repeat = True,
    ):
        self._parent_dg = parent_dg
        self._container_queue = []
        self._number_of_rows = 0
        self._spec = spec
        self._gap = gap
        self._repeat = repeat

    def _get_next_cell_container(self):
        if not self._container_queue:
            if not self._repeat and self._number_of_rows > 0:
                raise StreamlitAPIException("The row is already filled up.")

            # Create a new row using st.columns:
            self._number_of_rows += 1
            spec = self._spec[self._number_of_rows % len(self._spec) - 1]
            self._container_queue.extend(self._parent_dg.columns(spec, gap=self._gap))

        return self._container_queue.pop(0)

    def __getattr__(self, name):
        return getattr(self._get_next_cell_container(), name)


def grid(
    *spec,
    gap = "small",
    vertical_align = "top",
):
    """
    Insert a multi-element, grid container into your app.

    This function inserts a container into your app that arranges
    multiple elements in a grid layout as defined by the provided spec.
    Elements can be added to the returned container by calling methods directly
    on the returned object.

    Args:
        *spec (int | Iterable[int]): One or many row specs controlling the number and width of cells in each row.
            Each spec can be one of:
                * An integer specifying the number of cells. In this case, all cells have equal
                width.
                * An iterable of numbers (int or float) specifying the relative width of
                each cell. E.g., ``[0.7, 0.3]`` creates two cells, the first
                one occupying 70% of the available width and the second one 30%.
                Or, ``[1, 2, 3]`` creates three cells where the second one is twice
                as wide as the first one, and the third one is three times that width.
                The function iterates over the provided specs in a round-robin order. Upon filling a row,
                it moves on to the next spec, or the first spec if there are no
                more specs.
        gap (Optional[str], optional): The size of the gap between cells, specified as "small", "medium", or "large".
            This parameter defines the visual space between grid cells. Defaults to "small".
        vertical_align (Literal["top", "center", "bottom"], optional): The vertical alignment of the cells in the row.
            Defaults to "top".
    """

    container = stylable_container(
        key=f"grid_{vertical_align}",
        css_styles=[
            """
div[data-testid="column"] > div[data-testid="stVerticalBlockBorderWrapper"] > div {
height: 100%;
}
""",
            """
div[data-testid="column"] > div {
height: 100%;
}
""",
            f"""
div[data-testid="column"] > div[data-testid="stVerticalBlockBorderWrapper"] > div > div[data-testid="stVerticalBlock"] > div.element-container {{
    {"margin-top: auto;" if vertical_align in ["center", "bottom"] else ""}
    {"margin-bottom: auto;" if vertical_align == "center" else ""}
}}
""",
            f"""
div[data-testid="column"] > div > div[data-testid="stVerticalBlock"] > div.element-container {{
    {"margin-top: auto;" if vertical_align in ["center", "bottom"] else ""}
    {"margin-bottom: auto;" if vertical_align == "center" else ""}
}}
""",
        ],
    )

    return GridDeltaGenerator(
        parent_dg=container, spec=list(spec), gap=gap, repeat=True
    )


# Let's start by populating the sidebar.
with st.sidebar:
    st.image("./snowflake_logo.png")
    st.write("")
    app_mode = st.selectbox("App Mode:", ["Example App", "Custom UI Features"])
    st.write("☝️ Toggle for more features!")

    # Now change its color using a css selector,
    # we can search for the sidebar, then change its css properties.
    st.markdown(
        """
        <style>
            [data-testid=stSidebar] {
                background-color: #e4f6ff;
            }
            [data-testid=stSidebarUserContent] {
                padding-top: 3.5rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def example_app():
    st.sidebar.markdown(
        """
        <style>
            div.block-container {
                padding: 0px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    # Header section
    with stylable_container(
        key="title_container",
        css_styles="""
        {
            display: flex;
            padding-top: 50px;
            text-align: center;
            padding-bottom: 50px;
            flex-direction: row;
            align-items: center;
            box-sizing: border-box;
            background-color: #f4f8f9;
            justify-content: space-around;

            p {
                font-family: sans-serif;
            }

            > div:nth-child(2),
            > div:nth-child(3),
            > div:nth-child(4) {
                > div > div > div:nth-child(1) p {
                    color: #0095d2;
                    font-size: 50px;
                    font-weight: bold;
                }
                > div > div > div:nth-child(2) p {
                    color: #000000;
                    font-size: 18px;
                    font-weight: normal;
                }
            }
        }
            """,
        wrapper_style= """
            padding-left: 50px;
            padding-right: 50px;
            padding-bottom: 20px;
        """
    ):
        with st.container():
            st.write("9,437")
            st.write("Global Customers")
        with st.container():
            st.write("4.2B")
            st.write("Average Daily Queries")
        with st.container():
            st.write("2,416")
            st.write("Marketplace Listings")


    with stylable_container(
        key="blue_title_text",
        css_styles="""
        {
            p {
                color: #0095d2;
                font-size: 50px;
                font-weight: bold;
                text-align: center;
                font-family: sans-serif;
            }
        }
            """,
    ):
        st.write("Leading Companies")

    with stylable_container(
        key="black_title_text",
        css_styles="""
        {
            p {
                color: #000000;
                font-size: 50px;
                font-weight: bold;
                text-align: center;
                font-family: sans-serif;
            }
        }
            """,
    ):
        st.write("Lead with Snowflake")

    with stylable_container(
        key="description_text",
        css_styles="""
        {
            p {
                color: #000000;
                font-size: 18px;
                text-align: center;
                font-family: sans-serif;
            }
        }
            """,
        wrapper_style="""
            padding: 0px 150px;
        """,
    ):
        st.write(
            """
            Across the world and across industries, organizations are using the
            Snowflake Data Cloud to collaborate with data, build data applications
            and pull ahead of their competitors.
            """
        )

    # Icons section
    with stylable_container(
        key="icons_description_text",
        css_styles="""
        {
            p {
                color: #000000;
                font-size: 18px;
                font-style: italic;
                text-align: center;
                padding-top: 25px;
                padding-bottom: 25px;
                box-sizing: border-box;
                font-family: sans-serif;
            }
        }
            """,
    ):
        st.write("Over 7,200 brands mobilize their data with Snowflake")

    icons_arr = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Canva_Logo.svg/2560px-Canva_Logo.svg.png",
        "https://download.logo.wine/logo/Mastercard/Mastercard-Logo.wine.png",
        "https://1000logos.net/wp-content/uploads/2019/05/Electronic-Arts-Logo-2006.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Sainsbury%27s_Logo.svg/2560px-Sainsbury%27s_Logo.svg.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Cisco_logo.svg/1024px-Cisco_logo.svg.png",
        "https://upload.wikimedia.org/wikipedia/commons/9/9d/Comcast_logo.svg",
        "https://1000logos.net/wp-content/uploads/2021/04/Albertsons-logo.png",
        "https://logos-world.net/wp-content/uploads/2021/09/Notre-Dame-Logo.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Komatsu_company_logos.svg/2560px-Komatsu_company_logos.svg.png",
        "https://1000logos.net/wp-content/uploads/2021/05/NBCUniversal-logo.png",
    ]
    with stylable_container(
        key="row_1_icons_container",
        css_styles="""
            {
                display: flex;
                flex-direction: row;
                align-items: center;
                justify-content: space-around;


                > div {
                    width: 140px;

                    > div > div {
                        width: 140px !important;
                    }
                }
            }
            """,
    ):
        st.image(icons_arr[0], width=140)
        st.image(icons_arr[1], width=140)
        st.image(icons_arr[2], width=140)
        st.image(icons_arr[3], width=140)
        st.image(icons_arr[4], width=140)

    with stylable_container(
        key="row_2_icons_container",
        css_styles="""
        {
            display: flex;
            flex-direction: row;
            align-items: center;
            padding-bottom: 100px;
            box-sizing: border-box;
            justify-content: space-around;

            > div {
                width: 140px;

                > div > div {
                    width: 140px !important;
                }
            }
        }
            """,
    ):
        st.image(icons_arr[5], width=140)
        st.image(icons_arr[6], width=140)
        st.image(icons_arr[7], width=140)
        st.image(icons_arr[8], width=140)
        st.image(icons_arr[9], width=140)

    # Buttons section
    with stylable_container(
        key="buttons_container",
        css_styles="""
        {
            div[data-testid="stVerticalBlock"] {
                align-items: center;
            }
        }
            """,
    ):
        button1_col, button2_col = st.columns(2)

        with button1_col:
            with stylable_container(
                key="filled_button",
                css_styles="""
                {
                    button {
                        height: 56px;
                        width: 220px;
                        margin: 10px;
                        color: #ffffff;
                        border-radius: 50px;
                        text-transform: uppercase;
                        background-color: #0095d2;
                        border: 1px solid #0095d2;
                    }
                }
                    """,
            ):
                st.button("VIEW CUSTOMERS")

        with button2_col:
            with stylable_container(
                key="non_filled_button",
                css_styles="""
                {
                    button {
                        width: 220px;
                        margin: 10px;
                        height: 56px;
                        color: #0095d2;
                        border-radius: 50px;
                        text-transform: uppercase;
                        border: 1px solid #0095d2;
                        background-color: #ffffff;
                    }
                }
                    """,
            ):
                st.button("CUSTOMER WEBINARS")

    # Footer section
    with stylable_container(
        key="footer_container",
        css_styles="""
        {
            padding-top: 100px;
            box-sizing: border-box;

            .element-container {
                height: 70px;
                display: flex;
                color: #ffffff;
                text-align: center;
                align-items: center;
                background-color: #0054a3;

                a {
                    color: #ffffff;
                }
            }
        }
            """,
    ):
        st.write("For more information, visit www.snowflake.com")


def custom_ui_features():
    # Clear the padding MD from other mode
    st.sidebar.markdown("")

    st.title("✨ Custom UI for Streamlit in Snowflake")

    """
    Custom UI enables customization of the look, feel, and front-end behavior of Streamlit in Snowflake apps.
    This feature supports the following:
    - Custom HTML and CSS using `unsafe_allow_html=True` in [st.markdown](https://docs.streamlit.io/library/api-reference/text/st.markdown).
    - Iframed HTML, CSS, and JavaScript using [st.components.v1.html](https://docs.streamlit.io/develop/api-reference/custom-components/st.components.v1.html).

    Many of the examples in this app also leverage the `streamlit-extras` package, which
    includes a number of features unlocked by Custom UI (some features still may not work).

    👉 **[Check out the docs to learn more.](https://docs.snowflake.com/en/developer-guide/streamlit/additional-features#custom-ui-in-sis)**
    """
            
    st.subheader("Add a stylable container")
    st.caption("Taken (with slight modification) from [streamlit-extras](https://arnaudmiribel.github.io/streamlit-extras/extras/stylable_container/)")

    with st.expander("`stylable_container()`"):
        st.code(inspect.getsource(stylable_container))

    with echo_expander(label="Usage"):
        with stylable_container(
            key="green_button",
            css_styles="""
                button {
                    background-color: green;
                    color: white;
                    border-radius: 20px;
                }
                """,
        ):
            st.button("Green button")

        st.button("Normal button")

        with stylable_container(
            key="container_with_border",
            css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px)
                }
                """,
        ):
            st.markdown("This is a container with a border.")

    st.subheader("Styled cards")
    st.caption("Uses `stylable_container()` from above")

    with echo_expander():
        card_style = """
            {
                border: 1px groove #52546a;
                border-radius: 10px;
                padding-left: 25px;
                padding-top: 10px;
                padding-bottom: 10px;
                box-shadow: -6px 8px 20px 1px #00000052;
            }
        """

        col1, _, col2 = st.columns([3, 1, 1.6])
        with col1:
            with stylable_container("Card1", css_styles=card_style):
                "**Card 1**"
                "This is an example of basic card text."

        with col2:
            with stylable_container("Card2", css_styles=card_style):
                st.metric("New York", "19.8M", "367K", help="Population growth")

    st.subheader("Annotated text")

    with echo_expander():
        from streamlit_extras.annotated_text import annotated_text
        
        annotated_text(
            "This ",
            ("is", "verb", "#8ef"),
            " some ",
            ("annotated", "adj", "#faa"),
            ("text", "noun", "#afa"),
            " for those of ",
            ("you", "pronoun", "#fea"),
            " who ",
            ("like", "verb", "#8ef"),
            " this sort of ",
            ("thing", "noun", "#afa"),
        )

    st.subheader("Add a grid layout")
    st.caption("Taken from [streamlit-extras](https://arnaudmiribel.github.io/streamlit-extras/extras/grid/). Extends `stylable_container()`.")

    with st.expander("`grid()`"):
        grid_dg_code = inspect.getsource(GridDeltaGenerator)
        grid_code = inspect.getsource(grid)
        st.code(grid_dg_code + "\n\n" + grid_code)

    with echo_expander(label="Usage"):
        import pandas as pd
        import numpy as np
        
        random_df = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

        my_grid = grid(2, [2, 4, 1], 1, 4, vertical_align="bottom")

        # Row 1:
        my_grid.dataframe(random_df, use_container_width=True)
        my_grid.line_chart(random_df, use_container_width=True)
        # Row 2:
        my_grid.selectbox("Select Country", ["Germany", "Italy", "Japan", "USA"])
        my_grid.text_input("Your name")
        my_grid.button("Send", use_container_width=True)
        # Row 3:
        my_grid.text_area("Your message", height=40)
        # Row 4:
        my_grid.button("Example 1", use_container_width=True)
        my_grid.button("Example 2", use_container_width=True)
        my_grid.button("Example 3", use_container_width=True)
        my_grid.button("Example 4", use_container_width=True)
        # Row 5 (uses the spec from row 1):
        with my_grid.expander("Show Filters", expanded=True):
            st.slider("Filter by Age", 0, 100, 50)
            st.slider("Filter by Height", 0.0, 2.0, 1.0)
            st.slider("Filter by Weight", 0.0, 100.0, 50.0)
        my_grid.dataframe(random_df, use_container_width=True)

    st.subheader("YData Profile - Iris dataset stats")

    """
    Custom UI also supports rendering full HTML documents in an iframe.
    This is especially useful for python packages like `ydata-profiling` that can
    output HTML. In this case, we generate an interactive exploratory data analysis
    of a sample pandas dataframe (the classic [Iris dataset](https://archive.ics.uci.edu/dataset/53/iris)).
    """

    with st.echo():
        import streamlit.components.v1 as components
        from sklearn.datasets import load_iris
        from ydata_profiling import ProfileReport
        
        @st.cache_data
        def generate_report():
            df = load_iris(as_frame=True).data
            return ProfileReport(df).to_html()
        
        html = generate_report()
        components.html(html, height=650, scrolling=True)


if app_mode == "Example App":
    example_app()
elif app_mode == "Custom UI Features":
    custom_ui_features()
