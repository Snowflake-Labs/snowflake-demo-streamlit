![](../shared_assets/sis-header.jpeg)

## Private Preview

**Note:** This is an experimental preview feature and is not fully functional. Support may be limited to specific accounts. 

## Bidirectional Custom Components 

This app demonstrates how to use bidirectional custom components in Streamlit in Snowflake.


## Steps for using custom components in Streamlit in Snowflake

1. Download the component code from pypi, and extract the tarball

2. Add the component to the `_stcore/components/` directory in your app.

3. Add the component's directory to the ROOT_LOCATION of the app

4. Add the pythoncode containing the `declare_component` function to `ROOT_LOCATION/COMPONENT_NAME/` 

As an example, see the `streamlit_echarts` component in this app. 


## Limitations
* Only components which don't trigger requests to external services are supported.
* Supported components include:
    * AgGrid (streamlit-aggrid)
    * ECharts (streamlit-echarts)


## Troubleshooting
* When using git to add component files, git add may ignore files in `build`, or `frontend` directories.