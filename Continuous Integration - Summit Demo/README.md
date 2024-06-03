![](../shared_assets/sis-header.jpeg)

# Snowflake Summit Demo 2024

This repo contains a demo that was used during the Snowflake Summit in June of 2024. In this demo we show
users how to create a full CI/CD workflow with Github and the SnowCLI, along with how to use Snowflake Cortex
inside Streamlit in Snowflake.

To set up this repo, simply clone it, set up your [SnowCLI config](https://docs.snowflake.com/en/developer-guide/snowflake-cli-v2/index),
then run ```snow streamlit deploy --replace``` to deploy your version of the app. All the GitHub workflows are in the .github folder as well.

The end of the app relies on a table created in the demo called ```streamlit.public.feedback_table```. To create this table, you can [upload](https://docs.snowflake.com/en/user-guide/data-load-web-ui) the dummy data supplied in the ```feedback.csv``` file.

Note: All data in this demo is dummy data, and this demo used a trial account. Please add your own info to the ```tmp_config.toml``` file to use.

Questions? Please email tyler.richards@snowflake.com to get more info.

## Demo App Preview
![File Snapshot](assets/snapshot_app.gif)