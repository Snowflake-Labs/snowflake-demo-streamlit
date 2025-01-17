from streamlit_echarts import st_echarts

options = {
    "xAxis": {
        "type": "category",
        "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
    "yAxis": {"type": "value"},
    "series": [
        {"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "line"}
    ],
}
st_echarts(options=options)


def render_basic_candlestick():
    option = {
        "xAxis": {"data": ["2017-10-24", "2017-10-25", "2017-10-26", "2017-10-27"]},
        "yAxis": {},
        "series": [
            {
                "type": "k",
                "data": [
                    [20, 34, 10, 38],
                    [40, 35, 30, 50],
                    [31, 38, 33, 44],
                    [38, 15, 5, 42],
                ],
            }
        ],
    }
    st_echarts(option, height="500px")

render_basic_candlestick()

options = {
    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
    "legend": {
        "data": ["Direct", "Mail Ad", "Affiliate Ad", "Video Ad", "Search Engine"]
    },
    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
    "xAxis": {"type": "value"},
    "yAxis": {
        "type": "category",
        "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
    "series": [
        {
            "name": "Direct",
            "type": "bar",
            "stack": "total",
            "label": {"show": True},
            "emphasis": {"focus": "series"},
            "data": [320, 302, 301, 334, 390, 330, 320],
        },
        {
            "name": "Mail Ad",
            "type": "bar",
            "stack": "total",
            "label": {"show": True},
            "emphasis": {"focus": "series"},
            "data": [120, 132, 101, 134, 90, 230, 210],
        },
        {
            "name": "Affiliate Ad",
            "type": "bar",
            "stack": "total",
            "label": {"show": True},
            "emphasis": {"focus": "series"},
            "data": [220, 182, 191, 234, 290, 330, 310],
        },
        {
            "name": "Video Ad",
            "type": "bar",
            "stack": "total",
            "label": {"show": True},
            "emphasis": {"focus": "series"},
            "data": [150, 212, 201, 154, 190, 330, 410],
        },
        {
            "name": "Search Engine",
            "type": "bar",
            "stack": "total",
            "label": {"show": True},
            "emphasis": {"focus": "series"},
            "data": [820, 832, 901, 934, 1290, 1330, 1320],
        },
    ],
}
st_echarts(options=options, height="500px")