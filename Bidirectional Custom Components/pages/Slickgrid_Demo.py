# Copyright 2025 Snowflake Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import numpy as np
import math
import random
from streamlit_slickgrid import (
    add_tree_info,
    slickgrid,
    Formatters,
    Filters,
    FieldType,
    OperatorType,
    ExportServices,
    StreamlitSlickGridFormatters,
    StreamlitSlickGridSorters,
)

st.set_page_config(
    layout="wide",
)


@st.cache_resource
def mockData(count):
    """Build some mock data."""
    mockDataset = []

    epics_in_milestone = 0
    tasks_in_epic = 0
    m = 0
    e = 0
    t = 0

    for i in range(count):
        randomYear = 2000 + math.floor(random.random() * 10)
        randomMonth = math.floor(random.random() * 11)
        randomDay = math.floor((random.random() * 29))
        randomPercent = round(random.random() * 100)

        if t >= tasks_in_epic:
            tasks_in_epic = random.randint(2, 10)
            t = 0
            e += 1
        else:
            t += 1

        if e >= epics_in_milestone:
            epics_in_milestone = random.randint(2, 10)
            tasks_in_epic = 0
            m += 1
            e = 0
            t = 0

        mockDataset.append(
            {
                "id": i,
                "milestone": f"Milestone M{m:02}",
                "epic": None if e == 0 else f"Epic M{m:02}/E{e:02}",
                "task": None if t == 0 else f"Task M{m:02}/E{e:02}/T{t:02}",
                "stages": [round(random.random() * 100) for _ in range(3)],
                "duration": round(random.random() * 100),
                "percentComplete": randomPercent,
                "start": f"{randomYear:02}-{randomMonth + 1:02}-{randomDay:02}",
                "finish": f"{randomYear + 1:02}-{randomMonth + 1:02}-{randomDay:02}",
                "effortDriven": (i % 5 == 0),
            }
        )

    return mockDataset


"""
# Streamlit-SlickGrid demo

For more info, see https://github.com/streamlit/streamlit-slickgrid.
"""

# streamlit-slickgrid requires the data to be a list of dicts.
#
# For example:
#
#   data = [
#     {"id": 0, "continent": "america", "revenue": 20000, "paused": False},
#     {"id": 1, "continent": "africa",  "revenue": 40100, "paused": False},
#     {"id": 2, "continent": "asia",    "revenue": 10300, "paused": True},
#     {"id": 3, "continent": "europe",  "revenue": 30200, "paused": False},
#     ...
#   ]
#
# Here we're just building a random dataset:
data = mockData(1000)

# Coalesce the milestone, epic, and task fields into a single one called title.
data = add_tree_info(
    data,
    tree_fields=["milestone", "epic", "task"],
    join_fields_as="title",
    id_field="id",
)

# Some nice colors to use in the table.
red = "#ff4b4b"
orange = "#ffa421"
yellow = "#ffe312"
green = "#21c354"
teal = "#00c0f2"
blue = "#1c83e1"
violet = "#803df5"
white = "#fafafa"
gray = "#808495"
black = "#262730"

# Declare SlickGrid columns.
#
# See full list of options at:
# - https://github.com/ghiscoding/slickgrid-universal/blob/master/packages/common/src/interfaces/column.interface.ts#L40
#
# Not all column options are supported, though!
columns = [
    {
        "id": "title",
        "name": "Title",
        "field": "title",
        "sortable": True,
        "minWidth": 50,
        "type": FieldType.string,
        "filterable": True,
        "formatter": Formatters.tree,
        "exportCustomFormatter": Formatters.treeExport,
    },
    {
        "id": "duration",
        "name": "Duration (days)",
        "field": "duration",
        "sortable": True,
        "minWidth": 100,
        "type": FieldType.number,
        "filterable": True,
        "filter": {
            "model": Filters.slider,
            "operator": ">=",
        },
        "formatter": StreamlitSlickGridFormatters.numberFormatter,
        "params": {
            "colors": [
                # [maxValue, foreground, background]
                [20, blue, None],  # None is the same as leaving out
                [50, green],
                [100, gray],
            ],
            "minDecimal": 0,
            "maxDecimal": 2,
            "numberSuffix": "d",
        },
    },
    {
        "id": "stages",
        "name": "Stages",
        "field": "stages",
        "sortable": True,
        "sorter": StreamlitSlickGridSorters.numberArraySorter,
        "minWidth": 100,
        # Sorry, the "stages" field contains arrays, which aren't filterable.
        "filterable": False,
        "formatter": StreamlitSlickGridFormatters.stackedBarFormatter,
        "params": {
            "colors": [
                # [maxValue, foreground, background]
                [20, white, red],
                [70, black, orange],
                [100, white, green],
            ],
            "minDecimal": 0,
            "maxDecimal": 2,
            "min": 0,
            "max": 300,
        },
    },
    {
        "id": "%",
        "name": "% Complete",
        "field": "percentComplete",
        "sortable": True,
        "minWidth": 100,
        "type": FieldType.number,
        "filterable": True,
        "filter": {
            "model": Filters.sliderRange,
            "maxValue": 100,
            "operator": OperatorType.rangeInclusive,
            "filterOptions": {"hideSliderNumbers": False, "min": 0, "step": 5},
        },
        # Use the default progress bar formatter:
        # "formatter": Formatters.progressBar,
        #
        # Or use this fancy one that's ultra-configurable:
        "formatter": StreamlitSlickGridFormatters.barFormatter,
        "params": {
            "colors": [[50, white, red], [100, white, green]],
            "minDecimal": 0,
            "maxDecimal": 2,
            "numberSuffix": "%",
        },
    },
    {
        "id": "start",
        "name": "Start",
        "field": "start",
        "type": FieldType.date,
        "filterable": True,
        "filter": {"model": Filters.compoundDate},
        "formatter": Formatters.dateIso,
    },
    {
        "id": "finish",
        "name": "Finish",
        "field": "finish",
        "type": FieldType.date,
        "filterable": True,
        "filter": {"model": Filters.dateRange},
        "formatter": Formatters.dateIso,
    },
    {
        "id": "effort-driven",
        "name": "Effort Driven",
        "field": "effortDriven",
        "sortable": True,
        "minWidth": 100,
        "type": FieldType.boolean,
        "filterable": True,
        "filter": {
            "model": Filters.singleSelect,
            "collection": [
                {"value": "", "label": ""},
                {"value": True, "label": "True"},
                {"value": False, "label": "False"},
            ],
        },
        "formatter": Formatters.checkmarkMaterial,
    },
]


# Configure additional options streamlit-slickgrid.
#
# See full list of options at:
# - https://github.com/ghiscoding/slickgrid-universal/blob/master/packages/common/src/interfaces/gridOption.interface.ts#L76
#
# Not all grid options are supported, though!
options = {
    #
    # Allow filtering (based on column filter* properties)
    "enableFiltering": True,
    # --
    #
    # Debounce/throttle the input text filter if you have lots of data
    # filterTypingDebounce: 250,
    # --
    #
    # Set up export options.
    "enableTextExport": True,
    "enableExcelExport": True,
    "excelExportOptions": {"sanitizeDataExport": True},
    "textExportOptions": {"sanitizeDataExport": True},
    "externalResources": [
        ExportServices.ExcelExportService,
        ExportServices.TextExportService,
    ],
    # --
    #
    # Pin columns.
    # "frozenColumn": 0,
    # --
    #
    # Pin rows.
    # "frozenRow": 0,
    # --
    #
    # Don't scroll table when too big. Instead, just let it grow.
    # "autoHeight": True,
    # --
    #
    "autoResize": {
        "minHeight": 500,
    },
    # --
    #
    # Set up tree.
    "enableTreeData": True,
    "multiColumnSort": False,
    "treeDataOptions": {
        "columnId": "title",
        "indentMarginLeft": 15,
        "initiallyCollapsed": True,
        # This is a field that add_tree_info() inserts in your data:
        "parentPropName": "__parent",
        # This is a field that add_tree_info() inserts in your data:
        "levelPropName": "__depth",
        #
        # If you're building your own tree (without add_tree_info),
        # you should configure the props above accordingly.
        #
        # See below for more info:
        # - https://ghiscoding.github.io/slickgrid-react-demos/#/example27
        # - https://ghiscoding.github.io/slickgrid-react-demos/#/example28
    },
}

out = slickgrid(data, columns, options, key="mygrid", on_click="rerun")


@st.dialog("Details", width="large")
def show_dialog(item):
    st.write("Congrats! You clicked on the row below:")
    st.write(item)

    st.write("Here's a random chart for you:")
    st.write("")

    st.scatter_chart(np.random.randn(100, 5))


if out is not None:
    row, col = out
    show_dialog(data[row])